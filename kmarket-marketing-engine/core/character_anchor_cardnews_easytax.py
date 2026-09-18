"""
CharacterAnchorCardnewsEasyTax - 💰 [EasyTax 카드뉴스 전용 독립 캐릭터 일관성 앵커 모듈]
- 숏폼 파일과 100% 분리된 카드뉴스 독자 모듈 (숏폼 파일 장애/수정 시 상호 영향 0%)
- 1, 2, 4번 실사 슬라이드 간 100% 동일 인물 유지 (Gemini 3.1 Flash-Lite 멀티모달 & 텍스트 앵커 이중 락)
- 3, 5번 슬라이드는 순정 스마트폰 금융 UI 목업 유지
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

# EasyTax 카드뉴스 슬라이드별 5장 전 슬라이드 동일 인물 앵커 연속성 힌트
CARDNEWS_CONTINUITY_HINTS = {
    1: "master reference character,",
    2: "the exact same identical person as slide 1 with identical facial bone structure, identical eyes, identical nose, identical lips, and identical hairstyle,",
    3: "the exact same identical protagonist person from slide 1 with identical facial bone structure, identical eyes, identical nose, identical lips, and identical hairstyle,",
    4: "the exact same identical protagonist person from slide 1 with identical facial bone structure, identical eyes, identical nose, identical lips, and identical hairstyle,",
    5: "the exact same identical protagonist person from slide 1 with identical facial bone structure, identical eyes, identical nose, identical lips, and identical hairstyle,",
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
    - 🚨 [핵심 개선] 순수 얼굴 골격/눈매/피부톤/헤어스타일만 앵커로 고정!
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = [p.strip() for p in persona_anchor_desc.split(",")]
    clothing_keywords = [
        "wearing", "jacket", "shirt", "sweater", "hoodie", "uniform", "blazer",
        "cardigan", "suit", "polo", "t-shirt", "vest", "coat", "clothes", "outfit", "pants", "apron"
    ]
    face_traits = []
    for p in parts:
        p_clean = p.replace("Asian ", "").replace("Asian", "").strip()
        if any(cw in p_clean.lower() for cw in clothing_keywords):
            continue
        for job_word in ["factory worker", "student", "engineer", "instructor", "worker"]:
            p_clean = p_clean.replace(job_word, "person").strip()
        if p_clean:
            face_traits.append(p_clean)

    appearance_desc = ", ".join(face_traits) if face_traits else "gentle warm eyes, natural healthy hair"
    appearance_desc = " ".join(appearance_desc.split())

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent identical facial bone structure, identical eyes, identical nose, and identical hairstyle across all cardnews slides, "
        f"{appearance_desc}"
    )
    return char


def build_easytax_cardnews_scene_prompt(
    slide_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = ""
) -> str:
    """
    EasyTax 카드뉴스 전용 5장 슬라이드 전원 동일 인물 프롬프트 빌더 (사용자 확정 절대 구조):
    [1순위 최전방 Token 0]: 고정된 주인공 인물 묘사 (나이, 성별, 에스닉, 얼굴 골격, 눈매, 헤어스타일, 고유 식별자)
    [2순위]: 해당 슬라이드의 핸드폰 파지 또는 핵심 손동작 액션
    [3순위]: 3m 거리 웨이스트 샷(3 meters away), iPhone 15 Pro, 8등신 비율(8-head tall), 사실적 질감 수식어
    [4순위 후방]: 해당 슬라이드의 배경 장소 및 의상 세부 묘사
    """
    framing_suffix = (
        "wide medium waist-up shot photographed from 3 meters away on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "the subject occupies about 55% to 60% of the vertical frame with generous open background space above the head and around the shoulders, "
        "showing complete upper torso from head down to hips and belt line, natural 8-head tall realistic adult human body proportions, "
        "raw unedited natural human skin texture, realistic mobile phone camera sensor capture, NO beauty filter, authentic candid mobile photo"
    )
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the exact same protagonist person from slide 1 with identical facial bone structure,")

    if slide_idx == 1:
        # 1순위: 주인공 인물 묘사(Token 0) ➔ 2순위: 스마트폰 정면 파지 ➔ 3순위: 3m 거리/화각/비율 ➔ 4순위: 의상/거실 배경
        prompt = (
            f"{char}, {continuity}. "
            f"holding a sleek modern smartphone vertically in one hand at waist level, showing the black vertical display screen turned facing directly forward toward the camera, "
            f"{framing_suffix}, "
            f"sitting naturally in a normal bright modern living room with softly blurred bookshelf and natural window ambient light in the background, "
            f"wearing clean comfortable civilian casual clothes, a simple neat casual t-shirt, "
            f"warm genuine friendly natural smile, looking directly into the camera lens with authentic trustworthy eye contact."
        )
    elif slide_idx == 2:
        # 1순위: 주인공 인물 묘사(Token 0) ➔ 2순위: 도구 작업 손동작 ➔ 3순위: 3m 거리/화각/비율 ➔ 4순위: 공장 배경/유니폼
        prompt = (
            f"{char}, {continuity}. "
            f"hands naturally working with industrial tools, diligently working at a factory workstation, honest hardworking posture, proud sincere determined eyes with a warm hopeful smile, NO smartphone in hand, absolutely not holding any mobile phone, "
            f"{framing_suffix}, "
            f"in a modern high-tech industrial assembly workshop with softly blurred automated machinery, clean workspace, and authentic factory ambient lighting, "
            f"wearing a real industrial company navy blue work jacket uniform with front zipper, safety ID badge, and work gloves, {scene_action}."
        )
    elif slide_idx == 3:
        # 1순위: 주인공 인물 묘사(Token 0) ➔ 2순위: 빈손/제스처 ➔ 3순위: 3m 거리/화각/비율 ➔ 4순위: 카페 배경/니트
        prompt = (
            f"{char}, {continuity}, positioned on the right half of the frame. "
            f"empty hands resting naturally and comfortably on the wooden table, or gesturing gently with an open palm toward the empty left side with a peaceful, relieved, and confident smile, NO smartphone in hand, completely empty natural hands, absolutely not holding any mobile device, "
            f"{framing_suffix}, "
            f"sitting comfortably on a wooden chair in a warm quiet sunlit cafe or cozy room with clean open negative space on the left half of the frame, "
            f"wearing soft cozy civilian clothes, a stylish pastel beige knit sweater or warm daily cardigan."
        )
    elif slide_idx == 4:
        # 1순위: 주인공 인물 묘사(Token 0) ➔ 2순위: 비행기표/여권 손동작 ➔ 3순위: 3m 거리/화각/비율 ➔ 4순위: 공항 배경/사복
        prompt = (
            f"{char}, {continuity}. "
            f"holding an airline boarding pass flight ticket home and passport with both hands, radiant ecstatic smile of pure homecoming joy, tears of relief in eyes, ready to visit beloved family, NO smartphone in hand, absolutely not holding any mobile phone, "
            f"{framing_suffix}, "
            f"at a bright spacious modern airport international departure terminal beside a travel suitcase luggage with gifts for family back home, "
            f"wearing stylish casual travel clothing, a fashionable casual denim jacket or autumn trench coat over a white shirt, comfortable traveler outfit, {scene_action}."
        )
    elif slide_idx == 5:
        # 1순위: 주인공 인물 묘사(Token 0) ➔ 2순위: 엄지척 제스처 ➔ 3순위: 3m 거리/화각/비율 ➔ 4순위: 카페 배경/셔츠
        prompt = (
            f"{char}, {continuity}, positioned on the right half of the frame. "
            f"leaning slightly forward over the cafe table looking directly into the camera with an encouraging enthusiastic friendly smile, giving a confident thumbs-up sign (thumbs up) or welcoming open-hand gesture directly toward the viewer, warmly inviting them to check their tax refund, NO smartphone in hand, absolutely not holding any mobile device, completely empty hands, "
            f"{framing_suffix}, "
            f"in a modern stylish coffee shop setting, seated at a wooden cafe table with a warm ceramic coffee mug on the table, clean open negative space on the left half of the frame, "
            f"wearing neat smart-casual clothing, a neat stylish button-down shirt or elegant casual blouse."
        )
    else:
        prompt = f"{char}, {continuity}. {scene_action}. {framing_suffix}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_easytax_cardnews_negative_prompt(lang: str, extra: str = "") -> str:
    """
    EasyTax 카드뉴스 전용 부정 프롬프트 (90% 얼빡샷/가분수/얼큰이/광각왜곡/밀랍인형/3D CG/8k 화보 원천 차단):
    - 🎯 [1순위 최전방 배치]: 90% 클로즈업(extreme close-up, cropped head, oversized head) 및 에스닉 차단 최전방 락
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")

    framing_and_distortion_neg = (
        "extreme close-up, close-up, macro shot, headshot, bust shot, cropped head, zoomed-in face, "
        "face taking up entire frame, face taking up more than 30% of image, oversized head, giant face, giant head, "
        "tight framing, cropped hair, head touching top edge, bobblehead, deformed anatomy, "
        "8k, commercial advertisement, studio lighting, studio photoshoot, professional photo shoot, fashion magazine cover, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, creepy smile, toothy grimace, exaggerated wide smile, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
        "plastic skin, smooth plastic texture, wax figure, mannequin, doll, airbrushed, beauty filter, smooth skin filter, porcelain skin, oily skin glare, shiny plastic surface, "
        "3d render, CGI, digital painting, digital illustration, octane render, unreal engine, anime, cartoon, artificial look, over-smoothed skin, glossy skin, "
        "back of phone, rear phone case, back cover of smartphone, phone camera lenses on device, triple camera bump, "
        "horizontal phone, tilted phone, pointing like remote, "
        "blank background, plain grey wall, solid color backdrop, empty studio wall, "
        "closed eyes, deformed fingers, extra fingers, missing fingers, fused fingers, bad anatomy, "
        "elderly, old person, middle-aged, age inconsistency, "
        "different person, character change, multiple people, crowd"
    )

    # 🎯 우즈베키스탄(uz), 카자흐스탄(kk), 러시아(ru) 등 튀르크/유라시아계는 caucasian을 절대 금지하면 안 됨!
    if lang in ["uz", "kk", "ru"]:
        base_neg = framing_and_distortion_neg
    else:
        base_neg = f"caucasian, white person, blonde hair, blue eyes, {framing_and_distortion_neg}"

    # 🎯 [1순위 맨 앞 배치]: ethnic_neg를 맨 첫머리에 전진 배치
    parts = []
    if ethnic_neg:
        parts.append(ethnic_neg)
    parts.append(base_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
