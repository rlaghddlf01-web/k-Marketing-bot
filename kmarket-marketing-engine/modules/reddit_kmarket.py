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
    HOURLY_REDDIT_LIMIT, DAILY_REDDIT_PROMO_LIMIT,
    BASE_URLS
)
from core.db_manager import DBManager
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager
from core.reddit_browser_driver import RedditBrowserDriver
from core.reddit_safety_orchestrator import RedditSafetyOrchestrator
from core.reddit_account_health import AccountHealthMonitor

logger = logging.getLogger("KMarketRedditHunter")

class KMarketRedditHunter:
    """
    🛒 [K-Market 전용 실시간 무인 Reddit Lead Hunter & Safety Orchestrator]
    - 200+ 가구/가전/생필품 매트릭스 + Gemini AI 시맨틱 문맥 인텐트 판별
    - 3단계 간접 홍보 전략 (순수도움 40% / 간접유도 40% / 프로필 20%)
    - RedditSafetyOrchestrator와 연동: 업보트 + 비홍보 댓글 + 홍보 댓글 안전 실행
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.driver = RedditBrowserDriver(service_id="kmarket")
        self.health = AccountHealthMonitor(service_id="kmarket")
        self.orchestrator = RedditSafetyOrchestrator(
            service_id="kmarket",
            db_mgr=self.db_mgr,
            supabase_mgr=self.supabase_mgr
        )
        self.orchestrator.set_promo_handler(self._execute_single_promo)
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

    def _execute_single_promo(self, auto_post: bool = True) -> int:
        """홍보 댓글 1건 안전 실행 (Orchestrator가 호출)"""
        return self.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=auto_post)

    def run_safe_cycle(self) -> Dict[str, Any]:
        """업보트 + 피드 스크롤 + 비홍보 댓글 + 홍보 댓글 1회 안전 종합 사이클 실행"""
        return self.orchestrator.run_safe_cycle()

    def scan_and_reply(self, limit_per_sub: int = 15, max_promo: int = 1, auto_post: bool = True, **kwargs) -> int:
        """
        타깃 서브레딧들의 실시간 글을 무인 스캔하고,
        품목 + AI 문맥 검증을 통과한 글에 3단계 간접 홍보 답변 게시
        """
        if not self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
            logger.info("🛡️ [K-Market] 일일 홍보 한도 초과 또는 쿨다운/워밍업 상태로 스킵")
            return 0

        subreddits = self.keywords_matrix.get("target_subreddits", [
            "Living_in_Korea", "korea", "teachinginkorea", "seoul",
            "StudyInKorea", "movingtokorea", "EPIK", "Yonsei",
            "KoreaUniversity", "SNU", "Busan", "Daegu"
        ])
        logger.info(f"🛒 [K-Market Reddit Hunter] {len(subreddits)}개 커뮤니티 실시간 스캔 가동...")

        live_posts = self.driver.fetch_live_posts(subreddits, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 글이 없어 대기합니다.")
            return 0

        processed_count = 0
        all_flattened_keywords = []
        for cat in ["appliances", "furniture", "household_kitchen", "korean_shopping_platforms", "moving_housing_services", "korean_language_institutes_kli", "foreigner_support_centers", "intent_triggers"]:
            all_flattened_keywords.extend(self.keywords_matrix.get(cat, []))

        for post in live_posts:
            if processed_count >= max_promo:
                break

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
            if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_PROMO_LIMIT):
                logger.info(f"[{subreddit}] 채널 안전 한도 초과로 스킵")
                continue

            # 1단계: 품목/행위 키워드 1차 매칭 검사
            combined_text = f"{title} {body}".lower()
            has_keyword_match = any(kw.lower() in combined_text for kw in all_flattened_keywords)
            if not has_keyword_match:
                continue

            # 2단계: Gemini AI 정밀 시맨틱 인텐트 판별
            intent_res = self.gemini.reddit_engine.classify_kmarket_reddit_intent(title, body)
            if not intent_res.get("is_relevant", False):
                logger.info(f"⏭️ [AI 필터링] 케이마켓 무관 글 스킵: '{title}'")
                continue

            logger.info(f"🎯 [K-Market 타깃 질문 포착!] '{title}' (카테고리: {intent_res.get('category')})")

            # 3단계: 다국어 랜딩 URL
            target_lang = "en"
            base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/{target_lang}"

            # 4단계: 3단계 간접 홍보 답변 생성
            reply_content = self.gemini.reddit_engine.generate_reddit_response(
                post_title=title,
                post_body=body,
                target_lang=target_lang,
                landing_url=landing_url
            )

            # 5단계: 영구 프로필 브라우저 드라이버를 통한 무인 댓글 작성
            post_success = False
            if auto_post:
                logger.info(f"✍️ [K-Market 무인 댓글 게시 시도] '{title}'...")
                comment_res = self.driver.post_comment_humanlike(post_url=post_url, comment_text=reply_content)
                post_success = comment_res.get("success", False)
                if not post_success:
                    logger.warning(f"댓글 게시 실패: {comment_res.get('error')}")
                    continue

                # 6단계: 가시성 검증 (삭제/숨김 여부 체크)
                time.sleep(10)
                visible = self.driver.check_comment_visible(post_url, reply_content[:50])
                if not visible:
                    self.health.report_deletion(post_url, reply_content[:100])
                    logger.warning("⚠️ K-Market 홍보 댓글 삭제 감지! 헬스 모니터에 기록")
            else:
                post_success = True

            # 7단계: SQLite DB 및 헬스 모니터 기록
            self.db_mgr.record_history(
                content_type="reddit_reply",
                service_id="kmarket",
                target_lang=target_lang,
                title=f"[{intent_res.get('category')}] {title}",
                content_text=reply_content,
                target_url=landing_url,
                external_id=post_id
            )
            self.health.record_promo_comment()
            processed_count += 1
            logger.info(f"✅ [K-Market Reddit] 성공 처리 완료 (총 {processed_count}건)")

        return processed_count

if __name__ == "__main__":
    db = DBManager()
    supa = SupabaseManager(db)
    hunter = KMarketRedditHunter(db, supa)
    print("Testing K-Market Reddit Hunter live scan...")
    count = hunter.scan_and_reply(limit_per_sub=3, max_promo=1, auto_post=False)
    print(f"Scan finished. Processed: {count} posts.")
