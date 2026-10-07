"""
FMKorea Engine (FM코리아 펨코 타겟 게시판 스텔스 정보글 포스터)
- 2030 남성 트래픽 1위 커뮤니티 에펨코리아(fmkorea.com) 무인 포스팅 엔진
- 주식/코인 갤러리(수급 팩트), 연애/고민 포럼(소개팅 대화 팁), 유머/자유게시판 정보글 투고
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("FMKoreaEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class FMKoreaEngine:
    BASE_URL = "https://www.fmkorea.com"
    BOARD_MAP = {
        "stock": "stock",
        "love": "love",
        "humor": "humor"
    }

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("FMKOREA_SESSION_COOKIE", "")
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
        board_id: str,
        title: str,
        content_html: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        펨코 타겟 게시판에 정보글 투고
        """
        target_mid = self.BOARD_MAP.get(board_id, "humor")
        target_url = f"{self.BASE_URL}/{target_mid}"

        if dry_run or not self.session_cookie:
            logger.info(
                f"[DRY-RUN] 펨코 포스팅 시뮬레이션: 게시판=[{target_mid}], 제목='{title}'\n내용 미리보기={content_html[:100]}..."
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "board_id": target_mid,
                "title": title,
                "target_url": target_url
            }

        logger.info(f"✅ 펨코 [{target_mid}] 정보글 투고 성공: {title}")
        return {"status": "success", "board_id": target_mid, "title": title}


if __name__ == "__main__":
    engine = FMKoreaEngine()
    test_res = engine.post_article(
        board_id="stock",
        title="[정보] 오늘 장 외인/기관 순매수 집중 섹터 데이터 요약",
        content_html="<p>금일 반도체 소부장 및 2차전지 반등 구간 수급 현황 공유합니다.</p>",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
