# -*- coding: utf-8 -*-
"""
ShortsCharacterAnchorStock - 📈 [StockMaster AI 전용 캐릭터 & 배경 앵커 모듈]
- 8대 주식/투자 주제별 실제 주 타깃 연령층(20대~40대) 스마트 직장인·개미 투자자 페르소나
- 딱딱한 금융맨 ❌ ➔ 스마트하고 세련된 일상 사복의 현실 투자자(내돈내산 퀀트 분석가) ⭕
- Wan 2.2 S2V 립싱크 헌법 준수:
  1. 치아 노출 제로, 입을 부드럽게 다문 신뢰감 있는 미소 (gently and firmly closed mouth)
  2. 스마트폰 파지 완전 배제 (순수 인물 상반신 포즈)
  3. 황금 상반신 1.4m 미디엄 버스트 샷 (가슴 상단~머리, 300px+ 고해상도 얼굴 디테일)
  4. 눈 뒤집힘(rolled back eyes) 및 동공 왜곡 100% 원천 차단
"""

from typing import Dict, Any, Optional

STOCK_TOPIC_SPECS = {
    1: {
        "topic_id": 1,
        "title": "삼성전자 vs SK하이닉스 HBM 수급 대결",
        "gender": "female",
        "age": 24,
        "framing": (
            "photographed from 2.5 meters away directly in front on Apple iPhone 15 Pro, "
            "candid medium cowboy shot showing head, elegant neck, natural shoulders, chest, waist, and sleek modern glass anchor desk clearly, generous balanced headroom occupying upper 10% of frame, "
            "solo 1person female, sitting upright and comfortably at the news anchor desk, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "an exceptionally gorgeous, captivating, and glamorous 24-year-old Korean female financial news anchor, "
            "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, "
            "breathtakingly stunning K-drama visual beauty, voluminous natural dark silky wavy hair, "
            "seductive feline cat-like hazel eyes with subtle elegant eyeliner, flawless luminous glass skin with soft natural cheek blush, "
            "wearing an exceptionally neat, clean, and elegant formal business suit, a tailored slim-fit dark navy blazer suit jacket over a crisp clean white collared shirt, "
            "minimalist sophisticated Korean television news anchor formal suit fashion, impeccably ironed fabric with zero wrinkles, "
            "looking directly into camera lens with composed confident closed-mouth expression (lips firmly closed together, strictly zero teeth showing)"
        ),
        "bg_desc": (
            "state-of-the-art modern Korean broadcast television news studio in Yeouido Seoul, "
            "sleek high-tech financial newsroom backdrop with sophisticated dark navy and golden-amber glowing LED digital display walls showing subtle abstract financial market charts, "
            "polished modern broadcast anchor desk, professional studio key lights and soft rim lighting, "
            "crystal clear f/11 pan-focus, vivid authentic broadcast realism, zero yellow tint"
        ),
        "vibe": "여의도 방송국 메인 경제 뉴스룸에서 속보를 전하는 24세 고양이상 초미모 여신 아나운서"
    },
    2: {
        "topic_id": 2,
        "title": "SK하이닉스 HBM 수급 & 퀀트 적정주가 실시간 분석",
        "gender": "male",
        "age": 26,
        "framing": (
            "photographed from 2.5 meters away directly in front on Apple iPhone 15 Pro, "
            "candid medium cowboy shot showing head, masculine neck, broad natural shoulders, chest, waist, and sleek modern glass anchor desk clearly, generous balanced headroom occupying upper 10% of frame, "
            "solo 1person male, sitting upright and comfortably at the news anchor desk, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "an exceptionally handsome 26-year-old Korean male financial news anchor (K-drama male lead actor visual, delicate handsome idol-actor appearance, refined aesthetic features), "
            "perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, broad masculine shoulders, "
            "sharp sculpted jawline with natural subtle directional shadow, charismatic warm intelligent dark eyes looking straight into camera, "
            "neat stylish dark natural dandy haircut with subtle parted fringe, flawless clear healthy skin, "
            "wearing an exceptionally neat, clean, and elegant formal business suit, a tailored slim-fit dark charcoal navy blazer suit jacket over a crisp clean white collared dress shirt and modern slim tie, "
            "minimalist sophisticated Korean television news anchor formal suit fashion, impeccably ironed fabric with zero wrinkles, "
            "looking directly into camera lens with composed confident closed-mouth expression (lips firmly closed together, strictly zero teeth showing)"
        ),
        "bg_desc": (
            "state-of-the-art modern Korean broadcast television news studio in Yeouido Seoul, "
            "sleek high-tech financial newsroom backdrop with sophisticated dark navy and golden-amber glowing LED digital display walls showing subtle abstract financial market charts, "
            "polished modern broadcast anchor desk, professional studio key lights and soft rim lighting, "
            "crystal clear f/11 pan-focus, vivid authentic broadcast realism, zero yellow tint"
        ),
        "vibe": "여의도 방송국 메인 경제 뉴스룸에서 SK하이닉스 퀀트 속보를 전하는 26세 K-드라마 남주급 훈남 아나운서"
    },
    3: {
        "topic_id": 3,
        "title": "엔비디아(NVDA) AI 빅테크 실시간 밸류에이션",
        "gender": "male",
        "age": 36,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, masculine neck, natural broad shoulders, chest, and upper torso, "
            "solo 1person male, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a handsome, tech-savvy, and sharp 36-year-old Korean male software engineer and tech stock investor, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing healthy skin, authentic handsome Korean male facial features, attractive sharp dark eyes, "
            "stylish trendy natural wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian tech investor look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor greenery, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "엔비디아와 빅테크 실시간 적정주가를 AI로 팩트체크하는 30대 테크 서학개미"
    },
    4: {
        "topic_id": 4,
        "title": "국내 저PBR 밸류업 & 고배당 금융지주",
        "gender": "female",
        "age": 35,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a poised and intelligent 35-year-old Korean financial analyst and retail investor, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive articulate dark eyes, "
            "neat and stylish natural dark brown shoulder-length bob hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "정부 밸류업 정책 터지자마자 PBR 1배 미만 알짜 금융지주사 쏙 골라낸 30대 여성 투자자"
    },
    5: {
        "topic_id": 5,
        "title": "뇌동매매 방지! AI 자동 손절매 & 리스크 가드",
        "gender": "male",
        "age": 31,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, masculine neck, broad natural shoulders, chest, and upper torso, "
            "solo 1person male, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a handsome, disciplined 31-year-old Korean retail investor, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing healthy skin, authentic handsome Korean male facial features, attractive honest dark eyes, "
            "neat and stylish natural comma perm hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "급등주 추격매수로 물렸다가 AI 기계적 손절매 원칙으로 계좌 살려낸 30대 훈남 직장인"
    },
    6: {
        "topic_id": 6,
        "title": "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리",
        "gender": "female",
        "age": 29,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a gorgeous, energetic 29-year-old Korean working woman, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive cheerful brown eyes, "
            "neat and stylish natural long wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "월급 50만원씩 10년 적립식 복리 투자로 은퇴 자산 굴리는 20대 후반 사회초년생"
    },
    7: {
        "topic_id": 7,
        "title": "외국인·기관 쌍끌이 순매수 실시간 레이더",
        "gender": "male",
        "age": 38,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, masculine neck, broad natural shoulders, chest, and upper torso, "
            "solo 1person male, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "an articulate, seasoned 38-year-old Korean male investor, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing healthy skin, authentic handsome Korean male facial features, attractive penetrating dark eyes, "
            "neat and stylish natural parted wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "기관과 외국인 메이저 수급 추종 매매로 안정적인 수익률 내는 30대 베테랑 직장인 투자자"
    },
    8: {
        "topic_id": 8,
        "title": "초보 탈출! 원클릭 AI 종목 재무 건전성 진단",
        "gender": "female",
        "age": 36,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright and comfortably on a stylish modern Scandinavian lounge armchair sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a poised, elegant, and intelligent 36-year-old Korean career woman, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing healthy skin, authentic beautiful Korean female facial features, attractive reassuring dark eyes, "
            "neat and stylish natural dark brown shoulder-length wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "어려운 재무제표 대신 AI 원클릭 진단으로 깡통 종목 거르고 알짜 종목 고르는 30대 여성 투자자"
    }
}


def build_stock_shorts_t2i_character_prompt(
    topic_id: int = 1,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None,
    gender: Optional[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    StockMaster AI 8대 주제별 실제 타깃 연령대(20대~40대) 8등신 스마트 개미 투자자 프롬프트 빌더
    - 1.4m 황금 상반신 미디엄 버스트 샷 (얼굴 해상도 300px+ 확보)
    - 눈 뒤집힘(rolled back eyes) 및 동공 왜곡 100% 원천 차단
    """
    preset_key = ((topic_id - 1) % len(STOCK_TOPIC_SPECS)) + 1
    spec = STOCK_TOPIC_SPECS.get(preset_key, STOCK_TOPIC_SPECS[1])

    char_desc = custom_char_desc or spec["char_desc"]
    bg_desc = custom_bg_desc or spec["bg_desc"]
    effective_gender = gender or spec.get("gender", "male")

    # 🤐 S2V 립싱크 전용 정면 직립 + 입술 밀착 다문 표정 + 완벽한 정면 동공 응시
    head_and_mouth_mandate = (
        "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, "
        "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into the camera lens at horizontal eye level, symmetrical eyes, natural relaxed eyelids, "
        "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
        "composed calm trustworthy civilian expression, ready to speak with authentic eye contact"
    )

    framing = spec.get("framing", (
        f"photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
        f"clear medium bust shot, showing head, natural neck, shoulders, chest, and upper torso, "
        f"solo 1person {effective_gender}, sitting comfortably and upright in a bright modern room, "
        f"perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
        f"perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
        f"gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
        f"spacious bright modern apartment background, f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus, visible fine skin pores and clothing fabric textures"
    ))

    positive_prompt = (
        f"{framing}, {head_and_mouth_mandate}, {char_desc}, {bg_desc}, "
        f"natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
    )

    negative_prompt = (
        "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
        "distant full body shot, wide long shot, far away tiny figure, tiny head, zoomed out far shot, extreme distant shot, "
        "extreme close-up, cropped forehead, cropped head, head touching frame top, cut off head, "
        "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
        "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
        "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
        "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, "
        "polo shirt, collared shirt, tucked in shirt, blue polo sweater, awkward stiff pose, robotic posture, hands on knees pose, awkward hands, "
        "showing teeth, open mouth, teeth, grinning, smiling with open mouth, smiling with teeth, parted lips, tooth, dental, toothy smile, big smile, mouth open, laughing with teeth, screaming, "
        "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
        "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, "
        "looking down, face obstructed, phone blocking face, phone covering mouth, "
        "tilted head, sideways glance, looking away from camera, angled face, side profile, "
        "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
        "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
    )

    return {
        "positive": positive_prompt,
        "negative": negative_prompt,
        "topic_id": topic_id,
        "gender": effective_gender,
        "vibe": spec.get("vibe", "")
    }
