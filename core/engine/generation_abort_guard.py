# -*- coding: utf-8 -*-
"""
GenerationAbortGuard - 🛑 [대시보드 비상 정지 및 GPU 인터럽트 킬스위치 가드레일]
- 대시보드의 [정지] / [전체 정지] 버튼 클릭 시 0.1초 만에 ComfyUI /interrupt 및 큐 삭제 실행
- 전역 Abort Event로 모든 백그라운드 생성 파이프라인(카드뉴스, 숏폼 등)의 슬라이드 루프 즉각 탈출
- Fallback 예외 은폐 방지: 중단 신호 발생 시 Fallback 이미지로 때우며 루프를 계속 도는 현상 원천 차단
"""

import json
import logging
import threading
import urllib.request
from typing import Optional, Dict

logger = logging.getLogger("GenerationAbortGuard")


class GenerationAbortedException(Exception):
    """사용자 또는 시스템에 의해 작업이 즉각 중단(Abort)되었을 때 발생하는 예외"""
    pass


class GenerationAbortGuard:
    """
    🛑 [대시보드 정지 킬스위치 및 스코프 격리 가드레일]
    - global 스코프: 대시보드 마스터 정지(/api/all/stop, /api/emergency/stop)
    - channel_xxx 스코프: 특정 단일 채널(레딧, 블로그 등) 독립 정지 (타 팩토리 작업 간섭 원천 차단)
    - factory_xxx 스코프: 특정 숏폼/카드뉴스 제작 작업 독립 정지
    """
    _global_abort_event = threading.Event()
    _scoped_events: Dict[str, threading.Event] = {}
    _lock = threading.Lock()

    @classmethod
    def trigger_global_stop(cls, host: str = "http://127.0.0.1:8188", reason: str = "대시보드 사용자 전역 정지"):
        """대시보드 전역 정지: 모든 스코프 및 GPU 즉시 중단"""
        with cls._lock:
            cls._global_abort_event.set()
            for ev in cls._scoped_events.values():
                ev.set()

        logger.warning(f"🛑 [GenerationAbortGuard] 전역 중단(Global Abort) 활성화: {reason}")
        cls._interrupt_comfyui(host=host)

    @classmethod
    def trigger_stop(
        cls,
        scope: str = "global",
        host: str = "http://127.0.0.1:8188",
        reason: str = "채널/작업 정지",
        interrupt_gpu: bool = False
    ):
        """특정 스코프(단일 채널 또는 특정 팩토리 작업)만 격리 중단 (타 채널/작업 영향 0%)"""
        if not scope or scope == "global":
            cls.trigger_global_stop(host=host, reason=reason)
            return

        with cls._lock:
            if scope not in cls._scoped_events:
                cls._scoped_events[scope] = threading.Event()
            cls._scoped_events[scope].set()

        logger.warning(f"🛑 [GenerationAbortGuard] 스코프 격리 중단 활성화 [{scope}]: {reason}")
        if interrupt_gpu:
            cls._interrupt_comfyui(host=host)

    @classmethod
    def reset_stop_flag(cls, scope: Optional[str] = None):
        """새로운 작업 시작 시 중단 플래그 리셋"""
        with cls._lock:
            if scope is None or scope == "global":
                cls._global_abort_event.clear()
                cls._scoped_events.clear()
                logger.info("🟢 [GenerationAbortGuard] 전역 및 모든 스코프 중단 플래그 리셋 완료 (새 작업 준비)")
            else:
                if scope in cls._scoped_events:
                    cls._scoped_events[scope].clear()
                logger.info(f"🟢 [GenerationAbortGuard] [{scope}] 스코프 중단 플래그 리셋 완료")

    @classmethod
    def is_abort_requested(cls, scope: Optional[str] = None) -> bool:
        """현재 중단 신호가 활성화되어 있는지 확인 (전역 중단 또는 해당 스코프 중단)"""
        if cls._global_abort_event.is_set():
            return True
        if scope:
            with cls._lock:
                # 1. 스코프 완전 일치 검사
                if scope in cls._scoped_events and cls._scoped_events[scope].is_set():
                    return True
                # 2. 계층형 스코프 상속 검사 (예: brand_kmarket 중단 시 brand_kmarket:xxx 자식도 중단)
                for reg_scope, ev in cls._scoped_events.items():
                    if ev.is_set():
                        if scope == reg_scope:
                            return True
                        if scope.startswith(f"{reg_scope}:") or scope.startswith(f"{reg_scope}/") or scope.startswith(f"{reg_scope}_"):
                            return True
        return False

    @classmethod
    def assert_not_aborted(cls, scope: Optional[str] = None):
        """중단 신호가 활성화되어 있으면 즉시 예외를 발생시켜 루프 즉시 탈출"""
        if cls.is_abort_requested(scope=scope):
            raise GenerationAbortedException(f"작업이 정지 요청({scope or '전역'})에 의해 즉시 안전하게 중단되었습니다.")

    @classmethod
    def _interrupt_comfyui(cls, host: str = "http://127.0.0.1:8188"):
        """ComfyUI 현재 실행 중인 KSampler 긴급 중단 및 큐 삭제"""
        try:
            req_int = urllib.request.Request(
                f"{host}/interrupt",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_int, timeout=2) as resp:
                pass
            logger.info("🛑 [GenerationAbortGuard] ComfyUI /interrupt 긴급 신호 발송 완료")
        except Exception as e:
            logger.debug(f"ComfyUI interrupt 신호 예외 (Comfy 미실행 시 무시): {e}")

        try:
            req_queue = urllib.request.Request(
                f"{host}/queue",
                data=json.dumps({"clear": True}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_queue, timeout=2) as resp:
                pass
            logger.info("🧹 [GenerationAbortGuard] ComfyUI /queue 전체 삭제 완료")
        except Exception as e:
            logger.debug(f"ComfyUI queue 삭제 예외 (무시): {e}")
