"""
EasyTaxAppCapturer - [이지텍스 실제 웹서비스 언어별 모바일 화면 고화질 캡처 & 에셋 제공 모듈]
- https://easy-tax.app/{lang} (메인 홈 1분 환급 조회 화면)
- https://easy-tax.app/{lang}/pricing (선결제 0원 100% 후불제 안심 화면)
- Playwright 모바일 뷰포트(iPhone 규격: 430x932)로 팝업 없이 순정 앱 화면 자동 캡처
- 언어별 로컬 캐싱(data/cache/easytax_screens/) 지원으로 0.01초 초고속 재사용
- 네트워크 지연 시 PhoneAppScreenRenderer 엔진으로 자동 Fallback 무중단 보장
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional
from PIL import Image

logger = logging.getLogger("EasyTaxAppCapturer")


class EasyTaxAppCapturer:
    """이지텍스 모바일 웹뷰 화면 전담 캡처러"""

    def __init__(self, base_url: str = "https://ktrs-service.vercel.app"):
        self.base_url = base_url.rstrip("/")
        # 프로젝트 내부 캐시 디렉토리
        from config import DATA_DIR
        self.cache_dir = DATA_DIR / "cache" / "easytax_screens"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_screen_path(self, lang: str = "uz", screen_type: str = "step0") -> Path:
        """
        언어별, 화면 유형별(step0: 환급 0단계 모의조회, home_cta: 메인홈 신청) 모바일 스크린샷 이미지 경로 반환.
        캐시가 있으면 즉시 반환, 없으면 Playwright로 실시간 캡처.
        """
        lang = (lang or "uz").lower().strip()
        cache_file = self.cache_dir / f"easytax_{lang}_{screen_type}.png"

        # 1. 캐시 존재 및 크기 유효성 확인 (10KB 이상)
        if cache_file.exists() and cache_file.stat().st_size > 10240:
            logger.info(f"[{lang.upper()}] ⚡ 이지텍스 모바일 앱 화면 캐시 사용: {cache_file.name}")
            return cache_file

        # 2. 실시간 캡처 시도
        try:
            logger.info(f"[{lang.upper()}] 🌐 이지텍스 모바일 실제 앱 화면 실시간 캡처 시도 ({screen_type})...")
            captured = self._capture_live_screen(lang, screen_type, cache_file)
            if captured and cache_file.exists():
                return cache_file
        except Exception as e:
            logger.warning(f"[{lang.upper()}] ⚠️ 실시간 캡처 실패: {e}, Fallback 렌더러 가동")

        # 3. Fallback
        return self._generate_fallback_screen(lang, screen_type, cache_file)

    def _capture_live_screen(self, lang: str, screen_type: str, out_path: Path) -> bool:
        """Playwright를 이용한 실제 이지텍스 모바일 웹뷰 스크린샷"""
        from playwright.sync_api import sync_playwright

        # 라우트 결정: 3번은 '환급 0단계 모의조회' iframe 순정 화면, 5번은 '메인홈 1분조회' 화면
        if screen_type in ["step0", "pricing"]:
            target_url = f"{self.base_url}/estimate?simulation=true&lang={lang}"
        else:
            target_url = f"{self.base_url}/?lang={lang}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # iPhone 14 Pro Max 뷰포트 (430 x 932, scale 2)
            context = browser.new_context(
                viewport={"width": 430, "height": 932},
                device_scale_factor=2,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                is_mobile=True,
                has_touch=True
            )
            page = context.new_page()

            # 페이지 로드 (domcontentloaded)
            try:
                page.goto(target_url, timeout=20000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
            except Exception as e:
                logger.error(f"URL 접속 실패 ({target_url}): {e}")
                browser.close()
                return False

            # 불필요한 플로팅 챗봇/팝업 완벽 제거 (클린 스크린 100% 보장)
            page.evaluate("""
                () => {
                    const removeTarget = (el) => {
                        try { el.remove(); } catch(e) { el.style.display = 'none'; }
                    };
                    document.querySelectorAll('[role="dialog"], .fixed.bottom-4, .fixed.bottom-6, .fixed.bottom-0, [class*="fixed"]').forEach(el => {
                        const txt = (el.innerText || '');
                        if (txt.includes('Menejer') || txt.includes('Kim') || txt.includes('매니저') || txt.includes('0-BOSQICH') || txt.includes('0-단계')) {
                            removeTarget(el);
                        }
                    });
                    document.querySelectorAll('button').forEach(btn => {
                        if ((btn.innerText || '').includes('Menejer') || (btn.innerText || '').includes('매니저')) {
                            removeTarget(btn.parentElement || btn);
                        }
                    });
                }
            """)
            page.wait_for_timeout(600)

            # 상단 880px 영역 캡처 (스마트폰 앱 화면 규격)
            page.screenshot(path=str(out_path), full_page=False)
            browser.close()
            logger.info(f"[{lang.upper()}] ✅ 이지텍스 실물 모바일 화면 캡처 성공: {out_path.name}")
            return True

    def _generate_fallback_screen(self, lang: str, screen_type: str, out_path: Path) -> Path:
        """PhoneAppScreenRenderer를 활용한 고화질 Fallback 모바일 앱 UI 생성"""
        from core.phone_app_screen_renderer import PhoneAppScreenRenderer
        renderer = PhoneAppScreenRenderer()

        if screen_type == "pricing":
            return renderer.render_pricing_guarantee_screen(lang=lang, out_path=out_path)
        else:
            return renderer.render_home_cta_screen(lang=lang, out_path=out_path)
