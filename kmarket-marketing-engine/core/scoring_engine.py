from typing import Dict, Any

class KMarketScoringEngine:
    """
    🛒 [K-Market 전용 자가학습 평가기]
    - 0원 나눔 바이럴 클릭률 (40%)
    - 17개국 번역 채팅 및 매물 문의 전환율 (35%)
    - 소셜 저장/공유 반응 (25%)
    """
    @staticmethod
    def calculate_score(views: int = 0, clicks: int = 0, conversions: int = 0, 
                        upvotes: int = 0, comments_count: int = 0) -> float:
        # 1. 반응 점수 (최대 25점)
        engagement_score = min(25.0, (upvotes * 2.0) + (comments_count * 2.5))
        # 2. 유입 점수 (최대 40점)
        traffic_score = min(40.0, (clicks / max(views, 1) / 0.05) * 40.0) if views > 0 else min(40.0, clicks * 4.0)
        # 3. 매물 문의/채팅 전환 점수 (최대 35점)
        conversion_score = min(35.0, conversions * 11.6)

        return round(engagement_score + traffic_score + conversion_score, 1)

    @classmethod
    def evaluate(cls, metrics: Dict[str, Any]) -> Dict[str, Any]:
        score = cls.calculate_score(
            metrics.get("views", 0), metrics.get("clicks", 0), metrics.get("conversions", 0),
            metrics.get("upvotes", 0), metrics.get("comments_count", 0)
        )
        grade = "S (골든 나눔 카피)" if score >= 85.0 else "A (우수 매물 카피)" if score >= 70.0 else "B (일반)" if score >= 50.0 else "C (개선)"
        return {"score": score, "grade": grade, "is_golden": score >= 85.0, "brand": "kmarket"}


class EasyTaxScoringEngine:
    """
    💰 [EasyTax 전용 자가학습 평가기]
    - 세무 모의계산 완료 및 환급 신청 전환율 (50% - 초고부가가치)
    - 공인 세무 가이드 유입률 (30%)
    - 세무 팩트 신뢰도 & 저장/북마크 (20%)
    """
    @staticmethod
    def calculate_score(views: int = 0, clicks: int = 0, conversions: int = 0, 
                        upvotes: int = 0, comments_count: int = 0) -> float:
        # 1. 세무 신뢰도 반응 점수 (최대 20점)
        engagement_score = min(20.0, (upvotes * 2.0) + (comments_count * 3.0))
        # 2. 유입 점수 (최대 30점)
        traffic_score = min(30.0, (clicks / max(views, 1) / 0.04) * 30.0) if views > 0 else min(30.0, clicks * 3.0)
        # 3. 환급 신청서 제출 전환 점수 (최대 50점 - 핵심 KPI)
        conversion_score = min(50.0, conversions * 16.6)

        return round(engagement_score + traffic_score + conversion_score, 1)

    @classmethod
    def evaluate(cls, metrics: Dict[str, Any]) -> Dict[str, Any]:
        score = cls.calculate_score(
            metrics.get("views", 0), metrics.get("clicks", 0), metrics.get("conversions", 0),
            metrics.get("upvotes", 0), metrics.get("comments_count", 0)
        )
        grade = "S (골든 세무 카피)" if score >= 85.0 else "A (우수 세무 카피)" if score >= 70.0 else "B (일반)" if score >= 50.0 else "C (개선)"
        return {"score": score, "grade": grade, "is_golden": score >= 85.0, "brand": "easytax"}
