# -*- coding: utf-8 -*-
"""
ShortsCharacterAnchorInsurance - 🛡️ [보험 리밸런스 전용 캐릭터 & 배경 앵커 모듈]
- 8대 국민 보험 주제별 실제 주 타깃 연령층(30대~50대) 일반인 소비자 페르소나
- 딱딱한 정장 전문가 ❌ ➔ 편안하고 신뢰감 있는 일상 사복의 일반인(내돈내산 호갱탈출 팁) ⭕
- Wan 2.2 S2V 립싱크 헌법 준수:
  1. 치아 노출 제로, 입을 부드럽게 다문 온화한 미소 (gently closed mouth)
  2. 스마트폰 파지 완전 배제 (순수 인물 상반신 포즈)
  3. 황금 상반신 1.4m 미디엄 버스트 샷 (가슴 상단~머리, 300px+ 고해상도 얼굴 디테일)
  4. 눈 뒤집힘(rolled back eyes) 및 동공 왜곡 100% 원천 차단
"""

from typing import Dict, Any, Optional

INSURANCE_TOPIC_SPECS = {
    1: {
        "topic_id": 1,
        "title": "실손의료비 4세대 전환 손익",
        "gender": "female",
        "age": 42,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, graceful neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, comfortably sitting upright on a modern living room sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures"
        ),
        "char_desc": (
            "an authentic relatable 42-year-old Korean woman (homemaker and working professional), healthy glowing skin, neat natural elegant hairstyle, "
            "wearing clean stylish civilian casual clothes, a chic modern daily outfit, "
            "approachable civilian consumer persona, looking directly into camera with genuine composed closed-mouth expression (lips fully closed together, zero teeth)"
        ),
        "bg_desc": (
            "modern bright sunlit apartment living room with cozy neutral fabric sofa, stylish clean bookshelf and fresh green indoor plants in background, "
            "crisp clear natural window daylight, vivid vibrant realistic color balance, tack sharp f/11 deep pan-focus, zero yellow tint"
        ),
        "vibe": "병원도 안 가는데 매달 11만원 내던 실비 1만2천원으로 줄이고 속 시원해진 40대 똑순이 주부/직장인"
    },
    2: {
        "topic_id": 2,
        "title": "운전자보험 1만원대 다이어트",
        "gender": "male",
        "age": 36,
        "framing": (
            "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
            "clear medium waist-up shot showing head, broad suited shoulders, suit jacket, arms, and torso down to the waistline and belt, "
            "subtle headroom occupying upper 5% of frame, "
            "solo 1person male, standing with natural upright posture, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, head held straight and level, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, symmetrical eyes with natural relaxed eyelids, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures"
        ),
        "char_desc": (
            "a handsome and sharp 35-year-old Korean male professional, youthful attractive look, "
            "strictly no glasses, bare clean face with clear natural skin, authentic handsome Korean male facial features, attractive gentle dark eyes, sharp clean jawline, "
            "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe), "
            "wearing a sharp tailored dark navy business suit jacket over a crisp white dress shirt and neat tie, pristine executive professional look, "
            "looking directly into camera lens with confident composed closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama handsome relatable commuter look"
        ),
        "bg_desc": (
            "bustling modern Seoul Gangnam business boulevard background with modern architectural glass facade and green city trees behind him, "
            "bright crisp natural morning sunlight, crystal clear edge-to-edge deep focus across the entire scene, vivid authentic Korean city realism, zero yellow tint"
        ),
        "vibe": "강남/여의도 도심 빌딩 숲 출근길에서 1만3천원 운전자보험 꿀팁 알려주는 훈남 직장인 실사 비주얼"
    },
    3: {
        "topic_id": 3,
        "title": "암보험 일반암 vs 유사암 진실",
        "gender": "female",
        "age": 45,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright in a modern home study library, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus across entire frame, visible fine skin pores and fabric textures"
        ),
        "char_desc": (
            "a poised and sensible 45-year-old Korean career woman, clear fair skin, neat graceful short bob hairstyle, "
            "wearing an elegant, neat, and sophisticated luxury knit sweater, articulate and trustworthy closed-mouth expression looking directly into camera (lips completely closed, zero teeth)"
        ),
        "bg_desc": (
            "warm modern home study library with dark oak bookshelves filled with books, warm ambient lighting, crisp deep focus"
        ),
        "vibe": "건강검진 앞두고 증권 열어봤다가 갑상선암 500만원 보고 깜짝 놀라 팩트체크한 40대 여성"
    },
    4: {
        "topic_id": 4,
        "title": "뇌·심장 질환 뇌출혈 vs 뇌혈관",
        "gender": "male",
        "age": 42,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, masculine neck, broad natural shoulders, chest, and upper torso, "
            "solo 1person male, standing upright in a bright modern luxury living room, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus across entire frame, visible fine skin pores and fabric textures"
        ),
        "char_desc": (
            "an exceptionally handsome, stylish, and trustworthy 40s Korean male (youthful handsome look in his early 40s), "
            "clear smooth healthy skin, sharp masculine jawline, warm honest engaging dark eyes, "
            "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair), "
            "wearing a modern sophisticated charcoal-grey crewneck knit sweater, chic high-end Korean civilian casual look, "
            "looking directly into camera lens with composed trustworthy closed-mouth expression (lips firmly closed together, strictly zero teeth showing)"
        ),
        "bg_desc": (
            "bright modern luxury living room with large window showing soft daylight, minimalist Scandinavian wooden furniture, tack sharp focus"
        ),
        "vibe": "혈압약 먹기 시작해서 증권 펴봤더니 뇌경색 미보장인 거 알고 뇌혈관으로 제대로 갈아탄 40대 가장"
    },
    5: {
        "topic_id": 5,
        "title": "아는 사람 부탁으로 가입한 보험 손익 분석",
        "gender": "male",
        "age": 33,
        "framing": (
            "photographed from 2.5 meters away on Apple iPhone 15 Pro, "
            "clear medium waist-up upper body shot showing head, masculine neck, broad natural shoulders, white oxford cotton shirt, arms, and torso down to the waistline, "
            "subtle headroom occupying upper 5% of frame, "
            "solo 1person male, sitting naturally and upright on a modern wooden chair in a contemporary cafe lounge, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, head held straight and level, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus across entire frame, visible fine skin pores and sharp fabric textures"
        ),
        "char_desc": (
            "an exceptionally handsome and charming 33-year-old Korean male professional (top-tier Korean drama male lead actor look, striking youthful attractive look in his early 30s), "
            "strictly no glasses, bare clean face with clear smooth healthy skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, warm charismatic dark eyes, "
            "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair), "
            "wearing a crisp tailored modern white oxford cotton shirt, sophisticated high-end Korean civilian smart casual look, "
            "looking directly into camera lens with composed trustworthy closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama handsome relatable lead look"
        ),
        "bg_desc": (
            "contemporary bright modern Scandinavian cafe lounge with warm wooden interior and soft natural daylight through window, tack sharp f/11 focus"
        ),
        "vibe": "지인 권유로 들었던 보험의 매달 새는 돈을 1초 만에 확인하고 스마트하게 리모델링한 30대 훈남 가장"
    },
    6: {
        "topic_id": 6,
        "title": "어린이·어른이 100세 만기 리모델링",
        "gender": "female",
        "age": 30,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright on a stylish modern lounge sofa, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a gorgeous and charming 30-year-old Korean young woman, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive gentle brown eyes, "
            "neat and stylish natural soft wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "부모님이 100세 만기로 들어준 보험 서른 살 넘어 열어보고 비갱신형으로 알뜰하게 리모델링한 8등신 30대 훈녀 직장인/엄마"
    },
    7: {
        "topic_id": 7,
        "title": "내 보험 정밀 비교 & 새는 보험료 다이어트",
        "gender": "female",
        "age": 37,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright in a modern Scandinavian living room, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a poised and intelligent 37-year-old Korean woman (smart professional and homemaker), perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive articulate eyes, "
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
        "vibe": "매달 20~30만원씩 나가던 가족 보험 34개사와 정밀 비교해서 더 싸고 보장 좋은 최저가로 깔끔하게 다이어트한 똑순이 30대 여성"
    },
    8: {
        "topic_id": 8,
        "title": "AI 보험료 역추정 비교 & 가성비 리모델링",
        "gender": "female",
        "age": 39,
        "framing": (
            "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
            "solo 1person female, sitting upright in a modern Scandinavian living room, perfectly centered in frame, "
            "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures"
        ),
        "char_desc": (
            "a poised, elegant, and intelligent 39-year-old Korean woman (smart professional and homemaker), perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear glowing healthy skin, authentic beautiful Korean female facial features, attractive reassuring brown eyes, "
            "neat and stylish natural dark brown wavy hairstyle, "
            "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
            "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
            "modern K-drama relatable civilian look"
        ),
        "bg_desc": (
            "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
            "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
            "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint"
        ),
        "vibe": "전화번호 입력 없이 AI 역추정으로 같은 가격에 보장 더 큰 최적의 보험을 찾아낸 똑순이 30대 후반 여성"
    }
}


def build_insurance_shorts_t2i_character_prompt(
    topic_id: int = 1,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None,
    gender: Optional[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    보험 리밸런스 8대 주제별 실제 타깃 연령대(30대~50대) 일반인 마스터 프롬프트 빌더
    - 일상 사복 패션 & 편안한 공간 배경
    - 립싱크 최적화 (gently and firmly closed mouth, strictly zero teeth)
    - 1.4m 미디엄 버스트 샷 (얼굴 해상도 300px+ 확보 및 동공 이탈 원천 차단)
    """
    preset_key = ((topic_id - 1) % len(INSURANCE_TOPIC_SPECS)) + 1
    spec = INSURANCE_TOPIC_SPECS.get(preset_key, INSURANCE_TOPIC_SPECS[1])

    char_desc = custom_char_desc or spec["char_desc"]
    bg_desc = custom_bg_desc or spec["bg_desc"]
    effective_gender = gender or spec.get("gender", "female")

    # 🤐 S2V 립싱크 전용 정면 직립 + 입술 밀착 다문 표정 + 완벽한 정면 동공 응시
    head_and_mouth_mandate = (
        "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, "
        "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into the camera lens at horizontal eye level, symmetrical eyes, natural relaxed eyelids, "
        "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
        "composed calm trustworthy civilian expression, ready to speak with authentic eye contact"
    )

    # 주제별 맞춤 framing 지원
    if "framing" in spec:
        framing = spec["framing"]
    else:
        framing = (
            f"photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
            f"clear medium bust shot, showing head, natural neck, shoulders, chest, and upper torso, "
            f"solo 1person {effective_gender}, sitting comfortably and upright in a bright modern room, "
            f"perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
            f"perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
            f"gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
            f"spacious bright modern apartment background, f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus, visible fine skin pores and fabric textures"
        )

    positive_prompt = (
        f"{framing}, {head_and_mouth_mandate}, {char_desc}, {bg_desc}, "
        f"natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
    )

    negative_prompt = (
        "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
        "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
        "cropped forehead, cropped head, head touching frame top, cut off head, "
        "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
        "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
        "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
        "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, awkward stiff pose, robotic posture, "
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

