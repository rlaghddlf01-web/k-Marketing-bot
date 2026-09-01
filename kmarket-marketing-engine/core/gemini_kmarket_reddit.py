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

# 50:50 황금 비율 (순수 정보 50% vs 구글 검색 유도 50%)
_PROMO_LEVELS = {
    1: 0.50,  # 순수 도움 (브랜드/홍보 0%, URL 0개)
    2: 0.50,  # 자연스러운 구글 'k-market korea' 검색 유도 (노링크)
}


def _choose_promo_level() -> int:
    """가중치 기반 50:50 랜덤 레벨 선택"""
    return 1 if random.random() < 0.50 else 2


class KMarketGeminiReddit:
    """K-Market 전용 레딧 50:50 생활 정보 및 구글 검색 유도 답변기"""
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
        """K-Market 전용 50:50 생활 정보 & 구글 검색 유도 답변 생성"""
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

        # 홍보 레벨별 프롬프트 분기 (50:50)
        if promo_level == 1:
            promo_instruction = """### TYPE 1 — 100% PURE PRACTICAL HELP (NO PROMOTION, NO SEARCH SUGGESTION):
1. DO NOT mention ANY brand, app, service, search keyword, or website.
2. Provide 100% genuinely helpful, practical expat advice for living in Korea.
3. Share real tips like how to avoid bulky waste disposal sticker fees, recycling rules in Korea, moving tips, etc.
4. Write like chatting with a close foreign friend. ZERO commercial intent."""

        else:
            promo_instruction = """### TYPE 2 — NATURAL GOOGLE SEARCH SUGGESTION (NO URLS, 100% SAFE):
1. Provide 80% genuinely helpful, practical advice first.
2. At the very end of your comment, add ONE casual recommendation to search on Google:
   - "If you need $0 free furniture or moving sale items from other expats, try searching 'k-market korea' on Google."
   - "There's a secondhand platform for foreigners in Korea with auto-translation — search 'k-market korea' on Google to find it."
3. NEVER post any raw clickable URLs or links (http/https/www/dot-com).
4. ONLY suggest searching the exact keyword 'k-market korea' on Google."""

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
