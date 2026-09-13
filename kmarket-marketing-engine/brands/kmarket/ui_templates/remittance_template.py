# -*- coding: utf-8 -*-
"""
RemittanceTemplate - 📱 [케이마켓 전용 모바일 앱 및 해외 송금/나눔 UI 템플릿]
- 케이마켓 고유 브랜드 컬러(스마트 에메랄드 #00B074 & 모던 화이트)
- 해외 송금 완료 / 무료 생활 나눔 / 월급 입금 내역 동적 렌더링
- 스마트폰 액정 규격(469 x 1024, 1:2.18 비율) 최적화
"""

from PIL import Image, ImageDraw, ImageFont


class RemittanceTemplate:
    """케이마켓 모바일 UI 생성기"""

    def render(self, title: str = "해외 송금 완료", amount: int = 1500000) -> Image.Image:
        """케이마켓 전용 모바일 화면을 469x1024로 생성"""
        W, H = 469, 1024
        ui = Image.new("RGBA", (W, H), (246, 248, 250, 255))
        draw = ImageDraw.Draw(ui)

        # 1. 상단 상태바
        font_status = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 22)
        draw.text((35, 16), "9:41", fill=(20, 24, 32, 255), font=font_status)

        # 2. 상단 헤더
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 32)
        bbox = draw.textbbox((0, 0), title, font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 80), title, fill=(15, 20, 28, 255), font=font_title)

        # 3. 성공 카드
        draw.rounded_rectangle([(30, 140), (439, 255)], radius=18, fill=(255, 255, 255, 255))
        font_brand = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 24)
        font_desc = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 19)
        draw.text((50, 165), "K-MARKET 공식 나눔·송금", fill=(0, 168, 108, 255), font=font_brand)
        draw.text((50, 205), "수수료 0원으로 안전하게 완료되었습니다.", fill=(70, 80, 95, 255), font=font_desc)

        # 4. 금액 메인 카드
        draw.rounded_rectangle([(30, 275), (439, 615)], radius=22, fill=(255, 255, 255, 255))
        font_lbl = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 24)
        bbox_lbl = draw.textbbox((0, 0), "절약 / 송금 금액", font=font_lbl)
        tw_lbl = bbox_lbl[2] - bbox_lbl[0]
        draw.text(((W - tw_lbl) // 2, 325), "절약 / 송금 금액", fill=(90, 100, 115, 255), font=font_lbl)

        font_amt = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 52)
        amt_str = f"₩{amount:,}"
        bbox_amt = draw.textbbox((0, 0), amt_str, font=font_amt)
        tw_amt = bbox_amt[2] - bbox_amt[0]
        draw.text(((W - tw_amt) // 2, 375), amt_str, fill=(15, 20, 28, 255), font=font_amt)

        # 수신자 정보 구분선
        draw.line([(55, 465), (414, 465)], fill=(230, 235, 240, 255), width=2)
        font_row = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 21)
        draw.text((55, 490), "수신 국가", fill=(90, 100, 115, 255), font=font_row)
        draw.text((300, 490), "베트남(VND)", fill=(15, 20, 28, 255), font=font_row)
        draw.text((55, 545), "이용 수수료", fill=(90, 100, 115, 255), font=font_row)
        draw.text((335, 545), "0원 (무료)", fill=(0, 168, 108, 255), font=font_row)

        # 5. 최근 나눔/거래 섹션
        font_section = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 24)
        draw.text((35, 645), "K-MARKET 실시간 나눔", fill=(80, 90, 105, 255), font=font_section)
        draw.rounded_rectangle([(30, 685), (439, 820)], radius=18, fill=(255, 255, 255, 255))
        draw.text((50, 715), "쿠쿠 압력밥솥 + 식기 나눔", fill=(15, 20, 28, 255), font=font_brand)
        draw.text((50, 760), "서울 구로구 이웃 직거래", fill=(90, 100, 115, 255), font=font_desc)
        draw.text((360, 725), "0원", fill=(0, 168, 108, 255), font=font_brand)

        # 홈 인디케이터
        draw.rounded_rectangle([(165, 1005), (304, 1011)], radius=3, fill=(0, 0, 0, 255))
        return ui
