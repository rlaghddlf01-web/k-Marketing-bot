# -*- coding: utf-8 -*-
"""
PromptDirectorCardNews (EasyTax) - 📸 [이지택스 카드뉴스 전용 시나리오 & 프롬프트 디렉터]
- 핵심 원칙: '치아를 훤히 드러내고 활짝 웃으며 폰을 앞으로 내미는 극적 환희 컷'
- 스크롤을 멈추게 하는 폭발적인 CTR(클릭률)과 세금 환급 기쁨의 카타르시스 극대화
- 1080x1350 (4:5 인스타그램/페이스북 표준 광고 캔버스) 최적화
"""

from typing import Dict, Any


CARDNEWS_NATIONALITIES = {
    "vi": {
        "description": "an ecstatic cheerful Vietnamese woman in her late 20s, laughing with pure joy, showing sparkling clean white teeth in a wide enthusiastic smile, sparkling happy eyes",
        "headline": "한국 세금 환급 310만원 입금 완료!",
        "subhead": "외국인 근로자 5년치 환급금, 놓치지 말고 지금 조회하세요."
    },
    "uz": {
        "description": "a joyfully smiling handsome Uzbek worker in his early 30s, big thrilled toothy smile, proudly thrusting smartphone forward towards camera",
        "headline": "KTRS 세금 환급 입금 확인 완료!",
        "subhead": "5년간 못 받은 환급금, 단 1분 만에 안전하게 계좌 입금."
    },
    "ko": {
        "description": "an excited happy Korean presenter woman in her late 20s, big bright smile showing teeth, delightfully holding phone up towards viewer",
        "headline": "숨은 환급금 310만원, 전액 입금 완료!",
        "subhead": "국세청 종합소득세 경정청구, 간편 조회로 바로 찾으세요."
    }
}


class PromptDirectorCardNewsEasyTax:
    """이지택스 카드뉴스 프롬프트 및 카피 디렉터"""

    @classmethod
    def get_t2i_prompt(cls, nationality_code: str = "vi") -> Dict[str, str]:
        """카드뉴스용 활짝 웃는 극적 환희 마스터컷 프롬프트 반환"""
        nat = CARDNEWS_NATIONALITIES.get(nationality_code, CARDNEWS_NATIONALITIES["vi"])

        pos = (
            f"masterpiece, best quality, ultra-photorealistic portrait of {nat['description']}, "
            f"sitting in a sunlit modern interior room. "
            f"She is proudly thrusting a modern smartphone forward towards the camera with one hand, "
            f"presenting the vertical black phone screen directly to viewer with great excitement. "
            f"Wide energetic open toothy smile, ecstatic thrilled expression, laughing cheerfully, "
            f"sharp focus on pristine face and crisp phone bezel, natural pores, gorgeous realistic lighting, 8k uhd."
        )

        neg = (
            "closed mouth, sad, neutral, frowning, deformed fingers, extra digits, missing fingers, "
            "bad hands, blurry screen, tilted phone, overexposed, cartoon, 3d render, anime, plastic, lowres"
        )

        return {"positive": pos, "negative": neg}

    @classmethod
    def get_copywriting(cls, nationality_code: str = "vi", amount: int = 3100000) -> Dict[str, str]:
        """카드뉴스용 헤드카피 및 서브카피 반환"""
        nat = CARDNEWS_NATIONALITIES.get(nationality_code, CARDNEWS_NATIONALITIES["vi"])
        amt_str = f"{amount // 10000}만 원"
        return {
            "headline": f"세금 환급 {amt_str} 전액 입금 완료!",
            "subhead": nat["subhead"],
            "badge": "국세청(NTS) 공식 환급 인증",
            "cta": "지금 내 환급금 무료 조회하기 >"
        }
