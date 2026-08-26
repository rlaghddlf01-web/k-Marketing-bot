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
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxRedditHunter")

TARGET_SUBREDDITS = ["korea", "Living_in_Korea", "teachinginkorea", "Hanguk", "seoul"]
EASYTAX_KEYWORDS = ["tax", "tax refund", "year-end", "3.3%", "withholding", "income tax", "e-9", "d-2", "salary deduction", "article 30", "hometax", "overpaid tax"]

class EasyTaxRedditHunter:
    """
    💰 [EasyTax (KTRS) 전용 Reddit Lead Hunter]
    - r/korea, r/Living_in_Korea 등에서 '세금 환급', '연말정산', '3.3% 알바 세금' 질문 실시간 감지
    - 조세특례제한법 제30조 팩트 법률 답변 80% + EasyTax 100% 무료 시뮬레이션 안내 20% (Anti-Ban 공인 면책)
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        self.reddit = None
        self._init_reddit()

    def _init_reddit(self):
        client_id = os.getenv("EASYTAX_REDDIT_CLIENT_ID") or REDDIT_CLIENT_ID
        secret = os.getenv("EASYTAX_REDDIT_SECRET") or REDDIT_CLIENT_SECRET
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
                logger.info("EasyTax Reddit PRAW 클라이언트 연동 완료")
            except Exception as e:
                logger.warning(f"EasyTax Reddit 클라이언트 초기화 실패 (시뮬레이션 가동): {e}")
                self.reddit = None

    def scan_and_reply(self, limit: int = 5) -> int:
        """EasyTax 세무/비자 질문 글 실시간 스캔 & 팩트 답변"""
        processed_count = 0

        if self.reddit:
            try:
                for sub_name in TARGET_SUBREDDITS:
                    sub = self.reddit.subreddit(sub_name)
                    for post in sub.new(limit=limit):
                        text = f"{post.title} {post.selftext}".lower()
                        if any(kw in text for kw in EASYTAX_KEYWORDS):
                            if self._process_post(post.id, post.title, post.selftext, sub_name, post_obj=post):
                                processed_count += 1
            except Exception as e:
                logger.error(f"EasyTax 레딧 스캔 에러: {e}")
        else:
            # 안전 시뮬레이션
            sample_posts = [
                {"id": f"tax_sim_{int(time.time())}", "title": "How do D-2 student 3.3% tax refunds work in Korea?", "body": "I worked part-time at a restaurant and 3.3% was deducted. Can I claim this back?", "sub": "Living_in_Korea"}
            ]
            for p in sample_posts:
                if self._process_post(p["id"], p["title"], p["body"], p["sub"]):
                    processed_count += 1

        return processed_count

    def _process_post(self, post_id: str, title: str, body: str, subreddit: str, post_obj: Any = None) -> bool:
        if self.db_mgr.is_already_processed(post_id):
            return False

        channel_key = f"reddit_easytax:{subreddit}"
        if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT):
            return False

        target_lang = "en"
        campaign = UTMTracker.generate_campaign_tag("easytax", f"reddit_{subreddit}", target_lang)
        base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")
        landing_url = UTMTracker.build_service_landing_url(
            service_id="easytax",
            base_domain=base_domain,
            lang=target_lang,
            path="",
            source="reddit",
            medium="tax_advisory_comment",
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
                logger.info(f"💰 [EasyTax Reddit] r/{subreddit} 실계정 세무 팩트 답변 등록 완료!")
            except Exception as e:
                logger.error(f"EasyTax 레딧 답변 등록 실패: {e}")
                return False

        self.db_mgr.record_history(
            content_type="reddit_reply",
            service_id="easytax",
            target_lang="en",
            title=title,
            content_text=reply_content,
            target_url=landing_url,
            external_id=post_id
        )
        return True
