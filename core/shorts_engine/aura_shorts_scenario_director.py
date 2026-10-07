# -*- coding: utf-8 -*-
"""
AuraShortsScenarioDirector - 🎬 [Aura 8대 주제 22초 3단계 숏폼 대본 & 비주얼 오버레이 디렉터]
- 8대 주제별 인물 정의 및 배경 정의와 100% 일치 연동
- Wan 2.2 S2V 립싱크 모션 프롬프트: 1.2m 친밀한 테이블 대화 제스처 (스마트폰 파지 배제)
- 22초 3단계 완결형 단일 스토리라인:
  1) [0초 ~ 10초] 인물 립싱크 킬러 훅 (소개팅 썰, 공감 포인트)
  2) [10초 ~ 18초] 라이브 앱 기능 안내 (탈출 전화, 자막 통화, 50:50 게이트 등)
  3) [18초 ~ 22초] 안심 신뢰 뱃지 & 공식 검색어 촉구 CTA ("네이버에 아우라AI데이팅 검색")
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraShortsScenarioDirector")


class AuraShortsScenarioDirector:
    """Aura 22초 완결형 숏폼 대본 및 화면 오버레이 기획 엔진"""

    SCRIPTS_22S = {
        1: {
            "topic_id": 1,
            "theme_name": "소개팅 탈출 전화",
            "theme_code": "escape_call",
            "gender": "female",
            "hook_p1_5s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요?",
            "hook_p2_5s": "화장실로 튀어서 일 분 뒤 긴급 탈출 예약을 딱 누르세요!",
            "hook_0_10s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요? 화장실로 튀어서 일 분 뒤 긴급 탈출 예약을 딱 누르세요!",
            "app_10_18s": "일 분 뒤에 진짜 구원 전화가 걸려오고 화면에 탈출 대본까지 다 떠요!",
            "cta_18_22s": "합법적으로 칼탈출 성공! 네이버에 아우라AI데이팅 한번 검색해보세요!",
            "debate_question": "이 탈출법, 센스다 vs 너무하다?",
            "hero_copy": "합법적으로 칼탈출 성공!",
            "top_header": "",
            "bottom_step1_title": "",
            "bottom_step1_sub": "",
            "bottom_step2_title": "",
            "bottom_step2_sub": "",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a beautiful 28-year-old Korean office woman sitting across a dinner table, looking directly into camera with expressive authentic eye contact, "
                "speaking articulate words with natural lip sync and expressive mouth articulation, gentle head nodding and subtle head tilts, dynamic upper body gestures, leaning forward slightly in a lively engaging conversation, no phone in hand, natural lifelike motion"
            ),
            "char_desc": (
                "a beautiful 28-year-old Korean woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face, slender elegant long neck, calm low ponytail hairstyle, clear fair skin, "
                "refined subtle makeup, wearing stylish sophisticated civilian dating clothes, a chic modern evening dinner outfit, "
                "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
            ),
            "bg_desc": (
                "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
                "antique dark wooden dining table, blurred delicate wine glasses and neat linen napkin in the background"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        },
        2: {
            "topic_id": 2,
            "theme_name": "실시간 자막 통화",
            "theme_code": "live_subtitles",
            "gender": "female",
            "hook_p1_5s": "곤니치와! 저 한국어 1도 모르는데 친구 사귄 비결!",
            "hook_p2_5s": "아우라 앱으로 영상통화 걸면 화면 밑에 넷플릭스처럼 실시간 자막이 다 떠요!",
            "hook_0_10s": "곤니치와! 저 한국어 1도 모르는데 친구 사귄 비결! 아우라 앱으로 영상통화 걸면 화면 밑에 넷플릭스처럼 실시간 자막이 다 떠요!",
            "app_10_18s": "제가 일본어로 말하면 한국어 자막이 실시간으로 뜨고, 한국어로 말씀하셔도 일본어로 번역돼서 소통 끝!",
            "cta_18_22s": "일본인 친구 생기면 도쿄에서 어디 가고 싶으신가요? 네이버에 아우라AI데이팅 검색해보세요!",
            "debate_question": "자막 통화로 외국인 친구 사귀기, 가능하다 vs 어렵다?",
            "top_header": "",
            "bottom_step1_title": "",
            "bottom_step1_sub": "",
            "bottom_step2_title": "",
            "bottom_step2_sub": "",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a lovely 24-year-old Japanese young woman (Nanami) in Tokyo, sitting in an authentic living room with wooden bookshelves and green plants, looking directly into camera with charming sweet eye contact, "
                "speaking naturally with smooth clear lip sync, lively head tilting and friendly nodding while talking, expressive upper body gestures, relaxed engaging conversational movement, no phone in hand, lifelike video call motion"
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
            "voice_pitch": "+5Hz",
            "voice_rate": "+6%"
        },
        3: {
            "topic_id": 3,
            "theme_name": "50:50 VIP 게이트",
            "theme_code": "vip_gate",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱 깔았다가 남자가 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손?",
            "hook_p2_5s": "아우라는 남녀 성비 50:50 안 맞으면 남자 가입 대기 걸어버려요!",
            "hook_0_10s": "소개팅 앱 깔았다가 남자가 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손? 아우라는 남녀 성비 50:50 안 맞으면 남자 가입 대기 걸어버려요!",
            "app_10_18s": "남성은 정원 찰 때까지 줄 서서 대기하고, 여성은 VIP 프리패스로 바로 입장! 물 흐리는 사람 1도 없고 대화 퀄리티가 완전 달라요.",
            "cta_18_22s": "남녀 50:50 정원제, 찬성인가요 반대인가요? 불쾌감 없는 프리미엄 소개팅, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "50:50 황금 성비 청정 라운지 • AURA",
            "bottom_step1_title": "남탕 불쾌감 제로! 50:50 정원제",
            "bottom_step1_sub": "남성 대기열 관리 • 여성 VIP 프리패스 즉시 입장",
            "bottom_step2_title": "수질 100% 보장 • 청정 매너 라운지",
            "bottom_step2_sub": "엄격한 성비 관리 • 고품격 매너 라운지",
            "debate_question": "남녀 50:50 정원제, 찬성 vs 반대?",
            "hero_copy": "남초 제로, 50:50 완벽 성비!",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "an exceptionally gorgeous glamorous 26-year-old Korean woman standing by the glass railing of an upscale rooftop terrace, looking directly into camera with deeply captivating alluring eye contact, "
                "speaking smoothly with clear realistic lip sync, subtle head tilts and gentle nodding, holding a crystal wine glass comfortably at waist level, expressive feminine upper body gestures, captivating lively motion"
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
                "standing beside modern glass balustrade overlooking breathtaking panoramic sparkling glittering Seoul city night skyline and skyscraper lights against dark midnight blue sky, "
                "soft warm ambient architectural uplighting, glowing warm golden patio mood lamps creating dramatic rich depth, bokeh, and cinematic evening intimacy"
            ),
            "voice_pitch": "-7Hz",
            "voice_rate": "+12%"
        },
        4: {
            "topic_id": 4,
            "theme_name": "청담동 화보 보정",
            "theme_code": "cheongdam_enhance",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱에 인조인간 필터 올렸다가 실물 보고 도망가지 마시고...",
            "hook_p2_5s": "아우라 앱에 셀카 한 장 넣으면 청담동 화보로 바로 바꿔줍니다!",
            "hook_0_10s": "소개팅 앱에 인조인간 필터 올렸다가 실물 보고 도망가지 마시고, 아우라 앱에 셀카 한 장 넣으면 청담동 화보로 바로 바꿔줍니다!",
            "app_10_18s": "내 본래 이목구비는 그대로 살리면서 피부톤과 조명을 청담동 스튜디오 감성으로 세련되고 사랑스럽게 업그레이드해 줘요.",
            "cta_18_22s": "이 정도 보정이면 사기다 vs 자기관리다? 내 얼굴 그대로 인생 화보 만들기, 네이버에 아우라AI데이팅 검색해보세요!",
            "debate_question": "이 정도 보정, 사기다 vs 자기관리다?",
            "hero_copy": "내 본판 그대로 인생 화보 완성!",
            "top_header": "청담동 스냅 화보급 AI 보정 • AURA",
            "bottom_step1_title": "가짜 필터 NO! 본판 100% 보존",
            "bottom_step1_sub": "인위적인 틱톡 필터 탈피 • 자연스러운 실사 화보",
            "bottom_step2_title": "청담 스튜디오 감성 즉각 업그레이드",
            "bottom_step2_sub": "매칭률 5배 상승 • 세련되고 사랑스러운 무드",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a gorgeous 23-year-old Korean young woman, sitting gracefully in a designer white armchair inside a modern Cheongdam photography studio, looking directly into camera with radiant gentle eye contact, "
                "speaking smoothly with authentic lip sync, natural delicate head movements, subtle head tilting and gentle nodding, expressive soft upper body posture, lively editorial photoshoot motion, no phone in hand"
            ),
            "char_desc": (
                "a breathtakingly stunning 23-year-old Korean young woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck and collarbone, pure legendary first-love visual aesthetic, "
                "flowing natural dark silky wavy hair, immaculate luminous glass skin, captivating innocent eyes, delicate facial symmetry, "
                "wearing an elegant soft knit cardigan layered over a clean camisole, stylish feminine studio photoshoot attire, refined modern aesthetic fashion, looking directly into the camera lens"
            ),
            "bg_desc": (
                "high-end luxury photography studio in Cheongdam, modern curved architectural round arch alcove wall with soft warm peach-beige ambient indirect glow, "
                "elegant designer single white lounge armchair in the center, clean polished studio floor, tack sharp f/11 focus"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+3%"
        },
        5: {
            "topic_id": 5,
            "theme_name": "가치관 밸런스 매칭",
            "theme_code": "balance_match",
            "gender": "female",
            "hook_p1_5s": "소개팅 첫 만남 더치페이, 칼같이 반띵인가요? 아니면 번갈아 내기인가요?",
            "hook_p2_5s": "아우라에서 밸런스 게임 투표하면 나랑 가치관 똑같은 사람만 연결해 줘요!",
            "hook_0_10s": "소개팅 첫 만남 더치페이, 칼같이 반띵인가요? 아니면 번갈아 내기인가요? 아우라에서 밸런스 게임 투표하면 나랑 가치관 똑같은 사람만 연결해 줘요!",
            "app_10_18s": "얼굴만 보고 만났다가 연락 문제, 데이트 비용 때문에 싸우지 마세요! 가치관 100% 일치자만 매칭되니까 대화가 너무 잘 통해요.",
            "cta_18_22s": "첫 만남 더치페이, 여러분의 선택은? 나와 생각 통하는 사람 찾기, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "가치관 밸런스 매칭 • AURA",
            "bottom_step1_title": "연락 주기 & 데이트 비용 밸런스 투표",
            "bottom_step1_sub": "더치페이 vs 번갈아 내기 가치관 실시간 확인",
            "bottom_step2_title": "생각 100% 통하는 사람 즉시 연결",
            "bottom_step2_sub": "소비관/연애관 갈등 제로 • 편안한 연애 시작",
            "debate_question": "첫 만남 더치페이, 반띵 vs 번갈아 내기?",
            "hero_copy": "생각 통하는 사람만 100% 매칭!",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a bright friendly 21-year-old Korean college girl, seated comfortably at a brunch table, looking into camera with lively authentic eye contact, "
                "speaking expressively with smooth realistic lip sync, enthusiastic head nodding and playful head tilts, natural hand and upper body gestures while talking, friendly and dynamic movement, no phone in hand, lifelike motion"
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
                "cozy outdoor brunch cafe patio with lush green leaves canopy, rustic wooden table with iced latte, "
                "pleasant tree shade with dappled natural sunlight, tack sharp f/11 focus"
            ),
            "voice_pitch": "+6Hz",
            "voice_rate": "+6%"
        },
        6: {
            "topic_id": 6,
            "theme_name": "AI 첫대화 비서",
            "theme_code": "ai_icebreaker",
            "gender": "male",
            "hook_p1_5s": "마음에 드는 이성한테 첫 메세지 보낼 때, 뭐라고 보낼지 막막했던 적 있으시죠?",
            "hook_p2_5s": "아우라 AI 비서 켜면 상대 취향 딱 분석해서 센스 넘치는 첫마디를 써줘요!",
            "hook_0_10s": "마음에 드는 이성한테 첫 메세지 보낼 때, 뭐라고 보낼지 막막했던 적 있으시죠? 아우라 AI 비서 켜면 상대 취향 딱 분석해서 센스 넘치는 첫마디를 써줘요!",
            "app_10_18s": "상대 프로필을 분석해 1초 만에 티키타카 터지는 맞춤 대화를 추천해 주니까 첫 대화 피로도가 제로예요.",
            "cta_18_22s": "읽씹 없는 첫 대화 치트키, 네이버에 아우라AI데이팅 한번 검색해보세요!",
            "top_header": "AI 첫대화 답장 비서 • AURA",
            "bottom_step1_title": "읽씹 탈출! 상대 맞춤형 첫인사 생성",
            "bottom_step1_sub": "숨 막히는 단답 대화 원천 차단 • 티키타카 폭발",
            "bottom_step2_title": "AI 대화 코칭 • 애프터 성공률 98%",
            "bottom_step2_sub": "답장 고민 끝 • 센스 넘치는 자연스러운 핑퐁",
            "debate_question": "매칭 후 첫 메시지, 센스 멘트 vs 솔직 담백?",
            "hero_copy": "읽씹 없는 첫 대화 치트키 가동!",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "an exceptionally handsome 26-year-old Korean adult man (K-drama male lead actor visual), standing on an upscale outdoor rooftop sky lounge terrace at night, looking directly into camera with warm romantic eye contact, "
                "speaking expressively with highly synchronized lip movements, natural head tilting and gentle nodding while talking, dynamic subtle upper body gestures, natural shoulder movements, leaning forward slightly in a friendly engaging conversation, no phone in hand, lively authentic human motion"
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
            "voice_pitch": "-3Hz",
            "voice_rate": "+12%"
        },
        7: {
            "topic_id": 7,
            "theme_name": "AI 아우라 진단",
            "theme_code": "aura_diagnosis",
            "gender": "female",
            "hook_p1_5s": "요즘 인스타 스토리에서 난리 난 내 얼굴 아우라 매력 테스트 해보셨나요?",
            "hook_p2_5s": "셀카 한 장 넣었더니 AI가 상위 3.8% 다정한 여우상이라고 분석해 줬어요!",
            "hook_0_10s": "요즘 인스타 스토리에서 난리 난 내 얼굴 아우라 매력 테스트 해보셨나요? 셀카 한 장 넣었더니 AI가 상위 3.8% 다정한 여우상이라고 분석해 줬어요!",
            "app_10_18s": "내 얼굴의 고유한 분위기와 매력 키워드를 분석해서 인스타에 바로 올리고 싶은 고화질 진단 카드로 도출해 줍니다.",
            "cta_18_22s": "내 아우라 점수, 몇 점 나올 것 같으신가요? 내 고유의 매력 찾기, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "AI 매력도 진단 리포트 • AURA",
            "bottom_step1_title": "상위 % 아우라 진단 카드 도출",
            "bottom_step1_sub": "Gemini Vision AI 얼굴 분위기 & 매력 분석",
            "bottom_step2_title": "인스타 스토리 자랑용 고화질 카드",
            "bottom_step2_sub": "내 매력 타이틀 확인 • 바이럴 폭발 테스트",
            "debate_question": "내 얼굴 아우라 매력, 상위 몇 %일까?",
            "hero_copy": "AI 매력 분석, 상위 3.8% 진단!",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a fashionable 25-year-old Korean woman, sitting in a trendy cafe looking directly into camera with charming playful eye contact, "
                "smiling delightfully and speaking smoothly with authentic lip sync, gentle head tilting and subtle nodding, "
                "delicate subtle hand micro-gestures, natural small finger movements, no exaggerated hand waving, no wild arm movements, "
                "calm and elegant upper body posture, chic authentic lifelike motion"
            ),
            "char_desc": (
                "a mesmerizingly attractive 25-year-old Korean it-girl, perfect 8-head-high golden ratio model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, "
                "trendy textured dark hair with subtle soft ash highlights, flawless glowing porcelain skin, "
                "wearing a chic form-fitting ribbed knit top, trendy hip Seongsu cafe fashion, alluring stylish influencer aesthetic, looking directly into the camera lens"
            ),
            "bg_desc": (
                "trendy hip espresso bar and modern art gallery cafe in Seongsu-dong, mid-century modern aesthetic interior, "
                "framed contemporary art posters, warm designer lamp glow"
            ),
            "voice_pitch": "+1Hz",
            "voice_rate": "+7%"
        },
        8: {
            "topic_id": 8,
            "theme_name": "500m 안심 레이더",
            "theme_code": "safe_radar",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱에서 며칠씩 간만 보고 톡만 질질 끌다가 지치셨던 분들 계시죠?",
            "hook_p2_5s": "아우라는 내가 원할 때 동네 편한 친구를 500미터 안심 보안으로 바로 만날 수 있어요!",
            "hook_0_10s": "소개팅 앱에서 며칠씩 간만 보고 톡만 질질 끌다가 지치셨던 분들 계시죠? 아우라는 내가 원할 때 동네 편한 친구를 500미터 안심 보안으로 바로 만날 수 있어요!",
            "app_10_18s": "실제 주소 노출 없이 성수동 카페 메이트나 가벼운 러닝 메이트를 안전하게 찾아서 당일 번개로 만날 수 있어요.",
            "cta_18_22s": "동네 산책 메이트, 동성만 가능 vs 이성도 가능? 스토킹 걱정 없는 동네 친구, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "500m 안심 레이더 • AURA",
            "bottom_step1_title": "간보기 톡 지쳤다면? 500m 안심 매칭",
            "bottom_step1_sub": "내가 원할 때 바로 만나는 동네 편한 친구",
            "bottom_step2_title": "안전한 24시간 지도 퀘스트",
            "bottom_step2_sub": "실시간 러닝·카페 메이트 안심 번개",
            "debate_question": "동네 산책 메이트, 동성만 vs 이성도 가능?",
            "hero_copy": "스토킹 걱정 제로, 500m 안심 매칭!",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "an energetic 25-year-old Korean young woman, sitting at a sunny outdoor terrace cafe looking directly into camera with charming eye contact, "
                "speaking smoothly and naturally with clean lip sync, gentle head tilting and subtle nodding, "
                "delicate subtle hand micro-gestures with both hands and fingers resting on top of the terrace cafe table, natural small finger movements, calm and elegant upper body posture, active pleasant lifelike motion"
            ),
            "char_desc": (
                "an exceptionally stunning 25-year-old Korean fitness goddess visual, perfect 8-head-high golden ratio athletic model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, glowing radiant sun-kissed fair skin, "
                "sleek high ponytail hairstyle, "
                "wearing a chic rich saturated deep cobalt blue and dark navy form-fitting athletic zip-up top, sleek stylish outdoor activewear, refreshing fitness runner fashion, looking directly into the camera lens"
            ),
            "bg_desc": (
                "sunny outdoor terrace cafe near Seoul Forest park, lush green trees and park walking trail visible in background, "
                "bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+8%"
        }
    }

    @classmethod
    def get_full_scenario(
        cls,
        topic_id: int = 1,
        gender: Optional[str] = None,
        use_ai_script: bool = True
    ) -> Dict[str, Any]:
        """EasyTax의 get_full_scenario와 100% 동일한 인터페이스 반환 (제미나이 100% 자율 창작 대본 지원)"""
        norm_id = ((topic_id - 1) % len(cls.SCRIPTS_22S)) + 1
        s = cls.SCRIPTS_22S.get(norm_id, cls.SCRIPTS_22S[1])

        effective_gender = gender or s["gender"]

        hook_p1 = s.get("hook_p1_5s", "")
        hook_p2 = s.get("hook_p2_5s", "")
        hook_full = s.get("hook_0_10s", f"{hook_p1} {hook_p2}")
        app_speech = s.get("app_10_18s", "")
        cta_speech = s.get("cta_18_22s", "")
        debate_q = s.get("debate_question", "여러분의 생각은 어떠신가요?")

        # 🤖 [제미나이 2.5 Flash 실시간 자율 대본 생성]
        if use_ai_script:
            try:
                from brands.aura.aura_shorts_script_writer import AuraShortsScriptWriter
                ai_script = AuraShortsScriptWriter().generate_dynamic_script(topic_id=norm_id)
                if ai_script:
                    hook_p1 = ai_script.get("hook_p1_5s", hook_p1)
                    hook_p2 = ai_script.get("hook_p2_5s", hook_p2)
                    hook_full = ai_script.get("hook_0_10s", hook_full)
                    app_speech = ai_script.get("app_10_18s", app_speech)
                    cta_speech = ai_script.get("cta_18_22s", cta_speech)
                    debate_q = ai_script.get("debate_question", debate_q)
                    logger.info(f"🎉 [Aura 시나리오] 주제 #{norm_id} 제미나이 100% 순수 자율 창작 대본 탑재 완료")
            except Exception as e:
                logger.warning(f"⚠️ [Aura 시나리오] 제미나이 대본 생성 중 예외 발생, 골든 대본 유지: {e}")

        full_speech = f"{hook_full} {app_speech} {cta_speech}"

        visual_dir = {
            "top_header": s.get("top_header", ""),
            "bottom_step1_title": s.get("bottom_step1_title", ""),
            "bottom_step1_sub": s.get("bottom_step1_sub", ""),
            "bottom_step2_title": s.get("bottom_step2_title", ""),
            "bottom_step2_sub": s.get("bottom_step2_sub", ""),
            "cta_button_text": s.get("cta_button_text", "네이버에 [아우라AI데이팅] 검색 >")
        }

        return {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "gender": effective_gender,
            "speech_hook": hook_full,
            "speech_hook_part1": hook_p1,
            "speech_hook_part2": hook_p2,
            "speech_app": app_speech,
            "speech_cta": cta_speech,
            "debate_question": debate_q,
            "hero_copy": s.get("hero_copy", ""),
            "full_speech": full_speech,
            "visual_direction": visual_dir,
            "s2v_motion_prompt": s["s2v_motion_prompt"],
            "character_desc": s["char_desc"],
            "background_desc": s["bg_desc"],
            "voice_pitch": s.get("voice_pitch", "+6Hz"),
            "voice_rate": s.get("voice_rate", "+3%")
        }
