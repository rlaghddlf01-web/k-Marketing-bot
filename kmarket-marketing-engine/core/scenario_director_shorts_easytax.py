"""
ScenarioDirectorShortsEasyTax - 💰 EasyTax 전용 9:16 실무 세무·감정 테마 숏폼 비디오 전담 시나리오 디렉터
- 6대 감정 테마 × 만 15~34세 청년 페르소나 매트릭스
- ★ [절대 규칙] 인물 사진 생성 시 100% 동양인(Asian / East Asian / Southeast Asian) 엄격 지정
"""

import random
from typing import Dict, Any, Optional
from config import LANGUAGES

LIFESTYLE_THEMES = [
    {
        "id": "travel_healing",
        "name": "여행/힐링형 (주말 휴가/비행기)",
        "action_prompt": "happy young Asian traveler with backpack walking at airport terminal or scenic nature, genuine smile, cinematic vlog 4k",
        "negative_prompt": "creepy smile, floating phone, distorted hands, extra fingers, cartoon, 3d render, indoor studio model, caucasian, white person, blonde hair",
        "hook_template": "travel"
    },
    {
        "id": "walking_home_happy",
        "name": "퇴근길 행복/해방감 (하루 일과 후 가벼운 발걸음)",
        "action_prompt": "smiling young Asian worker walking outdoor street at sunset, looking at smartphone with relieved happy expression, natural cinematic lighting",
        "negative_prompt": "creepy stare, floating limbs, deformed anatomy, fake mockup, studio portrait, caucasian, white person, blonde hair",
        "hook_template": "relief"
    },
    {
        "id": "shopping_gift",
        "name": "쇼핑/득템형 (전자제품/필요한 물건 구매)",
        "action_prompt": "young Asian adult holding new electronics package or shopping bags, smiling genuinely in modern urban street, 4k vertical",
        "negative_prompt": "bad hands, floating objects, fashion runway, distorted fingers, caucasian, white person, blonde hair",
        "hook_template": "shopping"
    },
    {
        "id": "family_remittance",
        "name": "가족 송금/효도형 (본국 가족과 영상통화)",
        "action_prompt": "young Asian person sitting comfortably, holding smartphone on video call, warm genuine emotional smile talking to family, cozy room",
        "negative_prompt": "creepy smile, floating phone, bad anatomy, deformed limbs, caucasian, white person, blonde hair",
        "hook_template": "family"
    },
    {
        "id": "bank_shock_joy",
        "name": "통장 입금 쇼크형 (예상치 못한 목돈 발견)",
        "action_prompt": "Asian person holding smartphone with two hands naturally close-up, looking at screen with pleasantly shocked excited smile, natural realistic",
        "negative_prompt": "six fingers, floating phone, disembodied hands, distorted screen, cartoon, caucasian, white person, blonde hair",
        "hook_template": "shock"
    },
    {
        "id": "friends_celebrate",
        "name": "친구들과 식사/파티형 (환급 꿀팁 공유)",
        "action_prompt": "young diverse Asian friends dining together at cozy restaurant, cheerful atmosphere laughing and checking smartphone together",
        "negative_prompt": "creepy stare, bad hands, floating objects, extra limbs, caucasian, white person, blonde hair",
        "hook_template": "friends"
    }
]

# 🎯 조특법 제30조 청년(만 15~34세) 동양인 숏폼/카드뉴스 페르소나 매트릭스
PERSONAS = [
    {"age_group": "20대 초반 (만 20~24세)", "gender": "male", "visa": "D-2", "visa_name": "동양인 유학생 (알바 3.3% 환급)", "typical_refund_krw": 950000},
    {"age_group": "20대 초반 (만 20~24세)", "gender": "female", "visa": "D-2", "visa_name": "동양인 유학생 (시간제 근로 소득세 환급)", "typical_refund_krw": 1150000},
    {"age_group": "20대 후반 (만 25~29세)", "gender": "male", "visa": "E-9", "visa_name": "동양인 제조/뿌리산업 근로자 (90% 감면)", "typical_refund_krw": 3840000},
    {"age_group": "20대 후반 (만 25~29세)", "gender": "female", "visa": "E-9", "visa_name": "동양인 제조/식품가공 근로자 (90% 감면)", "typical_refund_krw": 3450000},
    {"age_group": "20대 후반 (만 25~29세)", "gender": "male", "visa": "E-2", "visa_name": "동양계 외국인 강사 (조세조약 2년 면세)", "typical_refund_krw": 4200000},
    {"age_group": "30대 초반 (만 30~34세)", "gender": "male", "visa": "E-7", "visa_name": "동양인 IT/엔지니어 전문직 (5개년 소급)", "typical_refund_krw": 5200000},
    {"age_group": "30대 초반 (만 30~34세)", "gender": "female", "visa": "H-2", "visa_name": "동포/동양인 방문취업 근로자 (가족 인적공제)", "typical_refund_krw": 2800000}
]

class ScenarioDirectorShortsEasyTax:
    """EasyTax 숏폼 비디오 전담 시나리오 디렉터 (100% 동양인 인물 특화)"""
    def __init__(self):
        self.themes = LIFESTYLE_THEMES
        self.personas = PERSONAS

    def plan_daily_scenario(self, lang: str = "en") -> Dict[str, Any]:
        theme = random.choice(self.themes)
        persona = random.choice(self.personas)
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])

        # ★ 대표님 절대 수칙: 인물 사진 생성 시 반드시 동양인(Asian) 지정
        scene1_action = (
            f"cinematic authentic vertical 9:16 photo of a young Asian ({persona['gender']}) in South Korea holding smartphone, "
            f"{theme['action_prompt']}, pleasantly shocked emotional expression looking at bank deposit notification, natural cinematic lighting, 4k ultra-detailed"
        )

        scene2_action = (
            f"cinematic authentic vertical 9:16 photo of a young Asian ({persona['gender']}) in South Korea, "
            f"holding smartphone showing screen to camera with a confident reassuring warm smile, professional modern clean Korean street or cozy indoor background, 4k photorealistic"
        )

        negative_prompt = (
            f"{theme['negative_prompt']}, caucasian, white person, blonde hair, blue eyes, western model, non-asian, european look"
        )

        return {
            "service_id": "easytax",
            "theme_id": theme["id"],
            "theme_name": theme["name"],
            "hook_template": theme["hook_template"],
            "target_lang": lang,
            "lang_name": lang_info.get("name", "English"),
            "age_group": persona["age_group"],
            "gender": persona["gender"],
            "visa": persona["visa"],
            "visa_name": persona["visa_name"],
            "typical_refund_krw": persona["typical_refund_krw"],
            "refund_amount_krw": persona["typical_refund_krw"],
            "duration_sec": 18,
            "scenes": [
                {
                    "scene_idx": 1,
                    "name": "Hook & Bank Deposit Shock",
                    "duration_sec": 9,
                    "action_prompt": scene1_action
                },
                {
                    "scene_idx": 2,
                    "name": "Trust Facts & Profile CTA",
                    "duration_sec": 9,
                    "action_prompt": scene2_action
                }
            ],
            "action_prompt": scene1_action,
            "scene1_action_prompt": scene1_action,
            "scene2_action_prompt": scene2_action,
            "negative_prompt": negative_prompt
        }
