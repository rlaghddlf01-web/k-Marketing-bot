"""
TelegramAICommunityManager - 🤖 17개국어 24시간 실시간 AI 커뮤니티 매니저 (챗봇)
- [기능 1] 신규 유저 입장(new_chat_members) 즉시 17개국 모국어 환영 & 첫 대화 유도
- [기능 2] 방에 올라오는 외국인 질문(가구/세무/원룸) 실시간 감지 ➔ Gemini AI 1초 네이티브 답변
- [기능 3] 불법 도박/코인/스팸 링크 감지 시 즉시 메시지 자동 삭제
- [기능 4] 24시간 무인 백그라운드 데몬 가동 및 실시간 응답 통계 집계
"""

import os
import re
import time
import json
import logging
import threading
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from config import BASE_URLS, LANGUAGES

logger = logging.getLogger("TelegramAICommunityManager")

SPAM_PATTERNS = [
    r't\.me\/(?!kmarket|easytax)',  # 타사 텔레그램 링크
    r'https?:\/\/[^\s]+(casino|gambling|bet|crypto|token|airdrop|binance|porn)', # 카지노/코인/불법
    r'(카지노|바카라|토토|코인리딩|고수익알바|성인용품)'
]

# 🛋️ K-Market 전용 웰컴 템플릿 (가구/가전 0원 나눔 중심)
WELCOME_TEMPLATES_KMARKET = {
    "ko": "👋 안녕하세요 {name}님! K-Market 공식 외국인 생활 커뮤니티에 오신 것을 환영합니다!\n\n🛋️ 필요하신 가구/가전(침대, 책상, 냉장고 등)이 있으신가요? 편하게 말씀해 주시면 0원 나눔 매물을 바로 찾아드릴게요!",
    "en": "👋 Welcome {name} to the K-Market Official Expat Community!\n\n🛋️ Looking for free/used furniture (bed, desk, fridge) or home essentials? Feel free to ask anytime!",
    "vi": "👋 Chào mừng {name} đến với Cộng đồng K-Market tại Hàn Quốc!\n\n🛋️ Bạn đang tìm đồ nội thất (giường, bàn, tủ lạnh) hay đồ gia dụng 0đ? Hãy nhắn tin ngay nhé!",
    "uz": "👋 Xush kelibsiz {name}! K-Market Koreyadagi rasmiy hamjamiyatiga xush kelibsiz!\n\n🛋️ Sizga bepul mebel (karavot, stol, muzlatgich) kerakmi? Bemalol yozing, topib beramiz!",
    "ru": "👋 Добро пожаловать, {name}, в официальное сообщество K-Market в Корее!\n\n🛋️ Ищете бесплатную мебель/технику (кровать, стол, холодильник)? Задавайте любые вопросы!",
    "mn": "👋 Тавтай морилно уу {name}! K-Market Солонгос дахь албан ёсны группт тавтай морил!\n\n🛋️ Танд үнэгүй тавилга (ор, ширээ, хөргөгч) хэрэгтэй юу? Чөлөөтэй асуугаарай!",
    "tl": "👋 Maligayang pagdating {name} sa K-Market Korea Community!\n\n🛋️ Naghahanap ka ba ng libreng gamit o gamit sa bahay? Magtanong ka lang dito!",
    "th": "👋 ยินดีต้อนรับ {name} สู่ชุมชน K-Market เกาหลี!\n\n🛋️ กำลังหาเฟอร์นิเจอร์ฟรี/เครื่องใช้ไฟฟ้า (เตียง, ตู้เย็น)? สอบถามได้ตลอดเวลาเลยครับ!",
    "id": "👋 Selamat datang {name} di Komunitas Resmi K-Market Korea!\n\n🛋️ Butuh perabotan gratis/murah (kasur, meja, kulkas)? Silakan tanyakan di sini!"
}

# 💰 EasyTax 전용 웰컴 템플릿 (세무 환급/소득세 감면 중심)
WELCOME_TEMPLATES_EASYTAX = {
    "ko": "👋 안녕하세요 {name}님! EasyTax 대한민국 국세청 세무 환급 커뮤니티에 오신 것을 환영합니다!\n\n💰 중소기업 90% 소득세 감면(조특법 30조)이나 알바 3.3% 환급, 지난 5개년 누락 세금 환급이 궁금하시면 언제든 질문해 주세요!",
    "en": "👋 Welcome {name} to the EasyTax Official Korean Expat Tax Refund Community!\n\n💰 Questions about your 90% Income Tax Exemption (Article 30), Part-Time 3.3% Refund, or 5-Year Past Taxes? Feel free to ask anytime!",
    "vi": "👋 Chào mừng {name} đến với Cộng đồng Hoàn Thuế EasyTax Hàn Quốc!\n\n💰 Bạn có thắc mắc về giảm 90% thuế thu nhập (Điều 30), hoàn thuế part-time 3.3% hay truy thu 5 năm qua? Hãy hỏi ngay nhé!",
    "uz": "👋 Xush kelibsiz {name}! EasyTax Koreya soliq qaytarish rasmiy hamjamiyatiga xush kelibsiz!\n\n💰 90% daromad solig'i imtiyozi (30-modda) yoki talabalar soliq qaytarishi bo'yicha savollaringiz bormi? Bemalol so'rang!",
    "ru": "👋 Добро пожаловать, {name}, в официальное налоговое сообщество EasyTax в Корее!\n\n💰 Хотите вернуть налоги (скидка 90% по ст. 30, возврат за 5 лет)? Задавайте любые вопросы!",
    "mn": "👋 Тавтай морилно уу {name}! EasyTax Солонгосын татварын буцаан олголтын группт тавтай морил!\n\n💰 90% татварын хөнгөлөлт болон 5 жилийн татварын буцаан олголтын талаар асуух зүйл байна уу? Чөлөөтэй асуугаарай!",
    "tl": "👋 Maligayang pagdating {name} sa EasyTax Korea Tax Refund Community!\n\n💰 May tanong ka ba tungkol sa 90% Tax Exemption o Tax Refund? Magtanong ka lang dito!",
    "th": "👋 ยินดีต้อนรับ {name} สู่ชุมชนขอคืนภาษี EasyTax เกาหลี!\n\n💰 มีข้อสงสัยเกี่ยวกับการลดหย่อนภาษี 90% หรือขอคืนภาษีย้อนหลัง 5 ปี สอบถามได้เลยครับ!",
    "id": "👋 Selamat datang {name} di Komunitas Pajak EasyTax Korea!\n\n💰 Butuh info pengurangan pajak 90% atau pengembalian pajak 5 tahun terakhir? Tanyakan di sini!"
}


class TelegramAICommunityManager:
    """17개국어 24시간 실시간 AI 커뮤니티 매니저 (브랜드별 독립 인스턴스)"""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        brand: str = "kmarket"
    ):
        self.brand = brand.lower()

        # 브랜드별 토큰 및 채팅방 독립 바인딩
        if self.brand == "easytax":
            self.bot_token = bot_token or os.getenv("EASYTAX_TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
            self.chat_id = chat_id or os.getenv("EASYTAX_TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
        else:
            self.bot_token = bot_token or os.getenv("KMARKET_TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
            self.chat_id = chat_id or os.getenv("KMARKET_TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.last_update_id = 0
        self.total_ai_replies = 0
        self.total_welcomed = 0
        self.total_spam_deleted = 0

    def start_background_daemon(self):
        """24시간 실시간 감지 데몬 스레드 가동"""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_polling_loop, daemon=True)
        self._thread.start()
        logger.info(f"🤖 [TelegramAIManager] 24시간 17개국어 실시간 AI 매니저 가동 완료! (Brand: {self.brand})")

    def stop_background_daemon(self):
        """데몬 스레드 정지"""
        self.is_running = False
        logger.info("⏹️ [TelegramAIManager] AI 커뮤니티 매니저가 정지되었습니다.")

    def _run_polling_loop(self):
        """텔레그램 롱폴링 감지 루프"""
        while self.is_running:
            try:
                updates = self._get_updates()
                for upd in updates:
                    self._process_single_update(upd)
            except Exception as e:
                logger.error(f"❌ [TelegramAIManager] 롱폴링 에러: {e}")
            time.sleep(1.5)

    def _get_updates(self) -> List[Dict[str, Any]]:
        """텔레그램 Bot API getUpdates 호출"""
        if not self.bot_token:
            return []

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates?offset={self.last_update_id + 1}&timeout=5"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UniversalGrowthBot/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("ok"):
                    res_list = data.get("result", [])
                    if res_list:
                        self.last_update_id = res_list[-1]["update_id"]
                    return res_list
        except Exception:
            pass
        return []

    def _process_single_update(self, update: Dict[str, Any]):
        """단일 메시지/이벤트 분석 및 1초 대응"""
        msg = update.get("message") or update.get("channel_post")
        if not msg:
            return

        chat = msg.get("chat", {})
        chat_id = str(chat.get("id"))
        msg_id = msg.get("message_id")
        from_user = msg.get("from", {})
        first_name = from_user.get("first_name", "Friend")
        user_lang = from_user.get("language_code", "en")[:2]

        # 1. 🌟 신규 유저 입장(new_chat_members) 감지 ➔ 모국어 웰컴 인사
        if "new_chat_members" in msg:
            for new_m in msg["new_chat_members"]:
                if not new_m.get("is_bot"):
                    m_name = new_m.get("first_name", "Friend")
                    self._send_welcome_message(chat_id, m_name, user_lang)
            return

        text = msg.get("text", "")
        if not text:
            return

        # 2. 🚨 스팸 / 불법 광고 감지 ➔ 즉시 삭제
        if self._is_spam(text):
            self._delete_message(chat_id, msg_id)
            self.total_spam_deleted += 1
            logger.info(f"🛡️ [스팸 차단] 불법 홍보 메시지 자동 즉시 삭제 완료 (Chat: {chat_id})")
            return

        # 3. 💬 유저의 가구 / 세무 / 생활 질문 실시간 감지 ➔ Gemini 1초 답변
        if self._is_user_query(text):
            reply_text = self._generate_ai_reply(text, user_lang, first_name)
            if reply_text:
                self._send_reply_message(chat_id, msg_id, reply_text)
                self.total_ai_replies += 1
                logger.info(f"✨ [AI 답변 완료] {first_name}님의 질문에 1초 네이티브 답변 발송!")

    def _is_spam(self, text: str) -> bool:
        for p in SPAM_PATTERNS:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def _is_user_query(self, text: str) -> bool:
        keywords = [
            "가구", "침대", "책상", "냉장고", "0원", "나눔", "세금", "환급", "연말정산", "감면",
            "bed", "fridge", "desk", "free", "tax", "refund", "article 30", "e-9", "d-2",
            "giuong", "tu lanh", "thue", "hoan thue", "mebel", "soliq", "viza", "nalog"
        ]
        text_lower = text.lower()
        return any(k in text_lower for k in keywords) or "?" in text or "어떻게" in text or "how" in text_lower

    def _send_welcome_message(self, chat_id: str, name: str, lang_code: str):
        if self.brand == "easytax":
            template = WELCOME_TEMPLATES_EASYTAX.get(lang_code, WELCOME_TEMPLATES_EASYTAX["en"])
        else:
            template = WELCOME_TEMPLATES_KMARKET.get(lang_code, WELCOME_TEMPLATES_KMARKET["en"])
            
        welcome_text = template.format(name=name)
        self._send_raw_message(chat_id, welcome_text)
        self.total_welcomed += 1

    def _generate_ai_reply(self, user_query: str, lang_code: str, user_name: str) -> str:
        """Gemini AI로 1초 네이티브 친절 답변 생성 (브랜드별 독립)"""
        if self.brand == "easytax":
            et_url = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
            prompt = f"""You are the official AI tax assistant for EasyTax (Certified Korean Expat Tax Refund & 90% Income Tax Exemption Service).
A foreign member ({user_name}) asked the following question in our EasyTax Telegram community:

User Query: "{user_query}"
User Preferred Language: {lang_code}

STRICT GUIDELINES:
1. Answer warmly and concisely in 2~3 sentences in the user's language ({lang_code}).
2. Explain Korean tax benefits (Article 30 90% income tax reduction for E-9/H-2/E-7, part-time 3.3% refund for D-2 students, 5-year past refund).
3. Guide them to EasyTax ({et_url}) for a 3-minute free tax simulation with zero upfront fees.
4. Output ONLY the clean response message text."""
        else:
            km_url = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")
            prompt = f"""You are the friendly official community manager for K-Market (0-won free secondhand furniture & expat living marketplace).
A foreign member ({user_name}) asked the following question in our K-Market Telegram community:

User Query: "{user_query}"
User Preferred Language: {lang_code}

STRICT GUIDELINES:
1. Answer warmly and concisely in 2~3 sentences in the user's language ({lang_code}).
2. Guide them on how to claim 0-won free furniture (beds, desks, fridges) and safe secondhand items with auto-translation chat.
3. Guide them to K-Market ({km_url}).
4. Output ONLY the clean response message text."""

        try:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY_KMARKET") or os.getenv("GEMINI_FREE_API_KEY_KMARKET") or os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            return res.text.strip()
        except Exception as e:
            logger.warning(f"⚠️ AI 답변 생성 오류: {e}")
            return f"Hello {user_name}! For 0-won furniture & electronics, check {km_url}. For Korean tax refunds (up to 90% reduction), check {et_url}! 😊"

    def _send_reply_message(self, chat_id: str, reply_to_msg_id: int, text: str):
        if not self.bot_token:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_to_message_id": reply_to_msg_id
        }
        self._post_json(url, payload)

    def _send_raw_message(self, chat_id: str, text: str):
        if not self.bot_token:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self._post_json(url, {"chat_id": chat_id, "text": text})

    def _delete_message(self, chat_id: str, message_id: int):
        if not self.bot_token:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/deleteMessage"
        self._post_json(url, {"chat_id": chat_id, "message_id": message_id})

    def _post_json(self, url: str, data: Dict[str, Any]):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "UniversalGrowthBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
        except Exception as e:
            logger.warning(f"⚠️ Telegram API 호출 오류: {e}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "total_ai_replies": self.total_ai_replies,
            "total_welcomed": self.total_welcomed,
            "total_spam_deleted": self.total_spam_deleted
        }
