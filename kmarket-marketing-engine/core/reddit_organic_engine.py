"""
🌱 [Reddit Organic Engine — 유기적 활동 엔진]
- 업보트(좋아요) 자동화: 타깃 + 인기 서브레딧 혼합
- 피드 스크롤/읽기 시뮬레이션
- 비홍보 도움 댓글 자동 작성 (Gemini AI)
- 모든 활동을 AccountHealthMonitor와 연동
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional

from config import (
    DAILY_REDDIT_ORGANIC_LIMIT, DAILY_REDDIT_UPVOTE_LIMIT,
    ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC,
)
from core.reddit_browser_driver import RedditBrowserDriver
from core.reddit_account_health import AccountHealthMonitor
from core.gemini_reddit_organic import RedditOrganicAI

logger = logging.getLogger("RedditOrganicEngine")

# 유기적 활동용 서브레딧 풀 (타깃 + 일반 인기)
_TARGET_SUBS = [
    "Living_in_Korea", "korea", "teachinginkorea", "seoul",
    "StudyInKorea", "movingtokorea", "EPIK", "Hanguk"
]

# 일반 인기 서브레딧 (다양성 유지 + 카르마 축적)
_GENERAL_SUBS = [
    "AskReddit", "todayilearned", "LifeProTips",
    "travel", "solotravel", "digitalnomad",
    "languagelearning", "Korean"
]


class RedditOrganicEngine:
    """
    🌱 레딧 유기적 활동 엔진
    - 업보트, 스크롤, 비홍보 댓글을 인간처럼 수행
    - AccountHealthMonitor와 연동하여 안전 한도 준수
    """
    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id
        self.driver = RedditBrowserDriver(service_id=service_id)
        self.health = AccountHealthMonitor(service_id=service_id)
        self.organic_ai = RedditOrganicAI()

    # ──────────────────────────────────────────
    # 👍 업보트 세션
    # ──────────────────────────────────────────

    def run_upvote_session(self, count: int = 0) -> Dict[str, Any]:
        """
        업보트 세션 실행
        - 타깃 + 일반 서브레딧 혼합 (70:30)
        - 글 읽기 → 업보트 클릭 → 다음 글로 이동
        """
        actual_count = count if count > 0 else random.randint(3, 6)
        result = {"upvoted": 0, "errors": 0}

        if not self.health.can_upvote(DAILY_REDDIT_UPVOTE_LIMIT):
            logger.info("🛡️ 일일 업보트 한도 도달, 세션 스킵")
            return result

        # 서브레딧 혼합 선택 (타깃 70% + 일반 30%)
        subs_to_scan = []
        for _ in range(actual_count):
            if random.random() < 0.7:
                subs_to_scan.append(random.choice(_TARGET_SUBS))
            else:
                subs_to_scan.append(random.choice(_GENERAL_SUBS))

        # 먼저 글 목록 수집
        unique_subs = list(set(subs_to_scan))[:3]
        posts = self.driver.fetch_live_posts(unique_subs, limit_per_sub=10)

        if not posts:
            logger.info("스캔된 글이 없어 업보트 세션 종료")
            return result

        # 랜덤하게 선택하여 업보트
        random.shuffle(posts)
        for post in posts[:actual_count]:
            if not self.health.can_upvote(DAILY_REDDIT_UPVOTE_LIMIT):
                break

            try:
                read_sec = random.randint(3, 10)
                res = self.driver.upvote_post(post["url"], read_sec=read_sec)
                if res.get("success"):
                    self.health.record_upvote()
                    result["upvoted"] += 1
                    logger.info(f"👍 업보트 완료: '{post['title'][:50]}...'")
                else:
                    result["errors"] += 1
            except Exception as e:
                logger.error(f"업보트 에러: {e}")
                result["errors"] += 1

            # 업보트 간 자연스러운 딜레이
            delay = random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC)
            logger.info(f"⏳ 다음 활동까지 {delay}초 대기...")
            time.sleep(delay)

        logger.info(f"👍 업보트 세션 완료: {result['upvoted']}건 성공")
        return result

    # ──────────────────────────────────────────
    # 📖 스크롤/읽기 세션
    # ──────────────────────────────────────────

    def run_browse_session(self, duration_sec: int = 0) -> Dict[str, Any]:
        """
        피드 스크롤/읽기 세션
        - 자연스러운 브라우징 시뮬레이션
        - 타깃 + 일반 서브레딧 혼합
        """
        actual_duration = duration_sec if duration_sec > 0 else random.randint(60, 180)
        sub = random.choice(_TARGET_SUBS + _GENERAL_SUBS)
        result = self.driver.scroll_feed(sub, duration_sec=actual_duration)
        logger.info(f"📖 브라우징 세션 완료: r/{sub}")
        return result

    # ──────────────────────────────────────────
    # 💬 비홍보 댓글 세션
    # ──────────────────────────────────────────

    def run_organic_comment_session(self, count: int = 0) -> Dict[str, Any]:
        """
        비홍보 순수 도움 댓글 세션
        - AI로 100% 비홍보 댓글 생성
        - 타깃 서브레딧의 질문 글에 도움 답변
        """
        actual_count = count if count > 0 else random.randint(2, 3)
        result = {"commented": 0, "errors": 0}

        if not self.health.can_post_organic(DAILY_REDDIT_ORGANIC_LIMIT):
            logger.info("🛡️ 일일 유기적 댓글 한도 도달, 세션 스킵")
            return result

        # 타깃 서브레딧에서 질문글 스캔
        subs = random.sample(_TARGET_SUBS, min(3, len(_TARGET_SUBS)))
        posts = self.driver.fetch_live_posts(subs, limit_per_sub=15)

        if not posts:
            logger.info("스캔된 글이 없어 댓글 세션 종료")
            return result

        # 질문성 글 필터링 (제목에 ? 포함, how/where/what 등)
        question_posts = [
            p for p in posts
            if any(q in p["title"].lower() for q in ["?", "how", "where", "what", "when", "anyone", "any", "help", "advice", "recommend", "tip"])
        ]

        if not question_posts:
            question_posts = posts  # 질문글이 없으면 일반 글에도 댓글 가능

        random.shuffle(question_posts)

        for post in question_posts[:actual_count]:
            if not self.health.can_post_organic(DAILY_REDDIT_ORGANIC_LIMIT):
                break

            try:
                # AI로 비홍보 댓글 생성
                comment = self.organic_ai.generate_organic_comment(
                    post_title=post["title"],
                    post_body=post.get("body", ""),
                    target_lang="en"
                )

                if not comment:
                    logger.warning("유기적 댓글 생성 실패, 스킵")
                    continue

                # 댓글 게시
                res = self.driver.post_comment_humanlike(post["url"], comment)
                if res.get("success"):
                    self.health.record_organic_comment()
                    result["commented"] += 1
                    logger.info(f"💬 비홍보 댓글 등록 완료: '{post['title'][:50]}...'")

                    # 댓글 가시성 확인 (10초 후)
                    time.sleep(10)
                    visible = self.driver.check_comment_visible(post["url"], comment[:50])
                    if not visible:
                        self.health.report_deletion(post["url"], comment[:100])
                        logger.warning("⚠️ 댓글이 보이지 않음! 삭제/숨김 감지")
                else:
                    result["errors"] += 1
                    logger.warning(f"유기적 댓글 등록 실패: {res.get('error')}")

            except Exception as e:
                logger.error(f"유기적 댓글 에러: {e}")
                result["errors"] += 1

            # 댓글 간 딜레이
            delay = random.randint(ORGANIC_DELAY_MIN_SEC, ORGANIC_DELAY_MAX_SEC)
            logger.info(f"⏳ 다음 댓글까지 {delay}초 대기...")
            time.sleep(delay)

        logger.info(f"💬 유기적 댓글 세션 완료: {result['commented']}건 성공")
        return result
