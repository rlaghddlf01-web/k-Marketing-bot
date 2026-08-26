import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, BASE_URLS
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.notifier import Notifier

logger = logging.getLogger("FreeStuffNotifier")

class FreeStuffNotifier:
    """
    [무인 자동화 5] 매일 아침 '0원 무료 나눔 & 환급 꿀팁' 17개국어 데일리 브리핑 생성기
    """
    def __init__(self, db_mgr: DBManager, notifier: Notifier):
        self.db_mgr = db_mgr
        self.notifier = notifier
        self.output_dir = OUTPUTS_DIR / "briefings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.items = self._load_items()

    def _load_items(self) -> List[Dict[str, Any]]:
        path = DATA_DIR / "kmarket_items.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def generate_daily_briefing(self, target_langs: List[str] = None) -> List[Path]:
        """오늘의 무료나눔 매물 & 환급 팁 데일리 브리핑 생성 및 파일 저장"""
        if not target_langs:
            target_langs = ["ko", "en", "vi", "zh", "uz"]

        free_items = [item for item in self.items if item.get("is_free", False)]
        saved_files = []
        base_domain = BASE_URLS.get("kmarket", "https://k-market.app")

        for lang in target_langs:
            lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
            campaign = UTMTracker.generate_campaign_tag("kmarket", "daily_briefing", lang)
            landing_url = UTMTracker.build_landing_url(
                base_domain=base_domain,
                lang=lang,
                path="welcome",
                source="daily_briefing",
                medium="push_feed",
                campaign=campaign
            )

            lines = [
                f"🎁 [Daily Expat Free Giveaway & Perks Briefing - {lang_info['name']}]",
                f"📅 Today's Verified $0 Free Items in Korea:\n"
            ]
            for idx, it in enumerate(free_items[:3], 1):
                title = it.get("title_en", it.get("title_ko")) if lang != "ko" else it.get("title_ko")
                lines.append(f"{idx}. {title}")
                lines.append(f"   📍 Location: {it.get('location')}")
                lines.append(f"   📦 Type: {it.get('pickup_type')}\n")

            lines.append(f"👉 Claim these free items on K-Market: {landing_url}")
            briefing_text = "\n".join(lines)

            file_path = self.output_dir / f"briefing_{lang}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(briefing_text)

            self.db_mgr.record_history(
                content_type="briefing",
                service_id="kmarket",
                target_lang=lang,
                title="Daily Free Giveaways Briefing",
                content_text=briefing_text,
                target_url=landing_url,
                external_id=f"briefing_{lang}_{len(saved_files)}"
            )
            saved_files.append(file_path)

        logger.info(f"데일리 브리핑 {len(saved_files)}개 언어 파일 생성 완료")
        return saved_files
