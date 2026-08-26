"""
PexelsClient - Pexels 공식 API 연동 17개국 고화질 세로형(9:16) 실사/목업 이미지 공급기
- 언어/국가별 최적 실사 키워드 자동 매핑
- 스마트폰 목업, 통장 확인, 실제 다국적 인물 고화질 사진 실시간 다운로드 & 캐싱
"""

import json
import logging
import urllib.request
import io
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
from config import PEXELS_API_KEY, DATA_DIR

logger = logging.getLogger("PexelsClient")

# 🎯 17개국 언어별 Pexels 최적 검색 쿼리 매핑
PEXELS_QUERIES_BY_LANG: Dict[str, List[str]] = {
    "vi": [
        "vietnamese person smartphone",
        "southeast asian student phone",
        "vietnamese worker smiling",
        "asian person holding phone vertical"
    ],
    "uz": [
        "central asian man smartphone",
        "young male worker industrial",
        "person holding smartphone table",
        "office worker calculator"
    ],
    "zh": [
        "asian student library smartphone",
        "chinese young professional phone",
        "asian person checking mobile banking",
        "modern asian youth phone"
    ],
    "en": [
        "international student campus smartphone",
        "person checking bank app phone",
        "phone screen mockup hand vertical",
        "young professional laptop coffee"
    ],
    "mn": [
        "asian young adult phone winter",
        "person holding smartphone mockup",
        "asian student modern casual",
        "office desk calculator phone"
    ],
    "ru": [
        "person checking finances phone",
        "young professional office mobile",
        "calculator tax documents table",
        "hand holding smartphone vertical"
    ],
    "th": [
        "thai young adult smartphone",
        "southeast asian person mobile app",
        "young worker factory smiling",
        "phone screen vertical mockup"
    ],
    "id": [
        "indonesian student smartphone",
        "southeast asian worker mobile",
        "person holding phone vertical desk",
        "checking mobile banking phone"
    ],
    "ne": [
        "south asian young man phone",
        "worker factory smartphone",
        "person holding phone vertical",
        "calculating tax finance papers"
    ],
    "km": [
        "southeast asian worker smiling phone",
        "person holding smartphone vertical",
        "young adult checking mobile screen"
    ],
    "tl": [
        "filipino student smartphone",
        "young professional smiling phone",
        "hand holding phone screen mockup"
    ],
    "my": [
        "southeast asian student mobile",
        "young worker checking smartphone"
    ],
    "bn": [
        "south asian researcher smartphone",
        "young man checking phone banking"
    ],
    "ja": [
        "japanese student smartphone clean",
        "asian professional checking phone"
    ],
    "es": [
        "hispanic student smartphone campus",
        "young person holding phone vertical"
    ],
    "ar": [
        "middle eastern student smartphone",
        "person checking finances phone"
    ],
    "ko": [
        "korean student smartphone mockup",
        "checking mobile app smartphone hand",
        "desk calculator finance documents"
    ]
}


class PexelsClient:
    """
    📸 Pexels 고화질 세로형(9:16) 실사 사진 공급 클라이언트
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PEXELS_API_KEY
        self.cache_dir = DATA_DIR / "pexels_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Image.Image] = {}

    def fetch_portrait_photo(self, query: str = "person smartphone vertical", page: int = 1) -> Optional[Image.Image]:
        """주어진 검색어로 Pexels에서 세로형(portrait) 고화질 사진 1장 다운로드"""
        if not self.api_key:
            logger.warning("Pexels API 키가 설정되지 않았습니다.")
            return None

        # 캐시 확인
        cache_key = f"{query}_{page}".replace(" ", "_").lower()
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key].copy()

        cached_file = self.cache_dir / f"{cache_key}.jpg"
        if cached_file.exists():
            try:
                img = Image.open(cached_file).convert("RGB")
                self._memory_cache[cache_key] = img
                return img.copy()
            except Exception:
                pass

        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=5&page={page}"
        req = urllib.request.Request(url, headers={
            "Authorization": self.api_key,
            "User-Agent": "UniversalExpatMarketingEngine/1.0"
        })

        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                photos = data.get("photos", [])
                if photos:
                    # 'large' 또는 'large2x' 고화질 URL 선택
                    photo_url = photos[0].get("src", {}).get("large") or photos[0].get("src", {}).get("medium")
                    if photo_url:
                        img_req = urllib.request.Request(photo_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                            img_bytes = img_resp.read()
                            with open(cached_file, "wb") as f:
                                f.write(img_bytes)
                            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                            self._memory_cache[cache_key] = img
                            logger.info(f"✅ Pexels 고화질 실사 로드 성공 [{query}]: {cached_file.name}")
                            return img.copy()
        except Exception as e:
            logger.warning(f"Pexels API 호출 실패 ({query}): {e}")

        return None

    def fetch_photo_for_lang(self, lang: str = "vi", service_id: str = "easytax") -> Optional[Image.Image]:
        """언어 및 서비스에 최적화된 고화질 Pexels 실사 사진 1장 획득"""
        import random
        queries = PEXELS_QUERIES_BY_LANG.get(lang, PEXELS_QUERIES_BY_LANG["en"])
        query = random.choice(queries)
        return self.fetch_portrait_photo(query=query, page=random.randint(1, 3))
