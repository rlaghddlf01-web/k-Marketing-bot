# -*- coding: utf-8 -*-
"""
RemoteComfyBridge - 🌉 [원격 GPU ComfyUI 고속 통신 및 미디어 자동 동기화 브릿지]
- 원격 GPU 머신(ComfyUI Wan2.1 / Wan2.2)과 HTTP REST API 양방향 파일 통신
- 로컬 입력 에셋(레퍼런스 이미지, 마스크, TTS 오디오) 원격 자동 업로드 (/upload/image)
- 원격 생성 산출물(카드뉴스 고화질 사진, 립싱크 숏폼 MP4) 로컬 스트림 다운로드 (/view)
- 생성 완료 즉시 로컬 웹 서빙용 outputs 폴더 및 사용자 PC 바탕화면 자동 동시 배포
"""

import os
import sys
import shutil
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("RemoteComfyBridge")


class RemoteComfyBridge:
    """원격 ComfyUI GPU 엔진 브릿지 및 미디어 싱크 매니저"""

    def __init__(self, host: Optional[str] = None):
        from config import COMFY_HOST, OUTPUTS_DIR, DESKTOP_DIR
        self.host = (host or COMFY_HOST).rstrip("/")
        self.outputs_dir = Path(OUTPUTS_DIR)
        self.desktop_dir = Path(DESKTOP_DIR)
        self.temp_cache_dir = self.outputs_dir / "remote_cache"
        self.temp_cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_remote(self) -> bool:
        """현재 대상 호스트가 외부 네트워크 컴퓨터인지 여부"""
        return not any(lh in self.host for lh in ["127.0.0.1", "localhost", "0.0.0.0"])

    def check_health(self, timeout: float = 3.0) -> bool:
        """원격 ComfyUI 엔진 온라인 상태 및 시스템 헬스체크"""
        try:
            r = requests.get(f"{self.host}/system_stats", timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("system", {}).get("os") is not None
        except Exception as e:
            logger.debug(f"ComfyUI 헬스체크 예외 ({self.host}): {e}")
        return False

    def upload_file(self, local_path: str, subfolder: str = "", overwrite: bool = True) -> str:
        """
        로컬 파일을 원격 ComfyUI의 input 디렉토리로 업로드
        :param local_path: 업로드할 로컬 파일 경로
        :param subfolder: ComfyUI input 내 하위 폴더 (선택)
        :param overwrite: 덮어쓰기 여부
        :return: 원격에 저장된 파일 이름
        """
        p = Path(local_path)
        if not p.exists():
            raise FileNotFoundError(f"업로드할 로컬 파일이 존재하지 않습니다: {local_path}")

        filename = p.name
        url = f"{self.host}/upload/image"

        with open(local_path, "rb") as f:
            files = {"image": (filename, f, "application/octet-stream")}
            data = {"overwrite": "true" if overwrite else "false"}
            if subfolder:
                data["subfolder"] = subfolder

            res = requests.post(url, files=files, data=data, timeout=60)
            res.raise_for_status()
            res_data = res.json()
            remote_name = res_data.get("name", filename)
            logger.info(f"📤 [원격 브릿지] 원격 GPU input으로 파일 업로드 완료: {remote_name} ({p.stat().st_size} bytes)")
            return remote_name

    def download_file(
        self,
        filename: str,
        subfolder: str = "",
        file_type: str = "output",
        target_path: Optional[str] = None
    ) -> str:
        """
        원격 ComfyUI에서 생성된 미디어를 로컬로 스트림 다운로드
        :param filename: 원격 파일명
        :param subfolder: 하위 폴더
        :param file_type: 'output' 또는 'temp'
        :param target_path: 로컬 저장 목표 경로 (None일 경우 임시 캐시 폴더에 저장)
        :return: 로컬에 저장된 파일의 절대 경로
        """
        params = {"filename": filename, "type": file_type}
        if subfolder:
            params["subfolder"] = subfolder

        url = f"{self.host}/view"
        res = requests.get(url, params=params, stream=True, timeout=120)
        res.raise_for_status()

        dest = Path(target_path) if target_path else self.temp_cache_dir / filename
        dest.parent.mkdir(parents=True, exist_ok=True)

        with open(dest, "wb") as f:
            for chunk in res.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

        logger.info(f"📥 [원격 브릿지] 원격 GPU 산출물 다운로드 완료: {dest.name} ({dest.stat().st_size} bytes)")
        return str(dest)

    def dispatch_to_desktop_and_outputs(
        self,
        source_path: str,
        category: str,
        brand: str = "kmarket",
        custom_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        완성된 미디어 파일을:
        1) 로컬 웹 대시보드 outputs 서빙 경로에 배치
        2) 사용자 PC 바탕화면 공식 폴더에 동시 배치
        :return: {"output_path": str, "desktop_path": str}
        """
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"배포할 소스 파일이 없습니다: {source_path}")

        final_name = custom_name or src.name
        brand_kr = "케이마켓" if brand.lower() == "kmarket" else "이지텍스"

        # 1. 로컬 outputs 폴더 배치 (대시보드 실시간 웹 서빙용)
        out_cat_dir = self.outputs_dir / category
        out_cat_dir.mkdir(parents=True, exist_ok=True)
        out_dest = out_cat_dir / final_name
        if src.resolve() != out_dest.resolve():
            shutil.copy2(src, out_dest)

        # 2. 로컬 바탕화면 폴더 배치 (사용자 데스크탑 즉시 열람용)
        from config import (
            DESKTOP_CARDNEWS_KMARKET, DESKTOP_CARDNEWS_EASYTAX,
            DESKTOP_SHORTS_KMARKET, DESKTOP_SHORTS_EASYTAX
        )
        if category == "cardnews":
            desktop_base = DESKTOP_CARDNEWS_KMARKET if brand.lower() == "kmarket" else DESKTOP_CARDNEWS_EASYTAX
        elif category == "shorts":
            desktop_base = DESKTOP_SHORTS_KMARKET if brand.lower() == "kmarket" else DESKTOP_SHORTS_EASYTAX
        else:
            desktop_base = self.desktop_dir / f"{category}_산출물" / brand_kr

        desktop_base.mkdir(parents=True, exist_ok=True)
        desktop_dest = desktop_base / final_name
        shutil.copy2(src, desktop_dest)

        logger.info(f"✨ [동시 배포 완료] 바탕화면: {desktop_dest} │ 웹 대시보드: {out_dest}")
        return {
            "output_path": str(out_dest),
            "desktop_path": str(desktop_dest),
            "web_url": f"/outputs/{category}/{final_name}"
        }
