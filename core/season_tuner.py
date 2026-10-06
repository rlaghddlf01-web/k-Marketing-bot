import datetime
from typing import Dict, List

class SeasonTuner:
    """
    외국인 라이프사이클 시즌 오토 튜너 (Seasonal Auto-Tuner)
    월별/시즌별 서비스 발행 가중치를 자동으로 계산
    """
    
    @staticmethod
    def get_current_season_weights(month: int = None) -> Dict[str, float]:
        if month is None:
            month = datetime.datetime.now().month

        # 기본 균등 가중치
        weights = {
            "kmarket": 0.30,
            "easytax": 0.30,
            "ktelecom": 0.15,
            "housing": 0.10,
            "remit": 0.10,
            "loan": 0.05
        }

        # 1월, 2월: 연말정산 집중 기간 + 신학기 입국 준비
        if month in [1, 2]:
            weights["easytax"] = 0.45
            weights["kmarket"] = 0.25
            weights["ktelecom"] = 0.15
            weights["housing"] = 0.10
            weights["remit"] = 0.03
            weights["loan"] = 0.02

        # 5월: 종합소득세 신고의 달 (외국인 아르바이트/사업소득 환급 피크)
        elif month == 5:
            weights["easytax"] = 0.60
            weights["kmarket"] = 0.20
            weights["ktelecom"] = 0.08
            weights["housing"] = 0.04
            weights["remit"] = 0.04
            weights["loan"] = 0.04

        # 8월: 가을 2학기 신입 유학생 대규모 입국 시즌
        elif month == 8:
            weights["kmarket"] = 0.45
            weights["ktelecom"] = 0.25
            weights["housing"] = 0.15
            weights["easytax"] = 0.10
            weights["remit"] = 0.03
            weights["loan"] = 0.02

        # 9월, 10월, 12월: 추석 명절 및 연말 해외송금 피크 시즌
        elif month in [9, 10, 12]:
            weights["remit"] = 0.35
            weights["kmarket"] = 0.25
            weights["easytax"] = 0.25
            weights["ktelecom"] = 0.05
            weights["housing"] = 0.05
            weights["loan"] = 0.05

        return weights

    @classmethod
    def get_recommended_service_for_today(cls) -> str:
        """오늘 요일 및 시즌에 맞는 최우선 마케팅 서비스 추천"""
        now = datetime.datetime.now()
        weekday = now.weekday() # 0: 월 ~ 6: 일
        weights = cls.get_current_season_weights(now.month)

        # 요일별 기본 순환 + 시즌 가중치 결합
        if weekday in [0, 2]: # 월, 수
            return "kmarket" if weights["kmarket"] >= 0.25 else "easytax"
        elif weekday in [1, 3]: # 화, 목
            return "easytax" if weights["easytax"] >= 0.25 else "kmarket"
        elif weekday == 4: # 금
            return "ktelecom" if weights["ktelecom"] >= 0.10 else "kmarket"
        elif weekday == 5: # 토
            return "remit" if weights["remit"] >= 0.15 else "easytax"
        else: # 일
            return "kmarket" # 주말 무료나눔 리포트
