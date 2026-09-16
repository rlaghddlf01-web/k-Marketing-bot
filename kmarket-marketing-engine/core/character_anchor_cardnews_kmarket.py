# -*- coding: utf-8 -*-
"""
CharacterAnchorCardnewsKMarket - 🛒 [K-Market 카드뉴스 전용 독립 캐릭터 일관성 앵커 모듈]
- 숏폼 파일과 100% 분리된 카드뉴스 독자 모듈 (숏폼 파일 장애/수정 시 상호 영향 0%)
- 1~5번 실사 슬라이드 간 100% 동일 인물 유지 (동일 마스터 시드 + 8개국 에스닉 얼굴 앵커)
- 아이폰 15 Pro 일상 스냅샷 실사 톤앤매너 (3D CG/밀랍인형/8k 배제, CFG 3.2 최적화)
- 스마트폰 화면 매립 없이 100% 순수 자연스러운 생활 밀착형 실사 씬 연출
"""

from typing import Dict

# ======================================================================
# 🌍 17개국 언어 -> 타깃 국가 에스닉 외모 앵커 딕셔너리
# ======================================================================
LANG_ETHNIC_MAP: Dict[str, str] = {
    "vi": "authentic Vietnamese (Southeast Asian ethnicity with distinct Vietnamese features, warm golden-tan skin, gentle almond eyes, radiant smile, NOT Chinese)",
    "uz": "authentic Uzbek (Central Asian Turkic-Eurasian ethnicity with distinctive Uzbek facial features: prominent straight high nose bridge, deep-set expressive almond-shaped hazel-brown eyes with natural double eyelids, soft defined cheekbones and elegant slim jawline, natural warm olive-tan skin, healthy dark brown hair, authentic Tashkent Central Asian appearance, definitely NOT East Asian, NOT Chinese, NOT Korean)",
    "ru": "authentic Russian Eastern European",
    "mn": "authentic Mongolian (Central Asian Mongolian ethnicity with distinctive high cheekbones, radiant sun-kissed skin, expressive warm dark eyes, authentic Mongolian look, NOT Southeast Asian, NOT Chinese)",
    "th": "authentic Thai (Southeast Asian ethnicity with warm tan skin, friendly gentle smile, distinctive Thai features, NOT Chinese)",
    "ne": "authentic Nepali (Himalayan South Asian ethnicity with warm wheatish skin, distinctive expressive deep eyes, genuine warm smile, NOT Chinese)",
    "bn": "authentic Bangladeshi South Asian",
    "my": "authentic Burmese Myanmar (Southeast Asian ethnicity with natural warm olive skin tone, gentle smile, distinctive Myanmar appearance, NOT Chinese)",
    "km": "authentic Cambodian Khmer (Southeast Asian ethnicity with warm golden-brown skin, distinctive Khmer facial features, friendly radiant smile, NOT Chinese)",
    "zh": "Chinese East Asian",
    "ja": "Japanese East Asian",
    "id": "authentic Indonesian (Southeast Asian ethnicity with warm light-brown skin, cheerful friendly expression, distinctive Indonesian look, NOT Chinese)",
    "tl": "Filipino Southeast Asian",
    "ar": "Arabic Middle Eastern",
    "es": "Latin American",
    "en": "Southeast Asian",
    "ko": "Korean East Asian",
    "si": "Sri Lankan South Asian",
    "kk": "authentic Kazakh (Central Asian Turkic-Eurasian ethnicity with distinctive sharp high nose bridge, expressive eyes, authentic Almaty Central Asian features, NOT Chinese)",
    "ur": "Pakistani South Asian",
}

# 언어별 부정 에스닉 프롬프트 (타깃 민족 외 모두 차단)
LANG_NEGATIVE_ETHNIC: Dict[str, str] = {
    "vi": "Korean, Japanese, Chinese, East Asian features, fair pale skin",
    "uz": "East Asian, Chinese, Korean, Japanese features, flat face, flat nose bridge, monolid eyes, round face, pale East Asian skin, blonde hair, blue eyes",
    "ru": "East Asian, Asian features",
    "mn": "Southeast Asian, Korean, Japanese, Chinese features",
    "th": "Korean, Japanese, Chinese, East Asian, pale fair skin",
    "ne": "East Asian, Korean, Japanese, Chinese features, flat face",
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
    "kk": "East Asian, Chinese, Korean, Japanese features, flat face, flat nose bridge, monolid eyes",
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

# K-Market 카드뉴스 슬라이드별 동일 인물 연속성 힌트
CARDNEWS_CONTINUITY_HINTS = {
    1: "",  # 1번 슬라이드: 주인공 마스터 컷
    2: "the exact same person as slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    3: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    4: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
    5: "the exact same protagonist person from slide 1 with identical ethnicity, identical facial bone structure and identical hairstyle,",
}


def build_kmarket_cardnews_char_anchor(
    lang: str,
    gender: str,
    age_group_ko: str,
    persona_anchor_desc: str
) -> str:
    """
    K-Market 카드뉴스 전용 캐릭터 앵커 생성:
    - 한글 나이 -> 영어 자동 변환
    - 에스닉 외모 자동 주입
    - 성별 영어 변환
    - 순수 얼굴 골격/눈매/피부톤/헤어스타일만 고정하여 슬라이드별 다양한 의상/배경 자율성 보장
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = [p.strip() for p in persona_anchor_desc.split(",")]
    clothing_and_conflict_keywords = [
        "wearing", "jacket", "shirt", "sweater", "hoodie", "uniform", "blazer",
        "cardigan", "suit", "polo", "t-shirt", "vest", "coat", "clothes", "outfit", "pants", "apron",
        "fair skin", "pale skin", "white skin", "east asian", "korean", "chinese", "japanese",
        "bob haircut", "bob cut", "straight bob", "student", "college"
    ]
    face_traits = []
    for p in parts:
        p_clean = p.replace("East Asian", "").replace("Asian ", "").replace("Asian", "").strip()
        if any(cw in p_clean.lower() for cw in clothing_and_conflict_keywords):
            continue
        for job_word in ["factory worker", "student", "engineer", "instructor", "worker", "person"]:
            p_clean = p_clean.replace(job_word, "").strip()
        if p_clean and len(p_clean) > 3:
            face_traits.append(p_clean)

    appearance_desc = ", ".join(face_traits) if face_traits else "gentle warm eyes, natural healthy hair"
    appearance_desc = " ".join(appearance_desc.split())

    char = (
        f"a real {age_en} {ethnic} {gender_en} "
        f"with consistent identical facial bone structure, identical eyes, and identical hairstyle across all cardnews slides, "
        f"{appearance_desc}"
    )
    return char


ITEM_KO_TO_EN: Dict[str, str] = {
    "가구": "furniture item",
    "가전": "home appliance",
    "세탁기": "washing machine",
    "냉장고": "compact refrigerator",
    "전자레인지": "microwave oven",
    "밥솥": "rice cooker",
    "책상": "study desk",
    "의자": "comfortable desk chair",
    "침대": "cozy bed frame",
    "청소기": "vacuum cleaner",
    "선풍기": "electric fan",
    "난방기": "space heater",
    "모니터": "computer monitor",
    "옷장": "wardrobe closet",
    "서랍장": "storage chest of drawers",
}


def build_kmarket_cardnews_scene_prompt(
    slide_idx: int,
    char: str,
    scene_action: str,
    extra_detail: str = "",
    item_name: str = ""
) -> str:
    """
    K-Market 카드뉴스 전용 5장 슬라이드 전원 동일 인물 실사 씬 프롬프트 (스마트폰 매립 없음):
    - Slide 1: 0원 무료 나눔 물품(가전/가구 등)을 받고 활짝 웃는 환희 컷
    - Slide 2: 아늑한 원룸 자취방에 가구/가전을 멋지게 배치하고 뿌듯해하는 컷
    - Slide 3: 한국 생활비 150만원 절약하고 편안하게 차 한잔 마시며 휴식하는 컷
    - Slide 4: 절약한 돈으로 고향 가족을 생각하거나 여유를 되찾은 감동 컷
    - Slide 5: 시청자에게 케이마켓 0원 나눔을 자신 있게 추천하는 따뜻한 엄지척(👍) 컷
    """
    # 🎯 [아이폰 15 Pro 일상 스냅 사진 골든 공식] — 3.5m 거리 와이드 환경 샷, 배경/가구 70~75% & 인물 25~30%, f/11 팬포커스(블러 0%)
    iphone_candid_framing = (
        "authentic candid environmental lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 3.5 meters away with natural smartphone camera lens, "
        "wide environmental view, natural 8-head tall realistic adult human body proportions, "
        "subject occupies only about 25% to 30% of the frame with generous open space around showing the surrounding room environment and furniture in deep depth of field (f/11 aperture), "
        "tack sharp deep pan-focus across the entire background, f/11 small aperture with all background furniture and walls completely in sharp crisp focus, "
    )
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the exact same protagonist,")

    # 🎯 [대표님 절대 지침] 1번 슬라이드는 두 손 직거래의 물리적 사실성을 위해 무조건 "소형 가전제품"으로 강제
    if any(k in item_name for k in ["전자레인지", "microwave"]):
        item_appliance_en = "compact microwave oven"
    elif any(k in item_name for k in ["밥솥", "rice cooker"]):
        item_appliance_en = "electric rice cooker"
    elif any(k in item_name for k in ["포트", "kettle"]):
        item_appliance_en = "electric kettle"
    else:
        # 가구/침대 등 대형 품목이 테마로 들어와도 1번 직거래 씬은 무조건 소형 가전(전자레인지/밥솥)으로 고정
        item_appliance_en = "compact microwave oven"

    item_desc_slide1 = f"a clean modern {item_appliance_en}"

    # 슬라이드 2~5 일반 품목 매핑
    item_en = ITEM_KO_TO_EN.get(item_name.strip(), "")
    if not item_en:
        for k, v in ITEM_KO_TO_EN.items():
            if k in item_name:
                item_en = v
                break
    if not item_en:
        item_en = "useful home appliance and furniture"

    item_desc = f"a clean modern {item_en}"

    if slide_idx == 1:
        # 🌟 1번: 두 손으로 소형 가전(전자레인지 등)을 건네받는 생생한 거리 스냅 (우즈베크 주인공 얼굴 100% 앵커링)
        prompt = (
            f"authentic candid lifestyle street photo shot on iPhone 15 Pro, casual everyday mobile phone snapshot taken from 3.5 meters away, "
            f"wide environmental shot, subject occupies about 30% of the frame in full context of the clean sunny Korean residential street sidewalk in warm daytime sunlight. "
            f"In the center of the frame, the main protagonist {char} is happily receiving {item_desc_slide1} with both hands from a kind local giver. "
            f"The giver is viewed partially from the side holding the other side of the small appliance box, keeping full visual focus directly on the protagonist {char}, "
            f"wearing comfortable neat civilian casual clothes, a simple neat jacket or sweater, "
            f"with a beaming natural smile of pure joy and gratitude, looking happily at the giveaway item with trustworthy eye contact. "
            f"Clean Korean residential street background with tack sharp clear focus on the streetscape, asphalt road, storefront signs and buildings in deep depth of field (f/11 aperture), "
            f"completely crisp and sharp background across the entire frame, deep focus f/11 aperture showing crystal clear distant buildings and street details, "
            f"raw unedited natural human skin texture with subtle real pores, matte skin finish, "
            f"natural outdoor daylight ambient lighting, realistic mobile phone camera sensor capture, natural mobile lifestyle snapshot"
        )
    elif slide_idx == 2:
        # 🌟 2번: 0원 가전으로 풀세팅된 원룸 자취방 실사 스냅샷 (실사 톤 고정, 3D 조감도/애니메이션 원천 배제)
        prompt = (
            f"authentic candid documentary lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone snapshot taken by a roommate from 3.5 meters away, "
            f"wide environmental full-room view, subject occupies about 25% of the frame with natural 8-head tall adult body proportions. "
            f"Inside a real lived-in cozy Korean studio apartment room with bright natural window daylight, authentic linoleum flooring, real wooden cabinets. "
            f"The protagonist {continuity} {char} is standing comfortably near the kitchen counter, "
            f"smiling with warm genuine satisfaction admiring the newly furnished cozy room. "
            f"On the counter and desk, a real physical compact microwave oven, small refrigerator, and neat furniture are arranged in tack-sharp f/11 deep depth of field pan-focus across the entire room. "
            f"Raw unedited natural human skin texture with real pores, subtle skin sheen, natural matte cotton clothes, real everyday smartphone camera sensor capture, authentic documentary photo"
        )
    elif slide_idx == 3:
        # 3번: 150만원 절약 안도와 휴식 (배경 인테리어 선명 유지)
        prompt = (
            f"authentic candid lifestyle portrait photo shot on iPhone 15 Pro, {iphone_candid_framing}of {continuity} {char}, "
            f"seated comfortably on a simple sofa or wooden chair in the warm cozy room, "
            f"holding a warm ceramic mug of tea or coffee with a peaceful, deeply relieved smile, "
            f"wearing comfortable casual sweater, feeling proud and secure about saving over 1,500,000 KRW on living costs, "
            f"soft warm ambient interior lighting, clean cozy home background in tack sharp focus (f/11), "
            f"same consistent face and hairstyle as slide 1, raw natural skin texture, matte finish, deep focus f/11 pan-focus, sharp clear room details"
        )
    elif slide_idx == 4:
        # 4번: 가족 송금 또는 고향 생각 감동 (배경 인테리어 선명 유지)
        prompt = (
            f"authentic candid documentary photo shot on iPhone 15 Pro, {iphone_candid_framing}of {continuity} {char}, "
            f"sitting naturally near a sunny window in the studio room, looking at a framed family photo on the desk with an emotional heartfelt grateful smile, "
            f"wearing comfortable casual clothing, tears of pride and happiness in eyes, feeling accomplished supporting family while living well in Korea, "
            f"warm golden hour window sunlight casting gentle light, clean organized room with sharp background details (f/11), "
            f"same consistent face and hairstyle as slide 1, raw natural skin texture, deep focus f/11 pan-focus, crisp interior details"
        )
    elif slide_idx == 5:
        # 5번: 시청자에게 케이마켓 나눔 추천 (카메라 3.5m 거리 와이드 풀샷, 인물 25~30% / 방 배경 70% 이상 칼핀 노출, 클로즈업 0%)
        prompt = (
            f"authentic candid wide environmental lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone photo taken from 3.5 meters away, "
            f"wide full room interior view with deep depth of field (f/11 aperture pan-focus), tack sharp focus across the entire room showing the furnished studio room, desk, drawers, bed, and appliances in crisp clarity. "
            f"The room interior and furniture occupy over 70% of the entire frame. "
            f"The protagonist {continuity} {char} occupies only about 25% of the frame standing in the center room, full upper body and environment visible, "
            f"looking directly into the camera lens with an enthusiastic friendly smile, "
            f"giving a natural subtle thumbs-up gesture or welcoming open-hand gesture to the viewer, warmly inviting other foreign workers to use K-Market for free giveaways, "
            f"wearing clean smart-casual clothes, a neat button-down shirt or stylish sweater, "
            f"same consistent face and hairstyle as slide 1, raw natural skin texture, matte finish, wide full-body environmental perspective, distant camera view 3.5 meters away, tack sharp deep focus f/11 pan-focus across the entire room and background furniture"
        )
    else:
        prompt = f"authentic candid snapshot of {char}, {scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_kmarket_cardnews_negative_prompt(lang: str, slide_idx: int = 1, extra: str = "") -> str:
    """
    K-Market 카드뉴스 전용 부정 프롬프트 (뒷배경 블러/보케/가분수/얼큰이/광각왜곡/밀랍인형/3D CG 전면 원천 차단):
    - Slide 1: 2인 직거래 나눔 씬 허용 (multiple people 제외, 대규모 군중 crowd만 차단)
    - Slide 2~5: 단독 인물 일관성 유지를 위해 multiple people, crowd 차단
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")

    # 1번 슬라이드는 2인 직거래 나눔이므로 multiple people 허용 (혼잡한 군중만 차단)
    people_neg = "crowd, massive group of people, chaotic background, blurry crowd" if slide_idx == 1 else "different person, character change, multiple people, crowd"

    distortion_neg = (
        "anime, cartoon, comic, manga, animated, drawing, sketch, vector art, illustration, digital painting, digital illustration, graphic novel, cel shading, 2d, 2d character, pixar style, disney style, 3d model, 3d render, CGI, blender render, architectural rendering, 3d architectural visualization, 3d interior render, 3ds max, vray render, architectural drawing, cgi room, unreal engine, octane render, artificial look, plastic skin, smooth plastic texture, wax figure, mannequin, doll, airbrushed, beauty filter, smooth skin filter, porcelain skin, oily skin glare, shiny plastic surface, over-smoothed skin, glossy skin, "
        "bokeh, shallow depth of field, blurry background, soft background, out of focus background, background blur, portrait mode blur, macro blur, fuzzy background, depth of field blur, hazy background, "
        "8k, 8k uhd, photorealistic, commercial advertisement, studio lighting, studio photoshoot, professional photo shoot, fashion magazine cover, "
        "bobblehead, big head, oversized head, giant head, large head, dwarf body, short body, deformed anatomy, "
        "extreme close-up, macro shot, headshot, bust shot, cropped head, zoomed-in face, face taking up entire frame, face taking up more than 20% of image, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
        "blank background, plain grey wall, solid color backdrop, empty studio wall, "
        "closed eyes, deformed fingers, extra fingers, missing fingers, fused fingers, bad anatomy, "
        "elderly, old person, middle-aged, age inconsistency, "
        f"{people_neg}"
    )

    # 🎯 우즈베키스탄(uz), 카자흐스탄(kk), 러시아(ru) 등 튀르크/유라시아계는 caucasian을 차단하면 안 됨!
    if lang in ["uz", "kk", "ru"]:
        base_neg = distortion_neg
    else:
        base_neg = f"caucasian, white person, blonde hair, blue eyes, {distortion_neg}"

    parts = [base_neg]
    if ethnic_neg:
        parts.append(ethnic_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
