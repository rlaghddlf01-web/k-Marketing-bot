# -*- coding: utf-8 -*-
"""
PhoneAppScreenRenderer - 📱 [실제 은행 앱 환급 화면 15개국어 정밀 벡터 렌더러]
- 대표님 레퍼런스(NH BANK / KakaoBank) 100% 완벽 재현
- 상단 상태바 (9:41, WiFi, 배터리) + 은행 네비게이션 헤더 + 은행 로고
- 15개 언어별 세무 환급 완료 타이틀 + 대형 환급 금액(KRW) + 수령자 ID + 파란색 체크 인증 마크
- 아이폰/갤럭시 최신 플래그십 슬림 베젤 & 라운드 글래스 스크린 에셋 출력
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import DATA_DIR, OUTPUTS_DIR

logger = logging.getLogger("PhoneAppScreenRenderer")

# 17개국 폰트 후보
FALLBACK_FONTS = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
]

def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for fp in FALLBACK_FONTS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

# 15개 언어별 실제 은행 환급 화면 텍스트 사전
BANK_REFUND_I18N: Dict[str, Dict[str, str]] = {
    "uz": {
        "bank_name": "NH BANK",
        "title": "[SOLIQNI\nQAYTARISH\nMAVJUD]",
        "desc": "To'landi ID: NTS_KR",
        "status": "Muvaffaqiyatli to'landi"
    },
    "vi": {
        "bank_name": "NH BANK",
        "title": "[HOÀN THUẾ\nĐÃ VỀ TÀI KHOẢN\nTHÀNH CÔNG]",
        "desc": "Người nhận: Lao động E-9",
        "status": "Đã giải ngân từ Cục Thuế"
    },
    "en": {
        "bank_name": "NH BANK",
        "title": "[INCOME TAX\nREFUND DEPOSIT\nCONFIRMED]",
        "desc": "Deposited by: National Tax Service",
        "status": "Transfer Completed"
    },
    "ko": {
        "bank_name": "NH농협은행",
        "title": "[국세환급금\n소득세 90% 감면\n입금 완료]",
        "desc": "입금처: 대한민국 국세청",
        "status": "정상 계좌 입금 완료"
    },
    "zh": {
        "bank_name": "NH 农协银行",
        "title": "[国税退税\n所得税90%减免\n已成功入账]",
        "desc": "汇款方: 韩国国税厅(NTS)",
        "status": "转账已完成"
    },
    "ru": {
        "bank_name": "NH BANK",
        "title": "[ВОЗВРАТ НАЛОГА\nУСПЕШНО\nПОСТУПИЛ]",
        "desc": "Отправитель: Налоговая служба",
        "status": "Платеж выполнен"
    },
    "mn": {
        "bank_name": "NH BANK",
        "title": "[ТАТВАРЫН БУЦААН\nОЛГОЛТ ДАНСАНД\nОРЛОО]",
        "desc": "Хүлээн авагч: E-9 Ажилтан",
        "status": "Гүйлгээ амжилттай"
    },
    "th": {
        "bank_name": "NH BANK",
        "title": "[เงินคืนภาษี\nโอนเข้าบัญชี\nเรียบร้อยแล้ว]",
        "desc": "ผู้โอน: กรมสรรพากรเกาหลี",
        "status": "โอนเงินสำเร็จ"
    },
    "id": {
        "bank_name": "NH BANK",
        "title": "[PENGEMBALIAN\nPAJAK BERHASIL\nDICAIRKAN]",
        "desc": "Pengirim: National Tax Service",
        "status": "Dana Berhasil Masuk"
    },
    "tl": {
        "bank_name": "NH BANK",
        "title": "[NA-DEPOSIT NA\nANG TAX REFUND\nSA ACCOUNT MO]",
        "desc": "Sender: Korean Tax Office",
        "status": "Matagumpay na Na-transfer"
    },
    "ne": {
        "bank_name": "NH BANK",
        "title": "[कर फिर्ता रकम\nखातामा जम्मा\nभएको छ]",
        "desc": "पठाउने: कोरियाली कर कार्यालय",
        "status": "रकम ट्रान्सफर सम्पन्न"
    },
    "my": {
        "bank_name": "NH BANK",
        "title": "[အခွန်ပြန်အမ်းငွေ\nဘဏ်စာရင်းသို့\nဝင်ရောက်ပြီး]",
        "desc": "လွှဲပို့သူ: အမျိုးသားအခွန်ဌာန",
        "status": "ငွေလွှဲအောင်မြင်သည်"
    },
    "km": {
        "bank_name": "NH BANK",
        "title": "[ប្រាក់ពន្ធបានត្រឡប់\nចូលគណនី\nដោយជោគជ័យ]",
        "desc": "អ្នកផ្ញើ: អគ្គនាយកដ្ឋានពន្ធដារ",
        "status": "ការផ្ទេរប្រាក់បានជោគជ័យ"
    },
    "si": {
        "bank_name": "NH BANK",
        "title": "[බදු මුදල් ආපසු\nගිණුමට බැර\nකර ඇත]",
        "desc": "යවන්නා: කොරියානු බදු කාර්යාලය",
        "status": "සාර්ථකව තැන්පත් කරන ලදී"
    },
    "ur": {
        "bank_name": "NH BANK",
        "title": "[ٹیکس ریفنڈ رقم\nاکاؤنٹ میں جمع\nہو گئی]",
        "desc": "بھیجنے والا: کورین ٹیکس سروس",
        "status": "منتقلی مکمل ہو گئی"
    }
}


class PhoneAppScreenRenderer:
    """
    📱 대표님 레퍼런스 스타일 실제 스마트폰 은행 앱 화면 렌더러
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "cardnews" / "phone_screens")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_bank_phone_screen(
        self,
        amount_krw: int = 4250000,
        lang: str = "vi",
        user_name: str = "NGUYEN VAN T.",
        width: int = 480,
        height: int = 960
    ) -> Path:
        """
        대표님 예시 사진과 100% 동일한 NH농협 모바일 뱅킹 세무 환급 화면 렌더링
        - 규격: width × height (비율 약 1:2 스마트폰 액정 화면)
        - 깔끔한 화이트 바디 + 상단 네이비 바 + 노란색 NH 로고 + 선명한 볼드 타이틀 + 체크 서클
        """
        data = BANK_REFUND_I18N.get(lang, BANK_REFUND_I18N["en"])
        bank_name = data.get("bank_name", "NH BANK")
        title_lines = data.get("title", "[SOLIQNI\nQAYTARISH\nMAVJUD]").split("\n")
        desc_text = data.get("desc", f"ID: {user_name}")

        # 포맷팅된 금액 (천 단위 공백 또는 쉼표 구분: 예 4 250 000 KRW)
        amount_formatted = f"{amount_krw:,}".replace(",", " ") + " KRW"

        # 1. 고해상도 액정 캔버스 (스마트폰 곡면 스크린)
        screen = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(screen)

        # 2. 상단 네이비 헤더 바 (y: 0 ~ 130px)
        header_h = int(height * 0.135)
        draw.rectangle([(0, 0), (width, header_h)], fill=(28, 64, 138, 255))  # NH 네이비 블루 (#1C408A)

        # 상태바 (9:41, 와이파이, 배터리)
        font_status = _load_font(int(width * 0.04), bold=True)
        draw.text((int(width * 0.08), int(height * 0.022)), "9:41", font=font_status, fill=(255, 255, 255, 240))
        
        # 배터리 & 신호 아이콘 간단 벡터
        bat_x, bat_y = int(width * 0.82), int(height * 0.024)
        draw.rounded_rectangle([bat_x, bat_y, bat_x + 36, bat_y + 18], radius=4, outline=(255, 255, 255, 220), width=2)
        draw.rectangle([bat_x + 3, bat_y + 3, bat_x + 28, bat_y + 15], fill=(255, 255, 255, 220))
        draw.rectangle([bat_x + 37, bat_y + 6, bat_x + 39, bat_y + 12], fill=(255, 255, 255, 220))

        # 뒤로가기 화살표 '<'
        font_back = _load_font(int(width * 0.055), bold=True)
        draw.text((int(width * 0.06), int(height * 0.07)), "<", font=font_back, fill=(255, 255, 255, 255))

        # 헤더 중앙 'NH BANK'
        font_header_bank = _load_font(int(width * 0.045), bold=True)
        hb_bbox = draw.textbbox((0, 0), bank_name, font=font_header_bank)
        hb_w = hb_bbox[2] - hb_bbox[0]
        draw.text(((width - hb_w) // 2, int(height * 0.075)), bank_name, font=font_header_bank, fill=(255, 255, 255, 255))

        # 3. 화이트 카드 본체 상단 농협 앰블럼 (노란색/오렌지 날개 로고)
        logo_y = header_h + int(height * 0.045)
        # 로고 아이콘 (노란색 황금 심볼)
        logo_x = int(width * 0.08)
        draw.ellipse([logo_x, logo_y, logo_x + 40, logo_y + 40], fill=(245, 166, 35, 255))
        draw.ellipse([logo_x + 8, logo_y + 8, logo_x + 32, logo_y + 32], fill=(255, 255, 255, 255))
        draw.rectangle([logo_x + 16, logo_y - 6, logo_x + 24, logo_y + 14], fill=(245, 166, 35, 255))
        
        # 은행 로고 텍스트 'NH BANK'
        font_logo_text = _load_font(int(width * 0.062), bold=True)
        draw.text((logo_x + 52, logo_y + 2), bank_name, font=font_logo_text, fill=(20, 52, 115, 255))

        # 4. 볼드 헤드라인 타이틀: [SOLIQNI QAYTARISH MAVJUD]
        title_y = logo_y + int(height * 0.08)
        font_title = _load_font(int(width * 0.072), bold=True)
        for line in title_lines:
            line_str = line.strip()
            if line_str:
                draw.text((int(width * 0.08), title_y), line_str, font=font_title, fill=(15, 23, 42, 255))
                title_y += int(width * 0.09)

        # 5. 대형 환급 금액: 4 250 000 KRW
        title_y += int(height * 0.02)
        font_amt = _load_font(int(width * 0.088), bold=True)
        draw.text((int(width * 0.08), title_y), amount_formatted, font=font_amt, fill=(15, 23, 42, 255))
        title_y += int(width * 0.12)

        # 6. 세부 정보: To'landi ID / Người nhận
        font_desc = _load_font(int(width * 0.048), bold=False)
        draw.text((int(width * 0.08), title_y), desc_text, font=font_desc, fill=(71, 85, 105, 255))
        title_y += int(width * 0.065)
        draw.text((int(width * 0.08), title_y), f"ID: {user_name}", font=font_desc, fill=(71, 85, 105, 255))

        # 7. 파란색 체크 인증 마크 원형 배지 (우측 하단)
        check_r = int(width * 0.11)
        check_cx = int(width * 0.76)
        check_cy = title_y + int(height * 0.12)
        draw.ellipse([check_cx - check_r, check_cy - check_r, check_cx + check_r, check_cy + check_r], fill=(120, 150, 185, 255))
        
        # 체크 표시 (흰색 벡터)
        p1 = (check_cx - int(check_r * 0.4), check_cy)
        p2 = (check_cx - int(check_r * 0.1), check_cy + int(check_r * 0.35))
        p3 = (check_cx + int(check_r * 0.45), check_cy - int(check_r * 0.35))
        draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(width * 0.025))

        # 8. 하단 홈 인디케이터 바 (아이폰 제스처 바)
        bar_w = int(width * 0.36)
        bar_x = (width - bar_w) // 2
        bar_y = height - int(height * 0.03)
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 6], radius=3, fill=(180, 180, 180, 200))

        # 9. 둥근 모서리 마스킹 처리
        corner_mask = Image.new("L", (width, height), 0)
        cm_draw = ImageDraw.Draw(corner_mask)
        cm_draw.rounded_rectangle([0, 0, width, height], radius=int(width * 0.08), fill=255)
        
        screen.putalpha(corner_mask)

        # 10. 스마트폰 메탈 프레임 (슬림 다크 티타늄 베젤 테두리)
        phone_device = Image.new("RGBA", (width + 16, height + 16), (0, 0, 0, 0))
        pd_draw = ImageDraw.Draw(phone_device)
        pd_draw.rounded_rectangle([0, 0, width + 16, height + 16], radius=int(width * 0.09) + 4, fill=(40, 44, 52, 255), outline=(120, 130, 145, 255), width=3)
        phone_device.paste(screen, (8, 8), screen)

        # 저장
        out_filename = f"phone_screen_{lang}_{amount_krw}.png"
        out_path = self.output_dir / out_filename
        phone_device.save(out_path, "PNG")
        logger.info(f"📱 [PhoneAppScreenRenderer] NH BANK 실물 스마트폰 환급 화면 렌더링 완료: {out_filename}")
        return out_path

    def render_pricing_guarantee_screen(self, lang: str = "uz", out_path: Optional[Path] = None) -> Path:
        """
        슬라이드 3번용: 이지텍스 [선결제 0원 / 100% 후불제 안심 보증] 모바일 앱 화면 렌더링
        """
        lang = (lang or "uz").lower().strip()
        width, height = 480, 960
        screen = Image.new("RGBA", (width, height), (248, 250, 252, 255))
        draw = ImageDraw.Draw(screen)

        # 상단 네이비 바
        draw.rectangle([(0, 0), (width, 100)], fill=(15, 23, 42, 255))
        f_stat = _load_font(18, bold=True)
        draw.text((36, 20), "9:41", font=f_stat, fill=(255, 255, 255, 230))
        draw.text((width // 2 - 45, 60), "EasyTax", font=_load_font(22, bold=True), fill=(245, 158, 11, 255))

        # 메인 카드 1: 선결제 0원 안심 배지
        draw.rounded_rectangle([24, 130, width - 24, 430], radius=20, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
        draw.ellipse([width // 2 - 40, 160, width // 2 + 40, 240], fill=(238, 242, 255, 255))
        draw.text((width // 2 - 15, 175), "🛡️", font=_load_font(36))

        # 타이틀 & 설명 (우즈벡어 / 영어 / 한국어 지원)
        i18n_s3 = {
            "uz": ("OLDINDAN TO'LOV 0 SO'M", "Faqat pulingiz tushgandan so'ng xizmat haqi olinadi.\nAgar mablag' chiqmasa, 0 so'm!", "100% ISHONCHLI KAFOLAT"),
            "vi": ("TRẢ TRƯỚC 0 ĐỒNG", "Chỉ thanh toán phí sau khi tiền về tài khoản.\nKhông có tiền hoàn lại = 0 đồng phí!", "BẢO HÀNH 100% AN TÂM"),
            "ko": ("선결제 0원 후불제", "환급금이 개인 통장에 입금된 후에만 정산.\n환급 실패 시 비용 0원 전액 보증!", "100% 안심 후불제"),
            "en": ("0 KRW UPFRONT FEE", "Pay fee ONLY after refund lands in your bank.\nNo refund = Zero fee guaranteed!", "100% SAFE & GUARANTEED"),
        }
        t_head, t_body, t_badge = i18n_s3.get(lang, i18n_s3["en"])

        draw.text((width // 2 - int(draw.textlength(t_head, _load_font(24, True)) / 2), 260), t_head, font=_load_font(24, True), fill=(15, 23, 42, 255))
        
        # 바디 설명 2줄
        lines = t_body.split("\n")
        y_pos = 305
        for l in lines:
            draw.text((width // 2 - int(draw.textlength(l, _load_font(15, False)) / 2), y_pos), l, font=_load_font(15, False), fill=(71, 85, 105, 255))
            y_pos += 24

        # 하단 황금 배지
        draw.rounded_rectangle([60, 365, width - 60, 405], radius=10, fill=(245, 158, 11, 255))
        draw.text((width // 2 - int(draw.textlength(t_badge, _load_font(15, True)) / 2), 374), t_badge, font=_load_font(15, True), fill=(255, 255, 255, 255))

        # 세무사 인증 카드 2
        draw.rounded_rectangle([24, 450, width - 24, 750], radius=20, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
        draw.text((45, 475), "⚖️ National Certified CPA", font=_load_font(18, True), fill=(30, 41, 59, 255))
        draw.text((45, 515), "• Korean Tax Office (NTS) Direct Link\n• E-9 90% Special Tax Exemption\n• Encrypted Personal Data Vault\n• 100% Non-face-to-face Mobile Tax", font=_load_font(15, False), fill=(100, 116, 139, 255))

        # 하단 CTA 버튼 모의
        draw.rounded_rectangle([40, 670, width - 40, 725], radius=14, fill=(15, 23, 42, 255))
        draw.text((width // 2 - 80, 688), "EASYTAX VERIFIED", font=_load_font(16, True), fill=(245, 158, 11, 255))

        # 프레임 합성
        corner_mask = Image.new("L", (width, height), 0)
        cm_draw = ImageDraw.Draw(corner_mask)
        cm_draw.rounded_rectangle([0, 0, width, height], radius=int(width * 0.08), fill=255)
        screen.putalpha(corner_mask)

        phone_device = Image.new("RGBA", (width + 16, height + 16), (0, 0, 0, 0))
        pd_draw = ImageDraw.Draw(phone_device)
        pd_draw.rounded_rectangle([0, 0, width + 16, height + 16], radius=int(width * 0.09) + 4, fill=(40, 44, 52, 255), outline=(120, 130, 145, 255), width=3)
        phone_device.paste(screen, (8, 8), screen)

        out_path = out_path or (self.output_dir / f"easytax_app_pricing_{lang}.png")
        phone_device.save(out_path, "PNG")
        logger.info(f"📱 [PhoneAppScreenRenderer] 이지텍스 0원 보증 모바일 화면 생성 완료: {out_path.name}")
        return out_path

    def render_home_cta_screen(self, lang: str = "uz", out_path: Optional[Path] = None) -> Path:
        """
        슬라이드 5번용: 이지텍스 [1분 환급금 조회 메인 홈 CTA] 모바일 앱 화면 렌더링
        """
        lang = (lang or "uz").lower().strip()
        width, height = 480, 960
        screen = Image.new("RGBA", (width, height), (15, 23, 42, 255))  # 프리미엄 다크 네이비 테마
        draw = ImageDraw.Draw(screen)

        # 상태바
        f_stat = _load_font(18, bold=True)
        draw.text((36, 20), "9:41", font=f_stat, fill=(255, 255, 255, 230))
        draw.text((width // 2 - 50, 60), "EasyTax", font=_load_font(26, bold=True), fill=(245, 158, 11, 255))

        i18n_s5 = {
            "uz": ("1 DAQIQADA PULINGIZNI\nTEKSHIRING", "5 yil o'tib ketsa, bu mablag' davlatga ketadi!", "TEKSHIRISHNI BOSHLASH ➔"),
            "vi": ("KIỂM TRA TIỀN HOÀN\nCHỈ TRONG 1 PHÚT", "Quá hạn 5 năm, tiền sẽ bị nộp vào ngân sách!", "BẮT ĐẦU TRA CỨU NGAY ➔"),
            "ko": ("1분 만에 내 환급금\n조회하기", "5년 지나면 국가 귀속! 놓친 세금을 찾으세요.", "지금 무료 환급 조회 ➔"),
            "en": ("CHECK REFUND\nIN 1 MINUTE", "Claim your money before 5-year expiration!", "START FREE CHECK NOW ➔"),
        }
        t_head, t_sub, t_btn = i18n_s5.get(lang, i18n_s5["en"])

        # 메인 원형 그래픽 (환급 게이지 / 골드 코인)
        draw.ellipse([width // 2 - 80, 160, width // 2 + 80, 320], outline=(245, 158, 11, 200), width=6)
        draw.text((width // 2 - 35, 215), "💰", font=_load_font(56))

        # 메인 카피
        lines = t_head.split("\n")
        y_pos = 360
        for l in lines:
            draw.text((width // 2 - int(draw.textlength(l, _load_font(25, True)) / 2), y_pos), l, font=_load_font(25, True), fill=(255, 255, 255, 255))
            y_pos += 34

        # 서브 카피 (경고/긴급)
        y_pos += 15
        draw.text((width // 2 - int(draw.textlength(t_sub, _load_font(15, False)) / 2), y_pos), t_sub, font=_load_font(15, False), fill=(251, 191, 36, 255))

        # 3가지 핵심 요약 박스
        y_box = 480
        draw.rounded_rectangle([30, y_box, width - 30, y_box + 140], radius=16, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255))
        draw.text((50, y_box + 20), "⚡ 1-Minute Non-face-to-face Check", font=_load_font(16, True), fill=(241, 245, 249, 255))
        draw.text((50, y_box + 58), "🔒 100% Safe Government NTS Direct", font=_load_font(16, True), fill=(241, 245, 249, 255))
        draw.text((50, y_box + 96), "🎁 Upfront Fee 0 KRW Guarantee", font=_load_font(16, True), fill=(245, 158, 11, 255))

        # 초대형 메인 골드 액션 버튼 (CTA)
        btn_y = 670
        draw.rounded_rectangle([30, btn_y, width - 30, btn_y + 70], radius=18, fill=(245, 158, 11, 255))
        draw.text((width // 2 - int(draw.textlength(t_btn, _load_font(18, True)) / 2), btn_y + 22), t_btn, font=_load_font(18, True), fill=(15, 23, 42, 255))

        # 프레임 합성
        corner_mask = Image.new("L", (width, height), 0)
        cm_draw = ImageDraw.Draw(corner_mask)
        cm_draw.rounded_rectangle([0, 0, width, height], radius=int(width * 0.08), fill=255)
        screen.putalpha(corner_mask)

        phone_device = Image.new("RGBA", (width + 16, height + 16), (0, 0, 0, 0))
        pd_draw = ImageDraw.Draw(phone_device)
        pd_draw.rounded_rectangle([0, 0, width + 16, height + 16], radius=int(width * 0.09) + 4, fill=(40, 44, 52, 255), outline=(120, 130, 145, 255), width=3)
        phone_device.paste(screen, (8, 8), screen)

        out_path = out_path or (self.output_dir / f"easytax_app_home_{lang}.png")
        phone_device.save(out_path, "PNG")
        logger.info(f"📱 [PhoneAppScreenRenderer] 이지텍스 1분 조회 메인 모바일 화면 생성 완료: {out_path.name}")
        return out_path

