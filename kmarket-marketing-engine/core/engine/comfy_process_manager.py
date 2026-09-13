# -*- coding: utf-8 -*-
"""
ComfyProcessManager - 🎮 [ComfyUI Wan2.1/2.2 무인 자동 기동 & 프로세스 자율 매니저]
- 사용자가 별도로 배치 파일(run_nvidia_gpu.bat 등)을 찾아 실행할 필요를 100% 영구 제거
- 대시보드에서 카드뉴스/숏폼 제작 버튼 클릭 시 8188 포트 응답 여부 자동 감지
- 미기동 상태일 때 D:\\ComfyUI_Wan_Engine 내장 엔진을 백그라운드로 자동 실행 & 포트 대기
"""

import os
import sys
import time
import json
import logging
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ComfyProcessManager")


class ComfyProcessManager:
    """ComfyUI 로컬 백그라운드 프로세스 자율 매니저"""

    COMFY_DIR = Path(r"D:\ComfyUI_Wan_Engine")
    HOST = "http://127.0.0.1:8188"
    _process: Optional[subprocess.Popen] = None

    @classmethod
    def is_running(cls) -> bool:
        """ComfyUI 포트(8188) 응답 여부 확인"""
        try:
            with urllib.request.urlopen(f"{cls.HOST}/system_stats", timeout=2) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                return stats.get("system", {}).get("os") is not None
        except Exception:
            return False

    @classmethod
    def ensure_running(cls, wait_timeout: int = 50, log_callback=None) -> bool:
        """
        ComfyUI가 이미 켜져 있으면 즉시 True 반환.
        꺼져 있으면 백그라운드로 조용히 자동 기동하고 준비될 때까지 대기.
        """
        if cls.is_running():
            logger.info("⚡ [ComfyUI 자율 매니저] ComfyUI 엔진이 이미 정상 가동 중입니다.")
            return True

        if not cls.COMFY_DIR.exists():
            msg = f"⚠️ [ComfyUI 자율 매니저] {cls.COMFY_DIR} 경로가 존재하지 않습니다."
            logger.warning(msg)
            if log_callback:
                log_callback(msg, "warning")
            return False

        python_exe = cls.COMFY_DIR / "python_embeded" / "python.exe"
        main_py = cls.COMFY_DIR / "ComfyUI" / "main.py"

        if not python_exe.exists() or not main_py.exists():
            msg = "⚠️ [ComfyUI 자율 매니저] ComfyUI 내장 실행 파일이 누락되었습니다."
            logger.warning(msg)
            if log_callback:
                log_callback(msg, "warning")
            return False

        cmd = [
            str(python_exe),
            "-s",
            str(main_py),
            "--windows-standalone-build",
            "--fast", "fp16_accumulation"
        ]

        msg_start = "🚀 [ComfyUI 자율 매니저] ComfyUI GPU 엔진을 백그라운드에서 자동 기동합니다 (창 없이 조용히 실행)..."
        logger.info(msg_start)
        if log_callback:
            log_callback(msg_start, "info")

        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            cls._process = subprocess.Popen(
                cmd,
                cwd=str(cls.COMFY_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags
            )
        except Exception as e:
            err_msg = f"❌ [ComfyUI 자율 매니저] 백그라운드 기동 실패: {e}"
            logger.error(err_msg)
            if log_callback:
                log_callback(err_msg, "danger")
            return False

        # 포트 열릴 때까지 폴링 대기
        start_t = time.time()
        while time.time() - start_t < wait_timeout:
            time.sleep(2.5)
            if cls.is_running():
                msg_ready = "🎉 [ComfyUI 자율 매니저] ComfyUI 엔진 기동 완료! GPU 실사 생성 준비 완료!"
                logger.info(msg_ready)
                if log_callback:
                    log_callback(msg_ready, "success")
                return True

        msg_timeout = "⚠️ [ComfyUI 자율 매니저] 기동 대기 시간 초과 (초기 모델 로딩 중일 수 있습니다)."
        logger.warning(msg_timeout)
        if log_callback:
            log_callback(msg_timeout, "warning")
        return cls.is_running()
