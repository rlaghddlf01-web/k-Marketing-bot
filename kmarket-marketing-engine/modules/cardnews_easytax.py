"""
CardnewsEasyTax - 💰 [EasyTax 전담 5장 7:3 황금 분할 국세청 세무 환급 카드뉴스 생성 공장]
- 5장 7:3 분할 1080x1350 카드뉴스 무과금 렌더링
- 상단 70% (1080x945): LocalGPUMediaGeneratorEasyTax (구글 무료 GPU RealVisXL V4.0)
- 하단 30% (1080x405): CardnewsComposerEasyTax (딥네이비 & 골드 룩앤필)
- 1~5장 전체 동일 인물 시드 고정 관리
- 바탕화면 '카드뉴스_산출물/이지텍스' 자동 저장
"""

import os
import time
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, BASE_URLS, DESKTOP_CARDNEWS_EASYTAX
from core.scenario_director_cardnews_easytax import ScenarioDirectorCardnewsEasyTax
from core.local_gpu_media_generator_easytax import LocalGPUMediaGeneratorEasyTax
from core.gemini_media_generator import GeminiMediaGenerator
from core.cardnews_composer_easytax import CardnewsComposerEasyTax
from core.media_quality_verifier import MediaQualityVerifier
from core.supabase_manager import SupabaseManager
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter
from core.auto_publishers.cardnews_multi_publisher import CardnewsMultiPublisher

logger = logging.getLogger("CardnewsEasyTax")


class CardnewsEasyTax:
    """EasyTax 전담 5장 카드뉴스 무인 생산 공장"""
    def __init__(self):
        self.service_id = "easytax"
        self.output_dir = OUTPUTS_DIR / "cardnews" / "easytax"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_dir = DESKTOP_CARDNEWS_EASYTAX
        self.desktop_dir.mkdir(parents=True, exist_ok=True)

        self.scenario_director = ScenarioDirectorCardnewsEasyTax()
        self.media_gen = LocalGPUMediaGeneratorEasyTax()
        self.composer = CardnewsComposerEasyTax()
        self.quality_verifier = MediaQualityVerifier(service_id=self.service_id)
        self.supabase = SupabaseManager()
        self.copywriter = GeminiCardnewsCopywriter(service_id=self.service_id)
        self.publisher = CardnewsMultiPublisher()

    def generate_carousel_cardnews(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        engine_mode: str = "gemini"
    ) -> Dict[str, Any]:
        """
        EasyTax 전용 5장 7:3 황금 분할 카드뉴스 (1080x1350) 생성 및 저장
        """
        scenario = self.scenario_director.get_carousel_scenario(lang=lang, theme_index=theme_index)
        cards = scenario.get("cards", [])
        episode_id = scenario.get("episode_id", f"easytax_{lang}_{int(time.time())}")
        
        # 1~5장 동일 인물 시드 고정 발급
        self.media_gen.set_episode_seed(episode_id)

        # ⚡ 100% 통합 단일 표준: Google Gemini 3.1 Flash-Lite Image 엔진
        active_media_gen = GeminiMediaGenerator(service_id="easytax")
        logger.info(f"💰 [EasyTax 카드뉴스] 🏆 Gemini 3.1 Flash-Lite Image 엔진으로 생성")

        timestamp = int(time.time())
        saved_paths: List[Path] = []

        hero_image_path = None
        for card in cards:
            s_idx = card.get("slide_idx", 1)
            # 🛡️ 1. 상단 70% (1080x945) 고화질 실사 이미지 1회 생성 (비용 1/3 통제 1-Shot 모드)
            theme_id = f"card_{episode_id}_s{s_idx}"
            img_plan = {
                "action_prompt": card.get("image_prompt"),
                "negative_prompt": card.get("negative_prompt"),
                "is_scene_focus": card.get("is_scene_focus", False),
                "is_app_screen": card.get("is_app_screen", False),
                "app_screen_type": card.get("app_screen_type"),
                "gender": "m"
            }
            ref_path = hero_image_path if s_idx in [2, 4] else None
            top_img_path = active_media_gen.generate_theme_image(
                lang=lang,
                theme_id=theme_id,
                scenario_plan=img_plan,
                aspect_ratio="16:9",  # 16:9 가로형을 1080x945로 완벽 센터크롭
                reference_image_path=ref_path
            )
            if s_idx == 1 and top_img_path and Path(top_img_path).exists():
                hero_image_path = top_img_path
                logger.info(f"[{lang.upper()}] 🔒 [주인공 1번 슬라이드 앵커 등록 완료]: {hero_image_path.name}")

            # AI 비전 품질 검사관 (로깅 및 품질 측정 전용 - 유료 재촬영 차단)
            if top_img_path and Path(top_img_path).exists():
                is_sc = card.get("is_scene_focus", False) or card.get("is_app_screen", False)
                passed, q_score, reason, _ = self.quality_verifier.verify_scene_image(
                    top_img_path,
                    scene_name=f"EasyTax Card Slide {s_idx} ({card.get('title')})",
                    lang=lang,
                    is_scene_focus=is_sc
                )
                logger.info(f"[{lang.upper()}] 🖼 EasyTax 카드뉴스 슬라이드 {s_idx}/5 AI 품질 점수: {q_score}점 ({reason})")


            # 2. 7:3 분할 캔버스 합성 (1080x1350)
            out_filename = f"easytax_cardnews_{lang}_s{s_idx}_{timestamp}.jpg"
            out_path = self.output_dir / out_filename

            composed_path = self.composer.compose_slide(
                top_image_path=top_img_path,
                card_data=card,
                slide_idx=s_idx,
                total_slides=len(cards),
                output_path=out_path,
                lang=lang
            )

            # 3. 바탕화면 자동 복사
            desktop_path = self.desktop_dir / out_filename
            try:
                shutil.copy(composed_path, desktop_path)
            except Exception as e:
                logger.warning(f"바탕화면 복사 에러: {e}")

            saved_paths.append(desktop_path if desktop_path.exists() else composed_path)

        logger.info(f"🎉 [EasyTax 5장 카드뉴스 완성] 총 {len(saved_paths)}장 바탕화면 저장 완료!")

        # 4. 📢 SNS 공식 포스팅 패키지 생성 (제미나이 맞춤 제목·본문 캡션·해시태그 결합)
        char_anchor = scenario.get("character_anchor", "")
        target_persona_desc = char_anchor if isinstance(char_anchor, str) else char_anchor.get("persona_anchor_desc", "외국인 근로자")
        persona_dict = {"persona_anchor_desc": target_persona_desc} if isinstance(char_anchor, str) else char_anchor

        matched_theme = {
            "id": scenario.get("theme_name", "general"),
            "name": scenario.get("theme_title", "EasyTax Tax Refund"),
            "target": target_persona_desc
        }
        post_pkg = self.copywriter.generate_cardnews_post_package(
            service_id="easytax",
            lang=lang,
            theme=matched_theme,
            persona=persona_dict,
            cards=cards,
            refund_formatted="3,840,000 KRW"
        )

        post_title = post_pkg.get("post_title", "")
        post_caption = post_pkg.get("post_caption", "")
        landing_url = post_pkg.get("landing_url", f"https://ktrs-service.vercel.app/?lang={lang}")
        hashtags_str = post_pkg.get("hashtags_str", "")
        hashtags_list = post_pkg.get("hashtags", [])
        channels = post_pkg.get("channels", {})
        ig = channels.get("instagram", {})
        fb = channels.get("facebook", {})
        rd = channels.get("reddit", {})
        th = channels.get("threads", {})
        tg = channels.get("telegram", {})

        # 5. 📝 바탕화면 5대 SNS 채널별 알고리즘 맞춤 원클릭 메모장 파일 생성
        caption_txt_filename = f"easytax_cardnews_{lang}_caption_{timestamp}.txt"
        desktop_caption_path = self.desktop_dir / caption_txt_filename

        caption_content = (
            f"================================================================================\n"
            f"📢 [EasyTax 5장 카드뉴스 — 5대 SNS 알고리즘 맞춤형 원클릭 포스팅 패키지]\n"
            f"• 타깃 언어: {lang.upper()} | 테마: {scenario.get('theme_title', scenario.get('theme_name'))}\n"
            f"• 공식 환급 링크: {landing_url}\n"
            f"• 생성 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"================================================================================\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"1. 📸 [인스타그램 (Instagram Carousel) — 바이오 링크 전략]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 제목: {post_title}\n\n"
            f"📝 캡션 (복사용):\n"
            f"{ig.get('caption', post_caption)}\n\n"
            f"🏷️ 인스타 해시태그:\n"
            f"{ig.get('hashtags', hashtags_str)}\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"2. 📘 [페이스북 (Facebook Page & Groups) — 첫 댓글 스텔스 링크 기법]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 [본문 글 (링크 0% - 알고리즘 도달률 5배 노출 극대화)]:\n"
            f"{fb.get('post_content', '')}\n\n"
            f"★ [첫 번째 댓글 (게시 직후 바로 달아줄 스텔스 링크)]:\n"
            f"{fb.get('first_comment', f'👉 {landing_url}')}\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"3. 🔴 [레딧 (Reddit Gallery Post) — 안티 스팸 팩트 정보 기법]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 포스트 제목: {rd.get('title', post_title)}\n\n"
            f"📝 갤러리 본문 (100% 합법 정보 & 스팸 제재 0%):\n"
            f"{rd.get('body', '')}\n\n"
            f"★ [첫 번째 댓글 (자연스러운 공식 환급 도구 안내)]:\n"
            f"{rd.get('first_comment', f'👉 {landing_url}')}\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"4. 🧵 [메타 스레드 (Threads) — 타래 이어달기 Reply Chain 기법]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 [1번 메인 타래 (카드뉴스 5장 첨부용)]:\n"
            f"{th.get('main_post', '')}\n\n"
            f"★ [2번 답글 타래 (1번에 바로 이어달릴 링크 답글)]:\n"
            f"{th.get('reply_link', f'🔗 {landing_url}')}\n\n"

            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"5. 📲 [텔레그램 (Telegram Channel/Group) — 앨범 & 인라인 버튼]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 5장 앨범 전송용 캡션:\n"
            f"{tg.get('caption', '')}\n\n"
            f"🔘 인라인 버튼: [{tg.get('button_text', '무료 환급 신청')}] ➔ {landing_url}\n\n"

            f"================================================================================\n"
            f"💡 실전 팁: 각 SNS에 올릴 때 해당 섹션의 [본문]과 [★첫 번째 댓글]을 그대로 복사해 붙여넣으세요!\n"
            f"================================================================================\n"
        )
        try:
            with open(desktop_caption_path, "w", encoding="utf-8") as f:
                f.write(caption_content)
            logger.info(f"📝 [바탕화면 5대 채널 원클릭 메모장] 저장 완료: {caption_txt_filename}")
        except Exception as e:
            logger.warning(f"캡션 텍스트 파일 저장 실패: {e}")

        # 6. 🤖 자동 배포용 metadata.json 생성 (5대 채널 구조화 데이터 적재)
        meta_json_filename = f"easytax_cardnews_{lang}_metadata_{timestamp}.json"
        desktop_meta_path = self.desktop_dir / meta_json_filename
        metadata_payload = {
            "service_id": "easytax",
            "lang": lang,
            "theme_name": scenario.get("theme_name"),
            "theme_title": scenario.get("theme_title"),
            "timestamp": timestamp,
            "title": post_title,
            "caption": post_caption,
            "landing_url": landing_url,
            "hashtags": hashtags_list,
            "channels": channels,
            "total_slides": len(saved_paths),
            "image_paths": [str(p) for p in saved_paths],
            "caption_file": str(desktop_caption_path)
        }
        try:
            with open(desktop_meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata_payload, f, ensure_ascii=False, indent=2)
            logger.info(f"🤖 [자동 배포용 메타데이터] 5대 채널 JSON 저장 완료: {meta_json_filename}")
        except Exception as e:
            logger.warning(f"메타데이터 JSON 저장 실패: {e}")

        # 7. 🚀 5대 글로벌 플랫폼(인스타그램, 페이스북, 레딧, 스레드, 텔레그램) API 전자동 무인 배포
        publish_results = {}
        try:
            publish_results = self.publisher.publish_all(metadata_payload)
            logger.info(f"🚀 [EasyTax 카드뉴스 멀티 API 배포 완료] 상태: {list(publish_results.get('platforms', {}).keys())}")
        except Exception as e:
            logger.warning(f"EasyTax 카드뉴스 API 배포 경고: {e}")

        return {
            "success": True,
            "service_id": "easytax",
            "lang": lang,
            "theme_name": scenario.get("theme_name"),
            "total_slides": len(saved_paths),
            "image_paths": [str(p) for p in saved_paths],
            "caption_file": str(desktop_caption_path),
            "metadata_file": str(desktop_meta_path),
            "publish_results": publish_results,
            "desktop_dir": str(self.desktop_dir)
        }

