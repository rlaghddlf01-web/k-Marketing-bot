# -*- coding: utf-8 -*-
"""
TypecastSynthesizer - 🎙️ [타입캐스트(Typecast) 초실사 AI 음성 합성 독립 레고 블록]
================================================================================
- Typecast 공식 API (v1 / ssfm-v30)를 활용한 전문 성우급 음성 합성
- 기본 음성: 'tc_667ce80314cb3a612d6959e8' (Aura 데이팅 전용 트렌디 20대 여성 보이스)
- Wan 2.2 S2V 립싱크 100% 호환 (16kHz Mono 자동 변환 및 무음 정밀 트리밍 탑재)
- GeminiTTSSynthesizer와 100% 동일한 인터페이스로 언제든 자유로운 교체 가능
"""

import os
import sys
import wave
import logging
import requests
import subprocess
import imageio_ffmpeg
from pathlib import Path
from typing import Optional

# Ensure engine root is in sys.path
_engine_root = Path(__file__).resolve().parent.parent.parent
if str(_engine_root) not in sys.path:
    sys.path.insert(0, str(_engine_root))

logger = logging.getLogger("TypecastSynthesizer")


class TypecastSynthesizer:
    """Typecast API 실시간 고음질 음성 합성기"""

    API_URL = "https://api.typecast.ai/v1/text-to-speech"
    DEFAULT_VOICE_ID = "tc_667ce80314cb3a612d6959e8"
    DEFAULT_MODEL = "ssfm-v30"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice_id: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("TYPECAST_API_KEY", "")
        self.default_voice_id = default_voice_id or os.getenv("TYPECAST_VOICE_ID_AURA", self.DEFAULT_VOICE_ID)
        self.model = model or self.DEFAULT_MODEL
        self.output_dir = output_dir or r"D:\ComfyUI_Wan_Engine\ComfyUI\input"
        os.makedirs(self.output_dir, exist_ok=True)

        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"

    def synthesize(
        self,
        text: str,
        output_wav_path: str,
        voice_id: Optional[str] = None,
        sample_rate: int = 24000
    ) -> str:
        """
        주어진 텍스트를 Typecast API로 고음질 WAV 음성 파일로 합성
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        v_id = voice_id or self.default_voice_id

        if not text or not text.strip():
            with wave.open(str(out_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b"\x00" * int(sample_rate * 0.1 * 2))
            logger.info(f"🔇 [TypecastSynthesizer] 빈 텍스트 무음 처리 완료 -> {out_p.name}")
            return str(out_p)

        if not self.api_key:
            raise RuntimeError("Typecast API 키가 설정되지 않았습니다.")

        logger.info(f"🎙️ [TypecastSynthesizer] 음성 합성 요청 (Voice: {v_id}, Model: {self.model}): \"{text[:30]}...\"")

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_id": v_id,
            "model": self.model
        }

        try:
            resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                raise RuntimeError(f"Typecast API 호출 실패 [HTTP {resp.status_code}]: {resp.text}")

            audio_data = resp.content
            if not audio_data or len(audio_data) < 100:
                raise RuntimeError("Typecast API로부터 유효한 오디오 데이터를 수신하지 못했습니다.")

            with open(str(out_p), "wb") as f:
                f.write(audio_data)

            logger.info(f"✅ [TypecastSynthesizer] 합성 성공 ({len(audio_data):,} bytes) -> {out_p.name}")
            return str(out_p)

        except Exception as e:
            logger.error(f"❌ [TypecastSynthesizer] 음성 합성 에러: {e}")
            raise

    def generate_speech_wav(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "female",
        rate: str = "+0%",
        pitch: Optional[str] = None,
        target_duration: Optional[float] = None,
        filename_prefix: str = "speech",
        voice_name: Optional[str] = None
    ) -> str:
        """
        BaseShortsProducer 및 S2VClipStitcher 표준 100% 호환 인터페이스
        - Typecast 고음질 생성 -> FFmpeg 16kHz Mono 표준 변환 -> 무음 정밀 트리밍
        """
        v_id = voice_name or self.default_voice_id
        out_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}.wav")
        temp_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}_typecast_raw.wav")

        # 1. Typecast 원본 합성
        self.synthesize(text=text, output_wav_path=temp_wav_path, voice_id=v_id)

        # 2. FFmpeg 16kHz Mono 변환 (Wan 2.2 S2V 완벽 동기화)
        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", temp_wav_path,
            "-ar", "16000",
            "-ac", "1"
        ]
        if target_duration is not None:
            cmd.extend(["-t", str(target_duration)])
        cmd.append(out_wav_path)

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception:
                pass

        # 3. 무음 정밀 보존 트리밍 (말끝 음절 100% 보존)
        try:
            self._strip_silence(out_wav_path, threshold_ratio=0.015, pad_start_ms=50, pad_end_ms=350)
        except Exception:
            pass

        return out_wav_path

    @staticmethod
    def _strip_silence(wav_path: str, threshold_ratio: float = 0.015, pad_start_ms: int = 50, pad_end_ms: int = 350):
        """WAV 파일의 선두 50ms 즉각 시작, 후두 350ms 여유를 주어 말끝 음절('요', '드') 무손실 보존"""
        import numpy as np
        from scipy.io import wavfile

        sr, data = wavfile.read(wav_path)
        if len(data) == 0:
            return

        mono_data = np.mean(data, axis=1) if len(data.shape) > 1 else data
        peak = np.max(np.abs(mono_data))
        if peak < 100:
            return

        thresh = max(100, int(peak * threshold_ratio))
        non_silent = np.where(np.abs(mono_data) > thresh)[0]

        if len(non_silent) > 0:
            pad_start = int(sr * (pad_start_ms / 1000.0))
            pad_end = int(sr * (pad_end_ms / 1000.0))
            start_idx = max(0, non_silent[0] - pad_start)
            end_idx = min(len(data), non_silent[-1] + pad_end)
            trimmed_data = data[start_idx:end_idx]
            wavfile.write(wav_path, sr, trimmed_data)
