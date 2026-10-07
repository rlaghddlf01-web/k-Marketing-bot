"""
CharacterAnchorBuilder - 🎭 [캐릭터 일관성 앵커 전문 생성 엔진]
- K-Market & EasyTax 양대 시나리오 작가가 공통으로 사용하는 캐릭터 고정 모듈
- 3대 핵심 개선:
  1) 한국어 나이 텍스트 → 영어 자동 변환 (AI 프롬프트 혼동 방지)
  2) 씬별 물리적 외모 고정 포인트 강화 (헤어/피부/의상 초정밀 명시)
  3) 씬 간 연속성 힌트 자동 삽입 ("same person, continuing the story")
"""

from typing import Dict

# ======================================================================
# 🌍 17개국 언어 → 타깃 국가 에스닉 외모 앵커 딕셔너리
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

# 한국어 나이대 → 영어 변환 테이블
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

# 씬 번호별 연속성 힌트 문구
SCENE_CONTINUITY_HINTS = {
    1: "",  # 첫 씬은 힌트 없음
    2: "the exact same person as the previous scene,",
    3: "the exact same protagonist continuing the story,",
    4: "the same protagonist shown earlier,",
    5: "the same main character from the beginning,",
}


def build_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str
) -> str:
    """
    언어 코드 + 페르소나 정보로 완전한 캐릭터 앵커 문자열 생성
    - 한글 나이 → 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    Returns: str (Imagen 3에 바로 삽입 가능한 완성형 캐릭터 설명)
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)  # 한글 변환 실패 시 원본
    gender_en = "man" if gender == "male" else "woman"

    # persona_anchor_desc에서 의상/헤어 디테일만 추출 (앞 2개 쉼표 제외한 뒷부분)
    # 예: "a specific 21-year-old Asian female ... with black bob haircut, ... wearing oversized beige knit"
    # → 쉼표 기준 3번째 이후 의상/스타일 부분만 추출
    parts = persona_anchor_desc.split(",")
    style_details = ", ".join(parts[2:]).strip() if len(parts) >= 3 else persona_anchor_desc

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent appearance throughout the video, "
        f"{style_details}"
    )
    return char


def build_scene_prompt(
    scene_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = ""
) -> str:
    """
    씬 번호 + 캐릭터 + 행동묘사로 최종 이미지 프롬프트 생성
    - 씬 1: 단독 소개
    - 씬 2~5: "exact same person, continuing the story" 연속성 힌트 자동 삽입
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


def build_negative_prompt(lang: str, extra: str = "") -> str:
    """
    언어별 에스닉 차단 + 공통 품질 차단 negative prompt 생성
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
