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
from core.character_phenotype_definitions import (
    COUNTRY_8_PHENOTYPES,
    COUNTRY_8_NEGATIVE_ETHNIC,
)

# ======================================================================
# 🌍 17개국 언어 -> 타깃 국가 에스닉 외모 앵커 딕셔너리 (8개국 고유 골격 모듈 100% 연동)
# ======================================================================
LANG_ETHNIC_MAP: Dict[str, str] = COUNTRY_8_PHENOTYPES

# 언어별 부정 에스닉 프롬프트 (타깃 민족 외 모두 차단)
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
    persona_anchor_desc: str,
    persona_cat: str = "campus"
) -> str:
    """
    K-Market 전용: 언어 코드 + 자취/캠퍼스 페르소나 정보로 완전한 캐릭터 앵커 문자열 생성
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 🎨 [핵심 변경] 의상은 동적 풀에서 매번 랜덤 선택 (하드코딩 0%, 봇 자율 결정)
      → campus/industry/it 카테고리별 10~12벌 풀에서 랜덤 1개 자동 착용
    """
    from core.dynamic_outfit_kmarket import get_dynamic_outfit

    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    # 물리적 외모만 추출 (anchor_desc에서 의상 제거 완료 → 얼굴/헤어/체형만 남음)
    parts = persona_anchor_desc.split(",")
    physical_details = ", ".join(parts[2:]).strip() if len(parts) >= 3 else persona_anchor_desc

    # 🎨 테마/카테고리에 맞는 의상을 매번 다르게 동적 선택
    dynamic_outfit = get_dynamic_outfit(persona_cat, gender)

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent appearance throughout the video, "
        f"{physical_details}, {dynamic_outfit}"
    )
    return char


def build_kmarket_scene_prompt(
    scene_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = "",
    item_name: str = ""
) -> str:
    """
    K-Market 전용 5단계 자취 생활 다큐멘터리 씬 프롬프트 생성
    - 씬 1: 🎨 [동적 생성] 실외 보도블록 2인 물건 직접 인계 (의상·아이템 100% 동적)
    - 씬 2: 원룸 배치 & 룸투어 (동일 인물 유지)
    - 씬 3: 150만원 절약 환호 (동일 인물 유지)
    - 씬 4~5: 스마트폰 목업 (별도 렌더러)
    """
    continuity = SCENE_CONTINUITY_HINTS.get(scene_idx, "the same protagonist,")
    if scene_idx == 1:
        from core.dynamic_outfit_kmarket import get_counterpart_outfit

        # 🎨 주인공 의상에서 대비되는 상대방 의상 자동 선택 (색상 겹침 방지)
        counterpart_outfit = get_counterpart_outfit(char)

        # 🛒 테마 아이템 동적 반영 (60대 테마 실물 아이템 자동 삽입)
        item_desc = f"a compact portable {item_name}" if item_name else "a compact portable household item"

        # 📌 Slide 1 전용: 주인공 골격({char}) 맨 최전방(Token 0) 배치 + 실외 길거리 보도블록 2인 실물 아이템 직접 인계
        prompt = (
            f"{char}. Candid documentary eye-level outdoor street photo of strictly two people only on a sunny residential sidewalk in broad daylight, "
            f"person A on the left is cheerfully receiving {item_desc} with both hands from person B (a friendly young Asian local resident {counterpart_outfit}) on the right, "
            f"the two people are wearing completely different contrasting outfits with different colors, "
            f"{scene_action}, "
            f"clean direct hand-to-hand item handover exchange between only two people on the sidewalk, no skin-to-skin contact, "
            f"both individuals standing upright with complete legs visible on the outdoor concrete pavement, "
            f"empty residential street sidewalk background, zero pedestrians, no other people anywhere, "
            f"highly detailed facial features, sharp clear eyes, well-defined face, natural skin texture, "
            f"unposed authentic photojournalism, 8k uhd, photorealistic, sharp focus"
        )
    elif scene_idx == 2:
        item_desc = f"a clean {item_name}" if item_name else "a clean household item"
        prompt = (
            f"{char}, {continuity}. Authentic eye-level medium interior documentary shot, {scene_action}, "
            f"peaceful relieved warm smile relaxing in cozy beautifully furnished studio apartment with {item_desc} under warm interior lamp lighting, "
            f"authentic studio apartment interior living environment, "
            f"unposed natural lifestyle photography, warm ambient room lighting, 8k uhd, photorealistic, sharp focus"
        )
    elif scene_idx == 3:
        prompt = (
            f"{char}, {continuity}. Authentic eye-level medium lifestyle documentary shot, {scene_action}, "
            f"same consistent character appearance as previous scenes, cozy studio room desk environment, "
            f"unposed natural documentary photography, 8k uhd, photorealistic"
        )
    elif scene_idx == 5:
        prompt = (
            f"{char}, {continuity}. Authentic eye-level medium creator lifestyle documentary portrait, {scene_action}, "
            f"same consistent character appearance as previous scenes, authentic furnished studio room background, "
            f"looking directly into camera with an encouraging and decisive confident smile, pointing forward with friendly inviting gesture, "
            f"natural studio interior lighting, unposed direct connection, 8k uhd, photorealistic, sharp focus"
        )
    else:
        prompt = f"{char}. {scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_kmarket_negative_prompt(lang: str, extra: str = "") -> str:
    """
    K-Market 전용 부정 프롬프트:
    - 🎯 [1순위 최전방 배치]: ethnic_neg (Korean, East Asian, Chinese 차단)를 맨 첫머리에 배치하여 UMT5 토큰 감쇠 원천 방지
    - 공부/독서/필기 차단, 얼굴 뭉개짐/기형 손가락/플라스틱 인형 피부 원천 차단
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")
    base_neg = (
        "three people, 3 people, third person, middle person, extra person, crowd, merged bodies, "
        "missing legs, no legs, floating torso, cut off legs, amputee, disembodied torso, wooden box, crate, basket, cage, "
        "studying, reading books, writing, notebook, pen, pencil, classroom, homework, exams, "
        "empty hands, handshake without furniture, standing without furniture, people only, no furniture, missing item, "
        "blurry face, blurred face, melted face, smudged face, undefined facial features, faceless, "
        "distorted face, deformed eyes, squinting, bad eyes, asymmetric eyes, bad teeth, deformed mouth, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, bobblehead, creepy smile, toothy grimace, exaggerated wide smile, "
        "out of focus face, soft focus face, motion blur on face, foggy face, hazy face, "
        "deformed fingers, fused fingers, extra fingers, missing fingers, malformed hands, claw hands, "
        "bad anatomy, grotesque, "
        "close up face portrait, face zoom, macro headshot portrait, head shot, glamour fashion shoot, "
        "instagram influencer pose, professional fashion photoshoot, posing for camera, looking straight at camera, "
        "caucasian, white person, blonde hair, blue eyes, floating phone, "
        "cartoon, 3d render, illustration, painting, CGI, plastic skin, lowres, jpeg artifacts, "
        "elderly, old person, middle-aged, different person, character change"
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
build_char_anchor = build_kmarket_char_anchor
build_scene_prompt = build_kmarket_scene_prompt
build_negative_prompt = build_kmarket_negative_prompt
