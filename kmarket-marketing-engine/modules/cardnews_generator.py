"""
CardnewsGenerator - [카드뉴스 통합 파사드(Facade) 오케스트레이터]
각 서비스별 전담 카드뉴스 팩토리 모듈로 위임(Delegation) 호출합니다.

1. 💰 EasyTax 카드뉴스 전담:
   - CardnewsEasyTax (modules/cardnews_easytax.py)
2. 🛒 K-Market 카드뉴스 전담:
   - CardnewsKMarket (modules/cardnews_kmarket.py)
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from modules.cardnews_easytax import CardnewsEasyTax
from modules.cardnews_kmarket import CardnewsKMarket

logger = logging.getLogger("CardnewsGenerator")


class CardnewsGenerator:
    """
    📸 카드뉴스 무인 공장 통합 파사드
    - 하위 호환성을 유지하며 실제 로직은 각 전담 팩토리 모듈로 100% 위임
    """
    def __init__(self, db_mgr=None, router=None):
        self.cardnews_easytax = CardnewsEasyTax()
        self.cardnews_kmarket = CardnewsKMarket()

    def generate_carousel_cardnews(
        self,
        service_id: str = "kmarket",
        lang: str = "vi",
        theme_index: Optional[int] = None,
        engine_mode: str = "colab_gpu"
    ) -> List[Path]:
        """서비스 ID에 따라 전담 카드뉴스 공장으로 즉시 분기 위임"""
        service_id = service_id.lower()
        if service_id == "easytax":
            return self.cardnews_easytax.generate_carousel_cardnews(lang=lang, theme_index=theme_index, engine_mode=engine_mode)
        else:
            return self.cardnews_kmarket.generate_carousel_cardnews(lang=lang, theme_index=theme_index, engine_mode=engine_mode)

    # server.py 호환 별칭 (generate_carousel → generate_carousel_cardnews)
    def generate_carousel(
        self,
        service_id: str = "kmarket",
        lang: str = "vi",
        theme_index: Optional[int] = None,
        engine_mode: str = "colab_gpu"
    ) -> List[Path]:
        """generate_carousel_cardnews의 server.py 호환 별칭"""
        return self.generate_carousel_cardnews(
            service_id=service_id,
            lang=lang,
            theme_index=theme_index,
            engine_mode=engine_mode
        )
