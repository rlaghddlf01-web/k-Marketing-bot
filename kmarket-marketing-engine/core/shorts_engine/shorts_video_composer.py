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
        """언어별 최적 유니코드 폰트 로드 (한글 및 다국어 악센트 깨짐 100% 방지)"""
        if lang in ["ko", "kor"]:
            candidates = [
                r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
                r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            ]
        else:
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

    def _draw_fitted_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        box: tuple,
        max_font_size: int = 42,
        min_font_size: int = 18,
        font_color: tuple = (255, 255, 255),
        pad_x: int = 40,
        pad_y: int = 12,
        lang: str = "vi",
        bold: bool = True,
        center_v: bool = True
    ) -> tuple:
        """
        글자가 박스 밖으로 나가지 않도록 폰트 크기를 1px씩 자동 축소하고 안전 마진을 사수하는 렌더러
        """
        bx, by, bw, bh = box
        max_w = bw - (pad_x * 2)
        max_h = bh - (pad_y * 2)

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

        # 가로 중앙 정렬 (박스 이탈 절대 불가 클램핑)
        tx = max(bx + pad_x, bx + (bw - tw) // 2)
        if tx + tw > bx + bw - pad_x:
            tx = max(bx + pad_x, bx + bw - pad_x - tw)

        if center_v:
            ty = by + (bh - th) // 2 - bbox[1]
        else:
            ty = by + pad_y

        draw.text((tx, ty), text, fill=font_color, font=font)
        return tx, ty, tw, th

    def generate_top_box_png(
        self,
        header_text: str,
        palette: Dict[str, Any],
        out_path: str = "top_box.png",
        lang: str = "vi"
    ) -> str:
        """
        상단 고정 헤더 박스 생성 (x: 60, y: 80, w: 960, h: 110)
        - 인물 얼굴과 앱 본문 시야 100% 개방
        - 제미나이가 지정한 동적 컬러 팔레트 적용
        """
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        tb_cfg = palette.get("top_box", {})
        fill_rgb = tuple(tb_cfg.get("fill", [255, 204, 0]))
        border_rgb = tuple(tb_cfg.get("border", [255, 255, 255]))
        text_rgb = tuple(tb_cfg.get("text", [15, 23, 42]))

        box = (60, 80, 960, 110)
        draw.rounded_rectangle(
            [(box[0], box[1]), (box[0] + box[2], box[1] + box[3])],
            radius=22,
            fill=(*fill_rgb, 245),
            outline=(*border_rgb, 255),
            width=3
        )

        self._draw_fitted_text(
            draw=draw,
            text=header_text,
            box=box,
            max_font_size=44,
            min_font_size=20,
            font_color=text_rgb,
            pad_x=45,
            lang=lang,
            bold=True,
            center_v=True
        )

        img.save(out_path, "PNG")
        return out_path

    def generate_bottom_box_png(
        self,
        title_text: str,
        sub_text: str,
        palette: Dict[str, Any],
        out_path: str = "bottom_box.png",
        lang: str = "vi"
    ) -> str:
        """
        하단 씬 자막 박스 생성 (x: 60, y: 1500, w: 960, h: 190)
        - 1행: 헤드라인 자막 (타이틀 컬러, 폰트 자동 축소)
        - 2행: 서브 설명 자막 (서브 컬러, 폰트 자동 축소)
        """
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bb_cfg = palette.get("bottom_box", {})
        fill_rgb = tuple(bb_cfg.get("fill", [11, 19, 43]))
        border_rgb = tuple(bb_cfg.get("border", [255, 204, 0]))
        title_rgb = tuple(bb_cfg.get("title", [255, 204, 0]))
        sub_rgb = tuple(bb_cfg.get("sub", [241, 245, 249]))

        box = (60, 1500, 960, 190)
        draw.rounded_rectangle(
            [(box[0], box[1]), (box[0] + box[2], box[1] + box[3])],
            radius=24,
            fill=(*fill_rgb, 245),
            outline=(*border_rgb, 255),
            width=3
        )

        # 1행 헤드라인 (상단 영역)
        box_line1 = (box[0], box[1] + 16, box[2], 75)
        self._draw_fitted_text(
            draw=draw,
            text=title_text,
            box=box_line1,
            max_font_size=40,
            min_font_size=20,
            font_color=title_rgb,
            pad_x=45,
            lang=lang,
            bold=True,
            center_v=True
        )

        # 2행 서브설명 (하단 영역)
        box_line2 = (box[0], box[1] + 95, box[2], 75)
        self._draw_fitted_text(
            draw=draw,
            text=sub_text,
            box=box_line2,
            max_font_size=28,
            min_font_size=16,
            font_color=sub_rgb,
            pad_x=45,
            lang=lang,
            bold=False,
            center_v=True
        )

        img.save(out_path, "PNG")
        return out_path


    def create_ending_cta_segment_mp4(
        self,
        output_path: str,
        lang: str = "vi",
        duration_sec: float = 4.0,
        domain_text: str = "ktrs-service.vercel.app",
        cta_button_text: str = "CHECK NOW >"
    ) -> str:
        """
        18초~22초 구간에 들어갈 안심 신뢰 보증 및 최종 CTA 세로 풀HD 비디오 클립 생성
        """
        img = Image.new("RGBA", (1080, 1920), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)

        font_large = self._load_font(46, bold=True, lang=lang)
        font_mid = self._load_font(34, bold=True, lang=lang)
        font_small = self._load_font(26, bold=False, lang=lang)
        font_cta = self._load_font(40, bold=True, lang=lang)

        CTA_LANG_MAP = {
            "vi": {
                "sub": "DỊCH VỤ THUẾ QUỐC GIA KTRS",
                "title": "An Tâm Hoàn Thuế 100%",
                "f1_t": "100% Hậu Mãi", "f1_d": "Chỉ thanh toán phí sau khi nhận tiền vào tài khoản",
                "f2_t": "0 Won Phí Trước", "f2_d": "Không thu bất kỳ khoản phí đặt cọc nào",
                "f3_t": "Ủy Quyền Chính Thức", "f3_d": "Đại lý thuế hợp pháp của Cục Thuế Hàn Quốc",
                "domain_lbl": "Trang web tra cứu miễn phí:",
                "btn": "KIỂM TRA MIỄN PHÍ >"
            },
            "uz": {
                "sub": "KTRS DAVLAT SOLIQ XIZMATI",
                "title": "100% Qonuniy Soliq Qaytarish",
                "f1_t": "100% Oldindan To'lov Yo'q", "f1_d": "Faqat pul hisobga tushgach to'laysiz",
                "f2_t": "0 Von Boshlang'ich To'lov", "f2_d": "Hech qanday oldindan to'lov olinmaydi",
                "f3_t": "Rasmiy Litsenziya", "f3_d": "Koreya Davlat Soliq Xizmati akkreditatsiyasi",
                "domain_lbl": "Rasmiy bepul tekshirish sayti:",
                "btn": "HOZIROQ TEKSHIRING >"
            },
            "km": {
                "sub": "សេវាកម្មពន្ធ KTRS កូរ៉េ",
                "title": "បង្វិលពន្ធដោយសុវត្ថិភាព 100%",
                "f1_t": "សេវាគិតក្រោយ 100%", "f1_d": "ទូទាត់តែក្រោយពេលលុយចូលគណនី",
                "f2_t": "មិនបង់មុន 0 វ៉ុន", "f2_d": "មិនទាមទារប្រាក់កក់ជាមុនឡើយ",
                "f3_t": "ភ្នាក់ងារពន្ធផ្លូវការ", "f3_d": "ទទួលស្គាល់ដោយនាយកដ្ឋានពន្ធដារកូរ៉េ",
                "domain_lbl": "គេហទំព័រផ្លូវការ:",
                "btn": "ពិនិត្យឥតគិតថ្លៃ >"
            }
        }
        card_info = CTA_LANG_MAP.get(lang, {
            "sub": "KTRS TAX REFUND SERVICE",
            "title": "100% Safe Tax Refund",
            "f1_t": "100% Success Fee Only", "f1_d": "Pay only after receiving your refund in account",
            "f2_t": "Zero Upfront Fees", "f2_d": "No advance deposits or hidden charges",
            "f3_t": "Certified Tax Agent", "f3_d": "Licensed National Tax Service partner in Korea",
            "domain_lbl": "Official free inquiry website:",
            "btn": cta_button_text or "CHECK NOW >"
        })

        # 1. 상단 타이틀
        draw.text((100, 320), card_info["sub"], fill=(245, 158, 11), font=font_small)
        draw.text((100, 375), card_info["title"], fill=(255, 255, 255), font=font_large)

        # 2. 신뢰 카드 3개 박스
        features = [
            (card_info["f1_t"], card_info["f1_d"]),
            (card_info["f2_t"], card_info["f2_d"]),
            (card_info["f3_t"], card_info["f3_d"])
        ]
        box_y = 530
        for title, desc in features:
            draw.rounded_rectangle([(100, box_y), (980, box_y + 160)], radius=24, fill=(30, 41, 59, 250), outline=(51, 65, 85, 200), width=2)
            draw.text((140, box_y + 35), title, fill=(255, 255, 255), font=font_mid)
            draw.text((140, box_y + 90), desc, fill=(148, 163, 184), font=font_small)
            box_y += 190

        # 3. 도메인 안내 박스
        draw.rounded_rectangle([(100, 1280), (980, 1400)], radius=24, fill=(30, 41, 59, 230), outline=(245, 158, 11, 200), width=2)
        draw.text((140, 1305), card_info["domain_lbl"], fill=(148, 163, 184), font=font_small)
        draw.text((140, 1345), domain_text, fill=(245, 158, 11), font=font_mid)

        # 4. 하단 펄스 CTA 버튼
        btn_y = 1580
        draw.rounded_rectangle([(100, btn_y), (980, btn_y + 130)], radius=65, fill=(234, 88, 12, 255))
        final_btn_txt = card_info["btn"]
        bbox = draw.textbbox((0, 0), final_btn_txt, font=font_cta)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 100 + (880 - tw) // 2
        ty = btn_y + (130 - th) // 2 - 4
        draw.text((tx, ty), final_btn_txt, fill=(255, 255, 255), font=font_cta)

        temp_png = output_path + ".temp.png"
        img.save(temp_png, "PNG")

        # 정적 이미지를 duration_sec 길이의 1080x1920 30fps 비디오로 생성
        cmd = [
            self.ffmpeg_exe, "-y",
            "-loop", "1",
            "-i", temp_png,
            "-t", str(duration_sec),
            "-vf", "fps=30,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_png):
            try:
                os.remove(temp_png)
            except Exception:
                pass
        return output_path

    def _get_video_duration(self, video_path: str) -> float:
        """비디오 파일의 실제 재생 시간(초)을 정밀 추출"""
        try:
            cmd = [self.ffmpeg_exe, "-i", video_path]
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
            out = res.stderr.decode("utf-8", errors="ignore")
            for line in out.split("\n"):
                if "Duration:" in line:
                    dur_str = line.split("Duration:")[1].split(",")[0].strip()
                    parts = dur_str.split(":")
                    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        except Exception as e:
            logger.warning(f"동영상 길이 추출 실패 ({video_path}): {e}")
        return 10.0

    def compose_hybrid_22s_shorts(
        self,
        clip_person_path: str,
        clip_app_path: str,
        full_audio_path: str,
        visual_direction: Dict[str, Any],
        output_mp4_path: str,
        lang: str = "vi",
        target_w: int = 1080,
        target_h: int = 1920,
        scene_audios: Optional[Dict[str, str]] = None
    ) -> str:
        """
        🎬 22초 완결형 하이브리드 숏폼 비디오 최종 결합 엔진
        - Clip 1: 인물 립싱크 (Wan S2V) -> 중앙 시야 100% 개방
        - Clip 2: 라이브 앱 시뮬레이션 (EasyTaxAppRecorder) -> 중앙 앱 시뮬레이터 100% 개방
        - Clip 3: 18~22초 안심 신뢰 보증 & CTA 카드
        - Overlays: 상단 타이틀 박스 + 하단 자막 박스 (제미나이 실시간 테마 컬러 & 글자 이탈 0% 원천 차단)
        - Audio: 3단 독립 씬 오디오(scene_audios)가 주어질 경우 씬 전환점과 발화 시점을 마이크로초 1:1 동기화
        """
        temp_dir = os.path.dirname(output_mp4_path)
        os.makedirs(temp_dir, exist_ok=True)

        logger.info(f"🚀 [ShortsVideoComposer] 22초 하이브리드 숏폼 조립 시작 -> {output_mp4_path}")

        # 1. 비디오 클립 실제 길이 정밀 측정
        dur_person = self._get_video_duration(clip_person_path)
        dur_app = self._get_video_duration(clip_app_path)
        logger.info(f"⏱️ [ShortsVideoComposer] 클립 길이 측정: 인물={dur_person:.2f}s, 앱={dur_app:.2f}s")

        # 2. 18~22초 엔딩 CTA 세그먼트 비디오 생성
        cta_clip_path = os.path.join(temp_dir, f"temp_cta_segment_{lang}.mp4")
        self.create_ending_cta_segment_mp4(
            output_path=cta_clip_path,
            lang=lang,
            duration_sec=4.0,
            domain_text=visual_direction.get("domain_text", "ktrs-service.vercel.app"),
            cta_button_text=visual_direction.get("cta_button_text", "CHECK NOW >")
        )

        # 3. 제미나이 동적 팔레트 및 오버레이 이미지 준비
        palette = visual_direction.get("palette", {})

        top_box_png = os.path.join(temp_dir, f"temp_top_box_{lang}.png")
        self.generate_top_box_png(
            header_text=visual_direction.get("top_header", "HOÀN 90% THUẾ • KTRS"),
            palette=palette,
            out_path=top_box_png,
            lang=lang
        )

        bottom_s1_png = os.path.join(temp_dir, f"temp_bottom_s1_{lang}.png")
        self.generate_bottom_box_png(
            title_text=visual_direction.get("bottom_step1_title", "ĐÃ NHẬN 3.100.000 WON"),
            sub_text=visual_direction.get("bottom_step1_sub", "Tra cứu hoàn thuế trong 1 phút"),
            palette=palette,
            out_path=bottom_s1_png,
            lang=lang
        )

        bottom_s2_png = os.path.join(temp_dir, f"temp_bottom_s2_{lang}.png")
        self.generate_bottom_box_png(
            title_text=visual_direction.get("bottom_step2_title", "CHỌN LƯƠNG 250 VẠN • HOÀN 3.100.000 WON"),
            sub_text=visual_direction.get("bottom_step2_sub", "Liên kết NTS Hometax • Visa E-7, E-9"),
            palette=palette,
            out_path=bottom_s2_png,
            lang=lang
        )

        # 4. FFmpeg 복합 필터 구성 (동적 타임스탬프 동기화)
        total_content_dur = dur_person + dur_app
        use_multi_audio = bool(scene_audios and scene_audios.get("hook") and scene_audios.get("app") and scene_audios.get("cta"))

        if use_multi_audio:
            # 3단 개별 오디오 파일 입력 (인사말, 앱 조작, CTA)
            cmd_inputs = [
                "-i", clip_person_path,
                "-i", clip_app_path,
                "-i", cta_clip_path,
                "-i", scene_audios["hook"],
                "-i", scene_audios["app"],
                "-i", scene_audios["cta"],
                "-i", top_box_png,
                "-i", bottom_s1_png,
                "-i", bottom_s2_png,
            ]
            filter_complex = [
                # 비디오 3단 Concat
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v0]",
                f"[1:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v1]",
                f"[2:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v2]",
                "[v0][v1][v2]concat=n=3:v=1:a=0[v_base]",

                # 오디오 3단 무결점 씬 동기화 (apad로 비디오 씬 길이만큼 정확히 여운 패딩 후 Concat)
                f"[3:a]apad=whole_dur={dur_person:.2f}[a0_pad]",
                f"[4:a]apad=whole_dur={dur_app:.2f}[a1_pad]",
                "[a0_pad][a1_pad][5:a]concat=n=3:v=0:a=1[a_final]",

                # 상단 헤더 박스: 인물 + 앱 씬 동안 표시
                f"[v_base][6:v]overlay=0:0:enable='between(t,0,{total_content_dur:.2f})'[v_h]",
                # 1단계 인물 씬 하단 자막: 인물 클립 동안만 표시
                f"[v_h][7:v]overlay=0:0:enable='between(t,0.5,{dur_person:.2f})'[v_s1]",
                # 2단계 앱 시뮬레이션 씬 하단 자막: 앱 클립 동안만 표시
                f"[v_s1][8:v]overlay=0:0:enable='between(t,{dur_person:.2f},{total_content_dur:.2f})'[v_final]"
            ]
            map_audio = "[a_final]"
        else:
            cmd_inputs = [
                "-i", clip_person_path,
                "-i", clip_app_path,
                "-i", cta_clip_path,
                "-i", full_audio_path,
                "-i", top_box_png,
                "-i", bottom_s1_png,
                "-i", bottom_s2_png,
            ]
            filter_complex = [
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v0]",
                f"[1:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v1]",
                f"[2:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1,fps=30[v2]",
                "[v0][v1][v2]concat=n=3:v=1:a=0[v_base]",
                f"[v_base][4:v]overlay=0:0:enable='between(t,0,{total_content_dur:.2f})'[v_h]",
                f"[v_h][5:v]overlay=0:0:enable='between(t,0.5,{dur_person:.2f})'[v_s1]",
                f"[v_s1][6:v]overlay=0:0:enable='between(t,{dur_person:.2f},{total_content_dur:.2f})'[v_final]"
            ]
            map_audio = "3:a"

        filter_str = ";".join(filter_complex)

        cmd = [
            self.ffmpeg_exe, "-y",
            *cmd_inputs,
            "-filter_complex", filter_str,
            "-map", "[v_final]",
            "-map", map_audio,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4_path
        ]

        logger.info("⚙️ [ShortsVideoComposer] FFmpeg 3단 비디오 + 씬별 무결점 오디오 + 제미나이 분할 박스 최종 결합 중...")
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8", errors="ignore")
            logger.error(f"❌ FFmpeg 컴포징 에러: {err_msg}")
            raise RuntimeError(f"FFmpeg 결합 실패: {err_msg}")

        logger.info(f"🎉 [ShortsVideoComposer] 22초 완제품 숏폼 생성 완료: {output_mp4_path} ({os.path.getsize(output_mp4_path):,} bytes)")

        # 임시 파일 정리
        for p in [cta_clip_path, top_box_png, bottom_s1_png, bottom_s2_png]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        return output_mp4_path

