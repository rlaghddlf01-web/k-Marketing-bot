# -*- coding: utf-8 -*-
"""
BaseShortsProducer - 🎬 [AI 숏폼 비디오 통합 생산 엔진 표준 추상 클래스]
- Wan 2.1 T2I 기반 고품질 인물 마스터컷 생성
- PhoneScreenEmbedder를 통한 실제 서비스 UI 액정 정밀 매립 (원근 왜곡 + 손가락 피부 오클루전)
- Edge-TTS 다국어 음성 생성 및 Wan 2.2 S2V 립싱크 모션 렌더링
- 1080x1920 세로 풀HD 최종 마케팅 컴포징
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.tts_voice_synthesizer import TTSVoiceSynthesizer
from .shorts_video_composer import ShortsVideoComposer

logger = logging.getLogger("ShortsEngine")


class BaseShortsProducer(ABC):
    """이지텍스 및 케이마켓 숏폼 엔진의 공통 기반 클래스"""

    def __init__(self, brand_name: str):
        self.brand_name = brand_name
        self.embedder = PhoneScreenEmbedder()
        self.wan_client = WanPipelineClient()
        self.tts = TTSVoiceSynthesizer()
        self.composer = ShortsVideoComposer()
        
        # 로컬 바탕화면 숏폼 산출물 폴더 자동 관리
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")
        self.output_base = self.desktop / "숏폼_산출물" / self.brand_name
        self.output_base.mkdir(parents=True, exist_ok=True)

        # ComfyUI 엔진 상태 확인
        self._wan_available = self.wan_client.check_health()
        if self._wan_available:
            logger.info(f"✅ [{self.brand_name}] ComfyUI 연결 성공 - GPU 숏폼 렌더링 모드 준비 완료")
        else:
            logger.warning(f"⚠️ [{self.brand_name}] ComfyUI 대기 상태 - 작업 시작 시 자동 기동됩니다.")

    def ensure_engine_ready(self) -> bool:
        """ComfyUI GPU 엔진 준비 확인 및 자동 기동"""
        if not self._wan_available:
            self._wan_available = self.wan_client.check_health(auto_start=True)
        return self._wan_available

    def prepare_framed_input_image(
        self,
        embedded_img: Image.Image,
        target_w: int = 480,
        target_h: int = 832
    ) -> Image.Image:
        """
        S2V 모델(Wan 2.2 S2V) 최적 해상도로 스마트폰 액정 영역이 잘리지 않도록 안전 프레이밍
        """
        W, H = embedded_img.size
        scale = target_h / float(H)
        scaled_w = int(W * scale)
        scaled_img = embedded_img.resize((scaled_w, target_h), Image.Resampling.LANCZOS)
        
        # 스마트폰이 좌측이나 중앙에 위치할 수 있으므로 안전 크롭 계산
        if scaled_w > target_w:
            crop_left = max(0, min(20, scaled_w - target_w))
            framed_img = scaled_img.crop((crop_left, 0, crop_left + target_w, target_h))
        else:
            framed_img = scaled_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
        return framed_img

    @abstractmethod
    def get_character_prompt(self, lang: str, **kwargs) -> Dict[str, str]:
        """브랜드별/국가별 T2I 인물 프롬프트 반환"""
        pass

    @abstractmethod
    def render_ui_image(self, lang: str, **kwargs) -> Image.Image:
        """스마트폰 액정에 박아 넣을 실제 UI 캡처/영수증 이미지 반환"""
        pass

    @abstractmethod
    def get_speech_script(self, lang: str, **kwargs) -> str:
        """국가별 맞춤형 나레이션/대사 스크립트 반환"""
        pass

    @abstractmethod
    def produce(self, lang: str, **kwargs) -> Dict[str, Any]:
        """숏폼 1편 전체 자동 생산 파이프라인 실행"""
        pass
