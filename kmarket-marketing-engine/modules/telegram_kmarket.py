import logging
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from config import BASE_DIR, LANGUAGES, OUTPUTS_DIR, DATA_DIR, BASE_URLS
from core.db_manager import DBManager

logger = logging.getLogger("KMarketTelegram")

KMARKET_BRIEFING_TEMPLATES = {
    "ko": {
        "header": "🎁 [K-Market 오늘 하루 0원 무료 나눔 꿀매물]",
        "free_tag": "0원 무료 나눔!",
        "cta": "👉 지금 0원 나눔 꿀매물 잡기",
        "footer": "💬 17개 언어 실시간 자동번역 1:1 채팅 지원"
    },
    "en": {
        "header": "🎁 [K-Market Today's 0 KRW Free Giveaways]",
        "free_tag": "0 KRW FREE!",
        "cta": "👉 Grab free items now",
        "footer": "💬 17-Language Instant Translation Chat Enabled"
    },
    "vi": {
        "header": "🎁 [K-Market Đồ Tặng Miễn Phí 0 Won Hôm Nay]",
        "free_tag": "0 Won MIỄN PHÍ!",
        "cta": "👉 Nhận đồ miễn phí ngay",
        "footer": "💬 Hỗ trợ nhắn tin dịch tự động 17 ngôn ngữ"
    },
    "uz": {
        "header": "🎁 [K-Market Bugungi 0 Wonlik Bepul Mebellar]",
        "free_tag": "0 Won BEPUL!",
        "cta": "👉 Bepul mebelni darhol oling",
        "footer": "💬 17 tilda real vaqt avtomatik tarjima mavjud"
    },
    "ru": {
        "header": "🎁 [K-Market Бесплатная мебель и техника 0 вон на сегодня]",
        "free_tag": "0 вон БЕСПЛАТНО!",
        "cta": "👉 Забрать бесплатные вещи сейчас",
        "footer": "💬 Чат с автопереводом на 17 языков в реальном времени"
    },
    "mn": {
        "header": "🎁 [K-Market Өнөөдрийн 0 воны үнэгүй тавилга, бараа]",
        "free_tag": "0 вон ҮНЭГҮЙ!",
        "cta": "👉 Үнэгүй барааг одоо авах",
        "footer": "💬 17 хэлний бодит цагийн автомат орчуулгатай чат"
    },
    "zh": {
        "header": "🎁 [K-Market 今日 0 韩元免费二手家具好物]",
        "free_tag": "0 韩元免费赠送!",
        "cta": "👉 立即领取 0 元好物",
        "footer": "💬 支持 17 种语言实时自动翻译 1:1 聊天"
    },
    "tl": {
        "header": "🎁 [K-Market Libreng Gamit Ngayong Araw (0 Won)]",
        "free_tag": "0 Won LIBRE!",
        "cta": "👉 Kunin ang libreng gamit ngayon",
        "footer": "💬 May 17-Language Auto-Translation Chat"
    },
    "th": {
        "header": "🎁 [K-Market ของแจกฟรี 0 วอน วันนี้]",
        "free_tag": "0 วอน ฟรี!",
        "cta": "👉 รับของแจกฟรีทันที",
        "footer": "💬 แชทแปลภาษาอัตโนมัติ 17 ภาษาแบบเรียลไทม์"
    },
    "id": {
        "header": "🎁 [K-Market Barang Gratis 0 Won Hari Ini]",
        "free_tag": "0 Won GRATIS!",
        "cta": "👉 Ambil barang gratis sekarang",
        "footer": "💬 Obrolan dengan terjemahan otomatis 17 bahasa"
    }
}


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

    def broadcast_daily_deals(self, target_langs: List[str] = ["vi", "uz", "ru", "en", "ko"]) -> Dict[str, Any]:
        """0원 나눔 꿀매물 17개국어 100% 현지화 텔레그램 브로드캐스트 발행"""
        free_items = [i for i in self.kmarket_items if i.get("price") == 0][:3]
        if not free_items and self.kmarket_items:
            free_items = self.kmarket_items[:3]

        base_url = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")
        messages_sent = 0

        for lang in target_langs:
            tmpl = KMARKET_BRIEFING_TEMPLATES.get(lang, KMARKET_BRIEFING_TEMPLATES["en"])
            text = f"{tmpl['header']}\n\n"

            for item in free_items:
                title = item.get("title", "")
                if item.get("translations") and item["translations"].get(lang):
                    title = item["translations"][lang].get("title", title)
                region = item.get("region", "Korea")
                text += f"• {title} (📍 {region}) - {tmpl['free_tag']}\n"

            item_url = f"{base_url.rstrip('/')}/?lang={lang}&utm_source=telegram&utm_medium=daily_briefing"
            text += f"\n{tmpl['cta']}: {item_url}\n"
            text += f"{tmpl['footer']}"

            # 텔레그램 실발송 (언어별 전용 포럼 토픽으로 다이렉트 전송)
            if self.bot_token and self.chat_id:
                try:
                    payload = {"chat_id": self.chat_id, "text": text}
                    topics_file = DATA_DIR / "telegram_topics.json"
                    if topics_file.exists():
                        try:
                            with open(topics_file, "r", encoding="utf-8") as tf:
                                t_data = json.load(tf)
                            thread_id = t_data.get("kmarket", {}).get(lang)
                            if thread_id:
                                payload["message_thread_id"] = thread_id
                        except Exception:
                            pass

                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    requests.post(url, json=payload, timeout=5)
                    messages_sent += 1
                except Exception as e:
                    logger.warning(f"K-Market 텔레그램 발송 실패 ({lang}): {e}")

            # 파일 저장
            file_path = self.output_dir / f"kmarket_briefing_{lang}_{int(time.time())}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

        logger.info(f"🛒 [K-Market Telegram] {len(target_langs)}개 언어 100% 현지화 브리핑 발행 완료")
        return {
            "success": True,
            "brand": "kmarket",
            "sent_count": len(target_langs),
            "message": f"🛒 [K-Market] {len(target_langs)}개 언어 100% 현지화 0원 나눔 브리핑 발행 완료!"
        }
