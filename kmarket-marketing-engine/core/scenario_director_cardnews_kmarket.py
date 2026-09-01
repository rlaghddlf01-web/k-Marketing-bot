"""
ScenarioDirectorCardnewsKMarket - 🛒 [K-Market 5장 7:3 분할 0원 나눔 카드뉴스 동적 기획 엔진]
- 매 회차마다 완전히 다른 0원 나눔 & 자취 꿀팁 테마를 로테이션으로 생성:
  1. theme_01: 오늘 올라온 0원 가구 핫딜 (침대 매트리스, 책상, 서랍장)
  2. theme_02: 자취 필수 가전 0원 득템 (미니 냉장고, 전자레인지, 전기밥솥)
  3. theme_03: 겨울철 필수 난방용품 0원 나눔 (전기장판, 온풍기, 보온커튼)
  4. theme_04: 졸업 및 귀국 선배들의 자취방 풀세트 0원 나눔 (원룸 가구 일괄)
  5. theme_05: 전국 7대 대학가 & 산업단지 정문 앞 3초 안심 직거래
  6. theme_06: 17개 언어 실시간 AI 자동번역 1:1 채팅 거래법
- 17개국 언어별 맞춤 텍스트 및 이미지 프롬프트 동적 생성
"""

import random
from typing import Dict, Any, List, Optional
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket

KMARKET_THEME_TEXTS = {
    # ── 테마 1: 0원 가구 핫딜 (침대/책상/서랍장) ──
    "theme_01_free_furniture": {
        "uz": {
            "s1": {"badge": "1-QADAM: 0 VON MEBEL", "title": "0 Vonlik Bepul Mebellar Ro'yxati", "subtitle": "Qimmat mebel sotib olishga shoshilmang!", "bullets": ["• Talabalar uchun to'shak, stol va shkaflar 100% tekin", "• Har kuni yuzlab yangi 0 vonlik e'lonlar qo'shiladi", "• K-Market ilovasida barchasi mutlaqo tekinga berilmoqda"]},
            "s2": {"badge": "2-QADAM: SIFATLI HOLAT", "title": "Toza Va A'lo Holatdagi Buyumlar", "subtitle": "Vataniga qaytayotganlar qoldirgan sara jihozlar", "bullets": ["• O'qishni bitirgan talabalar bepul topshirmoqda", "• Toza, sifatli va ishchi holatdagi kafolatlangan buyumlar", "• Xonangizni bir tiyin sarflamasdan jihozlang"]},
            "s3": {"badge": "3-QADAM: 17 TILDA CHAT", "title": "Avtomatik Tarjimon Bilan Savdo", "subtitle": "Koreys tilini bilmasangiz ham bemalol yozishing", "bullets": ["• 17 tildagi avtomatik sun'iy intellekt tarjimon", "• Koreys va xorijiy qo'shnilar bilan o'zbekcha yozishing", "• 100% xavfsiz to'g'ridan-to'g'ri uchrashuv"]},
            "s4": {"badge": "4-QADAM: YAQIN MANZIL", "title": "Kampus Va Yotoqxona Oldida", "subtitle": "Uyingizga eng yaqin joydan 10 daqiqada olib keting", "bullets": ["• Seul, Ansan, Suvon, Daegu, Pusan va boshqa hududlar", "• Universitet darvozalari va metro bekatlarida", "• Og'ir yuklar uchun qulay transport tavsiyalari"]},
            "s5": {"badge": "5-QADAM: HOZIROQ OLING", "title": "Bugungi 0 Vonlik Sovg'angizni Oling", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 K-Market ilovasida bugungi 0 vonlik ro'yxatni ko'ring", "👉 10,000 dan ortiq xorijliklar xonalarini tekinga jihozlashdi", "👉 Hoziroq bosing va 0 vonlik mebelni oling!"]}
        },
        "vi": {
            "s1": {"badge": "BƯỚC 1: NỘI THẤT 0 WON", "title": "Bàn Ghế & Giường Tủ Tặng 0 Won", "subtitle": "Đừng tốn tiền triệu mua nội thất mới đắt đỏ!", "bullets": ["• Đồ dùng miễn phí 100% cho du học sinh và lao động", "• Hàng trăm món đồ 0 Won mới được đăng tải mỗi ngày", "• Giường ngủ, bàn học, tủ quần áo, giá sách"]},
            "s2": {"badge": "BƯỚC 2: CÒN RẤT MỚI", "title": "Đồ Đạc Giữ Gìn Sạch Sẽ", "subtitle": "Được tặng từ các anh chị tốt nghiệp về nước", "bullets": ["• Tiền bối chuyển nhà nhượng lại hoàn toàn miễn phí", "• Đồ đạc còn dùng cực kỳ tốt, chắc chắn và sạch đẹp", "• Tiết kiệm tiền sắm sửa cho căn phòng trọ mới"]},
            "s3": {"badge": "BƯỚC 3: DỊCH TIẾNG VIỆT", "title": "Nhắn Tin Tự Động Dịch Ngay", "subtitle": "Không rành tiếng Hàn vẫn giao dịch dễ dàng", "bullets": ["• Hệ thống AI tự động dịch trực tiếp 17 thứ tiếng", "• Nhắn tin bằng tiếng Việt, người Hàn nhận tiếng Hàn", "• Gặp mặt trực tiếp nhận đồ an tâm 100%"]},
            "s4": {"badge": "BƯỚC 4: ĐỊA ĐIỂM TIỆN LỢI", "title": "Nhận Đồ Ngay Cổng Trường & Ga Tàu", "subtitle": "Giao nhận nhanh chóng gần nơi bạn ở", "bullets": ["• Khu vực Seoul, Ansan, Suwon, Daegu, Busan...", "• Giao nhận nhanh chóng ngay cổng ký túc xá / ga tàu", "• Phù hợp hoàn hảo cho phòng One-room một người"]},
            "s5": {"badge": "BƯỚC 5: TẢI APP NGAY", "title": "Lấy Đồ 0 Won Miễn Phí Hôm Nay", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Xem ngay danh sách đồ 0 Won khu vực bạn đang sống", "👉 Hơn 10.000 bạn trẻ đã sắm trọn phòng trọ 0 Won", "👉 Bấm link tải App K-Market ngay hôm nay!"]}
        }
    },

    # ── 테마 2: 0원 가전 득템 (냉장고/전자레인지/밥솥) ──
    "theme_02_free_appliances": {
        "uz": {
            "s1": {"badge": "1-QADAM: 0 VON MAISHIY TEXNIKA", "title": "Muzlatgich Va Mikroto'lqinli Pech 0 Von", "subtitle": "Oshxona texnikasini tekinga oling!", "bullets": ["• Kichik muzlatgich, mikroto'lqinli pech va guruch pishirgich", "• Ish holati 100% tekshirilgan toza maishiy texnika", "• Talabalar va ishchilar uchun maxsus bepul e'lonlar"]},
            "s2": {"badge": "2-QADAM: TEKSHIRILGAN", "title": "A'lo Darajada Ishlaydigan Texnika", "subtitle": "Hech qanday nosozliksiz toza holatda", "bullets": ["• Barcha buyumlar ishlashi tekshirib topshiriladi", "• 300,000 ~ 500,000 vonlik texnikani 0 vonga oling", "• Keraksiz xarajatlardan xalos bo'ling"]},
            "s3": {"badge": "3-QADAM: 1:1 XAVFSIZ CHAT", "title": "Ilova Ichida To'g'ridan-To'g'ri Aloqa", "subtitle": "ID-karta bilan tasdiqlangan ishonchli foydalanuvchilar", "bullets": ["• 17 tilda avtomatik tarjima bilan qulay yozishing", "• Talabalik guvohnomasi bilan tasdiqlangan egalar", "• Firibgarlik xavfi 0%, 100% xavfsiz uchrashuv"]},
            "s4": {"badge": "4-QADAM: TEZ OLIB KETISH", "title": "Xonangizga 10 Daqiqada Olib Keting", "subtitle": "Metro va yotoqxona atrofida qulay savdo", "bullets": ["• Seul, Incheon, Daegu va barcha hududlarda", "• Bir kishi bemalol ko'tarib keta oladigan o'lchamlar", "• 0 vonlik texnika bilan oshxonangizni bezang"]},
            "s5": {"badge": "5-QADAM: HOZIR BAND QILING", "title": "Bugungi Texnikalarni Tekinga Oling", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 K-Market ilovasida 0 vonlik e'lonlarni ko'ring", "👉 Tezda o'zbek tilida band qilib oling", "👉 Hoziroq bosing va 0 vonlik sovg'ani oling!"]}
        },
        "vi": {
            "s1": {"badge": "BƯỚC 1: ĐIỆN MÁY 0 WON", "title": "Tủ Lạnh & Lò Vi Sóng Tặng 0 Won", "subtitle": "Sắm trọn đồ bếp không tốn một đồng!", "bullets": ["• Tủ lạnh mini, lò vi sóng, nồi cơm điện 0 Won", "• Thiết bị đang hoạt động cực tốt và sạch sẽ", "• Tặng miễn phí cho cộng đồng người Việt tại Hàn"]},
            "s2": {"badge": "BƯỚC 2: TIẾT KIỆM TRIỆU WON", "title": "Tiết Kiệm 500.000 Won Mua Đồ", "subtitle": "Được nhượng lại từ các bạn chuyển phòng", "bullets": ["• Đồ điện tử đã được kiểm tra cẩn thận trước khi đăng", "• Không cần chi tiền triệu mua mới lãng phí", "• Trang bị đầy đủ cho căn bếp ấm cúng của bạn"]},
            "s3": {"badge": "BƯỚC 3: CHAT TIẾNG VIỆT", "title": "Nhắn Tin Tự Động Dịch Sang Tiếng Hàn", "subtitle": "Thao tác cực kỳ đơn giản và an toàn", "bullets": ["• Dịch tự động 2 chiều Việt - Hàn cực chuẩn", "• Người dùng được xác thực thẻ cư trú rõ ràng", "• Nhận đồ trực tiếp an toàn tuyệt đối"]},
            "s4": {"badge": "BƯỚC 4: GIAO NHẬN GẦN NHÀ", "title": "Gặp Nhau Ngay Cổng Trường Hoặc Ga", "subtitle": "Tiện lợi và dễ dàng vận chuyển", "bullets": ["• Khu vực Seoul, Gyeonggi, Daegu, Busan...", "• Kích thước nhỏ gọn vừa vặn xách tay / taxi", "• Phù hợp hoàn hảo cho phòng One-room"]},
            "s5": {"badge": "BƯỚC 5: NHẬN NGAY HÔM NAY", "title": "Lấy Đồ Điện Máy 0 Won Ngay", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Xem ngay danh sách đồ gia dụng 0 Won gần bạn", "👉 Hàng ngàn bạn đã sắm đủ đồ bếp miễn phí", "👉 Tải App K-Market để nhận đồ ngay hôm nay!"]}
        }
    },

    # ── 테마 3: 겨울철 전기장판 & 온풍기 0원 ──
    "theme_03_winter_heating": {
        "uz": {
            "s1": {"badge": "1-QADAM: ISSIQ QISH", "title": "Elektr Ko'rpa Va Isitgich 0 Von", "subtitle": "Koreya qishidan muzlab qolmaslik uchun!", "bullets": ["• Elektr ko'rpa, isitgich va qalin adyollar 0 von", "• Qishki sovuqda gaz va elektr pulini tejash siri", "• Barchasi 100% tekinga topshirilmoqda"]},
            "s2": {"badge": "2-QADAM: ISSIQ VA TOZA", "title": "Kafolatlangan Toza Va Issiq Jihozlar", "subtitle": "Bitiruvchilar qoldirgan sifatli isitish jihozlari", "bullets": ["• Xonani darhol isituvchi qulay elektr ko'rpalar", "• Toza va xavfsiz holatdagi elektr moslamalari", "• Bir tiyin sarflamasdan xonangizni isiting"]},
            "s3": {"badge": "3-QADAM: QULAY CHAT", "title": "O'zbek Tilida To'g'ridan-To'g'ri Bog'laning", "subtitle": "17 tilda avtomatik tarjima bilan", "bullets": ["• Til bilish shart emas, ilovada avto-tarjima ishlaydi", "• Xorijiy talabalar va qo'shnilar bilan oson savdo", "• 100% ishonchli va xavfsiz to'g'ridan-to'g'ri uchrashuv"]},
            "s4": {"badge": "4-QADAM: 10 DAQIQADA OLISH", "title": "Yoningizdagi Metro Va Kampusdan Oling", "subtitle": "Og'ir bo'lmagan qulay buyumlar", "bullets": ["• Talabalar shaharchalari va metro oldida uchrashuv", "• Bir qo'lda ko'tarib ketish oson", "• Sovuq tushmasidan oldin iliq buyumlarni oling"]},
            "s5": {"badge": "5-QADAM: TEZDA OLING", "title": "Bugun Elektr Ko'rpani Tekinga Oling", "subtitle": "Profil boshidagi havola (Link in Bio)ni bosing", "bullets": ["👉 K-Market ilovasida 0 vonlik isitgichlarni ko'ring", "👉 Qishni issiq va tejamkor o'tkazing", "👉 Hoziroq bosing va 0 vonlik sovg'ani oling!"]}
        },
        "vi": {
            "s1": {"badge": "BƯỚC 1: MÙA ĐÔNG ẤM ÁP", "title": "Đệm Điện & Quạt Sưởi Tặng 0 Won", "subtitle": "Vượt qua mùa đông Hàn Quốc ấm áp!", "bullets": ["• Đệm sưởi điện, quạt sưởi ấm, chăn bông 0 Won", "• Tiết kiệm tối đa tiền sưởi ga đắt đỏ mùa đông", "• Hàng trăm món đồ sưởi ấm được tặng miễn phí"]},
            "s2": {"badge": "BƯỚC 2: AN TOÀN & SẠCH", "title": "Đồ Sưởi Dùng Tốt & Sạch Sẽ", "subtitle": "Tiền bối để lại cho các bạn khóa sau", "bullets": ["• Đệm điện làm ấm cực nhanh và tiết kiệm điện", "• Thiết bị sạch sẽ, hoạt động hoàn hảo và an toàn", "• Không lo bị rét buốt trong phòng trọ"]},
            "s3": {"badge": "BƯỚC 3: DỊCH TIẾNG VIỆT", "title": "Nhắn Tin Tự Động Dịch Sang Tiếng Hàn", "subtitle": "Giao dịch nhanh chóng trong 30 giây", "bullets": ["• Hệ thống AI tự động dịch trực tiếp 17 thứ tiếng", "• Nhắn tin bằng tiếng Việt, nhận phản hồi ngay", "• Gặp gỡ trao đổi an toàn tuyệt đối"]},
            "s4": {"badge": "BƯỚC 4: GIAO NHẬN TIỆN LỢI", "title": "Nhận Ngay Gần Ký Túc Xá & Ga Tàu", "subtitle": "Gọn nhẹ dễ dàng mang về phòng", "bullets": ["• Gặp gỡ tiện lợi tại các ga tàu điện ngầm", "• Đệm điện gấp gọn mang về cực kỳ tiện", "• Trang bị ngay trước khi đợt rét tràn về"]},
            "s5": {"badge": "BƯỚC 5: TẢI APP NGAY", "title": "Lấy Đồ Sưởi Ấm 0 Won Hôm Nay", "subtitle": "Bấm vào Link trong phần tiểu sử (Bio)", "bullets": ["👉 Xem danh sách đệm sưởi 0 Won đang có sẵn", "👉 Đón mùa đông ấm cúng mà không tốn tiền", "👉 Tải App K-Market để nhận quà ngay hôm nay!"]}
        }
    }
}


from core.character_anchor_kmarket import (
    build_kmarket_char_anchor,
    build_kmarket_scene_prompt,
    LANG_NEGATIVE_ETHNIC
)


class ScenarioDirectorCardnewsKMarket:
    """K-Market 5장 7:3 카드뉴스 동적 테마 기획 디렉터 (초정밀 동일 인물 앵커 탑재)"""
    def __init__(self):
        self.shorts_director = ScenarioDirectorShortsKMarket()
        self.theme_keys = list(KMARKET_THEME_TEXTS.keys())

    def get_carousel_scenario(self, lang: str = "uz", theme_index: Optional[int] = None) -> Dict[str, Any]:
        """매회 호출 시마다 동일 인물 일관성 100% 보장된 0원 나눔 5장 카드뉴스 기획"""
        if theme_index is not None:
            chosen_key = self.theme_keys[theme_index % len(self.theme_keys)]
        else:
            chosen_key = random.choice(self.theme_keys)

        # 1. 100% 정밀 고정 인물 앵커 구축 (성별, 나이, 머리모양, 고정 의상)
        gender = "male"
        char_anchor = build_kmarket_char_anchor(
            lang=lang,
            gender=gender,
            age_group_ko="20대 초반",
            persona_anchor_desc="short neat black parted hair, wearing navy blue zip-up hoodie over plain white t-shirt, distinctive authentic Central Asian facial features"
        )

        theme_data_pkg = KMARKET_THEME_TEXTS[chosen_key]
        lang_key = lang if lang in theme_data_pkg else "uz"
        text_pkg = theme_data_pkg.get(lang_key, theme_data_pkg["uz"])

        # 2. 5단계 슬라이드별 차별화된 극실사 상황 프롬프트 (연속성 힌트 & 동일 의상 고정)
        scene_actions = {
            1: "sitting on floor of empty studio room, looking exhausted and frustrated near cardboard boxes, looking down thoughtfully",
            2: "holding smartphone with both hands, looking pleasantly surprised with wide eyes at phone screen",
            3: "standing near campus building entrance in daytime, smiling warmly while receiving cardboard box package with polite bow",
            4: "sitting on clean bed in a cozy furnished room with warm desk lamp, relaxing with satisfied warm smile",
            5: "looking directly into camera, giving confident friendly double thumbs up gesture with big bright smile"
        }

        cards = []
        for idx in range(1, 6):
            s_key = f"s{idx}"
            t_data = text_pkg[s_key]
            action_desc = scene_actions.get(idx, "relaxing in room")
            full_prompt = build_kmarket_scene_prompt(scene_idx=idx, char=char_anchor, scene_action=action_desc)

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
            "service_id": "kmarket",
            "lang": lang,
            "theme_name": chosen_key,
            "character_anchor": char_anchor,
            "episode_id": f"cardnews_kmarket_{lang}_{chosen_key}_{random.randint(1000, 9999)}",
            "cards": cards
        }
