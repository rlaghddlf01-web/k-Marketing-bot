# -*- coding: utf-8 -*-
"""
ShortsCharacterAnchorAura - 💖 [Aura 8대 주제 전용 2030 캐릭터 & 배경 앵커 모듈]
- 8대 주제별 특화 인물 정의(Persona & Fashion) 및 배경 정의(Setting & Lighting) 100% 통일
- [Wan 실전 줌인 편향 보정 규격]:
  1. 주제별 최적 거리 차등화 (1.4m 비디오챗 ~ 4.0m 야외 러닝 와이드 롱샷)
  2. 머리 위 여백(Generous Headroom) 및 주변 환경 심도(Environmental Depth) 확보
  3. 포즈: 스마트폰 파지 완전 배제, 자연스러운 일상 대화/야외 포즈
  4. 표정: Wan 2.2 S2V 립싱크 헌법 준수 (치아 노출 제로, 입을 부드럽게 다문 온화한 미소)
  5. 얼빡샷(extreme close-up) 강력 차단 네거티브 탑재
"""

from typing import Dict, Any, Optional

# 8대 주제별 인물, 배경 및 Wan 실전 보정 거리 매트릭스
AURA_8_TOPIC_SPECS = {
    1: {
        "topic_id": 1,
        "title": "소개팅 탈출 전화",
        "gender": "female",
        "framing": (
            "photographed from 1.6 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and dark wooden dining table clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "a beautiful 28-year-old Korean woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face, slender elegant long neck, calm low ponytail hairstyle, clear fair skin, "
            "refined subtle makeup, wearing stylish sophisticated civilian dating clothes, a chic modern evening dinner outfit, "
            "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
        ),
        "bg_desc": (
            "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
            "antique dark wooden dining table, delicate wine glasses and neat linen napkin in the background in tack sharp f/11 focus"
        ),
        "vibe": "청담동 고급 비스트로에서 눈길을 싹쓸이하는 세련되고 우아한 로맨스 드라마 여주급 직장인 비주얼"
    },
    2: {
        "topic_id": 2,
        "title": "실시간 자막 통화",
        "gender": "female",
        "framing": (
            "photographed from 2.0 meters away from the date's first-person eye-level perspective on Apple iPhone 15 Pro 24mm main camera, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid cowboy medium shot showing chest, waist, and warm wooden furniture clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background bookshelves and plants in sharp crisp focus, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous 24-year-old Japanese young woman (Nanami), perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
            "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
            "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
            "wearing clean stylish civilian casual clothes, a neat comfortable daily outfit, looking directly into the camera lens"
        ),
        "bg_desc": (
            "warm cozy living room with authentic dark oak wooden bookshelves filled with books, "
            "vibrant lush green indoor potted plants, warm directional room ambient lighting creating natural depth and rich realistic shadows, "
            "warm inviting atmosphere with over 75% background rich interior details in tack sharp f/11 focus"
        ),
        "vibe": "도쿄 잇걸 미모의 나나미, 따뜻한 원목 책장과 초록 식물 배경에서 세련된 일상 사복으로 쨍하고 선명한 아이폰 15 Pro 실사 비주얼"
    },
    3: {
        "topic_id": 3,
        "title": "50:50 VIP 게이트",
        "gender": "female",
        "framing": (
            "photographed from 1.8 meters away from the date's first-person eye-level perspective on Apple iPhone 15 Pro, "
            "solo 1person female, standing gracefully by the glass railing of an upscale rooftop terrace, perfectly centered in the middle of frame, "
            "perfectly frontal portrait view looking directly into the camera lens with deeply captivating magnetic eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful collarbones, "
            "gently closed mouth, natural full lips closed together with subtle alluring smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "elegantly holding a delicate crystal wine glass filled with deep red wine comfortably at waist height in one hand, wine glass held strictly at lower waist level far below the chest and mouth, "
            "candid medium cowboy standing shot showing waist, chest, shoulders, and elegant posture clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real skin texture, fine pores and silky hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous glamorous 26-year-old Korean woman standing with effortless confidence and poise, perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, breathtakingly stunning high-society VIP beauty, "
            "voluminous natural dark silky wavy hair falling gracefully over her bare shoulders, seductive feline cat-like hazel eyes with subtle smoky eyeliner, "
            "flawless luminous glass skin with soft natural cheek blush, sharp high cheekbones and sculpted jawline, "
            "wearing an ultra-luxurious glamorous evening party dress, a chic upscale rooftop lounge cocktail outfit, sophisticated high-society date-night style, "
            "captivating sultry romantic charisma, unforgettable date-night VIP goddess aesthetic"
        ),
        "bg_desc": (
            "romantic midnight night view in Seoul, ultra-luxury high-end hotel rooftop sky lounge and open-air champagne bar in Gangnam, "
            "standing beside modern glass balustrade overlooking breathtaking panoramic sparkling glittering Seoul city night skyline and skyscraper lights against dark midnight blue sky in tack sharp f/11 focus, "
            "soft warm ambient architectural uplighting, glowing warm golden patio mood lamps creating dramatic rich depth, crisp details, and cinematic evening intimacy"
        ),
        "vibe": "밤의 특급호텔 루프탑 테라스에서 서울 야경을 배경으로 와인잔을 들고 서서 상대를 유혹하듯 마주하는 치명적인 섹시 고혹미 VIP 여신"
    },
    4: {
        "topic_id": 4,
        "title": "청담동 화보 보정",
        "gender": "female",
        "framing": (
            "photographed from 2.5 meters away from the photographer's direct eye-level perspective inside a luxury Cheongdam studio on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in frame, medium chest-up seated photoshoot portrait, "
            "seated gracefully in the single designer white lounge armchair with the chair's curved backrest and armrests framing her naturally, "
            "eye-level strictly anchored at the upper 35% golden ratio line of the frame, "
            "tight balanced 15% headroom margin above head, "
            "perfectly frontal portrait view looking directly into the camera lens with captivating gentle eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, slender elegant long neck, collarbone and graceful shoulders visible, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "chest and shoulders filling 65% of the frame with high aesthetic elegance, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, crisp high micro-contrast, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous glamorous 25-year-old Korean young woman with a breathtakingly seductive feline cat-like facial aesthetic, "
            "captivating alluring cat-like almond hazel eyes with subtle sharp winged eyeliner, sharp high cheekbones, delicate cute button nose, sculpted elegant jawline, "
            "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, graceful collarbone, "
            "flawless luminous glass skin with soft natural peach blush, realistic skin pores and authentic fine skin texture, "
            "natural full lips gently closed together with a subtle alluring confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "voluminous silky dark wavy hair falling gracefully over shoulders, "
            "wearing stylish sophisticated civilian dating clothes, an elegant chic off-shoulder knit top, modern luxurious date-night fashion, looking directly into the camera lens"
        ),
        "bg_desc": (
            "high-end luxury photography studio in Cheongdam, modern curved architectural round arch alcove wall in warm peach-beige tone clearly visible behind her, "
            "modern curved studio architecture, tack sharp f/11 focus"
        ),
        "vibe": "청담동 최고급 스튜디오의 아치형 백월과 화이트 라운지 체어에 앉아 상단 35% 시선으로 앙큼하고 매혹적인 고양이상 섹시 뷰티를 뽐내는 정석 화보"
    },
    5: {
        "topic_id": 5,
        "title": "가치관 밸런스 매칭",
        "gender": "female",
        "framing": (
            "photographed from 1.6 meters directly across a brunch table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and brunch table clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous 21-year-old Korean campus goddess with breathtakingly enchanting feline cat-like facial features, "
            "captivating alluring cat-like almond dark eyes with subtle sharp upturned winged eyeliner, "
            "sharp high cheekbones, delicate cute petite nose, sculpted flawless V-line jawline, "
            "radiant luminous porcelain glass skin with soft natural peach cheek glow, "
            "neat sleek low bun hairstyle with subtle elegant side fringe framing her face perfectly, "
            "wearing a chic clean minimalist white ribbed-knit sleeveless dress with a wide-strap square neckline, "
            "fitted ribbed texture accentuating her graceful slender collarbone and delicate bare shoulders, elegant sophisticated summer brunch date attire, looking directly into the camera lens"
        ),
        "bg_desc": (
            "cozy outdoor brunch cafe patio in Yeonnam-dong surrounded by abundant lush vibrant green leaves, rich lush tree canopy with deep green foliage filling the background in tack sharp f/11 focus, fresh refreshing garden terrace atmosphere, rustic wooden table with cute brunch plates and iced latte, pleasant natural daylight filtering through green leaves"
        ),
        "vibe": "성수/연남동에서 번호 따일 확률 100%인 사랑스럽고 발랄한 대학생 캠퍼스 여신"
    },
    6: {
        "topic_id": 6,
        "title": "AI 첫대화 비서",
        "gender": "male",
        "framing": (
            "authentic candid snapshot shot on Apple iPhone 15 Pro, photographed from 2.0 meters directly across an outdoor rooftop terrace from the date's first-person eye-level perspective, "
            "solo 1person male, standing gracefully, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and broad masculine shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "arms resting naturally straight down at sides, hands visible outside pockets, strictly no hands in pockets, "
            "candid medium cowboy standing shot showing waist, chest, broad shoulders, and tall 8-head model silhouette clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally handsome 26-year-old Korean adult man (K-drama male lead actor visual, delicate handsome idol-actor appearance, refined aesthetic features), perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, slender athletic male physique with broad masculine shoulders, "
            "soft gentle smile with lips closed together, refined handsome features, sharp sculpted jawline with natural subtle directional shadow, charismatic warm romantic gaze, strictly no teeth showing, "
            "neat stylish dark brown natural dandy haircut with subtle parted fringe framing his face, "
            "authentic real human skin texture with visible fine pores and natural skin tone, "
            "wearing a stylish, trendy modern casual jacket outfit, sophisticated 2030 Seoul dating fashion with diverse contemporary colors and textures, clean minimalist innerwear, effortless charismatic boyfriend-material date look, "
            "arms resting naturally straight down at sides, hands visible outside pockets, strictly no hands in pockets, "
            "authentic candid mobile phone snapshot on Apple iPhone 15 Pro, looking directly into camera lens"
        ),
        "bg_desc": (
            "upscale modern outdoor open-air rooftop sky lounge terrace in Seoul at night with glowing warm Edison string bulb lights and elegant golden patio lanterns, "
            "standing beside sleek glass balustrade overlooking vibrant colorful glowing city neon lights and panoramic glittering Seoul night skyline in tack sharp f/11 focus, "
            "luxurious warm architectural uplighting illuminating the terrace ambiance naturally, authentic iPhone 15 Pro mobile night photo atmosphere"
        ),
        "vibe": "밤의 야외 루프탑 라운지 테라스에 서서 상대를 바라보며 심쿵을 부르는 세련된 트렌디 남친짤 실사 비주얼"
    },
    7: {
        "topic_id": 7,
        "title": "AI 아우라 진단",
        "gender": "female",
        "framing": (
            "photographed from 1.6 meters directly across a cafe table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful collarbone, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "both hands and slender elegant fingers clearly visible resting naturally and gracefully on top of the cafe table, "
            "candid medium cowboy shot showing chest, waist, and cafe table clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "a mesmerizingly attractive 25-year-old Korean it-girl, perfect 8-head-high golden ratio model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, "
            "trendy textured dark hair with subtle soft ash highlights, flawless glowing porcelain skin, "
            "wearing a chic form-fitting ribbed knit top, trendy hip Seongsu cafe fashion, alluring stylish influencer aesthetic, looking directly into the camera lens"
        ),
        "bg_desc": (
            "trendy hip espresso bar and modern art gallery cafe in Seongsu-dong, mid-century modern aesthetic interior, "
            "framed contemporary art posters, warm designer lamp glow in tack sharp f/11 focus"
        ),
        "vibe": "상위 0.1% 아우라를 뿜어내는 매혹적인 트렌디 핫플 여우상 퀸"
    },
    8: {
        "topic_id": 8,
        "title": "500m 안심 레이더",
        "gender": "female",
        "framing": (
            "photographed from 1.8 meters directly across a warm brown wooden terrace cafe table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and athletic posture, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "both hands and slender elegant fingers clearly visible resting naturally and gracefully on top of the warm brown wooden terrace cafe table, "
            "candid medium cowboy shot showing chest, waist, and warm brown wooden terrace cafe table clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally stunning 25-year-old Korean fitness goddess visual, perfect 8-head-high golden ratio athletic model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, glowing radiant sun-kissed fair skin, "
            "sleek high ponytail hairstyle, "
            "wearing a chic rich saturated deep cobalt blue and dark navy form-fitting athletic zip-up top, sleek stylish outdoor activewear, refreshing fitness runner fashion, looking directly into the camera lens"
        ),
        "bg_desc": (
            "sunny outdoor terrace cafe near Seoul Forest park, rustic warm natural brown oak wooden cafe table, lush green trees and park walking trail visible in background in tack sharp f/11 focus, "
            "bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
        ),
        "vibe": "서울숲에서 마주치면 고개 돌아가는 건강미 넘치는 산뜻한 여신 러너"
    }
}


def build_aura_shorts_t2i_character_prompt(
    topic_id: int = 1,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None
) -> Dict[str, str]:
    """
    Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (Wan 실전 줌인 편향 보정 골든 공식):
    1. 8대 주제별 맞춤형 카메라 거리 차등화 (1.4m ~ 4.0m)
    2. 머리 위 여백(Generous Headroom) 및 주변 환경 심도(Environmental Depth) 확보
    3. 스마트폰 파지 배제, 자연스러운 일상 제스처
    4. 🤐 [S2V 립싱크 헌법]: 치아 없는 입 다문 부드러운 미소 (lips completely closed together, zero teeth)
    5. 📐 [완벽한 정면 직립 헌법]: 고개 기울임(Head tilt) 제로, 수직 직립 정면 응시
    6. 얼빡샷(extreme close-up) 강력 차단 네거티브 탑재
    7. 💡 [3점 입체 조명 & 림라이트 & f/11 딥팬포커스 실사 규격]
    """
    norm_id = ((topic_id - 1) % len(AURA_8_TOPIC_SPECS)) + 1
    spec = AURA_8_TOPIC_SPECS.get(norm_id, AURA_8_TOPIC_SPECS[1])

    char = custom_char_desc or spec["char_desc"]
    bg = custom_bg_desc or spec["bg_desc"]
    framing = spec["framing"]

    # 🤐 S2V 립싱크 전용 정면 직립 + 입 다문 미소 헌법 (Wan 2.2 S2V 립싱크 궤적 극대화 & 고개 틀어짐 원천 차단)
    head_and_mouth_mandate = (
        "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, looking straight and directly into the camera lens with level eye line, "
        "gently closed mouth, natural lips closed, looking at camera, mouth gently shut, lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
        "charming gentle confident resting smile, looking directly into the camera lens with warm authentic eye contact ready to speak. "
    )

    # 📏 [대표님 특명: 8등신 황금비율 & 소두 모델 비율 헌법] (얼빡샷/대두 현상 원천 영구 박멸)
    body_proportion_mandate = (
        "perfect 8-head-high body proportions, golden ratio 1:8 head-to-body proportion, "
        "delicate small petite head and face size, slender elegant long neck, graceful slender collarbone, "
        "well-proportioned slender model physique, graceful shoulders, slender waist, "
        "tall slender high-fashion model silhouette, balanced 20% headroom margin above head, "
        "well-balanced human anatomy with refined small head proportion. "
    )

    # 🖐️ 포즈: 주제별 맞춤 스탠딩/착석 구분 (스마트폰 파지 배제, 자연스러운 제스처)
    if norm_id == 3:
        natural_pose = (
            "standing gracefully with an elegant tall posture by the rooftop glass railing, perfectly upright model silhouette, "
            "holding a delicate crystal wine glass comfortably at lower waist level in one hand, other arm resting naturally, "
            "NO smartphone held in hands, poised confident high-society VIP posture. "
        )
        environment_action = f"standing on {bg}. "
    elif norm_id == 4:
        natural_pose = (
            "seated comfortably and gracefully inside the single designer white lounge armchair with an elegant upright posture, "
            "arms resting naturally on the armchair, cardigan layered softly, NO smartphone held in hands, professional editorial model photoshoot posture. "
        )
        environment_action = f"seated inside the designer armchair with {bg}. "
    elif norm_id == 6:
        natural_pose = (
            "standing with an upright tall 8-head model posture by the outdoor rooftop sky lounge glass railing, "
            "broad masculine shoulders and slender waist, arms resting naturally at sides, hands visible outside pockets, strictly no hands in pockets, strictly no hands in pants, NO smartphone held in hands, handsome male model standing pose. "
        )
        environment_action = f"standing outdoors on {bg}. "
    elif norm_id == 7:
        natural_pose = (
            "seated comfortably and gracefully in an upright posture at the cafe table, "
            "both hands and slender elegant fingers clearly visible resting naturally and gracefully on top of the cafe table in front of her, "
            "hands resting openly on the table surface, strictly no hidden hands, strictly no hands inside sleeves, strictly no folded arms hiding hands, "
            "NO smartphone held in hands, chic confident influencer dating posture. "
        )
        environment_action = f"sitting at {bg}. "
    elif norm_id == 8:
        natural_pose = (
            "seated comfortably and gracefully in an upright posture across the sunny outdoor terrace cafe brown wooden table, "
            "both hands and slender elegant fingers clearly visible resting naturally and gracefully on top of the warm natural brown wooden terrace table in front of her, "
            "hands resting openly on the wood tabletop surface, strictly no hidden hands, strictly no hands in pockets, strictly no hands inside sleeves, strictly no crossed arms, "
            "NO smartphone held in hands, refreshing athletic fitness dating posture. "
        )
        environment_action = f"sitting at the outdoor terrace cafe wooden table with {bg}. "
    else:
        natural_pose = (
            "seated comfortably in an upright conversational posture with arms resting naturally on table or chair, "
            "both hands clearly visible resting naturally on table, NO smartphone held in hands, natural effortless human posture. "
        )
        environment_action = f"sitting in {bg}. "

    # 💡 [3점 입체 조명 & 골든 림라이트 & 실사 텍스처 헌법]
    lighting_mandate = (
        "cinematic warm 3-point portrait lighting, soft diffused warm key lighting from 45-degree angle casting subtle natural shadows across jawline and cheekbones creating rich 3D facial depth, "
        "subtle warm golden rim light outlining hair strands and jacket shoulders, "
        "realistic skin subsurface scattering, natural subtle skin highlights, NO flat camera flash look, "
    )

    # 긍정 프롬프트 최종 조립 (100% 정면 직립 POV + 8등신 소두 모델 비율 + 입체 조명 + f/11 딥 팬포커스 무필터 실사 규격)
    positive = (
        f"masterpiece, best quality, ultra-photorealistic portrait, authentic candid snapshot shot on iPhone 15 Pro, "
        f"{framing} of {char}. "
        f"{environment_action}"
        f"{natural_pose}"
        f"{body_proportion_mandate}"
        f"{head_and_mouth_mandate}"
        f"{lighting_mandate}"
        f"Raw unedited authentic iPhone 15 Pro 48MP mobile camera capture, realistic human skin texture with visible real pores and authentic fine details, "
        f"Apple iPhone 15 Pro Smart HDR photo, authentic mobile camera sensor capture, pristine optical sharpness, rich deep blacks, high micro-contrast, crisp clean highlights, punchy vivid clarity, NO beauty filter, zero skin smoothing, "
        f"f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background in tack sharp crisp focus."
    )

    # 주제별 특화 네거티브 차단
    topic_specific_neg = ""
    if norm_id == 1:
        topic_specific_neg = (
            "man, male, man's back, back of head, back of shoulder, man's shoulder, suit jacket in foreground, over-the-shoulder, 2 people, two people, second person, obstructed foreground, "
            "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
        )
    elif norm_id == 2:
        topic_specific_neg = (
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, soft skin, glowing skin, dreamy glow, "
            "blurry background, bokeh, bokeh blur, shallow depth of field, out of focus background, hazy, smeared texture, low contrast, "
        )
    elif norm_id == 4:
        topic_specific_neg = (
            "strobe, softbox, studio lighting, beauty filter, airbrushed skin, plastic skin, porcelain skin, skin smoothing, glamour glow, soft glow, creamy skin, "
            "curtain, sheer curtain, window, sunlight streaming through, outdoor, cafe, dining table, brunch table, "
            "backlight, backlighting, optical halation, lens flare, hazy glow, dreamy glow, blown out background, washed out, "
        )
    elif norm_id == 5:
        topic_specific_neg = (
            "t-shirt, crew neck, short sleeves, sleeves, baggy clothes, casual cotton tee, round neck, "
        )
    elif norm_id == 6:
        topic_specific_neg = (
            "hands in pockets, hands in jacket pockets, hands in pants pockets, hidden hands, "
            "anime, manga, manhwa, webtoon, cartoon, 3d render, cgi, illustration, drawing, digital art, "
            "doll, plastic skin, porcelain skin, airbrushed skin, skin smoothing, beauty filter, fake face, alien chin, pointed chin, "
            "flat flash, harsh camera flash, whitewashed face, washed out skin, "
            "dark dotted shirt, patterned shirt, dark clothing, formal suit, necktie, buttoned-up formal collar, "
            "teenager, high school student, child, boy, baby face, "
            "middle-aged, 30s, 35 years old, uncle, stern face, "
            "completely exposed wide forehead, slicked hair, pomade, mushroom hair, helmet hair, puffy cartoon hair, "
            "ordinary face, average looking male, plain looking, flat nose, ugly, "
        )
    elif norm_id == 7:
        topic_specific_neg = (
            "white jacket, white windbreaker, white clothes, loose fit, baggy clothes, oversized jacket, puffy jacket, "
            "hidden hands, hands in sleeves, missing hands, hands under table, covered hands, crossed arms hiding hands, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, soft skin, glowing skin, dreamy glow, "
            "blurry background, bokeh, bokeh blur, shallow depth of field, out of focus background, hazy, smeared texture, low contrast, "
        )
    elif norm_id == 8:
        topic_specific_neg = (
            "silver table, metal table, aluminum table, stainless table, steel table, metallic tabletop, chrome tabletop, grey metal table, "
            "white jacket, white windbreaker, white clothes, loose fit, baggy clothes, oversized jacket, puffy jacket, "
            "hidden hands, hands in sleeves, missing hands, hands under table, covered hands, crossed arms hiding hands, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, soft skin, glowing skin, dreamy glow, "
            "blurry background, bokeh, bokeh blur, shallow depth of field, out of focus background, hazy, smeared texture, low contrast, "
        )

    # 부정 프롬프트 (대두, 얼빡샷, 하단 쏠림, 카우보이샷, 과도한 헤드룸, 고개 기울임, 갸웃거림, 스마트폰 파지, 열린 입, 치아 노출, 3D CGI, 렌즈 블러 원천 차단)
    negative = (
        f"{topic_specific_neg}"
        "cowboy shot, thighs, knees, full body, standing, excessive headroom, empty top half, giant empty ceiling, subject placed too low, character sinking to bottom, bottom heavy framing, tiny face at bottom, "
        "big head, large head, oversized head, bobblehead, broad face, wide jaw, chubby cheeks, fat face, "
        "short thick neck, swollen neck, disproportionate body ratio, giant head, macro face shot, tight bust shot, passport photo crop, "
        "tilted head, head tilt, cocked head, head tilted to the side, crooked head, tilted neck, asymmetric head angle, off-axis head posture, slanted head, "
        "holding phone, phone in hand, smartphone facing camera, electronic device in hand, "
        "open mouth, parted lips, slightly open mouth, half-open mouth, open lips, visible teeth, showing teeth, teeth, smiling with teeth, grinning, laughing, "
        "distant shot, far away, microscopic figure, tiny face, subject far in distance, head cut off, cropped top of head, "
        "deformed fingers, extra digits, missing fingers, bad hands, mutated hands, "
        "cartoon, 3d render, anime, plastic skin, doll, dull, dark, lowres, text, watermark, "
        "blurry, lens blur, out of focus, soft focus, bokeh blur, depth of field blur, hazy, dreamy glow, overexposed, airbrushed, beauty filter, skin smoothing"
    )

    return {"positive": positive, "negative": negative}
