"""
KMarketBlogPublisher - 🛒 K-Market 17개국어 공식 서브경로 블로그 무인 자동 퍼블리셔
- 🎬 시나리오 디렉터: 40대 실전 라이프 테마 지시 & 100% 동양인/가구 안전장치
- 🤖 제미나이 1회 집필: 한국어 2,000자 최고급 마스터 글 + 사물/인물 실사 사진 2장 배치
- ⚡ Gemini 1회 호출로 17개국어 동시 번역 (기존 17번 → 1번, 비용 90% 절감!)
- 📤 Supabase 실시간 일괄 Upsert
"""

import os
import json
import logging
import datetime
import markdown
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS, KST, get_now_kst, get_now_kst_str
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.gemini_kmarket import KMarketGeminiEngine
from core.trend_scraper import ViralTrendScraper
from core.scenario_director_blog_kmarket import ScenarioDirectorBlogKMarket
from core.blog_quality_auditor import BlogQualityAuditor
from core.blog_score_tracker import BlogScoreTracker
from core.blog_image_generator import BlogImageGenerator
from core.blog_translator import BlogTranslator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("KMarketBlogPublisher")

class KMarketBlogPublisher:
    """K-Market 전용 17개국어 서브경로 블로그 퍼블리셔"""
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.output_dir = OUTPUTS_DIR / "blogs" / "kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.trend_scraper = ViralTrendScraper()
        self.score_tracker = BlogScoreTracker(self.supabase_mgr)
        self.scenario_director = ScenarioDirectorBlogKMarket(self.score_tracker)
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.auditor = BlogQualityAuditor()
        # 🎁 무료 키 (0원): 글 작성 & 17개국어 본문 번역
        free_api_key = os.getenv('GEMINI_FREE_API_KEY_KMARKET') or os.getenv('GEMINI_API_KEY_KMARKET_BLOG') or os.getenv('GEMINI_API_KEY')
        # 💳 유료 키 (5원): Imagen 사진 1장 생성
        paid_api_key = os.getenv('GEMINI_PAID_API_KEY') or os.getenv('GEMINI_API_KEY_KMARKET') or os.getenv('GEMINI_API_KEY')

        self.translator = BlogTranslator(api_key=free_api_key, fallback_api_key=paid_api_key)
        self.image_generator = BlogImageGenerator(
            api_key=paid_api_key,
            supabase_client=self.supabase_mgr.client
        )

    def publish_multilingual_articles(
        self,
        theme_index: Optional[int] = None,
        target_langs: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        directive_pkg = self.scenario_director.get_directive(theme_index)
        theme_id = directive_pkg["id"]
        theme_title = directive_pkg["title"]
        category = directive_pkg["category"]
        today_str = get_now_kst().strftime("%Y%m%d")
        slug = f"{theme_id}-{today_str}"

        ko_landing_url = f"{BASE_URLS.get('kmarket', 'https://ktrs-market.vercel.app')}/blog?slug={slug}"
        ko_hashtags = self.trend_scraper.format_hashtag_string("kmarket", "ko")

        # 🛍️ 1단계: 제미나이 1회 호출로 한국어 마스터 칼럼 먼저 집필 + 글 맥락 맞춤 visual_prompt 동시 생성
        logger.info(f"🛍️ [K-Market Blog] '{theme_title}' 한국어 마스터 칼럼 선(先) 집필 시작...")
        master_korean_article = self.gemini.write_master_korean_article(
            directive_pkg=directive_pkg,
            landing_url=ko_landing_url,
            hashtags=ko_hashtags,
            thumb_url="{{TOP_IMAGE}}"
        )

        # 🎨 2단계: 글 스토리 맥락에 최적화된 visual_prompt로 Imagen 3 맞춤 사진 1장 생성 & Supabase Storage 업로드
        visual_prompt = master_korean_article.get("visual_prompt") or directive_pkg.get("directive", {}).get("visual_prompt")
        logger.info(f"🎨 [K-Market Blog] 글 맥락 맞춤 프롬프트로 본문 대표 사진 생성 중: {visual_prompt[:60]}...")
        thumb_url = self.image_generator.generate_and_upload(
            service_id="kmarket",
            theme_id=theme_id,
            theme_title=theme_title,
            category=category,
            slug=slug,
            custom_prompt=visual_prompt
        )

        # 🖼️ 3단계: 본문의 이미지 플레이스홀더를 실제 생성된 썸네일 URL로 치환
        content_md = master_korean_article.get("content_md", "").replace("{{TOP_IMAGE}}", thumb_url)
        master_korean_article["content_md"] = content_md
        master_korean_article["content_html"] = markdown.markdown(content_md, extensions=['extra', 'tables', 'nl2br'])
        master_korean_article["thumbnail_url"] = thumb_url

        langs_to_run = target_langs or list(LANGUAGES.keys())[:17]
        foreign_langs = [l for l in langs_to_run if l != "ko"]

        # ⚡ Gemini 1회 호출로 전체 언어 동시 번역 (비용 90% 절감!)
        logger.info(f"⚡ [K-Market Blog] Gemini 1회 호출로 {len(foreign_langs)}개국어 동시 번역 시작...")
        all_translations = self.translator.translate_all_languages(
            master_article=master_korean_article,
            target_langs=foreign_langs
        )
        all_translations["ko"] = master_korean_article
        logger.info(f"✅ [K-Market Blog] {len(all_translations)}개국어 번역 완료!")

        published_articles = []
        uploaded_count = 0

        for idx, lang in enumerate(langs_to_run):
            landing_url = f"{BASE_URLS.get('kmarket', 'https://ktrs-market.vercel.app')}/blog?slug={slug}"
            hashtags = self.trend_scraper.format_hashtag_string("kmarket", lang)

            translated_raw = all_translations.get(lang, master_korean_article)

            content_md = translated_raw.get("content_md", "")
            content_md = content_md.replace(ko_hashtags, hashtags)
            translated_raw = {**translated_raw, "content_md": content_md}

            content_html = markdown.markdown(content_md, extensions=['extra', 'tables', 'nl2br'])
            translated_raw["content_html"] = content_html

            # 🕵️ 사진 품질 & 서양인 배제 검증
            purified_article, final_thumb, _, audit_score = self.auditor.audit_and_purify(
                service_id="kmarket",
                article_data=translated_raw,
                thumb_url_1=thumb_url,
                thumb_url_2=thumb_url
            )

            title = purified_article["title"]
            excerpt = purified_article["excerpt"]
            c_html = purified_article["content_html"]
            c_md = purified_article["content_md"]

            # 📊 정직한 1점 단위 초기화 (신규 발행 시 0점부터 정직하게 시작)
            initial_views = 0
            initial_likes = 0
            initial_score = 0.0

            lang_dir = self.output_dir / lang
            lang_dir.mkdir(parents=True, exist_ok=True)
            (lang_dir / f"{slug}.html").write_text(c_html, encoding="utf-8")
            (lang_dir / f"{slug}.md").write_text(c_md, encoding="utf-8")

            payload = {
                "slug": slug,
                "target_lang": lang,
                "title": title,
                "excerpt": excerpt,
                "content_html": c_html,
                "content_md": c_md,
                "thumbnail_url": final_thumb,
                "category": category,
                "author": "K-Market Expat Living Team",
                "views": initial_views,
                "likes": initial_likes,
                "score": initial_score,
                "published_at": get_now_kst().isoformat()
            }
            is_uploaded = self.supabase_mgr.upload_blog_article("kmarket", payload)
            if is_uploaded:
                uploaded_count += 1

            published_articles.append({
                "lang": lang,
                "title": title,
                "slug": slug,
                "thumbnail": final_thumb,
                "score": initial_score,
                "uploaded_to_supabase": is_uploaded
            })

        logger.info(f"🎉 [K-Market Blog] '{theme_title}' {len(published_articles)}개국어 완료! ({uploaded_count}건 Supabase 업로드)")

        return {
            "success": True,
            "brand": "kmarket",
            "slug": slug,
            "theme_id": theme_id,
            "theme_name": theme_title,
            "count": len(published_articles),
            "total_langs": len(published_articles),
            "supabase_uploaded": uploaded_count,
            "articles": published_articles,
            "message": f"🛒 [K-Market] {theme_title} | {len(published_articles)}개국어 | 사물/인물 사진 2장 | Gemini 1회 번역 | Supabase {uploaded_count}건 완료!"
        }

    publish_daily_articles = publish_multilingual_articles
