# -*- coding: utf-8 -*-
"""
ShortsKMarketLocalGPU - 🛒 [K-Market 전담 완전 분리형 로컬 GPU 5단계 정품 숏폼 파이프라인]
- 기존 modules/shorts_kmarket.py 및 코어 파일은 100% 무손실 보존
- 씬 1: 소형 나눔 물품(쿠쿠 밥솥/식기) 골목 직거래 실사 컷
- 씬 2: 나눔 물품으로 아늑해진 방 & 150만원 절약 실사 컷
- 씬 3: KTRS 마켓 실제 모바일 웹 0원 피드 스크롤 비디오 클립
- 씬 4: 실시간 1:1 자동번역 채팅창 실제 작동 비디오 클립
- 씬 5: 나눔 받은 방에서 카메라 정면 응시 CTA 추천 실사 컷
- 2단 그라데이션 UI 자막 카드 + Edge-TTS 신경망 음성 + 신나는 숏폼 BGM
- NVENC 하드웨어 가속 60fps 마스터링
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import BASE_DIR, DATA_DIR, OUTPUTS_DIR, DESKTOP_DIR
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket
from core.kmarket_screencast_provider import KMarketScreencastProvider
from core.motion_video_composer import MotionVideoComposer
from core.tts_engine import TTSEngine

logger = logging.getLogger("ShortsKMarketLocalGPU")

class ShortsKMarketLocalGPU:
    """K-Market 전담 로컬 GPU 분리형 숏폼 생산 공장"""
    def __init__(self):
        self.service_id = "kmarket"
        self.output_dir = OUTPUTS_DIR / "shorts_kmarket_local_gpu"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 바탕화면 전용 출력 경로 (OneDrive 및 로컬 바탕화면 양방향 보장)
        self.desktop_onedrive = Path(r"C:\Users\zkfnt\OneDrive\Desktop\숏폼_산출물\KTRS마켓_로컬GPU")
        self.desktop_local = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\KTRS마켓_로컬GPU")
        self.desktop_onedrive.mkdir(parents=True, exist_ok=True)
        self.desktop_local.mkdir(parents=True, exist_ok=True)

        self.scenario_director = ScenarioDirectorShortsKMarket()
        self.screencast_provider = KMarketScreencastProvider()
        self.motion_composer = MotionVideoComposer(output_dir=self.output_dir)
        self.tts_engine = TTSEngine()

    def produce_shorts(self, lang: str = "ko") -> Dict[str, Any]:
        """
        정품 5단계 시네마틱 숏폼 1편 제작
        """
        timestamp = int(time.time())
        print("=" * 65)
        print(f"🎬 [KTRS 마켓 로컬 GPU] 정품 5단계 숏폼 제작 시작 (언어: {lang.upper()})")
        print("=" * 65)

        # 1. 5단계 시나리오 기획
        scenario = self.scenario_director.plan_daily_scenario(lang=lang, force_mode="B_gemini_story5")
        hook_title = scenario.get("hook_title", "K-Market 0원 나눔")
        voice_text = scenario.get("voice_text", "비싼 가구 사지 말고 K-Market에서 0원에 받으세요!")
        captions = scenario.get("captions", ["🎁 0원 무료나눔", "📍 대학교 자취촌"])
        town_target = scenario.get("town", "흑석 중앙대")
        item_name = scenario.get("item", "쿠쿠 전기밥솥 & 식기")

        print(f"🧠 [1/4] 시나리오 기획 완료: {scenario.get('theme_name')}")
        print(f"   • 나눔 소형 물품: {item_name} ({town_target})")

        # 2. Edge-TTS 신경망 음성 생성
        audio_filename = f"kmarket_local_voice_{lang}_{timestamp}.mp3"
        audio_path = self.tts_engine.generate_speech(voice_text, lang=lang, filename=audio_filename)
        print(f"🎙️ [2/4] 신경망 성우 음성 생성 완료: {audio_path.name}")

        # 3. 5단계 시네마틱 씬 구성 (사진 3장 + 실제 모바일 비디오 2개)
        print("🖼️ [3/4] 5단계 씬별 정품 비주얼 에셋 결합 중...")
        
        # 씬 1, 2, 5 정품 실사 인물 사진 (소형 물품 나눔 컷)
        media_dir = DATA_DIR / "gemini_generated_media" / "kmarket"
        s1_img = media_dir / "kmarket_ko_univ_cau_heukseok_s1_m_9x16.png"
        s2_img = media_dir / "kmarket_ko_univ_cau_heukseok_s2_m_9x16.png"
        s5_img = media_dir / "kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"

        # 씬 3: KTRS 마켓 실제 모바일 피드 스크롤 비디오 클립
        feed_clip = self.screencast_provider.get_or_render_feed_clip(
            lang=lang, target_area=town_target, item_name=item_name, duration_sec=3.5
        )
        # 씬 4: 실시간 1:1 자동번역 채팅창 실제 구동 비디오 클립
        detail_clip = self.screencast_provider.get_or_render_detail_clip(
            lang=lang, item_name=item_name, target_area=town_target, duration_sec=3.5
        )

        scene_images = [
            {
                "scene_idx": 1,
                "duration_sec": 3.8,
                "image_path": str(s1_img),
                "video_path": None,
                "name": "골목 소형 나눔 직거래 만남"
            },
            {
                "scene_idx": 2,
                "duration_sec": 3.8,
                "image_path": str(s2_img),
                "video_path": None,
                "name": "아늑한 방 완성 & 150만원 절약"
            },
            {
                "scene_idx": 3,
                "duration_sec": 3.5,
                "image_path": None,
                "video_path": str(feed_clip),
                "name": "KTRS 마켓 실물 0원 피드 스크롤 영상"
            },
            {
                "scene_idx": 4,
                "duration_sec": 3.5,
                "image_path": None,
                "video_path": str(detail_clip),
                "name": "17개 언어 실시간 1:1 자동번역 채팅 영상"
            },
            {
                "scene_idx": 5,
                "duration_sec": 4.0,
                "image_path": str(s5_img),
                "video_path": None,
                "name": "아늑한 방에서 최종 CTA 추천"
            }
        ]

        for s in scene_images:
            p = s['video_path'] if s['video_path'] else s['image_path']
            print(f"   • 씬 {s['scene_idx']}: {s['name']} -> {Path(p).name} ({s['duration_sec']}초)")

        # 4. MotionVideoComposer로 5단계 시네마틱 결합 렌더링
        print("🎬 [4/4] 2단 UI 자막 + BGM 믹싱 + 5060 Ti 모션 비디오 렌더링 시작...")
        mp4_path = self.motion_composer.compose_story5_shorts(
            scene_images=scene_images,
            audio_path=audio_path,
            service_id="kmarket",
            lang=lang,
            title=hook_title,
            captions=captions,
            scenario_plan=scenario
        )

        if not mp4_path or not Path(mp4_path).exists():
            print("❌ 렌더링 실패")
            return {"success": False, "error": "mp4 rendering failed"}

        # 5. 바탕화면으로 직접 복사 (모니터 즉시 확인용)
        out_name = f"KTRS마켓_정품5단계_완제품쇼츠_{timestamp}.mp4"
        dest_onedrive = self.desktop_onedrive / out_name
        dest_local = self.desktop_local / out_name
        direct_desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop") / "KTRS마켓_정품5단계_완제품쇼츠.mp4"

        shutil.copy(mp4_path, dest_onedrive)
        shutil.copy(mp4_path, dest_local)
        shutil.copy(mp4_path, direct_desktop)

        size_mb = round(direct_desktop.stat().st_size / (1024 * 1024), 2)
        print("=" * 65)
        print(f"🎉 [대성공!] 5단계 정품 숏폼 완제품 제작 완료 ({size_mb} MB)")
        print(f"🏆 [바탕화면 정중앙 바로가기]:")
        print(f"   ➔ {direct_desktop}")
        print("=" * 65)

        return {
            "success": True,
            "mp4_path": str(direct_desktop),
            "size_mb": size_mb
        }

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    factory = ShortsKMarketLocalGPU()
    res = factory.produce_shorts(lang="ko")
