# -*- coding: utf-8 -*-
"""
FontManager - 🔤 [8대 황금 타깃 국가 및 17개국어 전용 유니코드 폰트 매니저]
- 네팔(데바나가리), 캄보디아(크메르), 태국어, 미얀마(버마), 몽골/우즈벡(키릴), 베트남(성조) 등
- 윈도우 정품 시스템 내장 유니코드 폰트를 언어별로 100% 매칭하여 Tofu(□) 글자 깨짐 완전 방지
- TrueType 및 TrueType Collection(.ttc) 인덱스 안전 로딩 지원
"""

import os
import logging
from typing import List, Optional
from PIL import ImageFont

logger = logging.getLogger("FontManager")


class FontManager:
    """17개국 언어별 최적 유니코드 폰트 자동 매칭 및 캐싱 관리자"""

    _font_cache = {}

    # 언어별 최우선 폰트 후보 경로 (Windows Fonts 기반)
    FONT_CANDIDATES = {
        # 1. 한국어
        "ko": [
            (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        # 2. 베트남어, 인도네시아어, 영어, 스페인어, 타갈로그어 (라틴 및 다이아크리틱 악센트)
        "vi": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
            (r"C:\Windows\Fonts\tahomabd.ttf", r"C:\Windows\Fonts\tahoma.ttf", 0),
        ],
        "id": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        "en": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        "tl": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        # 3. 우즈베키스탄, 몽골, 러시아, 카자흐스탄 (키릴 및 라틴 확장)
        "uz": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        "mn": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        "ru": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        "kk": [
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
            (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", 0),
        ],
        # 4. 캄보디아(크메르어), 태국어
        "km": [
            (r"C:\Windows\Fonts\LeelaUIb.ttf", r"C:\Windows\Fonts\LeelawUI.ttf", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        "th": [
            (r"C:\Windows\Fonts\LeelaUIb.ttf", r"C:\Windows\Fonts\LeelawUI.ttf", 0),
            (r"C:\Windows\Fonts\tahomabd.ttf", r"C:\Windows\Fonts\tahoma.ttf", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        # 5. 네팔어, 힌디어, 벵골어, 싱할라어 (데바나가리 및 인도/남아시아 계열 문자)
        "ne": [
            (r"C:\Windows\Fonts\Nirmala.ttc", r"C:\Windows\Fonts\Nirmala.ttc", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        "hi": [
            (r"C:\Windows\Fonts\Nirmala.ttc", r"C:\Windows\Fonts\Nirmala.ttc", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        "bn": [
            (r"C:\Windows\Fonts\Nirmala.ttc", r"C:\Windows\Fonts\Nirmala.ttc", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        "si": [
            (r"C:\Windows\Fonts\Nirmala.ttc", r"C:\Windows\Fonts\Nirmala.ttc", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        # 6. 미얀마어 (버마어)
        "my": [
            (r"C:\Windows\Fonts\mmrtextb.ttf", r"C:\Windows\Fonts\mmrtext.ttf", 0),
            (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf", 0),
        ],
        # 7. 중국어
        "zh": [
            (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyh.ttc", 0),
            (r"C:\Windows\Fonts\simsun.ttc", r"C:\Windows\Fonts\simsun.ttc", 0),
            (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf", 0),
        ],
        # 8. 일본어
        "ja": [
            (r"C:\Windows\Fonts\YuGothB.ttc", r"C:\Windows\Fonts\YuGothM.ttc", 0),
            (r"C:\Windows\Fonts\msgothic.ttc", r"C:\Windows\Fonts\msgothic.ttc", 0),
            (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf", 0),
        ]
    }

    @classmethod
    def load_font(cls, size: int, bold: bool = True, lang: str = "ko") -> ImageFont.FreeTypeFont:
        """
        언어 코드(lang), 크기(size), 볼드 여부(bold)에 따라 최적의 유니코드 폰트를 반환.
        캐싱을 통해 불필요한 I/O 방지.
        """
        norm_lang = (lang or "ko").lower().strip()
        cache_key = (norm_lang, size, bold)
        if cache_key in cls._font_cache:
            return cls._font_cache[cache_key]

        candidates = cls.FONT_CANDIDATES.get(norm_lang, cls.FONT_CANDIDATES["ko"])

        for bold_path, regular_path, font_index in candidates:
            target_path = bold_path if bold else regular_path
            if os.path.exists(target_path):
                try:
                    font = ImageFont.truetype(target_path, size, index=font_index)
                    cls._font_cache[cache_key] = font
                    return font
                except Exception as e:
                    logger.debug(f"폰트 로드 실패 ({target_path}): {e}")
                    continue

        # 범용 폴백: Segoe UI -> 맑은 고딕 -> 기본 폰트
        fallbacks = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
        for fb in fallbacks:
            if os.path.exists(fb):
                try:
                    font = ImageFont.truetype(fb, size)
                    cls._font_cache[cache_key] = font
                    return font
                except Exception:
                    continue

        return ImageFont.load_default()
