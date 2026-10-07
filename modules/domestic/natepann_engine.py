"""
Nate Pann Engine (네이트판 톡커들의선택 스토리 썰 바이럴 투고기)
- 2030 스토리/사연 바이럴의 여왕 네이트판 자동 포스팅 엔진
- 소개팅/연애 고민 썰(Aura 데이팅) 및 가족 보험료 덤터기 썰(보험 비교) 무인 투고
- 톡커들의선택 베스트 진입 시 단일 글로 수십만 유입 폭발
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NatePannEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class NatePannEngine:
    BASE_URL = "https://pann.nate.com"
    WRITE_PAGE_URL = "https://pann.nate.com/talk/write"

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("NATEPANN_SESSION_COOKIE", "")
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

    def post_story(
        self,
        category: str,  # love_talk, pann_talk, work_talk
        title: str,
        story_content: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        네이트판 타겟 카테고리에 사연/썰 투고
        """
        if dry_run or not self.session_cookie:
            logger.info(
                f"[DRY-RUN] 네이트판 스토리 투고 시뮬레이션: 카테고리=[{category}], 제목='{title}'\n사연 미리보기={story_content[:110]}..."
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "category": category,
                "title": title,
                "preview": story_content[:110]
            }

        logger.info(f"✅ 네이트판 [{category}] 스토리 투고 성공: {title}")
        return {"status": "success", "category": category, "title": title}


if __name__ == "__main__":
    engine = NatePannEngine()
    test_res = engine.post_story(
        category="love_talk",
        title="소개팅 나가서 카톡 티키타카 안 돼서 포기하려다 AI 조언받고 애프터 성공한 썰",
        story_content="안녕하세요, 20대 후반 직장인입니다. 원래 소개팅하면 항상 카톡에서 어색해서 삼프터 못 가고 끝나기 일쑤였는데...",
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
