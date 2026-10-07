# -*- coding: utf-8 -*-
"""
CardnewsToReelsConverter - 🎬 [카드뉴스 5장 PNG → 릴스/숏폼 MP4 슬라이드쇼 자동 변환 엔진]
========================================================================================
- 역할:
  1. 카드뉴스 5장 PNG 슬라이드를 1080x1920 세로 릴스/숏폼용 MP4 슬라이드쇼 영상으로 변환
  2. 각 슬라이드 3.5초 + 크로스페이드 전환 0.5초 = 총 약 15.5초 (릴스/숏폼 최적 체류 시간)
  3. FFmpeg(imageio_ffmpeg) 기반 안정적 렌더링 + Ken Burns 줌(6%) + 크로스페이드(xfade)
  4. 신나는 로열티프리 BGM(기본: bgm_03_carefree.mp3 우쿨렐레) 자동 믹싱 & 엔딩 페이드아웃
  5. 3개 브랜드(Aura, Insurance, Stock) 범용 사용 가능한 독립 레고 블록
- 원칙: Rule 1 (앱별 완전 독립 모듈화), Rule 5 (눈가림 금지, FFmpeg 원천 설계)
"""

import os
import sys
import glob
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_EXE = "ffmpeg"

logger = logging.getLogger("CardnewsToReelsConverter")


class CardnewsToReelsConverter:
    """🎬 카드뉴스 5장 PNG → 릴스/숏폼 MP4 슬라이드쇼 변환 엔진"""

    # 9:16 세로 릴스 최적 규격
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    # 슬라이드당 체류 시간 (초)
    SLIDE_DURATION = 3.5

    # 크로스페이드 전환 시간 (초)
    FADE_DURATION = 0.5

    # Ken Burns 줌 비율 (1.0 = 줌 없음, 1.06 = 6% 줌)
    ZOOM_SCALE = 1.06

    # 출력 영상 프레임레이트
    FPS = 30

    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg = ffmpeg_path or FFMPEG_EXE

    def resolve_default_bgm(self, brand: str = "aura") -> Optional[str]:
        """기본 BGM 경로 탐색 (1순위: bgm_03_carefree.mp3, 2순위: 기타 mp3)"""
        current_file = Path(__file__).resolve()
        brand_bgm_dir = current_file.parent.parent / "brands" / brand / "assets" / "bgm"
        if not brand_bgm_dir.exists():
            return None

        # 💖 Aura 데이팅: 대표님 지정 03번 Carefree 100% 고정
        if "aura" in brand.lower():
            pick3 = brand_bgm_dir / "bgm_03_carefree.mp3"
            if pick3.exists() and pick3.stat().st_size > 50000:
                return str(pick3)

        # 🛡️ 타 브랜드: BGM 풀에서 무작위 선택
        mp3s = sorted(glob.glob(str(brand_bgm_dir / "*.mp3")))
        if mp3s:
            import random
            return random.choice(mp3s)
        return None

    def convert(
        self,
        slide_paths: List[str],
        output_path: str,
        slide_duration: Optional[float] = None,
        fade_duration: Optional[float] = None,
        zoom_enabled: bool = True,
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.22,
        brand: str = "aura"
    ) -> Dict[str, Any]:
        """
        카드뉴스 슬라이드 이미지들을 릴스/숏폼 MP4 영상으로 변환

        Args:
            slide_paths: 슬라이드 PNG/JPG 파일 경로 리스트 (2~10장)
            output_path: 출력 MP4 파일 경로
            slide_duration: 슬라이드당 체류 시간(초), 기본 3.5초
            fade_duration: 페이드 전환 시간(초), 기본 0.5초
            zoom_enabled: Ken Burns 줌 효과 활성화 여부
            bgm_path: 배경음악 MP3/WAV 파일 경로 (없을 시 bgm_03_carefree.mp3 자동 탐색)
            bgm_volume: BGM 볼륨 (0.0~1.0), 기본 0.22
            brand: 브랜드명 (기본 "aura")
        Returns:
            {"status": "success"/"error", "output": output_path, ...}
        """
        dur = slide_duration or self.SLIDE_DURATION
        fade = fade_duration or self.FADE_DURATION

        # 입력 검증
        valid_slides = [p for p in slide_paths if os.path.exists(p)]
        if len(valid_slides) < 2:
            return {"status": "error", "message": f"유효한 슬라이드 {len(valid_slides)}장 (최소 2장 필요)"}

        n = len(valid_slides)
        total_duration = round((dur - fade) * (n - 1) + dur, 1)

        # BGM 경로 미지정 시 기본 3번 Carefree 자동 해석
        if not bgm_path or not os.path.exists(bgm_path):
            bgm_path = self.resolve_default_bgm(brand)

        # 출력 디렉터리 확보
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        try:
            # FFmpeg 복합 필터 구성
            filter_complex = self._build_filter_complex(n, dur, fade, zoom_enabled, bgm_path, bgm_volume, total_duration)
            cmd = self._build_ffmpeg_command(valid_slides, output_path, filter_complex, dur, bgm_path, total_duration)

            logger.info(f"🎬 [CardnewsToReels] {n}장 슬라이드 → 릴스 MP4 변환 시작...")
            logger.info(f"   📐 규격: {self.TARGET_WIDTH}x{self.TARGET_HEIGHT} | ⏱️ 총길이: {total_duration}초 | 🎵 BGM: {os.path.basename(bgm_path) if bgm_path else '없음'}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode != 0:
                logger.error(f"❌ FFmpeg 에러:\n{result.stderr[-600:]}")
                return {"status": "error", "message": f"FFmpeg 에러 (코드 {result.returncode})", "stderr": result.stderr[-600:]}

            if os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ [CardnewsToReels] 릴스 MP4 변환 성공! ({file_size:,} bytes, {file_size/1024/1024:.2f} MB)")
                return {
                    "status": "success",
                    "output": output_path,
                    "slides_count": n,
                    "duration_sec": total_duration,
                    "file_size": file_size,
                    "resolution": f"{self.TARGET_WIDTH}x{self.TARGET_HEIGHT}",
                    "bgm": os.path.basename(bgm_path) if bgm_path else None
                }
            else:
                return {"status": "error", "message": "출력 파일 생성 실패 또는 크기 부족"}

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "FFmpeg 렌더링 타임아웃 (180초 초과)"}
        except Exception as e:
            logger.error(f"❌ [CardnewsToReels] 변환 예외: {e}")
            return {"status": "error", "message": str(e)}

    def _build_filter_complex(
        self,
        n: int,
        dur: float,
        fade: float,
        zoom: bool,
        bgm_path: Optional[str],
        bgm_volume: float,
        total_duration: float
    ) -> str:
        """FFmpeg 복합 필터 그래프 생성 (스케일 + Ken Burns + 크로스페이드 + BGM)"""
        filters = []
        d_frames = int(dur * self.FPS)

        # 1단계: 각 입력 이미지 처리
        for i in range(n):
            scale_pad = (
                f"[{i}:v]scale={self.TARGET_WIDTH}:{self.TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={self.TARGET_WIDTH}:{self.TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1"
            )

            if zoom:
                zs = self.ZOOM_SCALE
                if i % 2 == 0:
                    # 짝수 슬라이드: 줌인 (1.0 → 1.06)
                    zp = f",zoompan=z='min(zoom+0.0006,{zs})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d_frames}:s={self.TARGET_WIDTH}x{self.TARGET_HEIGHT}:fps={self.FPS}"
                else:
                    # 홀수 슬라이드: 줌아웃 (1.06 → 1.0)
                    zp = f",zoompan=z='if(lte(zoom,1.0),{zs},max(1.001,zoom-0.0006))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d_frames}:s={self.TARGET_WIDTH}x{self.TARGET_HEIGHT}:fps={self.FPS}"
                scale_pad += zp

            # constant framerate 보장: setpts 후 fps 필터 적용 (xfade 필수 요구사항)
            scale_pad += f",setpts=PTS-STARTPTS,fps={self.FPS}[v{i}]"
            filters.append(scale_pad)

        # 2단계: 크로스페이드 체인 연결
        if n == 1:
            filters.append(f"[v0]null[vout]")
        else:
            filters.append(
                f"[v0][v1]xfade=transition=fade:duration={fade}:offset={dur - fade}[vf0]"
            )
            for i in range(2, n):
                prev = f"vf{i - 2}"
                cur_offset = round((dur - fade) * i, 2)
                out_label = f"vf{i - 1}" if i < n - 1 else "vout"
                filters.append(
                    f"[{prev}][v{i}]xfade=transition=fade:duration={fade}:offset={cur_offset}[{out_label}]"
                )

            if n == 2:
                filters.append(f"[vf0]null[vout]")

        # 3단계: BGM 오디오 믹싱 (정확한 재생시간으로 자르고 엔딩 2초 페이드아웃)
        if bgm_path and os.path.exists(bgm_path):
            audio_idx = n
            fadeout_st = max(0.0, total_duration - 2.0)
            filters.append(
                f"[{audio_idx}:a]volume={bgm_volume},afade=t=out:st={fadeout_st}:d=2,atrim=0:{total_duration},asetpts=PTS-STARTPTS[aout]"
            )

        return ";\n".join(filters)

    def _build_ffmpeg_command(
        self,
        slide_paths: List[str],
        output_path: str,
        filter_complex: str,
        dur: float,
        bgm_path: Optional[str],
        total_duration: float
    ) -> List[str]:
        """FFmpeg 명령어 배열 구성"""
        cmd = [self.ffmpeg, "-y"]

        # 입력 이미지들
        for p in slide_paths:
            cmd.extend(["-loop", "1", "-t", str(dur), "-i", p])

        # BGM 입력
        has_bgm = bool(bgm_path and os.path.exists(bgm_path))
        if has_bgm:
            cmd.extend(["-i", bgm_path])

        # 필터 복합 그래프
        cmd.extend(["-filter_complex", filter_complex])

        if has_bgm:
            cmd.extend(["-map", "[vout]", "-map", "[aout]"])
        else:
            cmd.extend(["-map", "[vout]"])

        # 비디오/오디오 인코딩 옵션 (15.5초 정확한 컷팅 + 고화질 H.264)
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", str(self.FPS),
            "-t", str(total_duration)
        ])

        if has_bgm:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        cmd.extend(["-movflags", "+faststart", output_path])
        return cmd


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    brand_dir = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura")
    slides = sorted(glob.glob(str(brand_dir / "slide_*.png")))
    if len(slides) >= 2:
        converter = CardnewsToReelsConverter()
        out = str(brand_dir / "test_reels_output.mp4")
        result = converter.convert(slides, out, brand="aura")
        print(f"결과: {result}")
    else:
        print("슬라이드 이미지 파일 없음")
