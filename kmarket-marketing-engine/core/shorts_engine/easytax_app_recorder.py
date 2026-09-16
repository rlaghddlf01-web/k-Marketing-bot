# -*- coding: utf-8 -*-
"""
EasyTaxAppRecorder - 📱 [EasyTax 웹앱 실시간 시뮬레이션 고화질 8초 녹화 모듈]
- Playwright 헤드리스 브라우저 기반
- 타깃 URL: https://ktrs-service.vercel.app/estimate?simulation=true&persona={lang}&lang={lang}
- step === 0 자동 인터랙션 (슬라이더 이동, 월급 250만원 클릭, 310만원 환급액 산출)
- 1080x1920 세로 9:16 최적화 고화질 MP4 트랜스코딩
"""

import os
import time
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

logger = logging.getLogger("EasyTaxAppRecorder")


class EasyTaxAppRecorder:
    """EasyTax 실시간 웹앱 시뮬레이션 레코더"""

    BASE_URL = "https://ktrs-service.vercel.app/estimate"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        logger.info("📱 [EasyTaxAppRecorder] 초기화 완료")

    def record_simulation_clip(
        self,
        lang: str = "vi",
        duration_sec: float = 8.0,
        output_mp4_path: str = "app_simulation.mp4",
        persona: Optional[str] = None
    ) -> str:
        """
        웹앱 시뮬레이션을 녹화하여 지정된 8초 MP4 파일로 저장
        1) 메인 홈 화면: 모국어 헤드라인부터 부드러운 세로 스크롤 (NTS 연동, 비자, 24억 실적)
        2) 환급 0단계 화면: 슬라이더 조작 ➡️ 월급 선택 ➡️ 310만원 환급액 도출
        - 흰 스플래시 로딩 화면 100% 제거
        - 불필요한 플로팅 팁 팝업 및 챗봇 100% 걷어냄
        - 가로폭 100% 꽉 채운 1080x1920 세로 풀HD 출력
        """
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        target_persona = persona or lang
        home_url = f"https://ktrs-service.vercel.app/?lang={lang}"
        estimate_url = f"{self.BASE_URL}?simulation=true&persona={target_persona}&lang={lang}"
        logger.info(f"🌐 [AppRecorder] 녹화 시작: 메인({home_url}) ➡️ 0단계({estimate_url})")

        clean_css = """
            body, html { width: 100% !important; max-width: 100% !important; margin: 0 !important; overflow-x: hidden !important; }
            main, div { max-width: 100% !important; }
            /* 불필요한 하단 팁 팝업, 챗봇 플로팅 바, 안내창 완벽 제거 */
            [class*="bottom-4"], [class*="bottom-2"], [class*="bottom-0"], [role="dialog"], [class*="popup"], [class*="toast"] {
                display: none !important;
            }
        """

        scroll_js = """
            () => {
                const startY = window.scrollY;
                const diff = 750;
                const duration = 2200;
                const startTime = performance.now();
                return new Promise(resolve => {
                    function step(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
                        window.scrollTo(0, startY + diff * ease);
                        if (progress < 1) {
                            requestAnimationFrame(step);
                        } else {
                            resolve();
                        }
                    }
                    requestAnimationFrame(step);
                });
            }
        """

        # 8개국 홈 화면 사전 무결점 프리셋 확인 (흰색 스플래시 화면 100% 제거)
        preset_home = Path(__file__).resolve().parent / "presets" / f"easytax_home_{lang}.mp4"
        use_preset_home = preset_home.exists() and preset_home.stat().st_size > 0
        if use_preset_home:
            logger.info(f"✨ [AppRecorder] 8개국 무결점 홈 프리셋 감지 -> 즉시 로드 (흰색 스플래시 0초 보장): {preset_home.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_p = Path(temp_dir)
            dir_home = temp_p / "rec_home"
            dir_est = temp_p / "rec_est"
            dir_home.mkdir(parents=True, exist_ok=True)
            dir_est.mkdir(parents=True, exist_ok=True)

            logger.info("🚀 [AppRecorder] Playwright Chromium 실행...")
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
                )

                # ── Part 1: 프리셋이 없을 때만 실시간 홈 화면 녹화 ──
                if not use_preset_home:
                    ctx_home = browser.new_context(
                        viewport={"width": 430, "height": 932},
                        device_scale_factor=2.5,
                        is_mobile=True,
                        has_touch=True,
                        record_video_dir=str(dir_home),
                        record_video_size={"width": 430, "height": 932}
                    )
                    p_home = ctx_home.new_page()
                    p_home.goto(home_url, wait_until="domcontentloaded")
                    p_home.add_style_tag(content=clean_css)
                    p_home.wait_for_timeout(1400) # 스플래시 로딩 통과 후 본문 안정화 대기
                    p_home.evaluate(scroll_js)    # 아래로 부드럽게 스크롤
                    p_home.wait_for_timeout(1000)
                    ctx_home.close()

                # ── Part 2: 환급 0단계 라이브 시뮬레이션 녹화 (약 4초) ──
                ctx_est = browser.new_context(
                    viewport={"width": 430, "height": 932},
                    device_scale_factor=2.5,
                    is_mobile=True,
                    has_touch=True,
                    record_video_dir=str(dir_est),
                    record_video_size={"width": 430, "height": 932}
                )
                p_est = ctx_est.new_page()
                p_est.goto(estimate_url, wait_until="domcontentloaded")
                p_est.add_style_tag(content=clean_css)
                p_est.wait_for_timeout(2500) # 슬라이더 조작 ➡️ 250만원 클릭 대기
                # 결과 카드(환급액)가 화면 중앙에 오도록 살짝 부드럽게 스크롤
                p_est.evaluate("() => window.scrollBy({top: 380, behavior: 'smooth'})")
                p_est.wait_for_timeout(2200) # 310만원 환급액 강조 대기
                ctx_est.close()

                browser.close()

            # 녹화된 파일 처리
            est_webms = list(dir_est.glob("*.webm"))
            if not est_webms:
                raise RuntimeError("❌ [AppRecorder] 환급 0단계 시뮬레이션 녹화 비디오가 존재하지 않습니다.")
            est_raw = str(est_webms[0])

            # Part 1 MP4 준비 (프리셋 사용 또는 녹화본 변환)
            home_mp4 = str(temp_p / "part1_home.mp4")
            if use_preset_home:
                # 프리셋에서 정확히 3.5초 추출
                cmd_home = [
                    self.ffmpeg_exe, "-y",
                    "-t", "3.5",
                    "-i", str(preset_home),
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                    home_mp4
                ]
            else:
                home_webms = list(dir_home.glob("*.webm"))
                if not home_webms:
                    raise RuntimeError("❌ [AppRecorder] 홈 녹화 비디오가 존재하지 않습니다.")
                cmd_home = [
                    self.ffmpeg_exe, "-y",
                    "-ss", "1.3",
                    "-t", "3.5",
                    "-i", str(home_webms[0]),
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                    home_mp4
                ]
            subprocess.run(cmd_home, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Part 2 MP4 변환 (앞부분 1.2초 번역 전환 깜빡임 스킵하여 모국어 완성 화면부터 시작, 4.5초 유지)
            est_mp4 = str(temp_p / "part2_est.mp4")
            cmd_est = [
                self.ffmpeg_exe, "-y",
                "-ss", "1.2",
                "-t", "4.5",
                "-i", est_raw,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                est_mp4
            ]
            subprocess.run(cmd_est, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 두 비디오 Concat (3.5s + 4.5s = 8.0s)
            concat_list_file = str(temp_p / "concat_list.txt")
            with open(concat_list_file, "w", encoding="utf-8") as f:
                f.write(f"file '{home_mp4.replace(os.sep, '/')}'\n")
                f.write(f"file '{est_mp4.replace(os.sep, '/')}'\n")

            cmd_concat = [
                self.ffmpeg_exe, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_file,
                "-c", "copy",
                str(out_p)
            ]
            logger.info(f"⚙️ [AppRecorder] 메인 스크롤 + 환급 0단계 8초 결합 중... ➡️ {out_p.name}")
            subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not out_p.exists() or out_p.stat().st_size == 0:
            raise RuntimeError(f"❌ 최종 앱 시뮬레이션 파일 생성 실패: {out_p}")

        logger.info(f"✅ [AppRecorder] 8초 앱 시뮬레이션 비디오 생성 완료: {out_p} ({out_p.stat().st_size:,} bytes)")
        return str(out_p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    recorder = EasyTaxAppRecorder()
    test_out = "scratch/test_app_sim_vi.mp4"
    recorder.record_simulation_clip(lang="vi", duration_sec=8.0, output_mp4_path=test_out)
    logger.info(f"Success: {test_out}")

