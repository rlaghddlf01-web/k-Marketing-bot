"""
KMarketIFrameEngine - [케이마켓 실제 웹사이트 9:16 모바일 iFrame 캡처 & 렌더링 엔진]
- 실제 케이마켓 웹사이트(https://ktrs-market.vercel.app/)의 모바일 웹뷰를 9:16 (1080x1920)로 로딩
- 17개국 언어 파라미터(?lang=vi, ?lang=mn 등) 지원
- 9:16 풀스크린 카드뉴스 이미지 및 스무스 스크롤 모션 비디오 자동 합성
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, BASE_DIR

logger = logging.getLogger("KMarketIFrame")


class KMarketIFrameEngine:
    """
    📱 케이마켓 9:16 모바일 웹뷰 iFrame 전담 렌더러
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "cardnews")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://ktrs-market.vercel.app"

    def get_mobile_iframe_url(self, lang: str = "vi", category: str = "all") -> str:
        """17개국 언어 및 카테고리가 적용된 케이마켓 실제 모바일 웹 URL 생성"""
        return f"{self.base_url}/?lang={lang}&cat={category}&view=mobile"

    def render_iframe_cardnews_set(self, lang: str = "vi") -> List[Path]:
        """
        9:16 세로형 모바일 웹뷰 기반 케이마켓 4장 카드뉴스 렌더링
        """
        from core.kmarket_webview_composer import KMarketWebviewComposer
        composer = KMarketWebviewComposer(self.output_dir)
        
        cards = []
        for idx in range(1, 5):
            card_path = composer.render_slide(slide_idx=idx, lang=lang)
            cards.append(card_path)
            
        logger.info(f"[{lang.upper()}] 📱 iFrame 웹뷰 기반 9:16 카드뉴스 4장 세트 완성")
        return cards
