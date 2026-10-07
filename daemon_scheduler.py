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
from config import KMARKET_LANGUAGES, EASYTAX_LANGUAGES, get_next_golden_eight_language, GOLDEN_EIGHT_DETAILS, GOLDEN_EIGHT_LANGUAGES
from core.golden_batch_producer import GoldenBatchProducer


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
    def __init__(self, brand: str = "all"):
        self.target_brand = brand
        brand_label = "EasyTax 전용" if brand == "easytax" else "K-Market 전용" if brand == "kmarket" else "듀얼 채널 통합"
        logger.info(f"[Universal Expat Growth Engine] {brand_label} 무인 데몬 가동 준비 중...")
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
        self.golden_batch_producer = GoldenBatchProducer()

        self.last_morning_briefing_date = None
        self.last_evening_briefing_date = None
        self.last_shorts_hour = None
        self.last_cardnews_hour = None
        # 하루 3회 블로그 발행 기록 (09시, 14시, 19시)
        self.blog_published_slots = set()
        # 하루 2회 8대 국가 풀가동 슬롯 (morning, evening)
        self.golden_slots_done = set()

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

        # 4. 하루 2대 골든 슬롯 (아침 11:30 & 저녁 18:30) 8개국 대량 생산 (이지텍스 8+8 / KTRS 마켓 8+8)
        # 매 슬롯마다 8개국 숏폼 + 8개국 카드뉴스 완전 무인 렌더링 (일 총 32숏폼 + 32카드뉴스)
        is_morning_slot = (current_hour == 11 and current_minute >= 30) or (current_hour == 12 and current_minute < 30)
        is_evening_slot = (current_hour == 18 and current_minute >= 30) or (current_hour == 19 and current_minute < 30)

        slot_to_run = None
        if is_morning_slot and f"{today_str}_morning" not in self.golden_slots_done:
            slot_to_run = "morning"
        elif is_evening_slot and f"{today_str}_evening" not in self.golden_slots_done:
            slot_to_run = "evening"

        if slot_to_run:
            try:
                target_str = "이지텍스" if self.target_brand == "easytax" else "KTRS 마켓" if self.target_brand == "kmarket" else "듀얼 브랜드"
                logger.info(f"🌟 [{slot_to_run.upper()} 골든 슬롯: {target_str}] 8대 황금 타깃 대량 생산 배치 시작...")
                slot_res = self.golden_batch_producer.execute_slot(slot_name=slot_to_run, brand=self.target_brand)
                self.golden_slots_done.add(f"{today_str}_{slot_to_run}")
                logger.info(
                    f"🌟 [{slot_to_run.upper()} 골든 슬롯 ({target_str}) 완료] "
                    f"숏폼: {slot_res.get('shorts_success', 0)}/{slot_res.get('shorts_total', 0)} 성공, "
                    f"카드뉴스: {slot_res.get('cardnews_success', 0)}/{slot_res.get('cardnews_total', 0)} 성공"
                )
            except Exception as e:
                logger.error(f"골든 슬롯 대량 생산 실패 ({slot_to_run}): {e}")

        # 5. 매시간: Supabase 클라우드 자가학습 데이터 동기화
        try:
            synced = self.supabase_mgr.sync_histories_to_cloud()
            if synced > 0:
                logger.info(f"Supabase 클라우드 자가학습 데이터 {synced}건 실시간 동기화 완료")
        except Exception as e:
            logger.error(f"클라우드 동기화 실패: {e}")

        logger.info("--- [오토파일럿 루프 완료] ---")

    def start_loop(self, interval_seconds: int = 60):
        """무한 루프로 스케줄러 실행 (기본 60초 주기 체크)"""
        logger.info(f"🔄 [Universal Expat Growth Engine] 오토파일럿 데몬 루프 가동 (체크 주기: {interval_seconds}초)")
        while True:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"오토파일럿 루프 예외 발생: {e}")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Universal Expat Growth Engine Autopilot Daemon")
    parser.add_argument("--brand", type=str, choices=["easytax", "kmarket", "all"], default="all", help="타깃 브랜드 (easytax / kmarket / all)")
    args = parser.parse_args()
    daemon = AutopilotDaemon(brand=args.brand)
    daemon.start_loop(interval_seconds=60)


