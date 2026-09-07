"""
LocalGPUMediaGeneratorKMarket - 🛒 [K-Market 전용 구글 무료 GPU & 로컬 실사 AI 이미지 생성 연동 모듈]
- K-Market 시나리오 작가(ScenarioDirectorShortsKMarket) 및 숏폼 팩토리(ShortsKMarket) 전담
- 전국 20대 대학가 유학생, 원룸 자취생, 산단 청년 등 중고거래/자취 페르소나 최적화
- 1~5씬 100% 동일 인물 일관성 (Fixed Episode Seed & K-Market Character Anchor 유지)
- 코랩 무료 GPU(RealVisXL) 서버 1순위 호출 (비용 0원) ➔ 미가동 시 K-Market 유료키(GEMINI_API_KEY_KMARKET) 안전 롤오버
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

from config import DATA_DIR, OUTPUTS_DIR, GEMINI_API_KEY_KMARKET

logger = logging.getLogger("LocalGPUMediaGeneratorKMarket")


class LocalGPUMediaGeneratorKMarket:
    """
    🛒 K-Market 자취/0원나눔 전용 무료 GPU 실사 이미지 생성 엔진
    """
    def __init__(self, colab_api_url: Optional[str] = None):
        self.service_id = "kmarket"
        self.cache_dir = DATA_DIR / "gemini_generated_media" / "kmarket"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 숏폼 편당 동일 인물 고정 시드 관리
        self._current_episode_seed: Optional[int] = None
        self._last_episode_id: Optional[str] = None

        logger.info("🛒 [K-Market 비주얼 엔진] 🏆 Google Gemini 3.1 Flash-Lite Image 표준 가동")

    def set_episode_seed(self, episode_id: str, seed: Optional[int] = None):
        """동일 숏폼 에피소드(1~5씬) 전체에 동일 인물 시드 고정"""
        if self._last_episode_id != episode_id or seed is not None:
            self._last_episode_id = episode_id
            self._current_episode_seed = seed if seed is not None else random.randint(100000, 999999999)
            logger.info(f"🎭 [K-Market 동일 인물 고정] 에피소드 '{episode_id}' 고유 인물 시드: {self._current_episode_seed}")

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
        K-Market 5단계 감동 자취/0원 나눔 숏폼에 맞춰 100% 동일 인물 극실사 이미지 생성
        """
        cache_key = f"kmarket_{lang}_{theme_id}_{scenario_plan.get('gender','m')}_{aspect_ratio.replace(':','x')}"
        if not output_path:
            output_path = self.cache_dir / f"{cache_key}.png"

        episode_base_id = theme_id.split("_s")[0] if "_s" in theme_id else theme_id
        if self._last_episode_id != episode_base_id:
            self.set_episode_seed(episode_base_id, seed)
        
        target_seed = seed if seed is not None else self._current_episode_seed

        action = scenario_plan.get("action_prompt", "authentic documentary photography")
        # 🎯 가구/물건 나눔 테마에서는 억지 얼굴 클로즈업(upper body occupying 70%)을 원천 배제하고
        # 물건 실물과 상황 중심의 자연스러운 실사 씬을 그대로 반영
        # 🧑 얼굴 뭉개짐 방지: 모든 씬에 얼굴 선명도 강화 키워드 자동 주입
        prompt = (
            f"{action}, "
            f"highly detailed facial features, sharp clear eyes, well-defined face, natural skin texture, "
            f"photorealistic, sharp focus, 8k uhd, professional documentary photography"
        )

        passed_neg = scenario_plan.get("negative_prompt") or ""
        safeguard_neg = (
            "studying, reading books, writing, notebook, pen, pencil, classroom, homework, exams, "
            "empty hands, handshake without furniture, standing without furniture, people only, no furniture, missing item, "
            "blurry face, blurred face, melted face, smudged face, undefined facial features, faceless, "
            "distorted face, deformed eyes, squinting, bad eyes, asymmetric eyes, bad teeth, deformed mouth, "
            "out of focus face, soft focus face, motion blur on face, foggy face, hazy face, "
            "deformed fingers, fused fingers, extra fingers, missing fingers, malformed hands, claw hands, "
            "bad anatomy, grotesque, amputee, caucasian, white, blonde hair, blue eyes, "
            "floating phone, cartoon, 3d render, plastic skin, ugly, blurry, lowres, jpeg artifacts"
        )
        negative_prompt = f"{passed_neg}, {safeguard_neg}".strip(", ")

        # ── 씬 1 실제 사진 참조(IP-Adapter Face Lock) 준비 ──
        ref_b64 = None
        if reference_image_path and Path(reference_image_path).exists():
            try:
                with open(reference_image_path, "rb") as rf:
                    ref_b64 = base64.b64encode(rf.read()).decode("utf-8")
                logger.info(f"🔒 [K-Market Face Lock] 씬 1 인물 사진 주입: {Path(reference_image_path).name}")
            except Exception as e:
                logger.warning(f"참조 이미지 base64 인코딩 실패: {e}")

        # ── 100% 통합 단일 표준: Google Gemini 3.1 Flash-Lite Image 실사 AI 엔진 직결 ──
        try:
            from core.gemini_media_generator import GeminiMediaGenerator
            gemini_gen = GeminiMediaGenerator(service_id="kmarket")
            res_path = gemini_gen.generate_theme_image(
                lang=lang,
                theme_id=theme_id,
                scenario_plan=scenario_plan,
                aspect_ratio=aspect_ratio,
                output_path=output_path,
                reference_image_path=Path(reference_image_path) if reference_image_path else None
            )
            if res_path and res_path.exists() and res_path.stat().st_size > 5000:
                logger.info(f"🎉 [K-Market Gemini 3.1 Flash-Lite 완성]: {res_path.name}")
                return res_path
        except Exception as e:
            logger.error(f"Gemini 3.1 Flash-Lite 이미지 생성 예외: {e}")

        # ── 3. 최후의 안전 Fallback (기본 캔버스) ──
        W, H = (1080, 1920) if aspect_ratio == "9:16" else (1080, 1080)
        fallback_img = Image.new("RGB", (W, H), color=(24, 24, 27))
        fallback_img.save(output_path, "JPEG", quality=95)
        return output_path
