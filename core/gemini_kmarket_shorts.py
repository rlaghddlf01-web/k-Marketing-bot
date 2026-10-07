"""
KMarketGeminiShorts - 🛒 K-Market 30초 숏폼 비디오 대본 생성 전담 AI 엔진
"""

import json
import logging
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_KMARKET, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketGeminiShorts")

class KMarketGeminiShorts:
    """K-Market 전용 숏폼 비디오 대본 생성기"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("K-Market 숏폼 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"K-Market 숏폼 Gemini 초기화 실패: {e}")
                self.client = None

    def generate_shorts_script(self, *args, target_lang: str = "ko", psychology: str = "free_giveaway_empathy", **kwargs) -> Dict[str, Any]:
        """K-Market 0원 나눔 및 알뜰 매물 30초 숏폼 대본 생성"""
        if args and isinstance(args[-1], str) and len(args[-1]) == 2:
            target_lang = args[-1]
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        proven_scripts = self.supabase_mgr.fetch_kmarket_proven_scripts(limit=2)
        proven_guide = ""
        if proven_scripts:
            proven_guide = f"\n[Proven Real Pitch Reference]: {proven_scripts[0].get('script_text')[:120]}"

        prompt = f"""
Create a highly engaging, viral 30-second vertical short-form video script for expats/international students in South Korea about saving money with K-Market's $0 giveaways, moving sales, and 17-language auto-translation chat.

[Language]: {lang_info['name']} ({lang_info['native_name']})
{proven_guide}

### STRUCTURE:
1. Hook (0-3s): How to get clean studio furniture/appliances for $0 in Korea.
2. Story/Proof (3-23s): Expat students moving out giving away neat desks, mini fridges, and microwaves.
3. Solution & CTA (23-30s): Direct to profile link to download K-Market app.

Output JSON format strictly with keys:
"hook_title": (punchy headline for screen overlay),
"voiceover_text": (entire 30s speech fluently written in {lang_info['name']}),
"captions": [(array of 3-4 short sentences for on-screen text overlays)],
"cta_text": (closing call to action in {lang_info['name']}),
"disclaimer": (disclaimer in {lang_info['name']}: "Verified expat secondhand community across Korean university towns & industrial areas.")
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"K-Market Gemini 숏폼 생성 에러: {e}")

        return {
            "hook_title": "🎁 Get $0 Free Furniture in Korea",
            "voiceover_text": "Moving to a new studio room in Korea? Don't spend thousands! Check out verified $0 giveaways and university moving sales on K-Market with instant 17-language translation!",
            "captions": [
                "🎁 100% Free $0 Giveaways Everyday",
                "🚚 University Moving Sales & Desks",
                "💬 Instant 17-Language Translation Chat"
            ],
            "cta_text": "Download K-Market from profile link now!",
            "disclaimer": "Verified expat secondhand community across Korean university towns & industrial areas."
        }
