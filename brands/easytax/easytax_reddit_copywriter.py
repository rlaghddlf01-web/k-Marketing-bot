# -*- coding: utf-8 -*-
"""
EasyTaxRedditCopywriter - 💰 [EasyTax 전용 레딧 외국인 세무·소득세 환급 AI 카피라이터]
================================================================================
• 역할:
  - 레딧 내 외국인 원어민강사, 직장인, 프리랜서, 유학생의 세무/환급/홈택스 질문 실시간 분석
  - 팩트 기반 세무 조언 + 안심 톤앤매너로 신뢰성 높은 답변 생성
  - 80:20 스텔스 비율 (80% 구글 검색어 'Korea Tax Refund Service (KTRS)' 유도 vs 20% 순수 도움)
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

from brands.easytax.scenarios.reddit_easytax_scenarios import EASYTAX_REDDIT_SCENARIOS

logger = logging.getLogger("EasyTaxRedditCopywriter")

_PROMO_LEVELS = {
    1: 0.20,  # 순수 도움 (브랜드 0%, 검색어 0개)
    2: 0.80,  # 자연스러운 구글 'Korea Tax Refund Service (KTRS)' 검색 유도 (노링크)
}

def _choose_promo_level() -> int:
    return 2 if random.random() < 0.80 else 1


class EasyTaxRedditCopywriter:
    """EasyTax 전용 레딧 외국인 세무 AI 카피라이터 & 인텐트 판별기"""

    OFFICIAL_SEARCH_KEYWORD = "Korea Tax Refund Service (KTRS)"
    OFFICIAL_KOREAN_KEYWORD = "KTRS 세금 환급"
    OFFICIAL_URL = "https://ktrs-service.vercel.app/"

    def __init__(self):
        import config
        candidates = [
            {"name": "ET_KEY", "key": getattr(config, "GEMINI_API_KEY_EASYTAX", None)},
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
        logger.info(f"💰 [EasyTaxRedditCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

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
        text = re.sub(r"(?i)\b(?:just\s+)?search\s+['\"]?Korea Tax Refund Service (KTRS)['\"]?\s+on\s+google\b", "Korea Tax Refund Service (KTRS)", text)
        text = re.sub(r'(?i)\bon\s+google\b', "", text)
        text = re.sub(r'(?i)\bgoogle\s+it\b', "", text)
        text = text.replace("**Korea Tax Refund Service (KTRS)**", "Korea Tax Refund Service (KTRS)").replace("*Korea Tax Refund Service (KTRS)*", "Korea Tax Refund Service (KTRS)")
        # 중복 마침표 및 어색한 대시 정리
        text = re.sub(r'\s*\.\s*\.', '.', text)
        text = re.sub(r'\s*—\s*', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def classify_easytax_reddit_intent(self, post_title: str, post_body: str = "") -> Dict[str, Any]:
        """
        💰 [EasyTax 레딧 100% 순수 파이썬 사전 심사 게이트 (Zero Gemini 호출 원칙)]
        - 1단계: 네거티브 정규식 (중고물품, 이사, 데이팅, 불법체류, 코인, 의료, 관광 등 탈락)
        - 2단계: 4대 세무 클러스터 포지티브 정규식 매칭 및 카테고리/시나리오ID 자동 확정
        """
        combined = f"{post_title} {post_body}".lower()

        negative_patterns = [
            r"\b(secondhand|used\s*furniture|bed|mattress|sofa|fridge|microwave|air\s*fryer|monitor|moving\s*sale|damas)\b",
            r"\b(dating|tinder|bumble|hookup|romance|clubbing|nightlife|escort|girlfriend|boyfriend)\b",
            r"\b(illegal\s*work|fake\s*visa|overstay\s*fine|police\s*arrest|court\s*criminal|drug\s*test)\b",
            r"\b(crypto|bitcoin|ethereum|upbit|bithumb|casino|gambling|sports\s*betting)\b",
            r"\b(plastic\s*surgery|rhinoplasty|botox|filler|lasik|dermatology)\b",
            r"\b(restaurant\s*recommendation|street\s*food|itinerary|hotel\s*review|flight\s*ticket)\b"
        ]
        has_negative = any(re.search(pat, combined, re.IGNORECASE) for pat in negative_patterns)
        if has_negative:
            logger.info(f"🚫 [EasyTax 레딧 파이썬 심사 탈락] 네거티브 키워드 감지: '{post_title[:35]}'")
            return {"is_relevant": False, "category": "negative_filter", "reason": "비관련 주제 (중고/연애/불법/코인/의료/관광)"}

        cluster_rules = [
            (
                "article_30_sme_reduction",
                1,
                r"\b(article\s*30|sme\s*tax|small\s*business\s*tax|90%\s*tax|tax\s*reduction|tax\s*exemption|youth\s*tax\s*reduction|foreign\s*engineer\s*tax|tax\s*treaty|article\s*20)\b"
            ),
            (
                "freelancer_3_3_refund",
                2,
                r"\b(3\.3%|withholding\s*tax|freelance\s*tax|may\s*tax|comprehensive\s*income\s*tax|tutoring\s*tax|part-time\s*tax|translation\s*tax|arbeit\s*tax|refund\s*3\.3)\b"
            ),
            (
                "retroactive_5yr_claim",
                3,
                r"\b(retroactive\s*tax|gyeongjeong|amended\s*tax\s*return|5\s*years?\s*tax|past\s*taxes?|missed\s*deduction|unclaimed\s*tax|wolse\s*tax\s*credit|rent\s*deduction)\b"
            ),
            (
                "year_end_settlement_expat",
                4,
                r"\b(year-end\s*tax|yeonmal\s*jeongsan|hometax|tax\s*settlement|tax\s*refund|income\s*tax\s*korea|taxes?\s*in\s*korea|korean\s*tax|paying\s*taxes?\s*korea|woncheon\s*jingsu|withholding\s*receipt|leaving\s*korea\s*tax)\b"
            ),
            (
                "general_expat_tax",
                12,
                r"\b(expat\s*tax|foreign\s*worker\s*tax|teachinginkorea\s*tax|e-2\s*tax|e-7\s*tax|f-4\s*tax)\b"
            )
        ]

        for cat_name, scen_id, pat in cluster_rules:
            if re.search(pat, combined, re.IGNORECASE):
                logger.info(f"🎯 [EasyTax 레딧 파이썬 심사 통과] '{post_title[:35]}' ➔ {cat_name} (시나리오 {scen_id})")
                return {
                    "is_relevant": True,
                    "category": cat_name,
                    "scenario_id": scen_id,
                    "reason": f"파이썬 {cat_name} 패턴 100% 매칭"
                }

        return {
            "is_relevant": False,
            "category": "no_keyword_match",
            "reason": "EasyTax 핵심 타겟 키워드 미매칭"
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
        """EasyTax 전용 레딧 80:20 스텔스 영문 답변 생성 (Zero URL 원칙)"""
        promo_level = promo_level if promo_level is not None else _choose_promo_level()
        s_id = scenario_id or random.randint(1, 12)
        scenario_info = EASYTAX_REDDIT_SCENARIOS.get(s_id, EASYTAX_REDDIT_SCENARIOS[1])

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
2. Provide genuinely helpful, accurate, and reassuring factual tax advice (how Korean tax brackets work, Article 30 requirements, or Hometax basics).
3. Write like a knowledgeable foreign expat peer or tax mentor in Korea.
4. Keep it clear, professional, and 100% non-commercial."""
        else:
            promo_instruction = f"""### TYPE 2 — 100% NATURAL PEER EXPERIENCE (ZERO PROMOTION, ZERO GOOGLE MENTIONS, ZERO URLS):
1. Provide 80% accurate, reassuring, and factual tax advice tailored to OP's question first (year-end tax rules, 3.3% refund, medical/housing deductions in Korea).
2. At the very end of your response, mention '{self.OFFICIAL_SEARCH_KEYWORD}' ONLY as a casual past personal experience like a fellow foreigner living in Korea:
   - Example style: "When I did my taxes last year, I used {self.OFFICIAL_SEARCH_KEYWORD} and it was really convenient because it gave a clear breakdown in English without dealing with Korean certs."
   - Example style: "I used {self.OFFICIAL_SEARCH_KEYWORD} when calculating my freelance withholding refund in English before submitting documents to HR, saved me a bunch of headache."
3. 🚨 CRITICAL NEGATIVE CONSTRAINTS (VIOLATIONS TRIGGER INSTANT SPAM BAN):
   - NEVER use the word "Google" or "search on Google" or "Google it".
   - NEVER use command phrases like "Check out", "Visit", "Go to", or "Download".
   - NEVER include any URLs, domains, or web links.
   - ONLY mention it naturally as a service/calculator you personally used in Korea."""

        prompt = f"""You are a knowledgeable expat tax specialist and long-time foreign resident in Korea, answering a tax/income question on Reddit (in r/{subreddit or 'teachinginkorea'}).

{scenario_context}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL STYLE GUIDELINES:
1. Tone: Reassuring, clear, peer-to-peer expat forum comment. Do NOT use spammy marketing emojis or bullet lists.
2. Length: Exactly 2 to 4 sentences. Extremely concise, authentic, and direct.
3. NEVER use formal corporate marketing jargon, features lists, or commercial pitches. Write like an actual expat worker sharing their own experience with Korean taxes.
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
                            logger.info(f"✍️ [EasyTax Reddit 댓글 생성 성공] (Key: {key_info['name']}, Model: {model_name}, Promo Level: {promo_level})")
                            return clean_text
                    except Exception as model_err:
                        logger.debug(f"댓글 생성 모델 {model_name} 실패: {model_err}")
                        continue
            except Exception as key_err:
                logger.warning(f"키 {key_info['name']} 오류: {key_err}")
                continue

        fallback = scenario_info.get("sample_reply", "")
        return self._eradicate_urls(fallback)
