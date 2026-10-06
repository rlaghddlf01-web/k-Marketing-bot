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
from core.shorts_engine import EasyTaxShortsProducer, KMarketShortsProducer

logger = logging.getLogger("ShortsVideoFactory")


class ShortsVideoFactory:
    """
    🎬 숏폼 비디오 무인 공장 통합 파사드 (신형 로컬 GPU Wan 2.2 S2V 엔진 연동)
    """
    def __init__(self, *args, **kwargs):
        self.shorts_easytax = EasyTaxShortsProducer()
        self.shorts_kmarket = KMarketShortsProducer()

    def produce_shorts(
        self,
        service_id: str = "easytax",
        lang: str = "vi",
        target_langs: Optional[List[str]] = None,
        force_mode: Optional[str] = None,
        engine_mode: str = "gpu"
    ) -> Dict[str, Any]:
        """서비스 ID에 따라 전담 신형 GPU 숏폼 공장으로 즉시 분기 위임"""
        service_id = service_id.lower()
        if target_langs and len(target_langs) > 0 and lang == "vi":
            lang = target_langs[0]
        if service_id == "kmarket":
            return self.shorts_kmarket.produce(lang=lang)
        else:
            return self.shorts_easytax.produce(lang=lang)
