"""
KMarketPhoneMockupRenderer - 📱 [K-Market 전담 스마트폰 아이프레임 목업 렌더러]
- 규격: 1080x945 (카드뉴스 상단 70% 황금 규격)
- 배경: #0B132B (카드뉴스 하단 텍스트 컨테이너와 100% 심리스 일치)
- 중앙: 최신 슬림 베젤 스마트폰 프레임 (다이내믹 아일랜드 + 은은한 네온 오렌지 #F97316 테두리)
- 순정 앱 화면:
  * 4번 슬라이드 (translation): 실제 17개국어 자동번역 배지 및 다국어 지원 화면
  * 5번 슬라이드 (giveaway): 0원 무료나눔 카테고리 및 실시간 매물 피드
- Playwright → Vercel 다이렉트 접속 (로컬 서버 의존 완전 제거)
- PIL 대체 렌더러: 빈 흰 화면 원천 금지 → 풍성한 앱 콘텐츠 렌더링
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("KMarketPhoneMockupRenderer")


class KMarketPhoneMockupRenderer:
    """K-Market 카드뉴스 4번/5번 전용 순정 스마트폰 목업 렌더러"""

    def __init__(self):
        self.width = 1080
        self.height = 945
        self.bg_color = (11, 19, 43)  # #0B132B

    def render_mockup(
        self,
        mode: str = "translation",
        lang: str = "ko",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        4번(translation) 또는 5번(giveaway) 스마트폰 목업을 1080x945 해상도로 렌더링
        """
        if output_path is None:
            output_path = Path(f"outputs/cardnews/kmarket/mockup_{mode}_{lang}_{int(time.time())}.png")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Playwright를 통한 실제 웹뷰 렌더링 시도
        try:
            return self._render_via_playwright(mode=mode, lang=lang, output_path=output_path)
        except Exception as e:
            logger.warning(f"Playwright 목업 렌더링 실패 ({e}) -> PIL 안전 대체 렌더링 가동")
            return self._render_via_pil_fallback(mode=mode, lang=lang, output_path=output_path)

    # ──────────────────────────────────────────────────────────────
    # Playwright → Vercel 직접 접속 → 웹 캡처 → 스마트폰 프레임 합성
    # ──────────────────────────────────────────────────────────────
    def _render_via_playwright(
        self,
        mode: str,
        lang: str,
        output_path: Path
    ) -> Path:
        """
        Playwright → Vercel 직접 접속 → 모달/배너 제거 → 웹 캡처 → 스마트폰 프레임 합성
        📌 로컬 서버(127.0.0.1:8000) 의존 완전 제거 — Vercel 다이렉트 접속만 사용
        """
        from playwright.sync_api import sync_playwright

        # 1. 언어별 URL 라우팅
        if lang in ("ko", "kr", ""):
            target_url = "https://ktrs-market.vercel.app/"
        else:
            target_url = f"https://ktrs-market.vercel.app/{lang}"

        # 폰 스크린 내부 해상도 (베젤 제외 순수 화면 영역)
        screen_w, screen_h = 446, 800
        temp_capture = output_path.parent / f"_temp_webcap_{mode}_{lang}.png"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": screen_w, "height": screen_h},
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
                    "Mobile/15E148 Safari/604.1"
                )
            )
            page.goto(target_url, timeout=25000, wait_until="networkidle")
            page.wait_for_timeout(1500)

            # 🛡️ 슬라이드별 맞춤 UI 캡처 제어
            # 1. 언어 선택 팝업 모달 닫기 / 완전 삭제 (대표님 지침: 4번 국가 표시 팝업 삭제)
            close_btn = page.query_selector('button[aria-label="알림창 닫기"]')
            if close_btn:
                try:
                    close_btn.click()
                    page.wait_for_timeout(800)
                except Exception:
                    pass

            # 잔여 모달/배너 정리 및 스크롤 활성화
            page.evaluate("""() => {
                document.querySelectorAll('div.fixed.inset-0').forEach(el => el.remove());
                const pwa = Array.from(document.querySelectorAll('div')).find(d => 
                    d.className && d.className.includes('fixed') && d.textContent.includes('1초 앱 설치')
                );
                if (pwa) pwa.remove();
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
            }""")
            page.wait_for_timeout(500)

            if mode == "translation":
                # 4번 슬라이드: 팝업 삭제된 K-Market 깨끗한 모바일 홈 화면 (최상단 메인 UI)
                page.wait_for_timeout(500)
            else:
                # 5번 슬라이드: '0원 무료나눔' 카테고리 클릭 -> 실제 매물 피드로 스크롤
                page.evaluate("""() => {
                    const zeroBtn = Array.from(document.querySelectorAll('button, div, a')).find(el => 
                        el.innerText && el.innerText.includes('0원 무료나눔')
                    );
                    if (zeroBtn) zeroBtn.click();
                }""")
                page.wait_for_timeout(1000)

                # 0원 무료나눔 매물 피드 영역으로 스크롤
                page.evaluate("window.scrollTo(0, 1300);")
                page.wait_for_timeout(800)

            page.screenshot(path=str(temp_capture))
            browser.close()

        # 2. 스마트폰 프레임 합성
        result = self._composite_into_phone_frame(temp_capture, output_path)
        try:
            temp_capture.unlink(missing_ok=True)
        except Exception:
            pass
        logger.info(f"✅ [K-Market 스마트폰 목업 생성 완료]: {output_path.name} (모드: {mode}, 언어: {lang})")
        return result

    # ──────────────────────────────────────────────────────────────
    # 웹 캡처 → 스마트폰 프레임 합성
    # ──────────────────────────────────────────────────────────────
    def _composite_into_phone_frame(
        self,
        web_capture_path: Path,
        output_path: Path
    ) -> Path:
        """캡처된 웹 스크린샷을 다크 캔버스 위 스마트폰 프레임 안에 정밀 합성 (1080x945)"""
        canvas = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(canvas)

        phone_w, phone_h = 470, 870
        phone_x = (self.width - phone_w) // 2
        phone_y = (self.height - phone_h) // 2

        # 폰 외곽 그림자 & 베젤
        draw.rounded_rectangle(
            [(phone_x, phone_y), (phone_x + phone_w, phone_y + phone_h)],
            radius=44, fill=(15, 23, 42), outline=(249, 115, 22), width=3
        )

        # 스크린 영역 좌표
        sm = 12
        sx1, sy1 = phone_x + sm, phone_y + sm
        sx2, sy2 = phone_x + phone_w - sm, phone_y + phone_h - sm
        sw, sh = sx2 - sx1, sy2 - sy1

        # 흰색 스크린 바탕
        draw.rounded_rectangle([(sx1, sy1), (sx2, sy2)], radius=34, fill=(250, 248, 245))

        # 웹 캡처 이미지를 스크린 영역에 맞춰 삽입 (둥근 모서리 마스크)
        web_img = Image.open(web_capture_path).convert("RGB").resize((sw, sh), Image.LANCZOS)
        mask = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (sw - 1, sh - 1)], radius=30, fill=255)
        canvas.paste(web_img, (sx1, sy1), mask)

        # 다이내믹 아일랜드 노치
        nw, nh = 120, 24
        nx = (self.width - nw) // 2
        ny = phone_y + 16
        draw.rounded_rectangle([(nx, ny), (nx + nw, ny + nh)], radius=12, fill=(0, 0, 0))

        canvas.save(output_path, "JPEG", quality=95)
        return output_path

    # ──────────────────────────────────────────────────────────────
    # PIL 오프라인 대체 렌더러 (풍성한 앱 콘텐츠 포함)
    # ──────────────────────────────────────────────────────────────
    def _render_via_pil_fallback(
        self,
        mode: str,
        lang: str,
        output_path: Path
    ) -> Path:
        """
        Playwright 불가 시 PIL로 실물 콘텐츠가 포함된 스마트폰 목업 렌더링
        📌 빈 흰 화면 절대 금지 — 번역 뱃지/채팅 or 0원 매물 카드 풍성 렌더링
        """
        canvas = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(canvas)

        # 폰 본체 (470 x 870)
        phone_w, phone_h = 470, 870
        phone_x = (self.width - phone_w) // 2
        phone_y = (self.height - phone_h) // 2

        # 폰 외곽 그림자 & 베젤
        draw.rounded_rectangle(
            [(phone_x, phone_y), (phone_x + phone_w, phone_y + phone_h)],
            radius=44, fill=(15, 23, 42), outline=(249, 115, 22), width=3
        )

        # 화면 영역
        sm = 12
        sx1, sy1 = phone_x + sm, phone_y + sm
        sx2, sy2 = phone_x + phone_w - sm, phone_y + phone_h - sm

        draw.rounded_rectangle([(sx1, sy1), (sx2, sy2)], radius=34, fill=(250, 248, 245))

        # 다이내믹 아일랜드 노치
        nw, nh = 120, 24
        nx = (self.width - nw) // 2
        ny = phone_y + 16
        draw.rounded_rectangle([(nx, ny), (nx + nw, ny + nh)], radius=12, fill=(0, 0, 0))

        # 폰트 로딩
        try:
            font_bold = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 24)
            font_md = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 18)
            font_sm = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 15)
            font_xs = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
        except Exception:
            font_bold = ImageFont.load_default()
            font_md = font_bold
            font_sm = font_bold
            font_xs = font_bold

        # 앱 헤더 바
        header_y = sy1 + 45
        draw.rectangle([(sx1, header_y), (sx2, header_y + 55)], fill=(255, 255, 255))
        title_text = "KTRS MARKET" if lang != "ko" else "KTRS 마켓 (KTRS MARKET)"
        draw.text((sx1 + 18, header_y + 14), title_text, font=font_bold, fill=(24, 24, 27))

        content_y = header_y + 65

        if mode == "translation":
            self._draw_translation_content(draw, sx1, sx2, content_y, font_md, font_sm, font_xs)
        else:
            self._draw_giveaway_content(draw, sx1, sx2, content_y, font_md, font_sm, font_xs)

        canvas.save(output_path, "JPEG", quality=95)
        return output_path

    # ──────────────────────────────────────────────────────────────
    # PIL 콘텐츠 드로잉 헬퍼
    # ──────────────────────────────────────────────────────────────
    def _draw_translation_content(self, draw, sx1, sx2, y, font_md, font_sm, font_xs):
        """4번 슬라이드: 17개국어 번역 기능 시각화 (언어 뱃지 그리드 + 채팅 말풍선)"""
        draw.text((sx1 + 18, y), "17개국어 실시간 자동번역", font=font_md, fill=(249, 115, 22))
        y += 38

        # 언어 뱃지 그리드 (2열)
        flags = [
            "🇻🇳 Tiếng Việt", "🇺🇿 O'zbekcha",
            "🇲🇳 Монгол", "🇨🇳 中文",
            "🇯🇵 日本語", "🇷🇺 Русский",
            "🇹🇭 ไทย", "🇺🇸 English",
            "🇰🇭 ភាសាខ្មែរ", "🇳🇵 नेपाली",
            "🇧🇩 বাংলা", "🇲🇲 မြန်မာ",
        ]
        badge_w = (sx2 - sx1 - 54) // 2
        for i, flag_text in enumerate(flags):
            col = i % 2
            row = i // 2
            bx = sx1 + 18 + col * (badge_w + 12)
            by = y + row * 38
            draw.rounded_rectangle(
                [(bx, by), (bx + badge_w, by + 32)],
                radius=8, fill=(240, 237, 230)
            )
            draw.text((bx + 10, by + 7), flag_text[:14], font=font_xs, fill=(60, 50, 40))

        y += 38 * 6 + 25

        # 실시간 번역 채팅 말풍선
        chats = [
            ("🇻🇳", "Bàn này còn dùng được không ạ?", (220, 235, 255)),
            ("🇰🇷", "네! 상태 좋아요, 바로 가져가세요 😊", (255, 243, 224)),
            ("🇺🇿", "Qachon olib ketsam bo'ladi?", (220, 245, 220)),
            ("🇰🇷", "오늘 저녁 7시에 연세대 앞에서요!", (255, 243, 224)),
        ]
        for emoji, text, bg_color in chats:
            cw = sx2 - sx1 - 50
            draw.rounded_rectangle(
                [(sx1 + 18, y), (sx1 + 18 + cw, y + 48)],
                radius=14, fill=bg_color
            )
            draw.text((sx1 + 30, y + 8), f"{emoji} {text[:28]}", font=font_xs, fill=(30, 30, 30))
            y += 58

    def _draw_giveaway_content(self, draw, sx1, sx2, y, font_md, font_sm, font_xs):
        """5번 슬라이드: 0원 나눔 피드 시각화 (실물 매물 카드 리스트)"""
        draw.text((sx1 + 18, y), "오늘의 0원 무료나눔 매물", font=font_md, fill=(249, 115, 22))
        y += 42

        items = [
            {"title": "원목 공부책상 & 의자", "loc": "신촌 연세대 앞", "time": "3분 전", "color": (180, 140, 100)},
            {"title": "소형 미니냉장고 (삼성)", "loc": "안암 고려대 후문", "time": "12분 전", "color": (160, 180, 200)},
            {"title": "LED 스탠드 & 수납장", "loc": "혜화 성균관대", "time": "25분 전", "color": (200, 180, 160)},
            {"title": "전자레인지 (깨끗)", "loc": "왕십리 한양대", "time": "1시간 전", "color": (170, 190, 170)},
            {"title": "에어프라이어 5L", "loc": "수원 아주대", "time": "2시간 전", "color": (190, 170, 190)},
        ]

        card_w = sx2 - sx1 - 36
        for item in items:
            # 카드 배경
            draw.rounded_rectangle(
                [(sx1 + 18, y), (sx1 + 18 + card_w, y + 88)],
                radius=14, fill=(255, 255, 255), outline=(235, 230, 220), width=1
            )
            # 썸네일 (색상 박스로 대체)
            draw.rounded_rectangle(
                [(sx1 + 26, y + 8), (sx1 + 96, y + 78)],
                radius=10, fill=item["color"]
            )
            # 0원 뱃지
            draw.rounded_rectangle(
                [(sx1 + 30, y + 56), (sx1 + 72, y + 74)],
                radius=6, fill=(249, 115, 22)
            )
            draw.text((sx1 + 37, y + 58), "0원", font=font_xs, fill=(255, 255, 255))
            # 매물 제목
            draw.text((sx1 + 108, y + 14), item["title"][:16], font=font_sm, fill=(24, 24, 27))
            # 위치 & 시간
            draw.text((sx1 + 108, y + 38), item["loc"], font=font_xs, fill=(120, 120, 120))
            draw.text((sx1 + 108, y + 58), item["time"], font=font_xs, fill=(160, 160, 160))
            y += 98
