import os
import re
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
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager
from core.reddit_browser_driver import RedditBrowserDriver
from core.reddit_safety_orchestrator import RedditSafetyOrchestrator
from core.reddit_account_health import AccountHealthMonitor

logger = logging.getLogger("EasyTaxRedditHunter")

class EasyTaxRedditHunter:
    """
    💰 [EasyTax (KTRS) 전용 실시간 무인 Reddit Lead Hunter & Safety Orchestrator]
    - 조특법 제30조(90% 소득세 감면), D-2 유학생 3.3% 환급, 5개년 소급 경정청구 실시간 질문 감지
    - 3단계 간접 팩트 답변 전략 (순수팩트 40% / 간접유도 40% / 프로필 20%)
    - RedditSafetyOrchestrator와 연동: EasyTax 독립 계정 세션으로 업보트 + 비홍보 댓글 + 홍보 댓글 안전 실행
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        # 🔑 EasyTax 전용 독립 브라우저 세션 & 계정 건강 관리자
        self.driver = RedditBrowserDriver(service_id="easytax")
        self.health = AccountHealthMonitor(service_id="easytax")
        self.orchestrator = RedditSafetyOrchestrator(
            service_id="easytax",
            db_mgr=self.db_mgr,
            supabase_mgr=self.supabase_mgr
        )
        self.orchestrator.set_promo_handler(self._execute_single_promo)
        self.strong_tax_phrases = [
            "tax refund", "tax return", "income tax", "withholding tax",
            "year-end", "year end", "article 30", "hometax", "pension refund",
            "national pension", "salary deduction", "paystub", "nts", "3.3%",
            "종합소득세", "연말정산", "경정청구", "세무서", "overpaid tax"
        ]
        self.negative_patterns = [
            r"\btaxi\b", r"\btaxicab\b", r"\bsyntax\b", r"\btaxidermy\b", r"\btaxonomy\b"
        ]
        self.tax_regex_patterns = [
            r"\btax\b", r"\btaxes\b", r"\b3\.3%?\b"
        ]
        self.target_subreddits = [
            "Living_in_Korea", "korea", "teachinginkorea", "StudyinKorea",
            "seoul", "EPIK", "Hanguk", "USFK", "movingtokorea"
        ]

    def _execute_single_promo(self, auto_post: bool = True) -> int:
        """홍보 댓글 1건 안전 실행 (Orchestrator가 호출)"""
        return self.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=auto_post)

    def run_safe_cycle(self) -> Dict[str, Any]:
        """EasyTax 독립 세션: 업보트 + 피드 스크롤 + 비홍보 댓글 + 홍보 댓글 1회 안전 종합 사이클 실행"""
        return self.orchestrator.run_safe_cycle()

    def scan_and_reply(self, limit_per_sub: int = 15, max_promo: int = 1, auto_post: bool = True, **kwargs) -> int:
        """타깃 서브레딧들의 실시간 글을 무인 스캔하고, 세무/비자/환급 질문에 100% 맞춤 팩트 + 구글 검색 유도 댓글 게시"""
        if not self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
            logger.info("🛡️ [EasyTax] 일일 안전 한도 초과 또는 쿨다운 상태로 스킵")
            return 0

        logger.info(f"💰 [EasyTax Reddit Hunter] {len(self.target_subreddits)}개 외국인/강사/유학생 커뮤니티 실시간 스캔 가동...")

        # 1. EasyTax 독립 브라우저 드라이버로 실시간 최신 글 수집
        live_posts = self.driver.fetch_live_posts(self.target_subreddits, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 세무 질문 글이 없어 대기합니다.")
            return 0

        processed_count = 0

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

            # 채널별 시간당/일일 안전 한도 체크
            channel_key = f"reddit_easytax:{subreddit}"
            if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_PROMO_LIMIT):
                logger.info(f"[{subreddit}] EasyTax 채널 안전 한도 초과로 스킵")
                continue

            # 1단계: 세무 키워드 1차 매칭 검사 (단어 경계 \b 및 네거티브 필터링 적용)
            combined_text = f"{title} {body}".lower()
            has_strong_tax = any(p in combined_text for p in self.strong_tax_phrases)
            if not has_strong_tax:
                # 확실한 세무 복합어가 없는 상태에서 taxi, cab, syntax 등 네거티브 단어가 있으면 즉시 스킵
                if any(re.search(neg, combined_text, re.IGNORECASE) for neg in self.negative_patterns):
                    continue
                # 단독 tax/taxes 단어 경계 검사
                has_tax_token = any(re.search(pat, combined_text, re.IGNORECASE) for pat in self.tax_regex_patterns)
                if not has_tax_token:
                    continue

            # 2단계: Gemini AI 정밀 시맨틱 인텐트 판별 (영화/생활 질문 오인 방지)
            intent_res = self.gemini.reddit_engine.classify_easytax_reddit_intent(title, body)
            if not intent_res.get("is_relevant", False):
                logger.info(f"⏭️ [AI 필터링] EasyTax 세무 무관 글 스킵: '{title}' (사유: {intent_res.get('reason', '무관')})")
                continue

            logger.info(f"🎯 [EasyTax 세무 타깃 질문 포착!] r/{subreddit} - '{title}' (카테고리: {intent_res.get('category')})")

            target_lang = "en"
            base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/?lang={target_lang}"

            # 3단계: Gemini 3단계 간접 홍보 법적 팩트 답변 생성
            reply_content = self.gemini.reddit_engine.generate_reddit_response(
                post_title=title,
                post_body=body,
                target_lang=target_lang,
                landing_url=landing_url
            )


            # 3단계: 영구 프로필 브라우저 드라이버를 통한 무인 댓글 작성
            post_success = False
            if auto_post:
                logger.info(f"🚀 [EasyTax Reddit 전송 시작] URL: {post_url}")
                res = self.driver.post_comment_humanlike(post_url, reply_content)
                post_success = res.get("success", False)
                if post_success:
                    logger.info(f"🎉 [EasyTax Reddit] r/{subreddit} 실계정 팩트 답변 등록 성공!")
                    # 4단계: 가시성 검증 (삭제/숨김 여부 체크)
                    time.sleep(10)
                    visible = self.driver.check_comment_visible(post_url, reply_content[:50])
                    if not visible:
                        self.health.report_deletion(post_url, reply_content[:100])
                        logger.warning("⚠️ EasyTax 홍보 댓글 삭제 감지! 헬스 모니터에 기록")
                else:
                    logger.warning(f"EasyTax 댓글 등록 실패: {res.get('error')}")
                    continue
            else:
                post_success = True

            # 5단계: 성공한 경우에만 DB 및 헬스 모니터 기록
            self.db_mgr.record_history(
                content_type="reddit_reply",
                service_id="easytax",
                target_lang=target_lang,
                title=title,
                content_text=reply_content,
                target_url=landing_url,
                external_id=post_id
            )
            self.health.record_promo_comment()
            processed_count += 1
            logger.info(f"✅ [EasyTax Reddit] 성공 처리 완료 (총 {processed_count}건)")

        return processed_count

if __name__ == "__main__":
    db = DBManager()
    supa = SupabaseManager(db)
    hunter = EasyTaxRedditHunter(db, supa)
    print("Testing EasyTax Reddit Hunter live scan...")
    count = hunter.scan_and_reply(limit_per_sub=3, max_promo=1, auto_post=False)
    print(f"Scan finished. Processed: {count} posts.")
