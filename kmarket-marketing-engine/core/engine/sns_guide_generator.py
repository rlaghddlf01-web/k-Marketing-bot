# -*- coding: utf-8 -*-
"""
SNSGuideGenerator - 📢 [다국어 4대 SNS 포스팅 패키지 생성 전담 모듈]
- 타깃 현지어(우즈베크어, 몽골어, 베트남어 등) 원문 복사용 텍스트
- 관리자용 한국어 대조/해설 텍스트 2단 병기 제공
- 지원 채널: 🧵 스레드 (Threads), 📸 인스타그램 (Instagram), 📘 페이스북 (Facebook), ✈️ 텔레그램 (Telegram)
"""

from typing import Dict, Any, List
from pathlib import Path

# 언어별 국가명 및 고유 해시태그 사전
LANG_INFO: Dict[str, Dict[str, str]] = {
    "uz": {
        "name_ko": "우즈베키스탄 (Uzbekistan)",
        "name_native": "O'zbekiston",
        "hashtags": "#EasyTax #SoliqQaytarish #DaromadSoligi #E9Visa #JanubiyKoreya #OzbeklarKoreyada #KoreyadaHayot #E7Visa #KTRS #SoliqMaslahati",
    },
    "mn": {
        "name_ko": "몽골 (Mongolia)",
        "name_native": "Монгол",
        "hashtags": "#EasyTax #ТатварБуцаанОлголт #E9Виз #СолонгосДахьМонголчууд #СолонгосынАмьдрал #ТатварынХөнгөлөлт #KTRS #ЭхОрондооБуцах",
    },
    "vi": {
        "name_ko": "베트남 (Vietnam)",
        "name_native": "Việt Nam",
        "hashtags": "#EasyTax #HoànThuế #ThuếThuNhập #E9Visa #LaoĐộngHànQuốc #CuộcSốngHànQuốc #ViệtNamTạiHàn #이지택스 #외국인세금환급 #조특법30조",
    },
    "th": {
        "name_ko": "태국 (Thailand)",
        "name_native": "ประเทศไทย",
        "hashtags": "#EasyTax #ขอคืนภาษีเกาหลี #แรงงานไทยในเกาหลี #วีซ่าE9 #ชีวิตในเกาหลี #คนไทยในเกาหลี #KTRS #สิทธิแรงงาน",
    },
    "km": {
        "name_ko": "캄보디아 (Cambodia)",
        "name_native": "កម្ពុជា",
        "hashtags": "#EasyTax #បង្វិលពន្ធកូរ៉េ #ពលករខ្មែរនៅកូរ៉េ #ទិដ្ឋាការE9 #ជីវិតនៅកូរ៉េ #KTRS #ពន្ធលើប្រាក់ចំណូល",
    },
    "ne": {
        "name_ko": "네팔 (Nepal)",
        "name_native": "नेपाल",
        "hashtags": "#EasyTax #कोरियाकरफिर्ता #नेपालीकोरिया #E9भिसा #कोरियामाजीवन #KTRS #आम्दानीकर",
    },
    "id": {
        "name_ko": "인도네시아 (Indonesia)",
        "name_native": "Indonesia",
        "hashtags": "#EasyTax #RefundPajakKorea #TKIJepangKorea #VisaE9 #PekerjaMigranIndonesia #KTRS #PajakPenghasilan",
    },
    "my": {
        "name_ko": "미얀마 (Myanmar)",
        "name_native": "မြန်မာ",
        "hashtags": "#EasyTax #ကိုရီးယားအခွန်ပြန်အမ်းငွေ #မြန်မာလုပ်သား #E9ဗီဇာ #KTRS #အခွန်ပြန်အမ်း",
    },
    "ru": {
        "name_ko": "러시아/중앙아시아 (Russian)",
        "name_native": "Русский",
        "hashtags": "#EasyTax #ВозвратНалогаКорея #РаботаВКорее #ВизаE9 #РусскоязычныеВКорее #KTRS #НалогиКорея",
    },
    "zh": {
        "name_ko": "중국 (China)",
        "name_native": "中文",
        "hashtags": "#EasyTax #韩国退税 #退税申请 #E9签证 #韩国打工 #在韩华人 #KTRS #退税查询",
    },
    "en": {
        "name_ko": "영어 (Global English)",
        "name_native": "English",
        "hashtags": "#EasyTax #KoreaTaxRefund #E9Visa #WorkInKorea #ForeignWorker #KTRS #TaxRefundKorea",
    },
}

# 4대 채널별 17개국 현지어 카피 사전
CHANNEL_COPY_TEMPLATES: Dict[str, Dict[str, Dict[str, str]]] = {
    "uz": {
        "threads": (
            "🔥 {card1_title} ({amount_fmt})\n\n"
            "Janubiy Koreya Davlat Soliq Idorasi (NTS) qonuniy imtiyozi bo'yicha daromad solig'ini 90% gacha qaytarib olishingiz mumkin.\n"
            "So'nggi 5 yil davomida to'langan soliqlarni 1 daqiqada bepul hisoblab ko'ring.\n"
            "Oldindan to'lov 0 von! Pul sizning hisobingizga tushgandan so'ng xizmat haqi olinadi.\n\n"
            "👉 Bepul tekshirish: {link}"
        ),
        "instagram": (
            "🇰🇷 Janubiy Koreyada ishlayotgan vatandoshlar diqqatiga!\n"
            "\"{card1_title} - {amount_fmt} hisobingizga tushdi!\"\n\n"
            "Xorijiy ishchilar uchun 90% daromad solig'i imtiyozi (Soliq qonuni 30-moddasi).\n"
            "Ariza topshirish orqali so'nggi 5 yil davomida to'langan soliqlarni bank kartangizga qaytarib oling 💸\n\n"
            "✨ EasyTax-ning 3 ta asosiy kafolati:\n"
            "1️⃣ Oldindan to'lov 0 von! (Avval pul tushadi, keyin hisob-kitob)\n"
            "2️⃣ Litsenziyalangan soliq kompaniyasi orqali 100% qonuniy NTS rasmiylashtirish\n"
            "3️⃣ Smartfonda 1 daqiqada bepul hisob-kitob!\n\n"
            "🔍 Hozir profil havolasini (Link in Bio) bosing va qaytariladigan pulingizni tekshiring!\n\n"
            "{hashtags}"
        ),
        "facebook": (
            "📢 [MUHIM E'LON] {theme_title} - Soliqni 90% gacha qaytarib olish imkoniyati ({amount_fmt})\n\n"
            "Koreyaning zavod, qurilish, qishloq xo'jaligi va logistika sohalarida mehnat qilayotgan yurtdoshlarimiz diqqatiga.\n"
            "So'nggi 5 yil davomida Koreya davlatiga to'lagan daromad solig'ingizning 90% gacha bo'lgan qismini qonuniy ravishda qaytarib olishingiz mumkin.\n\n"
            "📌 Asosiy ma'lumotlar:\n"
            "• O'rtacha qaytariladigan summa: 2,000,000 ~ 4,500,000 KRW ({amount_fmt} haqiqiy misol)\n"
            "• Oldindan hech qanday to'lov yo'q (Avval NTS-dan pul keladi, keyin to'lov)\n"
            "• E-9, E-7, H-2, F-4 va boshqa barcha viza egalari uchun\n\n"
            "⚠️ Diqqat: 5 yillik qonuniy muddat o'tsa, pullar davlat hisobiga o'tib ketadi va qaytarib bo'lmaydi.\n\n"
            "👉 Rasmiy bepul tekshirish havolasi:\n"
            "{link}"
        ),
        "telegram": (
            "⚡ [E'lon] Koreya Davlat Soliq Idorasi - Xorijiy ishchilar uchun soliq qaytarish\n\n"
            "💰 Kutilayotgan summa: {amount_fmt}\n"
            "✅ Ruxsat berilgan vizalar: E-9, E-7, H-2, F-4, D-2 va boshqalar\n"
            "🛡️ Xizmat narxi: 0 von (100% natijadan keyin to'lov, oldindan pul olinmaydi)\n"
            "⏱️ Kerakli vaqt: Smartfonda 1 daqiqa\n\n"
            "🔗 Hozir tekshirish: {link}"
        ),
    },
    "mn": {
        "threads": (
            "🔥 {card1_title} ({amount_fmt})\n\n"
            "БНСУ-ын Татварын албанаас (NTS) гадаад ажилчдын орлогын албан татварыг 90% хүртэл хөнгөлөх хуулийн дагуу буцаан олголт авах боломжтой.\n"
            "Сүүлийн 5 жилийн хугацаанд төлсөн татвараа 1 минутанд үнэгүй тооцоолж үзээрэй.\n"
            "Урьдчилгаа төлбөр 0 вон! Буцаан олголт таны дансанд орсны дараа тооцоо хийгдэнэ.\n\n"
            "👉 Үнэгүй шалгах: {link}"
        ),
        "instagram": (
            "🇰🇷 Солонгост ажиллаж буй Монголчуудын анхааралд!\n"
            "\"{card1_title} - {amount_fmt} дансанд орлоо!\"\n\n"
            "Гадаад ажилчдын орлогын албан татварыг 90% хөнгөлөх хууль ёсны эрх.\n"
            "Хүсэлт гаргаснаар сүүлийн 5 жилд төлсөн татвараа дансандаа найдвартай буцаан аваарай 💸\n\n"
            "✨ EasyTax-ийн 3 баталгаа:\n"
            "1️⃣ Урьдчилгаа 0 вон! (Татварын албанаас мөнгө орсны дараа төлнө)\n"
            "2️⃣ Албан ёсны татварын хуулийн фирмийн 100% хууль ёсны үйлчилгээ\n"
            "3️⃣ Гар утсаараа ердөө 1 минутанд үнэгүй шалгах боломжтой!\n\n"
            "🔍 Профайл дээрх холбоосыг (Link in Bio) дарж буцаан олголтоо шалгаарай!\n\n"
            "{hashtags}"
        ),
        "facebook": (
            "📢 [ЧУХАЛ МЭДЭГДЭЛ] {theme_title} - Татварын 90% хүртэл буцаан олголт авах заавар ({amount_fmt})\n\n"
            "Солонгосын үйлдвэр, барилга, хөдөө аж ахуй, логистикийн салбарт хөдөлмөрлөж буй нийт Монголчууддаа энэ өдрийн мэнд хүргэе.\n"
            "Сүүлийн 5 жилд БНСУ-ын Татварын албанд төлсөн орлогын албан татварынхаа 90 хүртэлх хувийг хуулийн дагуу буцаан авах эрхтэй.\n\n"
            "📌 Гол мэдээлэл:\n"
            "• Дундаж буцаан олголт: 2,000,000 ~ 4,500,000 KRW ({amount_fmt} бодит жишээ)\n"
            "• Урьдчилгаа хураамж 0 вон (Мөнгө дансанд орсны дараа тооцоо хийгдэнэ)\n"
            "• E-9, E-7, H-2, F-4, D-2 зэрэг бүх визтэй иргэд хамрагдах боломжтой\n\n"
            "⚠️ 5 жилийн хугацаа хэтэрвэл мөнгө улсын орлого болж буцаан авах боломжгүй болно.\n\n"
            "👉 Албан ёсны үнэгүй шалгах холбоос:\n"
            "{link}"
        ),
        "telegram": (
            "⚡ [Мэдэгдэл] БНСУ-ын Татварын алба - Гадаад иргэдийн татварын буцаан олголт\n\n"
            "💰 Боломжит буцаан олголт: {amount_fmt}\n"
            "✅ Хамаарах виз: E-9, E-7, H-2, F-4, D-2 гэх мэт\n"
            "🛡️ Урьдчилгаа төлбөр: 0 вон (100% амжилттай болсны дараа төлбөртэй)\n"
            "⏱️ Хугацаа: Гар утсаар 1 минутанд\n\n"
            "🔗 Шалгах холбоос: {link}"
        ),
    },
    "vi": {
        "threads": (
            "🔥 {card1_title} ({amount_fmt})\n\n"
            "Cơ quan Thuế Quốc gia Hàn Quốc (NTS) hỗ trợ hoàn thuế thu nhập lên đến 90% cho lao động nước ngoài.\n"
            "Kiểm tra số tiền thuế đã nộp trong 5 năm qua hoàn toàn miễn phí chỉ trong 1 phút.\n"
            "0 đồng chi phí trả trước! Chỉ thanh toán sau khi tiền thuế đã về tài khoản ngân hàng của bạn an toàn.\n\n"
            "👉 Kiểm tra miễn phí ngay: {link}"
        ),
        "instagram": (
            "🇰🇷 Thông báo hoàn thuế thu nhập chính thức từ Cục Thuế Hàn Quốc (NTS)!\n"
            "\"{card1_title} - Đã nhận {amount_fmt}!\"\n\n"
            "Chính sách giảm 90% thuế thu nhập cho người lao động nước ngoài (Luật Thuế Điều 30).\n"
            "Chỉ cần đăng ký, toàn bộ tiền thuế 5 năm qua sẽ được chuyển thẳng về tài khoản ngân hàng của bạn 💸\n\n"
            "✨ 3 cam kết vàng từ EasyTax:\n"
            "1️⃣ 0 đồng chi phí trước! (Tiền về tài khoản mới thanh toán phí)\n"
            "2️⃣ Xử lý hồ sơ 100% hợp pháp trực tiếp với Cơ quan Thuế Hàn Quốc\n"
            "3️⃣ Kiểm tra số tiền hoàn thuế trên điện thoại chỉ mất đúng 1 phút!\n\n"
            "🔍 Bấm ngay vào đường link ở phần tiểu sử (Link in Bio) để kiểm tra tiền của bạn!\n\n"
            "{hashtags}"
        ),
        "facebook": (
            "📢 [THÔNG BÁO QUAN TRỌNG] {theme_title} - Hướng dẫn nhận hoàn thuế thu nhập 90% ({amount_fmt})\n\n"
            "Gửi toàn thể anh chị em lao động Việt Nam đang làm việc tại các nhà máy, công trường, nông nghiệp tại Hàn Quốc.\n"
            "Bạn có quyền được nhận lại tới 90% số tiền thuế thu nhập cá nhân đã đóng cho Cục Thuế trong 5 năm qua.\n\n"
            "📌 Thông tin cốt lõi:\n"
            "• Số tiền hoàn lại trung bình: 2.000.000 ~ 4.500.000 KRW (Trường hợp thực tế {amount_fmt})\n"
            "• Không mất bất kỳ chi phí đặt cọc hay trả trước nào (Hậu kiểm an toàn 100%)\n"
            "• Áp dụng cho tất cả visa: E-9, E-7, H-2, F-4, D-2\n\n"
            "⚠️ Thời hạn hiệu lực 5 năm đang trôi qua, sau 5 năm số tiền này sẽ bị sung công quỹ vĩnh viễn!\n\n"
            "👉 Đường link kiểm tra hoàn thuế miễn phí chính thức:\n"
            "{link}"
        ),
        "telegram": (
            "⚡ [Thông báo] Cục Thuế Hàn Quốc - Hoàn thuế cho lao động nước ngoài\n\n"
            "💰 Số tiền dự kiến: {amount_fmt}\n"
            "✅ Đối tượng visa: E-9, E-7, H-2, F-4, D-2...\n"
            "🛡️ Phí dịch vụ: 0 VNĐ (Không phí trước, tiền về mới thanh toán)\n"
            "⏱️ Thời gian: 1 phút trên điện thoại\n\n"
            "🔗 Kiểm tra ngay tại đây: {link}"
        ),
    },
}


class SNSGuideGenerator:
    """다국어 4대 SNS 포스팅 패키지 생성기 (현지어 + 한국어 2단 세트 자동 조립)"""

    @classmethod
    def generate_guide_content(
        cls,
        lang: str,
        theme_title: str,
        amount: int,
        cards: List[Dict[str, Any]]
    ) -> str:
        amount_fmt = f"{amount:,} KRW"
        info = LANG_INFO.get(lang, LANG_INFO.get("en", {}))
        lang_name_ko = info.get("name_ko", lang.upper())
        lang_name_native = info.get("name_native", lang.upper())
        hashtags = info.get("hashtags", "#EasyTax #KoreaTaxRefund #E9Visa #WorkInKorea")
        link = f"https://ktrs-service.vercel.app/?lang={lang}"

        card1_title = cards[0].get("title", "") if len(cards) > 0 else ""
        card5_title = cards[4].get("title", "") if len(cards) > 4 else ""

        # 0. 🤖 제미나이 AI 100% 현지어 실시간 4대 SNS 패키지 창작 시도
        native_threads = None
        native_insta = None
        native_fb = None
        native_tg = None
        try:
            from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter
            copywriter = GeminiCardnewsCopywriter(service_id="easytax")
            gemini_pack = copywriter.generate_cardnews_post_package(
                service_id="easytax",
                lang=lang,
                theme={"name": theme_title},
                persona={},
                cards=cards,
                refund_formatted=amount_fmt
            )
            ch = gemini_pack.get("channels", {})
            if ch.get("threads") and ch.get("instagram"):
                native_threads = f"{ch['threads'].get('main_post', '')}\n\n{ch['threads'].get('reply_link', '')}"
                native_insta = f"{ch['instagram'].get('caption', '')}\n\n{ch['instagram'].get('hashtags', hashtags)}"
                native_fb = f"{ch['facebook'].get('post_content', '')}\n\n{ch['facebook'].get('first_comment', '')}"
                native_tg = f"{ch['telegram'].get('caption', '')}\n\n👉 {link}"
        except Exception as e:
            pass

        if not native_threads:
            # 현지어 카피 템플릿 추출 (지원 언어 외에는 범용 템플릿 적용)
            templates = CHANNEL_COPY_TEMPLATES.get(lang)
            if not templates:
                templates = cls._build_generic_templates(lang, card1_title, card5_title, amount_fmt, link, hashtags, theme_title)

            # 1. 🧵 스레드 본문
            native_threads = templates["threads"].format(
                card1_title=card1_title, card5_title=card5_title, amount_fmt=amount_fmt, link=link, hashtags=hashtags, theme_title=theme_title
            )
            native_insta = templates["instagram"].format(
                card1_title=card1_title, card5_title=card5_title, amount_fmt=amount_fmt, link=link, hashtags=hashtags, theme_title=theme_title
            )
            native_fb = templates["facebook"].format(
                card1_title=card1_title, card5_title=card5_title, amount_fmt=amount_fmt, link=link, hashtags=hashtags, theme_title=theme_title
            )
            native_tg = templates["telegram"].format(
                card1_title=card1_title, card5_title=card5_title, amount_fmt=amount_fmt, link=link, hashtags=hashtags, theme_title=theme_title
            )
        ko_threads = (
            f"🔥 {card1_title} ({amount_fmt})\n\n"
            f"대한민국 국세청(NTS) 조세특례제한법 제30조 외국인 소득세 최대 90% 감면 혜택 안내.\n"
            f"지난 5년 동안 성실히 일하며 납부한 세금을 단 1분 만에 무료로 모의 계산해보세요.\n"
            f"착수금/선결제 0원! 국세청에서 환급금이 먼저 입금된 후 정산하는 100% 안전 후불제입니다.\n\n"
            f"👉 무료 확인하기: {link}"
        )

        # 2. 📸 인스타그램 본문
        ko_insta = (
            f"🇰🇷 대한민국 국세청 외국인 근로자 세무 환급 안내\n"
            f"\"{card1_title} - {amount_fmt} 입금 완료!\"\n\n"
            f"외국인 근로자를 위한 90% 소득세 감면 혜택 (조세특례제한법 제30조)\n"
            f"신청만 하면 지난 5년 동안 낸 세금이 내 통장으로 안전하게 입금됩니다 💸\n\n"
            f"✨ 이지택스(EasyTax) 3대 안심 보증:\n"
            f"1️⃣ 착수금/선결제 0원! (국세청 환급금 먼저 입금 후 후불 정산)\n"
            f"2️⃣ 공인 세무법인의 100% 합법 국세청 다이렉트 전산 처리\n"
            f"3️⃣ 스마트폰으로 단 1분 만에 간편 모의 계산 완료!\n\n"
            f"지금 프로필 링크(Link in Bio)를 누르고 숨어있는 내 환급금을 확인하세요! 🔍\n\n"
            f"{hashtags} #외국인세금환급 #조특법30조 #국세청환급 #E9근로자 #E7비자 #환급금조회"
        )

        # 3. 📘 페이스북 본문
        ko_fb = (
            f"📢 [필독] {theme_title} - 소득세 최대 90% 환급 신청 안내 ({amount_fmt})\n\n"
            f"한국의 제조 공장, 농축산, 건설, 물류 현장에서 땀 흘려 일하시는 근로자 여러분 안녕하십니까.\n"
            f"최근 5년 동안 대한민국 국세청에 납부하신 소득세 중 최대 90%를 합법적으로 돌려받으실 수 있습니다.\n\n"
            f"📌 핵심 안내 사항:\n"
            f"• 평균 환급액: 200만 ~ 450만 원 상당 ({amount_fmt} 실사례 다수)\n"
            f"• 선결제 수수료 0원 (국세청에서 입금 확인 후 정산하는 안전 후불제)\n"
            f"• E-9, E-7, H-2, F-4, D-2 등 외국인 근로자 전원 대상\n\n"
            f"5년의 법적 소멸시효가 지나면 세금이 국가로 환수되오니, 지금 바로 공식 링크에서 무료 조회를 진행해보시기 바랍니다.\n\n"
            f"👉 공식 간편 환급 조회:\n"
            f"{link}"
        )

        # 4. ✈️ 텔레그램 본문
        ko_tg = (
            f"⚡ [공지] 대한민국 국세청 외국인 근로자 세금 환급 안내\n\n"
            f"💰 예상 환급금: {amount_fmt}\n"
            f"✅ 대상 비자: E-9, E-7, H-2, F-4, D-2 등 외국인 근로자\n"
            f"🛡️ 수수료: 0원 (100% 성공 후불제, 사전 비용 없음)\n"
            f"⏱️ 소요 시간: 스마트폰 1분 조회\n\n"
            f"🔗 지금 바로 확인하기: {link}"
        )

        doc = f"""================================================================================
📢 [EasyTax 카드뉴스 공식 SNS 포스팅 패키지]
🌍 타깃 국가: {lang_name_ko} ({lang.upper()})
💰 대표 환급금: {amount_fmt}
🎯 카드뉴스 주제: {theme_title}
🔗 공식 간편 환급 링크: {link}
================================================================================
💡 [포스팅 안내]:
- 아래 채널별로 【1. 현지어 복사용 본문】을 복사하여 외국인 커뮤니티에 바로 업로드하십시오.
- 【2. 한국어 관리자 대조/해설본】을 통해 어떤 내용으로 홍보되는지 사전에 검토하실 수 있습니다.
================================================================================


1. 🧵 스레드 (Threads) 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_threads}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_threads}

--------------------------------------------------------------------------------


2. 📸 인스타그램 (Instagram) 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_insta}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_insta}

--------------------------------------------------------------------------------


3. 📘 페이스북 (Facebook) 그룹/커뮤니티 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_fb}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_fb}

--------------------------------------------------------------------------------


4. ✈️ 텔레그램 (Telegram) 단톡방 / 채널 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_tg}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_tg}

================================================================================
"""
        return doc

    @classmethod
    def _build_generic_templates(
        cls,
        lang: str,
        card1_title: str,
        card5_title: str,
        amount_fmt: str,
        link: str,
        hashtags: str,
        theme_title: str
    ) -> Dict[str, str]:
        """사전에 정의되지 않은 기타 언어용 영어/글로벌 베이스 템플릿"""
        return {
            "threads": (
                "🔥 {card1_title} ({amount_fmt})\n\n"
                "Korea National Tax Service (NTS) tax refund benefit up to 90% income tax reduction.\n"
                "Check your tax refund accumulated over the past 5 years for free in just 1 minute.\n"
                "Upfront fee: 0 KRW! Pay only after the refund arrives in your bank account.\n\n"
                "👉 Free check: {link}"
            ),
            "instagram": (
                "🇰🇷 Official Tax Refund Announcement for Foreign Workers in Korea\n"
                "\"{card1_title} - {amount_fmt} Deposited!\"\n\n"
                "90% income tax reduction benefit under Article 30 of the Special Tax Treatment Act.\n"
                "Check your 5-year tax refund safely deposited into your bank account 💸\n\n"
                "✨ 3 Promises of EasyTax:\n"
                "1️⃣ 0 KRW upfront fee! (Pay only after receiving refund from NTS)\n"
                "2️⃣ 100% legal direct NTS processing by certified tax firm\n"
                "3️⃣ Quick 1-minute estimation on mobile phone!\n\n"
                "🔍 Click Link in Bio now to check your hidden refund!\n\n"
                "{hashtags}"
            ),
            "facebook": (
                "📢 [NOTICE] {theme_title} - Tax Refund up to 90% Guide ({amount_fmt})\n\n"
                "To all foreign workers working in Korea's factories, construction, agriculture, and logistics.\n"
                "You are legally entitled to claim back up to 90% of your paid income tax over the past 5 years.\n\n"
                "📌 Key Information:\n"
                "• Average refund: 2,000,000 ~ 4,500,000 KRW (Actual case: {amount_fmt})\n"
                "• 0 KRW upfront fee (100% success-based safe post-payment)\n"
                "• Eligible visas: E-9, E-7, H-2, F-4, D-2 and more\n\n"
                "⚠️ If the 5-year statute of limitations expires, the money cannot be refunded.\n\n"
                "👉 Official Free Estimation Link:\n"
                "{link}"
            ),
            "telegram": (
                "⚡ [Notice] Korea NTS Tax Refund for Foreign Workers\n\n"
                "💰 Estimated refund: {amount_fmt}\n"
                "✅ Eligible visas: E-9, E-7, H-2, F-4, D-2...\n"
                "🛡️ Fee: 0 KRW upfront (Pay only after success)\n"
                "⏱️ Time needed: 1 minute on smartphone\n\n"
                "🔗 Check now: {link}"
            ),
        }

    @classmethod
    def generate_kmarket_guide_content(
        cls,
        lang: str,
        theme_title: str,
        cards: List[Dict[str, Any]],
        item_name: str = "가구/가전"
    ) -> str:
        """KTRS 마켓 0원 나눔 4대 SNS 포스팅 패키지 생성 (현지어 + 한국어 2단 병기)"""
        info = LANG_INFO.get(lang, LANG_INFO.get("en", {}))
        lang_name_ko = info.get("name_ko", lang.upper())
        lang_name_native = info.get("name_native", lang.upper())
        hashtags = f"#KMarket #0WonFree #LifeInKorea #KTRS #SecondhandKorea #ForeignWorker #StudyInKorea"
        link = f"https://kmarket.co.kr/?lang={lang}"

        card1_title = cards[0].get("title", "") if len(cards) > 0 else ""
        card5_title = cards[4].get("title", "") if len(cards) > 4 else ""

        # 0. 🤖 제미나이 AI 100% 현지어 실시간 4대 SNS 패키지 창작 시도
        native_threads = None
        native_insta = None
        native_fb = None
        native_tg = None
        try:
            from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter
            copywriter = GeminiCardnewsCopywriter(service_id="kmarket")
            gemini_pack = copywriter.generate_cardnews_post_package(
                service_id="kmarket",
                lang=lang,
                theme={"name": theme_title, "item": item_name},
                persona={},
                cards=cards
            )
            ch = gemini_pack.get("channels", {})
            if ch.get("threads") and ch.get("instagram"):
                native_threads = f"{ch['threads'].get('main_post', '')}\n\n{ch['threads'].get('reply_link', '')}"
                native_insta = f"{ch['instagram'].get('caption', '')}\n\n{ch['instagram'].get('hashtags', hashtags)}"
                native_fb = f"{ch['facebook'].get('post_content', '')}\n\n{ch['facebook'].get('first_comment', '')}"
                native_tg = f"{ch['telegram'].get('caption', '')}\n\n👉 {link}"
        except Exception as e:
            pass

        if not native_threads:
            # 언어별 K-Market 전용 템플릿
            if lang == "uz":
                native_threads = (
                f"🔥 {card1_title}\n\n"
                f"Koreyada yashayotgan vatandoshlar uchun KTRS Market 0 vonlik bepul buyumlar ulashish xizmati!\n"
                f"Koreyada yashash xarajatlarini 1,500,000 von tejab qoling. Bepul maishiy texnika va mebellarni olib keting.\n"
                f"17 tilda avtomatik tarjima qilinadigan xavfsiz 1:1 chat!\n\n"
                f"👉 Bepul buyumlarni ko'rish: {link}\n\n{hashtags}"
            )
            native_insta = (
                f"🇰🇷 Koreyada yashovchi barcha talabalar va ishchilar diqqatiga!\n"
                f"\"{card1_title}\"\n\n"
                f"KTRS Market orqali 0 von evaziga ajoyib mebel va maishiy texnikalarni bepul oling!\n"
                f"Koreyada dastlabki jihozlash xarajatlarini 1,500,000 KRW gacha tejang 🛋️✨\n\n"
                f"✨ K-Market 3 ta katta afzalligi:\n"
                f"1️⃣ 0 vonlik 100% bepul ulashish va arzon ikkilamchi bozor\n"
                f"2️⃣ Til bilish shart emas: 17 tilda real vaqtda avtomatik tarjima chati\n"
                f"3️⃣ Talabalar va ishchilar uchun ishonchli xavfsiz 1:1 uchrashuv\n\n"
                f"🔍 Hozir profil havolasini (Link in Bio) bosing va bugungi bepul buyumlarni oling!\n\n{hashtags}"
            )
            native_fb = (
                f"📢 [KTRS MARKET 0 VONLIK BEPUL ULASHISH] {theme_title}\n\n"
                f"Koreyada yashayotgan barcha xorijliklar uchun eng kerakli platforma!\n"
                f"Koreyadan vatanga qaytayotgan tanishlar va talabalar qoldirgan toza, sifatli maishiy texnika va mebellarni bepul oling.\n\n"
                f"📌 Asosiy ma'lumotlar:\n"
                f"• 1,500,000 KRW gacha tejash imkoniyati\n"
                f"• Kir yuvish mashinasi, mikroto'lqinli pech, muzlatgich, stol-stullar 100% bepul\n"
                f"• 17 tildagi avtomatik tarjima tufayli koreys tilini bilmasdan ham bemalol gaplashishingiz mumkin\n\n"
                f"👉 Bepul buyumlarni tekshirish havolasi:\n{link}"
            )
            native_tg = (
                f"⚡ [E'lon] K-Market - Koreyada 0 vonlik bepul maishiy texnika va mebellar\n\n"
                f"🎁 Narxi: 0 KRW (100% bepul)\n"
                f"✅ Mahsulotlar: Muzlatgich, kir yuvish mashinasi, mikroto'lqinli pech, krovat va boshqalar\n"
                f"🌐 Xizmat: 17 tilda avtomatik tarjima chati\n\n"
                f"🔗 Hozir ko'rish: {link}"
            )
        elif lang == "mn":
            native_threads = (
                f"🔥 {card1_title}\n\n"
                f"Солонгост амьдарч буй Монголчуудад зориулсан KTRS Market 0 төгрөгөөр үнэгүй эд зүйлс авах боломж!\n"
                f"Амьжиргааны зардлаасаа 1,500,000 вон хэмнээрэй. Цахилгаан бараа, тавилгыг үнэгүй аваарай.\n"
                f"17 хэлээр автоматаар орчуулагддаг найдвартай 1:1 чат!\n\n"
                f"👉 Үнэгүй авах: {link}\n\n{hashtags}"
            )
            native_insta = (
                f"🇰🇷 Солонгост амьдарч буй нийт Монголчуудын анхааралд!\n"
                f"\"{card1_title}\"\n\n"
                f"KTRS Market-ээр дамжуулан 0 воноор чанартай тавилга, гэр ахуйн цахилгаан бараа үнэгүй аваарай!\n"
                f"Гэрийн тохижилтын зардлаа 1,500,000 KRW хүртэл хэмнээрэй 🛋️✨\n\n"
                f"✨ K-Market-ийн 3 давуу тал:\n"
                f"1️⃣ 0 воны 100% үнэгүй зар болон хямд хэрэглэсэн барааны зах\n"
                f"2️⃣ Солонгос хэл мэдэх шаардлагагүй: 17 хэлний бодит цагийн автомат орчуулга\n"
                f"3️⃣ Оюутан, ажилчдад зориулсан аюулгүй 1:1 шууд уулзалт\n\n"
                f"🔍 Профайл дээрх холбоосыг (Link in Bio) дарж өнөөдрийн үнэгүй барааг шалгаарай!\n\n{hashtags}"
            )
            native_fb = (
                f"📢 [KTRS MARKET 0 ВОНЫ ҮНЭГҮЙ БАРАА] {theme_title}\n\n"
                f"Солонгост амьдарч буй гадаад иргэдэд хамгийн хэрэгтэй платформ!\n"
                f"Эх орондоо буцаж буй хүмүүсийн үлдээсэн цэвэрхэн, чанартай цахилгаан бараа, тавилгыг үнэгүй аваарай.\n\n"
                f"📌 Гол мэдээлэл:\n"
                f"• 1,500,000 KRW хүртэл хэмнэх боломж\n"
                f"• Угаалгын машин, богино долгионы зуух, хөргөгч, ширээ сандал 100% үнэгүй\n"
                f"• 17 хэлний автомат орчуулгатай тул хэлний бэрхшээлгүй харилцах боломжтой\n\n"
                f"👉 Албан ёсны үнэгүй бараа шалгах холбоос:\n{link}"
            )
            native_tg = (
                f"⚡ [Мэдэгдэл] K-Market - Солонгос дахь 0 воны үнэгүй тавилга, цахилгаан бараа\n\n"
                f"🎁 Үнэ: 0 KRW (100% үнэгүй)\n"
                f"✅ Бараа: Хөргөгч, угаалгын машин, богино долгионы зуух, ор г.м\n"
                f"🌐 Үйлчилгээ: 17 хэлний автомат орчуулгын чат\n\n"
                f"🔗 Шалгах холбоос: {link}"
            )
        elif lang == "vi":
            native_threads = (
                f"🔥 {card1_title}\n\n"
                f"Nền tảng KTRS Market tặng đồ miễn phí 0đ cho cộng đồng người Việt tại Hàn Quốc!\n"
                f"Tiết kiệm ngay 1.500.000 KRW chi phí sắm đồ sinh hoạt. Nhận đồ gia dụng và nội thất xịn sò hoàn toàn 0đ.\n"
                f"Tính năng chat tự động dịch 17 ngôn ngữ giúp giao dịch an toàn 100%!\n\n"
                f"👉 Xem đồ miễn phí ngay: {link}\n\n{hashtags}"
            )
            native_insta = (
                f"🇰🇷 Gửi toàn thể anh chị em lao động và du học sinh tại Hàn Quốc!\n"
                f"\"{card1_title}\"\n\n"
                f"Nhận đồ nội thất và đồ điện gia dụng xịn sò hoàn toàn 0 đồng trên KTRS Market!\n"
                f"Tiết kiệm tới 1.500.000 KRW tiền sắm sửa ban đầu khi mới sang Hàn 🛋️✨\n\n"
                f"✨ 3 ưu điểm vượt trội của K-Market:\n"
                f"1️⃣ 100% đồ tặng 0 đồng và chợ đồ cũ giá cực rẻ\n"
                f"2️⃣ Không lo rào cản ngôn ngữ: Chat tự động dịch 17 ngôn ngữ theo thời gian thực\n"
                f"3️⃣ Gặp gỡ trực tiếp 1:1 an toàn, tiện lợi cho du học sinh và người lao động\n\n"
                f"🔍 Bấm ngay vào link ở phần tiểu sử (Link in Bio) để nhận đồ miễn phí hôm nay!\n\n{hashtags}"
            )
            native_fb = (
                f"📢 [KTRS MARKET TẶNG ĐỒ 0 ĐỒNG] {theme_title}\n\n"
                f"Cứu cánh cực lớn cho anh chị em du học sinh và lao động tại Hàn Quốc!\n"
                f"Nhận ngay đồ gia dụng, bàn ghế, tủ lạnh, máy giặt từ các anh chị về nước để lại hoàn toàn miễn phí 0đ.\n\n"
                f"📌 Thông tin cốt lõi:\n"
                f"• Tiết kiệm từ 1.500.000 KRW chi phí mua sắm đồ dùng\n"
                f"• Đầy đủ máy giặt, lò vi sóng, nồi cơm điện, bàn học 100% miễn phí\n"
                f"• Không biết tiếng Hàn vẫn chat mượt mà nhờ hệ thống tự động dịch 17 thứ tiếng\n\n"
                f"👉 Link kiểm tra danh sách đồ miễn phí chính thức:\n{link}"
            )
            native_tg = (
                f"⚡ [Thông báo] K-Market - Đồ gia dụng và nội thất 0 đồng tại Hàn Quốc\n\n"
                f"🎁 Giá: 0 KRW (100% miễn phí)\n"
                f"✅ Mặt hàng: Tủ lạnh, máy giặt, lò vi sóng, giường, bàn ghế...\n"
                f"🌐 Tiện ích: Chat tự động dịch 17 ngôn ngữ\n\n"
                f"🔗 Xem ngay tại đây: {link}"
            )
        else:
            native_threads = (
                f"🔥 {card1_title}\n\n"
                f"KTRS Market 0 KRW free giveaway platform for foreigners living in Korea!\n"
                f"Save over 1,500,000 KRW on initial living costs. Get free appliances and furniture.\n"
                f"17-language real-time auto-translation chat for safe 1:1 meetings!\n\n"
                f"👉 Check free items: {link}\n\n{hashtags}"
            )
            native_insta = (
                f"🇰🇷 For all international students and workers in Korea!\n"
                f"\"{card1_title}\"\n\n"
                f"Get quality furniture and home appliances for 0 KRW through KTRS Market!\n"
                f"Save up to 1,500,000 KRW on living setup expenses 🛋️✨\n\n"
                f"✨ 3 Key Advantages of K-Market:\n"
                f"1️⃣ 100% 0 KRW free giveaways and affordable second-hand marketplace\n"
                f"2️⃣ No language barrier: Real-time 17-language auto-translation chat\n"
                f"3️⃣ Safe and verified 1:1 local direct exchange\n\n"
                f"🔍 Click Link in Bio now to claim today's free items!\n\n{hashtags}"
            )
            native_fb = (
                f"📢 [KTRS MARKET 0 KRW GIVEAWAYS] {theme_title}\n\n"
                f"The ultimate community platform for foreigners living in Korea!\n"
                f"Get clean, reliable appliances and furniture left by graduating students and returning workers for free.\n\n"
                f"📌 Key Highlights:\n"
                f"• Save over 1,500,000 KRW on room furnishing\n"
                f"• Washing machines, microwaves, refrigerators, desks 100% free\n"
                f"• Communicate effortlessly without Korean through 17-language auto-translation chat\n\n"
                f"👉 Official Free Items Link:\n{link}"
            )
            native_tg = (
                f"⚡ [Notice] K-Market - 0 KRW Free Appliances & Furniture in Korea\n\n"
                f"🎁 Price: 0 KRW (100% Free)\n"
                f"✅ Items: Fridge, washing machine, microwave, bed, desks and more\n"
                f"🌐 Service: 17-language auto-translation chat\n\n"
                f"🔗 Check now: {link}"
            )

        ko_threads = (
            f"🔥 {card1_title}\n\n"
            f"한국 거주 외국인을 위한 KTRS 마켓 0원 무료 나눔 커뮤니티!\n"
            f"가전/가구값 150만 원 아끼고 자취방 풀세팅 완료. 귀국 선배들이 남긴 A급 물품을 0원에 득템하세요.\n"
            f"한국어 몰라도 17개 언어 실시간 자동번역 채팅으로 1:1 안전 직거래!\n\n"
            f"👉 0원 매물 확인하기: {link}"
        )
        ko_insta = (
            f"🇰🇷 한국 거주 외국인 유학생 & 근로자를 위한 0원 무료 나눔 플랫폼 K-Market!\n"
            f"\"{card1_title}\"\n\n"
            f"귀국하는 선배들이 남기고 간 깨끗한 가전/가구를 100% 무료(0원)로 득템하세요!\n"
            f"원룸 자취방 세팅비 150만 원 절약 🛋️✨\n\n"
            f"✨ 케이마켓 3대 특장점:\n"
            f"1️⃣ 0원 무료 나눔 & 알뜰 중고거래 커뮤니티\n"
            f"2️⃣ 17개국어 실시간 자동번역 채팅으로 소통 걱정 끝!\n"
            f"3️⃣ 캠퍼스/원룸 1:1 직거래로 안전하고 신속한 나눔\n\n"
            f"지금 프로필 링크(Link in Bio)를 누르고 오늘의 0원 매물을 확인하세요! 🔍\n\n"
            f"{hashtags}"
        )
        ko_fb = (
            f"📢 [KTRS 마켓 0원 무료 나눔] {theme_title}\n\n"
            f"한국에서 생활하는 외국인 근로자 및 유학생 여러분 안녕하십니까.\n"
            f"귀국하거나 이사하는 분들이 남겨주신 양질의 가전, 가구, 생활용품을 0원에 나눔받으실 수 있습니다.\n\n"
            f"📌 핵심 안내 사항:\n"
            f"• 가구/가전 구매 비용 최대 150만 원 상당 절약\n"
            f"• 세탁기, 전자레인지, 밥솥, 침대, 책상 등 100% 무료 나눔 다수\n"
            f"• 17개국어 실시간 번역 채팅 지원으로 언어 장벽 없이 약속 완료\n\n"
            f"👉 공식 0원 나눔 확인 링크:\n{link}"
        )
        ko_tg = (
            f"⚡ [공지] K-Market - 한국 생활 0원 무료 나눔 물품 안내\n\n"
            f"🎁 가격: 0원 (100% 무료)\n"
            f"✅ 대상 물품: 냉장고, 세탁기, 전자레인지, 가구 등\n"
            f"🌐 지원 기능: 17개국어 실시간 자동번역 채팅\n\n"
            f"🔗 지금 확인하기: {link}"
        )

        doc = f"""================================================================================
📢 [K-Market 카드뉴스 공식 SNS 포스팅 패키지]
🌍 타깃 국가: {lang_name_ko} ({lang.upper()})
🎯 카드뉴스 주제: {theme_title}
🔗 공식 K-Market 링크: {link}
================================================================================
💡 [포스팅 안내]:
- 아래 채널별로 【1. 현지어 복사용 본문】을 복사하여 외국인 커뮤니티에 바로 업로드하십시오.
- 【2. 한국어 관리자 대조/해설본】을 통해 어떤 내용으로 홍보되는지 사전에 검토하실 수 있습니다.
================================================================================


1. 🧵 스레드 (Threads) 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_threads}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_threads}

--------------------------------------------------------------------------------


2. 📸 인스타그램 (Instagram) 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_insta}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_insta}

--------------------------------------------------------------------------------


3. 📘 페이스북 (Facebook) 그룹/커뮤니티 포스팅 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_fb}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_fb}

--------------------------------------------------------------------------------


4. ✈️ 텔레그램 (Telegram) 단톡방 / 채널 팩
--------------------------------------------------------------------------------
📌 [1. {lang_name_native} 복사용 본문 (SNS 원문)]:
{native_tg}

🇰🇷 [2. 한국어 관리자 대조/해설본]:
{ko_tg}

================================================================================
"""
        return doc

