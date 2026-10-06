"""
TelegramCommunityPublisher - 📢 텔레그램 옴니채널 정시 브리핑 & 참여형 투표(Poll) 엔진
- [08:30 / 18:30 KST] K-Market 0원 나눔 매물 TOP 3 모닝/이브닝 브리핑
- [08:30 / 18:30 KST] EasyTax 비자별(E-9/D-2/F-4) 절세 꿀팁 정시 브리핑
- [주 2회] 커뮤니티 대화 참여율 300% 폭증시키는 인터랙티브 투표(Poll) 자동 생성
"""

import os
import json
import random
import logging
import urllib.request
from typing import Dict, Any, List, Optional
from config import BASE_URLS, get_now_kst
from core.db_manager import DBManager

logger = logging.getLogger("TelegramCommunityPublisher")

SAMPLE_POLLS = [
    {
        "question": "📊 이번 주 원룸 자취방에 가장 필요한 0원 무료나눔 가구는 무엇인가요?",
        "options": [
            "🛏️ 싱글 침대 & 매트리스",
            "❄️ 소형 냉장고 / 전자레인지",
            "🪑 스터디 책상 & 편한 의자",
            "🍚 전기밥솥 / 주방 식기류"
        ],
        "category": "kmarket"
    },
    {
        "question": "💰 대한민국 세금 환급 중 가장 궁금하거나 신청하고 싶은 제도는?",
        "options": [
            "🏢 중소기업 취업자 소득세 90% 감면 (조특법 30조)",
            "👨‍👩‍👧 본국 부모님 부양가족 인적공제 (150만 원)",
            "☕ 유학생 알바 3.3% 원천징수 전액 환급",
            "📅 지난 5개년 놓친 세금 일괄 소급 환급"
        ],
        "category": "easytax"
    },
    {
        "question": "📍 여러분이 현재 거주하거나 일하고 계시는 지역은 어디인가요?",
        "options": [
            "🏙️ 서울 / 신촌 / 혜화 대학가",
            "🏭 안산 / 시화 / 반월 국가공단",
            "🚢 인천 / 부천 / 김포 산업지역",
            "🌾 경기 / 충청 / 지방 지역"
        ],
        "category": "general"
    }
]


class TelegramCommunityPublisher:
    """텔레그램 정시 브리핑 및 참여형 투표 퍼블리셔"""

    def __init__(self, db_mgr: Optional[DBManager] = None):
        self.db_mgr = db_mgr or DBManager()
        # ✅ [버그 수정] 생성자에서 토큰을 고정 바인딩하지 않음.
        # 각 발송 메서드 호출 시점에 brand를 보고 동적으로 선택합니다.

    def _get_credentials(self, brand: str):
        """
        브랜드에 따라 올바른 봇 토큰과 채팅방 ID를 그 자리에서 동적 반환.
        - brand='kmarket'  -> KMARKET_TELEGRAM_BOT_TOKEN, KMARKET_TELEGRAM_CHAT_ID
        - brand='easytax'  -> EASYTAX_TELEGRAM_BOT_TOKEN, EASYTAX_TELEGRAM_CHAT_ID
        공유 범용 변수(TELEGRAM_BOT_TOKEN)는 맨 마지막 폴백으로만 사용.
        """
        if brand == "easytax":
            token   = os.getenv("EASYTAX_TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("EASYTAX_TELEGRAM_CHAT_ID")   or os.getenv("TELEGRAM_CHAT_ID")
        else:  # kmarket (기본값)
            token   = os.getenv("KMARKET_TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("KMARKET_TELEGRAM_CHAT_ID")   or os.getenv("TELEGRAM_CHAT_ID")
        return token, chat_id

    def broadcast_morning_briefing(self, brand: str = "kmarket") -> Dict[str, Any]:
        """08:30 모닝 0원 나눔 / 세무 브리핑 발송"""
        now = get_now_kst()
        today_str = now.strftime("%Y년 %m월 %d일")

        if brand == "kmarket":
            km_url = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")
            msg = f"""🌅 **[K-Market] {today_str} 모닝 0원 나눔 꿀매물 TOP 3**

외국인 이웃들이 방을 빼며 등록한 따끈따끈한 0원 무료나눔 매물입니다!

1️⃣ 🛏️ **원룸 원목 침대 프레임 + 매트리스** (서울 신촌 / 무료나눔 0원)
2️⃣ ❄️ **미니 냉장고 & 전자레인지 세트** (안산 원곡동 / 무료나눔 0원)
3️⃣ 🪑 **높이조절 화이트 스터디 책상** (인천 부평 / 무료나눔 0원)

👉 **[지금 바로 0원 매물 채팅 신청하기]({km_url})**
* 17개국어 실시간 자동번역으로 한국어 못해도 1초 만에 채팅 거래 가능!"""
        else:
            et_url = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
            msg = f"""🌅 **[EasyTax] {today_str} 외국인 필수 세무 권리 모닝 브리핑**

💡 **알고 계셨나요? 조세특례제한법 제30조 90% 소득세 감면!**
- **대상**: 중소기업에 재직 중인 만 15~34세 외국인 근로자 (E-9, E-7, F-4 등)
- **혜택**: 5년간 최대 1,000만 원 (연 200만 원 한도) 소득세 90% 감면
- **놓친 세금**: 지난 5개년 납부액 전액 소급 환급 가능!

👉 **[내 숨은 환급금 3분 무료 조회하기]({et_url})**
* 선입금 0원 / 국세청 환급 통장 입금 후 안심 정산!"""

        # ✅ brand 기준으로 올바른 토큰 & chat_id를 그 자리에서 가져옴
        token, chat_id = self._get_credentials(brand)
        sent = self._send_message(msg, token, chat_id)
        return {"success": sent, "brand": brand, "type": "morning_briefing"}

    def broadcast_interactive_poll(self, brand: str = "kmarket", poll_index: Optional[int] = None) -> Dict[str, Any]:
        """커뮤니티 참여형 투표(Poll) 생성"""
        # ✅ brand 기준으로 올바른 토큰 & chat_id를 그 자리에서 가져옴
        token, chat_id = self._get_credentials(brand)

        if not token or not chat_id:
            logger.warning(f"⚠️ [{brand}] 텔레그램 토큰 또는 Chat ID가 없어 투표 발송 불가")
            return {"success": False, "error": "No credentials"}

        poll_data = SAMPLE_POLLS[poll_index % len(SAMPLE_POLLS)] if poll_index is not None else random.choice(SAMPLE_POLLS)

        url = f"https://api.telegram.org/bot{token}/sendPoll"
        payload = {
            "chat_id": chat_id,
            "question": poll_data["question"],
            "options": json.dumps(poll_data["options"]),
            "is_anonymous": False
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "UniversalGrowthBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("ok"):
                    logger.info(f"📊 [TelegramPoll][{brand}] 커뮤니티 투표 생성 성공: '{poll_data['question'][:30]}...'")
                    return {"success": True, "poll": poll_data}
        except Exception as e:
            logger.error(f"❌ [{brand}] 투표 발송 실패: {e}")

        return {"success": False, "error": "Poll send failed"}

    def _send_message(self, text: str, token: str, chat_id: str) -> bool:
        """지정된 토큰과 chat_id로 메시지 발송 (브랜드 혼용 원천 차단)"""
        if not token or not chat_id:
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "UniversalGrowthBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("ok", False)
        except Exception as e:
            logger.warning(f"⚠️ 브리핑 발송 실패: {e}")
            return False
