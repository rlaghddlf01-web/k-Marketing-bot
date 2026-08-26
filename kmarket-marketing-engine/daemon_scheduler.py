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
from modules.reddit_lead_hunter import RedditLeadHunter
from modules.shorts_video_factory import ShortsVideoFactory
from modules.programmatic_seo import ProgrammaticSEO
from modules.cardnews_generator import CardnewsGenerator
from modules.free_stuff_notifier import FreeStuffNotifier
from modules.guide_pdf_generator import GuidePDFGenerator
from modules.social_publisher import SocialPublisher

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("AutopilotDaemon")

class AutopilotDaemon:
    """
    🚀 100% 무인 24시간 완전 자율 마케팅 오토파일럿 데몬
    - 듀얼 채널 7:3 황금 비율 (K-Market 70% + EasyTax 30%)
    - 브랜드별 분리 발행 및 상호 교차 멘션 자동화
    """
    def __init__(self):
        logger.info("🚀 [Universal Expat Growth Engine] 듀얼 채널 무인 데몬 가동 준비 중...")
        self.db_mgr = DBManager()
        self.supabase_mgr = SupabaseManager(self.db_mgr)
        self.router = ServiceRouter()
        self.gemini = GeminiEngine(self.supabase_mgr)
        self.tts = TTSEngine()
        self.notifier = Notifier()
        self.uploader = DirectUploader()

        # 7대 무인 모듈 인스턴스화
        self.reddit_hunter = RedditLeadHunter(self.db_mgr, self.router, self.gemini)
        self.shorts_factory = ShortsVideoFactory(self.db_mgr, self.router, self.gemini, self.tts)
        self.seo_engine = ProgrammaticSEO(self.db_mgr)
        self.cardnews_gen = CardnewsGenerator(self.db_mgr, self.router)
        self.free_notifier = FreeStuffNotifier(self.db_mgr, self.notifier)
        self.pdf_gen = GuidePDFGenerator(self.db_mgr)
        self.publisher = SocialPublisher(self.db_mgr, self.notifier)

        self.last_daily_report_date = None
        self.last_shorts_hour = None
        self.last_cardnews_hour = None

    def run_cycle(self):
        """1회 스케줄 사이클 실행 (듀얼 채널 7:3 자동화)"""
        now = datetime.datetime.now()
        current_hour = now.hour
        today_str = now.strftime("%Y-%m-%d")

        logger.info(f"--- [오토파일럿 루프 시작: {now.strftime('%Y-%m-%d %H:%M:%S')}] ---")

        # 1. 상시 작업 (매 5~10분): 레딧 실시간 질문 스캔 & 답변
        try:
            replied = self.reddit_hunter.scan_and_reply(limit=5)
            logger.info(f"레딧 리드 스캔 완료 ({replied}건 응답)")
        except Exception as e:
            logger.error(f"레딧 스캔 실패: {e}")
            self.notifier.send_sos_alert("RedditLeadHunter", str(e))

        # 1-1. 상시 작업 (매 10~15분): EasyTax 이탈 고객 15분 후속 알림 & 문자(SMS) 자동 트리거
        try:
            import urllib.request
            cron_url = "https://ktrs-service.vercel.app/api/cron/follow-up"
            req = urllib.request.Request(cron_url, headers={"User-Agent": "KTRS-Marketing-Daemon/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info(f"📲 [EasyTax] 15분 이탈 고객 자동 복구 SMS/메신저 엔진 가동 완료 (HTTP {resp.status})")
        except Exception as e:
            logger.warning(f"EasyTax 이탈 고객 SMS 트리거 알림: {e}")

        # 2. 매일 아침 08시: 0원 무료나눔 & 세금 환급 데일리 브리핑
        if current_hour == 8 and self.last_daily_report_date != today_str:
            try:
                self.free_notifier.generate_daily_briefing()
                self.last_daily_report_date = today_str
                logger.info("아침 데일리 브리핑 자동 배포 완료")
            except Exception as e:
                logger.error(f"데일리 브리핑 실패: {e}")

        # 3. 매일 오후 14시: 듀얼 채널 숏폼 일괄 렌더링 (K-Market 70% + EasyTax 30%)
        if current_hour == 14 and self.last_shorts_hour != 14:
            try:
                # 🛒 K-Market 공식 채널 (5개 핵심 언어 0원 나눔 숏폼)
                km_res = self.shorts_factory.produce_shorts(service_id="kmarket", target_langs=["en", "vi", "zh", "ko", "uz"])
                # 💰 EasyTax 공식 채널 (3개 핵심 언어 90% 감면 숏폼)
                tax_res = self.shorts_factory.produce_shorts(service_id="easytax", target_langs=["vi", "en", "zh"])
                
                self.last_shorts_hour = 14
                logger.info(f"오후 14시 듀얼 채널 숏폼 무인 렌더링 완료 (K-Market {len(km_res)}건 + EasyTax {len(tax_res)}건)")
            except Exception as e:
                logger.error(f"숏폼 렌더링 실패: {e}")

        # 4. 카드뉴스 생성 (사용자 요청에 따라 정지)
        # if current_hour == 20 and self.last_cardnews_hour != 20:
        #     logger.info("저녁 20시 카드뉴스 배포는 일시 정지 상태입니다.")

        # 5. 매시간: Supabase 클라우드 자가학습 데이터 동기화
        try:
            synced = self.supabase_mgr.sync_histories_to_cloud()
            if synced > 0:
                logger.info(f"Supabase 클라우드 자가학습 데이터 {synced}건 실시간 동기화 완료")
        except Exception as e:
            logger.error(f"클라우드 동기화 실패: {e}")

        logger.info(f"--- [오토파일럿 루프 완료] ---\n")
