# -*- coding: utf-8 -*-
"""
EasyTaxRedditScanner - 🔍 [EasyTax 전용 레딧 외국인 세무·환급 2단계 실시간 족집게 스캐너]
========================================================================================
• 역할:
  - 1단계: 순수 파이썬(EasyTaxRedditFilter) 100% 심사 (비용 0원, 0.001초 판별)
    * 50+ 네거티브 블랙리스트(중고물품/이사/데이팅/불법체류/코인도박) 즉시 0회 탈락
    * 4대 화이트리스트(조특법 30조, 3.3% 환급, 5개년 경정청구, 연말정산) 키워드 매칭 및 가중치 채점
    * 상위 1등 알짜 질문글만 엄선하여 2단계로 전달
  - 2단계: 순수 파이썬 인텐트 정밀 심사(EasyTaxRedditCopywriter.classify_easytax_reddit_intent)
  - SQLite DB 중복 검사 및 채널별 안전 Rate Limit 통제
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.db_manager import DBManager
from core.reddit_browser_driver import RedditBrowserDriver
from brands.easytax.easytax_reddit_copywriter import EasyTaxRedditCopywriter

logger = logging.getLogger("EasyTaxRedditScanner")

EASYTAX_TARGET_SUBREDDITS = [
    "teachinginkorea",
    "Living_in_Korea",
    "korea",
    "TEFL",
    "seoul",
    "StudyInKorea",
    "movingtokorea"
]


class EasyTaxRedditFilter:
    """1단계: 순수 파이썬 100% 고정밀 족집게 필터 (제목 + 본문 심층 분석)"""

    NEGATIVE_PATTERNS = [
        r"\b(secondhand|used\s*furniture|bed|mattress|sofa|fridge|microwave|air\s*fryer|monitor|moving\s*sale|damas)\b",
        r"\b(dating|tinder|bumble|hookup|romance|clubbing|nightlife|escort|girlfriend|boyfriend)\b",
        r"\b(illegal\s*work|fake\s*visa|overstay\s*fine|police\s*arrest|court\s*criminal|drug\s*test)\b",
        r"\b(crypto|bitcoin|ethereum|upbit|bithumb|casino|gambling|sports\s*betting)\b",
        r"\b(plastic\s*surgery|rhinoplasty|botox|filler|lasik|dermatology)\b",
        r"\b(restaurant\s*recommendation|street\s*food|itinerary|hotel\s*review|flight\s*ticket)\b"
    ]

    GLOBAL_SUBREDDITS = {"korea", "TEFL"}

    POSITIVE_CLUSTERS = {
        "article_30_sme_reduction": {
            "weight": 40.0,
            "patterns": [
                r"\b(article\s*30|sme\s*tax|small\s*business\s*tax|90%\s*tax|tax\s*reduction|tax\s*exemption)\b",
                r"\b(youth\s*tax\s*reduction|foreign\s*engineer\s*tax|tax\s*treaty|article\s*20)\b"
            ]
        },
        "freelancer_3_3_refund": {
            "weight": 35.0,
            "patterns": [
                r"\b(3\.3%|withholding\s*tax|freelance\s*tax|may\s*tax|comprehensive\s*income\s*tax)\b",
                r"\b(tutoring\s*tax|part-time\s*tax|translation\s*tax|arbeit\s*tax|refund\s*3\.3)\b"
            ]
        },
        "retroactive_5yr_claim": {
            "weight": 35.0,
            "patterns": [
                r"\b(retroactive\s*tax|gyeongjeong|amended\s*tax\s*return|5\s*years?\s*tax|past\s*taxes?)\b",
                r"\b(missed\s*deduction|unclaimed\s*tax|wolse\s*tax\s*credit|rent\s*deduction)\b"
            ]
        },
        "year_end_settlement_expat": {
            "weight": 35.0,
            "patterns": [
                r"\b(year-end\s*tax|yeonmal\s*jeongsan|hometax|tax\s*settlement|tax\s*refund)\b",
                r"\b(income\s*tax\s*korea|taxes?\s*in\s*korea|korean\s*tax|paying\s*taxes?\s*korea)\b",
                r"\b(woncheon\s*jingsu|withholding\s*receipt|leaving\s*korea\s*tax)\b"
            ]
        }
    }

    BODY_BOOSTERS = [
        r"\b(refund|deduction|hometax|paycheck|salary|employer|owe\s*taxes?|get\s*money\s*back)\b",
        r"\b(e-2|e-7|f-4|f-5|f-6|d-2|hagwon|school|academy|foreigner)\b"
    ]

    @classmethod
    def evaluate_post(cls, title: str, body: str = "", subreddit: str = "") -> Dict[str, Any]:
        clean_title = (title or "").strip()
        clean_body = (body or "").strip()
        combined = f"{clean_title} \n {clean_body}".lower()

        if len(clean_title) < 5:
            return {"is_passed": False, "score": 0.0, "reason": "제목 길이 미달"}

        for pattern in cls.NEGATIVE_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return {"is_passed": False, "score": 0.0, "reason": f"블랙리스트 감지: '{match.group(0)}'"}

        sub_lower = (subreddit or "").lower()
        if any(sub_lower == g.lower() for g in cls.GLOBAL_SUBREDDITS):
            k_anchor_pattern = r"\b(korea|korean|seoul|hagwon|epik|tefl\s*korea|한국)\b"
            if not re.search(k_anchor_pattern, combined, re.IGNORECASE):
                return {"is_passed": False, "score": 0.0, "reason": "한국 관련 앵커 부재"}

        total_score = 0.0
        matched_clusters = []
        matched_keywords = []

        for cluster_name, cluster_data in cls.POSITIVE_CLUSTERS.items():
            cluster_matches = []
            for pat in cluster_data["patterns"]:
                match = re.search(pat, combined, re.IGNORECASE)
                if match:
                    cluster_matches.append(match.group(0))

            if cluster_matches:
                matched_clusters.append(cluster_name)
                matched_keywords.extend(cluster_matches)
                total_score += cluster_data["weight"] + (len(cluster_matches) * 5.0)

        if not matched_keywords:
            return {"is_passed": False, "score": 0.0, "reason": "세무 타겟 키워드 0개"}

        if len(clean_body) > 30:
            total_score += 5.0

        for b_pat in cls.BODY_BOOSTERS:
            if re.search(b_pat, combined, re.IGNORECASE):
                total_score += 4.0

        if "?" in clean_title or "?" in clean_body:
            total_score += 5.0

        is_passed = total_score >= 40.0
        return {
            "is_passed": is_passed,
            "score": min(100.0, total_score),
            "matched_cluster": matched_clusters[0] if matched_clusters else None,
            "matched_keywords": matched_keywords,
            "reason": f"합격 ({min(100.0, total_score):.1f}점)" if is_passed else "점수 미달"
        }


class EasyTaxRedditScanner:
    """EasyTax 전용 레딧 2단계 스캐너 (1등 리드만 엄선)"""

    def __init__(self, db_mgr: Optional[DBManager] = None, driver: Optional[RedditBrowserDriver] = None):
        self.db_mgr = db_mgr or DBManager()
        self.driver = driver or RedditBrowserDriver(service_id="easytax")
        self.copywriter = EasyTaxRedditCopywriter()

    def scan_target_subreddits(
        self,
        subreddits: Optional[List[str]] = None,
        limit_per_sub: int = 15,
        max_final_leads: int = 2
    ) -> List[Dict[str, Any]]:
        target_subs = subreddits or EASYTAX_TARGET_SUBREDDITS
        logger.info(f"🔍 [EasyTax Reddit Scanner] {len(target_subs)}개 서브레딧 스캔 시작...")

        live_posts = self.driver.fetch_live_posts(target_subs, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 글이 없습니다.")
            return []

        candidates = []
        for post in live_posts:
            post_id = post.get("id")
            title = post.get("title", "")
            body = post.get("body", "")
            subreddit = post.get("subreddit", "")
            post_url = post.get("url", "")

            if self.db_mgr.is_already_processed(post_id):
                continue

            # 🚨 [신선도 게이트: 7일(168시간) 이내 작성글만 엄격 허용]
            import time
            created_utc = post.get("created_utc")
            if created_utc and (time.time() - float(created_utc)) > (7.0 * 86400.0):
                logger.info(f"⏭️ [7일 초과 탈락] '{title[:30]}' (작성: {(time.time() - float(created_utc)) / 86400.0:.1f}일 전)")
                continue

            eval_res = EasyTaxRedditFilter.evaluate_post(title, body, subreddit=subreddit)
            if not eval_res["is_passed"]:
                continue

            candidates.append({
                "post_id": post_id,
                "title": title,
                "body": body,
                "subreddit": subreddit,
                "post_url": post_url,
                "score": eval_res["score"],
                "eval": eval_res
            })

        if not candidates:
            logger.info("EasyTax 파이썬 1차 심사 통과 글 없음")
            return []

        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:max_final_leads]

        # 2단계: 파이썬 시맨틱 인텐트 및 클러스터 정밀 검증
        qualified_leads = []
        for cand in top_candidates:
            title = cand["title"]
            body = cand["body"]
            subreddit = cand["subreddit"]

            intent_res = self.copywriter.classify_easytax_reddit_intent(title, body)
            if not intent_res.get("is_relevant", False):
                logger.info(f"⏭️ [파이썬 인텐트 탈락] '{title[:35]}' ({intent_res.get('reason', '')})")
                continue

            logger.info(f"🎯 [EasyTax 최종 합격 리드] r/{subreddit}: '{title[:40]}' (카테고리: {intent_res.get('category')}, 시나리오 {intent_res.get('scenario_id')})")
            qualified_leads.append({
                "post_id": cand["post_id"],
                "title": title,
                "body": body,
                "subreddit": subreddit,
                "post_url": cand["post_url"],
                "score": cand["score"],
                "intent": intent_res
            })

        return qualified_leads
