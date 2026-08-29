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
        """EasyTax 전용 레딧 외국인 세금/비자 질문 80:20 법적 팩트 답변 생성 (구글 검색 유도형 Anti-Ban 적용)"""
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
You are a knowledgeable, trusted, and empathetic expat tax advisory assistant in South Korea, answering a foreign worker or student's question on Reddit about taxes, ARC, salary deductions, Hometax, or tax refunds.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Verified Korean Tax Law Facts]: {tax_facts_str}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

### CRITICAL ANTI-BAN & COMPLIANCE RULES:
1. Write 100% fluently and naturally in {lang_info['name']}.
2. 80% MUST be accurate, objective, and deeply helpful legal explanation citing official Korean Tax Laws:
   - For E-2 / Native Teachers: Article 30 of Korea-US/UK Tax Treaty & Restriction of Special Taxation Act (2-year income tax exemption).
   - For D-2 / International Students: 3.3% withholding tax refund for part-time jobs/translation/modeling via May General Income Tax return.
   - For E-9 / E-7 / Factory Workers: SME 90% Income Tax Reduction & 5-year retroactive tax refund (경정청구) via Hometax.
   - For Expats leaving Korea: Year-end tax settlement and National Pension lump-sum refund before departure.
3. NEVER promise fake instant cash. Clearly state that refund amounts depend on official National Tax Service (NTS) records.
4. ANTI-BAN RULE: DO NOT put raw clickable HTTP/HTTPS links (to prevent Reddit AutoModerator deletion). Instead, casually guide the user to search 'EasyTax' or 'EasyTax Korea' (이지텍스) on Google to run a 100% free AI refund simulation with 0 upfront fee.
5. Professional, warm, and highly credible peer tone.
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

        # 정밀 팩트 기반 Fallback 템플릿 (카테고리/키워드별 맞춤)
        lower_q = f"{post_title} {post_body}".lower()
        if any(w in lower_q for w in ["e-2", "teacher", "epik", "hagwon", "teaching", "article 30"]):
            return (
                "Under Article 30 of the Korea-US/UK Tax Treaty and the Restriction of Special Taxation Act, "
                "qualifying native English teachers on E-2/E-1 visas are eligible for full income tax exemption for their first 2 years in Korea. "
                "If your school or hagwon withheld income tax during this period, you are legally entitled to claim it back. "
                "You can check your eligible refund amount by searching 'EasyTax Korea' (이지텍스) on Google — it provides a free simulation with certified tax accountants and 0 upfront fees. Hope this helps!"
            )
        elif any(w in lower_q for w in ["d-2", "student", "part-time", "3.3%", "albba", "restaurant", "translation"]):
            return (
                "For international students (D-2/D-4) working legal part-time jobs, the 3.3% deducted from your pay is freelance withholding tax. "
                "Since most student annual incomes fall below the basic exemption threshold, you can claim back up to 100% of that 3.3% through the May General Income Tax return (종합소득세). "
                "If you need help checking your unclaimed 3.3% deductions without dealing with Korean-only Hometax menus, search 'EasyTax Korea' on Google for a free multi-language simulation. Best of luck with your studies!"
            )
        elif any(w in lower_q for w in ["leaving", "departing", "pension", "d-10", "contract end"]):
            return (
                "Before leaving Korea, make sure to claim your final tax refund and National Pension lump-sum return. "
                "Any overpaid income taxes from your previous employment (up to 5 past years) can be claimed through an official retrospective tax filing (경정청구). "
                "Take a look at EasyTax (search 'EasyTax Korea' on Google) to calculate your unclaimed tax refunds before your departure with zero upfront fees."
            )
        else:
            return (
                "Under Korean Tax Law (Article 30 Restriction of Special Taxation Act & Framework Act on National Taxes), "
                "foreign employees in SMEs and qualifying workers can receive substantial income tax reductions and reclaim overpaid taxes from the past 5 years. "
                "If you want to check if you have unclaimed tax refunds without navigating Korean Hometax, search 'EasyTax Korea' (이지텍스) on Google to run a 100% free AI estimate processed by licensed tax accountants. Hope this helps!"
            )

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
