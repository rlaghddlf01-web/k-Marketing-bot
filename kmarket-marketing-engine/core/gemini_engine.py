import os
import json
import logging
from typing import Optional, List, Dict, Any
from config import GEMINI_API_KEY, DATA_DIR, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("GeminiEngine")

class GeminiEngine:
    """
    Gemini 17개국 다국어 카피라이팅 & Few-Shot 자가학습 엔진
    (팩트 가드레일 엄격 준수 + 고득점 모범사례 자동 주입)
    """
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()
        self.easytax_facts = self._load_json(DATA_DIR / "easytax_rules.json")
        self.kmarket_facts = self._load_json(DATA_DIR / "kmarket_items.json")

    def _init_gemini(self):
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"Gemini Client 초기화 실패: {e}")
                self.client = None
        else:
            logger.info("GEMINI_API_KEY 미설정 -> 템플릿 기반 자가 생성 모드 가동")

    def _load_json(self, path) -> Any:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_reddit_response(self, post_title: str, post_body: str, 
                                 service_id: str, service_data: Dict[str, Any], 
                                 target_lang: str = "en", landing_url: str = "") -> str:
        """
        레딧 질문에 대한 80% 팩트 정보 + 20% 소프트 랜딩 댓글 생성 (Few-Shot 자가학습 주입)
        """
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["en"])
        few_shots = self.supabase_mgr.fetch_golden_few_shots(service_id, target_lang, min_score=80.0, limit=2)
        
        few_shot_prompt = ""
        if few_shots:
            few_shot_prompt = "\n\n### [Golden High-Performing Reference Examples (Mimic this natural, helpful tone)]:\n"
            for idx, sample in enumerate(few_shots, 1):
                few_shot_prompt += f"Example {idx}:\n{sample}\n\n"

        fact_context = ""
        if service_id == "easytax":
            fact_context = f"\n[Official Korean Tax Facts for Expats]: {json.dumps(self.easytax_facts, ensure_ascii=False)}"
        elif service_id == "kmarket":
            fact_context = f"\n[Real Verified Marketplace Listings]: {json.dumps(self.kmarket_facts[:3], ensure_ascii=False)}"

        prompt = f"""
You are a helpful and experienced expat in South Korea answering a Reddit question from a fellow foreigner.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Target Service]: {service_data.get('name')}
[Official Landing URL]: {landing_url}
{fact_context}
{few_shot_prompt}

[Reddit Post Title]: {post_title}
[Reddit Post Content]: {post_body}

### CRITICAL RULES (STRICT DATA INTEGRITY & ANTI-BAN):
1. Write 100% fluently in {lang_info['name']}.
2. 80% of the response MUST be genuine, highly practical, and helpful advice answering their specific situation based on real Korean regulations.
3. NEVER invent fake laws, benefits, or money amounts. Only use verified facts.
4. The remaining 20% should be a gentle, natural organic mention (Soft CTA) of the service ({service_data.get('name')}) as a helpful expat community resource, without raw http/https URLs to prevent AutoModerator bot filters.
5. Do NOT sound like an aggressive advertisement or bot. Use casual, empathetic community tone.
"""

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API 호출 에러: {e}")

        # Fallback Template
        return self._generate_fallback_reddit_reply(post_title, service_id, service_data, target_lang, landing_url)

    def generate_shorts_script(self, service_id: str, service_data: Dict[str, Any], target_lang: str = "ko") -> Dict[str, Any]:
        """
        17개국 숏폼 대본 생성 (후킹 3초 -> 핵심 팩트/스토리 20초 -> 해결책 CTA 7초)
        """
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])
        few_shots = self.supabase_mgr.fetch_golden_few_shots(service_id, target_lang, min_score=80.0, limit=1)

        few_shot_text = f"\n[Top Performing Script Style]:\n{few_shots[0]}" if few_shots else ""

        fact_summary = ""
        if service_id == "easytax":
            fact_summary = """
- 조세특례제한법 제30조: E-9 비전문취업 근로자 중소기업 소득세 최대 90% 감면 (연 200만원 한도, 5년간).
- D-2 유학생 아르바이트 3.3% 원천징수 세금 전액 환급.
- 최근 5개년도(2020~2025) 누락된 연말정산·월세 세액공제 전액 소급 환급.
- 외국인등록증 사진 1장 업로드 시 Gemini AI OCR로 3초 자동인식, 카카오/PASS 3분 무료 조회.
"""
        elif service_id == "kmarket":
            fact_summary = """
- 0원 무료 나눔(Free Giveaways): 졸업/귀국 유학생 및 근로자의 침대, 책상, 전자레인지 등 $0 나눔.
- 원클릭 무빙 아웃 세일(Moving Sale): 방 전체 살림(가구+가전) 일괄 처분.
- 17개국 실시간 양방향 번역 채팅: 모국어로 대화해도 한국인/타국인과 자동 번역 소통.
- AI 안티스캠(Anti-Scam) 탑재로 선입금/사기 100% 차단 및 외국인등록증 실명 인증.
"""

        prompt = f"""
Create a viral 30-second vertical short-form video script for foreign expats living in South Korea.
[Service]: {service_data.get('name')} - {service_data.get('description')}
[Language]: {lang_info['name']} ({lang_info['native_name']})
[Verified Core Facts & Legal Benefits to Highlight]:
{fact_summary}
{few_shot_text}

### CRITICAL ANTI-BAN & FINANCIAL COMPLIANCE RULES (MANDATORY):
1. NO financial scam/phishing triggers: NEVER use words like 'free instant cash', 'easy money', or 'give away funds'.
2. Educational/Informational Frame: Frame the script as an official educational guide regarding Korean Tax Law (Article 30 Restriction of Special Taxation Act) & legal expat rights.
3. Trust & Safety: Clearly mention that the calculation is 100% free with NO upfront fees, handled via certified licensed tax accountants.
4. Professional & Empathetic Community Tone: Speak like a knowledgeable expat peer.

### SCRIPT STRUCTURE:
1. Hook (0-3s): Informative question or surprising regulation fact for expats in Korea.
2. Story/Proof (3-23s): Explain the real legal benefit / marketplace feature with concrete facts.
3. Solution & CTA (23-30s): Clear direction to check the free official tool in bio.

Output JSON format strictly with keys:
"hook_title": (punchy informative headline for screen overlay),
"voiceover_text": (entire 30s speech fluently written in {lang_info['name']}),
"captions": [(array of 3-5 short sentences for on-screen text overlays)],
"cta_text": (closing call to action in {lang_info['name']}),
"disclaimer": (official legal disclaimer in {lang_info['name']}: "Processed via certified tax agents under Korean tax law. Actual refund amounts depend on individual income records.")
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
                logger.error(f"Gemini 숏폼 대본 생성 실패: {e}")

        # Fallback Template
        if service_id == "easytax":
            if target_lang == "vi":
                return {
                    "hook_title": "🇻🇳 Bạn đã nhận lại 90% thuế tại Hàn Quốc chưa?",
                    "voiceover_text": "Người lao động visa E-9 và du học sinh D-2 tại Hàn Quốc được giảm tới 90% thuế thu nhập theo luật. Hãy kiểm tra hoàn thuế 5 năm qua chỉ trong 3 phút với EasyTax!",
                    "captions": ["Giảm tới 90% thuế cho visa E-9", "Hoàn lại 100% thuế 3.3% cho D-2", "Tra cứu miễn phí chỉ 3 phút với EasyTax"],
                    "cta_text": "Nhấn vào link bio để nhận tiền ngay!"
                }
            elif target_lang == "zh":
                return {
                    "hook_title": "🇨🇳 在韩留学生&打工人必看！90%退税福利",
                    "voiceover_text": "在韩国打工被扣的3.3%所得税，以及E-9中小企业90%税金减免，近5年的税金都能全额退回！只需3分钟用EasyTax免费查询！",
                    "captions": ["在韩打工3.3%退税", "E-9企业90%税金减免", "近5年多交税金全额退回"],
                    "cta_text": "点击主页链接立即免费查询！"
                }
            else:
                return {
                    "hook_title": "💰 Did you claim back your Korean taxes?",
                    "voiceover_text": "Expats and students in Korea can legally claim back up to 90% of income tax and all 3.3% withholding taxes from the past 5 years. Check your free refund in 3 mins on EasyTax!",
                    "captions": ["Claim back taxes in Korea", "Up to 90% reduction for SME workers", "Free 3-min AI check on EasyTax"],
                    "cta_text": "Link in bio to claim now!"
                }
        else:
            if target_lang == "vi":
                return {
                    "hook_title": "🎁 Đồ dùng 0 Won miễn phí tại Hàn Quốc!",
                    "voiceover_text": "Chuyển nhà hay tốt nghiệp về nước? Nhận ngay giường, bàn học, lò vi sóng 0 Won hoặc thanh lý toàn bộ đồ đạc với K-Market. Có chat dịch tự động tiếng Việt!",
                    "captions": ["Nhận đồ 0 Won miễn phí", "Thanh lý chuyển nhà trọn gói", "Chat dịch tự động tiếng Việt"],
                    "cta_text": "Nhấn link bio để xem đồ ngay!"
                }
            else:
                return {
                    "hook_title": "🎁 $0 Free Giveaways & Moving Sale in Korea!",
                    "voiceover_text": "Moving out or arriving in Korea? Grab $0 free furniture and appliances from verified neighbors on K-Market with real-time 17-language chat translation!",
                    "captions": ["$0 Free giveaways near you", "1-click moving out sale", "17 languages auto-translated chat"],
                    "cta_text": "Check link in bio!"
                }

    def _generate_fallback_reddit_reply(self, title: str, service_id: str, service_data: Dict[str, Any], lang: str, url: str) -> str:
        if service_id == "easytax":
            return (
                "In South Korea, under Article 30 of the Restriction of Special Taxation Act, foreign workers on E-9/H-2 visas "
                "at SMEs can legally get up to a 90% income tax reduction, and D-2 students can claim back 100% of their 3.3% withholding tax "
                "retroactively for the past 5 years (2020-2025).\n\n"
                "You can check your exact eligible refund in 3 minutes by searching 'EasyTax Korea' on Google. "
                "The tool uses certified tax accountants so you don't leave your hard-earned money behind!"
            )
        else:
            return (
                "If you're setting up your room in Korea or moving out soon, check out the local expat community boards.\n\n"
                "Many graduating students give away desks, microwaves, and mini-fridges for 0 KRW (free giveaway). "
                "You can browse verified 0 KRW items and moving-out packages with real-time automatic 17-language translation by searching 'K-Market' on Google. Good luck settling in!"
            )
