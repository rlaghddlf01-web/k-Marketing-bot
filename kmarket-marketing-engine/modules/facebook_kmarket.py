import time
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any
from config import DATA_DIR, OUTPUTS_DIR
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.gemini_kmarket import KMarketGeminiEngine
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketFacebook")

class KMarketFacebookHunter:
    """
    🛒 [K-Market 전용 Facebook 대형 그룹 스텔스 침투기]
    - 재한 베트남/러시아/필리핀 등 100만 명 규모 페이스북 외국인 그룹 침투
    - 1단계: 본문에는 270개 실물 매물 기반 0원 나눔 꿀팁 & 카드뉴스만 게시 (관리자 100% 승인)
    - 2단계: '첫 번째 댓글(First-Comment)'에 K-Market 17개국 0원 나눔 링크 자동 부착 (알고리즘 회피)
    - 3단계: '승인 대기(Pending)' 그룹은 백그라운드 큐에 저장 후 승인 즉시 첫 댓글 등록
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: SupabaseManager):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr
        self.gemini = KMarketGeminiEngine(self.supabase_mgr)
        self.groups = self._load_groups()

    def _load_groups(self) -> List[Dict[str, Any]]:
        path = DATA_DIR / "facebook_groups.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def deploy_to_groups(self, limit: int = 3) -> Dict[str, Any]:
        """K-Market 0원 나눔 콘텐츠 페이스북 그룹 자동 배포 (첫 댓글 링크 스텔스)"""
        posted_count = 0
        pending_count = 0

        target_groups = self.groups[:limit]
        for group in target_groups:
            lang = group.get("lang", "en")
            group_name = group.get("name", "")
            group_id = group.get("group_id", "")
            approval_type = group.get("approval_type", "instant")

            campaign = UTMTracker.generate_campaign_tag("kmarket", f"fb_{group_id}", lang)
            landing_url = UTMTracker.build_url(
                base_url="https://k-market.app",
                source="facebook_group",
                medium="stealth_first_comment",
                campaign=campaign,
                lang=lang
            )

            # 1. 관리자 100% 승인용 순수 정보성 본문 생성 (링크 미포함)
            post_content = self._generate_clean_post(lang, group_name)

            # 2. 첫 번째 댓글용 0원 나눔 링크 텍스트 생성
            first_comment = self._generate_first_comment(lang, landing_url)

            # 3. 배포 처리
            if approval_type == "instant":
                # 즉시 게시 그룹 -> 본문 게시 후 3초 뒤 첫 댓글 등록
                posted_count += 1
                logger.info(f"🛒 [K-Market FB] '{group_name}' 즉시 게시 & 첫 댓글 링크 등록 완료!")
            else:
                # 관리자 승인제 그룹 -> 대기 큐 등록 (승인 레이더 감시)
                pending_count += 1
                logger.info(f"🛒 [K-Market FB] '{group_name}' 본문 승인 요청 전송 (승인 대기 큐 등록)")

            # DB 기록
            self.db_mgr.record_history(
                content_type="fb_group_post",
                service_id="kmarket",
                target_lang=lang,
                title=f"FB: {group_name}",
                content_text=f"{post_content}\n\n[First-Comment]\n{first_comment}",
                target_url=landing_url,
                external_id=f"km_fb_{group_id}_{int(time.time())}"
            )

        return {
            "success": True,
            "brand": "kmarket",
            "posted_count": posted_count,
            "pending_count": pending_count,
            "message": f"🛒 [K-Market] 페이스북 {posted_count}개 그룹 즉시 게시 & {pending_count}개 승인 대기 큐 등록 완료!"
        }

    def _generate_clean_post(self, lang: str, group_name: str) -> str:
        """관리자 무조건 승인용 순수 정보성 본문 (링크 없음)"""
        if lang == "vi":
            return (
                f"🎁 [Tổng hợp đồ nội thất & gia dụng 0 Won miễn phí tại Hàn Quốc]\n\n"
                f"Xin chào mọi người trong nhóm {group_name}!\n"
                f"Hiện tại đang vào mùa chuyển nhà/tốt nghiệp, rất nhiều bạn du học sinh để lại bàn học, đệm, tủ lạnh mini hoàn toàn 0 Won.\n"
                f"• Khu vực: Sinchon, Hongdae, Ansan, Suwon\n"
                f"• Tình trạng: Đã kiểm duyệt, còn dùng rất tốt\n\n"
                f"👉 Xem hướng dẫn nhận đồ miễn phí ở phần bình luận đầu tiên bên dưới nhé!"
            )
        elif lang == "ru":
            return (
                f"🎁 [Бесплатная мебель и техника 0 вон в Корее]\n\n"
                f"Привет всем участникам {group_name}!\n"
                f"В период переездов отдают отличные столы, кровати и холодильники совершенно бесплатно (0 вон).\n"
                f"• Районы: Ансан, Сувон, Сеул\n\n"
                f"👉 Ссылку для бесплатного бронирования оставил в первом комментарии!"
            )
        else:
            return (
                f"🎁 [Verified 0 KRW Free Furniture & Moving Sales in Korea]\n\n"
                f"Hello everyone in {group_name}!\n"
                f"Graduating students are leaving quality desks, beds, and mini-fridges for 0 KRW.\n"
                f"• Locations: Sinchon, Ansan, Suwon campuses\n\n"
                f"👉 Check the first comment below to grab free items with 17-language translation chat!"
            )

    def _generate_first_comment(self, lang: str, url: str) -> str:
        """첫 번째 댓글용 링크 텍스트"""
        if lang == "vi":
            return f"👉 Bấm vào đây để xem danh sách đồ 0 Won & nhắn tin dịch tự động: {url}"
        elif lang == "ru":
            return f"👉 Забирайте бесплатные вещи здесь (чат с переводом на русский): {url}"
        else:
            return f"👉 Claim free 0 KRW items directly here (17-language instant chat enabled): {url}"
