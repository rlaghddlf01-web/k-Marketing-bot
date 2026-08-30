"""
ScenarioDirectorBlogKMarket - 🛒 K-Market 17개국어 공식 블로그 전담 시나리오 디렉터 (총괄 지휘자)
- [단일 책임 원칙] 모든 글의 기획, 구성, 톤앤매너, CTA 규칙, 비주얼(사진 2장), 0원 나눔 안전수칙 지시를 전담 하달
- 40대 초정밀 실전 외국인 라이프스타일·0원 나눔·중고거래 테마 전수 탑재
- 100% 동양인/한국 로컬 원룸 실사 가드레일 & 사진 2장 배치 명령
- 깨끗한 CTA 버튼 포맷 가드레일 하달
- Supabase 유입 점수 자가학습 랭킹 기반 고성과 테마 우선 선정
"""

import random
import logging
from typing import Dict, Any, Optional
from core.blog_score_tracker import BlogScoreTracker

logger = logging.getLogger("ScenarioDirectorBlogKMarket")

KMARKET_BLOG_THEMES = [
    # 1. 🛋️ [원룸 이사 & 가구/가전 0원 풀세팅 (1~5)]
    {
        "id": "km_moving_freshman",
        "title": "신학기 원룸 이사 & 가구 구매 비용 100만 원 절약법",
        "category": "moving_setup",
        "key_facts": ["대형폐기물 스티커 비용 0원화", "K-Market 0원 나눔 활용", "침대/매트리스 득템 노하우"],
        "visual_prompt": "Asian student standing happily in cozy neat Korean studio apartment with arranged furniture"
    },
    {
        "id": "km_studio_appliances_zero",
        "title": "선배 유학생 졸업 시즌! 냉장고, 전자레인지, 밥솥 0원 무료나눔 받는 꿀팁",
        "category": "moving_setup",
        "key_facts": ["졸업생 귀국 무료나눔 매물", "전자레인지/밥솥 0원 나눔", "기숙사 직거래 팁"],
        "visual_prompt": "Clean modern Korean studio room kitchen counter with microwave and rice cooker"
    },
    {
        "id": "km_study_desk",
        "title": "스터디용 높이조절 책상 & 인체공학 의자 득템기",
        "category": "moving_setup",
        "key_facts": ["공부용 책상/시디즈 의자", "시중가 대비 90% 절약", "용달/직접 수거 요령"],
        "visual_prompt": "Asian university student studying at neat desk near bright window in studio"
    },
    {
        "id": "km_bulky_waste_zero",
        "title": "대형폐기물 스티커 비용(2만~5만 원) 아끼고 이웃에게 0원 나눔하는 법",
        "category": "moving_setup",
        "key_facts": ["구청 스티커 비용 절약", "1시간 내 수거 예약", "환경보호 및 나눔 문화"],
        "visual_prompt": "Neat Korean studio room interior with organized wooden shelf and sofa"
    },
    {
        "id": "km_moving_checklist_100k",
        "title": "한국 원룸 첫 계약 후 필수 생활용품 10만 원으로 끝내기 체크리스트",
        "category": "moving_setup",
        "key_facts": ["필수 가전/식기 체크리스트", "다이소 vs K-Market 비교", "10만원 풀세팅 실화"],
        "visual_prompt": "Asian young couple checking checklist on phone in new studio apartment"
    },

    # 2. 🚲 [교통/통학/이동 수단 알뜰 직거래 (6~10)]
    {
        "id": "km_bicycle_commute",
        "title": "출퇴근/통학용 중고 자전거 & 전동 킥보드 안심 거래",
        "category": "mobility",
        "key_facts": ["하이브리드 자전거 직거래", "배터리 수명 체크법", "따릉이 대비 가성비 비교"],
        "visual_prompt": "Asian student riding bicycle on university campus in Seoul in sunny afternoon"
    },
    {
        "id": "km_used_laptop",
        "title": "외국인 유학생 과제용 중고 노트북 (LG그램/맥북) 배터리/스펙 검증 직거래 노하우",
        "category": "digital_it",
        "key_facts": ["배터리 사이클 확인", "한영 키보드 설정", "직거래 현장 하드웨어 테스트"],
        "visual_prompt": "Asian student typing on modern slim laptop in campus library"
    },
    {
        "id": "km_lease_deposit_safety",
        "title": "외국인 유학생 원룸 전입신고 & 보증금 떼이지 않는 확정일자 받는 법",
        "category": "life_safety",
        "key_facts": ["전입신고 14일 이내 필수", "주민센터 확정일자 도장", "보증금 우선변제권 확보"],
        "visual_prompt": "Asian student holding Korean lease contract with verified stamp outside community center"
    }
]

class ScenarioDirectorBlogKMarket:
    """
    🛒 K-Market 17개국어 공식 블로그 전담 시나리오 디렉터 (총괄 지휘자)
    - 제미나이에게 완벽한 글의 구성, 100% 동양인/한국 로컬 가구 사진 2장 배치, 깨끗한 CTA 링크 명령을 전담 하달
    """
    def __init__(self, score_tracker: Optional[BlogScoreTracker] = None):
        self.themes = KMARKET_BLOG_THEMES
        self.score_tracker = score_tracker or BlogScoreTracker()

    def get_directive(self, theme_index: Optional[int] = None, lang: str = "ko") -> Dict[str, Any]:
        """
        🎯 [50% 실유입 가중치 + 50% 랜덤 탐색] 균형 테마 선정
        - 50% 확률: 실제 방문자 유입/전환 점수가 가장 높은 1위 테마 우선 채택
        - 50% 확률: 40개 전체 테마 중에서 무작위로 새로운 테마 탐색 (다양성 100% 보장)
        """
        if theme_index is not None:
            theme = self.themes[theme_index % len(self.themes)]
        else:
            best_theme_id = self.score_tracker.get_top_performing_theme_id("kmarket", lang)
            matched_themes = [t for t in self.themes if t["id"] == best_theme_id]

            if matched_themes and random.random() < 0.5:
                theme = matched_themes[0]
                logger.info(f"🏆 [가중치 50% 채택] 실유입 1위 테마 선정: '{theme['title']}'")
            else:
                theme = random.choice(self.themes)
                logger.info(f"🎲 [랜덤 50% 채택] 40개 테마 중 새로운 테마 탐색: '{theme['title']}'")

        writing_directive = {
            "topic_title": theme["title"],
            "category": theme["category"],
            "key_facts": theme["key_facts"],
            "guideline": (
                "1. [분량 & 필력] 워드프레스 최고급 매거진 수준의 유려하고 생생한 2,000자 한국어 마스터 칼럼으로 집필할 것.\n"
                "2. [대표 사진 연동] 본문 맨 위(대제목 # 바로 아래)에 상단 대표 사진 1장만 배치하고, 본문 중간에는 임의의 가짜 이미지 태그나 style 텍스트를 절대 삽입하지 말 것.\n"
                "3. [CTA 링크 엄격 규칙] 링크 텍스트 안에 URL 주소를 괄호로 중복 노출하지 말 것! 반드시 다음과 같이 깔끔하게 작성할 것:\n"
                "   - 올바른 예: 👉 **[지금 바로 내 주변 0원 나눔 및 알뜰 매물 확인하기]({landing_url})**\n"
                "   - 절대 금지: 👉 [지금 바로 확인하기 (https://...)] (URL 중복 노출 절대 금지)\n"
                "4. [구성 요소] 서론(신학기 이사 비용 부담 공감) -> 1. 원룸 이사 100만 원 아끼는 노하우 -> 2. 신품 vs K-Market 직거래 비용 비교표 -> 3. 외국인 100% 안전 직거래 3대 수칙 -> 4. 깔끔한 CTA 버튼 -> 실시간 바이럴 해시태그."
            ),
            "visual_prompt": theme["visual_prompt"]
        }

        return {
            "id": theme["id"],
            "title": theme["title"],
            "category": theme["category"],
            "directive": writing_directive
        }

    # 호환성 별칭
    def get_scenario(self, theme_index: Optional[int] = None) -> Dict[str, Any]:
        return self.get_directive(theme_index)
