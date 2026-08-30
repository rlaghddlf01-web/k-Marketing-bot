"""
🧠 [Reddit Safety Orchestrator — 일일 활동 안전 총괄 오케스트레이터]
- 하루 전체 레딧 활동을 "진짜 사람 일정"처럼 매일 무작위 ±30분 시프트 스케줄링
  1. 아침 기상 (기본 08:00 ±30분)  🌱 피드 스크롤 3~5분 + 업보트 3~5건
  2. 오전 활동 (기본 10:00 ±30분)  💬 비홍보 댓글 2~3건 + 업보트 3~5건  
  3. 점심 시간 (기본 13:00 ±30분)  🎯 홍보 댓글 1건 (워밍업 통과 시) + 업보트 2~3건
  4. 오후 활동 (기본 16:00 ±30분)  💬 비홍보 댓글 2~3건 + 업보트 2~3건
  5. 저녁 피크 (기본 20:00 ±30분)  🎯 홍보 댓글 0~1건 + 비홍보 1~2건 + 업보트 2~3건
- 업보트 40% + 비홍보 댓글 35% + 스크롤 20% + 홍보 5% 비율 엄격 유지
- 워밍업 기간(카르마 < 100) → 홍보 댓글 자동 0건 강제 차단
- 주말 활동량 30% 자동 감량 (실제 유저 패턴 반영)
- 경고 레벨 기반 자동 쿨다운 관리
"""

import os
import time
import json
import random
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import (
    DATA_DIR,
    DAILY_REDDIT_PROMO_LIMIT, DAILY_REDDIT_ORGANIC_LIMIT,
    DAILY_REDDIT_UPVOTE_LIMIT, HOURLY_REDDIT_LIMIT,
    REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC,
    ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC,
    WARMUP_KARMA_THRESHOLD,
    get_now_kst, get_now_kst_str,
)
from core.reddit_organic_engine import RedditOrganicEngine
from core.reddit_account_health import AccountHealthMonitor
from core.reddit_browser_driver import RedditBrowserDriver
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("RedditSafetyOrchestrator")

# 5대 기본 스케줄 슬롯 (기본 시각)
DEFAULT_SLOTS = [
    {"slot_id": "slot_08", "base_hour": 8,  "base_min": 0,  "name": "아침 기상 세션"},
    {"slot_id": "slot_10", "base_hour": 10, "base_min": 0,  "name": "오전 활성 세션"},
    {"slot_id": "slot_13", "base_hour": 13, "base_min": 0,  "name": "점심 골든타임"},
    {"slot_id": "slot_16", "base_hour": 16, "base_min": 0,  "name": "오후 활성 세션"},
    {"slot_id": "slot_20", "base_hour": 20, "base_min": 0,  "name": "저녁 피크 세션"},
]


class RedditSafetyOrchestrator:
    """
    🧠 Reddit 일일 활동 안전 총괄 오케스트레이터
    - 매일 매일 다른 시간(±30분 무작위 시프트)으로 5회 분산 활동
    - 카르마 100점 미만 시 홍보 댓글 0건 강제 차단
    - 주말 활동량 30% 감량
    """
    def __init__(self, service_id: str = "kmarket", db_mgr: Optional[DBManager] = None, supabase_mgr: Optional[SupabaseManager] = None):
        self.service_id = service_id
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.health = AccountHealthMonitor(service_id=service_id)
        self.organic = RedditOrganicEngine(service_id=service_id)
        self.driver = RedditBrowserDriver(service_id=service_id)
        self.plan_file = DATA_DIR / "reddit_profiles" / f"{service_id}_daily_plan.json"

        # 홍보 모듈 핸들러 (kmarket_bot / easytax_bot에서 주입)
        self._promo_handler = None

    def set_promo_handler(self, handler_func):
        """홍보 댓글 핸들러 설정"""
        self._promo_handler = handler_func

    # ──────────────────────────────────────────
    # 🎲 일일 무작위 ±30분 시프트 플래너
    # ──────────────────────────────────────────

    def _get_or_create_daily_plan(self) -> Dict[str, Any]:
        """오늘 날짜의 ±30분 랜덤 시프트 스케줄 생성 및 로드"""
        today_str = get_now_kst_str("%Y-%m-%d")
        plan = {}

        if self.plan_file.exists():
            try:
                with open(self.plan_file, "r", encoding="utf-8") as f:
                    plan = json.load(f)
            except Exception:
                plan = {}

        # 날짜가 바뀌었으면 새로운 랜덤 플랜 생성
        if plan.get("date") != today_str:
            planned_slots = []
            for item in DEFAULT_SLOTS:
                # ±30분 무작위 시프트 (예: 08시 -> 07:35 ~ 08:30)
                shift_minutes = random.randint(-25, 30)
                base_dt = datetime.datetime.strptime(f"{today_str} {item['base_hour']:02d}:{item['base_min']:02d}", "%Y-%m-%d %H:%M")
                planned_dt = base_dt + datetime.timedelta(minutes=shift_minutes)
                planned_slots.append({
                    "slot_id": item["slot_id"],
                    "name": item["name"],
                    "planned_time": planned_dt.strftime("%H:%M"),
                    "executed": False,
                    "executed_at": None,
                    "shift_minutes": shift_minutes
                })

            plan = {
                "date": today_str,
                "service_id": self.service_id,
                "slots": planned_slots
            }
            try:
                self.plan_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.plan_file, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
                times_summary = ", ".join([f"{s['name']}({s['planned_time']})" for s in planned_slots])
                logger.info(f"🎲 [{self.service_id}] 오늘(±30분 시프트) 일일 계획 확정: {times_summary}")
            except Exception as e:
                logger.error(f"일일 계획 저장 실패: {e}")

        return plan

    def _save_daily_plan(self, plan: Dict[str, Any]):
        """일일 계획 파일 저장"""
        try:
            with open(self.plan_file, "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"일일 계획 저장 에러: {e}")

    # ──────────────────────────────────────────
    # ⏰ 시간대별 인간 스케줄 실행 엔진
    # ──────────────────────────────────────────

    def run_scheduled_session(self, current_hour: Optional[int] = None) -> Dict[str, Any]:
        """
        현재 시간에 맞는 레딧 스케줄 세션 1회 실행
        - 매일 생성된 ±30분 시프트 시각을 체크하여 자동 실행
        - 주말 활동량 30% 감량
        - 카르마 < 100 워밍업 시 홍보 댓글 0건 강제 차단
        """
        now = get_now_kst()
        current_time_str = now.strftime("%H:%M")
        today_str = now.strftime("%Y-%m-%d")
        plan = self._get_or_create_daily_plan()

        # 건강 상태 확인
        health_status = self.health.get_status_summary()
        if health_status["in_cooldown"] and health_status["alert_level"] >= 3:
            logger.warning(f"🚨 [{self.service_id}] 위험 레벨 쿨다운 중 — 활동 스킵")
            return {"status": "cooldown", "alert_level": health_status["alert_level"]}

        is_weekend = now.weekday() >= 5
        results = {
            "timestamp": get_now_kst_str(),
            "service_id": self.service_id,
            "status": "idle",
            "executed_slot": None,
            "upvotes": 0,
            "organic_comments": 0,
            "promo_comments": 0,
            "browsing_done": False
        }

        # 오늘 실행해야 할 슬롯 중 예정 시각이 도래한 미실행 슬롯 찾기
        for slot in plan.get("slots", []):
            if slot.get("executed"):
                continue

            # 예정된 시각(HH:MM)이 지났는지 확인
            if current_time_str >= slot["planned_time"]:
                slot_id = slot["slot_id"]
                logger.info(f"🚀 [{self.service_id}] {slot['name']} 실행 시작 (예정: {slot['planned_time']}, 현재: {current_time_str}, 시프트: {slot.get('shift_minutes')}분)")

                # 1. 아침 기상 (기본 08:00 ±30분)
                if slot_id == "slot_08":
                    browse_sec = random.randint(180, 300)
                    if is_weekend: browse_sec = int(browse_sec * 0.7)
                    b_res = self.organic.run_browse_session(duration_sec=browse_sec)
                    results["browsing_done"] = b_res.get("success", False)

                    upvote_cnt = random.randint(3, 5)
                    u_res = self.organic.run_upvote_session(count=upvote_cnt)
                    results["upvotes"] = u_res.get("upvoted", 0)

                # 2. 오전 활성 (기본 10:00 ±30분)
                elif slot_id == "slot_10":
                    c_cnt = random.randint(2, 3)
                    if is_weekend: c_cnt = max(1, c_cnt - 1)
                    c_res = self.organic.run_organic_comment_session(count=c_cnt)
                    results["organic_comments"] = c_res.get("commented", 0)

                    time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

                    u_cnt = random.randint(3, 5)
                    u_res = self.organic.run_upvote_session(count=u_cnt)
                    results["upvotes"] = u_res.get("upvoted", 0)

                # 3. 점심 골든타임 (기본 13:00 ±30분)
                elif slot_id == "slot_13":
                    u_cnt = random.randint(2, 3)
                    u_res = self.organic.run_upvote_session(count=u_cnt)
                    results["upvotes"] = u_res.get("upvoted", 0)

                    time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

                    # 🛡️ 카르마 100 미만 워밍업 상태면 홍보 댓글 0건 강제 차단
                    if self._promo_handler and self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
                        try:
                            p_cnt = self._promo_handler()
                            results["promo_comments"] = p_cnt
                        except Exception as e:
                            logger.error(f"홍보 댓글 실행 에러: {e}")
                    else:
                        logger.info(f"🌱 [워밍업/한도 보호] 카르마 {self.health.get_karma()}/{WARMUP_KARMA_THRESHOLD} — 홍보 댓글 0건 유지")

                # 4. 오후 활성 (기본 16:00 ±30분)
                elif slot_id == "slot_16":
                    c_cnt = random.randint(2, 3)
                    if is_weekend: c_cnt = max(1, c_cnt - 1)
                    c_res = self.organic.run_organic_comment_session(count=c_cnt)
                    results["organic_comments"] = c_res.get("commented", 0)

                    time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

                    u_cnt = random.randint(2, 3)
                    u_res = self.organic.run_upvote_session(count=u_cnt)
                    results["upvotes"] = u_res.get("upvoted", 0)

                # 5. 저녁 피크 (기본 20:00 ±30분)
                elif slot_id == "slot_20":
                    c_cnt = random.randint(1, 2)
                    c_res = self.organic.run_organic_comment_session(count=c_cnt)
                    results["organic_comments"] = c_res.get("commented", 0)

                    time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

                    # 🛡️ 워밍업 통과 & 일일 한도(2건) 미달 시에만 홍보
                    if self._promo_handler and self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
                        try:
                            p_cnt = self._promo_handler()
                            results["promo_comments"] = p_cnt
                        except Exception as e:
                            logger.error(f"홍보 댓글 실행 에러: {e}")
                    else:
                        logger.info(f"🌱 [워밍업/한도 보호] 카르마 {self.health.get_karma()}/{WARMUP_KARMA_THRESHOLD} — 홍보 댓글 0건 유지")

                    time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

                    u_cnt = random.randint(2, 3)
                    u_res = self.organic.run_upvote_session(count=u_cnt)
                    results["upvotes"] = u_res.get("upvoted", 0)

                # 슬롯 완료 기록
                slot["executed"] = True
                slot["executed_at"] = get_now_kst_str()
                self._save_daily_plan(plan)
                results["status"] = "executed"
                results["executed_slot"] = slot_id
                break  # 한 번 호출에 1개 슬롯만 실행

        return results

    # ──────────────────────────────────────────
    # 🧠 종합 1회 사이클 (단독 실행 봇 / 수동 테스트용)
    # ──────────────────────────────────────────

    def run_safe_cycle(self) -> Dict[str, Any]:
        """단독 실행 시: 스크롤 + 업보트 + 비홍보댓글 + 홍보댓글 1회 종합 순차 실행"""
        results = {
            "timestamp": get_now_kst_str(),
            "service_id": self.service_id,
            "karma_checked": False,
            "upvotes": 0,
            "organic_comments": 0,
            "promo_comments": 0,
            "browsing_done": False,
            "skipped_reason": None,
        }

        now = get_now_kst()
        is_weekend = now.weekday() >= 5

        # 0. 건강 상태 확인
        health_status = self.health.get_status_summary()
        logger.info(f"📊 [Reddit 건강 상태] 카르마: {health_status['karma']}, "
                     f"워밍업: {health_status['is_warmup']}, "
                     f"경고: {health_status['alert_level']}, "
                     f"오늘 홍보: {health_status['today_promo']}, "
                     f"오늘 유기적: {health_status['today_organic']}, "
                     f"오늘 업보트: {health_status['today_upvotes']}")

        if health_status["in_cooldown"]:
            if health_status["alert_level"] >= 3:
                logger.warning("🚨 위험 레벨 쿨다운 중 — 모든 활동 중단")
                results["skipped_reason"] = f"cooldown_alert_{health_status['alert_level']}"
                return results

        # 1. 카르마 확인
        try:
            karma_info = self.driver.get_account_karma()
            if karma_info.get("karma", 0) > 0 or karma_info.get("username"):
                self.health.update_karma(karma_info["karma"], karma_info.get("username"))
                results["karma_checked"] = True
        except Exception as e:
            logger.warning(f"카르마 확인 실패: {e}")

        # 2. 피드 스크롤
        try:
            browse_duration = random.randint(40, 120)
            if is_weekend: browse_duration = int(browse_duration * 0.7)
            browse_res = self.organic.run_browse_session(duration_sec=browse_duration)
            results["browsing_done"] = browse_res.get("success", False)
        except Exception as e:
            logger.error(f"브라우징 세션 에러: {e}")

        time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

        # 3. 업보트 세션
        try:
            upvote_count = random.randint(3, 5)
            if is_weekend: upvote_count = max(1, int(upvote_count * 0.7))
            upvote_res = self.organic.run_upvote_session(count=upvote_count)
            results["upvotes"] = upvote_res.get("upvoted", 0)
        except Exception as e:
            logger.error(f"업보트 세션 에러: {e}")

        time.sleep(random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC))

        # 4. 비홍보 댓글 세션
        try:
            organic_count = random.randint(1, 2)
            organic_res = self.organic.run_organic_comment_session(count=organic_count)
            results["organic_comments"] = organic_res.get("commented", 0)
        except Exception as e:
            logger.error(f"유기적 댓글 세션 에러: {e}")

        time.sleep(random.randint(REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC))

        # 5. 홍보 댓글 (워밍업 통과 & 일일 한도 미달 시에만)
        if self._promo_handler and self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
            try:
                promo_count = self._promo_handler()
                results["promo_comments"] = promo_count
            except Exception as e:
                logger.error(f"홍보 댓글 세션 에러: {e}")
        else:
            if self.health.is_warmup_phase():
                results["skipped_reason"] = "warmup_phase"
                logger.info(f"🌱 워밍업 단계(카르마 {self.health.get_karma()}/{WARMUP_KARMA_THRESHOLD}) — 홍보 댓글 0건 유지")
            elif not self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
                results["skipped_reason"] = "daily_limit_or_cooldown"

        return results

    def get_status(self) -> Dict[str, Any]:
        """현재 오케스트레이터 상태 요약"""
        plan = self._get_or_create_daily_plan()
        return {
            **self.health.get_status_summary(),
            "promo_handler_set": self._promo_handler is not None,
            "today_plan": plan.get("slots", [])
        }
