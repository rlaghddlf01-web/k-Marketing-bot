# -*- coding: utf-8 -*-
"""
CardnewsTypographyEasyTax - 🏛️ [EasyTax 전용 1080x1350 시나리오 디렉터 & 제미나이 연동 무결점 타이포그래피 엔진]
- 시나리오 디렉터 및 제미나이가 실시간 창작한 card_data(제목, 부제, 불릿, 배지, CTA버튼)를 100% 동적 반영
- Playwright Chromium(Google HarfBuzz + Skia) 기반 전 언어 네이티브 무결점 텍스트 셰이핑
- EasyTax 전용 로열 네이비 & 럭셔리 골드 테마 + 공식 브랜드 로고 배지 (🏛️ EasyTax | 국세청 공식 세무법인)
- 1~5번 슬라이드: 하단 딥 네이비 그라디언트 스크림 + 카테고리 배지 + 골드 헤드라인 + 서브타이틀 + 3줄 불릿 + 동적 CTA
"""

import html
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import io
from playwright.sync_api import sync_playwright

logger = logging.getLogger("CardnewsTypographyEasyTax")


class CardnewsTypographyEasyTax:
    """EasyTax 전용 카드뉴스 고해상도 무결점 타이포그래피 렌더러 (제미나이 100% 동적 주입)"""

    def __init__(self):
        self.viewport_w = 540
        self.viewport_h = 675
        self.scale_factor = 2.0  # 540x675 * 2.0 = 1080x1350

    def render_overlay(
        self,
        card_data: Dict[str, Any],
        s_idx: int,
        lang: str
    ) -> Image.Image:
        """
        제미나이가 실시간 창작한 card_data를 바탕으로 1080x1350 투명 RGBA 오버레이 렌더링
        """
        badge = card_data.get("badge", f"STEP {s_idx}")
        title = card_data.get("title", "")
        subtitle = card_data.get("subtitle", "")
        bullets = card_data.get("bullets", [])

        # EasyTax 전용 브랜드 로고 헤더
        brand_logo_html = """
            <div class="brand-badge brand-easytax">
                <span class="brand-icon">🏛️</span>
                <span class="brand-text">EasyTax</span>
                <span class="brand-sub">국세청 공식 세무법인</span>
            </div>
        """
        page_badge = f"{s_idx:02d} / 05 >"

        # CTA 버튼 텍스트: 제미나이가 실시간 창작한 cta_button 연동
        btn_text = card_data.get("cta_button") or ("다음 내용 보기 >" if s_idx not in (1, 5) else "내 환급금 조회하기 >")

        # EasyTax 테마: 1, 5번은 럭셔리 골드 CTA, 2, 3, 4번은 다크 네이비 CTA
        cta_bg = "#d4af37" if s_idx in (1, 5) else "#1e293b"
        cta_color = "#0b132b" if s_idx in (1, 5) else "#ffffff"
        badge_bg = "#1e50a0"
        badge_color = "#ffffff"

        # 불릿 HTML 구성
        bullets_html = ""
        for b in bullets[:3]:
            if b:
                clean_b = b.lstrip("•-123456789. ")
                bullets_html += f"""<div class="bullet-item"><span class="bullet-dot">•</span><span class="bullet-text">{html.escape(clean_b)}</span></div>"""

        overlay_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=540, height=675, initial-scale=1.0">
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                    font-family: 'Leelawadee UI', 'Nirmala UI', 'Myanmar Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                }}
                body {{
                    width: 540px;
                    height: 675px;
                    background: transparent;
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}

                /* 상단 EasyTax 브랜드 헤더 */
                .top-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 24px 28px 12px;
                    z-index: 10;
                }}
                .brand-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    background: rgba(11, 19, 43, 0.84);
                    backdrop-filter: blur(8px);
                    padding: 6px 14px;
                    border-radius: 24px;
                    border: 1px solid rgba(212, 175, 55, 0.35);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }}
                .brand-badge .brand-icon {{
                    font-size: 14px;
                }}
                .brand-badge .brand-text {{
                    color: #ffffff;
                    font-weight: 800;
                    font-size: 13.5px;
                    letter-spacing: -0.3px;
                }}
                .brand-badge .brand-sub {{
                    color: #d4af37;
                    font-weight: 600;
                    font-size: 10.5px;
                    padding-left: 4px;
                    border-left: 1px solid rgba(212, 175, 55, 0.3);
                }}
                .page-index {{
                    color: #d4af37;
                    font-weight: 800;
                    font-size: 13px;
                    background: rgba(11, 19, 43, 0.78);
                    padding: 5px 12px;
                    border-radius: 16px;
                    border: 1px solid rgba(212, 175, 55, 0.35);
                    letter-spacing: 0.5px;
                }}

                /* 하단 그라디언트 스크림 및 콘텐츠 컨테이너 */
                .bottom-scrim {{
                    width: 100%;
                    background: linear-gradient(
                        180deg,
                        rgba(11, 19, 43, 0.0) 0%,
                        rgba(11, 19, 43, 0.76) 22%,
                        rgba(11, 19, 43, 0.95) 55%,
                        rgba(11, 19, 43, 0.99) 100%
                    );
                    padding: 40px 28px 26px;
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    z-index: 5;
                }}

                /* 카테고리/단계 배지 (로열 블루) */
                .category-badge {{
                    align-self: flex-start;
                    background: {badge_bg};
                    color: {badge_color};
                    font-weight: 800;
                    font-size: 12px;
                    padding: 5px 13px;
                    border-radius: 6px;
                    letter-spacing: -0.2px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    margin-bottom: 2px;
                }}

                /* 헤드라인 타이틀 (럭셔리 골드) */
                .headline-title {{
                    font-size: 22px;
                    font-weight: 800;
                    color: #ffd700;
                    line-height: 1.32;
                    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.85);
                    letter-spacing: -0.4px;
                    word-break: break-word;
                }}

                /* 서브타이틀 */
                .subtitle-text {{
                    font-size: 13.5px;
                    font-weight: 500;
                    color: #e2e8f0;
                    line-height: 1.45;
                    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
                    letter-spacing: -0.2px;
                    word-break: break-word;
                }}

                /* 3줄 불릿 리스트 */
                .bullets-list {{
                    display: flex;
                    flex-direction: column;
                    gap: 3px;
                    margin: 4px 0 6px;
                }}
                .bullet-item {{
                    display: flex;
                    align-items: baseline;
                    gap: 6px;
                    font-size: 12.5px;
                    color: #cbd5e1;
                    line-height: 1.38;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.7);
                }}
                .bullet-dot {{
                    color: #38bdf8;
                    font-weight: 900;
                    font-size: 14px;
                }}
                .bullet-text {{
                    word-break: break-word;
                }}

                /* 하단 CTA 버튼 */
                .cta-button {{
                    width: 100%;
                    background: {cta_bg};
                    color: {cta_color};
                    font-size: 15px;
                    font-weight: 800;
                    padding: 12px 20px;
                    border-radius: 12px;
                    text-align: center;
                    border: none;
                    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
                    letter-spacing: -0.2px;
                    margin-top: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="top-header">
                {brand_logo_html}
                <div class="page-index">{page_badge}</div>
            </div>
            <div class="bottom-scrim">
                <div class="category-badge">{html.escape(badge)}</div>
                <div class="headline-title">{html.escape(title)}</div>
                {f'<div class="subtitle-text">{html.escape(subtitle)}</div>' if subtitle else ''}
                {f'<div class="bullets-list">{bullets_html}</div>' if bullets_html else ''}
                <div class="cta-button">{html.escape(btn_text)}</div>
            </div>
        </body>
        </html>"""
        return self._render_html_to_image(overlay_html)

    def _render_html_to_image(self, html_content: str) -> Image.Image:
        """Playwright Chromium으로 HTML을 1080x1350 투명 RGBA 이미지로 렌더링"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": self.viewport_w, "height": self.viewport_h},
                    device_scale_factor=self.scale_factor
                )
                page.set_content(html_content)
                page.wait_for_timeout(100)
                png_bytes = page.screenshot(type="png", omit_background=True)
                browser.close()

            overlay_img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
            if overlay_img.size != (1080, 1350):
                overlay_img = overlay_img.resize((1080, 1350), Image.Resampling.LANCZOS)
            return overlay_img

        except Exception as e:
            logger.error(f"Chromium 타이포그래피 오버레이 렌더링 실패: {e}")
            return Image.new("RGBA", (1080, 1350), (0, 0, 0, 0))

    def composite_slide(
        self,
        composite_photo: Image.Image,
        card_data: Dict[str, Any],
        s_idx: int,
        lang: str
    ) -> Image.Image:
        """
        EasyTax 슬라이드 합성:
        - composite_photo를 1080x1350 센터 크롭
        - 제미나이의 실시간 card_data 타이포그래피 오버레이를 알파 합성
        """
        canvas = Image.new("RGB", (1080, 1350), (11, 19, 43))
        W, H = composite_photo.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = composite_photo.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # EasyTax 제미나이 동적 타이포그래피 오버레이 합성
        overlay = self.render_overlay(
            card_data=card_data,
            s_idx=s_idx,
            lang=lang
        )

        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        return canvas
