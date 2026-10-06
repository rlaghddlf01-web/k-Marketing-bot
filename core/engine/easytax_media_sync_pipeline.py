# -*- coding: utf-8 -*-
"""
EasyTaxMediaSyncPipeline - 💰 [이지텍스 세무 전용 미디어 동기화 & 바탕화면 배포 파이프라인]
- EasyTax 세무 환급 브랜드 산출물(세무 카드뉴스, 환급 숏폼, 립싱크 S2V) 전용 처리
- 원격 GPU에서 수신한 미디어를 로컬 outputs 및 바탕화면 [카드뉴스_산출물/이지텍스], [숏폼_산출물/이지텍스]에 100% 자동 배치
- K-Market 코드와 완전 분리 격리된 독립 모듈
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("EasyTaxMediaSyncPipeline")


class EasyTaxMediaSyncPipeline:
    """이지텍스 세무 전용 미디어 동기화 & 로컬 바탕화면 배포 엔진"""

    BRAND = "easytax"
    BRAND_KR = "이지텍스"

    def __init__(self):
        from config import (
            OUTPUTS_DIR,
            DESKTOP_CARDNEWS_EASYTAX,
            DESKTOP_SHORTS_EASYTAX,
            DESKTOP_THREADS_EASYTAX
        )
        self.outputs_dir = Path(OUTPUTS_DIR)
        self.desktop_cardnews = Path(DESKTOP_CARDNEWS_EASYTAX)
        self.desktop_shorts = Path(DESKTOP_SHORTS_EASYTAX)
        self.desktop_threads = Path(DESKTOP_THREADS_EASYTAX)

        # 디렉토리 보장
        self.desktop_cardnews.mkdir(parents=True, exist_ok=True)
        self.desktop_shorts.mkdir(parents=True, exist_ok=True)
        self.desktop_threads.mkdir(parents=True, exist_ok=True)

    def dispatch_media(
        self,
        source_path: str,
        category: str,
        custom_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        이지텍스 세무 산출물을 outputs 및 바탕화면 이지텍스 전용 폴더에 동시 배포
        :param source_path: 생성된 로컬 파일 경로
        :param category: 'cardnews', 'shorts', 'threads' 등
        :param custom_name: 저장할 커스텀 파일명 (선택)
        :return: {'output_path': str, 'desktop_path': str, 'web_url': str}
        """
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"[EasyTax] 소스 파일을 찾을 수 없습니다: {source_path}")

        filename = custom_name or src.name

        # 1. 로컬 웹 대시보드 outputs 서빙 폴더 복사
        web_cat_dir = self.outputs_dir / category
        web_cat_dir.mkdir(parents=True, exist_ok=True)
        web_dest = web_cat_dir / filename
        if src.resolve() != web_dest.resolve():
            shutil.copy2(src, web_dest)

        # 2. 사용자 PC 바탕화면 이지텍스 전용 폴더 복사
        if category == "cardnews":
            desktop_target_dir = self.desktop_cardnews
        elif category == "shorts":
            desktop_target_dir = self.desktop_shorts
        elif category == "threads":
            desktop_target_dir = self.desktop_threads
        else:
            desktop_target_dir = self.desktop_cardnews.parent / f"{category}_산출물" / self.BRAND_KR

        desktop_target_dir.mkdir(parents=True, exist_ok=True)
        desktop_dest = desktop_target_dir / filename
        shutil.copy2(src, desktop_dest)

        logger.info(f"💰 [EasyTax] 바탕화면 실물 배치 완료: {desktop_dest} (웹 대시보드: /outputs/{category}/{filename})")

        return {
            "output_path": str(web_dest),
            "desktop_path": str(desktop_dest),
            "web_url": f"/outputs/{category}/{filename}"
        }
