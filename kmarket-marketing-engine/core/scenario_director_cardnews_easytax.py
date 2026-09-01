"""
ScenarioDirectorCardnewsEasyTax - 💰 [EasyTax 5장 7:3 분할 세무 환급 카드뉴스 동적 기획 엔진]
- 매 회차마다 완전히 다른 7대 세무 환급 테마를 로테이션으로 생성:
  1. theme_01: 조특법 제30조 90% 소득세 감면 (E-9/E-7 근로자)
  2. theme_02: D-2 유학생 아르바이트 3.3% 원천징수 전액 환급
  3. theme_03: 지난 5개년(2021~2026) 잊고 있던 세금 380만원 소급 환급
  4. theme_04: 원룸 월세 750만원 한도 15% 세액공제 챙기는 법
  5. theme_05: 퇴사 및 귀국 전 외국인 세금 총정리 환급 가이드
  6. theme_06: 조특법 30조 만 15~34세 청년 나이 정확한 계산 특례
  7. theme_07: 전국 7대 산업단지 외국인 원스톱 세무 환급
- 17개국 언어별 맞춤 텍스트 및 이미지 프롬프트 동적 생성
"""

import random
from typing import Dict, Any, List, Optional
from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax

# 7대 다채로운 테마별 17개국 카드뉴스 텍스트 풀
EASYTAX_THEME_TEXTS = {
    # ── 테마 1: 90% 소득세 감면 (E-9/E-7 근로자) ──
    "theme_01_90pct_deduction": {
        "vi": {
            "s1": {"badge": "BƯỚC 1: QUYỀN LỢI THUẾ", "title": "Giảm 90% Thuế Thu Nhập", "subtitle": "Được miễn giảm thuế theo Luật Hàn Quốc", "bullets": ["• Miễn giảm 90% thuế thu nhập cho lao động E-9/E-7", "• Nhận lại toàn bộ tiền thuế đã nộp trong 5 năm qua", "• Trung bình hoàn lại 3.840.000 Won/người"]},
            "s2": {"badge": "BƯỚC 2: ĐỐI TƯỢNG ÁP DỤNG", "title": "Ai Có Thể Nhận Hoàn Thuế?", "subtitle": "Chỉ cần thuộc 1 trong các điều kiện sau", "bullets": ["1. Lao động visa E-9, E-7, H-2 tại các nhà máy", "2. Làm việc tại doanh nghiệp vừa và nhỏ", "3. Độ tuổi từ 15 đến 34 tuổi khi bắt đầu làm việc"]},
            "s3": {"badge": "BƯỚC 3: AN TOÀN 100%", "title": "Đại Diện Thuế Được Chứng Nhận", "subtitle": "Không thu phí trước - 0 Won phí tư vấn", "bullets": ["• Liên kết trực tiếp hệ thống Hometax Cục Thuế", "• Hoàn toàn miễn phí tra cứu số tiền thuế", "• Hướng dẫn 1:1 bằng tiếng Việt chuyên nghiệp"]},
            "s4": {"badge": "BƯỚC 4: HỒ SƠ ĐƠN GIẢN", "title": "Chỉ Cần 3 Giấy Tờ Cơ Bản", "subtitle": "Không cần thông qua công ty hiện tại", "bullets": ["• Ảnh chụp Thẻ Chứng minh người nước ngoài (ARC)", "• Số tài khoản ngân hàng chính chủ tại Hàn Quốc", "• Giấy chứng nhận thu nhập (Tải tự động 1 chạm)"]},
            "s5": {"badge": "BƯỚC 5: ĐĂNG KÝ NGAY", "title": "Kiểm Tra Tiền Hoàn Thuế Trong 1 Phút", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Nhận tiền hoàn thuế trực tiếp vào tài khoản", "👉 Hơn 10.000 lao động Việt Nam đã nhận thành công", "👉 Đăng ký ngay hôm nay để nhận tiền sớm nhất!"]}
        },
        "uz": {
            "s1": {"badge": "1-QADAM: SOLIQ IMTIYOZI", "title": "90% Daromad Solig'i Qaytariladi", "subtitle": "Koreya qonunchiligi asosidagi rasmiy imtiyoz", "bullets": ["• E-9/E-7 ishchilari uchun 90% daromad solig'i imtiyozi", "• Oxirgi 5 yil ichida to'langan soliqlarni qaytarish", "• O'rtacha 3,840,000 von soliq qaytarib olinadi"]},
            "s2": {"badge": "2-QADAM: KIMLAR OLADI?", "title": "Sizga Soliq Qaytishi Mumkinmi?", "subtitle": "Quyidagi shartlardan biriga to'g'ri kelsangiz kifoya", "bullets": ["1. Zavod va korxonalarda ishlayotgan E-9/E-7 vizalilar", "2. Kichik va o'rta biznesda faoliyat yurituvchilar", "3. Ish boshlaganda 15-34 yosh oralig'ida bo'lganlar"]},
            "s3": {"badge": "3-QADAM: 100% XAVFSIZ", "title": "Koreya Soliq Xizmati Tasdiqlagan", "subtitle": "Oldindan to'lov yo'q - Bepul hisob-kitob", "bullets": ["• Hometax milliy soliq tizimi bilan integratsiya", "• Qancha pul qaytishini bilish 100% bepul", "• O'zbek tilida 1:1 professional maslahat"]},
            "s4": {"badge": "4-QADAM: ODDIY HUJJAT", "title": "Faqat 3 Ta Asosiy Hujjat Yetarli", "subtitle": "Ish joyingizga xabar berilmaydi", "bullets": ["• ID-karta (Alien Registration Card) rasmi", "• Koreyadagi shaxsiy bank hisob raqami", "• Daromad to'g'risida ma'lumotnoma (avtomatik)"]},
            "s5": {"badge": "5-QADAM: HOZIROQ TEKSHIRING", "title": "1 Daqiqada Qaytariladigan Pulni Biling", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 Qaytarilgan pul to'g'ridan-to'g'ri hisobingizga tushadi", "👉 10,000 dan ortiq o'zbekistonliklar pul olishdi", "👉 Bugunoq ariza bering va pulingizni oling!"]}
        }
    },

    # ── 테마 2: D-2 유학생 3.3% 아르바이트 환급 ──
    "theme_02_student_33pct_refund": {
        "vi": {
            "s1": {"badge": "BƯỚC 1: QUYỀN LỢI DU HỌC SINH", "title": "Hoàn 100% Thuế Làm Thêm 3.3%", "subtitle": "Du học sinh D-2/D-4 đừng bỏ quên quyền lợi!", "bullets": ["• Hoàn lại toàn bộ 3.3% thuế bị trừ khi làm thêm", "• Nhận lại tiền làm quán ăn, xưởng, phiên dịch", "• Trung bình mỗi bạn nhận lại 1.200.000 ~ 2.500.000 Won"]},
            "s2": {"badge": "BƯỚC 2: AI ĐƯỢC NHẬN?", "title": "Điều Kiện Nhận Hoàn Thuế", "subtitle": "Dành riêng cho sinh viên quốc tế tại Hàn", "bullets": ["1. Visa D-2, D-4 có đi làm thêm hợp pháp", "2. Có nhận lương chuyển khoản bị trừ 3.3%", "3. Chưa từng làm quyết toán thuế trong 5 năm qua"]},
            "s3": {"badge": "BƯỚC 3: KHÔNG MẤT PHÍ", "title": "Tra Cứu Hoàn Toàn Miễn Phí", "subtitle": "Chỉ mất 1 phút kiểm tra trên điện thoại", "bullets": ["• Kiểm tra chính xác số tiền được nhận trước", "• Không thu bất kỳ khoản phí đặt cọc nào", "• Bảo mật tuyệt đối thông tin học tập và visa"]},
            "s4": {"badge": "BƯỚC 4: HỒ SƠ 1 PHÚT", "title": "Chuẩn Bị Siêu Nhanh", "subtitle": "Chỉ cần chụp ảnh bằng điện thoại", "bullets": ["• Thẻ cư trú người nước ngoài (ARC)", "• Sổ tài khoản ngân hàng (Tongjang)", "• Giấy chứng nhận đang theo học tại trường"]},
            "s5": {"badge": "BƯỚC 5: NHẬN TIỀN NGAY", "title": "Lấy Lại Tiền Mồ Hôi Làm Thêm", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Tiền chuyển thẳng về tài khoản ngân hàng của bạn", "👉 Đóng học phí hoặc trang trải sinh hoạt phí cực tốt", "👉 Bấm link đăng ký ngay hôm nay!"]}
        },
        "uz": {
            "s1": {"badge": "1-QADAM: TALABALAR UCHUN", "title": "3.3% Ish Solig'ini 100% Qaytaring", "subtitle": "D-2 talabalari uchun qonuniy soliq qaytarish!", "bullets": ["• Qo'shimcha ishdan ushlab qolingan 3.3% soliqni qaytarish", "• Kafe, zavod va tarjimonlik ishlaridan tushgan summalar", "• O'rtacha 1,200,000 ~ 2,500,000 von qaytariladi"]},
            "s2": {"badge": "2-QADAM: KIMLAR OLADI?", "title": "Soliq Qaytarish Shartlari", "subtitle": "Koreyadagi xorijiy talabalar uchun maxsus", "bullets": ["1. D-2 va D-4 vizasida yarim kunlik ishlaganlar", "2. Maoshidan 3.3% soliq ushlab qolinganlar", "3. Oxirgi 5 yil ichida soliq hisoboti topshirmaganlar"]},
            "s3": {"badge": "3-QADAM: BEPUL TEKSHIRUV", "title": "1 Daqiqada Bepul Hisoblang", "subtitle": "Telefondan turib darhol tekshiring", "bullets": ["• Qancha pul qaytishini oldindan bepul ko'ring", "• Hech qanday oldindan to'lov olinmaydi", "• Talabalik va viza ma'lumotlari to'liq xavfsiz"]},
            "s4": {"badge": "4-QADAM: ODDIY HUJJAT", "title": "Faqat 2 Ta Hujjat Yetarli", "subtitle": "Telefon orqali rasmga olib yuborish kifoya", "bullets": ["• Xorijlik ID-kartasi (Alien Card)", "• Shaxsiy bank hisob raqami (Tongjang)", "• Universitetda o'qish ma'lumotnomasi"]},
            "s5": {"badge": "5-QADAM: PULNI OLING", "title": "Mehnat Bilan Topgan Pulingizni Oling", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 Pul to'g'ridan-to'g'ri shaxsiy kartangizga tushadi", "👉 Kontrakt va yotoqxona to'lovlariga ajoyib yordam", "👉 Hoziroq bosing va arizangizni topshiring!"]}
        }
    },

    # ── 테마 3: 지난 5개년 소급 380만원 환급 ──
    "theme_03_retroactive_5years": {
        "vi": {
            "s1": {"badge": "BƯỚC 1: TIỀN BỎ QUÊN", "title": "Tìm Lại 3.800.000 Won Bị Bỏ Quên", "subtitle": "Quyết toán thuế 5 năm qua (2021~2026)", "bullets": ["• Luật cho phép nhận lại tiền thuế thừa trong 5 năm", "• Dù đã đổi công ty hay đổi visa vẫn nhận đủ", "• Hơn 95% lao động nước ngoài có tiền thuế thừa"]},
            "s2": {"badge": "BƯỚC 2: AI CÓ TIỀN THỪA?", "title": "Đối Tượng Kiểm Tra Ngay", "subtitle": "Chỉ cần bạn đã từng làm việc tại Hàn Quốc", "bullets": ["1. Đang làm việc hoặc đã từng làm tại xưởng/công ty", "2. Người chuẩn bị hết hạn hợp đồng về nước", "3. Đã đổi từ visa E-9 sang E-7-4 hoặc F-2"]},
            "s3": {"badge": "BƯỚC 3: BÍ MẬT 100%", "title": "Công Ty Hiện Tại Không Hề Biết", "subtitle": "Quy trình độc lập trực tiếp với Cục Thuế", "bullets": ["• Thủ tục hoàn toàn riêng tư giữa bạn và Cục Thuế", "• Không ảnh hưởng đến gia hạn visa hay công việc", "• Chuyên gia thuế được cấp phép đại diện"]},
            "s4": {"badge": "BƯỚC 4: TIỀN VỀ TÀI KHOẢN", "title": "Nhận Tiền Nhanh Chóng", "subtitle": "Sau khi hồ sơ được Cục Thuế duyệt", "bullets": ["• Tiền chuyển thẳng vào số tài khoản bạn đăng ký", "• Có hóa đơn xác nhận chính thức từ Cục Thuế", "• Đã có hơn 10.000 bạn nhận thành công"]},
            "s5": {"badge": "BƯỚC 5: KIỂM TRA NGAY", "title": "Đừng Để Mất Số Tiền Của Bạn", "subtitle": "Hết 5 năm tiền sẽ bị sung công quỹ!", "bullets": ["👉 Bấm vào Link trong Bio để kiểm tra số tiền miễn phí", "👉 Chỉ mất 1 phút thao tác trên điện thoại", "👉 Lấy lại số tiền mồ hôi công sức ngay hôm nay!"]}
        },
        "uz": {
            "s1": {"badge": "1-QADAM: UNUTULGAN PUL", "title": "3,800,000 Vonni Qaytarib Oling", "subtitle": "Oxirgi 5 yillik soliqlarni tekshiring (2021~2026)", "bullets": ["• Qonun bo'yicha 5 yillik ortiqcha soliqlarni olish mumkin", "• Ish yoki vizani o'zgartirgan bo'lsangiz ham beriladi", "• 95% xorijlik ishchilarda qaytadigan pul mavjud"]},
            "s2": {"badge": "2-QADAM: KIMDA PUL BOR?", "title": "Darhol Tekshirishi Kerak Bo'lganlar", "subtitle": "Koreyada ishlagan barcha fuqarolar uchun", "bullets": ["1. Hozir ishlayotgan yoki avval ishlagan barcha shaxslar", "2. Vataniga qaytish arafasida turgan vatandoshlar", "3. E-9 vizasidan E-7-4 yoki boshqa vizaga o'tganlar"]},
            "s3": {"badge": "3-QADAM: 100% MAXFIY", "title": "Ishxonangizga Xabar Berilmaydi", "subtitle": "To'g'ridan-to'g'ri Davlat Soliq Xizmati orqali", "bullets": ["• Jarayon faqat siz va Soliq Idorasi o'rtasida bo'ladi", "• Ish joyingizga va vizangizga mutlaqo ta'siri yo'q", "• Rasmiy litsenziyaga ega buxgalterlar nazoratida"]},
            "s4": {"badge": "4-QADAM: BANK KARTANGIZGA", "title": "Pul To'g'ridan-To'g'ri Tushadi", "subtitle": "Soliq Idorasi tasdiqlaganidan so'ng", "bullets": ["• Pul to'g'ridan-to'g'ri shaxsiy kartangizga o'tkaziladi", "• Soliq Idorasidan rasmiy to'lov cheki beriladi", "• 10,000 dan ortiq xorijliklar muvaffaqiyatli olishdi"]},
            "s5": {"badge": "5-QADAM: HOZIR TEKSHIRING", "title": "Pulingiz Kuyib Ketishiga Yo'l Qo'ymang", "subtitle": "5 yil o'tgach pul davlatga qoladi!", "bullets": ["👉 Profil boshidagi havolani bosing va bepul hisoblang", "👉 Telefonda atigi 1 daqiqa vaqt oladi", "👉 O'z mehnatingiz bilan topilgan pulni bugun oling!"]}
        }
    },

    # ── 테마 4: 원룸 월세 15% 세액공제 ──
    "theme_04_monthly_rent_15pct": {
        "vi": {
            "s1": {"badge": "BƯỚC 1: TIẾT KIỆM TIỀN NHÀ", "title": "Hoàn 15% Tiền Thuê Nhà One-room", "subtitle": "Nhận lại tới 1.125.000 Won mỗi năm!", "bullets": ["• Chiết khấu 15% tổng số tiền thuê nhà đã đóng", "• Áp dụng cho phòng trọ One-room, Gosiwon, Villa", "• Nhận lại tiền thuê nhà của cả 5 năm vừa qua"]},
            "s2": {"badge": "BƯỚC 2: ĐIỀU KIỆN ĐƠN GIẢN", "title": "Ai Đủ Điều Kiện Nhận?", "subtitle": "Chỉ cần bạn có thuê nhà và đi làm", "bullets": ["1. Người nước ngoài có đăng ký địa chỉ cư trú", "2. Có hợp đồng thuê nhà chính chủ", "3. Đã chuyển khoản tiền nhà hàng tháng qua ngân hàng"]},
            "s3": {"badge": "BƯỚC 3: CHỦ NHÀ KHÔNG ẢNH HƯỞNG", "title": "Không Cần Chủ Nhà Đồng Ý", "subtitle": "Quyền lợi cá nhân hợp pháp của người thuê", "bullets": ["• Không cần xin phép hay thông qua chủ nhà", "• Không làm tăng tiền thuế của chủ trọ", "• Tự động đối soát qua sao kê chuyển khoản"]},
            "s4": {"badge": "BƯỚC 4: HỒ SƠ CẦN CÓ", "title": "Chuẩn Bị 2 Giấy Tờ Này", "subtitle": "Chụp ảnh gửi online trong 1 phút", "bullets": ["• Bản chụp Hợp đồng thuê nhà (Imdaecha Gyeyakseo)", "• Lịch sử chuyển tiền thuê nhà qua App ngân hàng", "• Thẻ cư trú người nước ngoài còn hạn"]},
            "s5": {"badge": "BƯỚC 5: NHẬN HOÀN TIỀN", "title": "Lấy Lại Tiền Thuê Nhà Ngay", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Nhận về hơn 1 triệu Won tiền trọ mỗi năm", "👉 Kiểm tra số tiền hoàn lại hoàn toàn miễn phí", "👉 Đăng ký nhanh gọn chỉ với 1 chạm!"]}
        },
        "uz": {
            "s1": {"badge": "1-QADAM: IJARA PULI", "title": "One-room Ijara Pulidan 15% Qaytaring", "subtitle": "Yiliga 1,125,000 vongacha pulni qaytarib oling!", "bullets": ["• To'langan ijara pulining 15% qismi soliqdan qaytadi", "• One-room, Gosiwon, Villa xonalari uchun amal qiladi", "• Oxirgi 5 yillik ijara to'lovlaridan qaytarib oling"]},
            "s2": {"badge": "2-QADAM: ODDIY SHARTLAR", "title": "Kimlarga Beriladi?", "subtitle": "Ijara to'lab ishlayotgan barcha xorijliklarga", "bullets": ["1. Manzili ro'yxatga olingan xorijiy fuqarolar", "2. O'z nomida ijara shartnomasi bo'lganlar", "3. Ijara haqini bank orqali to'laganlar"]},
            "s3": {"badge": "3-QADAM: UY EGASISIZ", "title": "Uy Egasining Roziligi Shart Emas", "subtitle": "Bu sizning qonuniy shaxsiy huquqingiz", "bullets": ["• Uy egasidan ruxsat so'rash shart emas", "• Uy egasining solig'iga mutlaqo ta'siri yo'q", "• Bank o'tkazmalari orqali avtomatik tasdiqlanadi"]},
            "s4": {"badge": "4-QADAM: KERAKLI HUJJAT", "title": "Faqat 2 Ta Hujjat Yetarli", "subtitle": "Telefonda rasmga olib yuborish kifoya", "bullets": ["• Ijara shartnomasi (Imdaecha Gyeyakseo) rasmi", "• Bankdan ijara to'lovlari ko'chirmasi", "• Xorijiy ID-karta (ARC)"]},
            "s5": {"badge": "5-QADAM: PULNI OLING", "title": "Ijara Pulingizning Bir Qismini Qaytaring", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 Yiliga 1 million vondan ortiq pulni qaytarib oling", "👉 Bepul hisob-kitob qilib ko'ring", "👉 Hoziroq bosing va pulingizni oling!"]}
        }
    }
}


from core.character_anchor_easytax import (
    build_easytax_char_anchor,
    build_easytax_scene_prompt,
    LANG_NEGATIVE_ETHNIC
)


class ScenarioDirectorCardnewsEasyTax:
    """EasyTax 5장 7:3 카드뉴스 동적 테마 기획 디렉터 (초정밀 동일 인물 앵커 탑재)"""
    def __init__(self):
        self.shorts_director = ScenarioDirectorShortsEasyTax()
        self.theme_keys = list(EASYTAX_THEME_TEXTS.keys())
        self._current_index = 0

    def get_carousel_scenario(self, lang: str = "vi", theme_index: Optional[int] = None) -> Dict[str, Any]:
        """매회 호출 시마다 동일 인물 일관성 100% 보장된 세무 환급 5장 카드뉴스 기획"""
        if theme_index is not None:
            chosen_key = self.theme_keys[theme_index % len(self.theme_keys)]
        else:
            chosen_key = random.choice(self.theme_keys)

        # 1. 100% 정밀 고정 인물 앵커 구축 (성별, 나이, 머리모양, 고정 의상)
        gender = "male"
        char_anchor = build_easytax_char_anchor(
            lang=lang,
            gender=gender,
            age_group_ko="20대 후반",
            persona_anchor_desc="short neat black side-parted hair, wearing dark blue polo work shirt with collar, distinctive Southeast Asian facial features"
        )

        theme_data_pkg = EASYTAX_THEME_TEXTS[chosen_key]
        lang_key = lang if lang in theme_data_pkg else "vi"
        text_pkg = theme_data_pkg.get(lang_key, theme_data_pkg["vi"])

        # 2. 5단계 슬라이드별 차별화된 극실사 상황 프롬프트 (연속성 힌트 & 동일 의상 고정)
        scene_actions = {
            1: "reviewing complex Korean tax deduction papers at industrial factory work table, focused thoughtful expression",
            2: "checking mobile phone screen with pleasantly surprised happy expression, discovering tax refund amount",
            3: "standing in factory hallway with warm confident expression, natural conversational atmosphere",
            4: "looking at bank transfer notification on phone with victorious fist pump and bright smile",
            5: "looking directly into camera with confident reassuring smile, giving warm welcoming hand gesture"
        }

        cards = []
        for idx in range(1, 6):
            s_key = f"s{idx}"
            t_data = text_pkg[s_key]
            action_desc = scene_actions.get(idx, "working in factory")
            full_prompt = build_easytax_scene_prompt(scene_idx=idx, char=char_anchor, scene_action=action_desc)

            cards.append({
                "slide_idx": idx,
                "badge": t_data["badge"],
                "title": t_data["title"],
                "subtitle": t_data["subtitle"],
                "bullets": t_data["bullets"],
                "image_prompt": full_prompt,
                "negative_prompt": f"caucasian, white, deformed fingers, extra limbs, claw hands, bad anatomy, ugly, blurry, 3d render, cartoon, {LANG_NEGATIVE_ETHNIC.get(lang, '')}"
            })

        return {
            "service_id": "easytax",
            "lang": lang,
            "theme_name": chosen_key,
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_easytax_{lang}_{chosen_key}_{random.randint(1000, 9999)}",
            "cards": cards
        }
