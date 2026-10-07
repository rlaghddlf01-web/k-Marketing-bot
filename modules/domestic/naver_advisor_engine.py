"""
Naver Search Advisor Engine (네이버 서치어드바이저 수집 요청 및 색인 가속 엔진)
- 네이버 웹마스터도구(서치어드바이저)에 새로 발행된 블로그 및 웹페이지 URL 즉시 수집 요청
- 네이버 검색 로봇(Yeti)이 1분 이내에 콘텐츠를 긁어가도록 핑 자동 전송
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NaverAdvisorEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class NaverAdvisorEngine:
    PING_ENDPOINT = "https://searchadvisor.naver.com/api/v1/crawl/request"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NAVER_SEARCH_ADVISOR_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def request_crawl(self, target_url: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        네이버 서치어드바이저에 특정 URL 수집 요청 전송
        """
        if dry_run or not self.is_configured():
            logger.info(f"[DRY-RUN] 네이버 서치어드바이저 수집 요청 핑: {target_url}")
            return {
                "status": "success",
                "mode": "dry_run",
                "target_url": target_url,
                "message": "수집 요청 핑 시뮬레이션 완료"
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": target_url
        }

        try:
            res = requests.post(self.PING_ENDPOINT, headers=headers, json=payload, timeout=10)
            if res.status_code in [200, 201, 202]:
                logger.info(f"✅ 네이버 서치어드바이저 수집 요청 성공: {target_url}")
                return {"status": "success", "url": target_url}
            else:
                logger.warning(f"⚠️ 네이버 서치어드바이저 응답 ({res.status_code}): {res.text}")
                return {"status": "warning", "code": res.status_code, "response": res.text}
        except Exception as e:
            logger.error(f"❌ 네이버 서치어드바이저 예외 발생: {str(e)}")
            return {"status": "error", "message": str(e)}

    def batch_request_crawl(self, urls: List[str], dry_run: bool = False) -> List[Dict[str, Any]]:
        results = []
        for url in urls:
            results.append(self.request_crawl(url, dry_run=dry_run))
        return results


if __name__ == "__main__":
    engine = NaverAdvisorEngine()
    res = engine.request_crawl("https://blog.naver.com/test-article-123", dry_run=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
