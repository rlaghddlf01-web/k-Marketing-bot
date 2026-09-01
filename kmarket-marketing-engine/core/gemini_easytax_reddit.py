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

# 50:50 황금 비율 (순수 정보 50% vs 구글 검색 유도 50%)
_PROMO_LEVELS = {
    1: 0.50,  # 순수 법적 팩트/도움 (브랜드/홍보 0%, URL 0개)
    2: 0.50,  # 자연스러운 구글 'ktrs tax' 검색 유도 (노링크)
}


def _choose_promo_level() -> int:
    """가중치 기반 50:50 랜덤 레벨 선택"""
    return 1 if random.random() < 0.50 else 2


class EasyTaxGeminiReddit:
    """EasyTax 전용 레딧 50:50 세무 법률 및 구글 검색 유도 답변기"""
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
        """EasyTax 전용 50:50 세무 정보 & 구글 검색 유도 답변 생성"""
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

        # 홍보 레벨별 프롬프트 분기 (50:50)
        if promo_level == 1:
            promo_instruction = """### TYPE 1 — 100% PURE LEGAL & TAX HELP (NO PROMOTION, NO SEARCH SUGGESTION):
1. DO NOT mention ANY brand, app, service, search keyword, or company name.
2. Provide 100% accurate, objective legal/tax explanations citing official Korean Tax Law & NTS (국세청) guidelines.
3. Guide the user on exact official steps through Hometax or regional tax offices.
4. Write like a warm, knowledgeable expat peer. ZERO commercial intent."""

        else:
            promo_instruction = """### TYPE 2 — NATURAL GOOGLE SEARCH SUGGESTION (NO URLS, 100% SAFE):
1. Provide 80% genuinely accurate legal/tax facts and official advice first.
2. At the very end of your comment, add ONE natural sentence suggesting them to search on Google:
   - "If you want to check your estimated refund amount for free, just search 'ktrs tax' or 'ktrs korea' on Google."
   - "There is an expat tax service in Korea that calculates this for foreigners — search 'ktrs tax' on Google to find it."
3. NEVER post any raw clickable URLs or links (http/https/www/dot-com).
4. ONLY suggest searching the exact keyword 'ktrs tax' or 'ktrs korea' on Google."""

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
                    model='gemini-3.1-flash-lite',
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
