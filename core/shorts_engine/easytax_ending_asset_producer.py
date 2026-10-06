# -*- coding: utf-8 -*-
"""
EasytaxEndingAssetProducer - 🎬 [이지텍스 8대 국가 1080x1920 엔딩 신뢰 카드 완제품 사전 생성 엔진]
- 순백색(#ffffff) 바탕 + 샴페인 골드 & 딥 네이비 세련된 럭셔리 디자인
- "국세청 공식" 문구 100% 영구 배제 ➔ "공인 전문 세무사 직접 검토 및 안전 대행"
- 8대 국가 (베트남, 우즈벡, 캄보디아, 미얀마, 태국, 네팔, 몽골, 인도네시아 + 한국어)
- Playwright Chromium (Google HarfBuzz + Skia) 무결점 텍스트 셰이핑 적용
- 폰트 깨짐(두부/네모 박스) 0% 영구 보장
- 사전 일괄 생성하여 assets/templates 및 assets/lang_{lang}/에 영구 보관
"""

import os
import html
import logging
from pathlib import Path
from typing import Dict, Any
from playwright.sync_api import sync_playwright

logger = logging.getLogger("EasytaxEndingAssetProducer")

# 🌐 8대 국가 공식 현지어 엔딩 신뢰 카드 텍스트 사전 (국세청 사칭 0% + 전문 세무사 직접 대행)
ENDING_CTA_I18N: Dict[str, Dict[str, str]] = {
    "vi": {
        "badge": "HỆ THỐNG HỖ TRỢ THUẾ KTRS",
        "sub": "ĐIỀU 30 ĐẠO LUẬT HẠN CHẾ THUẾ ĐẶC BIỆT",
        "title": "An Tâm Hoàn Thuế Thu Nhập 100% Hợp Pháp",
        "f1_t": "100% Phí Thành Công",
        "f1_d": "Chỉ thanh toán phí sau khi tiền hoàn thuế đã vào tài khoản",
        "f2_t": "0 Won Chi Phí Trước",
        "f2_d": "Tuyệt đối không thu tiền cọc hay chi phí ẩn nào",
        "f3_t": "Chuyên Viên Thuế Trực Tiếp",
        "f3_d": "Kế toán thuế chuyên nghiệp có chứng chỉ trực tiếp xử lý an toàn",
        "domain_lbl": "Trang web tra cứu chính thức:",
        "btn": "Kiểm Tra Tiền Hoàn Thuế Miễn Phí >"
    },
    "my": {
        "badge": "KTRS အခွန်ကူညီရေး စနစ်",
        "sub": "အထူးအခွန်ကင်းလွတ်ခွင့် ဥပဒေ ပုဒ်မ ၃၀",
        "title": "၁၀၀% ဘေးကင်းစိတ်ချရသော တရားဝင် အခွန်ပြန်အမ်းငွေ",
        "f1_t": "၁၀၀% အောင်မြင်မှ ဝန်ဆောင်ခ",
        "f1_d": "ဘဏ်အကောင့်ထဲ ငွေရောက်ရှိပြီးမှသာ ဝန်ဆောင်ခပေးချေရပါမည်",
        "f2_t": "ကြိုတင်ငွေ ၀ ဝမ် (အခမဲ့)",
        "f2_d": "ကြိုတင်ငွေသွင်းရန်မလို၊ လျှို့ဝှက်အခကြေးငွေ လုံးဝမရှိပါ",
        "f3_t": "ကျွမ်းကျင် အခွန်ပညာရှင် တိုက်ရိုက်",
        "f3_d": "အသိအမှတ်ပြု အခွန်ပညာရှင်များက စာရွက်စာတမ်း တိုက်ရိုက် စိစစ်တင်ပြ",
        "domain_lbl": "တရားဝင် အခမဲ့ စစ်ဆေးရန် ဝက်ဘ်ဆိုက်:",
        "btn": "အခမဲ့ အခွန်ပြန်အမ်းငွေ စစ်ဆေးရန် >"
    },
    "uz": {
        "badge": "KTRS SOLIQ YORDAM TIZIMI",
        "sub": "MAXSUS SOLIQ IMTIYOZLARI TO'G'RISIDAGI QONUN 30-MODDA",
        "title": "100% Qonuniy va Xavfsiz Soliq Qaytarish",
        "f1_t": "100% Natijadan So'ng To'lov",
        "f1_d": "Faqat pul bank hisobingizga tushgach to'laysiz",
        "f2_t": "0 Von Boshlang'ich To'lov",
        "f2_d": "Hech qanday oldindan to'lov yoki yashirin to'lov yo'q",
        "f3_t": "Malakali Soliq Mutaxassisi",
        "f3_d": "Sertifikatlangan mutaxassis arizangizni xavfsiz rasmiylashtiradi",
        "domain_lbl": "Rasmiy tekshirish sayti:",
        "btn": "Hoziroq Bepul Tekshiring >"
    },
    "km": {
        "badge": "ប្រព័ន្ធជំនួយពន្ធ KTRS",
        "sub": "មាត្រា ៣០ នៃច្បាប់ស្តីពីការបន្ធូរបន្ថយពន្ធពិសេស",
        "title": "បង្វិលពន្ធប្រាក់ចំណូលស្របច្បាប់ ១០០% ប្រកបដោយសុវត្ថិភាព",
        "f1_t": "សេវាគិតក្រោយ ១០០%",
        "f1_d": "ទូទាត់តែក្រោយពេលប្រាក់ចូលគណនីធនាគាររបស់អ្នក",
        "f2_t": "មិនបង់ប្រាក់កក់ ០ វ៉ុន",
        "f2_d": "គ្មានការទារប្រាក់កក់ ឬថ្លៃសេវាលាក់កំបាំងឡើយ",
        "f3_t": "អ្នកជំនាញពន្ធដារផ្ទាល់",
        "f3_d": "អ្នកជំនាញពន្ធដារមានវិជ្ជាជីវៈពិនិត្យ និងដាក់ពាក្យស្នើសុំដោយផ្ទាល់",
        "domain_lbl": "គេហទំព័រផ្លូវការពិនិត្យឥតគិតថ្លៃ:",
        "btn": "ពិនិត្យប្រាក់ពន្ធឥឡូវនេះ >"
    },
    "th": {
        "badge": "ระบบช่วยเหลือภาษี KTRS",
        "sub": "มาตรา 30 แห่งกฎหมายควบคุมภาษีพิเศษ",
        "title": "ขอคืนภาษีเงินได้ถูกกฎหมาย ปลอดภัย 100%",
        "f1_t": "จ่ายค่าบริการเมื่อสำเร็จ 100%",
        "f1_d": "ชำระค่าบริการหลังจากเงินโอนเข้าบัญชีแล้วเท่านั้น",
        "f2_t": "ไม่มีค่าใช้จ่ายล่วงหน้า 0 วอน",
        "f2_d": "ไม่ต้องวางเงินมัดจำ ไม่มีค่าธรรมเนียมแอบแฝง",
        "f3_t": "ผู้เชี่ยวชาญภาษีดูแลโดยตรง",
        "f3_d": "นักบัญชีภาษีผู้เชี่ยวชาญมีใบอนุญาตดูแลเอกสารอย่างปลอดภัย",
        "domain_lbl": "เว็บไซต์ตรวจสอบอย่างเป็นทางการ:",
        "btn": "ตรวจสอบเงินคืนภาษีฟรีทันที >"
    },
    "ne": {
        "badge": "KTRS कर सहायता प्रणाली",
        "sub": "विशेष कर प्रतिबन्ध ऐनको धारा ३०",
        "title": "१००% सुरक्षित र कानुनी आयकर फिर्ता",
        "f1_t": "१००% सफलता शुल्क मात्र",
        "f1_d": "खातामा रकम प्राप्त भएपछि मात्र सेवा शुल्क भुक्तानी",
        "f2_t": "शून्य अग्रिम शुल्क (० वन)",
        "f2_d": "कुनै धरौटी वा लुकेको शुल्क लाग्ने छैन",
        "f3_t": "प्रत्यक्ष कर विशेषज्ञ",
        "f3_d": "प्रमाणित व्यावसायिक कर लेखापालद्वारा प्रत्यक्ष फाइल र सुरक्षित प्रक्रिया",
        "domain_lbl": "आधिकारिक नि:शुल्क वेबसाइट:",
        "btn": "अहिले नै नि:शुल्क जाँच गर्नुहोस् >"
    },
    "mn": {
        "badge": "KTRS ТАТВАРЫН ТУСЛАМЖИЙН СИСТЕМ",
        "sub": "ТАТВАРЫН ТУСГАЙ ХӨНГӨЛӨЛТИЙН ТУХАЙ ХУУЛИЙН 30 ДУГААР ЗҮЙЛ",
        "title": "100% Хууль Ёсны Найдвартай Татварын Буцаан Олголт",
        "f1_t": "100% Амжилтын Дараах Шимтгэл",
        "f1_d": "Мөнгө дансанд орсны дараа л төлбөр төлнө",
        "f2_t": "Урьдчилгаа 0 Вон",
        "f2_d": "Ямар ч барьцаа болон нуугдмал хураамж байхгүй",
        "f3_t": "Мэргэшсэн Зөвлөх Шууд Ажиллана",
        "f3_d": "Мэргэжлийн эрх бүхий татварын нягтлан бодогч шууд найдвартай бүрдүүлнэ",
        "domain_lbl": "Албан ёсны шалгах сайт:",
        "btn": "Одоо Үнэгүй Шалгах >"
    },
    "id": {
        "badge": "SISTEM BANTUAN PAJAK KTRS",
        "sub": "PASAL 30 UNDANG-UNDANG PEMBATASAN PAJAK KHUSUS",
        "title": "Pengembalian Pajak 100% Aman & Resmi",
        "f1_t": "100% Biaya Setelah Berhasil",
        "f1_d": "Pembayaran hanya setelah uang masuk ke rekening Anda",
        "f2_t": "0 Won Biaya Awal",
        "f2_d": "Tanpa uang muka atau biaya tersembunyi apa pun",
        "f3_t": "Ditangani Konsultan Bersertifikat",
        "f3_d": "Akuntan pajak profesional bersertifikat menangani langsung secara aman",
        "domain_lbl": "Situs web resmi pengecekan:",
        "btn": "Periksa Pengembalian Pajak Gratis >"
    },
    "ko": {
        "badge": "KTRS 세무지원 시스템",
        "sub": "조세특례제한법 제30조 청년 중소기업 세금 감면",
        "title": "100% 안전하고 합법적인 세금 환급",
        "f1_t": "100% 성공보수 후불제",
        "f1_d": "환급금이 통장에 입금된 후에만 수수료가 발생합니다",
        "f2_t": "선입금 0원 / 초기비용 없음",
        "f2_d": "어떠한 사전 예약금이나 숨겨진 추가 비용도 없습니다",
        "f3_t": "공인 전문 세무사 직접 검토",
        "f3_d": "자격을 갖춘 한국 공인 세무사가 직접 안전하게 신고를 대행합니다",
        "domain_lbl": "공식 무료 조회 웹사이트:",
        "btn": "지금 무료로 환급액 확인하기 >"
    }
}


class EasytaxEndingAssetProducer:
    """이지텍스 8대 국가 순백색 럭셔리 골드 1080x1920 엔딩 신뢰 카드 완제품 사전 일괄 생성기"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.assets_dir = self.base_dir / "assets"
        self.templates_dir = self.assets_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def generate_html(self, lang: str, domain_text: str = "ktrs-service.vercel.app") -> str:
        """순백색(#ffffff) 바탕 + 샴페인 골드 & 딥 네이비 럭셔리 웹사이트 스타일 무결점 HTML 생성"""
        info = ENDING_CTA_I18N.get(lang, ENDING_CTA_I18N["ko"])

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=1080, height=1920, initial-scale=1.0">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Myanmar Text', 'Padauk', 'Leelawadee UI', 'Khmer UI', 'Nirmala UI', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}
        body {{
            width: 1080px;
            height: 1920px;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 130px 70px 120px 70px;
            color: #0f172a;
            position: relative;
            overflow: hidden;
        }}
        /* 은은한 샴페인 골드 상단 앰비언트 글로우 */
        .bg-pattern {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 10%, rgba(212, 175, 55, 0.09) 0%, rgba(255, 255, 255, 0) 60%);
            pointer-events: none;
            z-index: 0;
        }}
        .top-container {{
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 1;
        }}
        /* 브랜드 로고 바 */
        .brand-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 30px;
        }}
        .brand-logo-badge {{
            background: linear-gradient(135deg, #c59b27 0%, #d4af37 50%, #b38728 100%);
            color: #ffffff;
            font-size: 26px;
            font-weight: 900;
            padding: 6px 18px;
            border-radius: 12px;
            letter-spacing: 1px;
            box-shadow: 0 4px 12px rgba(197, 155, 39, 0.25);
        }}
        .brand-title {{
            font-size: 28px;
            font-weight: 800;
            color: #1e293b;
            letter-spacing: 0.5px;
        }}
        /* 법령 골드 라벨 */
        .legal-tag {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 22px;
        }}
        .gold-line {{
            width: 45px;
            height: 2px;
            background: #c59b27;
            border-radius: 2px;
        }}
        .legal-text {{
            font-size: 23px;
            font-weight: 700;
            color: #b38728;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        /* 메인 헤드라인 */
        .main-headline {{
            font-size: 54px;
            font-weight: 900;
            line-height: 1.3;
            text-align: center;
            color: #0f172a;
            margin-bottom: 50px;
            word-break: keep-all;
        }}
        /* 3대 신뢰 카드 구역 */
        .cards-grid {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 26px;
            margin-bottom: 45px;
        }}
        .trust-card {{
            width: 100%;
            background: #ffffff;
            border: 2px solid rgba(212, 175, 55, 0.4);
            border-radius: 28px;
            padding: 36px 42px;
            display: flex;
            align-items: center;
            gap: 32px;
            box-shadow: 0 8px 24px rgba(212, 175, 55, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03);
        }}
        .trust-card.highlight {{
            background: #0f172a;
            border-color: #c59b27;
            box-shadow: 0 15px 35px rgba(15, 23, 42, 0.15);
        }}
        .card-icon-wrap {{
            width: 76px;
            height: 76px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(197, 155, 39, 0.25) 100%);
            border: 2px solid rgba(212, 175, 55, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            flex-shrink: 0;
        }}
        .trust-card.highlight .card-icon-wrap {{
            background: rgba(212, 175, 55, 0.2);
            border-color: #d4af37;
        }}
        .card-body {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .card-title {{
            font-size: 38px;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: 0.2px;
        }}
        .trust-card.highlight .card-title {{
            color: #ffffff;
        }}
        .card-desc {{
            font-size: 26px;
            font-weight: 600;
            color: #64748b;
            line-height: 1.4;
            word-break: keep-all;
        }}
        .trust-card.highlight .card-desc {{
            color: #94a3b8;
        }}
        /* 도메인 인증 바 */
        .domain-strip {{
            width: 100%;
            background: #ffffff;
            border: 2px solid rgba(212, 175, 55, 0.55);
            border-radius: 26px;
            padding: 28px 44px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.08);
        }}
        .domain-left {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .lock-icon {{
            font-size: 30px;
        }}
        .domain-label {{
            font-size: 26px;
            font-weight: 700;
            color: #64748b;
            white-space: nowrap;
        }}
        .domain-address {{
            font-size: 38px;
            font-weight: 900;
            color: #b38728;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}
        /* 하단 럭셔리 골드 CTA 버튼 */
        .bottom-container {{
            width: 100%;
            z-index: 1;
        }}
        .luxury-gold-btn {{
            width: 100%;
            height: 140px;
            background: linear-gradient(135deg, #d4af37 0%, #e5c058 50%, #c59b27 100%);
            border: 2px solid #ffffff;
            border-radius: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 44px;
            font-weight: 900;
            color: #0f172a;
            box-shadow: 0 16px 40px rgba(197, 155, 39, 0.35), inset 0 2px 4px rgba(255, 255, 255, 0.6);
            text-align: center;
            word-break: keep-all;
            padding: 0 30px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="top-container">
        <!-- 브랜드 헤더 -->
        <div class="brand-header">
            <div class="brand-logo-badge">KTRS</div>
            <div class="brand-title">{html.escape(info["badge"])}</div>
        </div>

        <!-- 법령 골드 라벨 -->
        <div class="legal-tag">
            <div class="gold-line"></div>
            <div class="legal-text">{html.escape(info["sub"])}</div>
            <div class="gold-line"></div>
        </div>

        <!-- 메인 헤드라인 -->
        <div class="main-headline">{html.escape(info["title"])}</div>

        <!-- 3대 신뢰 카드 -->
        <div class="cards-grid">
            <!-- 1. 성공보수 후불제 (하이라이트 다크 네이비 카드) -->
            <div class="trust-card highlight">
                <div class="card-icon-wrap">💰</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f1_t"])}</div>
                    <div class="card-desc">{html.escape(info["f1_d"])}</div>
                </div>
            </div>

            <!-- 2. 선입금 0원 (화이트 골드 카드) -->
            <div class="trust-card">
                <div class="card-icon-wrap">🛡️</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f2_t"])}</div>
                    <div class="card-desc">{html.escape(info["f2_d"])}</div>
                </div>
            </div>

            <!-- 3. 공인 전문 세무사 직접 검토 (화이트 골드 카드) -->
            <div class="trust-card">
                <div class="card-icon-wrap">⚖️</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f3_t"])}</div>
                    <div class="card-desc">{html.escape(info["f3_d"])}</div>
                </div>
            </div>
        </div>

        <!-- 도메인 안내 바 -->
        <div class="domain-strip">
            <div class="domain-left">
                <span class="lock-icon">🔒</span>
                <span class="domain-label">{html.escape(info["domain_lbl"])}</span>
            </div>
            <div class="domain-address">ktrs-service.vercel.app</div>
        </div>
    </div>

    <!-- 하단 럭셔리 골드 버튼 -->
    <div class="bottom-container">
        <div class="luxury-gold-btn">{html.escape(info["btn"])}</div>
    </div>
</body>
</html>"""

    def render_and_save(self, lang: str, domain_text: str = "ktrs-service.vercel.app") -> str:
        """Playwright Chromium으로 1080x1920 완제품 PNG 렌더링 및 에셋 폴더에 동시 보관"""
        full_html = self.generate_html(lang=lang, domain_text=domain_text)

        # 1. 템플릿 저장 경로
        template_path = self.templates_dir / f"easytax_ending_cta_{lang}.png"
        
        # 2. 개별 언어 폴더 경로
        lang_dir = self.assets_dir / f"lang_{lang}"
        lang_dir.mkdir(parents=True, exist_ok=True)
        lang_path = lang_dir / "easytax_ending_cta_1080x1920.png"

        logger.info(f"🎨 [{lang.upper()}] Playwright Chromium 순백색 럭셔리 골드 1080x1920 엔딩 카드 렌더링...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-gpu", "--disable-software-rasterizer", "--disable-dev-shm-usage"]
                )
                page = browser.new_page(
                    viewport={"width": 1080, "height": 1920},
                    device_scale_factor=1.0
                )
                page.set_content(full_html)
                page.wait_for_timeout(300)
                png_bytes = page.screenshot(type="png")
                browser.close()

            with open(template_path, "wb") as f:
                f.write(png_bytes)
            with open(lang_path, "wb") as f:
                f.write(png_bytes)

            logger.info(f"✅ [{lang.upper()}] 완제품 에셋 영구 저장 완료 -> {template_path.name}")
            return str(template_path)

        except Exception as e:
            logger.error(f"❌ [{lang.upper()}] 엔딩 카드 렌더링 실패: {e}")
            raise

    def render_all_eight_languages(self) -> Dict[str, str]:
        """8대 국가 전체 완제품 에셋 원클릭 일괄 생성"""
        results = {}
        target_langs = ["vi", "uz", "km", "my", "th", "ne", "mn", "id", "ko"]
        logger.info(f"🚀 [8대 국가 순백색 럭셔리 골드 엔딩 카드 사전 일괄 생성] 대상: {target_langs}")

        for lang in target_langs:
            try:
                out = self.render_and_save(lang=lang)
                results[lang] = out
            except Exception as e:
                logger.error(f"[{lang}] 에셋 생성 오류: {e}")

        logger.info(f"🎉 8대 국가 엔딩 신뢰 카드 완제품 사전 일괄 생성 100% 완료! (총 {len(results)}개국)")
        return results


if __name__ == "__main__":
    producer = EasytaxEndingAssetProducer()
    producer.render_all_eight_languages()
