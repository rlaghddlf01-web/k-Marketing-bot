import time
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any
from config import DATA_DIR, OUTPUTS_DIR, BASE_URLS
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager
from core.facebook_browser_driver import FacebookBrowserDriver

logger = logging.getLogger("EasyTaxFacebook")

class EasyTaxFacebookHunter:
    """
    💰 [EasyTax (KTRS) 전용 Facebook 대형 그룹 스텔스 침투기]
    - 재한 베트남/러시아/필리핀 등 100만 명 규모 페이스북 외국인 그룹 침투
    - 1단계: 본문에는 조세특례제한법 제30조 90% 감면 & 3.3% 환급 법률 팩트만 게시 (관리자 100% 승인)
    - 2단계: '첫 번째 댓글(First-Comment)'에 EasyTax 선입금 0원 3분 무료 모의계산 링크 부착 (알고리즘 회피)
    - 3단계: '승인 대기(Pending)' 그룹은 백그라운드 큐에 저장 후 승인 즉시 첫 댓글 등록
    - 4단계: Playwright 무인 브라우저(FacebookBrowserDriver)를 통한 실제 그룹 포스팅 및 첫 댓글 자동 입력 지원
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        self.browser_driver = FacebookBrowserDriver(service_id="easytax")
        self.groups = self._load_groups()

    def _load_groups(self) -> List[Dict[str, Any]]:
        path = DATA_DIR / "facebook_groups.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _get_next_rotation_groups(self, count: int = 2) -> List[Dict[str, Any]]:
        """순환 큐에서 다음 순번의 페이스북 그룹들 추출 (중복 방지 로테이션)"""
        if not self.groups:
            return []
        state_file = DATA_DIR / "fb_rotation_state_easytax.json"
        curr_idx = 0
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    curr_idx = json.load(f).get("index", 0)
            except Exception:
                curr_idx = 0

        selected = []
        for i in range(count):
            idx = (curr_idx + i) % len(self.groups)
            selected.append(self.groups[idx])

        # 다음 인덱스 저장
        next_idx = (curr_idx + count) % len(self.groups)
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump({"index": next_idx}, f)
        except Exception:
            pass

        return selected

    def deploy_to_groups(self, limit: int = 2, browser_mode: bool = False, headless: bool = True) -> Dict[str, Any]:
        """EasyTax 합법 세무 가이드 카드뉴스 + 첫 댓글 링크 페이스북 순환 배포 (실제 무인 브라우저 모드 지원)"""
        posted_count = 0
        pending_count = 0
        target_groups = self._get_next_rotation_groups(count=limit)
        deployed_group_names = []

        # 실물 카드뉴스 5장 이미지 경로 확인
        desktop_dir = Path(r"C:\Users\zkfnt\Desktop\카드뉴스_산출물\이지텍스")
        cardnews_files = sorted(list(desktop_dir.glob("*.jpg")), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        if not cardnews_files:
            cardnews_files = sorted(list((OUTPUTS_DIR / "cardnews").glob("*.png")), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        cardnews_summary = f"(공인 세무 5장 카드뉴스 {len(cardnews_files)}장 첨부)" if cardnews_files else ""

        for group in target_groups:
            lang = group.get("lang", "en")
            group_name = group.get("name", "")
            group_id = group.get("group_id", "")
            approval_type = group.get("approval_type", "instant")
            deployed_group_names.append(group_name.split("(")[0].strip())

            campaign = UTMTracker.generate_campaign_tag("easytax", f"fb_{group_id}", lang)
            base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
            landing_url = UTMTracker.build_service_landing_url(
                service_id="easytax",
                base_domain=base_domain,
                lang=lang,
                path="",
                source="facebook_group",
                medium="stealth_first_comment",
                campaign=campaign
            )

            # 1. 관리자 100% 승인용 순수 정보성 본문 생성 (링크 미포함)
            post_content = self._generate_clean_post(lang, group_name)

            # 2. 첫 번째 댓글용 0원 무료 모의계산 링크 텍스트 생성
            first_comment = self._generate_first_comment(lang, landing_url)

            # 3. 배포 처리 (실제 브라우저 모드 or 시뮬레이션 모드)
            browser_res = None
            if browser_mode:
                group_url = f"https://www.facebook.com/groups/{group_id}"
                img_paths_str = [str(f) for f in cardnews_files]
                browser_res = self.browser_driver.post_to_group(
                    group_url=group_url,
                    post_content=post_content,
                    image_paths=img_paths_str,
                    first_comment=first_comment,
                    headless=headless
                )
                if browser_res.get("success"):
                    posted_count += 1
                    logger.info(f"🚀 [FacebookBrowserDriver] '{group_name}' 실제 그룹 포스팅 & 첫 댓글 자동 완성 성공!")
                else:
                    logger.warning(f"⚠️ [FacebookBrowserDriver] '{group_name}' 브라우저 게시 대기/실패: {browser_res.get('message')}")
            else:
                if approval_type == "instant":
                    posted_count += 1
                    logger.info(f"💰 [EasyTax FB] '{group_name}' {cardnews_summary} 즉시 게시 & 첫 댓글 링크 패키징 완료 (대기 모드)")
                else:
                    pending_count += 1
                    logger.info(f"💰 [EasyTax FB] '{group_name}' {cardnews_summary} 본문 승인 요청 대기")

            # DB 기록
            self.db_mgr.record_history(
                content_type="fb_group_post",
                service_id="easytax",
                target_lang=lang,
                title=f"FB: {group_name}",
                content_text=f"{post_content}\n\n[Attached Media]\n{cardnews_summary}\n\n[First-Comment]\n{first_comment}",
                target_url=landing_url,
                external_id=f"tax_fb_{group_id}_{int(time.time())}"
            )

        groups_str = " + ".join(deployed_group_names)
        return {
            "success": True,
            "brand": "easytax",
            "posted_count": posted_count,
            "pending_count": pending_count,
            "browser_mode": browser_mode,
            "message": f"👥 EasyTax 5장 카드뉴스 페이스북 [{groups_str}] {len(target_groups)}개 그룹 배포 파이프라인 처리 완료!"
        }

    def _generate_clean_post(self, lang: str, group_name: str) -> str:
        """관리자 무조건 승인용 순수 정보성 본문 (링크 없음)"""
        if lang == "vi":
            return (
                f"🏛️ [Quyền lợi thuế hợp pháp cho lao động E-9/H-2 & du học sinh D-2 tại Hàn Quốc]\n\n"
                f"Xin chào anh chị em nhóm {group_name}!\n"
                f"Theo Luật Miễn giảm Thuế Đặc biệt (Điều 30) của Cục Thuế Quốc gia Hàn Quốc:\n"
                f"• Người lao động E-9/H-2 làm tại doanh nghiệp vừa và nhỏ được giảm tới 90% thuế thu nhập.\n"
                f"• Du học sinh D-2 làm thêm bị trừ 3.3% được hoàn lại 100% toàn bộ.\n"
                f"• Có thể yêu cầu hoàn thuế truy thu trong vòng 5 năm qua (2020~2025).\n"
                f"🛡️ Hoàn toàn miễn phí tính thử • Không thu phí trước.\n\n"
                f"👉 Xem công cụ tính thử tiền hoàn thuế miễn phí ở bình luận đầu tiên bên dưới nhé!"
            )
        elif lang == "uz":
            return (
                f"🏛️ [Koreyadagi E-9/H-2 ishchilari va talabalar uchun qonuniy soliq imtiyozlari]\n\n"
                f"Assalomu alaykum, {group_name} guruhi a'zolari!\n"
                f"Koreya Milliy Soliq Xizmati Maxsus Soliq Imtiyozlari Qonuni (30-modda)ga binoan:\n"
                f"• Ishlab chiqarish sohasidagi E-9 ishchilari daromad solig'idan 90% gacha chegirma oladi.\n"
                f"• So'nggi 5 yil (2020~2025) uchun qaytarib olinmagan soliqlarni to'liq qaytarish mumkin.\n"
                f"🛡️ 100% bepul hisob-kitob • Hech qanday oldindan to'lov yo'q.\n\n"
                f"👉 Bepul hisoblash vositasi havolasi birinchi izohda qoldirildi!"
            )
        elif lang == "km":
            return (
                f"🏛️ [សិទ្ធិទទួលបានការបង្វិលសងពន្ធស្របច្បាប់សម្រាប់ពលករ E-9 និងនិស្សិតនៅកូរ៉េ]\n\n"
                f"សួស្តីបងប្អូនសមាជិកក្រុម {group_name} ទាំងអស់គ្នា!\n"
                f"យោងតាមច្បាប់កាត់បន្ថយពន្ធពិសេស (មាត្រា ៣០) របស់អគ្គនាយកដ្ឋានពន្ធដារកូរ៉េ៖\n"
                f"• ពលករ E-9 ក្នុងវិស័យផលិតកម្ម/កសិកម្ម ទទួលបានការបញ្ចុះពន្ធលើប្រាក់ចំណូលរហូតដល់ 90%។\n"
                f"• អាចទាមទារប្រាក់បង្វិលសងពន្ធថយក្រោយរហូតដល់ ៥ ឆ្នាំ (២០២០~២០២៥)។\n"
                f"🛡️ ការគណនាសាកល្បងឥតគិតថ្លៃ ១០០% • គ្មានការគិតថ្លៃសេវាជាមុនឡើយ។\n\n"
                f"👉 សូមពិនិត្យមើលតំណភ្ជាប់គណនាប្រាក់បង្វិលសងពន្ធឥតគិតថ្លៃនៅមតិយោបល់ដំបូងខាងក្រោម!"
            )
        elif lang == "ne":
            return (
                f"🏛️ [कोरियामा ई-९ कामदार र विद्यार्थीहरूका लागि कानुनी कर फिर्ता अधिकार]\n\n"
                f"नमस्ते {group_name} समूहका सम्पूर्ण साथीहरू!\n"
                f"कोरियाको विशेष कर न्यूनीकरण ऐन (धारा ३०) अनुसार:\n"
                f"• निर्माण तथा उत्पादन क्षेत्रका E-9 कामदारहरूले ९०% सम्म आयकर छुट पाउँछन्।\n"
                f"• विगत ५ वर्ष (२०२०~२०२५) को कर फिर्ता (Refund) दाबी गर्न सकिन्छ।\n"
                f"🛡️ १००% नि:शुल्क अनुमान • कुनै अग्रिम शुल्क लाग्दैन।\n\n"
                f"👉 आफ्नो कर फिर्ता रकम नि:शुल्क जाँच गर्न पहिलो कमेन्ट हेर्नुहोस्!"
            )
        elif lang == "th":
            return (
                f"🏛️ [สิทธิขอคืนภาษีอย่างถูกต้องตามกฎหมายสำหรับแรงงาน E-9 และนักศึกษาในเกาหลี]\n\n"
                f"สวัสดีสมาชิกกลุ่ม {group_name} ทุกคนครับ/ค่ะ!\n"
                f"ตามพระราชบัญญัติลดหย่อนภาษีพิเศษ (มาตรา 30) ของกรมสรรพากรเกาหลีใต้:\n"
                f"• แรงงานวีซ่า E-9/H-2 มีสิทธิได้รับการลดหย่อนภาษีเงินได้สูงสุดถึง 90%\n"
                f"• สามารถยื่นขอคืนภาษีย้อนหลังได้สูงสุดถึง 5 ปี (2020~2025)\n"
                f"🛡️ คำนวณเบื้องต้นฟรี 100% • ไม่มีค่าบริการล่วงหน้า\n\n"
                f"👉 ตรวจสอบลิงก์คำนวณยอดเงินภาษีคืนฟรีได้ที่ความคิดเห็นแรกด้านล่างเลยครับ/ค่ะ!"
            )
        elif lang == "id":
            return (
                f"🏛️ [Hak Pengembalian Pajak Legal bagi Pekerja E-9 & Mahasiswa di Korea]\n\n"
                f"Halo rekan-rekan grup {group_name}!\n"
                f"Berdasarkan UU Pengurangan Pajak Khusus (Pasal 30) Badan Pajak Nasional Korea:\n"
                f"• Pekerja E-9 berhak mendapatkan pemotongan pajak penghasilan hingga 90%.\n"
                f"• Mahasiswa D-2 & pekerja paruh waktu dapat klaim pengembalian pajak 3.3%.\n"
                f"• Klaim pengembalian berlaku surut hingga 5 tahun ke belakang (2020~2025).\n"
                f"🛡️ Simulasi 100% Gratis • Tanpa biaya di muka.\n\n"
                f"👉 Cek komentar pertama di bawah untuk menghitung perkiraan uang kembali secara gratis!"
            )
        elif lang == "mn":
            return (
                f"🏛️ [Солонгос дахь E-9 ажилчид болон D-2 оюутнуудын татварын хууль ёсны эрх]\n\n"
                f"{group_name} группийн нийт гишүүдэд энэ өдрийн мэнд хүргэе!\n"
                f"БНСУ-ын Татварын тусгай хөнгөлөлтийн хууль (30-р зүйл)-ийн дагуу:\n"
                f"• Үйлдвэрлэлийн салбарын E-9 ажилчид орлогын албан татвараас 90% хүртэл хөнгөлөлт эдэлнэ.\n"
                f"• D-2 оюутнууд цагийн ажлын 3.3% татварыг 100% буцаан авах боломжтой.\n"
                f"• Сүүлийн 5 жилийн (2020~2025) татварыг нөхөн буцаан авах эрхтэй.\n"
                f"🛡️ 100% үнэ төлбөргүй тооцоолол • Урьдчилгаа төлбөргүй.\n\n"
                f"👉 Буцаан олголтын хэмжээгээ үнэгүй шалгах линкийг эхний сэтгэгдлээс харна уу!"
            )
        elif lang == "my":
            return (
                f"🏛️ [ကိုရီးယားရှိ E-9 လုပ်သားများနှင့် ကျောင်းသားများအတွက် တရားဝင် အခွန်ပြန်အမ်းငွေ ရပိုင်ခွင့်]\n\n"
                f"{group_name} အဖွဲ့ဝင်များအားလုံး မင်္ဂလာပါ!\n"
                f"ကိုရီးယား အမျိုးသားအခွန်ဦးစီးဌာန အထူးအခွန်လျှော့ပေါ့မှုဥပဒေ (ပုဒ်မ ၃၀) အရ -\n"
                f"• E-9 ကုန်ထုတ်လုပ်ငန်းလုပ်သားများသည် ဝင်ငွေခွန် ၉၀% အထိ လျှော့ပေါ့ခွင့်ရရှိသည်။\n"
                f"• လွန်ခဲ့သော ၅ နှစ် (၂၀၂၀~၂၀၂၅) အထိ နောက်ကြောင်းပြန် အခွန်ပြန်အမ်းငွေ တောင်းခံနိုင်သည်။\n"
                f"🛡️ ၁၀၀% အခမဲ့ တွက်ချက်စစ်ဆေးနိုင်သည် • ကြိုတင်အခကြေးငွေ လုံးဝမရှိပါ။\n\n"
                f"👉 ပြန်အမ်းငွေပမာဏကို အခမဲ့တွက်ချက်ရန် အောက်ပါ ပထမဆုံး comment ကို ကြည့်ပါ!"
            )
        elif lang == "ru":
            return (
                f"🏛️ [Законные налоговые льготы для иностранцев в Корее (E-9, H-2, D-2)]\n\n"
                f"Здравствуйте, участники группы {group_name}!\n"
                f"По закону о налоговых льготах (Статья 30):\n"
                f"• Работники виз E-9/H-2 имеют право на скидку до 90% по подоходному налогу.\n"
                f"• Студенты виз D-2 могут вернуть 100% налога 3.3% за подработку.\n"
                f"• Возврат возможен за последние 5 лет (2020~2025).\n"
                f"🛡️ 100% бесплатный предварительный расчет без предоплаты.\n\n"
                f"👉 Ссылка для бесплатного расчета возврата находится в первом комментарии!"
            )
        else:
            return (
                f"🏛️ [Legal Tax Refund Rights for Foreign Workers & Students in Korea]\n\n"
                f"Hello members of {group_name}!\n"
                f"Under Korean Restriction of Special Taxation Act (Article 30):\n"
                f"• E-9/H-2 workers are eligible for up to 90% income tax reduction.\n"
                f"• D-2 students can claim a 100% refund on 3.3% part-time withholding taxes.\n"
                f"• Valid for retroactive 5-year claims (2020~2025).\n"
                f"🛡️ 100% Free simulation • Zero upfront fees.\n\n"
                f"👉 Check the first comment below to estimate your exact refund amount for free!"
            )

    def _generate_first_comment(self, lang: str, url: str) -> str:
        """첫 번째 댓글용 링크 텍스트 (Anti-Ban 면책 포함)"""
        if lang == "vi":
            return f"👉 Bấm vào đây để tính thử số tiền hoàn thuế miễn phí trong 3 phút (Đại lý thuế công nhận): {url}"
        elif lang == "uz":
            return f"👉 Qaytariladigan soliq summasini 3 daqiqada bepul hisoblang (Soliq agentligi): {url}"
        elif lang == "km":
            return f"👉 ចុចទីនេះដើម្បីគណនាប្រាក់បង្វិលសងពន្ធរបស់អ្នកដោយឥតគិតថ្លៃក្នុងរយៈពេល 3 នាទី៖ {url}"
        elif lang == "ne":
            return f"👉 ३ मिनेटमा आफ्नो कर फिर्ता रकम नि:शुल्क गणना गर्नुहोस् (प्रमाणित कर सेवा): {url}"
        elif lang == "th":
            return f"👉 คลิกที่นี่เพื่อคำนวณยอดเงินภาษีคืนของคุณได้ฟรีใน 3 นาที (ตัวแทนภาษีรับรอง): {url}"
        elif lang == "id":
            return f"👉 Hitung pengembalian pajak Anda secara gratis dalam 3 menit (Agen Pajak Resmi): {url}"
        elif lang == "mn":
            return f"👉 Татварын буцаан олголтоо 3 минутад үнэгүй тооцоолж үзэх (Албан ёсны татварын систем): {url}"
        elif lang == "my":
            return f"👉 မိမိ၏ အခွန်ပြန်အမ်းငွေကို ၃ မိနစ်အတွင်း အခမဲ့ တွက်ချက်ရန် ဤနေရာကိုနှိပ်ပါ: {url}"
        elif lang == "ru":
            return f"👉 Рассчитайте сумму возврата налога бесплатно за 3 минуты (Сертифицированный сервис): {url}"
        else:
            return f"👉 Estimate your refund for free in 3 minutes (Processed by certified National Tax agents): {url}"
