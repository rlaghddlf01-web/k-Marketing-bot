"""
📢 [Reddit Post Publisher — 프로필 핀 포스트 & 서브레딧 단독 발행 전담 모듈]
- Playwright Persistent Context 기반 레딧 단독 포스트(Post) 발행 및 프로필 핀(Sticky) 고정
- 내 프로필 (u/username) 및 자체 서브레딧 (r/subreddit) 게시 완벽 지원
- Human-like 타이핑, 마크다운 렌더링, 핀 고정 자동화
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import DATA_DIR
from core.reddit_browser_driver import RedditBrowserDriver, _UA_POOL, _bezier_points

logger = logging.getLogger("RedditPostPublisher")


class RedditPostPublisher:
    """
    📢 [레딧 단독 포스트 및 프로필 핀 퍼블리셔]
    - 내 프로필(u/username)에 단독 포스트 작성 및 'Pin to profile' 상단 고정
    - 자체 서브레딧(r/...)에 단독 포스트 작성
    """
    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id
        self.driver = RedditBrowserDriver(service_id=service_id)
        self.profile_dir = self.driver.profile_dir

    def publish_profile_post(self, title: str, body: str, pin_to_profile: bool = True) -> Dict[str, Any]:
        """
        내 계정 프로필(u/username)에 단독 포스트를 발행하고 상단 핀(Pin to profile)으로 고정
        """
        from playwright.sync_api import sync_playwright

        result = {
            "success": False,
            "post_url": None,
            "pinned": False,
            "error": None
        }

        # 1. 현재 로그인 사용자명 확인
        account_info = self.driver.get_account_karma()
        username = account_info.get("username")
        if not username or account_info.get("session_expired"):
            logger.error(f"🚨 [{self.service_id.upper()}] 레딧 로그인 세션이 만료되었습니다. 포스팅 불가.")
            result["error"] = "session_expired"
            return result

        logger.info(f"🚀 [{self.service_id.upper()}] u/{username} 프로필에 공식 쇼케이스 포스트 발행 시작...")

        try:
            with sync_playwright() as p:
                context = self.driver._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                # 프로필 포스트 작성 URL 접속
                submit_url = f"https://www.reddit.com/user/{username}/submit"
                logger.info(f"🌐 포스트 작성 페이지 접속: {submit_url}")
                page.goto(submit_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(random.randint(3000, 5000))

                # 리다이렉트되거나 /submit 경로일 경우 대비
                current_url = page.url
                if "/submit" not in current_url:
                    page.goto("https://www.reddit.com/submit", wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(3000)

                # 1. 제목 입력창 찾기 및 입력
                title_loc = page.locator("textarea[placeholder*='Title' i], textarea[aria-label*='Title' i], input[placeholder*='Title' i], [name='title']").first
                try:
                    title_loc.wait_for(state="visible", timeout=10000)
                    title_loc.click()
                    page.wait_for_timeout(500)
                    self.driver._human_type(page, title)
                except Exception as e:
                    logger.warning(f"제목 입력 locator 실패, JS evaluate 시도: {e}")
                    page.evaluate("""(t) => {
                        const el = document.querySelector('textarea[placeholder*="Title" i], textarea[name="title"], input[name="title"], [role="textbox"]');
                        if (el) {
                            el.focus();
                            el.value = t;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", title)

                page.wait_for_timeout(random.randint(1000, 2000))

                # 2. 본문 에디터 찾기 및 입력
                # 마크다운 모드 버튼이 있으면 클릭하여 서식 무결성 보장
                try:
                    md_btn = page.locator("button:has-text('Markdown'), button:has-text('Markdown Mode'), button[aria-label*='Markdown']").first
                    if md_btn.is_visible(timeout=2000):
                        md_btn.click()
                        page.wait_for_timeout(800)
                except Exception:
                    pass

                body_loc = page.locator("div[role='textbox'][contenteditable='true'], textarea[placeholder*='Text' i], textarea[name='text'], div[slot='rte']").first
                try:
                    body_loc.wait_for(state="visible", timeout=8000)
                    body_loc.click()
                    page.wait_for_timeout(500)

                    # 긴 본문은 안전한 클립보드/인젝션 + 사람 타이핑 조합으로 입력
                    page.evaluate("""(bText) => {
                        const el = document.querySelector('div[role="textbox"][contenteditable="true"], textarea[placeholder*="Text" i], textarea[name="text"], div[slot="rte"]');
                        if (el) {
                            el.focus();
                            if (el.tagName.toLowerCase() === 'textarea') {
                                el.value = bText;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            } else {
                                document.execCommand('insertText', false, bText);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }
                    }""", body)
                except Exception as e:
                    logger.error(f"본문 입력 실패: {e}")
                    result["error"] = f"Body input failed: {e}"
                    context.close()
                    return result

                page.wait_for_timeout(random.randint(2000, 3500))

                # 3. 'Post' 발행 버튼 클릭
                post_success = False
                post_btn = page.locator("button:has-text('Post'):not([disabled]), button[type='submit']:has-text('Post'), button[data-testid='submit_button']").first
                try:
                    if post_btn.is_visible(timeout=3000) and post_btn.is_enabled():
                        post_btn.click()
                        post_success = True
                except Exception:
                    pass

                if not post_success:
                    clicked = page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button'));
                        for (const b of btns) {
                            const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                            if (txt === 'post' && !b.disabled) {
                                b.click();
                                return true;
                            }
                        }
                        return false;
                    }""")
                    post_success = clicked

                if not post_success:
                    logger.error(f"❌ [{self.service_id.upper()}] Post 버튼을 누르지 못했습니다.")
                    result["error"] = "Post button click failed"
                    context.close()
                    return result

                logger.info(f"⏳ [{self.service_id.upper()}] 포스트 발행 처리 중 (5~8초 대기)...")
                page.wait_for_timeout(random.randint(5000, 8000))

                # 발행된 포스트 URL 추출
                post_url = page.url
                result["post_url"] = post_url
                result["success"] = True
                logger.info(f"✅ [{self.service_id.upper()}] 프로필 포스트 발행 성공! URL: {post_url}")

                # 4. 프로필 상단 핀(Pin to profile) 고정 시도
                if pin_to_profile:
                    try:
                        logger.info("📌 프로필 상단 고정(Pin to profile) 메뉴 조작 시도...")
                        # 모더레이터 쉴드/더보기 메뉴 클릭
                        menu_clicked = page.evaluate("""() => {
                            const modBtn = document.querySelector('button[aria-label*="Mod" i], button[aria-label*="Distinguish" i], shreddit-post-overflow-menu');
                            if (modBtn) {
                                modBtn.click();
                                return true;
                            }
                            const moreBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.getAttribute('aria-label') || '').includes('more'));
                            if (moreBtns.length > 0) {
                                moreBtns[0].click();
                                return true;
                            }
                            return false;
                        }""")
                        page.wait_for_timeout(1500)

                        pin_btn = page.locator("button:has-text('Pin to Profile'), button:has-text('Sticky to Profile'), [role='menuitem']:has-text('Pin')").first
                        if pin_btn.is_visible(timeout=3000):
                            pin_btn.click()
                            page.wait_for_timeout(2000)
                            result["pinned"] = True
                            logger.info("📌 [Pin to Profile] 성공적으로 프로필 상단에 고정되었습니다!")
                        else:
                            logger.info("📌 상단 핀 고정 버튼 미발견 (포스트 작성 완료 상태)")
                    except Exception as e:
                        logger.debug(f"핀 고정 추가 조작 실패 (글 자체는 정상 발행됨): {e}")

                context.close()
        except Exception as e:
            logger.error(f"프로필 포스트 발행 중 치명적 에러: {e}")
            result["error"] = str(e)

        return result

    def publish_subreddit_post(self, subreddit: str, title: str, body: str) -> Dict[str, Any]:
        """자체 서브레딧 (r/subreddit)에 단독 포스트 발행"""
        from playwright.sync_api import sync_playwright

        result = {
            "success": False,
            "post_url": None,
            "error": None
        }

        logger.info(f"🚀 [{self.service_id.upper()}] r/{subreddit} 서브레딧에 포스트 발행 시작...")

        try:
            with sync_playwright() as p:
                context = self.driver._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                submit_url = f"https://www.reddit.com/r/{subreddit}/submit"
                page.goto(submit_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(random.randint(3000, 5000))

                # 제목 입력
                title_loc = page.locator("textarea[placeholder*='Title' i], textarea[aria-label*='Title' i], input[placeholder*='Title' i]").first
                title_loc.wait_for(state="visible", timeout=8000)
                title_loc.click()
                self.driver._human_type(page, title)

                page.wait_for_timeout(1000)

                # 본문 입력
                body_loc = page.locator("div[role='textbox'][contenteditable='true'], textarea[placeholder*='Text' i], textarea[name='text']").first
                body_loc.wait_for(state="visible", timeout=8000)
                body_loc.click()

                page.evaluate("""(bText) => {
                    const el = document.querySelector('div[role="textbox"][contenteditable="true"], textarea[placeholder*="Text" i], textarea[name="text"]');
                    if (el) {
                        el.focus();
                        if (el.tagName.toLowerCase() === 'textarea') {
                            el.value = bText;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        } else {
                            document.execCommand('insertText', false, bText);
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                }""", body)

                page.wait_for_timeout(2000)

                # Post 버튼 클릭
                post_btn = page.locator("button:has-text('Post'):not([disabled]), button[type='submit']:has-text('Post')").first
                post_btn.click()

                page.wait_for_timeout(6000)
                result["post_url"] = page.url
                result["success"] = True
                logger.info(f"✅ [{self.service_id.upper()}] r/{subreddit} 포스트 발행 완료! URL: {page.url}")

                context.close()
        except Exception as e:
            logger.error(f"서브레딧 포스트 발행 에러: {e}")
            result["error"] = str(e)

        return result
