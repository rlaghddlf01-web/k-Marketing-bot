"""
ScenarioDirectorThreadsEasyTax - 💰 EasyTax 15개국어 Threads 세무 환급 타래 바이럴 전담 시나리오 디렉터
"""

import random
from typing import Dict, Any

THREADS_EASYTAX_THEMES = [
    {"hook": "E-9 비자 형들 주목! 소득세 90% 감면 신청 안 했으면 300만원 날린 겁니다", "tag": "e9_tax"},
    {"hook": "D-2 유학생 알바비에서 3.3% 떼였죠? 5월에 100% 다 돌려받는 법", "tag": "d2_tax"},
    {"hook": "본국 부모님께 돈 보낸 영수증으로 세금 150만원 더 돌려받은 후기", "tag": "family_deduction"},
    {"hook": "동사무소 무인발급기에서 원천징수영수증 500원에 1분 만에 떼는 법", "tag": "tax_docs"}
]

class ScenarioDirectorThreadsEasyTax:
    """EasyTax Threads 전담 시나리오 디렉터"""
    def __init__(self):
        self.themes = THREADS_EASYTAX_THEMES

    def get_thread_scenario(self) -> Dict[str, Any]:
        return random.choice(self.themes)
