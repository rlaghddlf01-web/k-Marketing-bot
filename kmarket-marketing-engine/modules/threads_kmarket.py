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
        """언어별 맞춤 50:50 순수 원룸/생활 정보 vs 구글 'k-market korea' 검색 유도 스레드 콘텐츠 생성"""
        import random
        # 50:50 확률로 순수 정보 타래(Type 1) vs 구글 검색 유도 타래(Type 2)
        is_pure_info = (random.random() < 0.50)

        if is_pure_info:
            # 🌿 TYPE 1: 100% 순수 생활 정보성 타래 (홍보 0%, URL 0개, 검색유도 0개)
            if lang == "vi":
                posts = [
                    "3 mẹo tiết kiệm tiền triệu khi thuê phòng trọ và vứt rác tại Hàn Quốc 🧵👇 #DuHocHanQuoc #KinhNghiemSong #SeoulLife",
                    "1/ Vứt rác cồng kềnh (bàn, ghế, nệm): Đừng bao giờ vứt bừa bãi! Phải ra cửa hàng tiện lợi mua tem dán rác thải lớn (대형폐기물 스티커) hoặc quét mã QR dán lên để tránh bị phạt 100,000 won.",
                    "2/ Tiền cọc phòng (보증금): Khi ký hợp đồng nhà, nhớ đi làm ngay 'Xác nhận ngày chuyển đến' (확정일자) tại trung tâm 주민센터 để bảo vệ 100% tiền cọc khi trả phòng.",
                    "3/ Đồ dùng mùa đông: Máy sưởi, chăn điện nên mua vào tháng 10 hoặc xin lại của các anh chị khóa trên tốt nghiệp về nước để tiết kiệm chi phí."
                ]
                hook = "3 mẹo tiết kiệm tiền triệu khi thuê phòng & sinh sống tại Hàn Quốc"
            elif lang == "en":
                posts = [
                    "3 money-saving studio room hacks every foreigner in Korea needs to know 🧵👇 #KoreaLiving #ExpatHacks #SeoulStudio",
                    "1/ Bulky Waste Disposal: Never dump desks or mattresses on the street! Buy a disposal sticker (대형폐기물 스티커) at any convenience store to avoid a 100,000 KRW fine.",
                    "2/ Protect Your Deposit: The moment you move in, visit the local 주민센터 to get the official 'Fixed Date' stamp (확정일자). This legally protects your housing deposit.",
                    "3/ Winter Heating (난방): Set your boiler to '외출' (away mode) rather than turning it off completely when leaving the house — it saves massive gas bill costs."
                ]
                hook = "3 Money-Saving Studio Living & Deposit Protection Hacks in Korea"
            else: # ko
                posts = [
                    "재한 외국인 유학생 & 사회초년생을 위한 원룸 자취 절약 꿀팁 3가지 🧵👇 #자취꿀팁 #원룸생활 #이사팁",
                    "1/ 대형 폐기물 배출: 가구/가전 버릴 땐 편의점에서 종량제 스티커를 사서 붙이거나 구청 앱으로 신고해야 10만원 과태료를 피할 수 있습니다.",
                    "2/ 전월세 보증금 보호: 이사 당일 주민센터에서 전입신고와 함께 '확정일자'를 받아야 보증금을 안전하게 법적으로 보호받습니다.",
                    "3/ 난방법 가스비 절약: 외출 시 보일러를 끄지 말고 '외출 모드'나 20도 정도로 유지하는 것이 난방비 폭탄을 막는 비결입니다."
                ]
                hook = "외국인 유학생 및 1인 가구 원룸 자취 절약 & 보증금 보호 수칙"

        else:
            # 🎯 TYPE 2: 80% 나눔 꿀팁 + 구글 'k-market korea' 검색 유도 타래 (노링크, 스팸 0%)
            if lang == "vi":
                posts = [
                    "Bí quyết sinh tồn cho du học sinh và người lao động Việt Nam: Cách nhận đồ nội thất 0 Won tại Hàn Quốc 🧵👇 #DuHocHanQuoc #KMarket #0wonKorea",
                    "1/ Mùa tốt nghiệp và chuyển phòng (tháng 2 & 8), sinh viên tại các trường đại học lớn tặng lại 0 Won rất nhiều bàn học, ghế, tủ lạnh mini còn cực kỳ mới.",
                    "2/ Mẹo nhận đồ an toàn: Luôn hẹn nhận đồ trực tiếp tại cổng trường hoặc ga tàu, kiểm tra tình trạng thực tế và không bao giờ chuyển tiền đặt cọc trước.",
                    "3/ Muốn xem danh sách các món đồ 0 Won và đồ gia dụng cũ đang được tặng hôm nay, bạn hãy lên Google tìm kiếm: 'k-market korea' nhé!"
                ]
                hook = "Bí quyết nhận đồ nội thất 0 Won & sinh tồn tiết kiệm tại Hàn Quốc"
            elif lang == "en":
                posts = [
                    "Moving to Korea or graduating soon? Here is how international students get 0 KRW verified furniture in Seoul 🧵👇 #KoreaExpat #SeoulLife #ExpatHacks",
                    "1/ Every semester, graduating expats leave behind barely-used desks, chairs, and mini-fridges in university areas like Sinchon, Anam, and Hongdae for free.",
                    "2/ Anti-scam tip: Always trade in open campus meetup spots, check seller profiles, and use auto-translated chat to overcome language barriers.",
                    "3/ Want to browse today's live 0 KRW giveaways and moving sales? Just search 'k-market korea' on Google to check the listings!"
                ]
                hook = "How international students get 0 KRW verified furniture in Seoul"
            else: # ko
                posts = [
                    "재한 외국인 유학생 & 직장인을 위한 원룸 이사 꿀팁: 0원 무료나눔 가구 득템하는 법 🧵👇 #0원나눔 #무빙세일 #외국인생활",
                    "1/ 신촌, 안암, 혜화 대학가 졸업 시즌마다 침대, 책상, 소형 가전이 0원에 대량 등록됩니다. 버리는 비용 대신 필요한 이웃에게 무료 나눔하는 문화!",
                    "2/ 안전 직거래 수칙: 기숙사/지하철역 앞 직거래, 신원 인증 확인, 17개국 자동번역 채팅으로 언어 장벽 해결.",
                    "3/ 오늘 실시간으로 올라온 0원 무료나눔 가전/가구를 확인해보려면, 구글에서 'k-market korea' 검색해보시면 바로 보실 수 있습니다!"
                ]
                hook = "외국인 유학생 0원 나눔 가구 득템 및 안전 직거래 가이드"

        full_md = "\n\n---\n\n".join([f"**Post {i+1}**\n{p}" for i, p in enumerate(posts)])
        return {
            "hook_title": hook,
            "is_pure_info": is_pure_info,
            "posts": posts,
            "full_markdown": full_md,
            "landing_url": landing_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
