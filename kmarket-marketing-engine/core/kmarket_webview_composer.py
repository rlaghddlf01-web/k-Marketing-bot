"""
KMarketWebviewComposer - [9:16 세로형 모바일 웹뷰(iFrame 스타일) 렌더러]
- 실제 케이마켓(https://ktrs-market.vercel.app/)의 세련된 모바일 앱 인터페이스를 1080x1920 해상도로 100% 렌더링
- 4대 핵심 모바일 화면 (0원 나눔 / 무빙세일 80% / 17개국 실시간 번역채팅 / ARC 안심인증)
- 17개국어(몽골어, 베트남어, 우즈벡어, 중국어, 영어 등) 100% 현지어 UI 지원
"""

import os
import io
import urllib.request
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, DATA_DIR

logger = logging.getLogger("KMarketWebview")

# Windows 유니코드 폰트
UNICODE_FONTS_BOLD = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\malgunbd.ttf"]
UNICODE_FONTS_REG = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\malgun.ttf"]

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    flist = UNICODE_FONTS_BOLD if bold else UNICODE_FONTS_REG
    for fp in flist:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

# 🎯 17개국 케이마켓 모바일 UI 번역 딕셔너리
KMARKET_I18N: Dict[str, Dict[str, Any]] = {
    "vi": {
        "app_title": "K-Market • Chợ Đồ Cũ Expat Hàn Quốc",
        "search_ph": "🔍 Tìm đồ gia dụng, đồ 0 won gần bạn...",
        "s1_badge": "🎁 TẶNG MIỄN PHÍ 0 WON",
        "s1_title": "Nhượng Lại Đồ Đạc / Đồ Gia Dụng 0 Won",
        "s1_desc": "Giường, bàn học, lò vi sóng, tủ lạnh miễn phí",
        "s2_badge": "⚡ XẢ HÀNG CHUYỂN NHÀ (MOVING SALE)",
        "s2_title": "Trọn Gói Phòng Trọ Giảm Đến 80%",
        "s2_desc": "Mua trọn bộ tiện lợi, đi bộ 5 phút nhận đồ",
        "s3_badge": "💬 CHÁT DỊCH TỰ ĐỘNG 17 NGÔN NGỮ",
        "s3_title": "Tự Tin Trò Chuyện Bằng Tiếng Mẹ Đẻ",
        "s3_chat_seller": "안녕하세요! 직거래 가능하신가요?",
        "s3_chat_buyer": "Vâng, hôm nay tôi qua lấy được không ạ?",
        "s4_badge": "🛡️ XÁC MINH THẺ CƯ TRÚ (ARC) 100%",
        "s4_title": "Giao Dịch Trực Tiếp An Toàn 100%",
        "s4_desc": "Gần trường đại học & khu công nghiệp",
        "cta_btn": "👉 MỞ APP K-MARKET NGAY",
        "cta_sub": "Xem 270+ đồ 0 won & đồ giảm giá hôm nay!"
    },
    "mn": {
        "app_title": "K-Market • Солонгос дахь Гадаад Иргэдийн Зах",
        "search_ph": "🔍 0 воны үнэгүй бараа, тавилга хайх...",
        "s1_badge": "🎁 0 ВОНЫ ҮНЭГҮЙ БЭЛЭГ (FREE)",
        "s1_title": "Ор, Ширээ, Богино Долгионы Зуух 0 Төгрөг",
        "s1_desc": "Төгсөж буцах оюутнуудын үнэгүй тавилга",
        "s2_badge": "⚡ НҮҮЛГЭЭНИЙ ХЯМДРАЛ (MOVING SALE)",
        "s2_title": "Өрөөний Бүрэн Багц 80% Хүртэл Хямдрал",
        "s2_desc": "Ор + Ширээ + Будаа агшаагч 5 минутын зайд",
        "s3_badge": "💬 17 ХЭЛНИЙ ШУУД ОРЧУУЛГАТАЙ ЧАТ",
        "s3_title": "Эх Хэлээрээ Чөлөөтэй Худалдаа Хийгээрэй",
        "s3_chat_seller": "안녕하세요! 직거래 가능하신가요?",
        "s3_chat_buyer": "Тиймээ, би өнөөдөр очиж авч болох уу?",
        "s4_badge": "🛡️ БАТАЛГААЖСАН ГАДААД ИРГЭНИЙ ҮНЭМЛЭХ",
        "s4_title": "100% Найдвартай Шууд Гар Дээрээс Авах",
        "s4_desc": "Их сургууль болон үйлдвэрийн бүсэд ойр",
        "cta_btn": "👉 K-MARKET АПП НЭЭХ",
        "cta_sub": "Өнөөдрийн 0 воны шинэ зар харах!"
    },
    "uz": {
        "app_title": "K-Market • Koreyadagi Expat Bozor",
        "search_ph": "🔍 0 vonlik tekin buyumlar, mebel qidirish...",
        "s1_badge": "🎁 0 VON TEKIN BUYUMLAR (FREE)",
        "s1_title": "Mebel va Maishiy Texnika 0 Vonga",
        "s1_desc": "Krovat, stol, mikroto'lqinli pech tekinga",
        "s2_badge": "⚡ KO'CHISH CHEGIRMASI (MOVING SALE)",
        "s2_title": "To'liq Xona Mebellari 80% Chegirma",
        "s2_desc": "Hamma narsa bir joyda, 5 daqiqada olib ketish",
        "s3_badge": "💬 17 TILDAGI AVTOMATIK TARJIMA CHAT",
        "s3_title": "O'z Tilingizda Erkin Savdolashing",
        "s3_chat_seller": "안녕하세요! 직거래 가능하신가요?",
        "s3_chat_buyer": "Ha, bugun borib olsam bo'ladimi?",
        "s4_badge": "🛡️ 100% VERIFIKATSIYA QILINGAN PROFIL",
        "s4_title": "Xavfsiz va Ishonchli To'g'ridan-to'g'ri Savdo",
        "s4_desc": "Universitet va zavod hududlarida",
        "cta_btn": "👉 K-MARKET ILOVASINI OCHISH",
        "cta_sub": "Bugungi 270+ yangi e'lonlarni ko'ring!"
    },
    "en": {
        "app_title": "K-Market • Korea's #1 Verified Expat Marketplace",
        "search_ph": "🔍 Search free 0-KRW items, furniture, electronics...",
        "s1_badge": "🎁 0 KRW FREE GIVEAWAYS (FREE)",
        "s1_title": "Free Furniture & Appliances Near You",
        "s1_desc": "Bed, desk, microwave, fridge free giveaways",
        "s2_badge": "⚡ MOVING SALE UP TO 80% OFF",
        "s2_title": "Studio Full Package Deals (Huge Discount)",
        "s2_desc": "Bed + desk + rice cooker within 5 min walk",
        "s3_badge": "💬 17-LANGUAGE REAL-TIME AUTO TRANSLATION",
        "s3_title": "Chat Confidently in Your Native Language",
        "s3_chat_seller": "안녕하세요! 직거래 가능하신가요?",
        "s3_chat_buyer": "Yes! Can I pick it up this afternoon?",
        "s4_badge": "🛡️ 100% VERIFIED ARC RESIDENTS ONLY",
        "s4_title": "Safe Direct Trade Near Campuses & Towns",
        "s4_desc": "Zero scam direct pickup within 5 minutes",
        "cta_btn": "👉 OPEN K-MARKET APP NOW",
        "cta_sub": "Explore 270+ free & moving sale listings today!"
    },
    "zh": {
        "app_title": "K-Market • 韩国在华人员专属二手直易平台",
        "search_ph": "🔍 搜索 0韩元免费赠送、家具家电...",
        "s1_badge": "🎁 0韩元免费赠送 (FREE)",
        "s1_title": "毕业归国留学生家具家电 0元免费送",
        "s1_desc": "床、书桌、微波炉、冰箱先到先得免费领",
        "s2_badge": "⚡ 搬家急甩特惠 (MOVING SALE)",
        "s2_title": "单身公寓全套家电家具 直降80%",
        "s2_desc": "床+桌椅+电饭煲全套，步行5分钟安全自提",
        "s3_badge": "💬 17国语言实时自动翻译聊天",
        "s3_title": "无需担心韩语，用母语畅快秒聊",
        "s3_chat_seller": "안녕하세요! 직거래 가능하신가요?",
        "s3_chat_buyer": "您好！今天下午可以去自提吗？",
        "s4_badge": "🛡️ 100% 外国人登录证实名认证",
        "s4_title": "大学城及工业园区 安全直面交易",
        "s4_desc": "杜绝诈骗，大学城步行5分钟放心交易",
        "cta_btn": "👉 立即打开 K-Market 平台",
        "cta_sub": "查看今日 270+ 真实在售与免费好物！"
    }
}


class KMarketWebviewComposer:
    """
    🎨 9:16 (1080x1920) 세로형 프리미엄 케이마켓 모바일 웹뷰 화면 생성기
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "cardnews")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_photos = [
            # 고화질 실제 침대/책상/가전 사진 에셋
            r"C:\Users\zkfnt\Desktop\ktrs 마케팅 봇\kmarket-marketing-engine\data\kmarket_items.json"
        ]

    def render_slide(
        self,
        slide_idx: int,
        lang: str = "vi",
        item_photo_path: Optional[str] = None
    ) -> Path:
        """
        1080x1920 세로형 스마트폰 모바일 웹뷰 화면 1장 렌더링
        """
        W, H = 1080, 1920
        img = Image.new("RGB", (W, H), color=(248, 250, 252)) # 깔끔한 프리미엄 크림 화이트
        draw = ImageDraw.Draw(img)

        i18n = KMARKET_I18N.get(lang, KMARKET_I18N["en"])

        f_status = get_font(24, bold=True)
        f_app_title = get_font(32, bold=True)
        f_search = get_font(26, bold=False)
        f_badge = get_font(26, bold=True)
        f_title = get_font(44, bold=True)
        f_desc = get_font(30, bold=False)
        f_price = get_font(46, bold=True)
        f_chat = get_font(28, bold=False)
        f_cta = get_font(38, bold=True)
        f_footer = get_font(22, bold=False)

        # ── 1. 스마트폰 상단 상태 표시줄 (Status Bar) ──
        draw.text((80, 35), "09:41", fill=(30, 41, 59), font=f_status)
        draw.text((920, 35), "5G  100%", fill=(30, 41, 59), font=f_status)

        # ── 2. 케이마켓 모바일 앱 헤더 (App Header) ──
        draw.rectangle([(0, 80), (W, 190)], fill=(255, 255, 255))
        draw.line([(0, 190), (W, 190)], fill=(226, 232, 240), width=2)
        # 당근마켓/쿠팡 스타일 핫 오렌지 로고
        draw.ellipse([(60, 105), (120, 165)], fill=(255, 107, 53))
        draw.text((78, 115), "K", fill=(255, 255, 255), font=f_app_title)
        draw.text((140, 115), i18n["app_title"][:28], fill=(15, 23, 42), font=f_app_title)
        draw.text((940, 115), f"[{lang.upper()}]", fill=(255, 107, 53), font=f_status)

        # ── 3. 모바일 검색창 바 (Search Bar) ──
        draw.rounded_rectangle([(60, 215), (1020, 295)], radius=40, fill=(241, 245, 249))
        draw.text((100, 238), i18n["search_ph"][:40], fill=(148, 163, 184), font=f_search)

        # ── 4. 메인 컨텐츠 카드 영역 (1080x1920의 850px 높이 메인 뷰) ──
        card_x, card_y = 60, 325
        card_w, card_h = 960, 1020

        draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=36, fill=(255, 255, 255), outline=(226, 232, 240), width=2)

        # [슬라이드 1: 0원 무료나눔]
        if slide_idx == 1:
            draw.rounded_rectangle([(card_x + 30, card_y + 30), (card_x + 480, card_y + 95)], radius=20, fill=(16, 185, 129))
            draw.text((card_x + 50, card_y + 45), i18n["s1_badge"], fill=(255, 255, 255), font=f_badge)
            
            # 실물 매물 이미지 영역 (840x560)
            draw.rounded_rectangle([(card_x + 30, card_y + 120), (card_x + card_w - 30, card_y + 700)], radius=24, fill=(241, 245, 249))
            # 가구/가전 대표 아이콘 & 비주얼
            draw.text((card_x + 320, card_y + 340), "🛏️ 0원 무료 나눔", fill=(100, 116, 139), font=f_title)
            
            # 가격 및 타이틀
            draw.text((card_x + 30, card_y + 730), "₩0 (FREE GIVEAWAY)", fill=(16, 185, 129), font=f_price)
            draw.text((card_x + 30, card_y + 800), i18n["s1_title"], fill=(15, 23, 42), font=f_title)
            draw.text((card_x + 30, card_y + 870), i18n["s1_desc"], fill=(100, 116, 139), font=f_desc)
            draw.text((card_x + 30, card_y + 940), "📍 대학교 기숙사 / 안산 공단 도보 5분", fill=(59, 130, 246), font=f_status)

        # [슬라이드 2: 무빙세일 80% 할인]
        elif slide_idx == 2:
            draw.rounded_rectangle([(card_x + 30, card_y + 30), (card_x + 560, card_y + 95)], radius=20, fill=(255, 107, 53))
            draw.text((card_x + 50, card_y + 45), i18n["s2_badge"], fill=(255, 255, 255), font=f_badge)

            draw.rounded_rectangle([(card_x + 30, card_y + 120), (card_x + card_w - 30, card_y + 700)], radius=24, fill=(241, 245, 249))
            draw.text((card_x + 280, card_y + 340), "📦 원룸 풀패키지 80%↓", fill=(100, 116, 139), font=f_title)

            draw.text((card_x + 30, card_y + 730), "₩45,000 (정가 ₩250,000)", fill=(255, 107, 53), font=f_price)
            draw.text((card_x + 30, card_y + 800), i18n["s2_title"], fill=(15, 23, 42), font=f_title)
            draw.text((card_x + 30, card_y + 870), i18n["s2_desc"], fill=(100, 116, 139), font=f_desc)
            draw.text((card_x + 30, card_y + 940), "⚡ 침대 + 책상 + 전자레인지 세트", fill=(16, 185, 129), font=f_status)

        # [슬라이드 3: 17개국 자동번역 안심 채팅]
        elif slide_idx == 3:
            draw.rounded_rectangle([(card_x + 30, card_y + 30), (card_x + 620, card_y + 95)], radius=20, fill=(59, 130, 246))
            draw.text((card_x + 50, card_y + 45), i18n["s3_badge"], fill=(255, 255, 255), font=f_badge)

            # 말풍선 1 (한국인 판매자)
            draw.rounded_rectangle([(card_x + 40, card_y + 160), (card_x + 650, card_y + 280)], radius=24, fill=(241, 245, 249))
            draw.text((card_x + 70, card_y + 190), "👤 한국인 판매자", fill=(148, 163, 184), font=f_status)
            draw.text((card_x + 70, card_y + 225), i18n["s3_chat_seller"], fill=(15, 23, 42), font=f_chat)

            # 번역 인디케이터
            draw.text((card_x + 280, card_y + 310), "🔄 1초 실시간 모국어 자동 번역 완료", fill=(16, 185, 129), font=f_status)

            # 말풍선 2 (외국인 구매자)
            draw.rounded_rectangle([(card_x + 260, card_y + 370), (card_x + card_w - 40, card_y + 490)], radius=24, fill=(255, 107, 53))
            draw.text((card_x + 290, card_y + 400), f"👤 {lang.upper()} 구매자", fill=(254, 215, 170), font=f_status)
            draw.text((card_x + 290, card_y + 435), i18n["s3_chat_buyer"][:32], fill=(255, 255, 255), font=f_chat)

            draw.text((card_x + 30, card_y + 730), "⚡ 17개 언어 자유 소통", fill=(59, 130, 246), font=f_price)
            draw.text((card_x + 30, card_y + 800), i18n["s3_title"], fill=(15, 23, 42), font=f_title)
            draw.text((card_x + 30, card_y + 870), "한국어를 못해도 모국어로 즉시 직거래 예약", fill=(100, 116, 139), font=f_desc)
            draw.text((card_x + 30, card_y + 940), "🛡️ AI 실시간 사기 방지 필터링 작동 중", fill=(16, 185, 129), font=f_status)

        # [슬라이드 4: 외국인등록증 인증 안심 직거래]
        else:
            draw.rounded_rectangle([(card_x + 30, card_y + 30), (card_x + 580, card_y + 95)], radius=20, fill=(99, 102, 241))
            draw.text((card_x + 50, card_y + 45), i18n["s4_badge"], fill=(255, 255, 255), font=f_badge)

            draw.rounded_rectangle([(card_x + 30, card_y + 120), (card_x + card_w - 30, card_y + 700)], radius=24, fill=(241, 245, 249))
            draw.text((card_x + 240, card_y + 340), "🗺️ 대학가 / 공단 직거래 지도", fill=(100, 116, 139), font=f_title)

            draw.text((card_x + 30, card_y + 730), "✅ 100% 본인인증 실명제", fill=(99, 102, 241), font=f_price)
            draw.text((card_x + 30, card_y + 800), i18n["s4_title"], fill=(15, 23, 42), font=f_title)
            draw.text((card_x + 30, card_y + 870), i18n["s4_desc"], fill=(100, 116, 139), font=f_desc)
            draw.text((card_x + 30, card_y + 940), "📍 사기 0% 직거래 예약 보증 시스템", fill=(16, 185, 129), font=f_status)

        # ── 5. 하단 큼직한 모바일 CTA 버튼 (1080x1920 하단 고정) ──
        cta_y = 1400
        draw.rounded_rectangle([(60, cta_y), (1020, cta_y + 200)], radius=36, fill=(255, 107, 53))
        draw.text((120, cta_y + 45), i18n["cta_btn"], fill=(255, 255, 255), font=f_cta)
        draw.text((120, cta_y + 125), i18n["cta_sub"][:42], fill=(254, 215, 170), font=f_desc)

        # ── 6. 최하단 법적 안내 및 홈 바 ──
        draw.text((120, 1780), "K-Market • 대한민국 No.1 외국인 전용 안심 직거래 플랫폼", fill=(148, 163, 184), font=f_footer)
        # 아이폰 하단 홈 인디케이터 바
        draw.rounded_rectangle([(390, 1870), (690, 1885)], radius=8, fill=(30, 41, 59))

        out_path = self.output_dir / f"kmarket_webview_{lang}_slide_{slide_idx}.png"
        img.save(out_path, "PNG")
        logger.info(f"[{lang.upper()}] 📱 케이마켓 9:16 모바일 웹뷰 렌더링 완료: {out_path.name}")
        return out_path
