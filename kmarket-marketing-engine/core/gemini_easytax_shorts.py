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
        """EasyTax 합법 세무 환급 20초 2단 씬 숏폼 대본 생성 (Scene 1: 훅/입금 9초 + Scene 2: CTA 9초)"""
        if args and isinstance(args[-1], str) and len(args[-1]) == 2:
            target_lang = args[-1]
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        proven_scripts = self.supabase_mgr.fetch_easytax_proven_scripts(limit=2)
        proven_guide = ""
        if proven_scripts:
            proven_guide = f"\n[Proven Real Pitch Reference]: {proven_scripts[0].get('script_text')[:120]}"

        prompt = f"""
Create a highly engaging, viral 20-second (2-Scene, 18-20s total) short-form video script for expats in South Korea about Korean Tax Law benefits (Article 30 90% tax relief & 5-year retroactive refunds).

[Language]: {lang_info['name']} ({lang_info['native_name']})
{proven_guide}

### 2-SCENE TIMELINE STRUCTURE:
1. SCENE 1 (0-9s) - [Hook & Bank Deposit Shock]:
   - Speech (9s): Shocking fact about 90% income tax relief (Article 30) or part-time 3.3% refund with unexpected bank deposit alert (+₩3,840,000 KRW).
   - Captions: 2 punchy short subtitle lines.
2. SCENE 2 (9-18s) - [Trust & Profile Link CTA]:
   - Speech (9s): 100% Free AI calculation via certified tax agents, zero upfront fee, direct to click profile link in bio.
   - Captions: 2 closing action subtitle lines.

Output strictly JSON with keys:
"hook_title": (punchy headline for screen overlay),
"voiceover_text": (entire 18-20s combined voiceover fluently in {lang_info['name']}),
"scene1_voiceover": (0-9s speech in {lang_info['name']}),
"scene1_captions": [(array of 2 short strings for Scene 1 subtitles)],
"scene2_voiceover": (9-18s speech in {lang_info['name']}),
"scene2_captions": [(array of 2 short strings for Scene 2 subtitles)],
"cta_text": (closing CTA button label in {lang_info['name']}),
"captions": [(array of 4 combined short sentences)],
"disclaimer": (official legal disclaimer in {lang_info['name']}: "Processed via certified tax agents under Korean tax law.")
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
                logger.error(f"EasyTax Gemini 숏폼 생성 에러: {e}")

        return {
            "hook_title": "🏛️ Korean Expat Tax: 90% Relief",
            "voiceover_text": "Did you know foreign workers in Korea can get up to 90% tax relief under Article 30? Check your 5-year refund 100% free with certified tax partners via link in bio!",
            "scene1_voiceover": "Did you know foreign workers in Korea can legally reduce up to 90% of income tax under Article 30? Over 3.8 million KRW deposited!",
            "scene1_captions": [
                "🏛️ 90% Income Tax Reduction (Article 30)",
                "💬 +₩3,840,000 KRW Deposited!"
            ],
            "scene2_voiceover": "Check your 5-year retroactive refund in 3 minutes with certified tax partners. Click the link in bio for 100% free check!",
            "scene2_captions": [
                "🛡️ 100% Free AI Check • Certified Partner",
                "👉 Click Link in Bio to Check Now!"
            ],
            "captions": [
                "🏛️ 90% Income Tax Reduction (Article 30)",
                "💬 +₩3,840,000 KRW Deposited!",
                "🛡️ 100% Free AI Check • Certified Partner",
                "👉 Click Link in Bio to Check Now!"
            ],
            "cta_text": "👉 Click link in bio to check free refund!",
            "disclaimer": "Processed via certified tax agents under Korean tax law."
        }
