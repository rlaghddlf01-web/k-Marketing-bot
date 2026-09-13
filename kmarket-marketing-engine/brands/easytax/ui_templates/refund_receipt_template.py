# -*- coding: utf-8 -*-
"""
RefundReceiptTemplate - 🧾 [이지택스 국세청 세금 환급 영수증 템플릿]
- 환급 금액(예: 3,100,000원, 2,850,000원 등)을 자유자재로 동적 렌더링
- 카드 배경색 및 행 배경색과 100% 일치하는 무결점 배경 처리
- Segoe UI Bold 및 Malgun Gothic Bold 타이포그래피 정렬
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class RefundReceiptTemplate:
    """이지택스 세금 환급 스마트폰 UI 생성기"""

    def __init__(self, base_image_path: str = None):
        if base_image_path is None:
            base_image_path = os.path.join(os.path.dirname(__file__), "base_refund_ui.png")
        self.base_image_path = base_image_path

    def render(self, amount: int = 3100000) -> Image.Image:
        """
        금액을 입력받아 완벽하게 리마스터된 영수증 UI 이미지를 반환
        """
        ui = Image.open(self.base_image_path).convert("RGBA")
        draw = ImageDraw.Draw(ui)

        formatted_amount = f"₩{amount:,}"
        formatted_tx = f"+{amount:,}원"

        # 1. 상단 카드 금액 렌더링
        # 카드 배경색 (243, 243, 243)으로 기존 텍스트 완벽 지우기
        draw.rectangle([(70, 368), (420, 458)], fill=(243, 243, 243, 255))
        font_amt = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 48)

        bbox_amt = draw.textbbox((0, 0), formatted_amount, font=font_amt)
        tw_amt = bbox_amt[2] - bbox_amt[0]
        draw.text(((469 - tw_amt) // 2, 385), formatted_amount, fill=(30, 30, 32, 255), font=font_amt)

        # 2. 하단 거래 내역 금액 렌더링
        # 행 배경색 (242, 244, 243)으로 기존 녹색 텍스트 완벽 지우기
        draw.rectangle([(250, 735), (460, 800)], fill=(242, 244, 243, 255))
        font_tx = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 24)

        bbox_tx = draw.textbbox((0, 0), formatted_tx, font=font_tx)
        tw_tx = bbox_tx[2] - bbox_tx[0]
        draw.text((445 - tw_tx, 755), formatted_tx, fill=(42, 142, 92, 255), font=font_tx)

        return ui
