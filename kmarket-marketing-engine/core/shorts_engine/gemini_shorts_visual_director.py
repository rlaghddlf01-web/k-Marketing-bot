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
        amount: int = 3100000
    ) -> Dict[str, Any]:
        """
        테마를 분석하여 언어 자동 선택, 10초 이상 여유 있는 립싱크 대본, 인물 프롬프트, 박스 비주얼을 실시간 생성
        """
        theme = theme_info or {}
        theme_name = theme.get("name", "한국 세금 90% 소득세 감면 및 환급")
        target = theme.get("target", "외국인 근로자")
        persona = theme.get("persona_type", "E-9/E-7 근로자")
        refund_krw = theme.get("refund_est", amount)
        refund_formatted = f"{refund_krw:,}"

        # 언어 자동 선택 플래그
        is_auto_lang = not lang or lang == "auto" or lang not in GOLDEN_8_COUNTRIES
        lang_instruction = (
            "Select the SINGLE BEST matching country/language code from ['vi', 'uz', 'km', 'id', 'th', 'kk', 'tl', 'my'] that most strongly resonates with today's theme and Korean foreign worker demographics."
            if is_auto_lang else
            f"Use the designated target language code '{lang}'."
        )

        # 1. 제미나이 마스터 시스템 프롬프트 구성
        system_instruction = f"""
You are the world's best viral vertical video director (TikTok/Reels/Shorts) creating a high-converting 22-second marketing video for KTRS EasyTax (Easy Korean Tax Refund App for Foreign Workers).

[Today's Theme]: {theme_name}
[Target Audience]: {target} (Persona: {persona})
[Verified Legal Benefit]: Up to 90% income tax reduction under Korean tax regulations. Average refund: ₩{refund_formatted} KRW. 100% Native Language Mobile App. 0 Won upfront fee (100% success fee only after receiving refund into bank account).

[Language Selection Instruction]:
{lang_instruction}

[SCENE 1: 0s ~ 11s Human Actor Lip-Sync - CRITICAL PACING & STORYLINE]:
The actor is speaking directly to the camera for 10 to 11 seconds.
To prevent the actor from speaking too fast like a chatterbox ("수다쟁이"), strictly follow this 3-sentence calm, friendly peer-to-peer structure:
- Sentence 1 (Warm greeting & empathy matching theme):
  Introduce oneself by a native name and specific workplace/role in Korea matching today's theme, and empathize with the tax deducted from the monthly salary.
  (e.g., "Hello, I am [Native Name], working at [Workplace/City]! Every month when getting paid, were you sad about the deducted tax?")
- Sentence 2 (Super-simple legal fact & money proof without rigid jargon):
  Do NOT use rigid jargon like 'Article 30'. Explain easily: under Korean law, foreign workers can get back up to 90% of taxes! I also received ₩{refund_formatted} KRW straight into my account via KTRS!
- Sentence 3 (App screen transition bridge):
  "How did I get it on my phone in 1 minute? Let me show you on my screen right now!"

[STRICT WORD COUNT LIMITS FOR SPEECH_HOOK TO ENSURE 10~11 SECONDS CALM PACE]:
- If Uzbek (uz) or Russian/Kazakh (kk): STRICT MAXIMUM 14 to 16 WORDS! (Uzbek/Russian words have many syllables; NEVER exceed 16 words so the voice speaks calmly and deeply without rushing).
- If Khmer (km), Thai (th), Burmese (my): STRICT MAXIMUM 16 to 19 WORDS!
- If Vietnamese (vi), Tagalog (tl), Indonesian (id): STRICT MAXIMUM 20 to 24 WORDS!

[ACTOR PERSONA & VISUAL PROMPT GENERATION (Wan 2.1 T2I)]:
- gender: "male" or "female" (must match the character and voice naturally)
- character_desc: English prompt for T2I model (ethnicity matching selected language, age around 24~30, neat workplace outfit matching theme like industrial polo shirt or university hoodie, natural authentic face, closed lips)
- background_desc: English prompt for background (cozy modern dormitory room, Seoul apartment, or tidy living space with soft indoor lighting matching theme)

[OVERLAY BOX TEXTS & COLORS (STRICT ZERO OVERFLOW)]:
- top_header: Maximum 22 characters in native language (e.g., HOÀN 90% THUẾ • KTRS)
- bottom_step1_title: Maximum 25 characters (Scene 1 headline, e.g., ĐÃ NHẬN 3.840.000 WON)
- bottom_step1_sub: Maximum 35 characters (Scene 1 subtitle)
- bottom_step2_title: Maximum 25 characters (Scene 2 headline, e.g., CHỌN LƯƠNG • TÍNH 1 PHÚT)
- bottom_step2_sub: Maximum 35 characters (Scene 2 subtitle)
- cta_button_text: Maximum 18 characters (e.g., KIỂM TRA MIỄN PHÍ >)
- palette_id: one of ['gold_navy', 'emerald_navy', 'crimson_gold', 'cyber_cyan', 'royal_purple', 'sunset_orange'] matching the theme mood.
- STRICTLY NO UNICODE EMOJIS (No 🏛️, 💰, ⚡ to avoid font corruption).

Return ONLY valid JSON matching this exact structure:
{{
  "selected_lang": "vi",
  "gender": "male",
  "character_desc": "a friendly 27-year-old Vietnamese male factory worker in neat dark work shirt...",
  "background_desc": "warm cozy modern apartment room in Ansan, soft ambient window daylight...",
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

                    speech_hook = data.get("speech_hook", "").strip()
                    speech_app = data.get("speech_app", "").strip()
                    speech_cta = data.get("speech_cta", "").strip()
                    full_speech = f"{speech_hook} {speech_app} {speech_cta}".strip()

                    gender = data.get("gender", "male").lower()
                    char_desc = data.get("character_desc", "")
                    bg_desc = data.get("background_desc", "")

                    country_meta = GOLDEN_8_COUNTRIES.get(resolved_lang, GOLDEN_8_COUNTRIES["vi"])
                    country_name = country_meta["country"]

                    logger.info(f"✨ [GeminiShortsVisualDirector] 제미나이 디렉팅 성공! 언어: {resolved_lang.upper()} ({country_name}), 성별: {gender}, 팔레트: {palette['name']}")
                    return {
                        "lang": resolved_lang,
                        "country_name": country_name,
                        "theme_name": theme_name,
                        "amount": refund_krw,
                        "amount_formatted": refund_formatted,
                        "gender": gender,
                        "character_desc": char_desc,
                        "background_desc": bg_desc,
                        "speech_hook": speech_hook,
                        "speech_app": speech_app,
                        "speech_cta": speech_cta,
                        "full_speech": full_speech,
                        "palette_id": palette_id,
                        "palette": palette,
                        "visual_direction": {
                            "top_header": data.get("top_header", "HOÀN 90% THUẾ • KTRS"),
                            "bottom_step1_title": data.get("bottom_step1_title", f"ĐÃ NHẬN {refund_formatted} WON"),
                            "bottom_step1_sub": data.get("bottom_step1_sub", "Tra cứu hoàn thuế trong 1 phút"),
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

        from .shorts_scenario_script_director import ShortsScenarioScriptDirector
        base_cfg = ShortsScenarioScriptDirector.SCRIPTS_22S.get(resolved_lang, ShortsScenarioScriptDirector.SCRIPTS_22S["vi"])
        full_speech = f"{base_cfg['hook_0_10s']} {base_cfg['app_10_18s']} {base_cfg['cta_18_22s']}"

        return {
            "lang": resolved_lang,
            "country_name": base_cfg["country_name"],
            "theme_name": theme_name,
            "amount": refund_krw,
            "amount_formatted": refund_formatted,
            "gender": "female",
            "character_desc": "",
            "background_desc": "",
            "speech_hook": base_cfg["hook_0_10s"],
            "speech_app": base_cfg["app_10_18s"],
            "speech_cta": base_cfg["cta_18_22s"],
            "full_speech": full_speech,
            "palette_id": chosen_palette_id,
            "palette": palette,
            "visual_direction": {
                "top_header": base_cfg["top_header"],
                "bottom_step1_title": base_cfg["bottom_step1_title"],
                "bottom_step1_sub": base_cfg["bottom_step1_sub"],
                "bottom_step2_title": base_cfg["bottom_step2_title"],
                "bottom_step2_sub": base_cfg["bottom_step2_sub"],
                "domain_text": "ktrs-service.vercel.app",
                "cta_button_text": base_cfg.get("cta_button_text", "KIỂM TRA MIỄN PHÍ >"),
                "palette": palette
            }
        }
