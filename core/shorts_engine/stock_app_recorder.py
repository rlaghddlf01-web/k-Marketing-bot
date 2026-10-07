# -*- coding: utf-8 -*-
"""
StockAppRecorder - 📱 [StockMaster AI 삼성전자 4대 심층 모달 24초 100% 실물 라이브 녹화 모듈]
=============================================================================================
- Playwright 헤드리스 브라우저 기반
- 타깃 URL: https://stockmaster-ai.vercel.app/
- 24초 풀스크린 완벽 시연 타임라인:
  1) [0.0s ~ 3.5s] 350개 핵심 우량주 10분 계량 전광판 메인 헤더 & 1위 주도주 실시간 조망
  2) [3.5s ~ 6.5s] 검색창에 '삼성전자' 타이핑 ➔ 삼성전자 클릭 ➔ 4대 심층 모달 팝업 오픈
  3) [6.5s ~ 11.0s] [수급 현황] 탭 ➔ 3대 주체별 순매수량 그래프 + 하단 4조 거래대금/신용잔고율 풀뷰
  4) [11.0s ~ 15.5s] [기술 지표] 탭 ➔ 체결강도 158.07% + 볼린저 밴드 + 하단 4대 지표 카드 풀뷰
  5) [15.5s ~ 19.5s] [리스크 평가] 탭 ➔ 안전 위험도(30/100) + 하단 아킬레스건 안전 박스 풀뷰
  6) [19.5s ~ 24.0s] [기본 정보] 탭 ➔ PER 41.67 / PBR 4.27 / ROE 31.39% + 하단 실적 추이 바 차트 풀뷰
- 1080x1920 세로 풀HD 9:16 모바일 최적화 고화질 MP4 출력 (CRF 18, 30fps)
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

logger = logging.getLogger("StockAppRecorder")


class StockAppRecorder:
    """📈 StockMaster AI 삼성전자 4대 탭 심층 모달 24초 실물 웹앱 녹화기"""

    BASE_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.presets_dir = Path(__file__).resolve().parent / "presets"
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        logger.info("📱 [StockAppRecorder] 초기화 완료")

    def record_simulation_clip(
        self,
        topic_id: int = 1,
        duration_sec: float = 24.0,
        output_mp4_path: str = "stock_app_sim.mp4",
        force_fresh_record: bool = True
    ) -> str:
        """
        100% 실시간 웹앱(https://stockmaster-ai.vercel.app/) 브라우저 직접 접속 라이브 녹화
        - 캐시 사용 0% 전면 배제 (매 실행 시마다 실시간 최신 퀀트 데이터 녹화)
        - 1080x1920 세로 풀HD 고화질 출력
        """
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎬 [StockAppRecorder] 실시간 스톡마스터 AI 웹앱 브라우저 라이브 녹화 시작 (주제 {topic_id}, {self.BASE_URL})")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_recordings = Path(temp_dir) / "recordings"
            temp_recordings.mkdir(parents=True, exist_ok=True)

            raw_webm = self._record_browser_flow(temp_recordings, topic_id=topic_id, target_duration=duration_sec)

            if not raw_webm or not Path(raw_webm).exists():
                raise RuntimeError("❌ [StockAppRecorder] 브라우저 녹화 파일 생성 실패")

            # FFmpeg 트랜스코딩: 1080x1920 9:16 Full HD & 30fps & 고화질 (crf 18)
            logger.info(f"🔄 [StockAppRecorder] 1080x1920 세로 풀HD 트랜스코딩 중: {raw_webm} -> {out_p}")

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

        logger.info(f"🎉 [StockAppRecorder] 실시간 웹앱 라이브 시연 클립 완성 (주제 {topic_id}): {out_p} ({out_p.stat().st_size / 1024 / 1024:.2f} MB)")
        return str(out_p)

    def _record_browser_flow(self, record_dir: Path, topic_id: int = 1, target_duration: float = 24.0) -> Optional[str]:
        """Playwright 브라우저에서 인스타 릴스처럼 부드러운 스크롤 애니메이션으로 4대 탭의 상하단 내용을 완벽하게 녹화"""

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
                viewport={"width": 430, "height": 840},
                device_scale_factor=2.0,
                is_mobile=True,
                has_touch=True,
                record_video_dir=str(record_dir),
                record_video_size={"width": 430, "height": 840}
            )

            page = context.new_page()

            try:
                # 1. 페이지 로드
                logger.info(f"🌐 [StockAppRecorder] 페이지 로딩: {self.BASE_URL}")
                t_browser_start = time.time()
                page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1000)

                # 2. 광고 iframe 및 팝업 정리
                page.evaluate("""() => {
                    const style = document.createElement('style');
                    style.innerHTML = `
                        iframe,
                        [class*="ads"],
                        div[id*="google"] {
                            display: none !important;
                            opacity: 0 !important;
                            visibility: hidden !important;
                            pointer-events: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                    document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.overflowX = 'hidden';

                    // 부드러운 스크롤 헬퍼 등록
                    window.smoothScrollModal = function(targetY, durationMs = 600) {
                        return new Promise(resolve => {
                            const modal = document.querySelector('div.fixed.inset-0') || document.body;
                            const startY = modal.scrollTop || 0;
                            const diff = targetY - startY;
                            const startTime = performance.now();
                            function step(now) {
                                const progress = Math.min((now - startTime) / durationMs, 1);
                                const ease = 0.5 - Math.cos(progress * Math.PI) / 2;
                                modal.scrollTop = startY + diff * ease;
                                if (progress < 1) {
                                    requestAnimationFrame(step);
                                } else {
                                    modal.scrollTop = targetY;
                                    resolve();
                                }
                            }
                            requestAnimationFrame(step);
                        });
                    };

                    // 메인 페이지 순수 선형 초저속 연속 스크롤 헬퍼 (일정한 속도로 천천히 하강)
                    window.smoothScrollPageLinear = function(targetY, durationMs = 24000) {
                        return new Promise(resolve => {
                            const startY = window.scrollY || 0;
                            const diff = targetY - startY;
                            const startTime = performance.now();
                            function step(now) {
                                const progress = Math.min((now - startTime) / durationMs, 1);
                                window.scrollTo(0, startY + diff * progress);
                                if (progress < 1) {
                                    requestAnimationFrame(step);
                                } else {
                                    window.scrollTo(0, targetY);
                                    resolve();
                                }
                            }
                            requestAnimationFrame(step);
                        });
                    };
                }""")
                page.wait_for_timeout(200)

                # 주제별 시작 스크롤 위치 및 연출 분기
                if topic_id in [3, 5, 6]:
                    # [주제 3, 5, 6] 앱 맨 처음 최상단 (y=0)에서 시작
                    page.evaluate("() => window.scrollTo(0, 0)")
                    page.wait_for_timeout(300)
                elif topic_id == 4:
                    # 🌟 [주제 4] 10분 계량 전광판 1위 종목의 '계량 가중치 분석 (DETAIL SCORES)' 상세 카드로 즉시 스크롤!
                    page.evaluate("""() => {
                        const target = Array.from(document.querySelectorAll('*')).find(el => 
                            el.textContent && (el.textContent.includes('수급 가속 특례') || el.textContent.includes('진입 가능') || el.textContent.includes('DETAIL SCORES')) && el.children.length === 0
                        );
                        if (target) {
                            target.scrollIntoView({ behavior: 'instant', block: 'start' });
                            window.scrollBy(0, -60);
                        } else {
                            window.scrollTo(0, 6590);
                        }
                    }""")
                    page.wait_for_timeout(400)
                else:
                    # [주제 1, 2] 10분 계량 전광판 위치로 스크롤 이동
                    page.evaluate("() => window.scrollTo(0, 4090)")
                    page.wait_for_timeout(300)

                # 정확한 녹화 시작 타임스탬프 계산
                self._ready_offset = time.time() - t_browser_start
                logger.info(f"⏱️ [StockAppRecorder] 녹화 시작점 동기화: offset={self._ready_offset:.2f}s (주제 {topic_id})")

                if topic_id == 5:
                    # =========================================================================
                    # 🌟 [주제 5: 최상단(y=0)부터 💡 시장 스트레스 & ■ 4대 매크로 ➔ 📰 실시간 LIVE NEWS 풀스크린 연속 스크롤]
                    # =========================================================================
                    macro_dur_ms = int(target_duration * 0.52 * 1000)
                    news_dur_ms = max(3000, int((target_duration - (macro_dur_ms / 1000.0) - 1.0) * 1000))

                    page.evaluate(f"""() => {{
                        let startY = 0;
                        let targetY = 4050;
                        let durationMs = {macro_dur_ms};
                        let startTime = performance.now();
                        function step(now) {{
                            let progress = Math.min((now - startTime) / durationMs, 1);
                            window.scrollTo(0, startY + (targetY - startY) * progress);
                            if (progress < 1) requestAnimationFrame(step);
                        }}
                        requestAnimationFrame(step);
                    }}""")
                    page.wait_for_timeout(macro_dur_ms)

                    # Live News 카드 상단 맞춤 & 클릭
                    page.evaluate("""() => {
                        const liveTab = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.trim() === 'Live News' && el.children.length === 0);
                        const card = liveTab ? liveTab.closest('.glass-card') || liveTab.parentElement.parentElement : null;
                        if (card) {
                            const cardTop = card.getBoundingClientRect().top + window.scrollY;
                            window.scrollTo(0, cardTop - 50);
                        } else {
                            window.scrollTo(0, 7332);
                        }
                    }""")
                    page.wait_for_timeout(300)
                    try:
                        live_tab = page.locator('div, button, span').filter(has_text='Live News').last
                        live_tab.click()
                    except Exception as ex:
                        logger.warning(f"Live News click fallback: {ex}")
                    page.wait_for_timeout(500)

                    # 실시간 LIVE NEWS 뉴스 피드 연속 스크롤
                    page.evaluate(f"""() => {{
                        const liveTab = Array.from(document.querySelectorAll('*')).find(el => el.textContent && el.textContent.trim() === 'Live News' && el.children.length === 0);
                        const card = liveTab ? liveTab.closest('.glass-card') || liveTab.parentElement.parentElement : null;
                        const box = card ? card.querySelector('.overflow-y-auto') : null;
                        if (box) {{
                            let start = 0;
                            let target = 220;
                            let duration = {news_dur_ms};
                            let startTime = performance.now();
                            function step(now) {{
                                let progress = Math.min((now - startTime) / duration, 1);
                                box.scrollTop = start + target * progress;
                                if (progress < 1) requestAnimationFrame(step);
                            }}
                            requestAnimationFrame(step);
                        }}
                    }}""")
                    page.wait_for_timeout(news_dur_ms)
                    page.wait_for_timeout(500)

                elif topic_id == 3:
                    # =========================================================================
                    # 🌟 [주제 3: 뇌동매매 방지! 실시간 1등 종목 포착 ➔ 4대 모달 '리스크 평가' 탭 라이브 시연]
                    # =========================================================================
                    init_dur_ms = int(target_duration * 0.15 * 1000)
                    remain_ms = max(10000, int(target_duration * 1000 - init_dur_ms))

                    # 10분 계량 전광판으로 스크롤
                    page.evaluate("() => window.scrollTo(0, 4090)")
                    page.wait_for_timeout(init_dur_ms)

                    # 당일 1위 종목 자동 감지
                    detected_top1 = page.evaluate("""() => {
                        const text = document.body.innerText || '';
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                        let boardIdx = -1;
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('계량 전광판 및 실시간 리스크 센터')) {
                                boardIdx = i;
                                break;
                            }
                        }
                        if (boardIdx !== -1) {
                            for (let i = boardIdx; i < Math.min(boardIdx + 60, lines.length); i++) {
                                if (lines[i] === '1' && i + 1 < lines.length) {
                                    return lines[i+1];
                                }
                            }
                        }
                        return '한온시스템';
                    }""")
                    stock_query = detected_top1 or "한온시스템"
                    logger.info(f"🏆 [StockAppRecorder] 주제 3번 실시간 1위 리스크가드 종목: {stock_query}")

                    inp = page.query_selector('input')
                    if inp:
                        inp.click()
                        inp.fill("")
                        for char in stock_query:
                            inp.type(char, delay=50)
                        page.wait_for_timeout(300)

                    span_target = page.query_selector(f'text="{stock_query}"')
                    if span_target:
                        span_target.click()
                        page.wait_for_timeout(800)

                    # [리스크 평가] 탭 원클릭
                    tab_risk = page.query_selector('text="리스크 평가"')
                    if tab_risk:
                        tab_risk.click()
                        page.wait_for_timeout(500)

                    # 리스크 평가 상세 지표 & 기계적 손절선 & 아킬레스건 박스 상하 완벽 스크롤
                    scroll_1_ms = int(remain_ms * 0.45)
                    scroll_2_ms = int(remain_ms * 0.45)
                    page.evaluate(f"() => window.smoothScrollModal(380, {scroll_1_ms})")
                    page.wait_for_timeout(scroll_1_ms)
                    page.evaluate(f"() => window.smoothScrollModal(0, {scroll_2_ms})")
                    page.wait_for_timeout(scroll_2_ms)
                    page.wait_for_timeout(500)

                elif topic_id == 6:
                    # =========================================================================
                    # 🌟 [주제 6: 스톡마스터AI 총괄 - 최상단부터 전광판까지 풀스크린 연속 스크롤]
                    # =========================================================================
                    scroll_dur_ms = max(5000, int((target_duration - 0.5) * 1000))
                    page.evaluate(f"() => window.smoothScrollPageLinear(4400, {scroll_dur_ms})")
                    page.wait_for_timeout(scroll_dur_ms)
                    page.wait_for_timeout(500)

                elif topic_id == 4:
                    # =========================================================================
                    # 🌟 [주제 4: 1위 주도주 계량 가중치 분석 상세 카드 (첫 화면) ➔ 4대 모달 탭 풀스크롤]
                    # =========================================================================
                    top1_dur_ms = int(target_duration * 0.18 * 1000)
                    search_dur_ms = 2200
                    remain_ms = max(8000, int(target_duration * 1000 - top1_dur_ms - search_dur_ms))
                    tab_dur_ms = int(remain_ms / 4)

                    page.wait_for_timeout(1000)
                    page.evaluate("() => window.scrollBy({top: 320, behavior: 'smooth'})")
                    page.wait_for_timeout(max(500, top1_dur_ms - 1000))

                    # 1위 종목명 자동 감지
                    detected_top1 = page.evaluate("""() => {
                        const text = document.body.innerText || '';
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                        let boardIdx = -1;
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('계량 전광판 및 실시간 리스크 센터')) {
                                boardIdx = i;
                                break;
                            }
                        }
                        if (boardIdx === -1) return '후성';
                        for (let i = boardIdx; i < Math.min(boardIdx + 60, lines.length); i++) {
                            if (lines[i] === '1' && i + 1 < lines.length) {
                                return lines[i+1];
                            }
                        }
                        return '후성';
                    }""")
                    stock_query = detected_top1 or "후성"
                    logger.info(f"🏆 [StockAppRecorder] 주제 4번 1위 종목 모달 오픈: {stock_query}")

                    page.evaluate("() => window.scrollTo(0, 4090)")
                    page.wait_for_timeout(300)
                    inp = page.query_selector('input')
                    if inp:
                        inp.click()
                        inp.fill("")
                        for char in stock_query:
                            inp.type(char, delay=40)
                        page.wait_for_timeout(200)

                    span_target = page.query_selector(f'text="{stock_query}"')
                    if span_target:
                        span_target.click()
                        page.wait_for_timeout(800)

                    # 4대 모달 탭 비례 순환
                    # 1번째: [수급 현황]
                    tab_supply = page.query_selector('text="수급 현황"')
                    if tab_supply:
                        tab_supply.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(320, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 400))

                    # 2번째: [기술 지표]
                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_tech = page.query_selector('text="기술 지표"')
                    if tab_tech:
                        tab_tech.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(380, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                    # 3번째: [리스크 평가]
                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_risk = page.query_selector('text="리스크 평가"')
                    if tab_risk:
                        tab_risk.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(260, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                    # 4번째: [기본 정보]
                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_basic = page.query_selector('text="기본 정보"')
                    if tab_basic:
                        tab_basic.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(320, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                else:
                    # =========================================================================
                    # 🌟 [주제 1, 2: 삼성전자 / SK하이닉스 종목 모달]
                    # =========================================================================
                    init_dur_ms = int(target_duration * 0.15 * 1000)
                    search_dur_ms = 2200
                    remain_ms = max(8000, int(target_duration * 1000 - init_dur_ms - search_dur_ms))
                    tab_dur_ms = int(remain_ms / 4)

                    page.wait_for_timeout(init_dur_ms)

                    stock_query = "SK하이닉스" if topic_id == 2 else "삼성전자"
                    inp = page.query_selector('input')
                    if inp:
                        inp.click()
                        inp.fill("")
                        for char in stock_query:
                            inp.type(char, delay=50)
                        page.wait_for_timeout(300)

                    span_target = page.query_selector(f'text="{stock_query}"')
                    if span_target:
                        span_target.click()
                        page.wait_for_timeout(800)

                    # 4대 탭 순차 순환
                    tab_supply = page.query_selector('text="수급 현황"')
                    if tab_supply:
                        tab_supply.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(320, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 400))

                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_tech = page.query_selector('text="기술 지표"')
                    if tab_tech:
                        tab_tech.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(380, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_risk = page.query_selector('text="리스크 평가"')
                    if tab_risk:
                        tab_risk.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(260, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                    page.evaluate("() => window.smoothScrollModal(0, 200)")
                    page.wait_for_timeout(200)
                    tab_basic = page.query_selector('text="기본 정보"')
                    if tab_basic:
                        tab_basic.click()
                        page.wait_for_timeout(400)
                        page.evaluate("() => window.smoothScrollModal(320, 600)")
                        page.wait_for_timeout(max(500, tab_dur_ms - 600))

                # 28초 채우기
                elapsed = time.time() - t_browser_start - self._ready_offset
                remain = target_duration - elapsed
                if remain > 0:
                    page.wait_for_timeout(int(remain * 1000) + 100)

            except Exception as e:
                logger.error(f"❌ [StockAppRecorder] 브라우저 자동화 중 오류: {e}")
            finally:
                context.close()
                browser.close()

        # 녹화된 파일 찾기
        recorded_files = list(record_dir.glob("*.webm"))
        if recorded_files:
            return str(recorded_files[0])
        return None

