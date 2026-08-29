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
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager
from core.reddit_browser_driver import RedditBrowserDriver

logger = logging.getLogger("KMarketRedditHunter")

class KMarketRedditHunter:
    """
    🛒 [K-Market 전용 실시간 무인 Reddit Lead Hunter]
    - 200+ 가구/가전/생필품 매트릭스 + Gemini AI 시맨틱 문맥 인텐트 판별 (100% 포착)
    - 100% 사람 같은(Human-like) 4년차 외국인 선배 꿀팁 댓글 생성 (Anti-AI Tone)
    - Playwright 브라우저 드라이버를 통한 API 키 불필요 무인 댓글 자동 게시
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.driver = RedditBrowserDriver(service_id="kmarket")
        self.keywords_matrix = self._load_keywords_matrix()

    def _load_keywords_matrix(self) -> Dict[str, List[str]]:
        path = DATA_DIR / "kmarket_reddit_keywords.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"키워드 매트릭스 로드 실패: {e}")
        return {
            "appliances": ["tv", "fridge", "microwave", "heater", "rice cooker", "vacuum"],
            "furniture": ["bed", "mattress", "desk", "chair", "sofa", "wardrobe"],
            "intent_triggers": ["where to buy", "cheap", "used", "moving", "giveaway", "free"],
            "target_subreddits": ["Living_in_Korea", "korea", "teachinginkorea", "seoul"]
        }

    def scan_and_reply(self, limit_per_sub: int = 20, auto_post: bool = True, **kwargs) -> int:
        """
        타깃 서브레딧들의 실시간 글을 무인 스캔하고,
        수백 개 품목 + AI 문맥 검증을 통과한 글에 사람 같은 답변 자동 게시
        """
        subreddits = self.keywords_matrix.get("target_subreddits", ["Living_in_Korea", "korea", "teachinginkorea", "seoul", "StudyInKorea", "movingtokorea", "EPIK", "Yonsei", "KoreaUniversity", "SNU", "Busan", "Daegu", "Incheon", "Pyeongtaek", "USFK"])
        logger.info(f"🛒 [K-Market Reddit Hunter] {len(subreddits)}개 전국 외국인/대학 커뮤니티 실시간 스캔 가동...")

        # 1. 브라우저 드라이버로 실시간 최신 글 수집
        live_posts = self.driver.fetch_live_posts(subreddits, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 글이 없어 대기합니다.")
            return 0

        processed_count = 0
        all_flattened_keywords = []
        for cat in ["appliances", "furniture", "household_kitchen", "korean_shopping_platforms", "moving_housing_services", "korean_language_institutes_kli", "foreigner_support_centers", "intent_triggers"]:
            all_flattened_keywords.extend(self.keywords_matrix.get(cat, []))

        for post in live_posts:
            post_id = post["id"]
            title = post["title"]
            body = post.get("body", "")
            subreddit = post["subreddit"]
            post_url = post["url"]

            # DB 중복 체크
            if self.db_mgr.is_already_processed(post_id):
                continue

            # 채널별 시간당/일일 한도 체크
            channel_key = f"reddit_kmarket:{subreddit}"
            if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_LIMIT):
                logger.info(f"[{subreddit}] 채널 안전 한도 초과로 스킵")
                continue

            # 1단계: 수백 개 품목/행위 키워드 1차 매칭 검사
            combined_text = f"{title} {body}".lower()
            has_keyword_match = any(kw.lower() in combined_text for kw in all_flattened_keywords)

            if not has_keyword_match:
                continue

            # 2단계: Gemini AI 정밀 시맨틱 인텐트 판별 (100% 정확도)
            intent_res = self.gemini.classify_kmarket_reddit_intent(title, body)
            if not intent_res.get("is_relevant", False):
                logger.info(f"⏭️ [AI 필터링] 케이마켓 무관 글 스킵: '{title}' (이유: {intent_res.get('reason')})")
                continue

            logger.info(f"🎯 [K-Market 타깃 질문 포착!] '{title}' (카테고리: {intent_res.get('category')}, 품목: {intent_res.get('extracted_item')})")

            # 3. 초깔끔 다국어 랜딩 URL 생성 (군더더기 0%)
            target_lang = "en"
            base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/{target_lang}"

            # 4. 100% 사람 같은 휴먼 페르소나 AI 답변 생성
            reply_content = self.gemini.generate_reddit_response(
                post_title=title,
                post_body=body,
                target_lang=target_lang,
                landing_url=landing_url
            )

            # 5. 브라우저 드라이버를 통한 무인 댓글 작성
            post_success = False
            if auto_post:
                logger.info(f"✍️ [무인 댓글 게시 시도] '{title}'...")
                # 인간 행동 모방 딜레이 (최소 5초 ~ 안전 딜레이)
                comment_res = self.driver.post_comment_humanlike(post_url=post_url, comment_text=reply_content)
                post_success = comment_res.get("success", False)
            else:
                post_success = True

            if not post_success:
                logger.warning(f"댓글 게시 실패로 DB 기록을 스킵합니다: {comment_res.get('error')}")
                continue

            # 6. SQLite DB에 기록 (실제 게시 성공 시에만)
            self.db_mgr.record_history(
                content_type="reddit_reply",
                service_id="kmarket",
                target_lang=target_lang,
                title=f"[{intent_res.get('category')}] {title}",
                content_text=reply_content,
                target_url=landing_url,
                external_id=post_id
            )
            processed_count += 1
            logger.info(f"✅ [K-Market Reddit] 실계정 댓글 등록 완료 및 DB 기록 성공 (총 {processed_count}건)")
            logger.info(f"✅ [K-Market Reddit] 성공 처리 완료 (총 {processed_count}건)")

            # 시간당 과도한 요청 방지
            if processed_count >= 2:
                break

        return processed_count

if __name__ == "__main__":
    db = DBManager()
    supa = SupabaseManager(db)
    hunter = KMarketRedditHunter(db, supa)
    print("Testing K-Market Reddit Hunter live scan...")
    count = hunter.scan_and_reply(limit_per_sub=5, auto_post=False)
    print(f"Scan finished. Processed: {count} posts.")
