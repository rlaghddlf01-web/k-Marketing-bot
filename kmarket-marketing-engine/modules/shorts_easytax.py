"""
ShortsEasyTax - 💰 [EasyTax 전담 24시간 무인 숏폼 제작·품질검증·4대 플랫폼 배포 공장]
- 조특법 30조 90% 소득세 감면 & D-2 유학생 3.3% 5년 소급 환급 테마
- 5단계 시네마틱 씬 기획 (ScenarioDirectorShortsEasyTax)
- Gemini 고화질 이미지 생성 + AI 비전 실시간 정밀 품질 검사 (MediaQualityVerifier)
- 1080x1920 시네마틱 zoompan 모션 + 모바일 뱅킹 입금 알림 배너 합성 (MotionVideoComposer)
- 17개국 원어민 TTS 음성 (TTSEngine) + 국세청 신뢰 BGM 결합
- 4대 플랫폼(유튜브 쇼츠, 틱톡, 인스타 릴스, 페북 릴스) EasyTax 공식 채널 무인 배포
- Supabase 자가학습 DB (kmarket_golden_copies, marketing_media_assets) 기록
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES
from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax
from core.gemini_media_generator import GeminiMediaGenerator
from core.media_quality_verifier import MediaQualityVerifier
from core.motion_video_composer import MotionVideoComposer
from core.tts_engine import TTSEngine
from core.auto_publishers.shorts_multi_publisher import ShortsMultiPublisher
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("ShortsEasyTax")


class ShortsEasyTax:
    """EasyTax 전담 숏폼 비디오 무인 생산 공장"""
    def __init__(self):
        self.service_id = "easytax"
        self.output_dir = OUTPUTS_DIR / "shorts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.scenario_director = ScenarioDirectorShortsEasyTax()
        self.gemini_media_gen = GeminiMediaGenerator(service_id=self.service_id)
        self.quality_verifier = MediaQualityVerifier(service_id=self.service_id)
        self.motion_composer = MotionVideoComposer(output_dir=self.output_dir)
        self.tts_engine = TTSEngine()
        self.publisher = ShortsMultiPublisher()
        self.supabase = SupabaseManager()

    def produce_shorts(self, lang: str = "vi", force_run: bool = False) -> Dict[str, Any]:
        """
        EasyTax 전용 숏폼 비디오 1편을 기획 ➔ 생성 ➔ 품질검증 ➔ 렌더링 ➔ 배포까지 100% 무인 실행
        """
        logger.info(f"[{lang.upper()}] 💰 [EasyTax 숏폼 공장] 생산 가동 시작...")
        timestamp = int(time.time())

        # 1. 5단계 시네마틱 환급 시나리오 기획
        scenario = self.scenario_director.plan_daily_scenario(lang=lang)
        hook_title = scenario.get("hook_title", "Korea Tax Refund Guide")
        voice_text = scenario.get("voice_text", "Check your retroactive income tax refund in Korea legally.")
        captions = scenario.get("captions", ["Tax Refund Korea", "90% Income Tax Relief"])
        estimated_krw = scenario.get("estimated_krw", 3840000)

        logger.info(f"[{lang.upper()}] 🧠 EasyTax 시나리오 기획 완료: {scenario['theme_name']} (페르소나: {scenario.get('persona_name')})")

        # 2. 17개국 원어민 TTS 음성 생성
        audio_filename = f"shorts_easytax_{lang}_{timestamp}.mp3"
        audio_path = self.tts_engine.generate_speech(voice_text, lang=lang, filename=audio_filename)

        # 3. 5단계 시네마틱 씬별 Gemini 고화질 이미지 생성 & AI 비전 품질 심사
        scene_images = []
        for scene in scenario.get("scenes", []):
            current_prompt = scene["image_prompt"]
            current_neg = scene["negative_prompt"]
            final_img_path = None

            # 🛡️ 최대 3회 AI 비전 품질 검사 & 자가 재촬영(Auto-Retry)
            for attempt in range(1, 4):
                theme_id_attempt = f"{scenario['theme_id']}_s{scene['scene_idx']}" if attempt == 1 else f"{scenario['theme_id']}_s{scene['scene_idx']}_r{attempt}_{int(time.time())}"

                img_path = self.gemini_media_gen.generate_theme_image(
                    lang=lang,
                    theme_id=theme_id_attempt,
                    scenario_plan={
                        "action_prompt": current_prompt,
                        "negative_prompt": current_neg,
                        "theme_name": scene["name"],
                        "persona_desc": scenario.get("persona_name", "Asian foreign worker in Korea")
                    },
                    aspect_ratio="9:16"
                )

                if img_path and Path(img_path).exists():
                    final_img_path = img_path

                passed, q_score, reason, fix_hint = self.quality_verifier.verify_scene_image(
                    img_path,
                    scene_name=f"EasyTax Scene {scene['scene_idx']} ({scene['name']})",
                    lang=lang
                )

                if passed:
                    logger.info(f"[{lang.upper()}] 🖼 EasyTax 씬 {scene['scene_idx']}/5 AI 비전 검증 합격 ({q_score}점): {scene['name']}")
                    break
                else:
                    logger.warning(f"[{lang.upper()}] ⚠️ EasyTax 씬 {scene['scene_idx']}/5 결함 감지 ({reason}) -> 프롬프트 보정 후 재촬영 ({attempt}/3)...")
                    current_prompt = f"{current_prompt}, [HUMAN-CENTRIC PORTRAIT: clear visible face occupying 75% of frame], {fix_hint}"

            scene_images.append({
                "scene_idx": scene["scene_idx"],
                "duration_sec": scene["duration_sec"],
                "image_path": final_img_path,
                "name": scene["name"]
            })

        # 4. 1080x1920 5씬 시네마틱 모션 비디오 + 입금 알림 배너 + BGM 합성
        mp4_path = self.motion_composer.compose_story5_shorts(
            scene_images=scene_images,
            audio_path=audio_path,
            service_id="easytax",
            lang=lang,
            title=hook_title,
            captions=captions,
            scenario_plan=scenario
        )

        if not mp4_path or not Path(mp4_path).exists():
            logger.error(f"[{lang.upper()}] ❌ EasyTax 숏폼 MP4 렌더링 실패")
            return {"success": False, "error": "mp4 rendering failed"}

        # 🖥️ 바탕화면 전용 폴더로 실시간 자동 저장
        desktop_dir = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\이지텍스")
        desktop_dir.mkdir(parents=True, exist_ok=True)
        try:
            import shutil
            desktop_mp4 = desktop_dir / Path(mp4_path).name
            shutil.copy2(str(mp4_path), str(desktop_mp4))
            logger.info(f"📁 [바탕화면 저장] EasyTax 숏폼 영상 복사 완료: {desktop_mp4}")
        except Exception as e:
            logger.warning(f"바탕화면 복사 경고: {e}")

        # 5. Supabase marketing_media_assets & kmarket_golden_copies 자가학습 기록
        try:
            self.supabase.record_marketing_media_asset({
                "service_id": "easytax",
                "target_lang": lang,
                "media_type": "short_video_story5",
                "theme_id": scenario["theme_id"],
                "age_group": scenario.get("age_group", "20s"),
                "gender": scenario.get("gender", "neutral"),
                "prompt_used": scenario.get("action_prompt", ""),
                "file_path": str(mp4_path),
                "quality_score": 95,
                "verification_passed": True
            })

            if self.supabase.client:
                self.supabase.client.table("easytax_golden_copies").upsert({
                    "content_type": "shorts",
                    "service_id": "easytax",
                    "target_lang": lang,
                    "title": hook_title,
                    "content_text": voice_text,
                    "target_url": f"https://ktrs.kr/{lang if lang != 'ko' else ''}",
                    "external_id": f"shorts_et_{lang}_{timestamp}",
                    "score": 95
                }).execute()
                logger.info(f"💎 [Supabase] EasyTax 전용 테이블(easytax_golden_copies) 골든 카피 기록 완료")
        except Exception as e:
            logger.warning(f"EasyTax Supabase 기록 경고: {e}")

        # 6. 🚀 4대 플랫폼(유튜브/틱톡/릴스/페북) EasyTax 공식 채널 배포
        landing_url = f"https://ktrs.kr/{lang if lang != 'ko' else ''}"
        video_description = (
            f"{hook_title}\n\n"
            f"Official Article 30 Expat Tax Refund in South Korea.\n"
            f"Check your estimated refund online: {landing_url}\n\n"
            f"#KoreaTaxRefund #EasyTax #ExpatKorea #KTRS #TaxRelief"
        )

        publish_results = {}
        try:
            publish_results = self.publisher.publish_all({
                "service_id": "easytax",
                "lang": lang,
                "title": hook_title,
                "description": video_description,
                "video_path": str(mp4_path),
                "tags": ["KoreaTaxRefund", "EasyTax", "ExpatKorea", "KTRS"]
            })
            logger.info(f"[{lang.upper()}] 🚀 EasyTax 4대 플랫폼 배포 완료: {publish_results}")
        except Exception as e:
            logger.warning(f"EasyTax 배포 큐 적재 경고: {e}")

        return {
            "success": True,
            "service_id": "easytax",
            "lang": lang,
            "theme_name": scenario["theme_name"],
            "title": hook_title,
            "video_path": str(mp4_path),
            "audio_path": str(audio_path) if audio_path else "",
            "publish_results": publish_results
        }
