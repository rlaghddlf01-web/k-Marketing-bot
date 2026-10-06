# -*- coding: utf-8 -*-
"""
EasyTax Brand Package
- UI Templates: 국세청 세금 환급 영수증 및 입금 완료 UI
- Scenarios: 숏폼(입 다문 컷) vs 카드뉴스(활짝 웃는 컷) 프롬프트 디렉터
- Pipelines: 이지택스 숏폼 및 카드뉴스 자율 생성기
"""

from .easytax_shorts_pipeline import EasyTaxShortsPipeline
from .easytax_cardnews_pipeline import EasyTaxCardNewsPipeline

__all__ = ["EasyTaxShortsPipeline", "EasyTaxCardNewsPipeline"]
