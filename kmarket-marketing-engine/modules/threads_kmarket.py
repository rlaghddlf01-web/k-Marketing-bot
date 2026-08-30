import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS, DATA_DIR
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager
from core.scenario_director_threads_kmarket import ScenarioDirectorThreadsKMarket

logger = logging.getLogger("KMarketThreads")

class KMarketThreadsPublisher:
    """
    🛒 [K-Market 전용 Meta Threads 바이럴 스레드 무인 자동화 엔진]
    - 2030 유학생 및 재한 외국인을 타깃으로 한 타래(Thread)형 바이럴 포스팅
    - 1번 본문: 강력한 후킹 ("한국 졸업생들이 0원에 버리고 가는 가구 득템하는 법 🧵👇")
    - 2~3번 타래: 신촌/안암/혜화 실물 매물 제보 & 안전 직거래 꿀팁
    - 마지막 타래: K-Market 17개국어 자동번역 앱 바로가기 UTM 링크
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.scenario_director = ScenarioDirectorThreadsKMarket()
        self.output_dir = OUTPUTS_DIR / "threads" / "kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)

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

    def publish_daily_threads(self, target_langs: Optional[List[str]] = None) -> Dict[str, Any]:
        """K-Market 타래형 바이럴 스레드 생성 및 배포 (3개 언어 순환)"""
        if target_langs is None:
            target_langs = self._get_next_rotation_langs(count=3)
        published_threads = []
        base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app")

        for lang in target_langs:
            campaign = UTMTracker.generate_campaign_tag("kmarket", f"threads_{lang}", lang)
            landing_url = UTMTracker.build_landing_url(
                base_domain=base_domain,
                lang=lang,
                path="welcome",
                source="threads",
                medium="viral_story_thread",
                campaign=campaign
            )

            # 1. 3~4단 타래(Thread) 포스트 생성
            thread_data = self._generate_kmarket_thread(lang, landing_url)

            # 2. 산출물 파일 저장 (JSON & Markdown)
            filename_base = f"kmarket_threads_{lang}_{int(time.time())}"
            json_path = self.output_dir / f"{filename_base}.json"
            md_path = self.output_dir / f"{filename_base}.md"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(thread_data, f, ensure_ascii=False, indent=2)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(thread_data.get("full_markdown", ""))

            # 3. DB 발행 이력 기록
            self.db_mgr.record_history(
                content_type="threads_post",
                service_id="kmarket",
                target_lang=lang,
                title=thread_data.get("hook_title", ""),
                content_text=thread_data.get("full_markdown", "")[:500] + "...",
                target_url=landing_url,
                external_id=f"km_threads_{lang}_{int(time.time())}"
            )

            published_threads.append({
                "lang": lang,
                "title": thread_data.get("hook_title", ""),
                "posts_count": len(thread_data.get("posts", [])),
                "file": json_path.name
            })
            logger.info(f"🛒 [K-Market Threads] {lang.upper()} 타래 포스트 생성 완료: {thread_data.get('hook_title', '')}")

        return {
            "success": True,
            "brand": "kmarket",
            "count": len(published_threads),
            "threads": published_threads,
            "message": f"🛒 [K-Market] {len(published_threads)}개 언어 Threads 바이럴 타래가 성공적으로 배포되었습니다!"
        }

    def _generate_kmarket_thread(self, lang: str, landing_url: str) -> Dict[str, Any]:
        """언어별 맞춤 타래형 스레드 콘텐츠 생성"""
        if lang == "vi":
            posts = [
                "Bí quyết sinh tồn cho du học sinh và người lao động Việt Nam tại Hàn Quốc: Đừng bao giờ mua đồ nội thất mới đắt đỏ khi mới sang! 🧵👇 #DuHocHanQuoc #KMarket #0won",
                "1/ Mùa tốt nghiệp (tháng 2 & 8), sinh viên tại Yonsei, Korea Univ tặng lại 0 Won rất nhiều giường, bàn học, tủ lạnh mini còn cực mới thay vì vứt bỏ mất phí.",
                "2/ Cách giao dịch an toàn: Luôn hẹn nhận đồ trực tiếp tại cổng trường hoặc ga tàu, kiểm tra xác thực người dùng và tuyệt đối không chuyển cọc trước.",
                f"3/ Kho đồ 0 Won miễn phí và chat dịch tiếng Việt tự động đã có sẵn trên app K-Market:\n👉 Xem ngay tại đây: {landing_url}"
            ]
            hook = "Bí quyết nhận đồ nội thất 0 Won & sinh tồn tại Hàn Quốc"
        elif lang == "en":
            posts = [
                "Moving to Korea or graduating soon? Here is how international students get 0 KRW verified furniture and appliances in Seoul 🧵👇 #KoreaExpat #SeoulLife #KMarket",
                "1/ Every semester, graduating expats leave behind barely-used desks, chairs, and mini-fridges in Sinchon, Anam, and Hongdae. Instead of paying trash disposal fees, they give them away for free.",
                "2/ Anti-scam tip: Always trade in public campus spots, verify user profiles, and use auto-translated chat to overcome language barriers.",
                f"3/ Browse today's live 0 KRW giveaways with 17-language instant chat on K-Market:\n👉 Claim your items here: {landing_url}"
            ]
            hook = "How international students get 0 KRW verified furniture in Seoul"
        else: # ko
            posts = [
                "재한 외국인 유학생 & 직장인을 위한 원룸 이사 꿀팁: 0원 무료나눔 가구 득템하는 법 🧵👇 #KMarket #0원나눔 #외국인생활",
                "1/ 신촌, 안암, 혜화 대학가 졸업 시즌마다 침대, 책상, 소형 가전이 0원에 대량 등록됩니다. 폐기물 스티커 비용 대신 필요한 외국인에게 무료 나눔하는 문화!",
                "2/ 안전 직거래 수칙: 기숙사 정문 앞 직거래, 신원 인증 확인, 17개국 자동번역 채팅으로 소통 단절 해결.",
                f"3/ 오늘 등록된 전국 0원 나눔 실물 매물 실시간 확인:\n👉 K-Market 바로가기: {landing_url}"
            ]
            hook = "외국인 유학생 0원 나눔 가구 득템 및 안전 직거래 가이드"

        full_md = "\n\n---\n\n".join([f"**Post {i+1}**\n{p}" for i, p in enumerate(posts)])
        return {
            "hook_title": hook,
            "posts": posts,
            "full_markdown": full_md,
            "landing_url": landing_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
