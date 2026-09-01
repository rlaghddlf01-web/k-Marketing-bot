"""
🎵 [BGMManager — 숏폼 전용 10대 경쾌한 BGM 풀 및 스마트 로테이션 엔진]
- 10종의 다양한 숏폼 최적화 상업용 무료 경쾌한 BGM 풀 자동 관리
- 영상 렌더링 시 직전 사용된 트랙과 중복되지 않도록 무작위 순환(Shuffle Rotation) 선택
- 음원 파일 부재 시 고품질 프로그래머틱 화음/멜로디 신디사이저로 자동 무중단 생성
"""

import os
import wave
import struct
import math
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import BASE_DIR

logger = logging.getLogger("BGMManager")

# 🎯 숏폼 최적화 경쾌한 10대 BGM 메타데이터 정의
UPBEAT_BGM_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "bgm_01_marimba",
        "filename": "bgm_01_upbeat_marimba.wav",
        "title": "Upbeat Marimba & Mallet Pop",
        "genre": "마림바 & 실로폰 팝",
        "tempo_bpm": 128,
        "mood": "아기자기하고 귀여운 느낌 (0원 나눔 가구 득템)",
        "scale": "major",
        "root_hz": 261.63, # C4
        "chord_prog": [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]] # C - G - Am - F
    },
    {
        "id": "bgm_02_acoustic",
        "filename": "bgm_02_acoustic_breeze.wav",
        "title": "Acoustic Breeze & Strum",
        "genre": "밝은 어쿠스틱 스트럼 & 박수",
        "tempo_bpm": 120,
        "mood": "따뜻하고 산뜻한 캠퍼스 분위기 (유학생 이사 꿀팁)",
        "scale": "major",
        "root_hz": 293.66, # D4
        "chord_prog": [[0, 4, 7], [9, 12, 16], [5, 9, 12], [7, 11, 14]] # D - Bm - G - A
    },
    {
        "id": "bgm_03_synthpop",
        "filename": "bgm_03_future_synth_pop.wav",
        "title": "Future Bright Synth Groove",
        "genre": "통통 튀는 퓨처 신스 팝",
        "tempo_bpm": 130,
        "mood": "2030 트렌디 비트 (17개국 자동번역 앱 시연)",
        "scale": "major",
        "root_hz": 261.63, # C4
        "chord_prog": [[5, 9, 12], [7, 11, 14], [9, 12, 16], [0, 4, 7]] # F - G - Am - C
    },
    {
        "id": "bgm_04_chillhouse",
        "filename": "bgm_04_chill_house_beat.wav",
        "title": "Seoul Urban Chill House",
        "genre": "신나는 로파이 하우스",
        "tempo_bpm": 124,
        "mood": "세련된 도심 리듬감 (외국인 밀집 타운 정보)",
        "scale": "major",
        "root_hz": 220.00, # A3
        "chord_prog": [[0, 4, 7, 11], [5, 9, 12, 16], [7, 11, 14, 17], [0, 4, 7, 11]]
    },
    {
        "id": "bgm_05_whistle",
        "filename": "bgm_05_whistle_happy_snap.wav",
        "title": "Whistle & Snaps Happy Day",
        "genre": "경쾌한 휘슬 & 핑거 스냅",
        "tempo_bpm": 126,
        "mood": "기분 좋은 멜로디 (생활비 절약 비법)",
        "scale": "major",
        "root_hz": 261.63,
        "chord_prog": [[0, 4, 7], [5, 9, 12], [0, 4, 7], [7, 11, 14]]
    },
    {
        "id": "bgm_06_moneydrop",
        "filename": "bgm_06_joyful_money_drop.wav",
        "title": "Joyful Deposit & Money Pop",
        "genre": "짜릿한 서프라이즈 머니 팝",
        "tempo_bpm": 132,
        "mood": "축제 분위기 (세금 환급금 입금 알림)",
        "scale": "major",
        "root_hz": 329.63, # E4
        "chord_prog": [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]
    },
    {
        "id": "bgm_07_tropical",
        "filename": "bgm_07_sunny_tropical.wav",
        "title": "Sunny Tropical Island Vibe",
        "genre": "햇살 가득 트로피컬 하우스",
        "tempo_bpm": 125,
        "mood": "청량하고 시원한 느낌 (스트레스 제로 한국 생활)",
        "scale": "major",
        "root_hz": 261.63,
        "chord_prog": [[0, 4, 7], [9, 12, 16], [5, 9, 12], [7, 11, 14]]
    },
    {
        "id": "bgm_08_kpopdance",
        "filename": "bgm_08_kpop_energy_dance.wav",
        "title": "K-Pop Energy Dance Beat",
        "genre": "케이팝 스타일 댄스 인스트",
        "tempo_bpm": 135,
        "mood": "빠르고 신나는 K-바이브 (초반 3초 후킹)",
        "scale": "major",
        "root_hz": 293.66,
        "chord_prog": [[0, 4, 7], [5, 9, 12], [9, 12, 16], [7, 11, 14]]
    },
    {
        "id": "bgm_09_jazzyhop",
        "filename": "bgm_09_jazzy_walking_hop.wav",
        "title": "Walking Campus Jazzy Hop",
        "genre": "발걸음이 가벼운 재즈 힙합",
        "tempo_bpm": 118,
        "mood": "리듬감 있는 베이스 (대학가 무빙세일 투어)",
        "scale": "major",
        "root_hz": 220.00,
        "chord_prog": [[0, 3, 7, 10], [5, 8, 12, 15], [2, 5, 9, 12], [7, 10, 14, 17]]
    },
    {
        "id": "bgm_10_poprock",
        "filename": "bgm_10_feelgood_pop_rock.wav",
        "title": "Feel Good Bright Pop Rock",
        "genre": "긍정 에너지 팝 락",
        "tempo_bpm": 130,
        "mood": "활기차고 당찬 에너지 (출국 전 환급 총정리)",
        "scale": "major",
        "root_hz": 261.63,
        "chord_prog": [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]
    }
]


class BGMManager:
    """
    🎵 [BGMManager] 숏폼 비디오 BGM 10종 자동 로테이션 및 합성 엔진
    """
    def __init__(self, bgm_dir: Optional[Path] = None):
        self.bgm_dir = bgm_dir or (BASE_DIR / "outputs" / "bgm")
        self.bgm_dir.mkdir(parents=True, exist_ok=True)
        self.catalog = UPBEAT_BGM_CATALOG
        self._last_played_idx: int = -1
        self.ensure_all_bgms_exist()

    # ─────────────────────────────────────────────────────────────
    # 🎼 1. 프로그래머틱 10종 고음질 경쾌한 WAV 오디오 생성기
    # ─────────────────────────────────────────────────────────────

    def _synthesize_track(self, info: Dict[str, Any], duration_sec: float = 24.0) -> Path:
        """
        수학적 가산 합성(Harmonics + ADSR + 드럼 리듬)을 통해
        방송/숏폼 규격 16-bit 44.1kHz 스테레오 경쾌한 BGM WAV를 자동 렌더링
        """
        output_file = self.bgm_dir / info["filename"]
        if output_file.exists() and output_file.stat().st_size > 100000:
            return output_file

        sample_rate = 44100
        bpm = info.get("tempo_bpm", 128)
        beat_dur = 60.0 / bpm
        root_hz = info.get("root_hz", 261.63)
        progression = info.get("chord_prog", [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]])

        total_samples = int(duration_sec * sample_rate)
        left_channel = [0.0] * total_samples
        right_channel = [0.0] * total_samples

        # 음계 계산 함수 (세미톤)
        def note_hz(semitones: float) -> float:
            return root_hz * (2.0 ** (semitones / 12.0))

        # 코드 진행 시퀀싱 (4마디 루프)
        chord_dur_beats = 4.0
        chord_dur_sec = chord_dur_beats * beat_dur
        num_chords = len(progression)

        # 1) 화음 & 아르페지오 (Marimba/Pluck 레이어)
        step_dur_sec = beat_dur / 2.0 # 8비트 아르페지오
        current_time = 0.0
        step_idx = 0

        while current_time < duration_sec:
            chord_idx = int(current_time / chord_dur_sec) % num_chords
            current_chord = progression[chord_idx]
            note_semi = current_chord[step_idx % len(current_chord)]
            freq = note_hz(note_semi + 12) # 1옥타브 높여서 통통 튀게

            # 노트 시작 인덱스
            start_s = int(current_time * sample_rate)
            note_len_s = int(step_dur_sec * 0.85 * sample_rate)

            # ADSR 엔벨로프 + 마림바 배음 합성
            for i in range(note_len_s):
                idx = start_s + i
                if idx >= total_samples:
                    break
                t_env = i / note_len_s
                # 빠른 어택, 지수 감쇄 (통통 튀는 타격감)
                envelope = (1.0 - math.exp(-t_env * 50.0)) * math.exp(-t_env * 6.5)
                
                phase = (2.0 * math.pi * freq * (i / sample_rate))
                # 기본파 + 2배음 + 3배음 (밝고 경쾌한 톤)
                sample_val = (
                    math.sin(phase) * 0.6 +
                    math.sin(phase * 2.0) * 0.25 +
                    math.sin(phase * 3.0) * 0.15
                ) * envelope * 0.35

                # 스테레오 패닝 (통통 튀는 입체감)
                pan = 0.5 + 0.25 * math.sin(step_idx * 0.8)
                left_channel[idx] += sample_val * (1.0 - pan)
                right_channel[idx] += sample_val * pan

            current_time += step_dur_sec
            step_idx += 1

        # 2) 바운시 베이스라인 (Bouncy Bass Layer)
        current_time = 0.0
        while current_time < duration_sec:
            chord_idx = int(current_time / chord_dur_sec) % num_chords
            bass_root = progression[chord_idx][0]
            freq = note_hz(bass_root - 12) # 1옥타브 낮춰서 든든하게

            start_s = int(current_time * sample_rate)
            bass_len_s = int(beat_dur * 0.8 * sample_rate)

            for i in range(bass_len_s):
                idx = start_s + i
                if idx >= total_samples:
                    break
                t_env = i / bass_len_s
                envelope = (1.0 - math.exp(-t_env * 40.0)) * math.exp(-t_env * 3.5)
                phase = 2.0 * math.pi * freq * (i / sample_rate)
                # 따뜻하고 묵직한 서브베이스
                sample_val = (math.sin(phase) * 0.8 + math.sin(phase * 2.0) * 0.2) * envelope * 0.40
                left_channel[idx] += sample_val * 0.5
                right_channel[idx] += sample_val * 0.5

            current_time += beat_dur

        # 3) 경쾌한 숏폼 퍼커션 (Snaps / Shaker / Kick Rhythm)
        current_time = 0.0
        beat_idx = 0
        while current_time < duration_sec:
            start_s = int(current_time * sample_rate)

            # 킥 드럼 (정박 1, 3박)
            if beat_idx % 2 == 0:
                kick_len = int(0.12 * sample_rate)
                for i in range(kick_len):
                    idx = start_s + i
                    if idx >= total_samples:
                        break
                    t = i / kick_len
                    # 피치 드롭 140Hz -> 45Hz
                    pitch = 140.0 * (1.0 - t * 0.7)
                    kick_val = math.sin(2.0 * math.pi * pitch * (i / sample_rate)) * (1.0 - t) * 0.45
                    left_channel[idx] += kick_val
                    right_channel[idx] += kick_val

            # 스냅 / 림샷 (엇박 2, 4박)
            if beat_idx % 2 == 1:
                snap_len = int(0.08 * sample_rate)
                for i in range(snap_len):
                    idx = start_s + i
                    if idx >= total_samples:
                        break
                    t = i / snap_len
                    # 노이즈 + 고음 클릭
                    noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 18.0) * 0.25
                    left_channel[idx] += noise
                    right_channel[idx] += noise

            current_time += beat_dur
            beat_idx += 1

        # WAV 파일 바이너리 패킹 (16-bit PCM Stereo)
        with wave.open(str(output_file), "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)

            # 최대 진폭 노멀라이징 (-1.0dB 피크 방지)
            max_amp = max(max([abs(x) for x in left_channel]), max([abs(x) for x in right_channel]), 0.001)
            scale_factor = 0.85 / max_amp

            raw_bytes = bytearray()
            for l, r in zip(left_channel, right_channel):
                l_int = max(-32767, min(32767, int(l * scale_factor * 32767)))
                r_int = max(-32767, min(32767, int(r * scale_factor * 32767)))
                raw_bytes.extend(struct.pack("<hh", l_int, r_int))

            wav.writeframes(raw_bytes)

        logger.info(f"✨ 10대 경쾌한 BGM 생성 완료: {output_file.name} ({info['genre']})")
        return output_file

    def ensure_all_bgms_exist(self):
        """10대 BGM 트랙이 outputs/bgm/에 모두 준비되어 있는지 확인하고 없으면 자동 생성"""
        for info in self.catalog:
            try:
                self._synthesize_track(info)
            except Exception as e:
                logger.warning(f"BGM 트랙 생성 중 경고 ({info['filename']}): {e}")

    # ─────────────────────────────────────────────────────────────
    # 🎲 2. 중복 방지 스마트 로테이션 선택기
    # ─────────────────────────────────────────────────────────────

    def get_random_upbeat_bgm(self, service_id: str = "kmarket") -> Path:
        """
        직전 사용된 BGM과 연속으로 겹치지 않게 무작위로 다음 경쾌한 BGM 선택
        """
        # 기존 단일 고정 파일이 있으면 후보군에 포함
        available_files = [self.bgm_dir / item["filename"] for item in self.catalog if (self.bgm_dir / item["filename"]).exists()]
        
        # 파일이 없으면 즉시 생성 보장
        if not available_files:
            self.ensure_all_bgms_exist()
            available_files = [self.bgm_dir / item["filename"] for item in self.catalog if (self.bgm_dir / item["filename"]).exists()]

        # 그래도 없으면 기본 wav 파일 탐색
        if not available_files:
            fallback = list(self.bgm_dir.glob("*.wav")) + list(self.bgm_dir.glob("*.mp3"))
            if fallback:
                return fallback[0]
            # 비상시 bgm_kmarket.wav 경로 반환
            return self.bgm_dir / "bgm_kmarket.wav"

        # 직전 곡과 다른 인덱스 무작위 선택 (셔플 로테이션)
        candidate_indices = [i for i in range(len(available_files)) if i != self._last_played_idx]
        if not candidate_indices:
            chosen_idx = 0
        else:
            chosen_idx = random.choice(candidate_indices)

        self._last_played_idx = chosen_idx
        selected_file = available_files[chosen_idx]
        
        # 일치하는 정보 로그
        matched_info = next((item for item in self.catalog if item["filename"] == selected_file.name), None)
        genre_str = f"[{matched_info['genre']}]" if matched_info else ""
        logger.info(f"🎶 [BGM 로테이션] 숏폼 믹싱 음원 선정: {selected_file.name} {genre_str} ({service_id})")
        return selected_file

    def list_available_bgms(self) -> List[Dict[str, Any]]:
        """10대 BGM 트랙의 실시간 상태 반환"""
        res = []
        for item in self.catalog:
            p = self.bgm_dir / item["filename"]
            res.append({
                **item,
                "exists": p.exists(),
                "size_kb": round(p.stat().st_size / 1024, 1) if p.exists() else 0
            })
        return res
