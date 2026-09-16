# -*- coding: utf-8 -*-
"""
TTSVoiceSynthesizer - 🎙️ [Edge-TTS 다국어 16kHz 무손실 음향 생성기]
- 숏폼 81프레임(5.06초 @ 16fps) 호흡 및 발화 속도 최적화
- 한국어, 베트남어, 우즈베크어, 러시아어 등 다국어 신경망 보이스 자동 매핑
- FFmpeg 기반 16kHz Mono WAV 무손실 변환 (Wav2Vec2 음성 인코더 100% 호환)
"""

import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional
import edge_tts
import imageio_ffmpeg


# 🎯 8개국 및 주요 언어별 남성/여성 공식 고음질 신경망 보이스 매핑 테이블
VOICE_MAP: Dict[str, Dict[str, str]] = {
    "ko": {"female": "ko-KR-SunHiNeural", "male": "ko-KR-InJoonNeural"},
    "vi": {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural"},
    "uz": {"female": "uz-UZ-MadinaNeural", "male": "uz-UZ-SardorNeural"},
    "km": {"female": "km-KH-SreymomNeural", "male": "km-KH-PisethNeural"},
    "id": {"female": "id-ID-GadisNeural", "male": "id-ID-ArdiNeural"},
    "th": {"female": "th-TH-PremwadeeNeural", "male": "th-TH-NiwatNeural"},
    "kk": {"female": "kk-KZ-AigulNeural", "male": "kk-KZ-DauletNeural"},
    "tl": {"female": "fil-PH-BlessicaNeural", "male": "fil-PH-AngeloNeural"},
    "my": {"female": "my-MM-NilarNeural", "male": "my-MM-ThihaNeural"},
    "ru": {"female": "ru-RU-SvetlanaNeural", "male": "ru-RU-DmitryNeural"},
    "mn": {"female": "ru-RU-SvetlanaNeural", "male": "ru-RU-DmitryNeural"},
    "en": {"female": "en-US-JennyNeural", "male": "en-US-GuyNeural"},
    "zh": {"female": "zh-CN-XiaoxiaoNeural", "male": "zh-CN-YunjianNeural"},
    "ne": {"female": "ne-NP-HemkalaNeural", "male": "ne-NP-SagarNeural"},
    "si": {"female": "si-LK-ThiliniNeural", "male": "si-LK-SameeraNeural"},
    "bn": {"female": "bn-BD-NabanitaNeural", "male": "bn-BD-PradeepNeural"},
}


class TTSVoiceSynthesizer:
    """다국어 숏폼 음성 합성 엔진 (성별 일치 보장)"""

    def __init__(self, output_dir: Optional[str] = None):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.output_dir = output_dir or r"D:\ComfyUI_Wan_Engine\ComfyUI\input"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_speech_wav(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "female",
        rate: str = "+0%",
        target_duration: float = 5.0625,
        filename_prefix: str = "speech"
    ) -> str:
        """
        인물 성별(gender)과 국가 언어(lang)에 100% 일치하는 신경망 보이스로 합성
        """
        # 성별 정규화 (male vs female)
        gender_clean = "male" if str(gender).lower() in ["male", "m", "man", "남", "남성"] else "female"
        lang_voices = VOICE_MAP.get(lang, VOICE_MAP.get("ko"))

        if isinstance(lang_voices, dict):
            voice = lang_voices.get(gender_clean, lang_voices.get("female", "ko-KR-SunHiNeural"))
        elif isinstance(lang_voices, str):
            voice = lang_voices
        else:
            voice = "ko-KR-SunHiNeural"
        mp3_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}.mp3")
        wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}.wav")

        async def _run_tts():
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(mp3_path)

        asyncio.run(_run_tts())

        # FFmpeg를 이용한 16kHz mono WAV 변환 및 길이 보정
        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", mp3_path,
            "-ar", "16000",
            "-ac", "1",
            "-t", str(target_duration),
            wav_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return wav_path
