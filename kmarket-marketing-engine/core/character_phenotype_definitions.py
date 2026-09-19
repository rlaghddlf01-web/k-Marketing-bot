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
    # 1. 베트남 (vi) - 남방 킨족(Kinh) 고유 골격: 부드러운 계란형 V라인 + 선명한 인폴드 쌍꺼풀 + 섬세한 작은 코 & 볼륨 입술 + 꿀빛 카라멜 피부
    "vi": (
        "authentic Southern Vietnamese Kinh ethnicity, soft oval face with softly defined subtle cheekbones and a slender slim V-line jawline, "
        "clear distinct infold double eyelids with bright deep almond-shaped dark eyes and soft arched eyebrows, "
        "delicate compact nose bridge with a softly rounded small tip, voluptuous soft natural lips, "
        "radiant luminous honey-golden light caramel skin tone, clean smooth healthy skin"
    ),
    # 2. 캄보디아 (km) - 크메르(Khmer) 고유 골격: 사각-하트형 턱뼈 윤곽 + 크고 깊은 둥근 눈(아웃라인 쌍꺼풀) + 넓은 콧볼 & 도톰한 입술 + 앰버 골든 브론즈 피부
    "km": (
        "authentic Cambodian Khmer ethnicity, strong solid square-heart face with distinct defined mandible jawline contour and three-dimensional structured facial bone structure, "
        "large deep-set round eyes with thick prominent bold outline double eyelids and no epicanthic fold, "
        "prominent wider rounded nose bridge, highly defined full voluptuous lips, "
        "rich healthy amber-golden bronze tan skin tone, clean smooth healthy skin, Phnom Penh urban look"
    ),
    # 3. 태국 (th) - 시암 타이(Thai) 고유 골격: 갸름한 하트형 + 시원한 큰 눈(인아웃 쌍꺼풀) + 곧고 좁은 콧망울 & 입꼬리 + 골든 허니 피부
    "th": (
        "authentic Thai ethnicity, sleek slender heart-shaped face with small delicate rounded chin and refined sophisticated facial proportions, "
        "wide-open large expressive eyes with long dense dark eyelashes and glamorous in-out double eyelids, "
        "straight refined high nose bridge with small narrow compact nose tip, elegant lips with naturally upturned lip corners, "
        "bright warm radiant golden-honey complexion, clean smooth healthy skin"
    ),
    # 4. 인도네시아 (id) - 자바(Javanese) 고유 골격: 타원-직사각형 이마/턱선 + 온화한 갈색 눈(얇은 쌍꺼풀) + 둥근 콧망울 & 도톰 입술 + 전통 사워마탕 올리브 브라운 피부
    "id": (
        "authentic Indonesian Javanese ethnicity, soft oval-rectangular face with gentle flat smooth forehead and soft rounded jawline, "
        "warm gentle expressive brown eyes with soft natural thin double eyelids and dense natural eyebrows, "
        "rounded nose bridge with gently sloping wider nasal base, soft full gentle lips, "
        "traditional authentic sawo matang warm ochre-olive brown skin tone, clean smooth healthy skin"
    ),
    # 5. 미얀마 (my) - 버마족(Bamar) 고유 골격: 넓은 이마 둥근 계란형 + 사슴 같은 맑은 큰 눈(인폴드 쌍꺼풀) + 아담한 코 & 부드러운 입술 + 옐로우 골든 올리브 피부
    "my": (
        "authentic Myanmar Bamar ethnicity, broad smooth forehead and soft round-oval face shape with rounded gentle jawline giving a peaceful warm impression, "
        "large bright clear doe-like expressive eyes with soft gentle infold double eyelids and neat well-groomed arched eyebrows, "
        "petite compact nose with a neatly rounded small nose tip, soft curved medium-full lips, "
        "clear bright glowing yellow-golden olive skin tone, clean smooth healthy skin"
    ),
    # 6. 네팔 (ne) - 히말라야 파하디(Pahadi) 고유 골격: 각진 고산지대 역삼각 턱선 + 인도-티베트 융합 깊은 눈 + 높고 날렵한 직선 매부리 콧대 + 밀빛 올리브 피부
    "ne": (
        "authentic Nepalese Himalayan Pahadi ethnicity, narrow angular high-altitude mountain bone structure with high defined forehead and three-dimensional inverted triangle tapered jawline, "
        "deep-set Indo-Tibetan fusion expressive eyes with thick bold straight dark eyebrows and an intense clear gaze, "
        "prominent highly elevated sharp aquiline straight nose bridge, sharply defined thin-to-medium lips, "
        "warm wheatish-olive golden skin tone, clean smooth healthy skin"
    ),
    # 7. 몽골 (mn) - 현대 울란바토르 도시인(Modern Urban Mongolian) 고유 골격: 높은 광대뼈 & 탄탄한 사각턱 + 가로로 긴 시원한 눈매 + 단단한 콧대 & 일자 입술 + 라이트 골든 피부
    "mn": (
        "authentic modern urban Mongolian from Ulaanbaatar, broad solid strong face with prominent well-defined high cheekbones and a firm straight solid square-oval jawline, "
        "horizontally long sleek elongated cool expressive eyes with thin subtle hooded double eyelids, "
        "straight solid firm nose bridge, neat clean straight-line lips, "
        "clean smooth clear light-golden skin tone, clean smooth healthy skin, modern urban look"
    ),
    # 8. 우즈베키스탄 (uz) - 튀르크-유라시안(Turkic-Eurasian) 고유 골격: 동서양 융합 타원형 + 딥셋 헤이즐 눈(아웃라인 쌍꺼풀) + 서구적 오뚝한 콧대 + 상아빛 올리브 피부
    "uz": (
        "authentic Uzbek Central Asian Turkic-Eurasian ethnicity, East-West fusion Eurasian bone structure with slim sculpted refined Eurasian oval face, "
        "deep-set expressive hazel-brown eyes with prominent Western-style distinct bold outline double eyelids and thick dark eyelashes, "
        "prominently high straight elevated defined nose bridge, sculpted attractive defined lips, "
        "fair bright warm ivory-olive skin tone, clean smooth healthy skin, Tashkent urban look"
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
        "South Asian, Indian, Pakistani, Middle Eastern, Arab, Caucasian, "
        "beard, mustache, facial hair, stubble, goatee, five o'clock shadow, sideburns, "
        "pale porcelain skin, fair skin, white face, flat nose, monolid eyes, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "km": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "South Asian, Indian, Pakistani, Middle Eastern, Arab, Caucasian, "
        "beard, mustache, facial hair, stubble, goatee, five o'clock shadow, sideburns, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "th": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "South Asian, Indian, Pakistani, Middle Eastern, Arab, Caucasian, "
        "beard, mustache, facial hair, stubble, goatee, five o'clock shadow, sideburns, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "id": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "South Asian, Indian, Pakistani, Middle Eastern, Arab, Caucasian, "
        "beard, mustache, facial hair, stubble, goatee, five o'clock shadow, sideburns, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, long neck, elongated neck, bobblehead, creepy smile, toothy grimace, "
        "multiple people, two people, extra person, bystander, partner"
    ),
    "my": (
        "Korean, East Asian, Chinese, Han Chinese, Japanese, K-pop style, K-pop hairstyle, parted haircut, "
        "South Asian, Indian, Pakistani, Middle Eastern, Arab, Caucasian, "
        "beard, mustache, facial hair, stubble, goatee, five o'clock shadow, sideburns, "
        "pale porcelain skin, fair skin, white face, monolid eyes, flat nose, "
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
        "red cheeks, rosy cheeks, flushed cheeks, heavy blush, rouge, clown makeup, painted face, face paint, sunburn, sunburned, red spots, "
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
