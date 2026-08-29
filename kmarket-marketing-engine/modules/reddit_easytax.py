import os
import sys
import json
import time
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    DATA_DIR,
    REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC,
    HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT,
    BASE_URLS
)
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager
from core.reddit_browser_driver import RedditBrowserDriver

logger = logging.getLogger("EasyTaxRedditHunter")

class EasyTaxRedditHunter:
    """
    💰 [EasyTax (KTRS) 전용 실시간 무인 Reddit Lead Hunter]
    - 조특법 제30조(90% 소득세 감면), D-2 유학생 3.3% 환급, 5개년 소급 경정청구 실시간 질문 감지
    - 레딧 공식 OAuth API + 브라우저 듀얼 엔진으로 100% 안전 발행
    - 80:20 법적 팩트 답변 + 구글 검색 유도형(Search 'EasyTax Korea' on Google) Anti-Ban 탑재
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        # 공용 인증 세션(kmarket_cookies.json) 활용
        self.driver = RedditBrowserDriver(service_id="kmarket")
        self.tax_keywords = [
            "tax", "taxes", "tax refund", "year-end", "year end", "3.3%",
            "withholding", "income tax", "e-9", "e-2", "e-1", "e-7", "d-2", "d-4", "d-10",
            "salary deduction", "article 30", "hometax", "overpaid tax", "pension refund",
            "national pension", "severance", "exemption", "paystub", "nts"
        ]
        self.target_subreddits = [
            "Living_in_Korea", "korea", "teachinginkorea", "StudyinKorea",
            "seoul", "EPIK", "Hanguk", "USFK", "movingtokorea"
        ]

    def scan_and_reply(self, limit_per_sub: int = 15, auto_post: bool = True, **kwargs) -> int:
        """타깃 서브레딧들의 실시간 글을 무인 스캔하고, 세무/비자/환급 질문에 팩트 답변 자동 게시"""
        logger.info(f"💰 [EasyTax Reddit Hunter] {len(self.target_subreddits)}개 외국인/강사/유학생 커뮤니티 실시간 스캔 가동...")

        # 1. 브라우저/API 드라이버로 실시간 최신 글 수집
        live_posts = self.driver.fetch_live_posts(self.target_subreddits, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 세무 질문 글이 없어 대기합니다.")
            return 0

        processed_count = 0

        for post in live_posts:
            post_id = post["id"]
            title = post["title"]
            body = post.get("body", "")
            subreddit = post["subreddit"]
            post_url = post["url"]

            # DB 중복 체크
            if self.db_mgr.is_already_processed(post_id):
                continue

            # 채널별 시간당/일일 안전 한도 체크
            channel_key = f"reddit_easytax:{subreddit}"
            if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT):
                logger.info(f"[{subreddit}] EasyTax 채널 안전 한도 초과로 스킵")
                continue

            # 세무 키워드 1차 매칭 검사
            combined_text = f"{title} {body}".lower()
            has_keyword_match = any(kw.lower() in combined_text for kw in self.tax_keywords)

            if not has_keyword_match:
                continue

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

            # 2단계: Gemini 80:20 법적 팩트 답변 생성 (구글 검색 유도형)
            logger.info(f"💡 [EasyTax 매칭 성공] r/{subreddit} - '{title}'")
            reply_content = self.gemini.generate_reddit_response(
                post_title=title,
                post_body=body,
                target_lang=target_lang,
                landing_url=landing_url
            )

            # 3단계: 댓글 실제 등록 (Dual-Engine: OAuth API 우선 전송)
            post_success = False
            if auto_post:
                logger.info(f"🚀 [EasyTax Reddit 전송 시작] URL: {post_url}")
                res = self.driver.post_comment_humanlike(post_url, reply_content)
                post_success = res.get("success", False)
                if post_success:
                    logger.info(f"🎉 [EasyTax Reddit] r/{subreddit} 실계정 팩트 답변 등록 100% 성공! ({res.get('permalink')})")
                else:
                    logger.warning(f"EasyTax 댓글 등록 실패: {res.get('error')}")

            # 4단계: 성공한 경우에만 DB 기록
            if post_success:
                self.db_mgr.record_history(
                    content_type="reddit_reply",
                    service_id="easytax",
                    target_lang=target_lang,
                    title=title,
                    content_text=reply_content,
                    target_url=landing_url,
                    external_id=post_id
                )
                processed_count += 1

                # 안전 간격 딜레이
                delay = random.randint(REPLY_DELAY_MIN_SEC, REPLY_DELAY_MAX_SEC)
                logger.info(f"⏳ 계정보호 쿨다운: {delay}초 대기...")
                time.sleep(delay)

        return processed_count
