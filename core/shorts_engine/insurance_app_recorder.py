# -*- coding: utf-8 -*-
"""
InsuranceAppRecorder - 📱 [보험 리밸런스 실제 웹앱 실시간 시뮬레이션 고화질 12초 녹화 모듈]
- Playwright 헤드리스 브라우저 기반
- 타깃 URL: https://insure-rebalance.vercel.app/
- 사용자 지정 12초 완벽 시연 파이프라인 (2단 직결 23초 숏폼 전담):
  1) [0.0s ~ 0.8s] 상단 헤더/팝업 없는 신뢰도 뷰 시작
     - Standard (Topic 1~6): '제휴 협력 파트너 33개사 실시간 통합 비교' (y=3780)
     - OneClick (Topic 7~8): '원클릭 내 보험 분석 & 고객과의 안심 3대 약속' (y=13450)
  2) [0.8s ~ 2.8s] 주제별 맞춤 카테고리/특약/생년월일/성별 클릭 및 정밀 분석 버튼 실행
  3) [2.8s ~ 12.0s] (무려 9.2초 동안!) 가독성 높고 부드럽게 주제별 리포트 및 비교 순위표 안착 스크롤
  4) ✨ 불필요한 공시자료/상담 푸터 영역 침범 Zero
- 1080x1920 세로 풀HD 9:16 모바일 최적화 고화질 MP4 출력
- 모든 플로팅 팝업, 실시간 상담 요청 바, 박효진 설계사 플로팅 버튼 전면 제거(Clean View)
"""

import os
import sys
import time
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceAppRecorder")


class InsuranceAppRecorder:
    """🛡️ 보험 리밸런스 실제 웹앱 실시간 시뮬레이션 레코더"""

    BASE_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.presets_dir = Path(__file__).resolve().parent / "presets"
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        logger.info("📱 [InsuranceAppRecorder] 초기화 완료")

    def record_simulation_clip(
        self,
        topic_id: int = 1,
        duration_sec: float = 12.0,
        output_mp4_path: str = "insurance_app_sim.mp4",
        force_fresh_record: bool = False
    ) -> str:
        """
        주제별 맞춤 시연 플로우(33개사 제휴/원클릭 안심약속 -> 조건 선택/입력 -> 분석 -> 리포트/순위표 안착) 12초 실물 녹화
        - 1080x1920 세로 풀HD 고화질 출력
        """
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        preset_cache = self.presets_dir / f"insure_app_sim_topic{topic_id}_12s.mp4"

        if preset_cache.exists() and not force_fresh_record and preset_cache.stat().st_size > 100000:
            logger.info(f"⚡ [InsuranceAppRecorder] 캐시된 12초 고화질 실물 앱 녹화본 사용 (주제 {topic_id}): {preset_cache}")
            shutil.copyfile(preset_cache, out_p)
            return str(out_p)

        logger.info(f"🎬 [InsuranceAppRecorder] 실제 웹앱 실시간 12초 브라우징 녹화 시작 (주제 {topic_id}, {self.BASE_URL})")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_recordings = Path(temp_dir) / "recordings"
            temp_recordings.mkdir(parents=True, exist_ok=True)

            raw_webm = self._record_browser_flow(temp_recordings, topic_id=topic_id, target_duration=duration_sec)

            if not raw_webm or not Path(raw_webm).exists():
                raise RuntimeError("❌ [InsuranceAppRecorder] 브라우저 녹화 파일 생성 실패")

            # FFmpeg 트랜스코딩: 1080x1920 9:16 Full HD & 30fps & 고화질 (crf 18)
            logger.info(f"🔄 [InsuranceAppRecorder] 1080x1920 세로 풀HD 트랜스코딩 중: {raw_webm} -> {out_p}")

            offset = getattr(self, "_ready_offset", 0.0)

            cmd = [
                self.ffmpeg_exe,
                "-y",
                "-ss", f"{offset:.2f}",
                "-i", str(raw_webm),
                "-t", f"{duration_sec:.2f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an",
                str(out_p)
            ]

            res = subprocess.run(cmd, capture_output=True)
            if res.returncode != 0:
                err_msg = res.stderr.decode("utf-8", errors="ignore") if res.stderr else "unknown"
                logger.error(f"❌ FFmpeg 변환 실패: {err_msg}")
                raise RuntimeError(f"FFmpeg transcode error: {err_msg}")

            # 캐시 저장
            try:
                shutil.copyfile(out_p, preset_cache)
                logger.info(f"💾 [InsuranceAppRecorder] 프리셋 캐시 저장 완료 (주제 {topic_id}): {preset_cache}")
            except Exception as e:
                logger.warning(f"⚠️ 캐시 저장 실패: {e}")

        logger.info(f"🎉 [InsuranceAppRecorder] 12초 실물 웹앱 시연 클립 완성 (주제 {topic_id}): {out_p} ({out_p.stat().st_size / 1024 / 1024:.2f} MB)")
        return str(out_p)

    def _record_browser_flow(self, record_dir: Path, topic_id: int = 1, target_duration: float = 12.0) -> Optional[str]:
        """Playwright 브라우저에서 주제별 사용자 시연 시나리오를 정밀하게 자동화하며 녹화"""
        try:
            from brands.insurance.insurance_web_simulator_actions import get_topic_action_spec
            spec = get_topic_action_spec(topic_id)
        except Exception:
            import sys
            from pathlib import Path
            engine_root = Path(__file__).resolve().parent.parent.parent
            if str(engine_root) not in sys.path:
                sys.path.insert(0, str(engine_root))
            from brands.insurance.insurance_web_simulator_actions import get_topic_action_spec
            spec = get_topic_action_spec(topic_id)
        
        logger.info(f"🎯 [InsuranceAppRecorder] 주제 {topic_id} 액션 스펙 적용: {spec}")

        init_y = spec.get("init_scroll_y", 3780)
        birth_val = spec.get("birth", "19820512")
        gender_val = spec.get("gender", "여성")
        cat_kw = spec.get("category_keyword", "의료실비")
        sub_kw = spec.get("sub_keyword", "4세대 실손")
        start_y = spec.get("start_scroll_y", 11600)
        end_y = spec.get("end_scroll_y", 25500)
        scroll_ms = spec.get("duration_scroll_ms", 8800)
        mode = spec.get("mode", "standard")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--mute-audio"
                ]
            )

            context = browser.new_context(
                viewport={"width": 430, "height": 764},
                device_scale_factor=2.5,
                is_mobile=True,
                has_touch=True,
                record_video_dir=str(record_dir),
                record_video_size={"width": 430, "height": 764}
            )

            page = context.new_page()

            try:
                # 1. 페이지 로드
                logger.info(f"🌐 [InsuranceAppRecorder] 페이지 로딩: {self.BASE_URL}")
                t_browser_start = time.time()
                page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(300)

                # 🌟 [2. 상단 헤더, 모든 플로팅 팝업, 모달 오버레이 전면 제거 및 로딩 즉각 완료 JS 주입]
                page.evaluate("""() => {
                    const style = document.createElement('style');
                    style.innerHTML = `
                        header,
                        [class*="popup"],
                        [class*="modal"],
                        [class*="toast"],
                        [class*="fixed"],
                        div[class*="z-30"],
                        div[class*="z-40"],
                        div[class*="z-50"] {
                            display: none !important;
                            opacity: 0 !important;
                            visibility: hidden !important;
                            pointer-events: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                    document.querySelectorAll('header, div[class*="z-30"], div[class*="z-40"]').forEach(el => el.remove());
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.overflowX = 'hidden';

                    // 로딩 루프 즉각 완료 오버라이드 (0.0초 즉시 결과 렌더링)
                    const orig = window.setTimeout;
                    window.setTimeout = function(fn, delay, ...args) {
                        if (delay === 300 || delay === 400 || (delay >= 200 && delay <= 500)) {
                            return orig(fn, 0, ...args);
                        }
                        return orig(fn, delay, ...args);
                    };
                }""")
                page.wait_for_timeout(200)

                # 3. 주제별 시작 지점으로 즉시 스크롤 이동
                page.evaluate(f"() => window.scrollTo(0, {init_y})")
                page.wait_for_timeout(400)

                # 🌟 [정확한 녹화 시작 타임스탬프 계산]
                self._ready_offset = time.time() - t_browser_start
                logger.info(f"⏱️ [InsuranceAppRecorder] 시작점 동기화 (y={init_y}): offset={self._ready_offset:.2f}s")

                smooth_scroll = """
                    (targetY, duration) => {
                        return new Promise(resolve => {
                            const startY = window.scrollY;
                            const diff = targetY - startY;
                            const startTime = performance.now();
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

                # ==========================================
                # 🌟 [0.0s ~ 0.4s] 신뢰도 헤더 뷰 유지
                # ==========================================
                page.wait_for_timeout(400)

                if mode == "oneclick":
                    # ==========================================
                    # 🌟 [Topic 7 & 8: 원클릭 내 보험 정밀 분석 플로우]
                    # ==========================================
                    # [0.4s ~ 0.7s] 성별 선택 및 생년월일 입력
                    page.evaluate(f"({smooth_scroll})(13900, 100)")
                    page.wait_for_timeout(100)
                    
                    # 성별 선택
                    g_btn = page.locator(f'button:has-text("{gender_val}")').last
                    g_btn.scroll_into_view_if_needed()
                    g_btn.click()
                    page.wait_for_timeout(50)

                    # 생년월일 입력
                    inps = page.locator('input')
                    cnt = inps.count()
                    for i in range(cnt):
                        el = inps.nth(i)
                        box = el.bounding_box()
                        if box and box['y'] + page.evaluate("window.scrollY") > 13000:
                            el.fill(str(birth_val))
                            break
                    page.wait_for_timeout(50)

                    # [0.7s ~ 1.0s] 암보험 선택
                    page.evaluate(f"({smooth_scroll})(14500, 100)")
                    page.wait_for_timeout(100)
                    c_btn = page.locator(f'button:has-text("{cat_kw}")').last
                    c_btn.scroll_into_view_if_needed()
                    c_btn.click()
                    page.wait_for_timeout(50)

                    # [1.0s ~ 1.2s] '내 보험 정밀 분석 시작하기' 대형 버튼 Playwright 네이티브 클릭!
                    start_btn = page.locator('button:has-text("내 보험 정밀 분석 시작하기")').last
                    start_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(50)
                    start_btn.click()

                    # [1.2s ~ 1.3s] 결과 렌더링 즉시 감지 (로딩 모달 0초 전면 생략)
                    try:
                        page.wait_for_selector('text="보험 1건씩 개별 정밀 분석"', timeout=6000)
                    except Exception:
                        page.wait_for_timeout(500)
                    page.wait_for_timeout(50)

                else:
                    # ==========================================
                    # 🌟 [Topic 1 ~ 6: 33개사 제휴 및 상품 비교 플로우]
                    # ==========================================
                    page.evaluate(f"({smooth_scroll})(5200, 180)")
                    page.wait_for_timeout(200)
                    page.evaluate(f"""() => {{
                        const kw = '{cat_kw}';
                        const btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes(kw))
                            || Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('의료실비'));
                        if (btn) btn.click();
                    }}""")
                    page.wait_for_timeout(80)

                    page.evaluate(f"({smooth_scroll})(7150, 180)")
                    page.wait_for_timeout(200)
                    page.evaluate(f"""() => {{
                        const subKw = '{sub_kw}';
                        const btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes(subKw))
                            || Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('4세대 실손'));
                        if (btn) btn.click();
                    }}""")
                    page.wait_for_timeout(80)

                    page.evaluate(f"({smooth_scroll})(8400, 180)")
                    page.wait_for_timeout(200)
                    page.evaluate(f"""() => {{
                        const inp = Array.from(document.querySelectorAll('input')).find(el => (el.placeholder || '').includes('19770101'));
                        if (inp) {{
                            inp.focus();
                            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(inp, '{birth_val}');
                            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            inp.blur();
                        }}
                        const targetGender = '{gender_val}';
                        const gBtn = Array.from(document.querySelectorAll('button')).find(b => {{
                            const r = b.getBoundingClientRect();
                            return (r.top + window.scrollY) > 8000 && (r.top + window.scrollY) < 9000 && (b.innerText || '').trim() === targetGender;
                        }}) || Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').trim() === '여성');
                        if (gBtn) gBtn.click();
                    }}""")
                    page.wait_for_timeout(250)

                    page.evaluate(f"({smooth_scroll})(9300, 150)")
                    page.wait_for_timeout(180)
                    page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button')).filter(el => {
                            const r = el.getBoundingClientRect();
                            return (r.top + window.scrollY) > 8800 && (r.top + window.scrollY) < 10100;
                        });
                        btns.forEach(b => {
                            const txt = (b.innerText || '').trim();
                            if (txt === '가입중' || txt === '아니오' || txt.includes('5% 할인')) {
                                b.click();
                            }
                        });
                    }""")
                    page.wait_for_timeout(250)

                    page.evaluate(f"({smooth_scroll})(9700, 120)")
                    page.wait_for_timeout(150)
                    page.evaluate("""() => {
                        const submit = Array.from(document.querySelectorAll('button')).find(el => {
                            const r = el.getBoundingClientRect();
                            const top = r.top + window.scrollY;
                            return top > 9000 && (el.innerText || '').includes('무료로 비교 분석하기');
                        });
                        if (submit) submit.click();
                    }""")
                    page.wait_for_timeout(400)

                # ==========================================
                # 🌟 결과 리포트부터 목표 지점까지 부드럽고 가독성 높은 안착 스크롤!
                # ==========================================
                smooth_result_scroll = """
                    (startY, endY, duration) => {
                        return new Promise(resolve => {
                            window.scrollTo(0, startY);
                            const diff = endY - startY;
                            const startTime = performance.now();
                            function step(currentTime) {
                                const elapsed = currentTime - startTime;
                                const progress = Math.min(elapsed / duration, 1);
                                const ease = progress < 0.5 
                                    ? 2 * progress * progress 
                                    : -1 + (4 - 2 * progress) * progress;
                                window.scrollTo(0, startY + diff * ease);
                                if (progress < 1) {
                                    requestAnimationFrame(step);
                                } else {
                                    window.scrollTo(0, endY);
                                    resolve();
                                }
                            }
                            requestAnimationFrame(step);
                        });
                    }
                """
                page.evaluate(f"({smooth_result_scroll})({start_y}, {end_y}, {scroll_ms})")
                
                # 남은 녹화 시간 유지
                rem_wait_ms = max(int(scroll_ms) + 500, 7500)
                page.wait_for_timeout(rem_wait_ms)

                logger.info(f"✅ [InsuranceAppRecorder] 전체 고화질 시연 & 완벽 안착 완료 (주제 {topic_id})")

            finally:
                context.close()
                browser.close()

            video_files = list(record_dir.glob("*.webm"))
            if video_files:
                return str(video_files[0])

            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    recorder = InsuranceAppRecorder()
    out = recorder.record_simulation_clip(
        topic_id=4,
        duration_sec=12.0,
        output_mp4_path="scratch/test_topic4_12s.mp4",
        force_fresh_record=True
    )
    print("최종 완성된 12초 녹화본:", out)
