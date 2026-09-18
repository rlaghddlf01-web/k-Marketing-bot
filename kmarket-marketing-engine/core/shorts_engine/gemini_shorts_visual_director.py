# -*- coding: utf-8 -*-
"""
GeminiShortsVisualDirector - 🎬 [제미나이 기반 숏폼 올인원 실시간 디렉터]
- 시나리오 디렉터의 60대 테마를 분석하여:
  1) 최적의 8개국 타깃 언어(vi, uz, km, id, th, kk, tl, my) 자동 선택
  2) 테마 맞춤형 인물 프롬프트(성별, 나이, 의상, 작업환경/기숙사 배경) 자동 설계
  3) 10초 이상 여유 있는 호흡의 3단계 대본 창작 (자기소개+공감 -> 쉬운 90% 환급 -> 폰 시연 브릿지)
  4) 언어별 엄격한 단어 수 가드레일 (우즈베크어 14~16단어, 베트남어 20~24단어)로 수다쟁이 방지
  5) 테마 무드별 상/하단 박스 컬러 팔레트 및 글자 이탈 없는 자막 매칭
"""

import os
import json
import logging
import random
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_EASYTAX, LANGUAGES

logger = logging.getLogger("GeminiShortsVisualDirector")

# 🎯 8대 황금 타깃 국가 및 모국어 정의
GOLDEN_8_COUNTRIES = {
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "country": "Vietnam"},
    "uz": {"name": "Uzbek", "native": "O'zbek", "country": "Uzbekistan"},
    "km": {"name": "Khmer", "native": "ភាសាខ្មែរ", "country": "Cambodia"},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "country": "Indonesia"},
    "th": {"name": "Thai", "native": "ภาษาไทย", "country": "Thailand"},
    "kk": {"name": "Kazakh/Russian", "native": "Қазақша / Русский", "country": "Kazakhstan"},
    "tl": {"name": "Tagalog/English", "native": "Tagalog", "country": "Philippines"},
    "my": {"name": "Burmese", "native": "မြန်မာ", "country": "Myanmar"},
}

# 🎨 테마별 럭셔리 박스 컬러 팔레트 사전
THEME_PALETTES = {
    "gold_navy": {
        "name": "골드 & 딥네이비 (국세청 신뢰 & 공식 환급)",
        "top_box": {"fill": [255, 204, 0], "border": [255, 255, 255], "text": [15, 23, 42]},
        "bottom_box": {"fill": [11, 19, 43], "border": [255, 204, 0], "title": [255, 204, 0], "sub": [241, 245, 249]}
    },
    "emerald_navy": {
        "name": "에메랄드 그린 & 네이비 (감동 & 고향 방문/가족 사랑)",
        "top_box": {"fill": [16, 185, 129], "border": [255, 255, 255], "text": [255, 255, 255]},
        "bottom_box": {"fill": [15, 23, 42], "border": [52, 211, 153], "title": [52, 211, 153], "sub": [241, 245, 249]}
    },
    "crimson_gold": {
        "name": "크림슨 버건디 & 웜 골드 (5년 소멸시효 긴급 알림)",
        "top_box": {"fill": [225, 29, 72], "border": [255, 255, 255], "text": [255, 255, 255]},
        "bottom_box": {"fill": [24, 24, 27], "border": [251, 191, 36], "title": [251, 191, 36], "sub": [255, 255, 255]}
    },
    "cyber_cyan": {
        "name": "사이버 미드나잇 & 네온 사이언 (1분 실시간 계산기 실증)",
        "top_box": {"fill": [6, 182, 212], "border": [255, 255, 255], "text": [15, 23, 42]},
        "bottom_box": {"fill": [15, 23, 42], "border": [6, 182, 212], "title": [6, 182, 212], "sub": [241, 245, 249]}
    },
    "royal_purple": {
        "name": "로열 바이올렛 & 엠버 골드 (공단 선배의 90% 비법 전수)",
        "top_box": {"fill": [139, 92, 246], "border": [255, 255, 255], "text": [255, 255, 255]},
        "bottom_box": {"fill": [19, 16, 34], "border": [245, 158, 11], "title": [245, 158, 11], "sub": [241, 245, 249]}
    },
    "sunset_orange": {
        "name": "선셋 오렌지 & 다크 차콜 (꿈의 보상 & 연말정산 성공)",
        "top_box": {"fill": [249, 115, 22], "border": [255, 255, 255], "text": [255, 255, 255]},
        "bottom_box": {"fill": [23, 27, 36], "border": [249, 115, 22], "title": [249, 115, 22], "sub": [241, 245, 249]}
    }
}


class GeminiShortsVisualDirector:
    """제미나이 AI 기반 22초 숏폼 올인원 실시간 디렉팅 엔진"""

    def __init__(self):
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        if GEMINI_API_KEY_EASYTAX:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY_EASYTAX)
                logger.info("🎬 [GeminiShortsVisualDirector] Google GenAI 클라이언트 초기화 완료")
            except Exception as e:
                logger.warning(f"⚠️ [GeminiShortsVisualDirector] GenAI 초기화 실패: {e}")
                self.client = None
        else:
            logger.info("⚠️ [GeminiShortsVisualDirector] GEMINI_API_KEY_EASYTAX 미설정 -> 폴백 테마 모드")

    def generate_visual_direction(
        self,
        lang: Optional[str] = None,
        theme_info: Optional[Dict[str, Any]] = None,
        amount: int = 3100000,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        테마를 분석하여 언어 자동 선택, 10초 이상 여유 있는 립싱크 대본, 인물 프롬프트, 박스 비주얼을 실시간 생성
        (성별은 지정되지 않을 시 50:50 균등 확률로 남성/여성 자동 분배)
        """
        theme = theme_info or {}
        theme_name = theme.get("name", "한국 세금 90% 소득세 감면 및 환급")
        target = theme.get("target", "외국인 근로자")
        persona = theme.get("persona_type", "E-9/E-7 근로자")
        refund_krw = theme.get("refund_est", amount)
        refund_formatted = f"{refund_krw:,}"

        # 성별 50:50 균등 분배 (지정값 없으면 female / male 5:5 확률 선택)
        target_gender = str(gender).lower().strip() if gender and str(gender).lower().strip() in ["male", "female"] else random.choice(["female", "male"])

        # 언어 자동 선택 플래그
        is_auto_lang = not lang or lang == "auto" or lang not in GOLDEN_8_COUNTRIES
        lang_instruction = (
            "Select the SINGLE BEST matching country/language code from ['vi', 'uz', 'km', 'id', 'th', 'kk', 'tl', 'my'] that most strongly resonates with today's theme and Korean foreign worker demographics."
            if is_auto_lang else
            f"Use the designated target language code '{lang}'."
        )

        # 8대국 에스닉 앵커 가이드
        from core.shorts_engine.shorts_character_anchor_easytax import get_shorts_ethnic_positive
        ethnic_guide = get_shorts_ethnic_positive(lang) if not is_auto_lang else "authentic facial features matching selected country (strictly NOT East Asian/Chinese for Central Asian countries like Uzbekistan/Kazakhstan)"

        # 1. 제미나이 마스터 시스템 프롬프트 구성
        system_instruction = f"""
You are the world's best viral vertical video director (TikTok/Reels/Shorts) creating a high-converting 22-second marketing video for KTRS EasyTax (Easy Korean Tax Refund App for Foreign Workers).

[Today's Theme]: {theme_name}
[Target Audience]: {target} (Persona: {persona})
[Verified Legal Benefit]: Up to 90% income tax reduction under Korean tax regulations. Average refund: ₩{refund_formatted} KRW. 100% Native Language Mobile App. 0 Won upfront fee (100% success fee only after receiving refund into bank account).

[CRITICAL MARKETING PROPOSITION & MANDATORY CORE CONCEPTS (STRICT ENFORCEMENT)]:
The entire marketing video exists to solve ONE clear question for foreign workers in Korea:
"Can I get back the income taxes that were deducted from my monthly paychecks?" (월급에서 떼인 소득세 환급 / Tax refund of salary deductions)
1. MANDATORY: The speaker MUST explicitly state in their native language that this money is:
   - "TAXES DEDUCTED FROM MONTHLY SALARY" (월급에서 원천징수되어 떼인 세금)
   - "TAX REFUND RECEIVED FROM THE NATIONAL TAX SERVICE" (국세청에서 돌려받은 세금 환급)
2. STRICTLY PROHIBITED: NEVER simply say "I received money" or "3,680,000 won arrived in my account" without explicitly stating that it is TAX REFUND FROM SALARY DEDUCTIONS! If the viewer doesn't understand it is a tax refund of salary deductions, they will mistake it for a loan, bonus, lottery, or scam!
3. NATIVE LANGUAGE KEYWORD REQUIREMENTS:
   - Uzbek (uz): MUST include "oylikdan ushlab qolingan soliq" (tax deducted from monthly salary) AND "soliqni qaytarib oldim" / "soliq qaytarmasi" (got tax refund).
   - Vietnamese (vi): MUST include "tiền thuế bị trừ từ lương" (tax deducted from salary) AND "hoàn thuế" (tax refund).
   - Indonesian (id): MUST include "pajak yang dipotong dari gaji" AND "pengembalian pajak".
   - Russian/Kazakh (kk): MUST include "налог, удержанный с зарплаты" AND "возврат налога".
   - Tagalog (tl): MUST include "taxes deducted from salary" AND "tax refund".
   - Khmer (km): MUST include "ពន្ធកាត់ពីប្រាក់ខែ" AND "បង្វិលពន្ធ".
   - Thai (th): MUST include "ภาษีที่ถูกหักจากเงินเดือน" AND "เงินคืนภาษี".
   - Burmese (my): MUST include "လစာမှ ဖြတ်တောက်ခံရသော အခွန်" AND "အခွန်ပြန်အမ်းငွေ".

[Language Selection Instruction]:
{lang_instruction}

[MANDATORY ETHNICITY & FACIAL BONE STRUCTURE]:
{ethnic_guide}

[SCENE 1: 0s ~ 10s Human Actor Lip-Sync - FULL 10-SECOND CONTINUOUS SPEECH (81f + 81f)]:
The human actor scene is strictly composed of TWO 5-SECOND SHOTS (Shot 1: 0s~5s, Shot 2: 5s~10s) combined seamlessly into ONE 10.0-SECOND CONTINUOUS SCENE.
CRITICAL MANDATE: THE ACTOR MUST SPEAK VIBRANTLY AND CONTINUOUSLY ACROSS THE ENTIRE 10 SECONDS! ZERO IDLE STARING, ZERO DEAD SILENCE!
The speaker is ONE SINGLE foreign worker persona working in Korea (e.g. manufacturing/factory/construction E-9, E-7 worker).

CRITICAL STAGING & POSE (0s ~ 10s CONTINUOUS CONSISTENT POSE):
- The actor sits or stands comfortably in their clean dormitory room in Korea, HOLDING A SLEEK MODERN SMARTPHONE STEADILY IN ONE HAND AT CHEST/WAIST LEVEL WITH THE SCREEN FACING FORWARD TOWARDS THE CAMERA FROM THE VERY START (0s) TO THE VERY END (10s).
- The actor LOOKS DIRECTLY INTO THE CAMERA LENS AT ALL TIMES with attentive, sincere, friendly eye contact.
- THE PHONE AND HANDS REMAIN STEADY AND STILL (no rapid hand gestures, no waving or sudden raising of phone). All motion is natural speech lip sync and subtle head movement to guarantee 0% hand distortion or screen tearing!

[AVERAGE 20-SECOND FULL SCRIPT ARCHITECTURE - NATURAL HUMAN TEMPO (+0%)]:
Do NOT use artificial speedup. The speech must sound 100% natural, peer-to-peer, and trustworthy.
The script has an average total duration of ~20 seconds (18s ~ 22s depending on language characteristics):
1. `speech_hook_part1` (Shot 1: 0s ~ 5s, speaks for ~4.5s at +0% tempo to fill the 81 frames):
   Hooks viewer by directly asking about or mentioning the taxes deducted from monthly wages while working in Korea:
   - Uzbek (uz): 7 to 9 words (e.g., "Har oy oyligingizdan ushlab qolingan soliqni bilasizmi?")
   - Vietnamese (vi): 11 to 13 words (e.g., "Bạn có biết tiền thuế bị trừ từ lương hàng tháng có thể lấy lại?")
   - Russian/Kazakh (kk): 7 to 9 words (e.g., "Знаете ли вы, что налог, удержанный с зарплаты, можно вернуть?")
   - Indonesian (id): 8 to 10 words (e.g., "Tahu nggak kalau pajak yang dipotong dari gaji bisa diambil kembali?")
   - Tagalog (tl): 9 to 11 words (e.g., "Did you know you can get back taxes deducted from your monthly salary?")
   - Thai (th), Khmer (km), Burmese (my): 8 to 10 words
   STRICTLY PROHIBITED: NEVER mention tuition, students, studying abroad, universities! Only factory/workplace foreign worker persona!

2. `speech_hook_part2` (Shot 2: 5s ~ 10s, speaks for ~4.5s at +0% tempo):
   Excited tax refund receipt proof via KTRS app (MUST state {refund_formatted} won of salary tax refunded!):
   *NOTE: Numbers like {refund_formatted} take 4~5 words to pronounce in audio!*
   - Uzbek (uz): 7 to 9 words (e.g., "Men KTRS orqali oylikdan ushlab qolingan {refund_formatted} von soliqni qaytarib oldim!")
   - Vietnamese (vi): 11 to 13 words (e.g., "Tôi vừa được hoàn lại {refund_formatted} won tiền thuế từ lương qua app KTRS rồi!")
   - Russian/Kazakh (kk): 7 to 9 words (e.g., "Через KTRS я только что вернул {refund_formatted} вон налога с зарплаты!")
   - Indonesian (id): 9 to 11 words (e.g., "Saya baru saja terima pengembalian pajak gaji {refund_formatted} won lewat KTRS!")
   - Tagalog (tl): 9 to 11 words
   - Thai (th), Khmer (km), Burmese (my): 8 to 10 words
   *RESULT: Part 1 (~4.5s) + Part 2 (~4.5s) fills the entire 10-second human scene with zero awkward silence!*

3. `speech_app` (10s ~ End, speaks for ~8s to 11s over the App Simulation screen):
   AT EXACTLY 10.0 SECONDS, THE SCREEN SWITCHES TO THE KTRS LIVE MOBILE APP DEMO.
   THE EXACT SAME SPEAKER'S VOICE CONTINUES SEAMLESSLY OVER THE APP DEMO WITHOUT INTERRUPTION!
   Explains in native language how easy it is to calculate YOUR salary tax refund in 1 minute on mobile, 0 won upfront fee, and check via link below:
   - Uzbek (uz): 12 to 15 words (e.g., "Ilovada oylikni kiritib, qancha soliq qaytarilishini 1 daqiqada bepul hisoblang! Oldindan to'lov yo'q, quyidagi havoladan bepul tekshiring!")
   - Vietnamese (vi): 22 to 26 words (e.g., "Chỉ cần nhập lương vào app, tính ngay số tiền thuế được hoàn miễn phí trong 1 phút! Miễn phí ban đầu, bấm link bên dưới kiểm tra ngay!")
   - Russian/Kazakh (kk): 12 to 15 words
   - Indonesian (id) & Tagalog (tl): 18 to 22 words
   - Thai (th), Khmer (km), Burmese (my): 15 to 18 words
   *CRITICAL: As soon as speech_app finishes, the entire video immediately stops with zero trailing dead space!*

[ACTOR PERSONA & DIVERSE VISUAL SETTING GENERATION (Wan 2.1 T2I & Wan 2.2 S2V)]:
- MANDATORY ASSIGNED GENDER: "{target_gender.upper()}" (STRICT! Output "gender": "{target_gender}")
- actor_persona_name: Korean & native description matching "{target_gender}"
  * If female: authentic female name & role (e.g. Uzbek: "말리카 (26세, 화성 부품공장 2년차 / Malika)", Vietnamese: "흐엉 (25세, 안산 전자공장 / Hương)", etc.)
  * If male: authentic male name & role (e.g. Uzbek: "자수르 (28세, 반월공단 3년차 / Jasur)", Vietnamese: "투안 (27세, 구미 제조업 / Tuấn)", etc.)
- gender: MUST BE "{target_gender}"!

[DIVERSE DYNAMIC BACKGROUND MANDATE (CRITICAL)]:
Do NOT always use the same living room! Dynamically select the setting that best resonates with today's theme mood:
1. ✈️ Airport Terminal & Travel: "spacious modern international airport terminal departure lounge, travel luggage suitcase beside, ready to fly home to visit family with refund money" (Best for flight ticket, vacation, family remittance themes)
2. ☕ Aesthetic Modern Cafe: "warm sunlit quiet modern coffee shop lounge armchair, softly blurred cafe interior" (Best for 1-minute mobile check, weekend ease, tax tips)
3. 🏭 Industrial Factory & Workshop: "clean modern high-tech industrial assembly workshop or tidy plant breakroom, softly blurred automated machinery" (Best for manufacturing E-9, overtime tax reduction, plant workers)
4. 🏠 Cozy Modern Living Room & Studio: "warm bright modern studio apartment living room, neat minimalist desk, soft window daylight" (Best for dorm life, living alone, roommate stories)
5. 🎓 University Campus & Study Lounge: "bright quiet modern university library or study lounge" (Best for D-2 student part-time 3.3% tax refund)
*CRITICAL MANDATE: NEVER include 'in Korea' or 'in South Korea' in background_desc or character_desc to prevent AI ethnicity distortion! Just describe the setting itself naturally.*

- actor_outfit: neat realistic outfit matching the theme and chosen location (e.g. "stylish pastel casual t-shirt", "neat industrial polo work shirt", "comfortable travel jacket", "clean smart casual shirt")
- actor_location: Korean summary of the chosen diverse setting (e.g. "인천공항 출국장 라운지 (캐리어 지참)", "화성 산업단지 공장 휴게실", "안산 감성 카페 창가 좌석", "따뜻한 원룸 거실")
- character_desc: English prompt for Wan 2.1 T2I (ethnicity matching selected language, gender: "{target_gender}", age around 24~29, neat outfit, looking directly into camera lens with attentive eye contact, holding sleek smartphone naturally in one hand at waist level facing forward, lips completely closed together, mouth gently shut, strictly zero open mouth, absolutely zero teeth showing)
- background_desc: English prompt for the chosen diverse setting (e.g. airport departure lounge with luggage, sunny modern cafe table, clean industrial workshop breakroom, or cozy modern room with window light. NEVER write 'in Korea')
- s2v_motion_prompt: English prompt for Wan 2.2 S2V (e.g. "a friendly foreign {target_gender} worker sitting or standing comfortably in the scene, holding a smartphone steadily in one hand facing forward to camera, looking directly into camera lens with attentive eye contact, stable hands, still posture, speaking sincerely and naturally with clear lip sync and subtle natural head movement, no rapid hand gestures, clean realistic motion")

[CRITICAL AMOUNT & REAL PHOTO INTEGRITY MANDATE]:
- In speech_hook_part2, speech_hook, and bottom_step1_title, you MUST use the EXACT given refund amount "{refund_formatted}" won (e.g. "{refund_formatted} von" or "₩{refund_formatted}"). NEVER change this amount to 2,400,000 or any other number! It must match {refund_formatted} with 100% mathematical precision!
- In character_desc, strictly NEVER use beauty/glamour buzzwords like 'handsome', 'beautiful', 'model', 'gorgeous', 'chiseled', 'elegant'! Instead describe an everyday honest foreign worker with authentic friendly facial features, wearing comfortable civilian casual clothes, with raw unedited natural skin texture with real pores to guarantee a 100% real iPhone mobile photo with ZERO plastic/CGI look!

[OVERLAY BOX TEXTS & COLORS (STRICT ZERO OVERFLOW)]:
- top_header: Maximum 22 characters in native language (e.g., HOÀN 90% THUẾ • KTRS, 90% SOLIQ QAYTARISH • KTRS)
- bottom_step1_title: Maximum 25 characters (Scene 1 headline, MUST include "{refund_formatted}" AND specify TAX REFUND, e.g., {refund_formatted} VON SOLIQ QAYTARILDI, HOÀN {refund_formatted} WON THUẾ)
- bottom_step1_sub: Maximum 35 characters (Scene 1 subtitle, MUST state taxes deducted from monthly salary, e.g., Oylikdan ushlab qolingan soliqni tekshiring, Kiểm tra thuế bị trừ từ lương 1 phút)
- bottom_step2_title: Maximum 25 characters (Scene 2 headline, e.g., CHỌN LƯƠNG • TÍNH 1 PHÚT, OYLIKNI KIRITING • 1 DAQIQA)
- bottom_step2_sub: Maximum 35 characters (Scene 2 subtitle, e.g., NTS Hometax rasmiy xizmati, Trực tiếp liên kết NTS Hometax)
- cta_button_text: Maximum 18 characters (e.g., HOZIROQ TEKSHIRING >, KIỂM TRA MIỄN PHÍ >)
- palette_id: one of ['gold_navy', 'emerald_navy', 'crimson_gold', 'cyber_cyan', 'royal_purple', 'sunset_orange'] matching the theme mood.
- STRICTLY NO UNICODE EMOJIS (No 🏛️, 💰, ⚡ to avoid font corruption).

Return ONLY valid JSON matching this exact structure:
{{
  "selected_lang": "vi",
  "actor_persona_name": "...",
  "gender": "{target_gender}",
  "actor_outfit": "...",
  "actor_location": "...",
  "character_desc": "a friendly 25-year-old {target_gender} worker in neat work shirt, holding smartphone facing forward, looking directly into camera...",
  "background_desc": "warm cozy modern apartment room in Korea, soft ambient window daylight...",
  "s2v_motion_prompt": "a friendly {target_gender} worker holding smartphone steadily facing forward, looking directly into camera, speaking sincerely with clear lip sync, stable hands",
  "speech_hook_kr": "안녕하세요! 한국에서 일하는 ...",
  "speech_hook_part1": "...",
  "speech_hook_part2": "...",
  "speech_hook": "...",
  "speech_app": "...",
  "speech_cta": "...",
  "top_header": "...",
  "bottom_step1_title": "...",
  "bottom_step1_sub": "...",
  "bottom_step2_title": "...",
  "bottom_step2_sub": "...",
  "cta_button_text": "...",
  "palette_id": "gold_navy"
}}
"""

        # 2. 제미나이 호출 시도
        if self.client:
            models_to_try = ["gemini-flash-latest", "gemini-3.1-flash-lite"]
            for model_name in models_to_try:
                try:
                    logger.info(f"🤖 [GeminiShortsVisualDirector] 제미나이 올인원 실시간 디렉팅 호출 ({model_name}, 테마: {theme_name[:25]})...")
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=system_instruction
                    )
                    raw_text = res.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif raw_text.startswith("```"):
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()

                    data = json.loads(raw_text)

                    # 언어 결정
                    resolved_lang = data.get("selected_lang", "vi")
                    if resolved_lang not in GOLDEN_8_COUNTRIES:
                        resolved_lang = "vi" if is_auto_lang else lang

                    palette_id = data.get("palette_id", "gold_navy")
                    palette = THEME_PALETTES.get(palette_id, THEME_PALETTES["gold_navy"])

                    speech_hook_p1 = data.get("speech_hook_part1", "").strip()
                    speech_hook_p2 = data.get("speech_hook_part2", "").strip()
                    speech_hook = data.get("speech_hook", "").strip()

                    if not speech_hook_p1 or not speech_hook_p2:
                        from .s2v_clip_stitcher import S2VClipStitcher
                        speech_hook_p1, speech_hook_p2 = S2VClipStitcher.split_speech_into_two_parts(speech_hook)

                    if not speech_hook:
                        speech_hook = f"{speech_hook_p1} {speech_hook_p2}".strip()

                    # 🛡️ 금액 무결성 100% 강제 동기화 (LLM 숫자 왜곡 원천 차단)
                    import re
                    num_pattern = r'\b\d{1,3}(?:,\d{3})+\b|\b\d{6,8}\b'
                    for fn in re.findall(num_pattern, speech_hook_p2):
                        if fn.replace(",", "") != str(refund_krw):
                            logger.info(f"🔄 [금액 무결성 동기화] Shot 2 발화 금액 교정: {fn} -> {refund_formatted}")
                            speech_hook_p2 = speech_hook_p2.replace(fn, refund_formatted)
                    for fn in re.findall(num_pattern, speech_hook):
                        if fn.replace(",", "") != str(refund_krw):
                            speech_hook = speech_hook.replace(fn, refund_formatted)

                    bottom_s1_title = data.get("bottom_step1_title", f"ĐÃ NHẬN {refund_formatted} WON")
                    for fn in re.findall(num_pattern, bottom_s1_title):
                        if fn.replace(",", "") != str(refund_krw):
                            bottom_s1_title = bottom_s1_title.replace(fn, refund_formatted)

                    speech_hook_kr = data.get("speech_hook_kr", "").strip()
                    speech_app = data.get("speech_app", "").strip()
                    speech_cta = data.get("speech_cta", "").strip()
                    full_speech = f"{speech_hook} {speech_app} {speech_cta}".strip()

                    gender = data.get("gender", "male").lower()
                    actor_persona_name = data.get("actor_persona_name", f"{resolved_lang.upper()} 근로자")
                    actor_outfit = data.get("actor_outfit", "깔끔한 근무복")
                    actor_location = data.get("actor_location", "한국 거주지")
                    char_desc = data.get("character_desc", "")
                    bg_desc = data.get("background_desc", "")
                    s2v_motion = data.get("s2v_motion_prompt", "a friendly foreign worker sitting comfortably in a clean room, holding a smartphone steadily in one hand facing forward to camera, looking directly into camera lens with attentive eye contact, stable hands, still posture, speaking sincerely and naturally with clear lip sync and subtle natural head movement, no rapid hand gestures, clean realistic motion")

                    country_meta = GOLDEN_8_COUNTRIES.get(resolved_lang, GOLDEN_8_COUNTRIES["vi"])
                    country_name = country_meta["country"]

                    logger.info(f"✨ [GeminiShortsVisualDirector] 디렉팅 성공! 언어: {resolved_lang.upper()} ({country_name}) | 인물: {actor_persona_name} ({gender}) | 의상: {actor_outfit}")
                    logger.info(f"🎙️ [인사말 한국어]: {speech_hook_kr[:60]}...")
                    logger.info(f"⏱️ [5초 샷 1]: {speech_hook_p1}")
                    logger.info(f"⏱️ [5초 샷 2]: {speech_hook_p2}")
                    return {
                        "lang": resolved_lang,
                        "country_name": country_name,
                        "theme_name": theme_name,
                        "amount": refund_krw,
                        "amount_formatted": refund_formatted,
                        "gender": gender,
                        "actor_persona_name": actor_persona_name,
                        "actor_outfit": actor_outfit,
                        "actor_location": actor_location,
                        "character_desc": char_desc,
                        "background_desc": bg_desc,
                        "s2v_motion_prompt": s2v_motion,
                        "speech_hook_kr": speech_hook_kr,
                        "speech_hook_part1": speech_hook_p1,
                        "speech_hook_part2": speech_hook_p2,
                        "speech_hook": speech_hook,
                        "speech_app": speech_app,
                        "speech_cta": speech_cta,
                        "full_speech": full_speech,
                        "palette_id": palette_id,
                        "palette": palette,
                        "visual_direction": {
                            "top_header": data.get("top_header", "HOÀN 90% THUẾ • KTRS"),
                            "bottom_step1_title": bottom_s1_title,
                            "bottom_step1_sub": data.get("bottom_step1_sub", "Tra cứu hoàn thuế dalam 1 phút"),
                            "bottom_step2_title": data.get("bottom_step2_title", f"ƯỚC TÍNH {refund_formatted} WON"),
                            "bottom_step2_sub": data.get("bottom_step2_sub", "Liên kết NTS Hometax • Visa E-7, E-9"),
                            "domain_text": "ktrs-service.vercel.app",
                            "cta_button_text": data.get("cta_button_text", "KIỂM TRA MIỄN PHÍ >"),
                            "palette": palette
                        }
                    }
                except Exception as e:
                    logger.warning(f"⚠️ [GeminiShortsVisualDirector] {model_name} 호출 실패: {e}")
                    continue

        # 3. 폴백: 기본 템플릿 및 무작위 테마 팔레트 선택
        logger.info("ℹ️ [GeminiShortsVisualDirector] 폴백 모드 가동")
        resolved_lang = "vi" if is_auto_lang else lang
        palette_keys = list(THEME_PALETTES.keys())
        chosen_palette_id = random.choice(palette_keys)
        palette = THEME_PALETTES[chosen_palette_id]

        from core.gemini_shorts_copywriter import GeminiShortsCopywriter
        from config import LANGUAGES
        copywriter = GeminiShortsCopywriter(service_id="easytax")
        script_data = copywriter.generate_shorts_script(
            service_id="easytax",
            lang=resolved_lang,
            scenario=theme_info,
            refund_formatted=refund_formatted
        )
        speech_hook = script_data.get("hook_0_10s", "")
        speech_app = script_data.get("app_10_18s", "")
        speech_cta = script_data.get("cta_18_22s", "")
        full_speech = f"{speech_hook} {speech_app} {speech_cta}".strip()
        country_name = LANGUAGES.get(resolved_lang, {}).get("name", resolved_lang.upper())

        return {
            "lang": resolved_lang,
            "country_name": country_name,
            "theme_name": theme_name,
            "amount": refund_krw,
            "amount_formatted": refund_formatted,
            "gender": "female",
            "actor_persona_name": f"{resolved_lang.upper()} 근로자",
            "actor_outfit": "단정한 근무복",
            "actor_location": "한국 거주지",
            "character_desc": "",
            "background_desc": "",
            "s2v_motion_prompt": "a friendly foreign worker sitting comfortably in a clean room, holding a smartphone steadily in one hand facing forward to camera, looking directly into camera lens with attentive eye contact, stable hands, still posture, speaking sincerely and naturally with clear lip sync and subtle natural head movement, no rapid hand gestures, clean realistic motion",
            "speech_hook_kr": "한국에서 일하는 여러분! 세금 환급 꼭 받으세요!",
            "speech_hook": speech_hook,
            "speech_app": speech_app,
            "speech_cta": speech_cta,
            "full_speech": full_speech,
            "palette_id": chosen_palette_id,
            "palette": palette,
            "visual_direction": {
                "top_header": script_data.get("top_header", "90% INCOME TAX REFUND • KTRS"),
                "bottom_step1_title": script_data.get("bottom_step1_title", f"{refund_formatted} REFUND"),
                "bottom_step1_sub": script_data.get("bottom_step1_sub", "1-Minute Free Check"),
                "bottom_step2_title": script_data.get("bottom_step2_title", f"TAX REFUND {refund_formatted}"),
                "bottom_step2_sub": script_data.get("bottom_step2_sub", "National Tax Service"),
                "domain_text": "ktrs-service.vercel.app",
                "cta_button_text": script_data.get("cta_button_text", "KIỂM TRA MIỄN PHÍ >"),
                "palette": palette
            }
        }
