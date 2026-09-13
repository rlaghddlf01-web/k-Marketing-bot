# -*- coding: utf-8 -*-
"""
KMarketCardNewsPipeline - 📸 [케이마켓 전용 고화질 카드뉴스 생산 공장]
- 1단계: '치아를 훤히 드러낸 활짝 웃는 환희' 사진 (스크롤 스톱 극대화)
- 2단계: 케이마켓 송금/나눔 UI 생성 후 OpenCV 서브픽셀 정밀 매립
- 3단계: 1080x1350 (4:5) 스마트 에메랄드(#00B074) 카드뉴스 캔버스 합성
- 4단계: 감각적인 헤드라인 + K-MARKET 인증 뱃지 + CTA 버튼 오버레이
- 5단계: 로컬 바탕화면 전용 출력
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from .ui_templates.remittance_template import RemittanceTemplate
from .scenarios.prompt_director_cardnews import PromptDirectorCardNewsKMarket


class KMarketCardNewsPipeline:
    """케이마켓 카드뉴스 자동 생산 파이프라인"""

    def __init__(self):
        self.embedder = PhoneScreenEmbedder()
        self.ui_template = RemittanceTemplate()
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")

    def produce(
        self,
        nationality_code: str = "vi",
        custom_master_image: Image.Image = None,
        output_filename: str = "kmarket_cardnews_master.png"
    ) -> str:
        """케이마켓 카드뉴스 1회 완성 실행"""
        # 1. 케이마켓 UI 생성
        ui_img = self.ui_template.render(title="K-MARKET 무료 나눔", amount=1500000)

        # 2. 마스터 이미지 (활짝 웃는 사진)
        if custom_master_image is not None:
            master_img = custom_master_image
        else:
            default_candidate = self.desktop / "vietnamese_deep_focus_presenter.png"
            if default_candidate.exists():
                master_img = Image.open(str(default_candidate))
            else:
                master_img = Image.open(str(self.desktop / "vietnamese_refund_completed.png"))

        # 3. OpenCV 정밀 액정 매립
        embedded_img = self.embedder.embed_screen(base_image=master_img, ui_image=ui_img)

        # 4. 1080x1350 (4:5) 카드뉴스 캔버스 합성
        canvas = Image.new("RGB", (1080, 1350), (16, 24, 32)) # 모던 다크 배경
        draw = ImageDraw.Draw(canvas)

        # 상단 70% 사진 배치 (1080 x 945)
        W, H = embedded_img.size
        scale = max(1080 / W, 945 / H)
        resized_photo = embedded_img.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)
        
        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 945) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 945))
        canvas.paste(photo_cropped, (0, 0))

        # 구분선: 3px 에메랄드 라인 (#00B074)
        draw.line([(0, 945), (1080, 945)], fill=(0, 176, 116), width=4)

        # 하단 30% 텍스트 컨테이너
        copy = PromptDirectorCardNewsKMarket.get_copywriting(nationality_code)

        font_head = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 46)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 26)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)

        # 뱃지 (상단 왼쪽)
        draw.rounded_rectangle([(60, 975), (380, 1015)], radius=8, fill=(0, 140, 90))
        draw.text((75, 982), copy["badge"], fill=(255, 255, 255), font=font_badge)

        # 헤드라인 (민트 에메랄드 컬러)
        draw.text((60, 1035), copy["headline"], fill=(0, 220, 140), font=font_head)

        # 서브카피 (화이트 컬러)
        draw.text((60, 1110), copy["subhead"], fill=(220, 225, 235), font=font_sub)

        # CTA 버튼 (하단 중앙)
        draw.rounded_rectangle([(60, 1190), (1020, 1280)], radius=16, fill=(0, 176, 116))
        bbox_cta = draw.textbbox((0, 0), copy["cta"], font=font_head)
        tw_cta = bbox_cta[2] - bbox_cta[0]
        draw.text(((1080 - tw_cta) // 2, 1205), copy["cta"], fill=(255, 255, 255), font=font_head)

        # 5. 로컬 데스크탑 전용 저장
        out_desktop = self.desktop / output_filename
        canvas.save(str(out_desktop), "PNG", quality=95)

        return str(out_desktop)
