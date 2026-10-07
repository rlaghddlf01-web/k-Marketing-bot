# -*- coding: utf-8 -*-
"""
EasyTaxRedditEngine - 💰 [EasyTax 전용 레딧 외국인 세무·소득세 환급 무인 마케팅 총괄 엔진]
========================================================================================
• 역할:
  - 핵심 서브레딧 대상 100% 무인 실시간 스캔 & 스텔스 댓글 침투 총괄
  - 80:20 스텔스 비율 + Zero URL 스텔스 원칙: 직접 링크 0% + 오직 자연스러운 'Korea Tax Refund Service (KTRS)' 추천
  - RedditSafetyOrchestrator 연동: 업보트 + 피드 스크롤 + 비홍보 댓글 + 홍보 댓글 안전 실행
  - 가시성 검증 (10초 후 댓글 삭제 여부 자동 확인) & 헬스 모니터 연동
  - 24시간 365일 무인 자율 구동 지원
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from config import HOURLY_REDDIT_LIMIT, DAILY_REDDIT_PROMO_LIMIT
from core.db_manager import DBManager
from core.reddit_browser_driver import RedditBrowserDriver
from core.reddit_safety_orchestrator import RedditSafetyOrchestrator
from core.reddit_account_health import AccountHealthMonitor
from brands.easytax.easytax_reddit_scanner import EasyTaxRedditScanner
from brands.easytax.easytax_reddit_copywriter import EasyTaxRedditCopywriter

logger = logging.getLogger("EasyTaxRedditEngine")


class EasyTaxRedditEngine:
    """EasyTax 전용 레딧 무인 마케팅 총괄 엔진"""

    SERVICE_ID = "easytax"
    OFFICIAL_SEARCH_KEYWORD = "Korea Tax Refund Service (KTRS)"
    OFFICIAL_KOREAN_KEYWORD = "KTRS 세금 환급"
    OFFICIAL_LANDING_URL = "https://ktrs-service.vercel.app/"

    def __init__(self, db_mgr: Optional[DBManager] = None, supabase_mgr: Optional[Any] = None, *args, **kwargs):
        self.supabase_mgr = supabase_mgr
        self.db_mgr = db_mgr or DBManager()
        self.driver = RedditBrowserDriver(service_id=self.SERVICE_ID)
        self.health = AccountHealthMonitor(service_id=self.SERVICE_ID)
        self.copywriter = EasyTaxRedditCopywriter()
        self.scanner = EasyTaxRedditScanner(db_mgr=self.db_mgr, driver=self.driver)

        self.orchestrator = RedditSafetyOrchestrator(
            service_id=self.SERVICE_ID,
            db_mgr=self.db_mgr,
            supabase_mgr=None
        )
        self.orchestrator.set_promo_handler(self._execute_single_promo)
        logger.info("💰 [EasyTaxRedditEngine] EasyTax 레딧 전담 무인 엔진 초기화 완료")

    def _execute_single_promo(self, auto_post: bool = True) -> int:
        return self.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=auto_post)

    def run_safe_cycle(self) -> Dict[str, Any]:
        """업보트 + 피드 스크롤 + 비홍보 댓글 + 홍보 댓글 1회 안전 종합 사이클 실행"""
        logger.info("🔄 [EasyTax Reddit] 안전 종합 사이클 가동...")
        return self.orchestrator.run_safe_cycle()

    def scan_and_reply(
        self,
        subreddits: Optional[List[str]] = None,
        limit_per_sub: int = 15,
        max_promo: int = 1,
        auto_post: bool = True
    ) -> int:
        if not self.health.can_post_promo(DAILY_REDDIT_PROMO_LIMIT):
            logger.info("🛡️ [EasyTax Reddit] 일일 안전 한도 도달 또는 쿨다운 상태로 스킵")
            return 0

        leads = self.scanner.scan_target_subreddits(subreddits=subreddits, limit_per_sub=limit_per_sub, max_final_leads=max_promo)
        if not leads:
            logger.info("처리 가능한 신규 EasyTax 타겟 글이 없습니다.")
            return 0

        processed_count = 0
        for lead in leads:
            if processed_count >= max_promo:
                break

            post_id = lead["post_id"]
            title = lead["title"]
            body = lead["body"]
            subreddit = lead["subreddit"]
            post_url = lead["post_url"]
            intent = lead.get("intent", {})

            channel_key = f"reddit_easytax:{subreddit}"
            if not self.db_mgr.can_post_to_channel(channel_key, HOURLY_REDDIT_LIMIT, DAILY_REDDIT_PROMO_LIMIT):
                logger.info(f"[{subreddit}] 채널 안전 한도 초과로 스킵")
                continue

            scenario_id = intent.get("scenario_id", 1)
            reply_content = self.copywriter.generate_reddit_response(
                post_title=title,
                post_body=body,
                subreddit=subreddit,
                target_lang="en",
                scenario_id=scenario_id
            )

            post_success = False
            if auto_post:
                logger.info(f"✍️ [EasyTax Reddit 스텔스 댓글 게시 시도] r/{subreddit}: '{title[:35]}'...")
                comment_res = self.driver.post_comment_humanlike(post_url=post_url, comment_text=reply_content)
                post_success = comment_res.get("verified", False)
                if not post_success:
                    err_msg = comment_res.get('error', 'unknown_error')
                    logger.warning(f"댓글 게시 실패: {err_msg}")
                    self.db_mgr.record_history(
                        content_type="reddit_skipped",
                        service_id=self.SERVICE_ID,
                        target_lang="en",
                        title=f"[SKIPPED:{err_msg}] {title}",
                        content_text=str(err_msg),
                        target_url=post_url,
                        external_id=post_id
                    )
                    continue

                time.sleep(10)
                visible = self.driver.check_comment_visible(post_url, reply_content[:50])
                if not visible:
                    self.health.report_deletion(post_url, reply_content[:100])
                    logger.warning("⚠️ EasyTax 홍보 댓글 삭제 감지! 헬스 모니터에 기록")
            else:
                logger.info(f"🧪 [시뮬레이션 모드 댓글 생성]\n{reply_content}")
                post_success = True

            self.db_mgr.record_history(
                content_type="reddit_reply",
                service_id=self.SERVICE_ID,
                target_lang="en",
                title=f"[{intent.get('category', 'easytax')}] {title}",
                content_text=reply_content,
                target_url=self.OFFICIAL_LANDING_URL,
                external_id=post_id
            )
            self.health.record_promo_comment()
            processed_count += 1
            logger.info(f"✅ [EasyTax Reddit] 성공 처리 완료 (누적 {processed_count}건)")

        return processed_count


# 하위 호환성 별칭
EasyTaxRedditPipeline = EasyTaxRedditEngine
EasyTaxRedditHunter = EasyTaxRedditEngine

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    engine = EasyTaxRedditEngine()
    print("\n" + "=" * 80)
    print("💰 [EasyTax 전용 Reddit 무인 마케팅 엔진 테스트]")
    print("=" * 80)
    res_count = engine.scan_and_reply(limit_per_sub=3, max_promo=1, auto_post=False)
    print(f"\n🎉 테스트 완료: {res_count}건 처리됨")
