"""
ShortsVideoFactory - [숏폼 비디오 통합 파사드(Facade) 오케스트레이터]
각 서비스별 전담 숏폼 팩토리 모듈로 위임(Delegation) 호출합니다.

1. 💰 EasyTax 숏폼 전담:
   - ShortsEasyTax (modules/shorts_easytax.py)
2. 🛒 K-Market 숏폼 전담:
   - ShortsKMarket (modules/shorts_kmarket.py)
"""

import logging
from typing import Dict, Any, Optional, List
from modules.shorts_easytax import ShortsEasyTax
from modules.shorts_kmarket import ShortsKMarket

logger = logging.getLogger("ShortsVideoFactory")


class ShortsVideoFactory:
    """
    🎬 숏폼 비디오 무인 공장 통합 파사드
    - 하위 호환성을 유지하며 실제 로직은 각 전담 팩토리 모듈로 100% 위임
    """
    def __init__(self, *args, **kwargs):
        # 하위 호환성: db_mgr, router, gemini, tts 등 레거시 인자 무시
        self.shorts_easytax = ShortsEasyTax()
        self.shorts_kmarket = ShortsKMarket()

    def produce_shorts(
        self,
        service_id: str = "easytax",
        lang: str = "vi",
        target_langs: Optional[List[str]] = None,
        force_mode: Optional[str] = None,
        engine_mode: str = "colab_gpu"
    ) -> Dict[str, Any]:
        """서비스 ID에 따라 전담 숏폼 공장으로 즉시 분기 위임"""
        service_id = service_id.lower()
        # target_langs가 있으면 첫 번째 언어를 lang으로 사용
        if target_langs and len(target_langs) > 0 and lang == "vi":
            lang = target_langs[0]
        if service_id == "kmarket":
            return self.shorts_kmarket.produce_shorts(lang=lang, force_mode=force_mode, engine_mode=engine_mode)
        else:
            return self.shorts_easytax.produce_shorts(lang=lang, engine_mode=engine_mode)
