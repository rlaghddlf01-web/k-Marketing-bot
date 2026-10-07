"""
Twitter / X Engine (트위터 X 실시간 속보 및 바이럴 타래 트윗기)
- 트위터(X) 공식 API v2 기반 24시간 실시간 트윗 및 바이럴 스레드 자동 발행
- 주식 장전 08:30 속보, Aura 연애 공감 명언/밸런스 게임, 실손보험 절약 팩트 트윗
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TwitterXEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class TwitterXEngine:
    API_URL = "https://api.twitter.com/2/tweets"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("TWITTER_API_KEY", "")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET", "")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and self.access_token and self.access_token_secret)

    def post_tweet(
        self,
        text: str,
        reply_to_tweet_id: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        단일 트윗 자동 발행
        """
        if dry_run or not self.is_configured():
            logger.info(f"[DRY-RUN] 트위터(X) 트윗 시뮬레이션: '{text[:90]}...'")
            return {
                "status": "success",
                "mode": "dry_run",
                "text": text,
                "tweet_id": "dry_run_tweet_99999"
            }

        auth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret
        )

        payload: Dict[str, Any] = {"text": text}
        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

        try:
            res = requests.post(self.API_URL, auth=auth, json=payload, timeout=10)
            data = res.json()
            if res.status_code in [200, 201]:
                tweet_id = data.get("data", {}).get("id", "")
                logger.info(f"✅ 트위터(X) 발행 성공 (ID: {tweet_id})")
                return {"status": "success", "tweet_id": tweet_id, "text": text}
            else:
                logger.error(f"❌ 트위터(X) 발행 실패 ({res.status_code}): {res.text}")
                return {"status": "error", "code": res.status_code, "response": res.text}
        except Exception as e:
            logger.error(f"❌ 트위터(X) 예외 발생: {str(e)}")
            return {"status": "error", "message": str(e)}

    def post_thread(self, tweet_list: List[str], dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        연속 타래(스레드) 트윗 발행
        """
        results = []
        prev_id = None
        for text in tweet_list:
            res = self.post_tweet(text, reply_to_tweet_id=prev_id, dry_run=dry_run)
            results.append(res)
            prev_id = res.get("tweet_id")
        return results


if __name__ == "__main__":
    engine = TwitterXEngine()
    test_res = engine.post_tweet(
        text="[장전 시황 속보] 2026 오늘 아침 외국인/기관 수급 집중 테마주 TOP 3 팩트체크 완료. 지금 바로 확인하세요. #주식 #급등주 #주식마스터AI",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
