import time
import logging
import datetime
from typing import Dict, Any, List
from config import BASE_URLS
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
from modules.threads_easytax import EasyTaxThreadsPublisher

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
    - 17개국어 Meta Threads 합법 세무 권리 타래 스레드 배포
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
        self.threads_publisher = EasyTaxThreadsPublisher(self.db_mgr, self.supabase_mgr)

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

        # 가중치 기반 오늘 최적의 타깃 1개 언어 추출 (베트남 25%, 우즈벡 14%, 중국 12% 등)
        from config import get_weighted_language
        chosen_lang = get_weighted_language("easytax")
        logger.info(f"🎯 [EasyTax 봇 타깃 언어] {chosen_lang.upper()} 선정 (인구통계 가중치 1위)")

        # 1. 5개년 세무 환급 숏폼 영상 1개 정밀 생성
        try:
            shorts = self.shorts_factory.produce_shorts(service_id="easytax", target_langs=[chosen_lang])
            results["shorts_count"] = len(shorts)
        except Exception as e:
            logger.error(f"EasyTax 숏폼 생성 에러: {e}")

        # 2. 4장 캐러셀 세무 카드뉴스 생성
        try:
            cards = self.cardnews_gen.generate_carousel(service_id="easytax", lang=chosen_lang)
            results["cardnews_count"] = len(cards)
            logger.info(f"✅ [EasyTax 봇] 세무 카드뉴스 {len(cards)}장 렌더링 완료")
        except Exception as e:
            logger.error(f"EasyTax 카드뉴스 생성 에러: {e}")

        # 3. 비자/세금 질문 실시간 스캔 & 팩트 법률 답변
        try:
            replied = self.reddit_hunter.scan_and_reply(limit=3)
            results["reddit_count"] = replied
        except Exception as e:
            logger.error(f"EasyTax 레딧 스캔 에러: {e}")

        # 4. 17개국 텔레그램 세무 팁 브리핑 발송 (선정된 타깃 언어)
        try:
            tg_res = self.telegram_pusher.broadcast_daily_tax_tips(target_langs=[chosen_lang])
            results["telegram_count"] = tg_res.get("sent_count", 0)
        except Exception as e:
            logger.error(f"EasyTax 텔레그램 발송 에러: {e}")

        # 5. 페이스북 대형 그룹 스텔스 침투
        try:
            fb_res = self.fb_hunter.deploy_to_groups(limit=2)
            results["facebook_count"] = fb_res.get("posted_count", 0) + fb_res.get("pending_count", 0)
        except Exception as e:
            logger.error(f"EasyTax 페이스북 배포 에러: {e}")

        # 6. 17개국어 글로벌 SEO 세무 블로그 칼럼 발행 (선정된 타깃 언어)
        try:
            blog_res = self.blog_publisher.publish_daily_articles(target_langs=[chosen_lang])
            results["blog_count"] = blog_res.get("count", 0)
        except Exception as e:
            logger.error(f"EasyTax 블로그 발행 에러: {e}")

        # 7. 17개국어 Meta Threads 합법 세무 권리 스레드 배포
        try:
            th_res = self.threads_publisher.publish_daily_threads(target_langs=[chosen_lang])
            results["threads_count"] = th_res.get("count", 0)
        except Exception as e:
            logger.error(f"EasyTax Threads 배포 에러: {e}")

        # 8. 이탈 고객 15분 자동 복구 SMS & 메신저 케어 실시간 트리거
        try:
            import urllib.request
            cron_url = f"{BASE_URLS.get('easytax', 'https://ktrs-service.vercel.app')}/api/cron/follow-up"
            req = urllib.request.Request(cron_url, headers={"User-Agent": "KTRS-Marketing-Daemon/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info(f"📲 [EasyTax] 15분 이탈 고객 자동 복구 SMS/메신저 트리거 성공 (HTTP {resp.status})")
        except Exception as e:
            logger.warning(f"EasyTax 이탈 고객 SMS 트리거 알림: {e}")

        return results
