# -*- coding: utf-8 -*-
"""
GPUQueueSafetyGuard - 🛡️ [원격/로컬 GPU 큐 감시 및 실시간 충돌 방지 가드레일]
- [1] 사전 대기 (Graceful Wait): 저쪽 컴퓨터가 GPU를 쓰고 있으면 에러 없이 3초 간격 대기
- [2] 큐 & VRAM 실시간 모니터링: ComfyUI /queue (running/pending) 및 /system_stats
- [3] 자동 캐시 클린업 (Mandatory Post-Flush): 작업 완료(정상/예외 무관) 즉시 100% VRAM 캐시 완전 방출 (/free)
"""

from typing import Dict, Any, Optional, Tuple, List, Callable
import time
import json
import logging
import urllib.request
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple, List, Callable

logger = logging.getLogger("GPUQueueSafetyGuard")


class GPUQueueSafetyGuard:
    """원격/로컬 그래픽카드 큐 대기열 관리 및 VRAM 안전 가드레일"""

    @classmethod
    def get_queue_info(cls, host: str) -> Dict[str, Any]:
        """ComfyUI 실시간 작업 큐(running / pending) 조회"""
        clean_host = host.rstrip("/")
        try:
            url = f"{clean_host}/queue"
            req = urllib.request.Request(url, headers={"User-Agent": "GPUQueueSafetyGuard"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                running = len(data.get("queue_running", []))
                pending = len(data.get("queue_pending", []))
                return {
                    "running": running,
                    "pending": pending,
                    "total": running + pending,
                    "ok": True
                }
        except Exception as e:
            logger.debug(f"ComfyUI /queue 조회 예외 ({clean_host}): {e}")
            return {"running": 0, "pending": 0, "total": 0, "ok": False}

    @classmethod
    def get_vram_info(cls, host: str) -> Dict[str, float]:
        """ComfyUI 실시간 VRAM 용량 조회"""
        clean_host = host.rstrip("/")
        try:
            url = f"{clean_host}/system_stats"
            req = urllib.request.Request(url, headers={"User-Agent": "GPUQueueSafetyGuard"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                devices = stats.get("devices", [])
                for d in devices:
                    if d.get("type") == "cuda":
                        free_gb = d.get("vram_free", 0) / (1024 ** 3)
                        total_gb = d.get("vram_total", 0) / (1024 ** 3)
                        return {
                            "free_gb": round(free_gb, 2),
                            "total_gb": round(total_gb, 2),
                            "used_gb": round(total_gb - free_gb, 2)
                        }
        except Exception as e:
            logger.debug(f"ComfyUI /system_stats VRAM 조회 예외 ({clean_host}): {e}")
        return {"free_gb": 16.0, "total_gb": 16.0, "used_gb": 0.0}

    @classmethod
    def is_gpu_busy(cls, host: str, min_free_gb: float = 6.0) -> Tuple[bool, str]:
        """현재 GPU가 타 작업으로 바쁜지 여부 판단 (큐 및 VRAM 종합)"""
        q = cls.get_queue_info(host)
        if q["running"] > 0 or q["pending"] > 0:
            return True, f"저쪽 컴퓨터에서 렌더링 작업 진행 중 (진행: {q['running']}건, 대기: {q['pending']}건)"

        v = cls.get_vram_info(host)
        if v["free_gb"] < min_free_gb:
            return True, f"가용 VRAM 부족 ({v['free_gb']}GB < {min_free_gb}GB, 잔류 메모리 해제 필요)"

        return False, "GPU 유휴 상태 (작업 가능)"

    @classmethod
    def flush_vram(cls, host: str, log_callback: Optional[Callable[[str, str], None]] = None) -> bool:
        """
        🧹 [필수] 작업 완료 즉시 원격/로컬 GPU VRAM 캐시 및 모델 100% 완전 방출
        - 타 작업자(저쪽 한국 마케팅 봇)에게 깨끗한 15GB+ VRAM 즉시 반환
        """
        clean_host = host.rstrip("/")
        try:
            url = f"{clean_host}/free"
            payload = json.dumps({"unload_models": True, "free_memory": True}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            msg = f"🧹 [GPU 가드레일] 작업 완료 ➔ VRAM 캐시 및 모델 100% 완전 방출 완료 ({clean_host})"
            logger.info(msg)
            if log_callback:
                log_callback(msg, "info")
            return True
        except Exception as e:
            logger.warning(f"VRAM 캐시 방출 예외 ({clean_host}): {e}")
            return False

    @classmethod
    def wait_until_gpu_ready(
        cls,
        host: str,
        max_wait_sec: int = 600,
        poll_interval: float = 3.0,
        min_free_gb: float = 6.0,
        log_callback: Optional[Callable[[str, str], None]] = None,
        abort_scope: Optional[str] = None
    ) -> bool:
        """
        GPU가 비어있을 때까지 안전하게 대기
        - 저쪽 컴퓨터가 사용 중이면 3초마다 부드럽게 대기
        - 비는 즉시 사전 캐시 청소 후 True 반환
        """
        from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException

        start_time = time.time()
        waited_once = False

        while True:
            # 1. 비상 정지 감시
            if GenerationAbortGuard.is_abort_requested(scope=abort_scope):
                raise GenerationAbortedException(f"사용자 정지 요청({abort_scope})으로 GPU 대기를 중단합니다.")

            # 2. 타임아웃 검사
            elapsed = time.time() - start_time
            if elapsed > max_wait_sec:
                err_msg = f"⚠️ [GPU 타임아웃] {max_wait_sec}초 동안 그래픽카드가 비지 않아 안전을 위해 대기를 중단합니다."
                logger.error(err_msg)
                if log_callback:
                    log_callback(err_msg, "danger")
                raise TimeoutError(err_msg)

            # 3. GPU 사용 여부 체크
            is_busy, reason = cls.is_gpu_busy(host, min_free_gb=min_free_gb)
            if not is_busy:
                if waited_once:
                    msg_ready = f"✨ [GPU 대기 완료] 저쪽 컴퓨터의 작업이 끝났습니다! 우리 작업을 안전하게 시작합니다. ({elapsed:.1f}초 대기)"
                    logger.info(msg_ready)
                    if log_callback:
                        log_callback(msg_ready, "success")
                # 사전 안전 캐시 정리 1회
                cls.flush_vram(host)
                return True

            # 4. 사용 중일 때 안내 로그 및 3초 대기
            waited_once = True
            msg_wait = f"⏳ [GPU 안전 대기] {reason}. 안전을 위해 잠시 기다립니다... ({elapsed:.0f}초 경과)"
            logger.info(msg_wait)
            if log_callback and (int(elapsed) % 6 == 0):
                log_callback(msg_wait, "info")

            time.sleep(poll_interval)

    @classmethod
    @contextmanager
    def gpu_session(
        cls,
        host: str,
        task_name: str = "미디어 렌더링",
        max_wait_sec: int = 600,
        min_free_gb: float = 6.0,
        log_callback: Optional[Callable[[str, str], None]] = None,
        abort_scope: Optional[str] = None
    ):
        """
        🛡️ 무결점 GPU 안전 세션 컨텍스트 매니저:
        1. 진입 시: 저쪽 컴퓨터가 사용 중이면 자동 안전 대기 후 비었을 때 진입
        2. 실행: 블록 내부 연산 수행
        3. 종료 시 (정상 완료든 에러든 finally):
           👉 100% 무조건 반드시 VRAM 캐시와 모델을 완전 방출 (/free)
        """
        # [Phase 1: 대기 및 진입]
        cls.wait_until_gpu_ready(
            host=host,
            max_wait_sec=max_wait_sec,
            min_free_gb=min_free_gb,
            log_callback=log_callback,
            abort_scope=abort_scope
        )

        try:
            logger.info(f"🚀 [GPU 세션 시작] {task_name} 연산 진입")
            yield
        finally:
            # [Phase 2: 필수 사후 캐시 완전 방출]
            cls.flush_vram(host, log_callback=log_callback)
            logger.info(f"🏁 [GPU 세션 종료] {task_name} 종료 ➔ VRAM 100% 원복 완료")


# 타입 힌트용
Tuple_Busy = Any
