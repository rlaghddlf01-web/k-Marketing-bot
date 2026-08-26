"""
VideoComposer — 이미지 프레임 + TTS 음성 + BGM → 최종 .mp4 숏폼 영상 합성
  ✅ imageio-ffmpeg (내장 FFmpeg) 사용, 회원가입/API키 불필요
  ✅ 음성 위에 BGM을 낮은 볼륨으로 믹싱
  ✅ 이미지를 영상 길이만큼 정지 화면으로 루프
"""

import logging
import os
import wave
import struct
from pathlib import Path
from typing import Optional

logger = logging.getLogger("VideoComposer")


class VideoComposer:
    """
    [무인 자동화 3] 숏폼 영상 최종 합성기
    - 입력:  ① 1080x1920 정지 이미지(.png)  ② TTS 음성(.mp3)  ③ BGM(.wav)
    - 출력: 최종 세로형 숏폼 영상(.mp4)
    """

    def __init__(self, bgm_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        from config import OUTPUTS_DIR, BASE_DIR
        self.bgm_dir = bgm_dir or (BASE_DIR / "outputs" / "bgm")
        self.output_dir = output_dir or (OUTPUTS_DIR / "shorts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.bgm_dir.mkdir(parents=True, exist_ok=True)

        # imageio-ffmpeg에서 내장 ffmpeg 경로 확인
        try:
            import imageio_ffmpeg
            self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            logger.info("FFmpeg 내장 경로 확인: {}".format(self.ffmpeg_path))
        except Exception as e:
            self.ffmpeg_path = "ffmpeg"
            logger.warning("imageio-ffmpeg 로드 실패, 시스템 ffmpeg 사용 시도: {}".format(e))

    # ─────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────
    def compose(
        self,
        frame_path: Path,
        audio_path: Optional[Path],
        service_id: str = "kmarket",
        lang: str = "en",
        bgm_volume: float = 0.08,
    ) -> Optional[Path]:
        """
        이미지 + 음성 + BGM을 합성하여 .mp4 파일 생성

        Args:
            frame_path:  1080x1920 PNG 이미지 경로
            audio_path:  TTS 음성 mp3 경로 (None이면 BGM만 사용)
            service_id:  'kmarket' 또는 'easytax'
            lang:        언어 코드 ('vi', 'zh' 등)
            bgm_volume:  BGM 볼륨 비율 (0.0 ~ 1.0, 기본 0.08 = 목소리가 잘 들리는 낮은 볼륨)

        Returns:
            생성된 .mp4 경로 or None
        """
        try:
            # 1. 음성 길이 측정 → 영상 길이 결정
            duration = self._get_audio_duration_sec(audio_path)
            if duration < 5:
                duration = 30.0  # 음성 없으면 30초 기본

            # 2. BGM 파일 선택
            bgm_path = self._select_bgm(service_id)

            # 3. 최종 mp4 경로
            output_path = self.output_dir / "shorts_{}_{}_.mp4".format(service_id, lang)

            # 4. FFmpeg 명령어 조립 및 실행
            success = self._run_ffmpeg(
                frame_path=frame_path,
                audio_path=audio_path,
                bgm_path=bgm_path,
                output_path=output_path,
                duration=duration,
                bgm_volume=bgm_volume,
            )

            if success:
                size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2)
                logger.info("[{}/{}] 숏폼 영상 합성 완료: {} ({}MB)".format(
                    service_id, lang, output_path.name, size_mb
                ))
                return output_path
            else:
                logger.error("[{}/{}] FFmpeg 합성 실패".format(service_id, lang))
                return None

        except Exception as e:
            logger.error("[VideoComposer] compose 오류: {}".format(e))
            return None

    # ─────────────────────────────────────────────────────────
    # 내부 헬퍼
    # ─────────────────────────────────────────────────────────
    def _get_audio_duration_sec(self, audio_path: Optional[Path]) -> float:
        """mp3 파일 길이(초) 측정 — mutagen 없이 파일 크기로 추정"""
        if not audio_path or not Path(audio_path).exists():
            return 30.0
        try:
            # mp3 평균 비트레이트 128kbps 가정 → 파일크기(bytes) / (128000/8)
            size_bytes = os.path.getsize(audio_path)
            estimated = size_bytes / 16000.0
            return max(10.0, min(estimated, 120.0))
        except Exception:
            return 30.0

    def _select_bgm(self, service_id: str) -> Optional[Path]:
        """서비스별 BGM 파일 선택"""
        bgm_name = "bgm_kmarket.wav" if service_id == "kmarket" else "bgm_easytax.wav"
        bgm_path = self.bgm_dir / bgm_name
        if bgm_path.exists():
            return bgm_path
        # 폴백: bgm 폴더에 아무 wav/mp3나 있으면 사용
        for ext in ["*.wav", "*.mp3"]:
            candidates = list(self.bgm_dir.glob(ext))
            if candidates:
                return candidates[0]
        return None

    def _run_ffmpeg(
        self,
        frame_path: Path,
        audio_path: Optional[Path],
        bgm_path: Optional[Path],
        output_path: Path,
        duration: float,
        bgm_volume: float,
    ) -> bool:
        """
        FFmpeg 명령어 구성:
          - 입력1: 정지 이미지 (loop)
          - 입력2: TTS 음성
          - 입력3: BGM (낮은 볼륨 믹싱)
          - 출력: H.264 + AAC .mp4
        """
        import subprocess

        # ── 기본 필터 구성 ──
        inputs = [
            "-loop", "1",
            "-framerate", "1",
            "-i", str(frame_path),
        ]

        if audio_path and Path(audio_path).exists():
            inputs += ["-i", str(audio_path)]

        if bgm_path and bgm_path.exists():
            inputs += ["-i", str(bgm_path)]

        # ── 오디오 필터 (음성 + BGM 믹싱) ──
        audio_filter = ""
        audio_map = []

        has_voice = audio_path and Path(audio_path).exists()
        has_bgm = bgm_path and bgm_path.exists()

        if has_voice and has_bgm:
            # 음성(입력1) + BGM(입력2) 믹싱: BGM 볼륨을 bgm_volume으로 낮춤
            voice_idx = 1
            bgm_idx = 2
            audio_filter = "[{}:a]volume=1.0[voice];[{}:a]volume={}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]".format(
                voice_idx, bgm_idx, bgm_volume
            )
            audio_map = ["-filter_complex", audio_filter, "-map", "0:v", "-map", "[aout]"]
        elif has_voice:
            audio_map = ["-map", "0:v", "-map", "1:a"]
        elif has_bgm:
            bgm_idx = 1
            audio_map = ["-map", "0:v", "-map", "{}:a".format(bgm_idx)]
        else:
            audio_map = ["-map", "0:v", "-an"]

        # ── 출력 설정 ──
        output_opts = [
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-t", str(duration),
            "-movflags", "+faststart",
            "-y",
            str(output_path),
        ]

        cmd = [self.ffmpeg_path] + inputs + audio_map + output_opts

        logger.debug("FFmpeg 명령어: {}".format(" ".join(cmd)))

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )
            if result.returncode == 0:
                return True
            else:
                err = result.stderr.decode("utf-8", errors="ignore")[-500:]
                logger.error("FFmpeg 오류: {}".format(err))
                return False
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg 타임아웃 (120초 초과)")
            return False
        except Exception as e:
            logger.error("FFmpeg 실행 예외: {}".format(e))
            return False
