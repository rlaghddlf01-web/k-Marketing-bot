import time
import random
import logging
from typing import List, Dict, Any
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_AUTO_REPLY,
    REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC,
    HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT
)
from core.db_manager import DBManager
from core.service_router import ServiceRouter
from core.utm_tracker import UTMTracker
from core.gemini_engine import GeminiEngine
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("RedditLeadHunter")

TARGET_SUBREDDITS = ["korea", "Living_in_Korea", "teachinginkorea", "Hanguk"]

class RedditLeadHunter:
    """
    [무인 자동화 1] 레딧 실시간 리드 감지 & Anti-Ban 자가학습 댓글 작성기
    """
    def __init__(self, db_mgr: DBManager, router: ServiceRouter, gemini: GeminiEngine):
        self.db_mgr = db_mgr
        self.router = router
        self.gemini = gemini
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self):
        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT,
                    username=REDDIT_USERNAME,
                    password=REDDIT_PASSWORD
                )
                logger.info("Reddit PRAW 클라이언트 연동 완료")
            except Exception as e:
                logger.warning(f"Reddit 클라이언트 초기화 실패 (시뮬레이션 모드 가동): {e}")
                self.reddit = None

    def scan_and_reply(self, limit: int = 10) -> int:
        """새로운 질문 글을 스캔하고 맞춤형 팩트 답변 등록"""
        processed_count = 0

        # PRAW 실제 연동 시
        if self.reddit:
            try:
                for sub_name in TARGET_SUBREDDITS:
                    sub = self.reddit.subreddit(sub_name)
                    for post in sub.new(limit=limit):
                        if self._process_post(post.id, post.title, post.selftext, sub_name, post_obj=post):
                            processed_count += 1
            except Exception as e:
                logger.error(f"레딧 스캔 중 에러: {e}")
        else:
            # PRAW 미설정 시 안전 시뮬레이션 동작
            sample_posts = [
                {"id": "sim_post_001", "title": "How do D-2 student tax refunds work in Korea?", "body": "I worked part-time at a cafe and 3.3% was deducted. Can I get this back?", "sub": "Living_in_Korea"},
                {"id": "sim_post_002", "title": "Moving out of Sinchon studio, where to buy cheap desk or get free fridge?", "body": "Looking for secondhand appliances near Yonsei.", "sub": "korea"}
            ]
            for p in sample_posts:
                if self._process_post(p["id"], p["title"], p["body"], p["sub"]):
                    processed_count += 1

        return processed_count

    def _process_post(self, post_id: str, title: str, body: str, subreddit: str, post_obj: Any = None) -> bool:
        # 1. 중복 확인
        if self.db_mgr.is_already_processed(post_id):
            return False

        # 2. Rate Limit 확인 (안티밴 가드레일)
        channel_key = f"reddit:{subreddit}"
        if not self.db_mgr.check_rate_limit(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT):
            logger.warning(f"[{channel_key}] Rate Limit 도달로 응답 건너뜀 (Anti-Ban 보호)")
            return False

        # 3. 서비스 지능형 라우팅
        full_text = f"{title} {body}"
        service_id, service_data = self.router.route_query(full_text)

        # 4. 동적 UTM 랜딩 링크 생성
        target_lang = "en"
        campaign = UTMTracker.generate_campaign_tag(service_id, "reddit", target_lang)
        base_domain = service_data.get("landing_url", "https://k-market.app")
        landing_url = UTMTracker.build_landing_url(
            base_domain=base_domain,
            lang=target_lang,
            path="welcome",
            source="reddit",
            medium="lead_comment",
            campaign=campaign,
            content=subreddit
        )

        # 5. Few-Shot 자가학습 프롬프트 기반 80:20 댓글 생성
        reply_content = self.gemini.generate_reddit_response(
            post_title=title,
            post_body=body,
            service_id=service_id,
            service_data=service_data,
            target_lang="en",
            landing_url=landing_url
        )

        # 6. Anti-Ban 랜덤 지터 딜레이
        if REDDIT_AUTO_REPLY and post_obj:
            delay = random.randint(REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC)
            logger.info(f"[{post_id}] 자연스러운 휴먼 딜레이 대기 ({delay}초)...")
            time.sleep(min(delay, 5)) # 백그라운드 작업 시 적응형 대기
            try:
                post_obj.reply(reply_content)
                logger.info(f"[{post_id}] 레딧 댓글 등록 성공!")
            except Exception as e:
                logger.error(f"레딧 댓글 등록 실패: {e}")
                return False

        # 7. DB 기록 및 Rate Limit 카운트
        hist_id = self.db_mgr.record_history(
            content_type="reddit_reply",
            service_id=service_id,
            target_lang="en",
            title=title,
            content_text=reply_content,
            target_url=landing_url,
            external_id=post_id
        )
        self.db_mgr.record_rate_limit_action(channel_key, "reply")
        logger.info(f"리드 응답 저장 완료 (History ID: {hist_id}) -> {service_id.upper()}")
        return True
