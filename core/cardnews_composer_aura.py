"""
CardnewsComposerEasyTax - 💰 [EasyTax 전용 7:3 황금 분할 1080x1350 카드뉴스 캔버스 합성 엔진]
- 규격: 1080 × 1350 (4:5 인스타그램/페이스북 최고 전환율 규격)
- 상단 70% (1080 × 945px): 4K 극실사 환급/산단 사진 배치
- 구분선: 3px 럭셔리 골드 라인 (#D4AF37)
- 하단 30% (1080 × 405px): 딥 네이비(#0B132B) 전용 텍스트 컨테이너
- 17개국어 전용 폰트 렌더링 (베트남어 복합성조, 러시아어, 우즈베크어, 한국어 등 100% 무결점)
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("CardnewsComposerEasyTax")


def _load_font(size: int, bold: bool = True, lang: str = "vi") -> ImageFont.FreeTypeFont:
    """
    🎯 언어별 최적 유니코드 폰트 자동 매칭
    - 한국어: Malgun Gothic (맑은 고딕)
    - 베트남어/라틴/키릴(우즈벡, 러시아 등): Segoe UI / Arial (베트남어 복합 성조 100% 지원)
    """
    if lang == "ko":
        font_candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
    elif lang in ["vi", "es", "id", "tl", "en"]:  # 베트남어 및 라틴 성조 문자 100% 지원
        font_candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
            r"C:\Windows\Fonts\timesbd.ttf" if bold else r"C:\Windows\Fonts\times.ttf",
        ]
    elif lang in ["ru", "uz", "mn", "kk"]:  # 키릴 및 중앙아시아 문자
        font_candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        ]
    else:
        font_candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        ]

    for p in font_candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _sanitize_display_text(text: str) -> str:
    """화면 렌더링 시 네모(□)로 깨지는 4바이트 특수 이모지를 안전하게 제거"""
    if not text:
        return ""
    emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
    cleaned = emoji_pattern.sub("", text)
    return cleaned.strip()


class CardnewsComposerEasyTax:
    """
    💰 EasyTax 전용 7:3 분할 카드뉴스 캔버스 합성기
    """
    WIDTH = 1080
    HEIGHT = 1350
    TOP_HEIGHT = 945      # 상단 70% (사진 영역)
    BOTTOM_HEIGHT = 405   # 하단 30% (텍스트 영역)

    # 테마 색상 (EasyTax: 딥네이비 & 골드 & 화이트)
    BG_COLOR = (11, 19, 43)        # #0B132B (딥 네이비)
    BORDER_COLOR = (212, 175, 55)   # #D4AF37 (골드)
    TEXT_WHITE = (255, 255, 255)
    TEXT_GOLD = (251, 191, 36)      # #FBBF24
    TEXT_MUTED = (203, 213, 225)    # #CBD5E1 (소프트 그레이)
    BADGE_BG = (30, 41, 59)         # #1E293B

    def __init__(self):
        pass

    def _draw_centered_autofit_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        y: int,
        target_w: int = 984,
        max_h: int = 110,
        start_size: int = 60,
        min_size: int = 24,
        bold: bool = True,
        fill_color: tuple = (255, 255, 255),
        line_spacing: int = 8,
        lang: str = "vi"
    ) -> int:
        """
        🎯 [가로 너비 맞춤 동적 폰트 스케일링 & 중앙 정렬 엔진]
        """
        for size in range(start_size, min_size - 1, -1):
            font = _load_font(size, bold=bold, lang=lang)
            words = text.split(" ")
            lines = []
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip() if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]
                if w <= target_w:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # 외톨이 단어 방지 (마지막 줄에 1단어만 남는 경우 균형 조정)
            if len(lines) == 2 and len(lines[1].split()) == 1 and len(lines[0].split()) > 2:
                words_l0 = lines[0].split()
                cand_l0 = " ".join(words_l0[:-1])
                cand_l1 = f"{words_l0[-1]} {lines[1]}"
                b0 = draw.textbbox((0, 0), cand_l0, font=font)
                b1 = draw.textbbox((0, 0), cand_l1, font=font)
                if (b0[2] - b0[0]) <= target_w and (b1[2] - b1[0]) <= target_w:
                    lines = [cand_l0, cand_l1]

            # 각 줄의 가로폭 및 전체 높이 계산
            line_heights = []
            line_widths = []
            exceeds_w = False
            for l in lines:
                bb = draw.textbbox((0, 0), l, font=font)
                lw = bb[2] - bb[0]
                if lw > target_w:
                    exceeds_w = True
                    break
                line_widths.append(lw)
                line_heights.append(bb[3] - bb[1])

            if exceeds_w:
                continue

            total_h = sum(line_heights) + line_spacing * max(0, len(lines) - 1)
            if total_h <= max_h or size == min_size:
                # 🎯 정중앙(Center) 배치 렌더링
                curr_y = y
                for idx, line_str in enumerate(lines):
                    lw = line_widths[idx]
                    center_x = (self.WIDTH - lw) // 2
                    draw.text((center_x, curr_y), line_str, font=font, fill=fill_color)
                    curr_y += line_heights[idx] + line_spacing
                return curr_y

        return y + max_h

    def compose_slide(
        self,
        top_image_path: Optional[Path],
        card_data: Dict[str, Any],
        slide_idx: int,
        total_slides: int = 5,
        output_path: Optional[Path] = None,
        lang: str = "vi"
    ) -> Path:
        """
        7:3 분할 완성형 카드뉴스 단일 슬라이드 합성
        """
        # 1. 베이스 캔버스 생성 (1080 x 1350)
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        font_badge = _load_font(30, bold=True, lang=lang)
        font_indicator = _load_font(30, bold=True, lang=lang)

        # 2. 상단 70% 사진 합성 (1080 x 945px 맞춤 크롭 & 배치)
        if top_image_path and os.path.exists(top_image_path):
            try:
                top_img = Image.open(top_image_path).convert("RGB")
                img_ratio = top_img.width / top_img.height
                target_ratio = self.WIDTH / self.TOP_HEIGHT

                if img_ratio > target_ratio:
                    new_h = self.TOP_HEIGHT
                    new_w = int(self.TOP_HEIGHT * img_ratio)
                else:
                    new_w = self.WIDTH
                    new_h = int(self.WIDTH / img_ratio)

                resized_img = top_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - self.WIDTH) // 2
                top = (new_h - self.TOP_HEIGHT) // 2
                cropped_img = resized_img.crop((left, top, left + self.WIDTH, top + self.TOP_HEIGHT))

                canvas.paste(cropped_img, (0, 0))
            except Exception as e:
                logger.warning(f"EasyTax 상단 사진 합성 실패 (솔리드 대체): {e}")
                draw.rectangle([(0, 0), (self.WIDTH, self.TOP_HEIGHT)], fill=(15, 23, 42))
        else:
            draw.rectangle([(0, 0), (self.WIDTH, self.TOP_HEIGHT)], fill=(15, 23, 42))

        # 📱 2-1. [스마트폰 인셋 합성]: 1번(NH BANK 통지), 3번(이지텍스 0원보증 앱화면), 5번(이지텍스 1분조회 메인화면)
        try:
            from core.screen_inset_compositor import ScreenInsetCompositor
            compositor = ScreenInsetCompositor()
            top_part = canvas.crop((0, 0, self.WIDTH, self.TOP_HEIGHT))

            if slide_idx == 1:
                search_scope = f"{card_data.get('title', '')} {card_data.get('subtitle', '')} {' '.join(card_data.get('bullets', []))}"
                amount_candidates = re.findall(r'\b\d{1,3}(?:[,\.\s]\d{3})+\b', search_scope)
                parsed_amount = 3800000
                if amount_candidates:
                    valid_nums = [int(re.sub(r'[^\d]', '', c)) for c in amount_candidates if int(re.sub(r'[^\d]', '', c)) >= 100000]
                    if valid_nums:
                        parsed_amount = valid_nums[0]
                composed_top = compositor.composite_screen_onto_photo(
                    base_photo=top_part,
                    amount_krw=parsed_amount,
                    lang=lang,
                    user_name="E-9 WORKER"
                )
                canvas.paste(composed_top, (0, 0))
                logger.info("📱 [슬라이드 1] 대표님 레퍼런스 스타일 스마트폰 액정 실물 인셋 합성 성공!")

            elif slide_idx == 3:
                from core.easytax_app_capturer import EasyTaxAppCapturer
                capturer = EasyTaxAppCapturer()
                screen_path = capturer.get_screen_path(lang=lang, screen_type="step0")
                composed_top = compositor.composite_easytax_screen_onto_photo(
                    base_photo=top_part,
                    screen_img_path=screen_path,
                    lang=lang,
                    position="center",
                    scale=0.74
                )
                canvas.paste(composed_top, (0, 0))
                logger.info(f"📱 [슬라이드 3] 이지텍스 실제 앱 0원 보증 모바일 화면 인셋 합성 성공! ({lang})")

            elif slide_idx == 5:
                from core.easytax_app_capturer import EasyTaxAppCapturer
                capturer = EasyTaxAppCapturer()
                screen_path = capturer.get_screen_path(lang=lang, screen_type="home_cta")
                composed_top = compositor.composite_easytax_screen_onto_photo(
                    base_photo=top_part,
                    screen_img_path=screen_path,
                    lang=lang,
                    position="center",
                    scale=0.74
                )
                canvas.paste(composed_top, (0, 0))
                logger.info(f"📱 [슬라이드 5] 이지텍스 실제 앱 1분 조회 CTA 모바일 화면 인셋 합성 성공! ({lang})")

        except Exception as e:
            logger.warning(f"슬라이드 {slide_idx} 화면 인셋 합성 건너뜀: {e}")

        # 3. 7:3 경계 골드 구분선 그리기 (3px)
        draw.line([(0, self.TOP_HEIGHT), (self.WIDTH, self.TOP_HEIGHT)], fill=self.BORDER_COLOR, width=3)

        # 4. 하단 30% 대형 가로 맞춤 & 정중앙 정렬 텍스트 렌더링 (Y: 945px ~ 1350px)
        y_cursor = self.TOP_HEIGHT + 14
        margin_x = 48
        target_content_w = 984  # 1080 - 96 (안전 가로 영역)

        # ── A. 상단 배지 & 슬라이드 인디케이터
        badge_text = _sanitize_display_text(card_data.get("badge", f"STEP {slide_idx:02d}"))
        indicator_text = f"{slide_idx:02d} / {total_slides:02d} >"

        badge_bbox = draw.textbbox((margin_x, y_cursor), f"  {badge_text}  ", font=font_badge)
        padded_bbox = (badge_bbox[0], badge_bbox[1] - 4, badge_bbox[2] + 4, badge_bbox[3] + 4)
        draw.rectangle(padded_bbox, fill=self.BADGE_BG, outline=self.BORDER_COLOR, width=2)
        draw.text((margin_x + 10, y_cursor), badge_text, font=font_badge, fill=self.TEXT_GOLD)

        ind_bbox = draw.textbbox((0, 0), indicator_text, font=font_indicator)
        ind_w = ind_bbox[2] - ind_bbox[0]
        draw.text((self.WIDTH - margin_x - ind_w, y_cursor), indicator_text, font=font_indicator, fill=self.TEXT_GOLD)

        y_cursor += 56

        # ── B. 🎯 [가로 꽉 채움 초대형 헤드라인] (60pt ~ 30pt 중앙 정렬)
        title_text = _sanitize_display_text(card_data.get("title", ""))
        y_cursor = self._draw_centered_autofit_text(
            draw=draw, text=title_text,
            y=y_cursor, target_w=target_content_w,
            max_h=110, start_size=60, min_size=28, bold=True,
            fill_color=self.TEXT_WHITE, line_spacing=6, lang=lang
        )
        y_cursor += 6

        # ── C. 🎯 [가로 꽉 채움 골드 서브카피] (36pt ~ 24pt 중앙 정렬)
        sub_text = _sanitize_display_text(card_data.get("subtitle", ""))
        if sub_text:
            y_cursor = self._draw_centered_autofit_text(
                draw=draw, text=sub_text,
                y=y_cursor, target_w=target_content_w,
                max_h=65, start_size=34, min_size=22, bold=True,
                fill_color=self.TEXT_GOLD, line_spacing=4, lang=lang
            )
            y_cursor += 8

        # ── D. 🎯 [3줄 핵심 요약 대형 불릿 포인트] (28pt ~ 20pt 시원한 줄간격)
        bullets = card_data.get("bullets", [])
        for b in bullets[:3]:
            b_str = _sanitize_display_text(str(b).strip())
            if not b_str.startswith("•") and not b_str[0].isdigit():
                b_str = f"• {b_str}"
            y_cursor = self._draw_centered_autofit_text(
                draw=draw, text=b_str,
                y=y_cursor, target_w=target_content_w,
                max_h=55, start_size=26, min_size=18, bold=False,
                fill_color=self.TEXT_MUTED, line_spacing=4, lang=lang
            )
            y_cursor += 6

        # 5. 최종 파일 저장
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(output_path, "JPEG", quality=95)
            logger.info(f"✅ [EasyTax 7:3 카드뉴스 렌더링 완료]: {output_path.name}")

        return output_path
