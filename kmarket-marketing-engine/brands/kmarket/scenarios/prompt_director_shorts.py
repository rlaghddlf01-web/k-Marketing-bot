# -*- coding: utf-8 -*-
"""
PromptDirectorShorts (K-Market) - 🎬 [케이마켓 숏폼 전용 시나리오 & 프롬프트 디렉터]
- 핵심 원칙: '입을 부드럽게 다문 온화한 미소(Soft closed-mouth smile)' 마스터컷 생성
- 케이마켓(외국인 생활 커뮤니티, 중고 무료 나눔, 해외 송금) 5초 숏폼 대본 제공
"""

from typing import Dict, Any


KMARKET_SHORT_PROMPTS = {
    "vi": {
        "nationality": "Vietnamese",
        "description": "a smart attractive Vietnamese young woman, natural neat hairstyle, stylish emerald green knit sweater, warm friendly eyes",
        "script": "한국 생활 필수 앱 케이마켓! 무료 나눔부터 송금까지 지금 바로 시작하세요!"
    },
    "uz": {
        "nationality": "Uzbek",
        "description": "a trustworthy energetic Uzbek young man, clean modern casual jacket, confident pleasant smile, looking directly at camera",
        "script": "외국인을 위한 최고의 플랫폼 케이마켓! 수수료 없는 송금과 나눔을 경험해보세요!"
    },
    "ko": {
        "nationality": "Korean",
        "description": "a warm welcoming Korean presenter, stylish daily wear, approachable smile, neat modern room background",
        "script": "한국 거주 외국인들을 위한 케이마켓! 무료 나눔과 안전한 송금을 만나보세요!"
    }
}


class PromptDirectorShortsKMarket:
    """케이마켓 숏폼 프롬프트 및 대본 디렉터"""

    @classmethod
    def get_t2i_prompt(cls, nationality_code: str = "vi") -> Dict[str, str]:
        """숏폼용 입 다문 마스터컷 프롬프트 반환"""
        nat = KMARKET_SHORT_PROMPTS.get(nationality_code, KMARKET_SHORT_PROMPTS["vi"])

        pos = (
            f"masterpiece, best quality, ultra-photorealistic portrait of {nat['description']}, "
            f"sitting comfortably in a brightly lit modern stylish living room. "
            f"Holding a smartphone vertically in one hand facing forward towards the camera. "
            f"Her expression is a gentle, relaxed, warm, closed-mouth smile with lips naturally resting together and NO teeth showing, "
            f"looking directly at the camera with sincere friendly eye contact, ready to speak. "
            f"Sharp focus on her expressive face, natural skin pores, realistic hair texture, 8k uhd, cinematic film lighting."
        )

        neg = (
            "open mouth, showing teeth, smiling wide with mouth open, parted lips, talking mouth, "
            "deformed fingers, extra digits, missing fingers, bad hands, blurry screen, tilted phone, "
            "overexposed, cartoon, 3d render, anime, plastic skin, dull, dark, lowres, text, watermark"
        )

        return {"positive": pos, "negative": neg}

    @classmethod
    def get_speech_script(cls, nationality_code: str = "vi") -> str:
        """5초 숏폼 전용 음성 멘트 반환"""
        nat = KMARKET_SHORT_PROMPTS.get(nationality_code, KMARKET_SHORT_PROMPTS["vi"])
        return nat["script"]
