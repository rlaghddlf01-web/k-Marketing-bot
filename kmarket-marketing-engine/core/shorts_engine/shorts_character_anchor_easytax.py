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
) -> Dict[str, str]:
    """
    Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성:
    1. 타깃 국가별 정밀 에스닉 긍정 프롬프트 주입
    2. 동양인/중국인 편향 방지 네거티브 및 국가별 맞춤 필터 주입 (중앙아시아는 백인 차단 면제)
    3. 스마트폰 파지 및 시선/표정 무결성 헌법 적용
    """
    ethnic_pos = get_shorts_ethnic_positive(lang)
    ethnic_neg = get_shorts_ethnic_negative(lang)

    # 배경 및 인물 묘사에서 'in Korea' 오염 및 뷰티/CG 유발어 철저 정화
    # 배경 및 인물 묘사에서 'in Korea' 오염 및 뷰티/CG 유발어 철저 정화
    char_desc = (custom_char_desc or default_char_desc).replace("in Korea", "").replace("in South Korea", "").strip()
    bg_desc = (custom_bg_desc or default_bg_desc).replace("in Korea", "").replace("in South Korea", "").strip()
    
    # 🚫 [플라스틱/밀랍인형/3D CGI 0% 박멸] AI 화보/뷰티 필터 가중치 자극 단어 완전 멸균
    for bad_w in ["handsome", "beautiful", "gorgeous", "attractive", "model", "flawless", "chiseled", "elegant", "aesthetic"]:
        char_desc = char_desc.replace(bad_w, "").replace(bad_w.capitalize(), "").strip()
        bg_desc = bg_desc.replace(bad_w, "").replace(bad_w.capitalize(), "").strip()

    # 🚫 [테이블/책상 가슴 가림 원천 차단] 테이블에 팔을 얹어 폰을 두 손으로 조작하는 자세 원천 방지
    for table_w in ["wooden table and ceramic coffee mug", "wooden table", "cafe table", "desk", "counter"]:
        bg_desc = bg_desc.replace(table_w, "comfortable lounge armchair").replace(table_w.capitalize(), "").strip()

    # 🚫 [폰 파지 & 입모양 중복 지시어 정제] char_desc에 들어있는 파지/입모양 구문을 제거하여 단일 골든 헌법으로 통합
    for dup_phrase in [
        "holding sleek smartphone naturally in one hand at waist level facing forward",
        "holding sleek smartphone naturally in one hand",
        "holding a smartphone vertically in one hand facing forward to camera",
        "holding a smartphone steadily in one hand facing forward to camera",
        "holding sleek modern smartphone vertically in one hand",
        "holding smartphone",
        "holding sleek smartphone",
        "lips completely closed together, mouth gently shut, strictly zero open mouth, absolutely zero teeth showing",
        "lips completely closed together",
        "mouth gently shut",
        "strictly zero open mouth",
        "absolutely zero teeth showing",
    ]:
        char_desc = char_desc.replace(dup_phrase, "").strip()

    # 중복 쉼표 정리
    char_desc = ", ".join([p.strip() for p in char_desc.split(",") if p.strip()])

    if not bg_desc:
        bg_desc = "a normal bright modern cozy living room with soft natural window ambient daylight and blurred background"

    # 인물 묘사에 에스닉 앵커가 없으면 맨 앞에 강력 주입
    if ethnic_pos:
        full_char = f"{ethnic_pos}, honest friendly facial features, {char_desc}"
    else:
        full_char = f"honest friendly facial features, {char_desc}"

    # 🎯 [카드뉴스 100% 검증 골든 화각] 아이폰 15 Pro 일상 스냅 사진 (2.5미터 카우보이 샷, 폰카 날것의 실사)
    iphone_candid_framing = (
        "authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
        "photographed from 2.5 meters away with natural smartphone camera lens, "
        "medium cowboy shot, waist-up view showing the complete upper body from head down to hips and belt, "
        "natural 8-head tall realistic adult human body proportions, natural slender neck and shoulders, "
        "subject occupies about 55% to 60% of the vertical frame with generous open space around, "
    )

    # 🤐 [대표님 절대 지침: 입벌림 절대 금지] 완벽한 립 닫힘 헌법 (S2V 립싱크 찢어짐 0%)
    closed_mouth_mandate = (
        "lips completely closed together, mouth gently and firmly closed, strictly closed lips, "
        "mouth shut naturally, zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
        "calm confident pleasant resting face, looking directly into the camera lens with sincere trustworthy eye contact, "
    )

    # 📱 [핵심 파지 헌법: 프롬프트 최우선 배치] 스마트폰 검은 액정 정면 파지를 최전방에 배치하여 어텐션 1순위 확보
    phone_hold_front = (
        "holding a sleek modern smartphone vertically in one hand at chest level in front of torso, "
        "with the black vertical display screen turned facing directly forward toward the camera lens, crisp smartphone screen bezel, "
        "firm one-handed grip, the other arm relaxed naturally at side, the smartphone is held clearly inside the frame at mid-torso height. "
    )

    positive = (
        f"{full_char}. Authentic candid snapshot shot on iPhone 15 Pro, "
        f"{phone_hold_front}"
        f"{iphone_candid_framing}"
        f"sitting naturally in {bg_desc}. "
        f"Wearing clean comfortable civilian casual clothes, a simple neat casual shirt or everyday t-shirt. "
        f"{closed_mouth_mandate}"
        f"clear wide-open eyes, alert and attentive eyes, sharp iris and pupil, focused lively eye contact, "
        f"raw unedited natural human skin texture with subtle real pores and natural imperfections, matte skin finish, "
        f"natural everyday room ambient lighting, realistic mobile phone camera sensor capture, NO beauty filter, authentic candid mobile photo"
    )

    # 🚫 [카드뉴스 검증 골든 네거티브 + 폰 각도 무결성 헌법]
    distortion_and_beauty_negative = (
        "8k, commercial advertisement, studio lighting, studio photoshoot, professional photo shoot, fashion magazine cover, "
        "holding phone with two hands, two handed grip, typing on phone, text messaging, phone resting on table, phone resting on lap, "
        "tilted phone, angled phone, leaning phone, phone facing inward, horizontal phone, phone pointed like remote, "
        "phone cut off at bottom, phone cropped at edge, phone partially out of frame, phone held too low, "
        "back of phone, rear phone case, back cover of smartphone, phone camera lenses on device, triple camera bump, "
        "upside down phone, handing over phone, offering phone, thrusting forward, outstretched arm, "
        "phone to ear, making phone call, talking on phone, phone obscuring face, deformed hand holding phone, "
        "open mouth, parted lips, slightly open mouth, half-open mouth, open lips, visible teeth, showing teeth, teeth, smiling with teeth, grinning, laughing, "
        "bobblehead, big head, oversized head, giant head, large head, dwarf body, short body, deformed anatomy, "
        "bug eyes, bulging eyes, bulging eyeballs, sunken eyes, deep-set hollow eyes, long neck, elongated neck, thin giraffe neck, creepy smile, toothy grimace, exaggerated wide smile, "
        "extreme close-up, macro shot, headshot, bust shot, cropped head, zoomed-in face, face taking up entire frame, face taking up more than 20% of image, "
        "wide-angle lens distortion, fisheye lens, perspective distortion, "
        "plastic skin, smooth plastic texture, wax figure, mannequin, doll, airbrushed, beauty filter, smooth skin filter, porcelain skin, oily skin glare, shiny plastic surface, "
        "3d render, CGI, digital painting, digital illustration, octane render, unreal engine, anime, cartoon, artificial look, over-smoothed skin, glossy skin, glamour photo, "
        "half-closed eyes, sleepy eyes, squinting eyes, droopy eyelids, lazy eyes, asymmetric eyes, unnatural gaze, staring blankly, weird eyes, "
        "overexposed, blown out highlights, washed out, harsh white lighting, excessive brightness, pale bleached skin, "
        "blank background, plain grey wall, solid color backdrop, empty studio wall, "
        "deformed hands, extra fingers, missing fingers, fused fingers, claw fingers, bad anatomy, "
        "blurry, low quality"
    )

    # 🎯 [1순위 최전방 배치]: ethnic_neg를 무조건 1순위 맨 앞에 배치!
    if lang in EURASIAN_LANGS:
        neg_parts = [ethnic_neg, distortion_and_beauty_negative]
    else:
        neg_parts = [ethnic_neg, "caucasian, white person, blonde hair, blue eyes", distortion_and_beauty_negative]

    # 빈 문자열 제거 후 결합
    negative = ", ".join([p.strip() for p in neg_parts if p.strip()])

    return {"positive": positive, "negative": negative}
