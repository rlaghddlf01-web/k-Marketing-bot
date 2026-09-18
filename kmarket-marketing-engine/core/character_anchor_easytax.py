"""
CharacterAnchorEasyTax - 💰 [EasyTax 세무/환급 전용 캐릭터 일관성 앵커 모듈]
- EasyTax 시나리오 작가(ScenarioDirectorShortsEasyTax) 전용 캐릭터 고정 모듈
- 전국 20대 국가산단 근로자, D-2 유학생 알바, E-7 IT 전문직 등 비자별 페르소나 최적화
- 3대 핵심 일관성 보장:
  1) 한국어 나이대 -> 영어 자동 변환 (Imagen 3 프롬프트 오류 원천 차단)
  2) 작업복/연구복/스마트캐주얼 등 세무 환급 수혜자 의상/외모 초정밀 고정
  3) 씬 1~5 단계별 연속성 힌트 자동 주입 ("exact same person continuing the story")
"""

from typing import Dict
from core.character_phenotype_definitions import (
    COUNTRY_8_PHENOTYPES,
    COUNTRY_8_NEGATIVE_ETHNIC,
)

# ======================================================================
# 🌍 17개국 언어 -> 타깃 국가 에스닉 외모 앵커 딕셔너리 (8개국 고유 골격 모듈 100% 연동)
# ======================================================================
LANG_ETHNIC_MAP: Dict[str, str] = COUNTRY_8_PHENOTYPES
LANG_NEGATIVE_ETHNIC: Dict[str, str] = COUNTRY_8_NEGATIVE_ETHNIC

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

# EasyTax 씬 번호별 연속성 힌트 문구
SCENE_CONTINUITY_HINTS = {
    1: "",  # 첫 씬: 단독 소개
    2: "the exact same person as the previous scene,",
    3: "the exact same protagonist continuing the story,",
    4: "the same protagonist shown earlier,",
    5: "the same main character from the beginning,",
}


def build_easytax_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str
) -> str:
    """
    EasyTax 전용: 언어 코드 + 세무 페르소나 정보로 완전한 캐릭터 앵커 문자열 생성
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 직업/의상 디테일 보존
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


def build_easytax_scene_prompt(
    scene_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = ""
) -> str:
    """
    EasyTax 전용 5단계 환급 드라마 씬 프롬프트 생성
    - 씬 1: 급여명세서/세금 고민
    - 씬 2: 환급금 입금 알림에 놀람과 환희
    - 씬 3: 국세청 공인 안심 확인
    - 씬 4: 고향 여행 / 가족 송금 행복
    - 씬 5: 환급 통지서 및 승리 포즈
    """
    continuity = SCENE_CONTINUITY_HINTS.get(scene_idx, "the same protagonist,")
    if scene_idx == 1:
        # 🎯 주인공 골격({char}) 맨 최전방(Token 0) 배치
        prompt = (
            f"{char}. Cinematic authentic 9:16 portrait of the protagonist, "
            f"{scene_action}, "
            f"highly detailed realistic face, 4k ultra realistic photograph, "
            f"human-centric framing, face occupying 60% of frame"
        )
    else:
        prompt = (
            f"{char}, {continuity}. Cinematic authentic 9:16 portrait of the protagonist, "
            f"{scene_action}, "
            f"same consistent face and clothing as scene {scene_idx-1}, "
            f"4k ultra realistic photograph, human-centric framing"
        )
    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_easytax_negative_prompt(lang: str, extra: str = "") -> str:
    """
    EasyTax 전용 부정 프롬프트 (타깃 외 민족 차단 + 세무사 사칭 차단 + 손가락 왜곡 방지):
    - 🎯 [1순위 최전방 배치]: ethnic_neg (Korean, East Asian, Chinese 차단)를 맨 첫머리에 배치하여 UMT5 토큰 감쇠 원천 방지
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")
    base_neg = (
        "caucasian, white person, blonde hair, blue eyes, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, bobblehead, creepy smile, toothy grimace, exaggerated wide smile, "
        "deformed fingers, extra fingers, fused fingers, bad anatomy, "
        "cartoon, 3d render, illustration, painting, CGI, "
        "elderly, old person, middle-aged, age inconsistency, "
        "different person, character change, multiple people, crowd"
    )
    # 🎯 [1순위 맨 앞 배치]: ethnic_neg를 맨 첫머리에 전진 배치
    parts = []
    if ethnic_neg:
        parts.append(ethnic_neg)
    parts.append(base_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)


# 하위 호환용 별칭 (Alias)
build_char_anchor = build_easytax_char_anchor
build_scene_prompt = build_easytax_scene_prompt
build_negative_prompt = build_easytax_negative_prompt
