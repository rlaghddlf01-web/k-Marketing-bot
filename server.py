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
import logging
import threading
import time
from datetime import datetime
import mimetypes
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

class DummyBrandService:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        return lambda *args, **kwargs: None
    def __bool__(self):
        return False



from config import (
    OUTPUTS_DIR, BASE_DIR as CFG_BASE_DIR, DATA_DIR, KST, get_now_kst, get_now_kst_str,
    GOLDEN_EIGHT_LANGUAGES, GOLDEN_EIGHT_DETAILS, get_next_golden_eight_language, get_golden_rotation_info
)
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.service_router import ServiceRouter
from core.season_tuner import SeasonTuner
from core.gemini_engine import GeminiEngine
from core.tts_engine import TTSEngine
from core.notifier import Notifier
from core.kmarket_bot import KMarketGrowthBot
from core.easytax_bot import EasyTaxRefundBot
from core.blog_scheduler import BlogScheduler
from core.engine.gpu_lock import gpu_lock_manager

from modules.reddit_lead_hunter import RedditLeadHunter
from modules.shorts_video_factory import ShortsVideoFactory
from modules.programmatic_seo import ProgrammaticSEO
from modules.cardnews_generator import CardnewsGenerator
from modules.free_stuff_notifier import FreeStuffNotifier
from modules.guide_pdf_generator import GuidePDFGenerator
from core.direct_uploader import DirectUploader
from core.telegram_ai_community_manager import TelegramAICommunityManager
from core.telegram_member_scraper import TelegramMemberScraper
from core.telegram_outreach_poster import TelegramOutreachPoster
from core.telegram_stealth_inviter import TelegramStealthInviter
from modules.telegram_community_publisher import TelegramCommunityPublisher
from core.golden_batch_producer import GoldenBatchProducer
from core.today_live_tracker import TodayLiveTracker

# 🚀 3대 브랜드 실시간 마케팅 무인 발행 라이브 피드 추적기
today_live_tracker = TodayLiveTracker()

# 🌟 8대 황금 타깃 듀얼 브랜드 대량 생산 배치 프로듀서
golden_batch_producer = GoldenBatchProducer()

# 🌟 8대 황금 타깃 무단 자동 실행 전면 차단 (수동 클릭 전용)
golden_batch_daemon_running = {
    "kmarket": False,
    "easytax": False,
    "all": False
}

def _golden_daemon_loop(brand: str):
    log_event(f"ℹ️ [골든 배치] {brand.upper()} 수동 1회 실행 대기 모드 (무단 자동 발행 차단됨)", "info")
    # 무단 자동 무한 루프 차단: 오직 대시보드 버튼 클릭 시 1회성 실행만 지원

# 💖 2026 대한민국 3대 슈퍼앱 전용 24대 옴니채널 마케팅 파이프라인
try:
    from brands.aura.aura_pipeline import AuraPipeline
    aura_pipeline = AuraPipeline(dry_run=False)
except Exception as e:
    aura_pipeline = None

try:
    from brands.insurance.insurance_pipeline import InsurancePipeline
    insurance_pipeline = InsurancePipeline(dry_run=False)
except Exception as e:
    insurance_pipeline = None

try:
    from brands.stock.stock_pipeline import StockPipeline
    stock_pipeline = StockPipeline(dry_run=False)
except Exception as e:
    stock_pipeline = None

brand_pipelines = {
    "aura": aura_pipeline,
    "insurance": insurance_pipeline,
    "stock": stock_pipeline
}

brand_daemons_running = {
    "aura": False,
    "insurance": False,
    "stock": False
}

brand_stats = {
    "aura": {"cycle": 0, "last_run": "대기 중", "total_published": 0},
    "insurance": {"cycle": 0, "last_run": "대기 중", "total_published": 0},
    "stock": {"cycle": 0, "last_run": "대기 중", "total_published": 0}
}

def _brand_kin_worker(brand: str):
    name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 Stock Master 주식AI"}
    brand_kr = name_map.get(brand, brand.upper())
    
    # 각 브랜드 전용 독립 레고 블록 지식iN 스케줄러 로드
    scheduler = None
    try:
        if brand == "aura":
            from brands.aura.aura_kin_scheduler import AuraKinScheduler
            scheduler = AuraKinScheduler()
        elif brand == "insurance":
            from brands.insurance.insurance_kin_scheduler import InsuranceKinScheduler
            scheduler = InsuranceKinScheduler()
        elif brand == "stock":
            from brands.stock.stock_kin_scheduler import StockKinScheduler
            scheduler = StockKinScheduler()
    except Exception as ie:
        log_event(f"❌ [{brand_kr} 지식iN 스케줄러 로드 실패] {ie}", "error")
        return

    log_event(f"🎯 [{brand_kr}] 네이버 지식iN 24시간 실시간 레이더 가동 시작 (300초 주기 / 1일 10건 목표)", "success")

    while brand_daemons_running.get(brand, False):
        try:
            res = scheduler.trigger_scheduled_catch()
            status = res.get("status", "")
            
            if res.get("success"):
                rec = res.get("record", {})
                pub_url = res.get("published_url", "")
                daily_total = res.get("daily_total", 1)
                log_event(f"🎉 [{brand_kr} 지식iN 등록 성공!] '{rec.get('title', '')}' ➔ {pub_url} (오늘 누적 {daily_total}/10건)", "success")
            elif status == "daily_quota_full" or status == "daily_limit_reached":
                # 당일 10개 쿼터 완료 시 조용히 대기 (과도한 로그 방지)
                pass
            elif status == "login_required":
                log_event(f"⚠️ [{brand_kr} 지식iN] 네이버 1회 로그인 세션 저장이 필요합니다.", "warning")
            else:
                msg = res.get("message")
                if msg and "새로운 질문이 없습니다" not in msg and "금일 목표" not in msg:
                    log_event(f"ℹ️ [{brand_kr} 지식iN] {msg}", "info")
        except Exception as e:
            log_event(f"⚠️ [{brand_kr} 지식iN 레이더 예외] {e}", "warning")

        # 300초(5분) 대기 (5초 슬립 루프로 정지 신호 즉시 감지)
        for _ in range(60):
            if not brand_daemons_running.get(brand, False):
                break
            time.sleep(5)

    log_event(f"⏹️ [{brand_kr}] 네이버 지식iN 무인 레이더가 정지되었습니다.", "info")



def _brand_blog_worker(brand: str):
    """
    ⏰ [정시 무인 스케줄러 - 15분 시차 분산(Staggered) + 슬롯 윈도우 자율 보정]
    - 제미나이 무료 키 및 IP/서버 부하 분산을 위해 브랜드별 15분 간격 분산 발행:
      * 💖 Aura AI 데이팅: 09:45 / 14:45 / 19:45 KST
      * 🛡️ 보험 리밸런스: 10:00 / 15:00 / 20:00 KST
      * 📈 StockMaster AI: 10:15 / 15:15 / 20:15 KST
    """
    name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 Stock Master 주식AI"}
    brand_kr = name_map.get(brand, brand.upper())

    if brand == "aura":
        slots = [
            ("slot_1", 9, 45, 14, 44, "오전 09:45"),
            ("slot_2", 14, 45, 19, 44, "오후 14:45"),
            ("slot_3", 19, 45, 23, 59, "저녁 19:45"),
        ]
    elif brand == "insurance":
        slots = [
            ("slot_1", 10, 0, 14, 59, "오전 10:00"),
            ("slot_2", 15, 0, 19, 59, "오후 15:00"),
            ("slot_3", 20, 0, 23, 59, "저녁 20:00"),
        ]
    else:  # stock
        slots = [
            ("slot_1", 10, 15, 15, 14, "오전 10:15"),
            ("slot_2", 15, 15, 20, 14, "오후 15:15"),
            ("slot_3", 20, 15, 23, 59, "저녁 20:15"),
        ]

    slot_desc = " / ".join([s[5] for s in slots])
    log_event(f"⏰ [{brand_kr}] 4대 채널 옴니 블로그 15분 시차 정시 스케줄러 가동 ({slot_desc})", "success")
    executed_slots = set()

    # 서버 재시작 시 디스크에 이미 기록된 오늘자 발행 내역을 executed_slots에 사전 복원
    try:
        if brand == "aura":
            from brands.aura.aura_blog_scheduler import AuraBlogScheduler
            s_inst = AuraBlogScheduler()
        elif brand == "insurance":
            from brands.insurance.insurance_blog_scheduler import InsuranceBlogScheduler
            s_inst = InsuranceBlogScheduler()
        else:
            from brands.stock.stock_blog_scheduler import StockBlogScheduler
            s_inst = StockBlogScheduler()

        today_init = get_now_kst().strftime("%Y-%m-%d")
        for h in s_inst.state.get("history", []):
            if (h.get("published_at") or "").startswith(today_init):
                # 오늘 이미 발행된 건수만큼 슬롯을 사전 잠금
                executed_slots.add(f"{today_init}_slot_1")
    except Exception:
        pass

    while brand_daemons_running.get(brand, False):
        try:
            now = get_now_kst()
            today_str = now.strftime("%Y-%m-%d")
            cur_min = now.hour * 60 + now.minute

            for slot_id, s_h, s_m, e_h, e_m, s_label in slots:
                start_total = s_h * 60 + s_m
                end_total = e_h * 60 + e_m
                slot_key = f"{today_str}_{slot_id}"

                if start_total <= cur_min <= end_total and slot_key not in executed_slots:
                    executed_slots.add(slot_key)

                    if brand == "aura":
                        from brands.aura.aura_blog_scheduler import AuraBlogScheduler
                        scheduler = AuraBlogScheduler()
                        res = scheduler.run_one_cycle()
                        if res.get("status") == "BLOCKED_DAILY_CAP":
                            log_event(f"ℹ️ [{brand_kr}] {s_label} 스케줄: {res.get('message')}", "info")
                            continue

                        brand_stats[brand]["cycle"] += 1
                        brand_stats[brand]["last_run"] = get_now_kst_str()
                        brand_stats[brand]["total_published"] = scheduler.state.get("published_count", brand_stats[brand]["total_published"] + 1)
                        naver_url = res.get('publish_results', {}).get('channels', {}).get('naver_blog', {}).get('url', '-')
                        tistory_url = res.get('publish_results', {}).get('channels', {}).get('tistory', {}).get('url', '-')
                        log_event(f"🎉 [{brand_kr}] {s_label} 정시 발행 완료! 주제: '{res.get('title')}' (네이버: {naver_url} | 티스토리: {tistory_url})", "success")

                    elif brand == "insurance":
                        from brands.insurance.insurance_blog_scheduler import InsuranceBlogScheduler
                        scheduler = InsuranceBlogScheduler()
                        res = scheduler.run_one_cycle()
                        if res.get("status") == "BLOCKED_DAILY_CAP":
                            log_event(f"ℹ️ [{brand_kr}] {s_label} 스케줄: {res.get('message')}", "info")
                            continue

                        brand_stats[brand]["cycle"] += 1
                        brand_stats[brand]["last_run"] = get_now_kst_str()
                        brand_stats[brand]["total_published"] = scheduler.state.get("published_count", brand_stats[brand]["total_published"] + 1)
                        naver_url = res.get('publish_results', {}).get('channels', {}).get('naver_blog', {}).get('url', '-')
                        tistory_url = res.get('publish_results', {}).get('channels', {}).get('tistory', {}).get('url', '-')
                        log_event(f"🎉 [{brand_kr}] {s_label} 정시 발행 완료! 주제: '{res.get('title')}' (네이버: {naver_url} | 티스토리: {tistory_url})", "success")

                    elif brand == "stock":
                        from brands.stock.stock_blog_scheduler import StockBlogScheduler
                        scheduler = StockBlogScheduler()
                        res = scheduler.run_one_cycle()
                        if res.get("status") == "BLOCKED_DAILY_CAP":
                            log_event(f"ℹ️ [{brand_kr}] {s_label} 스케줄: {res.get('message')}", "info")
                            continue

                        brand_stats[brand]["cycle"] += 1
                        brand_stats[brand]["last_run"] = get_now_kst_str()
                        brand_stats[brand]["total_published"] = scheduler.state.get("published_count", brand_stats[brand]["total_published"] + 1)
                        naver_url = res.get('publish_results', {}).get('channels', {}).get('naver_blog', {}).get('url', '-')
                        tistory_url = res.get('publish_results', {}).get('channels', {}).get('tistory', {}).get('url', '-')
                        log_event(f"🎉 [{brand_kr}] {s_label} 정시 발행 완료! 주제: '{res.get('title')}' (네이버: {naver_url} | 티스토리: {tistory_url})", "success")

            # 5초마다 시계 감시 및 정지 신호 즉시 감지
            for _ in range(6):
                if not brand_daemons_running.get(brand, False):
                    break
                time.sleep(5)

        except Exception as e:
            import traceback
            err_detail = traceback.format_exc()
            log_event(f"❌ [{brand_kr} 블로그 스케줄러 오류] {e}\n{err_detail}", "error")
            time.sleep(10)

    log_event(f"⏹️ [{brand_kr}] 4대 채널 옴니 블로그 무인 스케줄러가 정지되었습니다.", "info")


def _brand_daemon_loop(brand: str):
    name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 Stock Master 주식AI"}
    brand_kr = name_map.get(brand, brand.upper())
    log_event(f"🚀 [{brand_kr}] 무인 자율 마케팅 데몬 가동! (지식iN 24시간 실시간 레이더 + 15분 시차 분산 블로그/카드뉴스/숏폼 스케줄러 탑재)", "success")

    # 1. 지식iN 자율 레이더 스레드 가동 (정해진 5분 주기 감시, 일일 한도 달성 시 취침)
    threading.Thread(target=_brand_kin_worker, args=(brand,), daemon=True).start()

    # 2. 4대 채널 옴니 블로그 무인 정시 스케줄러 가동 (15분 시차 분산: Aura 45분 / 보험 00분 / 주식 15분)
    threading.Thread(target=_brand_blog_worker, args=(brand,), daemon=True).start()

    # 3. 🤖 [24시간 무인 인간 행동 봇 (08:30, 12:30, 15:30, 21:30 KST - 하루 45분 체류 및 3~5회 좋아요, 0 API)]
    def _human_behavior_worker():
        while brand_daemons_running.get(brand, False):
            try:
                if brand == "aura":
                    from brands.aura.aura_human_behavior_bot import AuraHumanBehaviorBot
                    AuraHumanBehaviorBot(headless=True).run_daemon()
                elif brand == "insurance":
                    from brands.insurance.insurance_human_behavior_bot import InsuranceHumanBehaviorBot
                    InsuranceHumanBehaviorBot(headless=True).run_daemon()
                elif brand == "stock":
                    from brands.stock.stock_human_behavior_bot import StockHumanBehaviorBot
                    StockHumanBehaviorBot(headless=True).run_daemon()
            except Exception as he:
                log_event(f"⚠️ [{brand_kr} 인간 행동 봇 데몬 예외] {he}", "warning")
            time.sleep(30)
    threading.Thread(target=_human_behavior_worker, daemon=True).start()

    # 4. 🎬 [골든타임 15분 시차 숏폼 데몬 - 하루 3회 (오전/점심/저녁) 슬롯 윈도우 자율 단발 생산 & 4대 채널 송출]
    def _omni_shorts_daemon_worker():
        if brand == "aura":
            shorts_slots = [
                ("morning", 9, 30, 12, 14, "오전 09:30"),
                ("lunch", 12, 15, 18, 14, "점심 12:15"),
                ("evening", 18, 15, 23, 59, "저녁 18:15")
            ]
        elif brand == "insurance":
            shorts_slots = [
                ("morning", 9, 45, 12, 29, "오전 09:45"),
                ("lunch", 12, 30, 18, 29, "점심 12:30"),
                ("evening", 18, 30, 23, 59, "저녁 18:30")
            ]
        else:  # stock
            shorts_slots = [
                ("morning", 10, 0, 12, 44, "오전 10:00"),
                ("lunch", 12, 45, 18, 44, "점심 12:45"),
                ("evening", 18, 45, 23, 59, "저녁 18:45")
            ]

        executed_shorts_slots = set()
        slot_desc = " / ".join([s[5] for s in shorts_slots])
        log_event(f"🎬 [{brand_kr}] 숏폼 하루 3회 슬롯 윈도우 스케줄러 상주 가동 (매일 {slot_desc} KST)", "success")
        
        while brand_daemons_running.get(brand, False):
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                for slot_id, s_h, s_m, e_h, e_m, s_label in shorts_slots:
                    start_total = s_h * 60 + s_m
                    end_total = e_h * 60 + e_m
                    slot_key = f"{today_str}_{slot_id}"

                    if start_total <= cur_min <= end_total and slot_key not in executed_shorts_slots:
                        executed_shorts_slots.add(slot_key)
                        time_label = "오전" if s_h < 12 else ("점심" if s_h < 17 else "저녁")
                        log_event(f"⏰ [{brand_kr}] {time_label} {s_h:02d}:{s_m:02d} 골든타임 도달! 쏘기 직전 숏폼 1편 신선 제작 및 4대 채널 단발 송출 시작...", "info")
                        res = {}
                        if brand == "aura":
                            from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
                            res = AuraOmniShortsPilot().execute_single_slot()
                        elif brand == "insurance":
                            from brands.insurance.insurance_omni_shorts_pilot import InsuranceOmniShortsPilot
                            res = InsuranceOmniShortsPilot().execute_single_slot()
                        elif brand == "stock":
                            from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
                            res = StockOmniShortsPilot().execute_single_slot()
                        
                        status = res.get("status", "unknown") if isinstance(res, dict) else "done"
                        if status == "success":
                            log_event(f"🎉 [{brand_kr}] {time_label} 숏폼 4대 채널 송출 성공! ({res.get('title', '')})", "success")
                        elif status == "skipped":
                            log_event(f"ℹ️ [{brand_kr}] 숏폼 송출 스킵: {res.get('message', '')}", "info")
                        else:
                            log_event(f"⚠️ [{brand_kr}] 숏폼 송출 결과: {res.get('error') or res.get('message') or status}", "warning")
            except Exception as se:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"⚠️ [{brand_kr} 숏폼 정시 데몬 예외 발생 - 자동 복구됨] {se}\n{err_detail}", "warning")
            time.sleep(20)
    threading.Thread(target=_omni_shorts_daemon_worker, daemon=True).start()

    # 5. 📸 [1일 3회 순차 롤링 카드뉴스 데몬 - 1차 오전(10:30~11:00) / 2차 오후(14:30~15:00) / 3차 저녁(20:30~21:00) KST]
    def _omni_cardnews_daemon_worker():
        if brand == "aura":
            card_slots = [
                ("morning", 10, 30, 14, 29, "오전 10:30"),
                ("afternoon", 14, 30, 20, 29, "오후 14:30"),
                ("evening", 20, 30, 23, 59, "저녁 20:30")
            ]
        elif brand == "insurance":
            card_slots = [
                ("morning", 10, 45, 14, 44, "오전 10:45"),
                ("afternoon", 14, 45, 20, 44, "오후 14:45"),
                ("evening", 20, 45, 23, 59, "저녁 20:45")
            ]
        else:  # stock
            card_slots = [
                ("morning", 11, 0, 14, 59, "오전 11:00"),
                ("afternoon", 15, 0, 20, 59, "오후 15:00"),
                ("evening", 21, 0, 23, 59, "저녁 21:00")
            ]

        executed_card_slots = set()
        slot_desc = " / ".join([s[5] for s in card_slots])
        log_event(f"📸 [{brand_kr}] 카드뉴스 하루 3회 슬롯 윈도우 스케줄러 상주 가동 (매일 {slot_desc} KST)", "success")

        while brand_daemons_running.get(brand, False):
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                for slot_id, c_h, c_m, e_h, e_m, c_label in card_slots:
                    start_total = c_h * 60 + c_m
                    end_total = e_h * 60 + e_m
                    slot_key = f"{today_str}_{slot_id}"

                    if start_total <= cur_min <= end_total and slot_key not in executed_card_slots:
                        executed_card_slots.add(slot_key)
                        time_label = "점심" if c_h < 15 else "야간"
                        log_event(f"⏰ [{brand_kr}] {time_label} {c_h:02d}:{c_m:02d} 골든타임 도달! 쏘기 직전 순차 5장 카드뉴스 제작 및 Meta 단발 송출 시작...", "info")
                        res = {}
                        if brand == "aura":
                            from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
                            res = AuraOmniCardnewsPilot().execute_single_slot()
                        elif brand == "insurance":
                            from brands.insurance.insurance_omni_cardnews_pilot import InsuranceOmniCardnewsPilot
                            res = InsuranceOmniCardnewsPilot().execute_single_slot()
                        elif brand == "stock":
                            from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
                            res = StockOmniCardnewsPilot().execute_single_slot()

                        status = res.get("status", "unknown") if isinstance(res, dict) else "done"
                        if status == "success":
                            log_event(f"🎉 [{brand_kr}] {time_label} 카드뉴스 Meta 송출 성공! ({res.get('title', '')})", "success")
                        elif status == "skipped":
                            log_event(f"ℹ️ [{brand_kr}] 카드뉴스 스킵: {res.get('message', '')}", "info")
                        else:
                            log_event(f"⚠️ [{brand_kr}] 카드뉴스 결과: {res.get('error') or res.get('message') or status}", "warning")
            except Exception as ce:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"⚠️ [{brand_kr} 카드뉴스 정시 데몬 예외 발생 - 자동 복구됨] {ce}\n{err_detail}", "warning")
            time.sleep(20)
    threading.Thread(target=_omni_cardnews_daemon_worker, daemon=True).start()

    # 6. 🎬 [24시간 무인 유튜브 전담 30분 스텔스 봇 (09:00, 13:00, 16:30, 22:30 KST - 쇼츠 16~35초 완시청, 댓글 탐색, 좋아요 2~3회, 0 API)]
    def _youtube_behavior_worker():
        while brand_daemons_running.get(brand, False):
            try:
                if brand == "aura":
                    from brands.aura.aura_youtube_behavior_bot import AuraYouTubeBehaviorScheduler
                    AuraYouTubeBehaviorScheduler().start()
                elif brand == "insurance":
                    from brands.insurance.insurance_youtube_behavior_bot import InsuranceYouTubeBehaviorScheduler
                    InsuranceYouTubeBehaviorScheduler().start()
                elif brand == "stock":
                    from brands.stock.stock_youtube_behavior_bot import StockYouTubeBehaviorScheduler
                    StockYouTubeBehaviorScheduler().start()
            except Exception as ye:
                log_event(f"⚠️ [{brand_kr} 유튜브 스텔스 봇 데몬 예외] {ye}", "warning")
            time.sleep(60)
    threading.Thread(target=_youtube_behavior_worker, daemon=True).start()

    # 7. 📱 [24시간 무인 틱톡 전담 30분 스텔스 봇 (09:30, 13:30, 17:00, 23:00 KST - FYP 완시청, 댓글 탐색, 좋아요 2~3회, 0 API)]
    def _tiktok_behavior_worker():
        while brand_daemons_running.get(brand, False):
            try:
                if brand == "aura":
                    from brands.aura.aura_tiktok_behavior_bot import AuraTikTokBehaviorScheduler
                    AuraTikTokBehaviorScheduler().start()
                elif brand == "insurance":
                    from brands.insurance.insurance_tiktok_behavior_bot import InsuranceTikTokBehaviorScheduler
                    InsuranceTikTokBehaviorScheduler().start()
                elif brand == "stock":
                    from brands.stock.stock_tiktok_behavior_bot import StockTikTokBehaviorScheduler
                    StockTikTokBehaviorScheduler().start()
            except Exception as te:
                log_event(f"⚠️ [{brand_kr} 틱톡 스텔스 봇 데몬 예외] {te}", "warning")
            time.sleep(60)
    threading.Thread(target=_tiktok_behavior_worker, daemon=True).start()

    # 8. 🤖 [24시간 무인 레딧 전담 스텔스 안전 침투 데몬 (08:00, 10:00, 13:00, 16:00, 20:00 ±30분 무작위 시프트)]
    def _reddit_daemon_worker():
        channel_key = f"{brand}_reddit"
        log_event(f"🤖 [{brand_kr}] 레딧 24시간 스텔스 안전 침투 데몬 상주 시작 (08:00/10:00/13:00/16:00/20:00 ±30분)", "success")
        while brand_daemons_running.get(brand, False):
            try:
                res = {}
                if brand == "aura":
                    from brands.aura.aura_reddit_engine import AuraRedditEngine
                    aura_reddit = AuraRedditEngine()
                    res = aura_reddit.orchestrator.run_scheduled_session()
                elif brand == "insurance":
                    from brands.insurance.insurance_reddit_engine import InsuranceRedditEngine
                    ins_reddit = InsuranceRedditEngine()
                    res = ins_reddit.orchestrator.run_scheduled_session()
                elif brand == "stock":
                    from brands.stock.stock_reddit_engine import StockRedditEngine
                    stock_reddit = StockRedditEngine()
                    res = stock_reddit.orchestrator.run_scheduled_session()

                if res.get("status") == "executed":
                    clear_channel_error(channel_key)
                    slot_name = res.get("executed_slot", "세션")
                    up = res.get("upvotes", 0)
                    org = res.get("organic_comments", 0)
                    pro = res.get("promo_comments", 0)
                    log_event(f"🎉 [{brand_kr} 레딧 정시 세션 완료] {slot_name} | 업보트: {up}건 | 비홍보댓글: {org}건 | 스텔스홍보: {pro}건", "success")
                elif res.get("status") == "cooldown":
                    log_event(f"🛡️ [{brand_kr} 레딧] 안전 쿨다운 상태로 이번 시간대 대기", "info")
            except Exception as re:
                import traceback
                err_detail = traceback.format_exc()
                record_channel_error(channel_key, str(re))
                log_event(f"❌ [{brand_kr} 레딧 세션 오류] {re}\n{err_detail}", "error")
            time.sleep(60)
    threading.Thread(target=_reddit_daemon_worker, daemon=True).start()

    # 9. ☕ [24시간 무인 네이버 카페 정예 스텔스 침투 데몬 (15분 시차: Aura 14:15 / 보험 14:30 / 주식 14:45 ~ 23:59 슬롯 윈도우 자율 침투)]
    def _brand_cafe_worker():
        import asyncio
        cafe_hour = 14
        cafe_min = 15 if brand == "aura" else (30 if brand == "insurance" else 45)
        start_total = cafe_hour * 60 + cafe_min
        end_total = 23 * 60 + 59
        executed_cafe_slots = set()
        log_event(f"☕ [{brand_kr}] 네이버 카페 슬롯 윈도우 스케줄러 상주 가동 (매일 오후 {cafe_hour:02d}:{cafe_min:02d} KST)", "success")

        while brand_daemons_running.get(brand, False):
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute
                slot_str = f"{today_str}_cafe_{cafe_hour:02d}{cafe_min:02d}"

                if start_total <= cur_min <= end_total and slot_str not in executed_cafe_slots:
                    executed_cafe_slots.add(slot_str)
                    log_event(f"⏰ [{brand_kr}] 오후 {cafe_hour:02d}:{cafe_min:02d} 골든타임 도달! 5일 로테이션 스캔 & 파이썬 100% 심사 침투 가동...", "info")
                    if brand == "aura":
                        from brands.aura.aura_cafe_pipeline import AuraCafePipeline
                        res = asyncio.run(AuraCafePipeline().run_daily_stealth_infiltration(dry_run=False))
                        log_event(f"☕ [Aura 카페 침투 결과] {res.get('status')}: {res.get('message', '완료')}", "success" if "SUCCESS" in str(res.get("status")) else "info")
                    elif brand == "insurance":
                        from brands.insurance.insurance_cafe_pipeline import InsuranceCafePipeline
                        res = asyncio.run(InsuranceCafePipeline().run_daily_stealth_infiltration(dry_run=False))
                        log_event(f"☕ [보험 카페 침투 결과] {res.get('status')}: {res.get('message', '완료')}", "success" if "SUCCESS" in str(res.get("status")) else "info")
                    elif brand == "stock":
                        from brands.stock.stock_cafe_pipeline import StockCafePipeline
                        res = asyncio.run(StockCafePipeline().run_daily_stealth_infiltration(dry_run=False))
                        log_event(f"☕ [주식 카페 침투 결과] {res.get('status')}: {res.get('message', '완료')}", "success" if "SUCCESS" in str(res.get("status")) else "info")
            except Exception as cde:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"⚠️ [{brand_kr} 네이버 카페 데몬 예외 발생 - 자동 복구됨] {cde}\n{err_detail}", "warning")
            time.sleep(20)
    threading.Thread(target=_brand_cafe_worker, daemon=True).start()

    # 10. 🧵 [24시간 무인 스레드 전담 45분 스텔스 봇 (08:45, 12:45, 16:00, 22:00 KST - 하루 45분 체류, 2~3회 좋아요, 0 API)]
    def _threads_human_worker():
        import asyncio
        slots = [
            {"name": "오전 루틴", "start_h": 8, "start_m": 45, "end_h": 9, "end_m": 15, "min": 10, "likes": 1},
            {"name": "점심 루틴", "start_h": 12, "start_m": 45, "end_h": 13, "end_m": 15, "min": 10, "likes": 1},
            {"name": "오후 루틴", "start_h": 16, "start_m": 0, "end_h": 16, "end_m": 30, "min": 10, "likes": 1},
            {"name": "야간 루틴", "start_h": 22, "start_m": 0, "end_h": 22, "end_m": 30, "min": 15, "likes": 2},
        ]
        executed_today = set()
        log_event(f"🧵 [{brand_kr}] 스레드 45분 인간 행동 봇 상주 가동 (08:45, 12:45, 16:00, 22:00 KST)", "success")

        while brand_daemons_running.get(brand, False):
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                curr_h = now.hour
                curr_m = now.minute

                if curr_h == 0 and curr_m < 5:
                    executed_today.clear()

                for s_idx, slot in enumerate(slots):
                    slot_key = f"{today_str}_slot_{s_idx}"
                    if slot_key not in executed_today:
                        if (curr_h > slot["start_h"] or (curr_h == slot["start_h"] and curr_m >= slot["start_m"])):
                            if (curr_h < slot["end_h"] or (curr_h == slot["end_h"] and curr_m <= slot["end_m"])):
                                executed_today.add(slot_key)
                                log_event(f"⏰ [{brand_kr}] 스레드 {slot['name']} 기상! {slot['min']}분 체류 및 하트 탐색 시작...", "info")
                                if brand == "aura":
                                    from brands.aura.aura_threads_human_bot import AuraThreadsHumanBot
                                    res = asyncio.run(AuraThreadsHumanBot(headless=True).run_session(duration_sec=slot["min"]*60, target_likes=slot["likes"]))
                                elif brand == "insurance":
                                    from brands.insurance.insurance_threads_human_bot import InsuranceThreadsHumanBot
                                    res = asyncio.run(InsuranceThreadsHumanBot(headless=True).run_session(duration_sec=slot["min"]*60, target_likes=slot["likes"]))
                                elif brand == "stock":
                                    from brands.stock.stock_threads_human_bot import StockThreadsHumanBot
                                    res = asyncio.run(StockThreadsHumanBot(headless=True).run_session(duration_sec=slot["min"]*60, target_likes=slot["likes"]))
                                log_event(f"🎉 [{brand_kr}] 스레드 {slot['name']} 완료 (체류 {res.get('duration_sec', 0)}초, 정독 {res.get('posts_read', 0)}건, 좋아요 {res.get('likes_given', 0)}건)", "success")
            except Exception as the:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"⚠️ [{brand_kr} 스레드 인간 행동 봇 예외] {the}\n{err_detail}", "warning")
            time.sleep(30)
    threading.Thread(target=_threads_human_worker, daemon=True).start()

    # 11. ✍️ [24시간 무인 스레드 1일 2회 정시 순수 텍스트 AI 발행 (모닝 09:30 / 이브닝 19:30 KST - 사진 0장 + 첫댓글 체인)]
    def _threads_text_worker():
        import asyncio
        text_slots = [
            ("morning", 9, 30, 11, 0, "오전 09:30 모닝 피드"),
            ("evening", 19, 30, 21, 0, "저녁 19:30 퇴근/야간 피크")
        ]
        executed_text_slots = set()
        log_event(f"✍️ [{brand_kr}] 스레드 1일 2회 순수 텍스트 AI 발행 스케줄러 상주 가동 (매일 09:30 / 19:30 KST)", "success")

        while brand_daemons_running.get(brand, False):
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                for slot_id, s_h, s_m, e_h, e_m, s_label in text_slots:
                    start_total = s_h * 60 + s_m
                    end_total = e_h * 60 + e_m
                    slot_key = f"{today_str}_{slot_id}"

                    if start_total <= cur_min <= end_total and slot_key not in executed_text_slots:
                        executed_text_slots.add(slot_key)
                        log_event(f"⏰ [{brand_kr}] {s_label} 도달! Gemini 순수 텍스트 자율 집필 & 스레드 1회 송출 시작...", "info")
                        res = {}
                        if brand == "aura":
                            from brands.aura.aura_threads_text_pipeline import AuraThreadsTextPipeline
                            res = asyncio.run(AuraThreadsTextPipeline(headless=True).execute_slot(slot=slot_id, dry_run=False))
                        elif brand == "insurance":
                            from brands.insurance.insurance_threads_text_pipeline import InsuranceThreadsTextPipeline
                            res = asyncio.run(InsuranceThreadsTextPipeline(headless=True).execute_slot(slot=slot_id, dry_run=False))
                        elif brand == "stock":
                            from brands.stock.stock_threads_text_pipeline import StockThreadsTextPipeline
                            res = asyncio.run(StockThreadsTextPipeline(headless=True).execute_slot(slot=slot_id, dry_run=False))

                        if res.get("success"):
                            log_event(f"🎉 [{brand_kr}] {s_label} 스레드 발행 성공! (사진 0장 + 첫댓글 체인 완료)", "success")
                        else:
                            log_event(f"⚠️ [{brand_kr}] {s_label} 스레드 발행 결과: {res.get('publish_result', {}).get('message', '실패')}", "warning")
            except Exception as tte:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"⚠️ [{brand_kr} 스레드 텍스트 정시 데몬 예외 발생 - 자동 복구됨] {tte}\n{err_detail}", "warning")
            time.sleep(20)
    threading.Thread(target=_threads_text_worker, daemon=True).start()


# 📲 텔레그램 24시간 커뮤니티 — 브랜드별 독립 인스턴스 (K-Market / EasyTax 완전 분리)
telegram_ai_managers = {
    "kmarket": TelegramAICommunityManager(brand="kmarket"),
    "easytax": TelegramAICommunityManager(brand="easytax")
}
# [방법 1] 타 그룹 홍보 게시 엔진 (브랜드별 독립 세션)
telegram_outreach_posters = {
    "kmarket": TelegramOutreachPoster(brand="kmarket"),
    "easytax": TelegramOutreachPoster(brand="easytax")
}
# [초대] 서브폰 스텔스 초대기 (브랜드별 독립 세션)
telegram_stealth_inviters = {
    "kmarket": TelegramStealthInviter(brand="kmarket"),
    "easytax": TelegramStealthInviter(brand="easytax")
}
telegram_scraper = TelegramMemberScraper()
telegram_publisher = TelegramCommunityPublisher()

# 🇰🇷 대한민국 3대 슈퍼앱 텔레그램 독립 레고 블록 엔진 (Aura / InsureBalance / StockMaster)
try:
    from brands.aura.aura_telegram_engine import AuraTelegramEngine
except (ImportError, ModuleNotFoundError):
    AuraTelegramEngine = DummyBrandService
try:
    from brands.insurance.insurance_telegram_engine import InsuranceTelegramEngine
except (ImportError, ModuleNotFoundError):
    InsuranceTelegramEngine = DummyBrandService
try:
    from brands.stock.stock_telegram_engine import StockTelegramEngine
except (ImportError, ModuleNotFoundError):
    StockTelegramEngine = DummyBrandService

domestic_telegram_engines = {
    "aura": AuraTelegramEngine(),
    "insurance": InsuranceTelegramEngine(),
    "stock": StockTelegramEngine()
}

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

from core.ab_evolution_engine import ABEvolutionEngine

recent_logs = []
channel_errors: Dict[str, Dict[str, Any]] = {}

def record_channel_error(channel_key: str, error_msg: str):
    """🚨 특정 채널 먹통/에러 발생 시 대시보드 실시간 알림 큐에 등록"""
    global channel_errors
    now_kst = get_now_kst()
    clean_err = str(error_msg).replace("\n", " ")[:150]
    channel_errors[channel_key] = {
        "channel": channel_key,
        "error": clean_err,
        "time": now_kst.strftime("%H:%M:%S"),
        "timestamp": now_kst.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ERROR"
    }
    log_event(f"🚨 [{channel_key}] 채널 장애/먹통 감지! {clean_err}", "error")

def clear_channel_error(channel_key: str):
    """✅ 채널 정상 작동 시 장애 상태 자동 해제"""
    global channel_errors
    if channel_key in channel_errors:
        channel_errors.pop(channel_key, None)

ab_evolution_engine = ABEvolutionEngine()
MEDIA_ENGINE_SETTINGS_FILE = DATA_DIR / "media_engine_settings.json"

def get_media_engine_settings() -> dict:
    if MEDIA_ENGINE_SETTINGS_FILE.exists():
        try:
            with open(MEDIA_ENGINE_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "kmarket_shorts": "ab_auto",
        "kmarket_cardnews": "ab_auto",
        "easytax_shorts": "ab_auto",
        "easytax_cardnews": "ab_auto"
    }

def set_media_engine_setting(channel_key: str, engine_mode: str):
    settings = get_media_engine_settings()
    settings[channel_key] = engine_mode
    try:
        MEDIA_ENGINE_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEDIA_ENGINE_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass

log_counter = 0

def log_event(text: str, log_type: str = "info"):
    global recent_logs, log_counter
    log_counter += 1
    now_kst = get_now_kst()
    time_str = now_kst.strftime("%H:%M:%S")
    timestamp_str = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    recent_logs.append({
        "id": log_counter,
        "text": text,
        "type": log_type,
        "time": time_str,
        "timestamp": timestamp_str
    })
    if len(recent_logs) > 200:
        recent_logs.pop(0)

class DashboardLoggingHandler(logging.Handler):
    """모든 브랜드/엔진의 Python 표준 로거 이벤트를 가로채 대시보드 실시간 로그에 포워딩"""
    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                lvl = "error"
            elif record.levelno >= logging.WARNING:
                lvl = "warning"
            elif any(w in msg for w in ["성공", "완료", "SUCCESS", "배포", "🎉", "🚀", "✅"]):
                lvl = "success"
            else:
                lvl = "info"

            if record.exc_info:
                import traceback
                tb = "".join(traceback.format_exception(*record.exc_info))
                msg = f"{msg}\n[상세 오류 원인 및 추적]\n{tb}"

            log_event(msg, lvl)
        except Exception:
            pass

_dash_handler = DashboardLoggingHandler()
_dash_handler.setFormatter(logging.Formatter("%(message)s"))
_dash_handler.setLevel(logging.INFO)

for _name in [
    "AuraBlogScheduler", "AuraBlogEngine", "AuraMultiPublisher",
    "AuraNaverPublisher", "AuraTistoryPublisher", "AuraBrunchPublisher",
    "AuraSupabaseManager", "AuraPipeline", "InsurancePipeline", "StockPipeline",
    "AuraRedditEngine", "AuraRedditScanner", "AuraRedditCopywriter",
    "InsuranceRedditEngine", "InsuranceRedditScanner", "InsuranceRedditCopywriter",
    "StockRedditEngine", "StockRedditScanner", "StockRedditCopywriter",
    "RedditBrowserDriver", "RedditSafetyOrchestrator", "RedditOrganicEngine", "AccountHealthMonitor",
    "ChannelScheduler",
    "AuraYouTubeScheduler", "AuraYouTubeAPIPublisher", "AuraYouTubeBotPublisher", "AuraYouTubeHybridPilot",
    "AuraMetaScheduler", "AuraMetaPublisher",
    "InsuranceYouTubeScheduler", "InsuranceYouTubeAPIPublisher", "InsuranceYouTubeBotPublisher", "InsuranceYouTubeHybridPilot",
    "InsuranceMetaScheduler", "InsuranceMetaPublisher",
    "StockShortsScheduler", "StockQuantShortsBuilder", "StockYouTubeAPIPublisher", "StockYouTubeBotPublisher", 
    "StockMetaScheduler", "StockMetaPublisher",
    "AuraKinScanner", "InsuranceKinScanner", "StockKinScanner",
    "AuraHumanBehaviorBot", "InsuranceHumanBehaviorBot", "StockHumanBehaviorBot",
    "AuraMetaStealthIncubator", "InsuranceMetaStealthIncubator", "StockMetaStealthIncubator",
    "AuraYouTubeBehaviorBot", "InsuranceYouTubeBehaviorBot", "StockYouTubeBehaviorBot",
    "AuraYouTubeBehaviorScheduler", "InsuranceYouTubeBehaviorScheduler", "StockYouTubeBehaviorScheduler",
    "AuraYouTubeIncubator", "InsuranceYouTubeIncubator", "StockYouTubeIncubator",
    "AuraTikTokBehaviorBot", "InsuranceTikTokBehaviorBot", "StockTikTokBehaviorBot",
    "AuraTikTokBehaviorScheduler", "InsuranceTikTokBehaviorScheduler", "StockTikTokBehaviorScheduler",
    "AuraThreadsHumanBot", "InsuranceThreadsHumanBot", "StockThreadsHumanBot",
    "AuraThreadsPublisher", "InsuranceThreadsPublisher", "StockThreadsPublisher",
    "AuraThreadsTextPipeline", "InsuranceThreadsTextPipeline", "StockThreadsTextPipeline",
    "AuraCafePipeline", "InsuranceCafePipeline", "StockCafePipeline",
    "AuraCafeScanner", "InsuranceCafeScanner", "StockCafeScanner",
    "AuraCafeIncubator", "StockCafeIncubator"
]:
    _t_log = logging.getLogger(_name)
    _t_log.addHandler(_dash_handler)
    _t_log.setLevel(logging.INFO)
    _t_log.propagate = False

# 루트 로거에도 등록하여 임의의 미지정 하위 모듈 로그도 100% 직결
logging.getLogger().addHandler(_dash_handler)

def init_verified_live_logs():
    """서버 부팅 시 3대 브랜드 무인 관제 센터 정상 가동 안내만 깔끔하게 출력"""
    log_event("🚀 [System] 대한민국 3대 슈퍼앱 24시간 무인 마케팅 관제 센터 가동 완료 (포트 8080)", "success")
    log_event("🌐 [Live Web] 💖 Aura AI 데이팅: https://aura-ai-dating.vercel.app/", "info")
    log_event("🌐 [Live Web] 🛡️ 보험 리밸런스: https://insure-rebalance.vercel.app/", "info")
    log_event("🌐 [Live Web] 📈 StockMaster AI: https://stockmaster-ai.vercel.app/", "info")
    log_event("⏰ [Schedule] 3대 브랜드 15분 시차 분산 스케줄러가 정상 대기 중입니다.", "success")

init_verified_live_logs()

# 🏭 원클릭 마케팅 콘텐츠 팩토리 서비스 인스턴스
from core.engine.factory_service import FactoryService
factory_service = FactoryService(log_callback=log_event)

# 단일 채널 실물 실행기
def execute_single_channel_task(module_name: str) -> str:
    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    router = ServiceRouter()
    gemini = GeminiEngine(supabase_mgr)
    tts = TTSEngine()
    
    engine_settings = get_media_engine_settings()

    if module_name == "kmarket_shorts":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        target_lang = get_next_golden_eight_language("kmarket_shorts")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        res = factory.produce_shorts(service_id="kmarket", lang=target_lang, engine_mode="gemini")
        return f"🔴 K-Market 8대 황금 타깃 쇼츠 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) 렌더링 완료"
    elif module_name == "easytax_shorts":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        target_lang = get_next_golden_eight_language("easytax_shorts")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        res = factory.produce_shorts(service_id="easytax", lang=target_lang, engine_mode="gemini")
        return f"🔴 EasyTax 8대 황금 타깃 세무 쇼츠 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) 렌더링 완료"
    elif module_name == "kmarket_tiktok":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        target_lang = get_next_golden_eight_language("kmarket_tiktok")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        res = factory.produce_shorts(service_id="kmarket", lang=target_lang, engine_mode="gemini")
        return f"🎵 K-Market 8대 황금 타깃 틱톡 비디오 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) 렌더링 완료"
    elif module_name == "easytax_tiktok":
        factory = ShortsVideoFactory(db_mgr, router, gemini, tts)
        target_lang = get_next_golden_eight_language("easytax_tiktok")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        res = factory.produce_shorts(service_id="easytax", lang=target_lang, engine_mode="gemini")
        return f"🎵 EasyTax 8대 황금 타깃 틱톡 비디오 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) 렌더링 완료"
    elif module_name == "kmarket_cardnews":
        card = CardnewsGenerator(db_mgr, router)
        target_lang = get_next_golden_eight_language("kmarket_cardnews")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        cards = card.generate_carousel(service_id="kmarket", lang=target_lang, engine_mode="gemini")
        return f"📸 K-Market 8대 황금 타깃 카드뉴스 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) {len(cards)}장 생성 완료"
    elif module_name == "easytax_cardnews":
        card = CardnewsGenerator(db_mgr, router)
        target_lang = get_next_golden_eight_language("easytax_cardnews")
        info = GOLDEN_EIGHT_DETAILS.get(target_lang, {})
        flag, native = info.get("flag", "🌐"), info.get("native", target_lang)
        cards = card.generate_carousel(service_id="easytax", lang=target_lang, engine_mode="gemini")
        return f"📸 EasyTax 8대 황금 타깃 카드뉴스 [{flag} {native} ({target_lang})] (🏆 Gemini 3.1 Flash-Lite) {len(cards)}장 생성 완료"
    elif module_name == "kmarket_reddit" or module_name == "reddit":
        import importlib
        import core.gemini_kmarket_reddit
        import core.reddit_browser_driver
        import core.reddit_safety_orchestrator
        import modules.reddit_kmarket
        importlib.reload(core.gemini_kmarket_reddit)
        importlib.reload(core.reddit_browser_driver)
        importlib.reload(core.reddit_safety_orchestrator)
        importlib.reload(modules.reddit_kmarket)
        hunter = modules.reddit_kmarket.KMarketRedditHunter(db_mgr, supabase_mgr)
        res = hunter.run_safe_cycle()
        if res.get("skipped_reason") == "session_expired":
            return "🚨 K-Market 레딧 세션 만료: 브라우저 로그아웃 감지됨 (python login_kmarket_session.py 재로그인 필요)"
        elif res.get("skipped_reason") == "warmup_phase":
            return f"🌱 K-Market 레딧 워밍업 완료: 업보트 {res.get('upvotes')}건, 비홍보 도움답변 {res.get('organic_comments')}건 (카르마 축적 중, 홍보 0건 강제 차단)"
        elif res.get("promo_comments", 0) > 0:
            return f"🎯 K-Market 레딧 안전 사이클 완료: 홍보 {res.get('promo_comments')}건, 비홍보 {res.get('organic_comments')}건, 업보트 {res.get('upvotes')}건"
        else:
            return f"🛡️ K-Market 레딧 안전 사이클 완료: 업보트 {res.get('upvotes')}건, 비홍보 {res.get('organic_comments')}건 (홍보 대기)"
    elif module_name == "easytax_reddit":
        import importlib
        import core.gemini_easytax_reddit
        import core.reddit_browser_driver
        import core.reddit_safety_orchestrator
        import modules.reddit_easytax
        importlib.reload(core.gemini_easytax_reddit)
        importlib.reload(core.reddit_browser_driver)
        importlib.reload(core.reddit_safety_orchestrator)
        importlib.reload(modules.reddit_easytax)
        hunter = modules.reddit_easytax.EasyTaxRedditHunter(db_mgr, supabase_mgr)
        res = hunter.run_safe_cycle()
        if res.get("skipped_reason") == "session_expired":
            return "🚨 EasyTax 레딧 세션 만료: 브라우저 로그아웃 감지됨 (python login_easytax_session.py 재로그인 필요)"
        elif res.get("skipped_reason") == "warmup_phase":
            return f"🌱 EasyTax 레딧 워밍업 완료: 업보트 {res.get('upvotes')}건, 비홍보 도움답변 {res.get('organic_comments')}건 (카르마 축적 중, 홍보 0건 강제 차단)"
        elif res.get("promo_comments", 0) > 0:
            return f"🎯 EasyTax 레딧 안전 사이클 완료: 팩트안내 {res.get('promo_comments')}건, 비홍보 {res.get('organic_comments')}건, 업보트 {res.get('upvotes')}건"
        else:
            return f"🛡️ EasyTax 레딧 안전 사이클 완료: 업보트 {res.get('upvotes')}건, 비홍보 {res.get('organic_comments')}건 (홍보 대기)"
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
        res = publisher.publish_multilingual_articles()
        return f"🌐 K-Market 17개국어 SEO 블로그 칼럼 {res.get('total_langs', 17)}건 생성 & Supabase 업로드 완료"
    elif module_name == "easytax_blog":
        import importlib
        import modules.blog_easytax
        importlib.reload(modules.blog_easytax)
        publisher = modules.blog_easytax.EasyTaxBlogPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_multilingual_articles()
        return f"🌐 EasyTax 공인 세무 SEO 블로그 칼럼 {res.get('total_langs', 15)}건 생성 & Supabase 업로드 완료"
    elif module_name == "kmarket_threads":
        import importlib
        import modules.threads_kmarket
        importlib.reload(modules.threads_kmarket)
        publisher = modules.threads_kmarket.KMarketThreadsPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_threads()
        return f"🧵 K-Market Threads 바이럴 스레드 [{res.get('time_slot', 'slot').upper()}] {res.get('count', 3)}건 배포 완료"
    elif module_name == "easytax_threads":
        import importlib
        import modules.threads_easytax
        importlib.reload(modules.threads_easytax)
        publisher = modules.threads_easytax.EasyTaxThreadsPublisher(db_mgr, supabase_mgr)
        res = publisher.publish_daily_threads()
        return f"🧵 EasyTax Threads 세무 스레드 [{res.get('time_slot', 'slot').upper()}] {res.get('count', 3)}건 배포 완료"
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

    # 💖 [Aura 데이팅 전용 채널 실행기]
    elif module_name.startswith("aura_"):
        if module_name in ["aura_omni_blog", "aura_blog", "aura_magazine", "aura_naver_blog", "aura_tistory", "aura_brunch"]:
            from brands.aura.aura_blog_scheduler import AuraBlogScheduler
            res = AuraBlogScheduler().run_one_cycle()
            ch = res.get('publish_results', {}).get('channels', {})
            naver_url = ch.get('naver_blog', {}).get('url', '-')
            tistory_url = ch.get('tistory', {}).get('post_url', ch.get('tistory', {}).get('url', '-'))
            feed_status = ch.get('aura_app', {}).get('status', 'OK')
            brunch_status = ch.get('brunch', {}).get('status', '-')
            return f"💖 [Aura 4대 옴니 배포 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 앱피드: {feed_status}\n  - 🟢 네이버: {naver_url}\n  - 🟠 티스토리: {tistory_url}\n  - 🟡 브런치: {brunch_status}"
        elif module_name in ["aura_shorts", "aura_naver_clip", "aura_omni_shorts"]:
            from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
            pilot = AuraOmniShortsPilot()
            log_event("🚀 [Aura] 쏘기 직전 숏폼 1편 단독 제작 및 4대 채널(유튜브+클립+릴스) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot()
            if res.get("status") == "skipped":
                return f"🛑 [Aura 숏폼] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            yt_url = ch.get("youtube", {}).get("video_url", "-")
            clip_status = ch.get("naver_clip", {}).get("status", "-")
            return f"🎉 [Aura 숏폼 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 🔴 유튜브: {yt_url}\n  - 🟢 네이버 클립: {clip_status}\n  - 📁 파일: {res.get('video_file')}"
        elif module_name == "aura_master_photo":
            from brands.aura.aura_shorts_pipeline import AuraShortsPipeline
            pipeline = AuraShortsPipeline()
            log_event("🎨 [Aura 대시보드] Wan 2.1 T2I 실사 인물 사진 단독 생성 시작...", "info")
            res_photo = pipeline.produce_master_photo()
            return f"📸 [Aura 실사 인물 마스터 사진 생성 완료]\n  • 파일 저장: {res_photo.get('photo_path')}"
        elif module_name in ["aura_cardnews", "aura_omni_cardnews"]:
            from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
            pilot = AuraOmniCardnewsPilot()
            log_event("🎨 [Aura] 쏘기 직전 5장 카드뉴스 단독 제작 및 Meta(페북+인스타) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot(force=True)
            if res.get("status") == "skipped":
                return f"🛑 [Aura 카드뉴스] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            fb_res = ch.get("facebook_cardnews", {}).get("status", "-")
            ig_res = ch.get("instagram_carousel", {}).get("status", "-")
            return f"🎉 [Aura 5장 카드뉴스 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 📘 페이스북 앨범: {fb_res}\n  - 📸 인스타그램 캐러셀: {ig_res}\n  - 📁 슬라이드: {res.get('slides_count')}장"
        elif module_name in ["aura_threads", "aura_omni_threads"]:
            import asyncio
            from brands.aura.aura_threads_text_pipeline import AuraThreadsTextPipeline
            log_event("🧵 [Aura 스레드] Gemini 순수 텍스트 1회 자율 집필 및 라이브 송출 가동...", "info")
            res = asyncio.run(AuraThreadsTextPipeline(headless=True).execute_slot(slot="morning", dry_run=False))
            if res.get("success"):
                clear_channel_error("aura_threads")
                pub = res.get("publish_result", {})
                log_event(f"🎉 [Aura 스레드 발행 성공] 본문 + 1번 타래글(공식 검색어 '아우라AI데이팅' & 랜딩 URL) 체인 완료", "success")
                return f"💖 [Aura 스레드 텍스트 발행 완료]\n  • 결과: 성공 (사진 0장 + 공식 검색어 & 첫댓글 링크 체인)\n  • 증빙 캡처: {pub.get('screenshot_path', '-')}"
            err_msg = res.get("publish_result", {}).get("message") or res.get("error", "스레드 세션 접속 또는 버튼 탐색 실패")
            record_channel_error("aura_threads", err_msg)
            log_event(f"❌ [Aura 스레드 송출 실패] {err_msg}", "error")
            return f"💖 [Aura 스레드 실패] {err_msg}"
        elif module_name in ["aura_nate_pann", "aura_dcinside", "aura_ppomppu"]:
            from brands.aura.aura_pipeline import AuraPipeline
            res = AuraPipeline(dry_run=False).run_viral_community_cycle()
            return f"💖 [Aura 커뮤니티 바이럴] 네이트판 사연 & 디시 연애갤 투고 완료"
        elif module_name == "aura_naver_kin":
            from brands.aura.aura_kin_pipeline import AuraKinPipeline
            res = AuraKinPipeline().run_catch_cycle(max_catch=1)
            if res.get("success"):
                rec = res.get("record", {})
                return f"💖 [Aura 지식iN 낚아채기 완료] '{rec.get('title', '')}' (적합도 {rec.get('score')}점)"
            else:
                return f"💖 [Aura 지식iN] {res.get('message', '대기 중')}"
        elif module_name in ["aura_seo", "aura_search_advisor", "aura_omni_seo", "aura_google_ping"]:
            from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
            res = AuraSearchIndexingHub().ping_all_engines()
            return res.get("message", "🌐 Aura 2대 포털 검색엔진 동시 색인 핑 전송 완료")
        elif module_name in ["aura_reddit", "aura_reddit_cycle", "aura_reddit_promo"]:
            from brands.aura.aura_reddit_engine import AuraRedditEngine
            log_event("🔍 [Aura 레딧] 12대 글로벌 서브레딧 실시간 스캔 & 파이썬 심사 시작...", "info")
            engine = AuraRedditEngine()
            if module_name == "aura_reddit_cycle":
                cycle_res = engine.run_safe_cycle()
                log_event(f"💖 [Aura 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 체류 피드 탐색, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건", "success")
                return f"💖 [Aura 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건"
            else:
                log_event("🚀 [Aura 레딧] 12대 서브레딧 스캔 및 실시간 스텔스 댓글 게시 가동...", "info")
                processed = engine.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=True)
                clear_channel_error("aura_reddit")
                if processed > 0:
                    log_event("🎉 [Aura 레딧 스텔스 마케팅 성공] 실시간 타겟 글에 '아우라AI데이팅' 검색 유도 댓글 등록 완료!", "success")
                    return f"💖 [Aura 레딧 스텔스 마케팅 1회 완료] 댓글 {processed}건 게시 성공 (검색어: '아우라AI데이팅' 포함)"
                else:
                    log_event("ℹ️ [Aura 레딧] 조건 부합 신규 글 부재 또는 안전 한도/세션 대기 중", "info")
                    return "💖 [Aura 레딧 스캔 완료] 조건 부합 글 부재 또는 안전 대기"
        elif module_name in ["aura_human_bot", "aura_instagram_stealth", "aura_meta_stealth"]:
            from brands.aura.aura_human_behavior_bot import AuraHumanBehaviorBot
            log_event("🤖 [Aura 인스타 스텔스] 사람처럼 탐색 탭 체류 및 좋아요 가동...", "info")
            bot = AuraHumanBehaviorBot(headless=True)
            res = bot.execute_single_session()
            log_event(f"🎉 [Aura 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"💖 [Aura 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["aura_youtube_bot", "aura_youtube_stealth"]:
            from brands.aura.aura_youtube_behavior_bot import AuraYouTubeBehaviorScheduler
            log_event("🎬 [Aura 유튜브 스텔스] 사람처럼 쇼츠 완시청 및 좋아요 가동...", "info")
            res = AuraYouTubeBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [Aura 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편 완시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"💖 [Aura 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["aura_tiktok_bot", "aura_tiktok_stealth"]:
            from brands.aura.aura_tiktok_behavior_bot import AuraTikTokBehaviorScheduler
            log_event("🎵 [Aura 틱톡 스텔스] 사람처럼 FYP 피드 탐색 및 댓글창 열람 가동...", "info")
            res = AuraTikTokBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [Aura 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개 시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"💖 [Aura 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["aura_threads_bot", "aura_threads_stealth"]:
            from brands.aura.aura_threads_human_bot import AuraThreadsHumanBot
            log_event("🧵 [Aura 스레드 스텔스] 사람처럼 타임라인 정독 및 하트 탐색 가동...", "info")
            res = AuraThreadsHumanBot(headless=True).execute_single_session()
            log_event(f"🎉 [Aura 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"💖 [Aura 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["aura_naver_cafe", "aura_daum_cafe"]:
            import asyncio
            from brands.aura.aura_cafe_pipeline import AuraCafePipeline
            pipe = AuraCafePipeline()
            res = asyncio.run(pipe.run_daily_stealth_infiltration(dry_run=False))
            return f"☕ [Aura 카페 스텔스] {res.get('message', '카페 스텔스 침투 완료')}"
        else:
            from brands.aura.aura_pipeline import AuraPipeline
            res = AuraPipeline(dry_run=False).run_full_daily_cycle()
            return f"💖 [Aura #{module_name}] 자율 파이프라인 가동 완료"

    # 🛡️ [InsureBalance 보험비교 전용 채널 실행기]
    elif module_name.startswith("insurance_"):
        from brands.insurance.insurance_pipeline import InsurancePipeline
        pipe = InsurancePipeline(dry_run=False)
        if module_name in ["insurance_omni_blog", "insurance_blog", "insurance_naver_blog", "insurance_tistory", "insurance_brunch"]:
            from brands.insurance.insurance_blog_scheduler import InsuranceBlogScheduler
            res = InsuranceBlogScheduler().run_one_cycle()
            ch = res.get('publish_results', {}).get('channels', {})
            naver_url = ch.get('naver_blog', {}).get('url', '-')
            tistory_url = ch.get('tistory', {}).get('post_url', ch.get('tistory', {}).get('url', '-'))
            feed_status = ch.get('insurance_app', {}).get('status', 'OK')
            brunch_status = ch.get('brunch', {}).get('status', '-')
            return f"🛡️ [보험비교 3대 옴니 배포 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 🟢 네이버: {naver_url}\n  - 🟠 티스토리: {tistory_url}\n  - 🟡 브런치: {brunch_status}"
        elif module_name in ["insurance_ppomppu", "insurance_bobaedream", "insurance_dcinside"]:
            res = pipe.run_community_cycle()
            return f"🛡️ [보험비교] 뽐뿌 재테크 & 보배드림 운전자보험 정보글 투고 완료"
        elif module_name == "insurance_naver_kin":
            from brands.insurance.insurance_kin_pipeline import InsuranceKinPipeline
            res = InsuranceKinPipeline().run_catch_cycle(max_catch=1)
            if res.get("success"):
                rec = res.get("record", {})
                return f"🛡️ [보험비교 지식iN 낚아채기 완료] '{rec.get('title', '')}' (적합도 {rec.get('score')}점)"
            else:
                return f"🛡️ [보험비교 지식iN] {res.get('message', '대기 중')}"
        elif module_name in ["insurance_shorts", "insurance_naver_clip", "insurance_omni_shorts"]:
            from brands.insurance.insurance_omni_shorts_pilot import InsuranceOmniShortsPilot
            pilot = InsuranceOmniShortsPilot()
            log_event("🚀 [보험비교] 쏘기 직전 숏폼 1편 단독 제작 및 4대 채널(유튜브+클립+릴스) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot()
            if res.get("status") == "skipped":
                return f"🛡️ [보험 숏폼] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            yt_url = ch.get("youtube", {}).get("video_url", "-")
            clip_status = ch.get("naver_clip", {}).get("status", "-")
            return f"🎉 [보험 숏폼 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 🔴 유튜브: {yt_url}\n  - 🟢 네이버 클립: {clip_status}\n  - 📁 파일: {res.get('video_file')}"
        elif module_name == "insurance_master_photo":
            from brands.insurance.insurance_shorts_pipeline import InsuranceShortsPipeline
            pipeline = InsuranceShortsPipeline()
            log_event("🎨 [보험비교 대시보드] Wan 2.1 T2I 실사 인물 사진 단독 생성 시작...", "info")
            res_photo = pipeline.produce_master_photo()
            return f"📸 [보험비교 실사 인물 마스터 사진 생성 완료]\n  • 파일 저장: {res_photo.get('photo_path')}"
        elif module_name in ["insurance_cardnews", "insurance_omni_cardnews"]:
            from brands.insurance.insurance_omni_cardnews_pilot import InsuranceOmniCardnewsPilot
            pilot = InsuranceOmniCardnewsPilot()
            log_event("🎨 [보험비교] 쏘기 직전 5장 카드뉴스 단독 제작 및 Meta(페북+인스타) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot()
            if res.get("status") == "skipped":
                return f"🛡️ [보험 카드뉴스] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            fb_res = ch.get("facebook_cardnews", {}).get("status", "-")
            ig_res = ch.get("instagram_carousel", {}).get("status", "-")
            return f"🎉 [보험 5장 카드뉴스 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 📘 페이스북 앨범: {fb_res}\n  - 📸 인스타그램 캐러셀: {ig_res}\n  - 📁 슬라이드: {res.get('slides_count')}장"
        elif module_name in ["insurance_threads", "insurance_omni_threads"]:
            import asyncio
            from brands.insurance.insurance_threads_text_pipeline import InsuranceThreadsTextPipeline
            log_event("🧵 [보험비교 스레드] Gemini 순수 텍스트 1회 자율 집필 및 라이브 송출 가동...", "info")
            res = asyncio.run(InsuranceThreadsTextPipeline(headless=True).execute_slot(slot="morning", dry_run=False))
            if res.get("success"):
                clear_channel_error("insurance_threads")
                pub = res.get("publish_result", {})
                log_event(f"🎉 [보험비교 스레드 발행 성공] 본문 + 1번 타래글(공식 검색어 '보험 리밸런스' & 랜딩 URL) 체인 완료", "success")
                return f"🛡️ [보험비교 스레드 텍스트 발행 완료]\n  • 결과: 성공 (사진 0장 + 공식 검색어 & 첫댓글 링크 체인)\n  • 증빙 캡처: {pub.get('screenshot_path', '-')}"
            err_msg = res.get("publish_result", {}).get("message") or res.get("error", "스레드 세션 접속 실패")
            record_channel_error("insurance_threads", err_msg)
            log_event(f"❌ [보험비교 스레드 송출 실패] {err_msg}", "error")
            return f"🛡️ [보험비교 스레드 실패] {err_msg}"
        elif module_name in ["insurance_seo", "insurance_search_advisor", "insurance_omni_seo", "insurance_google_ping"]:
            from brands.insurance.insurance_search_indexing_hub import InsuranceSearchIndexingHub
            res = InsuranceSearchIndexingHub().ping_all_engines()
            return res.get("message", "🌐 보험비교 2대 포털 검색엔진 동시 색인 핑 전송 완료")
        elif module_name in ["insurance_reddit", "insurance_reddit_cycle", "insurance_reddit_promo"]:
            from brands.insurance.insurance_reddit_engine import InsuranceRedditEngine
            log_event("🔍 [보험비교 레딧] 10대 글로벌 서브레딧 실시간 스캔 & 파이썬 심사 시작...", "info")
            engine = InsuranceRedditEngine()
            if module_name == "insurance_reddit_cycle":
                cycle_res = engine.run_safe_cycle()
                log_event(f"🛡️ [보험 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 체류 피드 탐색, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건", "success")
                return f"🛡️ [보험 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건"
            else:
                log_event("🚀 [보험비교 레딧] 10대 서브레딧 스캔 및 실시간 스텔스 댓글 게시 가동...", "info")
                processed = engine.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=True)
                clear_channel_error("insurance_reddit")
                if processed > 0:
                    log_event("🎉 [보험 레딧 스텔스 마케팅 성공] 실시간 타겟 글에 '보험 리밸런스' 검색 유도 댓글 등록 완료!", "success")
                    return f"🛡️ [보험 레딧 스텔스 마케팅 1회 완료] 댓글 {processed}건 게시 성공 (검색어: '보험 리밸런스' 포함)"
                else:
                    log_event("ℹ️ [보험 레딧] 조건 부합 신규 글 부재 또는 안전 한도/세션 대기 중", "info")
                    return "🛡️ [보험 레딧 스캔 완료] 조건 부합 글 부재 또는 안전 대기"
        elif module_name in ["insurance_human_bot", "insurance_instagram_stealth", "insurance_meta_stealth"]:
            from brands.insurance.insurance_human_behavior_bot import InsuranceHumanBehaviorBot
            log_event("🤖 [보험 인스타 스텔스] 사람처럼 탐색 탭 체류 및 좋아요 가동...", "info")
            bot = InsuranceHumanBehaviorBot(headless=True)
            res = bot.execute_single_session()
            log_event(f"🎉 [보험 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"🛡️ [보험 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["insurance_youtube_bot", "insurance_youtube_stealth"]:
            from brands.insurance.insurance_youtube_behavior_bot import InsuranceYouTubeBehaviorScheduler
            log_event("🎬 [보험 유튜브 스텔스] 사람처럼 쇼츠 완시청 및 좋아요 가동...", "info")
            res = InsuranceYouTubeBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [보험 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편 완시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"🛡️ [보험 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["insurance_tiktok_bot", "insurance_tiktok_stealth"]:
            from brands.insurance.insurance_tiktok_behavior_bot import InsuranceTikTokBehaviorScheduler
            log_event("🎵 [보험 틱톡 스텔스] 사람처럼 FYP 피드 탐색 및 댓글창 열람 가동...", "info")
            res = InsuranceTikTokBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [보험 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개 시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"🛡️ [보험 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["insurance_threads_bot", "insurance_threads_stealth"]:
            from brands.insurance.insurance_threads_human_bot import InsuranceThreadsHumanBot
            log_event("🧵 [보험 스레드 스텔스] 사람처럼 타임라인 정독 및 하트 탐색 가동...", "info")
            res = InsuranceThreadsHumanBot(headless=True).execute_single_session()
            log_event(f"🎉 [보험 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"🛡️ [보험 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["insurance_naver_cafe", "insurance_daum_cafe", "insurance_cafe"]:
            import asyncio
            from brands.insurance.insurance_cafe_pipeline import InsuranceCafePipeline
            pipe = InsuranceCafePipeline()
            res = asyncio.run(pipe.run_daily_stealth_infiltration(dry_run=False))
            return f"☕ [보험비교 카페 스텔스] {res.get('message', '카페 스텔스 침투 완료')}"
        else:
            res = pipe.run_full_daily_cycle()
            return f"🛡️ [보험비교 #{module_name}] 자율 파이프라인 가동 완료"

    # 📈 [Stock Master 주식 AI 전용 채널 실행기]
    elif module_name.startswith("stock_"):
        from brands.stock.stock_pipeline import StockPipeline
        pipe = StockPipeline(dry_run=False)
        if module_name in ["stock_omni_blog", "stock_blog", "stock_naver_blog", "stock_tistory", "stock_brunch"]:
            from brands.stock.stock_blog_scheduler import StockBlogScheduler
            res = StockBlogScheduler().run_one_cycle()
            ch = res.get('publish_results', {}).get('channels', {})
            naver_url = ch.get('naver_blog', {}).get('url', '-')
            tistory_url = ch.get('tistory', {}).get('post_url', ch.get('tistory', {}).get('url', '-'))
            feed_status = ch.get('stock_app', {}).get('status', 'OK')
            brunch_status = ch.get('brunch', {}).get('status', '-')
            return f"📈 [주식AI 3대 옴니 배포 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 🟢 네이버: {naver_url}\n  - 🟠 티스토리: {tistory_url}\n  - 🟡 브런치: {brunch_status}"
        elif module_name in ["stock_dcinside", "stock_ppomppu"]:
            res = pipe.run_community_cycle()
            return f"📈 [주식AI] 디시 주식갤 & 뽐뿌 증권 시황 브리핑 투고 완료"
        elif module_name in ["stock_briefing", "stock_kakao_channel"]:
            res = pipe.run_premarket_briefing_cycle()
            return f"📈 [주식AI] 장전 08:30 핵심 섹터 알림톡 브리핑 발송 완료"
        elif module_name == "stock_naver_kin":
            from brands.stock.stock_kin_pipeline import StockKinPipeline
            res = StockKinPipeline().run_catch_cycle(max_catch=1)
            if res.get("success"):
                rec = res.get("record", {})
                return f"📈 [주식AI 지식iN 낚아채기 완료] '{rec.get('title', '')}' (적합도 {rec.get('score')}점)"
            else:
                return f"📈 [주식AI 지식iN] {res.get('message', '대기 중')}"
        elif module_name in ["stock_shorts", "stock_naver_clip", "stock_omni_shorts"]:
            from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
            pilot = StockOmniShortsPilot()
            log_event("🚀 [주식AI] 쏘기 직전 숏폼 1편 단독 제작 및 4대 채널(유튜브+클립+릴스) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot()
            if res.get("status") == "skipped":
                return f"📈 [주식 숏폼] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            yt_url = ch.get("youtube", {}).get("video_url", "-")
            clip_status = ch.get("naver_clip", {}).get("status", "-")
            return f"🎉 [주식 숏폼 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 🔴 유튜브: {yt_url}\n  - 🟢 네이버 클립: {clip_status}\n  - 📁 파일: {res.get('video_file')}"
        elif module_name in ["stock_cardnews", "stock_omni_cardnews"]:
            from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
            pilot = StockOmniCardnewsPilot()
            log_event("🎨 [주식AI] 쏘기 직전 5장 카드뉴스 단독 제작 및 Meta(페북+인스타) 1회 단발 송출 가동...", "info")
            res = pilot.execute_single_slot()
            if res.get("status") == "skipped":
                return f"📈 [주식 카드뉴스] {res.get('message', '오늘 송출 완료')}"
            ch = res.get("channels", {})
            fb_res = ch.get("facebook_cardnews", {}).get("status", "-")
            ig_res = ch.get("instagram_carousel", {}).get("status", "-")
            return f"🎉 [주식 5장 카드뉴스 1회 단발 송출 완료] 주제 #{res.get('topic_id')} '{res.get('title')}'\n  - 📘 페이스북 앨범: {fb_res}\n  - 📸 인스타그램 캐러셀: {ig_res}\n  - 📁 슬라이드: {res.get('slides_count')}장"
        elif module_name in ["stock_threads", "stock_omni_threads"]:
            import asyncio
            from brands.stock.stock_threads_text_pipeline import StockThreadsTextPipeline
            log_event("🧵 [주식AI 스레드] Gemini 순수 텍스트 1회 자율 집필 및 라이브 송출 가동...", "info")
            res = asyncio.run(StockThreadsTextPipeline(headless=True).execute_slot(slot="morning", dry_run=False))
            if res.get("success"):
                clear_channel_error("stock_threads")
                pub = res.get("publish_result", {})
                log_event(f"🎉 [주식AI 스레드 발행 성공] 본문 + 1번 타래글(공식 검색어 '스톡마스터 AI' & 랜딩 URL) 체인 완료", "success")
                return f"📈 [주식AI 스레드 텍스트 발행 완료]\n  • 결과: 성공 (사진 0장 + 공식 검색어 & 첫댓글 링크 체인)\n  • 증빙 캡처: {pub.get('screenshot_path', '-')}"
            err_msg = res.get("publish_result", {}).get("message") or res.get("error", "스레드 세션 접속 실패")
            record_channel_error("stock_threads", err_msg)
            log_event(f"❌ [주식AI 스레드 송출 실패] {err_msg}", "error")
            return f"📈 [주식AI 스레드 실패] {err_msg}"
        elif module_name in ["stock_seo", "stock_search_advisor", "stock_omni_seo", "stock_google_ping"]:
            from brands.stock.stock_search_indexing_hub import StockSearchIndexingHub
            res = StockSearchIndexingHub().ping_all_engines()
            return res.get("message", "🌐 주식AI 2대 포털 검색엔진 동시 색인 핑 전송 완료")
        elif module_name in ["stock_reddit", "stock_reddit_cycle", "stock_reddit_promo"]:
            from brands.stock.stock_reddit_engine import StockRedditEngine
            log_event("🔍 [주식AI 레딧] 10대 글로벌 서브레딧 실시간 스캔 & 파이썬 심사 시작...", "info")
            engine = StockRedditEngine()
            if module_name == "stock_reddit_cycle":
                cycle_res = engine.run_safe_cycle()
                log_event(f"📈 [주식 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 체류 피드 탐색, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건", "success")
                return f"📈 [주식AI 레딧 안전 사이클 완료] 업보트 {cycle_res.get('upvotes', 0)}건, 비홍보 {cycle_res.get('organic_comments', 0)}건, 스텔스홍보 {cycle_res.get('promo_comments', 0)}건"
            else:
                log_event("🚀 [주식AI 레딧] 10대 서브레딧 스캔 및 실시간 스텔스 댓글 게시 가동...", "info")
                processed = engine.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=True)
                clear_channel_error("stock_reddit")
                if processed > 0:
                    log_event("🎉 [주식 레딧 스텔스 마케팅 성공] 실시간 타겟 글에 '스톡마스터 AI' 검색 유도 댓글 등록 완료!", "success")
                    return f"📈 [주식AI 레딧 스텔스 마케팅 1회 완료] 댓글 {processed}건 게시 성공 (검색어: '스톡마스터 AI' 포함)"
                else:
                    log_event("ℹ️ [주식AI 레딧] 조건 부합 신규 글 부재 또는 안전 한도/세션 대기 중", "info")
                    return "📈 [주식AI 레딧 스캔 완료] 조건 부합 글 부재 또는 안전 대기"
        elif module_name in ["stock_human_bot", "stock_instagram_stealth", "stock_meta_stealth"]:
            from brands.stock.stock_human_behavior_bot import StockHumanBehaviorBot
            log_event("🤖 [주식 인스타 스텔스] 사람처럼 탐색 탭 체류 및 좋아요 가동...", "info")
            bot = StockHumanBehaviorBot(headless=True)
            res = bot.execute_single_session()
            log_event(f"🎉 [주식 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"📈 [주식 인스타 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 피드 {res.get('posts_viewed', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["stock_youtube_bot", "stock_youtube_stealth"]:
            from brands.stock.stock_youtube_behavior_bot import StockYouTubeBehaviorScheduler
            log_event("🎬 [주식 유튜브 스텔스] 사람처럼 쇼츠 완시청 및 좋아요 가동...", "info")
            res = StockYouTubeBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [주식 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편 완시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"📈 [주식 유튜브 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 쇼츠 {res.get('shorts_watched', 0)}편, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["stock_tiktok_bot", "stock_tiktok_stealth"]:
            from brands.stock.stock_tiktok_behavior_bot import StockTikTokBehaviorScheduler
            log_event("🎵 [주식 틱톡 스텔스] 사람처럼 FYP 피드 탐색 및 댓글창 열람 가동...", "info")
            res = StockTikTokBehaviorScheduler().execute_single_session()
            log_event(f"🎉 [주식 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개 시청, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"📈 [주식 틱톡 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, FYP 영상 {res.get('videos_watched', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["stock_threads_bot", "stock_threads_stealth"]:
            from brands.stock.stock_threads_human_bot import StockThreadsHumanBot
            log_event("🧵 [주식 스레드 스텔스] 사람처럼 타임라인 정독 및 하트 탐색 가동...", "info")
            res = StockThreadsHumanBot(headless=True).execute_single_session()
            log_event(f"🎉 [주식 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개 정독, 좋아요 {res.get('likes_given', 0)}회 성공", "success")
            return f"📈 [주식 스레드 스텔스 완료] 체류 {res.get('duration_sec', 0)}초, 글 {res.get('posts_read', 0)}개, 좋아요 {res.get('likes_given', 0)}회"
        elif module_name in ["stock_naver_cafe", "stock_daum_cafe", "stock_cafe"]:
            import asyncio
            from brands.stock.stock_cafe_pipeline import StockCafePipeline
            pipe = StockCafePipeline()
            res = asyncio.run(pipe.run_daily_stealth_infiltration(dry_run=False))
            return f"☕ [주식AI 카페 스텔스] {res.get('message', '카페 스텔스 침투 완료')}"
        else:
            res = pipe.run_full_daily_cycle()
            return f"📈 [주식AI #{module_name}] 자율 파이프라인 가동 완료"

    else:
        return f"{module_name} 실행 완료"


# 🛡️ [24시간 무인가동 상태 영구 보존 및 자동 복구 시스템]
def restore_unmanned_state():
    """서버 부팅 시 이전에 가동 중이던 모든 무인 자율주행 상태를 100% 자동 복구 및 즉시 재가동"""
    state = UnmannedStateManager.load_state()
    saved_channels = state.get("running_channels", {})
    saved_kmarket = state.get("kmarket_running", False)
    saved_easytax = state.get("easytax_running", False)
    saved_daemons = state.get("golden_batch_daemon_running", {})
    saved_telegram = state.get("telegram_manager_running", {})

    restored_count = 0

    # 1. K-Market 전체 봇 복구
    global kmarket_thread, kmarket_running
    if saved_kmarket:
        kmarket_running = True
        kmarket_thread = threading.Thread(target=kmarket_worker, daemon=True)
        kmarket_thread.start()
        restored_count += 1
        log_event("🔄 [무인 복구] K-Market 종합 무인봇 자동 재가동 완료", "info")

    # 2. EasyTax 전체 봇 복구
    global easytax_thread, easytax_running
    if saved_easytax:
        easytax_running = True
        easytax_thread = threading.Thread(target=easytax_worker, daemon=True)
        easytax_thread.start()
        restored_count += 1
        log_event("🔄 [무인 복구] EasyTax 종합 무인봇 자동 재가동 완료", "info")

    # 3. 개별 20대 무인 채널 자율 공장 루프 복구
    global running_channels
    for ch, is_active in saved_channels.items():
        if is_active and ch in running_channels:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()
                restored_count += 1

    # 4. 8대 황금 타깃 무인 예약 데몬 복구
    global golden_batch_daemon_running
    for brand, is_active in saved_daemons.items():
        if is_active and brand in golden_batch_daemon_running:
            if not golden_batch_daemon_running.get(brand, False):
                golden_batch_daemon_running[brand] = True
                threading.Thread(target=_golden_daemon_loop, args=(brand,), daemon=True).start()
                restored_count += 1

    # 5. 텔레그램 AI 커뮤니티 매니저 복구
    for brand, is_active in saved_telegram.items():
        if is_active and brand in telegram_ai_managers:
            mgr = telegram_ai_managers[brand]
            if not mgr.is_running:
                mgr.start_background_daemon()
                restored_count += 1

    if restored_count > 0:
        log_event(f"🛡️ [무인가동 불멸 모드] 서버 재시작 감지 — 이전 가동 중이던 {restored_count}개 무인 프로세스를 100% 자동 재개했습니다!", "success")
        print(f"\n========================================================")
        print(f"🛡️ [무인가동 불멸 모드] 이전 무인 가동 상태 {restored_count}개 100% 자동 복구 완료!")
        print(f"========================================================\n")

# 24시간 연속 무인 자율 공장 루프
def channel_continuous_worker(module_name: str):
    global running_channels

    # ⏰ #1 Aura 2030 매거진: 대한민국 표준시(KST) 하루 2회 (12:00 / 21:00) 정시 스케줄러
    if module_name in ["aura_blog", "aura_magazine"]:
        scheduler = ChannelScheduler(
            channel_name="💖 Aura 2030 매거진",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["12:00", "21:00"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #2 숏폼 / 틱톡 / 릴스 / 클립: 대한민국 표준시(KST) 하루 3회 (12:00 / 20:30 / 23:30) 정시 스케줄러
    if any(k in module_name for k in ["shorts", "tiktok", "naver_clip"]):
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 숏폼/릴스",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["12:00", "20:30", "23:30"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #3 실물 카드뉴스: 대한민국 표준시(KST) 하루 3회 (08:00 / 15:30 / 22:30) 정시 스케줄러
    if "cardnews" in module_name:
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 카드뉴스",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["08:00", "15:30", "22:30"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #4 블로그 / 외부 포털 채널: 대한민국 표준시(KST) 하루 3회 (09:00 / 13:00 / 19:00)
    if any(k in module_name for k in ["blog", "naver_blog", "tistory", "brunch", "naver_post"]):
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 블로그/칼럼",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["09:00", "13:00", "19:00"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #5-1 [💖 Aura 네이버 지식iN 100대 황금키워드 4대 슬롯 30분 정밀 레이더]
    if module_name == "aura_naver_kin":
        scheduler = ChannelScheduler(
            channel_name="💖 Aura 지식iN 100대 키워드 레이더",
            publish_fn=lambda: execute_single_channel_task("aura_naver_kin"),
            interval_seconds=1800
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #5 커뮤니티 바이럴 / 리드 헌터: 1시간 간격 정기 자율 헌팅
    if any(k in module_name for k in ["reddit", "ppomppu", "dcinside", "nate_pann", "bobaedream", "fmkorea", "naver_cafe", "daum_cafe", "naver_kin"]):
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 커뮤니티 헌터",
            publish_fn=lambda: execute_single_channel_task(module_name),
            interval_seconds=3600
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #6 구글 / 네이버 검색 색인 핑: 대한민국 표준시(KST) 하루 1회 (새벽 01:00)
    if any(k in module_name for k in ["seo", "search_advisor"]):
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 검색 색인 핑",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["01:00"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #7 페이스북 50만 그룹 침투기: 대한민국 표준시(KST) 하루 3회 (09:30 / 13:30 / 19:30)
    if "fb_groups" in module_name:
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 페북 침투기",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["09:30", "13:30", "19:30"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #8 Meta Threads 바이럴 스레드: 대한민국 표준시(KST) 하루 3회 (11:00 / 16:30 / 21:30)
    if "threads" in module_name:
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 스레드",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["11:00", "16:30", "21:30"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #9 텔레그램 / 카카오 알림톡 브리핑: 대한민국 표준시(KST) 하루 2회 (08:30 / 18:30)
    if any(k in module_name for k in ["briefing", "kakao_channel"]):
        brand_name = "💖 Aura" if "aura" in module_name else ("🛡️ 보험비교" if "insurance" in module_name else ("📈 주식AI" if "stock" in module_name else ("💰 EasyTax" if "easytax" in module_name else "🛒 K-Market")))
        scheduler = ChannelScheduler(
            channel_name=f"{brand_name} 브리핑/알림톡",
            publish_fn=lambda: execute_single_channel_task(module_name),
            time_slots=["08:30", "18:30"]
        )
        scheduler.run_scheduled_loop(
            is_running_checker=lambda: running_channels.get(module_name, False),
            on_log=log_event
        )
        return

    # ⏰ #10 기타 채널 기본 무인 자율 공장 루프
    log_event(f"🚀 [{module_name}] 24시간 연속 무인 자율 공장이 가동되었습니다.", "success")
    
    cycle = 0
    while running_channels.get(module_name, False):
        cycle += 1
        try:
            msg = execute_single_channel_task(module_name)
            clear_channel_error(module_name)
            log_event(f"⚡ [{module_name} #{cycle}] {msg}", "success")
        except Exception as e:
            import traceback
            err_detail = traceback.format_exc()
            record_channel_error(module_name, str(e))
            log_event(f"❌ [{module_name} 예외 발생] {e}\n{err_detail}", "error")
        
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

    def _serve_file(self, file_path: Path, content_type: str = "text/html; charset=utf-8"):
        if not file_path.exists():
            self._set_headers("text/plain", 404)
            self.wfile.write(b"404 Not Found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(content_type, 200)
            self.wfile.write(content)
        except Exception as e:
            self._set_headers("text/plain", 500)
            self.wfile.write(f"500 Internal Error: {e}".encode("utf-8"))

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
        elif path == "/aura_frame.html" or path == "/aura_frame":
            self._serve_file(BASE_DIR / "web" / "aura_frame.html", "text/html; charset=utf-8")
            return
        elif path == "/aura_video_chat.html" or path == "/aura_video_chat":
            self._serve_file(BASE_DIR / "web" / "aura_video_chat.html", "text/html; charset=utf-8")
            return
        elif path in ["/nanami_portrait.jpg", "/sample_avatar_male.jpg"]:
            self._serve_file(BASE_DIR / "web" / path.lstrip("/"), "image/jpeg")
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

        elif path.startswith("/desktop_media/"):
            rel_path = urllib.parse.unquote(path[len("/desktop_media/"):])
            user_desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop"
            file_path = user_desktop / rel_path
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                ext = file_path.suffix.lower()
                mime_type = "image/png" if ext == ".png" else "video/mp4" if ext == ".mp4" else "text/plain"
            self._serve_file(file_path, mime_type)
            return

        elif path == "/api/media_engine":
            self._handle_get_media_engine()
            return
        elif path == "/api/status":
            self._handle_get_status()
            return
        elif path == "/api/today-live-feed" or path.startswith("/api/today-live-feed/"):
            brand_part = path.replace("/api/today-live-feed", "").strip("/")
            self._handle_get_today_live_feed(brand=brand_part if brand_part else None)
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
        elif path == "/api/telegram/stats" or path.startswith("/api/telegram/stats"):
            self._handle_get_telegram_stats(parsed)
            return
        elif path == "/api/golden-targets":
            self._handle_get_golden_targets()
            return
        elif path == "/api/golden-batch/status":
            self._handle_get_golden_batch_status()
            return
        elif path.startswith("/api/kin/"):
            # /api/kin/aura/history, /api/kin/stock/history, /api/kin/insurance/history
            parts = path.strip("/").split("/")
            b = parts[2] if len(parts) >= 3 else "aura"
            self._handle_get_kin_history(b)
            return
        elif path.startswith("/api/cafe/"):
            # /api/cafe/aura/history, /api/cafe/stock/history, /api/cafe/insurance/history
            parts = path.strip("/").split("/")
            b = parts[2] if len(parts) >= 3 else "aura"
            self._handle_get_cafe_history(b)
            return
        elif path == "/api/stock/shorts/status" or path.startswith("/api/stock/shorts/status"):
            self._handle_get_stock_shorts_status()
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
        if path == "/api/media_engine":
            self._handle_post_media_engine(payload)
            return
        elif path == "/api/stock/shorts/run":
            self._handle_post_stock_shorts_run(payload)
            return
        elif path == "/api/stock/shorts/config":
            self._handle_post_stock_shorts_config(payload)
            return
        elif path == "/api/stock/shorts/toggle-daemon":
            self._handle_post_stock_shorts_toggle_daemon(payload)
            return
        elif path == "/api/aura/start":
            self._handle_brand_start("aura")
            return
        elif path == "/api/aura/stop":
            self._handle_brand_stop("aura")
            return
        elif path == "/api/insurance/start":
            self._handle_brand_start("insurance")
            return
        elif path == "/api/insurance/stop":
            self._handle_brand_stop("insurance")
            return
        elif path == "/api/stock/start":
            self._handle_brand_start("stock")
            return
        elif path == "/api/stock/stop":
            self._handle_brand_stop("stock")
            return
        elif path.startswith("/api/omni-blog/publish/"):
            brand = path.split("/")[-1]
            self._handle_publish_omni_blog(brand, payload)
            return
        elif path.startswith("/api/run-hub/"):
            parts = path.split("/")
            if len(parts) >= 5:
                self._handle_run_hub(parts[3], parts[4])
                return
        elif path == "/api/kmarket/start":
            self._handle_kmarket_start()
            return
        elif path == "/api/kmarket/stop":
            self._handle_kmarket_stop()
            return
        elif path == "/api/easytax/start":
            self._handle_easytax_start()
            return
        elif path == "/api/easytax/stop":
            self._handle_easytax_stop()
            return
        elif path == "/api/all/start":
            self._handle_all_start()
            return
        elif path == "/api/all/stop":
            self._handle_all_stop()
            return
        elif path.startswith("/api/channel/start/"):
            module_name = path.split("/")[-1]
            self._handle_channel_start(module_name)
            return
        elif path.startswith("/api/channel/stop/"):
            module_name = path.split("/")[-1]
            self._handle_channel_stop(module_name)
            return
        elif path.startswith("/api/run-module/"):
            module_name = path.split("/")[-1]
            self._handle_run_module(module_name)
            return
        elif path.startswith("/api/platforms/test-publish/"):
            platform_id = path.split("/")[-1]
            self._handle_test_publish(platform_id)
            return
        elif path.startswith("/api/pipeline/run/"):
            hub_id = path.split("/")[-1]
            self._handle_run_pipeline_hub(hub_id, payload)
            return
        elif path == "/api/scenarios/generate":
            self._handle_generate_scenario(payload)
            return
        elif path == "/api/scenarios/evolve":
            self._handle_evolve_scenario(payload)
            return
        elif path == "/api/golden-batch/run":
            self._handle_post_golden_batch_run(payload)
            return
        elif path == "/api/factory/run":
            self._handle_factory_run(payload)
            return
        elif path == "/api/golden-batch/daemon/start":
            self._handle_post_golden_batch_daemon_start(payload)
            return
        elif path == "/api/golden-batch/daemon/stop":
            self._handle_post_golden_batch_daemon_stop(payload)
            return
        elif path.startswith("/api/seo/ping/"):
            brand = path.split("/")[-1]
            self._handle_seo_ping(brand)
            return
        elif path.startswith("/api/kin/"):
            # /api/kin/aura/run, /api/kin/stock/run, /api/kin/insurance/run
            parts = path.strip("/").split("/")
            b = parts[2] if len(parts) >= 3 else "aura"
            self._handle_post_kin_run(b)
            return
        elif path.startswith("/api/cafe/"):
            # /api/cafe/aura/run, /api/cafe/stock/run, /api/cafe/insurance/run
            parts = path.strip("/").split("/")
            b = parts[2] if len(parts) >= 3 else "aura"
            self._handle_post_cafe_run(b)
            return
        elif path == "/api/google-index/ping":
            self._handle_google_index_ping(payload)
            return
        elif path == "/api/health/run-diagnostic":
            self._handle_run_health_diagnostic()
            return
        elif path == "/api/kmarket/google-index":
            self._handle_kmarket_google_index()
            return
        elif path == "/api/easytax/google-index":
            self._handle_easytax_google_index()
            return
        elif path == "/api/google-index":
            self._handle_google_index()
            return
        elif path == "/api/hashtags/refresh":
            self._handle_refresh_hashtags()
            return
        elif path == "/api/settings":
            self._handle_save_settings(payload)
            return
        elif path == "/api/telegram/toggle-manager":
            self._handle_telegram_toggle_manager(payload)
            return
        elif path == "/api/telegram/broadcast":
            self._handle_telegram_broadcast(payload)
            return
        elif path == "/api/telegram/run-invite":
            self._handle_telegram_run_invite(payload)
            return
        # ── [방법 1] 타 그룹 홍보 게시 아웃리치 ──────────────────
        elif path == "/api/telegram/outreach/run":
            self._handle_telegram_outreach_run(payload)
            return
        elif path == "/api/telegram/outreach/status":
            self._handle_telegram_outreach_status(payload)
            return
        # ── [초대] 서브폰 스텔스 초대 ─────────────────────────────
        elif path == "/api/telegram/stealth-invite":
            self._handle_telegram_stealth_invite(payload)
            return
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

            # 2. Aura 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'aura'")
            aura_row = cursor.fetchone()
            aura_count = aura_row[0]
            aura_score = aura_row[1]

            # 3. Insurance 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'insurance'")
            ins_row = cursor.fetchone()
            ins_count = ins_row[0]
            ins_score = ins_row[1]

            # 4. Stock 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'stock'")
            stock_row = cursor.fetchone()
            stock_count = stock_row[0]
            stock_score = stock_row[1]

            # 5. K-Market 전용 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'kmarket'")
            km_row = cursor.fetchone()
            km_count = km_row[0]
            km_score = km_row[1]

            # 6. EasyTax 전용 실적
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(score), 0.0) FROM marketing_history WHERE service_id = 'easytax'")
            tax_row = cursor.fetchone()
            tax_count = tax_row[0]
            tax_score = tax_row[1]

        def _get_brand_kin_quota(brand_key: str):
            state_file = DATA_DIR / f"{brand_key}_kin_daily_state.json"
            today_str = get_now_kst().strftime("%Y-%m-%d")
            if state_file.exists():
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        d = json.load(f)
                        if d.get("date") == today_str:
                            return {"today_total": d.get("daily_total", 0), "target": 10}
                except Exception:
                    pass
            return {"today_total": 0, "target": 10}

        aura_kin_q = _get_brand_kin_quota("aura")
        insurance_kin_q = _get_brand_kin_quota("insurance")
        stock_kin_q = _get_brand_kin_quota("stock")

        from core.emergency_guard import EmergencyGuard
        sentinel_report = EmergencyGuard(db_mgr).get_full_sentinel_report()

        # 3대 브랜드 독립 인간 행동 봇 (하루 45분 / 매회 2~3회 좋아요) 실시간 통계
        human_routines = {}
        try:
            from brands.aura.aura_human_behavior_bot import AuraHumanBehaviorBot
            from brands.insurance.insurance_human_behavior_bot import InsuranceHumanBehaviorBot
            from brands.stock.stock_human_behavior_bot import StockHumanBehaviorBot
            human_routines = {
                "aura": AuraHumanBehaviorBot().get_today_routine_summary(),
                "insurance": InsuranceHumanBehaviorBot().get_today_routine_summary(),
                "stock": StockHumanBehaviorBot().get_today_routine_summary(),
            }
        except Exception:
            pass

        data = {
            "master_autopilot_running": (
                brand_daemons_running.get("aura", False) or 
                brand_daemons_running.get("insurance", False) or 
                brand_daemons_running.get("stock", False)
            ),
            "emergency_status": {
                "is_emergency": sentinel_report.get("is_emergency", False),
                "overall_status": sentinel_report.get("overall_status", "healthy"),
                "alerts": sentinel_report.get("alerts", []),
                "summary": sentinel_report.get("summary", {})
            },
            "human_routines": human_routines,
            "mission_timeline": sentinel_report.get("mission_timeline", []),
            "production_details": sentinel_report.get("production_details", {}),
            "kin_quotas": {
                "aura": aura_kin_q,
                "insurance": insurance_kin_q,
                "stock": stock_kin_q
            },
            "aura_running": brand_daemons_running.get("aura", False),
            "aura_stats": brand_stats.get("aura", {}),
            "insurance_running": brand_daemons_running.get("insurance", False),
            "insurance_stats": brand_stats.get("insurance", {}),
            "stock_running": brand_daemons_running.get("stock", False),
            "stock_stats": brand_stats.get("stock", {}),
            "kmarket_running": kmarket_running,
            "kmarket_stats": kmarket_stats,
            "easytax_running": easytax_running,
            "easytax_stats": easytax_stats,
            "running_channels": running_channels,
            "season": season,
            "total_history_count": total_count,
            "top_score": top_score,
            "aura_history_count": aura_count,
            "aura_top_score": aura_score,
            "insurance_history_count": ins_count,
            "insurance_top_score": ins_score,
            "stock_history_count": stock_count,
            "stock_top_score": stock_score,
            "kmarket_history_count": km_count,
            "kmarket_top_score": km_score,
            "kmarket_seo_count": 1105,
            "easytax_history_count": tax_count,
            "easytax_top_score": tax_score,
            "easytax_seo_count": 5525,
            "golden_targets": {
                "kmarket_shorts": get_golden_rotation_info("kmarket_shorts"),
                "easytax_shorts": get_golden_rotation_info("easytax_shorts"),
                "kmarket_cardnews": get_golden_rotation_info("kmarket_cardnews"),
                "easytax_cardnews": get_golden_rotation_info("easytax_cardnews"),
                "kmarket_tiktok": get_golden_rotation_info("kmarket_tiktok"),
                "easytax_tiktok": get_golden_rotation_info("easytax_tiktok")
            },
            "golden_eight_languages": GOLDEN_EIGHT_LANGUAGES,
            "golden_eight_details": GOLDEN_EIGHT_DETAILS,
            "golden_batch_summary": golden_batch_producer.get_today_production_summary(),
            "today_live_feed": today_live_tracker.get_all_live_feed(),
            "auth_sentinel": (lambda: __import__('core.platform_auth_sentinel', fromlist=['PlatformAuthSentinel']).PlatformAuthSentinel.get_full_diagnostic_report())(),
            "gpu_status": gpu_lock_manager.get_status(),
            "channel_errors": channel_errors,
            "recent_logs": recent_logs[-50:]
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_get_today_live_feed(self, brand: Optional[str] = None):
        """🚀 3대 브랜드 실시간 마케팅 무인 발행 라이브 피드 반환 (전체 또는 개별 브랜드 독립)"""
        if brand and brand in ["aura", "insurance", "stock"]:
            data = today_live_tracker.get_brand_live_status(brand)
        else:
            data = today_live_tracker.get_all_live_feed()
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_get_golden_targets(self):
        data = {
            "channels": {
                "kmarket_shorts": get_golden_rotation_info("kmarket_shorts"),
                "easytax_shorts": get_golden_rotation_info("easytax_shorts"),
                "kmarket_cardnews": get_golden_rotation_info("kmarket_cardnews"),
                "easytax_cardnews": get_golden_rotation_info("easytax_cardnews"),
                "kmarket_tiktok": get_golden_rotation_info("kmarket_tiktok"),
                "easytax_tiktok": get_golden_rotation_info("easytax_tiktok")
            },
            "golden_eight": GOLDEN_EIGHT_LANGUAGES,
            "details": GOLDEN_EIGHT_DETAILS
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_get_golden_batch_status(self):
        """8대 황금 타깃 2슬롯 대량 생산 일일 통계 반환"""
        summary = golden_batch_producer.get_today_production_summary()
        summary["daemon_running"] = golden_batch_daemon_running
        self._set_headers("application/json")
        self.wfile.write(json.dumps(summary, ensure_ascii=False).encode("utf-8"))

    def _handle_post_golden_batch_daemon_start(self, payload):
        """8대 황금 타깃 24시간 무인 데몬 시작"""
        brand = payload.get("brand", "all").lower()
        if not golden_batch_daemon_running.get(brand, False):
            golden_batch_daemon_running[brand] = True
            UnmannedStateManager.update_golden_daemon(brand, True)
            threading.Thread(target=_golden_daemon_loop, args=(brand,), daemon=True).start()
            msg = f"⏰ [{brand.upper()}] 8대 황금 타깃 24시간 무인 예약 데몬이 가동되었습니다! (11:30 & 18:30 정시 자동 생산)"
            log_event(msg, "success")
        else:
            msg = f"[{brand.upper()}] 이미 8대 황금 타깃 무인 예약 데몬이 가동 중입니다."
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "daemon_running": golden_batch_daemon_running}, ensure_ascii=False).encode("utf-8"))

    def _handle_post_golden_batch_daemon_stop(self, payload):
        """8대 황금 타깃 24시간 무인 데몬 정지"""
        brand = payload.get("brand", "all").lower()
        golden_batch_daemon_running[brand] = False
        UnmannedStateManager.update_golden_daemon(brand, False)
        msg = f"⏹️ [{brand.upper()}] 8대 황금 타깃 무인 예약 데몬이 정지되었습니다."
        log_event(msg, "info")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": msg, "daemon_running": golden_batch_daemon_running}, ensure_ascii=False).encode("utf-8"))

    def _handle_post_golden_batch_run(self, payload):
        """8대 황금 타깃 대량 생산 즉시 실행 (백그라운드 스레드)"""
        slot_name = payload.get("slot_name", "manual")
        brand = payload.get("brand", "all").lower()
        content_type = payload.get("type", "all").lower()

        def _batch_worker():
            try:
                log_event(f"🌟 [골든 배치] {slot_name} ({brand} / {content_type}) 8개국 생산 가동...", "info")
                if content_type == "shorts":
                    if brand in ["kmarket", "all"]:
                        golden_batch_producer.produce_brand_shorts_batch("kmarket", slot_name)
                    if brand in ["easytax", "all"]:
                        golden_batch_producer.produce_brand_shorts_batch("easytax", slot_name)
                elif content_type == "cardnews":
                    if brand in ["kmarket", "all"]:
                        golden_batch_producer.produce_brand_cardnews_batch("kmarket", slot_name)
                    if brand in ["easytax", "all"]:
                        golden_batch_producer.produce_brand_cardnews_batch("easytax", slot_name)
                else:
                    golden_batch_producer.execute_slot(slot_name=slot_name, brand=brand)
                log_event(f"🎉 [골든 배치] {slot_name} ({brand}) 8개국 생산이 성공적으로 완료되었습니다!", "success")
            except Exception as e:
                log_event(f"❌ [골든 배치 실패] {e}", "danger")

        threading.Thread(target=_batch_worker, daemon=True).start()
        self._set_headers("application/json")
        self.wfile.write(json.dumps({
            "success": True,
            "message": f"8대 황금 타깃 골든 배치 생산 백그라운드 가동 시작 (슬롯: {slot_name}, 브랜드: {brand}, 유형: {content_type})"
        }, ensure_ascii=False).encode("utf-8"))

    def _handle_factory_run(self, payload: dict):
        """웹 대시보드 원클릭 팩토리 콘텐츠 제작 처리"""
        brand = payload.get("brand", "easytax")
        mode = payload.get("mode", "cardnews")
        lang = payload.get("lang", "vi")
        amount = payload.get("amount", "random")
        if str(amount).lower() != "random":
            try:
                amount = int(amount)
            except Exception:
                amount = "random"

        res = factory_service.run_factory_task(
            brand=brand,
            mode=mode,
            lang=lang,
            amount=amount
        )
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_channel_start(self, module_name: str):
        global running_channels
        if not running_channels.get(module_name, False):
            running_channels[module_name] = True
            UnmannedStateManager.update_channel(module_name, True)
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
        UnmannedStateManager.update_bot("kmarket", True)
        km_channels = ["kmarket_shorts", "kmarket_tiktok", "kmarket_cardnews", "kmarket_reddit", "kmarket_briefing", "kmarket_fb_groups", "kmarket_seo", "kmarket_pdf", "kmarket_blog", "kmarket_threads"]
        UnmannedStateManager.update_channels_batch(km_channels, True)
        if not kmarket_thread or not kmarket_thread.is_alive():
            kmarket_thread = threading.Thread(target=kmarket_worker, daemon=True)
            kmarket_thread.start()
        
        # 10대 채널 전체를 24시간 연속 무인 공장 루프로 가동
        for ch in km_channels:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()

        res = {"success": True, "message": "🛒 K-Market 10대 채널 24시간 무인 자율 공장이 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_kmarket_stop(self):
        global kmarket_running, running_channels
        kmarket_running = False
        UnmannedStateManager.update_bot("kmarket", False)
        km_channels = ["kmarket_shorts", "kmarket_tiktok", "kmarket_cardnews", "kmarket_reddit", "kmarket_briefing", "kmarket_fb_groups", "kmarket_seo", "kmarket_pdf", "kmarket_blog", "kmarket_threads"]
        UnmannedStateManager.update_channels_batch(km_channels, False)
        for ch in km_channels:
            running_channels[ch] = False
        if "kmarket" in telegram_ai_managers:
            telegram_ai_managers["kmarket"].stop_background_daemon()
        res = {"success": True, "message": "⏹️ K-Market 10대 채널 및 텔레그램 AI 매니저 무인 공장 정지 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_start(self):
        global easytax_thread, easytax_running, running_channels
        easytax_running = True
        UnmannedStateManager.update_bot("easytax", True)
        et_channels = ["easytax_shorts", "easytax_tiktok", "easytax_cardnews", "easytax_reddit", "easytax_briefing", "easytax_fb_groups", "easytax_seo", "easytax_pdf", "easytax_blog", "easytax_threads"]
        UnmannedStateManager.update_channels_batch(et_channels, True)
        if not easytax_thread or not easytax_thread.is_alive():
            easytax_thread = threading.Thread(target=easytax_worker, daemon=True)
            easytax_thread.start()
        
        # 10대 채널 전체를 24시간 연속 무인 공장 루프로 가동
        for ch in et_channels:
            if not running_channels.get(ch, False):
                running_channels[ch] = True
                threading.Thread(target=channel_continuous_worker, args=(ch,), daemon=True).start()

        res = {"success": True, "message": "💰 EasyTax 10대 채널 24시간 무인 자율 공장이 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_easytax_stop(self):
        global easytax_running, running_channels
        easytax_running = False
        UnmannedStateManager.update_bot("easytax", False)
        et_channels = ["easytax_shorts", "easytax_tiktok", "easytax_cardnews", "easytax_reddit", "easytax_briefing", "easytax_fb_groups", "easytax_seo", "easytax_pdf", "easytax_blog", "easytax_threads"]
        UnmannedStateManager.update_channels_batch(et_channels, False)
        for ch in et_channels:
            running_channels[ch] = False
        if "easytax" in telegram_ai_managers:
            telegram_ai_managers["easytax"].stop_background_daemon()
        res = {"success": True, "message": "⏹️ EasyTax 10대 채널 및 텔레그램 AI 매니저 무인 공장 정지 완료."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_brand_start(self, brand: str):
        global brand_daemons_running, running_channels
        brand_daemons_running[brand] = True
        
        # 3대 슈퍼앱 24대 마케팅 허브 전체 채널 일괄 가동
        brand_modules = [
            "shorts", "cardnews", "reddit", "omni_blog", "blog", "seo", "threads",
            "naver_kin", "naver_cafe", "daum_cafe", "ppomppu", "dcinside",
            "nate_pann", "bobaedream", "fmkorea", "kakao_channel"
        ]
        for m in brand_modules:
            ch_key = f"{brand}_{m}"
            running_channels[ch_key] = True

        t = threading.Thread(target=_brand_daemon_loop, args=(brand,), daemon=True)
        t.start()
        name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 Stock Master 주식AI"}
        brand_kr = name_map.get(brand, brand.upper())
        res = {"success": True, "message": f"🚀 {brand_kr} 24개 옴니채널 무인 마케팅 데몬 및 허브가 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_brand_stop(self, brand: str):
        global brand_daemons_running, running_channels
        brand_daemons_running[brand] = False
        prefix = f"{brand}_"
        for ch in list(running_channels.keys()):
            if ch.startswith(prefix):
                running_channels[ch] = False
        name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 Stock Master 주식AI"}
        brand_kr = name_map.get(brand, brand.upper())
        res = {"success": True, "message": f"⏹️ {brand_kr} 무인 마케팅 데몬 및 하위 채널이 정지되었습니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_run_hub(self, brand: str, hub_key: str):
        def _worker():
            name_map = {"aura": "💖 Aura", "insurance": "🛡️ 보험비교", "stock": "📈 주식AI", "kmarket": "🛒 K-Market", "easytax": "💰 EasyTax"}
            brand_kr = name_map.get(brand, brand.upper())
            module_name = f"{brand}_{hub_key}"
            log_event(f"⚡ [{brand_kr} #{hub_key}] 채널 원클릭 즉시 실행 중...", "info")
            try:
                res = execute_single_channel_task(module_name)
                clear_channel_error(module_name)
                log_event(f"🎉 [{brand_kr} #{hub_key}] 채널 즉시 실행 완료: {res}", "success")
            except Exception as ex:
                import traceback
                err_detail = traceback.format_exc()
                record_channel_error(module_name, str(ex))
                log_event(f"❌ [{brand_kr} #{hub_key}] 실행 중 오류 발생: {ex}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        res = {"success": True, "message": f"⚡ [{brand.upper()}] #{hub_key} 채널 즉시 발행 요청이 전달되었습니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_publish_omni_blog(self, brand: str, payload: dict = None):
        """💖 Aura / 🛡️ 보험비교 / 📈 주식AI 4대 채널 옴니블로그 1회 즉시 발행 (백그라운드 스레드)"""
        force_topic = payload.get("topic_id") if payload else None
        
        def _worker():
            name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ InsureBalance 보험비교", "stock": "📈 StockMaster 주식AI"}
            brand_kr = name_map.get(brand, brand.upper())
            log_event(f"🎬 [{brand_kr}] 4대 옴니블로그 1회 즉시 발행 가동 시작... (Gemini 2,000자 + 16:9 맞춤 사진)", "info")
            try:
                if brand == "aura":
                    from brands.aura.aura_blog_scheduler import AuraBlogScheduler
                    scheduler = AuraBlogScheduler()
                    res = scheduler.run_one_cycle(force_topic_id=force_topic)
                elif brand == "insurance":
                    from brands.insurance.insurance_blog_scheduler import InsuranceBlogScheduler
                    scheduler = InsuranceBlogScheduler()
                    res = scheduler.run_one_cycle(force_topic_id=force_topic)
                elif brand == "stock":
                    from brands.stock.stock_blog_scheduler import StockBlogScheduler
                    scheduler = StockBlogScheduler()
                    res = scheduler.run_one_cycle(force_topic_id=force_topic)
                else:
                    raise ValueError(f"Unknown brand: {brand}")

                channels = res.get("publish_results", {}).get("channels", {})
                naver_url = channels.get("naver_blog", {}).get("url", "-")
                tistory_url = channels.get("tistory", {}).get("post_url", channels.get("tistory", {}).get("url", "-"))
                brunch_status = channels.get("brunch", {}).get("status", "-")
                
                log_event(
                    f"🎉 [{brand_kr}] 4대 옴니블로그 1회 발행 대성공!\n"
                    f"  - 📚 주제: #{res.get('topic_id')} '{res.get('title')}'\n"
                    f"  - 🟢 네이버: {naver_url}\n"
                    f"  - 🟠 티스토리: {tistory_url}\n"
                    f"  - 🟡 브런치: {brunch_status}\n"
                    f"  - 🎨 16:9 사진: {res.get('image_url', '-')}\n"
                    f"  - ⏭️ 다음 예정 번호: #{res.get('next_topic_id', '-')}",
                    "success"
                )

                # 🌐 [신규 블로그 발행 완료 직후 2대 포털 검색엔진 동시 색인 핑 자동 전송]
                try:
                    log_event(f"🌐 [{brand_kr}] 신규 칼럼 구글·네이버 검색 로봇 색인 핑 자동 전송 중...", "info")
                    if brand == "aura":
                        from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
                        ping_res = AuraSearchIndexingHub().ping_all_engines()
                    elif brand == "insurance":
                        from brands.insurance.insurance_search_indexing_hub import InsuranceSearchIndexingHub
                        ping_res = InsuranceSearchIndexingHub().ping_all_engines()
                    elif brand == "stock":
                        from brands.stock.stock_search_indexing_hub import StockSearchIndexingHub
                        ping_res = StockSearchIndexingHub().ping_all_engines()
                    else:
                        ping_res = {"success": True}
                    log_event(f"🌐 [{brand_kr}] 2대 검색엔진 동시 색인 핑 전송 완료: {ping_res.get('message', '성공')}", "success")
                except Exception as pe:
                    log_event(f"⚠️ [{brand_kr}] 블로그 발행 후 색인 핑 자동 전송 예외: {pe}", "warning")

            except Exception as ex:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"❌ [{brand_kr}] 옴니블로그 발행 오류 발생: {ex}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        name_map = {"aura": "Aura 데이팅", "insurance": "보험비교", "stock": "주식AI"}
        res = {
            "success": True, 
            "message": f"🚀 [{name_map.get(brand, brand)}] 4대 옴니블로그 1회 즉시 발행이 시작되었습니다. 발행 완료 즉시 구글 & 네이버 색인 핑이 자동 전송됩니다!"
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_seo_ping(self, brand: str):
        """🌐 3대 슈퍼앱 (Aura · 보험비교 · 주식AI) 구글 + 네이버 2대 검색엔진 동시 색인 핑 전용 API"""
        def _worker():
            name_map = {
                "aura": "💖 Aura 데이팅", 
                "insurance": "🛡️ InsureBalance 보험비교", 
                "stock": "📈 StockMaster 주식AI",
                "kmarket": "🛒 K-Market",
                "easytax": "💰 EasyTax"
            }
            brand_kr = name_map.get(brand, brand.upper())
            log_event(f"🌐 [{brand_kr}] 2대 포털 검색엔진 (구글 + 네이버) 실시간 색인 핑 가속 가동...", "info")
            try:
                if brand == "aura":
                    from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
                    res = AuraSearchIndexingHub().ping_all_engines()
                elif brand == "insurance":
                    from brands.insurance.insurance_search_indexing_hub import InsuranceSearchIndexingHub
                    res = InsuranceSearchIndexingHub().ping_all_engines()
                elif brand == "stock":
                    from brands.stock.stock_search_indexing_hub import StockSearchIndexingHub
                    res = StockSearchIndexingHub().ping_all_engines()
                elif brand == "kmarket":
                    from modules.seo_kmarket import KMarketSEOPusher
                    res = KMarketSEOPusher(DBManager()).build_and_push_index()
                elif brand == "easytax":
                    from modules.seo_easytax import EasyTaxSEOPusher
                    res = EasyTaxSEOPusher(DBManager()).build_and_push_index()
                else:
                    res = {"success": False, "message": f"알 수 없는 브랜드: {brand}"}

                log_event(f"🎉 [{brand_kr}] {res.get('message', '2대 검색엔진 동시 색인 핑 전송 완료')}", "success")
            except Exception as ex:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"❌ [{brand_kr}] 색인 핑 전송 중 오류 발생: {ex}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        name_map = {"aura": "Aura 데이팅", "insurance": "보험비교", "stock": "주식AI", "kmarket": "K-Market", "easytax": "EasyTax"}
        res = {
            "success": True,
            "brand": brand,
            "message": f"🌐 [{name_map.get(brand, brand)}] 구글 서치콘솔 & 네이버 서치어드바이저 2대 검색엔진 동시 색인 핑이 백그라운드에서 발송되었습니다!"
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_get_kin_history(self, brand: str = "aura"):
        """💖 Aura, Stock Master, InsureBalance 3대 브랜드 지식iN 실시간 낚아채기 현황 및 히스토리 조회"""
        try:
            if brand == "stock":
                from brands.stock.stock_kin_scheduler import StockKinScheduler
                scheduler = StockKinScheduler()
            elif brand == "insurance":
                from brands.insurance.insurance_kin_scheduler import InsuranceKinScheduler
                scheduler = InsuranceKinScheduler()
            else:
                from brands.aura.aura_kin_scheduler import AuraKinScheduler
                scheduler = AuraKinScheduler()

            state = scheduler._load_state()
            if hasattr(scheduler, "get_current_slot"):
                slot = scheduler.get_current_slot()
            else:
                slot = {"name": "24시간 실시간 레이더 감시", "target": scheduler.DAILY_TARGET}
            history = scheduler.pipeline._load_history()
            today_str = datetime.now().strftime("%Y-%m-%d")
            actual_today = sum(1 for h in history if str(h.get("created_at", "")).startswith(today_str) and h.get("status") == "published")
            daily_total = max(state.get("daily_total", 0), actual_today)
            data = {
                "success": True,
                "brand": brand,
                "daily_total": daily_total,
                "daily_target": scheduler.DAILY_TARGET,
                "current_slot": slot,
                "slots_breakdown": state.get("slots", {}),
                "last_run_at": state.get("last_run_at", ""),
                "history": history
            }
        except Exception as e:
            data = {
                "success": False,
                "brand": brand,
                "daily_total": 0,
                "daily_target": 10,
                "current_slot": {"name": "오류", "target": 0},
                "history": [],
                "error": str(e)
            }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_post_kin_run(self, brand: str = "aura"):
        """💖 Aura, Stock, Insurance 3대 브랜드 지식iN 1회 낚아채기 즉시 실행 API"""
        brand_name_map = {
            "aura": "💖 Aura 데이팅",
            "stock": "📈 Stock Master 주식 AI",
            "insurance": "🛡️ InsureBalance 보험비교"
        }
        b_name = brand_name_map.get(brand, brand)

        def _worker():
            log_event(f"🚀 [{b_name} 지식iN] 100대 황금 키워드 실시간 질문 낚아채기 즉시 1회 실행 시작...", "info")
            try:
                if brand == "stock":
                    from brands.stock.stock_kin_scheduler import StockKinScheduler
                    scheduler = StockKinScheduler()
                elif brand == "insurance":
                    from brands.insurance.insurance_kin_scheduler import InsuranceKinScheduler
                    scheduler = InsuranceKinScheduler()
                else:
                    from brands.aura.aura_kin_scheduler import AuraKinScheduler
                    scheduler = AuraKinScheduler()

                res = scheduler.trigger_scheduled_catch()
                if res.get("success"):
                    rec = res.get("record", {})
                    log_event(
                        f"🎉 [{b_name} 지식iN 낚아채기 성공]\n"
                        f"  - 🏷️ 키워드: {rec.get('keyword')}\n"
                        f"  - ❓ 질문: {rec.get('title')}\n"
                        f"  - 📊 적합도: {rec.get('score')}점 ({rec.get('reason')})\n"
                        f"  - 🔗 바로가기: {rec.get('url')}",
                        "success"
                    )
                else:
                    log_event(f"ℹ️ [{b_name} 지식iN] {res.get('message', '새 질문 대기 중')}", "info")
            except Exception as ex:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"❌ [{b_name} 지식iN 실행 실패] {ex}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        res = {
            "success": True,
            "brand": brand,
            "message": f"🚀 [{b_name} 지식iN] 100대 황금 키워드 실시간 질문 낚아채기가 백그라운드에서 가동되었습니다!"
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_all_start(self):
        global running_channels, brand_daemons_running
        # 🇰🇷 [한국마케팅봇 전용] 대한민국 3대 슈퍼앱 (Aura · 보험비교 · 주식AI) 가동
        for b in ["aura", "insurance", "stock"]:
            if not brand_daemons_running.get(b, False):
                brand_daemons_running[b] = True
                threading.Thread(target=_brand_daemon_loop, args=(b,), daemon=True).start()
            main_ch = f"{b}_blog"
            if not running_channels.get(main_ch, False):
                running_channels[main_ch] = True
                threading.Thread(target=channel_continuous_worker, args=(main_ch,), daemon=True).start()

        res = {"success": True, "message": "🚀 [한국마케팅봇 전체 가동] 💖 Aura · 🛡️ 보험비교 · 📈 주식AI 3대 슈퍼앱 24시간 무인 공장이 일괄 가동되었습니다!"}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_all_stop(self):
        global running_channels, brand_daemons_running
        # 🇰🇷 [한국마케팅봇 전용] 대한민국 3대 슈퍼앱 (Aura · 보험비교 · 주식AI) 정지
        for b in ["aura", "insurance", "stock"]:
            brand_daemons_running[b] = False
        for ch in list(running_channels.keys()):
            if ch.startswith(("aura_", "insurance_", "stock_")):
                running_channels[ch] = False
        res = {"success": True, "message": "🛑 [한국마케팅봇 전체 정지] 💖 Aura · 🛡️ 보험비교 · 📈 주식AI 모든 봇 및 채널 가동이 안전하게 중지되었습니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_run_module(self, module_name: str):
        def _worker():
            try:
                log_event(f"⚡ [{module_name}] 즉시 1회 시험 실행 시작...", "info")
                res = execute_single_channel_task(module_name)
                clear_channel_error(module_name)
                log_event(f"✅ [{module_name}] 즉시 1회 실행 완료: {res}", "success")
            except Exception as e:
                import traceback
                err_detail = traceback.format_exc()
                record_channel_error(module_name, str(e))
                log_event(f"❌ [{module_name} 1회 실행 실패] {e}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        res = {"success": True, "message": f"⚡ [{module_name}] 즉시 1회 실행이 백그라운드에서 가동되었습니다."}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

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
            platforms = uploader.get_all_platforms_status()
        except Exception as e:
            platforms = {}
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"platforms": platforms}).encode("utf-8"))

    def _handle_get_hashtags(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        brand = qs.get("brand", ["aura"])[0].lower()

        from core.trend_scraper import ViralTrendScraper
        scraper = ViralTrendScraper()
        kr_live_trends = scraper.fetch_korea_live_trends()

        if brand == "aura":
            try:
                from brands.aura.aura_keyword_matrix import AuraKeywordMatrix
                matrix = AuraKeywordMatrix()
                data = matrix.get_dashboard_summary()
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"brand": "aura", "hashtags": data, "kr_live_trends": kr_live_trends}, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Aura 키워드 로드 실패: {e}", "warning")
        elif brand in ["insurance", "insure"]:
            try:
                from brands.insurance.insurance_keyword_matrix import InsuranceKeywordMatrix
                matrix = InsuranceKeywordMatrix()
                data = matrix.get_dashboard_summary()
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"brand": "insurance", "hashtags": data, "kr_live_trends": kr_live_trends}, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Insurance 키워드 로드 실패: {e}", "warning")
        elif brand in ["stock", "stockmaster"]:
            try:
                from brands.stock.stock_keyword_matrix import StockKeywordMatrix
                matrix = StockKeywordMatrix()
                data = matrix.get_dashboard_summary()
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"brand": "stock", "hashtags": data, "kr_live_trends": kr_live_trends}, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Stock 키워드 로드 실패: {e}", "warning")

        self._set_headers("application/json")
        self.wfile.write(json.dumps({"brand": brand, "hashtags": scraper.hashtag_db, "kr_live_trends": kr_live_trends}, ensure_ascii=False).encode("utf-8"))

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
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        brand = qs.get("brand", ["kmarket"])[0].lower()

        if brand == "aura":
            try:
                from brands.aura.aura_keyword_matrix import AuraKeywordMatrix
                matrix = AuraKeywordMatrix()
                data = matrix.refresh_all_categories()
                log_event("💖 [Aura] 2030 네이버 & 구글 실시간 바이럴 키워드 매트릭스가 새로고침되었습니다.", "success")
                self._set_headers("application/json")
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "💖 Aura 2030 실시간 네이버/구글 바이럴 키워드가 성공적으로 갱신되었습니다.",
                    "brand": "aura",
                    "hashtags": data
                }, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Aura 키워드 갱신 오류: {e}", "warning")
        elif brand in ["insurance", "insure"]:
            try:
                from brands.insurance.insurance_keyword_matrix import InsuranceKeywordMatrix
                matrix = InsuranceKeywordMatrix()
                data = matrix.refresh_all_categories()
                log_event("🛡️ [보험 리밸런스] 실시간 네이버 & 구글 키워드 매트릭스가 새로고침되었습니다.", "success")
                self._set_headers("application/json")
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "🛡️ 보험 리밸런스 실시간 네이버/구글 바이럴 키워드가 성공적으로 갱신되었습니다.",
                    "brand": "insurance",
                    "hashtags": data
                }, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Insurance 키워드 갱신 오류: {e}", "warning")
        elif brand in ["stock", "stockmaster"]:
            try:
                from brands.stock.stock_keyword_matrix import StockKeywordMatrix
                matrix = StockKeywordMatrix()
                data = matrix.refresh_all_categories()
                log_event("📈 [StockMaster] 실시간 네이버 & 구글 주식 키워드 매트릭스가 새로고침되었습니다.", "success")
                self._set_headers("application/json")
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "📈 StockMaster 실시간 네이버/구글 주식 키워드가 성공적으로 갱신되었습니다.",
                    "brand": "stock",
                    "hashtags": data
                }, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                log_event(f"⚠️ Stock 키워드 갱신 오류: {e}", "warning")

        from core.trend_scraper import ViralTrendScraper
        scraper = ViralTrendScraper()
        data = scraper.refresh_daily_trends()
        log_event("📈 실시간 바이럴 해시태그 트렌드가 새로고침되었습니다.", "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": "실시간 바이럴 해시태그가 성공적으로 갱신되었습니다.", "hashtags": data}).encode("utf-8"))

    def _handle_get_outputs(self):
        items = []
        user_desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop"

        # 1. 3대 브랜드 바탕화면 산출물 스캔 (Aura, Insurance, Stock 카드뉴스 슬라이드 & 숏폼 비디오)
        if user_desktop.exists():
            # (1) 카드뉴스 패키지 폴더들 탐색
            for folder in user_desktop.glob("*"):
                if folder.is_dir():
                    folder_name = folder.name
                    brand = "aura" if ("아우라" in folder_name or "aura" in folder_name.lower()) else \
                            "insurance" if ("보험" in folder_name or "insure" in folder_name.lower()) else \
                            "stock" if ("주식" in folder_name or "stock" in folder_name.lower()) else None
                    if brand:
                        for p in folder.glob("*"):
                            if p.is_file():
                                ext = p.suffix.lower()
                                media_type = "image" if ext in [".png", ".jpg", ".jpeg"] else "video" if ext in [".mp4", ".mov", ".avi"] else "audio" if ext in [".mp3", ".wav"] else "doc"
                                size_kb = round(p.stat().st_size / 1024, 1)
                                mtime = p.stat().st_mtime
                                rel_path = f"{folder.name}/{p.name}"
                                items.append({
                                    "name": f"[{folder.name}] {p.name}",
                                    "brand": brand,
                                    "category": "카드뉴스 슬라이드" if media_type == "image" else "숏폼 비디오" if media_type == "video" else "포스팅 가이드" if media_type == "doc" else "미디어",
                                    "type": media_type,
                                    "size": f"{size_kb} KB",
                                    "url": f"/desktop_media/{urllib.parse.quote(rel_path)}",
                                    "mtime": mtime
                                })

            # (2) 바탕화면 루트의 22초 숏폼 완제품 비디오 탐색
            for p in user_desktop.glob("*.mp4"):
                if p.is_file():
                    fname = p.name
                    brand = "aura" if ("아우라" in fname or "aura" in fname.lower() or "dating" in fname.lower()) else \
                            "insurance" if ("보험" in fname or "insure" in fname.lower()) else \
                            "stock" if ("주식" in fname or "stock" in fname.lower() or "quant" in fname.lower()) else "aura"
                    size_kb = round(p.stat().st_size / 1024, 1)
                    mtime = p.stat().st_mtime
                    items.append({
                        "name": fname,
                        "brand": brand,
                        "category": "22초 완성형 숏폼",
                        "type": "video",
                        "size": f"{size_kb} KB",
                        "url": f"/desktop_media/{urllib.parse.quote(fname)}",
                        "mtime": mtime
                    })

        # 2. data/outputs/ 레거시 및 공용 미디어 산출물 스캔
        categories = ["cardnews", "shorts", "pdf_guides", "briefings"]
        for cat in categories:
            cat_dir = OUTPUTS_DIR / cat
            if cat_dir.exists():
                for p in cat_dir.glob("*"):
                    if p.is_file():
                        ext = p.suffix.lower()
                        media_type = "image" if ext in [".png", ".jpg", ".jpeg"] else "video" if ext in [".mp4", ".mov", ".avi"] else "audio" if ext in [".mp3", ".wav"] else "doc"
                        size_kb = round(p.stat().st_size / 1024, 1)
                        mtime = p.stat().st_mtime
                        p_name = p.name.lower()
                        brand = "aura" if ("aura" in p_name or "아우라" in p.name) else \
                                "insurance" if ("insure" in p_name or "보험" in p.name) else \
                                "stock" if ("stock" in p_name or "주식" in p.name) else "aura"
                        items.append({
                            "name": p.name,
                            "brand": brand,
                            "category": cat.replace("_", " ").title(),
                            "type": media_type,
                            "size": f"{size_kb} KB",
                            "url": f"/outputs/{cat}/{p.name}",
                            "mtime": mtime
                        })

        # 1순위: 최신 생성순 (mtime 내림차순)
        items.sort(key=lambda x: -x["mtime"])
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"items": items, "gpu_status": gpu_lock_manager.get_status()}, ensure_ascii=False).encode("utf-8"))

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
            is_aura_running=brand_daemons_running.get("aura", False),
            is_ins_running=brand_daemons_running.get("insurance", False),
            is_stock_running=brand_daemons_running.get("stock", False),
            is_km_running=kmarket_running,
            is_tax_running=easytax_running
        )
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    def _handle_get_ir_analytics(self, parsed_url):
        import importlib
        import core.ir_analytics
        importlib.reload(core.ir_analytics)
        from core.ir_analytics import IRAnalyticsEngine
        query_params = urllib.parse.parse_qs(parsed_url.query)
        period = query_params.get("period", ["today"])[0]
        brand = query_params.get("brand", ["all"])[0]

        db_mgr = DBManager()
        engine = IRAnalyticsEngine(db_mgr)
        data = engine.get_detailed_dashboard_data(period=period, brand=brand)
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

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

        # 🧬 링크 클릭 유입 집계
        try:
            channel_hint = f"{target}_shorts" if "shorts" in utm_content else f"{target}_cardnews"
            engine_hint = "gemini"
            ab_evolution_engine.record_engagement(channel_hint, engine_hint, clicks=1)
            log_event(f"🎯 [유입 클릭] {target.upper()} 링크 유입 -> {engine_hint}", "success")
        except Exception:
            pass

        # 타겟 서비스로 리다이렉트
        target_url = "https://ktrs-market.vercel.app" if target == "kmarket" else "https://ktrs-service.vercel.app"
        self._set_headers("text/html", 302)
        self.send_header("Location", target_url)
        self.end_headers()

    def _handle_get_media_engine(self):
        """미디어 생성 엔진 설정 및 A/B 자가학습 통계 조회"""
        self._set_headers("application/json")
        self.wfile.write(json.dumps({
            "success": True,
            "settings": get_media_engine_settings(),
            "stats": ab_evolution_engine.get_all_stats()
        }, ensure_ascii=False).encode("utf-8"))

    def _handle_post_media_engine(self, payload):
        """미디어 생성 엔진 모드 변경"""
        channel_key = payload.get("channel_key")
        engine_mode = payload.get("engine_mode", "ab_auto")
        if channel_key:
            set_media_engine_setting(channel_key, engine_mode)
            log_event(f"⚡ [엔진 전환] {channel_key} -> {engine_mode}", "info")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({
            "success": True,
            "settings": get_media_engine_settings(),
            "stats": ab_evolution_engine.get_all_stats()
        }, ensure_ascii=False).encode("utf-8"))

    def _handle_kmarket_clean_view(self, parsed_url):
        """
        🛡️ KTRS 마켓 클린 모바일 뷰어 프록시:
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
            self.wfile.write(f"<h3>KTRS 마켓 로딩 실패 ({target_url}): {e}</h3>".encode("utf-8"))
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

            /* 🥕 당근마켓 / KTRS 마켓 순정 모바일 1열 리스트 스타일 */
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
        - KTRS 마켓 프론트엔드가 페이지 로드 시 호출하는 핵심 API
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
            is_aura_running=aura_running,
            is_ins_running=insurance_running,
            is_stock_running=stock_running,
            is_km_running=False,
            is_tax_running=False
        )
        score = res.get('health_score', 0)
        status_msg = f"🩺 [실시간 정밀 자가진단] 건강도 {score}%"
        log_event(status_msg, "info" if score < 100 else "success")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": True, "message": status_msg, "diagnosis": res}).encode("utf-8"))


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
            res = client.publish_url("https://ktrs-market.vercel.app/en")
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

    def _handle_get_telegram_stats(self, parsed):
        query_params = urllib.parse.parse_qs(parsed.query)
        brand = query_params.get("brand", ["stock"])[0].lower()
        if brand in domestic_telegram_engines:
            stats = domestic_telegram_engines[brand].get_status()
            self._set_headers("application/json")
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))
            return

        manager = telegram_ai_managers.get(brand, telegram_ai_managers["kmarket"])

        stats = {
            "brand": brand,
            "ai_manager": manager.get_stats(),
            "scraper": {
                "today_invited": telegram_scraper.get_today_invite_count(),
                "total_invited_history": len(telegram_scraper.get_already_invited_user_ids()),
                "target_groups_count": len(telegram_scraper.discoverer.get_all_groups())
            },
            "credentials": {
                "bot_configured": bool(manager.bot_token),
                "chat_configured": bool(manager.chat_id)
            }
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))

    def _handle_telegram_toggle_manager(self, payload: Dict[str, Any]):
        brand = payload.get("brand", "stock").lower()
        action = payload.get("action", "toggle")
        if brand in domestic_telegram_engines:
            res = domestic_telegram_engines[brand].toggle_daemon(action)
            log_event(res["message"], "success" if res.get("is_running") else "warning")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        manager = telegram_ai_managers.get(brand, telegram_ai_managers["kmarket"])

        if action == "start":
            if not manager.is_running:
                manager.start_background_daemon()
                UnmannedStateManager.update_telegram_manager(brand, True)
            msg = f"🤖 [TelegramAIManager] {brand.upper()} 24시간 17개국어 AI 커뮤니티 매니저가 가동되었습니다!"
            log_event(msg, "success")
        elif action == "stop":
            if manager.is_running:
                manager.stop_background_daemon()
                UnmannedStateManager.update_telegram_manager(brand, False)
            msg = f"⏹️ [TelegramAIManager] {brand.upper()} 24시간 AI 커뮤니티 매니저가 정지되었습니다."
            log_event(msg, "warning")
        else:
            if manager.is_running:
                manager.stop_background_daemon()
                msg = f"⏹️ [TelegramAIManager] {brand.upper()} 24시간 AI 커뮤니티 매니저가 정지되었습니다."
                log_event(msg, "warning")
            else:
                manager.start_background_daemon()
                msg = f"🤖 [TelegramAIManager] {brand.upper()} 24시간 17개국어 AI 커뮤니티 매니저가 가동되었습니다!"
                log_event(msg, "success")

        result = {"success": True, "brand": brand, "is_running": manager.is_running, "message": msg}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def _handle_telegram_broadcast(self, payload: Dict[str, Any]):
        b_type = payload.get("type", "morning_briefing")
        brand = payload.get("brand", "stock").lower()

        if brand in domestic_telegram_engines:
            if b_type == "poll":
                res = domestic_telegram_engines[brand].broadcast_poll()
            else:
                res = domestic_telegram_engines[brand].broadcast_briefing()
            log_event(res["message"], "success" if res.get("success") else "warning")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        if b_type == "poll":
            res = telegram_publisher.broadcast_interactive_poll()
            msg = f"📊 [Telegram] 커뮤니티 참여형 투표 발송 완료 ({brand.upper()})"
        else:
            res = telegram_publisher.broadcast_morning_briefing(brand)
            msg = f"🌅 [Telegram] {brand.upper()} 모닝 브리핑 발송 완료"

        log_event(msg, "success" if res.get("success") else "warning")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": res.get("success", False), "message": msg, "detail": res}, ensure_ascii=False).encode("utf-8"))

    def _handle_telegram_run_invite(self, payload: Dict[str, Any]):
        brand = payload.get("brand", "stock").lower()
        if brand in domestic_telegram_engines:
            res = domestic_telegram_engines[brand].execute_stealth_invite()
            log_event(res["message"], "success" if res.get("success") else "warning")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        manager = telegram_ai_managers.get(brand, telegram_ai_managers["kmarket"])
        target_chat = payload.get("chat_id") or manager.chat_id or "default_chat"
        res = telegram_scraper.execute_stealth_invite_cycle(target_chat_id=target_chat)
        msg = f"🕵️ [TelegramInviter] {brand.upper()} 스텔스 1회 초대 완료 (오늘 누적 {res.get('today_invited', 0)}명)"
        log_event(msg, "success" if res.get("success") else "warning")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": res.get("success", False), "message": msg, "detail": res}, ensure_ascii=False).encode("utf-8"))

    # ── [방법 1] 타 그룹 홍보 게시 아웃리치 핸들러 ──────────────────────
    def _handle_telegram_outreach_run(self, payload):
        """3대 국내 앱 & K-Market / EasyTax 타 그룹 홍보 게시 1회 실행"""
        brand = payload.get("brand", "stock").lower()
        if brand in domestic_telegram_engines:
            res = domestic_telegram_engines[brand].execute_outreach()
            log_event(res["message"], "success" if res.get("success") else "warning")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        poster = telegram_outreach_posters.get(brand, telegram_outreach_posters["kmarket"])
        res = poster.execute_outreach_cycle()
        status = res.get("status", "")
        if status == "POSTED":
            msg = f"📢 [{brand.upper()}] 아웃리치 게시 완료: @{res.get('group_username','')} ({res.get('lang','')})"
            log_event(msg, "success")
        elif status == "NO_ELIGIBLE_GROUPS":
            msg = f"⏸️ [{brand.upper()}] 아웃리치: 오늘 게시 가능한 그룹 없음 (5일 간격 유지 중)"
            log_event(msg, "info")
        else:
            msg = f"⚠️ [{brand.upper()}] 아웃리치 게시 실패: {res.get('error', 'Telethon 세션 미설정')}"
            log_event(msg, "warning")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": res.get("success", False), "message": msg, "detail": res}, ensure_ascii=False).encode("utf-8"))

    def _handle_telegram_outreach_status(self, payload):
        """3대 국내 앱 & K-Market / EasyTax 아웃리치 현황 조회"""
        brand = payload.get("brand", "stock").lower()
        if brand in domestic_telegram_engines:
            status = domestic_telegram_engines[brand].get_outreach_status()
            self._set_headers("application/json")
            self.wfile.write(json.dumps(status, ensure_ascii=False).encode("utf-8"))
            return

        poster = telegram_outreach_posters.get(brand, telegram_outreach_posters["kmarket"])
        status = poster.get_status()
        self._set_headers("application/json")
        self.wfile.write(json.dumps(status, ensure_ascii=False).encode("utf-8"))

    # ── [초대] 서브폰 스텔스 초대 핸들러 ─────────────────────────────────
    def _handle_telegram_stealth_invite(self, payload):
        """3대 국내 앱 & K-Market / EasyTax 서브폰 스텔스 1회 초대 실행"""
        brand = payload.get("brand", "stock").lower()
        if brand in domestic_telegram_engines:
            res = domestic_telegram_engines[brand].execute_stealth_invite()
            log_event(res["message"], "success" if res.get("success") else "warning")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        source_group = payload.get("source_group", None)  # 없으면 라운드로빈 자동 선택
        inviter = telegram_stealth_inviters.get(brand, telegram_stealth_inviters["kmarket"])
        res = inviter.execute_invite_cycle(source_group_username=source_group)
        status = res.get("status", "")
        if status == "INVITED":
            msg = f"🎉 [{brand.upper()}] 스텔스 초대 성공: {res.get('invited_user','')}(@{res.get('username','')}) │ 오늘 {res.get('today_count',0)}/{inviter.get_status()['daily_limit']}명"
            log_event(msg, "success")
        elif status == "DAILY_LIMIT_REACHED":
            msg = f"🛑 [{brand.upper()}] 오늘 초대 한도 달성 ({res.get('today_count',0)}명/일)"
            log_event(msg, "info")
        elif status == "NO_SESSION":
            msg = f"⚠️ [{brand.upper()}] 서브폰 세션 파일 없음 → setup_telethon_session.py 실행 필요"
            log_event(msg, "warning")
        else:
            msg = f"⚠️ [{brand.upper()}] 스텔스 초대 결과: {status} - {res.get('error', res.get('message', ''))}"
            log_event(msg, "warning")
        self._set_headers("application/json")
        self.wfile.write(json.dumps({"success": res.get("success", False), "message": msg, "detail": res}, ensure_ascii=False).encode("utf-8"))


    # ── [카페] 네이버 8대/5대 정예 카페 스텔스 침투 핸들러 ─────────
    def _handle_get_cafe_history(self, brand="aura"):
        """8대/5대 정예 카페 스텔스 침투 현황 및 최근 이력 반환"""
        if brand == "stock":
            from brands.stock.stock_live_tracker import StockLiveTracker
            tracker = StockLiveTracker()
        elif brand == "insurance":
            from brands.insurance.insurance_live_tracker import InsuranceLiveTracker
            tracker = InsuranceLiveTracker()
        else:
            from brands.aura.aura_live_tracker import AuraLiveTracker
            tracker = AuraLiveTracker()

        today_str = get_now_kst().strftime("%Y-%m-%d")
        cafe_info = tracker._get_cafe_info(today_str)
        res_data = {
            "success": True,
            "brand": brand,
            "data": cafe_info
        }
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))

    def _handle_post_cafe_run(self, brand="aura"):
        """8대/5대 정예 카페 1회 즉시 스텔스 침투 트리거 (백그라운드 비동기)"""
        name_map = {"aura": "💖 Aura 데이팅", "insurance": "🛡️ 보험 리밸런스", "stock": "📈 StockMaster AI"}
        b_name = name_map.get(brand, brand.upper())

        def _worker():
            try:
                import asyncio
                log_event(f"☕ [{b_name} 카페] 5일 로테이션 스캔 & 파이썬 100% 심사 침투 시작...", "info")
                if brand == "stock":
                    from brands.stock.stock_cafe_pipeline import StockCafePipeline
                    res = asyncio.run(StockCafePipeline().run_daily_stealth_infiltration(dry_run=False))
                elif brand == "insurance":
                    from brands.insurance.insurance_cafe_pipeline import InsuranceCafePipeline
                    res = asyncio.run(InsuranceCafePipeline().run_daily_stealth_infiltration(dry_run=False))
                else:
                    from brands.aura.aura_cafe_pipeline import AuraCafePipeline
                    res = asyncio.run(AuraCafePipeline().run_daily_stealth_infiltration(dry_run=False))

                st = res.get("status", "")
                msg = res.get("message", "완료")
                is_ok = "SUCCESS" in str(st) or "COMPLETED" in str(st)
                log_event(f"☕ [{b_name} 카페 결과] {st}: {msg}", "success" if is_ok else "info")
            except Exception as e:
                import traceback
                err = traceback.format_exc()
                log_event(f"❌ [{b_name} 카페 침투 예외] {e}\n{err}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        self._set_headers("application/json")
        self.wfile.write(json.dumps({
            "success": True,
            "brand": brand,
            "message": f"☕ [{b_name}] 네이버 카페 1회 즉시 침투가 백그라운드에서 시작되었습니다."
        }, ensure_ascii=False).encode("utf-8"))

    def _handle_seo_ping(self, brand="aura"):
        """구글/네이버 검색엔진 동시 색인 핑 전송"""
        if brand == "aura":
            from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
            res = AuraSearchIndexingHub().ping_all_engines()
        elif brand == "stock":
            from brands.stock.stock_search_indexing_hub import StockSearchIndexingHub
            res = StockSearchIndexingHub().ping_all_engines()
        elif brand == "insurance":
            from brands.insurance.insurance_search_indexing_hub import InsuranceSearchIndexingHub
            res = InsuranceSearchIndexingHub().ping_all_engines()
        else:
            res = {"success": False, "message": f"알 수 없는 브랜드: {brand}"}

        log_event(res.get("message", f"🌐 [{brand.upper()}] 색인 핑 전송 완료"), "success" if res.get("success") else "warning")
        self._set_headers("application/json")
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

    # ── [📈 StockMaster AI] 30초 퀀트 숏폼 자율 스케줄러 핸들러 ─────────
    def _handle_get_stock_shorts_status(self):
        """📈 StockMaster AI 30초 퀀트 숏폼 스케줄러 실시간 현황 조회"""
        try:
            from brands.stock.stock_shorts_scheduler import StockShortsScheduler
            scheduler = StockShortsScheduler()
            data = scheduler.get_status()
        except Exception as e:
            data = {"success": False, "error": str(e)}
        self._set_headers("application/json")
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_post_stock_shorts_run(self, payload: dict):
        """📈 StockMaster AI 30초 퀀트 숏폼 1회 즉시 생성 (수동/선택 주제)"""
        topic_id = payload.get("topic_id")
        if topic_id is not None:
            try:
                topic_id = int(topic_id)
            except Exception:
                topic_id = None

        def _worker():
            try:
                log_event(f"🎬 [StockMaster 숏폼] 주제 #{topic_id if topic_id else '자동 롤링'} 30초 완제품 즉시 렌더링 시작...", "info")
                from brands.stock.stock_shorts_scheduler import StockShortsScheduler
                scheduler = StockShortsScheduler()
                res = scheduler.trigger_now(topic_id=topic_id)
                rec = res.get("run_record", {})
                log_event(
                    f"🎉 [StockMaster 숏폼 완성!]\n"
                    f"  - 🏷️ 주제: #{rec.get('topic_id')} {rec.get('topic_title')}\n"
                    f"  - ⏱️ 실측 길이: {rec.get('duration')}s\n"
                    f"  - 💾 용량: {rec.get('file_size_mb')} MB\n"
                    f"  - 📁 파일: {rec.get('output_mp4')}\n"
                    f"  - ⏭️ 다음 순차 롤링 예정: #{res.get('next_topic_id')}",
                    "success"
                )
            except Exception as ex:
                import traceback
                err_detail = traceback.format_exc()
                log_event(f"❌ [StockMaster 숏폼 생성 실패] {ex}\n{err_detail}", "error")

        threading.Thread(target=_worker, daemon=True).start()
        self._set_headers("application/json")
        self.wfile.write(json.dumps({
            "success": True,
            "message": f"🚀 [StockMaster] 주제 #{topic_id if topic_id else '자동 롤링'} 숏폼 생성이 백그라운드에서 시작되었습니다."
        }, ensure_ascii=False).encode("utf-8"))

    def _handle_post_stock_shorts_config(self, payload: dict):
        """📈 StockMaster AI 30초 퀀트 숏폼 스케줄 설정 변경"""
        try:
            from brands.stock.stock_shorts_scheduler import StockShortsScheduler
            scheduler = StockShortsScheduler()
            updated_status = scheduler.update_config(payload)
            log_event("⚙️ [StockMaster 숏폼] 스케줄러 설정이 저장되었습니다.", "success")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(updated_status, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._set_headers("application/json", 500)
            self.wfile.write(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))

    def _handle_post_stock_shorts_toggle_daemon(self, payload: dict):
        """📈 StockMaster AI 30초 퀀트 숏폼 무인 데몬 ON/OFF 토글"""
        try:
            from brands.stock.stock_shorts_scheduler import StockShortsScheduler
            scheduler = StockShortsScheduler()
            enabled = payload.get("enabled", True)
            updated_status = scheduler.update_config({"daemon_enabled": enabled})
            status_text = "가동" if enabled else "정지"
            log_event(f"⚡ [StockMaster 숏폼] 24/7 무인 스케줄러가 {status_text}되었습니다.", "info")
            self._set_headers("application/json")
            self.wfile.write(json.dumps(updated_status, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._set_headers("application/json", 500)
            self.wfile.write(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))

def run_server(port: int = 8080):
    port = int(os.environ.get("PORT", port))
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

    # 🛡️ [대시보드 UI 스위치 연동 안전 대기 모드]
    # 서버 기동 시 임의 자동 가동을 방지하고 기본 OFF(대기) 상태 유지.
    # 사용자가 대시보드 화면(http://localhost:8080)에서 [가동/ON] 스위치를 켰을 때만 정시 스케줄러가 활성화됩니다.
    print("🛡️ [대시보드 제어 대기 모드] 3대 브랜드(Aura, 보험, 주식) 무인 스케줄러가 대기 모드로 시작되었습니다.")
    print("  • 웹 대시보드(http://localhost:8080)에서 [24/7 가동 ON] 스위치를 누르면 정시 스케줄러가 자율 가동됩니다.\n")

    # 🌐 서버 준비 완료 직후 브라우저 자동 오픈 (에러 없는 1초 컷 즉시 실행)
    def _open_browser():
        time.sleep(0.3)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
    threading.Thread(target=_open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_server()

