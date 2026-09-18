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
# 🎯 [에스닉 drift 방지] 모든 슬라이드에 에스닉/얼굴 특징 강조 키워드 추가
CARDNEWS_CONTINUITY_HINTS = {
    1: "",  # 1번 슬라이드: 주인공 마스터 컷
    2: "the exact same person as slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    3: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    4: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    5: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
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
    - 🚨 [핵심 개선] 의상(작업복 등)은 완전히 배제하고, 순수 얼굴 골격/눈매/피부톤/헤어스타일만 앵커로 고정!
      (슬라이드별 의상과 배경의 100% 자율 다양성 보장)
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    # persona_anchor_desc에서 의상/옷 관련 키워드 철저히 필터링 (순수 얼굴/헤어 외모 특성만 추출)
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
        f"with consistent identical facial bone structure, identical eyes, and identical hairstyle across all cardnews slides, "
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
    EasyTax 카드뉴스 전용 5장 슬라이드 전원 동일 인물 + 씬별 100% 다른 의상/배경/구도 프롬프트:
    - Slide 1: 바스트/미디엄 샷, 편안한 일상 캐주얼 사복, [유일하게 스마트폰 파지] 정면 내밀며 환급 환희
    - Slide 2: 와이드/미디엄 액션 샷, 공장/현장 작업장, 공장 작업 유니폼, [스마트폰 절대 금지] 성실한 노동
    - Slide 3: 3/4 샷(의자/소파 착석), 아늑한 카페/방, 포근한 니트 스웨터/가디건, [스마트폰 절대 금지] 좌측 앱 안내 제스처
    - Slide 4: 전신/웨이스트 샷, 공항 로비/캐리어, 예쁜 여행 사복(점퍼/코트), [스마트폰 절대 금지] 비행기표/여권 감동
    - Slide 5: 미디엄 샷(카페 테이블), 세련된 카페, 단정한 셔츠, [스마트폰 절대 금지] 커피잔 앞 엄지척(👍) 초대
    """
    # 🎯 [아이폰 15 Pro 일상 스냅 사진 골든 공식] — 자연스러운 폰카 화각(2.5m 거리), 8등신 인체 비례, 무보정 날 것의 실사
    iphone_candid_framing = (
        "authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 2.5 meters away with natural smartphone camera lens, "
        "medium cowboy shot, waist-up view showing the complete upper body from head down to hips and belt, "
        "natural 8-head tall realistic adult human body proportions, natural slender neck and shoulders, "
        "subject occupies about 55% to 60% of the vertical frame with generous open space around, "
    )
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the exact same protagonist,")

    if slide_idx == 1:
        # 1번: 주인공 골격({char}) 맨 최전방(Token 0) 배치 + 일상 거실/방, 스마트폰 정면 파지
        prompt = (
            f"{char}. Candid authentic {iphone_candid_framing}"
            f"sitting naturally in a normal bright modern living room with softly blurred bookshelf and natural window ambient light in the background. "
            f"Wearing clean comfortable civilian casual clothes, a simple neat casual t-shirt. "
            f"The person is holding a sleek modern smartphone vertically in one hand at waist level, "
            f"with the black vertical display screen turned facing directly forward toward the camera, crisp smartphone screen bezel. "
            f"Warm genuine friendly natural smile, looking directly into the camera lens with authentic trustworthy eye contact. "
            f"Raw unedited natural human skin texture with subtle real pores and natural imperfections, matte skin finish, "
            f"natural everyday room ambient lighting, realistic mobile phone camera sensor capture, NO beauty filter, authentic candid mobile photo"
        )
    elif slide_idx == 2:
        # 2번: 주인공 골격({char}) 맨 최전방 배치 + 공장/작업장 유니폼
        prompt = (
            f"{char}, {continuity}. Authentic candid industrial workplace photo taken on iPhone 15 Pro, {iphone_candid_framing}"
            f"in a completely different background setting from slide 1, now in a modern high-tech industrial assembly workshop with softly blurred automated machinery, clean workspace, and authentic factory ambient lighting. "
            f"Wearing a real industrial company navy blue work jacket uniform with front zipper, safety ID badge, and work gloves. "
            f"{scene_action}, "
            f"diligently working at a factory workstation, honest hardworking posture, proud sincere determined eyes with a warm hopeful smile, "
            f"hands naturally working with industrial tools, NO smartphone in hand, absolutely not holding any mobile phone, "
            f"raw real skin texture, subtle authentic forehead sweat, realistic mobile phone sensor capture"
        )
    elif slide_idx == 3:
        # 3번: 주인공 골격({char}) 맨 최전방 배치 + 아늑한 카페/방 포근한 니트
        prompt = (
            f"{char}, {continuity}. Authentic candid documentary lifestyle photo shot on iPhone 15 Pro, {iphone_candid_framing}positioned on the right half of the frame, "
            f"in a completely different setting from slide 2, now sitting comfortably on a wooden chair in a warm quiet sunlit cafe or cozy room, "
            f"with clean open negative space on the left half of the frame. "
            f"Wearing completely different soft cozy civilian clothes, a stylish pastel beige knit sweater or warm daily cardigan. "
            f"Empty hands resting naturally and comfortably on the wooden table, or gesturing gently with an open palm toward the empty left side with a peaceful, relieved, and confident smile. "
            f"NO smartphone in hand, completely empty natural hands, absolutely not holding any mobile device, "
            f"raw natural skin texture, matte finish, everyday ambient lighting"
        )
    elif slide_idx == 4:
        # 4번: 주인공 골격({char}) 맨 최전방 배치 + 공항 로비/캐리어
        prompt = (
            f"{char}, {continuity}. Authentic candid documentary travel photo shot on iPhone 15 Pro, {iphone_candid_framing}"
            f"in a completely different background setting, now at a bright spacious modern airport international departure terminal beside a travel suitcase luggage with gifts for family back home. "
            f"Wearing completely different stylish casual travel clothing, a fashionable casual denim jacket or autumn trench coat over a white shirt, comfortable traveler outfit. "
            f"{scene_action}, "
            f"holding an airline boarding pass flight ticket home and passport with both hands, radiant ecstatic smile of pure homecoming joy, tears of relief in eyes, ready to visit beloved family, "
            f"NO smartphone in hand, absolutely not holding any mobile phone, "
            f"raw natural skin texture, realistic mobile phone sensor capture"
        )
    elif slide_idx == 5:
        # 5번: 주인공 골격({char}) 맨 최전방 배치 + 세련된 카페 테이블 엄지척(👍)
        prompt = (
            f"{char}, {continuity}. Authentic candid portrait snapshot shot on iPhone 15 Pro, {iphone_candid_framing}positioned on the right half of the frame, "
            f"in a completely different modern stylish coffee shop setting, seated at a wooden cafe table with a warm ceramic coffee mug on the table, "
            f"clean open negative space on the left half of the frame. "
            f"Wearing completely different smart-casual clothing, a neat stylish button-down shirt or elegant casual blouse. "
            f"Leaning slightly forward over the cafe table looking directly into the camera with an encouraging enthusiastic friendly smile, "
            f"giving a confident thumbs-up sign (thumbs up) or welcoming open-hand gesture directly toward the viewer, warmly inviting them to check their tax refund, "
            f"NO smartphone in hand, absolutely not holding any mobile device, completely empty hands, "
            f"clean negative space on the left, "
            f"raw natural skin texture, matte finish, NO beauty filter"
        )
    else:
        prompt = f"{char}. authentic candid snapshot, {scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_easytax_cardnews_negative_prompt(lang: str, extra: str = "") -> str:
    """
    EasyTax 카드뉴스 전용 부정 프롬프트 (가분수/얼큰이/광각왜곡/밀랍인형/3D CG/8k 화보 원천 차단):
    - 🎯 [1순위 최전방 배치]: ethnic_neg (Korean, East Asian, Chinese 차단)를 맨 첫머리에 배치하여 UMT5 토큰 감쇠 원천 방지
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")

    distortion_neg = (
        "8k, commercial advertisement, studio lighting, studio photoshoot, professional photo shoot, fashion magazine cover, "
        "bobblehead, big head, oversized head, giant head, large head, dwarf body, short body, deformed anatomy, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, creepy smile, toothy grimace, exaggerated wide smile, "
        "extreme close-up, macro shot, headshot, bust shot, cropped head, zoomed-in face, face taking up entire frame, face taking up more than 20% of image, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
        "plastic skin, smooth plastic texture, wax figure, mannequin, doll, airbrushed, beauty filter, smooth skin filter, porcelain skin, oily skin glare, shiny plastic surface, "
        "3d render, CGI, digital painting, digital illustration, octane render, unreal engine, anime, cartoon, artificial look, over-smoothed skin, glossy skin, "
        "back of phone, rear phone case, back cover of smartphone, phone camera lenses on device, triple camera bump, "
        "handing over phone, offering phone, thrusting forward, outstretched arm, horizontal phone, tilted phone, pointing like remote, "
        "blank background, plain grey wall, solid color backdrop, empty studio wall, "
        "closed eyes, deformed fingers, extra fingers, missing fingers, fused fingers, bad anatomy, "
        "elderly, old person, middle-aged, age inconsistency, "
        "different person, character change, multiple people, crowd"
    )

    # 🎯 우즈베키스탄(uz), 카자흐스탄(kk), 러시아(ru) 등 튀르크/유라시아계는 caucasian을 절대 금지하면 안 됨!
    if lang in ["uz", "kk", "ru"]:
        base_neg = distortion_neg
    else:
        base_neg = f"caucasian, white person, blonde hair, blue eyes, {distortion_neg}"

    # 🎯 [1순위 맨 앞 배치]: ethnic_neg를 맨 첫머리에 전진 배치
    parts = []
    if ethnic_neg:
        parts.append(ethnic_neg)
    parts.append(base_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
