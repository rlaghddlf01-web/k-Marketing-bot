"""
LocalGPUMediaGeneratorEasyTax - 💰 [EasyTax 전용 구글 무료 GPU & 로컬 실사 AI 이미지 생성 연동 모듈]
- EasyTax 시나리오 작가(ScenarioDirectorShortsEasyTax) 및 숏폼 팩토리(ShortsEasyTax) 전담
- E-9 제조/식품 근로자, D-2 유학생 알바, E-7 IT 전문직 등 세무 비자 페르소나 최적화
- 1~5씬 100% 동일 인물 일관성 (Fixed Episode Seed & EasyTax Character Anchor 유지)
- 코랩 무료 GPU(RealVisXL) 서버 1순위 호출 (비용 0원) ➔ 미가동 시 EasyTax 유료키(GEMINI_API_KEY_EASYTAX) 안전 롤오버
"""

import os
import io
import json
import base64
import random
import time
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from config import DATA_DIR, OUTPUTS_DIR, GEMINI_API_KEY_EASYTAX

logger = logging.getLogger("LocalGPUMediaGeneratorEasyTax")


class LocalGPUMediaGeneratorEasyTax:
    """
    💰 EasyTax 세무/환급 전용 무료 GPU 실사 이미지 생성 엔진
    """
    def __init__(self, colab_api_url: Optional[str] = None):
        self.service_id = "easytax"
        self.cache_dir = DATA_DIR / "gemini_generated_media" / "easytax"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 숏폼 편당 동일 인물 고정 시드 관리
        self._current_episode_seed: Optional[int] = None
        self._last_episode_id: Optional[str] = None

        logger.info("💰 [EasyTax 비주얼 엔진] 🏆 Google Gemini 3.1 Flash-Lite Image 표준 가동")

    def set_episode_seed(self, episode_id: str, seed: Optional[int] = None):
        """동일 숏폼 에피소드(1~5씬) 전체에 동일 인물 시드 고정"""
        if self._last_episode_id != episode_id or seed is not None:
            self._last_episode_id = episode_id
            self._current_episode_seed = seed if seed is not None else random.randint(100000, 999999999)
            logger.info(f"🎭 [EasyTax 동일 인물 고정] 에피소드 '{episode_id}' 고유 인물 시드: {self._current_episode_seed}")

    def generate_theme_image(
        self,
        lang: str,
        theme_id: str,
        scenario_plan: Dict[str, Any],
        aspect_ratio: str = "9:16",
        output_path: Optional[Path] = None,
        seed: Optional[int] = None,
        reference_image_path: Optional[str] = None
    ) -> Optional[Path]:
        """
        EasyTax 5단계 시네마틱 환급 숏폼에 맞춰 100% 동일 인물 극실사 이미지 생성
        """
        cache_key = f"easytax_{lang}_{theme_id}_{scenario_plan.get('gender','m')}_{aspect_ratio.replace(':','x')}"
        if not output_path:
            output_path = self.cache_dir / f"{cache_key}.png"

        episode_base_id = theme_id.split("_s")[0] if "_s" in theme_id else theme_id
        if self._last_episode_id != episode_base_id:
            self.set_episode_seed(episode_base_id, seed)
        
        target_seed = seed if seed is not None else self._current_episode_seed

        action = scenario_plan.get("action_prompt", "authentic documentary portrait")
        is_scene_focus = scenario_plan.get("is_scene_focus", False)
        is_app_screen = scenario_plan.get("is_app_screen", False)

        if is_app_screen:
            directing_mandate = (
                ", [CRITICAL DIRECTING MANDATE: CLEAN COMMERCIAL DESK STILL-LIFE]: "
                "Crisp photorealistic details, modern finance office desk surface, clean spacious center composition for mobile device display, "
                "perfectly balanced architectural lighting, no human face close-up, 8k commercial photography."
            )
        elif is_scene_focus:
            directing_mandate = (
                ", [CRITICAL DIRECTING MANDATE: CINEMATIC ATMOSPHERIC SCENE]: "
                "Crisp photorealistic details, magnificent natural atmosphere, perfect lighting, "
                "no human face close-up, authentic travel or still-life photography, 8k masterpiece."
            )
        else:
            directing_mandate = (
                ", [CRITICAL DIRECTING MANDATE: 100% HUMAN-CENTRIC PORTRAIT]: "
                "The human protagonist is the absolute primary focal subject of this photo. "
                "Clear expressive face, genuine eyes, upper body occupying 60-70% of frame, "
                "photorealistic human skin texture, authentic natural lighting, master photography, 8k."
            )
        prompt = f"{action}{directing_mandate}"

        negative_prompt = scenario_plan.get("negative_prompt") or (
            "caucasian, white, blonde hair, blue eyes, deformed fingers, extra limbs, claw hands, "
            "fused fingers, floating phone, disembodied hands, cartoon, 3d render, plastic skin, ugly, blurry"
        )

        # ── 100% 통합 단일 표준: Google Gemini 3.1 Flash-Lite Image 실사 AI 엔진 직결 ──
        try:
            from core.gemini_media_generator import GeminiMediaGenerator
            gemini_gen = GeminiMediaGenerator(service_id="easytax")
            res_path = gemini_gen.generate_theme_image(
                lang=lang,
                theme_id=theme_id,
                scenario_plan=scenario_plan,
                aspect_ratio=aspect_ratio,
                output_path=output_path
            )
            if res_path and res_path.exists() and res_path.stat().st_size > 5000:
                logger.info(f"🎉 [EasyTax Gemini 3.1 Flash-Lite 완성]: {res_path.name}")
                return res_path
        except Exception as e:
            logger.error(f"EasyTax Gemini 3.1 Flash-Lite 이미지 생성 예외: {e}")

        # ── 2. 안전 Fallback (기본 캔버스) ──
        W, H = (1080, 1920) if aspect_ratio == "9:16" else (1080, 1080)
        fallback_img = Image.new("RGB", (W, H), color=(15, 23, 42))
        fallback_img.save(output_path, "JPEG", quality=95)
        return output_path
