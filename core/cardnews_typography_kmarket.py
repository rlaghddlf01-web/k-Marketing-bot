# -*- coding: utf-8 -*-
"""
CardnewsTypographyKMarket - 🛒 [K-Market 전용 1080x1350 시나리오 디렉터 & 제미나이 연동 무결점 타이포그래피 엔진]
- 시나리오 디렉터 및 제미나이가 실시간 창작한 card_data(제목, 부제, 불릿, 배지, CTA버튼)를 100% 동적 반영
- Playwright Chromium(Google HarfBuzz + Skia) 기반 전 언어 네이티브 무결점 텍스트 셰이핑
- 공식 브랜드 로고 배지 ([K] KTRS Market | 100% 안심 무료나눔) + 페이지 인덱스 (01 / 05 >)
- Slide 1, 2, 5: 하단 그라디언트 스크림 + 카테고리 배지 + 골드 헤드라인 + 서브타이틀 + 3줄 불릿 + 동적 CTA 버튼
- Slide 3, 4 (앱 순정 화면): 상단 64px 슬림 글래스모피즘 헤더 바 전용 레이아웃
"""

import html
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import io
from playwright.sync_api import sync_playwright

logger = logging.getLogger("CardnewsTypographyKMarket")

# 🌐 K-Market 브랜드 배지 100% 안심 무료나눔 다국어 사전 (17개국 전원 현지어 네이티브 매핑)
BRAND_SUB_I18N: Dict[str, str] = {
    "ko": "100% 안심 무료나눔",
    "en": "100% Safe Free Giveaway",
    "uz": "100% Xavfsiz Bepul Ulashish",
    "vi": "100% Miễn Phí An Toàn",
    "km": "ចែកជូនឥតគិតថ្លៃ ១០០% មានសុវត្ថិភាព",
    "th": "แจกฟรีปลอดภัย 100%",
    "id": "100% Gratis & Aman",
    "my": "၁၀၀% စိတ်ချရသော အခမဲ့",
    "ne": "१००% सुरक्षित नि:शुल्क",
    "mn": "100% Аюулгүй Үнэгүй",
    "ru": "100% Безопасно и Бесплатно",
    "zh": "100% 安心免费转赠",
    "ja": "100% 安心無料譲渡",
    "tl": "100% Ligtas at Libreng Pamimigay",
    "bn": "১০০% নিরাপদ বিনামূল্যে উপহার",
    "si": "100% ආරක්ෂිත නොමිලේ බෙදාහැරීම",
    "hi": "100% सुरक्षित निःशुल्क उपहार",
    "ur": "100% محفوظ مفت تحفہ",
    "ar": "توزيع مجاني آمن 100%",
    "fr": "100% Gratuit et Sécurisé",
    "es": "100% Gratis y Seguro",
}

# 🌐 CTA 버튼 다국어 폴백 (제미나이 생성 실패 시 대비 안전망)
DEFAULT_CTA_I18N: Dict[str, Dict[str, str]] = {
    "ko": {"view": "자세히 보기 >", "action": "지금 확인하기 >"},
    "en": {"view": "Learn More >", "action": "Claim Now >"},
    "uz": {"view": "Batafsil ko'rish >", "action": "Hozir olish >"},
    "vi": {"view": "Xem chi tiết >", "action": "Nhận ngay >"},
    "km": {"view": "មើលលម្អិត >", "action": "ទទួលយកឥឡូវនេះ >"},
    "th": {"view": "ดูรายละเอียด >", "action": "รับทันที >"},
    "id": {"view": "Lihat detail >", "action": "Klaim sekarang >"},
    "my": {"view": "အသေးစိတ်ကြည့်ရန် >", "action": "ယခုရယူရန် >"},
    "ne": {"view": "थप हेर्नुहोस् >", "action": "अहिले नै लिनुहोस् >"},
    "mn": {"view": "Дэлгэрэнгүй >", "action": "Одоо авах >"},
    "ru": {"view": "Подробнее >", "action": "Получить сейчас >"},
    "zh": {"view": "查看详情 >", "action": "立即领取 >"},
    "ja": {"view": "詳細を見る >", "action": "今すぐ確認 >"},
}


class CardnewsTypographyKMarket:
    """K-Market 전용 카드뉴스 고해상도 무결점 타이포그래피 렌더러 (제미나이 100% 동적 주입)"""

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
        page_badge = f"{s_idx:02d} / 05 >"

        # 🌟 Slide 3 & 4 (앱 순정 화면): 상단 64px 슬림 글래스모피즘 헤더 바 (앱 본문 시야 100% 보존)
        if s_idx in (3, 4):
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
                    }}
                    .slim-header-bar {{
                        width: 100%;
                        height: 32px;
                        background: rgba(15, 23, 42, 0.90);
                        backdrop-filter: blur(8px);
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: 0 14px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.4);
                        border-bottom: 1px solid rgba(255,255,255,0.1);
                    }}
                    .left-badge-group {{
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    .brand-mini {{
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        color: #ffffff;
                        font-weight: 800;
                        font-size: 11px;
                    }}
                    .brand-mini .k-dot {{
                        width: 14px;
                        height: 14px;
                        background: #ea580c;
                        border-radius: 3px;
                        color: #fff;
                        font-weight: 900;
                        font-size: 9px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .step-badge {{
                        background: #ea580c;
                        color: #ffffff;
                        font-weight: 800;
                        font-size: 10px;
                        padding: 2px 8px;
                        border-radius: 4px;
                        letter-spacing: -0.2px;
                    }}
                    .page-index {{
                        color: #f59e0b;
                        font-weight: 800;
                        font-size: 11px;
                        letter-spacing: 0.5px;
                    }}
                </style>
            </head>
            <body>
                <div class="slim-header-bar">
                    <div class="left-badge-group">
                        <div class="brand-mini">
                            <span class="k-dot">K</span>
                            <span>KTRS Market</span>
                        </div>
                        <div class="step-badge">{html.escape(badge)}</div>
                    </div>
                    <div class="page-index">{page_badge}</div>
                </div>
            </body>
            </html>"""
            return self._render_html_to_image(overlay_html)

        # 🌟 Slide 1, 2, 5: 하단 스크림 + 카테고리 배지 + 헤드라인 + 서브타이틀 + 3줄 불릿 + 동적 CTA 버튼
        # 100% 제미나이가 실시간 창작한 데이터 직접 연동
        title = card_data.get("title", "")
        subtitle = card_data.get("subtitle", "")
        bullets = card_data.get("bullets", [])

        # 🎯 브랜드 배지 서브텍스트 및 CTA 버튼: 100% 타깃 현지어 자동 매핑
        norm_lang = (lang or "en").lower().strip()
        brand_sub_text = BRAND_SUB_I18N.get(norm_lang, BRAND_SUB_I18N.get("en", "100% Safe Free Giveaway"))

        # CTA 버튼 텍스트: 제미나이가 작성한 cta_button 우선 적용 (없을 시 타깃 언어 fallback)
        cta_fallbacks = DEFAULT_CTA_I18N.get(norm_lang, DEFAULT_CTA_I18N.get("en", {"view": "Learn More >", "action": "Claim Now >"}))
        fallback_btn = cta_fallbacks["view"] if s_idx not in (1, 5) else cta_fallbacks["action"]
        btn_text = card_data.get("cta_button") or fallback_btn

        cta_bg = "#ea580c" if s_idx in (1, 5) else "#1e293b"
        cta_color = "#ffffff"
        badge_bg = "#ea580c"
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

                /* 상단 K-Market 브랜드 헤더 */
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
                    background: rgba(15, 23, 42, 0.82);
                    backdrop-filter: blur(8px);
                    padding: 6px 14px;
                    border-radius: 24px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
                }}
                .brand-badge .k-logo {{
                    width: 20px;
                    height: 20px;
                    background: #ea580c;
                    border-radius: 5px;
                    color: #fff;
                    font-weight: 900;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .brand-badge .brand-text {{
                    color: #ffffff;
                    font-weight: 800;
                    font-size: 13.5px;
                    letter-spacing: -0.3px;
                }}
                .brand-badge .brand-sub {{
                    color: #94a3b8;
                    font-weight: 600;
                    font-size: 10.5px;
                    padding-left: 4px;
                    border-left: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .page-index {{
                    color: #f59e0b;
                    font-weight: 800;
                    font-size: 13px;
                    background: rgba(15, 23, 42, 0.75);
                    padding: 5px 12px;
                    border-radius: 16px;
                    border: 1px solid rgba(245, 158, 11, 0.3);
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

                /* 카테고리/단계 배지 */
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

                /* 하단 CTA 버튼 */
                .cta-button {{
                    width: 100%;
                    background: linear-gradient(135deg, {cta_bg} 0%, #c2410c 100%);
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
                <div class="brand-badge">
                    <span class="k-logo">K</span>
                    <span class="brand-text">KTRS Market</span>
                    <span class="brand-sub">{html.escape(brand_sub_text)}</span>
                </div>
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
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-gpu", "--disable-software-rasterizer", "--disable-dev-shm-usage"]
                )
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
        base_photo: Image.Image,
        card_data: Dict[str, Any],
        s_idx: int,
        lang: str
    ) -> Image.Image:
        """
        K-Market 슬라이드 합성:
        - base_photo를 1080x1350 센터 크롭
        - 제미나이의 실시간 card_data 타이포그래피 오버레이를 알파 합성
        """
        canvas = Image.new("RGB", (1080, 1350), (15, 23, 42))
        W, H = base_photo.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = base_photo.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # K-Market 제미나이 동적 타이포그래피 오버레이 합성
        overlay = self.render_overlay(
            card_data=card_data,
            s_idx=s_idx,
            lang=lang
        )

        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        return canvas
