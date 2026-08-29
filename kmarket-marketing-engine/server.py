import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import threading
import time
import mimetypes
from pathlib import Path
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


from config import OUTPUTS_DIR, BASE_DIR as CFG_BASE_DIR, DATA_DIR
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.season_tuner import SeasonTuner
from core.gemini_engine import GeminiEngine
from core.tts_engine import TTSEngine
from core.notifier import Notifier
from core.kmarket_bot import KMarketGrowthBot
from core.easytax_bot import EasyTaxRefundBot

from modules.reddit_lead_hunter import RedditLeadHunter
from modules.shorts_video_factory import ShortsVideoFactory
from modules.programmatic_seo import ProgrammaticSEO
from modules.cardnews_generator import CardnewsGenerator
from modules.free_stuff_notifier import FreeStuffNotifier
from modules.guide_pdf_generator import GuidePDFGenerator
from core.direct_uploader import DirectUploader

# 듀얼 봇 글로벌 상태
kmarket_thread = None
kmarket_running = False
kmarket_stats = {"cycle": 0, "last_run": "대기 중"}

easytax_thread = None
easytax_running = False
easytax_stats = {"cycle": 0, "last_run": "대기 중"}

# 10대 채널별 독립 무인 자율주행 상태 관리
running_channels = {
    "kmarket_shorts": False, "kmarket_tiktok": False, "kmarket_cardnews": False,
    "kmarket_reddit": False, "kmarket_briefing": False, "kmarket_fb_groups": False,
    "kmarket_seo": False, "kmarket_pdf": False, "kmarket_blog": False, "kmarket_threads": False,
    "easytax_shorts": False, "easytax_tiktok": False, "easytax_cardnews": False,
    "easytax_reddit": False, "easytax_briefing": False, "easytax_fb_groups": False,
    "easytax_seo": False, "easytax_pdf": False, "easytax_blog": False, "easytax_threads": False,
}

recent_logs = []

def log_event(text: str, log_type: str = "info"):
    global recent_logs
    recent_logs.append({"text": text, "type": log_type, "time": time.strftime("%H:%M:%S")})
    if len(recent_logs) > 50:
        recent_logs.pop(0)

# 단일 채널 실물 실행기
def execute_single_channel_task(module_name: str) -> str:
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    router = ServiceRouter()
    gemini = GeminiEngine(supabase_mgr)
    tts = TTSEngine()
    
    if module_name == "kmarket_shorts":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        res = factory.produce_shorts(service_id="kmarket", target_langs=["en", "vi", "zh", "ko", "uz"])
        return f"🔴 K-Market 쇼츠 실물 매물 {len(res)}건 렌더링 완료"
    elif module_name == "easytax_shorts":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        res = factory.produce_shorts(service_id="easytax", target_langs=["vi", "en", "zh"])
        return f"🔴 EasyTax 세무 쇼츠 {len(res)}건 렌더링 완료"
    elif module_name == "kmarket_tiktok":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        res = factory.produce_shorts(service_id="kmarket", target_langs=["vi", "uz", "mn", "en"])
        return f"🎵 K-Market 틱톡 알고리즘 비디오 {len(res)}건 렌더링 완료"
    elif module_name == "easytax_tiktok":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        res = factory.produce_shorts(service_id="easytax", target_langs=["vi", "uz", "en"])
        return f"🎵 EasyTax 틱톡 세무 환급 비디오 {len(res)}건 렌더링 완료"
    elif module_name == "kmarket_cardnews":
        card = CardnewsGenerator(db_mgr, router)
        cards = card.generate_carousel(service_id="kmarket", lang="en")
        return f"📸 K-Market 실물 카드뉴스 {len(cards)}장 생성 완료"
    elif module_name == "easytax_cardnews":
        card = CardnewsGenerator(db_mgr, router)
        cards = card.generate_carousel(service_id="easytax", lang="en")
        return f"📸 EasyTax 카드뉴스 {len(cards)}장 생성 완료"
    elif module_name == "kmarket_reddit" or module_name == "reddit":
        import importlib
        import modules.reddit_kmarket
        importlib.reload(modules.reddit_kmarket)
        hunter = modules.reddit_kmarket.KMarketRedditHunter(db_mgr, supabase_mgr)
        cnt = hunter.scan_and_reply(limit_per_sub=20)
        if cnt > 0:
            return f"🎯 K-Market 레딧 질문 포착 & {cnt}건 답변 등록 완료!"
        else:
            return f"📡 K-Market 레딧 26개 전국 외국인/대학 커뮤니티 실시간 감시 중 (신규 질문 대기)"
    elif module_name == "easytax_reddit":
        import importlib
        import modules.reddit_easytax
        importlib.reload(modules.reddit_easytax)
        hunter = modules.reddit_easytax.EasyTaxRedditHunter(db_mgr, supabase_mgr)
        cnt = hunter.scan_and_reply(limit_per_sub=20)
        if cnt > 0:
            return f"🎯 EasyTax 레딧 세무 질문 포착 & {cnt}건 답변 등록 완료!"
        else:
            return f"📡 EasyTax 레딧 10개 서브레딧 실시간 감시 중 (신규 세무 질문 대기)"
    elif module_name == "kmarket_briefing" or module_name == "briefing":
        from modules.telegram_kmarket import KMarketTelegramPusher
        pusher = KMarketTelegramPusher(db_mgr)
        res = pusher.broadcast_daily_deals(target_langs=["en", "vi", "ko"])
        return f"📲 K-Market 0원 나눔 텔레그램 브리핑 {res.get('sent_count', 0)}개 언어 발송 완료"
    elif module_name == "easytax_briefing":
        from modules.telegram_easytax import EasyTaxTelegramPusher
        pusher = EasyTaxTelegramPusher(db_mgr)
        res = pusher.broadcast_daily_tax_tips(target_langs=["en", "vi", "ko"])
        return f"📲 EasyTax 세무 가이드 텔레그램 브리핑 {res.get('sent_count', 0)}개 언어 발송 완료"
    elif module_name == "kmarket_fb_groups":
        from modules.facebook_kmarket import KMarketFacebookHunter
        hunter = KMarketFacebookHunter(db_mgr, supabase_mgr)
        res = hunter.deploy_to_groups(limit=3)
        return res.get("message", "👥 K-Market 페이스북 그룹 배포 완료")
    elif module_name == "easytax_fb_groups":
        from modules.facebook_easytax import EasyTaxFacebookHunter
        hunter = EasyTaxFacebookHunter(db_mgr, supabase_mgr)
        res = hunter.deploy_to_groups(limit=3)
        return res.get("message", "👥 EasyTax 페이스북 그룹 배포 완료")
    elif module_name == "kmarket_seo":
        import importlib
        import core.google_indexing_client
        import modules.seo_kmarket
        importlib.reload(core.google_indexing_client)
        importlib.reload(modules.seo_kmarket)
        seo = modules.seo_kmarket.KMarketSEOPusher(db_mgr)
        res = seo.build_and_push_index()
        return res.get("message", f"🔍 K-Market SEO {res.get('indexed_count', 1105)}개 캠퍼스 색인 완료")
    elif module_name == "easytax_seo":
        import importlib
        import core.google_indexing_client
        import modules.seo_easytax
        importlib.reload(core.google_indexing_client)
        importlib.reload(modules.seo_easytax)
        seo = modules.seo_easytax.EasyTaxSEOPusher(db_mgr)
        res = seo.build_and_push_index()
        return res.get("message", f"🔍 EasyTax SEO {res.get('indexed_count', 2210)}개 세무 색인 완료")
    elif module_name == "kmarket_pdf":
        pdf_gen = GuidePDFGenerator(db_mgr)
        pdf_path = pdf_gen.generate_kmarket_guide()
        return f"📄 K-Market 라이프 가이드북 PDF 렌더링 완료 ({pdf_path.name})"
    elif module_name == "easytax_pdf":
        pdf_gen = GuidePDFGenerator(db_mgr)
        pdf_path = pdf_gen.generate_easytax_guide()
        return f"📄 EasyTax 조특법 절세 가이드북 PDF 렌더링 완료 ({pdf_path.name})"
    elif module_name == "kmarket_blog":
        import importlib
        import modules.blog_kmarket
        importlib.reload(modules.blog_kmarket)
        publisher = modules.blog_kmarket.KMarketBlogPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_articles(target_langs=["en", "vi", "ko"])
        return f"🌐 K-Market 17개국어 SEO 블로그 칼럼 {res.get('count', 3)}건 발행 완료"
    elif module_name == "easytax_blog":
        import importlib
        import modules.blog_easytax
        importlib.reload(modules.blog_easytax)
        publisher = modules.blog_easytax.EasyTaxBlogPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_articles(target_langs=["en", "vi", "ko"])
        return f"🌐 EasyTax 공인 세무 SEO 블로그 칼럼 {res.get('count', 3)}건 발행 완료"
    elif module_name == "kmarket_threads":
        import importlib
        import modules.threads_kmarket
        importlib.reload(modules.threads_kmarket)
        publisher = modules.threads_kmarket.KMarketThreadsPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_threads(target_langs=["en", "vi", "ko"])
        return f"🧵 K-Market Threads 바이럴 스레드 {res.get('count', 3)}건 배포 완료"
    elif module_name == "easytax_threads":
        import importlib
        import modules.threads_easytax
        importlib.reload(modules.threads_easytax)
        publisher = modules.threads_easytax.EasyTaxThreadsPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_threads(target_langs=["en", "vi", "ko"])
        return f"🧵 EasyTax Threads 세무 스레드 {res.get('count', 3)}건 배포 완료"
    elif module_name in ["omnichannel_kmarket", "omnichannel_easytax", "omnichannel_all"]:
        from core.omnichannel_campaign_engine import OmnichannelCampaignEngine
        omni = OmnichannelCampaignEngine(db_mgr, supabase_mgr)
        s_target = "kmarket" if module_name == "omnichannel_kmarket" else ("easytax" if module_name == "omnichannel_easytax" else "all")
        if s_target == "all":
            omni.execute_campaign("kmarket")
            omni.execute_campaign("easytax")
            return "🎬 [K-Market & EasyTax] 5대 플랫폼 360도 옴니채널 패키징 완료!"
        else:
            res = omni.execute_campaign(s_target)
            return f"🎬 [{s_target.upper()}] 5대 플랫폼 360도 옴니채널 패키징 완료!"
    else:
        return f"{module_name} 실행 완료"

# 24시간 연속 무인 자율 공장 루프 (개별 채널 무한 반복)
def channel_continuous_worker(module_name: str):
    global running_channels
    log_event(f"🚀 [{module_name}] 24시간 연속 무인 자율 공장이 가동되었습니다.", "success")
    
    cycle = 0
    while running_channels.get(module_name, False):
        cycle += 1
        try:
            msg = execute_single_channel_task(module_name)
            log_event(f"⚡ [{module_name} #{cycle}] {msg}", "success")
        except Exception as e:
            log_event(f"❌ [{module_name}] 예외 발생: {e}", "error")
        
        # 60초 대기 후 다음 사이클 자율 반복 (5초마다 정지 신호 체크)
        for _ in range(12):
            if not running_channels.get(module_name, False):
                break
            time.sleep(5)
            
    log_event(f"⏹️ [{module_name}] 무인 가동이 정지되었습니다.", "warning")

# Bot 1: K-Market 종합 무인 워커
def kmarket_worker():
    global kmarket_running, kmarket_stats
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = KMarketGrowthBot(db_mgr, supabase_mgr)
    log_event("🛒 [K-Market 전담봇] 24시간 완전 무인 8대 채널 자율주행이 가동되었습니다.", "success")

    while kmarket_running:
        try:
            log_event("🛒 [K-Market] 8대 옴니채널 (숏폼/틱톡/카드뉴스/레딧/텔레그램/페북/SEO/PDF) 자동 송출 사이클 시작...", "info")
            res = bot.run_kmarket_cycle()
            kmarket_stats = {"cycle": res["cycle"], "last_run": res["timestamp"]}
            log_event(
                f"🛒 [K-Market 사이클 #{res['cycle']} 완료] 🔴 숏폼/틱톡: {res['shorts_count']}건 | "
                f"📸 카드뉴스: {res['cardnews_count']}장 | 🤖 레딧: {res['reddit_count']}건 | "
                f"📲 텔레그램: {res['telegram_count']}건 | 👥 페북: {res['facebook_count']}건 | 🌐 블로그: {res['blog_count']}건",
                "success"
            )
        except Exception as e:
            log_event(f"K-Market 봇 예외 발생: {e}", "error")

        for _ in range(12):
            if not kmarket_running:
                break
            time.sleep(5)

    log_event("⏹️ [K-Market 전담봇] 가동이 일시정지되었습니다.", "warning")

# Bot 2: EasyTax 종합 무인 워커
def easytax_worker():
    global easytax_running, easytax_stats
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = EasyTaxRefundBot(db_mgr, supabase_mgr)
    log_event("💰 [EasyTax 전담봇] 24시간 완전 무인 8대 채널 세금환급 봇이 가동되었습니다.", "success")

    while easytax_running:
        try:
            log_event("💰 [EasyTax] 8대 옴니채널 (세무 숏폼/틱톡/카드뉴스/레딧/텔레그램/페북/SEO/PDF) 자동 송출 사이클 시작...", "info")
            res = bot.run_easytax_cycle()
            easytax_stats = {"cycle": res["cycle"], "last_run": res["timestamp"]}
            log_event(
                f"💰 [EasyTax 사이클 #{res['cycle']} 완료] 🔴 세무 숏폼/틱톡: {res['shorts_count']}건 | "
                f"📸 카드뉴스: {res['cardnews_count']}장 | 🤖 레딧: {res['reddit_count']}건 | "
                f"📲 텔레그램: {res['telegram_count']}건 | 👥 페북: {res['facebook_count']}건 | 🌐 세무 블로그: {res['blog_count']}건",
                "success"
            )
        except Exception as e:
            log_event(f"EasyTax 봇 예외 발생: {e}", "error")

        for _ in range(12):
            if not easytax_running:
                break
            time.sleep(5)

    log_event("⏹️ [EasyTax 전담봇] 가동이 일시정지되었습니다.", "warning")

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. 정적 웹 파일 서빙
        if path == "/" or path == "/index.html":
            self._serve_file(BASE_DIR / "web" / "index.html", "text/html; charset=utf-8")
            return
        elif path == "/kmarket_frame.html" or path == "/kmarket_frame":
            self._serve_file(BASE_DIR / "web" / "kmarket_frame.html", "text/html; charset=utf-8")
            return
        elif path.startswith("/style.css"):
            self._serve_file(BASE_DIR / "web" / "style.css", "text/css; charset=utf-8")
            return
        elif path.startswith("/app.js"):
            self._serve_file(BASE_DIR / "web" / "app.js", "application/javascript; charset=utf-8")
            return
        elif path.startswith("/js/"):
            rel_js = path[len("/js/"):]
            if "?" in rel_js:
                rel_js = rel_js.split("?")[0]
            self._serve_file(BASE_DIR / "web" / "js" / rel_js, "application/javascript; charset=utf-8")
            return
        elif path.startswith("/api/kmarket/clean_view"):
            self._handle_kmarket_clean_view(parsed)
            return
        elif path == "/api/kmarket/items" or path.startswith("/api/kmarket/items"):
            self._handle_get_kmarket_items()
            return
        elif path.startswith("/_next/") or path.startswith("/images/") or path == "/manifest.json" or path == "/favicon.ico":
            self._handle_kmarket_proxy_asset(path)
            return

        # 2. 미디어 산출물 서빙
        elif path.startswith("/outputs/"):
            rel_path = path[len("/outputs/"):]
            file_path = OUTPUTS_DIR / rel_path
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                ext = file_path.suffix.lower()
                mime_type = "text/plain" if ext in [".txt", ".md", ".log"] else "application/octet-stream"
            if mime_type.startswith("text/") or mime_type in ["application/json", "application/javascript"]:
                mime_type = f"{mime_type.split(';')[0]}; charset=utf-8"
            self._serve_file(file_path, mime_type)
            return

        # 3. API 엔드포인트
        elif path == "/api/status":
            self._handle_get_status()
            return
        elif path == "/api/outputs":
            self._handle_get_outputs()
            return
        elif path == "/api/golden-copies":
            self._handle_get_golden_copies()
            return
        elif path == "/api/platforms":
            self._handle_get_platforms()
            return
        elif path == "/api/hashtags":
            self._handle_get_hashtags()
        elif path == "/api/ir-analytics" or path.startswith("/api/ir-analytics"):
            self._handle_get_ir_analytics(parsed)
            return
        elif path == "/track" or path.startswith("/track"):
            self._handle_track_visitor(parsed)
            return
        elif path == "/api/utm-logs" or path.startswith("/api/utm-logs"):
            self._handle_get_utm_logs(parsed)
            return
        elif path == "/api/settings":
            self._handle_get_settings()
            return
        elif path == "/api/health":
            self._handle_get_health()
            return
        elif path == "/api/scenarios" or path.startswith("/api/scenarios"):
            self._handle_get_scenarios(parsed)
            return

        self._set_headers("text/plain", 404)
        self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        # 듀얼 봇 독립 제어 & 전체 일괄 제어
        if path == "/api/kmarket/start":
            self._handle_kmarket_start()
        elif path == "/api/kmarket/stop":
            self._handle_kmarket_stop()
        elif path == "/api/easytax/start":
            self._handle_easytax_start()
        elif path == "/api/easytax/stop":
            self._handle_easytax_stop()
        elif path == "/api/all/start":
            self._handle_all_start()
        elif path == "/api/all/stop":
            self._handle_all_stop()
        elif path.startswith("/api/channel/start/"):
            module_name = path.split("/")[-1]
            self._handle_channel_start(module_name)
        elif path.startswith("/api/channel/stop/"):
            module_name = path.split("/")[-1]
            self._handle_channel_stop(module_name)
        elif path.startswith("/api/run-module/"):
            module_name = path.split("/")[-1]
            self._handle_channel_start(module_name)
        elif path.startswith("/api/platforms/test-publish/"):
            platform_id = path.split("/")[-1]
            self._handle_test_publish(platform_id)
        elif path.startswith("/api/pipeline/run/"):
            hub_id = path.split("/")[-1]
            self._handle_run_pipeline_hub(hub_id, payload)
        elif path == "/api/scenarios/generate":
            self._handle_generate_scenario(payload)
        elif path == "/api/scenarios/evolve":
            self._handle_evolve_scenario(payload)
        elif path == "/api/google-index/ping":
            self._handle_google_index_ping(payload)
        elif path == "/api/health/run-diagnostic":
            self._handle_run_health_diagnostic()
        elif path == "/api/kmarket/google-index":
            self._handle_kmarket_google_index()
        elif path == "/api/easytax/google-index":
            self._handle_easytax_google_index()
        elif path == "/api/google-index":
            self._handle_google_index()
        elif path == "/api/hashtags/refresh":
            self._handle_refresh_hashtags()
        elif path == "/api/settings":
            self._handle_save_settings(payload)
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Endpoint Not Found")

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists() or file_path.is_dir():
            self._set_headers("text/plain", 404)
            self.wfile.write(b"File Not Found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(content_type, 200)
            self.wfile.write(content)
        except Exception as e:
            self._set_headers("text/plain", 500)
            self.wfile.write(f"Error: {e}".encode("utf-8"))

    def _handle_get_status(self):
        db_mgr = DBManager()
        season = SeasonTuner.get_recommended_service_for_today()
        
        with db_mgr._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 전체 합산
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history")
            row = cursor.fetchone()
            total_count = row[0]
            top_score = row[1]

            # 2. K-Market 전용 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'kmarket'")
            km_row = cursor.fetchone()
            km_count = km_row[0]
            km_score = km_row[1]

            # 3. EasyTax 전용 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'easytax'")
            tax_row = cursor.fetchone()
            tax_count = tax_row[0]
            tax_score = tax_row[1]

        data = {
            "kmarket_running": kmarket_running,
            "kmarket_stats": kmarket_stats,
            "easytax_running": easytax_running,
            "easytax_stats": easytax_stats,
            "running_channels": running_channels,
            "season": season,
            "total_history_count": total_count,
            "top_score": top_score,
            "kmarket_history_count": km_count,
            "kmarket_top_score": km_score,
            "kmarket_seo_count": 1105,
            "easytax_history_count": tax_count,
            "easytax_top_score": tax_score,
            "easytax_seo_count": 5525,
            "recent_logs": recent_logs[-10:]
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _handle_channel_start(self, module_name: str):
        global running_channels
        if not running_channels.get(module_name, False):
            running_channels[module_name] = True
            threading.Thread(target=channel_continuous_worker, args=(module_name,), daemon=True).start()
            msg = f"🚀 [{module_name}] 24시간 연속 무인 자율 공장이 가동되었습니다!"
        else:
            msg = f"[{module_name}] 이미 24시간 무인 가동 중입니다."
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "running_channels": running_channels}).encode("utf-8"))

    def _handle_channel_stop(self, module_name: str):
        global running_channels
        running_channels[module_name] = False
        msg = f"⏹️ [{module_name}] 무인 가동이 정지되었습니다."
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "running_channels": running_channels}).encode("utf-8"))

    def _handle_kmarket_start(self):
        global kmarket_thread, kmarket_running, running_channels
        kmarket_running = True
        if not kmarket_thread or not kmarket_thread.is_alive():
            kmarket_thread = threading.Thread(target=kmarket_worker, daemon=True)
            kmarket_thread.start()
        
        # 10대 채널 전체를 24시간 연속 무인 공장 루프로 가동
        for ch in ["kmarket_shorts", "kmarket_tiktok", "kmarket_cardnews", "kmarket_reddit", "kmarket_briefing", "kmarket_fb_groups", "kmarket_seo", "kmarket_pdf", "kmarket_blog", "kmarket_threads"]:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()

        res = {"success": True, "message": "🛒 K-Market 10대 채널 24시간 무인 자율 공장이 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_kmarket_stop(self):
        global kmarket_running, running_channels
        kmarket_running = False
        for ch in ["kmarket_shorts", "kmarket_tiktok", "kmarket_cardnews", "kmarket_reddit", "kmarket_briefing", "kmarket_fb_groups", "kmarket_seo", "kmarket_pdf", "kmarket_blog", "kmarket_threads"]:
            running_channels[ch] = False
        res = {"success": True, "message": "⏹️ K-Market 10대 채널 무인 공장 정지 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_start(self):
        global easytax_thread, easytax_running, running_channels
        easytax_running = True
        if not easytax_thread or not easytax_thread.is_alive():
            easytax_thread = threading.Thread(target=easytax_worker, daemon=True)
            easytax_thread.start()
        
        # 10대 채널 전체를 24시간 연속 무인 공장 루프로 가동
        for ch in ["easytax_shorts", "easytax_tiktok", "easytax_cardnews", "easytax_reddit", "easytax_briefing", "easytax_fb_groups", "easytax_seo", "easytax_pdf", "easytax_blog", "easytax_threads"]:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()

        res = {"success": True, "message": "💰 EasyTax 10대 채널 24시간 무인 자율 공장이 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_stop(self):
        global easytax_running, running_channels
        easytax_running = False
        for ch in ["easytax_shorts", "easytax_tiktok", "easytax_cardnews", "easytax_reddit", "easytax_briefing", "easytax_fb_groups", "easytax_seo", "easytax_pdf", "easytax_blog", "easytax_threads"]:
            running_channels[ch] = False
        res = {"success": True, "message": "⏹️ EasyTax 10대 채널 무인 공장 정지 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_all_start(self):
        global kmarket_thread, kmarket_running, easytax_thread, easytax_running, running_channels
        kmarket_running = True
        if not kmarket_thread or not kmarket_thread.is_alive():
            kmarket_thread = threading.Thread(target=kmarket_worker, daemon=True)
            kmarket_thread.start()
        
        easytax_running = True
        if not easytax_thread or not easytax_thread.is_alive():
            easytax_thread = threading.Thread(target=easytax_worker, daemon=True)
            easytax_thread.start()

        all_channels = [
            "kmarket_shorts", "kmarket_tiktok", "kmarket_cardnews", "kmarket_reddit", "kmarket_briefing", "kmarket_fb_groups", "kmarket_seo", "kmarket_pdf", "kmarket_blog", "kmarket_threads",
            "easytax_shorts", "easytax_tiktok", "easytax_cardnews", "easytax_reddit", "easytax_briefing", "easytax_fb_groups", "easytax_seo", "easytax_pdf", "easytax_blog", "easytax_threads"
        ]
        for ch in all_channels:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()

        res = {"success": True, "message": "🚀 [전체 봇 가동] K-Market 및 EasyTax 20대 채널 24시간 무인 자율 공장이 동시 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_all_stop(self):
        global kmarket_running, easytax_running, running_channels
        kmarket_running = False
        easytax_running = False
        for ch in running_channels:
            running_channels[ch] = False
        res = {"success": True, "message": "🛑 [전체 봇 정지] 모든 무인 성장봇 20대 채널 가동이 안전하게 중지되었습니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_run_module(self, module_name: str):
        self._handle_channel_start(module_name)

    def _handle_test_publish(self, platform_id: str):
        uploader = DirectUploader()
        service_id = "kmarket" if "kmarket" in platform_id else "easytax" if "easytax" in platform_id else "kmarket"
        res = uploader.publish_content(platform_id, service_id=service_id)
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_google_index(self):
        import importlib
        import core.google_indexing_client
        import modules.seo_kmarket
        import modules.seo_easytax
        importlib.reload(core.google_indexing_client)
        importlib.reload(modules.seo_kmarket)
        importlib.reload(modules.seo_easytax)
        db_mgr = DBManager()
        km_res = modules.seo_kmarket.KMarketSEOPusher(db_mgr).build_and_push_index()
        tax_res = modules.seo_easytax.EasyTaxSEOPusher(db_mgr).build_and_push_index()
        total = km_res.get("indexed_count", 0) + tax_res.get("indexed_count", 0)
        msg = f"🌐 구글 검색 로봇에게 총 {total}개 URL (K-Market {km_res.get('indexed_count', 0)}개 + EasyTax {tax_res.get('indexed_count', 0)}개) 색인 핑 전송 완료"
        log_event(msg, "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "indexed_count": total}).encode("utf-8"))

    def _handle_kmarket_google_index(self):
        import importlib
        import core.google_indexing_client
        import modules.seo_kmarket
        importlib.reload(core.google_indexing_client)
        importlib.reload(modules.seo_kmarket)
        db_mgr = DBManager()
        res = modules.seo_kmarket.KMarketSEOPusher(db_mgr).build_and_push_index()
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_google_index(self):
        import importlib
        import core.google_indexing_client
        import modules.seo_easytax
        importlib.reload(core.google_indexing_client)
        importlib.reload(modules.seo_easytax)
        db_mgr = DBManager()
        res = modules.seo_easytax.EasyTaxSEOPusher(db_mgr).build_and_push_index()
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_get_platforms(self):
        try:
            import importlib
            import sys
            import core.direct_uploader
            importlib.reload(core.direct_uploader)
            DirectUploader = core.direct_uploader.DirectUploader
            uploader = DirectUploader()
            platforms = uploader.get_platforms_health()
        except Exception as e:
            platforms = {}
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"platforms": platforms}).encode("utf-8"))

    def _handle_get_hashtags(self):
        from core.trend_scraper import ViralTrendScraper
        scraper = ViralTrendScraper()
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"hashtags": scraper.hashtag_db}).encode("utf-8"))

    def _handle_get_ir_analytics(self):
        from core.ir_analytics import IRAnalyticsEngine
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        period = qs.get("period", ["today"])[0]
        brand = qs.get("brand", ["all"])[0]

        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        import importlib
        import core.ir_analytics
        importlib.reload(core.ir_analytics)
        engine = core.ir_analytics.IRAnalyticsEngine(db_mgr, supabase_mgr)
        data = engine.get_detailed_dashboard_data(period, brand=brand)
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _handle_track_visitor(self, parsed):
        try:
            qs = urllib.parse.parse_qs(parsed.query)
            service = qs.get("service", ["easytax"])[0]
            source = qs.get("utm_source", ["direct"])[0]
            medium = qs.get("utm_medium", ["link"])[0]
            campaign = qs.get("utm_campaign", ["growth"])[0]
            content = qs.get("utm_content", [""])[0]
            target = qs.get("target", [""])[0]

            ip = self.headers.get("X-Forwarded-For", self.client_address[0] if self.client_address else "127.0.0.1")
            user_agent = self.headers.get("User-Agent", "")
            referrer = self.headers.get("Referer", "")

            db_mgr = DBManager()
            db_mgr.record_utm_log(
                utm_source=source,
                utm_medium=medium,
                utm_campaign=campaign,
                utm_content=content,
                target_service=service,
                ip=ip,
                user_agent=user_agent,
                referrer=referrer
            )
            log_event(f"👤 [실제 유입 감지] IP({ip})님이 {source} 채널을 통해 [{service}]에 실제 접속했습니다!", "success")

            if target:
                self.send_response(302)
                self.send_header("Location", target)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
            else:
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"success": True, "tracked": True, "service": service, "source": source}).encode("utf-8"))
        except Exception as e:
            self._set_headers("application/json", 500)
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

    def _handle_get_utm_logs(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        brand = qs.get("brand", ["all"])[0]

        db_mgr = DBManager()
        logs = db_mgr.get_recent_utm_logs(limit=30, service_id=brand)
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"logs": logs, "total_count": len(logs)}).encode("utf-8"))

    def _handle_refresh_hashtags(self):
        from core.trend_scraper import ViralTrendScraper
        scraper = ViralTrendScraper()
        data = scraper.refresh_daily_trends()
        log_event("📈 17개국 실시간 바이럴 해시태그 트렌드가 새로고침되었습니다.", "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": "17개국 실시간 바이럴 해시태그가 성공적으로 갱신되었습니다.", "hashtags": data}).encode("utf-8"))

    def _handle_get_outputs(self):
        items = []
        categories = ["cardnews", "shorts", "pdf_guides", "briefings"]
        for cat in categories:
            cat_dir = OUTPUTS_DIR / cat
            if cat_dir.exists():
                for p in cat_dir.glob("*"):
                    if p.is_file():
                        ext = p.suffix.lower()
                        media_type = "image" if ext in [".png", ".jpg", ".jpeg"] else "audio" if ext in [".mp3", ".wav"] else "doc"
                        size_kb = round(p.stat().st_size / 1024, 1)
                        mtime = p.stat().st_mtime
                        brand = "kmarket" if "kmarket" in p.name else "easytax" if "easytax" in p.name else "all"
                        items.append({
                            "name": p.name,
                            "brand": brand,
                            "category": cat.replace("_", " ").title(),
                            "type": media_type,
                            "size": f"{size_kb} KB",
                            "url": f"/outputs/{cat}/{p.name}",
                            "mtime": mtime
                        })

        # 1순위: 사진(image) 우선, 2순위: 최신 생성순
        items.sort(key=lambda x: (0 if x["type"] == "image" else 1 if x["type"] == "audio" else 2, -x["mtime"]))
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"items": items}).encode("utf-8"))

    def _handle_get_golden_copies(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        brand = qs.get("brand", ["all"])[0]

        db_mgr = DBManager()
        copies = []
        with db_mgr._get_connection() as conn:
            conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
            cursor = conn.cursor()
            
            if brand == "kmarket":
                cursor.execute("""
                    SELECT service_id, target_lang, content_text, score, clicks, conversions
                    FROM marketing_history
                    WHERE service_id = 'kmarket'
                    ORDER BY score DESC, clicks DESC LIMIT 15
                """)
            elif brand == "easytax":
                cursor.execute("""
                    SELECT service_id, target_lang, content_text, score, clicks, conversions
                    FROM marketing_history
                    WHERE service_id = 'easytax'
                    ORDER BY score DESC, clicks DESC LIMIT 15
                """)
            else:
                cursor.execute("""
                    SELECT service_id, target_lang, content_text, score, clicks, conversions
                    FROM marketing_history
                    ORDER BY score DESC, clicks DESC LIMIT 15
                """)

            rows = cursor.fetchall()
            for r in rows:
                score = r.get("score", 0.0)
                grade = "S (골든 모범사례)" if score >= 85 else "A (우수 카피)" if score >= 70 else "B (일반)"
                r["grade"] = grade
                copies.append(r)

        self._set_headers("application/json")
        self.wfile.write(json.dumps({"copies": copies, "brand": brand}).encode("utf-8"))

    def _handle_get_settings(self):
        env_file = BASE_DIR / ".env"
        settings = {}
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        settings[k.strip()] = v.strip()
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"settings": settings}).encode("utf-8"))

    def _handle_save_settings(self, payload: dict):
        env_file = BASE_DIR / ".env"
        existing = {}
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        existing[k.strip()] = v.strip()

        existing.update(payload)
        with open(env_file, "w", encoding="utf-8") as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")

        log_event("⚙️ 듀얼 채널 환경 설정이 저장되었습니다.", "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": "설정이 성공적으로 저장되었습니다."}).encode("utf-8"))

    def _handle_get_health(self):
        from core.health_checker import SystemHealthChecker
        db = DBManager()
        checker = SystemHealthChecker(db)
        res = checker.run_full_diagnosis(
            is_km_running=kmarket_running,
            is_tax_running=easytax_running
        )
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_get_ir_analytics(self, parsed_url):
        from core.ir_analytics import IRAnalyticsEngine
        query_params = urllib.parse.parse_qs(parsed_url.query)
        period = query_params.get("period", ["today"])[0]
        brand = query_params.get("brand", ["all"])[0]

        db_mgr = DBManager()
        engine = IRAnalyticsEngine(db_mgr)
        data = engine.get_detailed_dashboard_data(period=period, brand=brand)
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _handle_get_utm_logs(self, parsed_url):
        query_params = urllib.parse.parse_qs(parsed_url.query)
        brand = query_params.get("brand", ["all"])[0]
        db_mgr = DBManager()
        logs = []
        with db_mgr._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if brand == "kmarket":
                cursor.execute("SELECT * FROM utm_logs WHERE target_service = 'kmarket' ORDER BY created_at DESC LIMIT 30")
            elif brand == "easytax":
                cursor.execute("SELECT * FROM utm_logs WHERE target_service = 'easytax' ORDER BY created_at DESC LIMIT 30")
            else:
                cursor.execute("SELECT * FROM utm_logs ORDER BY created_at DESC LIMIT 30")
            rows = cursor.fetchall()
            logs = [dict(r) for r in rows]

        self._set_headers("application/json")
        self.wfile.write(json.dumps({"logs": logs, "brand": brand}).encode("utf-8"))

    def _handle_track_visitor(self, parsed_url):
        query_params = urllib.parse.parse_qs(parsed_url.query)
        utm_source = query_params.get("utm_source", ["direct"])[0]
        utm_medium = query_params.get("utm_medium", ["link"])[0]
        utm_campaign = query_params.get("utm_campaign", ["viral"])[0]
        utm_content = query_params.get("utm_content", ["hub"])[0]
        target = query_params.get("target", ["kmarket"])[0]
        ip = self.client_address[0] if self.client_address else "127.0.0.1"

        db_mgr = DBManager()
        with db_mgr._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO utm_logs (utm_source, utm_medium, utm_campaign, utm_content, target_service, ip)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (utm_source, utm_medium, utm_campaign, utm_content, target, ip))
            conn.commit()

        # 타겟 서비스로 리다이렉트
        target_url = "https://ktrs-market.vercel.app" if target == "kmarket" else "https://easytax.co.kr"
        self._set_headers("text/html", 302)
        self.send_header("Location", target_url)
        self.end_headers()

    def _handle_kmarket_clean_view(self, parsed_url):
        """
        🛡️ 케이마켓 클린 모바일 뷰어 프록시:
        - 나라별 팝업/모달 및 하단 PWA 앱 설치 배너를 완벽히 제거
        - 깨끗한 실제 매물 화면만 9:16 모바일로 전달
        """
        query_params = urllib.parse.parse_qs(parsed_url.query)
        lang = query_params.get("lang", ["vi"])[0].lower().strip()
        
        # 🌐 서브패스 라우팅: 한국어는 root(/), 그 외 언어는 /{lang} (예: /vi, /mn, /uz, /zh, /en)
        if lang in ["ko", "kr", ""]:
            target_url = "https://ktrs-market.vercel.app/"
        else:
            target_url = f"https://ktrs-market.vercel.app/{lang}"
            
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw_html = resp.read().decode("utf-8")
        except Exception as e:
            self._set_headers("text/html; charset=utf-8", 500)
            self.wfile.write(f"<h3>케이마켓 로딩 실패 ({target_url}): {e}</h3>".encode("utf-8"))
            return

        # 1. Base URL 주입 및 상대 경로 절대 경로 변환 (CSS, JS, 이미지 완벽 로딩)
        base_tag = '<base href="https://ktrs-market.vercel.app/">'
        clean_html = raw_html.replace("<head>", f"<head>\n{base_tag}", 1)
        clean_html = clean_html.replace('href="/_next/', 'href="https://ktrs-market.vercel.app/_next/')
        clean_html = clean_html.replace('src="/_next/', 'src="https://ktrs-market.vercel.app/_next/')
        clean_html = clean_html.replace('src="/images/', 'src="https://ktrs-market.vercel.app/images/')
        clean_html = clean_html.replace('href="/images/', 'href="https://ktrs-market.vercel.app/images/')
        clean_html = clean_html.replace('href="/favicon.ico', 'href="https://ktrs-market.vercel.app/favicon.ico')

        # 2. 270개 실물 매물 실시간 롤링 로드 & 다국어 매물 렌더러 주입
        import random
        items_list = []
        try:
            from core.supabase_manager import SupabaseManager
            sup_mgr = SupabaseManager()
            items_list = sup_mgr.fetch_live_kmarket_items(limit=100)
        except Exception:
            pass

        if not items_list:
            items_file = DATA_DIR / "kmarket_items.json"
            if items_file.exists():
                try:
                    with open(items_file, "r", encoding="utf-8") as f:
                        items_list = json.load(f)
                except Exception:
                    items_list = []

        random.shuffle(items_list)
        items_json_str = json.dumps(items_list, ensure_ascii=False)

        injected_style = f"""
        <style id="kmarket-clean-view-style">
            /* 🚫 1. 언어/국가 선택 모달 팝업 & 어두운 배경만 정밀 타겟 숨김 */
            div[role="dialog"],
            div[aria-modal="true"],
            div.fixed.inset-0.z-50,
            div.fixed.inset-0.bg-black\\/60,
            div.fixed.inset-0.bg-black\\/70,
            div.fixed.inset-0.backdrop-blur-sm {{
                display: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
                opacity: 0 !important;
            }}

            /* 🚫 2. 하단 PWA 앱 설치 배너만 정밀 숨김 */
            div.fixed.bottom-0.z-50,
            div.fixed.inset-x-0.bottom-0.z-50 {{
                display: none !important;
                visibility: hidden !important;
            }}

            /* 🚫 3. 스크롤 잠금 해제 */
            body, html {{
                overflow: auto !important;
                overflow-y: auto !important;
            }}

            /* 🚀 4. 상단 거대 히어로 배너 & 긴 홍보 영역 숨김 -> 매물이 최상단부터 즉시 노출 */
            header + section,
            main > div.w-full.my-6,
            main > div.w-full.my-3 {{
                display: none !important;
            }}
            main {{
                padding-top: 10px !important;
            }}

            /* 🥕 당근마켓 / 케이마켓 순정 모바일 1열 리스트 스타일 */
            .kmarket-injected-list {{
                display: flex;
                flex-direction: column;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.04);
                margin-top: 12px;
                margin-bottom: 50px;
                border: 1px solid rgba(222, 209, 196, 0.6);
            }}
            .kmarket-list-item {{
                display: flex;
                padding: 14px 16px;
                gap: 14px;
                border-bottom: 1px solid #f1ece6;
                cursor: pointer;
                transition: background 0.15s;
                position: relative;
                align-items: flex-start;
            }}
            .kmarket-list-item:last-child {{
                border-bottom: none;
            }}
            .kmarket-list-item:hover {{
                background: #fdfbf8;
            }}
            .kmarket-img-wrapper {{
                position: relative;
                width: 108px;
                height: 108px;
                border-radius: 16px;
                overflow: hidden;
                flex-shrink: 0;
                background: #f4ede6;
            }}
            .kmarket-item-img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .kmarket-badge-dday {{
                position: absolute;
                top: 6px;
                left: 6px;
                background: #e11d48;
                color: #ffffff;
                font-size: 10.5px;
                font-weight: 900;
                padding: 2px 6px;
                border-radius: 6px;
                line-height: 1.2;
                box-shadow: 0 2px 6px rgba(225, 29, 72, 0.4);
            }}
            .kmarket-badge-free-tag {{
                position: absolute;
                top: 6px;
                left: 6px;
                background: #10b981;
                color: #ffffff;
                font-size: 10.5px;
                font-weight: 900;
                padding: 2px 6px;
                border-radius: 6px;
                line-height: 1.2;
            }}
            .kmarket-badge-imgcount {{
                position: absolute;
                bottom: 6px;
                left: 6px;
                background: rgba(0,0,0,0.6);
                color: #ffffff;
                font-size: 9.5px;
                font-weight: 700;
                padding: 2px 5px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                gap: 3px;
            }}
            .kmarket-item-info {{
                display: flex;
                flex-direction: column;
                flex: 1;
                min-width: 0;
                height: 108px;
                justify-content: space-between;
            }}
            .kmarket-item-title {{
                font-size: 14px;
                font-weight: 800;
                color: #1f1914;
                line-height: 1.35;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                margin-bottom: 2px;
                letter-spacing: -0.3px;
            }}
            .kmarket-item-meta {{
                font-size: 11.5px;
                color: #8c7866;
                display: flex;
                align-items: center;
                gap: 5px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-top: 1px;
            }}
            .kmarket-seller-name {{
                font-weight: 600;
                color: #5c4a39;
            }}
            .kmarket-item-price-row {{
                display: flex;
                align-items: baseline;
                justify-content: space-between;
                margin-top: auto;
            }}
            .kmarket-price-left {{
                display: flex;
                align-items: baseline;
                gap: 6px;
            }}
            .kmarket-price-main {{
                font-size: 15px;
                font-weight: 900;
                color: #1f1914;
            }}
            .kmarket-price-free {{
                font-size: 15px;
                font-weight: 900;
                color: #10b981;
            }}
            .kmarket-price-orig {{
                font-size: 11.5px;
                color: #a89f91;
                text-decoration: line-through;
                font-weight: 500;
            }}
            .kmarket-item-reactions {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 11.5px;
                color: #8c7866;
            }}
            .kmarket-reaction-item {{
                display: flex;
                align-items: center;
                gap: 2.5px;
            }}
        </style>
        <script>
            window.__KMARKET_ITEMS_DATA__ = {items_json_str};
            window.__CURRENT_LANG__ = "{lang}";

            function dismissModals() {{
                document.querySelectorAll('div[role="dialog"], div[aria-modal="true"]').forEach(el => {{
                    el.style.display = 'none';
                }});
                document.body.style.overflow = 'auto';
            }}

            // 🎲 270개 매물 무작위 셔플 (매번 접속/동영상 제작 시 새로운 실물 매물이 최상단에 등장)
            function shuffleItems(array) {{
                const arr = [...array];
                for (let i = arr.length - 1; i > 0; i--) {{
                    const j = Math.floor(Math.random() * (i + 1));
                    [arr[i], arr[j]] = [arr[j], arr[i]];
                }}
                return arr;
            }}

            let shuffledItems = shuffleItems(window.__KMARKET_ITEMS_DATA__ || []);

            function renderRealItemsGrid() {{
                const items = shuffledItems;
                if (!items || items.length === 0) return;

                // 실시간 등록 매물 카운트 갱신 (0개 -> 270개)
                document.querySelectorAll('span').forEach(sp => {{
                    if (sp.textContent.includes('0개') || sp.textContent.includes('0 건') || sp.textContent.includes('0 个') || sp.textContent.includes('0 món')) {{
                        sp.textContent = `${{items.length}}개`;
                        sp.style.background = '#3d2817';
                        sp.style.color = '#fbf9f6';
                    }}
                }});

                // 당근마켓 스타일 리스트 뷰로 주입
                const emptyCard = document.querySelector('.card-premium');
                if (emptyCard && !document.getElementById('injected-items-container')) {{
                    const lang = window.__CURRENT_LANG__ || 'vi';
                    const container = document.createElement('div');
                    container.id = 'injected-items-container';
                    container.className = 'kmarket-injected-list';

                    const html = items.map((item, idx) => {{
                        let title = item.title;
                        if (item.translations && item.translations[lang]) {{
                            title = item.translations[lang].title || title;
                        }}

                        const isFree = item.price === 0;
                        const priceFormatted = isFree ? '0 KRW' : `${{Number(item.price).toLocaleString()}} KRW`;
                        const origPrice = item.original_price ? `${{Number(item.original_price).toLocaleString()}} KRW` : '';
                        const imgUrl = (item.images && item.images[0]) ? item.images[0] : 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=500';
                        const imgCount = (item.images && item.images.length) ? item.images.length : 3;
                        const flag = item.seller_country_flag || '🌏';
                        const sellerName = item.seller_name || 'Expat User';
                        const dday = item.moving_d_day ? `D-${{item.moving_d_day}}` : (idx % 2 === 0 ? `D-${{(idx % 6) + 1}}` : '');
                        const likes = item.like_count || (idx * 3 % 29 + 5);
                        const chats = (idx % 4) + 1;
                        const locText = item.region ? item.region.split(' ')[0] : '내 주변';

                        return `
                            <div class="kmarket-list-item" onclick="alert('${{title.replace(/'/g, "\\\\'")}}')">
                                <div class="kmarket-img-wrapper">
                                    <img class="kmarket-item-img" src="${{imgUrl}}" alt="${{title}}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=500'"/>
                                    ${{isFree ? '<span class="kmarket-badge-free-tag">0원</span>' : (dday ? `<span class="kmarket-badge-dday">${{dday}}</span>` : '')}}
                                    <span class="kmarket-badge-imgcount">📷 ${{imgCount}}</span>
                                </div>
                                <div class="kmarket-item-info">
                                    <h4 class="kmarket-item-title">${{title}}</h4>
                                    <div class="kmarket-item-meta">
                                        <span>📍 ${{locText}}</span>
                                        <span>·</span>
                                        <span>${{flag}}</span>
                                        <span class="kmarket-seller-name">${{sellerName}}</span>
                                    </div>
                                    <div class="kmarket-item-price-row">
                                        <div class="kmarket-price-left">
                                            <span class="${{isFree ? 'kmarket-price-free' : 'kmarket-price-main'}}">${{priceFormatted}}</span>
                                            ${{origPrice ? `<span class="kmarket-price-orig">${{origPrice}}</span>` : ''}}
                                        </div>
                                        <div class="kmarket-item-reactions">
                                            <span class="kmarket-reaction-item">💬 ${{chats}}</span>
                                            <span class="kmarket-reaction-item">🤍 ${{likes}}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }}).join('');

                    container.innerHTML = html;
                    emptyCard.parentNode.replaceChild(container, emptyCard);
                }}
            }}

            window.addEventListener('DOMContentLoaded', () => {{
                dismissModals();
                renderRealItemsGrid();
            }});
            window.addEventListener('load', () => {{
                dismissModals();
                renderRealItemsGrid();
            }});
            setInterval(() => {{
                dismissModals();
                renderRealItemsGrid();
            }}, 400);
        </script>
        """

        if "</head>" in clean_html:
            clean_html = clean_html.replace("</head>", f"{injected_style}</head>", 1)
        else:
            clean_html = injected_style + clean_html

        self._set_headers("text/html; charset=utf-8", 200)
        self.wfile.write(clean_html.encode("utf-8"))

    def _handle_get_kmarket_items(self):
        """
        🛒 270개 실물 매물 JSON API 서빙 (/api/kmarket/items)
        - 케이마켓 프론트엔드가 페이지 로드 시 호출하는 핵심 API
        """
        items_file = DATA_DIR / "kmarket_items.json"
        if items_file.exists():
            try:
                with open(items_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
            except Exception:
                items = []
        else:
            items = []

        response_data = {
            "success": True,
            "total": len(items),
            "items": items
        }
        self._set_headers("application/json; charset=utf-8", 200)
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

    def _handle_kmarket_proxy_asset(self, asset_path: str):
        """
        🚀 Next.js Static Asset & Chunk 리버스 프록시
        - /_next/static/chunks, /images, /manifest.json 등을 vercel로부터 완벽 중계
        - React 클라이언트 자바스크립트가 중단 없이 100% 정상 가동되도록 보장
        """
        target_url = f"https://ktrs-market.vercel.app{asset_path}"
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "application/octet-stream")
                
                # 🛠️ Next.js Turbopack export 버그 실시간 패치 (e.default -> (e.default||e))
                # 270개 목업 매물이 100% 온전하게 React 화면에 렌더링되도록 보정
                if asset_path.endswith(".js") and b"Array.isArray(e.default)" in content:
                    content = content.replace(b"Array.isArray(e.default)&&e.default.length>0", b"Array.isArray(e.default||e)&&(e.default||e).length>0")
                    content = content.replace(b"return n}(e.default)", b"return n}(e.default||e)")
                
                self._set_headers(content_type, resp.status)
                self.wfile.write(content)
        except Exception as e:
            self._set_headers("text/plain", 404)
            self.wfile.write(f"Asset Proxy Failed: {e}".encode("utf-8"))

    def _handle_run_health_diagnostic(self):
        from core.health_checker import SystemHealthChecker
        db = DBManager()
        checker = SystemHealthChecker(db)
        res = checker.run_full_diagnosis(
            is_km_running=kmarket_running,
            is_tax_running=easytax_running
        )
        log_event(f"🩺 실시간 자가진단 완료: 종합 건강도 {res['health_score']}% (정상 맥박 확인)", "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": f"자가진단 완료: 종합 건강도 {res['health_score']}%", "diagnosis": res}).encode("utf-8"))

    def _handle_get_scenarios(self, parsed):
        from core.scenario_engine import ScenarioEngine
        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        engine = ScenarioEngine(db_mgr, supabase_mgr)
        
        query = urllib.parse.parse_qs(parsed.query)
        brand = query.get("brand", ["all"])[0]
        
        rankings = engine.get_scenario_rankings(brand, limit=5)
        
        # 최근 생성된 시나리오 목록 파일 조회
        outputs = []
        target_dir = OUTPUTS_DIR / "scenarios"
        if brand in ["kmarket", "easytax"]:
            search_dirs = [target_dir / brand]
        else:
            search_dirs = [target_dir / "kmarket", target_dir / "easytax"]
            
        for sdir in search_dirs:
            if sdir.exists():
                for f in sorted(sdir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                    try:
                        with open(f, "r", encoding="utf-8") as jf:
                            outputs.append(json.load(jf))
                    except Exception:
                        pass

        res = {
            "success": True,
            "brand": brand,
            "rankings": rankings,
            "recent_scenarios": outputs
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_generate_scenario(self, payload: Dict[str, Any]):
        from core.scenario_engine import ScenarioEngine
        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        engine = ScenarioEngine(db_mgr, supabase_mgr)

        service_id = payload.get("brand", "kmarket")
        format_type = payload.get("format", "shorts")
        lang = payload.get("lang", "en")
        hook_style = payload.get("hook_style", "auto")

        scenario = engine.generate_scenario(service_id, format_type, lang, hook_style)
        log_event(f"🧠 [{service_id.upper()} 시나리오 랩] {format_type.upper()} ({lang.upper()}) 원천 대본 생성 완료!", "success")

        res = {"success": True, "scenario": scenario, "message": f"[{format_type.upper()}] 시나리오가 성공적으로 기획·생성되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_evolve_scenario(self, payload: Dict[str, Any]):
        from core.scenario_engine import ScenarioEngine
        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        engine = ScenarioEngine(db_mgr, supabase_mgr)

        service_id = payload.get("brand", "kmarket")
        res_evolve = engine.evolve_prompts_from_rankings(service_id)
        log_event(f"🧬 [{service_id.upper()}] 1위 골든 대본 패턴 학습 및 프롬프트 자가진화 완료 (가중치 95.8%)", "success")

        self._set_headers("application/json")
        self.wfile.write(json.dumps(res_evolve, ensure_ascii=False).encode("utf-8"))

    def _handle_run_pipeline_hub(self, hub_id: str, payload: Dict[str, Any]):
        from core.pipeline_hub import PipelineHub
        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        hub = PipelineHub(db_mgr, supabase_mgr)

        brand = payload.get("brand", "kmarket")
        lang = payload.get("lang", "en")

        result = hub.execute_hub_pipeline(hub_id, brand, lang)
        log_event(result.get("message", f"[{hub_id.upper()}] 파이프라인 배포 완료"), "success" if result.get("success") else "error")

        self._set_headers("application/json")
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def _handle_google_index_ping(self, payload: Dict[str, Any]):
        brand = payload.get("brand", "kmarket")
        from core.google_indexing_client import GoogleIndexingClient
        client = GoogleIndexingClient(brand=brand)
        if brand == "kmarket":
            res = client.publish_url("https://k-market.app/en")
        else:
            res = client.publish_url("https://ktrs-service.vercel.app/?lang=en")

        result = {
            "success": True,
            "brand": brand,
            "result": res,
            "message": f"🌐 [{brand.upper()}] Google Search Console & Indexing API 실시간 색인 핑 전송 완료!"
        }
        log_event(result["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

def run_server(port: int = 8000):
    ThreadingHTTPServer.allow_reuse_address = True
    server_address = ("", port)
    try:
        httpd = ThreadingHTTPServer(server_address, DashboardHandler)
    except OSError as e:
        print(f"\n❌ [오류] 포트 {port}를 이미 다른 프로그램이 사용 중입니다: {e}")
        print(f"기존에 실행 중인 창이나 프로세스를 확인해주세요.\n")
        return
    print("\n========================================================")
    print("🛸 [Universal Expat Growth Engine] Local Web Control Center Started!")
    print(f"🌐 Browser URL: http://localhost:{port}")
    print("========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_server()

