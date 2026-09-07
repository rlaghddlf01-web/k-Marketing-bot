import time
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any
from config import DATA_DIR, OUTPUTS_DIR, BASE_URLS
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager
from core.facebook_browser_driver import FacebookBrowserDriver

logger = logging.getLogger("KMarketFacebook")

class KMarketFacebookHunter:
    """
    🛒 [K-Market 전용 Facebook 대형 그룹 스텔스 침투기]
    - 재한 베트남/러시아/필리핀 등 100만 명 규모 페이스북 외국인 그룹 침투
    - 1단계: 본문에는 270개 실물 매물 기반 0원 나눔 꿀팁 & 카드뉴스만 게시 (관리자 100% 승인)
    - 2단계: '첫 번째 댓글(First-Comment)'에 K-Market 17개국 0원 나눔 링크 자동 부착 (알고리즘 회피)
    - 3단계: '승인 대기(Pending)' 그룹은 백그라운드 큐에 저장 후 승인 즉시 첫 댓글 등록
    - 4단계: Playwright 무인 브라우저(FacebookBrowserDriver)를 통한 실제 그룹 포스팅 및 첫 댓글 자동 입력 지원
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.browser_driver = FacebookBrowserDriver(service_id="kmarket")
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
        state_file = DATA_DIR / "fb_rotation_state_kmarket.json"
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
        """K-Market 0원 나눔 카드뉴스 + 스텔스 첫댓글 페이스북 그룹 순환 배포 (실제 무인 브라우저 모드 지원)"""
        posted_count = 0
        pending_count = 0
        target_groups = self._get_next_rotation_groups(count=limit)
        deployed_group_names = []

        # 실물 카드뉴스 5장 이미지 경로 확인
        desktop_dir = Path(r"C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓")
        cardnews_files = sorted(list(desktop_dir.glob("*.jpg")), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        if not cardnews_files:
            cardnews_files = sorted(list((OUTPUTS_DIR / "cardnews").glob("*.png")), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        cardnews_summary = f"(실물 5장 카드뉴스 {len(cardnews_files)}장 첨부)" if cardnews_files else ""

        for group in target_groups:
            lang = group.get("lang", "en")
            group_name = group.get("name", "")
            group_id = group.get("group_id", "")
            approval_type = group.get("approval_type", "instant")
            deployed_group_names.append(group_name.split("(")[0].strip())

            campaign = UTMTracker.generate_campaign_tag("kmarket", f"fb_{group_id}", lang)
            base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")
            landing_url = UTMTracker.build_landing_url(
                base_domain=base_domain,
                lang=lang,
                path="",
                source="facebook_group",
                medium="stealth_first_comment",
                campaign=campaign
            )

            # 1. 관리자 100% 승인용 순수 정보성 본문 생성 (링크 미포함)
            post_content = self._generate_clean_post(lang, group_name)

            # 2. 첫 번째 댓글용 0원 나눔 링크 텍스트 생성
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
                    logger.info(f"🚀 [FacebookBrowserDriver] '{group_name}' K-Market 실제 그룹 포스팅 & 첫 댓글 자동 완성 성공!")
                else:
                    logger.warning(f"⚠️ [FacebookBrowserDriver] '{group_name}' 브라우저 게시 대기/실패: {browser_res.get('message')}")
            else:
                if approval_type == "instant":
                    posted_count += 1
                    logger.info(f"🛒 [K-Market FB] '{group_name}' {cardnews_summary} 즉시 게시 & 첫 댓글 링크 패키징 완료 (대기 모드)")
                else:
                    pending_count += 1
                    logger.info(f"🛒 [K-Market FB] '{group_name}' {cardnews_summary} 본문 승인 요청 대기")

            # DB 기록
            self.db_mgr.record_history(
                content_type="fb_group_post",
                service_id="kmarket",
                target_lang=lang,
                title=f"FB: {group_name}",
                content_text=f"{post_content}\n\n[Attached Media]\n{cardnews_summary}\n\n[First-Comment]\n{first_comment}",
                target_url=landing_url,
                external_id=f"km_fb_{group_id}_{int(time.time())}"
            )

        groups_str = " + ".join(deployed_group_names)
        return {
            "success": True,
            "brand": "kmarket",
            "posted_count": posted_count,
            "pending_count": pending_count,
            "browser_mode": browser_mode,
            "message": f"🛒 K-Market 5장 카드뉴스 페이스북 [{groups_str}] {len(target_groups)}개 그룹 배포 파이프라인 처리 완료!"
        }

    def _generate_clean_post(self, lang: str, group_name: str) -> str:
        """관리자 무조건 승인용 순수 정보성 본문 (링크 없음)"""
        if lang == "vi":
            return (
                f"🎁 [Tổng hợp đồ nội thất & gia dụng 0 Won miễn phí tại Hàn Quốc]\n\n"
                f"Xin chào mọi người trong nhóm {group_name}!\n"
                f"Hiện tại đang vào mùa chuyển nhà/tốt nghiệp, rất nhiều bạn du học sinh để lại bàn học, đệm, tủ lạnh mini hoàn toàn 0 Won.\n"
                f"• Khu vực: Sinchon, Hongdae, Ansan, Suwon\n"
                f"• Tình trạng: Đã kiểm duyệt, còn dùng rất tốt\n\n"
                f"👉 Xem hướng dẫn nhận đồ miễn phí ở phần bình luận đầu tiên bên dưới nhé!"
            )
        elif lang == "uz":
            return (
                f"🎁 [Koreyada 0 Vonga Bepul Mebel va Maishiy Texnikalar]\n\n"
                f"Assalomu alaykum, {group_name} guruhi a'zolari!\n"
                f"O'qishni bitirayotgan yoki ko'chib o'tayotgan talabalar sifatli stol, krovat va mini-muzlatkichlarni 0 vonga tekinga bermoqda.\n"
                f"• Hududlar: Shinchon, Ansan, Suvon talabalar shaharchalari\n"
                f"• Holati: Tekshirilgan va a'lo darajada\n\n"
                f"👉 Bepul buyumlarni bron qilish havolasini birinchi izohda qoldirdim!"
            )
        elif lang == "km":
            return (
                f"🎁 [គ្រឿងសង្ហារឹម និងបរិក្ខារប្រើប្រាស់ក្នុងផ្ទះឥតគិតថ្លៃ 0 វ៉ុន នៅកូរ៉េ]\n\n"
                f"សួស្តីបងប្អូនសមាជិកក្រុម {group_name} ទាំងអស់គ្នា!\n"
                f"រដូវផ្លាស់ប្តូរទីលំនៅ មានការចែកជូនតុ រាន គ្រែ និងទូទឹកកកខ្នាតតូចដោយឥតគិតថ្លៃ (0 វ៉ុន)។\n"
                f"• តំបន់៖ ស៊ិនឆុន, អានសាន, ស៊ូវ៉ុន\n"
                f"• គុណភាព៖ នៅល្អស្អាត និងដំណើរការល្អទាំងអស់\n\n"
                f"👉 ពិនិត្យមើលតំណភ្ជាប់ទទួលយកអីវ៉ាន់ឥតគិតថ្លៃនៅមតិយោបល់ដំបូងខាងក្រោម!"
            )
        elif lang == "ne":
            return (
                f"🎁 [कोरियामा ० वन (0 KRW) मा नि:शुल्क फर्निचर र घरायसी सामानहरू]\n\n"
                f"नमस्ते {group_name} समूहका सम्पूर्ण साथीहरू!\n"
                f"कोठा सर्ने र अध्ययन पूरा गर्ने विद्यार्थीहरूले राम्रो अवस्थाका टेबल, ओछ्यान र फ्रिजहरू ० वनमा दिइरहेका छन्।\n"
                f"• क्षेत्रहरू: सिन्चोन, आन्सान, सुवोन\n"
                f"• अवस्था: प्रमाणित र प्रयोगयोग्य\n\n"
                f"👉 नि:शुल्क सामानहरू दाबी गर्न तलको पहिलो कमेन्ट हेर्नुहोस्!"
            )
        elif lang == "th":
            return (
                f"🎁 [รวมเฟอร์นิเจอร์และเครื่องใช้ไฟฟ้าฟรี 0 วอนในเกาหลีใต้]\n\n"
                f"สวัสดีทุกคนในกลุ่ม {group_name} ครับ/ค่ะ!\n"
                f"ช่วงนี้มีนักศึกษาและคนย้ายหอส่งต่อโต๊ะหนังสือ ฟูกนอน ตู้เย็นมินิสภาพดีฟรี 0 วอนเพียบเลยครับ\n"
                f"• พิกัด: ชินชน, อันซาน, ซูวอน\n"
                f"• สภาพ: ตรวจสอบแล้ว ใช้งานได้ดีเยี่ยม\n\n"
                f"👉 ดูลิงก์เลือกรับของฟรีได้ที่ความคิดเห็นแรกด้านล่างเลยครับ/ค่ะ!"
            )
        elif lang == "id":
            return (
                f"🎁 [Perabotan & Elektronik Gratis 0 Won di Korea Selatan]\n\n"
                f"Halo rekan-rekan di grup {group_name}!\n"
                f"Banyak mahasiswa dan pekerja yang pindahan memberikan meja belajar, kasur, dan kulkas mini secara GRATIS (0 Won).\n"
                f"• Wilayah: Sinchon, Ansan, Suwon\n"
                f"• Kondisi: Terverifikasi dan masih sangat bagus\n\n"
                f"👉 Cek link pengambilan barang gratis di komentar pertama di bawah ini!"
            )
        elif lang == "mn":
            return (
                f"🎁 [Солонгос дахь 0 воны үнэгүй тавилга болон гэр ахуйн бараа]\n\n"
                f"{group_name} группийн найзууддаа энэ өдрийн мэнд хүргэе!\n"
                f"Сургууль төгсөгчид болон нүүж буй оюутнууд бичгийн ширээ, ор, мини хөргөгчөө 0 воноор үнэгүй өгч байна.\n"
                f"• Байршил: Шинчон, Ансан, Сүвон оюутны хотхонууд\n"
                f"• Байдал: Шалгагдсан, ашиглахад маш сайн\n\n"
                f"👉 Үнэгүй бараа авах линкийг эхний сэтгэгдлээс шалгана уу!"
            )
        elif lang == "my":
            return (
                f"🎁 [ကိုရီးယားရှိ ၀ ဝမ် (0 KRW) အခမဲ့ ပရိဘောဂနှင့် အိမ်သုံးပစ္စည်းများ]\n\n"
                f"{group_name} မှ မိတ်ဆွေများအားလုံး မင်္ဂလာပါ!\n"
                f"အဆောင်ပြောင်းသူများနှင့် ကျောင်းပြီးသူများထံမှ စာကြည့်စားပွဲ၊ မွေ့ရာ၊ ရေခဲသေတ္တာအသေးများကို ၀ ဝမ်ဖြင့် အခမဲ့လက်ဆင့်ကမ်းပေးနေပါသည်။\n"
                f"• နေရာများ - ဆင်ချွန်း၊ အန်ဆန်၊ ဆူဝမ်\n"
                f"• အခြေအနေ - စစ်ဆေးပြီး အသုံးပြုရန် အလွန်ကောင်းမွန်\n\n"
                f"👉 အခမဲ့ပစ္စည်းများရယူရန် အောက်ပါ ပထမဆုံး comment ကို ကြည့်ရှုပါ!"
            )
        elif lang == "ru":
            return (
                f"🎁 [Бесплатная мебель и техника 0 вон в Корее]\n\n"
                f"Привет всем участникам {group_name}!\n"
                f"В период переездов отдают отличные столы, кровати и холодильники совершенно бесплатно (0 вон).\n"
                f"• Районы: Ансан, Сувон, Сеул\n\n"
                f"👉 Ссылку для бесплатного бронирования оставил в первом комментарии!"
            )
        else:
            return (
                f"🎁 [Verified 0 KRW Free Furniture & Moving Sales in Korea]\n\n"
                f"Hello everyone in {group_name}!\n"
                f"Graduating students are leaving quality desks, beds, and mini-fridges for 0 KRW.\n"
                f"• Locations: Sinchon, Ansan, Suwon campuses\n\n"
                f"👉 Check the first comment below to grab free items with 17-language translation chat!"
            )

    def _generate_first_comment(self, lang: str, url: str) -> str:
        """첫 번째 댓글용 링크 텍스트"""
        if lang == "vi":
            return f"👉 Bấm vào đây để xem danh sách đồ 0 Won & nhắn tin dịch tự động: {url}"
        elif lang == "uz":
            return f"👉 0 Vonga bepul narsalarni ko'rish va o'zbekcha tarjima chatida yozish: {url}"
        elif lang == "km":
            return f"👉 ចុចទីនេះដើម្បីមើលបញ្ជីអីវ៉ាន់ 0 វ៉ុន និងជជែកជាមួយប្រព័ន្ធបកប្រែស្វ័យប្រវត្តិ៖ {url}"
        elif lang == "ne":
            return f"👉 ० वनका नि:शुल्क सामानहरू हेर्न र नेपाली भाषा अनुवाद च्याट प्रयोग गर्न यहाँ थिच्नुहोस्: {url}"
        elif lang == "th":
            return f"👉 กดที่นี่เพื่อดูรายการของฟรี 0 วอนพร้อมระบบแชทแปลภาษาไทยอัตโนมัติ: {url}"
        elif lang == "id":
            return f"👉 Klaim barang gratis 0 Won & gunakan chat terjemahan otomatis di sini: {url}"
        elif lang == "mn":
            return f"👉 0 воны үнэгүй бараануудыг үзэх болон монгол чатаар харилцах: {url}"
        elif lang == "my":
            return f"👉 ၀ ဝမ် အခမဲ့ပစ္စည်းများကို ကြည့်ရှုရန်နှင့် မြန်မာဘာသာပြန်ချက်ဖြင့် စကားပြောဆိုရန် ဤနေရာကိုနှိပ်ပါ: {url}"
        elif lang == "ru":
            return f"👉 Забирайте бесплатные вещи здесь (чат с переводом на русский): {url}"
        else:
            return f"👉 Claim free 0 KRW items directly here (17-language instant chat enabled): {url}"
