# -*- coding: utf-8 -*-
"""
ShortsBrandCapsuleBadge (core/shorts_engine/shorts_brand_capsule_badge.py)
========================================================================
- 3대 브랜드(Aura, Insurance, Stock) 숏폼 영상(1080x1920) 상단 좌측 전용
- 카드뉴스 공식 디자인 시스템 100% 동일 계승 (Playwright 기반 완벽한 다크 글래스모피즘):
  1. 💖 Aura AI 데이팅: [💖 AURA | 50:50 남녀 황금 성비율] (핑크 #F472B6)
  2. 🛡️ 보험 리밸런스: [🛡️ 보험 리밸런스 | 34개사 실시간 비교] (민트 #34D399)
  3. 📈 StockMaster AI: [📈 StockMaster AI | 외인·기관 실시간 수급 포착] (골드 #FBBF24)
- 1080x1920 세로 풀HD 투명 배경 오버레이 레이어
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("ShortsBrandCapsuleBadge")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OVERLAYS_DIR = CURRENT_DIR / "presets" / "capsule_overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)


class ShortsBrandCapsuleBadge:
    """🎬 숏폼 영상 1080x1920 전용 상단 좌측 브랜드 캡슐 뱃지 오버레이 생성기"""

    BADGE_CONFIGS = {
        "aura": {
            "icon": "💖",
            "brand_name": "아우라 AI 데이팅",
            "sub_text": "현재 100% 무료",
            "sub_color_class": "text-pink-400",
            "filename": "aura_capsule_overlay_1080x1920.png"
        },
        "insurance": {
            "icon": "🛡️",
            "brand_name": "보험 리밸런스",
            "sub_text": "34개사 실시간 비교",
            "sub_color_class": "text-emerald-400",
            "filename": "insurance_capsule_overlay_1080x1920.png"
        },
        "stock": {
            "icon": "📈",
            "brand_name": "StockMaster AI",
            "sub_text": "외인·기관 실시간 수급 포착",
            "sub_color_class": "text-amber-400",
            "filename": "stock_capsule_overlay_1080x1920.png"
        }
    }

    @classmethod
    def _build_html_template(cls, config: Dict[str, Any]) -> str:
        """카드뉴스와 100% 동일한 글래스모피즘 상단 캡슐 뱃지 HTML 생성"""
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{
    background: transparent;
    margin: 0;
    padding: 0;
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR', sans-serif;
  }}
</style>
</head>
<body>
  <!-- 상단 좌측 브랜드 글래스모피즘 캡슐 뱃지 바 (카드뉴스 공식 규격과 100% 일치) -->
  <div style="position:absolute; top:70px; left:50px;">
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-3 px-6 shadow-2xl">
      <span class="text-2xl">{config["icon"]}</span>
      <span class="text-lg font-black tracking-wider text-white">{config["brand_name"]}</span>
      <span class="text-base font-bold {config["sub_color_class"]} pl-3 border-l border-white/30">{config["sub_text"]}</span>
    </div>
  </div>
</body>
</html>"""

    @classmethod
    def create_capsule_overlay_png(cls, brand_key: str, out_path: Optional[str] = None) -> str:
        """
        Playwright를 통해 1080x1920 세로 풀HD 투명 PNG 캡슐 뱃지 생성
        """
        config = cls.BADGE_CONFIGS.get(brand_key.lower())
        if not config:
            raise ValueError(f"지원하지 않는 브랜드 키입니다: {brand_key}")

        if not out_path:
            out_path = str(OVERLAYS_DIR / config["filename"])

        html_content = cls._build_html_template(config)

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1080, "height": 1920})
                page.set_content(html_content)
                page.wait_for_timeout(400)
                page.screenshot(path=out_path, omit_background=True)
                browser.close()
            logger.info(f"✅ [캡슐 뱃지 생성 성공] {brand_key.upper()} -> {out_path}")
        except Exception as e:
            logger.warning(f"Playwright 렌더링 실패({e}), PIL 백업 렌더러 시도...")
            cls._render_fallback_pil(config, out_path)

        return out_path

    @classmethod
    def _render_fallback_pil(cls, config: Dict[str, Any], out_path: str):
        """Playwright 사용 불가 시 PIL 고화질 백업 렌더링"""
        from PIL import Image, ImageDraw, ImageFont
        canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 캡슐 박스 (x: 50, y: 70, w: 460, h: 64)
        draw.rounded_rectangle([(50, 70), (510, 134)], radius=32, fill=(15, 23, 42, 230), outline=(255, 255, 255, 64), width=2)
        font = ImageFont.load_default()
        draw.text((80, 92), f"{config['brand_name']} | {config['sub_text']}", fill=(255, 255, 255), font=font)
        canvas.save(out_path, "PNG")

    @classmethod
    def get_overlay_path(cls, brand_key: str, force_refresh: bool = False) -> str:
        """브랜드별 1080x1920 상단 캡슐 뱃지 오버레이 경로 반환 (없으면 자동 렌더링)"""
        config = cls.BADGE_CONFIGS.get(brand_key.lower())
        if not config:
            return ""

        out_path = OVERLAYS_DIR / config["filename"]
        if force_refresh or not out_path.exists():
            cls.create_capsule_overlay_png(brand_key, str(out_path))

        return str(out_path)
