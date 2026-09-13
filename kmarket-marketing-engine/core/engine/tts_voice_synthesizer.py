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


VOICE_MAP: Dict[str, str] = {
    "ko": "ko-KR-SunHiNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "uz": "uz-UZ-MadinaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "mn": "ru-RU-SvetlanaNeural",  # 몽골어 대체 또는 영문
    "en": "en-US-JennyNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural",
    "tl": "fil-PH-BlessicaNeural",
    "km": "km-KH-SreymomNeural",
    "my": "my-MM-NilarNeural",
    "ne": "ne-NP-HemkalaNeural",
    "si": "si-LK-ThiliniNeural",
    "bn": "bn-BD-NabanitaNeural",
}


class TTSVoiceSynthesizer:
    """다국어 숏폼 음성 합성 엔진"""

    def __init__(self, output_dir: Optional[str] = None):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.output_dir = output_dir or r"D:\ComfyUI_Wan_Engine\ComfyUI\input"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_speech_wav(
        self,
        text: str,
        lang: str = "ko",
        rate: str = "+18%",
        target_duration: float = 5.0625,
        filename_prefix: str = "speech"
    ) -> str:
        """
        텍스트를 5초 숏폼 규격(16kHz mono WAV)으로 합성하여 반환
        """
        voice = VOICE_MAP.get(lang, "ko-KR-SunHiNeural")
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
