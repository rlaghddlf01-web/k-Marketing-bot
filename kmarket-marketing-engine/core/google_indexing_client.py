import os
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import BASE_DIR

logger = logging.getLogger("GoogleIndexingClient")

class GoogleIndexingClient:
    """
    Google Search Indexing API v3 공식 연동 클라이언트
    - Google Cloud Service Account 기반 OAuth2 Bearer 토큰 획득
    - URL_UPDATED 신호를 구글 검색 로봇에게 직접 전송하여 1~2시간 내 초고속 색인 보장
    """
    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    def __init__(self, key_path: Optional[Path] = None, brand: str = "kmarket", *args, **kwargs):
        resolved_brand = kwargs.get("brand") or kwargs.get("service_id") or brand or "kmarket"
        self.brand = str(resolved_brand).lower()
        self.key_path = key_path or kwargs.get("key_path") or self._find_key_file()
        self.credentials = None
        self._init_credentials()

    def _find_key_file(self) -> Optional[Path]:
        """브랜드별(kmarket/easytax) 독립 서비스 계정 키 파일 자동 탐색"""
        if self.brand == "easytax":
            candidates = [
                BASE_DIR / "service_account_easytax.json",
                BASE_DIR / "easy_service_account.json",
                BASE_DIR / "easy_service_account.json.json",
                Path("service_account_easytax.json"),
                Path("easy_service_account.json"),
                Path("easy_service_account.json.json"),
                BASE_DIR / "service_account.json"
            ]
        else:
            candidates = [
                BASE_DIR / "service_account_kmarket.json",
                BASE_DIR / "service_account.json",
                BASE_DIR / "service_account.json.json",
                Path("service_account_kmarket.json"),
                Path("service_account.json"),
                Path("service_account.json.json")
            ]

        for c in candidates:
            if c.exists() and c.is_file():
                return c
        return None

    def _init_credentials(self):
        if not self.key_path or not self.key_path.exists():
            logger.warning(f"Google Service Account key file not found for [{self.brand.upper()}]: {self.key_path}")
            return

        try:
            from google.oauth2 import service_account
            self.credentials = service_account.Credentials.from_service_account_file(
                str(self.key_path),
                scopes=self.SCOPES
            )
            logger.info(f"Google Indexing API authenticated for [{self.brand.upper()}] ({self.credentials.service_account_email})")
        except Exception as e:
            logger.error(f"Google Indexing API credential initialization failed for [{self.brand.upper()}]: {e}")
            self.credentials = None

    def is_configured(self) -> bool:
        return self.credentials is not None

    def get_service_account_email(self) -> str:
        if self.credentials:
            return getattr(self.credentials, "service_account_email", "")
        return ""

    def _get_access_token(self) -> Optional[str]:
        if not self.credentials:
            return None
        try:
            import google.auth.transport.requests
            request = google.auth.transport.requests.Request()
            self.credentials.refresh(request)
            return self.credentials.token
        except Exception as e:
            logger.error(f"Access Token refresh failed: {e}")
            return None

    def publish_url(self, url: str, notification_type: str = "URL_UPDATED") -> Dict[str, Any]:
        """단일 URL 구글 인덱싱 핑 전송"""
        token = self._get_access_token()
        if not token:
            return {"success": False, "url": url, "error": "Access Token not available"}

        payload = {
            "url": url,
            "type": notification_type
        }
        data_bytes = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            self.INDEXING_ENDPOINT,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                return {
                    "success": True,
                    "url": url,
                    "status_code": resp.status,
                    "response": resp_data
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Google Indexing API HTTP {e.code} Error ({url}): {err_body}")
            return {
                "success": False,
                "url": url,
                "status_code": e.code,
                "error": err_body
            }
        except Exception as e:
            logger.error(f"Google Indexing API error ({url}): {e}")
            return {"success": False, "url": url, "error": str(e)}

    def batch_publish_urls(self, urls: List[str], max_limit: int = 50) -> Dict[str, Any]:
        """주요 핵심 URL 대량 배치 색인 핑 전송 (구글 일일 쿼터 준수)"""
        if not self.is_configured():
            return {
                "success": False,
                "total_requested": len(urls),
                "success_count": 0,
                "failed_count": len(urls),
                "error": "Google Service Account key file not configured"
            }

        target_urls = urls[:max_limit]
        results = []
        success_count = 0
        failed_count = 0

        for u in target_urls:
            res = self.publish_url(u)
            results.append(res)
            if res.get("success"):
                success_count += 1
            else:
                failed_count += 1

        return {
            "success": success_count > 0,
            "total_requested": len(target_urls),
            "success_count": success_count,
            "failed_count": failed_count,
            "service_account": self.get_service_account_email(),
            "results": results[:5]
        }
