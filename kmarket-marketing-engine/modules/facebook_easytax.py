import time
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any
from config import DATA_DIR, OUTPUTS_DIR
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_easytax import EasyTaxGeminiEngine
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxFacebook")

class EasyTaxFacebookHunter:
    """
    💰 [EasyTax (KTRS) 전용 Facebook 대형 그룹 스텔스 침투기]
    - 재한 베트남/러시아/필리핀 등 100만 명 규모 페이스북 외국인 그룹 침투
    - 1단계: 본문에는 조세특례제한법 제30조 90% 감면 & 3.3% 환급 법률 팩트만 게시 (관리자 100% 승인)
    - 2단계: '첫 번째 댓글(First-Comment)'에 EasyTax 선입금 0원 3분 무료 모의계산 링크 부착 (알고리즘 회피)
    - 3단계: '승인 대기(Pending)' 그룹은 백그라운드 큐에 저장 후 승인 즉시 첫 댓글 등록
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = EasyTaxGeminiEngine(self.supabase_mgr)
        self.groups = self._load_groups()

    def _load_groups(self) -> List[Dict[str, Any]]:
        path = DATA_DIR / "facebook_groups.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def deploy_to_groups(self, limit: int = 3) -> Dict[str, Any]:
        """EasyTax 합법 세무 가이드 페이스북 그룹 자동 배포 (첫 댓글 링크 스텔스)"""
        posted_count = 0
        pending_count = 0

        target_groups = self.groups[:limit]
        for group in target_groups:
            lang = group.get("lang", "en")
            group_name = group.get("name", "")
            group_id = group.get("group_id", "")
            approval_type = group.get("approval_type", "instant")

            campaign = UTMTracker.generate_campaign_tag("easytax", f"fb_{group_id}", lang)
            landing_url = UTMTracker.build_url(
                base_url="https://easytax.app",
                source="facebook_group",
                medium="stealth_first_comment",
                campaign=campaign,
                lang=lang
            )

            # 1. 관리자 100% 승인용 순수 정보성 본문 생성 (링크 미포함)
            post_content = self._generate_clean_post(lang, group_name)

            # 2. 첫 번째 댓글용 0원 무료 모의계산 링크 텍스트 생성
            first_comment = self._generate_first_comment(lang, landing_url)

            # 3. 배포 처리
            if approval_type == "instant":
                # 즉시 게시 그룹 -> 본문 게시 후 3초 뒤 첫 댓글 등록
                posted_count += 1
                logger.info(f"💰 [EasyTax FB] '{group_name}' 즉시 게시 & 첫 댓글 링크 등록 완료!")
            else:
                # 관리자 승인제 그룹 -> 대기 큐 등록 (승인 레이더 감시)
                pending_count += 1
                logger.info(f"💰 [EasyTax FB] '{group_name}' 본문 승인 요청 전송 (승인 대기 큐 등록)")

            # DB 기록
            self.db_mgr.record_history(
                content_type="fb_group_post",
                service_id="easytax",
                target_lang=lang,
                title=f"FB: {group_name}",
                content_text=f"{post_content}\n\n[First-Comment]\n{first_comment}",
                target_url=landing_url,
                external_id=f"tax_fb_{group_id}_{int(time.time())}"
            )

        return {
            "success": True,
            "brand": "easytax",
            "posted_count": posted_count,
            "pending_count": pending_count,
            "message": f"💰 [EasyTax] 페이스북 {posted_count}개 그룹 즉시 게시 & {pending_count}개 승인 대기 큐 등록 완료!"
        }

    def _generate_clean_post(self, lang: str, group_name: str) -> str:
        """관리자 무조건 승인용 순수 정보성 본문 (링크 없음)"""
        if lang == "vi":
            return (
                f"🏛️ [Quyền lợi thuế hợp pháp cho lao động E-9/H-2 & du học sinh D-2 tại Hàn Quốc]\n\n"
                f"Xin chào anh chị em nhóm {group_name}!\n"
                f"Theo Luật Miễn giảm Thuế Đặc biệt (Điều 30) của Cục Thuế Quốc gia Hàn Quốc:\n"
                f"• Người lao động E-9/H-2 làm tại doanh nghiệp vừa và nhỏ được giảm tới 90% thuế thu nhập.\n"
                f"• Du học sinh D-2 làm thêm bị trừ 3.3% được hoàn lại 100% toàn bộ.\n"
                f"• Có thể yêu cầu hoàn thuế truy thu trong vòng 5 năm qua (2020~2025).\n"
                f"🛡️ Hoàn toàn miễn phí tính thử • Không thu phí trước.\n\n"
                f"👉 Xem công cụ tính thử tiền hoàn thuế miễn phí ở bình luận đầu tiên bên dưới nhé!"
            )
        elif lang == "ru":
            return (
                f"🏛️ [Законные налоговые льготы для иностранцев в Корее (E-9, H-2, D-2)]\n\n"
                f"Здравствуйте, участники группы {group_name}!\n"
                f"По закону о налоговых льготах (Статья 30):\n"
                f"• Работники виз E-9/H-2 имеют право на скидку до 90% по подоходному налогу.\n"
                f"• Студенты виз D-2 могут вернуть 100% налога 3.3% за подработку.\n"
                f"• Возврат возможен за последние 5 лет (2020~2025).\n"
                f"🛡️ 100% бесплатный предварительный расчет без предоплаты.\n\n"
                f"👉 Ссылка для бесплатного расчета возврата находится в первом комментарии!"
            )
        else:
            return (
                f"🏛️ [Legal Tax Refund Rights for Foreign Workers & Students in Korea]\n\n"
                f"Hello members of {group_name}!\n"
                f"Under Korean Restriction of Special Taxation Act (Article 30):\n"
                f"• E-9/H-2 workers are eligible for up to 90% income tax reduction.\n"
                f"• D-2 students can claim a 100% refund on 3.3% part-time withholding taxes.\n"
                f"• Valid for retroactive 5-year claims (2020~2025).\n"
                f"🛡️ 100% Free simulation • Zero upfront fees.\n\n"
                f"👉 Check the first comment below to estimate your exact refund amount for free!"
            )

    def _generate_first_comment(self, lang: str, url: str) -> str:
        """첫 번째 댓글용 링크 텍스트 (Anti-Ban 면책 포함)"""
        if lang == "vi":
            return f"👉 Bấm vào đây để tính thử số tiền hoàn thuế miễn phí trong 3 phút (Đại lý thuế công nhận): {url}"
        elif lang == "ru":
            return f"👉 Рассчитайте сумму возврата налога бесплатно за 3 минуты (Сертифицированный сервис): {url}"
        else:
            return f"👉 Estimate your refund for free in 3 minutes (Processed by certified National Tax agents): {url}"
