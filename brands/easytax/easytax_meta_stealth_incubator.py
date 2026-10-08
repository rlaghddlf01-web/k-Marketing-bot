# -*- coding: utf-8 -*-
"""
[독립 레고 블록] EasyTax Meta Stealth Incubator (💰 KTRS 세금 환급 전용 인스타그램 스텔스 인큐베이터)
==============================================================================================
- 브랜드: 💰 Korea Tax Refund Service (KTRS 세금 환급)
- 역할:
  1. API 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저, 비용 0원)
  2. 안티-핑거프린팅 주입 (navigator.webdriver 차단, window.chrome 모사)
  3. 인간 친화형 3차 베지어 곡선(Bézier Curve) 마우스 이동 및 불규칙 휠 스크롤
  4. 인스타그램 탐색 탭(Explore) 진입 후 3~8.5초 자연스러운 정독 체류
  5. 실제 하트(좋아요) 1~2회 클릭으로 진성 활성 사용자 지수(Trust Score) 극대화
  6. 주제 편향 방지: 일반 관심사(유머/맛집/힐링/동물 50%) + 세무/환급/외국인 꿀팁(50%)
  7. 심야 취침 모드 (00:00 ~ 07:00 KST): 계정 안전 휴식
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (품질 코딩), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import time
import json
import random
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import BASE_DIR, get_now_kst_str
except ImportError:
    BASE_DIR = PROJECT_ROOT
    def get_now_kst_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(fmt)

try:
    from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks
except ImportError:
    import contextlib
    @contextlib.asynccontextmanager
    async def async_browser_lock(name: str = ""):
        yield
    def get_safe_browser_args(headless: bool = True):
        return ["--disable-gpu", "--no-sandbox"]
    def clean_browser_profile_locks(p):
        pass

logger = logging.getLogger("EasyTaxMetaStealthIncubator")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# 🐶 일반 대중 관심사 키워드 (단일 주제 편향 방지 50%)
_GENERAL_HUMAN_KEYWORDS = [
    "귀여운 강아지 고양이 숏폼",
    "오늘의 꿀잼 릴스",
    "전국 숨은 맛집 투어",
    "힐링 여행 풍경",
    "직장인 공감 썰 숏폼",
    "요즘 뜨는 감성 카페",
    "퇴근길 일상 브이로그",
    "초간단 자취 요리 레시피"
]

# 💰 EasyTax 브랜드 & 외국인 근로자 관심사 키워드 (50%)
_EASYTAX_KEYWORDS = [
    "외국인 세금 환급 꿀팁",
    "연말정산 환급금 조회",
    "E-9 근로자 비자 혜택",
    "한국 종합소득세 환급",
    "외국인 근로자 전용 서비스",
    "KTRS 세금 환급",
    "외국인 비자 연장 서류",
    "한국 생활 정착 꿀팁"
]


def _bezier_points(start: tuple, end: tuple, steps: int = 15) -> List[tuple]:
    """인간 친화형 3차 베지어 곡선 마우스 이동 좌표 생성"""
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


class EasyTaxMetaStealthIncubator:
    """💰 KTRS 세금 환급 전용 메타(인스타그램) 계정 지수 스텔스 인큐베이터"""

    COUNTRIES = ["vi", "ne", "km", "id", "th", "mn", "my", "uz"]
    COUNTRY_LABELS = {
        "vi": "베트남 🇻🇳",
        "ne": "네팔 🇳🇵",
        "km": "캄보디아 🇰🇭",
        "id": "인도네시아 🇮🇩",
        "th": "태국 🇹🇭",
        "mn": "몽골 🇲🇳",
        "my": "미얀마 🇲🇲",
        "uz": "우즈베키스탄 🇺🇿"
    }

    def __init__(self, headless: bool = True):
        self.brand = "easytax"
        self.brand_name = "💰 Korea Tax Refund Service (KTRS 세금 환급)"
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "meta_chrome_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = CURRENT_DIR / "meta_session.json"
        self.history_file = CURRENT_DIR / "meta_stealth_history.json"
        self.rotation_file = CURRENT_DIR / "meta_account_rotation.json"

    def get_next_rotation_country(self) -> str:
        """8개 국가 계정을 순차적으로 교대 선택"""
        state = {"current_index": 0, "last_country": "vi"}
        if self.rotation_file.exists():
            try:
                with open(self.rotation_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                pass
        
        idx = state.get("current_index", 0)
        target_code = self.COUNTRIES[idx % len(self.COUNTRIES)]
        
        state["current_index"] = (idx + 1) % len(self.COUNTRIES)
        state["last_country"] = target_code
        state["updated_at"] = get_now_kst_str()
        try:
            with open(self.rotation_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
            
        return target_code

    def resolve_target_profile(self, nationality_code: str):
        """지정된 국가의 독립 프로필 및 세션 파일 경로 반환 (미연동 시 기본 프로필 폴백)"""
        p_dir = CURRENT_DIR / "profiles" / nationality_code / "meta_chrome_profile"
        s_file = CURRENT_DIR / "profiles" / nationality_code / "meta_session.json"
        if s_file.exists():
            return p_dir, s_file
        # 폴백: 기본 프로필
        return self.profile_dir, self.session_file

    def has_isolated_profile(self, nationality_code: str) -> bool:
        """해당 국가의 전용 독립 프로필/세션 존재 여부 (방식 ① 완벽 격리 여부)"""
        s_file = CURRENT_DIR / "profiles" / nationality_code / "meta_session.json"
        return s_file.exists()

    def is_available(self, nationality_code: Optional[str] = None) -> bool:
        """메타 영구 세션 또는 프로필 존재 여부 확인"""
        if nationality_code:
            _, s_file = self.resolve_target_profile(nationality_code)
            return s_file.exists()
        if self.session_file.exists():
            return True
        for c in self.COUNTRIES:
            if (CURRENT_DIR / "profiles" / c / "meta_session.json").exists():
                return True
        return False

    def is_night_sleep_time(self) -> bool:
        """심야 취침 모드 (00:00 ~ 07:00 KST) 검증"""
        now_h = datetime.now().hour
        return 0 <= now_h < 7

    async def run_warmup_session_async(self, nationality_code: Optional[str] = None, duration_seconds: int = 45, target_likes: int = 1) -> Dict[str, Any]:
        """Playwright 기반 인스타그램 인간 행동 웜업 세션 실행 (8개국 교대)"""
        if self.is_night_sleep_time():
            logger.info("🌙 [EasyTax Meta-Stealth] 심야 취침 모드 (00~07시): 인간 행동 웜업 생략 (계정 안전 휴식)")
            return {"status": "skipped", "reason": "night_sleep_mode", "brand": self.brand}

        target_country = nationality_code or self.get_next_rotation_country()
        country_label = self.COUNTRY_LABELS.get(target_country, target_country.upper())
        active_profile_dir, active_session_file = self.resolve_target_profile(target_country)
        clean_browser_profile_locks(active_profile_dir)

        ua = random.choice(_UA_POOL)
        pool = _GENERAL_HUMAN_KEYWORDS if random.random() < 0.5 else _EASYTAX_KEYWORDS
        target_kw = random.choice(pool)
        logger.info(f"🔄 [EasyTax 8대 계정 교대] 타깃 국가: {country_label} ({target_country.upper()}) | 관심사: '{target_kw}' ({duration_seconds}초)")

        result = {
            "timestamp": get_now_kst_str(),
            "nationality_code": target_country,
            "country_label": country_label,
            "keyword": target_kw,
            "posts_viewed": 0,
            "likes_given": 0,
            "duration": 0,
            "status": "success",
            "brand": self.brand
        }

        start_time = time.time()
        async with async_browser_lock(f"easytax_meta_stealth_{target_country}"):
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(active_profile_dir),
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1280, "height": 850},
                    args=get_safe_browser_args() + [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-infobars"
                    ]
                )

                # 영구 세션 쿠키 주입
                if active_session_file.exists():
                    try:
                        with open(active_session_file, "r", encoding="utf-8") as f:
                            raw_cookies = json.load(f).get("cookies", [])
                            clean_cookies = []
                            for c in raw_cookies:
                                c_item = {
                                    "name": c.get("name"),
                                    "value": c.get("value"),
                                    "domain": c.get("domain", ".instagram.com"),
                                    "path": c.get("path", "/")
                                }
                                if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                                    c_item["sameSite"] = c["sameSite"]
                                if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                                    c_item["secure"] = True
                                clean_cookies.append(c_item)
                            await context.add_cookies(clean_cookies)
                    except Exception as ce:
                        logger.debug(f"쿠키 주입 알림: {ce}")

                try:
                    page = context.pages[0] if context.pages else await context.new_page()

                    # 1. 안티 핑거프린팅 스크립트 주입
                    await page.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        window.chrome = { runtime: {} };
                    """)

                    # 2. 인스타그램 탐색 탭 진입
                    await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(random.uniform(3.5, 6.0))

                    # 팝업 / 알림 모달 닫기
                    try:
                        await page.keyboard.press("Escape")
                        close_btn = await page.query_selector('button:has-text("나중에 하기"), button:has-text("Not Now"), svg[aria-label="닫기"], svg[aria-label="Close"]')
                        if close_btn:
                            await close_btn.click()
                    except Exception:
                        pass

                    # 3. 인간 휠 스크롤 및 피드 정독 체류
                    while (time.time() - start_time) < duration_seconds:
                        scroll_delta = random.randint(350, 750)
                        await page.mouse.wheel(0, scroll_delta)
                        result["posts_viewed"] += 1

                        # 자연스러운 마우스 이동 시뮬레이션
                        p_start = (random.randint(150, 400), random.randint(200, 450))
                        p_end = (random.randint(450, 800), random.randint(350, 650))
                        points = _bezier_points(p_start, p_end, steps=12)
                        for pt in points:
                            await page.mouse.move(pt[0], pt[1])
                            await asyncio.sleep(0.015)

                        dwell = random.uniform(3.5, 8.0)
                        logger.info(f"📸 [EasyTax InstagramBot] 탐색 피드 스크롤({scroll_delta}px) 후 게시물 #{result['posts_viewed']} 정독 체류 ({dwell:.1f}초)...")
                        await asyncio.sleep(dwell)

                        # 4. [로그인 계정] 자연스러운 좋아요 1회 클릭 시뮬레이션
                        if result["likes_given"] < target_likes and (time.time() - start_time) > 10:
                            try:
                                like_btns = await page.query_selector_all('svg[aria-label="좋아요"], svg[aria-label="Like"]')
                                if like_btns:
                                    idx = min(result["likes_given"], len(like_btns) - 1)
                                    target_btn = like_btns[idx]
                                    box = await target_btn.bounding_box()
                                    if box:
                                        btn_x = box["x"] + box["width"] / 2
                                        btn_y = box["y"] + box["height"] / 2
                                        like_points = _bezier_points(p_end, (btn_x, btn_y), steps=15)
                                        for pt in like_points:
                                            await page.mouse.move(pt[0], pt[1])
                                            await asyncio.sleep(0.02)
                                        await asyncio.sleep(random.uniform(0.6, 1.3))
                                        await page.mouse.click(btn_x, btn_y)
                                        result["likes_given"] += 1
                                        logger.info(f"💖 [EasyTax Meta-Stealth] 실제 인스타그램 게시물 '좋아요' 클릭 성공! (누적: {result['likes_given']}회)")
                                        await asyncio.sleep(random.uniform(3.0, 5.0))
                            except Exception as le:
                                logger.debug(f"좋아요 인터랙션 생략: {le}")

                    result["duration"] = int(time.time() - start_time)
                    logger.info(f"✅ [EasyTax Meta-Stealth] 인간 웜업 완료 (탐색: {result['posts_viewed']}회, 좋아요: {result['likes_given']}회, 체류: {result['duration']}초)")
                    self._record_history(result)

                except Exception as e:
                    logger.warning(f"⚠️ [EasyTax Meta-Stealth] 웜업 세션 진행 경고: {e}")
                    result["status"] = "partial_success"
                    result["duration"] = int(time.time() - start_time)
                finally:
                    # 5. [롤링 세션 하트비트] 최신 갱신된 인증 쿠키 영구 저장 (로그인 풀림 원천 방지)
                    try:
                        fresh_cookies = await context.cookies()
                        if fresh_cookies and any(c.get("name") in ["sessionid", "ds_user_id"] for c in fresh_cookies):
                            with open(active_session_file, "w", encoding="utf-8") as f:
                                json.dump({"cookies": fresh_cookies, "updated_at": get_now_kst_str()}, f, ensure_ascii=False, indent=2)
                            logger.debug(f"🍪 [EasyTax] 최신 세션 쿠키 {len(fresh_cookies)}개 자동 갱신 완료")
                    except Exception:
                        pass
                    await context.close()

        return result

    def run_warmup_session(self, nationality_code: Optional[str] = None, duration_seconds: int = 45, target_likes: int = 1) -> Dict[str, Any]:
        """동기 호출 인터페이스 (8개국 교대 또는 특정 국가 지정)"""
        try:
            return asyncio.run(self.run_warmup_session_async(nationality_code=nationality_code, duration_seconds=duration_seconds, target_likes=target_likes))
        except Exception as e:
            logger.error(f"❌ [EasyTax Meta-Stealth] 웜업 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def _record_history(self, entry: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(entry)
        if len(history) > 30:
            history = history[-30:]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


if __name__ == "__main__":
    incubator = EasyTaxMetaStealthIncubator(headless=True)
    res = incubator.run_warmup_session()
    print(json.dumps(res, ensure_ascii=False, indent=2))
