"""
ScenarioDirector - [17개국 × 남녀 × 만15~34세 나이별 × 6대 감정 테마 × 스마트폰 안전 가드레일] 전담 기획 엔진
- 조세특례제한법 제30조 청년(만 15~34세) 기준 완벽 준수
- 언어별, 국적별, 성별, 나이대별 페르소나 자동 매트릭스 생성
- 6대 라이프스타일 감정 테마 (여행, 퇴근길 행복, 쇼핑 득템, 가족 송금, 통장 쇼크, 친구 축하)
- 스마트폰 공중부양/손가락 왜곡/조잡한 UI 차단 안전 쿼리 엔진
"""

import random
import logging
from typing import Dict, Any, List, Optional
from config import LANGUAGES

logger = logging.getLogger("ScenarioDirector")

# 🎯 6대 라이프스타일 & 감정 테마 정의
LIFESTYLE_THEMES = [
    {
        "id": "travel_healing",
        "name": "여행/힐링형 (주말 휴가/비행기)",
        "action_prompt": "happy young traveler with backpack walking at airport terminal or scenic nature, genuine smile, cinematic vlog 4k",
        "negative_prompt": "creepy smile, floating phone, distorted hands, extra fingers, cartoon, 3d render, indoor studio model",
        "hook_template": "travel"
    },
    {
        "id": "walking_home_happy",
        "name": "퇴근길 행복/해방감 (하루 일과 후 가벼운 발걸음)",
        "action_prompt": "smiling young worker walking outdoor street at sunset, looking at smartphone with relieved happy expression, natural cinematic lighting",
        "negative_prompt": "creepy stare, floating limbs, deformed anatomy, fake mockup, studio portrait",
        "hook_template": "relief"
    },
    {
        "id": "shopping_gift",
        "name": "쇼핑/득템형 (전자제품/필요한 물건 구매)",
        "action_prompt": "young adult holding new electronics package or shopping bags, smiling genuinely in modern urban street, 4k vertical",
        "negative_prompt": "bad hands, floating objects, fashion runway, distorted fingers",
        "hook_template": "shopping"
    },
    {
        "id": "family_remittance",
        "name": "가족 송금/효도형 (본국 가족과 영상통화)",
        "action_prompt": "young person sitting comfortably, holding smartphone on video call, warm genuine emotional smile talking to family, cozy room",
        "negative_prompt": "creepy smile, floating phone, bad anatomy, deformed limbs",
        "hook_template": "family"
    },
    {
        "id": "bank_shock_joy",
        "name": "통장 입금 쇼크형 (예상치 못한 목돈 발견)",
        "action_prompt": "person holding smartphone with two hands naturally close-up, looking at screen with pleasantly shocked excited smile, natural realistic",
        "negative_prompt": "six fingers, floating phone, disembodied hands, distorted screen, cartoon",
        "hook_template": "shock"
    },
    {
        "id": "friends_celebrate",
        "name": "친구들과 식사/파티형 (환급 꿀팁 공유)",
        "action_prompt": "young diverse friends dining together at cozy restaurant, cheerful atmosphere laughing and checking smartphone together",
        "negative_prompt": "creepy stare, bad hands, floating objects, extra limbs",
        "hook_template": "friends"
    }
]

# 🎯 조특법 제30조 기준 만 15세~34세 타깃 페르소나 매트릭스
AGE_GENDER_PERSONAS = [
    {
        "age_group": "20대 초반 (만 20~24세)",
        "gender": "male",
        "visa": "D-2",
        "visa_name": "유학생 (알바 3.3% 환급)",
        "typical_refund_krw": 950000,
        "persona_desc": "22-year-old male university international student in South Korea"
    },
    {
        "age_group": "20대 초반 (만 20~24세)",
        "gender": "female",
        "visa": "D-2",
        "visa_name": "유학생 (시간제 근로 소득세 환급)",
        "typical_refund_krw": 1150000,
        "persona_desc": "21-year-old female college student studying in South Korea"
    },
    {
        "age_group": "20대 후반 (만 25~29세)",
        "gender": "male",
        "visa": "E-9",
        "visa_name": "제조/뿌리산업 근로자 (90% 감면)",
        "typical_refund_krw": 3840000,
        "persona_desc": "27-year-old male skilled workforce in Korean industrial complex"
    },
    {
        "age_group": "20대 후반 (만 25~29세)",
        "gender": "female",
        "visa": "E-9",
        "visa_name": "제조/식품가공 근로자 (90% 감면)",
        "typical_refund_krw": 3450000,
        "persona_desc": "26-year-old female diligent factory workforce in South Korea"
    },
    {
        "age_group": "30대 초반 (만 30~34세)",
        "gender": "male",
        "visa": "E-7",
        "visa_name": "IT/엔지니어 전문직 (5개년 소급)",
        "typical_refund_krw": 4500000,
        "persona_desc": "32-year-old male tech engineer / professional working in South Korea"
    },
    {
        "age_group": "30대 초반 (만 30~34세)",
        "gender": "female",
        "visa": "H-2",
        "visa_name": "서비스/물류 근로자 (연말정산 소급)",
        "typical_refund_krw": 2900000,
        "persona_desc": "31-year-old female service/logistics professional in South Korea"
    }
]

# 🎯 17개국 인종/인구통계 키워드 매핑
DEMOGRAPHIC_KEYWORDS = {
    "vi": "Vietnamese Southeast Asian",
    "uz": "Central Asian Uzbek",
    "zh": "East Asian Chinese",
    "en": "International Expat student/worker",
    "mn": "Mongolian East Asian",
    "ru": "Russian / Central Asian Koryo-saram",
    "th": "Thai Southeast Asian",
    "id": "Indonesian Southeast Asian",
    "km": "Cambodian Khmer Southeast Asian",
    "ne": "Nepali South Asian",
    "tl": "Filipino Southeast Asian",
    "my": "Burmese Southeast Asian",
    "bn": "Bangladeshi South Asian",
    "ja": "Japanese East Asian",
    "es": "Hispanic Latin American",
    "ar": "Middle Eastern Arab",
    "ko": "Korean Multicultural youth"
}


class ScenarioDirector:
    """
    🎬 17개국 × 성별 × 만15~34세 나이 × 6대 감정 테마 시나리오 전담 디렉터
    """
    def __init__(self):
        pass

    def plan_daily_scenario(self, lang: str = "vi", service_id: str = "easytax") -> Dict[str, Any]:
        """
        매일 완전히 새로운 고전환 숏폼 기획안(페르소나 + 감정테마 + Pexels 비디오 검색 쿼리 + 안전 가드레일) 1개 생성
        """
        # 1. 감정/상황 테마 선택 (6개 중 1개)
        theme = random.choice(LIFESTYLE_THEMES)

        # 2. 만 15~34세 청년 페르소나 선택 (6개 중 1개)
        persona = random.choice(AGE_GENDER_PERSONAS)

        # 3. 국적/인종 키워드
        demo_str = DEMOGRAPHIC_KEYWORDS.get(lang, "International Expat")

        # 4. 스마트폰 왜곡 및 이상한 모델 차단 정밀 Pexels 비디오 검색 쿼리 조립
        if theme["id"] == "travel_healing":
            video_query = f"{demo_str} happy traveler vertical"
        elif theme["id"] == "walking_home_happy":
            video_query = f"{demo_str} person walking outdoor phone smiling"
        elif theme["id"] == "family_remittance":
            video_query = f"{demo_str} video call phone smiling family"
        elif theme["id"] == "bank_shock_joy":
            video_query = f"{demo_str} person checking phone excited shock"
        elif theme["id"] == "shopping_gift":
            video_query = f"{demo_str} person carrying shopping bags street"
        else:
            video_query = f"{demo_str} friends dining restaurant cheerful"

        scenario_plan = {
            "lang": lang,
            "service_id": service_id,
            "theme_id": theme["id"],
            "theme_name": theme["name"],
            "age_group": persona["age_group"],
            "gender": persona["gender"],
            "visa": persona["visa"],
            "visa_name": persona["visa_name"],
            "refund_amount_krw": persona["typical_refund_krw"],
            "persona_desc": f"{demo_str} {persona['persona_desc']}",
            "video_search_query": video_query,
            "action_prompt": theme["action_prompt"],
            "negative_guardrail": theme["negative_prompt"] + ", caucasian for asian, deformed limbs, floating phone, six fingers",
            "safety_rules": [
                "100% 9:16 vertical video only",
                "Strict ethnicity matching for target language",
                "Clear bottom 1/3 subtitle bar with 0% Korean text",
                "Mobile banking push notification at top floating area"
            ]
        }

        logger.info(f"[{lang.upper()}] 🎬 시나리오 기획 완료: {theme['name']} × {persona['age_group']} {persona['gender'].upper()} ({persona['visa']})")
        return scenario_plan
