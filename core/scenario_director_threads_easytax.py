# -*- coding: utf-8 -*-
"""
ScenarioDirectorThreadsEasyTax - 💰 EasyTax 17개국어 Threads 세무/환급 타래 바이럴 전담 시나리오 디렉터
- 3대 시간대(아침 11:00, 오후 16:30, 저녁 21:30)별 세무 권리 및 환급 팩트 제공
- 17개 언어권 외국인 근로자(E-9/E-7) 및 유학생(D-2) 맞춤 스토리 완비
"""

import random
from typing import Dict, Any, List

THREADS_EASYTAX_THEMES: List[Dict[str, Any]] = [
    {
        "name": "조특법 30조 중소기업 90% 소득세 감면",
        "title": "중소기업 외국인 근로자 5년간 소득세 90% 감면 합법 권리",
        "refund_formatted": "3,840,000 KRW",
        "target": "E-9/E-7 중소기업 제조업/농축산업 외국인 근로자",
        "hook": "E-9 비자 형들 주목! 소득세 90% 감면 신청 안 했으면 300만원 넘게 날린 겁니다",
        "tag": "e9_article30"
    },
    {
        "name": "D-2 유학생 알바 3.3% 원천징수 전액 환급",
        "title": "외국인 유학생 아르바이트 3.3% 떼인 세금 5월 종합소득세 100% 환급",
        "refund_formatted": "850,000 KRW",
        "target": "D-2/D-4 유학생 및 어학연수생",
        "hook": "식당/카페 알바비에서 3.3% 떼였죠? 국세청에서 100% 전액 다 돌려받는 법",
        "tag": "d2_parttime_tax"
    },
    {
        "name": "지난 5년 치 누락 환급금 소급 경정청구",
        "title": "회사 눈치 볼 필요 없이 지난 5개년(2021~2025) 세금 전액 소급 환급",
        "refund_formatted": "4,200,000 KRW",
        "target": "귀국 예정자 및 한국 체류 3년 이상 외국인",
        "hook": "회사 몰래 지난 5년 치 떼인 세금 420만원 통장에 꽂힌 실화 푼다",
        "tag": "retroactive_5years"
    },
    {
        "name": "본국 부모님 해외송금 부양가족 공제",
        "title": "본국 부모님께 돈 보낸 해외송금 영수증으로 1인당 150만원 추가 공제",
        "refund_formatted": "2,100,000 KRW",
        "target": "본국 가족에게 생활비 송금하는 외국인 근로자",
        "hook": "고향 부모님께 돈 보낸 영수증 한 장으로 세금 200만원 더 돌려받은 후기",
        "tag": "overseas_remittance"
    },
    {
        "name": "E-7-4 비자 변경 전 세금 체납 클린 방어",
        "title": "숙련기능인력 점수제 비자 변경 시 세금 체납 원천 차단 및 감면 점수 확보",
        "refund_formatted": "1,800,000 KRW",
        "target": "E-7-4 점수제 비자 전환 준비 근로자",
        "hook": "비자 연장할 때 출입국 세금 체납 걸려서 비자 뺏길 뻔했다가 살아난 썰",
        "tag": "visa_e74_taxcheck"
    },
    {
        "name": "출국만기보험 & 퇴직금 세금 정산",
        "title": "귀국 전 공항에서 받는 출국만기보험 및 퇴직소득세 정확한 절세 계산",
        "refund_formatted": "2,700,000 KRW",
        "target": "체류 만료 예정 외국인 근로자",
        "hook": "본국 돌아가기 전에 출국만기보험 퇴직금 세금 100만원 넘게 아끼는 비결",
        "tag": "departure_insurance"
    }
]

class ScenarioDirectorThreadsEasyTax:
    """EasyTax Threads 전담 시나리오 디렉터"""
    def __init__(self):
        self.themes = THREADS_EASYTAX_THEMES

    def get_thread_scenario(self) -> Dict[str, Any]:
        return random.choice(self.themes)
