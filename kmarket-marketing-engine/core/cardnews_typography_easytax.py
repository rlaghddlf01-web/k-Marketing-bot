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


# 🌐 EasyTax 브랜드 배지 100% 안심 후불제 다국어 사전 (17개국 전원 현지어 네이티브 매핑)
EASYTAX_BRAND_SUB_I18N: Dict[str, str] = {
    "ko": "100% 안심 후불제",
    "en": "100% Safe Pay-After-Refund",
    "uz": "100% Xavfsiz Keyin To'lash",
    "vi": "100% Trả sau an tâm",
    "km": "ទូទាត់ក្រោយដោយសុវត្ថិភាព ១០០%",
    "th": "จ่ายทีหลังปลอดภัย 100%",
    "id": "100% Bayar Setelah Cair Aman",
    "my": "၁၀၀% စိတ်ချရသော နောက်မှပေးချေမှု",
    "ne": "१००% सुरक्षित पछि भुक्तानी",
    "mn": "100% Баталгаат Дараа Төлбөр",
    "ru": "100% Безопасная постоплата",
    "zh": "100% 先退税后付费",
    "ja": "100% 安心後払い制",
    "tl": "100% Ligtas na Bayad-Mamaya",
    "bn": "১০০% নিরাপদ পরবর্তীতে পরিশোধ",
    "si": "100% ආරක්ෂිත පසුව ගෙවීම",
    "hi": "100% सुरक्षित बाद में भुगतान",
    "ur": "100% محفوظ بعد میں ادائیگی",
    "ar": "دفع لاحق آمن 100%",
    "fr": "Paiement après remboursement 100% sécurisé",
    "es": "Pago posterior 100% seguro",
}


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

        # 🎯 브랜드 배지 서브텍스트: 100% 타깃 현지어 안심 후불제 자동 매핑
        norm_lang = (lang or "en").lower().strip()
        brand_sub_text = EASYTAX_BRAND_SUB_I18N.get(
            norm_lang, EASYTAX_BRAND_SUB_I18N.get("en", "100% Safe Pay-After-Refund")
        )

        # KTRS 브랜드 로고 헤더
        brand_logo_html = f"""
            <div class="brand-badge brand-easytax">
                <span class="brand-icon">🏛️</span>
                <span class="brand-text">KTRS</span>
                <span class="brand-sub">{html.escape(brand_sub_text)}</span>
            </div>
        """
        page_badge = f"{s_idx:02d} / 05 >"

        # CTA 버튼 텍스트: 제미나이가 실시간 창작한 cta_button 연동
        btn_text = card_data.get("cta_button") or ("다음 내용 보기 >" if s_idx not in (1, 5) else "내 환급금 조회하기 >")

        # EasyTax 테마: 1~5번 전 슬라이드 럭셔리 골드(노랑) CTA 버튼 100% 통일
        cta_bg = "#d4af37"
        cta_color = "#0b132b"
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

                /* 하단 그라디언트 스크림 및 콘텐츠 컨테이너 (85% 걷어낸 초경량 소프트 비네팅) */
                .bottom-scrim {{
                    width: 100%;
                    background: linear-gradient(
                        180deg,
                        rgba(0, 0, 0, 0) 0%,
                        rgba(0, 0, 0, 0.15) 30%,
                        rgba(15, 23, 42, 0.35) 100%
                    );
                    padding: 20px 24px 22px;
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
                    font-size: 12.5px;
                    padding: 4px 12px;
                    border-radius: 6px;
                    letter-spacing: -0.2px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.5);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    margin-bottom: 2px;
                }}

                /* 🌟 [골드 입체 테두리 & 3D 딥 섀도우 헤드라인] */
                .headline-title {{
                    font-size: 23px;
                    font-weight: 900;
                    color: #ffd700;
                    line-height: 1.3;
                    -webkit-text-stroke: 3.5px #0a0f1d;
                    paint-order: stroke fill;
                    text-shadow: 0 4px 14px rgba(0, 0, 0, 0.95), 0 2px 4px rgba(0, 0, 0, 0.9);
                    letter-spacing: -0.4px;
                    word-break: break-word;
                }}

                /* 서브타이틀 */
                .subtitle-text {{
                    font-size: 13px;
                    font-weight: 700;
                    color: #ffffff;
                    line-height: 1.4;
                    -webkit-text-stroke: 2px #0a0f1d;
                    paint-order: stroke fill;
                    text-shadow: 0 3px 10px rgba(0, 0, 0, 0.95);
                    letter-spacing: -0.2px;
                    word-break: break-word;
                }}

                /* 3줄 불릿 리스트 */
                .bullets-list {{
                    display: flex;
                    flex-direction: column;
                    gap: 3px;
                    margin: 2px 0 4px;
                }}
                .bullet-item {{
                    display: flex;
                    align-items: baseline;
                    gap: 6px;
                    font-size: 12px;
                    font-weight: 700;
                    color: #ffffff;
                    line-height: 1.35;
                    -webkit-text-stroke: 1.8px #0a0f1d;
                    paint-order: stroke fill;
                    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95);
                }}
                .bullet-dot {{
                    color: #38bdf8;
                    font-weight: 900;
                    font-size: 13px;
                    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9);
                }}
                .bullet-text {{
                    word-break: break-word;
                }}

                /* 하단 CTA 버튼 (선명한 노랑/골드) */
                .cta-button {{
                    width: 100%;
                    background: {cta_bg};
                    color: {cta_color};
                    font-size: 15px;
                    font-weight: 800;
                    padding: 11px 20px;
                    border-radius: 12px;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
                    letter-spacing: -0.2px;
                    margin-top: 3px;
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

        # 상단 머리 위 공간감(Headroom) 보존 크롭 (상단 여백 80% 유지, 하단 텍스트 영역 우선 수용)
        crop_x = (resized_photo.width - 1080) // 2
        crop_y = max(0, min(int((resized_photo.height - 1350) * 0.25), resized_photo.height - 1350))
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
