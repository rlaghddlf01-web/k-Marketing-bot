"""
BlogScoreTracker - 📊 정직한 1점 단위 블로그 실유입 성과 트래커 & 순환 롤링 보조
- [원칙 1] 가짜 추정치 뻥튀기 전면 폐기 (신규 발행 시 무조건 0점부터 정직하게 시작)
- [원칙 2] 실제 방문자 1회 조회당 +1점, 실제 신청 전환당 +5점의 정직한 1점 단위 누적
- [원칙 3] 특정 테마 독점 방지 및 40개 테마 공평 순환 보장
"""

import logging
from typing import Dict, Any, List, Optional
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("BlogScoreTracker")


class BlogScoreTracker:
    """정직한 1점 단위 블로그 성과 트래커"""

    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()

    def calculate_article_score(self, views: int = 0, likes: int = 0, shares: int = 0, conversions: int = 0) -> float:
        """
        정직한 실데이터 채점 (가짜 뻥튀기 0%)
        - 실제 1조회(Views)당: +1.0점
        - 실제 1좋아요(Likes)당: +1.0점
        - 실제 1전환(Conversions)당: +5.0점
        - 초기 발행 시: 0.0점
        """
        total_score = float((views * 1.0) + (likes * 1.0) + (shares * 2.0) + (conversions * 5.0))
        return round(total_score, 1)

    def record_theme_performance(self, service_id: str, lang: str, theme_id: str, score: float, views: int = 0, conversions: int = 0):
        """실제 데이터 유입이 발생했을 때만 Supabase theme_learning_weights 갱신"""
        if not self.supabase_mgr.client:
            return

        # 실제 유입/전환이 0인 신규 발행 시에는 가중치 왜곡 방지를 위해 1.0 유지
        if views == 0 and conversions == 0 and score == 0.0:
            return

        try:
            res = self.supabase_mgr.client.table("theme_learning_weights") \
                .select("current_weight, total_conversions") \
                .eq("service_id", service_id) \
                .eq("target_lang", lang) \
                .eq("theme_id", theme_id) \
                .execute()

            cur_weight = 1.0
            total_c = conversions

            if res.data and len(res.data) > 0:
                row = res.data[0]
                prev_conv = int(row.get("total_conversions") or 0)
                cur_w = float(row.get("current_weight") or 1.0)
                total_c = prev_conv + conversions

                # 실제 전환 발생 시 정직하게 +0.1점 단위로 서서히 반영
                weight_boost = 0.1 * conversions
                cur_weight = round(cur_w + weight_boost, 2)

            self.supabase_mgr.client.table("theme_learning_weights").upsert({
                "service_id": service_id,
                "target_lang": lang,
                "theme_id": theme_id,
                "current_weight": cur_weight,
                "total_conversions": total_c
            }, on_conflict="service_id,target_lang,theme_id").execute()

            logger.info(f"📊 [정직한 테마 점수 갱신] {service_id}/{lang}/{theme_id} -> 점수 {score}점 (실제 가중치: {cur_weight})")
        except Exception as e:
            logger.warning(f"테마 성과 기록 실패: {e}")

    def get_top_performing_theme_id(self, service_id: str, lang: str = "ko") -> Optional[str]:
        """Supabase에서 실제 유입 가중치가 1.0보다 높은 유효 성과 테마 조회 (초기엔 None 반환하여 순환 유도)"""
        if not self.supabase_mgr.client:
            return None

        try:
            res = self.supabase_mgr.client.table("theme_learning_weights") \
                .select("theme_id, current_weight") \
                .eq("service_id", service_id) \
                .eq("target_lang", lang) \
                .gt("current_weight", 1.0) \
                .order("current_weight", desc=True) \
                .limit(1) \
                .execute()

            if res.data and len(res.data) > 0:
                best_theme = res.data[0].get("theme_id")
                return best_theme
        except Exception as e:
            logger.warning(f"최고 성과 테마 조회 실패: {e}")

        return None
