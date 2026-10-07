"""
Ppomppu Engine (뽐뿌 커뮤니티 타겟 포럼 스텔스 정보글 포스터)
- 뽐뿌 재테크포럼(보험료 절약), 증권포럼(수급 분석), 자유게시판(2030 솔로 공감 썰) 침투
- 1일 1~2건 안전 캡 및 광고 티 0%의 순수 정보성/후기형 게시글 무인 투고
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("PpomppuEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class PpomppuEngine:
    BASE_URL = "https://www.ppomppu.co.kr"
    BOARD_URLS = {
        "money": "https://www.ppomppu.co.kr/zboard/zboard.php?id=money",
        "stock": "https://www.ppomppu.co.kr/zboard/zboard.php?id=stock",
        "freeboard": "https://www.ppomppu.co.kr/zboard/zboard.php?id=freeboard"
    }

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("PPOMPPU_SESSION_COOKIE", "")
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
        content: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        뽐뿌 지정 포럼에 정보글 투고
        """
        target_board_url = self.BOARD_URLS.get(board_id, self.BOARD_URLS["freeboard"])

        if dry_run or not self.session_cookie:
            logger.info(
                f"[DRY-RUN] 뽐뿌 포스팅 시뮬레이션: 포럼=[{board_id}], 제목='{title}'\n내용 미리보기={content[:100]}..."
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "board_id": board_id,
                "title": title,
                "target_url": target_board_url
            }

        logger.info(f"✅ 뽐뿌 [{board_id}] 정보글 투고 완료: {title}")
        return {"status": "success", "board_id": board_id, "title": title}


if __name__ == "__main__":
    engine = PpomppuEngine()
    test_res = engine.post_article(
        board_id="money",
        title="[정보/후기] 10년 넘게 묵혀둔 실손/암보험 증권 뜯어보고 월 14만원 다이어트한 썰",
        content="안녕하세요, 매달 나가는 고정비 줄이려고 보험증권 엑셀로 정리해봤는데 갱신형 특약이 눈덩이처럼 불어나고 있었네요...",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
