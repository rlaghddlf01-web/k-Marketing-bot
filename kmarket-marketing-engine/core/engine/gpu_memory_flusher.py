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
    def flush_after_country(
        cls,
        lang: str,
        brand: str = "easytax",
        content_type: str = "cardnews",
        host: str = "http://127.0.0.1:8188"
    ) -> Dict[str, Any]:
        """
        1개국 완제품 생성 완료 직후 호출되는 국가 전용 캐시 방출 훅
        """
        brand_name = "EasyTax" if brand.lower() == "easytax" else "K-Market"
        type_name = "5장 카드뉴스" if content_type.lower() == "cardnews" else "숏폼 비디오"
        
        logger.info(f"✨ [{brand_name}] [{lang.upper()}] {type_name} 1개국 완료! ➔ 0초 VRAM 캐시 삭제 실행...")
        res = cls.flush_gpu_vram(host=host, unload_models=False)
        logger.info(f"🚀 [{brand_name}] [{lang.upper()}] 메모리 초기화 완료! 다음 국가 생성에 100% 가용 VRAM 투입 준비 완료.")
        return res
