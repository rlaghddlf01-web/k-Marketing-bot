"""
EasyTaxGeminiShorts - 💰 EasyTax 30초 숏폼 비디오 대본 생성 전담 AI 엔진
"""

import json
import logging
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_EASYTAX, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxGeminiShorts")

class EasyTaxGeminiShorts:
    """EasyTax 전용 숏폼 비디오 대본 생성기"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_EASYTAX
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("EasyTax 숏폼 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"EasyTax 숏폼 Gemini 초기화 실패: {e}")
                self.client = None

    def generate_shorts_script(self, *args, target_lang: str = "ko", psychology: str = "relief_rights", **kwargs) -> Dict[str, Any]:
        """EasyTax 합법 세무 환급 30초 숏폼 대본 생성 (refund_scripts 고도화 & Anti-Ban 가드레일)"""
        if args and isinstance(args[-1], str) and len(args[-1]) == 2:
            target_lang = args[-1]
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        proven_scripts = self.supabase_mgr.fetch_easytax_proven_scripts(limit=2)
        proven_guide = ""
        if proven_scripts:
            proven_guide = f"\n[Proven Real Pitch Reference]: {proven_scripts[0].get('script_text')[:120]}"

        prompt = f"""
Create a highly informative and viral 30-second educational short-form script for expats living in South Korea about Korean Tax Law benefits (Article 30 90% SME tax relief & 5-year retroactive refunds).

[Language]: {lang_info['name']} ({lang_info['native_name']})

### CRITICAL ANTI-BAN & COMPLIANCE RULES:
1. NO scam triggers: NEVER say 'free fast cash'. Frame strictly as official legal rights under Korean Tax Law.
2. Highlight: 100% Free AI simulation, ZERO upfront payment, filed via certified tax partner.
3. Target: E-9/H-2 workers (up to 90% reduction) & D-2 students (3.3% part-time tax refund).

### STRUCTURE:
1. Hook (0-3s): Informative fact about overpaid taxes for expats in Korea.
2. Story/Proof (3-23s): Explain the real legal benefit under Korean Tax Law Article 30 and 5-year back claim.
3. Solution & CTA (23-30s): Direct to check the free official tool in bio.

Output JSON format strictly with keys:
"hook_title": (punchy informative headline for screen overlay),
"voiceover_text": (entire 30s speech fluently written in {lang_info['name']}),
"captions": [(array of 3-4 short sentences for on-screen text overlays)],
"cta_text": (closing call to action in {lang_info['name']}),
"disclaimer": (official legal disclaimer in {lang_info['name']}: "Processed via certified tax agents under Korean tax law. Actual refund amounts depend on individual income records.")
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"EasyTax Gemini 숏폼 생성 에러: {e}")

        return {
            "hook_title": "🏛️ Korean Expat Tax Rights: 90% Relief",
            "voiceover_text": "Did you know foreign workers in South Korea can legally reduce up to 90% of income tax under Article 30? Check your 5-year overpaid tax refund 100% free with EasyTax!",
            "captions": [
                "🏛️ 90% Income Tax Reduction (Article 30)",
                "🎓 D-2 Student Part-Time 3.3% Refund",
                "🛡️ 100% Free AI Check • Certified Tax Partner"
            ],
            "cta_text": "Click profile link to check your free refund amount now!",
            "disclaimer": "Processed via certified tax agents under Korean tax law. Actual refund amounts depend on individual income records."
        }
