"""
EasyTaxGeminiReddit - 💰 EasyTax 레딧 외국인 세금/비자 질문 3단계 간접 홍보 답변 전담 AI 엔진
- Level 1 (순수 팩트, 40%): 브랜드 0%, 100% 법적 팩트만
- Level 2 (간접 유도, 40%): "AI 시뮬레이션 해보는 사이트가 있던데" 식
- Level 3 (브랜드 멘션, 20%): 프로필 참고 유도
"""

import json
import random
import logging
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_EASYTAX, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxGeminiReddit")

# 3단계 간접 홍보 전략 비율
_PROMO_LEVELS = {
    1: 0.40,  # 순수 법적 팩트 (브랜드 0%)
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


class EasyTaxGeminiReddit:
    """EasyTax 전용 레딧 80:20 세무 법률 3단계 간접 홍보 답변기"""
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
                logger.info("EasyTax 레딧 전용 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"EasyTax 레딧 Gemini 초기화 실패: {e}")
                self.client = None

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_reddit_response(self, post_title: str, post_body: str, target_lang: str = "en", landing_url: str = "") -> str:
        """EasyTax 전용 3단계 간접 홍보 세무 답변 생성"""
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        promo_level = _choose_promo_level()

        few_shots = self.supabase_mgr.fetch_golden_few_shots("easytax", target_lang, min_score=80.0, limit=2)
        proven_scripts = []
        if hasattr(self.supabase_mgr, "fetch_easytax_proven_scripts"):
            try:
                proven_scripts = self.supabase_mgr.fetch_easytax_proven_scripts(limit=2)
            except Exception:
                proven_scripts = []

        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [High-Performing Examples]:\n" + "\n\n".join(few_shots)
        if proven_scripts:
            proven_texts = [f"- {ps.get('script_text')}" for ps in proven_scripts]
            few_shot_prompt += "\n\n### [Proven Examples]:\n" + "\n".join(proven_texts)

        tax_facts_str = json.dumps(self.easytax_rules, ensure_ascii=False)

        # 홍보 레벨별 프롬프트 분기
        if promo_level == 1:
            promo_instruction = """### LEVEL 1 — PURE LEGAL FACTS (NO PROMOTION):
1. DO NOT mention ANY brand, app, service, or company name.
2. Provide 100% accurate, objective legal/tax explanations with Korean Tax Law citations.
3. Cite official sources like the National Tax Service (NTS/국세청), Hometax, Framework Act on National Taxes, etc.
4. Guide the user on exact steps they can take through official government channels.
5. Write like a knowledgeable peer, not a salesperson."""

        elif promo_level == 2:
            promo_instruction = """### LEVEL 2 — INDIRECT SERVICE MENTION:
1. Provide 80% accurate legal facts and official steps first.
2. Near the end, casually mention something like:
   - "there are free online tools that let you simulate your refund amount before filing"
   - "I found a free calculator that shows your potential refund based on NTS records"
   - "some services help foreigners navigate Hometax without dealing with the Korean-only interface"
3. DO NOT use the exact service name. Just describe the benefit vaguely.
4. NEVER include URLs."""

        else:
            promo_instruction = """### LEVEL 3 — PROFILE REFERENCE:
1. Provide 80% accurate legal facts first.
2. At the very end, add something natural like:
   - "I used a service called EasyTax Korea that handled everything with licensed accountants, linked in my profile"
   - "check my profile for the tax refund tool I used — it was free to simulate"
3. Mention the name ONLY once and ONLY if it flows naturally.
4. NEVER post a direct URL."""

        prompt = f"""You are a knowledgeable, trusted, and empathetic expat tax advisory peer in South Korea, answering a foreign worker or student's question on Reddit about taxes, ARC, salary deductions, Hometax, or tax refunds.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Verified Korean Tax Law Facts]: {tax_facts_str}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL RULES:
1. Write 100% fluently and naturally in {lang_info['name']}.
2. Key legal facts to cite when relevant:
   - E-2 / Native Teachers: Article 30 of Korea-US/UK Tax Treaty, 2-year income tax exemption
   - D-2 / Students: 3.3% withholding refund via May General Income Tax return (종합소득세)
   - E-9 / Factory Workers: SME 90% income tax reduction, 5-year retroactive refund (경정청구)
   - Departing Korea: Year-end settlement + National Pension lump-sum refund
3. NEVER promise fake instant cash. State that amounts depend on official NTS records.
4. Keep it concise (3-6 sentences).
5. Professional yet warm peer tone. No sales pitch.
6. DO NOT use bullet points — write like a normal Reddit comment.
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                result = response.text.strip()
                logger.info(f"💰 [EasyTax Reddit AI] Level {promo_level} 답변 생성 완료")
                return result
            except Exception as e:
                logger.error(f"EasyTax Gemini 레딧 생성 에러: {e}")

        # Level 1 순수 팩트 기반 Fallback
        lower_q = f"{post_title} {post_body}".lower()
        if any(w in lower_q for w in ["e-2", "teacher", "epik", "hagwon", "teaching", "article 30"]):
            return (
                "Under Article 30 of the Korea-US/UK Tax Treaty and the Restriction of Special Taxation Act, "
                "qualifying native English teachers on E-2/E-1 visas are eligible for full income tax exemption for their first 2 years in Korea. "
                "If your school withheld income tax during this period, you can claim it back through a year-end tax settlement or by filing at your local tax office. "
                "Bring your passport, ARC, employment contract, and pay stubs. The process is straightforward once you have the documents."
            )
        elif any(w in lower_q for w in ["d-2", "student", "part-time", "3.3%", "restaurant", "translation"]):
            return (
                "The 3.3% deducted from your part-time pay is freelance withholding tax. Since most student annual incomes fall below the basic exemption threshold, "
                "you can claim back up to 100% of that 3.3% through the May General Income Tax return (종합소득세 신고). "
                "You can do it yourself on Hometax, but the interface is only in Korean. The local tax office (세무서) staff are usually helpful if you go in person."
            )
        else:
            return (
                "Under Korean Tax Law, foreign employees in SMEs and qualifying workers can receive substantial income tax reductions "
                "and reclaim overpaid taxes from the past 5 years through an official retroactive filing (경정청구). "
                "Your first step would be to check your withholding tax records on Hometax (국세청 홈택스) or visit your nearest tax office with your ARC and pay stubs."
            )
