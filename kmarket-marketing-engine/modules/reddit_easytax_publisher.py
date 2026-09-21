"""
📢 [EasyTax 전용 Reddit Post Publisher — 프로필 핀 & 서브레딧 퍼블리셔]
- 100% EasyTax 전용 독립 퍼블리셔 모듈 (K-Market과 완전 분리)
- Playwright 영구 프로필 Context 기반 단독 포스트 발행 및 'Pin to profile' 상단 고정
- 한국어/영어 UI 완벽 대응 ('게시하기' / 'Post' / 'post-composer-title' / Lexical Editor)
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.reddit_browser_driver import RedditBrowserDriver

logger = logging.getLogger("EasyTaxRedditPublisher")


class EasyTaxRedditPublisher:
    """
    💰 [EasyTax 전용 레딧 단독 포스트 및 프로필 핀 퍼블리셔]
    - 내 프로필(u/easytax 계정)에 EasyTax 세무 가이드 포스트 작성 및 Pin 고정
    - 자체 서브레딧(r/easytax_...)에 단독 포스트 작성
    """
    def __init__(self):
        self.service_id = "easytax"
        self.driver = RedditBrowserDriver(service_id=self.service_id)
        self.profile_dir = self.driver.profile_dir

    def publish_profile_post(self, title: str, body: str, pin_to_profile: bool = True) -> Dict[str, Any]:
        """
        EasyTax 계정 프로필(u/username)에 단독 포스트를 발행하고 상단 핀으로 고정
        """
        from playwright.sync_api import sync_playwright

        result = {
            "success": False,
            "post_url": None,
            "pinned": False,
            "error": None
        }

        account_info = self.driver.get_account_karma()
        username = account_info.get("username")
        if not username or account_info.get("session_expired"):
            logger.error(f"🚨 [EASYTAX] 레딧 로그인 세션이 만료되었습니다. 포스팅 불가.")
            result["error"] = "session_expired"
            return result

        logger.info(f"💰 [EasyTax] u/{username} 프로필에 공식 세무 쇼케이스 포스트 발행 시작...")

        try:
            with sync_playwright() as p:
                context = self.driver._create_persistent_context(p, headless=True)
                page = context.pages[0] if context.pages else context.new_page()

                submit_url = f"https://www.reddit.com/user/{username}/submit"
                logger.info(f"🌐 [EasyTax] 포스트 작성 페이지 접속: {submit_url}")
                page.goto(submit_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(random.randint(3000, 5000))

                current_url = page.url
                if "/submit" not in current_url:
                    page.goto("https://www.reddit.com/submit", wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(3000)

                # 1. 제목 입력
                title_injected = page.evaluate("""(titleText) => {
                    const titleComp = document.querySelector('post-composer-title');
                    if (titleComp) {
                        const inner = titleComp.shadowRoot ? titleComp.shadowRoot.querySelector('textarea, input') : titleComp.querySelector('textarea, input');
                        if (inner) {
                            inner.focus();
                            inner.value = titleText;
                            inner.dispatchEvent(new Event('input', { bubbles: true }));
                            inner.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                        titleComp.focus();
                        titleComp.value = titleText;
                        return true;
                    }
                    const general = document.querySelector('textarea[name="title"], input[name="title"], textarea[placeholder*="Title" i], textarea[placeholder*="제목"]');
                    if (general) {
                        general.focus();
                        general.value = titleText;
                        general.dispatchEvent(new Event('input', { bubbles: true }));
                        return true;
                    }
                    return false;
                }""", title)

                if not title_injected:
                    title_loc = page.locator("post-composer-title, textarea[name='title'], input[name='title']").first
                    title_loc.click()
                    page.keyboard.type(title)

                page.wait_for_timeout(random.randint(1000, 2000))

                # 2. 본문 입력
                body_injected = page.evaluate("""(bText) => {
                    const editors = Array.from(document.querySelectorAll('div[data-lexical-editor="true"], div[slot="editor"], div[role="textbox"]'))
                        .filter(el => !el.closest('post-composer-title'));
                    
                    if (editors.length > 0) {
                        const ed = editors[0];
                        ed.focus();
                        ed.click();
                        document.execCommand('insertText', false, bText);
                        ed.dispatchEvent(new Event('input', { bubbles: true }));
                        return true;
                    }
                    return false;
                }""", body)

                if not body_injected:
                    try:
                        md_btn = page.locator("button:has-text('Markdown'), button:has-text('마크다운')").first
                        if md_btn.is_visible(timeout=1500):
                            md_btn.click()
                            page.wait_for_timeout(500)
                    except Exception:
                        pass

                page.wait_for_timeout(random.randint(2000, 3500))

                # 3. '게시하기' / 'Post' 버튼 클릭
                post_success = False
                post_locators = [
                    page.locator("button:has-text('게시하기')"),
                    page.locator("button:has-text('게시')"),
                    page.locator("button:has-text('Post')"),
                    page.locator("button[type='submit']:has-text('게시')"),
                    page.locator("button[type='submit']:has-text('Post')"),
                ]
                for loc in post_locators:
                    try:
                        if loc.count() > 0 and loc.first.is_visible(timeout=1500) and loc.first.is_enabled():
                            loc.first.click()
                            post_success = True
                            break
                    except Exception:
                        pass

                if not post_success:
                    clicked = page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                        for (const b of btns) {
                            const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                            if ((txt === '게시하기' || txt === '게시' || txt === 'post') && !b.disabled) {
                                b.click();
                                return true;
                            }
                        }
                        return false;
                    }""")
                    post_success = clicked

                if not post_success:
                    logger.error("❌ [EasyTax] '게시하기/Post' 버튼 클릭 실패")
                    result["error"] = "Post button click failed"
                    context.close()
                    return result

                logger.info("⏳ [EasyTax] 포스트 발행 처리 중 (5~8초 대기)...")
                page.wait_for_timeout(random.randint(6000, 9000))

                post_url = page.url
                result["post_url"] = post_url
                result["success"] = True
                logger.info(f"✅ [EasyTax] 프로필 포스트 발행 성공! URL: {post_url}")

                # 4. 상단 핀(Pin to profile) 고정
                if pin_to_profile:
                    try:
                        logger.info("[EasyTax] 📌 프로필 상단 고정(Pin) 조작 시도...")
                        page.evaluate("""() => {
                            const modBtn = document.querySelector('button[aria-label*="Mod" i], button[aria-label*="관리" i], button[aria-label*="Distinguish" i], shreddit-post-overflow-menu');
                            if (modBtn) {
                                modBtn.click();
                                return true;
                            }
                            const moreBtns = Array.from(document.querySelectorAll('button')).filter(b => {
                                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                                return aria.includes('more') || aria.includes('더보기') || aria.includes('옵션');
                            });
                            if (moreBtns.length > 0) {
                                moreBtns[0].click();
                                return true;
                            }
                            return false;
                        }""")
                        page.wait_for_timeout(1500)

                        pin_btn = page.locator("button:has-text('프로필에 고정'), button:has-text('Pin to Profile'), button:has-text('상단 고정'), [role='menuitem']:has-text('고정'), [role='menuitem']:has-text('Pin')").first
                        if pin_btn.is_visible(timeout=3000):
                            pin_btn.click()
                            page.wait_for_timeout(2000)
                            result["pinned"] = True
                            logger.info("[EasyTax] 📌 상단 핀 고정 성공!")
                        else:
                            logger.info("[EasyTax] 📌 상단 핀 고정 버튼 미발견 (포스트 작성 완료 상태)")
                    except Exception as e:
                        logger.debug(f"[EasyTax] 핀 고정 추가 조작 실패: {e}")

                context.close()
        except Exception as e:
            logger.error(f"[EasyTax] 프로필 포스트 발행 중 에러: {e}")
            result["error"] = str(e)

        return result
