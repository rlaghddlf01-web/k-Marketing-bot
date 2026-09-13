# -*- coding: utf-8 -*-
"""
K-Market Brand Package
- UI Templates: 케이마켓 모바일 앱 및 해외 송금/나눔 UI
- Scenarios: 숏폼(입 다문 컷) vs 카드뉴스(활짝 웃는 컷) 프롬프트 디렉터
- Pipelines: 케이마켓 숏폼 및 카드뉴스 자율 생성기
"""

from .kmarket_shorts_pipeline import KMarketShortsPipeline
from .kmarket_cardnews_pipeline import KMarketCardNewsPipeline

__all__ = ["KMarketShortsPipeline", "KMarketCardNewsPipeline"]
