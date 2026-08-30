"""
ScenarioDirectorShortsKMarket - 🛒 K-Market 전용 9:16 실물 매물/0원 나눔 숏폼 비디오 전담 시나리오 디렉터
- 270개 실물 매물 사진 & 대학가 무빙세일 숏폼 연출 기획
- ★ [규칙] 인물 등장 시 100% 동양인(Asian) 지정
"""

import random
from typing import Dict, Any, Optional

KMARKET_SHORTS_THEMES = [
    {"id": "km_shorts_0won_giveaway", "hook": "한국에서 가구/가전 0원에 얻는 법", "action": "Asian student smiling holding $0 giveaway sign in front of clean study desk"},
    {"id": "km_shorts_moving_sale", "hook": "대학가 원룸 무빙세일 꿀매물 대방출", "action": "young Asian expat student packing neat studio room with boxes and furniture"},
    {"id": "km_shorts_safe_arc_deal", "hook": "외국인등록증 인증 안전 직거래 현장", "action": "two Asian foreign students doing safe meetup deal near subway exit"},
    {"id": "km_shorts_17lang_chat", "hook": "한국어 몰라도 17개국 자동번역 채팅 거래", "action": "Asian person chatting happily on smartphone with instant translation"},
    {"id": "km_shorts_waste_fee_zero", "hook": "가구 버릴 때 폐기물 스티커 비용 0원 비법", "action": "showing clean studio room ready for new tenant without disposal fees"}
]

class ScenarioDirectorShortsKMarket:
    """K-Market 숏폼 비디오 전담 시나리오 디렉터"""
    def __init__(self):
        self.themes = KMARKET_SHORTS_THEMES

    def get_shorts_scenario(self, lang: str = "en") -> Dict[str, Any]:
        theme = random.choice(self.themes)
        return {
            "service_id": "kmarket",
            "theme_id": theme["id"],
            "hook": theme["hook"],
            "theme_name": theme["hook"],
            "content_mix_type": "50_50_mix",
            "action_prompt": f"cinematic authentic 9:16 vertical video of {theme['action']}, realistic Asian facial features, 4k realistic",
            "negative_prompt": "creepy smile, bad hands, distorted fingers, floating objects, caucasian, white person, blonde hair, non-asian"
        }
