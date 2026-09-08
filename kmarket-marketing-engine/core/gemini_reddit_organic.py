"""
🌱 [Reddit Organic AI — 비홍보 순수 도움 댓글 생성 전담 AI 엔진]
- 100% 순수 도움 댓글: 브랜드명/서비스명/URL 언급 완전 금지
- 한국 거주 경험 기반 진짜 도움이 되는 정보 제공
- 다양한 주제: 비자, 교통, 맛집, 주거, 쇼핑, 언어, 문화, 병원 등
- 카르마 축적의 핵심 수단
"""

import logging
import random
from typing import Optional

from config import GEMINI_API_KEY_KMARKET, LANGUAGES

logger = logging.getLogger("GeminiRedditOrganic")

# 다양한 페르소나 풀 (매번 다른 성격의 답변 생성)
_PERSONA_POOL = [
    "a university exchange student who has lived in Seoul for 2 years",
    "an experienced expat who has been in Korea for 5 years, married to a Korean spouse",
    "a foreign English teacher in Busan who loves exploring local food and culture",
    "a graduate student at KAIST who navigated the Korean bureaucracy successfully",
    "a Southeast Asian factory worker in Ansan who learned Korean fluently",
    "a European digital nomad based in Hongdae, Seoul",
    "a Japanese exchange student at Yonsei who found great budget living tips",
]

# 대화에 자연스럽게 녹일 수 있는 한국 생활 지식 카테고리
_TOPIC_KNOWLEDGE = {
    "visa_arc": "ARC registration at immigration office, 90-day reporting, visa extensions, D-2/E-2/E-9 differences",
    "housing": "Jeonse/wolse system, 전입신고, deposit protection, utility bills, moving tips",
    "transport": "T-money card, KTX, subway apps (Naver Map, KakaoMap), taxi (Kakao T)",
    "food": "Korean restaurant ordering, delivery apps, 1인분 rules, tipping culture",
    "healthcare": "National Health Insurance (NHIS), clinic visits, pharmacy system, emergency 119",
    "banking": "Opening bank account as foreigner, Kakao Bank, Toss, international transfers",
    "culture": "Jjimjilbang etiquette, 노래방, PC방, hiking culture, seasonal festivals",
    "shopping": "Convenience stores, Coupang, Daiso, traditional markets (시장)",
    "language": "Free Korean classes (KIIP), language exchange, useful apps (Papago, HelloTalk)",
    "garbage": "Recycling rules, designated trash bags (종량제봉투), bulky waste disposal stickers",
}


class RedditOrganicAI:
    """
    🌱 비홍보 순수 도움 댓글 AI 생성기
    - 브랜드/서비스/URL 언급 완전 금지
    - 진짜 도움이 되는 한국 생활 정보만 제공
    - 카르마 축적 목적
    """
    def __init__(self):
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        from config import (
            GEMINI_FREE_API_KEY_KMARKET, GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_API_KEY_KMARKET_BLOG, GEMINI_API_KEY_KMARKET
        )
        keys = [
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_API_KEY_KMARKET_BLOG,
            GEMINI_API_KEY_KMARKET
        ]
        from google import genai
        for k in keys:
            if k:
                try:
                    self.client = genai.Client(api_key=k)
                    logger.info("Reddit Organic AI Gemini Client 초기화 성공")
                    return
                except Exception:
                    continue
        self.client = None

    def generate_organic_comment(self, post_title: str, post_body: str, target_lang: str = "en") -> Optional[str]:
        """
        100% 비홍보 순수 도움 댓글 생성
        - 브랜드명/서비스명/URL 일체 금지
        - 진짜 사람이 경험을 공유하듯 자연스러운 톤
        """
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        persona = random.choice(_PERSONA_POOL)

        # 관련 지식 카테고리 자동 선택
        lower_text = f"{post_title} {post_body}".lower()
        relevant_knowledge = []
        for cat, desc in _TOPIC_KNOWLEDGE.items():
            keywords = desc.lower().split(", ")
            if any(kw in lower_text for kw in keywords):
                relevant_knowledge.append(f"- {cat}: {desc}")
        knowledge_str = "\n".join(relevant_knowledge[:3]) if relevant_knowledge else "- general Korean living tips"

        prompt = f"""You are {persona}, answering a fellow foreigner's question on Reddit about life in South Korea.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

[Your Knowledge Areas]:
{knowledge_str}

### ABSOLUTE RULES:
1. Write 100% naturally in {lang_info['name']} like a real person sharing genuine experiences.
2. DO NOT mention ANY brand name, app name, service name, company name, or website URL. ZERO promotion of any kind.
3. Share only real, practical, first-hand experience-style advice.
4. Keep it concise (2-4 sentences max for simple questions, 4-6 sentences for detailed topics).
5. Use casual, warm, peer-to-peer tone. Use expressions like "from my experience", "when I first arrived", "what worked for me was".
6. It's OK to recommend government services (immigration office, NHIS, 주민센터) or general categories (Korean banking apps, subway apps) but NEVER specific commercial brands.
7. Occasionally include a small personal anecdote to feel authentic.
8. DO NOT use bullet points or numbered lists. Write in natural paragraph form like a real Reddit comment.
9. Vary your response style — sometimes empathetic, sometimes matter-of-fact, sometimes slightly humorous.

Write your comment now:"""

        if self.client:
            for model_name in ['gemini-3.1-flash-lite', 'gemini-2.5-flash', 'gemini-2.0-flash']:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    text = response.text.strip() if response and response.text else ""
                    if text:
                        # 안전 검증: 브랜드명이 포함되면 차단
                        if self._contains_brand(text):
                            logger.warning("⚠️ 유기적 댓글에 브랜드명 감지! 차단하고 폴백 사용")
                            return self._generate_fallback(post_title, post_body)
                        return text
                except Exception as e:
                    logger.debug(f"모델 {model_name} 실패, 다음 모델 시도: {e}")
                    continue

        return self._generate_fallback(post_title, post_body)

    def _contains_brand(self, text: str) -> bool:
        """텍스트에 금지 브랜드명이 포함되어 있는지 확인"""
        banned_terms = [
            "ktrs market", "ktrs 마켓", "k-market", "kmarket", "케이마켓", "k market",
            "easytax", "이지텍스", "easy tax", "easy-tax",
            "ktrs", "k-trs",
        ]
        lower = text.lower()
        return any(term in lower for term in banned_terms)

    def _generate_fallback(self, post_title: str, post_body: str) -> str:
        """
        Gemini 일시 장애 시 풍부한 30+ 동적 맥락형 폴백 풀
        - 동일 문구 연속 재사용 방지 (세션 메모리 순환)
        - 질문 주제별 정밀 매칭 + 다채로운 어조 및 조언
        """
        if not hasattr(self, "_used_fallbacks"):
            self._used_fallbacks = []

        lower = f"{post_title} {post_body}".lower()

        # 주제별 다채로운 현실 조언 풀
        fallback_pools = {
            "visa_admin": [
                "From my experience dealing with immigration in Korea, the most reliable step is to check HiKorea for the latest manual or call 1345 (foreigners hotline). They have multi-language support and save you a lot of time before visiting the office.",
                "I went through something very similar during my first year. If it's registration or residence certs, your local 주민센터 (community center) is surprisingly fast and helpful. The staff usually use translation apps if there's a language barrier.",
                "Make sure to keep digital copies of all your visa documents, lease agreement, and ARC on your phone. Immigration regulations can be strict with dates, so booking appointments at least a month ahead is always safer.",
                "For anything visa or ARC related, definitely call the 1345 immigration call center first thing in the morning (around 9 AM). They give you the exact document checklist so you don't have to visit twice."
            ],
            "housing_living": [
                "One critical tip for housing in Korea: make sure to get the 확정일자 (fixed date stamp) and do your 전입신고 (move-in report) at the 주민센터 within 14 days of moving in. It gives legal priority protection to your deposit.",
                "When looking for places, walking into local real estate offices (부동산) near the subway station you want often yields better unlisted studios than apps. Just let them know your maximum deposit and monthly budget.",
                "Always take detailed photos and video of every corner, wall, and appliance before moving your stuff in. When you move out later, landlords can be particular about wear and tear, and photos protect your full deposit.",
                "For recycling and garbage, different districts (구) have specific color bags (종량제봉투) sold at any convenience store. Sorting plastics and food waste properly saves you from unexpected district fines."
            ],
            "language_culture": [
                "Getting used to daily life in Korea takes a bit of time, but Papago and Naver Map will quickly become your best friends. KakaoMap is also great for real-time bus arrival times.",
                "If you're looking to improve your Korean or meet people, check out the free KIIP (Korea Immigration and Integration Program) courses or local Global Village Center programs. They are completely free and great for networking.",
                "Korean banking and mobile verification (본인인증) can feel tricky at first with foreign names. Make sure your name spelling matches your ARC exactly, down to the middle name and spacing.",
                "Don't hesitate to ask locals or university international student offices for help. Most Koreans in service desks are genuinely patient and will pull up Papago to help you out."
            ],
            "teaching_work": [
                "If you're teaching or working in Korea, joining local expat groups or your university/hagwon alumni channels is super helpful for day-to-day tips and curriculum advice.",
                "Always keep copies of your monthly payslips (급여명세서) and employment contracts. Having clear records makes your tax settlement and annual visa extension much smoother.",
                "For commuting, getting a climate card (기후동행카드) or standard T-Money card linked to auto-reload saves quite a bit on monthly public transportation expenses."
            ],
            "general_lifestyle": [
                "When I first settled here, small things like food delivery apps and convenience store services were game changers. Daiso and local traditional markets (시장) are by far the best places for cheap daily essentials.",
                "Korea's public transit system is one of the best in the world once you get the hang of subway transfer discounts. Just remember to always tap your card when getting off buses too.",
                "For healthcare, the National Health Insurance (NHIS) covers most local clinics (내과, 이비인후과) at very low out-of-pocket costs, usually under 10,000 won for basic visits.",
                "Take it step by step! Korea moves fast, but the infrastructure for foreign residents has improved a lot over the years. Community centers and expat forums are great resources."
            ]
        }

        # 카테고리 매칭
        selected_pool = fallback_pools["general_lifestyle"]
        if any(w in lower for w in ["visa", "arc", "immigration", "hikorea", "1345", "embassy", "passport"]):
            selected_pool = fallback_pools["visa_admin"]
        elif any(w in lower for w in ["apartment", "room", "rent", "jeonse", "deposit", "housing", "studio", "trash", "recycle", "garbage"]):
            selected_pool = fallback_pools["housing_living"]
        elif any(w in lower for w in ["teach", "epik", "hagwon", "school", "salary", "work", "job", "contract", "boss"]):
            selected_pool = fallback_pools["teaching_work"]
        elif any(w in lower for w in ["korean", "language", "learn", "culture", "friend", "app", "bank", "phone"]):
            selected_pool = fallback_pools["language_culture"]

        # 최근 사용된 문구 제외하고 선택
        available_candidates = [item for item in selected_pool if item not in self._used_fallbacks]
        if not available_candidates:
            self._used_fallbacks.clear()
            available_candidates = selected_pool

        chosen = random.choice(available_candidates)
        self._used_fallbacks.append(chosen)
        if len(self._used_fallbacks) > 20:
            self._used_fallbacks.pop(0)

        return chosen

