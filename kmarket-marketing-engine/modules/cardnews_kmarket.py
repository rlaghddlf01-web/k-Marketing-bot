"""
CardnewsKMarket - 🛒 [K-Market 전담 5장 7:3 황금 분할 0원 나눔 카드뉴스 생성 공장]
- 5장 7:3 분할 1080x1350 카드뉴스 무과금 렌더링
- 상단 70% (1080x945): LocalGPUMediaGeneratorKMarket (구글 무료 GPU RealVisXL V4.0)
- 하단 30% (1080x405): CardnewsComposerKMarket (다크차콜 & 네온오렌지 룩앤필)
- 1~5장 전체 동일 인물 시드 고정 관리
- 바탕화면 '카드뉴스_산출물/케이마켓' 자동 저장
"""

import os
import time
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, BASE_URLS
from core.scenario_director_cardnews_kmarket import ScenarioDirectorCardnewsKMarket
from core.local_gpu_media_generator_kmarket import LocalGPUMediaGeneratorKMarket
from core.gemini_media_generator import GeminiMediaGenerator
from core.cardnews_composer_kmarket import CardnewsComposerKMarket
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("CardnewsKMarket")


class CardnewsKMarket:
    """K-Market 전담 5장 카드뉴스 무인 생산 공장"""
    def __init__(self):
        self.service_id = "kmarket"
        self.output_dir = OUTPUTS_DIR / "cardnews" / "kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_dir = Path(r"C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓")
        self.desktop_dir.mkdir(parents=True, exist_ok=True)

        self.scenario_director = ScenarioDirectorCardnewsKMarket()
        self.media_gen = LocalGPUMediaGeneratorKMarket()
        self.composer = CardnewsComposerKMarket()
        self.supabase = SupabaseManager()

    def generate_carousel_cardnews(
        self,
        lang: str = "uz",
        theme_index: Optional[int] = None,
        engine_mode: str = "colab_gpu"
    ) -> Dict[str, Any]:
        """
        K-Market 전용 5장 7:3 황금 분할 카드뉴스 (1080x1350) 생성 및 저장
        """
        scenario = self.scenario_director.get_carousel_scenario(lang=lang, theme_index=theme_index)
        cards = scenario.get("cards", [])
        episode_id = scenario.get("episode_id", f"kmarket_{lang}_{int(time.time())}")

        self.media_gen.set_episode_seed(episode_id)

        # ⚡ 이미지 생성 엔진 동적 선택 (대시보드 스위치 연동)
        if engine_mode == "gemini":
            active_media_gen = GeminiMediaGenerator(service_id="kmarket")
            logger.info(f"🛒 [K-Market 카드뉴스] 제미나이 Imagen AI 엔진으로 생성")
        else:
            active_media_gen = self.media_gen  # 기존 LocalGPUMediaGeneratorKMarket
            logger.info(f"🛒 [K-Market 카드뉴스] 무료 코랩 GPU 엔진으로 생성")

        timestamp = int(time.time())
        saved_paths: List[Path] = []

        logger.info(f"🛒 [K-Market 7:3 카드뉴스 생산 시작] {lang.upper()} - {scenario.get('theme_name')} (5장 슬라이드)...")

        for card in cards:
            s_idx = card.get("slide_idx", 1)
            # 1. 상단 70% (1080x945) 고화질 실사 이미지 생성 (무료 GPU)
            img_plan = {
                "action_prompt": card.get("image_prompt"),
                "negative_prompt": card.get("negative_prompt"),
                "gender": "m"
            }
            top_img_path = active_media_gen.generate_theme_image(
                lang=lang,
                theme_id=f"card_{episode_id}_s{s_idx}",
                scenario_plan=img_plan,
                aspect_ratio="16:9"
            )

            # 2. 7:3 분할 캔버스 합성 (1080x1350)
            out_filename = f"kmarket_cardnews_{lang}_s{s_idx}_{timestamp}.jpg"
            out_path = self.output_dir / out_filename

            composed_path = self.composer.compose_slide(
                top_image_path=top_img_path,
                card_data=card,
                slide_idx=s_idx,
                total_slides=len(cards),
                output_path=out_path
            )

            # 3. 바탕화면 자동 복사
            desktop_path = self.desktop_dir / out_filename
            try:
                shutil.copy(composed_path, desktop_path)
            except Exception as e:
                logger.warning(f"바탕화면 복사 에러: {e}")

            saved_paths.append(desktop_path if desktop_path.exists() else composed_path)

        logger.info(f"🎉 [K-Market 5장 카드뉴스 완성] 총 {len(saved_paths)}장 바탕화면 저장 완료!")

        return {
            "success": True,
            "service_id": "kmarket",
            "lang": lang,
            "theme_name": scenario.get("theme_name"),
            "total_slides": len(saved_paths),
            "image_paths": [str(p) for p in saved_paths],
            "desktop_dir": str(self.desktop_dir)
        }
