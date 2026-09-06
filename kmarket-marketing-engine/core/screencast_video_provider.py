# -*- coding: utf-8 -*-
"""
ScreencastVideoProvider - 📱 [EasyTax 실물 모바일 웹 화면 녹화 비디오 프로바이더]
- 정지 이미지 슬라이드쇼의 한계를 탈피하고 시청자에게 '실제 서비스 실체'를 증명
- 씬 3(조회/확인 단계)에 실제 스마트폰에서 이지텍스(KTRS) 모바일 웹 3초 간편조회가 일어나는 1080x1920 세로형 비디오 클립 생성 및 제공
- 스마트폰 목업 프레임 안에서 숫자가 0원에서 3,840,000원으로 고속 카운팅되는 역동적인 모션 그래픽 비디오 생성
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import DATA_DIR, OUTPUTS_DIR

logger = logging.getLogger("ScreencastVideoProvider")

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"


class ScreencastVideoProvider:
    """
    🎬 이지텍스 실물 스크린캐스트 비디오 클립 생성 및 공급자
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts" / "screencasts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.output_dir / "temp_frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def get_or_render_screencast_clip(
        self,
        lang: str = "vi",
        amount_krw: int = 3840000,
        duration_sec: float = 4.0,
        fps: int = 25
    ) -> Optional[Path]:
        """
        📱 실물 스마트폰 3초 간편조회 카운트업 비디오 클립 생성 (1080x1920, 25fps, H.264 MP4)
        """
        out_mp4 = self.output_dir / f"screencast_demo_{lang}_{amount_krw}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 10000:
            logger.info(f"⚡ [Screencast] 기존 캐시된 스크린캐스트 클립 재활용: {out_mp4.name}")
            return out_mp4

        total_frames = int(duration_sec * fps)
        W, H = 1080, 1920

        # 다국어 라벨
        i18n = {
            "vi": {"header": "EasyTax • Tính Thuế 1 Phút", "sub": "Đang kết nối Cục Thuế Quốc Gia (NTS)...", "done": "Số Tiền Hoàn Thuế Tối Đa"},
            "en": {"header": "EasyTax • 1-Min Tax Calculator", "sub": "Connecting to National Tax Service...", "done": "Max Estimated Tax Refund"},
            "ko": {"header": "EasyTax • 1분 무료 환급 조회", "sub": "국세청 홈택스 실시간 안전 연동 중...", "done": "예상 소득세 환급금 합계"}
        }
        meta = i18n.get(lang, i18n["en"])

        font_header = ImageFont.load_default()
        font_num = ImageFont.load_default()
        try:
            font_header = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 36)
            font_num = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 68)
            font_sub = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 26)
        except Exception:
            pass

        # 프레임 일괄 렌더링 (카운트업 애니메이션)
        frame_pattern = self.temp_dir / "frame_%04d.png"
        for f_idx in range(total_frames):
            progress = min(1.0, f_idx / (total_frames * 0.7))  # 70% 시점에 목표 금액 도달
            cur_amt = int(amount_krw * progress)

            frame = Image.new("RGB", (W, H), (15, 23, 42))  # 모던 다크 블루 배경
            draw = ImageDraw.Draw(frame)

            # 1. 스마트폰 베젤 외곽선 (중앙에 스마트폰 거치 형태)
            phone_box = [120, 180, 960, 1740]
            draw.rounded_rectangle(phone_box, radius=54, fill=(248, 250, 252), outline=(51, 65, 85), width=8)

            # 노치 / 카메라 아일랜드
            draw.rounded_rectangle([420, 204, 660, 238], radius=16, fill=(15, 23, 42))

            # 2. 웹 브라우저 상단 주소창 (https://ktrs.kr/vi)
            draw.rounded_rectangle([160, 260, 920, 320], radius=16, fill=(241, 245, 249), outline=(226, 232, 240), width=2)
            draw.text((180, 274), f"🔒 ktrs.kr/{lang} • Official Tax System", fill=(100, 116, 139), font=font_sub)

            # 3. EasyTax 서비스 헤더 & 국세청 로고 엠블럼
            draw.text((180, 360), meta["header"], fill=(15, 23, 42), font=font_header)
            draw.line([(180, 420), (900, 420)], fill=(226, 232, 240), width=2)

            # 4. 신청자 프로필 카드 (E-9 / D-2 비자 태그)
            draw.rounded_rectangle([180, 450, 900, 560], radius=20, fill=(238, 242, 255), outline=(99, 102, 241), width=2)
            draw.text((210, 475), "👤 외국인 근로자 소득세 경정청구 (조특법 30조)", fill=(67, 56, 202), font=font_sub)
            draw.text((210, 515), "5개년 (2020~2024) 90% 세액 감면 대상 확인 완료 ✅", fill=(79, 70, 229), font=font_sub)

            # 5. 실시간 환급금 카운터 대형 디스플레이 박스 (네온 그린 테두리)
            box_rect = [180, 600, 900, 900]
            draw.rounded_rectangle(box_rect, radius=24, fill=(15, 23, 42), outline=(16, 185, 129), width=4)
            
            draw.text((210, 640), meta["done"], fill=(148, 163, 184), font=font_sub)
            draw.text((210, 710), f"+₩{cur_amt:,} KRW", fill=(52, 211, 153), font=font_num)

            status_text = "● 실시간 국세청 전산 자동 매칭 중..." if progress < 1.0 else "✅ 최종 환급 결정 세액 산출 완료!"
            status_color = (250, 204, 21) if progress < 1.0 else (52, 211, 153)
            draw.text((210, 820), status_text, fill=status_color, font=font_sub)

            # 6. 하단 CTA 터치 버튼 (손가락 클릭 효과)
            btn_rect = [180, 950, 900, 1050]
            btn_fill = (37, 99, 235) if progress < 1.0 else (16, 185, 129)
            draw.rounded_rectangle(btn_rect, radius=20, fill=btn_fill)
            btn_text = "1분 만에 내 통장으로 환급 신청하기 👉" if progress >= 1.0 else "세액 계산 분석 중..."
            draw.text((240, 980), btn_text, fill=(255, 255, 255), font=font_header)

            frame.save(self.temp_dir / f"frame_{f_idx:04d}.png")

        # FFmpeg으로 MP4 인코딩
        cmd = [
            FFMPEG_EXE, "-y",
            "-r", str(fps),
            "-i", str(self.temp_dir / "frame_%04d.png"),
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-t", str(duration_sec),
            str(out_mp4)
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=40)
            # 임시 프레임 청소
            for f in self.temp_dir.glob("frame_*.png"):
                try:
                    f.unlink()
                except Exception:
                    pass

            if out_mp4.exists() and out_mp4.stat().st_size > 1000:
                logger.info(f"🎉 [Screencast] 실물 스마트폰 3초 간편조회 클립 생성 성공: {out_mp4.name}")
                return out_mp4
        except Exception as e:
            logger.error(f"스크린캐스트 렌더링 예외: {e}")

        return None
