import time
import logging
import datetime
from typing import Dict, Any
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.season_tuner import SeasonTuner
from core.gemini_engine import GeminiEngine
from core.tts_engine import TTSEngine
from core.notifier import Notifier
from core.direct_uploader import DirectUploader
from modules.reddit_kmarket import KMarketRedditHunter
from modules.reddit_easytax import EasyTaxRedditHunter
from modules.shorts_easytax import ShortsEasyTax
from modules.shorts_kmarket import ShortsKMarket
from modules.programmatic_seo import ProgrammaticSEO
from modules.cardnews_generator import CardnewsGenerator
from modules.free_stuff_notifier import FreeStuffNotifier
from modules.guide_pdf_generator import GuidePDFGenerator
from modules.social_publisher import SocialPublisher
from modules.blog_kmarket import KMarketBlogPublisher
from modules.blog_easytax import EasyTaxBlogPublisher

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("AutopilotDaemon")

class AutopilotDaemon:
    """
    100% 무인 24시간 완전 자율 마케팅 오토파일럿 데몬
    - 듀얼 채널 7:3 황금 비율 (K-Market 70% + EasyTax 30%)
    - 하루 3회 정기 블로그 발행 (EasyTax 15개국어 3회 + K-Market 17개국어 3회)
    - 브랜드별 분리 발행 및 상호 교차 멘션 자동화
    """
    def __init__(self):
        logger.info("[Universal Expat Growth Engine] 듀얼 채널 무인 데몬 가동 준비 중...")
        self.db_mgr = DBManager()
        self.supabase_mgr = SupabaseManager(self.db_mgr)
        self.router = ServiceRouter()
        self.gemini = GeminiEngine(self.supabase_mgr)
        self.tts = TTSEngine()
        self.notifier = Notifier()
        self.uploader = DirectUploader()

        # 무인 모듈 인스턴스화 (K-Market / EasyTax 완전 분리)
        self.km_reddit = KMarketRedditHunter(self.db_mgr, self.supabase_mgr)
        self.tax_reddit = EasyTaxRedditHunter(self.db_mgr, self.supabase_mgr)
        self.shorts_easytax = ShortsEasyTax()
        self.shorts_kmarket = ShortsKMarket()
        self.seo_engine = ProgrammaticSEO(self.db_mgr)
        self.cardnews_gen = CardnewsGenerator(self.db_mgr, self.router)
        self.free_notifier = FreeStuffNotifier(self.db_mgr, self.notifier)
        self.pdf_gen = GuidePDFGenerator(self.db_mgr)
        self.publisher = SocialPublisher(self.db_mgr, self.notifier)
        self.km_blog = KMarketBlogPublisher(self.db_mgr, self.supabase_mgr)
        self.tax_blog = EasyTaxBlogPublisher(self.db_mgr, self.supabase_mgr)

        self.last_morning_briefing_date = None
        self.last_evening_briefing_date = None
        self.last_shorts_hour = None
        self.last_cardnews_hour = None
        # 하루 3회 블로그 발행 기록 (09시, 14시, 19시)
        self.blog_published_slots = set()

    def run_cycle(self):
        """1회 스케줄 사이클 실행 (듀얼 채널 7:3 자동화 + 하루 3회 정기 블로그)"""
        now = datetime.datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        today_str = now.strftime("%Y-%m-%d")

        logger.info(f"--- [오토파일럿 루프 시작: {now.strftime('%Y-%m-%d %H:%M:%S')}] ---")

        # 1. 24시간 안전 스케줄 세션 (08시, 10시, 13시, 16시, 20시 인간 활동 분배)
        try:
            km_sess = self.km_reddit.orchestrator.run_scheduled_session(current_hour)
            tax_sess = self.tax_reddit.orchestrator.run_scheduled_session(current_hour)
            if km_sess.get("status") != "already_executed":
                logger.info(f"🛒 [K-Market Reddit 세션 완료] 슬롯: {km_sess.get('slot_key')}, 업보트: {km_sess.get('upvotes')}건, 비홍보: {km_sess.get('organic_comments')}건, 홍보: {km_sess.get('promo_comments')}건")
            if tax_sess.get("status") != "already_executed":
                logger.info(f"💰 [EasyTax Reddit 세션 완료] 슬롯: {tax_sess.get('slot_key')}, 업보트: {tax_sess.get('upvotes')}건, 비홍보: {tax_sess.get('organic_comments')}건, 홍보: {tax_sess.get('promo_comments')}건")
        except Exception as e:
            logger.error(f"레딧 스케줄 세션 실패: {e}")
            self.notifier.send_sos_alert("RedditOrchestrator", str(e))

        # 1-1. 상시 작업 (매 10~15분): EasyTax 이탈 고객 15분 후속 알림 & 문자(SMS) 자동 트리거
        try:
            import urllib.request
            cron_url = "https://ktrs-service.vercel.app/api/cron/follow-up"
            req = urllib.request.Request(cron_url, headers={"User-Agent": "KTRS-Marketing-Daemon/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info(f"[EasyTax] 15분 이탈 고객 자동 복구 SMS/메신저 엔진 가동 완료 (HTTP {resp.status})")
        except Exception as e:
            logger.warning(f"EasyTax 이탈 고객 SMS 트리거 알림: {e}")

        # 2. 매일 2회 정기 텔레그램 토픽 브리핑 (아침 08:40 출근/등교 직후 & 저녁 20:00 퇴근/휴식 피크)
        is_morning_slot = (current_hour == 8 and current_minute >= 40) or (current_hour == 9 and current_minute < 30)
        if is_morning_slot and self.last_morning_briefing_date != today_str:
            try:
                from modules.telegram_kmarket import KMarketTelegramPusher
                from modules.telegram_easytax import EasyTaxTelegramPusher
                kp = KMarketTelegramPusher(self.db_mgr)
                ep = EasyTaxTelegramPusher(self.db_mgr)
                kp.broadcast_daily_deals(["vi", "uz", "ru", "mn", "en"])
                ep.broadcast_daily_tax_tips(["vi", "uz", "ru", "mn", "en"])
                self.free_notifier.generate_daily_briefing()
                self.last_morning_briefing_date = today_str
                logger.info("🌅 [아침 08:40] 텔레그램 5개 언어 토픽 브리핑 1회차 자동 발송 완료!")
            except Exception as e:
                logger.error(f"아침 텔레그램 브리핑 실패: {e}")

        if current_hour == 20 and self.last_evening_briefing_date != today_str:
            try:
                from modules.telegram_kmarket import KMarketTelegramPusher
                from modules.telegram_easytax import EasyTaxTelegramPusher
                kp = KMarketTelegramPusher(self.db_mgr)
                ep = EasyTaxTelegramPusher(self.db_mgr)
                kp.broadcast_daily_deals(["vi", "uz", "ru", "mn", "en"])
                ep.broadcast_daily_tax_tips(["vi", "uz", "ru", "mn", "en"])
                self.last_evening_briefing_date = today_str
                logger.info("🌙 [저녁 20시] 텔레그램 5개 언어 토픽 브리핑 2회차 (저녁 피크) 자동 발송 완료!")
            except Exception as e:
                logger.error(f"저녁 텔레그램 브리핑 실패: {e}")

        # 3. 하루 3대 골든 타임 (09시, 14시, 19시) 블로그 정기 발행
        # EasyTax 15개국어 3회 / K-Market 17개국어 3회
        blog_slot_key = f"{today_str}_{current_hour}"
        if current_hour in [9, 14, 19] and blog_slot_key not in self.blog_published_slots:
            try:
                logger.info(f"[{current_hour}시 정기 블로그 발행 시작] EasyTax 15개국어 + K-Market 17개국어...")
                tax_res = self.tax_blog.publish_multilingual_articles()
                km_res = self.km_blog.publish_multilingual_articles()
                self.blog_published_slots.add(blog_slot_key)
                logger.info(f"[{current_hour}시 블로그 발행 완료] EasyTax {tax_res['total_langs']}개국 + K-Market {km_res['total_langs']}개국 업로드 성공!")
            except Exception as e:
                logger.error(f"블로그 정기 발행 실패: {e}")

        # 4. 매일 오후 14시: 듀얼 채널 숏폼 일괄 렌더링 (K-Market 70% + EasyTax 30%)
        if current_hour == 14 and self.last_shorts_hour != 14:
            try:
                # K-Market 공식 채널 (5개 핵심 언어 0원 나눔 & 실물 스크롤 숏폼)
                km_res = [self.shorts_kmarket.produce_shorts(lang=l) for l in ["en", "vi", "zh", "ko", "uz"]]
                # EasyTax 공식 채널 (3개 핵심 언어 90% 감면 숏폼)
                tax_res = [self.shorts_easytax.produce_shorts(lang=l) for l in ["vi", "en", "zh"]]
                
                self.last_shorts_hour = 14
                logger.info(f"오후 14시 듀얼 채널 숏폼 무인 렌더링 완료 (K-Market {len(km_res)}건 + EasyTax {len(tax_res)}건)")
            except Exception as e:
                logger.error(f"숏폼 렌더링 실패: {e}")

        # 5. 매시간: Supabase 클라우드 자가학습 데이터 동기화
        try:
            synced = self.supabase_mgr.sync_histories_to_cloud()
            if synced > 0:
                logger.info(f"Supabase 클라우드 자가학습 데이터 {synced}건 실시간 동기화 완료")
        except Exception as e:
            logger.error(f"클라우드 동기화 실패: {e}")

        logger.info("--- [오토파일럿 루프 완료] ---")
