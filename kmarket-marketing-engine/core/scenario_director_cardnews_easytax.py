"""
ScenarioDirectorCardnewsEasyTax - 💰 [EasyTax 4장 국세청 공인 세무 카드뉴스 전담 기획 엔진]
- Slide 1 (Hook): 조특법 30조 90% 감면 & 5년 소급 환급 팩트 폭격
- Slide 2 (Target): E-9/H-2 근로자 & D-2 유학생 3.3% 환급 대상 체크
- Slide 3 (Trust): 국세청 정식 공인 세무 대리 & 0원 AI 진단
- Slide 4 (Action): 프로필 링크 1분 비대면 무료 환급 조회
"""

from typing import Dict, Any, List, Optional
from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax

class ScenarioDirectorCardnewsEasyTax:
    """EasyTax 4장 캐러셀 카드뉴스 전담 기획 엔진"""
    def __init__(self):
        self.shorts_director = ScenarioDirectorShortsEasyTax()

    def get_carousel_scenario(self, lang: str = "en", theme_index: Optional[int] = None) -> Dict[str, Any]:
        sc = self.shorts_director.plan_daily_scenario(lang=lang)
        theme_name = sc.get("theme_name", "Korea Expat Tax Refund")

        return {
            "service_id": "easytax",
            "title": f"🏛️ EasyTax: {theme_name}",
            "cards": [
                {
                    "badge": "STEP 1: 팩트 체크",
                    "title": "외국인 근로자 90% 소득세 감면",
                    "subtitle": "조특법 제30조 국가 세무 혜택 (E-9/H-2/D-2)",
                    "bullets": [
                        "• 중소기업 취업 외국인 소득세 최대 90% 감면",
                        "• 지난 5개년(2021~2026) 더 낸 세금 전액 소급 환급",
                        "• D-2 유학생 아르바이트 3.3% 원천징수 100% 환급",
                        "• 국세청 세법 기준 1인 평균 384만 원 환급"
                    ]
                },
                {
                    "badge": "STEP 2: 환급 대상자",
                    "title": "나는 환급받을 수 있을까?",
                    "subtitle": "아래 3가지 중 1개만 해당되어도 신청 가능",
                    "bullets": [
                        "1. E-9/E-7/H-2 비자로 제조/농축산/건설 근무자",
                        "2. D-2/D-4 유학 중 합법 아르바이트(3.3% 공제) 경험자",
                        "3. 귀국을 앞두고 지난 세금을 총정리하고 싶은 분",
                        "• 비자 변경 전 5년 치 누락 세금 합법 수령"
                    ]
                },
                {
                    "badge": "STEP 3: 100% 안전 보장",
                    "title": "국세청 등록 세무사 공인 대리",
                    "subtitle": "착수금 0원 • 선입금 절대 요구 안 함",
                    "bullets": [
                        "• 국세청 홈택스 공식 API 실시간 연동",
                        "• 환급금 입금 전까지 비용 0원 (100% 무료 시뮬레이션)",
                        "• 17개 언어 모국어 1:1 세무 전담 안내",
                        "• 3분 모바일 비대면 간편 신청"
                    ]
                },
                {
                    "badge": "STEP 4: 즉시 환급 신청",
                    "title": "지금 1분 만에 내 환급금 확인",
                    "subtitle": "더 늦기 전에 5년 소멸시효 전 신청하세요",
                    "bullets": [
                        "👉 프로필 링크 클릭",
                        "👉 국가 및 비자 유형 선택",
                        "👉 AI 1분 무료 환급액 계산",
                        "👉 국세청 공식 환급금 본인 통장 입금!"
                    ]
                }
            ]
        }
