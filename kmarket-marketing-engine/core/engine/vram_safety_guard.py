# -*- coding: utf-8 -*-
"""
VRAMSafetyGuard - 🛡️ [GPU VRAM 안전 차단 및 과열 방지 가드레일]
- [1] 사전 진입 게이트: 비디오 렌더링 전 순수 가용 VRAM(최소 11.5GB+) 실시간 검증
- [2] 런타임 킬스위치: 모델 적재 시 CPU 대량 오프로드 감지 시 0.1초 만에 즉시 작업 중단(Interrupt)
- [3] 대시보드 연동: GPU 과열 및 저속 연산(1시간 이상 지연) 원천 차단 및 명확한 시각적 알림
"""

import json
import logging
import subprocess
import urllib.request
from typing import Dict, Any, Optional, Tuple, Callable

logger = logging.getLogger("VRAMSafetyGuard")


class VRAMSafetyException(RuntimeError):
    """VRAM 부족 및 GPU 과열 방지 안전 차단 예외"""
    pass


class VRAMSafetyGuard:
    """GPU VRAM 사전 검증 및 실시간 런타임 감시 엔진"""

    MIN_S2V_VRAM_GB = 11.5  # Wan 2.2 S2V 14B 모델 VRAM 탑재를 위한 최소 가용 메모리 (GB)

    @classmethod
    def get_vram_info(cls, host: str = "http://127.0.0.1:8188") -> Dict[str, float]:
        """
        현재 GPU VRAM 실시간 용량 조회 (ComfyUI system_stats 우선, nvidia-smi 백업)
        반환: {'free_gb': float, 'total_gb': float, 'used_gb': float}
        """
        # 1차 시도: ComfyUI /system_stats API
        try:
            req = urllib.request.Request(f"{host}/system_stats", headers={"User-Agent": "VRAMSafetyGuard"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                devices = stats.get("devices", [])
                for d in devices:
                    if d.get("type") == "cuda":
                        free_b = d.get("vram_free", 0)
                        total_b = d.get("vram_total", 0)
                        if total_b > 0:
                            free_gb = free_b / (1024 ** 3)
                            total_gb = total_b / (1024 ** 3)
                            return {
                                "free_gb": round(free_gb, 2),
                                "total_gb": round(total_gb, 2),
                                "used_gb": round(total_gb - free_gb, 2),
                                "source": "comfyui"
                            }
        except Exception as e:
            logger.debug(f"ComfyUI system_stats 조회 실패 (nvidia-smi 백업 전환): {e}")

        # 2차 시도: nvidia-smi CLI
        try:
            cmd = ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,nounits,noheader"]
            out = subprocess.check_output(cmd, text=True, timeout=3).strip()
            if out:
                free_mb, total_mb = [float(x.strip()) for x in out.split(",")]
                free_gb = free_mb / 1024.0
                total_gb = total_mb / 1024.0
                return {
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(total_gb - free_gb, 2),
                    "source": "nvidia-smi"
                }
        except Exception as e:
            logger.warning(f"nvidia-smi 조회 예외: {e}")

        # 알 수 없는 경우 보수적 반환
        return {"free_gb": 0.0, "total_gb": 16.0, "used_gb": 16.0, "source": "unknown"}

    @classmethod
    def assert_vram_headroom(
        cls,
        min_free_gb: Optional[float] = None,
        host: str = "http://127.0.0.1:8188",
        auto_free_fn: Optional[Callable[[], None]] = None
    ) -> Dict[str, float]:
        """
        [1단계: 사전 진입 게이트]
        비디오 렌더링 시작 전 VRAM 확보 여부 전수 검사.
        미달 시 auto_free_fn을 1회 호출해 잔류 모델을 비우고 재확인.
        그래도 미달 시 VRAMSafetyException을 발생시켜 작업 즉각 중단.
        """
        threshold = min_free_gb or cls.MIN_S2V_VRAM_GB
        info = cls.get_vram_info(host=host)

        if info["free_gb"] < threshold and auto_free_fn:
            logger.info(f"🧹 [VRAM 가드레일] 가용 VRAM 부족 감지 ({info['free_gb']}GB < {threshold}GB). 자동 메모리 비우기 1회 실행...")
            try:
                auto_free_fn()
            except Exception as e:
                logger.warning(f"자동 VRAM 비우기 실패: {e}")
            import time
            time.sleep(1.0)
            info = cls.get_vram_info(host=host)

        if info["free_gb"] < threshold:
            err_msg = (
                f"🚨 [VRAM 안전 차단] 텍스트 인코더(UMT5) 잔류 등으로 가용 VRAM이 부족합니다 "
                f"(현재 {info['free_gb']:.2f}GB / 안전 기준 {threshold:.1f}GB 이상). "
                "GPU 과열 및 비정상 지연(스텝당 4분, 총 1시간 20분 이상)을 방지하기 위해 "
                "작업을 즉시 안전하게 중단했습니다. (ComfyUI 메모리 클린업 필요)"
            )
            logger.error(err_msg)
            raise VRAMSafetyException(err_msg)

        logger.info(f"🛡️ [VRAM 안전 통과] 현재 가용 VRAM {info['free_gb']:.2f}GB / {info['total_gb']:.2f}GB (안전 기준 {threshold:.1f}GB 충족)")
        return info

    @classmethod
    def trigger_emergency_interrupt(cls, host: str = "http://127.0.0.1:8188"):
        """[비상 정지] ComfyUI 연산 즉시 중단 및 VRAM 강제 해제"""
        try:
            req_int = urllib.request.Request(
                f"{host}/interrupt",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_int, timeout=3) as resp:
                pass
            logger.info("🛑 [VRAM 가드레일] ComfyUI /interrupt 긴급 신호 발송 완료")
        except Exception as e:
            logger.warning(f"비상 interrupt 실패: {e}")

        try:
            req_free = urllib.request.Request(
                f"{host}/free",
                data=json.dumps({"unload_models": True, "free_memory": True}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_free, timeout=3) as resp:
                pass
            logger.info("🧹 [VRAM 가드레일] ComfyUI /free 모델 및 캐시 완전 방출 완료")
        except Exception as e:
            logger.warning(f"비상 free 실패: {e}")

    @classmethod
    def check_log_line_for_violation(cls, line: str) -> Tuple[bool, str]:
        """
        [2단계: 런타임 킬스위치]
        ComfyUI 로그 라인 검사: S2V 모델의 CPU 대량 오프로드 감지 시 True 및 사유 반환
        """
        # 패턴: loaded partially; 0.00 MB usable, 0.00 MB loaded, 12471.75 MB offloaded
        if "loaded partially" in line and "offloaded" in line:
            # offloaded 용량 확인
            try:
                import re
                m_off = re.search(r"([\d\.]+)\s*MB offloaded", line)
                m_load = re.search(r"([\d\.]+)\s*MB loaded", line)
                if m_off and m_load:
                    off_mb = float(m_off.group(1))
                    load_mb = float(m_load.group(1))
                    total_model_mb = off_mb + load_mb
                    # 거대 비디오 모델(Wan2.2 S2V 12GB 등, 5000MB 초과 모델)에 대한 킬스위치
                    if total_model_mb > 5000.0:
                        # 4,000MB(4GB) 이상 심각하게 CPU로 튕겨 나갔거나 GPU 적재량이 4,000MB 미만인 치명적 경우에만 차단
                        # (10GB 이상 정상 GPU 적재 시 2GB 미만의 버퍼 오프로드는 16GB GPU의 정상 고속 동작 대역입니다)
                        if off_mb > 4000.0 or load_mb < 4000.0:
                            reason = f"비디오 모델의 {off_mb:.1f}MB가 RAM으로 심각하게 밀려남 감지 (GPU 적재량: {load_mb:.1f}MB, 전체 크기: {total_model_mb:.1f}MB)"
                            return True, reason
            except Exception as e:
                logger.warning(f"VRAM 로그 라인 파싱 예외: {e}")
                return False, ""

        return False, ""

    @classmethod
    def get_latest_comfyui_log_path(cls) -> Optional[str]:
        """ComfyUI의 현재 활성 실행 로그 파일 경로 탐색"""
        import os
        import glob
        from pathlib import Path

        # 1. 표준 출력 로그 파일 (ComfyProcessManager 관리 경로)
        direct = Path(r"D:\ComfyUI_Wan_Engine\comfyui_stdout.log")
        if direct.exists() and direct.stat().st_size > 0:
            return str(direct)

        # 2. Antigravity task 실행 로그
        task_logs = glob.glob(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\*\.system_generated\tasks\task-*.log")
        recent = sorted(task_logs, key=os.path.getmtime, reverse=True)
        for p in recent[:10]:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
                    if "To see the GUI go to: http://127.0.0.1:8188" in content or "ComfyUI\\main.py" in content:
                        return p
            except Exception:
                pass

        return None
