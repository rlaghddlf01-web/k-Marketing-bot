# -*- coding: utf-8 -*-
"""
EasyTaxShortsPipeline - 🎬 [이지택스 전용 숏폼 동영상 생산 공장]
- 1단계: '입을 부드럽게 다문 미소' 마스터컷 인물 사진 생성 (Wan2.1 T2I)
- 2단계: 국세청 세금 환급 영수증 UI 생성 후 OpenCV 서브픽셀 정밀 매립
- 3단계: 5.06초(81프레임) 맞춤형 다국어 음성 생성 (Edge-TTS)
- 4단계: Wan 2.2 S2V 립싱크 렌더링 및 FFmpeg 오디오 결합
- 5단계: 로컬 바탕화면 전용 완성본 출력
"""

import os
from pathlib import Path
from PIL import Image

from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.tts_voice_synthesizer import TTSVoiceSynthesizer
from .ui_templates.refund_receipt_template import RefundReceiptTemplate
from .scenarios.prompt_director_shorts import PromptDirectorShortsEasyTax


class EasyTaxShortsPipeline:
    """이지택스 숏폼 자동 생산 파이프라인 (신규 EasyTaxShortsProducer로 위임)"""

    def __init__(self):
        from core.shorts_engine import EasyTaxShortsProducer
        self._producer = EasyTaxShortsProducer()

    def produce(
        self,
        nationality_code: str = "vi",
        amount: int = 3100000,
        custom_master_image: Image.Image = None,
        output_filename: str = "easytax_shorts_5s.mp4"
    ) -> str:
        """신규 1080p 독립 숏폼 엔진 호출"""
        res = self._producer.produce(
            lang=nationality_code,
            amount=amount,
            custom_hero_image=custom_master_image
        )
        return res.get("output_mp4", "")
