import os
import json
import logging
from typing import Optional, List, Dict, Any
from config import GEMINI_API_KEY_EASYTAX, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxGemini")

class EasyTaxGeminiEngine:
    """
    💰 [EasyTax (KTRS) 전용 Gemini AI 엔진]
    - 조세특례제한법 제30조(90% 소득세 감면), D-2 유학생 3.3% 환급, 5개년 소급 경정청구 전문
    - Anti-Ban & Financial Compliance 가드레일 엄격 내장 (선입금 0원, 공인 세무대리 팩트)
    """
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()
        self.easytax_rules = self._load_json(DATA_DIR / "easytax_rules.json")

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_EASYTAX
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("EasyTax 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"EasyTax Gemini 초기화 실패: {e}")
                self.client = None
        else:
            logger.info("GEMINI_API_KEY 미설정 -> EasyTax 템플릿 기반 자가 생성 모드 가동")

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_reddit_response(self, post_title: str, post_body: str, target_lang: str = "en", landing_url: str = "") -> str:
        """EasyTax 전용 레딧 외국인 세금/비자 질문 80:20 법적 팩트 답변 생성 (refund_scripts 고도화 주입)"""
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        few_shots = self.supabase_mgr.fetch_golden_few_shots("easytax", target_lang, min_score=80.0, limit=2)
        proven_scripts = self.supabase_mgr.fetch_easytax_proven_scripts(limit=2)
        
        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [High-Performing Legal/Tax Reference Examples]:\n" + "\n\n".join(few_shots)
        if proven_scripts:
            proven_texts = [f"- {ps.get('script_text')}" for ps in proven_scripts]
            few_shot_prompt += "\n\n### [Proven High-Converting Real Scenarios from EasyTax Engine]:\n" + "\n".join(proven_texts)

        tax_facts_str = json.dumps(self.easytax_rules, ensure_ascii=False)

        prompt = f"""
You are a knowledgeable and trusted tax advisory assistant in South Korea, answering a foreign worker or student's question on Reddit about taxes, ARC, salary deductions, or tax refunds.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Verified Korean Tax Law Facts]: {tax_facts_str}
[Landing URL]: {landing_url}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

### CRITICAL ANTI-BAN & COMPLIANCE RULES:
1. Write 100% fluently in {lang_info['name']}.
2. 80% MUST be accurate, objective legal explanation citing Korean Tax Law (e.g. Article 30 Restriction of Special Taxation Act for SME workers, or 3.3% withholding refund for D-2 part-time students).
3. NEVER promise fake instant cash. Clearly explain that refund eligibility is based on official National Tax Service records.
4. 20% gentle mention of EasyTax ({landing_url}) for a 100% free AI refund estimation (0 upfront fee, handled via certified tax accountants).
5. Professional, highly trustworthy, and reassuring tone.
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"EasyTax Gemini 레딧 생성 에러: {e}")

        return f"Under Korean Tax Law (Article 30), foreign workers in SMEs can receive up to 90% income tax reduction. D-2 students can claim back 100% of 3.3% withholding tax. You can simulate your 5-year refund 100% free with no upfront fees at EasyTax ({landing_url})."

    def generate_shorts_script(self, target_lang: str = "ko", psychology: str = "relief_rights") -> Dict[str, Any]:
        """EasyTax 합법 세무 환급 30초 숏폼 대본 생성 (refund_scripts 고도화 & Anti-Ban 가드레일)"""
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
