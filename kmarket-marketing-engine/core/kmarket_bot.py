import time
import logging
from config import get_now_kst_str
from typing import Dict, Any, List
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.gemini_kmarket import KMarketGeminiEngine
from core.tts_engine import TTSEngine
from core.notifier import Notifier
from core.direct_uploader import DirectUploader
from modules.reddit_kmarket import KMarketRedditHunter
from modules.shorts_video_factory import ShortsVideoFactory
from modules.cardnews_generator import CardnewsGenerator
from modules.telegram_kmarket import KMarketTelegramPusher
from modules.facebook_kmarket import KMarketFacebookHunter
from modules.blog_kmarket import KMarketBlogPublisher
from modules.threads_kmarket import KMarketThreadsPublisher

logger = logging.getLogger("KMarketBot")

class KMarketGrowthBot:
    """
    🛒 [Bot 1] K-Market 외국인 로컬 라이프 & 0원 나눔 24시간 전담 무인 성장봇
    - 0원 무료나눔 & 무빙세일 270개 실물 매물 숏폼 비디오 대량 생성 (일 3~5회)
    - 4장 캐러셀 실물 사진 카드뉴스 자동 배포
    - 레딧 중고/가구 질문 실시간 감지 & 안내
    - 17개국 텔레그램 0원 나눔 브리핑 발송
    - 100만 명 규모 페이스북 외국인 그룹 첫 댓글 스텔스 침투
    - 17개국어 WordPress/Medium 글로벌 SEO 블로그 칼럼 대량 발행
    - 17개국어 Meta Threads 바이럴 스토리텔링 타래 스레드 배포
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.router = ServiceRouter()
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.tts = TTSEngine()
        self.notifier = Notifier()
        self.uploader = DirectUploader()

        self.shorts_factory = ShortsVideoFactory(self.db_mgr, self.router, self.gemini, self.tts)
        self.cardnews_gen = CardnewsGenerator(self.db_mgr, self.router)
        self.telegram_pusher = KMarketTelegramPusher(self.db_mgr)
        self.reddit_hunter = KMarketRedditHunter(self.db_mgr, self.supabase_mgr)
        self.fb_hunter = KMarketFacebookHunter(self.db_mgr, self.supabase_mgr)
        self.blog_publisher = KMarketBlogPublisher(self.db_mgr, self.supabase_mgr)
        self.threads_publisher = KMarketThreadsPublisher(self.db_mgr, self.supabase_mgr)

        self.running = False
        self.last_run_time = None
        self.cycle_count = 0

    def run_kmarket_cycle(self) -> Dict[str, Any]:
        """K-Market 전담 사이클 1회 실행"""
        self.cycle_count += 1
        now_str = get_now_kst_str()
        self.last_run_time = now_str
        logger.info(f"🛒 [K-Market 봇] 사이클 #{self.cycle_count} 가동 시작 ({now_str})")

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

        # 가중치 기반 타깃 언어 동적 추출 (상위 가중치 3~5개국 우선 + 확률적 롱테일 추출)
        import random
        from config import KMARKET_LANGUAGE_WEIGHTS, get_weighted_language
        langs_pool = list(KMARKET_LANGUAGE_WEIGHTS.keys())
        weights_pool = list(KMARKET_LANGUAGE_WEIGHTS.values())
        sampled_langs = list(set(random.choices(langs_pool, weights=weights_pool, k=4)))
        if "vi" not in sampled_langs: sampled_langs.append("vi")
        if "zh" not in sampled_langs: sampled_langs.append("zh")

        # 1. 270개 실물 매물 사진 기반 0원 나눔 숏폼 생성
        try:
            shorts = self.shorts_factory.produce_shorts(service_id="kmarket", target_langs=sampled_langs)
            results["shorts_count"] = len(shorts)
        except Exception as e:
            logger.error(f"K-Market 숏폼 생성 에러: {e}")

        # 2. 4장 캐러셀 실물 카드뉴스 생성
        try:
            cards = self.cardnews_gen.generate_carousel(service_id="kmarket", lang=sampled_langs[0])
            results["cardnews_count"] = len(cards)
            logger.info(f"✅ [K-Market 봇] 카드뉴스 {len(cards)}장 렌더링 완료")
        except Exception as e:
            logger.error(f"K-Market 카드뉴스 생성 에러: {e}")

        # 3. 레딧 중고/가구 질문 실시간 스캔 & 안내
        try:
            replied = self.reddit_hunter.scan_and_reply(limit=3)
            results["reddit_count"] = replied
        except Exception as e:
            logger.error(f"K-Market 레딧 스캔 에러: {e}")

        # 4. 17개국 텔레그램 0원 나눔 브리핑 발송 (가중치 언어들)
        try:
            tg_res = self.telegram_pusher.broadcast_daily_deals(target_langs=sampled_langs[:3])
            results["telegram_count"] = tg_res.get("sent_count", 0)
        except Exception as e:
            logger.error(f"K-Market 텔레그램 발송 에러: {e}")

        # 5. 페이스북 대형 그룹 스텔스 침투
        try:
            fb_res = self.fb_hunter.deploy_to_groups(limit=2)
            results["facebook_count"] = fb_res.get("posted_count", 0) + fb_res.get("pending_count", 0)
        except Exception as e:
            logger.error(f"K-Market 페이스북 배포 에러: {e}")

        # 6. 17개국어 글로벌 SEO 블로그 칼럼 발행 (가중치 언어들)
        try:
            blog_res = self.blog_publisher.publish_daily_articles(target_langs=sampled_langs[:3])
            results["blog_count"] = blog_res.get("count", 0)
        except Exception as e:
            logger.error(f"K-Market 블로그 발행 에러: {e}")

        # 7. 17개국어 Meta Threads 바이럴 스레드 배포
        try:
            th_res = self.threads_publisher.publish_daily_threads(target_langs=sampled_langs[:3])
            results["threads_count"] = th_res.get("count", 0)
        except Exception as e:
            logger.error(f"K-Market Threads 배포 에러: {e}")

        return results
