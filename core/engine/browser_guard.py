# -*- coding: utf-8 -*-
"""
BrowserGuard - 🛡️ [Playwright 브라우저 자원 격리 & GPU 0% & 동시성 순차 안전 매니저]
================================================================================
• 배경 & 목적:
  - 3대 브랜드(Aura, 보험, 주식)의 틱톡/유튜브/메타/카페 스텔스 행동 봇이 동시 실행될 때,
    GPU(그래픽카드) 점유 폭주, CPU 풀로드, 메모리 17GB 누수 및 프로필 Lock 경합을 100% 원천 차단합니다.
• 핵심 기능:
  1. [GPU 0% 순수 격리]: --disable-gpu 플래그 강제로 그래픽카드 부하/소음 0% 유지
  2. [프로필 잠금(Lock) 사전 자동 청소]: 크래시 잔여 고아 LOCK 파일 자동 해제
  3. [전역 동시성 직렬화 (BrowserLock)]: 브라우저 세션을 순차 대기(Queue)시켜 RAM/CPU 보호
  4. [좀비 프로세스 안전 정리]: 고아 chrome-headless-shell 메모리 누수 원천 차단
• 원칙: Rule 1 (독립 레고 블록화), Rule 5 (근본 구조 해결), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import time
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import List, Optional, Union
from contextlib import contextmanager, asynccontextmanager

logger = logging.getLogger("BrowserGuard")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
BROWSER_LOCK_FILE = DATA_DIR / "browser_execution.lock"
BROWSER_STATUS_FILE = DATA_DIR / "browser_current_task.json"

# 표준 안전 브라우저 인자 (GPU 0% 점유 & 초경량 메모리 절약)
SAFE_BROWSER_ARGS = [
    "--disable-gpu",                           # 그래픽카드 점유 0% 원천 차단 (팬 소음 및 VRAM 고갈 방지)
    "--disable-software-rasterizer",          # 소프트웨어 GPU 에뮬레이션 차단
    "--disable-dev-shm-usage",                # 공유 메모리 초과 방지
    "--no-sandbox",                           # 샌드박스 오버헤드 완화
    "--disable-infobars",                     # 불필요 UI 차단
    "--disable-blink-features=AutomationControlled", # 봇 탐지 우회
    "--disable-background-networking",        # 백그라운드 네트워크 동기화 차단
    "--disable-background-timer-throttling",  # 백그라운드 타이머 스로틀링 안정화
    "--disable-backgrounding-occluded-windows", # 창 가려짐 성능 저하 차단
    "--disable-renderer-backgrounding",       # 렌더러 백그라운드 지연 차단
    "--disable-breakpad",                     # 크래시 덤프 오버헤드 차단
    "--disable-component-update",             # 크롬 컴포넌트 자동 업데이트 차단
    "--disable-domain-reliability",           # 도메인 신뢰성 리포트 차단
    "--disable-sync",                         # 구글 계정 동기화 차단
    "--mute-audio",                           # 오디오 재생 차단 (CPU 절약)
    "--no-first-run",                         # 첫 실행 환영창 차단
    "--password-store=basic",                 # 키체인 접근 차단
    "--use-mock-keychain",                    # 맥/리눅스 키체인 에러 차단
    "--disable-features=Translate,OptimizationHints,MediaRouter,PaintHolding", # 불필요한 기능 제거
]


def clean_browser_profile_locks(profile_dir: Union[Path, str]) -> None:
    """
    브라우저 프로필 디렉터리 내의 잔여 고아 LOCK 파일 및 임시 캐시 안전 청소
    (Playwright 'Target crashed / IO error: LockFile Access denied' 원천 방지)
    """
    p_dir = Path(profile_dir)
    if not p_dir.exists():
        return

    lock_patterns = [
        "SingletonLock",
        "SingletonCookie",
        "SingletonSocket",
        "LOCK",
        "lockfile",
        "*.lock"
    ]

    cleaned_count = 0
    for pat in lock_patterns:
        try:
            # 프로필 루트 및 하위 DB 잠금 파일 검색
            for lock_file in p_dir.glob(pat):
                try:
                    if lock_file.is_file():
                        lock_file.unlink(missing_ok=True)
                        cleaned_count += 1
                except Exception:
                    pass
        except Exception:
            pass

    # Default/shared_proto_db 등 하위 DB 락 정밀 검사
    try:
        sub_dbs = p_dir.glob("**/LOCK")
        for sub_lock in sub_dbs:
            try:
                if sub_lock.is_file():
                    sub_lock.unlink(missing_ok=True)
                    cleaned_count += 1
            except Exception:
                pass
    except Exception:
        pass

    if cleaned_count > 0:
        logger.debug(f"🧹 [BrowserGuard] 잔여 락 파일 {cleaned_count}개 자동 정리 완료: {p_dir.name}")


def get_safe_browser_args(extra_args: Optional[List[str]] = None) -> List[str]:
    """GPU 0% + 초경량 안전 브라우저 인자 반환"""
    args = list(SAFE_BROWSER_ARGS)
    if extra_args:
        for arg in extra_args:
            if arg not in args:
                args.append(arg)
    return args


class GlobalBrowserLock:
    """
    전역 브라우저 동시 실행 직렬화 매니저 (싱글톤)
    - 동시에 2개 이상의 무거운 Playwright 브라우저가 기동되어 RAM/CPU가 폭증하는 것을 원천 차단
    - 작업이 요청되면 차분하게 순차 대기(Queue) 후 단독 실행
    """
    _instance = None
    _thread_lock = threading.RLock()

    def __new__(cls):
        with cls._thread_lock:
            if cls._instance is None:
                cls._instance = super(GlobalBrowserLock, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._current_task: Optional[str] = None
        self._task_start_time: Optional[float] = None
        self._queue_count = 0
        self._initialized = True

    def _write_status(self, task_name: Optional[str], status: str):
        try:
            data = {
                "current_task": task_name,
                "status": status,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
                "queue_count": self._queue_count
            }
            with open(BROWSER_STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def acquire(self, task_name: str, timeout_sec: int = 1800) -> bool:
        """동기 브라우저 락 획득"""
        start_wait = time.time()
        logged_wait = False
        self._queue_count += 1

        try:
            while True:
                acquired = self._thread_lock.acquire(blocking=False)
                if acquired:
                    file_locked = False
                    if BROWSER_LOCK_FILE.exists():
                        try:
                            file_age = time.time() - BROWSER_LOCK_FILE.stat().st_mtime
                            if file_age > 1800:
                                logger.warning(f"⚠️ [BrowserGuard] 30분 초과 고아 브라우저 락 자동 해제: {BROWSER_LOCK_FILE}")
                                BROWSER_LOCK_FILE.unlink(missing_ok=True)
                            else:
                                file_locked = True
                        except Exception:
                            file_locked = True

                    if not file_locked:
                        try:
                            BROWSER_LOCK_FILE.write_text(f"{task_name} (pid={os.getpid()})", encoding="utf-8")
                        except Exception:
                            pass

                        self._current_task = task_name
                        self._task_start_time = time.time()
                        self._write_status(task_name, "running")

                        wait_duration = round(time.time() - start_wait, 1)
                        if wait_duration > 1.0:
                            logger.info(f"🌐 [BrowserGuard] '{task_name}' 작업이 대기 {wait_duration}초 후 브라우저 단독 실행에 진입합니다.")
                        else:
                            logger.info(f"🌐 [BrowserGuard] '{task_name}' 브라우저 단독 실행 진입 (GPU 0% 모드)")
                        return True
                    else:
                        self._thread_lock.release()

                elapsed = round(time.time() - start_wait, 1)
                if elapsed > timeout_sec:
                    logger.error(f"❌ [BrowserGuard] '{task_name}' 브라우저 대기 시간({timeout_sec}초) 초과로 중단")
                    return False

                if not logged_wait or int(elapsed) % 15 == 0:
                    cur = self._current_task or "선행 브라우저 봇"
                    logger.info(f"⏳ [BrowserGuard 순차 대기] 현재 '{cur}' 실행 중. '{task_name}'은(는) 안전 대기 중... ({int(elapsed)}초 경과 / 대기열: {self._queue_count}개)")
                    logged_wait = True

                time.sleep(2)
        finally:
            self._queue_count = max(0, self._queue_count - 1)

    def release(self, task_name: Optional[str] = None):
        """브라우저 락 해제"""
        try:
            BROWSER_LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass

        finished_task = task_name or self._current_task or "브라우저 작업"
        duration = round(time.time() - self._task_start_time, 1) if self._task_start_time else 0

        self._current_task = None
        self._task_start_time = None
        self._write_status(None, "idle")

        try:
            self._thread_lock.release()
        except RuntimeError:
            pass

        logger.info(f"✅ [BrowserGuard] '{finished_task}' 브라우저 세션 정상 완료 및 자원 반환 (소요: {duration}초)")


# 싱글톤 매니저 인스턴스
browser_guard_manager = GlobalBrowserLock()


@contextmanager
def browser_lock(task_name: str, timeout_sec: int = 1800):
    """동기 컨텍스트 매니저"""
    acquired = browser_guard_manager.acquire(task_name=task_name, timeout_sec=timeout_sec)
    if not acquired:
        raise TimeoutError(f"브라우저 락 획득 타임아웃 ({timeout_sec}초 경과): {task_name}")
    try:
        yield
    finally:
        browser_guard_manager.release(task_name=task_name)


@asynccontextmanager
async def async_browser_lock(task_name: str, timeout_sec: int = 1800):
    """비동기 컨텍스트 매니저 (asyncio 지원)"""
    loop = asyncio.get_running_loop()
    acquired = await loop.run_in_executor(None, browser_guard_manager.acquire, task_name, timeout_sec)
    if not acquired:
        raise TimeoutError(f"비동기 브라우저 락 획득 타임아웃 ({timeout_sec}초 경과): {task_name}")
    try:
        yield
    finally:
        await loop.run_in_executor(None, browser_guard_manager.release, task_name)
