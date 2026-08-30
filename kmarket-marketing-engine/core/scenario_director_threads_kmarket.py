"""
ScenarioDirectorThreadsKMarket - 🛒 K-Market 17개국어 Threads 구어체 타래 바이럴 전담 시나리오 디렉터
"""

import random
from typing import Dict, Any

THREADS_KMARKET_THEMES = [
    {"hook": "한국 원룸 이사할 때 가구 버리지 마세요! 0원 나눔 꿀팁", "tag": "moving"},
    {"hook": "외국인등록증으로 알뜰폰 유심 1만 원대 무제한 개통한 썰", "tag": "living"},
    {"hook": "쓰레기 종량제 봉투 잘못 버렸다가 10만 원 과태료 낼 뻔한 사연", "tag": "tips"},
    {"hook": "K-Market에서 0원으로 풀세팅한 내 감성 원룸 공개합니다", "tag": "giveaway"}
]

class ScenarioDirectorThreadsKMarket:
    """K-Market Threads 전담 시나리오 디렉터"""
    def __init__(self):
        self.themes = THREADS_KMARKET_THEMES

    def get_thread_scenario(self) -> Dict[str, Any]:
        return random.choice(self.themes)
