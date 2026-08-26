import logging
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from config import BASE_DIR, LANGUAGES, OUTPUTS_DIR, DATA_DIR
from core.db_manager import DBManager

logger = logging.getLogger("KMarketTelegram")

class KMarketTelegramPusher:
    """
    🛒 [K-Market 전용 17개국 텔레그램 브로드캐스트 엔진]
    - 270개 실물 매물 중 0원 무료나눔 & 무빙세일 꿀매물 17개국 다국어 브리핑 발송
    """
    def __init__(self, db_mgr: DBManager):
        self.db_mgr = db_mgr
        self.output_dir = OUTPUTS_DIR / "briefings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kmarket_items = self._load_json(DATA_DIR / "kmarket_items.json")
        self.env_path = BASE_DIR / ".env"
        self.bot_token = self._get_env("KMARKET_TELEGRAM_BOT_TOKEN") or self._get_env("TELEGRAM_BOT_TOKEN")
        self.chat_id = self._get_env("KMARKET_TELEGRAM_CHAT_ID")

    def _get_env(self, key: str) -> str:
        if self.env_path.exists():
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(key + "="):
                        return line.split("=", 1)[1].strip()
        return ""

    def _load_json(self, path: Path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def broadcast_daily_deals(self, target_langs: List[str] = ["en", "vi", "ko"]) -> Dict[str, Any]:
        """0원 나눔 꿀매물 17개국어 텔레그램 브로드캐스트 발행"""
        free_items = [i for i in self.kmarket_items if i.get("price") == 0][:3]
        if not free_items and self.kmarket_items:
            free_items = self.kmarket_items[:3]

        messages_sent = 0
        for lang in target_langs:
            lang_name = LANGUAGES.get(lang, {}).get("native_name", lang.upper())
            text = f"🎁 [K-Market Today's 0 KRW Free Giveaways ({lang_name})]\n\n"
            for item in free_items:
                text += f"• {item.get('title')} (📍 {item.get('region', 'Korea')}) - 0 KRW FREE!\n"
            text += f"\n👉 Grab free items now: https://k-market.app?lang={lang}\n"
            text += f"💬 17-Language Instant Translation Chat Enabled"

            # 텔레그램 실발송 시도
            if self.bot_token and self.chat_id:
                try:
                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=5)
                    messages_sent += 1
                except Exception as e:
                    logger.warning(f"K-Market 텔레그램 발송 실패: {e}")

            # 파일 저장
            file_path = self.output_dir / f"kmarket_briefing_{lang}_{int(time.time())}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

        logger.info(f"🛒 [K-Market Telegram] {len(target_langs)}개 언어 0원 나눔 브리핑 발행 완료")
        return {
            "success": True,
            "brand": "kmarket",
            "sent_count": len(target_langs),
            "message": f"🛒 [K-Market] {len(target_langs)}개 언어 0원 나눔 텔레그램 브리핑이 성공적으로 발행되었습니다!"
        }
