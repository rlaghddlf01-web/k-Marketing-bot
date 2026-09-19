# -*- coding: utf-8 -*-
"""
CharacterAnchorCardnewsKMarket - 🛒 [K-Market 카드뉴스 전용 독립 캐릭터 일관성 앵커 모듈]
- 숏폼 파일과 100% 분리된 카드뉴스 독자 모듈 (숏폼 파일 장애/수정 시 상호 영향 0%)
- 1~5번 실사 슬라이드 간 100% 동일 인물 유지 (동일 마스터 시드 + 8개국 에스닉 얼굴 앵커)
- 아이폰 15 Pro 일상 스냅샷 실사 톤앤매너 (3D CG/밀랍인형/8k 배제, CFG 3.2 최적화)
- 스마트폰 화면 매립 없이 100% 순수 자연스러운 생활 밀착형 실사 씬 연출
- 8개국 전원: 1번 카드 주는 사람 동일 에스닉 뒷모습(손/어깨만) 노출 + in Korea 전면 제거로 에스닉 희석 원천 차단
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
    - 뿔테 안경(glasses) 필터링으로 국가별 고유 눈매 훼손 방지
    """
    ethnic = LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP["en"])
    age_en = AGE_KO_TO_EN.get(age_group_ko, age_group_ko)
    gender_en = "man" if gender == "male" else "woman"

    parts = [p.strip() for p in persona_anchor_desc.split(",")]
    clothing_and_conflict_keywords = [
        "wearing", "jacket", "shirt", "sweater", "hoodie", "uniform", "blazer",
        "cardigan", "suit", "polo", "t-shirt", "vest", "coat", "clothes", "outfit", "pants", "apron",
        "fair skin", "pale skin", "white skin", "east asian", "korean", "chinese", "japanese",
        "bob haircut", "bob cut", "straight bob", "student", "college",
        "parted dark hair", "parted haircut", "parted hair", "k-pop haircut", "k-pop", "dandy cut", "comma hair",
        "glasses", "wire-frame glasses", "spectacles", "sunglasses", "round glasses", "black glasses"
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
        f"{ethnic}, a real {age_en} {gender_en} "
        f"with clean-shaven smooth skin, strictly no beard, no mustache, neat modern haircut, "
        f"consistent identical facial bone structure, identical eyes, and identical hairstyle across all cardnews slides, "
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
    - Slide 1: 0원 무료 나눔 물품(가전/가구 등)을 받고 활짝 웃는 환희 컷 (주는 사람은 동일 에스닉 뒷모습)
    - Slide 2: 아늑한 원룸 자취방에 가구/가전을 멋지게 배치하고 뿌듯해하는 컷 (in Korea 배제)
    - Slide 3: 생활비 150만원 절약하고 편안하게 차 한잔 마시며 휴식하는 컷
    - Slide 4: 절약한 돈으로 고향 가족을 생각하거나 여유를 되찾은 감동 컷
    - Slide 5: 시청자에게 케이마켓 0원 나눔을 자신 있게 추천하는 따뜻하고 밝은 클로징 인물 컷
    """
    # 🎯 [아이폰 15 Pro 일상 스냅 사진 골든 공식] — 3.5m 거리 와이드 환경 샷, 배경/가구 75~80% & 인물 20~25%, f/11 팬포커스(블러 0%)
    iphone_candid_framing = (
        "authentic candid environmental lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 3.5 meters away with natural smartphone camera lens, "
        "wide environmental view, the room interior and background furniture occupy over 75% of the frame, natural 8-head tall realistic adult human body proportions, "
        "subject occupies only about 20% to 25% of the frame situated naturally inside the environment with generous open space around showing the surrounding room environment and furniture in deep depth of field (f/11 aperture), "
        "tack sharp deep pan-focus across the entire background, f/11 small aperture with all background furniture and walls completely in sharp crisp focus, "
    )
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the exact same protagonist,")

    # 🎯 1번, 2번 슬라이드: 두 손 직거래 및 방 배치용 100% 실사 소형 가전/생활용품 동적 매핑
    # 🚫 음식물(라면 국물, 밥, 토스트, 조리 상태) 원천 차단을 위해:
    #    - 슬라이드 1: 박스 포장 전자기기/가전 (제조사 박스/손잡이 상자 수령)
    #    - 슬라이드 2: 원룸 배치 시 뚜껑/도어가 단단히 닫힌 비어있는 깨끗한 전자기기
    item_lower = item_name.lower()
    if any(k in item_lower for k in ["전자레인지", "microwave"]):
        item_slide1 = "a boxed compact digital microwave oven inside a manufacturer cardboard packaging box with carry handle, clean electronic home device, sealed product package, strictly unopened electronics with no food"
        item_slide2 = "a clean compact digital microwave oven with dark closed glass door, strictly an empty electronic kitchen appliance placed on the counter, no food inside, empty interior"
    elif any(k in item_lower for k in ["밥솥", "rice cooker"]):
        item_slide1 = "a boxed compact electric rice cooker appliance inside a manufacturer product box with carry handle, clean electronic home device, sealed cardboard package, strictly empty electronics with no food, no rice"
        item_slide2 = "a sleek modern electric rice cooker appliance with its lid firmly closed and latched, strictly an empty clean electronic device placed on the counter, no food, no steam, no rice"
    elif any(k in item_lower for k in ["에어프라이어", "airfryer", "air fryer"]):
        item_slide1 = "a boxed compact digital air fryer appliance inside a manufacturer packaging box, clean electronic home device, unopened box, strictly empty electronics with no food"
        item_slide2 = "a sleek compact digital air fryer appliance with its front drawer basket firmly pushed in and closed, clean empty electronic kitchen device on counter, no food inside"
    elif any(k in item_lower for k in ["멀티쿠커", "라면포트", "cooker"]):
        item_slide1 = "a boxed compact electric multi-cooker appliance inside a clean manufacturer product packaging box with handle, strictly a brand-new boxed electronic kitchen device, sealed cardboard product box, completely empty with no food, no noodles, no soup"
        item_slide2 = "a clean modern compact electric multi-cooker appliance with its glass lid tightly closed, strictly an empty clean electronic device placed neatly on the kitchen counter, no food inside, no steam, no soup, no noodles"
    elif any(k in item_lower for k in ["토스터", "toaster"]):
        item_slide1 = "a boxed compact 2-slice toaster appliance inside a manufacturer packaging box, clean electronic home device, sealed product box, strictly no bread"
        item_slide2 = "a clean compact 2-slice electric toaster appliance with empty top slots, strictly an empty electronic device on counter, no bread, no toast, no crumbs"
    elif any(k in item_lower for k in ["믹서기", "블렌더", "blender"]):
        item_slide1 = "a boxed compact personal electric blender appliance inside a manufacturer packaging box, clean home electronic device, sealed box, no liquid"
        item_slide2 = "a clean compact personal electric blender with transparent empty clean plastic jar and tight lid on, strictly empty clean device on counter, no smoothie, no fruit, no liquid"
    elif any(k in item_lower for k in ["포트", "주전자", "kettle"]):
        item_slide1 = "a boxed stainless steel electric kettle inside a manufacturer packaging box, clean electronic home device, sealed box, no liquid"
        item_slide2 = "a modern stainless steel electric kettle with lid tightly closed, strictly empty electronic device on desk, no liquid, no boiling water, no steam"
    elif any(k in item_lower for k in ["청소기", "vacuum"]):
        item_slide1 = "a boxed cordless stick vacuum cleaner inside a long manufacturer product packaging box, clean electronic home appliance"
        item_slide2 = "a sleek cordless stick vacuum cleaner neatly docked in charging stand against the wall"
    elif any(k in item_lower for k in ["다리미", "스팀", "steamer", "iron"]):
        item_slide1 = "a boxed handheld garment steamer appliance inside a manufacturer box, clean electronic device"
        item_slide2 = "a compact handheld garment steamer placed upright on desk, clean electronic device"
    elif any(k in item_lower for k in ["온풍기", "히터", "heater"]):
        item_slide1 = "a boxed compact ceramic space heater inside a manufacturer packaging box, clean home electronic device"
        item_slide2 = "a compact ceramic space heater placed neatly on the room floor, clean modern home appliance"
    elif any(k in item_lower for k in ["전기장판", "온수매트", "장판", "매트", "blanket", "mat"]):
        item_slide1 = "a boxed electric heating blanket appliance in a clean brand-new manufacturer product packaging cardboard box with carry handle, clearly an electronic appliance box, unopened sealed package, strictly electronics, no food"
        item_slide2 = "a clean modern electric heating blanket neatly spread flat over the mattress on the bed, clean cozy bedding in studio room"
    elif any(k in item_lower for k in ["이불", "차렵이불", "bedding", "quilt"]):
        item_slide1 = "a neatly boxed cozy microfiber bedding quilt set inside a clean manufacturer product box with carry handle, brand-new package"
        item_slide2 = "a clean cozy microfiber quilt neatly folded on the bed, clean warm bedding in studio room"
    elif any(k in item_lower for k in ["스탠드", "조명", "lamp"]):
        item_slide1 = "a boxed modern LED desk study lamp inside a manufacturer box, clean lighting product"
        item_slide2 = "a modern LED desk study lamp standing neatly on the study desk"
    elif any(k in item_lower for k in ["가습기", "humidifier"]):
        item_slide1 = "a boxed desktop ultrasonic humidifier appliance inside a manufacturer box, clean electronic device"
        item_slide2 = "a sleek desktop ultrasonic humidifier placed on desk, clean electronic device with lid closed, no water mist"
    elif any(k in item_lower for k in ["서랍장", "수납", "트롤리", "drawer"]):
        item_slide1 = "a compact storage organizer box with handle"
        item_slide2 = "a neat fabric storage drawer chest standing against the wall"
    elif any(k in item_lower for k in ["테이블", "밥상", "table"]):
        item_slide1 = "a neatly folded compact wooden tea table with carry strap"
        item_slide2 = "a folding wooden tea table placed neatly on the floor with clean surface"
    elif any(k in item_lower for k in ["선풍기", "fan"]):
        item_slide1 = "a boxed compact cooling desk fan inside a manufacturer box, clean home appliance"
        item_slide2 = "a compact cooling desk fan standing on table, clean modern home appliance"
    elif any(k in item_lower for k in ["거울", "mirror"]):
        item_slide1 = "a boxed LED tabletop vanity mirror inside a product box, clean cosmetic device"
        item_slide2 = "an LED tabletop vanity mirror standing neatly on desk"
    else:
        item_slide1 = "a boxed useful compact home appliance inside a manufacturer product cardboard box with carry handle, clean electronic device in sealed box, strictly unopened electronics with no food"
        item_slide2 = "a useful compact clean electronic home appliance placed neatly in the room, strictly an empty closed device, no food"

    item_desc_slide1 = item_slide1
    item_appliance_en = item_slide2

    if slide_idx == 1:
        # 🌟 1번: 에스닉 골격 최전방(Token 0) ➔ 3.5m 거리 ➔ 환경 배경 75% & 인물 20~25%
        prompt = (
            f"{char}, {continuity}. "
            f"Authentic candid lifestyle street photo shot on iPhone 15 Pro, casual everyday mobile phone snapshot taken from 3.5 meters away, "
            f"wide environmental streetscape view, wide city street and storefront background occupying over 75% of the frame in full context of a sunny city residential neighborhood sidewalk in warm daytime sunlight. "
            f"In the center of the frame, the protagonist occupies only about 20% to 25% of the frame, happily receiving {item_desc_slide1} with both hands from a kind fellow international student friend of the same ethnicity. "
            f"The fellow giver is viewed strictly from behind over the shoulder, with only their back, shoulders and hands holding the other side of the box, with zero facial features visible for the giver, keeping 100% full visual focus directly and exclusively on the protagonist, "
            f"wearing comfortable neat civilian casual clothes, a simple neat jacket or sweater, "
            f"with a beaming natural smile of pure joy and gratitude, looking happily at the giveaway item with trustworthy eye contact. "
            f"Clean residential street background with tack sharp clear focus on the streetscape, asphalt road, storefront signs and buildings in deep depth of field (f/11 aperture), "
            f"completely crisp and sharp background across the entire frame, deep focus f/11 aperture showing crystal clear distant buildings and street details, "
            f"raw unedited natural human skin texture with subtle real pores, matte skin finish, "
            f"natural outdoor daylight ambient lighting, realistic mobile phone camera sensor capture, natural mobile lifestyle snapshot"
        )
    elif slide_idx == 2:
        # 🌟 2번: 에스닉 골격 최전방(Token 0) ➔ 4m 거리 ➔ 방/가구 80% & 인물 20%
        prompt = (
            f"{char}, {continuity}. "
            f"Authentic candid wide environmental lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone snapshot taken from 4 meters away, "
            f"extreme wide full-room interior view, the cozy studio apartment room and furniture occupy over 80% of the entire frame, "
            f"generous open wide space showing authentic wooden kitchen cabinets, counter, linoleum floor, sunny window daylight, and ceiling in tack-sharp f/11 deep focus pan-focus across the entire room. "
            f"In the middle-ground, the protagonist is a natural full standing figure occupying only about 20% of the frame, "
            f"standing casually near the kitchen counter and table, smiling with warm genuine satisfaction admiring the furnished cozy room. "
            f"On the counter and desk, a real physical {item_appliance_en}, small refrigerator, and neat clean furniture are arranged in tack-sharp crisp focus. "
            f"Natural full-body perspective, distant camera view, raw unedited natural human skin texture, natural matte cotton clothes, real smartphone camera capture, authentic documentary photo"
        )
    elif slide_idx == 3:
        # 3번: 에스닉 골격 최전방(Token 0) ➔ 150만원 절약 안도와 휴식
        prompt = (
            f"{char}, {continuity}. "
            f"{iphone_candid_framing}seated comfortably on a simple sofa or wooden chair in the warm cozy room, "
            f"holding a warm ceramic mug of tea or coffee with a peaceful, deeply relieved smile, "
            f"wearing comfortable casual sweater, feeling proud and secure about saving over 1,500,000 KRW on living costs, "
            f"soft warm ambient interior lighting, clean cozy home background in tack sharp focus (f/11), "
            f"raw natural skin texture, matte finish, deep focus f/11 pan-focus, sharp clear room details"
        )
    elif slide_idx == 4:
        # 4번: 에스닉 골격 최전방(Token 0) ➔ 가족 송금 또는 고향 생각 감동
        prompt = (
            f"{char}, {continuity}. "
            f"{iphone_candid_framing}sitting naturally near a sunny window in the studio room, looking at a framed family photo on the desk with an emotional heartfelt grateful smile, "
            f"wearing comfortable casual clothing, tears of pride and happiness in eyes, feeling accomplished supporting family while living well, "
            f"soft warm natural morning window light, realistic cozy room interior in tack sharp focus (f/11), "
            f"authentic raw human skin texture, matte finish, deep depth of field f/11 pan-focus"
        )
    elif slide_idx == 5:
        # 🌟 5번: 에스닉 골격 최전방(Token 0) ➔ 3.5m 거리 ➔ 방 75% & 인물 20~25% + 은은한 엄지척
        prompt = (
            f"{char}, {continuity}. "
            f"Authentic candid wide environmental lifestyle photo shot on iPhone 15 Pro, casual everyday mobile phone photo taken from 3.5 meters away, "
            f"wide full room interior view with deep depth of field (f/11 aperture pan-focus), tack sharp focus across the entire room showing the furnished studio room, desk, drawers, bed, and appliances in crisp clarity. "
            f"The room interior and furniture occupy over 75% of the entire frame. "
            f"The protagonist occupies only about 20% to 25% of the frame, a natural full standing figure situated in the cozy studio room, "
            f"looking directly into the camera lens with an enthusiastic friendly smile, "
            f"giving a natural subtle thumbs-up gesture or welcoming open-hand gesture to the viewer, warmly welcoming and encouraging other fellow international students and expat friends to use K-Market for free giveaways, "
            f"wearing clean smart-casual clothes, a neat button-down shirt or stylish sweater, "
            f"raw natural skin texture, matte finish, wide full-body environmental perspective, distant camera view 3.5 meters away, tack sharp deep focus f/11 pan-focus across the entire room and background furniture"
        )
    else:
        prompt = f"{char}. authentic candid snapshot, {scene_action}"

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_kmarket_cardnews_negative_prompt(lang: str, slide_idx: int = 1, extra: str = "") -> str:
    """
    K-Market 카드뉴스 전용 부정 프롬프트 (뒷배경 블러/보케/가분수/얼큰이/광각왜곡/밀랍인형/3D CG 전면 원천 차단):
    - 🎯 [1순위 최전방 배치]: ethnic_neg (Korean, East Asian, Chinese 차단)를 맨 첫머리(Index 0)에 즉각 배치하여 UMT5 토큰 감쇠 원천 방지
    - 🚫 [음식물/라면/국물/조리 차단]: 주방가전 나눔 시 라면/국물/밥/토스트/음식물 일체 완벽 차단
    - 🚫 [정체불명 필터/쟁반/스펀지 차단]: 매트/장판 나눔 시 에어컨 필터, 플라스틱 쟁반, 스펀지 등 해괴한 물건 차단
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
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, creepy smile, toothy grimace, exaggerated wide smile, "
        "upper body shot, upper body close-up, portrait shot, headshot, bust shot, medium closeup, tight camera framing, cropped torso, subject taking up majority of frame, zoomed in face, face occupying more than 15% of image, "
        "extreme close-up, macro shot, cropped head, zoomed-in face, face taking up entire frame, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
        "blank background, plain grey wall, solid color backdrop, empty studio wall, "
        "closed eyes, deformed fingers, extra fingers, missing fingers, fused fingers, bad anatomy, "
        "air filter, cabin filter, car filter, pleated filter, accordion paper, plastic tray, plastic tub, foam pad, sponge, folded paper, weird container, distorted object, strange tray, plastic crate, basin, dish rack, "
        "food, cooked food, meal, soup, broth, stew, noodles, ramen, instant noodles, ramen noodles, ramen broth, "
        "pasta, rice, cooked rice, white rice, fried food, bread, toast, meat, vegetables, dining, eating, chewing, "
        "cooking, boiling, simmering, boiling pot, pot of soup, pot of noodles, bowl of soup, hot broth, red soup, "
        "spilled food, soup spill, dirty dishes, bowl of food, plate of food, open food container, "
        "food inside appliance, liquid inside appliance, steaming food, steam, vapor from food, greasy surface, "
        "eating utensils, chopsticks, spoons with food, forks with food, takeout box, street food, restaurant dish, "
        "elderly, old person, middle-aged, age inconsistency, "
        f"{people_neg}"
    )

    # 🎯 우즈베키스탄(uz), 카자흐스탄(kk), 러시아(ru) 등 튀르크/유라시아계는 caucasian을 차단하면 안 됨!
    if lang in ["uz", "kk", "ru"]:
        base_neg = distortion_neg
    else:
        base_neg = f"caucasian, white person, blonde hair, blue eyes, {distortion_neg}"

    # 🎯 [1순위 맨 앞 배치]: ethnic_neg를 맨 첫머리에 전진 배치하여 모델이 가장 먼저 읽도록 강제!
    parts = []
    if ethnic_neg:
        parts.append(ethnic_neg)
    parts.append(base_neg)
    if extra:
        parts.append(extra)
    return ", ".join(parts)
