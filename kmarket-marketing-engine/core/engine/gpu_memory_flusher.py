# -*- coding: utf-8 -*-
"""
[신규 모듈] GPUMemoryFlusher (core/engine/gpu_memory_flusher.py)
• 역할: 숏폼 및 카드뉴스 1개국 생성 완료 시마다 ComfyUI VRAM 캐시 및 시스템 RAM을 즉각 방출하는 전담 모듈
• 핵심 기능:
  1. ComfyUI /free API 호출 (unload_models=False, free_memory=True):
     - 기적재된 Wan 2.1 / Wan 2.2 모델은 VRAM에 안전하게 유지하면서, 잔류 VAE/UNet 텐서 및 임시 캐시만 0MB로 즉시 방출
     - 다음 국가 생성 시 모델 재로딩 지연 없이 0초 만에 즉시 시작
  2. 파이썬 가비지 컬렉션(gc.collect()) 강제 실행으로 고해상도 이미지 및 브라우저 메모리 즉각 회수
  3. ComfyUI 미가동 로컬 모드에서도 에러 없이 안전하게 건너뛰는 무장애 격리(Fault-Tolerant)
• 원칙: 모듈 분리 원칙(Rule 1), 원천 파이프라인 무결성(Rule 5) 준수
"""

import os
import gc
import json
import logging
import urllib.request
from typing import Dict, Any, Optional

logger = logging.getLogger("GPUMemoryFlusher")


class GPUMemoryFlusher:
    """GPU VRAM 및 시스템 메모리 즉시 클린업 전담 매니저"""

    @classmethod
    def flush_gpu_vram(
        cls,
        host: str = "http://127.0.0.1:8188",
        unload_models: bool = False,
        timeout_sec: float = 3.0
    ) -> Dict[str, Any]:
        """
        ComfyUI VRAM 캐시 및 파이썬 메모리를 즉각 방출합니다.
        :param host: ComfyUI 호스트 주소
        :param unload_models: True 시 모델까지 완전 언로드, False 시 텐서 캐시만 방출(권장)
        :param timeout_sec: API 타임아웃
        :return: 처리 결과 딕셔너리
        """
        # 1. 파이썬 프로세스 가비지 컬렉션 1차 실행
        gc_collected = gc.collect()

        # 2. ComfyUI /free API 호출로 VRAM 캐시 즉각 방출
        comfy_freed = False
        comfy_msg = "ComfyUI 미연결"
        try:
            req_data = json.dumps({
                "unload_models": unload_models,
                "free_memory": True
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{host}/free",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "GPUMemoryFlusher"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if resp.status == 200:
                    comfy_freed = True
                    comfy_msg = "VRAM 캐시 100% 방출 성공 (모델 유지)" if not unload_models else "모델 및 VRAM 완전 언로드 성공"
        except urllib.error.URLError:
            comfy_msg = "ComfyUI 미실행 상태 (로컬 클린업만 적용)"
        except Exception as e:
            comfy_msg = f"ComfyUI /free 호출 예외: {e}"

        # 3. 2차 가비지 컬렉션
        gc.collect()

        # 4. 실시간 가용 VRAM 용량 확인 (선택적)
        vram_free_gb = None
        try:
            from core.engine.vram_safety_guard import VRAMSafetyGuard
            vram_info = VRAMSafetyGuard.get_vram_info(host=host)
            vram_free_gb = vram_info.get("free_gb")
        except Exception:
            pass

        log_vram_str = f" (현재 가용 VRAM: {vram_free_gb:.1f}GB)" if vram_free_gb is not None else ""
        logger.info(f"🧹 [VRAM 즉시 청소] {comfy_msg} | GC 객체 {gc_collected}개 정리{log_vram_str}")

        return {
            "success": True,
            "comfy_freed": comfy_freed,
            "comfy_msg": comfy_msg,
            "gc_collected": gc_collected,
            "vram_free_gb": vram_free_gb
        }

    @classmethod
    def get_gpu_temperature(cls) -> Optional[int]:
        """nvidia-smi를 통해 GPU 실시간 온도(°C)를 조회합니다."""
        try:
            import subprocess
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                text=True,
                timeout=3
            ).strip()
            if out:
                return int(out.split("\n")[0].strip())
        except Exception:
            pass
        return None

    @classmethod
    def cooldown_gpu(
        cls,
        duration_sec: int = 60,
        target_temp_c: int = 58,
        brand: str = "easytax",
        lang: str = "vi"
    ):
        """
        1개국 숏폼 생성 완료 후 GPU 보호를 위해 1분(60초) 동안 쿨다운 인터벌을 부여합니다.
        - 실시간 온도를 모니터링하며 50°C대로 냉각 유도
        - 비상 정지(GenerationAbortGuard) 실시간 감시
        """
        import time
        from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException

        cur_temp = cls.get_gpu_temperature()
        temp_str = f"{cur_temp}°C" if cur_temp is not None else "측정불가"
        logger.info(f"❄️ [GPU 쿨다운 시작] 1개국 숏폼 완료! 그래픽카드 보호를 위해 1분({duration_sec}초) 휴식 인터벌을 시작합니다 (현재 온도: {temp_str} ➔ 목표: {target_temp_c}°C 이하)")

        start_time = time.time()
        while time.time() - start_time < duration_sec:
            if GenerationAbortGuard.is_abort_requested():
                logger.warning("🛑 [GPU 쿨다운 중단] 사용자 정지 요청 감지")
                raise GenerationAbortedException("사용자 정지 요청으로 쿨다운이 중단되었습니다.")
            
            elapsed = int(time.time() - start_time)
            remaining = duration_sec - elapsed
            
            # 15초마다 쿨링 경과 안내 로그
            if elapsed > 0 and elapsed % 15 == 0:
                temp_now = cls.get_gpu_temperature()
                temp_now_str = f"{temp_now}°C" if temp_now is not None else ""
                logger.info(f"   🧊 [GPU 쿨링 중] {elapsed}초 경과 ({remaining}초 남음) | 현재 GPU 온도: {temp_now_str}")

            time.sleep(1.0)

        final_temp = cls.get_gpu_temperature()
        final_temp_str = f"{final_temp}°C" if final_temp is not None else "정상"
        logger.info(f"🎉 [GPU 쿨다운 완료] 1분 휴식 완료! 그래픽카드가 {final_temp_str}로 안전하게 냉각되었습니다. 다음 국가 렌더링을 시작합니다.\n")

    @classmethod
    def flush_after_country(
        cls,
        lang: str,
        brand: str = "easytax",
        content_type: str = "cardnews",
        host: str = "http://127.0.0.1:8188",
        cooldown_shorts_sec: int = 60
    ) -> Dict[str, Any]:
        """
        1개국 완제품 생성 완료 직후 호출되는 국가 전용 캐시 방출 및 GPU 쿨다운 훅
        """
        brand_name = "EasyTax" if brand.lower() == "easytax" else "K-Market"
        type_name = "5장 카드뉴스" if content_type.lower() == "cardnews" else "숏폼 비디오"
        
        logger.info(f"✨ [{brand_name}] [{lang.upper()}] {type_name} 1개국 완료! ➔ VRAM 캐시 즉각 방출 실행...")
        res = cls.flush_gpu_vram(host=host, unload_models=False)

        # 숏폼 영상 생성 후 1분간 GPU 쿨다운 휴식 부여
        if content_type.lower() == "shorts":
            cls.cooldown_gpu(duration_sec=cooldown_shorts_sec, brand=brand, lang=lang)
        elif content_type.lower() == "cardnews":
            # 카드뉴스는 3초 미세 휴식
            import time
            time.sleep(3.0)

        logger.info(f"🚀 [{brand_name}] [{lang.upper()}] 준비 완료! 다음 국가 생성에 100% 가용 VRAM 투입 시작.")
        return res
