# -*- coding: utf-8 -*-
"""
ShortsVideoComposer - 🎬 [1080x1920 세로 풀HD 고화질 마케팅 비디오 컴포저]
- Wan S2V 생성 비디오를 1080x1920 인스타 릴스/틱톡 최적 규격으로 고화질 업스케일 및 프레이밍
- 다운로드 폴더 실전 레퍼런스 기반:
  1. 상단 신뢰/혜택 뱃지 (초기비용 0원, 100% 후불제, 무료) 오버레이
  2. 스마트폰 인증 강조 팝업 (환급액 표시, 송금 완료)
  3. 엔딩 전환 극대화 CTA (지금 확인하기, 링크 클릭) 오버레이
- FFmpeg 기반 고성능 하드웨어/소프트웨어 무손실 렌더링
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ShortsVideoComposer")


class ShortsVideoComposer:
    """숏폼 비디오 후처리 및 고화질 마케팅 컴포징 엔진"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _load_font(self, size: int, bold: bool = True, lang: str = "vi") -> ImageFont.FreeTypeFont:
        """언어별 최적 유니코드 폰트 로드"""
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def generate_badge_overlay_png(
        self,
        text_primary: str,
        text_secondary: Optional[str] = None,
        badge_type: str = "success",
        out_path: str = "badge.png",
        lang: str = "vi"
    ) -> str:
        """
        동영상 위에 오버레이할 반투명 글래스모피즘 마케팅 뱃지 이미지 생성 (1080x1920 풀사이즈 투명 PNG)
        """
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_main = self._load_font(34, bold=True, lang=lang)
        font_sub = self._load_font(22, bold=False, lang=lang)

        # 상단 좌측 뱃지 카드 박스 (x: 60, y: 120, w: 420, h: 100)
        bx, by, bw, bh = 60, 130, 420, 105
        # 반투명 화이트 글래스 배경
        draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=20, fill=(255, 255, 255, 230))

        # 체크 아이콘 또는 원형 심볼
        draw.ellipse([(bx + 20, by + 22), (bx + 80, by + 82)], fill=(34, 197, 94, 255))
        # 체크 마크 그리기
        draw.line([(bx + 38, by + 52), (bx + 48, by + 65)], fill=(255, 255, 255), width=5)
        draw.line([(bx + 48, by + 65), (bx + 64, by + 40)], fill=(255, 255, 255), width=5)

        # 메인 텍스트
        draw.text((bx + 96, by + 20), text_primary, fill=(15, 23, 42), font=font_main)
        if text_secondary:
            draw.text((bx + 96, by + 60), text_secondary, fill=(34, 197, 94), font=font_sub)

        img.save(out_path, "PNG")
        return out_path

    def generate_cta_overlay_png(
        self,
        cta_text: str,
        out_path: str = "cta.png",
        lang: str = "vi"
    ) -> str:
        """
        영상 마지막 구간에 띄울 전환 유도 CTA 버튼 오버레이 생성
        """
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_cta = self._load_font(38, bold=True, lang=lang)

        # 하단 중앙 CTA 버튼 (x: 140, y: 1680, w: 800, h: 110)
        bx, by, bw, bh = 140, 1680, 800, 110
        # 눈에 띄는 오렌지/골드 버튼
        draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=55, fill=(234, 88, 12, 245))

        # 텍스트 가운데 정렬
        bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = bx + (bw - tw) // 2
        ty = by + (bh - th) // 2 - 4
        draw.text((tx, ty), cta_text, fill=(255, 255, 255), font=font_cta)

        img.save(out_path, "PNG")
        return out_path

    def finalize_1080p_shorts(
        self,
        raw_video_path: str,
        output_mp4_path: str,
        badge_text_primary: Optional[str] = None,
        badge_text_secondary: Optional[str] = None,
        cta_text: Optional[str] = None,
        lang: str = "vi",
        target_w: int = 1080,
        target_h: int = 1920
    ) -> str:
        """
        원본 비디오를 1080x1920 고화질로 변환하고 마케팅 오버레이 뱃지를 결합하여 최종 MP4 생성
        """
        temp_dir = os.path.dirname(output_mp4_path)
        os.makedirs(temp_dir, exist_ok=True)

        # 1. 뱃지 및 CTA 오버레이 이미지 준비
        badge_png = None
        if badge_text_primary:
            badge_png = os.path.join(temp_dir, f"temp_badge_{lang}.png")
            self.generate_badge_overlay_png(
                text_primary=badge_text_primary,
                text_secondary=badge_text_secondary,
                out_path=badge_png,
                lang=lang
            )

        cta_png = None
        if cta_text:
            cta_png = os.path.join(temp_dir, f"temp_cta_{lang}.png")
            self.generate_cta_overlay_png(cta_text=cta_text, out_path=cta_png, lang=lang)

        # 2. FFmpeg 복합 필터 구성 (Scale to 1080x1920 + Overlay)
        filter_complex = []
        # 기본 비디오 1080x1920 스케일 (화면 비율 유지하며 꽉 차게 중앙 크롭)
        filter_complex.append(f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h}[base]")
        
        last_v = "base"
        input_args = ["-i", raw_video_path]
        curr_idx = 1

        if badge_png and os.path.exists(badge_png):
            input_args.extend(["-i", badge_png])
            filter_complex.append(f"[{last_v}][{curr_idx}:v]overlay=0:0:enable='between(t,0,999)'[v_badge]")
            last_v = "v_badge"
            curr_idx += 1

        if cta_png and os.path.exists(cta_png):
            input_args.extend(["-i", cta_png])
            # 마지막 4초 동안 혹은 전체 지속
            filter_complex.append(f"[{last_v}][{curr_idx}:v]overlay=0:0:enable='gte(t,1.5)'[v_final]")
            last_v = "v_final"
            curr_idx += 1

        filter_str = ";".join(filter_complex)

        cmd = [
            self.ffmpeg_exe, "-y",
            *input_args,
            "-filter_complex", filter_str,
            "-map", f"[{last_v}]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "19",
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "192k",
            output_mp4_path
        ]

        logger.info(f"🚀 [ShortsVideoComposer] FFmpeg 1080p 고화질 렌더링 시작 -> {output_mp4_path}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"✅ [ShortsVideoComposer] 1080p 숏폼 완성: {output_mp4_path}")

        # 임시 오버레이 정리
        for p in [badge_png, cta_png]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        return output_mp4_path
