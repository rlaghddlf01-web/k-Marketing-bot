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
from typing import Optional

logger = logging.getLogger("GenerationAbortGuard")


class GenerationAbortedException(Exception):
    """사용자 또는 시스템에 의해 작업이 즉각 중단(Abort)되었을 때 발생하는 예외"""
    pass


class GenerationAbortGuard:
    _abort_event = threading.Event()
    _lock = threading.Lock()

    @classmethod
    def trigger_global_stop(cls, host: str = "http://127.0.0.1:8188", reason: str = "대시보드 사용자 정지 요청"):
        """대시보드 정지 신호 수신 즉시 ComfyUI GPU KSampler 인터럽트 + 큐 삭제 + Abort 플래그 설정"""
        with cls._lock:
            cls._abort_event.set()

        logger.warning(f"🛑 [GenerationAbortGuard] 전역 중단(Abort) 활성화: {reason}")

        # 1. ComfyUI 현재 실행 중인 KSampler 긴급 중단
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

        # 2. ComfyUI 대기 큐 전체 삭제
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

    @classmethod
    def reset_stop_flag(cls):
        """새로운 작업 시작 시 중단 플래그 리셋"""
        with cls._lock:
            cls._abort_event.clear()
        logger.info("🟢 [GenerationAbortGuard] 전역 중단 플래그 리셋 완료 (새 작업 준비)")

    @classmethod
    def is_abort_requested(cls) -> bool:
        """현재 중단 신호가 활성화되어 있는지 확인"""
        return cls._abort_event.is_set()

    @classmethod
    def assert_not_aborted(cls):
        """중단 신호가 활성화되어 있으면 즉시 예외를 발생시켜 루프 즉시 탈출"""
        if cls._abort_event.is_set():
            raise GenerationAbortedException("작업이 대시보드 정지 요청에 의해 즉시 중단되었습니다.")
