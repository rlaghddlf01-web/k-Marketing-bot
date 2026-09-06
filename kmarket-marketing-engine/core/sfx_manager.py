# -*- coding: utf-8 -*-
"""
SFXManager - 🔔 [숏폼 바이럴 효과음(SFX) 합성 및 관리 엔진]
- 외부 다운로드 의존성 0% (Python wave 모듈 기반 프로그래머틱 고음질 합성)
- 카카오뱅크 입금 푸시 알림 벨 ("띵동~")
- 동전 짤랑 / 캐시 레지스터 카칭 ("Cha-ching!")
- 44.1kHz 16-bit Stereo 고음질 오디오 자동 캐싱
"""

import os
import wave
import struct
import math
import logging
from pathlib import Path
from typing import Optional

from config import DATA_DIR, OUTPUTS_DIR

logger = logging.getLogger("SFXManager")


class SFXManager:
    """
    🎶 바이럴 숏폼 전용 고음질 효과음 엔진
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "sfx")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_kakaobank_chaching_sfx(self) -> Path:
        """
        🔔 씬 2 전용: 카카오뱅크 '띵동~' 푸시 벨 + 캐시 카칭('Cha-ching!') 복합 효과음 (1.4초)
        """
        out_path = self.output_dir / "kakaobank_chaching.wav"
        if out_path.exists() and out_path.stat().st_size > 5000:
            return out_path

        sample_rate = 44100
        duration = 1.4
        total_samples = int(sample_rate * duration)
        
        # 2채널 스테레오 버퍼
        left_samples = [0.0] * total_samples
        right_samples = [0.0] * total_samples

        def add_tone(freq: float, start_t: float, dur: float, vol: float, decay: float = 6.0):
            start_idx = int(start_t * sample_rate)
            end_idx = min(total_samples, start_idx + int(dur * sample_rate))
            for i in range(start_idx, end_idx):
                t = (i - start_idx) / sample_rate
                env = math.exp(-decay * t)
                val = math.sin(2 * math.pi * freq * t) * vol * env
                # 약간의 하모닉스 배음 추가
                val += math.sin(2 * math.pi * freq * 2 * t) * (vol * 0.3) * env
                left_samples[i] += val
                right_samples[i] += val

        def add_metallic_clink(start_t: float, vol: float):
            # 카칭! 동전 부딪히는 고주파 복합 차임
            clink_freqs = [2489.0, 3136.0, 4186.0, 5587.0, 7040.0]
            for f in clink_freqs:
                add_tone(f, start_t, 0.35, vol * 0.25, decay=12.0)

        # 1. '띵' (G5 - 784Hz) t = 0.0s
        add_tone(783.99, 0.0, 0.4, 0.65, decay=5.0)
        
        # 2. '동' (C6 - 1046.5Hz) t = 0.18s
        add_tone(1046.50, 0.18, 0.6, 0.85, decay=4.5)

        # 3. '카칭!' (Cha-ching!) t = 0.45s ~ 0.85s (동전 여러 개가 찰랑거리는 사운드)
        add_metallic_clink(0.42, 0.70)
        add_metallic_clink(0.48, 0.85)
        add_metallic_clink(0.55, 0.95)
        add_metallic_clink(0.62, 0.75)
        add_metallic_clink(0.70, 0.60)

        # 4. 마무리 맑은 골드 차임 링잉 (t = 0.55s, E6)
        add_tone(1318.51, 0.55, 0.8, 0.60, decay=3.0)

        # 16-bit PCM 정규화 및 작성
        with wave.open(str(out_path), "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for l, r in zip(left_samples, right_samples):
                # 클리핑 방지
                clamped_l = max(-1.0, min(1.0, l))
                clamped_r = max(-1.0, min(1.0, r))
                val_l = int(clamped_l * 32767)
                val_r = int(clamped_r * 32767)
                frames.extend(struct.pack("<hh", val_l, val_r))
            wav.writeframes(frames)

        logger.info(f"🔔 [SFXManager] 카카오뱅크 띵동 카칭 효과음 합성 완료: {out_path.name}")
        return out_path
