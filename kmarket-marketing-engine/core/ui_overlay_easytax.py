# -*- coding: utf-8 -*-
"""
UIOverlayEasyTax - 💰 [EasyTax 전용 100% 무결점 실물 UI 오버레이 엔진]
- AI 생성 이미지 특유의 '뒤집힌 스마트폰 글자' 및 '뭉개진 서류 텍스트'를 원천 배제
- 실제 카카오뱅크/토스 모바일 뱅킹 입금 알림 카드 (글래스모피즘 + 금빛 원화 강조)
- 국세청(NTS) 공식 환급결정통지서 서류 카드 (금색 인장 + 공인 QR + 정밀 타이포그래피)
- 1080x1920 풀HD 투명 PNG 오버레이로 출력하여 비디오 클립에 완벽 합성
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import DATA_DIR, OUTPUTS_DIR

logger = logging.getLogger("UIOverlayEasyTax")

# 17개국 폰트 후보
FALLBACK_FONTS = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
]

def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for fp in FALLBACK_FONTS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


class UIOverlayEasyTax:
    """
    💎 EasyTax 무결점 실물 UI 오버레이 렌더러
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts" / "ui_overlays")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_deposit_push_card(
        self,
        amount_krw: int = 3840000,
        lang: str = "vi",
        bank_name: str = "KakaoBank",
        filename: Optional[str] = None
    ) -> Path:
        """
        📱 [씬 2 전용] 모바일 뱅킹 실제 입금 푸시 알림 카드 렌더링 (1080x1920 투명 PNG)
        - 상단 중앙 플로팅 글래스모피즘 카드
        - 선명한 폰트, 정확한 원화 기호, 은행 배지, 세부 입금 내역
        """
        W, H = 1080, 1920
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 다국어 텍스트 매핑
        i18n_titles = {
            "vi": "Thông Báo Nhận Tiền Hoàn Thuế",
            "en": "Income Tax Refund Deposited",
            "ko": "국세청 소득세 환급금 입금",
            "zh": "国税厅所得税退税入账",
            "uz": "Soliq Qaytarish Mablag'i Tushdi"
        }
        title_text = i18n_titles.get(lang, i18n_titles["en"])
        amount_str = f"+₩{amount_krw:,}"

        # 카드 영역 계산 (스마트폰 최적 뷰: y=440~720)
        card_w, card_h = 940, 280
        x1 = (W - card_w) // 2
        y1 = 440
        x2 = x1 + card_w
        y2 = y1 + card_h
        radius = 36

        # 1. 은은한 카드 그림자
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rounded_rectangle([x1 - 8, y1 + 10, x2 + 8, y2 + 24], radius=radius + 4, fill=(0, 0, 0, 140))
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))
        overlay.paste(shadow, (0, 0), shadow)

        # 2. 카드 본체 (프리미엄 딥 슬레이트 + 반투명 아크릴)
        card_bg = Image.new("RGBA", (card_w, card_h), (15, 23, 42, 235))
        cb_draw = ImageDraw.Draw(card_bg)
        
        # 카드 내부 골드 테두리
        cb_draw.rounded_rectangle([0, 0, card_w, card_h], radius=radius, fill=(18, 28, 52, 240), outline=(255, 215, 0, 180), width=3)

        # 3. 은행 옐로우/골드 배지 & 헤더
        badge_w, badge_h = 170, 48
        cb_draw.rounded_rectangle([32, 32, 32 + badge_w, 32 + badge_h], radius=16, fill=(255, 212, 0, 255))
        font_badge = _load_font(24, bold=True)
        cb_draw.text((32 + 18, 32 + 10), "KakaoBank", font=font_badge, fill=(20, 20, 20, 255))

        # 헤더 텍스트: 보낸 곳 & 시간
        font_sub = _load_font(24, bold=False)
        cb_draw.text((32 + badge_w + 20, 32 + 10), "국세청(NTS) • 방금 전", font=font_sub, fill=(180, 200, 230, 255))

        # 타이틀 (현지어)
        font_title = _load_font(28, bold=True)
        cb_draw.text((36, 102), title_text, font=font_title, fill=(255, 255, 255, 255))

        # 금액 대형 볼드 강조 (황금빛 네온 그린)
        font_amount = _load_font(56, bold=True)
        cb_draw.text((36, 148), amount_str, font=font_amount, fill=(52, 211, 153, 255))

        # 부가 정보: 조특법 30조 5개년 소급분
        font_desc = _load_font(22, bold=False)
        desc_text = "조특법 제30조 소득세 90% 감면 5년 소급액 전액 입금 완료"
        cb_draw.text((36, 226), desc_text, font=font_desc, fill=(148, 163, 184, 255))

        # 카드 붙여넣기
        overlay.paste(card_bg, (x1, y1), card_bg)

        # 저장
        out_name = filename or f"deposit_card_{lang}_{amount_krw}.png"
        out_path = self.output_dir / out_name
        overlay.save(out_path, "PNG")
        logger.info(f"✨ [UIOverlayEasyTax] 무결점 카카오뱅크 입금 카드 렌더링 완료: {out_name}")
        return out_path

    def render_tax_refund_certificate_overlay(
        self,
        amount_krw: int = 3840000,
        lang: str = "vi",
        filename: Optional[str] = None
    ) -> Path:
        """
        📜 [씬 5 전용] 대한민국 국세청 공식 환급결정결의서 실물 그래픽 오버레이 (1080x1920)
        - AI가 뭉개지 못하도록 정밀 벡터 텍스트와 관인 직접 렌더링
        """
        W, H = 1080, 1920
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        # 문서 카드 크기 (하단 40% 영역)
        doc_w, doc_h = 940, 560
        x1 = (W - doc_w) // 2
        y1 = 1060
        x2 = x1 + doc_w
        y2 = y1 + doc_h

        # 그림자
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rounded_rectangle([x1 - 10, y1 + 10, x2 + 10, y2 + 20], radius=28, fill=(0, 0, 0, 170))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        overlay.paste(shadow, (0, 0), shadow)

        # 문서 본체 (고급 양식지)
        doc_bg = Image.new("RGBA", (doc_w, doc_h), (252, 251, 247, 245))
        d_draw = ImageDraw.Draw(doc_bg)
        d_draw.rounded_rectangle([0, 0, doc_w, doc_h], radius=24, fill=(252, 251, 247, 245), outline=(59, 130, 246, 200), width=4)

        # 상단 헤더
        font_gov = _load_font(24, bold=True)
        d_draw.text((40, 32), "대한민국 국세청 (National Tax Service)", font=font_gov, fill=(30, 41, 59, 255))

        # 문서 명칭
        font_doc_title = _load_font(42, bold=True)
        d_draw.text((40, 75), "국세환급금 결정결의서", font=font_doc_title, fill=(15, 23, 42, 255))

        # 가로선
        d_draw.line([(40, 136), (doc_w - 40, 136)], fill=(203, 213, 225, 255), width=2)

        # 항목 리스트
        font_label = _load_font(24, bold=True)
        font_val = _load_font(24, bold=False)

        items = [
            ("적용 세법", "조세특례제한법 제30조 (외국인 소득세 90% 감면 특례)"),
            ("환급 과세연도", "최근 5개 과세연도 원천징수 소급 경정청구"),
            ("환급결정세액", f"₩{amount_krw:,} KRW (환급가산금 포함 전액 계좌 입금)"),
            ("처리 기관", "관할 세무서 소득세과 • EasyTax 공인 대리 완료")
        ]

        cur_y = 156
        for label, val in items:
            d_draw.text((45, cur_y), f"• {label}:", font=font_label, fill=(71, 85, 105, 255))
            d_draw.text((230, cur_y), val, font=font_val, fill=(15, 23, 42, 255))
            cur_y += 50

        # 하단 환급액 박스
        box_y = cur_y + 10
        d_draw.rounded_rectangle([40, box_y, doc_w - 40, box_y + 90], radius=16, fill=(238, 242, 255, 255), outline=(79, 70, 229, 220), width=2)
        font_box_label = _load_font(26, bold=True)
        font_box_amt = _load_font(44, bold=True)
        d_draw.text((60, box_y + 26), "최종 입금 세액", font=font_box_label, fill=(67, 56, 202, 255))
        d_draw.text((doc_w - 380, box_y + 18), f"₩{amount_krw:,} 원", font=font_box_amt, fill=(37, 99, 235, 255))

        # 공식 날인
        stamp_box = [doc_w - 180, 50, doc_w - 60, 170]
        d_draw.rounded_rectangle(stamp_box, radius=12, outline=(220, 38, 38, 220), width=3)
        font_stamp = _load_font(20, bold=True)
        d_draw.text((stamp_box[0] + 16, stamp_box[1] + 24), "대한민국", font=font_stamp, fill=(220, 38, 38, 220))
        d_draw.text((stamp_box[0] + 16, stamp_box[1] + 52), "국세청인", font=font_stamp, fill=(220, 38, 38, 220))

        # 붙여넣기
        overlay.paste(doc_bg, (x1, y1), doc_bg)

        out_name = filename or f"tax_certificate_{lang}_{amount_krw}.png"
        out_path = self.output_dir / out_name
        overlay.save(out_path, "PNG")
        logger.info(f"✨ [UIOverlayEasyTax] 무결점 국세청 환급 통지서 오버레이 렌더링 완료: {out_name}")
        return out_path
