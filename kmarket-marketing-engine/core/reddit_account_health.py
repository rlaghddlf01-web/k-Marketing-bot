"""
📊 [Reddit Account Health Monitor — 계정 건강 상태 추적기]
- 카르마 수치 추적 및 이력 관리
- 댓글 삭제/숨김 감지 (게시 후 확인)
- Shadowban 감지 (비로그인 시점에서 가시성 체크)
- 경고 레벨 기반 자동 쿨다운 관리
- 워밍업 상태 판단 (카르마 < WARMUP_KARMA_THRESHOLD → 홍보 금지)
"""

import json
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import DATA_DIR, WARMUP_KARMA_THRESHOLD, get_now_kst, get_now_kst_str

logger = logging.getLogger("RedditAccountHealth")

# 경고 레벨 정의
ALERT_NONE = 0       # 정상
ALERT_CAUTION = 1    # 주의 (댓글 1건 삭제 감지)
ALERT_WARNING = 2    # 경고 (댓글 2건+ 삭제 or 빠른 연속 삭제)
ALERT_DANGER = 3     # 위험 (shadowban 의심)
ALERT_CRITICAL = 4   # 긴급 (모든 활동 즉시 중단)

# 쿨다운 시간 (초)
COOLDOWN_MAP = {
    ALERT_NONE: 0,
    ALERT_CAUTION: 3600,        # 1시간 홍보 중단
    ALERT_WARNING: 86400,       # 24시간 홍보 중단
    ALERT_DANGER: 259200,       # 72시간 전체 활동 중단
    ALERT_CRITICAL: 604800,     # 7일 전체 활동 중단
}


class AccountHealthMonitor:
    """
    📊 Reddit 계정 건강 상태 추적 및 자동 보호 엔진
    - 카르마 추적, 삭제 감지, shadowban 감지
    - 경고 레벨에 따라 자동 쿨다운
    """
    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id
        self.state_file = DATA_DIR / "reddit_profiles" / f"{service_id}_health.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """건강 상태 파일 로드 (없으면 초기화)"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"건강 상태 로드 실패: {e}")
        return {
            "service_id": self.service_id,
            "karma": 0,
            "username": None,
            "alert_level": ALERT_NONE,
            "cooldown_until": None,
            "deleted_comments_count": 0,
            "total_comments_posted": 0,
            "total_upvotes_given": 0,
            "total_organic_comments": 0,
            "last_karma_check": None,
            "last_activity": None,
            "daily_promo_count": 0,
            "daily_organic_count": 0,
            "daily_upvote_count": 0,
            "daily_reset_date": None,
            "recent_deletions": [],
            "karma_history": [],
        }

    def _save_state(self):
        """건강 상태 영구 저장"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"건강 상태 저장 실패: {e}")

    # ──────────────────────────────────────────
    # 일일 카운터 관리
    # ──────────────────────────────────────────

    def _check_daily_reset(self):
        """날짜가 바뀌면 일일 카운터 초기화"""
        today = get_now_kst_str("%Y-%m-%d")
        if self.state.get("daily_reset_date") != today:
            self.state["daily_promo_count"] = 0
            self.state["daily_organic_count"] = 0
            self.state["daily_upvote_count"] = 0
            self.state["daily_reset_date"] = today
            self._save_state()
            logger.info(f"📅 일일 카운터 초기화 (날짜: {today})")

    def record_promo_comment(self):
        """홍보성 댓글 1건 기록"""
        self._check_daily_reset()
        self.state["daily_promo_count"] += 1
        self.state["total_comments_posted"] += 1
        self.state["last_activity"] = get_now_kst_str()
        self._save_state()

    def record_organic_comment(self):
        """비홍보 댓글 1건 기록"""
        self._check_daily_reset()
        self.state["daily_organic_count"] += 1
        self.state["total_organic_comments"] += 1
        self.state["last_activity"] = get_now_kst_str()
        self._save_state()

    def record_upvote(self):
        """업보트 1건 기록"""
        self._check_daily_reset()
        self.state["daily_upvote_count"] += 1
        self.state["total_upvotes_given"] += 1
        self._save_state()

    # ──────────────────────────────────────────
    # 카르마 & 워밍업 상태
    # ──────────────────────────────────────────

    def update_karma(self, karma: int, username: Optional[str] = None):
        """카르마 수치 업데이트"""
        self.state["karma"] = karma
        if username:
            self.state["username"] = username
        self.state["last_karma_check"] = get_now_kst_str()
        # 카르마 이력 기록 (최근 30건)
        self.state.setdefault("karma_history", []).append({
            "karma": karma,
            "timestamp": get_now_kst_str()
        })
        self.state["karma_history"] = self.state["karma_history"][-30:]
        self._save_state()
        logger.info(f"📊 카르마 업데이트: {karma} (username: {username})")

    def is_warmup_phase(self) -> bool:
        """워밍업 단계인지 확인 (카르마 < 임계값)"""
        return self.state.get("karma", 0) < WARMUP_KARMA_THRESHOLD

    def get_karma(self) -> int:
        """현재 카르마 반환"""
        return self.state.get("karma", 0)

    # ──────────────────────────────────────────
    # 한도 확인
    # ──────────────────────────────────────────

    def can_post_promo(self, daily_limit: int) -> bool:
        """홍보 댓글을 올릴 수 있는지 확인"""
        self._check_daily_reset()
        if self.is_warmup_phase():
            logger.info(f"🛡️ 워밍업 단계 (카르마 {self.get_karma()} < {WARMUP_KARMA_THRESHOLD}) — 홍보 댓글 차단")
            return False
        if self.is_in_cooldown():
            logger.info(f"🛡️ 쿨다운 중 — 홍보 댓글 차단 (해제: {self.state.get('cooldown_until')})")
            return False
        if self.state["daily_promo_count"] >= daily_limit:
            logger.info(f"🛡️ 일일 홍보 한도 도달 ({self.state['daily_promo_count']}/{daily_limit})")
            return False
        return True

    def can_post_organic(self, daily_limit: int) -> bool:
        """비홍보 댓글을 올릴 수 있는지 확인"""
        self._check_daily_reset()
        if self.is_in_cooldown() and self.state.get("alert_level", 0) >= ALERT_DANGER:
            logger.info("🛡️ 위험 레벨 쿨다운 — 모든 댓글 차단")
            return False
        return self.state["daily_organic_count"] < daily_limit

    def can_upvote(self, daily_limit: int) -> bool:
        """업보트를 할 수 있는지 확인"""
        self._check_daily_reset()
        if self.is_in_cooldown() and self.state.get("alert_level", 0) >= ALERT_DANGER:
            return False
        return self.state["daily_upvote_count"] < daily_limit

    # ──────────────────────────────────────────
    # 경고 & 쿨다운
    # ──────────────────────────────────────────

    def is_in_cooldown(self) -> bool:
        """쿨다운 중인지 확인"""
        cooldown_until = self.state.get("cooldown_until")
        if not cooldown_until:
            return False
        try:
            until_dt = datetime.datetime.fromisoformat(cooldown_until)
            if until_dt.tzinfo is None:
                from config import KST
                until_dt = until_dt.replace(tzinfo=KST)
            return get_now_kst() < until_dt
        except Exception:
            return False

    def report_deletion(self, post_url: str, comment_snippet: str):
        """댓글 삭제/숨김 감지 보고"""
        self.state["deleted_comments_count"] += 1
        self.state.setdefault("recent_deletions", []).append({
            "post_url": post_url,
            "snippet": comment_snippet[:100],
            "detected_at": get_now_kst_str()
        })
        self.state["recent_deletions"] = self.state["recent_deletions"][-20:]

        # 경고 레벨 자동 상향
        deleted_count = self.state["deleted_comments_count"]
        if deleted_count >= 5:
            new_level = ALERT_CRITICAL
        elif deleted_count >= 3:
            new_level = ALERT_DANGER
        elif deleted_count >= 2:
            new_level = ALERT_WARNING
        else:
            new_level = ALERT_CAUTION

        self._set_alert_level(new_level)
        logger.warning(f"⚠️ 댓글 삭제 감지! 총 {deleted_count}건, 경고 레벨: {new_level}")

    def report_shadowban_suspected(self):
        """Shadowban 의심 보고"""
        self._set_alert_level(ALERT_DANGER)
        logger.error("🚨 SHADOWBAN 의심! 72시간 전체 활동 중단")

    def _set_alert_level(self, level: int):
        """경고 레벨 설정 및 쿨다운 적용"""
        self.state["alert_level"] = level
        cooldown_sec = COOLDOWN_MAP.get(level, 0)
        if cooldown_sec > 0:
            from config import KST
            cooldown_until = get_now_kst() + datetime.timedelta(seconds=cooldown_sec)
            self.state["cooldown_until"] = cooldown_until.isoformat()
        self._save_state()

    def clear_alert(self):
        """경고 해제 (수동)"""
        self.state["alert_level"] = ALERT_NONE
        self.state["cooldown_until"] = None
        self.state["deleted_comments_count"] = 0
        self._save_state()
        logger.info("✅ 경고 레벨 수동 해제 완료")

    # ──────────────────────────────────────────
    # 상태 요약
    # ──────────────────────────────────────────

    def get_status_summary(self) -> Dict[str, Any]:
        """현재 건강 상태 요약"""
        self._check_daily_reset()
        return {
            "service_id": self.service_id,
            "username": self.state.get("username"),
            "karma": self.state.get("karma", 0),
            "is_warmup": self.is_warmup_phase(),
            "alert_level": self.state.get("alert_level", 0),
            "in_cooldown": self.is_in_cooldown(),
            "cooldown_until": self.state.get("cooldown_until"),
            "today_promo": self.state.get("daily_promo_count", 0),
            "today_organic": self.state.get("daily_organic_count", 0),
            "today_upvotes": self.state.get("daily_upvote_count", 0),
            "total_posted": self.state.get("total_comments_posted", 0),
            "total_deleted": self.state.get("deleted_comments_count", 0),
        }
