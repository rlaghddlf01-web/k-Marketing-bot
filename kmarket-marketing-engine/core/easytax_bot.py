import time
import logging
import datetime
from typing import Dict, Any, List
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.gemini_easytax import EasyTaxGeminiEngine
from core.tts_engine import TTSEngine
from core.notifier import Notifier
from core.direct_uploader import DirectUploader
from modules.reddit_easytax import EasyTaxRedditHunter
from modules.shorts_video_factory import ShortsVideoFactory
from modules.cardnews_generator import CardnewsGenerator
from modules.guide_pdf_generator import GuidePDFGenerator
from modules.telegram_easytax import EasyTaxTelegramPusher
from modules.facebook_easytax import EasyTaxFacebookHunter
from modules.blog_easytax import EasyTaxBlogPublisher

logger = logging.getLogger("EasyTaxBot")

class EasyTaxRefundBot:
    """
    💰 [Bot 2] EasyTax (KTRS) 국세청 외국인 세금 환급 24시간 전담 무인 봇
    - E-9 중소기업 90% 감면 & D-2 알바 3.3% 환급 숏폼 가이드 정밀 발행
    - Anti-Ban 공인 세무대리 4장 카드뉴스 배포
    - 외국인 세금/비자 질문 실시간 감지 & 100% 팩트 법률 답변 (조특법 30조 등)
    - 17개국 텔레그램 세무 팁 브리핑 발송
    - 100만 명 규모 페이스북 외국인 그룹 첫 댓글 스텔스 침투
    - 17개국어 WordPress/Medium 공인 세무 SEO 블로그 칼럼 대량 발행
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.router = ServiceRouter()
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        self.tts = TTSEngine()
        self.notifier = Notifier()
        self.uploader = DirectUploader()

        self.shorts_factory = ShortsVideoFactory(self.db_mgr, self.router, self.gemini, self.tts)
        self.cardnews_gen = CardnewsGenerator(self.db_mgr, self.router)
        self.pdf_gen = GuidePDFGenerator(self.db_mgr)
        self.telegram_pusher = EasyTaxTelegramPusher(self.db_mgr)
        self.reddit_hunter = EasyTaxRedditHunter(self.db_mgr, self.supabase_mgr)
        self.fb_hunter = EasyTaxFacebookHunter(self.db_mgr, self.supabase_mgr)
        self.blog_publisher = EasyTaxBlogPublisher(self.db_mgr, self.supabase_mgr)

        self.running = False
        self.last_run_time = None
        self.cycle_count = 0

    def run_easytax_cycle(self) -> Dict[str, Any]:
        """EasyTax 전담 사이클 1회 실행"""
        self.cycle_count += 1
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_run_time = now_str
        logger.info(f"💰 [EasyTax 봇] 사이클 #{self.cycle_count} 가동 시작 ({now_str})")

        results = {
            "cycle": self.cycle_count,
            "timestamp": now_str,
            "shorts_count": 0,
            "cardnews_count": 0,
            "reddit_count": 0,
            "telegram_count": 0,
            "facebook_count": 0,
            "blog_count": 0
        }

        # 1. 5개년 세무 환급 & E-9 90% 감면 가이드 숏폼 생성
        try:
            shorts = self.shorts_factory.produce_shorts(service_id="easytax", target_langs=["vi", "en", "zh"])
            results["shorts_count"] = len(shorts)
        except Exception as e:
            logger.error(f"EasyTax 숏폼 생성 에러: {e}")

        # 2. Anti-Ban 공인 세무 카드뉴스 4장 세트 생성
        try:
            cards = self.cardnews_gen.generate_carousel(service_id="easytax", lang="en")
            results["cardnews_count"] = len(cards)
        except Exception as e:
            logger.error(f"EasyTax 카드뉴스 생성 에러: {e}")

        # 3. 비자/세금 질문 실시간 스캔 & 팩트 법률 답변
        try:
            replied = self.reddit_hunter.scan_and_reply(limit=3)
            results["reddit_count"] = replied
        except Exception as e:
            logger.error(f"EasyTax 레딧 스캔 에러: {e}")

        # 4. 17개국 텔레그램 세무 팁 브리핑 발송
        try:
            tg_res = self.telegram_pusher.broadcast_daily_tax_tips(target_langs=["en", "vi", "ko"])
            results["telegram_count"] = tg_res.get("sent_count", 0)
        except Exception as e:
            logger.error(f"EasyTax 텔레그램 발송 에러: {e}")

        # 5. 페이스북 대형 그룹 스텔스 침투
        try:
            fb_res = self.fb_hunter.deploy_to_groups(limit=2)
            results["facebook_count"] = fb_res.get("posted_count", 0) + fb_res.get("pending_count", 0)
        except Exception as e:
            logger.error(f"EasyTax 페이스북 배포 에러: {e}")

        # 6. 17개국어 글로벌 SEO 세무 블로그 칼럼 발행
        try:
            blog_res = self.blog_publisher.publish_daily_articles(target_langs=["en", "vi", "ko"])
            results["blog_count"] = blog_res.get("count", 0)
        except Exception as e:
            logger.error(f"EasyTax 블로그 발행 에러: {e}")

        return results
