# -*- coding: utf-8 -*-
"""
[독립 레고 블록] EasyTax YouTube Behavior Bot (💰 유튜브 쇼츠 30분 스텔스 인간 행동 봇)
===================================================================================================
- 브랜드: Korea Tax Refund Service (KTRS 세금 환급)
- 역할:
  1. API 업로드 코드는 0% 배제! 오직 실제 사람처럼 유튜브 쇼츠 피드에 들어가 아무거나 시청, 체류, 댓글 탐색, 좋아요만 전담
  2. 하루 총 30분을 4개 일과 시간(09:15, 13:15, 16:45, 22:45)으로 분할 실행 (KMarket과 15분 시차 분산)
  3. [사용자 핵심 원칙] 특정 비즈니스 주제(자취/세금 등)를 검색할 필요 없이, 실제 사람처럼 추천 쇼츠 피드 진입 후 아무 영상이나 자연스럽게 시청
  4. 매 세션마다 실제 '좋아요' 2~3회 실행 (자연스러운 베지어 마우스 이동 + 텀)
  5. 고가치 시청자 신호: 쇼츠 1편당 16~35초 고체류 완시청 + 댓글창 열람 후 닫기
  6. Gemini AI 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저, API 비용 0원)
  7. 구글 계정 신뢰 지수(Creator Trust Score)를 극대화하여 나중에 숏폼 업로드 시 알고리즘 0회 노출 방지
- 원칙: Rule 1 (브랜드별 완전 독립 모듈화), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import time
import json
import random
import logging
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str

logger = logging.getLogger("EasyTaxYouTubeBehaviorBot")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# 💡 대중적인 인기/유머/일상 탐색 키워드 (검색 시뮬레이션용)
_POPULAR_TREND_KEYWORDS = [
    "인기 쇼츠",
    "오늘의 꿀잼 영상",
    "귀여운 강아지 고양이",
    "핫플 맛집 먹방 쇼츠",
    "힐링 여행 풍경",
    "일상 공감 꿀잼 숏폼",
    "초간단 맛있는 요리",
    "재미있는 챌린지"
]


def _bezier_points(start: tuple, end: tuple, steps: int = 15) -> List[tuple]:
    """자연스러운 인간 마우스 베지어 이동 곡선"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) / 2 + random.randint(-30, 30)
    cy = (sy + ey) / 2 + random.randint(-25, 25)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class EasyTaxYouTubeBehaviorBot:
    """💰 Korea Tax Refund Service (KTRS 세금 환급) 전용 유튜브 쇼츠 30분 스텔스 인간 행동 봇"""

    # KMarket과 15분 시차 분산 실행
    SLOTS = [
        {"id": "morning", "time": "09:15", "start_h": 9, "start_m": 15, "end_h": 12, "end_m": 59, "name": "🌅 아침 출근길 숏폼 (7분)", "target_min": 7},
        {"id": "lunch", "time": "13:15", "start_h": 13, "start_m": 15, "end_h": 16, "end_m": 29, "name": "🍱 점심시간 숏폼 (8분)", "target_min": 8},
        {"id": "afternoon", "time": "16:45", "start_h": 16, "start_m": 45, "end_h": 22, "end_m": 29, "name": "☕ 오후 휴식 숏폼 (7분)", "target_min": 7},
        {"id": "night", "time": "22:45", "start_h": 22, "start_m": 45, "end_h": 23, "end_m": 59, "name": "🌙 야간 침대 숏폼 (8분)", "target_min": 8}
    ]

    def __init__(self, headless: bool = True):
        self.brand = "easytax"
        self.brand_name = "💰 Korea Tax Refund Service (KTRS 세금 환급)"
        self.headless = headless
        self.youtube_profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.youtube_profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_human_routine_history.json"

    def check_saved_login_session(self) -> bool:
        """로컬 영구 세션 파일에 구글/유튜브 인증 토큰(LOGIN_INFO, SID 등)이 존재하는지 검증"""
        if not self.session_file.exists():
            return False
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
                cookies = sdata if isinstance(sdata, list) else sdata.get("cookies", [])
                auth_cookies = [c.get("name") for c in cookies if c.get("name") in ["LOGIN_INFO", "SID", "SSID", "SAPISID", "HSID"]]
                return len(auth_cookies) > 0
        except Exception:
            return False

    async def verify_page_login(self, page) -> bool:
        """실제 브라우저 화면에서 유튜브 로그인 여부 실시간 확인"""
        try:
            await asyncio.sleep(2.0)
            # 1. 로그인 상태 표시 요소 확인 (우측 상단 아바타 버튼 등)
            avatar = await page.query_selector("button#avatar-btn, ytd-topbar-menu-button-renderer #avatar-btn, img#avatar, button[aria-label*='계정'], button[aria-label*='Account'], ytd-user-avatar-renderer")
            if avatar:
                return True
            
            # 2. 미로그인 상태 표시 ("로그인" 버튼 등)
            signin_btn = await page.query_selector("a[href*='accounts.google.com/ServiceLogin'], ytd-button-renderer a[aria-label*='로그인'], a[aria-label*='Sign in'], button[aria-label*='로그인']")
            if signin_btn:
                return False

            # 3. 브라우저 컨텍스트 내 구글/유튜브 쿠키 확인
            cookies = await page.context.cookies()
            has_auth = any(c.get("name") in ["LOGIN_INFO", "SID", "SSID", "SAPISID"] for c in cookies)
            return has_auth
        except Exception as e:
            logger.debug(f"로그인 상태 확인 예외: {e}")
            return False

    async def rotate_to_next_channel(self, page) -> Optional[str]:
        """8대 브랜드 채널 순환 자동 전환기 (YouTube Channel Switcher)"""
        rotation_file = CURRENT_DIR / "youtube_channel_rotation.json"
        curr_idx = 0
        if rotation_file.exists():
            try:
                with open(rotation_file, "r", encoding="utf-8") as f:
                    curr_idx = json.load(f).get("current_index", 0)
            except Exception:
                curr_idx = 0

        try:
            logger.info("🔄 [Channel Rotator] 유튜브 채널 전환 페이지(https://www.youtube.com/channel_switcher) 접속 중...")
            await page.goto("https://www.youtube.com/channel_switcher", wait_until="domcontentloaded", timeout=35000)
            await asyncio.sleep(2.5)

            items = await page.query_selector_all("ytd-account-item-renderer, a[href*='channel_switcher']")
            if not items:
                logger.info("ℹ️ 채널 전환 목록이 단일 채널이거나 비어있어 현재 활성 채널로 진행합니다.")
                return None

            brand_items = []
            for it in items:
                t = (await it.inner_text()).strip()
                name = t.split("\n")[0].strip()
                if name:
                    brand_items.append((it, name))

            # 개인 계정(김홍일) 필터링하여 8개 외국인 세금 환급 채널만 순환
            target_pool = [b for b in brand_items if "김홍일" not in b[1]]
            if not target_pool:
                target_pool = brand_items

            selected_idx = curr_idx % len(target_pool)
            target_el, target_name = target_pool[selected_idx]

            logger.info(f"✨ [{self.brand_name}] 8개 채널 중 #{selected_idx + 1}/{len(target_pool)} '{target_name}'(으)로 전환 클릭...")
            await target_el.click()
            await asyncio.sleep(3.5)

            next_idx = (selected_idx + 1) % len(target_pool)
            with open(rotation_file, "w", encoding="utf-8") as f:
                json.dump({
                    "current_index": next_idx,
                    "last_channel_name": target_name,
                    "total_channels": len(target_pool),
                    "updated_at": get_now_kst_str()
                }, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ [{self.brand_name}] '{target_name}' 채널 전환 완료! (다음 세션 순환 예약: #{next_idx + 1})")
            return target_name
        except Exception as e:
            logger.warning(f"채널 자동 순환 전환 예외 (기본 채널 유지): {e}")
            return None

    def is_sleep_time(self) -> bool:
        """심야 취침 모드 (00:00 ~ 07:30 KST 계정 안전 휴식)"""
        now = datetime.now()
        return (now.hour == 0 and now.minute < 30) or (0 <= now.hour < 7) or (now.hour == 7 and now.minute < 30)

    async def _simulate_youtube_shorts_session(self, page, duration_sec: int, target_likes: int = 2) -> Dict[str, Any]:
        """유튜브 쇼츠 피드 진입, 아무 영상이나 자연스럽게 시청/체류, 댓글 열람 및 좋아요"""
        result = {"shorts_watched": 0, "likes": 0, "comments_inspected": 0, "platform": "youtube_shorts"}
        start_t = time.time()

        try:
            # 70% 확률로 쇼츠 추천 피드 직접 진입 (실제 사람들이 가장 많이 하는 방식)
            # 30% 확률로 대중적 인기 키워드 검색 후 진입
            if random.random() < 0.3:
                kw = random.choice(_POPULAR_TREND_KEYWORDS)
                logger.info(f"▶ [EasyTax YouTubeBot] 대중적 인기 쇼츠 검색 진입: '{kw}'")
                search_url = f"https://www.youtube.com/results?search_query={kw}&sp=CAISAhAB"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(random.uniform(3.0, 5.0))
                shorts_entry = await page.query_selector("ytd-reel-item-renderer, a[href*='/shorts/']")
                if shorts_entry:
                    await shorts_entry.click()
                    await asyncio.sleep(random.uniform(2.5, 4.0))
                else:
                    await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
            else:
                logger.info("▶ [EasyTax YouTubeBot] 유튜브 쇼츠 메인 추천 피드(https://www.youtube.com/shorts) 직접 진입")
                await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)

            await asyncio.sleep(random.uniform(2.5, 4.5))

            while (time.time() - start_t) < duration_sec:
                # 1. 나오는 숏폼 영상 아무거나 완시청 체류 (16 ~ 35초)
                watch_time = random.uniform(16.0, 35.0)
                logger.info(f"👀 [EasyTax YouTubeBot] 쇼츠 #{result['shorts_watched'] + 1} 영상 시청 중... ({watch_time:.1f}초 체류)")
                await asyncio.sleep(watch_time)
                result["shorts_watched"] += 1

                # 2. 호기심 댓글창 열람 시뮬레이션 (25% 확률)
                if random.random() < 0.25:
                    try:
                        comment_btn = await page.query_selector("button#comments-button, button[aria-label*='댓글'], ytd-comments-entry-point-header-renderer")
                        if comment_btn:
                            await comment_btn.click()
                            result["comments_inspected"] += 1
                            logger.info("💬 [EasyTax YouTubeBot] 시청자 댓글창 열람 체류 (5초)...")
                            await asyncio.sleep(random.uniform(4.0, 7.0))
                            close_comment = await page.query_selector("button#close-button, ytd-engagement-panel-section-list-renderer button[aria-label*='닫기']")
                            if close_comment:
                                await close_comment.click()
                            else:
                                await page.keyboard.press("Escape")
                            await asyncio.sleep(1.0)
                    except Exception:
                        pass

                # 3. 자연스러운 좋아요 클릭 (세션당 2~3회 목표)
                if result["likes"] < target_likes and (time.time() - start_t) > 15:
                    try:
                        like_buttons = await page.query_selector_all("button[aria-label*='좋아요'], button[aria-label*='like this'], ytd-like-button-renderer button")
                        for l_btn in like_buttons:
                            box = await l_btn.bounding_box()
                            if box and box["width"] > 0 and box["height"] > 0:
                                btn_x = box["x"] + box["width"] / 2
                                btn_y = box["y"] + box["height"] / 2
                                # 베지어 마우스 이동
                                p_start = (random.randint(200, 500), random.randint(300, 600))
                                for pt in _bezier_points(p_start, (btn_x, btn_y), steps=12):
                                    await page.mouse.move(pt[0], pt[1])
                                    await asyncio.sleep(0.015)
                                await asyncio.sleep(random.uniform(0.6, 1.2))
                                await page.mouse.click(btn_x, btn_y)
                                result["likes"] += 1
                                logger.info(f"💖 [EasyTax YouTubeBot] 유튜브 쇼츠 실제 '좋아요' 클릭 완료! (세션 누적: {result['likes']}/{target_likes}회)")
                                await asyncio.sleep(random.uniform(2.5, 4.5))
                                break
                    except Exception as le:
                        logger.debug(f"좋아요 시도 스킵: {le}")

                # 4. 다음 숏폼으로 스크롤 (PageDown)
                logger.info("⏬ [EasyTax YouTubeBot] 다음 추천 영상으로 스크롤 넘김...")
                await page.keyboard.press("PageDown")
                await asyncio.sleep(random.uniform(2.0, 3.8))

        except Exception as e:
            logger.warning(f"유튜브 숏폼 세션 예외: {e}")

        return result

    async def execute_slot_session_async(self, slot: Dict[str, Any]) -> Dict[str, Any]:
        """지정된 세션 실행 (쿠키 100% 주입 + 목표 좋아요 2~3회)"""
        slot_name = slot.get("name", "유튜브 인간 행동 세션")
        target_sec = slot.get("target_min", 7) * 60
        target_likes = random.randint(2, 3)

        logger.info("=" * 70)
        logger.info(f"🎬 [EasyTax 유튜브 30분 스텔스 봇] 시작: {slot_name} (목표: {slot.get('target_min')}분 | 목표 좋아요: {target_likes}회)")
        logger.info("=" * 70)

        session_start = time.time()
        ua = random.choice(_UA_POOL)
        summary = {
            "timestamp": get_now_kst_str(),
            "slot_id": slot.get("id"),
            "slot_name": slot_name,
            "target_min": slot.get("target_min"),
            "target_likes": target_likes,
            "actual_sec": 0,
            "likes_given": 0,
            "shorts_watched": 0,
            "comments_inspected": 0,
            "status": "success",
            "gemini_calls": 0,
            "brand": self.brand
        }

        # 🚨 [하드 락 1단계] 로컬 영구 세션 파일 존재 및 로그인 토큰 검증
        if not self.check_saved_login_session():
            logger.error("=" * 75)
            logger.error(f"🚨 [{self.brand_name}] 유튜브 계정 미로그인 상태 감지! (동작 강제 차단)")
            logger.error(f"   로그인하지 않고 유튜브를 보면 구글 알고리즘이 우리 브랜드 채널 활동으로 인식하지 않으며,")
            logger.error(f"   좋아요 클릭 시 '로그인' 팝업이 떠서 계정 워밍업 효과가 0%가 됩니다.")
            logger.error(f"👉 해결 방법: 바탕화면의 '[1회연동]_EasyTax_유튜브_영구로그인.bat'을 실행하여")
            logger.error(f"   KTRS 세금 환급 구글 계정으로 딱 1회만 로그인해 주시면 영구적으로 로그인 상태가 유지됩니다!")
            logger.error("=" * 75)
            summary["status"] = "login_required"
            summary["error"] = "유튜브 구글 계정 로그인이 필수입니다. 바탕화면의 [1회연동] 도구를 먼저 실행해 주세요."
            self._record_history(summary)
            return summary

        from core.engine.browser_guard import async_browser_lock, clean_browser_profile_locks, get_safe_browser_args

        clean_browser_profile_locks(self.youtube_profile_dir)

        async with async_browser_lock(f"EasyTax 유튜브 세션 ({slot_name})"):
            async with async_playwright() as p:
                try:
                    ctx_yt = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.youtube_profile_dir),
                        headless=self.headless,
                        user_agent=ua,
                        viewport={"width": 1280, "height": 850},
                        args=get_safe_browser_args()
                    )

                    # youtube_session.json 쿠키 주입
                    if self.session_file.exists():
                        try:
                            with open(self.session_file, "r", encoding="utf-8") as sf:
                                sdata = json.load(sf)
                                cookies = sdata if isinstance(sdata, list) else sdata.get("cookies", [])
                                if cookies:
                                    clean_cookies = []
                                    for c in cookies:
                                        c_item = {
                                            "name": c.get("name"),
                                            "value": c.get("value"),
                                            "domain": c.get("domain", ".youtube.com"),
                                            "path": c.get("path", "/")
                                        }
                                        if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                                            c_item["sameSite"] = c["sameSite"]
                                        if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                                            c_item["secure"] = True
                                        clean_cookies.append(c_item)
                                    await ctx_yt.add_cookies(clean_cookies)
                                    logger.info(f"🍪 [EasyTax YouTubeBot] 유튜브 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                        except Exception as ce:
                            logger.debug(f"유튜브 쿠키 주입 예외: {ce}")

                    page_yt = ctx_yt.pages[0] if ctx_yt.pages else await ctx_yt.new_page()
                    await page_yt.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                    # 🚨 [하드 락 2단계] 실제 브라우저 화면에서 유튜브 접속 및 로그인 상태 검증
                    logger.info("🔐 [EasyTax YouTubeBot] 유튜브 접속 및 계정 로그인 상태 실시간 검증 중...")
                    await page_yt.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
                    is_logged_in = await self.verify_page_login(page_yt)

                    if not is_logged_in:
                        logger.error("=" * 75)
                        logger.error(f"🚨 [{self.brand_name}] 브라우저 실제 화면에서 미로그인 상태가 확인되었습니다!")
                        logger.error(f"   로그인되지 않은 상태에서의 시청은 채널 점수 축적에 무효하므로 즉시 중단합니다.")
                        logger.error(f"👉 해결 방법: 바탕화면의 '[1회연동]_EasyTax_유튜브_영구로그인.bat'을 실행해 주세요.")
                        logger.error("=" * 75)
                        summary["status"] = "login_required"
                        summary["error"] = "실제 브라우저 미로그인 감지. 1회 연동 재실행 필요"
                        await ctx_yt.close()
                        self._record_history(summary)
                        return summary

                    logger.info("✅ [EasyTax YouTubeBot] 구글/유튜브 공식 계정 정상 로그인 확인 완료! 스텔스 인간 행동을 시작합니다.")

                    # 🔄 8대 브랜드 채널 순환 자동 전환
                    active_ch = await self.rotate_to_next_channel(page_yt)
                    if active_ch:
                        summary["active_channel"] = active_ch

                    yt_res = await self._simulate_youtube_shorts_session(page_yt, target_sec, target_likes=target_likes)
                    summary["shorts_watched"] = yt_res.get("shorts_watched", 0)
                    summary["likes_given"] = yt_res.get("likes", 0)
                    summary["comments_inspected"] = yt_res.get("comments_inspected", 0)

                    await ctx_yt.close()
                except Exception as e:
                    logger.warning(f"유튜브 브라우저 세션 오류: {e}")
                    summary["status"] = f"error: {e}"

        elapsed_sec = int(time.time() - session_start)
        summary["actual_sec"] = elapsed_sec
        logger.info(f"✅ [EasyTax 유튜브 스텔스 세션 완료] {slot_name} 체류: {elapsed_sec//60}분 {elapsed_sec%60}초 | 쇼츠 시청: {summary['shorts_watched']}편 | 좋아요: {summary['likes_given']}회 | 제미나이: 0회")
        self._record_history(summary)
        return summary

    def execute_slot_session(self, slot_id: str) -> Dict[str, Any]:
        """동기 호출 래퍼"""
        matched = next((s for s in self.SLOTS if s["id"] == slot_id), None)
        if not matched:
            matched = self.SLOTS[0]
        return asyncio.run(self.execute_slot_session_async(matched))

    def _record_history(self, summary: Dict[str, Any]):
        """일일 유튜브 인간 루틴 이력 디스크 저장"""
        try:
            records = []
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(summary)
            records = records[-100:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"유튜브 루틴 이력 저장 실패: {e}")

    def get_today_stats(self) -> Dict[str, Any]:
        """오늘의 유튜브 스텔스 누적 통계"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        total_sec = 0
        total_likes = 0
        total_watched = 0
        sessions_done = 0

        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                for r in records:
                    if r.get("timestamp", "").startswith(today_str):
                        total_sec += r.get("actual_sec", 0)
                        total_likes += r.get("likes_given", 0)
                        total_watched += r.get("shorts_watched", 0)
                        sessions_done += 1
            except Exception:
                pass

        return {
            "date": today_str,
            "sessions_done": sessions_done,
            "total_min": round(total_sec / 60, 1),
            "total_likes": total_likes,
            "total_watched": total_watched,
            "gemini_calls": 0,
            "target_daily_min": 30
        }

    def execute_single_session(self, duration_sec: int = 30, target_likes: int = 1) -> Dict[str, Any]:
        """대시보드 1초 즉시 실행용 유튜브 세션"""
        quick_slot = {
            "id": "quick_youtube",
            "time": "now",
            "name": "⚡ 대시보드 1초 즉시 유튜브 세션",
            "target_min": max(0.5, duration_sec / 60)
        }
        try:
            res = asyncio.run(self.execute_slot_session_async(quick_slot))
            if res.get("status") == "login_required":
                return {
                    "status": "login_required",
                    "message": res.get("error", "유튜브 구글 계정 로그인이 필요합니다. 바탕화면의 [1회연동] 도구를 먼저 실행해 주세요."),
                    "brand": self.brand
                }
            return {
                "status": res.get("status", "success"),
                "duration_sec": res.get("actual_sec", duration_sec),
                "shorts_watched": res.get("shorts_watched", 1),
                "likes_given": res.get("likes_given", target_likes),
                "brand": self.brand
            }
        except Exception as e:
            logger.error(f"❌ 1회 유튜브 세션 실패: {e}")
            return {"status": "error", "message": str(e), "duration_sec": 0, "shorts_watched": 0, "likes_given": 0}


class EasyTaxYouTubeBehaviorScheduler:
    """💰 KTRS 세금 환급 유튜브 24/7 백그라운드 무인 스케줄러 데몬"""

    def __init__(self):
        self.bot = EasyTaxYouTubeBehaviorBot(headless=True)
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._executed_today = set()

    def execute_single_session(self, duration_sec: int = 30) -> Dict[str, Any]:
        """단발 1회 실행"""
        return self.bot.execute_single_session(duration_sec=duration_sec)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="EasyTaxYouTubeBehaviorScheduler")
        self._thread.start()
        logger.info("🚀 [EasyTax YouTubeBehaviorScheduler] 24시간 무인 자율 데몬 백그라운드 기동 완료 (09:15, 13:15, 16:45, 22:45)")

    def _run_loop(self):
        while self.is_running:
            try:
                now = datetime.now()
                today_date = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                for slot in self.bot.SLOTS:
                    slot_id = slot["id"]
                    start_total = slot.get("start_h", 0) * 60 + slot.get("start_m", 0)
                    end_total = slot.get("end_h", 23) * 60 + slot.get("end_m", 59)
                    key = f"{today_date}_{slot_id}"

                    if start_total <= cur_min <= end_total and key not in self._executed_today:
                        logger.info(f"⏰ [EasyTax YouTube 스케줄 알람] {slot['name']} 골든타임 도달! 🚀 스텔스 세션 즉각 착수!")
                        self._executed_today.add(key)
                        self.bot.execute_slot_session(slot_id)

            except Exception as e:
                logger.warning(f"EasyTax 유튜브 스케줄러 루프 오류: {e}")

            time.sleep(25)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("\n" + "=" * 70)
    print("▶ [💰 Korea Tax Refund Service] 유튜브 쇼츠 30분 스텔스 인간 행동 봇 단독 테스트")
    print("=" * 70)
    bot = EasyTaxYouTubeBehaviorBot(headless=True)
    test_slot = {"id": "test", "time": "now", "name": "⚡ 1분 빠른 검증 세션", "target_min": 1}
    res = asyncio.run(bot.execute_slot_session_async(test_slot))
    print(f"\n결과: {json.dumps(res, ensure_ascii=False, indent=2)}")
    print(f"오늘 통계: {bot.get_today_stats()}")