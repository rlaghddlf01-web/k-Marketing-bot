# -*- coding: utf-8 -*-
"""
KMarketRedditCopywriter - 🛒 [K-Market 전용 레딧 외국인 생활·중고마켓 AI 카피라이터]
================================================================================
• 역할:
  - 레딧 내 외국인/유학생/교사들의 생활/중고물품/이사/가전 질문을 실시간 분석
  - 2030 영미권 네이티브 톤앤매너(Gen-Z/Millennial 캐주얼, 공감, 이모지)로 진정성 있는 답변 생성
  - 80:20 스텔스 비율 (80% 구글 검색어 'KTRS Market' 유도 vs 20% 순수 도움)
  - 다중 제미나이 무료키 및 모델 순환 체인 (2.5-flash-lite, flash-lite-latest, flash 등)
  - 🚨 Zero URL 물리적 박멸기: 본문/댓글 내 raw URL 100% 제거 및 구글 검색어 강제 치환
"""

import os
import sys
import re
import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.kmarket.scenarios.reddit_kmarket_scenarios import KMARKET_REDDIT_SCENARIOS

logger = logging.getLogger("KMarketRedditCopywriter")

_PROMO_LEVELS = {
    1: 0.20,  # 순수 도움 (브랜드 0%, 검색어 0개)
    2: 0.80,  # 자연스러운 구글 'KTRS Market' 검색 유도 (노링크)
}

def _choose_promo_level() -> int:
    return 2 if random.random() < 0.80 else 1


class KMarketRedditCopywriter:
    """K-Market 전용 레딧 외국인 생활·중고마켓 AI 카피라이터 & 인텐트 판별기"""

    OFFICIAL_SEARCH_KEYWORD = "KTRS Market"
    OFFICIAL_KOREAN_KEYWORD = "케이티알에스 마켓"
    OFFICIAL_URL = "https://ktrs-market.vercel.app/"

    def __init__(self):
        import config
        candidates = [
            {"name": "KM_KEY", "key": getattr(config, "GEMINI_API_KEY_KMARKET", None)},
            {"name": "DEFAULT_KEY", "key": getattr(config, "GEMINI_API_KEY", None)},
            {"name": "FREE_1", "key": getattr(config, "GEMINI_FREE_KEY_1", None)},
            {"name": "FREE_2", "key": getattr(config, "GEMINI_FREE_KEY_2", None)},
            {"name": "FREE_3", "key": getattr(config, "GEMINI_FREE_KEY_3", None)},
        ]
        free_keys = getattr(config, "GEMINI_FREE_KEYS", [])
        for idx, fk in enumerate(free_keys, 1):
            candidates.append({"name": f"FREE_POOL_{idx}", "key": fk})

        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append({"name": c["name"], "key": k})

        self._active_key_index = 0
        logger.info(f"🛒 [KMarketRedditCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @staticmethod
    def _eradicate_urls(text: str) -> str:
        """모든 형태의 raw URL 및 구글 검색 유도를 완벽 제거하고 자연스러운 문장으로 정제"""
        import re
        text = re.sub(r'\[([^\]]+)\]\((?:https?://|www\.)[^\)]+\)', r"\1", text)
        text = re.sub(r'https?://\S+', "", text)
        text = re.sub(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "", text)
        text = re.sub(r'\b[a-zA-Z0-9-]+\.(?:vercel\.app|app|co\.kr|kr|com|net|org)\b(?:\/\S*)?', "", text)
        # 구글 검색 및 링크 유도 어구 제거
        text = re.sub(r"(?i)\b(?:just\s+)?search\s+['\"]?KTRS Market['\"]?\s+on\s+google\b", "KTRS Market", text)
        text = re.sub(r'(?i)\bon\s+google\b', "", text)
        text = re.sub(r'(?i)\bgoogle\s+it\b', "", text)
        text = text.replace("**KTRS Market**", "KTRS Market").replace("*KTRS Market*", "KTRS Market")
        # 중복 마침표 및 어색한 대시 정리
        text = re.sub(r'\s*\.\s*\.', '.', text)
        text = re.sub(r'\s*—\s*', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def classify_kmarket_reddit_intent(self, post_title: str, post_body: str = "") -> Dict[str, Any]:
        """
        🛒 [K-Market 레딧 100% 순수 파이썬 사전 심사 게이트 (Zero Gemini 호출 원칙)]
        - 1단계: 네거티브 정규식 (비자, 법률, 세무, 코인, 데이팅, 의료 등 탈락)
        - 2단계: 4대 클러스터 포지티브 정규식 매칭 및 카테고리/시나리오ID 자동 확정
        """
        combined = f"{post_title} {post_body}".lower()

        # 1. 네거티브 패턴
        negative_patterns = [
            r"\b(visa\s*extension|e-7|e-9|f-2-7|f-4|d-10|immigration\s*office|alien\s*registration|overstay|deportation|visa\s*run)\b",
            r"\b(tax\s*return|withholding\s*tax|crypto|bitcoin|ethereum|forex|stock\s*trading|nhis\s*bill)\b",
            r"\b(election|court\s*case|lawyer|lawsuit|police\s*report)\b",
            r"\b(hospital\s*emergency|surgery|prescription|psychiatrist|std\s*test)\b",
            r"\b(dating|tinder|bumble|hookup|girlfriend|boyfriend|romance\s*scam|clubbing|escort)\b",
            r"\b(hiring|job\s*opening|salary|wage|hourly\s*rate|tutor\s*needed|employment)\b"
        ]
        has_negative = any(re.search(pat, combined, re.IGNORECASE) for pat in negative_patterns)
        if has_negative:
            logger.info(f"🚫 [K-Market 레딧 파이썬 심사 탈락] 네거티브 키워드 감지: '{post_title[:35]}'")
            return {"is_relevant": False, "category": "negative_filter", "reason": "비관련 주제 (비자/세무/의료/연애/구인)"}

        # 2. 포지티브 클러스터 규칙 (우선순위: 구체적 제품 -> 종합 세일 -> 플랫폼 -> 일반 생활)
        cluster_rules = [
            (
                "used_appliances",
                2,
                r"\b(fridge|refrigerator|washing\s*machine|microwave|air\s*fryer|monitor|screens?|laptop|vacuum|kettle|rice\s*cooker|electronics|appliances|used\s*monitor|damas|moving\s*van)\b"
            ),
            (
                "used_furniture",
                1,
                r"\b(bed|mattress|desk|chair|ikea|furniture|wardrobe|bookshelf|dining\s*table|sofa|couch|cheap\s*furniture|used\s*furniture)\b"
            ),
            (
                "zero_barrier_trade",
                4,
                r"\b(karrot|danggeun|secondhand\s*market|flea\s*market|craigslist\s*seoul|buy\s*used|sell\s*used|second\s*hand|where\s*to\s*buy|where\s*to\s*sell|arc\s*not\s*ready|without\s*arc|english\s*market)\b"
            ),
            (
                "moving_sale_clearance",
                7,
                r"\b(moving\s*out|moving\s*sale|leaving\s*korea|graduating|disposing\s*furniture|waste\s*stickers?|bulk\s*sale|room\s*clearance)\b"
            ),
            (
                "budget_living_essentials",
                6,
                r"\b(heating\s*bill|gas\s*bill|electric\s*blanket|ondol|humidifier|recycling|trash\s*bags?|jongnyangje|waste\s*disposal|sorting\s*garbage|fine\s*for\s*trash|bike|bicycle|scooter)\b"
            ),
            (
                "general_expat_living",
                12,
                r"\b(living\s*in\s*korea|seoul\s*expat|foreign\s*resident|exchange\s*student|settling\s*in\s*korea)\b"
            )
        ]

        for cat_name, scen_id, pat in cluster_rules:
            if re.search(pat, combined, re.IGNORECASE):
                logger.info(f"🎯 [K-Market 레딧 파이썬 심사 통과] '{post_title[:35]}' ➔ {cat_name} (시나리오 {scen_id})")
                return {
                    "is_relevant": True,
                    "category": cat_name,
                    "scenario_id": scen_id,
                    "reason": f"파이썬 {cat_name} 패턴 100% 매칭"
                }

        return {
            "is_relevant": False,
            "category": "no_keyword_match",
            "reason": "K-Market 핵심 타겟 키워드 미매칭"
        }

    def generate_reddit_response(
        self,
        post_title: str,
        post_body: str,
        subreddit: str = "",
        target_lang: str = "en",
        scenario_id: Optional[int] = None,
        promo_level: Optional[int] = None
    ) -> str:
        """K-Market 전용 레딧 80:20 스텔스 영문 답변 생성 (Zero URL 원칙)"""
        promo_level = promo_level if promo_level is not None else _choose_promo_level()
        s_id = scenario_id or random.randint(1, 12)
        scenario_info = KMARKET_REDDIT_SCENARIOS.get(s_id, KMARKET_REDDIT_SCENARIOS[1])

        scenario_context = f"""
[Scenario Theme]: {scenario_info.get('theme_name')}
[Target Pain Points]: {scenario_info.get('pain_points')}
[Solution Feature]: {scenario_info.get('solution_feature')}
[High-Performing Reference Example]:
"{scenario_info.get('sample_reply')}"
"""

        if promo_level == 1:
            promo_instruction = """### TYPE 1 — 100% PURE HELPFUL ADVICE (NO PROMOTION, NO SEARCH SUGGESTIONS):
1. DO NOT mention ANY brand, app name, search keyword, or website.
2. Provide genuinely helpful, warm, and practical tips for saving money on used furniture, handling Korean waste disposal, or finding budget living setups.
3. Write like a friendly foreign peer/student who has lived in Seoul for years.
4. Keep it casual, empathetic, and 100% non-commercial."""
        else:
            promo_instruction = f"""### TYPE 2 — 100% NATURAL PEER EXPERIENCE (ZERO PROMOTION, ZERO GOOGLE MENTIONS, ZERO URLS):
1. Provide 80% warm, practical, and empathetic advice tailored to OP's question first (furniture tips, student hacks, disposal rules in Seoul).
2. At the very end of your response, mention '{self.OFFICIAL_SEARCH_KEYWORD}' ONLY as a casual past personal experience like a fellow international resident:
   - Example style: "When I lived in Sinchon, I used {self.OFFICIAL_SEARCH_KEYWORD} and it was super convenient because it was multilingual and didn't need complicated Korean verification."
   - Example style: "I actually used {self.OFFICIAL_SEARCH_KEYWORD} when setting up my one-room near campus, got a desk and chair pretty cheap from graduating students."
3. 🚨 CRITICAL NEGATIVE CONSTRAINTS (VIOLATIONS TRIGGER INSTANT SPAM BAN):
   - NEVER use the word "Google" or "search on Google" or "Google it".
   - NEVER use command phrases like "Check out", "Visit", "Go to", or "Download".
   - NEVER include any URLs, domains, or web links.
   - ONLY mention it naturally as a tool/community you personally used in Korea."""

        prompt = f"""You are a helpful, culturally savvy international resident who has lived in Seoul, Korea for years, answering another foreigner's post on Reddit (in r/{subreddit or 'Living_in_Korea'}).

{scenario_context}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL STYLE GUIDELINES:
1. Tone: Friendly, natural, casual native English forum comment. Do NOT use spammy marketing emojis or bullet lists.
2. Length: Exactly 2 to 4 sentences. Extremely concise, authentic, and direct.
3. NEVER use formal corporate marketing jargon, features lists, or commercial pitches. Write like an actual international student or expat sharing their own lived experience.
4. Output ONLY the comment text directly, without any introduction or markdown code blocks.
"""

        total_keys = len(self.key_chain)
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            api_key = key_info["key"]

            try:
                client = self._get_genai_client(api_key)
                for model_name in ['gemini-2.5-flash-lite', 'gemini-flash-lite-latest', 'gemini-3.1-flash-lite', 'gemini-flash-latest', 'gemini-2.5-flash']:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if resp and resp.text:
                            text = resp.text.strip()
                            clean_text = self._eradicate_urls(text)
                            self._active_key_index = idx
                            logger.info(f"✍️ [K-Market Reddit 댓글 생성 성공] (Key: {key_info['name']}, Model: {model_name}, Promo Level: {promo_level})")
                            return clean_text
                    except Exception as model_err:
                        logger.debug(f"댓글 생성 모델 {model_name} 실패: {model_err}")
                        continue
            except Exception as key_err:
                logger.warning(f"키 {key_info['name']} 오류: {key_err}")
                continue

        fallback = scenario_info.get("sample_reply", "")
        return self._eradicate_urls(fallback)
