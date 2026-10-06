import logging
from pathlib import Path
from typing import Optional, Dict, Any
from core.notifier import Notifier
from core.db_manager import DBManager

logger = logging.getLogger("SocialPublisher")

class SocialPublisher:
    """
    [무인 자동화 7] SNS 및 텔레그램/메신저 채널 자동 피드 발행기
    """
    def __init__(self, db_mgr: DBManager, notifier: Notifier):
        self.db_mgr = db_mgr
        self.notifier = notifier

    def publish_feed(self, title: str, text: str, image_path: Optional[Path] = None, 
                     service_id: str = "kmarket", lang: str = "en") -> bool:
        """텔레그램 채널 및 소셜 피드에 자동 발행"""
        formatted_message = f"📢 *[{title}]*\n\n{text}"
        
        # 텔레그램 발행 시도
        success = self.notifier.send_telegram_message(formatted_message)
        
        # 메신저 슬롯 브로드캐스트
        self.notifier.broadcast_to_messengers(formatted_message)

        logger.info(f"[{lang.upper()}] 소셜 피드 발행 완료 ({service_id})")
        return success
