# -*- coding: utf-8 -*-
"""
PromptDirectorCardNews (K-Market) - 📸 [케이마켓 카드뉴스 전용 시나리오 & 프롬프트 디렉터]
- 핵심 원칙: '치아를 훤히 드러내고 활짝 웃으며 폰을 앞으로 내미는 극적 환희 컷'
- 0원 무료 생활 나눔, 수수료 0원 해외 송금의 기쁨 극대화
"""

from typing import Dict, Any


KMARKET_CARDNEWS_PROMPTS = {
    "vi": {
        "description": "an overjoyed Vietnamese young woman, laughing delightedly with sparkling white teeth showing in wide smile, joyful sparkling eyes",
        "headline": "압력밥솥·가구 0원 나눔 완료!",
        "subhead": "한국 생활 필수품, 이웃끼리 무료로 나누고 150만원 절약하세요."
    },
    "uz": {
        "description": "an ecstatic cheerful Uzbek young man, wide laughing toothy smile, delightfully thrusting smartphone forward towards camera",
        "headline": "수수료 0원 해외 송금 성공!",
        "subhead": "은행 갈 필요 없이 터치 한 번으로 안전하게 가족에게 송금."
    },
    "ko": {
        "description": "a joyful smiling Korean presenter woman, enthusiastic open toothy smile, excitedly showing smartphone forward",
        "headline": "케이마켓 무료 나눔 페스티벌!",
        "subhead": "외국인 주민과 따뜻한 정을 나누는 스마트 나눔 플랫폼."
    }
}


class PromptDirectorCardNewsKMarket:
    """케이마켓 카드뉴스 프롬프트 및 카피 디렉터"""

    @classmethod
    def get_t2i_prompt(cls, nationality_code: str = "vi") -> Dict[str, str]:
        """카드뉴스용 활짝 웃는 극적 환희 마스터컷 프롬프트 반환"""
        nat = KMARKET_CARDNEWS_PROMPTS.get(nationality_code, KMARKET_CARDNEWS_PROMPTS["vi"])

        pos = (
            f"masterpiece, best quality, ultra-photorealistic portrait of {nat['description']}, "
            f"sitting in a modern bright cozy apartment room. "
            f"She is proudly thrusting a modern smartphone forward towards the camera with one hand, "
            f"displaying the screen with vibrant energy. "
            f"Wide energetic open toothy smile, ecstatic thrilled expression, laughing cheerfully, "
            f"sharp focus on her face and the phone edge, natural skin pores, 8k uhd, professional studio lighting."
        )

        neg = (
            "closed mouth, sad, neutral, frowning, deformed fingers, extra digits, missing fingers, "
            "bad hands, blurry screen, tilted phone, overexposed, cartoon, 3d render, anime, plastic, lowres"
        )

        return {"positive": pos, "negative": neg}

    @classmethod
    def get_copywriting(cls, nationality_code: str = "vi") -> Dict[str, str]:
        """카드뉴스용 헤드카피 및 서브카피 반환"""
        nat = KMARKET_CARDNEWS_PROMPTS.get(nationality_code, KMARKET_CARDNEWS_PROMPTS["vi"])
        return {
            "headline": nat["headline"],
            "subhead": nat["subhead"],
            "badge": "K-MARKET 공식 생활 커뮤니티",
            "cta": "지금 무료 나눔 물품 확인하기 >"
        }
