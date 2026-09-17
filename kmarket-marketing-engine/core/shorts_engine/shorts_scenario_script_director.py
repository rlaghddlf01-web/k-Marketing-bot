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

    # 8개국어 22초 3단계 풀 스크립트 템플릿 딕셔너리 (월급에서 떼인 세금 환급 핵심 소구 완벽 반영)
    SCRIPTS_22S = {
        "vi": {
            "country_name": "Vietnam",
            "lang_name": "Tiếng Việt",
            "hook_p1_5s": "Bạn có biết tiền thuế bị trừ từ lương hàng tháng ở Hàn Quốc có thể lấy lại?",
            "hook_p2_5s": "Tôi vừa được hoàn lại 3.100.000 won tiền thuế từ lương qua app KTRS rồi!",
            "hook_0_10s": "Bạn có biết tiền thuế bị trừ từ lương hàng tháng ở Hàn Quốc có thể lấy lại? Tôi vừa được hoàn lại 3.100.000 won tiền thuế từ lương qua app KTRS rồi!",
            "app_10_18s": (
                "Cách làm siêu đơn giản! Chỉ cần nhập mức lương, "
                "số tiền thuế được hoàn 3.100.000 won hiện ra ngay lập tức!"
            ),
            "cta_18_22s": (
                "Hoàn toàn miễn phí ban đầu, 100% nhận tiền thuế rồi mới thanh toán! "
                "Nhấp vào link bên dưới để kiểm tra miễn phí ngay nhé!"
            ),
            "top_header": "HOÀN 90% THUẾ THU NHẬP • KTRS",
            "bottom_step1_title": "HOÀN 3.100.000 WON THUẾ LƯƠNG",
            "bottom_step1_sub": "Kiểm tra thuế bị trừ từ lương trong 1 phút",
            "bottom_step2_title": "CHỌN LƯƠNG 250 VẠN • HOÀN 3.100.000 WON",
            "bottom_step2_sub": "Trực tiếp liên kết NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "KIỂM TRA MIỄN PHÍ >"
        },
        "uz": {
            "country_name": "Uzbekistan",
            "lang_name": "O'zbek",
            "hook_p1_5s": "Har oy oyligingizdan ushlab qolingan soliqni bilasizmi?",
            "hook_p2_5s": "Men KTRS orqali oylikdan ushlab qolingan 3.100.000 von soliqni qaytarib oldim!",
            "hook_0_10s": "Har oy oyligingizdan ushlab qolingan soliqni bilasizmi? Men KTRS orqali oylikdan ushlab qolingan 3.100.000 von soliqni qaytarib oldim!",
            "app_10_18s": (
                "Juda oson! Ilovada oylik maoshingizni kiritib, "
                "3.100.000 von soliq qaytarmasini darhol hisoblab oling!"
            ),
            "cta_18_22s": (
                "Oldindan hech qanday to'lov yo'q, 100% pul tushgach to'laysiz! "
                "Quyidagi havoladan soliq qaytarmasini hoziroq bepul tekshiring!"
            ),
            "top_header": "90% SOLIQ QAYTARISH • KTRS",
            "bottom_step1_title": "3.100.000 VON SOLIQ QAYTARILDI",
            "bottom_step1_sub": "Oylikdan ushlab qolingan soliqni 1 daqiqada tekshiring",
            "bottom_step2_title": "MAOSH 2.5 MLN • 3.100.000 VON SOLIQ",
            "bottom_step2_sub": "NTS Hometax rasmiy xizmati • E-7, E-9 visa",
            "cta_button_text": "HOZIROQ TEKSHIRING >"
        },
        "km": {
            "country_name": "Cambodia",
            "lang_name": "ភាសាខ្មែរ",
            "hook_p1_5s": "បងប្អូនធ្វើការនៅកូរ៉េ! តើដឹងទេថាពន្ធកាត់ពីប្រាក់ខែអាចបង្វិលមកវិញបាន?",
            "hook_p2_5s": "ខ្ញុំទើបតែទទួលបានការបង្វិលពន្ធ 3,100,000 វ៉ុនពីប្រាក់ខែតាម KTRS App!",
            "hook_0_10s": (
                "បងប្អូនធ្វើការនៅកូរ៉េ! តើដឹងទេថាពន្ធកាត់ពីប្រាក់ខែអាចបង្វិលមកវិញបាន? "
                "ខ្ញុំទើបតែទទួលបានការបង្វិលពន្ធ 3,100,000 វ៉ុនពីប្រាក់ខែតាម KTRS App!"
            ),
            "app_10_18s": (
                "ងាយស្រួលណាស់! គ្រាន់តែជ្រើសរើសប្រាក់ខែរបស់អ្នក... "
                "មើលចុះ! ប្រាក់ពន្ធបង្វិល 3,100,000 វ៉ុនបានបង្ហាញភ្លាមៗ!"
            ),
            "cta_18_22s": (
                "មិនមានការបង់ប្រាក់មុនទេ សេវាគិតក្រោយ 100%! "
                "សូមចុច Link ខាងក្រោមដើម្បីពិនិត្យប្រាក់ពន្ធឥតគិតថ្លៃឥឡូវនេះ!"
            ),
            "top_header": "បង្វិលពន្ធ 90% • KTRS APP",
            "bottom_step1_title": "បង្វិលពន្ធកាត់ពីប្រាក់ខែ 3,100,000 វ៉ុន",
            "bottom_step1_sub": "ពិនិត្យប្រាក់ពន្ធកាត់ពីប្រាក់ខែក្នុង 1 នាទី",
            "bottom_step2_title": "ប្រាក់ខែ 2.5 លាន • បង្វិល 3,100,000 វ៉ុន",
            "bottom_step2_sub": "ភ្ជាប់ជាមួយ NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "ពិនិត្យឥតគិតថ្លៃ >"
        },
        "id": {
            "country_name": "Indonesia",
            "lang_name": "Bahasa Indonesia",
            "hook_p1_5s": "Teman-teman di Korea! Tahu nggak kalau pajak yang dipotong dari gaji bulanan bisa diambil kembali?",
            "hook_p2_5s": "Saya baru saja terima pengembalian pajak gaji 3.100.000 won lewat KTRS!",
            "hook_0_10s": (
                "Teman-teman di Korea! Tahu nggak kalau pajak yang dipotong dari gaji bulanan bisa diambil kembali? "
                "Saya baru saja terima pengembalian pajak gaji 3.100.000 won lewat KTRS!"
            ),
            "app_10_18s": (
                "Caranya gampang banget! Cukup masukkan gaji bulanan... "
                "Lihat, perkiraan dana pengembalian pajak 3.100.000 won langsung muncul!"
            ),
            "cta_18_22s": (
                "100% tanpa biaya di awal, bayar hanya setelah uang cair! "
                "Klik link di bawah sekarang untuk cek pajak gratis!"
            ),
            "top_header": "PENGEMBALIAN PAJAK 90% • KTRS",
            "bottom_step1_title": "PENGEMBALIAN PAJAK GAJI 3.100.000 WON",
            "bottom_step1_sub": "Cek pajak dipotong dari gaji dalam 1 menit",
            "bottom_step2_title": "GAJI 2.5 JUTA • ESTIMASI 3.100.000 WON",
            "bottom_step2_sub": "Terhubung resmi NTS Hometax • Visa E-7, E-9",
            "cta_button_text": "CEK SEKARANG >"
        },
        "kk": {
            "country_name": "Kazakhstan",
            "lang_name": "Қазақша / Русский",
            "hook_p1_5s": "Работаете в Корее? Знаете ли вы, что налог, удержанный с вашей зарплаты, можно вернуть?",
            "hook_p2_5s": "Через KTRS я только что вернул 3.100.000 вон налога с зарплаты!",
            "hook_0_10s": (
                "Работаете в Корее? Знаете ли вы, что налог, удержанный с вашей зарплаты, можно вернуть? "
                "Через KTRS я только что вернул 3.100.000 вон налога с зарплаты!"
            ),
            "app_10_18s": (
                "Все очень просто! Введите вашу зарплату в приложении... "
                "И вот, сумма возврата налога 3.100.000 вон видна сразу!"
            ),
            "cta_18_22s": (
                "Без предоплаты, оплата только после получения денег! "
                "Переходите по ссылке внизу и проверьте налог бесплатно прямо сейчас!"
            ),
            "top_header": "ВОЗВРАТ НАЛОГА 90% • KTRS",
            "bottom_step1_title": "ВОЗВРАТ НАЛОГА С ЗАРПЛАТЫ 3.100.000 W",
            "bottom_step1_sub": "Проверьте удержанный налог за 1 минуту",
            "bottom_step2_title": "ЗАРПЛАТА 2.5 МЛН • ВОЗВРАТ 3.100.000 ВОН",
            "bottom_step2_sub": "Интеграция с NTS Hometax • Визы E-7, E-9",
            "cta_button_text": "ПРОВЕРИТЬ СЕЙЧАС >"
        },
        "tl": {
            "country_name": "Philippines",
            "lang_name": "Tagalog / English",
            "hook_p1_5s": "Working in Korea? Did you know you can get a refund on the taxes deducted from your monthly salary?",
            "hook_p2_5s": "I just got back 3,100,000 won in salary tax refund through KTRS!",
            "hook_0_10s": (
                "Working in Korea? Did you know you can get a refund on the taxes deducted from your monthly salary? "
                "I just got back 3,100,000 won in salary tax refund through KTRS!"
            ),
            "app_10_18s": (
                "It is so easy! Just enter your monthly salary in the app... "
                "Look, your 3,100,000 won tax refund amount shows up right away!"
            ),
            "cta_18_22s": (
                "Zero upfront fees! Pay only after your refund is received safely! "
                "Click the link below to check your tax refund today!"
            ),
            "top_header": "90% TAX REFUND • KTRS APP",
            "bottom_step1_title": "3,100,000 KRW SALARY TAX REFUND",
            "bottom_step1_sub": "Check taxes deducted from salary in 1 min",
            "bottom_step2_title": "SALARY 2.5M KRW • 3,100,000 KRW REFUND",
            "bottom_step2_sub": "Direct NTS Hometax Link • E-7, E-9 Visa",
            "cta_button_text": "CHECK YOUR REFUND >"
        },
        "my": {
            "country_name": "Myanmar",
            "lang_name": "မြန်မာဘာသာ",
            "hook_p1_5s": "ကိုရီးယားမှာ အလုပ်လုပ်နေကြတဲ့ မိတ်ဆွေတို့ရေ! လစာထဲက ဖြတ်တောက်ခံရတဲ့ အခွန်ငွေတွေကို ပြန်လည်ရယူနိုင်တာ သိပါသလား?",
            "hook_p2_5s": "KTRS ကနေ လစာအခွန်ပြန်အမ်းငွေ ဝမ် ၃,၁၀၀,၀၀၀ အခုပဲ ပြန်ရပါပြီ!",
            "hook_0_10s": (
                "ကိုရီးယားမှာ အလုပ်လုပ်နေကြတဲ့ မိတ်ဆွေတို့ရေ! လစာထဲက ဖြတ်တောက်ခံရတဲ့ အခွန်ငွေတွေကို ပြန်လည်ရယူနိုင်တာ သိပါသလား? "
                "KTRS ကနေ လစာအခွန်ပြန်အမ်းငွေ ဝမ် ၃,၁၀၀,၀၀၀ အခုပဲ ပြန်ရပါပြီ!"
            ),
            "app_10_18s": (
                "လုပ်ရတာ အရမ်းလွယ်ကူပါတယ်! လစာကို ထည့်သွင်းလိုက်ရုံနဲ့... "
                "ကြည့်လိုက်ပါ! အခွန်ပြန်အမ်းငွေ ဝမ် ၃,၁၀၀,၀၀၀ ချက်ချင်း တွက်ချက်ပြသပေးပါတယ်!"
            ),
            "cta_18_22s": (
                "ကြိုတင်ပေးသွင်းငွေ လုံးဝ မလိုပါဘူး၊ ငွေဝင်မှ ဝန်ဆောင်ခပေးရတာပါ! "
                "အောက်ပါ လင့်ခ်ကို နှိပ်ပြီး အခွန်ပြန်အမ်းငွေ အခမဲ့ စစ်ဆေးကြည့်လိုက်ပါ!"
            ),
            "top_header": "အခွန် ၉၀% လျှော့ပေါ့ • KTRS APP",
            "bottom_step1_title": "လစာအခွန် ဝမ် ၃,၁၀၀,၀၀၀ ပြန်အမ်းငွေ ရရှိ",
            "bottom_step1_sub": "လစာမှ ဖြတ်တောက်ခံရသော အခွန်ကို ၁ မိနစ်အတွင်း စစ်ဆေးပါ",
            "bottom_step2_title": "လစာ ၂၅ သိန်း • ဝမ် ၃,၁၀၀,၀၀၀ ပြန်အမ်း",
            "bottom_step2_sub": "NTS Hometax တရားဝင်ချိတ်ဆက် • E-7, E-9",
            "cta_button_text": "အခမဲ့စစ်ဆေးပါ >"
        },
        "th": {
            "country_name": "Thailand",
            "lang_name": "ภาษาไทย",
            "hook_p1_5s": "เพื่อนๆ พี่น้องในเกาหลีครับ! รู้ไหมครับว่าภาษีที่ถูกหักจากเงินเดือนทุกเดือนสามารถขอคืนได้?",
            "hook_p2_5s": "ผมเพิ่งได้เงินคืนภาษีจากเงินเดือน 3,100,000 วอนผ่านแอป KTRS มาเลยครับ!",
            "hook_0_10s": (
                "เพื่อนๆ พี่น้องในเกาหลีครับ! รู้ไหมครับว่าภาษีที่ถูกหักจากเงินเดือนทุกเดือนสามารถขอคืนได้? "
                "ผมเพิ่งได้เงินคืนภาษีจากเงินเดือน 3,100,000 วอนผ่านแอป KTRS มาเลยครับ!"
            ),
            "app_10_18s": (
                "ขั้นตอนง่ายนิดเดียว! แค่กรอกเงินเดือน... "
                "ดูสิครับ! ยอดเงินคืนภาษี 3,100,000 วอนจะคำนวณขึ้นมาทันทีเลย!"
            ),
            "cta_18_22s": (
                "ฟรีค่าบริการล่วงหน้า 0 วอน! เงินเข้าจริงค่อยจ่าย มั่นใจได้ 100%! "
                "คลิกลิงก์ด้านล่างเพื่อเช็คเงินคืนภาษีฟรีตอนนี้ได้เลยครับ!"
            ),
            "top_header": "คืนภาษี 90% • KTRS APP",
            "bottom_step1_title": "คืนภาษีหักจากเงินเดือน 3,100,000 วอน",
            "bottom_step1_sub": "เช็คเงินคืนภาษีจากเงินเดือนใน 1 นาที",
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
        theme_id: Optional[str] = None,
        gender: Optional[str] = None
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
                amount=amount,
                gender=gender
            )
            res_lang = scenario.get("lang", "vi")
            if not scenario.get("country_name"):
                scenario["country_name"] = self.SCRIPTS_22S.get(res_lang, self.SCRIPTS_22S["vi"])["country_name"]
            return scenario
        except Exception as e:
            logger.error(f"❌ 제미나이 실시간 디렉팅 중 에러 발생: {e}")

        effective_lang = lang or "vi"
        base_cfg = self.SCRIPTS_22S.get(effective_lang, self.SCRIPTS_22S["vi"])
        amount_fmt = f"{amount:,}"
        full_speech = f"{base_cfg['hook_0_10s']} {base_cfg['app_10_18s']} {base_cfg['cta_18_22s']}"
        return {
            "country_name": base_cfg["country_name"],
            "lang": effective_lang,
            "amount": amount,
            "amount_formatted": amount_fmt,
            "speech_hook_part1": base_cfg.get("hook_p1_5s", base_cfg["hook_0_10s"]).replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
            "speech_hook_part2": base_cfg.get("hook_p2_5s", "").replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
            "speech_hook": base_cfg["hook_0_10s"].replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
            "speech_app": base_cfg["app_10_18s"].replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
            "speech_cta": base_cfg["cta_18_22s"],
            "full_speech": full_speech.replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
            "visual_direction": {
                "top_header": base_cfg["top_header"],
                "bottom_step1_title": base_cfg["bottom_step1_title"].replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
                "bottom_step1_sub": base_cfg["bottom_step1_sub"],
                "bottom_step2_title": base_cfg["bottom_step2_title"].replace("3.100.000", amount_fmt).replace("3,100,000", amount_fmt),
                "bottom_step2_sub": base_cfg["bottom_step2_sub"],
                "domain_text": "ktrs-service.vercel.app",
                "cta_button_text": base_cfg.get("cta_button_text", "HOZIROQ TEKSHIRING >")
            }
        }

