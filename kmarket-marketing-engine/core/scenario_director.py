"""
ScenarioDirector - [시나리오 디렉터 통합 파사드(Facade) 오케스트레이터]
각 채널/서비스별 전담 시나리오 디렉터 모듈을 위임(Delegation) 호출하며 하위 호환성을 100% 보장합니다.

1. 📝 블로그 전담:
   - ScenarioDirectorBlogEasyTax (38대 초정밀 실무 세무·서식·환급 테마)
   - ScenarioDirectorBlogKMarket (40대 실전 라이프스타일 테마)
2. 🎬 숏폼 비디오 전담:
   - ScenarioDirectorShortsEasyTax (6대 라이프스타일 감정 테마 × 만 15~34세 청년 페르소나 매트릭스)
   - ScenarioDirectorShortsKMarket (실물 매물 0원 나눔 숏폼 테마)
3. 📸 카드뉴스 전담:
   - ScenarioDirectorCardnewsEasyTax (4장 공인 세무 환급 카드뉴스)
   - ScenarioDirectorCardnewsKMarket (4장 실물 캐러셀 카드뉴스)
4. 🧵 스레드 전담:
   - ScenarioDirectorThreadsEasyTax (15개국어 타래 세무 환급)
   - ScenarioDirectorThreadsKMarket (17개국어 타래 바이럴)
"""

import logging
from typing import Dict, Any, List, Optional
from config import LANGUAGES

# 개별 전담 모듈 임포트
from core.scenario_director_blog_easytax import ScenarioDirectorBlogEasyTax, EASYTAX_BLOG_THEMES
from core.scenario_director_blog_kmarket import ScenarioDirectorBlogKMarket, KMARKET_BLOG_THEMES
from core.scenario_director_shorts_easytax import ScenarioDirectorShortsEasyTax, LIFESTYLE_THEMES as ORIGINAL_LIFESTYLE_THEMES, PERSONAS as ORIGINAL_PERSONAS
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket, KMARKET_SHORTS_THEMES
from core.scenario_director_cardnews_easytax import ScenarioDirectorCardnewsEasyTax
from core.scenario_director_cardnews_kmarket import ScenarioDirectorCardnewsKMarket
from core.scenario_director_threads_easytax import ScenarioDirectorThreadsEasyTax, THREADS_EASYTAX_THEMES
from core.scenario_director_threads_kmarket import ScenarioDirectorThreadsKMarket, THREADS_KMARKET_THEMES

logger = logging.getLogger("ScenarioDirector")


class ScenarioDirector:
    """
    🎬 시나리오 디렉터 통합 오케스트레이터 (Facade)
    - 외부 호출과의 완벽한 하위 호환성 유지
    - 실제 로직은 각 서비스/채널별 독립 전담 클래스로 위임
    """
    def __init__(self):
        # 1. 블로그 전담 디렉터
        self.blog_easytax = ScenarioDirectorBlogEasyTax()
        self.blog_kmarket = ScenarioDirectorBlogKMarket()

        # 2. 숏폼 전담 디렉터
        self.shorts_easytax = ScenarioDirectorShortsEasyTax()
        self.shorts_kmarket = ScenarioDirectorShortsKMarket()

        # 3. 카드뉴스 전담 디렉터
        self.cardnews_easytax = ScenarioDirectorCardnewsEasyTax()
        self.cardnews_kmarket = ScenarioDirectorCardnewsKMarket()

        # 4. 스레드 전담 디렉터
        self.threads_easytax = ScenarioDirectorThreadsEasyTax()
        self.threads_kmarket = ScenarioDirectorThreadsKMarket()

        # 하위 호환용 테마 참조
        self.lifestyle_themes = ORIGINAL_LIFESTYLE_THEMES
        self.personas = ORIGINAL_PERSONAS
        self.kmarket_blog_themes = KMARKET_BLOG_THEMES
        self.easytax_blog_themes = EASYTAX_BLOG_THEMES

    # ─────────────────────────────────────────────────────────────
    # 🎬 숏폼 & 카드뉴스 기획안 생성 (호환 인터페이스)
    # ─────────────────────────────────────────────────────────────
    def plan_daily_scenario(self, lang: str = "en", service_id: str = "easytax") -> Dict[str, Any]:
        """숏폼/카드뉴스 전담 디렉터로 위임"""
        service_id = service_id.lower()
        if service_id == "kmarket":
            # 케이마켓 숏폼 전담 디렉터 호출 (A타입 실물 피드 vs B타입 5단계 감동 50:50)
            return self.shorts_kmarket.plan_daily_scenario(lang=lang)
        else:
            # 이지텍스 숏폼 전담 디렉터 호출 (6대 감정 테마 x 페르소나)
            return self.shorts_easytax.plan_daily_scenario(lang=lang)

    # ─────────────────────────────────────────────────────────────
    # 📝 블로그 전용 기획안 추출 (호환 인터페이스)
    # ─────────────────────────────────────────────────────────────
    def get_kmarket_blog_scenario(self, theme_index: Optional[int] = None) -> Dict[str, Any]:
        """K-Market 블로그 전담 디렉터로 위임 (40대 실전 라이프 테마)"""
        return self.blog_kmarket.get_scenario(theme_index=theme_index)

    def get_easytax_blog_scenario(self, theme_index: Optional[int] = None) -> Dict[str, Any]:
        """EasyTax 블로그 전담 디렉터로 위임 (38대 실무 세무 테마)"""
        return self.blog_easytax.get_scenario(theme_index=theme_index)

    # ─────────────────────────────────────────────────────────────
    # 🧵 스레드 전용 기획안 추출 (신규 인터페이스)
    # ─────────────────────────────────────────────────────────────
    def get_threads_scenario(self, service_id: str = "easytax") -> Dict[str, Any]:
        """스레드 전담 디렉터로 위임"""
        if service_id.lower() == "kmarket":
            return self.threads_kmarket.get_thread_scenario()
        return self.threads_easytax.get_thread_scenario()
