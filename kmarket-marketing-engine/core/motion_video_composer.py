"""
MotionVideoComposer - 실제 움직이는 배경 비디오 + 4개 씬(Scene) 다이내믹 오버레이 + TTS + BGM 풀HD 숏폼 영상 합성기
- 씬 1 (0~5초): 충격 훅 타이틀 카드
- 씬 2 (5~15초): 1인칭 스마트폰 환급액 카운팅 UI
- 씬 3 (15~24초): 조특법 30조 & 국세청 공인 뱃지
- 씬 4 (24~30초): 대형 원클릭 CTA 배너
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, BASE_DIR

logger = logging.getLogger("MotionVideoComposer")

# Windows 폰트
FONT_BOLD_PATH = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REGULAR_PATH = r"C:\Windows\Fonts\malgun.ttf"

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


class MotionVideoComposer:
    """
    🎬 씬(Scene) 전환 기반의 진짜 움직이는 숏폼 비디오 합성기
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.output_dir / "temp_scenes"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            import imageio_ffmpeg
            self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_path = "ffmpeg"

    def _render_scene_overlay(
        self,
        scene_idx: int,
        lang: str,
        service_id: str,
        title: str,
        captions: List[str],
        estimated_krw: int = 3840000
    ) -> Path:
        """투명 배경 위에 특정 씬의 다이내믹 UI/자막 오버레이 렌더링 (1080x1920 RGBA)"""
        W, H = 1080, 1920
        # 투명 배경 생성 (RGBA)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        f_big = get_font(46, bold=True)
        f_mid = get_font(34, bold=True)
        f_sub = get_font(28, bold=False)
        f_badge = get_font(26, bold=True)
        f_cta = get_font(40, bold=True)

        # ── 상단 공통 브랜딩 바 (반투명 다크) ──
        draw.rounded_rectangle([(60, 60), (1020, 150)], radius=20, fill=(15, 23, 42, 220), outline=(59, 130, 246, 255), width=2)
        brand_name = "🛒 K-MARKET 외국인 직거래" if service_id == "kmarket" else "🏛️ 국세청 공식 외국인 소득세 환급 (EasyTax)"
        draw.text((90, 85), brand_name, fill=(255, 255, 255), font=f_badge)
        draw.text((860, 85), f"[{lang.upper()}]", fill=(251, 191, 36), font=f_badge)

        # ── 씬별 차별화 오버레이 ──
        if scene_idx == 1:
            # 💥 씬 1: 강력한 훅 타이틀 (대형 충격 카드)
            draw.rounded_rectangle([(60, 500), (1020, 1100)], radius=32, fill=(15, 23, 42, 235), outline=(239, 68, 68, 255), width=4)
            draw.text((100, 560), "🔥 긴급 공지 / URGENT", fill=(239, 68, 68), font=f_mid)
            draw.text((100, 640), title[:36], fill=(255, 255, 255), font=f_big)
            if len(title) > 36:
                draw.text((100, 720), title[36:72], fill=(255, 255, 255), font=f_big)
            draw.text((100, 840), "⚡ 당신이 몰랐던 대한민국 공식 합법 혜택", fill=(251, 191, 36), font=f_sub)
            draw.text((100, 920), "• 외국인 근로자 & 유학생 필수 확인", fill=(226, 232, 240), font=f_sub)

        elif scene_idx == 2:
            # 📱 씬 2: 스마트폰 환급 계산 카운터 UI
            draw.rounded_rectangle([(80, 420), (1000, 1280)], radius=36, fill=(15, 23, 42, 240), outline=(16, 185, 129, 255), width=4)
            # 모바일 뱅킹 입금 알림
            draw.rounded_rectangle([(120, 460), (960, 620)], radius=20, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
            draw.text((150, 485), "💬 국세청 / 시중은행 환급금 입금", fill=(52, 211, 153), font=f_badge)
            draw.text((150, 530), f"[입금완료] ₩{estimated_krw:,} 원", fill=(255, 255, 255), font=f_big)

            # 세부 내역
            draw.text((130, 660), "📋 5개년 누락 과오납 세액 산출:", fill=(148, 163, 184), font=f_mid)
            details = [
                ("• E-9/H-2 조특법 30조", "최대 90% 소득세 감면"),
                ("• D-2 알바 3.3% 환급", "기본공제 범위 전액 환급"),
                ("• 5개년 소급 경정청구", "2020~2025년 누락분 수령")
            ]
            for idx, (lbl, val) in enumerate(details):
                item_y = 730 + (idx * 110)
                draw.rounded_rectangle([(120, item_y), (960, item_y + 90)], radius=16, fill=(20, 30, 50, 255))
                draw.text((140, item_y + 25), lbl, fill=(251, 191, 36), font=f_sub)
                draw.text((540, item_y + 25), val, fill=(241, 245, 249), font=f_sub)

        elif scene_idx == 3:
            # 🛡️ 씬 3: 국세청 공인 뱃지 및 신뢰 증거
            draw.rounded_rectangle([(80, 520), (1000, 1180)], radius=32, fill=(15, 23, 42, 240), outline=(59, 130, 246, 255), width=3)
            draw.text((120, 570), "🏛️ 대한민국 국세청(NTS) 공식 법적 보호", fill=(147, 197, 253), font=f_mid)
            draw.text((120, 650), "• 100% 무료 AI 모의계산 (선입금 0원)", fill=(255, 255, 255), font=f_sub)
            draw.text((120, 740), "• 공인 세무법인 1:1 전담 안전 전자신고", fill=(255, 255, 255), font=f_sub)
            draw.text((120, 830), "• 외국인등록증 사진 1장으로 3분 신청", fill=(251, 191, 36), font=f_sub)
            draw.text((120, 920), "• 17개국 모국어 실시간 상담 지원", fill=(226, 232, 240), font=f_sub)

        else:
            # 👉 씬 4: 대형 원클릭 CTA 배너
            draw.rounded_rectangle([(60, 600), (1020, 1200)], radius=36, fill=(245, 158, 11, 250), outline=(255, 255, 255, 255), width=4)
            draw.text((120, 680), "👉 지금 바로 확인하세요!", fill=(15, 23, 42), font=f_big)
            draw.text((120, 780), "프로필 링크 클릭 시", fill=(15, 23, 42), font=f_mid)
            draw.text((120, 850), "3분 만에 무료 환급액 조회 완료!", fill=(15, 23, 42), font=f_cta)
            draw.text((120, 970), "⚡ 선착순 100% 무료 조회 지원 중", fill=(71, 85, 105), font=f_sub)

        # ── 하단 공통 면책 ──
        draw.text((70, 1800), "* 국세기본법 제45조의2에 따른 합법 세무대리 절차로 진행됩니다.", fill=(148, 163, 184), font=get_font(18, False))

        overlay_path = self.temp_dir / f"overlay_{service_id}_{lang}_s{scene_idx}.png"
        img.save(overlay_path)
        return overlay_path

    def compose_motion_shorts(
        self,
        bg_video_path: Optional[Path],
        audio_path: Optional[Path],
        service_id: str,
        lang: str,
        title: str,
        captions: List[str]
    ) -> Optional[Path]:
        """
        움직이는 배경 비디오 + 4개 씬 오버레이 + TTS 음성 + BGM -> 최종 H.264 MP4 숏폼 렌더링
        """
        output_mp4 = self.output_dir / f"shorts_{service_id}_{lang}_.mp4"

        # 1. 4개 씬 오버레이 이미지 렌더링
        s1 = self._render_scene_overlay(1, lang, service_id, title, captions)
        s2 = self._render_scene_overlay(2, lang, service_id, title, captions)
        s3 = self._render_scene_overlay(3, lang, service_id, title, captions)
        s4 = self._render_scene_overlay(4, lang, service_id, title, captions)

        # 2. 오디오 길이 확인
        audio_duration = 30.0
        if audio_path and audio_path.exists():
            try:
                audio_duration = max(10.0, audio_path.stat().st_size / 16000.0)
            except Exception:
                pass

        # 씬 전환 타이밍 분할
        t1 = round(audio_duration * 0.22, 1)  # 0~22% (0~6.6초)
        t2 = round(audio_duration * 0.55, 1)  # 22~55% (6.6~16.5초)
        t3 = round(audio_duration * 0.80, 1)  # 55~80% (16.5~24초)

        # BGM 경로
        bgm_name = "bgm_kmarket.wav" if service_id == "kmarket" else "bgm_easytax.wav"
        bgm_path = BASE_DIR / "outputs" / "bgm" / bgm_name

        # 3. FFmpeg 복합 필터 구성
        # 비디오 입력 (Pexels 비디오가 있으면 loop, 없으면 컬러 배경)
        if bg_video_path and bg_video_path.exists():
            video_input = ["-stream_loop", "-1", "-i", str(bg_video_path)]
        else:
            video_input = ["-f", "lavfi", "-i", f"color=c=0x0f172a:s=1080x1920:d={audio_duration}"]

        # 4개 오버레이 이미지 입력
        overlay_inputs = [
            "-i", str(s1),
            "-i", str(s2),
            "-i", str(s3),
            "-i", str(s4)
        ]

        audio_inputs = []
        if audio_path and audio_path.exists():
            audio_inputs += ["-i", str(audio_path)]
        if bgm_path.exists():
            audio_inputs += ["-i", str(bgm_path)]

        # 비디오 씬 전환 필터 (0->s1, t1->s2, t2->s3, t3->s4)
        v_filter = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
            f"[bg][1:v]overlay=0:0:enable='between(t,0,{t1})'[v1];"
            f"[v1][2:v]overlay=0:0:enable='between(t,{t1},{t2})'[v2];"
            f"[v2][3:v]overlay=0:0:enable='between(t,{t2},{t3})'[v3];"
            f"[v3][4:v]overlay=0:0:enable='gte(t,{t3})'[vout]"
        )

        # 오디오 믹싱 필터 (TTS 음성 1.0 + BGM 0.08)
        a_filter = ""
        has_voice = audio_path and audio_path.exists()
        has_bgm = bgm_path.exists()

        if has_voice and has_bgm:
            a_filter = "[5:a]volume=1.0[v_aud];[6:a]volume=0.08[b_aud];[v_aud][b_aud]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            maps = ["-filter_complex", f"{v_filter};{a_filter}", "-map", "[vout]", "-map", "[aout]"]
        elif has_voice:
            maps = ["-filter_complex", v_filter, "-map", "[vout]", "-map", "5:a"]
        else:
            maps = ["-filter_complex", v_filter, "-map", "[vout]"]

        cmd = [
            self.ffmpeg_path,
            "-y"
        ] + video_input + overlay_inputs + audio_inputs + maps + [
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-t", str(audio_duration),
            "-movflags", "+faststart",
            str(output_mp4)
        ]

        logger.info(f"FFmpeg 모션 비디오 렌더링 시작 ({service_id}/{lang})...")
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
            if res.returncode == 0 and output_mp4.exists():
                size_mb = round(output_mp4.stat().st_size / (1024 * 1024), 2)
                logger.info(f"✅ 진짜 움직이는 씬 전환 숏폼 영상 합성 완료: {output_mp4.name} ({size_mb}MB)")
                return output_mp4
            else:
                err = res.stderr.decode("utf-8", errors="ignore")[-400:]
                logger.error(f"FFmpeg 모션 렌더링 실패: {err}")
        except Exception as e:
            logger.error(f"모션 렌더링 예외: {e}")

        return None
