"""
TelegramGroupDiscoverer - 🌐 타깃 외국인 텔레그램 공개 그룹 자율 탐색 및 로테이션 큐 매니저
- 국가별/언어별 대형 외국인 공개 그룹 풀 로드 및 관리
- 다국어 키워드 기반 신규 그룹 자동 발굴 및 등록
- 라운드로빈(Round-Robin) 방식으로 최근에 덜 건드린 그룹을 우선 반환
"""

import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DATA_DIR, KST

logger = logging.getLogger("TelegramGroupDiscoverer")

TARGET_GROUPS_FILE = DATA_DIR / "telegram_target_groups.json"

DISCOVERY_KEYWORDS = {
    "uz": ["uzb korea", "koreyadagi ozbeklar", "tashkent seoul", "uzbekistan ansan", "korea viza uzb"],
    "vi": ["du hoc sinh han quoc", "vietnam korea", "viec lam han quoc", "hoi nguoi viet han quoc", "e9 han quoc"],
    "ru": ["работа в корее", "русскоязычные в корее", "узбекистан корея", "жилье в корее", "визы в корею"],
    "mn": ["солонгос дахь монголчууд", "солонгос ажил", "солонгос виз", "солонгос орон сууц"],
    "en": ["expats in seoul", "foreigners in korea", "korea university students", "living in korea", "seoul community"],
    "tl": ["ofw korea", "filipino in korea", "pinoy seoul", "korea jobs pinoy"],
    "th": ["คนไทยในเกาหลี", "ทำงานเกาหลี", "ชีวิตในเกาหลี"],
    "id": ["tki korea", "mahasiswa indonesia korea", "komunitas indonesia korea"]
}


class TelegramGroupDiscoverer:
    """타깃 그룹 자율 관리 및 라운드로빈 로테이션 큐 엔진"""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or TARGET_GROUPS_FILE
        self.groups: List[Dict[str, Any]] = []
        self._load_groups()

    def _load_groups(self):
        """JSON 데이터셋 로드"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.groups = json.load(f)
                logger.info(f"📂 [GroupDiscoverer] {len(self.groups)}개 타깃 그룹 로드 완료")
            except Exception as e:
                logger.error(f"❌ 타깃 그룹 로드 실패: {e}")
                self.groups = []
        else:
            self.groups = []

    def _save_groups(self):
        """JSON 데이터셋 저장"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.groups, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 타깃 그룹 저장 실패: {e}")

    def get_next_target_group(self) -> Optional[Dict[str, Any]]:
        """
        가장 최근에 스크래핑하지 않은(또는 한 번도 안 한) 최우선 활성 그룹 1개 반환 (라운드로빈)
        """
        active_groups = [g for g in self.groups if g.get("is_active", True)]
        if not active_groups:
            return None

        # 1. 한 번도 스크래핑 안 한 그룹 우선
        never_scraped = [g for g in active_groups if not g.get("last_scraped_at")]
        if never_scraped:
            # priority_score 높은 순
            never_scraped.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            return never_scraped[0]

        # 2. last_scraped_at 기준 가장 오래된 그룹 선택
        active_groups.sort(key=lambda x: x.get("last_scraped_at", ""))
        return active_groups[0]

    def record_scraping_result(self, group_id: str, invited_add_count: int = 0):
        """해당 그룹의 마지막 스크래핑 일시 및 초대 누적 수 갱신"""
        now_str = datetime.datetime.now(KST).isoformat()
        for g in self.groups:
            if g.get("id") == group_id or g.get("username") == group_id:
                g["last_scraped_at"] = now_str
                g["invited_count"] = g.get("invited_count", 0) + invited_add_count
                break
        self._save_groups()

    def register_discovered_group(
        self,
        name: str,
        username: str,
        target_country: str = "Global",
        language: str = "en",
        category: str = "discovered"
    ) -> bool:
        """자율 탐색된 신규 공개 그룹 등록 (중복 방지)"""
        clean_user = username.lstrip("@").strip()
        if not clean_user:
            return False

        for g in self.groups:
            if g.get("username", "").lstrip("@").lower() == clean_user.lower():
                return False  # 이미 존재

        new_group = {
            "id": f"disc_{clean_user.lower()}",
            "name": name,
            "username": clean_user,
            "target_country": target_country,
            "language": language,
            "category": category,
            "priority_score": 7,
            "last_scraped_at": None,
            "invited_count": 0,
            "is_active": True
        }
        self.groups.append(new_group)
        self._save_groups()
        logger.info(f"✨ [GroupDiscoverer] 신규 타깃 그룹 자동 발굴 등록: '{name}' (@{clean_user})")
        return True

    def get_all_groups(self) -> List[Dict[str, Any]]:
        return list(self.groups)
