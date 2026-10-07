"""
Tistory Blog Engine (티스토리 구글 SEO 자동 발행 엔진)
- Tistory Open API (OAuth 2.0) 기반 장문 칼럼 및 HTML 서식 포스팅
- 캡차 없이 1초 컷 무인 발행 및 구글 검색(SEO) 최적화 태그/카테고리 자동 설정
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TistoryEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class TistoryEngine:
    API_BASE = "https://www.tistory.com/apis/post/write"

    def __init__(self, access_token: Optional[str] = None, default_blog_name: Optional[str] = None):
        self.access_token = access_token or os.getenv("TISTORY_ACCESS_TOKEN", "")
        self.default_blog_name = default_blog_name or os.getenv("TISTORY_BLOG_NAME", "")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.default_blog_name)

    def publish_post(
        self,
        title: str,
        content_html: str,
        blog_name: Optional[str] = None,
        visibility: int = 3,  # 0: 비공개, 1: 보호, 3: 발행(공개)
        category_id: int = 0,
        tag_list: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        티스토리에 장문 칼럼 자동 발행
        """
        target_blog = blog_name or self.default_blog_name
        tags = ",".join(tag_list) if tag_list else ""

        if dry_run or not self.is_configured():
            logger.info(f"[DRY-RUN] 티스토리 포스팅 시뮬레이션: '{title}' (Blog: {target_blog}, Tags: {tags})")
            return {
                "status": "success",
                "mode": "dry_run",
                "blog_name": target_blog,
                "title": title,
                "url": f"https://{target_blog}.tistory.com/test-preview",
                "tags": tags
            }

        payload = {
            "access_token": self.access_token,
            "output": "json",
            "blogName": target_blog,
            "title": title,
            "content": content_html,
            "visibility": str(visibility),
            "category": str(category_id),
            "tag": tags
        }

        try:
            res = requests.post(self.API_BASE, data=payload, timeout=15)
            data = res.json()
            if res.status_code == 200 and "tistory" in data and data["tistory"].get("status") == "200":
                post_url = data["tistory"].get("url", "")
                post_id = data["tistory"].get("postId", "")
                logger.info(f"✅ 티스토리 자동 발행 성공: {post_url} (ID: {post_id})")
                return {
                    "status": "success",
                    "url": post_url,
                    "post_id": post_id,
                    "title": title
                }
            else:
                err_msg = data.get("tistory", {}).get("error_message", res.text)
                logger.error(f"❌ 티스토리 발행 실패: {err_msg}")
                return {"status": "error", "message": err_msg}
        except Exception as e:
            logger.error(f"❌ 티스토리 요청 예외 발생: {str(e)}")
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    engine = TistoryEngine()
    result = engine.publish_post(
        title="[테스트] 2026 AI 기반 실시간 주식/보험/데이팅 가이드",
        content_html="<h1>무인 마케팅 공장 테스트</h1><p>본 포스팅은 티스토리 엔진 단위 테스트용입니다.</p>",
        dry_run=True,
        tag_list=["AI마케팅", "자동발행", "구글SEO"]
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
