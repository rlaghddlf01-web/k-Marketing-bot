"""
CharacterAnchorCardnewsKMarket - 🛒 [K-Market 카드뉴스 전용 독립 캐릭터 일관성 앵커 모듈]
- 숏폼 파일과 100% 분리된 카드뉴스 독자 모듈 (숏폼 파일 장애/수정 시 상호 영향 0%)
- 1, 2, 5번 실사 슬라이드 간 100% 동일 인물 유지 (Gemini 3.1 Flash-Lite 멀티모달 & 텍스트 앵커 이중 락)
- 3, 4번 슬라이드는 순정 스마트폰 UI 목업 유지
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

# K-Market 카드뉴스 슬라이드별 연속성 힌트
CARDNEWS_CONTINUITY_HINTS = {
    1: "",  # 1번 슬라이드: 주인공 인계 도입
    2: "the exact same protagonist person as slide 1,",
    3: "mockup",
    4: "mockup",
    5: "the exact same protagonist person from slide 1 and slide 2 continuing the story,",
}


def build_kmarket_cardnews_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str,
    persona_cat: str = "campus"
) -> str:
    """
    K-Market 카드뉴스 전용 캐릭터 앵커 생성:
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 의상은 동적 풀에서 선택하여 고정 착용
    """
    from core.dynamic_outfit_kmarket import get_dynamic_outfit

    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = persona_anchor_desc.split(",")
    physical_details = ", ".join(parts[2:]).strip() if len(parts) >= 3 else persona_anchor_desc

    dynamic_outfit = get_dynamic_outfit(persona_cat, gender)

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent appearance across all cardnews slides, "
        f"{physical_details}, {dynamic_outfit}"
    )
    return char


def build_kmarket_cardnews_scene_prompt(
    slide_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = "",
    item_name: str = ""
) -> str:
    """
    K-Market 카드뉴스 전용 5장 슬라이드 프롬프트 생성:
    - Slide 1: 보도블록 2인 실물 인계 (주인공 Person A + 상대방 Person B)
    - Slide 2: 아늑한 원룸 배치 & 만족 (Slide 1과 동일 주인공)
    - Slide 3: 0원 나눔 피드 스마트폰 목업 (별도 렌더러)
    - Slide 4: 17개국어 자동번역 1:1 채팅 스마트폰 목업 (별도 렌더러)
    - Slide 5: 자신감 넘치는 최종 추천 & CTA (Slide 1, 2와 동일 주인공)
    """
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the same protagonist,")

    if slide_idx == 1:
        from core.dynamic_outfit_kmarket import get_counterpart_outfit

        counterpart_outfit = get_counterpart_outfit(char)
        item_desc = f"a compact portable {item_name}" if item_name else "a compact portable household item"

        prompt = (
            f"candid documentary eye-level outdoor street photo of strictly two people only on a clean Korean residential sidewalk in broad daylight, "
            f"person A ({char}) on the left is cheerfully receiving {item_desc} with both hands, "
            f"person B (a friendly young Asian local resident {counterpart_outfit}) on the right is handing over {item_desc} with both hands, "
            f"the two people are wearing completely different contrasting outfits with different colors, "
            f"{scene_action}, "
            f"clean direct hand-to-hand item handover exchange between only two people on the sidewalk, no skin-to-skin contact, "
            f"both individuals standing upright with complete legs visible on the outdoor concrete pavement, "
            f"empty residential street sidewalk background, zero pedestrians, no other people anywhere, "
            f"highly detailed facial features, sharp clear eyes, well-defined face, natural skin texture, "
            f"unposed authentic photojournalism, 8k uhd, photorealistic, sharp focus"
        )
    elif slide_idx == 2:
        item_desc = f"a clean {item_name}" if item_name else "a clean household item"
        prompt = (
            f"authentic eye-level medium interior documentary shot, {continuity} {char}, {scene_action}, "
            f"peaceful relieved warm smile relaxing in cozy beautifully furnished Korean studio apartment with {item_desc} under warm interior lamp lighting, "
            f"authentic Korean studio apartment interior living environment, "
            f"same consistent face and clothing as slide 1, "
            f"unposed natural lifestyle photography, warm ambient room lighting, 8k uhd, photorealistic, sharp focus"
        )
    elif slide_idx == 5:
        prompt = (
            f"authentic eye-level medium creator lifestyle documentary portrait, {continuity} {char}, {scene_action}, "
            f"same consistent character appearance, face and clothing as slide 1 and slide 2, authentic furnished Korean studio room background, "
            f"looking directly into camera with an encouraging and decisive confident smile, pointing forward with friendly inviting gesture, "
            f"natural studio interior lighting, unposed direct connection, 8k uhd, photorealistic, sharp focus"
        )
    else:
        prompt = f"{scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_kmarket_cardnews_negative_prompt(lang: str, slide_idx: int = 1, extra: str = "") -> str:
    """
    K-Market 카드뉴스 전용 부정 프롬프트
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")
    if slide_idx == 1:
        base_neg = (
            "three people, 3 people, third person, middle person, extra person, crowd, merged bodies, "
            "missing legs, no legs, floating torso, cut off legs, amputee, disembodied torso, wooden box, crate, basket, cage, "
            "studying, reading books, writing, notebook, pen, pencil, classroom, homework, exams, "
            "empty hands, handshake without furniture, standing without furniture, people only, no furniture, missing item, "
            "blurry face, blurred face, melted face, smudged face, undefined facial features, faceless, "
            "distorted face, deformed eyes, squinting, bad eyes, asymmetric eyes, bad teeth, deformed mouth, "
            "out of focus face, soft focus face, motion blur on face, foggy face, hazy face, "
            "deformed fingers, fused fingers, extra fingers, missing fingers, malformed hands, claw hands, "
            "bad anatomy, grotesque, caucasian, white person, blonde hair, blue eyes, "
            "cartoon, 3d render, illustration, painting, CGI, plastic skin, lowres, jpeg artifacts"
        )
    else:
        base_neg = (
            "two people, multiple people, crowd, extra person, "
            "blurry face, blurred face, melted face, smudged face, undefined facial features, faceless, "
            "distorted face, deformed eyes, bad teeth, deformed mouth, "
            "out of focus face, soft focus face, "
            "deformed fingers, fused fingers, extra fingers, missing fingers, malformed hands, "
            "bad anatomy, grotesque, caucasian, white person, blonde hair, blue eyes, "
            "different person, character change, inconsistent face, "
            "cartoon, 3d render, illustration, painting, CGI, plastic skin"
        )

    parts = [base_neg]
    if ethnic_neg:
        parts.append(ethnic_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
