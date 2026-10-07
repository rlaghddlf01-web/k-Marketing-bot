# -*- coding: utf-8 -*-
"""
UnmannedStateManager - 🛡️ [24시간 무인가동 상태 불멸 보존 관리자]
================================================================================
• 핵심 기능:
  - 서버 재부팅, 코드 수정 후 재실행, PC 재시작 시에도 무인가동 상태가 풀리지 않고 100% 자동 복구
  - 원자적(Atomic) JSON 저장으로 갑작스러운 프로세스 종료에도 파일 손상 0% 보장
  - 보존 대상:
    1) 20대 독립 채널 자율 공장 상태 (running_channels)
    2) K-Market 종합 무인봇 상태 (kmarket_running)
    3) EasyTax 종합 무인봇 상태 (easytax_running)
    4) 8대 황금 타깃 무인 예약 데몬 상태 (golden_batch_daemon_running)
    5) 텔레그램 24시간 17개국어 AI 커뮤니티 매니저 (telegram_manager_running)
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from config import DATA_DIR, get_now_kst_str

logger = logging.getLogger("UnmannedStateManager")

UNMANNED_STATE_FILE = DATA_DIR / "unmanned_state.json"

DEFAULT_CHANNELS = {
    "kmarket_shorts": False, "kmarket_tiktok": False, "kmarket_cardnews": False,
    "kmarket_reddit": False, "kmarket_briefing": False, "kmarket_fb_groups": False,
    "kmarket_seo": False, "kmarket_pdf": False, "kmarket_blog": False, "kmarket_threads": False,
    "easytax_shorts": False, "easytax_tiktok": False, "easytax_cardnews": False,
    "easytax_reddit": False, "easytax_briefing": False, "easytax_fb_groups": False,
    "easytax_seo": False, "easytax_pdf": False, "easytax_blog": False, "easytax_threads": False,
}

DEFAULT_GOLDEN_DAEMON = {
    "kmarket": False,
    "easytax": False,
    "all": False
}

DEFAULT_TELEGRAM_MANAGER = {
    "kmarket": False,
    "easytax": False
}


class UnmannedStateManager:
    """무인가동 영구 보존 및 자동 복구 관리자"""

    @classmethod
    def load_state(cls) -> Dict[str, Any]:
        """저장된 무인가동 상태 로드 (없거나 손상 시 기본값 반환)"""
        if not UNMANNED_STATE_FILE.exists():
            return cls._get_default_state()
        try:
            with open(UNMANNED_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            default = cls._get_default_state()
            for key in ["running_channels", "golden_batch_daemon_running", "telegram_manager_running"]:
                if key in state and isinstance(state[key], dict):
                    merged = dict(default[key])
                    merged.update(state[key])
                    state[key] = merged
                else:
                    state[key] = default[key]
            return state
        except Exception as e:
            logger.warning(f"무인가동 상태 파일 로드 예외 ({e}), 기본값 사용")
            return cls._get_default_state()

    @classmethod
    def save_state(cls, state: Dict[str, Any]) -> bool:
        """원자적(Atomic) 쓰기로 상태 저장"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            state["last_updated"] = get_now_kst_str()
            temp_file = UNMANNED_STATE_FILE.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            temp_file.replace(UNMANNED_STATE_FILE)
            logger.debug("💾 [UnmannedStateManager] 무인가동 상태 저장 완료")
            return True
        except Exception as e:
            logger.error(f"무인가동 상태 저장 실패: {e}")
            return False

    @classmethod
    def _get_default_state(cls) -> Dict[str, Any]:
        return {
            "running_channels": dict(DEFAULT_CHANNELS),
            "kmarket_running": False,
            "easytax_running": False,
            "golden_batch_daemon_running": dict(DEFAULT_GOLDEN_DAEMON),
            "telegram_manager_running": dict(DEFAULT_TELEGRAM_MANAGER),
            "last_updated": get_now_kst_str()
        }

    @classmethod
    def update_channel(cls, module_name: str, is_running: bool):
        """단일 채널 상태 갱신 및 즉시 저장"""
        state = cls.load_state()
        state["running_channels"][module_name] = is_running
        cls.save_state(state)

    @classmethod
    def update_channels_batch(cls, channel_names: List[str], is_running: bool):
        """복수 채널 일괄 상태 갱신 및 즉시 저장"""
        state = cls.load_state()
        for ch in channel_names:
            if ch in state["running_channels"]:
                state["running_channels"][ch] = is_running
        cls.save_state(state)

    @classmethod
    def update_bot(cls, brand: str, is_running: bool):
        """종합 봇 상태 갱신 (kmarket, easytax, all)"""
        state = cls.load_state()
        if brand in ["kmarket", "all"]:
            state["kmarket_running"] = is_running
        if brand in ["easytax", "all"]:
            state["easytax_running"] = is_running
        cls.save_state(state)

    @classmethod
    def update_golden_daemon(cls, brand: str, is_running: bool):
        """8대 황금 타깃 무인 예약 데몬 상태 갱신"""
        state = cls.load_state()
        state["golden_batch_daemon_running"][brand] = is_running
        cls.save_state(state)

    @classmethod
    def update_telegram_manager(cls, brand: str, is_running: bool):
        """텔레그램 AI 커뮤니티 매니저 상태 갱신"""
        state = cls.load_state()
        state["telegram_manager_running"][brand] = is_running
        cls.save_state(state)
