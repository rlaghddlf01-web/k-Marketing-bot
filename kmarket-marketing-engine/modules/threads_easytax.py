import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS, DATA_DIR
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager
from core.scenario_director_threads_easytax import ScenarioDirectorThreadsEasyTax

logger = logging.getLogger("EasyTaxThreads")

class EasyTaxThreadsPublisher:
    """
    💰 [EasyTax (KTRS) 전용 Meta Threads 세무/환급 바이럴 자동화 엔진]
    - E-9 중소기업 근로자 및 D-2 유학생을 타깃으로 한 합법 세무 권리 타래 포스팅
    - 1번 본문: 강력한 후킹 ("외국인 근로자 90% 소득세 감면 권리, 모르면 매년 200만원 손해 🧵👇")
    - 2~3번 타래: 조특법 제30조 요건, D-2 알바비 3.3% 100% 환급, 5개년 소급 경정청구
    - 마지막 타래: 선입금 0원 국세청 공인 대리 EasyTax 무료 계산기 UTM 링크
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        self.scenario_director = ScenarioDirectorThreadsEasyTax()
        self.output_dir = OUTPUTS_DIR / "threads" / "easytax"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_next_rotation_langs(self, count: int = 3) -> List[str]:
        """17개 언어 중 다음 순번의 3개 언어 순환 선택 (도배 방지 로테이션)"""
        all_langs = list(LANGUAGES.keys())
        state_file = DATA_DIR / "threads_rotation_state_easytax.json"
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
        """EasyTax 타래형 세무 환급 스레드 생성 및 배포 (3개 언어 순환)"""
        if target_langs is None:
            target_langs = self._get_next_rotation_langs(count=3)
        published_threads = []
        base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app")

        for lang in target_langs:
            campaign = UTMTracker.generate_campaign_tag("easytax", f"threads_{lang}", lang)
            landing_url = UTMTracker.build_service_landing_url(
                service_id="easytax",
                base_domain=base_domain,
                lang=lang,
                path="",
                source="threads",
                medium="viral_tax_thread",
                campaign=campaign
            )

            # 1. 3~4단 세무 타래(Thread) 포스트 생성
            thread_data = self._generate_easytax_thread(lang, landing_url)

            # 2. 산출물 파일 저장 (JSON & Markdown)
            filename_base = f"easytax_threads_{lang}_{int(time.time())}"
            json_path = self.output_dir / f"{filename_base}.json"
            md_path = self.output_dir / f"{filename_base}.md"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(thread_data, f, ensure_ascii=False, indent=2)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(thread_data.get("full_markdown", ""))

            # 3. DB 발행 이력 기록
            self.db_mgr.record_history(
                content_type="threads_post",
                service_id="easytax",
                target_lang=lang,
                title=thread_data.get("hook_title", ""),
                content_text=thread_data.get("full_markdown", "")[:500] + "...",
                target_url=landing_url,
                external_id=f"tax_threads_{lang}_{int(time.time())}"
            )

            published_threads.append({
                "lang": lang,
                "title": thread_data.get("hook_title", ""),
                "posts_count": len(thread_data.get("posts", [])),
                "file": json_path.name
            })
            logger.info(f"💰 [EasyTax Threads] {lang.upper()} 세무 타래 포스트 생성 완료: {thread_data.get('hook_title', '')}")

        return {
            "success": True,
            "brand": "easytax",
            "count": len(published_threads),
            "threads": published_threads,
            "message": f"💰 [EasyTax] {len(published_threads)}개 언어 Threads 세무 타래가 성공적으로 배포되었습니다!"
        }

    def _generate_easytax_thread(self, lang: str, landing_url: str) -> Dict[str, Any]:
        """언어별 맞춤 50:50 순수 생활/비자 정보 vs 구글 'ktrs tax' 검색 유도 스레드 콘텐츠 생성"""
        import random
        # 50:50 확률로 순수 정보 타래(Type 1) vs 구글 검색 유도 타래(Type 2)
        is_pure_info = (random.random() < 0.50)

        if is_pure_info:
            # 🌿 TYPE 1: 100% 순수 정보성 타래 (홍보 0%, URL 0개, 검색유도 0개)
            if lang == "vi":
                posts = [
                    "3 điều cực kỳ quan trọng về Visa E-9 và D-2 tại Hàn Quốc bạn nhất định phải nhớ 🧵👇 #KinhNghiemHanQuoc #VisaE9 #DuHocHanQuoc",
                    "1/ Gia hạn thẻ ARC: Hãy đặt lịch hẹn trên Hikorea trước ngày hết hạn ít nhất 2-3 tháng. Quá hạn dù chỉ 1 ngày bạn sẽ bị phạt hành chính rất nặng.",
                    "2/ Bảo hiểm y tế quốc dân (NHIS): Tiền bảo hiểm tự động trừ hàng tháng. Nếu đi khám tại phòng khám nội khoa (내과) gần nhà, chi phí chỉ khoảng 5,000 - 10,000 won.",
                    "3/ Đổi nơi làm việc (E-9): Phải hoàn tất đăng ký tại Trung tâm Việc làm (고용센터) trong vòng 3 tháng kể từ ngày nghỉ việc cũ."
                ]
                hook = "3 lưu ý sống còn về Visa E-9 & D-2 tại Hàn Quốc (Cập nhật 2026)"
            elif lang == "en":
                posts = [
                    "3 essential survival tips for foreign workers & students living in South Korea 🧵👇 #KoreaTips #ExpatLife #LifeInKorea",
                    "1/ ARC Renewal: Always book your appointment on HiKorea at least 2 months before expiration. Overstaying by even one day results in heavy fines.",
                    "2/ National Health Insurance (NHIS): Standard clinic visits (내과/이비인후과) usually cost under 10,000 KRW with insurance. Don't avoid going to the doctor!",
                    "3/ Moving registration (전입신고): You must report your new address within 14 days of moving at your local community center (주민센터)."
                ]
                hook = "3 Essential Expat Survival & Bureaucracy Tips in Korea (2026)"
            else: # ko
                posts = [
                    "외국인 유학생(D-2) & 근로자(E-9) 한국 생활 필수 행정 꿀팁 3가지 🧵👇 #외국인생활 #한국생활꿀팁 #비자연장",
                    "1/ 외국인등록증(ARC) 연장: 만료일 2~3달 전 하이코리아에서 사전 방문예약 필수. 단 하루만 늦어도 과태료가 부과됩니다.",
                    "2/ 국민건강보험 활용: 동네 내과/이비인후과 진료비는 보험 적용 시 5,000~10,000원 선으로 매우 저렴하니 아플 때 참지 마세요.",
                    "3/ 이사 후 전입신고: 이사한 날로부터 14일 이내 관할 주민센터에 주소지 변경 신고를 반드시 완료해야 합니다."
                ]
                hook = "외국인 유학생 및 근로자 한국 생활 필수 행정 수칙 3가지"

        else:
            # 🎯 TYPE 2: 80% 세법 팩트 + 구글 'ktrs tax' 검색 유도 타래 (노링크, 스팸 0%)
            if lang == "vi":
                posts = [
                    "Lao động Việt Nam visa E-9, E-7 và du học sinh D-2 tại Hàn Quốc: Quyền nhận lại hàng triệu won tiền thuế thu nhập 🧵👇 #HoanThueHanQuoc #ThueThuNhap #E9Korea",
                    "1/ Điều 30 Luật Miễn giảm thuế đặc biệt (조특법 제30조): Người lao động nước ngoài làm việc tại doanh nghiệp SME được GIẢM 90% thuế thu nhập trong 5 năm đầu (tối đa 2.000.000 KRW/năm).",
                    "2/ Du học sinh D-2 làm thêm bị trừ 3.3% thuế hoặc lao động đã về nước từ 2021-2025 đều có quyền nộp đơn yêu cầu hoàn thuế 5 năm (경정청구).",
                    "3/ Muốn tự kiểm tra xem mình được hoàn lại bao nhiêu tiền, bạn chỉ cần lên Google tìm kiếm: 'ktrs tax' hoặc 'ktrs korea' để xem bảng tính miễn phí nhé!"
                ]
                hook = "Quyền giảm 90% thuế thu nhập (Điều 30) & Hoàn thuế 5 năm cho lao động E-9"
            elif lang == "en":
                posts = [
                    "Foreign workers & international students in Korea: You might be leaving up to 2,000,000 KRW in unclaimed tax refunds every year 🧵👇 #KoreaTax #ExpatFinance #KoreaRefund",
                    "1/ Under Article 30 of the Restriction of Special Taxation Act, foreign employees in Korean SMEs are entitled to a 90% INCOME TAX REDUCTION for their first 5 years.",
                    "2/ Worked part-time with 3.3% withholding tax under D-2 visa? Or missed filing between 2021-2025? You can legally claim retroactive refunds for the past 5 years.",
                    "3/ Want to check your estimated refund amount for free? Just search 'ktrs tax' or 'ktrs korea' on Google to calculate it in 3 minutes!"
                ]
                hook = "90% Income Tax Exemption & 5-Year Retroactive Refund Guide for Expats"
            else: # ko
                posts = [
                    "외국인 근로자(E-9/E-7) 및 유학생(D-2) 국세청 소득세 90% 감면 팩트체크 🧵👇 #외국인세금환급 #조특법30조 #경정청구",
                    "1/ 조특법 제30조(중소기업 취업자 소득세 감면): 중소기업에 취업한 외국인 근로자는 5년간 소득세 90%(연 최대 200만원 한도)를 합법 감면받을 수 있습니다.",
                    "2/ D-2 유학생 3.3% 원천징수 환급 및 최근 5개년(2021~2025) 누락된 환급금 소급 경정청구 전액 신청 가능.",
                    "3/ 본인이 돌려받을 수 있는 예상 환급금이 얼마인지 무료로 확인해보려면, 구글에서 'ktrs tax' 검색해보시면 바로 계산 가능합니다!"
                ]
                hook = "외국인 근로자 조특법 제30조 90% 소득세 감면 및 5개년 소급 환급"

        full_md = "\n\n---\n\n".join([f"**Post {i+1}**\n{p}" for i, p in enumerate(posts)])
        return {
            "hook_title": hook,
            "is_pure_info": is_pure_info,
            "posts": posts,
            "full_markdown": full_md,
            "landing_url": landing_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
