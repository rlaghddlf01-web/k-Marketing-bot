# -*- coding: utf-8 -*-
"""
[신규 모듈] ShortsDynamicArtRenderer (core/shorts_engine/shorts_dynamic_art_renderer.py)
• 역할: 제미나이(Gemini)가 100% 자율 디렉팅한 숏폼 씬별 JSON 설계도를 읽고,
        다운로드 폴더 레퍼런스 영상과 100% 일치하는 고품질 비주얼 오버레이(1080x1920 투명 PNG)를 렌더링
• 지원 레이아웃 타입:
  1. center_white_card: 화면 중앙 화이트 글래스 카드 (네온 스카이블루/골드 테두리, 국기/하트, 캡슐 뱃지)
  2. top_left_stacked: 좌상단 3단 멀티컬러 볼드 스택 텍스트 (HOÀN 90% THUẾ / 0 WON FREE SHARING)
  3. phone_side_popup: 스마트폰 옆/좌측 미니 다크 글래스 팝업 (BƯỚC 1, 상승그래프, 체크마크)
  4. bottom_vibrant_card: 하단 로열블루/네온퍼플 와이드 카드 + 초대형 숫자 + 금화 코인(🪙) + 컨페티(🎊✨)
  5. trust_badge_card: 앰버/에메랄드 안심 신뢰 보증 카드 (선입금 0원 / 17개국어 번역)
  6. ending_cta_card: 크림슨 레드 + 골드 글로우 테두리 + 프로필 링크 유도
• 원칙: 모듈 분리 원칙(Rule 1), 땜질 코딩 금지(Rule 5) 준수
"""

import os
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ShortsDynamicArtRenderer")


class ShortsDynamicArtRenderer:
    """제미나이 자율 지능 기반 숏폼 다이내믹 아트 렌더러"""

    def __init__(self):
        self.font_cache = {}

    def _load_font(self, size: int, bold: bool = True, lang: str = "vi") -> ImageFont.FreeTypeFont:
        """언어별 최적 유니코드 볼드 폰트 로드 (17개국 문자 깨짐 100% 방지)"""
        cache_key = (size, bold, lang)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # 17개 언어별 최적 전용 폰트 우선순위 분기
        if lang in ["ko", "kor"]:
            candidates = [
                r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            ]
        elif lang in ["th", "km"]: # 태국어 / 크메르어 (캄보디아)
            candidates = [
                r"C:\Windows\Fonts\LeelaUIb.ttf" if bold else r"C:\Windows\Fonts\LeelawUI.ttf",
                r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            ]
        elif lang in ["my", "burmese"]: # 미얀마어 (버마)
            candidates = [
                r"C:\Windows\Fonts\mmrtextb.ttf" if bold else r"C:\Windows\Fonts\mmrtext.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            ]
        elif lang in ["ne", "hi"]: # 네팔어 / 힌디어
            candidates = [
                r"C:\Windows\Fonts\Nirmala.ttc",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            ]
        elif lang in ["mn"]: # 몽골어
            candidates = [
                r"C:\Windows\Fonts\monbaiti.ttf",
                r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            ]
        elif lang in ["zh", "cn"]: # 중국어
            candidates = [
                r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
                r"C:\Windows\Fonts\simsun.ttc",
            ]
        else: # 베트남어, 우즈벡어, 인니어, 필리핀어, 영어, 러시아어, 카자흐어 등 (라틴/키릴 확장)
            candidates = [
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
                r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
                r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            ]

        font = None
        for p in candidates:
            if os.path.exists(p):
                try:
                    font = ImageFont.truetype(p, size)
                    break
                except Exception:
                    continue

        if not font:
            font = ImageFont.load_default()

        self.font_cache[cache_key] = font
        return font

    def _load_emoji_font(self, size: int) -> ImageFont.FreeTypeFont:
        """윈도우 Segoe UI Emoji 폰트 로드"""
        p = r"C:\Windows\Fonts\seguiemj.ttf"
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
        return self._load_font(size, bold=True)

    def _clean_text(self, text: str) -> str:
        """폰트 깨짐(네모 상자)을 유발하는 모든 비표준 특수 이모지/서로게이트/특수기호 완벽 제거 및 정제"""
        if not text:
            return ""
        import re
        # 유니코드 이모지, 딩뱃, 미스크 심볼, 서로게이트 페어 완벽 정제
        emoji_pattern = re.compile(
            r"[\U00010000-\U0010ffff\uD800-\uDBFF\uDC00-\uDFFF\u2600-\u27BF\uE000-\uF8FF\uFE00-\uFE0F\u200D\u200B-\u200D\uFEFF]",
            flags=re.UNICODE
        )
        cleaned = emoji_pattern.sub("", str(text))
        return cleaned.strip()

    def _draw_fitted_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        box: Tuple[int, int, int, int],
        max_font_size: int = 44,
        min_font_size: int = 18,
        font_color: Tuple[int, int, int] = (255, 255, 255),
        pad_x: int = 20,
        pad_y: int = 8,
        lang: str = "vi",
        bold: bool = True,
        center_h: bool = True,
        center_v: bool = True
    ) -> Tuple[int, int, int, int]:
        """박스 크기에 맞춰 폰트 크기를 자동 축소하여 텍스트를 정밀 렌더링"""
        text = self._clean_text(text)
        bx, by, bw, bh = box
        max_w = max(10, bw - (pad_x * 2))
        max_h = max(10, bh - (pad_y * 2))

        size = max_font_size
        font = self._load_font(size, bold=bold, lang=lang)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        while (tw > max_w or th > max_h) and size > min_font_size:
            size -= 1
            font = self._load_font(size, bold=bold, lang=lang)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

        if center_h:
            tx = max(bx + pad_x, bx + (bw - tw) // 2)
        else:
            tx = bx + pad_x

        if center_v:
            ty = by + (bh - th) // 2 - bbox[1]
        else:
            ty = by + pad_y - bbox[1]

        draw.text((tx, ty), text, fill=font_color, font=font)
        return tx, ty, tw, th

    def _draw_pill_badge(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        center_x: int,
        top_y: int,
        bg_rgb: Tuple[int, int, int] = (52, 211, 153),
        text_rgb: Tuple[int, int, int] = (15, 23, 42),
        font_size: int = 24,
        lang: str = "vi"
    ) -> Tuple[int, int, int, int]:
        """레퍼런스 스타일 타원형 알약 캡슐 뱃지 렌더링"""
        text = self._clean_text(text)
        font = self._load_font(font_size, bold=True, lang=lang)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pad_x, pad_y = 20, 8
        bw = tw + (pad_x * 2)
        bh = th + (pad_y * 2)
        bx = center_x - (bw // 2)
        by = top_y

        # 알약 배경 (완전 둥근 모서리)
        draw.rounded_rectangle(
            [(bx, by), (bx + bw, by + bh)],
            radius=bh // 2,
            fill=(*bg_rgb, 255)
        )
        # 텍스트
        tx = bx + pad_x
        ty = by + pad_y - bbox[1]
        draw.text((tx, ty), text, fill=text_rgb, font=font)
        return bx, by, bw, bh

    def _draw_confetti(self, draw: ImageDraw.ImageDraw, count: int = 40):
        """화면 전반에 흩날리는 생동감 넘치는 축하 색종이(컨페티) & 스파클 효과"""
        colors = [
            (250, 204, 21, 230),  # Gold
            (56, 189, 248, 230),  # Sky Blue
            (52, 211, 153, 230),  # Mint
            (244, 114, 182, 230), # Pink
            (255, 255, 255, 240), # White
        ]
        rng = random.Random(42) # 일관된 시각 효과를 위해 고정 시드 사용

        for _ in range(count):
            x = rng.randint(40, 1040)
            y = rng.randint(200, 1800)
            size = rng.randint(8, 18)
            col = rng.choice(colors)
            shape = rng.choice(["rect", "circle", "sparkle"])

            if shape == "rect":
                draw.rectangle([(x, y), (x + size, y + size // 2)], fill=col)
            elif shape == "circle":
                draw.ellipse([(x, y), (x + size, y + size)], fill=col)
            elif shape == "sparkle":
                draw.line([(x - size, y), (x + size, y)], fill=col, width=2)
                draw.line([(x, y - size), (x, y + size)], fill=col, width=2)

    def _draw_dot_pattern(self, draw: ImageDraw.ImageDraw, top_left: Tuple[int, int], rows: int = 5, cols: int = 5):
        """레퍼런스 영상 상단에 들어간 모던 미니 도트 그리드 그래픽"""
        ox, oy = top_left
        dot_color = (52, 211, 153, 160)
        gap = 16
        for r in range(rows):
            for c in range(cols):
                cx = ox + (c * gap)
                cy = oy + (r * gap)
                draw.ellipse([(cx, cy), (cx + 4, cy + 4)], fill=dot_color)

    def _draw_decorations(
        self,
        draw: ImageDraw.ImageDraw,
        emojis: List[str],
        center_x: int,
        y: int,
        font_size: int = 36
    ):
        """국기, 하트, 코인 등 이모지/스티커를 가로로 배치"""
        if not emojis:
            return
        emoji_font = self._load_emoji_font(font_size)
        full_text = "  ".join(emojis)
        bbox = draw.textbbox((0, 0), full_text, font=emoji_font)
        tw = bbox[2] - bbox[0]
        tx = center_x - (tw // 2)
        ty = y - bbox[1]
        draw.text((tx, ty), full_text, fill=(255, 255, 255, 255), font=emoji_font)

    def render_dynamic_scene_overlay(
        self,
        scene: Dict[str, Any],
        out_path: str,
        lang: str = "vi",
        top_header_text: Optional[str] = None
    ) -> str:
        """
        🎬 [제미나이 100% 자율 디렉팅] 씬별 레이아웃 타입에 맞추어 1080x1920 풀HD 투명 오버레이 PNG 렌더링
        """
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        layout_type = scene.get("layout_type", "bottom_vibrant_card")
        badge = scene.get("badge", {})
        badge_text = badge.get("text", "")
        badge_bg = tuple(badge.get("bg_color", [52, 211, 153]))
        badge_fg = tuple(badge.get("text_color", [15, 23, 42]))

        headline_lines = scene.get("headline_lines", [])
        sub_text = scene.get("sub_text", "")
        decorations = scene.get("decorations", {})
        emojis = decorations.get("emojis", [])
        show_confetti = decorations.get("confetti", False)
        show_dots = decorations.get("show_dots_pattern", False)

        # 0. 컨페티 파티클
        if show_confetti:
            self._draw_confetti(draw, count=45)

        # 0-1. 상단 미니 도트 패턴
        if show_dots:
            self._draw_dot_pattern(draw, (80, 100), rows=6, cols=6)
            # 우상단 네온 원형 링
            draw.ellipse([(920, 80), (1000, 160)], outline=(52, 211, 153, 200), width=3)

        # 1. 상단 글로벌 고정 헤더 (옵션)
        if top_header_text and layout_type != "top_left_stacked":
            t_box = (60, 60, 960, 75)
            draw.rounded_rectangle(
                [(t_box[0], t_box[1]), (t_box[0] + t_box[2], t_box[1] + t_box[3])],
                radius=18,
                fill=(15, 23, 42, 230),
                outline=(245, 158, 11, 255),
                width=2
            )
            self._draw_fitted_text(
                draw=draw,
                text=top_header_text,
                box=t_box,
                max_font_size=32,
                min_font_size=16,
                font_color=(255, 255, 255),
                lang=lang,
                bold=True,
                center_h=True,
                center_v=True
            )

        # ==========================================
        # 2. 레이아웃별 전용 렌더링
        # ==========================================

        if layout_type == "center_white_card":
            # 🎨 1) [레퍼런스 0~3.5s] 중앙 화이트 글래스 카드
            cw, ch = 720, 310
            cx = (1080 - cw) // 2
            cy = 1080  # 인물 가슴 부위

            # 화이트 카드 배경 + 하늘색 네온 테두리
            draw.rounded_rectangle(
                [(cx, cy), (cx + cw, cy + ch)],
                radius=28,
                fill=(255, 255, 255, 250),
                outline=(56, 189, 248, 255),
                width=4
            )

            # 상단 캡슐 뱃지 (예: XIN CHÀO!)
            if badge_text:
                self._draw_pill_badge(
                    draw=draw,
                    text=badge_text,
                    center_x=540,
                    top_y=cy - 22,
                    bg_rgb=badge_bg,
                    text_rgb=badge_fg,
                    font_size=24,
                    lang=lang
                )

            # 멀티 라인 텍스트 렌더링
            curr_y = cy + 28
            for line_item in headline_lines:
                txt = line_item.get("text", "")
                col = tuple(line_item.get("color", [15, 23, 42]))
                line_box = (cx + 20, curr_y, cw - 40, 60)
                self._draw_fitted_text(
                    draw=draw,
                    text=txt,
                    box=line_box,
                    max_font_size=46,
                    min_font_size=24,
                    font_color=col,
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )
                curr_y += 62

            # 국기/이모지 장식 (예: 🇻🇳 🇰🇷)
            if emojis:
                self._draw_decorations(draw, emojis, center_x=540, y=curr_y + 10, font_size=38)

            # 카드 아래 하늘색 하트 (옵션)
            if decorations.get("bottom_heart", True):
                self._draw_decorations(draw, ["💙"], center_x=540, y=cy + ch + 18, font_size=40)

        elif layout_type == "top_left_stacked":
            # 🎨 2) [레퍼런스 3.5~7.0s] 좌상단 멀티컬러 스택 텍스트
            start_x = 80
            start_y = 120

            # 상단 캡슐 뱃지 (예: ƯU ĐÃI ĐẶC BIỆT)
            if badge_text:
                bx, by, bw, bh = self._draw_pill_badge(
                    draw=draw,
                    text=badge_text,
                    center_x=start_x + 140,
                    top_y=start_y,
                    bg_rgb=badge_bg,
                    text_rgb=badge_fg,
                    font_size=24,
                    lang=lang
                )
                start_y += bh + 25

            # 3단 스택 볼드 텍스트 (예: HOÀN / 90% / THUẾ)
            for line_item in headline_lines:
                txt = line_item.get("text", "")
                col = tuple(line_item.get("color", [34, 197, 94]))
                line_box = (start_x, start_y, 480, 75)
                self._draw_fitted_text(
                    draw=draw,
                    text=txt,
                    box=line_box,
                    max_font_size=64,
                    min_font_size=32,
                    font_color=col,
                    lang=lang,
                    bold=True,
                    center_h=False,
                    center_v=True
                )
                start_y += 78

            if sub_text:
                line_box = (start_x, start_y, 500, 50)
                self._draw_fitted_text(
                    draw=draw,
                    text=sub_text,
                    box=line_box,
                    max_font_size=28,
                    min_font_size=18,
                    font_color=(255, 255, 255),
                    lang=lang,
                    bold=False,
                    center_h=False,
                    center_v=True
                )

        elif layout_type == "phone_side_popup":
            # 🎨 3) [레퍼런스 7.0~10.5s] 스마트폰 옆/좌측 미니 팝업 카드
            pw, ph = 380, 480
            px, py = 40, 960

            # 다크 글래스 카드 배경
            draw.rounded_rectangle(
                [(px, py), (px + pw, py + ph)],
                radius=26,
                fill=(15, 23, 42, 240),
                outline=(52, 211, 153, 255),
                width=3
            )

            # 스텝 뱃지 (예: BƯỚC 1)
            if badge_text:
                self._draw_pill_badge(
                    draw=draw,
                    text=badge_text,
                    center_x=px + (pw // 2),
                    top_y=py + 18,
                    bg_rgb=badge_bg,
                    text_rgb=badge_fg,
                    font_size=22,
                    lang=lang
                )

            # 메인 텍스트
            if headline_lines:
                curr_y = py + 70
                for line_item in headline_lines:
                    txt = line_item.get("text", "")
                    col = tuple(line_item.get("color", [255, 255, 255]))
                    line_box = (px + 15, curr_y, pw - 30, 45)
                    self._draw_fitted_text(
                        draw=draw,
                        text=txt,
                        box=line_box,
                        max_font_size=26,
                        min_font_size=16,
                        font_color=col,
                        lang=lang,
                        bold=True,
                        center_h=True,
                        center_v=True
                    )
                    curr_y += 48

            # 내부 미니 인증 카드
            inner_box = (px + 25, py + 180, pw - 50, 260)
            draw.rounded_rectangle(
                [(inner_box[0], inner_box[1]), (inner_box[0] + inner_box[2], inner_box[1] + inner_box[3])],
                radius=18,
                fill=(30, 41, 59, 255),
                outline=(56, 189, 248, 200),
                width=2
            )
            # 체크마크 & 성공 버튼
            btn_box = (inner_box[0] + 20, inner_box[1] + 180, inner_box[2] - 40, 50)
            draw.rounded_rectangle(
                [(btn_box[0], btn_box[1]), (btn_box[0] + btn_box[2], btn_box[1] + btn_box[3])],
                radius=25,
                fill=(14, 165, 233, 255)
            )
            # 체크마크 벡터 그래픽
            chk_cx = btn_box[0] + 28
            chk_cy = btn_box[1] + 25
            draw.ellipse([(chk_cx - 12, chk_cy - 12), (chk_cx + 12, chk_cy + 12)], fill=(255, 255, 255, 255))
            draw.line([(chk_cx - 6, chk_cy), (chk_cx - 2, chk_cy + 4), (chk_cx + 6, chk_cy - 4)], fill=(14, 165, 233), width=3)

            btn_text_box = (btn_box[0] + 45, btn_box[1], btn_box[2] - 50, btn_box[3])
            self._draw_fitted_text(
                draw=draw,
                text=sub_text or "Thành công",
                box=btn_text_box,
                max_font_size=20,
                min_font_size=13,
                font_color=(255, 255, 255),
                lang=lang,
                bold=True,
                center_h=True,
                center_v=True
            )

        elif layout_type == "bottom_vibrant_card":
            # 🎨 4) [레퍼런스 10.5~15.0s] 하단 바이브런트 블루 와이드 카드 + 초대형 숫자 + 금화 코인
            bw, bh = 800, 310
            bx = (1080 - bw) // 2
            by = 1380

            # 바이브런트 블루 배경 + 네온 민트 테두리
            draw.rounded_rectangle(
                [(bx, by), (bx + bw, by + bh)],
                radius=32,
                fill=(37, 99, 235, 245),
                outline=(52, 211, 153, 255),
                width=4
            )

            # 상단 중앙 원형 상승 아이콘 (벡터 화살표)
            icon_size = 76
            icon_x = 540 - (icon_size // 2)
            icon_y = by - (icon_size // 2)
            draw.ellipse([(icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size)], fill=(16, 185, 129, 255))
            # 상승 화살표 벡터 드로잉
            arr_cx, arr_cy = 540, icon_y + 38
            draw.line([(arr_cx - 14, arr_cy + 8), (arr_cx - 2, arr_cy - 8), (arr_cx + 14, arr_cy - 4)], fill=(255, 255, 255), width=4)
            draw.polygon([(arr_cx + 6, arr_cy - 12), (arr_cx + 18, arr_cy - 6), (arr_cx + 12, arr_cy + 6)], fill=(255, 255, 255))

            # 배지 텍스트
            if badge_text:
                box_badge = (bx + 40, by + 48, bw - 80, 42)
                self._draw_fitted_text(
                    draw=draw,
                    text=badge_text,
                    box=box_badge,
                    max_font_size=28,
                    min_font_size=18,
                    font_color=(110, 231, 183),
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )

            # 초대형 금액/숫자 헤드라인 (예: 3.100.000 Won)
            curr_y = by + 95
            for line_item in headline_lines:
                txt = line_item.get("text", "")
                col = tuple(line_item.get("color", [255, 255, 255]))
                line_box = (bx + 30, curr_y, bw - 60, 95)
                self._draw_fitted_text(
                    draw=draw,
                    text=txt,
                    box=line_box,
                    max_font_size=68,
                    min_font_size=36,
                    font_color=col,
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )
                curr_y += 98

            # 서브 설명
            if sub_text:
                line_box = (bx + 40, curr_y, bw - 80, 45)
                self._draw_fitted_text(
                    draw=draw,
                    text=sub_text,
                    box=line_box,
                    max_font_size=24,
                    min_font_size=16,
                    font_color=(224, 231, 255),
                    lang=lang,
                    bold=False,
                    center_h=True,
                    center_v=True
                )

            # 좌우 4개 금화 코인(🪙 / ₩) 스티커 렌더링
            coin_positions = [
                (bx - 35, by + 20),
                (bx - 45, by + bh - 70),
                (bx + bw - 25, by + 20),
                (bx + bw - 15, by + bh - 70),
            ]
            for cpx, cpy in coin_positions:
                draw.ellipse([(cpx, cpy), (cpx + 60, cpy + 60)], fill=(234, 179, 8, 255), outline=(254, 240, 138, 255), width=2)
                draw.text((cpx + 14, cpy + 10), "₩", fill=(113, 63, 18), font=self._load_font(32, bold=True, lang=lang))

        elif layout_type == "trust_badge_card":
            # 🎨 5) [레퍼런스 15.0~18.5s] 앰버/에메랄드 안심 신뢰 보증 카드
            bw, bh = 940, 250
            bx = (1080 - bw) // 2
            by = 1440

            draw.rounded_rectangle(
                [(bx, by), (bx + bw, by + bh)],
                radius=26,
                fill=(124, 45, 18, 245),
                outline=(251, 146, 60, 255),
                width=3
            )

            # 상단 배지
            if badge_text:
                self._draw_pill_badge(
                    draw=draw,
                    text=badge_text,
                    center_x=540,
                    top_y=by + 16,
                    bg_rgb=badge_bg,
                    text_rgb=badge_fg,
                    font_size=22,
                    lang=lang
                )

            curr_y = by + 65
            for line_item in headline_lines:
                txt = line_item.get("text", "")
                col = tuple(line_item.get("color", [255, 255, 255]))
                line_box = (bx + 30, curr_y, bw - 60, 65)
                self._draw_fitted_text(
                    draw=draw,
                    text=txt,
                    box=line_box,
                    max_font_size=40,
                    min_font_size=22,
                    font_color=col,
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )
                curr_y += 68

            if sub_text:
                line_box = (bx + 30, curr_y, bw - 60, 45)
                self._draw_fitted_text(
                    draw=draw,
                    text=sub_text,
                    box=line_box,
                    max_font_size=24,
                    min_font_size=16,
                    font_color=(254, 215, 170),
                    lang=lang,
                    bold=False,
                    center_h=True,
                    center_v=True
                )

        else:
            # 🎨 6) [레퍼런스 18.5~22.0s] 크림슨 레드 엔딩 CTA 액션 카드
            bw, bh = 940, 260
            bx = (1080 - bw) // 2
            by = 1440

            draw.rounded_rectangle(
                [(bx, by), (bx + bw, by + bh)],
                radius=28,
                fill=(136, 19, 55, 245),
                outline=(250, 204, 21, 255),
                width=4
            )

            if badge_text:
                self._draw_pill_badge(
                    draw=draw,
                    text=badge_text,
                    center_x=540,
                    top_y=by + 16,
                    bg_rgb=badge_bg,
                    text_rgb=badge_fg,
                    font_size=24,
                    lang=lang
                )

            curr_y = by + 68
            for line_item in headline_lines:
                txt = line_item.get("text", "")
                col = tuple(line_item.get("color", [255, 255, 255]))
                line_box = (bx + 30, curr_y, bw - 60, 70)
                self._draw_fitted_text(
                    draw=draw,
                    text=txt,
                    box=line_box,
                    max_font_size=42,
                    min_font_size=24,
                    font_color=col,
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )
                curr_y += 72

            if sub_text:
                line_box = (bx + 30, curr_y, bw - 60, 45)
                self._draw_fitted_text(
                    draw=draw,
                    text=sub_text,
                    box=line_box,
                    max_font_size=26,
                    min_font_size=16,
                    font_color=(254, 240, 138),
                    lang=lang,
                    bold=True,
                    center_h=True,
                    center_v=True
                )

        img.save(out_path, "PNG")
        return out_path
