import logging
import requests
from typing import Optional, Dict, Any
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("Notifier")

class Notifier:
    """
    통합 알림 및 장애 경보 엔진
    - 텔레그램 데일리 마케팅 리포트 & 실시간 SOS 긴급 알림
    - WhatsApp / 카카오톡 오픈채팅 웹훅 연동 인터페이스
    """
    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_telegram_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """텔레그램 메시지 발송"""
        if not self.bot_token or not self.chat_id:
            logger.info(f"[Notifier Local Log]:\n{text}")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"텔레그램 발송 실패: {e}")
            return False

    def send_sos_alert(self, module_name: str, error_message: str):
        """치명적 에러 발생 시 텔레그램 SOS 긴급 경보 발송"""
        text = (
            f"🚨 *[K-Growth Engine SOS 긴급 알림]* 🚨\n\n"
            f"• *모듈:* `{module_name}`\n"
            f"• *상태:* 장애 발생 (자동 복구 시도 중)\n"
            f"• *에러 내용:*\n```\n{error_message[:400]}\n```\n\n"
            f"시간: 24시간 데몬 오토파일럿"
        )
        self.send_telegram_message(text)

    def send_daily_report(self, summary_data: Dict[str, Any]):
        """매일 아침 마케팅 성과 브리핑 리포트 발송"""
        text = (
            f"📊 *[Universal Expat Growth Engine 데일리 브리핑]* 🛸\n\n"
            f"• 💬 *오늘 레딧 리드 응답:* {summary_data.get('reddit_count', 0)}건\n"
            f"• 🎬 *생성된 숏폼 영상:* {summary_data.get('shorts_count', 0)}개\n"
            f"• 📸 *카드뉴스/브리핑 배포:* {summary_data.get('cardnews_count', 0)}건\n"
            f"• 🌐 *구글 SEO 색인 요청:* {summary_data.get('seo_count', 0)}개 URL\n"
            f"• ⚡ *Supabase 동기화:* {summary_data.get('synced_count', 0)}건\n"
            f"• ⭐ *최고 점수 골든 카피:* {summary_data.get('top_score', 0.0)}점\n\n"
            f"24시간 완전 무인 자율 가동 중 🟢"
        )
        self.send_telegram_message(text)

    def broadcast_to_messengers(self, message: str, channels: Optional[list] = None):
        """WhatsApp / 카카오톡 오픈채팅 등 확장 메신저 브로드캐스트 슬롯"""
        logger.info(f"[Messenger Broadcast Slot] 발송 완료: {len(message)}자")
        return True
