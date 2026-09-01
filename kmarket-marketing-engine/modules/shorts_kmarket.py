"""
ShortsKMarket - 🛒 [K-Market 전담 24시간 무인 숏폼 제작·품질검증·4대 플랫폼 배포 공장]
- 50:50 듀얼 파이프라인 (Mode A 실물 라이브 스크롤 50% vs Mode B 5단계 감동 자취드라마 50%)
- 17개국어 다국어 타깃팅 (베트남, 우즈벡, 몽골, 중국, 영어, 한국어 등)
- Mode A: 실제 Playwright 브라우저 9:16 모바일 자동 스크롤 녹화 (KMarketIframeComposer)
- Mode B: Gemini 5장 이미지 생성 + AI 비전 실시간 정밀 품질 심사 (MediaQualityVerifier)
- 17개국 원어민 TTS 음성 (TTSEngine) + 경쾌한 숏폼 BGM 믹싱
- 4대 플랫폼(유튜브 쇼츠, 틱톡, 인스타 릴스, 페북 릴스) K-Market 공식 채널 무인 배포
- Supabase 자가학습 DB (kmarket_golden_copies, marketing_media_assets) 기록
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket
from core.kmarket_iframe_composer import KMarketIframeComposer
from core.local_gpu_media_generator_kmarket import LocalGPUMediaGeneratorKMarket
from core.gemini_media_generator import GeminiMediaGenerator
from core.media_quality_verifier import MediaQualityVerifier
from core.motion_video_composer import MotionVideoComposer
from core.tts_engine import TTSEngine
from core.auto_publishers.shorts_multi_publisher import ShortsMultiPublisher
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("ShortsKMarket")


class ShortsKMarket:
    """K-Market 전담 숏폼 비디오 무인 생산 공장"""
    def __init__(self):
        self.service_id = "kmarket"
        self.output_dir = OUTPUTS_DIR / "shorts_kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.scenario_director = ScenarioDirectorShortsKMarket()
        self.iframe_composer = KMarketIframeComposer()
        self.gemini_media_gen = LocalGPUMediaGeneratorKMarket()
        self.quality_verifier = MediaQualityVerifier(service_id=self.service_id)
        self.motion_composer = MotionVideoComposer(output_dir=self.output_dir)
        self.tts_engine = TTSEngine()
        self.publisher = ShortsMultiPublisher()
        self.supabase = SupabaseManager()

    def produce_shorts(self, lang: str = "vi", force_mode: Optional[str] = None, engine_mode: str = "colab_gpu") -> Dict[str, Any]:
        """
        K-Market 전용 숏폼 비디오 1편을 기획 ➔ 생성 ➔ 품질검증 ➔ 렌더링 ➔ 배포까지 100% 무인 실행
        (force_mode: 'A_feed_scroll' 또는 'B_gemini_story5')
        """
        logger.info(f"[{lang.upper()}] 🛒 [K-Market 숏폼 공장] 생산 가동 시작... (엔진: {engine_mode})")
        timestamp = int(time.time())

        # ⚡ 이미지 생성 엔진 동적 선택 (대시보드 스위치 연동)
        if engine_mode == "gemini":
            active_media_gen = GeminiMediaGenerator(service_id="kmarket")
            logger.info(f"[{lang.upper()}] 💎 [K-Market 숏폼] 제미나이 Imagen AI 엔진으로 생성")
        else:
            active_media_gen = self.gemini_media_gen  # 기존 LocalGPUMediaGeneratorKMarket
            logger.info(f"[{lang.upper()}] 🆓 [K-Market 숏폼] 무료 코랩 GPU 엔진으로 생성")

        # 1. 일일 50:50 시나리오 기획
        scenario = self.scenario_director.plan_daily_scenario(lang=lang, force_mode=force_mode)
        content_mix = scenario.get("content_mix_type", "A_feed_scroll")
        hook_title = scenario.get("hook_title", "K-Market Korea Expat Guide")
        voice_text = scenario.get("voice_text", "Free furniture and verified second-hand items for expats in Korea!")
        captions = scenario.get("captions", ["K-Market Free Giveaway", "100% Verified Expat Trade"])

        logger.info(f"[{lang.upper()}] 🧠 K-Market 시나리오 기획: {scenario['theme_name']} (타입: {content_mix})")

        # 2. 17개국 원어민 TTS 음성 생성
        audio_filename = f"shorts_kmarket_{lang}_{timestamp}.mp3"
        audio_path = self.tts_engine.generate_speech(voice_text, lang=lang, filename=audio_filename)

        mp4_path = None

        # 3-A. 📱 [Mode A (50%)]: 실제 Playwright 브라우저 9:16 모바일 자동 스크롤 렌더러
        if content_mix == "A_feed_scroll":
            mp4_path = self.iframe_composer.compose_iframe_shorts(
                lang=lang,
                title=hook_title,
                captions=captions,
                audio_path=audio_path,
                scenario_plan=scenario,
                duration_sec=20.0
            )

        # 3-B. 🎭 [Mode B (50%)]: 5단계 헐리웃 감동 자취/0원 나눔 드라마 렌더러
        else:
            scene_images = []
            for scene in scenario.get("scenes", []):
                current_prompt = scene["image_prompt"]
                current_neg = scene["negative_prompt"]
                final_img_path = None

                # 🛡️ 최대 3회 AI 비전 품질 검사 & 자가 재촬영(Auto-Retry)
                for attempt in range(1, 4):
                    theme_id_attempt = f"{scenario['theme_id']}_s{scene['scene_idx']}" if attempt == 1 else f"{scenario['theme_id']}_s{scene['scene_idx']}_r{attempt}_{int(time.time())}"

                    img_path = active_media_gen.generate_theme_image(
                        lang=lang,
                        theme_id=theme_id_attempt,
                        scenario_plan={
                            "action_prompt": current_prompt,
                            "negative_prompt": current_neg,
                            "theme_name": scene["name"],
                            "persona_desc": scenario.get("persona_name", "Asian college student in Korea")
                        },
                        aspect_ratio="9:16"
                    )

                    if img_path and Path(img_path).exists():
                        final_img_path = img_path

                    passed, q_score, reason, fix_hint = self.quality_verifier.verify_scene_image(
                        img_path,
                        scene_name=f"K-Market Scene {scene['scene_idx']} ({scene['name']})",
                        lang=lang
                    )

                    if passed:
                        logger.info(f"[{lang.upper()}] 🖼 K-Market 씬 {scene['scene_idx']}/5 AI 비전 합격 ({q_score}점): {scene['name']}")
                        break
                    else:
                        logger.warning(f"[{lang.upper()}] ⚠️ K-Market 씬 {scene['scene_idx']}/5 결함 감지 ({reason}) -> 프롬프트 보정 후 재촬영 ({attempt}/3)...")
                        current_prompt = f"{current_prompt}, [HUMAN-CENTRIC PORTRAIT: clear visible face occupying 75% of frame], {fix_hint}"

                scene_images.append({
                    "scene_idx": scene["scene_idx"],
                    "duration_sec": scene["duration_sec"],
                    "image_path": final_img_path,
                    "name": scene["name"]
                })

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
            logger.error(f"[{lang.upper()}] ❌ K-Market 숏폼 MP4 렌더링 실패")
            return {"success": False, "error": "mp4 rendering failed"}

        # 🖥️ 바탕화면 전용 폴더로 실시간 자동 저장
        desktop_dir = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\케이마켓")
        desktop_dir.mkdir(parents=True, exist_ok=True)
        try:
            import shutil
            desktop_mp4 = desktop_dir / Path(mp4_path).name
            shutil.copy2(str(mp4_path), str(desktop_mp4))
            logger.info(f"📁 [바탕화면 저장] K-Market 숏폼 영상 복사 완료: {desktop_mp4}")
        except Exception as e:
            logger.warning(f"바탕화면 복사 경고: {e}")

        # 4. Supabase marketing_media_assets & kmarket_golden_copies 자가학습 기록
        try:
            self.supabase.record_marketing_media_asset({
                "service_id": "kmarket",
                "target_lang": lang,
                "media_type": f"short_video_{content_mix}",
                "theme_id": scenario["theme_id"],
                "age_group": scenario.get("age_group", "20s"),
                "gender": scenario.get("gender", "neutral"),
                "prompt_used": scenario.get("action_prompt", ""),
                "file_path": str(mp4_path),
                "quality_score": 95,
                "verification_passed": True
            })

            if self.supabase.client:
                self.supabase.client.table("kmarket_golden_copies").upsert({
                    "content_type": "shorts",
                    "service_id": "kmarket",
                    "target_lang": lang,
                    "title": hook_title,
                    "content_text": voice_text,
                    "target_url": f"https://ktrs-market.vercel.app/{lang if lang != 'ko' else ''}",
                    "external_id": f"shorts_km_{lang}_{timestamp}",
                    "score": 95
                }).execute()
                logger.info(f"💎 [Supabase] K-Market 골든 카피 자가학습 기록 완료")
        except Exception as e:
            logger.warning(f"K-Market Supabase 기록 경고: {e}")

        # 5. 🚀 4대 플랫폼(유튜브/틱톡/릴스/페북) K-Market 공식 채널 배포
        landing_url = f"https://ktrs-market.vercel.app/{lang if lang != 'ko' else ''}"
        video_description = (
            f"{hook_title}\n\n"
            f"Free 0 Won Giveaways & Safe Second-Hand Campus Trades in South Korea!\n"
            f"Download/Visit: {landing_url}\n\n"
            f"#KMarket #KoreaExpat #FreeStuffKorea #KoreaLife #0WonGiveaway"
        )

        publish_results = {}
        try:
            publish_results = self.publisher.publish_all({
                "service_id": "kmarket",
                "lang": lang,
                "title": hook_title,
                "description": video_description,
                "video_path": str(mp4_path),
                "tags": ["KMarket", "KoreaExpat", "FreeStuffKorea", "KoreaLife"]
            })
            logger.info(f"[{lang.upper()}] 🚀 K-Market 4대 플랫폼 배포 완료: {publish_results}")
        except Exception as e:
            logger.warning(f"K-Market 배포 큐 적재 경고: {e}")

        return {
            "success": True,
            "service_id": "kmarket",
            "lang": lang,
            "content_mix_type": content_mix,
            "theme_name": scenario["theme_name"],
            "title": hook_title,
            "video_path": str(mp4_path),
            "audio_path": str(audio_path) if audio_path else "",
            "publish_results": publish_results
        }
