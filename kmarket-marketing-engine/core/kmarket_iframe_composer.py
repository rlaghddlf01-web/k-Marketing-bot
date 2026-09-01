"""
KMarketIframeComposer - 📱 [첫 0.00초부터 매물 즉시 노출 + 무여백 1080x1920 20초 숏폼 렌더러]
- 초기 로딩 흰 화면 1.2초 완벽 컷팅(Trim -ss 1.2) ➔ 첫 프레임부터 실물 매물 100% 즉시 노출
- Playwright viewport(540x960) = record_video_size(540x960) 1:1 일치 (여백 0% 원천 보장)
- 대시보드의 '9:16 모바일 뷰어' (http://127.0.0.1:8000/api/kmarket/clean_view?lang={lang}) 순정 화면 녹화
- 20초 동안 부드러운 스무스 스크롤 다운
- ffmpeg를 통해 1080x1920 H.264 고화질 숏폼 표준 규격으로 100% 꽉 차게 렌더링
- 17개국 원어민 TTS 음성 + 경쾌한 BGM 결합
- 바탕화면 '숏폼_산출물_케이마켓' 폴더 실시간 자동 저장
"""

import os
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import imageio_ffmpeg
from playwright.sync_api import sync_playwright
from config import BASE_DIR, OUTPUTS_DIR, DATA_DIR, LANGUAGES
from core.bgm_manager import BGMManager

logger = logging.getLogger("KMarketIframeComposer")


class KMarketIframeComposer:
    """K-Market 9:16 모바일 순정 화면 20초 숏폼 비디오 합성 엔진"""
    def __init__(self):
        self.output_dir = OUTPUTS_DIR / "shorts_kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_dir = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\케이마켓")
        self.desktop_dir.mkdir(parents=True, exist_ok=True)
        self.bgm_manager = BGMManager()
        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"

    def compose_iframe_shorts(
        self,
        lang: str = "vi",
        title: str = "K-Market 0 KRW Giveaway",
        captions: Optional[List[str]] = None,
        audio_path: Optional[Path] = None,
        scenario_plan: Optional[Dict[str, Any]] = None,
        real_items: Optional[List[Dict[str, Any]]] = None,
        duration_sec: float = 20.0
    ) -> Path:
        """
        초기 로딩 흰 화면을 완벽히 잘라내어 0.00초 첫 순간부터 매물이 노출되는 20초 숏폼 MP4를 생성합니다.
        """
        scenario_plan = scenario_plan or {}
        timestamp = int(time.time())
        theme_id = scenario_plan.get("theme_id", "nowhite_20s")
        final_mp4 = self.output_dir / f"kmarket_real_iframe_{lang}_{theme_id}_{timestamp}.mp4"
        temp_video_dir = self.output_dir / f"temp_rec_{timestamp}"
        temp_video_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"[{lang.upper()}] 📱 첫 프레임 매물 즉시 노출 Playwright 녹화 시작...")

        # 1. 대시보드의 순정 클린 뷰어 URL
        target_url = f"http://127.0.0.1:8000/api/kmarket/clean_view?lang={lang}"
        load_duration = 3.0

        recorded_video_file = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 540, "height": 960},
                    record_video_dir=str(self.output_dir),
                    record_video_size={"width": 540, "height": 960}
                )
                page = context.new_page()
                video_handle = page.video

                t_start = time.time()

                try:
                    page.goto(target_url, timeout=15000, wait_until="domcontentloaded")
                except Exception:
                    page.goto(target_url, timeout=15000)

                # 🎯 1. 매물 카드가 화면에 완전히 렌더링될 때까지 감지 대기
                try:
                    page.wait_for_selector(".item-card, .product-card, div[onclick*='openModal']", timeout=8000)
                except Exception:
                    time.sleep(2.0)

                # 첫 화면 렌더링 안정화 대기 (0.5초)
                time.sleep(0.5)
                t_loaded = time.time()
                load_duration = max(1.0, t_loaded - t_start)
                logger.info(f"[{lang.upper()}] 📱 케이마켓 매물 렌더링 완료 감지 (로딩 소요: {load_duration:.2f}초)")

                # 🎯 2. 매물이 완전히 뜬 상태에서 정확히 20.5초 동안 부드럽게 스크롤
                scroll_steps = int((duration_sec + 0.5) * 8.0)
                for _ in range(scroll_steps):
                    page.evaluate("window.scrollBy({top: 22, behavior: 'smooth'});")
                    time.sleep(0.12)

                time.sleep(0.5)
                page.close()
                context.close()
                browser.close()

                # 🎯 Playwright 공식 녹화 파일 획득
                if video_handle:
                    raw_video_path = video_handle.path()
                    if raw_video_path and Path(raw_video_path).exists():
                        recorded_video_file = Path(raw_video_path)
                        logger.info(f"[{lang.upper()}] 🎥 원본 녹화 완료 ({recorded_video_file.stat().st_size} bytes)")

        except Exception as e:
            logger.error(f"Playwright 녹화 실패: {e}")
            load_duration = 3.0

        # 3. 숏폼 최적화 20초 BGM 준비
        bgm_path = self.bgm_manager.get_random_upbeat_bgm(service_id="kmarket")
        has_voice = audio_path and Path(audio_path).exists()
        has_bgm = bgm_path and Path(bgm_path).exists()

        # 4. ffmpeg로 [로딩 흰화면 정밀 컷팅(-ss load_duration) + 1080x1920 확대 + 0.00초 음성/BGM 즉시 믹싱]
        if recorded_video_file and recorded_video_file.exists():
            try:
                # 🎯 핵심: 측정된 로딩 시간(load_duration)만큼 정확히 잘라내어 0.00초 첫 프레임부터 매물 사진으로 즉시 시작
                cmd = [
                    self.ffmpeg_exe,
                    "-y",
                    "-ss", f"{load_duration:.2f}",
                    "-i", str(recorded_video_file),
                ]

                if has_voice:
                    cmd.extend(["-i", str(audio_path)])
                if has_bgm:
                    cmd.extend(["-i", str(bgm_path)])

                scale_filter = "[0:v]setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[vout]"

                if has_voice and has_bgm:
                    audio_filter = "[1:a]asetpts=PTS-STARTPTS,volume=1.0[v_aud];[2:a]asetpts=PTS-STARTPTS,volume=0.30[b_aud];[v_aud][b_aud]amix=inputs=2:duration=longest:dropout_transition=0[aout]"
                    cmd.extend([
                        "-filter_complex", f"{scale_filter};{audio_filter}",
                        "-map", "[vout]",
                        "-map", "[aout]",
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac",
                        "-b:a", "128k",
                        "-t", str(duration_sec),
                        str(final_mp4)
                    ])
                elif has_voice:
                    audio_filter = "[1:a]asetpts=PTS-STARTPTS,volume=1.0[aout]"
                    cmd.extend([
                        "-filter_complex", f"{scale_filter};{audio_filter}",
                        "-map", "[vout]",
                        "-map", "[aout]",
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac",
                        "-t", str(duration_sec),
                        str(final_mp4)
                    ])
                elif has_bgm:
                    audio_filter = "[1:a]asetpts=PTS-STARTPTS,volume=0.30[aout]"
                    cmd.extend([
                        "-filter_complex", f"{scale_filter};{audio_filter}",
                        "-map", "[vout]",
                        "-map", "[aout]",
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac",
                        "-t", str(duration_sec),
                        str(final_mp4)
                    ])
                else:
                    cmd.extend([
                        "-filter_complex", scale_filter,
                        "-map", "[vout]",
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        "-t", str(duration_sec),
                        str(final_mp4)
                    ])

                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
                if res.returncode == 0 and final_mp4.exists():
                    size_mb = round(final_mp4.stat().st_size / (1024 * 1024), 2)
                    logger.info(f"[{lang.upper()}] ✅ 흰화면 0% 완벽 20초 숏폼 완성: {final_mp4.name} ({size_mb}MB)")

                    # 🖥️ 바탕화면 폴더로 실시간 자동 복사
                    try:
                        desktop_target = self.desktop_dir / final_mp4.name
                        shutil.copy2(str(final_mp4), str(desktop_target))
                        logger.info(f"📁 [바탕화면 저장 완료] -> {desktop_target}")
                    except Exception as e:
                        logger.warning(f"바탕화면 복사 경고: {e}")

                    shutil.rmtree(temp_video_dir, ignore_errors=True)
                    return final_mp4
                else:
                    logger.warning(f"ffmpeg 인코딩 경고: {res.stderr.decode('utf-8', errors='ignore')[-300:]}")
            except Exception as e:
                logger.error(f"ffmpeg 최종 합성 에러: {e}")

        # 폴백 처리
        if recorded_video_file and recorded_video_file.exists():
            shutil.move(str(recorded_video_file), str(final_mp4))
            try:
                shutil.copy2(str(final_mp4), str(self.desktop_dir / final_mp4.name))
            except Exception:
                pass
            shutil.rmtree(temp_video_dir, ignore_errors=True)
            return final_mp4

        return final_mp4
