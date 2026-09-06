# -*- coding: utf-8 -*-
"""
ScreenInsetCompositor - 📱 [프리미엄 금융 카드뉴스 스타일: 최신 스마트폰 본체 디바이스 정밀 인셋 컴포지터]
- 어색한 손가락/손목 잘림을 100% 원천 배제
- 최신 플래그십 슬림 메탈 베젤 & 라운드 글래스 스마트폰 본체 에셋 렌더링
- PhoneAppScreenRenderer(15개 언어별 NH BANK 세무 환급 통지 화면) 탑재
- 고급스러운 3D 드롭 섀도우(Drop Shadow)로 인물 사진과 자연스러운 입체 분리감 형성
- 우측 전면에 단정하고 세련되게 배치되어 인물의 표정과 제스처를 전혀 가리지 않음
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

from core.phone_app_screen_renderer import PhoneAppScreenRenderer

logger = logging.getLogger("ScreenInsetCompositor")


class ScreenInsetCompositor:
    """토스·카카오뱅크 스타일의 세련된 최신 스마트폰 디바이스 인셋 합성기 (손가락 없는 클린 룩)"""
    def __init__(self):
        self.screen_renderer = PhoneAppScreenRenderer()

    def composite_screen_onto_photo(
        self,
        base_photo: Image.Image,
        amount_krw: int = 4250000,
        lang: str = "vi",
        user_name: str = "E-9 WORKER",
        scale: float = 0.68,
        position_offset: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """
        base_photo (1080 x 945 크기)의 우측 전면에
        손가락 없이 깔끔하고 세련된 '최신 스마트폰 디바이스 본체 + NH BANK 환급 화면'을 정밀 인셋
        """
        # 1. 15개 언어별 실제 스마트폰 환급 화면 렌더링 (베젤 포함 약 496 x 976)
        phone_path = self.screen_renderer.render_bank_phone_screen(
            amount_krw=amount_krw,
            lang=lang,
            user_name=user_name
        )
        phone_device = Image.open(phone_path).convert("RGBA")

        # 2. 카드뉴스 상단 사진(1080x945)에 딱 맞는 크기로 리사이즈 (너비 약 340px, 높이 약 670px)
        target_w = int(phone_device.width * scale)
        target_h = int(phone_device.height * scale)
        resized_phone = phone_device.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 3. 우측 전면 최적 배치 좌표 계산 (인물의 얼굴을 가리지 않는 황금 위치)
        if position_offset:
            paste_x, paste_y = position_offset
        else:
            paste_x = int(base_photo.width * 0.64)   # 약 690px
            paste_y = int(base_photo.height * 0.22)  # 약 210px

        # 4. 고급스러운 3D 입체 드롭 섀도우 생성 (토스/애플 스타일 은은한 깊이감)
        shadow_canvas = Image.new("RGBA", (base_photo.width, base_photo.height), (0, 0, 0, 0))
        shadow_box = Image.new("RGBA", (target_w + 40, target_h + 40), (0, 0, 0, 0))
        
        # 폰 알파 마스크를 그림자 형태로 블러링
        phone_alpha = resized_phone.split()[3]
        shadow_box.paste((0, 0, 0, 130), (20, 20), phone_alpha)
        shadow_box = shadow_box.filter(ImageFilter.GaussianBlur(18))

        # 그림자를 폰 살짝 아래/우측에 깔기
        shadow_canvas.paste(shadow_box, (paste_x - 10, paste_y + 8), shadow_box)

        # 5. 순차 합성 (인물 사진 -> 부드러운 그림자 -> 깔끔한 스마트폰 본체)
        result_photo = base_photo.convert("RGBA")
        result_photo.paste(shadow_canvas, (0, 0), shadow_canvas)
        result_photo.paste(resized_phone, (paste_x, paste_y), resized_phone)

        logger.info(f"📱 [ScreenInsetCompositor] 클린 최신 스마트폰 본체 인셋 성공 (x={paste_x}, y={paste_y}, 언어={lang})")
        return result_photo.convert("RGB")

    def composite_easytax_screen_onto_photo(
        self,
        base_photo: Image.Image,
        screen_img_path: Path,
        lang: str = "uz",
        position: str = "center",
        scale: float = 0.74,
    ) -> Image.Image:
        """
        슬라이드 3번(0원 보증 앱 화면) 및 5번(1분 환급신청 메인 앱 화면) 전용:
        실제 이지텍스 모바일 캡처 화면을 최신 스마트폰 디바이스 본체 프레임 + 3D 드롭 섀도우와 함께 합성.
        """
        if not screen_img_path or not screen_img_path.exists():
            logger.warning(f"스크린샷 파일 부재: {screen_img_path}, 원본 반환")
            return base_photo

        raw_screen = Image.open(screen_img_path).convert("RGBA")

        # 이미 스마트폰 베젤(테두리)이 씌워진 파일인지 판별
        # 너비 대비 높이 비율이 약 1:2 규격이거나, 430x932 등의 순정 캡처인 경우 스마트폰 프레임 씌우기
        if raw_screen.width <= 500 and raw_screen.height >= 900 and raw_screen.mode == "RGBA" and "phone_device" in str(screen_img_path):
            phone_device = raw_screen
        else:
            # 순정 웹 캡처 화면일 경우: 상단 상태바 & 모바일 라운드 글래스 및 슬림 베젤 프레임 입히기
            w, h = 480, 960
            screen_resized = raw_screen.resize((w, h), Image.Resampling.LANCZOS)
            
            # 둥근 모서리 마스킹
            corner_mask = Image.new("L", (w, h), 0)
            cm_draw = ImageDraw.Draw(corner_mask)
            cm_draw.rounded_rectangle([0, 0, w, h], radius=int(w * 0.08), fill=255)
            screen_resized.putalpha(corner_mask)

            # 슬림 티타늄 메탈 베젤
            phone_device = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
            pd_draw = ImageDraw.Draw(phone_device)
            pd_draw.rounded_rectangle([0, 0, w + 16, h + 16], radius=int(w * 0.09) + 4, fill=(30, 34, 42, 255), outline=(100, 116, 139, 255), width=3)
            phone_device.paste(screen_resized, (8, 8), screen_resized)

        # 2. 카드뉴스 상단 사진(1080x945)에 적합한 크기로 리사이즈
        target_w = int(phone_device.width * scale)
        target_h = int(phone_device.height * scale)
        resized_phone = phone_device.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 3. 위치 계산 (center: 정중앙 배치, right: 우측 배치)
        if position == "center":
            paste_x = (base_photo.width - target_w) // 2
            paste_y = (base_photo.height - target_h) // 2
        else:
            paste_x = int(base_photo.width * 0.60)
            paste_y = int(base_photo.height * 0.18)

        # 4. 프리미엄 3D 드롭 섀도우
        shadow_canvas = Image.new("RGBA", (base_photo.width, base_photo.height), (0, 0, 0, 0))
        shadow_box = Image.new("RGBA", (target_w + 50, target_h + 50), (0, 0, 0, 0))
        phone_alpha = resized_phone.split()[3]
        shadow_box.paste((0, 0, 0, 150), (25, 25), phone_alpha)
        shadow_box = shadow_box.filter(ImageFilter.GaussianBlur(22))
        shadow_canvas.paste(shadow_box, (paste_x - 12, paste_y + 10), shadow_box)

        # 5. 합성
        result_photo = base_photo.convert("RGBA")
        result_photo.paste(shadow_canvas, (0, 0), shadow_canvas)
        result_photo.paste(resized_phone, (paste_x, paste_y), resized_phone)

        logger.info(f"📱 [ScreenInsetCompositor] 이지텍스 실제 앱 화면 인셋 완료 (위치={position}, x={paste_x}, y={paste_y})")
        return result_photo.convert("RGB")

