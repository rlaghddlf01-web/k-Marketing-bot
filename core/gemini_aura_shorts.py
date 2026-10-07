# -*- coding: utf-8 -*-
"""
EasyTaxGeminiShorts - 🎬 [헐리웃 마스터 영화감독 & 10대 바이럴 화법 AI 숏폼 대본 생성기]
- 헐리웃 최고의 바이럴 영화감독 & 방송 작가 페르소나 탑재
- 10대 바이럴 스토리텔링 화법 (친구 수다 / 억울함 고백 / 우편함 언박싱 / 공단 꿀팁 등) 무작위 로테이션
- 세법 팩트(조특법 30조/3.3% 환급) + 국세환급금통지서 + 지역/인물 맞춤형 100% 구어체 대본 & SNS 설명문 창작
"""

import json
import random
import logging
from typing import Dict, Any, Optional, List
from config import GEMINI_API_KEY_EASYTAX, LANGUAGES
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxGeminiShorts")

# 🎬 10대 바이럴 스토리텔링 화법 포맷
STORYTELLING_FORMATS: List[Dict[str, str]] = [
    {
        "id": "friend_casual_chat",
        "name": "친구와의 일상 수다 / 비하인드 토크형",
        "style_guide": "Start casually like talking to a close expat friend on a phone call or over dinner: 'Hey, did you check your bank account today? Look what just happened to Minh in Banwol...' Very natural, friendly, warm, and lively."
    },
    {
        "id": "hardship_emotional_confession",
        "name": "억울함 & 현실 고생 감정 고백형",
        "style_guide": "Start with genuine heartfelt emotion: 'I worked 12 hours overtime every day in Korea for 3 years, thinking all that deducted tax was lost forever... But it was my legal right to claim back!' High empathy and relief."
    },
    {
        "id": "insider_secret_hack",
        "name": "공단 선배의 비밀 폭로 / 꿀팁 전수형",
        "style_guide": "Start like revealing a hidden life hack: 'The #1 secret Korean industrial complex veterans NEVER tell newcomers! Under Article 30, you can slash 90% of your income tax...' Authoritative, insider knowledge tone."
    },
    {
        "id": "unboxing_refund_notice",
        "name": "기숙사 우편함 [국세환급금통지서] 언박싱형",
        "style_guide": "Start with suspenseful reality: 'I saw an official government envelope from the National Tax Service in my mailbox today and got scared thinking it was a fine! But when I opened it, it was an official Tax Refund Notice for ₩{refund_formatted} KRW!' Thrilling and real."
    },
    {
        "id": "student_fact_check",
        "name": "유학생 3.3% 아르바이트 팩트체크 / 사이다형",
        "style_guide": "Punchy and direct for young international students: 'Stop losing your 3.3% part-time tax! The Korean government actually refunds 100% of it for D-2 students.' Fast, smart, empowering."
    },
    {
        "id": "family_care_remittance",
        "name": "고향 부모님 집수리 & 가족 사랑 감동형",
        "style_guide": "Warm and touching narrative: 'Sending hard-earned money back home to help parents renovate the house or buy medicine... Receiving ₩{refund_formatted} KRW tax refund made that dream possible today.' Emotional and respectful."
    },
    {
        "id": "dream_reward_flight",
        "name": "꿈의 보상 / 고향행 비행기 티켓형",
        "style_guide": "Exciting and celebratory: 'After years of hard work, I booked my direct flight ticket back home without hesitation! Why? Because Korean tax law refunded me ₩{refund_formatted} KRW.' Uplifting and victorious."
    },
    {
        "id": "colleague_surprise_envy",
        "name": "옆자리 동료의 깜짝 비밀 / 부러움형",
        "style_guide": "Curious and engaging story: 'My coworker at the factory suddenly bought a brand new phone and treated everyone to dinner. When I asked how, he smiled and showed me his tax refund notice...' Story-driven curiosity."
    },
    {
        "id": "live_calculator_proof",
        "name": "3초 실시간 계산기 실증형",
        "style_guide": "High-tech and practical: 'Don't guess how much you're owed. In just 3 clicks on your phone, see your exact 5-year refund calculated legally by certified tax accountants.' Clear, logical, and trustworthy."
    },
    {
        "id": "urgent_deadline_alert",
        "name": "5년 소멸시효 마감 긴급 알림형",
        "style_guide": "Urgent and informative: 'Warning: Korean tax refunds expire permanently after 5 years! If you worked in 2020-2021, your money is about to vanish unless you claim it now.' High urgency, important civic advice."
    }
]

# 🎬 헐리웃 마스터 영화감독 골든 시스템 프롬프트
HOLLYWOOD_DIRECTOR_SYSTEM_PROMPT = """
너는 헐리웃 최고의 바이럴 영화감독이자 숏폼 콘텐츠의 거장이야. 
네 대본은 사람들을 스마트폰 숏폼(릴스/틱톡/쇼츠)에서 첫 1초 만에 미친 듯이 사로잡지. 
그리고 넌 절대로 매일 같은 뻔한 패턴이나 똑같은 안내 멘트를 쓰지 않아.
너에게 지정된 [오늘의 화법 스타일]을 100% 흡수하여, 실제 그 인물이 친구에게 말하듯 극도로 생생하고 유니크한 구어체 대본을 창작해!
"""


class EasyTaxGeminiShorts:
    """EasyTax 전용 헐리웃 마스터 영화감독 숏폼 비디오 대본 생성기"""
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
                logger.info("EasyTax 헐리웃 마스터 감독 Gemini Client 초기화 성공")
            except Exception as e:
                logger.warning(f"EasyTax 숏폼 Gemini 초기화 실패: {e}")
                self.client = None

    def generate_shorts_script(
        self,
        *args,
        target_lang: str = "ko",
        scenario_plan: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        10대 바이럴 스토리텔링 화법 중 하나를 적용하여 20초 시네마틱 숏폼 대본 & 맞춤 설명문 생성
        """
        if args and isinstance(args[-1], str) and len(args[-1]) == 2:
            target_lang = args[-1]
        lang_info = LANGUAGES.get(target_lang, LANGUAGES["ko"])

        plan = scenario_plan or {}
        theme_name = plan.get("theme_name", "한국 세금 환급 & 꿈의 실현")
        archetype_name = plan.get("archetype_name", "비행기 여행 & 휴가형")
        archetype_id = plan.get("archetype_id", "dream_travel_flight")
        visa_name = plan.get("visa_name", "외국인 근로자")
        local_spot = plan.get("local_spot_name", "전국")
        refund_amount = plan.get("typical_refund_krw", 3840000)
        refund_formatted = f"{refund_amount:,}"

        # 10대 화법 포맷 중 하나를 무작위 또는 테마 매칭 선정
        story_format = random.choice(STORYTELLING_FORMATS)
        style_guide = story_format["style_guide"].format(refund_formatted=refund_formatted)

        prompt = f"""{HOLLYWOOD_DIRECTOR_SYSTEM_PROMPT}

### YOUR DIRECTING MISSION TODAY:
Create an ultra-engaging, emotional, and 100% UNIQUE 20-second vertical short-form video script & bespoke social media description for expats in South Korea.

[Target Language]: {lang_info['name']} ({lang_info['native_name']})
[Target Persona]: {visa_name} in {local_spot}, South Korea
[Director Theme]: {theme_name} ({archetype_name})
[Refund Calculation]: ₩{refund_formatted} KRW (under Article 30 90% tax relief / 5-year retroactive refund)
[Assigned Storytelling Narrative Style]: {story_format['name']}
[Narrative Voice Guide]: {style_guide}

### DIRECTING RULES:
1. DO NOT use generic boilerplate sentences. Adopt the assigned narrative style ({story_format['name']}) completely!
2. Speak in 100% natural, colloquial, spoken {lang_info['name']} as if a real person is filming and talking naturally.
3. Feature the official National Tax Refund Notice (국세환급금통지서) and certified licensed tax accountants (공인 세무사).

Output STRICTLY JSON format with keys:
{{
  "hook_title": "Punchy, viral headline for video overlay in {lang_info['name']}",
  "story_format_used": "{story_format['name']}",
  "voiceover_text": "Complete 18-20s fluent, conversational, emotional voiceover in {lang_info['name']} fully embodying {story_format['name']}",
  "video_description": "Rich, multi-paragraph social media post description (150-200 words) written 100% fluently in {lang_info['name']}. It must vividly describe this specific character story in {local_spot}, explain the tax law refund of ₩{refund_formatted} KRW, give a clear CTA to check free in 3 minutes via the link, and maintain certified tax accountant credibility.",
  "scene_overlays": [
    {{
      "scene_idx": 1,
      "badge": "Short 2-4 word hook badge in {lang_info['name']}",
      "main_text": "Scene 1 punchy on-screen headline in {lang_info['name']} (max 30 chars)",
      "sub_text": "Scene 1 short subtitle in {lang_info['name']}"
    }},
    {{
      "scene_idx": 2,
      "badge": "Mobile banking badge in {lang_info['name']}",
      "main_text": "Deposit confirmed on-screen text in {lang_info['name']}",
      "sub_text": "+₩{refund_formatted} KRW"
    }},
    {{
      "scene_idx": 3,
      "badge": "Legal relief badge in {lang_info['name']}",
      "main_text": "Scene 3 emotional relief quote in {lang_info['name']}",
      "sub_text": "Scene 3 subtitle in {lang_info['name']}"
    }},
    {{
      "scene_idx": 4,
      "badge": "Dream reward badge in {lang_info['name']}",
      "main_text": "Scene 4 flight/reward headline in {lang_info['name']}",
      "sub_text": "Scene 4 subtitle in {lang_info['name']}"
    }},
    {{
      "scene_idx": 5,
      "badge": "GIẤY BÁO HOÀN THUẾ QUỐC GIA (NTS)",
      "main_text": "Scene 5 CTA button headline in {lang_info['name']}",
      "sub_text": "Check free in 3 min via link in bio"
    }}
  ],
  "cta_text": "Compelling CTA button text in {lang_info['name']}",
  "captions": ["Subtitle 1", "Subtitle 2", "Subtitle 3", "Subtitle 4"],
  "disclaimer": "Processed via certified licensed tax accountants under Korean tax law."
}}
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                res_json = json.loads(response.text)
                logger.info(f"🎬 [{lang_info['name'].upper()}] 헐리웃 거장 감독 [{story_format['name']}] 대본 & 맞춤 설명문 생성 성공!")
                return res_json
            except Exception as e:
                logger.error(f"EasyTax Gemini 숏폼 생성 에러: {e}")

        # Fallback (안전 폴백 대본)
        return {
            "hook_title": f"✈️ ₩{refund_formatted} Tax Refund: Flight Home",
            "story_format_used": story_format["name"],
            "voiceover_text": f"Foreign workers in Korea can get up to 90% income tax refund under Article 30! Over {refund_formatted} KRW deposited—grab your flight ticket home! Check 100% free in 3 minutes via link in bio.",
            "video_description": f"Are you living and working in {local_spot}, South Korea? Under Article 30 of the Restriction of Special Taxation Act, foreign workers can claim up to 90% income tax reduction for the past 5 years! Check your estimated refund of over {refund_formatted} KRW in just 3 minutes for free with certified tax accountants via the link in bio.",
            "scene1_voiceover": f"Did you know foreign workers in Korea get 90% tax relief? +₩{refund_formatted} KRW just deposited into your account!",
            "scene1_captions": [
                f"🏛️ 90% Income Tax Reduction (Article 30)",
                f"💬 +₩{refund_formatted} KRW Deposited!"
            ],
            "scene2_voiceover": "Book your flight ticket and travel home with peace of mind! Check your 5-year refund in 3 minutes with certified tax accountants via link in bio!",
            "scene2_captions": [
                "✈️ Book Flight Tickets With Refund Money!",
                "👉 Click Link in Bio to Check Free in 3 Min!"
            ],
            "captions": [
                f"🏛️ 90% Income Tax Reduction (Article 30)",
                f"💬 +₩{refund_formatted} KRW Deposited!",
                "✈️ Book Flight Tickets With Refund Money!",
                "👉 Click Link in Bio to Check Free in 3 Min!"
            ],
            "cta_text": "👉 Click link in bio to check free refund!",
            "disclaimer": "Processed via certified licensed tax accountants under Korean tax law."
        }
