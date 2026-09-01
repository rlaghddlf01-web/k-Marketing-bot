# -*- coding: utf-8 -*-
"""
TTSEngine - 17개국 성별/연령 맞춤 다채로운 신경망 성우(Neural Voice) 합성 엔진
- 주인공 성별(m/f)에 따른 실시간 성우 자동 매칭
- 17개국 다국어별 복수 음색(Voice Pool) 로테이션 지원
"""

import os
import random
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
from config import LANGUAGES, OUTPUTS_DIR

logger = logging.getLogger("TTSEngine")

# 🎙️ 17개국 성별/음색별 최고급 Edge-TTS 신경망 성우 풀
VOICE_POOLS: Dict[str, Dict[str, List[str]]] = {
    "vi": {
        "f": ["vi-VN-HoaiMyNeural"],
        "m": ["vi-VN-NamMinhNeural"]
    },
    "zh": {
        "f": ["zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural"],
        "m": ["zh-CN-YunxiNeural", "zh-CN-YunjianNeural"]
    },
    "uz": {
        "f": ["uz-UZ-MadinaNeural"],
        "m": ["uz-UZ-SardorNeural"]
    },
    "en": {
        "f": ["en-US-JennyNeural", "en-US-AriaNeural", "en-US-AnaNeural"],
        "m": ["en-US-GuyNeural", "en-US-ChristopherNeural", "en-US-EricNeural"]
    },
    "ru": {
        "f": ["ru-RU-SvetlanaNeural"],
        "m": ["ru-RU-DmitryNeural"]
    },
    "tl": {
        "f": ["fil-PH-BlessicaNeural"],
        "m": ["fil-PH-AngeloNeural"]
    },
    "id": {
        "f": ["id-ID-GadisNeural"],
        "m": ["id-ID-ArdiNeural"]
    },
    "th": {
        "f": ["th-TH-PremwadeeNeural", "th-TH-AcharaNeural"],
        "m": ["th-TH-NiwatNeural"]
    },
    "mn": {
        "f": ["mn-MN-YesuiNeural"],
        "m": ["mn-MN-BataaNeural"]
    },
    "km": {
        "f": ["km-KH-SreymomNeural"],
        "m": ["km-KH-PisethNeural"]
    },
    "ne": {
        "f": ["ne-NP-HemkalaNeural"],
        "m": ["ne-NP-SagarNeural"]
    },
    "my": {
        "f": ["my-MM-NilarNeural"],
        "m": ["my-MM-ThihaNeural"]
    },
    "ja": {
        "f": ["ja-JP-NanamiNeural", "ja-JP-AoiNeural"],
        "m": ["ja-JP-KeitaNeural", "ja-JP-DaichiNeural"]
    },
    "es": {
        "f": ["es-ES-ElviraNeural", "es-ES-AbrilNeural"],
        "m": ["es-ES-AlvaroNeural"]
    },
    "fr": {
        "f": ["fr-FR-DeniseNeural"],
        "m": ["fr-FR-HenriNeural"]
    },
    "ko": {
        "f": ["ko-KR-SunHiNeural", "ko-KR-JiMinNeural"],
        "m": ["ko-KR-InJoonNeural", "ko-KR-BongJinNeural"]
    },
    "bn": {
        "f": ["bn-BD-NabanitaNeural"],
        "m": ["bn-BD-PradeepNeural"]
    },
    "si": {
        "f": ["si-LK-ThiliniNeural"],
        "m": ["si-LK-SameeraNeural"]
    }
}


class TTSEngine:
    """
    Edge-TTS 기반 17개국 성별/음색 맞춤 성우 음성 합성 엔진
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def select_voice(self, lang: str = "ko", gender: str = "f") -> str:
        """주인공 성별 및 언어에 맞는 최적의 신경망 성우 선정"""
        g_key = "m" if gender in ["m", "male", "남", "남성"] else "f"
        pool = VOICE_POOLS.get(lang, VOICE_POOLS.get("en", {}))
        gender_voices = pool.get(g_key, [])

        if gender_voices:
            voice = random.choice(gender_voices)
        else:
            # 기본 폴백
            lang_config = LANGUAGES.get(lang, LANGUAGES["ko"])
            voice = lang_config.get("voice", "ko-KR-SunHiNeural")

        logger.info(f"🎙️ [TTS 성우 선정] 언어: {lang.upper()} | 성별: {'남성' if g_key == 'm' else '여성'} | 성우: {voice}")
        return voice

    async def generate_speech_async(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "f",
        filename: str = "voiceover.mp3"
    ) -> Optional[Path]:
        """
        주어진 텍스트를 대상 언어와 성별에 맞는 네이티브 음성으로 합성하여 mp3 파일로 저장
        """
        voice = self.select_voice(lang=lang, gender=gender)
        target_path = self.output_dir / filename

        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(target_path))
            logger.info(f"[{lang.upper()}] TTS 생성 완료 ({voice}): {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Edge-TTS 생성 실패 ({lang}, {voice}): {e}")
            return None

    def generate_speech(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "f",
        filename: str = "voiceover.mp3"
    ) -> Optional[Path]:
        """동기 래퍼 함수"""
        try:
            return asyncio.run(self.generate_speech_async(text, lang, gender, filename))
        except Exception as e:
            logger.error(f"TTS 동기 실행 에러: {e}")
            return None
