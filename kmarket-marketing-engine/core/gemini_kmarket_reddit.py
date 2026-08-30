"""
KMarketGeminiReddit - 🛒 K-Market 레딧 질문 의도분류 & 3단계 간접 홍보 답변 전담 AI 엔진
- Level 1 (순수 도움, 40%): 브랜드 언급 0%, 100% 팩트
- Level 2 (간접 유도, 40%): "내가 쓰는 앱이 있는데" 식 간접 표현
- Level 3 (브랜드 멘션, 20%): 프로필 체크 유도
"""

import json
import random
import logging
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_KMARKET, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketGeminiReddit")

# 3단계 간접 홍보 전략 비율
_PROMO_LEVELS = {
    1: 0.40,  # 순수 도움 (브랜드 0%)
    2: 0.40,  # 간접 유도
    3: 0.20,  # 브랜드 멘션
}


def _choose_promo_level() -> int:
    """가중치 기반 랜덤 홍보 레벨 선택"""
    r = random.random()
    cumulative = 0
    for level, weight in _PROMO_LEVELS.items():
        cumulative += weight
        if r <= cumulative:
            return level
    return 1


class KMarketGeminiReddit:
    """K-Market 전용 레딧 질문 감지 및 3단계 간접 홍보 답변기"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()
        self.industrial_complexes = self._load_json(DATA_DIR / "industrial_complexes.json")
        self.universities = self._load_json(DATA_DIR / "universities.json")

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("K-Market 레딧 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"K-Market 레딧 Gemini 초기화 실패: {e}")
                self.client = None

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def classify_kmarket_reddit_intent(self, post_title: str, post_body: str) -> Dict[str, Any]:
        """레딧 질문글의 카테고리/의도 분류"""
        lower = f"{post_title} {post_body}".lower()
        if any(w in lower for w in ["moving", "leave korea", "leaving korea", "moving out", "bed", "desk", "sofa", "furniture", "throw away", "recycle"]):
            return {"category": "moving_sale", "score": 90, "is_relevant": True}
        elif any(w in lower for w in ["iphone", "galaxy", "macbook", "ipad", "laptop", "sim card", "prepaid sim"]):
            return {"category": "digital_goods", "score": 85, "is_relevant": True}
        elif any(w in lower for w in ["free", "giveaway", "cheap", "secondhand", "used"]):
            return {"category": "free_giveaway", "score": 95, "is_relevant": True}
        elif any(w in lower for w in ["where to buy", "shopping", "appliance", "rice cooker", "vacuum", "heater", "microwave"]):
            return {"category": "shopping", "score": 80, "is_relevant": True}
        return {"category": "general_living", "score": 75, "is_relevant": False}

    def generate_reddit_response(self, post_title: str, post_body: str, target_lang: str = "en", landing_url: str = "") -> str:
        """K-Market 전용 3단계 간접 홍보 답변 생성"""
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        promo_level = _choose_promo_level()

        few_shots = self.supabase_mgr.fetch_golden_few_shots("kmarket", target_lang, min_score=80.0, limit=2)
        proven_scripts = []
        if hasattr(self.supabase_mgr, "fetch_kmarket_proven_scripts"):
            try:
                proven_scripts = self.supabase_mgr.fetch_kmarket_proven_scripts(limit=2)
            except Exception:
                proven_scripts = []

        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [High-Performing Examples]:\n" + "\n\n".join(few_shots)
        if proven_scripts:
            proven_texts = [f"- {ps.get('script_text')}" for ps in proven_scripts]
            few_shot_prompt += "\n\n### [Proven Examples]:\n" + "\n".join(proven_texts)

        # 홍보 레벨별 프롬프트 분기
        if promo_level == 1:
            promo_instruction = """### LEVEL 1 — PURE HELP (NO PROMOTION):
1. DO NOT mention ANY brand, app, or service name.
2. Provide 100% genuinely helpful, practical advice.
3. Share real-world tips like how to avoid bulky waste fees, where to find free giveaways near universities, etc.
4. Write like you're chatting with a friend, no sales pitch at all."""

        elif promo_level == 2:
            promo_instruction = """### LEVEL 2 — INDIRECT MENTION:
1. Provide 80% genuinely helpful, practical advice first.
2. Near the end, casually mention something like:
   - "there's this app that auto-translates chat in 17 languages, really helped me with Korean sellers"
   - "I found this secondhand platform made specifically for foreigners in Korea, it has ARC verification so it's safe"
3. DO NOT use the exact brand name. Just describe the benefit vaguely.
4. NEVER include URLs."""

        else:
            promo_instruction = """### LEVEL 3 — PROFILE REFERENCE:
1. Provide 80% genuinely helpful advice first.
2. At the very end, add something natural like:
   - "I linked the platform I use in my profile if you wanna check it out"
   - "check my profile for the link — it's specifically made for expats"
3. Mention 'K-Market' or '케이마켓' ONLY if it flows naturally, MAX once.
4. NEVER post a direct URL."""

        prompt = f"""You are an experienced, helpful, and friendly senior foreign resident / expat living in South Korea, answering another foreigner's question on Reddit about moving, buying/selling used items, finding free giveaways, or studio living tips.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL RULES:
1. Write 100% naturally in {lang_info['name']} like a real person.
2. Keep it concise (3-5 sentences max).
3. NEVER post raw clickable URLs or links.
4. Use casual, warm, peer-to-peer tone with occasional personal anecdotes.
5. DO NOT use bullet points or numbered lists — write like a normal Reddit comment.
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt
                )
                result = response.text.strip()
                logger.info(f"🎯 [K-Market Reddit AI] Level {promo_level} 답변 생성 완료")
                return result
            except Exception as e:
                logger.error(f"K-Market Gemini 레딧 생성 에러: {e}")

        # Fallback (Level 1 순수 도움만)
        return (
            "When moving out or looking for furniture/appliances in Korea, you can save a lot by checking local expat moving sales. "
            "Instead of paying expensive district disposal fees for bulky items, many graduating students give away desks, microwaves, and chairs for free. "
            "Try posting in your university's international student group or community boards — there are always people giving stuff away around semester end. Hope your stay in Korea goes smoothly!"
        )
