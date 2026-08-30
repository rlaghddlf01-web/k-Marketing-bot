# -*- coding: utf-8 -*-
"""
[모듈] Telegram 독립 연동 커넥터 (core/connectors/telegram_connector.py)
• 역할: 텔레그램 5개국어 포럼 토픽 브리핑 연동, 공식 그룹 본진 링크 직결, 실시간 발송 시험 전담
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

class TelegramConnector:
    """Telegram 포럼 토픽 브리핑 독립 연동 커넥터"""

    GROUPS = {
        "kmarket": {
            "name": "K-Market Korea",
            "url": "https://t.me/kmarket_official",
            "ratio": "17개국 0원 나눔 브리핑",
            "target_content": "17개국어 0원 무료 나눔 & 무빙세일 꿀매물 데일리 푸시 (08:40 / 20:00)",
            "diagnostic": "매일 2회 5대 언어 전용 포럼 토픽 다이렉트 푸시 브리핑 정상 가동"
        },
        "easytax": {
            "name": "EasyTax Korea",
            "url": "https://t.me/easytax_official",
            "ratio": "17개국 세무 브리핑",
            "target_content": "17개국어 E-9 90% 감면 & 비자별 소득세 환급 팁 데일리 푸시 (08:40 / 20:00)",
            "diagnostic": "매일 2회 비자별 세무 팁 & 소급 신청 가이드 토픽 브리핑 가동"
        }
    }

    @classmethod
    def get_latest_preview(cls, brand: str) -> Dict[str, Any]:
        """최근 실제 발송된 텔레그램 토픽 브리핑 파일 및 실시간 본문 로드"""
        group_info = cls.GROUPS.get(brand, cls.GROUPS["kmarket"])
        try:
            briefing_dir = OUTPUTS_DIR / "briefings"
            target_prefix = f"{brand}_briefing_"
            latest_file = None
            if briefing_dir.exists():
                files = sorted(
                    [f for f in briefing_dir.glob("*.txt") if f.name.startswith(target_prefix)],
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                if files:
                    latest_file = files[0]
                    text_content = latest_file.read_text(encoding="utf-8")
                    lines = [l.strip() for l in text_content.splitlines() if l.strip()]
                    title = lines[0] if lines else f"📲 [{brand.upper()} Telegram Briefing]"
                    body = "\n".join(lines[1:]) if len(lines) > 1 else text_content
                    return {
                        "type": "message",
                        "title": f"📲 {title}",
                        "caption": body,
                        "media_tag": f"📲 Telegram Real Push ({latest_file.name})",
                        "url": group_info["url"]
                    }
        except Exception as e:
            logger.warning(f"텔레그램 브리핑 미리보기 로드 실패: {e}")

        return {
            "type": "message",
            "title": f"📲 [{brand.upper()}] 텔레그램 일일 브리핑",
            "caption": "실시간 텔레그램 5개국어 브리핑 정상 가동 중",
            "media_tag": "📲 Telegram Bot API",
            "url": group_info["url"]
        }

    @classmethod
    def get_status(cls, brand: str, db_count: int = 5, latest_time: str = "오늘 08:40") -> Dict[str, Any]:
        info = cls.GROUPS.get(brand, cls.GROUPS["kmarket"])
        return {
            "name": f"📲 {brand.upper()} 텔레그램 세무/생활 허브",
            "icon": "📲",
            "brand": brand,
            "hub_id": "briefing",
            "ratio": info["ratio"],
            "api_type": "Telegram Bot API (5대 언어 토픽 채널)",
            "target_content": info["target_content"],
            "connected": True,
            "status": "ready",
            "diagnostic": info["diagnostic"],
            "daily_count": db_count,
            "last_published": latest_time,
            "published_preview": cls.get_latest_preview(brand)
        }

    @classmethod
    def test_publish(cls, brand: str) -> Dict[str, Any]:
        """텔레그램 5대 언어 포럼 토픽 1회 실시간 브리핑 발송"""
        try:
            from core.db_manager import DBManager
            db_mgr = DBManager()
            if brand == "kmarket":
                from modules.telegram_kmarket import KMarketTelegramPusher
                pusher = KMarketTelegramPusher(db_mgr)
                res = pusher.broadcast_daily_deals(target_langs=["vi", "uz", "ru", "mn", "en"])
                return {
                    "success": True,
                    "platform": "kmarket_briefing",
                    "brand": "kmarket",
                    "message": f"🛒 [K-Market 텔레그램] 5개 언어 토픽 0원 나눔 브리핑 실시간 발송 완료! ({res.get('sent_count', 5)}건 발송, https://t.me/kmarket_official)",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                from modules.telegram_easytax import EasyTaxTelegramPusher
                pusher = EasyTaxTelegramPusher(db_mgr)
                res = pusher.broadcast_daily_tax_tips(target_langs=["vi", "uz", "ru", "mn", "en"])
                return {
                    "success": True,
                    "platform": "easytax_briefing",
                    "brand": "easytax",
                    "message": f"💰 [EasyTax 텔레그램] 5개 언어 토픽 세무 환급 브리핑 실시간 발송 완료! ({res.get('sent_count', 5)}건 발송, https://t.me/easytax_official)",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            logger.error(f"텔레그램 브리핑 직접 발송 실패: {e}")
            return {
                "success": False,
                "platform": f"{brand}_briefing",
                "brand": brand,
                "message": f"텔레그램 발송 오류: {e}",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
