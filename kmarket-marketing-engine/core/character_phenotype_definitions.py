# -*- coding: utf-8 -*-
"""
CharacterPhenotypeDefinitions - 🌍 [8개국 고유 에스닉 골격 및 인물 정의 독립 모듈]
- 숏폼(Shorts) 및 카드뉴스(Card News) 공통 단일 진실 공급원(Single Source of Truth)
- Wan 2.1 / UMT5 모델의 중국인 편향(Chinese bias) 및 백옥/미백 필터 원천 차단
- 한국 거리 촬영 시 현지인(Korean bystander/local giver)과의 얼굴 블렌딩/침범 방지
- 사용자 확정 8개국 고유 골격(킨족, 크메르, 타이, 자바, 버마, 파하디, 할하, 우즈베크) 100% 반영
"""

from typing import Dict

# ======================================================================
# 🌍 8대 핵심 타깃 국가 에스닉 골격 앵커 (사용자 지정 원형)
# ======================================================================
COUNTRY_8_PHENOTYPES: Dict[str, str] = {
    # 1. 베트남 (vi) - 남방 킨족(Kinh) 고유 골격 (조화로운 아몬드형 눈매 + 웜 카라멜 피부)
    "vi": (
        "authentic Southern Vietnamese Kinh ethnicity, expressive gentle almond-shaped dark eyes "
        "with clear natural double eyelids, warm honey-golden caramel skin tone, "
        "naturally contoured soft lips, gentle rounded small nose bridge, slender jawline, "
        "healthy dark brown wavy hair"
    ),
    # 2. 캄보디아 (km) - 크메르(Khmer) 고유 골격 (조화롭고 친근한 본토 크메르 골격)
    "km": (
        "authentic Cambodian Khmer ethnicity, gentle expressive almond-shaped dark eyes with clear natural double eyelids, "
        "neat natural eyebrows, warm healthy golden-tan skin tone, natural gentle smile, "
        "gentle rounded nose, softly defined natural cheekbones, authentic Phnom Penh Southeast Asian appearance"
    ),
    # 3. 태국 (th) - 중남부 타이(Thai) 고유 골격 (온화한 아몬드형 눈매 + 자연스러운 미소)
    "th": (
        "authentic Thai ethnicity, distinctive Thai facial features, expressive warm almond-shaped dark eyes with clear natural double eyelids "
        "and natural dark lashes, warm golden-tan sun-kissed skin tone, friendly gentle lips, soft compact nose tip, "
        "warm tropical complexion"
    ),
    # 4. 인도네시아 (id) - 자바/말레이계(Javanese) 고유 골격 (자연스러운 갈색 눈매 + 사워마탕 피부)
    "id": (
        "authentic Indonesian Javanese ethnicity, warm exotic light-brown tan skin tone, traditional sawo matang skin tone, "
        "friendly expressive almond-shaped brown eyes with soft natural double eyelids, full soft lips, soft rounded nose bridge, "
        "warm islander complexion"
    ),
    # 5. 미얀마 (my) - 버마족(Bamar) 고유 골격 (부드러운 타원형 얼굴 + 온화한 눈매)
    "my": (
        "authentic Myanmar Bamar ethnicity, gentle oval face, gentle expressive dark brown eyes with clear natural double eyelids, "
        "warm olive-tan golden skin tone, naturally shaped lips, soft peaceful facial features, "
        "distinct Southeast Asian appearance"
    ),
    # 6. 네팔 (ne) - 히말라야/파하디(Himalayan) 고유 골격 (또렷하고 조화로운 눈매 + 높은 콧대)
    "ne": (
        "authentic Nepalese Himalayan Pahadi ethnicity, expressive clear dark eyes with natural double eyelids, "
        "neat natural dark eyebrows, distinct straight high nose bridge, warm wheatish-olive skin tone, "
        "defined natural facial bone structure"
    ),
    # 7. 몽골 (mn) - 할하 유목민(Khalkha) 고유 골격 (자연스러운 광대 + 건강한 브론즈 피부)
    "mn": (
        "authentic Mongolian Khalkha ethnicity, natural defined high cheekbones, healthy sun-bronzed weathered tan skin "
        "with slight natural reddish flush on cheeks from cold steppe wind, strong defined jawline, "
        "warm expressive dark eyes with natural eyelids"
    ),
    # 8. 우즈베키스탄 (uz) - 튀르크-유라시아 골격 (검증 성공 앵커 유지)
    "uz": (
        "authentic Uzbek Central Asian Turkic-Eurasian ethnicity, distinctive Uzbek facial features, "
        "prominent straight high nose bridge, deep-set expressive almond-shaped hazel-brown eyes with natural double eyelids, "
        "soft defined cheekbones and elegant slim jawline, natural warm olive-tan skin, healthy dark brown hair, "
        "authentic Tashkent Central Asian appearance"
    ),
    # ── 기타 보조 국가 (기존 호환성 유지) ──
    "kk": (
        "authentic Kazakh Central Asian Turkic-Eurasian ethnicity, distinctive sharp high nose bridge, "
        "expressive eyes, authentic Almaty Central Asian features"
    ),
    "tl": (
        "authentic Filipino Southeast Asian ethnicity, distinct Filipino facial features, "
        "warm golden-tan skin, expressive gentle dark brown eyes, friendly radiant smile"
    ),
    "ru": "authentic Russian Eastern European",
    "bn": "authentic Bangladeshi South Asian",
    "ur": "authentic Pakistani South Asian",
    "si": "authentic Sri Lankan South Asian",
    "zh": "authentic Chinese East Asian",
    "ja": "authentic Japanese East Asian",
    "ko": "authentic Korean East Asian",
    "ar": "authentic Arabic Middle Eastern",
    "es": "authentic Latin American",
    "en": "authentic Southeast Asian",
}

# ======================================================================
# 🚫 국가별 정밀 네거티브 에스닉 & 단독 인물 고정 프롬프트 (1순위 차단 맨 앞 배치)
# ======================================================================
COUNTRY_8_NEGATIVE_ETHNIC: Dict[str, str] = {
    "vi": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "pale porcelain skin, fair skin, white face, flat nose, monolid eyes, beard, mustache, facial hair, stubble, goatee, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "km": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, beard, mustache, facial hair, stubble, goatee, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "th": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, beard, mustache, facial hair, stubble, goatee, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "id": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, beard, mustache, facial hair, stubble, goatee, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "my": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, beard, mustache, facial hair, stubble, goatee, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "ne": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, "
        "flat face, flat nose bridge, pale porcelain skin, fair skin, white face, monolid eyes, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "mn": (
        "Caucasian, white person, blonde hair, blue eyes, pale porcelain skin, K-pop style, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "weak jawline, double chin, multiple people, two people, extra person, bystander, partner"
    ),
    "uz": (
        "East Asian, Chinese, Han Chinese, Korean, Japanese, Mongolian, monolid eyes, "
        "flat face, flat nose bridge, round face, pale East Asian skin, K-pop style, blonde hair, blue eyes, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "kk": (
        "East Asian, Chinese, Korean, Japanese features, flat face, flat nose bridge, monolid eyes, K-pop style, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "tl": (
        "Korean, East Asian, Chinese, Japanese, K-pop style, pale fair skin, white face, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "ru": "East Asian, Asian features, multiple people, two people, extra person",
    "bn": "Korean, East Asian, Japanese, Chinese features, multiple people, two people, extra person",
    "ur": "Korean, East Asian, Japanese, Chinese features, multiple people, two people, extra person",
    "si": "Korean, East Asian, Japanese, Chinese features, multiple people, two people, extra person",
    "zh": "Korean, Japanese, Southeast Asian features, multiple people, two people, extra person",
    "ja": "Korean, Chinese, Southeast Asian features, multiple people, two people, extra person",
    "ko": "Southeast Asian, South Asian, Western features, multiple people, two people, extra person",
    "ar": "East Asian, Korean features, multiple people, two people, extra person",
    "es": "East Asian, Korean features, multiple people, two people, extra person",
    "en": "Korean, Japanese, Chinese, East Asian, pale fair skin, multiple people, two people, extra person",
}


def get_character_phenotype(lang: str) -> str:
    """언어 코드에 대응하는 8개국 고유 에스닉 골격 정의 반환 (기본값: 베트남 킨족)"""
    return COUNTRY_8_PHENOTYPES.get(lang, COUNTRY_8_PHENOTYPES.get("vi", "authentic Southeast Asian"))


def get_negative_phenotype(lang: str) -> str:
    """언어 코드에 대응하는 8개국 고유 네거티브 프롬프트 반환"""
    return COUNTRY_8_NEGATIVE_ETHNIC.get(lang, COUNTRY_8_NEGATIVE_ETHNIC.get("vi", "Chinese, East Asian"))
