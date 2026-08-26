import os
import json
import logging
from typing import Optional, List, Dict, Any
from config import GEMINI_API_KEY_KMARKET, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketGemini")

class KMarketGeminiEngine:
    """
    🛒 [K-Market 전용 Gemini AI 엔진]
    - 270개 실물 매물, 0원 무료 나눔, 귀국 무빙세일, 17개국 번역 채팅 전문
    - 외국인 로컬 라이프스타일 및 커뮤니티 바이럴 숏폼/대본 생성
    """
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()
        # Supabase 클라우드 실시간 270개 매물 우선 로드, 없으면 로컬 fallback
        self.kmarket_items = self.supabase_mgr.fetch_live_kmarket_items(free_only=False, limit=20)

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("K-Market 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"K-Market Gemini 초기화 실패: {e}")
                self.client = None
        else:
            logger.info("GEMINI_API_KEY 미설정 -> K-Market 템플릿 기반 자가 생성 모드 가동")

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def generate_reddit_response(self, post_title: str, post_body: str, target_lang: str = "en", landing_url: str = "") -> str:
        """K-Market 전용 레딧 가구/생활용품 질문 80:20 답변 생성"""
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        few_shots = self.supabase_mgr.fetch_golden_few_shots("kmarket", target_lang, min_score=80.0, limit=2)
        
        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [High-Performing Friendly Expat Examples]:\n" + "\n\n".join(few_shots)

        sample_items = json.dumps(self.kmarket_items[:3], ensure_ascii=False) if self.kmarket_items else "Bed, Desk, Refrigerator for 0 KRW"

        prompt = f"""
You are a friendly, veteran foreign expat living in South Korea, helping a fellow foreigner on Reddit finding second-hand furniture, moving sales, or settling in Korea.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[K-Market Real Verified Listings]: {sample_items}
[Landing URL]: {landing_url}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

### CRITICAL RULES:
1. Write 100% fluently in {lang_info['name']}.
2. 80% MUST be practical, kind advice on where/how to get affordable furniture, appliances, or moving in Korea (mentioning foreigner-friendly areas).
3. 20% gentle mention of K-Market (free 0 KRW giveaways, moving sales, 17-language auto-translate chat) with the link: {landing_url}.
4. Warm community tone, NO aggressive ad language.
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"K-Market Gemini 레딧 생성 에러: {e}")

        return f"Hey there! If you're looking for affordable or free furniture in Korea, check out local expat moving sales on K-Market ({landing_url}). You can find 0 KRW free giveaways and chat directly in 17 languages!"

    def generate_shorts_script(self, target_lang: str = "ko", psychology: str = "free_giveaway_emotional", ab_group: str = "A") -> Dict[str, Any]:
        """
        [K-Market 자가학습 고도화] 3대 심리 유형 & A/B 테스트 기반 숏폼 대본 생성
        - psychology:
          1. 'free_giveaway_emotional': 0원 나눔 감동/득템형
          2. 'urgent_moving_discount': 귀국 급처 90% 초특가형
          3. 'multi_lang_comfort': 17개국 모국어 편의/사기방지형
        - ab_group: 'A' (직설적 혜택 강조) / 'B' (외국인 공감 스토리텔링)
        """
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        
        # 심리 유형에 맞는 실시간 매물 매칭
        items = self.supabase_mgr.fetch_live_kmarket_items(psychology=psychology, limit=3)
        sample_item = items[0] if items else (self.kmarket_items[0] if self.kmarket_items else {"title": "원목 침대 & 매트리스", "price": 0, "region": "안산"})

        psychology_guidelines = {
            "free_giveaway_emotional": "Focus on warm community spirit and graduating expats giving away free $0 items (beds, desks, fridges) to newcomers.",
            "urgent_moving_discount": "Focus on urgent moving-out sales with up to 90% crazy discounts on full room furniture before leaving Korea.",
            "multi_lang_comfort": "Focus on zero scam anxiety with real-time 17-language auto-translated chat and ARC verified sellers in Korea."
        }

        ab_instruction = "Tone A: Punchy, urgent, direct-benefit driven headline and fast-paced speech." if ab_group == "A" else "Tone B: Warm, friendly expat peer storytelling with emotional connection."

        prompt = f"""
Create a viral 30-second vertical short-form script for foreign expats living in South Korea about K-Market.

[Target Psychology & Core Focus]: {psychology_guidelines.get(psychology, psychology_guidelines['free_giveaway_emotional'])}
[A/B Variant Style]: {ab_instruction} (Group: {ab_group})
[Language]: {lang_info['name']} ({lang_info['native_name']})
[Featured Real Listing]: {sample_item.get('title')} (Price: {sample_item.get('price')} KRW, Region: {sample_item.get('region')})

### STRUCTURE:
1. Hook (0-3s): Catchy opening strictly aligned with the psychology ({psychology}) in {lang_info['name']}.
2. Story/Feature (3-23s): Highlight the real listing and K-Market's 17-language chat & 0 KRW giveaways.
3. Solution & CTA (23-30s): Drive action to tap the profile link.

Output JSON format strictly with keys:
"psychology": "{psychology}",
"ab_group": "{ab_group}",
"hook_title": (punchy headline for screen overlay),
"voiceover_text": (entire 30s speech fluently written in {lang_info['name']}),
"captions": [(array of 3-4 short sentences for on-screen text overlays)],
"cta_text": (closing call to action in {lang_info['name']})
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                res_data = json.loads(response.text)
                res_data["psychology"] = psychology
                res_data["ab_group"] = ab_group
                return res_data
            except Exception as e:
                logger.error(f"K-Market Gemini 숏폼 생성 에러: {e}")

        return {
            "psychology": psychology,
            "ab_group": ab_group,
            "hook_title": f"🎁 0 KRW Free Stuff in Korea!",
            "voiceover_text": f"Did you know you can get free furniture and appliances in South Korea? On K-Market, expats are giving away items for zero Won with 17-language instant chat!",
            "captions": [
                "🎁 0 KRW Free Items in Korea",
                "📦 One-Click Moving Sales",
                "💬 17-Language Auto-Translate Chat"
            ],
            "cta_text": "Check K-Market link in bio to grab free items now!"
        }
