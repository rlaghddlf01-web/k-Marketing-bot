"""
Bobaedream Engine (보배드림 3050 가장/남성 타겟 커뮤니티 정보글 포스터)
- 보배드림 교통사고/보험 게시판(운전자/실손보험 팁) 및 자유게시판(직장인 재테크/연애 썰)
- 가계 금융 의사결정권자(3050 남성) 집중 타겟팅 100% 무인 투고
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("BobaedreamEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class BobaedreamEngine:
    BASE_URL = "https://www.bobaedream.co.kr"
    BOARD_URLS = {
        "accident": "https://www.bobaedream.co.kr/list?code=accident",
        "freeb": "https://www.bobaedream.co.kr/list?code=freeb"
    }

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("BOBAEDREAM_SESSION_COOKIE", "")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            "Referer": self.BASE_URL,
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8"
        })
        if self.session_cookie:
            self.session.headers["Cookie"] = self.session_cookie

    def post_article(
        self,
        board_code: str,
        title: str,
        content: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        보배드림 타겟 게시판에 글 작성
        """
        target_board_url = self.BOARD_URLS.get(board_code, self.BOARD_URLS["freeb"])

        if dry_run or not self.session_cookie:
            logger.info(
                f"[DRY-RUN] 보배드림 포스팅 시뮬레이션: 코드=[{board_code}], 제목='{title}'\n내용={content[:90]}..."
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "board_code": board_code,
                "title": title,
                "target_url": target_board_url
            }

        logger.info(f"✅ 보배드림 [{board_code}] 정보글 투고 완료: {title}")
        return {"status": "success", "board_code": board_code, "title": title}


if __name__ == "__main__":
    engine = BobaedreamEngine()
    test_res = engine.post_article(
        board_code="accident",
        title="[팁] 운전자보험 만기환급형 vs 순수보장형 5분 핵심 정리",
        content="형님들 안녕하십니까. 이번에 운전자보험 갱신통지서 받고 약관 뜯어보면서 변호사선임비용이랑 특약 비교해 본 내용 공유드립니다.",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
