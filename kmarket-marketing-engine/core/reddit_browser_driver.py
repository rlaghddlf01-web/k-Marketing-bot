"""
🌐 [Playwright 기반 무인 레딧 브라우저 드라이버 v2.0 — 2026.08 전면 재설계]
- 영구 프로필(Persistent Context) 방식으로 전환: 세션/쿠키/로컬스토리지 영구 유지
- 고급 Fingerprint 위장: Canvas/WebGL/UA 랜덤화, 뷰포트 변동
- Human-like 행동: 가변 타이핑, 오타 시뮬레이션, 베지어 마우스 이동, 관성 스크롤
- 업보트/스크롤/읽기 전용 메서드 추가 (유기적 활동 지원)
- token_v2 OAuth 오용 제거 → 영구 프로필 방식만 사용
"""

import os
import sys
import time
import json
import math
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import DATA_DIR

logger = logging.getLogger("RedditBrowserDriver")

# User-Agent 회전 풀 (5~10개, 실제 Chrome 최신 버전 기반)
_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]


def _bezier_points(start: tuple, end: tuple, steps: int = 20) -> List[tuple]:
    """베지어 곡선 기반 자연스러운 마우스 이동 경로 생성"""
    sx, sy = start
    ex, ey = end
    # 랜덤 제어점 (곡선이 살짝 휘어지도록)
    cx = (sx + ex) / 2 + random.randint(-80, 80)
    cy = (sy + ey) / 2 + random.randint(-60, 60)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class RedditBrowserDriver:
    """
    🌐 [Playwright 기반 무인 레딧 브라우저 드라이버 v2.0]
    - API 키 불필요: 영구 프로필(Persistent Context) 기반 100% 브라우저 자동화
    - 고급 fingerprint 위장 + human-like 행동 시뮬레이션
    - 업보트/스크롤/읽기/댓글 등 모든 유기적 활동 지원
    """
    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id
        self.profile_dir = DATA_DIR / "reddit_profiles" / service_id
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        # 세션별 UA 고정 (매 세션 새로 선택)
        self._session_ua = random.choice(_UA_POOL)
        # 뷰포트 랜덤 변동 (±50px)
        self._viewport = {
            "width": 1280 + random.randint(-50, 50),
            "height": 800 + random.randint(-30, 30)
        }

    # ──────────────────────────────────────────────
    # 🔧 Internal: Persistent Context 생성
    # ──────────────────────────────────────────────

    def _get_anti_fingerprint_scripts(self) -> str:
        """고급 fingerprint 위장 JS (navigator.webdriver + canvas + WebGL + plugins)"""
        return """
            // 1. navigator.webdriver 숨기기
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };

            // 2. Plugins 위장 (빈 배열이면 봇으로 판별)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin' }
                ]
            });

            // 3. Languages 위장
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'ko'] });

            // 4. Canvas fingerprint 랜덤화 (미세 노이즈 주입)
            const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const imgData = ctx.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imgData.data.length; i += 4) {
                        imgData.data[i] = imgData.data[i] ^ (Math.random() > 0.99 ? 1 : 0);
                    }
                    ctx.putImageData(imgData, 0, 0);
                }
                return origToDataURL.apply(this, arguments);
            };

            // 5. WebGL vendor/renderer 위장
            const getParam = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {
                if (param === 37445) return 'Intel Inc.';
                if (param === 37446) return 'Intel Iris OpenGL Engine';
                return getParam.apply(this, arguments);
            };
        """

    def _create_persistent_context(self, playwright_instance, headless: bool = True):
        """영구 프로필 기반 브라우저 컨텍스트 생성 (세션/쿠키 영구 보존)"""
        context = playwright_instance.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
            ],
            ignore_default_args=["--enable-automation"],
            user_agent=self._session_ua,
            viewport=self._viewport,
            locale="en-US",
            timezone_id="Asia/Seoul",
        )
        # 모든 새 페이지에 anti-fingerprint 스크립트 자동 주입
        for page in context.pages:
            page.add_init_script(self._get_anti_fingerprint_scripts())
        context.on("page", lambda p: p.add_init_script(self._get_anti_fingerprint_scripts()))
        return context

    # ──────────────────────────────────────────────
    # 🖱️ Human-like 행동 시뮬레이션
    # ──────────────────────────────────────────────

    def _human_mouse_move(self, page, target_x: int, target_y: int):
        """베지어 곡선 기반 자연스러운 마우스 이동"""
        try:
            # 현재 마우스 위치 추정 (뷰포트 중앙에서 시작)
            current = (self._viewport["width"] // 2, self._viewport["height"] // 2)
            points = _bezier_points(current, (target_x, target_y), steps=random.randint(12, 25))
            for px, py in points:
                page.mouse.move(px, py)
                time.sleep(random.uniform(0.005, 0.02))
        except Exception:
            pass  # 마우스 이동 실패해도 계속 진행

    def _human_scroll(self, page, direction: str = "down", amount: int = 300):
        """관성이 있는 자연스러운 스크롤 (가속 → 감속)"""
        steps = random.randint(4, 8)
        total = 0
        for i in range(steps):
            # 가속-감속 커브 (사인파)
            progress = i / steps
            ratio = math.sin(progress * math.pi)
            delta = int(amount / steps * (0.5 + ratio))
            if direction == "up":
                delta = -delta
            page.mouse.wheel(0, delta)
            total += abs(delta)
            time.sleep(random.uniform(0.05, 0.15))
        return total

    def _human_type(self, page, text: str):
        """사람처럼 타이핑 (가변 속도 + 구두점 슬로우 + 오타 시뮬레이션)"""
        paragraphs = text.split("\n\n")
        for p_idx, para in enumerate(paragraphs):
            words = para.split(" ")
            for w_idx, word in enumerate(words):
                if w_idx > 0:
                    page.keyboard.type(" ", delay=random.randint(30, 80))

                for c_idx, char in enumerate(word):
                    # 오타 시뮬레이션: 1.5% 확률로 오타 → 백스페이스 → 재입력
                    if random.random() < 0.015 and char.isalpha():
                        wrong_char = chr(ord(char) + random.choice([-1, 1]))
                        page.keyboard.type(wrong_char, delay=random.randint(25, 50))
                        time.sleep(random.uniform(0.1, 0.3))
                        page.keyboard.press("Backspace")
                        time.sleep(random.uniform(0.05, 0.15))

                    # 구두점/특수문자 근처: 느리게 (120~200ms)
                    if char in ".,!?;:'\"()-":
                        delay = random.randint(100, 200)
                    # 단어 시작: 약간 느리게
                    elif c_idx == 0:
                        delay = random.randint(50, 90)
                    # 일반: 30~70ms (사람 평균)
                    else:
                        delay = random.randint(30, 70)
                    page.keyboard.type(char, delay=delay)

                # 단어 사이 미세 쉼 (생각하는 시간)
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.3, 0.8))

            # 문단 구분
            if p_idx < len(paragraphs) - 1:
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
                time.sleep(random.uniform(0.5, 1.2))

    # ──────────────────────────────────────────────
    # 📰 글 스크래핑 (Persistent Context 방식)
    # ──────────────────────────────────────────────

    def fetch_live_posts(self, subreddits: List[str], limit_per_sub: int = 15) -> List[Dict[str, Any]]:
        """타깃 서브레딧들에서 실시간 최신 글 목록 무인 추출 (영구 프로필 사용)"""
        from playwright.sync_api import sync_playwright

        all_posts = []
        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                for sub in subreddits:
                    sub_url = f"https://www.reddit.com/r/{sub}/new/"
                    try:
                        logger.info(f"🔍 [Reddit Driver] r/{sub} 최신 글 스캔 중...")
                        page.goto(sub_url, wait_until="domcontentloaded", timeout=25000)
                        page.wait_for_timeout(random.randint(3000, 5000))

                        # 자연스러운 스크롤 (글 더 로딩)
                        self._human_scroll(page, "down", random.randint(200, 400))
                        page.wait_for_timeout(random.randint(1500, 2500))

                        # Modern Reddit shreddit-post 추출
                        posts_data = page.eval_on_selector_all(
                            "shreddit-post",
                            """elements => elements.map(el => {
                                return {
                                    id: el.getAttribute('id') || '',
                                    title: el.getAttribute('post-title') || '',
                                    permalink: el.getAttribute('permalink') || '',
                                    author: el.getAttribute('author') || '',
                                    content_type: el.getAttribute('content-type') || 'text'
                                };
                            })"""
                        )

                        for p_data in posts_data[:limit_per_sub]:
                            p_id = p_data.get("id", "")
                            p_title = p_data.get("title", "")
                            p_link = p_data.get("permalink", "")
                            if p_id and p_title and p_link:
                                all_posts.append({
                                    "id": p_id,
                                    "title": p_title,
                                    "body": p_title,  # shreddit 기본 텍스트 매칭
                                    "subreddit": sub,
                                    "permalink": p_link,
                                    "url": f"https://www.reddit.com{p_link}",
                                    "author": p_data.get("author", "redditor")
                                })

                        logger.info(f"✅ r/{sub} 실시간 글 {len(posts_data)}건 수집 완료")
                    except Exception as e:
                        logger.warning(f"r/{sub} 스캔 중 오류 (스킵): {e}")

                context.close()
        except Exception as e:
            logger.error(f"Reddit 브라우저 스캔 치명적 에러: {e}")

        return all_posts

    # ──────────────────────────────────────────────
    # 👍 업보트 (좋아요)
    # ──────────────────────────────────────────────

    def upvote_post(self, post_url: str, read_sec: int = 0) -> Dict[str, Any]:
        """글 접속 → 읽기 시뮬레이션 → 업보트 클릭"""
        from playwright.sync_api import sync_playwright
        result = {"success": False, "error": None}

        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                logger.info(f"👍 [Upvote] 글 접속 중: {post_url}")
                page.goto(post_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(random.randint(2000, 3500))

                # 읽기 시뮬레이션: 스크롤 + 대기
                actual_read = read_sec if read_sec > 0 else random.randint(3, 8)
                self._human_scroll(page, "down", random.randint(150, 350))
                time.sleep(actual_read)

                # 페이지 로딩 대기
                try:
                    page.wait_for_selector("shreddit-post, article, main", timeout=8000)
                except Exception:
                    pass

                # 업보트 버튼 클릭
                upvote_success = False
                try:
                    # 1. Playwright Shadow DOM piercing locators
                    up_locators = [
                        page.locator("shreddit-post shreddit-action-row button:first-child"),
                        page.locator("button[aria-label*='upvote' i]"),
                        page.locator("button[aria-label*='Upvote']"),
                        page.locator("button[icon-name='upvote']"),
                        page.locator("button[icon-name*='up']"),
                        page.locator("button[data-testid*='upvote']"),
                        page.locator("shreddit-post button[upvote]"),
                        page.locator("faceplate-tracker[noun='upvote'] button"),
                        page.locator("shreddit-post button:has(svg)"),
                    ]
                    for loc in up_locators:
                        if loc.count() > 0 and loc.first.is_visible(timeout=1500):
                            loc.first.click()
                            upvote_success = True
                            break
                except Exception:
                    pass

                if not upvote_success:
                    # 2. 브라우저 내부 JS evaluate 탐색
                    upvote_clicked = page.evaluate("""() => {
                        const post = document.querySelector('shreddit-post');
                        if (post) {
                            // shadowRoot 탐색
                            const root = post.shadowRoot || post;
                            const btn = root.querySelector('button[aria-label*="upvote" i], button[icon-name="upvote"], button:first-child');
                            if (btn) {
                                btn.click();
                                return { success: true, method: 'shadow-upvote' };
                            }
                        }
                        const btns = Array.from(document.querySelectorAll('button'));
                        for (const b of btns) {
                            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                            const icon = (b.getAttribute('icon-name') || '').toLowerCase();
                            const title = (b.getAttribute('title') || '').toLowerCase();
                            if (aria.includes('upvote') || icon.includes('upvote') || title.includes('upvote')) {
                                b.click();
                                return { success: true, method: 'query-button' };
                            }
                        }
                        return { success: false, error: 'Upvote button not found' };
                    }""")
                    upvote_success = upvote_clicked.get("success", False)

                if upvote_success:
                    page.wait_for_timeout(random.randint(1000, 2000))
                    result["success"] = True
                    logger.info("👍 [Upvote] 업보트 성공!")
                else:
                    result["error"] = "Upvote button not found"
                    logger.warning(f"업보트 실패: {result['error']}")

                context.close()
        except Exception as e:
            logger.error(f"업보트 중 예외: {e}")
            result["error"] = str(e)

        return result

    # ──────────────────────────────────────────────
    # 📖 피드 스크롤/읽기 시뮬레이션
    # ──────────────────────────────────────────────

    def scroll_feed(self, subreddit: str, duration_sec: int = 0) -> Dict[str, Any]:
        """서브레딧 피드 자연 스크롤 (진짜 사람처럼 읽는 시뮬레이션)"""
        from playwright.sync_api import sync_playwright
        result = {"success": False, "posts_seen": 0}
        actual_duration = duration_sec if duration_sec > 0 else random.randint(60, 180)

        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                feed_url = f"https://www.reddit.com/r/{subreddit}/hot/"
                logger.info(f"📖 [Browse] r/{subreddit} 피드 스크롤 시작 ({actual_duration}초)...")
                page.goto(feed_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(random.randint(2000, 4000))

                start_time = time.time()
                scroll_count = 0

                while time.time() - start_time < actual_duration:
                    # 스크롤
                    self._human_scroll(page, "down", random.randint(200, 500))
                    scroll_count += 1

                    # 가끔 글 하나 클릭해서 들어가기 (30% 확률)
                    if random.random() < 0.3:
                        clicked = page.evaluate("""() => {
                            const posts = document.querySelectorAll('shreddit-post a[slot="full-post-link"]');
                            if (posts.length > 0) {
                                const idx = Math.floor(Math.random() * Math.min(posts.length, 5));
                                posts[idx].click();
                                return true;
                            }
                            return false;
                        }""")
                        if clicked:
                            page.wait_for_timeout(random.randint(4000, 10000))
                            # 읽다가 스크롤
                            self._human_scroll(page, "down", random.randint(100, 300))
                            page.wait_for_timeout(random.randint(2000, 5000))
                            page.go_back()
                            page.wait_for_timeout(random.randint(1500, 3000))

                    # 읽는 시간 대기
                    time.sleep(random.uniform(2.0, 6.0))

                result["success"] = True
                result["posts_seen"] = scroll_count
                logger.info(f"📖 [Browse] r/{subreddit} 스크롤 완료 ({scroll_count}회 스크롤, {int(time.time()-start_time)}초)")

                context.close()
        except Exception as e:
            logger.error(f"피드 스크롤 중 예외: {e}")
            result["error"] = str(e)

        return result

    def read_post(self, post_url: str, read_sec: int = 0) -> Dict[str, Any]:
        """특정 글 접속 → 읽기 시뮬레이션 (업보트 없이)"""
        from playwright.sync_api import sync_playwright
        result = {"success": False}
        actual_read = read_sec if read_sec > 0 else random.randint(5, 15)

        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                page.goto(post_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(random.randint(2000, 3500))

                # 읽기 시뮬레이션
                self._human_scroll(page, "down", random.randint(150, 400))
                time.sleep(actual_read * 0.4)
                self._human_scroll(page, "down", random.randint(100, 250))
                time.sleep(actual_read * 0.6)

                result["success"] = True
                logger.info(f"📖 [Read] 글 읽기 완료 ({actual_read}초)")

                context.close()
        except Exception as e:
            logger.error(f"글 읽기 중 예외: {e}")
            result["error"] = str(e)

        return result

    # ──────────────────────────────────────────────
    # 💬 댓글 작성 (영구 프로필 방식만 사용)
    # ──────────────────────────────────────────────

    def post_comment_humanlike(self, post_url: str, comment_text: str) -> Dict[str, Any]:
        """
        [영구 프로필 Playwright 엔진]
        - token_v2 OAuth 오용 제거
        - 영구 프로필 세션 기반 100% 브라우저 자동화
        - Human-like 타이핑 + 베지어 마우스 이동
        """
        from playwright.sync_api import sync_playwright
        result = {"success": False, "error": None, "permalink": None}

        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                logger.info(f"🌐 [Reddit Commenter] 글 접속 중: {post_url}")
                page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(random.randint(3000, 5000))

                # 글 읽는 시뮬레이션 (3~6초)
                self._human_scroll(page, "down", random.randint(200, 400))
                time.sleep(random.uniform(3.0, 6.0))

                # 1. 댓글창 활성화 시도
                reply_activated = page.evaluate("""() => {
                    // 1. shreddit-composer 및 shadow/slot 탐색
                    const composer = document.querySelector('shreddit-composer, faceplate-textarea-input');
                    if (composer) {
                        composer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        const rte = composer.querySelector('div[slot="rte"]') ||
                                    composer.querySelector('div[contenteditable="true"]') ||
                                    composer.querySelector('div[role="textbox"]') ||
                                    composer.querySelector('textarea, p');
                        if (rte) {
                            rte.focus();
                            rte.click();
                            return { success: true, method: 'composer' };
                        }
                    }
                    // 2. 일반 텍스트 영역
                    const textbox = document.querySelector('div[contenteditable="true"][role="textbox"], textarea[placeholder*="comment"], div[slot="rte"]');
                    if (textbox) {
                        textbox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        textbox.focus();
                        textbox.click();
                        return { success: true, method: 'textbox' };
                    }
                    // 3. Add a comment 버튼 클릭
                    const addBtns = Array.from(document.querySelectorAll('button, faceplate-tracker')).filter(el => {
                        const txt = (el.innerText || el.getAttribute('aria-label') || '').toLowerCase();
                        return txt.includes('add a comment') || txt.includes('join the conversation');
                    });
                    if (addBtns.length > 0) {
                        addBtns[0].click();
                        return { success: true, method: 'add_comment_button' };
                    }
                    return { success: false, error: 'No comment input found' };
                }""")

                if not reply_activated.get("success"):
                    # Reply 버튼 클릭 시도
                    reply_btn = page.locator("button:has-text('Add a comment'), button:has-text('Reply'), button[aria-label*='Reply'], button[aria-label*='Comment']").first
                    try:
                        if reply_btn.is_visible(timeout=3000):
                            reply_btn.click()
                            page.wait_for_timeout(1500)
                        else:
                            result["error"] = "댓글 입력창을 찾을 수 없습니다 (로그인 세션 만료?)"
                            context.close()
                            return result
                    except Exception:
                        result["error"] = "댓글 입력창 활성화 실패"
                        context.close()
                        return result

                page.wait_for_timeout(random.randint(800, 1500))

                # 2. 사람처럼 타이핑
                self._human_type(page, comment_text)
                page.wait_for_timeout(random.randint(1500, 3000))

                # 3. 등록 버튼 클릭
                submit_success = False
                submit_err = None

                # 3-1. Playwright locators 시도
                submit_locators = [
                    page.locator("#comment-composer-submit-button"),
                    page.locator("shreddit-composer button[type='submit']"),
                    page.locator("button:has-text('Comment')"),
                    page.locator("button:has-text('Reply')"),
                    page.locator("button[slot='submit-button']"),
                ]
                for loc in submit_locators:
                    try:
                        if loc.is_visible(timeout=1500) and loc.is_enabled():
                            loc.click()
                            submit_success = True
                            break
                    except Exception:
                        pass

                # 3-2. 브라우저 내부 JS evaluate 시도
                if not submit_success:
                    click_res = page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                        for (const b of btns) {
                            const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                            const isSubmit = b.getAttribute('type') === 'submit' || b.id === 'comment-composer-submit-button';
                            const isComment = txt === 'comment' || txt === 'reply' || txt.includes('comment');
                            const r = b.getBoundingClientRect();
                            if ((isSubmit || isComment) && r.width > 0 && r.height > 0 && !b.disabled) {
                                b.click();
                                return true;
                            }
                        }
                        return false;
                    }""")
                    submit_success = click_res

                if not submit_success:
                    result["error"] = f"댓글 등록 버튼 클릭 실패: {submit_err}"
                    context.close()
                    return result

                page.wait_for_timeout(random.randint(3000, 5000))
                result["success"] = True
                context.close()
                return result
        except Exception as e:
            logger.error(f"댓글 작성 중 예외: {e}")
            result["error"] = str(e)
            return result

    def check_comment_visible(self, post_url: str, comment_snippet: str) -> bool:
        """게시한 댓글이 실제로 보이는지 비로그인 상태에서 확인 (shadowban 감지)"""
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                # 비로그인 임시 컨텍스트 (다른 사람 시점)
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                context = browser.new_context(
                    user_agent=random.choice(_UA_POOL),
                    viewport={"width": 1280, "height": 800}
                )
                page = context.new_page()
                page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(3000)

                # 댓글 텍스트의 처음 50자를 페이지에서 검색
                search_text = comment_snippet[:50].replace("'", "\\'")
                found = page.evaluate(f"""() => {{
                    return document.body.innerText.includes('{search_text}');
                }}""")

                browser.close()
                return found
        except Exception as e:
            logger.warning(f"댓글 가시성 확인 실패: {e}")
            return True  # 확인 불가 시 보이는 것으로 간주

    # ──────────────────────────────────────────────
    # 📊 프로필 카르마 조회
    # ──────────────────────────────────────────────

    def get_account_karma(self) -> Dict[str, Any]:
        """현재 로그인된 계정의 카르마 수치 조회"""
        from playwright.sync_api import sync_playwright
        result = {"karma": 0, "username": None, "error": None}

        try:
            with sync_playwright() as p:
                context = self._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                page.goto("https://www.reddit.com/", wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(random.randint(3000, 5000))

                # 로그인 상태 확인 및 카르마 파싱
                account_info = page.evaluate("""() => {
                    // 프로필 메뉴에서 username 추출 시도
                    const userEl = document.querySelector('faceplate-tracker[source="profile_menu"]') ||
                                   document.querySelector('a[href*="/user/"]');
                    let username = null;
                    if (userEl) {
                        const href = userEl.getAttribute('href') || '';
                        const match = href.match(/\\/user\\/([^/]+)/);
                        if (match) username = match[1];
                    }
                    // 카르마 수치
                    const karmaEl = document.querySelector('[id*="karma"]') ||
                                    document.querySelector('span[class*="karma"]');
                    let karma = 0;
                    if (karmaEl) {
                        const text = karmaEl.innerText.replace(/,/g, '').replace(/k/i, '000');
                        karma = parseInt(text) || 0;
                    }
                    return { username, karma };
                }""")

                result["username"] = account_info.get("username")
                result["karma"] = account_info.get("karma", 0)

                context.close()
        except Exception as e:
            logger.error(f"카르마 조회 실패: {e}")
            result["error"] = str(e)

        return result

    # ──────────────────────────────────────────────
    # 🔑 로그인 세션 (기존 유지)
    # ──────────────────────────────────────────────

    def open_interactive_login(self, timeout_sec: int = 150) -> bool:
        """
        최초 1회 구글 계정 로그인 세션 영구 등록을 위해 실제 크롬(Real Chrome) 브라우저 실행
        """
        from playwright.sync_api import sync_playwright

        print(f"\n========================================================")
        print(f"🔑 [{self.service_id.upper()}] 실제 크롬(Chrome)으로 레딧 로그인 창을 엽니다.")
        print(f"========================================================")
        print("1. 열린 크롬 창에서 'Log In' ➔ 'Continue with Google'을 눌러 로그인해 주세요.")
        print(f"2. 로그인이 완료되면 이 창을 닫거나 {timeout_sec}초 후 자동으로 세션이 영구 저장됩니다.")
        print("========================================================\n")

        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    channel="chrome",
                    headless=False,
                    ignore_default_args=["--enable-automation"],
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized",
                        "--no-sandbox",
                        "--disable-popup-blocking"
                    ],
                    viewport=None
                )

                print("👉 크롬 창에서 구글 로그인을 진행해 주세요.")
                print("👉 로그인이 완료되면(우측 상단에 내 프로필이 뜨면) 브라우저 창을 닫아주시거나 여기서 Enter를 누르세요.\n")

                try:
                    while len(context.pages) > 0:
                        time.sleep(2)
                except Exception:
                    pass

                # 쿠키 추출 및 영구 저장 (백업용)
                try:
                    cookies = context.cookies(["https://www.reddit.com", "https://reddit.com"])
                    cookie_file = self.profile_dir.parent / f"{self.service_id}_cookies.json"
                    with open(cookie_file, "w", encoding="utf-8") as f:
                        json.dump(cookies, f, indent=2)
                    print(f"🍪 [{self.service_id}] 인증 쿠키 {len(cookies)}개 백업 저장 완료: {cookie_file}")
                except Exception:
                    pass

                context.close()
                print(f"✅ [{self.service_id}] 로그인 세션이 영구 저장되었습니다! ({self.profile_dir})")
                return True
        except Exception as e:
            logger.error(f"로그인 세션 실행 에러: {e}")
            return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reddit Browser Driver v2.0")
    parser.add_argument("--login", action="store_true", help="1회 로그인 세션 등록 창 열기")
    parser.add_argument("--service", type=str, default="kmarket", help="서비스 ID (kmarket / easytax)")
    parser.add_argument("--karma", action="store_true", help="현재 계정 카르마 조회")
    args = parser.parse_args()

    driver = RedditBrowserDriver(service_id=args.service)
    if args.login:
        driver.open_interactive_login()
    elif args.karma:
        info = driver.get_account_karma()
        print(f"Username: {info['username']}, Karma: {info['karma']}")
    else:
        print("Scraping live sample posts...")
        posts = driver.fetch_live_posts(["Living_in_Korea", "korea"], limit_per_sub=5)
        print(f"Scraped {len(posts)} posts:")
        for p in posts[:3]:
            print(f"- {p['title']} ({p['url']})")
