# -*- coding: utf-8 -*-
"""
MediaSyncFacade - 🔀 [마켓/세무 독립 파이프라인 통합 디스패처 파사드]
- K-Market과 EasyTax 파이프라인의 책임을 명확히 격리하고 라우팅
- 브랜드별 전용 싱크 파이프라인 인스턴스 제공 및 산출물 안전 배포
"""

from typing import Dict, Any, Optional
from core.engine.kmarket_media_sync_pipeline import KMarketMediaSyncPipeline
from core.engine.easytax_media_sync_pipeline import EasyTaxMediaSyncPipeline


class MediaSyncFacade:
    """마켓 / 세무 브랜드별 독립 동기화 파이프라인 파사드"""

    _kmarket_pipeline = None
    _easytax_pipeline = None

    @classmethod
    def get_pipeline(cls, brand: str = "kmarket"):
        """브랜드에 따른 독립 전용 파이프라인 반환"""
        brand_clean = brand.lower().strip()
        if "easytax" in brand_clean or "tax" in brand_clean:
            if cls._easytax_pipeline is None:
                cls._easytax_pipeline = EasyTaxMediaSyncPipeline()
            return cls._easytax_pipeline
        else:
            if cls._kmarket_pipeline is None:
                cls._kmarket_pipeline = KMarketMediaSyncPipeline()
            return cls._kmarket_pipeline

    @classmethod
    def dispatch(
        cls,
        source_path: str,
        category: str,
        brand: str = "kmarket",
        custom_name: Optional[str] = None
    ) -> Dict[str, str]:
        """브랜드에 맞는 전용 파이프라인으로 안전하게 산출물 배포"""
        pipeline = cls.get_pipeline(brand)
        return pipeline.dispatch_media(source_path=source_path, category=category, custom_name=custom_name)
