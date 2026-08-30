"""
ScenarioDirectorCardnewsEasyTax - 💰 EasyTax 4장 공인 세무/환급 카드뉴스 전담 시나리오 디렉터
- 원래의 [6대 감정 테마 × 실사 비주얼 × 환급액 뱃지] 전담 연출
"""

from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax

class ScenarioDirectorCardnewsEasyTax:
    """EasyTax 4장 캐러셀 카드뉴스 전담 기획 엔진"""
    def __init__(self):
        self.shorts_director = ScenarioDirectorShortsEasyTax()

    def plan_daily_scenario(self, lang: str = "en"):
        return self.shorts_director.plan_daily_scenario(lang=lang)
