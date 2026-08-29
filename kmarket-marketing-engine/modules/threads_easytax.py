import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from config import BASE_DIR, OUTPUTS_DIR, LANGUAGES, BASE_URLS
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager

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
        self.output_dir = OUTPUTS_DIR / "threads" / "easytax"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def publish_daily_threads(self, target_langs: List[str] = ["en", "vi", "ko"]) -> Dict[str, Any]:
        """EasyTax 타래형 세무 환급 스레드 생성 및 배포"""
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
        """언어별 맞춤 세무 타래형 스레드 콘텐츠 생성"""
        if lang == "vi":
            posts = [
                "Lao động Việt Nam visa E-9, E-7 và du học sinh D-2 tại Hàn Quốc nhất định phải biết điều này nếu không muốn mất hàng triệu won tiền thuế 🧵👇 #HoanThueHanQuoc #EasyTax #VisaE9",
                "1/ Điều 30 Luật Miễn giảm thuế đặc biệt (조특법 제30조): Người lao động nước ngoài làm việc tại doanh nghiệp vừa và nhỏ (SME) được GIẢM 90% thuế thu nhập trong 5 năm đầu (tối đa 2.000.000 KRW/năm).",
                "2/ Du học sinh D-2 làm thêm bị trừ 3.3% thuế hoặc lao động đã về nước/chuyển xưởng từ 2021-2025 đều có thể yêu cầu HOÀN LẠI 100% hợp pháp.",
                f"3/ Kiểm tra số tiền hoàn thuế miễn phí trong 3 phút (Đại lý thuế công nhận của Cục Thuế Quốc gia - 선입금 0원):\n👉 Tính tiền hoàn thuế ngay: {landing_url}"
            ]
            hook = "Quyền giảm 90% thuế thu nhập (Điều 30) & Hoàn thuế 5 năm cho lao động E-9"
        elif lang == "en":
            posts = [
                "Foreign workers & international students in Korea: You might be leaving up to 2,000,000 KRW in unclaimed tax refunds every year 🧵👇 #KoreaTax #ExpatFinance #EasyTax",
                "1/ Under Article 30 of the Restriction of Special Taxation Act, foreign employees in Korean SMEs are entitled to a 90% INCOME TAX REDUCTION for their first 5 years.",
                "2/ Worked part-time with 3.3% withholding tax under D-2 visa? Or missed tax filing between 2021-2025? You can legally claim retroactive refunds for the past 5 years.",
                f"3/ Certified NTS tax accountants, zero upfront fee. Calculate your refund in 3 mins:\n👉 Free Tax Calculator: {landing_url}"
            ]
            hook = "90% Income Tax Exemption & 5-Year Retroactive Refund Guide for Expats"
        else: # ko
            posts = [
                "외국인 근로자(E-9/E-7) 및 유학생(D-2) 국세청 소득세 90% 감면 팩트체크 🧵👇 #외국인세금환급 #EasyTax #조특법30조",
                "1/ 조특법 제30조(중소기업 취업자 소득세 감면): 중소기업에 취업한 외국인 근로자는 5년간 소득세 90%(연 최대 200만원 한도)를 합법 감면받을 수 있습니다.",
                "2/ D-2 유학생 3.3% 원천징수 환급 및 최근 5개년(2021~2025) 누락된 환급금 소급 경정청구 전액 지원.",
                f"3/ 선입금 0원 국세청 공인 세무대리 3분 무료 환급 조회:\n👉 EasyTax 바로가기: {landing_url}"
            ]
            hook = "외국인 근로자 조특법 제30조 90% 소득세 감면 및 5개년 소급 환급"

        full_md = "\n\n---\n\n".join([f"**Post {i+1}**\n{p}" for i, p in enumerate(posts)])
        return {
            "hook_title": hook,
            "posts": posts,
            "full_markdown": full_md,
            "landing_url": landing_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
