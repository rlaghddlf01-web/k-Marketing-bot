# -*- coding: utf-8 -*-
"""
PromptDirectorShorts (EasyTax) - 🎬 [이지택스 숏폼 전용 시나리오 & 프롬프트 디렉터]
- 핵심 원칙: '입을 부드럽게 다문 온화한 미소(Soft closed-mouth smile)' 마스터컷 생성
- 립싱크 가동 범위(Dynamic Range) 극대화 및 치아 왜곡 원천 차단
- 5.06초(81프레임 @ 16fps) 최적화 다국어 세금 환급 안내 대본 제공
"""

from typing import Dict, Any


NATIONALITY_PROMPTS = {
    "vi": {
        "nationality": "Vietnamese",
        "description": "a beautiful friendly Vietnamese woman in her late 20s, warm golden beige skin tone, subtle natural makeup, wearing a clean cozy knit sweater",
        "script": "꼭 세금 환급 신청하세요! 저도 310만 원이나 들어왔어요!"
    },
    "uz": {
        "nationality": "Uzbek",
        "description": "a handsome polite Uzbek man in his early 30s, smart casual business shirt, warm gentle eyes, confident trustworthy look",
        "script": "한국에서 일하는 외국인 여러분, 세금 환급 꼭 받으세요! 저도 환급금 입금 완료됐어요!"
    },
    "ru": {
        "nationality": "Russian",
        "description": "a cheerful professional Slavic woman in her late 20s, neat hairstyle, wearing elegant professional office blouse",
        "script": "꼭 세금 환급 신청하세요! 저도 이번에 310만 원이나 환급받았어요!"
    },
    "ko": {
        "nationality": "Korean",
        "description": "a bright approachable Korean woman in her late 20s, natural daily look, soft pastel knit, friendly warm expression",
        "script": "꼭 세금 환급 신청하세요! 저도 310만 원이나 들어왔어요!"
    }
}


class PromptDirectorShortsEasyTax:
    """이지택스 숏폼 프롬프트 및 대본 디렉터"""

    @classmethod
    def get_t2i_prompt(cls, nationality_code: str = "vi") -> Dict[str, str]:
        """숏폼용 입 다문 마스터컷 프롬프트 반환"""
        nat = NATIONALITY_PROMPTS.get(nationality_code, NATIONALITY_PROMPTS["vi"])

        pos = (
            f"masterpiece, best quality, ultra-photorealistic portrait of {nat['description']}, "
            f"sitting comfortably in a modern bright warm cozy room with soft indoor lighting. "
            f"She is holding a modern smartphone vertically in her hand facing directly forward towards camera. "
            f"Her expression is a gentle, relaxed, warm, closed-mouth smile with lips naturally resting together and NO teeth showing, "
            f"looking directly at the camera with genuine friendly eye contact, ready to speak. "
            f"Sharp focus on her clear face, delicate natural skin texture, realistic hair strands, 8k uhd, cinematic film still."
        )

        neg = (
            "open mouth, showing teeth, smiling wide with mouth open, parted lips, talking mouth, "
            "deformed fingers, extra digits, missing fingers, bad hands, blurry screen, tilted phone, "
            "overexposed, cartoon, 3d render, anime, plastic skin, dull, dark, lowres, text, watermark"
        )

        return {"positive": pos, "negative": neg}

    @classmethod
    def get_speech_script(cls, nationality_code: str = "vi", amount: int = 3100000) -> str:
        """5초 숏폼 전용 음성 멘트 반환"""
        amt_str = f"{amount // 10000}만 원"
        return f"꼭 세금 환급 신청하세요! 저도 {amt_str}이나 들어왔어요!"
