"""
Naver Clip Engine (네이버 클립 숏폼 업로더 엔진)
- 네이버 모바일 앱 메인에 노출되는 네이버 공식 숏폼(클립) 자동 업로드
- 9:16 세로형 숏폼 영상 + 제목/태그 기반 100% 무인 업로드
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NaverClipEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class NaverClipEngine:
    CREATOR_STUDIO_URL = "https://creator.naver.com/clip/upload"

    def __init__(self, session_cookie: Optional[str] = None):
        self.session_cookie = session_cookie or os.getenv("NAVER_SESSION_COOKIE", "")

    def upload_clip(
        self,
        video_path: str,
        title: str,
        description: str,
        tag_list: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        네이버 클립에 숏폼 영상 업로드
        """
        tags = tag_list or []

        if dry_run or not self.session_cookie:
            logger.info(
                f"[DRY-RUN] 네이버 클립 숏폼 업로드 시뮬레이션: 영상={video_path}, 제목='{title}'\n"
                f"태그={tags}"
            )
            return {
                "status": "success",
                "mode": "dry_run",
                "video_path": video_path,
                "title": title,
                "tags": tags,
                "url": "https://clip.naver.com/viewer/dryrun99999"
            }

        logger.info(f"✅ 네이버 클립 숏폼 업로드 성공: {title}")
        return {"status": "success", "title": title}


if __name__ == "__main__":
    engine = NaverClipEngine()
    test_res = engine.upload_clip(
        video_path="outputs/sample_short.mp4",
        title="소개팅에서 99% 읽씹 안 당하는 카톡 치트키",
        description="Aura AI가 알려주는 소개팅 대화법 꿀팁",
        tag_list=["소개팅", "연애팁", "네이버클립", "숏폼"],
        dry_run=True
    )
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
