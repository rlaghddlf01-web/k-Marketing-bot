"""
KMarketRealBrowserCapturer - [실제 케이마켓 웹사이트 9:16 모바일 스크린샷 캡처기]
- Playwright Chromium 브라우저를 백그라운드(Headless)로 가동
- 실제 케이마켓(https://ktrs-market.vercel.app/?lang=vi 등)에 접속
- 1080x1920 세로형 모바일 뷰포트로 100% 실제 웹 화면을 스크린샷 캡처
- 카드뉴스 및 숏폼 비디오의 배경으로 100% 실제 UI 제공
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional
from playwright.sync_api import sync_playwright
from config import OUTPUTS_DIR

logger = logging.getLogger("KMarketCapturer")


class KMarketRealBrowserCapturer:
    """
    🌐 실제 케이마켓 웹사이트 모바일 스크린샷 전담 캡처기
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "cardnews")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://ktrs-market.vercel.app"

    def capture_real_kmarket_slides(self, lang: str = "vi") -> List[Path]:
        """
        실제 케이마켓 클린 뷰어에 접속하여 9:16 (1080x1920) 모바일 스크린샷 4장 캡처
        """
        captured_paths = []
        target_url = f"http://127.0.0.1:8000/api/kmarket/clean_view?lang={lang}"
        logger.info(f"🌐 [{lang.upper()}] 케이마켓 클린 모바일 뷰 캡처 시작: {target_url}")

        with sync_playwright() as p:
            # iPhone 14 Pro Max 뷰포트 비율 (1080x1920)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1080, "height": 1920},
                device_scale_factor=1.0,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
            )
            page = context.new_page()
            
            try:
                # 1. 메인 피드 로딩 대기
                page.goto(target_url, timeout=30000, wait_until="networkidle")
                page.wait_for_timeout(2000) # 리액트 하이드레이션 및 이미지 렌더링 대기

                # 🛡️ 팝업/모달/배너 100% 완전 박멸 (CSS + DOM 삭제)
                page.add_style_tag(content="""
                    div[role="dialog"],
                    div[aria-modal="true"],
                    div.fixed.inset-0.z-50,
                    div.fixed.inset-0.bg-black\\/60,
                    div.fixed.inset-0.bg-black\\/70,
                    div.fixed.inset-0.backdrop-blur-sm,
                    div.fixed.bottom-0.z-50,
                    div.fixed.inset-x-0.bottom-0.z-50 {
                        display: none !important;
                        visibility: hidden !important;
                        pointer-events: none !important;
                        opacity: 0 !important;
                    }
                    body, html {
                        overflow: auto !important;
                        overflow-y: auto !important;
                    }
                """)
                page.evaluate("""() => {
                    document.querySelectorAll('div[role="dialog"], div[aria-modal="true"], div.fixed.inset-0').forEach(el => el.remove());
                    document.querySelectorAll('div.fixed.bottom-0').forEach(el => el.remove());
                    document.body.style.overflow = 'auto';
                    document.documentElement.style.overflow = 'auto';
                }""")
                page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"페이지 로딩 대기 타임아웃 (계속 진행): {e}")

            # 슬라이드 1: 메인 상단 헤더 + 0원 나눔 피드 캡처
            s1_path = self.output_dir / f"kmarket_real_{lang}_slide_1.png"
            page.screenshot(path=str(s1_path), full_page=False)
            captured_paths.append(s1_path)

            # 슬라이드 2: 아래로 800px 스크롤 (무빙세일 매물 리스트 캡처)
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(800)
            s2_path = self.output_dir / f"kmarket_real_{lang}_slide_2.png"
            page.screenshot(path=str(s2_path), full_page=False)
            captured_paths.append(s2_path)

            # 슬라이드 3: 아래로 추가 800px 스크롤 (인기 가구/가전 캡처)
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(800)
            s3_path = self.output_dir / f"kmarket_real_{lang}_slide_3.png"
            page.screenshot(path=str(s3_path), full_page=False)
            captured_paths.append(s3_path)

            # 슬라이드 4: 아래로 추가 스크롤 (직거래 지도 및 하단 CTA)
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(800)
            s4_path = self.output_dir / f"kmarket_real_{lang}_slide_4.png"
            page.screenshot(path=str(s4_path), full_page=False)
            captured_paths.append(s4_path)

            browser.close()

        logger.info(f"🎉 [{lang.upper()}] 실제 케이마켓 웹사이트 9:16 스크린샷 4장 캡처 성공!")
        return captured_paths
