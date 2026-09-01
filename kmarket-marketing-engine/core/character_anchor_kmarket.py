"""
CharacterAnchorKMarket - 🛒 [K-Market 자취/0원나눔 전용 캐릭터 일관성 앵커 모듈]
- K-Market 시나리오 작가(ScenarioDirectorShortsKMarket) 전용 캐릭터 고정 모듈
- 전국 20대 대학가 유학생, 원룸 자취생, 산단 청년 등 중고거래/자취 페르소나 최적화
- 3대 핵심 일관성 보장:
  1) 한국어 나이대 -> 영어 자동 변환 (Imagen 3 프롬프트 오류 원천 차단)
  2) 캠퍼스 후드티, 니트, 플리스 등 자취/일상 생활밀착형 의상/외모 초정밀 고정
  3) 씬 1~5 단계별 연속성 힌트 자동 주입 ("exact same person continuing the story")
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

# K-Market 씬 번호별 연속성 힌트 문구
SCENE_CONTINUITY_HINTS = {
    1: "",  # 첫 씬: 단독 소개
    2: "the exact same person as the previous scene,",
    3: "the exact same protagonist continuing the story,",
    4: "the same protagonist shown earlier,",
    5: "the same main character from the beginning,",
}


def build_kmarket_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str
) -> str:
    """
    K-Market 전용: 언어 코드 + 자취/캠퍼스 페르소나 정보로 완전한 캐릭터 앵커 문자열 생성
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 캠퍼스룩/자취의상 디테일 보존
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = persona_anchor_desc.split(",")
    style_details = ", ".join(parts[2:]).strip() if len(parts) >= 3 else persona_anchor_desc

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent appearance throughout the video, "
        f"{style_details}"
    )
    return char


def build_kmarket_scene_prompt(
    scene_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = ""
) -> str:
    """
    K-Market 전용 5단계 헐리웃 감동 드라마 씬 프롬프트 생성
    - 씬 1: 텅 빈 원룸의 막막함
    - 씬 2: 비싼 가구 가격에 좌절
    - 씬 3: K-Market 0원 나눔 발견의 기쁨
    - 씬 4: 따뜻한 이웃과의 무료 직거래
    - 씬 5: 아늑한 방 완성 & 행복한 미소
    """
    continuity = SCENE_CONTINUITY_HINTS.get(scene_idx, "the same protagonist,")
    if scene_idx == 1:
        prompt = (
            f"cinematic authentic 9:16 portrait of {char}, "
            f"{scene_action}, "
            f"highly detailed realistic face, 4k ultra realistic photograph, "
            f"human-centric framing, face occupying 60% of frame"
        )
    else:
        prompt = (
            f"cinematic authentic 9:16 portrait of {continuity} {char}, "
            f"{scene_action}, "
            f"same consistent face and clothing as scene {scene_idx-1}, "
            f"4k ultra realistic photograph, human-centric framing"
        )
    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_kmarket_negative_prompt(lang: str, extra: str = "") -> str:
    """
    K-Market 전용 부정 프롬프트 (타깃 외 민족 차단 + 가구 왜곡/배경 찌그러짐 방지 + 기괴한 표정 차단)
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


# 하위 호환용 별칭 (Alias)
build_char_anchor = build_kmarket_char_anchor
build_scene_prompt = build_kmarket_scene_prompt
build_negative_prompt = build_kmarket_negative_prompt
