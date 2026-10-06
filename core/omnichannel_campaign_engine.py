import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    DATA_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS,
    get_weighted_language
)
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.tts_engine import TTSEngine
from core.direct_uploader import DirectUploader
from core.trend_scraper import ViralTrendScraper
from modules.shorts_video_factory import ShortsVideoFactory
from modules.cardnews_generator import CardnewsGenerator
from core.gemini_kmarket import KMarketGeminiEngine
from core.gemini_easytax import EasyTaxGeminiEngine

logger = logging.getLogger("OmnichannelEngine")

class OmnichannelCampaignEngine:
    """
    🌐 [360도 전방위 옴니채널 원소스-멀티배포 통합 엔진]
    - 1회 고품질 제작 (9:16 세로 숏폼 MP4 + 4장 캐러셀 카드뉴스 PNG)
    - 5대 메이저 플랫폼 동시 배포 패키징:
      ① YouTube Shorts
      ② TikTok
      ③ Instagram Reels & Carousel
      ④ Facebook Page & Reels
      ⑤ Reddit Video & Megathread Post
      ⑥ Telegram Broadcast
    """
    def __init__(self, db_mgr: Optional[DBManager] = None, supabase_mgr: Optional[SupabaseManager] = None):
        self.db_mgr = db_mgr or DBManager()
        self.supabase_mgr = supabase_mgr or SupabaseManager(self.db_mgr)
        self.router = ServiceRouter()
        self.tts = TTSEngine()
        self.trend_scraper = ViralTrendScraper()
        self.uploader = DirectUploader()
        
        self.gemini_kmarket = KMarketGeminiEngine(self.supabase_mgr)
        self.gemini_easytax = EasyTaxGeminiEngine(self.supabase_mgr)
        
        # Shorts & Cardnews Factories
        self.kmarket_shorts_factory = ShortsVideoFactory(self.db_mgr, self.router, self.gemini_kmarket, self.tts)
        self.easytax_shorts_factory = ShortsVideoFactory(self.db_mgr, self.router, self.gemini_easytax, self.tts)
        self.cardnews_gen = CardnewsGenerator(self.db_mgr, self.router)

    def execute_campaign(self, service_id: str = "kmarket", target_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        1개 브랜드(kmarket or easytax)에 대해 최상급 숏폼 + 카드뉴스를 렌더링하고
        5대 플랫폼 동시 배포 번들을 빌드 & 전송
        """
        if not target_lang:
            target_lang = get_weighted_language(service_id)

        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        service_data = self.router.get_service(service_id)
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"\n========================================================")
        logger.info(f"🚀 [Omnichannel Engine] {service_id.upper()} ({lang_info['name']}) 360도 캠페인 가동")
        logger.info(f"========================================================")

        campaign_result = {
            "service_id": service_id,
            "target_lang": target_lang,
            "timestamp": now_str,
            "shorts_video": None,
            "cardnews_slides": [],
            "channels": {
                "youtube": {"status": "ready", "title": "", "url": None},
                "tiktok": {"status": "ready", "caption": "", "hashtags": []},
                "instagram": {"status": "ready", "reels_ready": False, "carousel_ready": False},
                "facebook": {"status": "ready", "page_post_ready": False},
                "reddit": {"status": "ready", "thread_title": "", "subreddits": []},
                "telegram": {"status": "ready", "broadcast_ready": False}
            }
        }

        # 1. 고화질 9:16 세로 숏폼 영상 (MP4) 렌더링
        logger.info("🎬 [1단계] 9:16 세로 숏폼 비디오(MP4) 렌더링 중...")
        factory = self.easytax_shorts_factory if service_id == "easytax" else self.kmarket_shorts_factory
        shorts_list = factory.produce_shorts(service_id=service_id, target_langs=[target_lang])

        if shorts_list:
            shorts_item = shorts_list[0]
            campaign_result["shorts_video"] = {
                "file_path": shorts_item.get("file_path"),
                "hook_title": shorts_item.get("hook_title"),
                "voiceover": shorts_item.get("voiceover"),
                "hashtags": shorts_item.get("hashtags", []),
                "duration": shorts_item.get("duration", 30)
            }
            logger.info(f"✅ 숏폼 MP4 렌더링 완료: {shorts_item.get('file_path')}")

        # 2. 1080x1080 4장 캐러셀 카드뉴스 (PNG) 렌더링
        logger.info("🖼️ [2단계] 1080x1080 4장 캐러셀 카드뉴스 렌더링 중...")
        cards = self.cardnews_gen.generate_carousel(service_id=service_id, lang=target_lang)
        campaign_result["cardnews_slides"] = [str(c) for c in cards]
        logger.info(f"✅ 카드뉴스 {len(cards)}장 렌더링 완료")

        # 3. 5대 플랫폼 맞춤형 메타데이터 & 해시태그 패키징
        viral_tags = self.trend_scraper.get_viral_hashtags(service_id, target_lang, count=8)
        hook_title = campaign_result["shorts_video"]["hook_title"] if campaign_result["shorts_video"] else f"{service_data['name']} Korea Expat Guide"

        # A. YouTube Shorts
        yt_desc = f"{hook_title}\n\nSearch '{service_data['name']}' on Google to access all features.\n\n" + " ".join([f"#{t}" for t in viral_tags])
        campaign_result["channels"]["youtube"] = {
            "status": "packaged",
            "title": f"{hook_title} #Shorts",
            "description": yt_desc,
            "tags": viral_tags,
            "video_path": campaign_result["shorts_video"]["file_path"] if campaign_result["shorts_video"] else None
        }

        # B. TikTok
        campaign_result["channels"]["tiktok"] = {
            "status": "packaged",
            "caption": f"{hook_title} #korea #expatlife #lifeinkorea " + " ".join([f"#{t}" for t in viral_tags[:5]]),
            "video_path": campaign_result["shorts_video"]["file_path"] if campaign_result["shorts_video"] else None
        }

        # C. Instagram (Reels & Carousel)
        campaign_result["channels"]["instagram"] = {
            "status": "packaged",
            "reels_video": campaign_result["shorts_video"]["file_path"] if campaign_result["shorts_video"] else None,
            "carousel_images": campaign_result["cardnews_slides"],
            "caption": f"📌 {hook_title}\n\nCheck the link in bio for full details!\n\n" + " ".join([f"#{t}" for t in viral_tags])
        }

        # D. Facebook (Page Post)
        campaign_result["channels"]["facebook"] = {
            "status": "packaged",
            "video_path": campaign_result["shorts_video"]["file_path"] if campaign_result["shorts_video"] else None,
            "carousel_images": campaign_result["cardnews_slides"],
            "post_text": f"📢 [Korea Expat Guide] {hook_title}\n\nFind out more by searching '{service_data['name']}' on Google!"
        }

        # E. Reddit (Video Post & Megathread)
        reddit_subs = ["r/StudyinKorea", "r/teachinginkorea", "r/Korean", "r/Living_in_Korea"] if service_id == "easytax" else ["r/Living_in_Korea", "r/korea", "r/seoul", "r/StudyinKorea"]
        campaign_result["channels"]["reddit"] = {
            "status": "packaged",
            "thread_title": f"[Guide & Video] {hook_title}",
            "target_subreddits": reddit_subs,
            "video_path": campaign_result["shorts_video"]["file_path"] if campaign_result["shorts_video"] else None,
            "text_content": f"Hey everyone! Created a quick video guide on {hook_title}. For complete details, search '{service_data['name']}' on Google or check my bio link!"
        }

        # F. Telegram
        campaign_result["channels"]["telegram"] = {
            "status": "packaged",
            "broadcast_text": f"🔥 <b>{hook_title}</b>\n\n100% Free guide for expats in Korea.\n\n👉 <a href='{BASE_URLS.get(service_id, 'https://k-market.app')}'>Visit Website</a>",
            "media_path": campaign_result["cardnews_slides"][0] if campaign_result["cardnews_slides"] else None
        }

        # 4. DB 기록
        self.db_mgr.record_history(
            content_type="omnichannel_campaign",
            service_id=service_id,
            target_lang=target_lang,
            title=hook_title,
            content_text=json.dumps(campaign_result["channels"], ensure_ascii=False),
            target_url=BASE_URLS.get(service_id, ""),
            external_id=f"omni_{int(time.time())}"
        )

        logger.info("🎉 [Omnichannel Engine] 5대 플랫폼 동시 배포 번들 패키징 100% 완료!")
        return campaign_result
