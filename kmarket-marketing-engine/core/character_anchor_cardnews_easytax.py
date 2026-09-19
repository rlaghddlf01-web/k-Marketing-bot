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
    1: "master reference protagonist,",
    2: "the exact same identical person as slide 1 with identical facial bone structure and identical hairstyle,",
    3: "the exact same identical protagonist person from slide 1 with identical facial bone structure and identical hairstyle,",
    4: "the exact same identical protagonist person from slide 1 with identical facial bone structure and identical hairstyle,",
    5: "the exact same identical protagonist person from slide 1 with identical facial bone structure and identical hairstyle,",
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
    EasyTax 카드뉴스 전용 5장 슬라이드 전원 동일 인물 프롬프트 빌더 (물리적 가구 결합 포즈로 얼빡샷 100% 원천 차단):
    - 🎯 [아이폰 15 Pro 일상 스냅 사진 골든 공식]: 3.0m 거리, wide cowboy shot, head down past hips and waist, 인물 45~50% 차지
    - 🎯 [1번 슬라이드]: 소파 팔걸이에 한 팔 얹고 허리/골반(hip level) 높이에서 스마트폰 전면 파지 + 거실 가구 75% f/11 팬포커스
    - 🎯 [2번 슬라이드]: 작업대 앞에 두 발로 서서 도구 다루는 전신 스탠딩 + 공장 배경 75% f/11 팬포커스
    - 🎯 [3번 슬라이드]: 등받이 있는 카페 의자에 온전히 착석 + 머그잔 옆 빈손 테이블 안도 + 카페 배경 75% f/11 팬포커스
    - 🎯 [4번 슬라이드]: 공항 출발 게이트 캐리어 옆 스탠딩 + 양손 비행기표/여권 환희 + 공항 배경 75% f/11 팬포커스
    - 🎯 [5번 슬라이드]: 카페 테이블 앞 착석 + 머그잔 옆 카메라 정면 엄지척(👍) + 카페 인테리어 75% f/11 팬포커스
    """
    # 🎯 [최전방 공통 화각 가드레일]: 3미터 원거리 카우보이 샷, 머리부터 골반/허벅지까지 상반신 전체 노출 + f/11 팬포커스 무블러
    iphone_candid_framing = (
        "authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 3.0 meters away with natural smartphone camera lens, "
        "wide environmental cowboy shot, waist-up view showing the complete upper body from head down past hips and belt, "
        "natural 8-head tall realistic adult human body proportions, natural slender neck and shoulders, "
        "subject occupies about 45% to 50% of the vertical frame with generous open room space around, "
        "tack sharp deep pan-focus across the entire background (f/11 aperture) with all background details and furniture completely in sharp crisp focus with zero blur, "
    )
    continuity = CARDNEWS_CONTINUITY_HINTS.get(slide_idx, "the exact same protagonist person from slide 1 with identical facial bone structure and hairstyle,")
    uniform_clothing = "wearing clean comfortable civilian casual clothes, a neat casual jacket or daily shirt"

    if slide_idx == 1:
        # 🌟 1번: 최전방 아이폰 카우보이 화각 ➔ 소파 착석 & 팔걸이 ➔ 허리/골반 높이 스마트폰 정면 파지 ➔ 거실 가구 75% f/11 ➔ 환급 환희
        prompt = (
            f"candid authentic {iphone_candid_framing}of {char}, {continuity}. "
            f"seated comfortably on a modern fabric living room sofa with one arm resting naturally on the sofa armrest, and the other hand holding a sleek modern smartphone vertically at hip and waist level, presenting the clean front vertical black AMOLED display screen turned facing directly forward toward the camera, crisp smartphone screen bezel. "
            f"Authentic wooden bookshelves, indoor plants, textured wallpaper, sofa cushions, and clear window sunlight occupying over 75% of the frame. "
            f"{uniform_clothing}. "
            f"Warm genuine friendly natural smile, looking directly into the camera lens with authentic trustworthy eye contact celebrating huge tax refund relief. "
            f"Raw unedited natural human skin texture with subtle real pores and natural imperfections, matte skin finish, "
            f"natural everyday room ambient lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
        )
    elif slide_idx == 2:
        # 🌟 2번: 최전방 아이폰 카우보이 화각 ➔ 공장 작업대 스탠딩 ➔ 작업대/도구/기계 배경 75% f/11 ➔ 작업 동작 (스마트폰 절대 금지!)
        prompt = (
            f"authentic candid workplace environmental photo shot on iPhone 15 Pro, {iphone_candid_framing}of {char}, {continuity}. "
            f"standing on two feet in front of a clean assembly workbench with worktable, metal tool racks, parts bins, overhead industrial lighting, and clean machinery occupying over 75% of the frame. "
            f"{uniform_clothing}. "
            f"Both hands naturally working with industrial tools near the workbench surface, honest hardworking standing posture, proud sincere determined posture with a warm hopeful smile, "
            f"NO smartphone in hand, strictly NO sweat, strictly NO work uniform, "
            f"raw unedited natural human skin texture with subtle real pores, matte finish, "
            f"authentic factory ambient lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
        )
    elif slide_idx == 3:
        # 🌟 3번: 최전방 아이폰 카우보이 화각 ➔ 등받이 의자 착석 & 테이블 ➔ 카페 벽돌벽/원목책장/창문 배경 75% f/11 ➔ 테이블 안도 (스마트폰 절대 금지!)
        prompt = (
            f"authentic candid documentary lifestyle photo shot on iPhone 15 Pro, {iphone_candid_framing}of {char}, {continuity}. "
            f"sitting fully on a wooden cafe chair with backrest, seated beside a wooden cafe table with chair legs and table surface clearly visible. "
            f"Exposed brick walls, wooden bookshelves, hanging pendant lights, and sunny glass window occupying over 75% of the frame. "
            f"{uniform_clothing}. "
            f"Empty hands resting naturally on the wooden table beside a warm ceramic mug, peaceful, relieved, and confident smile, NO smartphone in hand, "
            f"raw unedited natural human skin texture with subtle real pores, matte skin finish, "
            f"natural warm cafe ambient lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
        )
    elif slide_idx == 4:
        # 🌟 4번: 최전방 아이폰 카우보이 화각 ➔ 캐리어 옆 스탠딩 ➔ 공항 터미널/게이트/전광판 배경 75% f/11 ➔ 비행기표 환희 (스마트폰 절대 금지!)
        prompt = (
            f"authentic candid documentary travel photo shot on iPhone 15 Pro, {iphone_candid_framing}of {char}, {continuity}. "
            f"standing proudly beside a travel suitcase luggage at the spacious airport departure lounge with international departure gate, flight information boards, airport seating, and shiny marble floor occupying over 75% of the frame. "
            f"{uniform_clothing}. "
            f"holding an airline boarding pass flight ticket and passport with both hands at waist level, radiant ecstatic smile of pure homecoming joy, ready to visit beloved family, NO smartphone in hand, "
            f"raw real human skin texture with subtle real pores, matte finish, "
            f"bright terminal ambient daylight, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
        )
    elif slide_idx == 5:
        # 🌟 5번: 최전방 아이폰 카우보이 화각 ➔ 카페 테이블 착석 & 머그잔 ➔ 카페 원목인테리어/커피바 배경 75% f/11 ➔ 엄지척 권유 (스마트폰 절대 금지!)
        prompt = (
            f"authentic candid snapshot shot on iPhone 15 Pro, {iphone_candid_framing}of {char}, {continuity}. "
            f"seated comfortably at a wooden cafe table with a warm ceramic coffee mug on the tabletop, textured wooden wall panels, warm ambient lighting, coffee bar counter, and cafe furniture occupying over 75% of the frame. "
            f"{uniform_clothing}. "
            f"Leaning slightly forward over the cafe table looking directly into the camera lens with an encouraging enthusiastic friendly smile, giving a natural confident thumbs-up sign (thumbs up) with hand resting above the table, NO smartphone in hand, "
            f"raw unedited natural human skin texture with subtle real pores, matte skin finish, "
            f"warm cozy cafe lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
        )
    else:
        prompt = f"candid snapshot shot on iPhone 15 Pro, {iphone_candid_framing}of {char}, {continuity}. {uniform_clothing}. {scene_action}."

    if extra_detail:
        prompt += f", {extra_detail}"
    return prompt


def build_easytax_cardnews_negative_prompt(lang: str, extra: str = "") -> str:
    """
    EasyTax 카드뉴스 전용 부정 프롬프트 (뒷배경 블러/보케/가분수/얼큰이/광각왜곡/밀랍인형/3D CG/8k 화보 전면 원천 차단):
    - 🎯 [1순위 최전방 배치]: ethnic_neg (Korean, East Asian, Chinese 차단)를 맨 첫머리에 배치
    - 🚫 [보케/아웃포커싱/배경흐림 100% 차단]: bokeh, background blur, blurry background, shallow depth of field 등 전면 차단
    - 🚫 [얼빡샷/가분수 차단]: extreme close-up, cropped head, zoomed-in face, face taking up more than 15% of image 등 전면 차단
    - 🚫 [싸구려 뷰티 필터/밀랍인형 차단]: beauty filter, smooth skin filter, airbrushed, plastic skin 등 전면 차단
    """
    ethnic_neg = LANG_NEGATIVE_ETHNIC.get(lang, "")

    framing_and_distortion_neg = (
        "anime, cartoon, comic, manga, animated, drawing, sketch, vector art, illustration, digital painting, digital illustration, 3d model, 3d render, CGI, blender render, unreal engine, octane render, artificial look, "
        "bokeh, shallow depth of field, blurry background, soft background, out of focus background, background blur, portrait mode blur, macro blur, fuzzy background, depth of field blur, hazy background, green blob, fake backdrop, green smudge, artificial blur, "
        "plastic skin, smooth plastic texture, wax figure, mannequin, doll, airbrushed, beauty filter, smooth skin filter, porcelain skin, oily skin glare, shiny plastic surface, over-smoothed skin, glossy skin, "
        "sweat, sweating, sweaty, sweat glistening, perspiration, wet face, oily skin, greasy face, "
        "dirty face, dirty skin, smudged face, flushed cheeks, red face, red cheeks, sunburned, sunburn, "
        "work uniform, factory uniform, blue work jacket, overalls, safety vest, apron, jumpsuit, boiler suit, greasy clothes, stained clothes, "
        "refugee, poverty, dirty clothes, beggar, messy hair, disheveled, exhausted, miserable, "
        "upper body close-up, portrait shot, headshot, bust shot, medium closeup, tight camera framing, cropped torso, subject taking up majority of frame, zoomed in face, face occupying more than 15% of image, "
        "extreme close-up, close-up, macro shot, cropped head, zoomed-in face, face taking up entire frame, oversized head, giant face, giant head, "
        "tight framing, cropped hair, head touching top edge, bobblehead, deformed anatomy, "
        "8k, 8k uhd, photorealistic, commercial advertisement, studio lighting, studio photoshoot, professional photo shoot, fashion magazine cover, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, creepy smile, toothy grimace, exaggerated wide smile, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
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
