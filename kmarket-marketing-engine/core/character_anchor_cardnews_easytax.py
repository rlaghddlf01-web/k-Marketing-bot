"""
CharacterAnchorCardnewsEasyTax - 💰 [EasyTax 카드뉴스 전용 독립 캐릭터 일관성 앵커 모듈]
- 숏폼 파일과 100% 분리된 카드뉴스 독자 모듈 (숏폼 파일 장애/수정 시 상호 영향 0%)
- 1, 2, 4번 실사 슬라이드 간 100% 동일 인물 유지 (Gemini 3.1 Flash-Lite 멀티모달 & 텍스트 앵커 이중 락)
- 3, 5번 슬라이드는 순정 스마트폰 금융 UI 목업 유지
"""

from typing import Dict

# ======================================================================
# 🌍 17개국 언어 -> 타깃 국가 에스닉 외모 앵커 딕셔너리
# ======================================================================
LANG_ETHNIC_MAP: Dict[str, str] = {
    "vi": "Vietnamese Southeast Asian",
    "uz": "Uzbek Central Asian",
    "ru": "Russian Eastern European",
    "mn": "Mongolian",
    "th": "Thai Southeast Asian",
    "ne": "Nepali South Asian",
    "bn": "Bangladeshi South Asian",
    "my": "Burmese Myanmar Southeast Asian",
    "km": "Cambodian Khmer Southeast Asian",
    "zh": "Chinese East Asian",
    "ja": "Japanese East Asian",
    "id": "Indonesian Southeast Asian",
    "tl": "Filipino Southeast Asian",
    "ar": "Arabic Middle Eastern",
    "es": "Latin American",
    "en": "Southeast Asian",
    "ko": "Korean East Asian",
    "si": "Sri Lankan South Asian",
    "kk": "Kazakh Central Asian",
    "ur": "Pakistani South Asian",
}

# 언어별 부정 에스닉 프롬프트 (타깃 민족 외 모두 차단)
LANG_NEGATIVE_ETHNIC: Dict[str, str] = {
    "vi": "Korean, Japanese, Chinese, East Asian features, fair pale skin",
    "uz": "East Asian, Korean, Japanese, Chinese features",
    "ru": "East Asian, Asian features",
    "mn": "Southeast Asian, Korean, Japanese features",
    "th": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "ne": "East Asian, Korean, Japanese, Chinese features",
    "bn": "East Asian, Korean, Japanese, Chinese features",
    "my": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "km": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "zh": "Korean, Japanese, Southeast Asian features",
    "ja": "Korean, Chinese, Southeast Asian features",
    "id": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "tl": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "ar": "East Asian, Korean features",
    "es": "East Asian, Korean features",
    "en": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "ko": "Southeast Asian, South Asian, Western features",
    "si": "East Asian, Korean, Japanese, Chinese features",
    "kk": "East Asian, Korean, Japanese features",
    "ur": "East Asian, Korean, Japanese, Chinese features",
}

# 한국어 나이대 -> 영어 변환 테이블
AGE_KO_TO_EN: Dict[str, str] = {
    "20대 초반": "early 20s",
    "20대 중반": "mid 20s",
    "20대 후반": "late 20s",
    "30대 초반": "early 30s",
    "30대 중반": "mid 30s",
    "30대 후반": "late 30s",
    "10대 후반": "late teens",
    "40대 초반": "early 40s",
}

# EasyTax 카드뉴스 슬라이드별 연속성 힌트
CARDNEWS_CONTINUITY_HINTS = {
    1: "",  # 1번 슬라이드: 일상 실내 주인공 소개
    2: "the exact same person as slide 1,",
    3: "mockup",
    4: "the exact same protagonist person from slide 1 and slide 2 continuing the story,",
    5: "mockup",
}


def build_easytax_cardnews_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str
) -> str:
    """
    EasyTax 카드뉴스 전용 캐릭터 앵커 생성:
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 작업복/일상복 스타일 정밀 고정
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = persona_anchor_desc.split(",")
    style_details = ", ".join(parts[2:]).strip() if len(parts) >= 3 else persona_anchor_desc

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent appearance across all cardnews slides, "
        f"{style_details}"
    )
    return char


def build_easytax_cardnews_scene_prompt(
    slide_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = ""
) -> str:
    """
    EasyTax 카드뉴스 전용 5장 슬라이드 프롬프트 생성:
    - Slide 1: 일상 실내 주인공 (환급 통지서 확인과 놀람)
    - Slide 2: 산업 현장 일터 (Slide 1과 동일 인물, 성실한 근로자의 보람)
    - Slide 3: 이지텍스 앱 환급 모의조회 목업 (스마트폰 인셋)
    - Slide 4: 사연의 결실/가족 송금/귀국 준비 (Slide 1, 2와 동일 인물)
    - Slide 5: 이지텍스 앱 메인 1분 조회 CTA 목업 (스마트폰 인셋)
    """
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the same protagonist,")

    if slide_idx == 1:
        prompt = (
            f"cinematic authentic eye-level indoor documentary portrait of {char}, "
            f"{scene_action}, "
            f"highly detailed realistic face, sharp eyes, natural skin texture, "
            f"4k ultra realistic photograph, human-centric framing"
        )
    elif slide_idx == 2:
        prompt = (
            f"cinematic authentic eye-level industrial documentary photo of {continuity} {char}, "
            f"{scene_action}, "
            f"same consistent face and hairstyle as slide 1, wearing company work uniform, "
            f"4k ultra realistic photograph, human-centric framing, sharp focus"
        )
    elif slide_idx == 4:
        prompt = (
            f"cinematic authentic eye-level documentary lifestyle photo of {continuity} {char}, "
            f"{scene_action}, "
            f"same consistent face and hairstyle as slide 1 and slide 2, radiant happy relieved smile, "
            f"4k ultra realistic photograph, natural warm golden hour lighting, sharp focus"
        )
    else:
        prompt = f"{scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_easytax_cardnews_negative_prompt(lang: str, extra: str = "") -> str:
    """
    EasyTax 카드뉴스 전용 부정 프롬프트
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")
    base_neg = (
        "caucasian, white person, blonde hair, blue eyes, "
        "deformed fingers, extra fingers, fused fingers, bad anatomy, "
        "cartoon, 3d render, illustration, painting, CGI, "
        "elderly, old person, middle-aged, age inconsistency, "
        "different person, character change, multiple people, crowd"
    )
    parts = [base_neg]
    if ethnic_neg:
        parts.append(ethnic_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
