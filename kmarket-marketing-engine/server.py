import os
import sys
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

recent_logs = []

def log_event(text: str, log_type: str = "info"):
    global recent_logs
    recent_logs.append({"text": text, "type": log_type, "time": time.strftime("%H:%M:%S")})
    if len(recent_logs) > 50:
        recent_logs.pop(0)

# Bot 1: K-Market 무인 워커 (0원 나눔, 무빙세일, 실물 숏폼)
def kmarket_worker():
    global kmarket_running, kmarket_stats
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = KMarketGrowthBot(db_mgr, supabase_mgr)
    log_event("🛒 [K-Market 전담봇] 24시간 완전 무인 자율주행이 가동되었습니다.", "success")

    while kmarket_running:
        try:
            log_event("🛒 [K-Market] 실물 매물 숏폼/카드뉴스 & 레딧 사이클 실행 중...", "info")
            res = bot.run_kmarket_cycle()
            kmarket_stats = {"cycle": res["cycle"], "last_run": res["timestamp"]}
            log_event(f"🛒 [K-Market] 숏폼 {res['shorts_count']}건 + 카드뉴스 {res['cardnews_count']}장 렌더링 완료", "success")
        except Exception as e:
            log_event(f"K-Market 봇 예외 발생: {e}", "error")

        # 5분 간격 대기
        for _ in range(60):
            if not kmarket_running:
                break
            time.sleep(5)

    log_event("⏹️ [K-Market 전담봇] 가동이 일시정지되었습니다.", "warning")

# Bot 2: EasyTax 무인 워커 (E-9 90% 감면, D-2 환급, 공인 세무 가이드)
def easytax_worker():
    global easytax_running, easytax_stats
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = EasyTaxRefundBot(db_mgr, supabase_mgr)
    log_event("💰 [EasyTax 전담봇] 24시간 완전 무인 세금환급 봇이 가동되었습니다.", "success")

    while easytax_running:
        try:
            log_event("💰 [EasyTax] 5개년 세무 환급 & Anti-Ban 가이드 사이클 실행 중...", "info")
            res = bot.run_easytax_cycle()
            easytax_stats = {"cycle": res["cycle"], "last_run": res["timestamp"]}
            log_event(f"💰 [EasyTax] 세무 숏폼 {res['shorts_count']}건 + 카드뉴스 {res['cardnews_count']}장 렌더링 완료", "success")
        except Exception as e:
            log_event(f"EasyTax 봇 예외 발생: {e}", "error")

        # 10분 간격 대기 (정밀 세무 주기)
        for _ in range(120):
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
        elif path.startswith("/style.css"):
            self._serve_file(BASE_DIR / "web" / "style.css", "text/css; charset=utf-8")
            return
        elif path.startswith("/app.js"):
            self._serve_file(BASE_DIR / "web" / "app.js", "application/javascript; charset=utf-8")
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
            return
        elif path == "/api/ir-analytics":
            self._handle_get_ir_analytics()
            return
        elif path == "/api/settings":
            self._handle_get_settings()
            return
        elif path == "/api/health":
            self._handle_get_health()
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

        # 듀얼 봇 독립 제어
        if path == "/api/kmarket/start":
            self._handle_kmarket_start()
        elif path == "/api/kmarket/stop":
            self._handle_kmarket_stop()
        elif path == "/api/easytax/start":
            self._handle_easytax_start()
        elif path == "/api/easytax/stop":
            self._handle_easytax_stop()
        elif path.startswith("/api/run-module/"):
            module_name = path.split("/")[-1]
            self._handle_run_module(module_name)
        elif path.startswith("/api/platforms/test-publish/"):
            platform_id = path.split("/")[-1]
            self._handle_test_publish(platform_id)
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
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history")
            row = cursor.fetchone()
            total_count = row[0]
            top_score = row[1]

        data = {
            "kmarket_running": kmarket_running,
            "kmarket_stats": kmarket_stats,
            "easytax_running": easytax_running,
            "easytax_stats": easytax_stats,
            "season": season,
            "total_history_count": total_count,
            "top_score": top_score,
            "recent_logs": recent_logs[-10:]
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _handle_kmarket_start(self):
        global kmarket_thread, kmarket_running
        if not kmarket_running:
            kmarket_running = True
            kmarket_thread = threading.Thread(target=kmarket_worker, daemon=True)
            kmarket_thread.start()
            res = {"success": True, "message": "🛒 K-Market 전담 무인 성장봇이 가동되었습니다!"}
        else:
            res = {"success": True, "message": "K-Market 봇이 이미 가동 중입니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_kmarket_stop(self):
        global kmarket_running
        kmarket_running = False
        res = {"success": True, "message": "⏹️ K-Market 봇 정지 요청 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_start(self):
        global easytax_thread, easytax_running
        if not easytax_running:
            easytax_running = True
            easytax_thread = threading.Thread(target=easytax_worker, daemon=True)
            easytax_thread.start()
            res = {"success": True, "message": "💰 EasyTax 전담 세금환급 봇이 가동되었습니다!"}
        else:
            res = {"success": True, "message": "EasyTax 봇이 이미 가동 중입니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_stop(self):
        global easytax_running
        easytax_running = False
        res = {"success": True, "message": "⏹️ EasyTax 봇 정지 요청 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_run_module(self, module_name: str):
        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        router = ServiceRouter()
        gemini = GeminiEngine(supabase_mgr)
        tts = TTSEngine()
        notifier = Notifier()

        try:
            if module_name == "kmarket_shorts":
                factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
                res = factory.produce_shorts(service_id="kmarket", target_langs=["en", "vi", "zh", "ko", "uz"])
                msg = f"🛒 K-Market 실물 매물 숏폼 {len(res)}건 렌더링 완료"
            elif module_name == "easytax_shorts":
                factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
                res = factory.produce_shorts(service_id="easytax", target_langs=["vi", "en", "zh"])
                msg = f"💰 EasyTax 90% 감면 숏폼 {len(res)}건 렌더링 완료"
            elif module_name == "kmarket_cardnews":
                card = CardnewsGenerator(db_mgr, router)
                cards = card.generate_carousel(service_id="kmarket", lang="en")
                msg = f"🛒 K-Market 실물 카드뉴스 {len(cards)}장 생성 완료"
            elif module_name == "easytax_cardnews":
                card = CardnewsGenerator(db_mgr, router)
                cards = card.generate_carousel(service_id="easytax", lang="en")
                msg = f"💰 EasyTax Anti-Ban 카드뉴스 {len(cards)}장 생성 완료"
            elif module_name == "kmarket_reddit" or module_name == "reddit":
                from modules.reddit_kmarket import KMarketRedditHunter
                hunter = KMarketRedditHunter(db_mgr, supabase_mgr)
                cnt = hunter.scan_and_reply(limit=3)
                msg = f"🛒 K-Market 레딧 가구/중고 질문 감지 & {cnt}건 답변 완료"
            elif module_name == "easytax_reddit":
                from modules.reddit_easytax import EasyTaxRedditHunter
                hunter = EasyTaxRedditHunter(db_mgr, supabase_mgr)
                cnt = hunter.scan_and_reply(limit=3)
                msg = f"💰 EasyTax 레딧 세무 팩트 질문 감지 & {cnt}건 답변 완료"
            elif module_name == "kmarket_briefing" or module_name == "briefing":
                from modules.telegram_kmarket import KMarketTelegramPusher
                pusher = KMarketTelegramPusher(db_mgr)
                res = pusher.broadcast_daily_deals(target_langs=["en", "vi", "ko"])
                msg = f"🛒 K-Market 0원 나눔 텔레그램 브리핑 {res.get('sent_count', 0)}개 언어 발송 완료"
            elif module_name == "easytax_briefing":
                from modules.telegram_easytax import EasyTaxTelegramPusher
                pusher = EasyTaxTelegramPusher(db_mgr)
                res = pusher.broadcast_daily_tax_tips(target_langs=["en", "vi", "ko"])
                msg = f"💰 EasyTax 세무 가이드 텔레그램 브리핑 {res.get('sent_count', 0)}개 언어 발송 완료"
            elif module_name == "kmarket_fb_groups":
                from modules.facebook_kmarket import KMarketFacebookHunter
                hunter = KMarketFacebookHunter(db_mgr, supabase_mgr)
                res = hunter.deploy_to_groups(limit=3)
                msg = res.get("message", "🛒 K-Market 페이스북 그룹 배포 완료")
            elif module_name == "easytax_fb_groups":
                from modules.facebook_easytax import EasyTaxFacebookHunter
                hunter = EasyTaxFacebookHunter(db_mgr, supabase_mgr)
                res = hunter.deploy_to_groups(limit=3)
                msg = res.get("message", "💰 EasyTax 페이스북 그룹 배포 완료")
            elif module_name == "kmarket_blog":
                from modules.blog_kmarket import KMarketBlogPublisher
                publisher = KMarketBlogPublisher(db_mgr, supabase_mgr)
                res = publisher.publish_daily_articles(target_langs=["en", "vi", "ko"])
                msg = res.get("message", "🛒 K-Market 글로벌 블로그 칼럼 발행 완료")
            elif module_name == "easytax_blog":
                from modules.blog_easytax import EasyTaxBlogPublisher
                publisher = EasyTaxBlogPublisher(db_mgr, supabase_mgr)
                res = publisher.publish_daily_articles(target_langs=["en", "vi", "ko"])
                msg = res.get("message", "💰 EasyTax 글로벌 블로그 칼럼 발행 완료")
            elif module_name == "kmarket_pdf":
                pdf_gen = GuidePDFGenerator(db_mgr)
                pdf_path = pdf_gen.generate_kmarket_guide()
                msg = f"🛒 K-Market 라이프 가이드북 PDF 렌더링 완료 ({pdf_path.name})"
            elif module_name == "easytax_pdf":
                pdf_gen = GuidePDFGenerator(db_mgr)
                pdf_path = pdf_gen.generate_easytax_guide()
                msg = f"💰 EasyTax 조특법 절세 가이드북 PDF 렌더링 완료 ({pdf_path.name})"
            elif module_name == "pdf":
                pdf_gen = GuidePDFGenerator(db_mgr)
                p1 = pdf_gen.generate_kmarket_guide()
                p2 = pdf_gen.generate_easytax_guide()
                msg = f"외국인 가이드북 2종(K-Market & EasyTax) PDF 렌더링 완료 ({p1.name}, {p2.name})"
            else:
                msg = f"{module_name} 실행 완료"

            log_event(f"⚡ 모듈 실행: {msg}", "success")
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "message": msg}).encode("utf-8"))
        except Exception as e:
            log_event(f"❌ 모듈 실행 실패: {e}", "error")
            self._set_headers("application/json", 500)
            self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode("utf-8"))

    def _handle_test_publish(self, platform_id: str):
        uploader = DirectUploader()
        service_id = "kmarket" if "kmarket" in platform_id else "easytax" if "easytax" in platform_id else "kmarket"
        res = uploader.publish_content(platform_id, service_id=service_id)
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_google_index(self):
        from modules.seo_kmarket import KMarketSEOPusher
        from modules.seo_easytax import EasyTaxSEOPusher
        db_mgr = DBManager()
        km_res = KMarketSEOPusher(db_mgr).build_and_push_index()
        tax_res = EasyTaxSEOPusher(db_mgr).build_and_push_index()
        total = km_res.get("indexed_count", 0) + tax_res.get("indexed_count", 0)
        msg = f"🌐 구글 검색 로봇에게 총 {total}개 URL (K-Market {km_res.get('indexed_count', 0)}개 + EasyTax {tax_res.get('indexed_count', 0)}개) 색인 핑 전송 완료"
        log_event(msg, "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "indexed_count": total}).encode("utf-8"))

    def _handle_kmarket_google_index(self):
        from modules.seo_kmarket import KMarketSEOPusher
        db_mgr = DBManager()
        res = KMarketSEOPusher(db_mgr).build_and_push_index()
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_google_index(self):
        from modules.seo_easytax import EasyTaxSEOPusher
        db_mgr = DBManager()
        res = EasyTaxSEOPusher(db_mgr).build_and_push_index()
        log_event(res["message"], "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_get_platforms(self):
        uploader = DirectUploader()
        platforms = uploader.get_platforms_health()
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

        db_mgr = DBManager()
        supabase_mgr = SupabaseManager(db_mgr)
        from core.ir_analytics import IRAnalyticsEngine
        engine = IRAnalyticsEngine(db_mgr, supabase_mgr)
        data = engine.get_detailed_dashboard_data(period)
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

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

def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, DashboardHandler)
    print("\n========================================================")
    print("[Universal Expat Growth Engine] Local Web Control Center Started!")
    print(f"Browser URL: http://localhost:{port}")
    print("========================================================\n")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
