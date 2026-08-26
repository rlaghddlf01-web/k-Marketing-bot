import time
import random
import logging
from typing import List, Dict, Any
import os
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT, REDDIT_USERNAME, REDDIT_PASSWORD,
    REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC,
    HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT,
    BASE_URLS
)
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketRedditHunter")

TARGET_SUBREDDITS = ["korea", "Living_in_Korea", "teachinginkorea", "Hanguk", "seoul"]
KMARKET_KEYWORDS = ["furniture", "desk", "bed", "moving sale", "giveaway", "free stuff", "fridge", "used", "secondhand", "appliance", "roommate", "studio", "leaving korea"]

class KMarketRedditHunter:
    """
    🛒 [K-Market 전용 Reddit Lead Hunter]
    - r/korea, r/Living_in_Korea 등에서 '중고 가구', '무빙세일', '0원 무료나눔' 질문 실시간 감지
    - 80% 지역별 꿀팁 답변 + 20% K-Market 0원 나눔/17개국 번역 채팅 자연스러운 안내
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self):
        client_id = os.getenv("KMARKET_REDDIT_CLIENT_ID") or REDDIT_CLIENT_ID
        secret = os.getenv("KMARKET_REDDIT_SECRET") or REDDIT_CLIENT_SECRET
        if client_id and secret:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=secret,
                    user_agent=REDDIT_USER_AGENT,
                    username=REDDIT_USERNAME,
                    password=REDDIT_PASSWORD
                )
                logger.info("K-Market Reddit PRAW 클라이언트 연동 완료")
            except Exception as e:
                logger.warning(f"K-Market Reddit 클라이언트 초기화 실패 (시뮬레이션 가동): {e}")
                self.reddit = None

    def scan_and_reply(self, limit: int = 5) -> int:
        """K-Market 중고/가구 질문 글 실시간 스캔 & 답변"""
        processed_count = 0

        if self.reddit:
            try:
                for sub_name in TARGET_SUBREDDITS:
                    sub = self.reddit.subreddit(sub_name)
                    for post in sub.new(limit=limit):
                        text = f"{post.title} {post.selftext}".lower()
                        if any(kw in text for kw in KMARKET_KEYWORDS):
                            if self._process_post(post.id, post.title, post.selftext, sub_name, post_obj=post):
                                processed_count += 1
            except Exception as e:
                logger.error(f"K-Market 레딧 스캔 에러: {e}")
        else:
            # 안전 시뮬레이션
            sample_posts = [
                {"id": f"km_sim_{int(time.time())}", "title": "Moving out of Sinchon studio, where to get free desk/bed?", "body": "Looking for affordable secondhand furniture near Yonsei.", "sub": "Living_in_Korea"}
            ]
            for p in sample_posts:
                if self._process_post(p["id"], p["title"], p["body"], p["sub"]):
                    processed_count += 1

        return processed_count

    def _process_post(self, post_id: str, title: str, body: str, subreddit: str, post_obj: Any = None) -> bool:
        if self.db_mgr.is_already_processed(post_id):
            return False

        channel_key = f"reddit_kmarket:{subreddit}"
        if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT):
            return False

        target_lang = "en"
        campaign = UTMTracker.generate_campaign_tag("kmarket", f"reddit_{subreddit}", target_lang)
        base_domain = BASE_URLS.get("kmarket", "https://k-market.app")
        landing_url = UTMTracker.build_landing_url(
            base_domain=base_domain,
            lang=target_lang,
            path="welcome",
            source="reddit",
            medium="community_comment",
            campaign=campaign
        )

        reply_content = self.gemini.generate_reddit_response(
            post_title=title,
            post_body=body,
            target_lang=target_lang,
            landing_url=landing_url
        )

        if post_obj:
            try:
                delay = random.randint(REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC)
                time.sleep(delay)
                post_obj.reply(reply_content)
                logger.info(f"🛒 [K-Market Reddit] r/{subreddit} 실계정 답변 등록 완료!")
            except Exception as e:
                logger.error(f"K-Market 레딧 답변 등록 실패: {e}")
                return False

        self.db_mgr.record_history(
            content_type="reddit_reply",
            service_id="kmarket",
            target_lang="en",
            title=title,
            content_text=reply_content,
            target_url=landing_url,
            external_id=post_id
        )
        return True
