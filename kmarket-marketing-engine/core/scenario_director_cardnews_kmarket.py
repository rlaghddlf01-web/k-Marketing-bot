"""
ScenarioDirectorCardnewsKMarket - 🛒 [K-Market 4장 실물 270개 매물 캐러셀 카드뉴스 전담 기획 엔진]
- Slide 1 (Hook): 한국 원룸 0원 나눔 & 무빙세일 득템 피드
- Slide 2 (Items): 대학가/산단 실시간 인증 0원 가구·가전 꿀매물
- Slide 3 (Safety): 17개국 1:1 자동번역 채팅 & 안심 직거래
- Slide 4 (Action): 프로필 링크에서 0원 매물 즉시 받기
"""

from typing import Dict, Any, List, Optional
import random

class ScenarioDirectorCardnewsKMarket:
    """K-Market 4장 캐러셀 카드뉴스 전담 기획 엔진"""
    def __init__(self):
        pass

    def get_carousel_scenario(self, lang: str = "en", theme_index: Optional[int] = None) -> Dict[str, Any]:
        return {
            "service_id": "kmarket",
            "title": "🛒 K-Market 한국 원룸 0원 무료나눔 & 중고 득템 가이드",
            "cards": [
                {
                    "badge": "STEP 1: 0원 득템 피드",
                    "title": "비싼 가구 사지 마세요! 0원 나눔",
                    "subtitle": "졸업생·선배 귀국 무빙세일 무료 나눔 꿀매물",
                    "bullets": [
                        "• 신촌/안암/혜화 원룸 책상, 의자, 침대 0원 무료 나눔",
                        "• 미니냉장고, 전자레인지, 밥솥 가전제품 득템",
                        "• 실시간 270개 인증 매물 매일 업데이트",
                        "• 유학생 및 외국인 근로자 전용 100% 무료"
                    ]
                },
                {
                    "badge": "STEP 2: 실시간 꿀매물",
                    "title": "대학가·산단 주변 실물 매물",
                    "subtitle": "내 주변 원룸 방빼기 직거래 매물 확인",
                    "bullets": [
                        "• 신촌 연세대 원룸 책상+스탠드 무료 나눔",
                        "• 고려대 안암 원룸 소형 냉장고 (상태 A급)",
                        "• 안산 원곡동/수원 영통 수납장 0원 나눔",
                        "• 평택 고덕/아산 탕정 생활가전 무빙세일"
                    ]
                },
                {
                    "badge": "STEP 3: 1:1 자동번역",
                    "title": "한국어 못해도 100% 안심 거래",
                    "subtitle": "17개 언어 실시간 자동번역 1:1 채팅 지원",
                    "bullets": [
                        "• 모국어로 편하게 채팅하면 한국어로 자동 번역",
                        "• 대학생 학생증 & 외국인등록증 인증 안전 거래",
                        "• 캠퍼스 정문 및 안심 직거래 스팟 지원",
                        "• 수수료 0원 • 무료 나눔 예약 시스템"
                    ]
                },
                {
                    "badge": "STEP 4: 지금 바로 받기",
                    "title": "프로필 링크에서 0원 매물 신청",
                    "subtitle": "선착순 나눔 완료 전 지금 확인하세요",
                    "bullets": [
                        "👉 프로필 링크 클릭",
                        "👉 내 지역(신촌/안암/안산/수원 등) 선택",
                        "👉 원하는 0원 매물 '나눔 신청' 클릭",
                        "👉 1:1 번역 채팅으로 약속 잡고 수령!"
                    ]
                }
            ]
        }
