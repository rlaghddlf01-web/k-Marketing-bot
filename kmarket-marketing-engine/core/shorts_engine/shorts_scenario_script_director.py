# -*- coding: utf-8 -*-
"""
ShortsScenarioScriptDirector - 🎬 [이지텍스 22초 3단계 다국어 대본 & 비주얼 오버레이 디렉터]
- 시나리오 디렉터 60대 테마 및 7대 페르소나 연계
- 1명의 주인공이 이끄는 22초 3단계 단일 스토리라인 생성:
  1) [0초 ~ 10초] 인물 립싱크 킬러 훅 (모국어 1분 조회 + 310만원 입금 체감)
  2) [10초 ~ 18초] 라이브 앱 조작 안내 (12개월 슬라이더 + 월급 250만 원 + 310만원 계산 연출)
  3) [18초 ~ 22초] 안심 신뢰 뱃지 & 최종 행동 촉구 CTA (선입금 0원, 100% 후불제, 도메인 연결)
- 상단/하단 분할 솔리드 박스형 자막 (인물과 앱 본문 시야 100% 확보, 이모지 깨짐 0%)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ShortsScenarioScriptDirector")


class ShortsScenarioScriptDirector:
    """22초 완결형 숏폼 다국어 대본 및 화면 오버레이 기획 엔진"""

    # 8개국어 22초 3단계 풀 스크립트 템플릿 딕셔너리
    SCRIPTS_22S = {
        "vi": {
            "country_name": "Vietnam",
            "lang_name": "Tiếng Việt",
            "hook_0_10s": (
                "Các bạn lao động tại Hàn Quốc ơi! "
                "Đã thử tra cứu hoàn thuế bằng tiếng mẹ đẻ trong 1 phút chưa? "
                "Tôi vừa dùng app KTRS và đã nhận 3.100.000 won về tài khoản rồi đấy!"
            ),
            "app_10_18s": (
                "Cách làm siêu đơn giản! Chỉ cần chọn số tháng làm việc và mức lương... "
                "Nhìn này, số tiền hoàn lại 3.100.000 won hiện ra ngay lập tức!"
            ),
            "cta_18_22s": (
                "Hoàn toàn miễn phí ban đầu, 100% nhận tiền rồi mới thanh toán! "
                "Nhấp vào link bên dưới để kiểm tra miễn phí ngay nhé!"
            ),
            "top_header": "HOÀN 90% THUẾ THU NHẬP • KTRS",
            "bottom_step1_title": "ĐÃ NHẬN 3.100.000 WON VỀ TÀI KHOẢN",
            "bottom_step1_sub": "Tra cứu hoàn thuế bằng tiếng mẹ đẻ trong 1 phút",
            "bottom_step2_title": "CHỌN LƯƠNG 250 VẠN • HOÀN 3.100.000 WON",
            "bottom_step2_sub": "Trực tiếp liên kết NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "KIỂM TRA MIỄN PHÍ >"
        },
        "uz": {
            "country_name": "Uzbekistan",
            "lang_name": "O'zbek",
            "hook_0_10s": (
                "Koreyada ishlayotgan vatandoshlar! "
                "Ona tilingizda 1 daqiqada soliq qaytarmasini tekshirib ko'rdingizmi? "
                "Men ham KTRS ilovasi orqali 3.100.000 vonni hisobimga oldim!"
            ),
            "app_10_18s": (
                "Juda oson! Ilovada ishlagan oylaringiz va oylik maoshingizni tanlasangiz... "
                "Qarang, 3.100.000 von qaytarilishi darhol chiqib keladi!"
            ),
            "cta_18_22s": (
                "Oldindan hech qanday to'lov yo'q, 100% pul tushgach to'laysiz! "
                "Hoziroq quyidagi havola orqali bepul tekshiring!"
            ),
            "top_header": "90% SOLIQ QAYTARMASI • KTRS",
            "bottom_step1_title": "3.100.000 VON HISOBGA TUSHDI",
            "bottom_step1_sub": "Ona tilingizda 1 daqiqada bepul tekshiring",
            "bottom_step2_title": "MAOSH 2.5 MLN • 3.100.000 VON QAYTADI",
            "bottom_step2_sub": "NTS Hometax rasmiy xizmati • E-7, E-9 visa",
            "cta_button_text": "HOZIROQ TEKSHIRING >"
        },
        "km": {
            "country_name": "Cambodia",
            "lang_name": "ភាសាខ្មែរ",
            "hook_0_10s": (
                "បងប្អូនធ្វើការនៅកូរ៉េ! "
                "តើបានពិនិត្យមើលការបង្វិលពន្ធជាភាសាខ្មែរក្នុង 1 នាទីហើយឬនៅ? "
                "ខ្ញុំទើបតែទទួលបាន 3,100,000 វ៉ុនចូលគណនីតាមរយៈ KTRS App!"
            ),
            "app_10_18s": (
                "ងាយស្រួលណាស់! គ្រាន់តែជ្រើសរើសចំនួនខែនិងប្រាក់ខែរបស់អ្នក... "
                "មើលចុះ! ប្រាក់ពន្ធ 3,100,000 វ៉ុនបានបង្ហាញភ្លាមៗ!"
            ),
            "cta_18_22s": (
                "មិនមានការបង់ប្រាក់មុនទេ សេវាគិតក្រោយ 100%! "
                "សូមចុច Link ខាងក្រោមដើម្បីពិនិត្យឥតគិតថ្លៃឥឡូវនេះ!"
            ),
            "top_header": "បង្វិលពន្ធ 90% • KTRS APP",
            "bottom_step1_title": "ទទួលបាន 3,100,000 វ៉ុនចូលគណនី",
            "bottom_step1_sub": "ពិនិត្យមើលការបង្វិលពន្ធជាភាសាខ្មែរក្នុង 1 នាទី",
            "bottom_step2_title": "ប្រាក់ខែ 2.5 លាន • បង្វិល 3,100,000 វ៉ុន",
            "bottom_step2_sub": "ភ្ជាប់ជាមួយ NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "ពិនិត្យឥតគិតថ្លៃ >"
        },
        "id": {
            "country_name": "Indonesia",
            "lang_name": "Bahasa Indonesia",
            "hook_0_10s": (
                "Teman-teman pekerja di Korea! "
                "Sudah cek pengembalian pajak pakai bahasa kita dalam 1 menit? "
                "Saya baru saja terima 3.100.000 won langsung ke rekening lewat aplikasi KTRS!"
            ),
            "app_10_18s": (
                "Caranya gampang banget! Cukup pilih lama kerja dan gaji bulanan... "
                "Lihat, perkiraan dana 3.100.000 won langsung muncul!"
            ),
            "cta_18_22s": (
                "100% tanpa biaya di awal, bayar hanya setelah uang cair! "
                "Klik link di bawah sekarang untuk cek gratis!"
            ),
            "top_header": "DISKON PAJAK 90% • KTRS APP",
            "bottom_step1_title": "CAIR 3.100.000 WON KE REKENING",
            "bottom_step1_sub": "Cek pengembalian pajak dalam 1 menit",
            "bottom_step2_title": "GAJI 2.5 JUTA • ESTIMASI 3.100.000 WON",
            "bottom_step2_sub": "Terhubung resmi NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "CEK SEKARANG >"
        },
        "kk": {
            "country_name": "Kazakhstan",
            "lang_name": "Қазақша / Русский",
            "hook_0_10s": (
                "Работаете в Корее? "
                "Проверяли возврат налогов на родном языке всего за 1 минуту? "
                "Я через приложение KTRS только что получил на счет 3.100.000 вон!"
            ),
            "app_10_18s": (
                "Все очень просто! Выбираете срок работы и зарплату в приложении... "
                "И вот, сумма возврата 3.100.000 вон видна сразу!"
            ),
            "cta_18_22s": (
                "Без предоплаты, оплата только после получения денег! "
                "Переходите по ссылке внизу и проверьте бесплатно прямо сейчас!"
            ),
            "top_header": "ВОЗВРАТ НАЛОГА 90% • KTRS",
            "bottom_step1_title": "ПОЛУЧЕНО 3.100.000 ВОН НА СЧЕТ",
            "bottom_step1_sub": "Расчет возврата налога за 1 минуту",
            "bottom_step2_title": "ЗАРПЛАТА 2.5 МЛН • ВОЗВРАТ 3.100.000 ВОН",
            "bottom_step2_sub": "Интеграция с NTS Hometax • Визы E-7, E-9",
            "cta_button_text": "ПРОВЕРИТЬ СЕЙЧАС >"
        },
        "tl": {
            "country_name": "Philippines",
            "lang_name": "Tagalog / English",
            "hook_0_10s": (
                "Calling all workers in Korea! "
                "Have you checked your tax refund in your native language in just 1 minute? "
                "I just received 3,100,000 won directly into my account through the KTRS app!"
            ),
            "app_10_18s": (
                "It is so easy! Just select how long you worked and your monthly salary... "
                "Look, your 3,100,000 won refund amount shows up right away!"
            ),
            "cta_18_22s": (
                "Zero upfront fees! Pay only after your refund is received safely! "
                "Click the link below to check your free estimate today!"
            ),
            "top_header": "90% TAX EXEMPTION • KTRS APP",
            "bottom_step1_title": "RECEIVED 3,100,000 KRW TO ACCOUNT",
            "bottom_step1_sub": "Check your tax refund in just 1 minute",
            "bottom_step2_title": "SALARY 2.5M KRW • 3,100,000 KRW REFUND",
            "bottom_step2_sub": "Direct NTS Hometax Link • E-7, E-9 Visa",
            "cta_button_text": "CHECK YOUR REFUND >"
        },
        "my": {
            "country_name": "Myanmar",
            "lang_name": "မြန်မာဘာသာ",
            "hook_0_10s": (
                "ကိုရီးယားမှာ အလုပ်လုပ်နေကြတဲ့ မိတ်ဆွေတို့ရေ! "
                "မိခင်ဘာသာစကားနဲ့ ၁ မိနစ်အတွင်း အခွန်ပြန်အမ်းငွေ စစ်ဆေးပြီးပြီလား? "
                "ကျွန်တော်လည်း KTRS app ကနေ ဝမ် ၃,၁၀၀,၀၀၀ အခုပဲ အကောင့်ထဲ ရောက်လာပါပြီ!"
            ),
            "app_10_18s": (
                "လုပ်ရတာ အရမ်းလွယ်ကူပါတယ်! လုပ်သက်ကာလနဲ့ လစာကို ရွေးချယ်လိုက်ရုံနဲ့... "
                "ကြည့်လိုက်ပါ! ပြန်အမ်းငွေ ဝမ် ၃,၁၀၀,၀၀၀ ချက်ချင်း တွက်ချက်ပြသပေးပါတယ်!"
            ),
            "cta_18_22s": (
                "ကြိုတင်ပေးသွင်းငွေ လုံးဝ မလိုပါဘူး၊ ငွေဝင်မှ ဝန်ဆောင်ခပေးရတဲ့ စိတ်ချရဆုံး ဝန်ဆောင်မှုပါ! "
                "အောက်ပါ လင့်ခ်ကို နှိပ်ပြီး အခမဲ့ စစ်ဆေးကြည့်လိုက်ပါ!"
            ),
            "top_header": "အခွန် ၉၀% လျှော့ပေါ့ • KTRS APP",
            "bottom_step1_title": "ဝမ် ၃,၁၀၀,၀၀၀ အကောင့်ထဲ ရောက်ရှိ",
            "bottom_step1_sub": "မိခင်ဘာသာစကားဖြင့် ၁ မိနစ်အတွင်း စစ်ဆေးပါ",
            "bottom_step2_title": "လစာ ၂၅ သိန်း • ဝမ် ၃,၁၀၀,၀၀၀ ပြန်အမ်း",
            "bottom_step2_sub": "NTS Hometax တရားဝင်ချိတ်ဆက် • E-7, E-9",
            "cta_button_text": "အခမဲ့စစ်ဆေးပါ >"
        },
        "th": {
            "country_name": "Thailand",
            "lang_name": "ภาษาไทย",
            "hook_0_10s": (
                "เพื่อนๆ พี่น้องที่ทำงานในเกาหลีครับ! "
                "เคยเช็คเงินคืนภาษีเป็นภาษาไทยใน 1 นาทีหรือยังครับ? "
                "ผมเพิ่งได้รับเงิน 3,100,000 วอนเข้าบัญชีผ่านแอป KTRS มาสดๆ ร้อนๆ เลยครับ!"
            ),
            "app_10_18s": (
                "ขั้นตอนง่ายนิดเดียว! แค่เลือกระยะเวลาทำงานกับเงินเดือน... "
                "ดูสิครับ! ยอดเงินคืน 3,100,000 วอนคำนวณขึ้นมาทันทีเลย!"
            ),
            "cta_18_22s": (
                "ฟรีค่าบริการล่วงหน้า 0 วอน! เงินเข้าจริงค่อยจ่าย มั่นใจได้ 100%! "
                "คลิกลิงก์ด้านล่างเพื่อเช็คสิทธิ์ฟรีตอนนี้ได้เลยครับ!"
            ),
            "top_header": "ลดหย่อนภาษี 90% • KTRS APP",
            "bottom_step1_title": "เงินเข้าบัญชี 3,100,000 วอนเรียบร้อย",
            "bottom_step1_sub": "เช็คเงินคืนภาษีภาษาไทยใน 1 นาที",
            "bottom_step2_title": "เงินเดือน 2.5 ล้าน • คืน 3,100,000 วอน",
            "bottom_step2_sub": "เชื่อมต่อ NTS Hometax • วีซ่า E-7, E-9",
            "cta_button_text": "เช็คสิทธิ์ฟรีทันที >"
        }
    }

    def __init__(self):
        from .gemini_shorts_visual_director import GeminiShortsVisualDirector
        self.gemini_director = GeminiShortsVisualDirector()
        logger.info("🎬 [ShortsScenarioScriptDirector] 제미나이 실시간 비주얼 디렉터 연동 초기화 완료")

    def get_full_scenario(
        self,
        lang: Optional[str] = None,
        amount: int = 3100000,
        theme_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        제미나이 AI와 60대 시나리오 테마를 연동하여 실시간으로 22초 대본과 박스 자막 및 색상 팔레트 생성
        (lang이 None이거나 'auto'인 경우 제미나이가 테마에 최적화된 8대 국가를 자동 선택)
        """
        # 1. 시나리오 테마 추출
        chosen_theme = None
        try:
            from core.scenario_director_shorts_easytax import EASYTAX_60_THEMES
            if theme_id:
                chosen_theme = next((t for t in EASYTAX_60_THEMES if t.get("id") == theme_id), None)
            if not chosen_theme:
                import random
                chosen_theme = random.choice(EASYTAX_60_THEMES)
        except Exception as e:
            logger.warning(f"테마 매트릭스 로드 예외: {e}")
            chosen_theme = {"name": "한국 세금 90% 소득세 감면 및 환급", "target": "외국인 근로자", "persona_type": "E-9/E-7 근로자", "refund_est": amount}

        # 2. 제미나이 실시간 비주얼 디렉터 호출
        try:
            scenario = self.gemini_director.generate_visual_direction(
                lang=lang,
                theme_info=chosen_theme,
                amount=amount
            )
            res_lang = scenario.get("lang", "vi")
            if not scenario.get("country_name"):
                scenario["country_name"] = self.SCRIPTS_22S.get(res_lang, self.SCRIPTS_22S["vi"])["country_name"]
            return scenario
        except Exception as e:
            logger.error(f"❌ 제미나이 실시간 디렉팅 중 에러 발생: {e}")


        # 3. 폴백 기본 반환
        base_cfg = self.SCRIPTS_22S.get(lang, self.SCRIPTS_22S["vi"])
        amount_fmt = f"{amount:,}"
        full_speech = f"{base_cfg['hook_0_10s']} {base_cfg['app_10_18s']} {base_cfg['cta_18_22s']}"

        return {
            "country_name": base_cfg["country_name"],
            "lang": lang,
            "amount": amount,
            "amount_formatted": amount_fmt,
            "speech_hook": base_cfg["hook_0_10s"],
            "speech_app": base_cfg["app_10_18s"],
            "speech_cta": base_cfg["cta_18_22s"],
            "full_speech": full_speech,
            "visual_direction": {
                "top_header": base_cfg["top_header"],
                "bottom_step1_title": base_cfg["bottom_step1_title"],
                "bottom_step1_sub": base_cfg["bottom_step1_sub"],
                "bottom_step2_title": base_cfg["bottom_step2_title"],
                "bottom_step2_sub": base_cfg["bottom_step2_sub"],
                "domain_text": "ktrs-service.vercel.app",
                "cta_button_text": base_cfg.get("cta_button_text", "KIỂM TRA MIỄN PHÍ >")
            }
        }

