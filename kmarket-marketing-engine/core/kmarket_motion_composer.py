"""
KMarketMotionComposer - 케이마켓 전용 9:16 세로형 숏폼 모션 비디오 합성 엔진
- [A타입 (50%)]: 실제 270개 매물 당근마켓 피드 부드러운 스크롤 애니메이션 + 0원 나눔 득템 뱃지
- [B타입 (50%)]: 1인칭 외국인 직거래/원룸 방빼기 일상 비디오 + 상단 1:1 번역 채팅 푸시 알림
- 100% 현지어(17개국) 자막 바 & 프로필 링크 CTA 배너 합성
"""

import os
import math
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
from config import BASE_DIR, OUTPUTS_DIR, DATA_DIR, LANGUAGES

logger = logging.getLogger("KMarketMotionComposer")

FONT_BOLD_PATH = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REGULAR_PATH = r"C:\Windows\Fonts\malgun.ttf"

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


class KMarketMotionComposer:
    def __init__(self):
        self.output_dir = OUTPUTS_DIR / "shorts_kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compose_kmarket_shorts(
        self,
        service_id: str,
        lang: str,
        title: str,
        captions: List[str],
        audio_path: Optional[Path],
        scenario_plan: Dict[str, Any],
        real_items: List[Dict[str, Any]],
        fps: int = 15,
        duration_sec: float = 4.0
    ) -> Path:
        """
        9:16 (1080x1920) 케이마켓 전용 고화질 MP4 숏폼 비디오 생성 (imageio 기반 무결점 렌더러)
        """
        content_type = scenario_plan.get("content_mix_type", "A_feed_scroll")
        timestamp = int(os.times().system * 100)
        output_mp4 = self.output_dir / f"kmarket_shorts_{lang}_{scenario_plan.get('theme_id', 'theme')}_{timestamp}.mp4"

        W, H = 1080, 1920
        total_frames = int(fps * duration_sec)

        logger.info(f"[{lang.upper()}] 🎬 케이마켓 숏폼 비디오 렌더링 시작 (타입: {content_type}, {total_frames}프레임)")

        frames = []
        for frame_idx in range(total_frames):
            progress = frame_idx / float(total_frames)

            if content_type == "A_feed_scroll":
                # 📱 A타입: 당근 피드 스크롤 프레임 생성
                pil_img = self._render_feed_scroll_frame(lang, title, captions, real_items, progress, W, H)
            else:
                # 🎭 B타입: 리얼 상황극 & 1:1 번역 채팅 프레임 생성
                pil_img = self._render_storytelling_frame(lang, title, captions, scenario_plan, progress, W, H)

            frames.append(np.array(pil_img))

        # imageio로 MP4 인코딩
        try:
            imageio.mimwrite(str(output_mp4), frames, fps=fps, quality=8)
        except Exception as e:
            logger.warning(f"MP4 코덱 폴백 -> 이미지 프레임 저장: {e}")
            output_mp4 = self.output_dir / f"kmarket_frame_{lang}_{timestamp}.png"
            pil_img.save(output_mp4)

        logger.info(f"[{lang.upper()}] ✅ 케이마켓 숏폼 렌더링 완료: {output_mp4.name}")
        return output_mp4

    def _render_feed_scroll_frame(
        self, lang: str, title: str, captions: List[str], items: List[Dict[str, Any]], progress: float, W: int, H: int
    ) -> Image.Image:
        """A타입: 당근마켓 실물 피드 스무스 스크롤 프레임"""
        # 부드러운 배경 그라데이션
        img = Image.new("RGB", (W, H), color=(248, 245, 240))
        draw = ImageDraw.Draw(img)

        f_header = get_font(34, bold=True)
        f_badge = get_font(22, bold=True)
        f_title = get_font(38, bold=True)
        f_sub = get_font(26, bold=False)
        f_price = get_font(32, bold=True)
        f_cta = get_font(36, bold=True)

        # 1. 상단 앱 헤더 바 (고정)
        draw.rectangle([(0, 0), (W, 140)], fill=(255, 255, 255))
        draw.text((60, 48), "🥕 K-Market Expat Feed", fill=(31, 25, 20), font=f_header)
        draw.rounded_rectangle([(780, 42), (1020, 98)], radius=16, fill=(244, 238, 230))
        draw.text((810, 54), "🔴 실시간 270개", fill=(140, 120, 102), font=f_badge)

        # 2. 스크롤 모션 (아래로 300px 스무스 이동)
        scroll_offset = int(math.sin(progress * math.pi) * 220)
        card_start_y = 170 - scroll_offset

        # 3. 실물 매물 카드 3개 렌더링
        for idx, item in enumerate(items[:4]):
            card_y = card_start_y + (idx * 310)
            if card_y + 290 < 0 or card_y > H - 250:
                continue

            # 카드 컨테이너
            draw.rounded_rectangle([(40, card_y), (W - 40, card_y + 280)], radius=24, fill=(255, 255, 255), outline=(222, 209, 196), width=2)

            # 좌측 이미지 더미 / 사진 박스
            draw.rounded_rectangle([(65, card_y + 25), (295, card_y + 255)], radius=18, fill=(240, 235, 228))
            is_free = item.get("price", 0) == 0
            badge_color = (225, 29, 72) if not is_free else (16, 185, 129)
            badge_text = "0원 나눔" if is_free else "D-3 무빙"
            draw.rounded_rectangle([(75, card_y + 35), (200, card_y + 75)], radius=10, fill=badge_color)
            draw.text((88, card_y + 44), badge_text, fill=(255, 255, 255), font=f_badge)

            # 우측 상품 텍스트
            item_title = item.get("title", "실물 중고 가전/가구 매물")
            if item.get("translations") and item["translations"].get(lang):
                item_title = item["translations"][lang].get("title", item_title)
            
            draw.text((320, card_y + 35), item_title[:28], fill=(31, 25, 20), font=f_title)
            region = item.get("region", "안산/시흥/평택")
            draw.text((320, card_y + 115), f"📍 {region} • 1:1 번역 채팅", fill=(140, 120, 102), font=f_sub)

            price_str = "🎁 0 KRW (FREE)" if is_free else f"{int(item.get('price', 50000)):,} KRW"
            draw.text((320, card_y + 190), price_str, fill=(255, 107, 53) if not is_free else (16, 185, 129), font=f_price)

        # 4. 하단 자막 바 (고정)
        draw.rectangle([(0, H - 320), (W, H)], fill=(20, 25, 35))
        draw.text((60, H - 290), title[:35], fill=(255, 255, 255), font=f_header)
        draw.text((60, H - 220), "👉 " + (captions[0] if captions else "프로필 링크에서 0원 매물 즉시 확인!"), fill=(251, 191, 36), font=f_sub)

        # 5. 최하단 CTA
        draw.rounded_rectangle([(60, H - 140), (W - 60, H - 40)], radius=20, fill=(16, 185, 129))
        draw.text((220, H - 105), "📲 K-Market 앱에서 실시간 득템하기", fill=(255, 255, 255), font=f_cta)

        return img

    def _render_storytelling_frame(
        self, lang: str, title: str, captions: List[str], scenario_plan: Dict[str, Any], progress: float, W: int, H: int
    ) -> Image.Image:
        """B타입: 1인칭 외국인 일상 스토리텔링 & 1:1 번역 채팅 알림 프레임"""
        img = Image.new("RGB", (W, H), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        f_header = get_font(36, bold=True)
        f_title = get_font(42, bold=True)
        f_sub = get_font(28, bold=False)
        f_chat = get_font(30, bold=True)
        f_cta = get_font(36, bold=True)

        # 1. 상단 스토리 테마 뱃지
        draw.rectangle([(60, 80), (W - 60, 200)], fill=(30, 41, 59), outline=(59, 130, 246), width=2)
        draw.text((90, 105), f"🌏 {scenario_plan.get('theme_name', '외국인 안심 직거래')}", fill=(147, 197, 253), font=f_header)
        draw.text((90, 150), f"👤 {scenario_plan.get('persona_role', '외국인 유학생/근로자')}", fill=(226, 232, 240), font=f_sub)

        # 2. [핵심] 상단 1:1 실시간 번역 채팅 푸시 알림 박스 (펄스 애니메이션)
        pulse = int(math.sin(progress * math.pi * 3) * 6)
        chat_y = 250 + pulse
        draw.rounded_rectangle([(60, chat_y), (W - 60, chat_y + 260)], radius=28, fill=(30, 41, 59), outline=(16, 185, 129), width=3)
        draw.text((100, chat_y + 35), "💬 K-Market 1:1 Live Auto-Translate", fill=(52, 211, 153), font=f_chat)
        draw.text((100, chat_y + 95), "“Tôi có thể nhận bàn học miễn phí hôm nay không?”", fill=(255, 255, 255), font=f_sub)
        draw.text((100, chat_y + 155), "↳ (한국어 자동 번역: '오늘 무료 책상 수령 가능한가요?')", fill=(148, 163, 184), font=f_sub)
        draw.text((100, chat_y + 205), "✅ 17-Language Realtime Safe Chat Verified", fill=(251, 191, 36), font=get_font(22, bold=True))

        # 3. 중앙 비주얼 일러스트 영역 (원룸 방빼기 / 기숙사 앞 직거래)
        draw.rounded_rectangle([(60, 560), (W - 60, 1400)], radius=32, fill=(24, 34, 53), outline=(71, 85, 105), width=2)
        draw.text((120, 640), "📦 귀국 무빙세일 & 0원 나눔 득템 현장", fill=(255, 255, 255), font=f_title)
        draw.text((120, 740), "• 한국인/외국인 간 언어 장벽 없는 모국어 채팅", fill=(226, 232, 240), font=f_sub)
        draw.text((120, 820), "• 전국 130개 산업단지 & 50개 대학가 실명 인증", fill=(226, 232, 240), font=f_sub)
        draw.text((120, 900), "• 출국 전날까지 80% 초특가 가전/가구 패키지", fill=(226, 232, 240), font=f_sub)

        # 4. 하단 자막 & 원클릭 프로필 CTA
        draw.rectangle([(0, H - 340), (W, H)], fill=(15, 23, 42))
        draw.text((60, H - 300), title[:36], fill=(255, 255, 255), font=f_header)
        draw.text((60, H - 230), captions[0] if captions else "지금 바로 내 주변 0원 나눔 매물을 확인하세요!", fill=(251, 191, 36), font=f_sub)

        draw.rounded_rectangle([(60, H - 150), (W - 60, H - 45)], radius=22, fill=(16, 185, 129))
        draw.text((180, H - 110), "👉 프로필 링크 클릭하고 1분 만에 득템!", fill=(255, 255, 255), font=f_cta)

        return img
