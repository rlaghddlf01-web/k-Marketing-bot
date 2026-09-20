"""
ShortsCharacterAnchorEasyTax - 💰 [EasyTax 숏폼 전용 인종/에스닉 고정 앵커 모듈]
- 이지텍스 카드뉴스(character_anchor_cardnews_easytax.py)의 검증된 8개국 에스닉 앵커 및 네거티브 필터 100% 연동
- Wan 2.1 T2I 모델의 동양인 편향 원천 차단
- 우즈베키스탄(uz), 카자흐스탄(kk) 등 튀르크-유라시아계 인물의 고유 이목구비(높은 콧대, 깊은 눈매, 헤이즐 브라운 눈) 완벽 보장
- 베트남(vi), 태국(th), 캄보디아(km), 인도네시아(id), 필리핀(tl), 미얀마(my) 등 동남아 인물의 정밀 에스닉 무결성 보장
"""

from typing import Dict, Optional
from core.character_anchor_cardnews_easytax import (
    LANG_ETHNIC_MAP,
    LANG_NEGATIVE_ETHNIC,
    AGE_KO_TO_EN,
    build_easytax_cardnews_char_anchor,
    build_easytax_cardnews_negative_prompt,
)

# 중앙아시아 / 유라시아 계열 (백인/코카시안 차단 필터 면제 국가)
EURASIAN_LANGS = {"uz", "kk", "ru"}


def get_shorts_ethnic_positive(lang: str) -> str:
    """8대 타깃 국가별 에스닉 긍정 프롬프트 반환"""
    return LANG_ETHNIC_MAP.get(lang, LANG_ETHNIC_MAP.get("vi", ""))


def get_shorts_ethnic_negative(lang: str) -> str:
    """8대 타깃 국가별 에스닉 부정 프롬프트 반환"""
    return LANG_NEGATIVE_ETHNIC.get(lang, "")


def build_shorts_t2i_character_prompt(
    lang: str,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None,
    default_char_desc: str = "",
    default_bg_desc: str = "",
    gender: str = "female",
    age_group_ko: str = "20대 후반",
) -> Dict[str, str]:
    """
    Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (카드뉴스 1번 슬라이드 골든 공식과 100% 동일 + 입 다문 립싱크 미소):
    1. 카드뉴스 검증 8개국 에스닉 캐릭터 앵커 1:1 연동
    2. 소파 팔걸이 결합 3.0m 와이드 카우보이 화각 + 골반/허리(hip & waist level) 스마트폰 정면 파지
    3. 거실 책장/화분/소파/창문 햇살 75% f/11 팬포커스
    4. 🤐 [S2V 립싱크 헌법]: 치아 없는 입 다문 부드러운 미소 (lips completely closed together, zero teeth)
    5. 아이폰 15 Pro 무필터 일상 스냅샷 실사 락
    """
    # 1. 8개국 에스닉 캐릭터 정의 (카드뉴스와 100% 동일)
    persona_desc = custom_char_desc or default_char_desc or "gentle warm eyes, natural healthy hair"
    char = build_easytax_cardnews_char_anchor(
        lang=lang,
        gender=gender,
        age_group_ko=age_group_ko,
        persona_anchor_desc=persona_desc
    )

    # 2. 🎯 [최전방 공통 화각 가드레일]: 3.5m 원거리 카우보이 화각 (인물 35~40% 차지, 배경 80% 이상 개방)
    iphone_candid_framing = (
        "authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 3.5 meters away with natural smartphone camera lens, "
        "wide environmental distant cowboy shot, waist-up view showing the complete upper body from head down past hips and belt, "
        "natural 8-head tall realistic adult human body proportions, natural slender neck and shoulders, "
        "subject occupies only about 35% to 40% of the vertical frame with generous open room space and surrounding interior around, "
        "tack sharp deep pan-focus across the entire background (f/11 aperture) with all background details and furniture completely in sharp crisp focus with zero blur, "
    )

    # 3. 의상 및 가구 결합 포즈 (카드뉴스 1번과 100% 동일)
    uniform_clothing = "wearing clean comfortable civilian casual clothes, a neat casual jacket or daily shirt"

    # 4. 🤐 [S2V 립싱크 전용 입 다문 미소 헌법]
    closed_mouth_mandate = (
        "lips completely closed together, mouth gently shut, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
        "calm confident pleasant gentle resting smile, looking directly into the camera lens with authentic trustworthy eye contact celebrating huge tax refund relief. "
    )

    # 5. 긍정 프롬프트 최종 조립 (3.5m 원거리 구도)
    positive = (
        f"candid authentic {iphone_candid_framing}of {char}. "
        f"seated comfortably on a modern fabric living room sofa at 3.5 meters distance with one arm resting naturally on the sofa armrest, "
        f"and the other hand holding a sleek modern smartphone vertically at hip and waist level, "
        f"presenting the clean front vertical black AMOLED display screen turned facing directly forward toward the camera, crisp smartphone screen bezel. "
        f"Authentic wooden bookshelves, indoor plants, textured wallpaper, sofa cushions, and clear window sunlight occupying over 80% of the frame. "
        f"{uniform_clothing}. "
        f"{closed_mouth_mandate}"
        f"Raw unedited natural human skin texture with subtle real pores and natural imperfections, matte skin finish, "
        f"natural everyday room ambient lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo shot on iPhone 15 Pro, NO beauty filter."
    )

    # 6. 부정 프롬프트 (얼빡샷/클로즈업 및 치아/열린 입 차단 100% 결합)
    negative = build_easytax_cardnews_negative_prompt(
        lang=lang,
        extra=(
            "close-up, extreme close-up, cropped torso, bust shot, headshot, zoomed-in, person filling frame, subject taking up majority of frame, large face, tight framing, "
            "empty hands, no phone in hand, smartphone in pocket, holding nothing, "
            "open mouth, parted lips, slightly open mouth, half-open mouth, open lips, visible teeth, showing teeth, teeth, smiling with teeth, grinning, laughing, "
            "holding phone with two hands, typing on phone, text messaging, phone resting on table, phone resting on lap, "
            "tilted phone, angled phone, leaning phone, phone facing inward, horizontal phone, phone pointed like remote, "
            "upside down phone, deformed hand holding phone"
        )
    )

    return {"positive": positive, "negative": negative}
