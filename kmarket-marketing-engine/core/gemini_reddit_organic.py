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
        api_key = GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("Reddit Organic AI Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"Reddit Organic AI Gemini 초기화 실패: {e}")
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
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                text = response.text.strip()
                # 안전 검증: 브랜드명이 포함되면 차단
                if self._contains_brand(text):
                    logger.warning("⚠️ 유기적 댓글에 브랜드명 감지! 차단하고 폴백 사용")
                    return self._generate_fallback(post_title, post_body)
                return text
            except Exception as e:
                logger.error(f"Organic AI 생성 에러: {e}")

        return self._generate_fallback(post_title, post_body)

    def _contains_brand(self, text: str) -> bool:
        """텍스트에 금지 브랜드명이 포함되어 있는지 확인"""
        banned_terms = [
            "k-market", "kmarket", "케이마켓", "k market",
            "easytax", "이지텍스", "easy tax", "easy-tax",
            "ktrs", "k-trs",
        ]
        lower = text.lower()
        return any(term in lower for term in banned_terms)

    def _generate_fallback(self, post_title: str, post_body: str) -> str:
        """Gemini 실패 시 범용 폴백 댓글"""
        lower = f"{post_title} {post_body}".lower()

        if any(w in lower for w in ["visa", "arc", "immigration", "foreigner registration"]):
            return random.choice([
                "From my experience, the immigration office near your area should be able to help with that. I'd recommend making an appointment through the HiKorea website first — walk-ins can have really long wait times. Bring your passport and any relevant documents just in case.",
                "I went through something similar when I first arrived. The local 주민센터 (community center) was actually super helpful for basic registration stuff. The staff there sometimes speak basic English too.",
            ])
        elif any(w in lower for w in ["apartment", "room", "rent", "jeonse", "deposit", "housing", "studio"]):
            return random.choice([
                "One thing I wish I knew earlier — always do 전입신고 (move-in registration) at your local 주민센터 right after signing the contract. It legally protects your deposit. Also take photos of everything before moving in!",
                "When I was apartment hunting, I found that going directly to local 부동산 (real estate offices) near the area I wanted gave me way better options than online listings. Just walk in and tell them your budget.",
            ])
        elif any(w in lower for w in ["food", "restaurant", "eat", "delivery"]):
            return random.choice([
                "Korean convenience stores are actually incredible for budget meals — they have surprisingly good 도시락 (lunch boxes) for around 3,000-4,000 won. Also, most restaurants have lunch specials that are way cheaper than dinner.",
                "When eating alone in Korea, look for places with 1인분 options or hit up 분식집 (snack shops) — tteokbokki, kimbap, and ramen are always cheap and delicious. No judgment eating alone here!",
            ])
        else:
            return random.choice([
                "When I first came to Korea, the culture shock was real but it gets so much easier with time. One tip — download a Korean map app (like the ones most locals use) because Google Maps doesn't work well here for navigation.",
                "Been through something similar! Korea can be confusing at first but the people are generally really helpful if you ask. The 주민센터 near your home is a great starting point for most administrative stuff.",
            ])
