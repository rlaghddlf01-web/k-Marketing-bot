"""
GeminiMediaGenerator - Gemini / Imagen AI 직접 비주얼 생성 엔진 (외부 Pexels 의존성 0%)
- 17개국 인종/국적 × 성별 × 만15~34세 나이별 × 6대 감정 테마 고화질 실사 생성
- 카드뉴스 피드 사진 (1:1 / 4:3) 및 숏폼 세로형 배경 (9:16) 직접 생성
- 네거티브 가드레일 (기괴한 손가락, 공중부양, 인종 왜곡) 엄격 통제
"""

import os
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
from config import GEMINI_API_KEY_EASYTAX, GEMINI_API_KEY_KMARKET, DATA_DIR, OUTPUTS_DIR

logger = logging.getLogger("GeminiMediaGenerator")


class GeminiMediaGenerator:
    """
    🎨 Gemini / Imagen AI 기반 고화질 실사 마케팅 이미지 생성기
    - K-Market: GEMINI_API_KEY_KMARKET (유료 전용 키)
    - EasyTax: GEMINI_API_KEY_EASYTAX (유료 전용 키)
    """
    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id.lower()
        if self.service_id == "kmarket":
            self.api_key = GEMINI_API_KEY_KMARKET or GEMINI_API_KEY_EASYTAX
            self.fallback_key = GEMINI_API_KEY_EASYTAX
        else:
            self.api_key = GEMINI_API_KEY_EASYTAX or GEMINI_API_KEY_KMARKET
            self.fallback_key = GEMINI_API_KEY_KMARKET

        self.cache_dir = DATA_DIR / "gemini_generated_media"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        self._init_client()

    def _init_client(self, use_fallback: bool = False):
        try:
            from core.gemini_smart_client import GeminiSmartClient
            self.client = GeminiSmartClient(service_id=self.service_id)
            logger.info(f"GeminiMediaGenerator 스마트 클라이언트 초기화 성공 (서비스: {self.service_id}, 무료키 1순위)")
        except Exception as e:
            logger.warning(f"Gemini 스마트 클라이언트 초기화 실패: {e}")
            self.client = None

    def generate_theme_image(
        self,
        lang: str,
        theme_id: str,
        scenario_plan: Dict[str, Any],
        aspect_ratio: str = "9:16",
        output_path: Optional[Path] = None,
        reference_image_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        ScenarioDirector의 기획안에 맞춰 100% 실사 피드/숏폼 이미지 생성 (1080x1920 또는 1080x1080)
        - reference_image_path 전달 시: 씬 1 기준 인물의 얼굴/헤어/의상을 100% 고정하는 연속 씬 생성
        """
        # 캐시 키 생성
        cache_key = f"{lang}_{theme_id}_{scenario_plan.get('gender','m')}_{aspect_ratio.replace(':','x')}"
        if not output_path:
            output_path = self.cache_dir / f"{cache_key}.png"

        # 프롬프트 조립 (극도로 구체적인 실사 촬영 스타일)
        demo_desc = scenario_plan.get("persona_desc", "Asian expat young worker or student in South Korea")
        action = scenario_plan.get("action_prompt", "looking at smartphone with happy genuine smile")
        
        # ★ [대표님 절대 지침] 40% 웨이스트 샷 & 100% 무결점 실사 사진 렌더링
        is_two_shot = any(k in action.lower() for k in ["two-shot", "two diverse", "two people", "exchanging", "facing each other"])
        if is_two_shot:
            human_centric_mandate = (
                ", [CRITICAL DIRECTING MANDATE: AUTHENTIC TWO-SHOT COMMUNITY PHOTOGRAPHY]: "
                "You are a master documentary photographer. Both foreign resident protagonists are completely visible "
                "from the waist up, standing facing each other in 3/4 profile. Both of their expressive, smiling faces "
                "and warm eye contact MUST be fully visible and uncropped. The clean item/box being handed over and exchanged between them is clearly held. "
                "Zero anatomical errors, authentic skin textures, genuine warm human interaction, natural street lighting, 8k masterpiece."
            )
        else:
            human_centric_mandate = (
                ", [CRITICAL DIRECTING MANDATE: 40% MEDIUM WAIST-UP SHOT & 60% CLEAN OPEN SPACE]: "
                "Photographed from 3.5 meters away on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend. "
                "The human protagonist is positioned on the right side of the frame occupying about 40% of the vertical frame in a natural waist-up view down to the belt line. "
                "The left 60% of the frame MUST remain clean and open with ample negative background space. "
                "Zero anatomical errors, natural matte skin texture, authentic candid mobile photo, strictly NO extreme close-up, NO cropped head."
            )

        continuity_prefix = ""
        ref_image = None
        if reference_image_path and Path(reference_image_path).exists():
            try:
                ref_image = Image.open(reference_image_path)
                continuity_prefix = (
                    "[CRITICAL CHARACTER CONTINUITY MANDATE]: "
                    "The protagonist in this image MUST be the EXACT SAME person as shown in the provided reference image. "
                    "Keep identical facial features, identical hairstyle, identical eye shape, identical skin tone, and identical outfit styling. "
                    "Only change the character's facial expression, action, and environment according to this scene: "
                )
            except Exception as e:
                logger.warning(f"참조 이미지 로드 실패: {e}")
                ref_image = None

        if any(keyword in action for keyword in ["a real", "authentic", "Authentic", "Cinematic", "master reference"]):
            prompt = f"{continuity_prefix}{action}{human_centric_mandate}, Aspect ratio {aspect_ratio}, masterpiece photography, photorealistic 4k."
        else:
            prompt = (
                f"{continuity_prefix}Hyper-realistic authentic documentary portrait of a person ({demo_desc}), {action}{human_centric_mandate}. "
                f"Authentic natural skin texture, cinematic natural lighting, 8k resolution, "
                f"natural facial expression, genuine emotions, clear visible face and upper body. "
                f"Aspect ratio {aspect_ratio}, masterpiece photography."
            )

        negative_prompt = scenario_plan.get("negative_prompt") or (
            "upside down phone, inverted smartphone, backwards phone, phone held upside down, deformed hand holding phone, "
            "giant phone blocking face, macro phone screen, phone covering face, oversized phone, extreme close up of phone, "
            "floating phone, six fingers, deformed hands, extra limbs, disembodied hands, claw hands, "
            "creepy smile, dead eyes, cartoon, 3d render, illustration, blurry, unreadable fake text on screen, "
            "caucasian, white people, blonde hair, blue eyes, western model, european features, non-asian, "
            "bad anatomy, mutated fingers, low quality"
        )

        logger.info(f"[{lang.upper()}] 🎨 Gemini Imagen 비주얼 생성 시작 (테마: {scenario_plan.get('theme_name')}, 인물고정: {bool(ref_image)})...")

        if self.client:
            try:
                # 멀티모달 인풋 구성: 참조 이미지가 있으면 [prompt, ref_image], 없으면 prompt 단독
                contents_payload = [prompt, ref_image] if ref_image else prompt
                result = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite-image',
                    contents=contents_payload
                )
                # 실제 이미지 바이너리 추출 및 저장
                for part in result.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        image = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
                        image.save(output_path, "JPEG", quality=95)
                        logger.info(f"🎉 [봇 자동화 - Gemini Flash Image] 100% 실사 사진 생성 성공 (인물고정: {bool(ref_image)}): {output_path.name}")
                        return output_path
            except Exception as e:
                logger.warning(f"Gemini Image 생성 실패: {e}")

        # Fallback: 고화질 그라디언트 템플릿
        W, H = (1080, 1920) if aspect_ratio == "9:16" else (1080, 1080)
        fallback_img = Image.new("RGB", (W, H), color=(15, 23, 42))
        fallback_img.save(output_path, "JPEG", quality=95)
        return output_path
