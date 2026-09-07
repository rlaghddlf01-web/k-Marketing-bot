# -*- coding: utf-8 -*-
"""
KMarketThreadsPublisher - 🛒 [K-Market 전용 Meta Threads 17개국어 바이럴 무인 자동화 엔진]
- 대한민국 표준시(KST) 하루 3회 정시 하이브리드 바이럴 체계:
  1회차 (11:00 KST): 📸 [카드뉴스 5장 첨부형] (링크 0% 후킹 본문 + 0.1초 링크 답글 댓글)
  2회차 (16:30 KST): 📝 [순수 텍스트 리얼 썰형] (광고 티 0% 3단 타래: 실화 썰 -> 팩트 요약 -> 링크 안내)
  3회차 (21:30 KST): 📸 [야간 모바일 카드뉴스형] (여유 시간 탐색 맞춤 + 0.1초 링크 답글 댓글)
- 제미나이 무료 키(Gemini 3.1 Flash-Lite) 100% 활용 (추가 비용 0원)
- 바탕화면 카드뉴스 산출물(1080x1350) 자동 탐색 및 재사용 (추가 비용 0원)
- 17개국어 순환(Rotation) 배포 지원
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS, DATA_DIR, get_now_kst_str
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.supabase_manager import SupabaseManager
from core.scenario_director_threads_kmarket import ScenarioDirectorThreadsKMarket
from core.gemini_threads_writer import GeminiThreadsWriter
from core.auto_publishers.cardnews_multi_publisher import ThreadsCardPublisher

logger = logging.getLogger("KMarketThreads")


class KMarketThreadsPublisher:
    """🛒 [K-Market 전용 Meta Threads 바이럴 무인 자동화 퍼블리셔]"""

    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.writer = GeminiThreadsWriter(service_id="kmarket")
        self.scenario_director = ScenarioDirectorThreadsKMarket()
        self.output_dir = OUTPUTS_DIR / "threads" / "kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_cardnews_dir = Path(r"C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓")

        creds = self._load_credentials()
        self.threads_publisher = ThreadsCardPublisher(creds)

    def _load_credentials(self) -> Dict[str, str]:
        env_path = BASE_DIR / ".env"
        creds = {}
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            creds[k.strip()] = v.strip()
            except Exception:
                pass
        return creds

    def _detect_current_slot(self) -> str:
        """대한민국 표준시(KST) 기준 하루 3회 정시 슬롯 자동 판별"""
        kst = timezone(timedelta(hours=9))
        hour = datetime.now(kst).hour
        if hour < 14:
            return "morning"    # 11:00 회차
        elif hour < 19:
            return "afternoon"  # 16:30 회차
        else:
            return "evening"    # 21:30 회차

    def _get_next_rotation_langs(self, count: int = 3) -> List[str]:
        """17개 언어 중 다음 순번의 3개 언어 순환 선택 (도배 방지 로테이션)"""
        all_langs = list(LANGUAGES.keys())
        state_file = DATA_DIR / "threads_rotation_state_kmarket.json"
        curr_idx = 0
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    curr_idx = json.load(f).get("index", 0)
            except Exception:
                curr_idx = 0

        selected = []
        for i in range(count):
            idx = (curr_idx + i) % len(all_langs)
            selected.append(all_langs[idx])

        next_idx = (curr_idx + count) % len(all_langs)
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump({"index": next_idx}, f)
        except Exception:
            pass

        return selected

    def _find_cardnews_images(self, lang: str) -> List[str]:
        """바탕화면 카드뉴스 산출물 폴더에서 5장 이미지 탐색 (추가 비용 0원 재사용)"""
        images = []
        if self.desktop_cardnews_dir.exists():
            # 1. 언어 맞춤 이미지 탐색 (예: kmarket_cardnews_ko_s*.jpg)
            pattern = f"kmarket_cardnews_{lang}_s*.jpg"
            found = sorted(self.desktop_cardnews_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
            if len(found) >= 5:
                images = [str(f) for f in found[:5]]
            elif found:
                images = [str(f) for f in found]

            # 2. 부족할 경우 다른 언어 고화질 카드뉴스 슬라이드 대체 활용
            if len(images) < 5:
                fallback_found = sorted(self.desktop_cardnews_dir.glob("kmarket_cardnews_*_s*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
                if len(fallback_found) >= 5:
                    images = [str(f) for f in fallback_found[:5]]

        # 3. 프로젝트 내부 outputs/cardnews/kmarket 폴백 탐색
        if len(images) < 5:
            proj_dir = OUTPUTS_DIR / "cardnews" / "kmarket"
            if proj_dir.exists():
                proj_found = sorted(proj_dir.glob(f"*{lang}*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
                if len(proj_found) >= 5:
                    images = [str(f) for f in proj_found[:5]]

        return images

    def publish_daily_threads(
        self,
        target_langs: Optional[List[str]] = None,
        time_slot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        K-Market 타래형 바이럴 스레드 생성 및 배포
        - target_langs: 지정 언어 목록 (None일 경우 17개 언어 순환 3개 선택)
        - time_slot: "morning"(11:00 카드뉴스), "afternoon"(16:30 순수 썰), "evening"(21:30 카드뉴스). None일 경우 자동 감지
        """
        if time_slot is None:
            time_slot = self._detect_current_slot()

        if target_langs is None:
            target_langs = self._get_next_rotation_langs(count=3)

        published_threads = []
        base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")

        logger.info(f"🧵 [K-Market Threads] 하루 3회 스케줄러 가동: time_slot={time_slot}, target_langs={target_langs}")

        for lang in target_langs:
            campaign = UTMTracker.generate_campaign_tag("kmarket", f"threads_{time_slot}_{lang}", lang)
            landing_url = UTMTracker.build_landing_url(
                base_domain=base_domain,
                lang=lang,
                path="",
                source="threads",
                medium=f"viral_{time_slot}_thread",
                campaign=campaign
            )

            # 1. 시나리오 테마 추출
            scenario = self.scenario_director.get_thread_scenario()

            # 2. 제미나이 무료 키 기반 17개국어 맞춤 타래 생성 (추가 비용 0원)
            thread_data = self.writer.generate_thread_package(
                lang=lang,
                time_slot=time_slot,
                theme=scenario,
                landing_url=landing_url
            )

            posts = thread_data.get("posts", [])
            hook_title = thread_data.get("hook_title", "")
            post_type = thread_data.get("post_type", "cardnews_attached" if time_slot != "afternoon" else "pure_story")

            # 3. 아침/저녁 슬롯: 카드뉴스 5장 이미지 자동 탐색 및 첨부
            attached_images = []
            if time_slot in ["morning", "evening"]:
                attached_images = self._find_cardnews_images(lang)

            # 4. 종합 마크다운 문서 빌드
            md_lines = [
                f"# 🛒 K-Market Meta Threads - [{time_slot.upper()} Slot]",
                f"- **언어**: {lang.upper()}",
                f"- **타입**: {post_type} ({'📸 카드뉴스 5장 첨부형' if attached_images else '📝 텍스트 썰형'})",
                f"- **랜딩 URL**: {landing_url}",
                f"- **생성 일시**: {get_now_kst_str()}",
                "",
                "---",
                ""
            ]

            if attached_images:
                md_lines.append(f"### 📸 첨부된 카드뉴스 이미지 ({len(attached_images)}장):")
                for img_p in attached_images:
                    md_lines.append(f"- `{img_p}`")
                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")

            for idx, p in enumerate(posts):
                if idx == 0:
                    role_label = "1번 메인 글 (링크 0% 알고리즘 극대화)"
                elif idx == 1 and time_slot == "afternoon":
                    role_label = "2번 팩트/노하우 요약 답글"
                else:
                    role_label = f"{idx+1}번 답글 (전환 링크 안내 댓글)"

                md_lines.append(f"### 🧵 Post #{idx+1} [{role_label}]")
                md_lines.append(p)
                md_lines.append("")

            full_md = "\n".join(md_lines)
            thread_data["full_markdown"] = full_md
            thread_data["attached_images"] = attached_images
            thread_data["landing_url"] = landing_url
            thread_data["created_at"] = get_now_kst_str()

            # 5. 산출물 파일 저장 (JSON & Markdown)
            timestamp = int(time.time())
            filename_base = f"kmarket_threads_{lang}_{time_slot}_{timestamp}"
            json_path = self.output_dir / f"{filename_base}.json"
            md_path = self.output_dir / f"{filename_base}.md"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(thread_data, f, ensure_ascii=False, indent=2)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(full_md)

            # 6. DB 이력 기록
            try:
                self.db_mgr.record_history(
                    content_type="threads_post",
                    service_id="kmarket",
                    target_lang=lang,
                    title=hook_title,
                    content_text=full_md[:500] + "...",
                    target_url=landing_url,
                    external_id=f"km_threads_{lang}_{time_slot}_{timestamp}"
                )
            except Exception as e:
                logger.warning(f"DB 이력 기록 실패: {e}")

            # 7. Meta Threads API 자동 송출 or 스테이징 패키징
            main_post = posts[0] if posts else ""
            reply_post = posts[-1] if len(posts) > 1 else landing_url
            card_payload = {
                "service_id": "kmarket",
                "lang": lang,
                "caption": main_post,
                "landing_url": landing_url,
                "image_paths": attached_images,
                "channels": {
                    "threads": {
                        "main_post": main_post,
                        "reply_link": reply_post
                    }
                }
            }
            pub_res = self.threads_publisher.publish(card_payload)

            published_threads.append({
                "lang": lang,
                "time_slot": time_slot,
                "title": hook_title,
                "post_type": post_type,
                "posts_count": len(posts),
                "images_count": len(attached_images),
                "file": json_path.name,
                "publish_status": pub_res.get("status", "ready_staged")
            })
            logger.info(f"🛒 [K-Market Threads] [{time_slot}] {lang.upper()} 타래 포스트 완료: {hook_title} (이미지 {len(attached_images)}장)")

        return {
            "success": True,
            "brand": "kmarket",
            "time_slot": time_slot,
            "count": len(published_threads),
            "threads": published_threads,
            "message": f"🛒 [K-Market] [{time_slot.upper()}] {len(published_threads)}개 언어 Threads 타래가 성공적으로 생성 및 배포되었습니다!"
        }
