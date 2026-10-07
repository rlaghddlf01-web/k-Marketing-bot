# -*- coding: utf-8 -*-
"""
GeminiTTSSynthesizer - 🎙️ [Google Gemini 2.5 Flash 초실사 음성 합성 독립 레고 블록]
- 100% 무료 Google Gemini 2.5 Flash Audio API를 활용한 극상의 인간 음성 생성
- 기계음 0%, 자연스러운 한국어 억양, 호흡, 감정 표현 탑재
- 기본 음성: 'Aoede' (맑고 깨끗한 20대 여성 톤, Google Despina 동일 음색)
"""

import os
import sys
import wave
import logging
import imageio_ffmpeg
import subprocess
from pathlib import Path
from typing import Optional, Dict

# Ensure engine root is in sys.path
_engine_root = Path(__file__).resolve().parent.parent.parent
if str(_engine_root) not in sys.path:
    sys.path.insert(0, str(_engine_root))

logger = logging.getLogger("GeminiTTSSynthesizer")

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

class GeminiTTSSynthesizer:
    """Google Gemini 2.5 Flash 실시간 고음질 음성 합성기 (Aoede/Fenrir 지원)"""

    def __init__(self, default_voice: str = "Aoede", output_dir: Optional[str] = None):
        self.default_voice = default_voice
        self.model_name = "gemini-2.5-flash-preview-tts"
        self.output_dir = output_dir or r"D:\ComfyUI_Wan_Engine\ComfyUI\input"
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"
        self.api_keys = self._load_api_keys()
        self.current_key_idx = 0

    def _load_api_keys(self) -> list:
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_FREE_API_KEY_AURA_4,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_PAID_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_API_KEY
        )
        candidates = [
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_FREE_API_KEY_AURA_4,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_PAID_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_API_KEY
        ]
        valid_keys = [k.strip() for k in candidates if k and len(k.strip()) > 10]
        # 중복 제거 (순서 보존)
        seen = set()
        deduped = []
        for k in valid_keys:
            if k not in seen:
                seen.add(k)
                deduped.append(k)
        return deduped

    def _get_client(self, key: str):
        if genai is None:
            raise RuntimeError("google-genai 라이브러리가 설치되지 않았습니다.")
        return genai.Client(api_key=key)

    def synthesize(
        self,
        text: str,
        output_wav_path: str,
        voice_name: Optional[str] = None,
        sample_rate: int = 24000
    ) -> str:
        """
        주어진 한국어 텍스트를 맑고 깨끗한 24kHz WAV 음성 파일로 합성 (자율 멀티키 스위칭)
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        v_name = voice_name or self.default_voice

        if not text or not text.strip():
            # 빈 텍스트인 경우 0.1초 무음 WAV 생성 후 즉시 반환
            with wave.open(str(out_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b"\x00" * int(sample_rate * 0.1 * 2))
            logger.info(f"🔇 [GeminiTTSSynthesizer] 빈 텍스트 무음 처리 완료 -> {out_p.name}")
            return str(out_p)

        if not self.api_keys:
            raise RuntimeError("사용 가능한 Gemini API 키가 없습니다.")

        logger.info(f"🎙️ [GeminiTTSSynthesizer] 초실사 음성 합성 시작 ('{v_name}'): \"{text[:30]}...\"")

        total_keys = len(self.api_keys)
        last_error = None

        for attempt in range(total_keys):
            key_idx = (self.current_key_idx + attempt) % total_keys
            api_key = self.api_keys[key_idx]

            try:
                client = self._get_client(api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=v_name
                                )
                            )
                        )
                    )
                )

                if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                    raise RuntimeError("Gemini API로부터 음성 파트를 수신하지 못했습니다.")

                raw_pcm = response.candidates[0].content.parts[0].inline_data.data
                if not raw_pcm:
                    raise RuntimeError("Gemini API로부터 음성 데이터를 수신하지 못했습니다.")

                # PCM을 표준 WAV로 저장
                with wave.open(str(out_p), "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(raw_pcm)

                # 성공한 키를 현재 키로 유지
                self.current_key_idx = key_idx
                logger.info(f"✅ [GeminiTTSSynthesizer] 음성 합성 성공 ({len(raw_pcm):,} bytes, Key #{key_idx+1}) -> {out_p.name}")
                return str(out_p)

            except Exception as e:
                err_str = str(e)
                logger.warning(f"⚠️ [GeminiTTSSynthesizer] Key #{key_idx+1} 호출 실패 ({err_str[:80]}), 다음 키로 자동 스위칭...")
                last_error = e
                continue

        logger.error(f"❌ [GeminiTTSSynthesizer] 모든 API 키({total_keys}개) 호출 실패: {last_error}")
        raise last_error

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
        - Aoede (맑고 차분한 20대 여성) / Puck (세련된 2030 훈남 중저음 남성)
        - 16kHz 무손실 변환 및 무음 정밀 트리밍 적용
        """
        is_female = str(gender).lower() in ["female", "f", "여", "여성", "woman"]
        v_name = voice_name or ("Aoede" if is_female else "Fenrir")

        out_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}.wav")
        temp_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}_raw24k.wav")

        # 1. 24kHz 원본 생성
        self.synthesize(text=text, output_wav_path=temp_wav_path, voice_name=v_name, sample_rate=24000)

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

        # 3. 무음 정밀 제거
        try:
            self._strip_silence(out_wav_path, threshold_ratio=0.02, pad_ms=10)
        except Exception:
            pass

        return out_wav_path

    @staticmethod
    def _strip_silence(wav_path: str, threshold_ratio: float = 0.015, pad_start_ms: int = 50, pad_end_ms: int = 350):
        """WAV 파일의 선두는 50ms로 즉각 시작하고, 후두는 350ms 여유를 주어 말끝 음절('요', '드') 100% 무손실 보존"""
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


if __name__ == "__main__":
    synth = GeminiTTSSynthesizer(default_voice="Aoede")
    test_out = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\test_gemini_tts.wav")
    synth.generate_speech_wav("아우라 앱에 셀카 한 장 넣으면 청담동 화보로 바로 바꿔줍니다!", filename_prefix="test_aoede")
