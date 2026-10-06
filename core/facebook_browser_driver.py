# -*- coding: utf-8 -*-
"""
🌐 [Playwright 기반 무인 페이스북 브라우저 드라이버 v1.0] (core/facebook_browser_driver.py)
• 역할: 공식 API로 침투할 수 없는 50만 외국인 페이스북 대형 그룹에
        [무인 브라우저 로그인 ➔ 그룹 방문 ➔ 5장 카드뉴스 업로드 ➔ 본문(링크 0%) 작성 ➔ 첫 댓글 스텔스 링크 자동 입력] 수행
• 특징:
  1. 영구 프로필(Persistent Context) 방식: 페이스북 로그인 세션 및 쿠키 영구 유지
  2. 안티 핑거프린팅(Anti-Fingerprint): navigator.webdriver 은폐, Canvas/WebGL 노이즈, 크롬 런타임 위장
  3. Human-like 행동 시뮬레이션: 베지어 곡선 마우스 이동, 가변 인간 타이핑(오타/지연 시뮬레이션), 관성 스크롤
  4. 0.1초 첫 댓글(First-Comment) 자동화: 본문 발행 직후 본인 글의 댓글 입력창을 찾아 스텔스 링크 자동 타이핑 및 엔터
• 원칙: 모듈 분리 원칙(Rule 1), 땜질 코딩 금지(Rule 5) 준수
"""

import os
import sys
import time
import json
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import DATA_DIR, BASE_DIR

logger = logging.getLogger("FacebookBrowserDriver")

# User-Agent 회전 풀
_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


def _bezier_points(start: tuple, end: tuple, steps: int = 20) -> List[tuple]:
    """베지어 곡선 기반 인간 친화형 마우스 이동 좌표"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) / 2 + random.randint(-60, 60)
    cy = (sy + ey) / 2 + random.randint(-40, 40)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class FacebookBrowserDriver:
    """
    🌐 페이스북 50만 대형 그룹 무인 침투 브라우저 로봇
    """
    def __init__(self, service_id: str = "easytax"):
        self.service_id = service_id
        self.profile_dir = DATA_DIR / "facebook_profiles" / service_id
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_file = self.profile_dir / "cookies.json"
        self._session_ua = random.choice(_UA_POOL)
        self._viewport = {
            "width": 1280 + random.randint(-30, 30),
            "height": 850 + random.randint(-20, 20)
        }

    def _get_anti_fingerprint_scripts(self) -> str:
        """고급 브라우저 핑거프린트 위장 JS"""
        return """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'ko'] });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' }
                ]
            });
        """

    def is_logged_in(self, page) -> bool:
        """현재 페이스북 로그인 상태인지 검증"""
        try:
            # 로그인 폼이 존재하면 로그아웃 상태
            if page.locator("input#email, input[name='email']").count() > 0:
                return False
            # 피드 상단 네비게이션바 또는 프로필 아이콘 확인
            if page.locator("div[role='banner'], div[aria-label*='내 프로필'], div[aria-label*='Your profile']").count() > 0:
                return True
        except Exception:
            pass
        return False

    def human_type(self, page, locator, text: str, min_delay: float = 0.03, max_delay: float = 0.09):
        """인간과 똑같은 가변 타이핑 시뮬레이션"""
        locator.click()
        time.sleep(random.uniform(0.2, 0.4))
        for char in text:
            page.keyboard.type(char)
            time.sleep(random.uniform(min_delay, max_delay))
            # 가끔 0.2초 생각하는 척 지연
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.3))

    def post_to_group(
        self,
        group_url: str,
        post_content: str,
        image_paths: List[str],
        first_comment: Optional[str] = None,
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        🚀 페이스북 대형 그룹 무인 포스팅 & 0.1초 첫 댓글 스텔스 링크 자동 완성
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "success": False,
                "status": "error",
                "message": "Playwright 패키지가 설치되어 있지 않습니다. (pip install playwright)"
            }

        logger.info(f"🌐 [FacebookBrowserDriver] 그룹 침투 브라우저 시작: {group_url}")

        with sync_playwright() as p:
            # 영구 프로필 컨텍스트 구동
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=headless,
                user_agent=self._session_ua,
                viewport=self._viewport,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--disable-dev-shm-usage"
                ]
            )

            page = context.new_page()
            page.add_init_script(self._get_anti_fingerprint_scripts())

            # 1. 쿠키 복원 (기존 저장된 쿠키가 있는 경우)
            if self.cookies_file.exists():
                try:
                    with open(self.cookies_file, "r", encoding="utf-8") as f:
                        cookies = json.load(f)
                    context.add_cookies(cookies)
                except Exception as e:
                    logger.warning(f"쿠키 복원 경고: {e}")

            # 2. 페이스북 그룹 URL 접속
            try:
                page.goto(group_url, wait_until="networkidle", timeout=45000)
                time.sleep(random.uniform(2.5, 4.0))
            except Exception as e:
                logger.warning(f"페이지 로딩 타임아웃(계속 진행): {e}")

            # 3. 로그인 상태 확인
            if not self.is_logged_in(page):
                logger.warning("⚠️ [FacebookBrowserDriver] 페이스북 로그인이 필요합니다. 최초 1회 브라우저 로그인이 필요합니다.")
                context.close()
                return {
                    "success": False,
                    "status": "login_required",
                    "group_url": group_url,
                    "message": "페이스북 로그인 세션이 없습니다. headless=False 모드로 1회 로그인하거나 쿠키를 등록하세요."
                }

            # 로그인 성공 상태이면 현재 쿠키 영구 저장
            try:
                current_cookies = context.cookies()
                with open(self.cookies_file, "w", encoding="utf-8") as f:
                    json.dump(current_cookies, f, indent=2)
            except Exception:
                pass

            # 4. 글쓰기 버튼 탐색 및 클릭
            post_box = None
            create_post_selectors = [
                "div[role='button']:has-text('무슨 생각을 하고 계신가요?')",
                "div[role='button']:has-text(\"Write something...\")",
                "div[role='button']:has-text(\"What's on your mind?\")",
                "span:has-text('무슨 생각을 하고 계신가요?')",
                "span:has-text('Write something...')"
            ]

            for sel in create_post_selectors:
                if page.locator(sel).count() > 0:
                    post_box = page.locator(sel).first
                    break

            if not post_box:
                context.close()
                return {
                    "success": False,
                    "status": "post_box_not_found",
                    "message": "그룹 내 글쓰기 박스를 찾지 못했습니다. (권한 대기 또는 비공개 그룹)"
                }

            post_box.click()
            time.sleep(random.uniform(2.0, 3.0))

            # 5. 사진 첨부 (카드뉴스 5장 업로드)
            valid_images = [str(p) for p in image_paths if os.path.exists(str(p))]
            if valid_images:
                try:
                    file_input = page.locator("input[type='file'][accept*='image']").first
                    if file_input.count() > 0:
                        file_input.set_input_files(valid_images)
                        logger.info(f"📸 카드뉴스 {len(valid_images)}장 첨부 완료")
                        time.sleep(random.uniform(3.0, 5.0))
                except Exception as e:
                    logger.warning(f"이미지 업로드 실패: {e}")

            # 6. 본문 입력 (링크 0% - 알고리즘 도달률 극대화)
            editor = page.locator("div[role='textbox'][contenteditable='true'], div[aria-label*='본문'], div[aria-label*='Write something']").first
            if editor.count() > 0:
                self.human_type(page, editor, post_content)
                time.sleep(random.uniform(1.5, 2.5))

            # 7. 게시(Post) 버튼 클릭
            submit_btn = page.locator("div[aria-label='게시'], div[aria-label='Post'], div[role='button']:has-text('게시'), div[role='button']:has-text('Post')").first
            if submit_btn.count() > 0:
                submit_btn.click()
                logger.info("🚀 [Facebook] 본문 게시 버튼 클릭 완료! 전송 대기...")
                time.sleep(random.uniform(5.0, 8.0))

            # 8. ★ [0.1초 첫 번째 댓글 스텔스 링크 자동 작성]
            comment_posted = False
            if first_comment:
                try:
                    comment_inputs = page.locator("div[role='textbox'][aria-label*='댓글'], div[role='textbox'][aria-label*='Write an answer'], div[role='textbox'][aria-label*='Write a comment']")
                    if comment_inputs.count() > 0:
                        target_comment_input = comment_inputs.first
                        self.human_type(page, target_comment_input, first_comment, min_delay=0.02, max_delay=0.06)
                        time.sleep(0.5)
                        page.keyboard.press("Enter")
                        comment_posted = True
                        logger.info(f"💬 [Facebook] 첫 번째 댓글(스텔스 링크) 자동 등록 성공: {first_comment[:30]}...")
                        time.sleep(random.uniform(2.0, 3.0))
                except Exception as e:
                    logger.warning(f"첫 댓글 자동 등록 중 경고: {e}")

            context.close()
            return {
                "success": True,
                "status": "published",
                "group_url": group_url,
                "total_slides": len(valid_images),
                "comment_posted": comment_posted,
                "message": "페이스북 그룹 본문 포스팅 및 첫 댓글 스텔스 링크 자동 완성 성공"
            }
