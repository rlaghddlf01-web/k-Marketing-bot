"""
PexelsVideoClient - Pexels 공식 Video API 연동 17개국 세로형(9:16) 실제 움직이는 고화질 비디오 공급기
- 언어/국가별 최적 실사 비디오 클립 실시간 검색 & 다운로드
- 스마트폰 사용, 계산기 타이핑, 외국인 근로자/학생 실제 비디오 제공
"""

import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import PEXELS_API_KEY, DATA_DIR

logger = logging.getLogger("PexelsVideoClient")

# 🎯 17개국 언어별 Pexels 실제 비디오 검색 쿼리 매핑
PEXELS_VIDEO_QUERIES: Dict[str, List[str]] = {
    "vi": [
        "vietnamese person using phone vertical",
        "asian person smartphone scrolling",
        "typing on smartphone desk vertical",
        "asian student holding phone smiling"
    ],
    "uz": [
        "person typing on smartphone vertical",
        "industrial worker looking at phone",
        "office worker calculating taxes",
        "person checking mobile app desk"
    ],
    "zh": [
        "asian student using mobile phone",
        "chinese person smartphone vertical",
        "checking bank account on smartphone",
        "typing on calculator desk vertical"
    ],
    "en": [
        "person using smartphone vertical",
        "international student campus phone",
        "typing on calculator tax desk",
        "person checking mobile phone outdoors"
    ],
    "mn": [
        "person scrolling phone screen vertical",
        "asian young adult phone winter",
        "office worker using calculator"
    ],
    "ru": [
        "person checking finances phone vertical",
        "typing on smartphone office",
        "calculator finance documents desk"
    ],
    "th": [
        "thai person smartphone vertical",
        "young worker checking phone",
        "person typing on mobile app"
    ],
    "id": [
        "indonesian person smartphone vertical",
        "young adult using mobile screen",
        "person holding phone desk vertical"
    ],
    "ko": [
        "smartphone screen touch vertical",
        "checking mobile app phone",
        "office calculator typing desk"
    ]
}


class PexelsVideoClient:
    """
    🎬 Pexels 세로형(9:16) 고화질 실제 비디오 공급 클라이언트
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PEXELS_API_KEY
        self.cache_dir = DATA_DIR / "pexels_video_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_portrait_video(self, query: str = "person using smartphone vertical", page: int = 1) -> Optional[Path]:
        """주어진 검색어로 Pexels에서 세로형(portrait) 고화질 실제 비디오(.mp4) 1개 다운로드"""
        if not self.api_key:
            logger.warning("Pexels API 키가 없습니다.")
            return None

        # 캐시 확인
        cache_key = f"{query}_{page}".replace(" ", "_").lower()
        cached_file = self.cache_dir / f"{cache_key}.mp4"
        if cached_file.exists() and cached_file.stat().st_size > 100000:
            logger.info(f"✅ 캐시된 Pexels 비디오 사용: {cached_file.name}")
            return cached_file

        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=5&page={page}"
        req = urllib.request.Request(url, headers={
            "Authorization": self.api_key,
            "User-Agent": "UniversalExpatMarketingEngine/1.0"
        })

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                videos = data.get("videos", [])
                if videos:
                    # 세로형(height > width) 고화질 HD 파일 찾기
                    for v in videos:
                        files = v.get("video_files", [])
                        hd_candidates = [
                            f for f in files
                            if f.get("width", 0) <= f.get("height", 0) and f.get("height", 0) >= 720
                        ]
                        if not hd_candidates:
                            hd_candidates = [f for f in files if f.get("width", 0) <= f.get("height", 0)]

                        if hd_candidates:
                            best_video = hd_candidates[0]
                            video_url = best_video.get("link")
                            if video_url:
                                logger.info(f"다운로드 시작: {best_video.get('width')}x{best_video.get('height')} 비디오...")
                                v_req = urllib.request.Request(video_url, headers={"User-Agent": "Mozilla/5.0"})
                                with urllib.request.urlopen(v_req, timeout=20) as v_resp:
                                    with open(cached_file, "wb") as f:
                                        f.write(v_resp.read())
                                size_mb = round(cached_file.stat().st_size / (1024 * 1024), 2)
                                logger.info(f"✅ Pexels 고화질 비디오 다운로드 성공 [{query}]: {cached_file.name} ({size_mb}MB)")
                                return cached_file
        except Exception as e:
            logger.warning(f"Pexels Video API 호출 실패 ({query}): {e}")

        return None

    def fetch_video_for_lang(self, lang: str = "vi", service_id: str = "easytax") -> Optional[Path]:
        """언어 및 서비스에 맞는 최적의 Pexels 세로형 실제 비디오 1개 획득"""
        import random
        queries = PEXELS_VIDEO_QUERIES.get(lang, PEXELS_VIDEO_QUERIES["en"])
        query = random.choice(queries)
        return self.fetch_portrait_video(query=query, page=random.randint(1, 2))
