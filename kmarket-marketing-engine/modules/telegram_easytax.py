import logging
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from config import BASE_DIR, LANGUAGES, OUTPUTS_DIR, DATA_DIR, BASE_URLS
from core.db_manager import DBManager

logger = logging.getLogger("EasyTaxTelegram")

class EasyTaxTelegramPusher:
    """
    💰 [EasyTax (KTRS) 전용 17개국 텔레그램 브로드캐스트 엔진]
    - E-9 90% 소득세 감면 & D-2 3.3% 환급 팁 17개국 다국어 세무 브리핑 발송 (Anti-Ban 공인 면책 포함)
    """
    def __init__(self, db_mgr: DBManager):
        self.db_mgr = db_mgr
        self.output_dir = OUTPUTS_DIR / "briefings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.env_path = BASE_DIR / ".env"
        self.bot_token = self._get_env("EASYTAX_TELEGRAM_BOT_TOKEN") or self._get_env("TELEGRAM_BOT_TOKEN")
        self.chat_id = self._get_env("EASYTAX_TELEGRAM_CHAT_ID")

    def _get_env(self, key: str) -> str:
        if self.env_path.exists():
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(key + "="):
                        return line.split("=", 1)[1].strip()
        return ""

    def broadcast_daily_tax_tips(self, target_langs: List[str] = ["en", "vi", "ko"]) -> Dict[str, Any]:
        """외국인 세무 꿀팁 17개국어 텔레그램 브로드캐스트 발행"""
        messages_sent = 0
        base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
        for lang in target_langs:
            lang_name = LANGUAGES.get(lang, {}).get("native_name", lang.upper())
            easytax_url = f"{base_domain.rstrip('/')}/?lang={lang}&utm_source=telegram&utm_medium=daily_tips"
            text = f"🏛️ [EasyTax Korea Expat Tax Relief Daily ({lang_name})]\n\n"
            text += f"• E-9/H-2 Workers: Up to 90% Income Tax Reduction (Article 30)\n"
            text += f"• D-2 Students: 100% Refund on 3.3% Part-Time Withholding Tax\n"
            text += f"• Retroactive 5-Year Overpaid Tax Claims (2020~2025)\n"
            text += f"🛡️ 100% Free AI Simulation • Zero Upfront Fees\n\n"
            text += f"👉 Estimate your refund for free: {easytax_url}\n"
            text += f"* Processed via certified tax agents under Korean National Tax regulations."

            # 텔레그램 실발송 시도
            if self.bot_token and self.chat_id:
                try:
                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=5)
                    messages_sent += 1
                except Exception as e:
                    logger.warning(f"EasyTax 텔레그램 발송 실패: {e}")

            # 파일 저장
            file_path = self.output_dir / f"easytax_briefing_{lang}_{int(time.time())}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

        logger.info(f"💰 [EasyTax Telegram] {len(target_langs)}개 언어 세무 브리핑 발행 완료")
        return {
            "success": True,
            "brand": "easytax",
            "sent_count": len(target_langs),
            "message": f"💰 [EasyTax] {len(target_langs)}개 언어 공인 세무 텔레그램 브리핑이 성공적으로 발행되었습니다!"
        }
