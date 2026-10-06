"""
TelegramStealthInviter - 🕵️ 서브폰 계정 기반 Telethon 스텔스 초대 엔진
[전략] 서브폰 = 로켓 부스터. 잘려도 되는 계정으로 초기 씨앗 멤버 확보
[안전] 하루 3~5명 극초저속 + 15~30분 불규칙 딜레이 + 영구 장부 중복 방지
[분리] K-Market / EasyTax 각각 독립 Telethon 세션 & 독립 초대 장부
"""

import os
import json
import random
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Set, Optional

from config import BASE_DIR, DATA_DIR, get_now_kst

logger = logging.getLogger("TelegramStealthInviter")

DAILY_LIMIT = 5          # 브랜드당 하루 최대 초대 인원 (절대 안전 캡)
SCRAPE_LIMIT = 200       # 타깃 그룹에서 한 번에 조회할 멤버 수

TARGET_GROUPS_FILE = DATA_DIR / "telegram_target_groups.json"


class TelegramStealthInviter:
    """
    서브폰 Telethon 기반 극초저속 스텔스 초대기
    K-Market / EasyTax 각각 독립 세션 & 독립 장부로 100% 분리
    """

    def __init__(
        self,
        brand: str = "kmarket",
        api_id: int = None,
        api_hash: str = None,
        session_name: str = None,
        db_path: Path = None
    ):
        self.brand = brand.lower()

        if self.brand == "easytax":
            self.api_id       = api_id   or int(os.getenv("EASYTAX_TELETHON_API_ID",  os.getenv("TELEGRAM_API_ID", "0")))
            self.api_hash     = api_hash or os.getenv("EASYTAX_TELETHON_API_HASH", os.getenv("TELEGRAM_API_HASH", ""))
            self.session_name = session_name or "easytax_worker"
            # 우리 그룹: 유저네임(예: easytax_korea_official) 또는 Chat ID 문자열
            self.target_chat  = os.getenv("EASYTAX_TELEGRAM_GROUP_USERNAME") or os.getenv("EASYTAX_TELEGRAM_CHAT_ID", "")
        else:
            self.api_id       = api_id   or int(os.getenv("KMARKET_TELETHON_API_ID",  os.getenv("TELEGRAM_API_ID", "0")))
            self.api_hash     = api_hash or os.getenv("KMARKET_TELETHON_API_HASH", os.getenv("TELEGRAM_API_HASH", ""))
            self.session_name = session_name or "kmarket_worker"
            self.target_chat  = os.getenv("KMARKET_TELEGRAM_GROUP_USERNAME") or os.getenv("KMARKET_TELEGRAM_CHAT_ID", "")

        self.db_path = db_path or (DATA_DIR / "telegram_stealth_invites.db")
        self._init_db()
        self._load_target_groups()

    # ─── DB ─────────────────────────────────────────────────
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS invite_history (
                user_id      TEXT NOT NULL,
                brand        TEXT NOT NULL,
                username     TEXT,
                first_name   TEXT,
                source_group TEXT,
                invited_at   TIMESTAMP,
                PRIMARY KEY (user_id, brand)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_log (
                brand       TEXT NOT NULL,
                log_date    TEXT NOT NULL,
                count       INTEGER DEFAULT 0,
                PRIMARY KEY (brand, log_date)
            )
        """)
        conn.commit()
        conn.close()

    def _load_target_groups(self):
        if TARGET_GROUPS_FILE.exists():
            with open(TARGET_GROUPS_FILE, "r", encoding="utf-8") as f:
                self.target_groups = json.load(f)
        else:
            self.target_groups = []

    # ─── 카운터 ──────────────────────────────────────────────
    def get_today_count(self) -> int:
        today = get_now_kst().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT count FROM daily_log WHERE brand=? AND log_date=?", (self.brand, today))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

    def _increment_count(self):
        today = get_now_kst().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_log (brand, log_date, count) VALUES (?,?,1)
            ON CONFLICT(brand, log_date) DO UPDATE SET count=count+1
        """, (self.brand, today))
        conn.commit()
        conn.close()

    def get_invited_ids(self) -> Set[str]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM invite_history WHERE brand=?", (self.brand,))
        rows = cur.fetchall()
        conn.close()
        return {r[0] for r in rows}

    def _record_invite(self, user_id: str, username: str, first_name: str, source: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO invite_history (user_id, brand, username, first_name, source_group, invited_at)
            VALUES (?,?,?,?,?,?)
        """, (str(user_id), self.brand, username, first_name, source, get_now_kst().isoformat()))
        conn.commit()
        conn.close()

    # ─── 딜레이 계산 ─────────────────────────────────────────
    def get_delay_seconds(self) -> int:
        """
        인간 모방 불규칙 딜레이:
        70% → 15~30분 (일반 간격)
        20% → 30~60분 (커피 브레이크)
        10% → 1~2시간 (장기 휴식)
        """
        r = random.random()
        if r < 0.70:
            return random.randint(900, 1800)
        elif r < 0.90:
            delay = random.randint(1800, 3600)
            logger.info(f"☕ [{self.brand.upper()}] 커피 브레이크: {delay//60}분")
            return delay
        else:
            delay = random.randint(3600, 7200)
            logger.info(f"😴 [{self.brand.upper()}] 장기 휴식: {delay//60}분")
            return delay

    # ─── 1회 초대 사이클 ─────────────────────────────────────
    def execute_invite_cycle(self, source_group_username: str = None) -> Dict[str, Any]:
        """타깃 그룹에서 1명을 골라 우리 방으로 안전 초대"""

        # 일일 캡 체크
        today_count = self.get_today_count()
        if today_count >= DAILY_LIMIT:
            return {
                "success": True, "status": "DAILY_LIMIT_REACHED",
                "brand": self.brand, "today_count": today_count,
                "message": f"[{self.brand}] 오늘 한도 {DAILY_LIMIT}명 달성 → 오늘 종료"
            }

        # 세션 파일 존재 여부 확인
        session_path = BASE_DIR / f"{self.session_name}.session"
        if not session_path.exists():
            logger.warning(
                f"⚠️  [{self.brand.upper()}] 서브폰 세션 없음: '{self.session_name}.session'\n"
                f"    → python setup_telethon_session.py --brand {self.brand}"
            )
            return {"success": False, "status": "NO_SESSION", "brand": self.brand}

        # 타깃 그룹 결정 (파라미터 우선, 없으면 라운드로빈)
        if not source_group_username:
            active = [g for g in self.target_groups if g.get("is_active", True)]
            if not active:
                return {"success": False, "status": "NO_GROUPS", "brand": self.brand}
            target_group = sorted(active, key=lambda x: x.get("last_scraped_at") or "")[0]
            source_group_username = target_group.get("username", "")

        already_invited = self.get_invited_ids()

        try:
            from telethon.sync import TelegramClient
            from telethon.tl.functions.channels import InviteToChannelRequest
            from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusLastWeek

            with TelegramClient(str(BASE_DIR / self.session_name), self.api_id, self.api_hash) as client:
                from telethon.errors import (
                    UserPrivacyRestrictedError,
                    UserAlreadyParticipantError,
                    UserNotMutualContactError,
                    PeerFloodError,
                    FloodWaitError
                )

                target_entity_name = "kmarket_official" if self.brand == "kmarket" else "easytax_official"
                target_chat_entity = client.get_entity(target_entity_name)

                # 타깃 그룹에서 최근 활성 대화 유저 추출 (멤버 숨김 그룹도 100% 수집 가능)
                candidates = []
                try:
                    for msg in client.iter_messages(source_group_username, limit=100):
                        sender = msg.sender
                        if not sender or not hasattr(sender, "id"):
                            continue
                        uid = str(sender.id)
                        if uid in already_invited:
                            continue
                        if getattr(sender, "bot", False) or getattr(sender, "deleted", False):
                            continue
                        if sender.id not in [c.id for c in candidates]:
                            candidates.append(sender)
                        if len(candidates) >= 15:
                            break
                except Exception as scrape_err:
                    logger.warning(f"⚠️ [{self.brand.upper()}] @{source_group_username} 메시지 수집 오류: {scrape_err}")

                # 폴백: get_participants 시도
                if not candidates:
                    try:
                        participants = client.get_participants(source_group_username, limit=SCRAPE_LIMIT)
                        for p in participants:
                            uid = str(p.id)
                            if uid in already_invited:
                                continue
                            if getattr(p, "bot", False) or getattr(p, "deleted", False):
                                continue
                            candidates.append(p)
                            if len(candidates) >= 10:
                                break
                    except Exception:
                        pass

                if not candidates:
                    return {
                        "success": True, "status": "NO_CANDIDATE",
                        "brand": self.brand, "source": source_group_username,
                        "message": f"[{self.brand}] @{source_group_username} 에서 신규 후보 없음"
                    }

                # 최대 5명의 후보 중 프라이버시 제한 없는 유저 1명 안전 초대
                invited_success = False
                last_err = None
                for candidate in candidates:
                    fname = getattr(candidate, "first_name", "Friend") or "Friend"
                    uname = getattr(candidate, "username", "") or ""
                    uid_str = str(candidate.id)

                    try:
                        client(InviteToChannelRequest(target_chat_entity, [candidate]))
                        self._record_invite(uid_str, uname, fname, source_group_username)
                        self._increment_count()
                        invited_success = True

                        logger.info(
                            f"🎉 [{self.brand.upper()}] 스텔스 초대 성공: {fname}(@{uname}) "
                            f"← @{source_group_username} │ 오늘 {self.get_today_count()}/{DAILY_LIMIT}명"
                        )
                        return {
                            "success": True, "status": "INVITED",
                            "brand": self.brand,
                            "invited_user": fname, "username": uname,
                            "source_group": source_group_username,
                            "today_count": self.get_today_count()
                        }
                    except (UserPrivacyRestrictedError, UserNotMutualContactError):
                        logger.info(f"🔒 [{self.brand.upper()}] {fname}(@{uname}) 유저의 초대 프라이버시 제한 -> 다음 후보 진행")
                        self._record_invite(uid_str, uname, fname, f"{source_group_username}_privacy_restricted")
                        continue
                    except UserAlreadyParticipantError:
                        logger.info(f"ℹ️ [{self.brand.upper()}] {fname}(@{uname}) 유저는 이미 방에 참여 중 -> 장부 기록 후 다음 후보")
                        self._record_invite(uid_str, uname, fname, f"{source_group_username}_already_member")
                        continue
                    except (PeerFloodError, FloodWaitError) as flood_e:
                        logger.warning(f"⚠️ [{self.brand.upper()}] 텔레그램 쿨다운 감지: {flood_e}")
                        return {"success": False, "status": "FLOOD_WAIT", "brand": self.brand, "error": str(flood_e)}
                    except Exception as ex:
                        last_err = ex
                        logger.warning(f"⚠️ [{self.brand.upper()}] 유저 {fname} 초대 스킵: {ex}")
                        self._record_invite(uid_str, uname, fname, f"{source_group_username}_skipped")
                        continue

                if not invited_success:
                    return {
                        "success": False, "status": "ALL_CANDIDATES_RESTRICTED",
                        "brand": self.brand, "error": f"조회된 후보들의 프라이버시 설정으로 스킵됨 ({last_err})"
                    }

        except Exception as e:
            logger.error(f"❌ [{self.brand.upper()}] 스텔스 초대 오류: {e}")
            return {"success": False, "status": "ERROR", "brand": self.brand, "error": str(e)}

    # ─── 대시보드 통계 ───────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        session_ready = (BASE_DIR / f"{self.session_name}.session").exists()
        return {
            "brand": self.brand,
            "today_count": self.get_today_count(),
            "daily_limit": DAILY_LIMIT,
            "total_invited": len(self.get_invited_ids()),
            "session_ready": session_ready,
            "session_name": self.session_name
        }
