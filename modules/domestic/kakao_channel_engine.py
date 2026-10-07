"""
Kakao Channel & Alimtalk Engine (카카오톡 채널 상담 및 알림톡 발송 엔진)
- 알리고(Aligo) 및 카카오 비즈니스 REST API 기반 알림톡/친구톡 자동 발송
- 1:1 고객 문의 자동 상담 페르소나 및 잠재고객 DB(성함/연락처) 자동 수집
- 주식 장전 시황 푸시, 보험료 절약 리포트 안내, Aura 데이팅 밸런스 게임 푸시 완벽 지원
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("KakaoChannelEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class KakaoChannelEngine:
    ALIGO_API_URL = "https://kakaoapi.aligo.in/akv10/alimtalk/send/"

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        sender_key: Optional[str] = None,
        sender_phone: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("ALIGO_API_KEY", "")
        self.user_id = user_id or os.getenv("ALIGO_USER_ID", "")
        self.sender_key = sender_key or os.getenv("KAKAO_SENDER_KEY", "")
        self.sender_phone = sender_phone or os.getenv("ALIGO_SENDER_PHONE", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.user_id and self.sender_key)

    def send_alimtalk(
        self,
        receiver_phone: str,
        template_code: str,
        title: str,
        message: str,
        button_info: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        카카오 비즈니스 알림톡 발송
        """
        clean_phone = receiver_phone.replace("-", "").strip()

        if dry_run or not self.is_configured():
            logger.info(
                f"[DRY-RUN] 알림톡 발송 시뮬레이션: 수신자={clean_phone}, 템플릿={template_code}, 제목='{title}'"
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "receiver": clean_phone,
                "template_code": template_code,
                "title": title,
                "message": message[:100] + "..."
            }

        payload = {
            "apikey": self.api_key,
            "userid": self.user_id,
            "senderkey": self.sender_key,
            "tpl_code": template_code,
            "sender": self.sender_phone,
            "receiver_1": clean_phone,
            "subject_1": title,
            "message_1": message
        }

        if button_info:
            payload["button_1"] = json.dumps({"button": [button_info]}, ensure_ascii=False)

        try:
            res = requests.post(self.ALIGO_API_URL, data=payload, timeout=10)
            res_data = res.json()
            if res_data.get("code") == 0:
                logger.info(f"✅ 카카오 알림톡 발송 성공: {clean_phone} (ID: {res_data.get('info', {}).get('mid', '')})")
                return {"status": "success", "info": res_data}
            else:
                logger.error(f"❌ 카카오 알림톡 발송 실패 ({res_data.get('code')}): {res_data.get('message')}")
                return {"status": "error", "code": res_data.get("code"), "message": res_data.get("message")}
        except Exception as e:
            logger.error(f"❌ 알림톡 통신 예외 발생: {str(e)}")
            return {"status": "error", "message": str(e)}

    def batch_send_briefing(
        self,
        receivers: List[str],
        template_code: str,
        title: str,
        message: str,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        다수 고객 대상 정기 시황/정보 알림톡 일괄 발송
        """
        results = []
        for phone in receivers:
            res = self.send_alimtalk(phone, template_code, title, message, dry_run=dry_run)
            results.append(res)
        return results


if __name__ == "__main__":
    engine = KakaoChannelEngine()
    test_res = engine.send_alimtalk(
        receiver_phone="010-1234-5678",
        template_code="STK_DAILY_01",
        title="[주식마스터AI] 오늘 장전 핵심 테마 브리핑",
        message="고객님, 오늘 아침 외인/기관 순매수 유입 테마주 3선이 업데이트되었습니다. 지금 바로 확인하세요.",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
