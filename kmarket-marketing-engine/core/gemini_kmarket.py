"""
KMarketGeminiEngine - 🛒 K-Market 전용 경량 Facade 오케스트레이터
- Blog: KMarketGeminiBlog (1회 한국어 마스터 글 + 동양인/가구 사진 2장 집필)
- Reddit: KMarketGeminiReddit (중고거래/무료나눔 답변)
- Shorts: KMarketGeminiShorts (0원 나눔 숏폼 대본)
"""

import logging
from typing import Dict, Any, Optional
from core.supabase_manager import SupabaseManager
from core.gemini_kmarket_blog import KMarketGeminiBlog
from core.gemini_kmarket_reddit import KMarketGeminiReddit
from core.gemini_kmarket_shorts import KMarketGeminiShorts

logger = logging.getLogger("KMarketGeminiEngine")

class KMarketGeminiEngine:
    """K-Market 전용 통합 Facade 엔진"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.blog_engine = KMarketGeminiBlog(self.supabase_mgr)
        self.reddit_engine = KMarketGeminiReddit(self.supabase_mgr)
        self.shorts_engine = KMarketGeminiShorts(self.supabase_mgr)

    def write_master_korean_article(self, directive_pkg: Dict[str, Any], landing_url: str = "", hashtags: str = "", thumb_url: str = "", thumb_url_1: str = "", thumb_url_2: str = "") -> Dict[str, str]:
        """한국어 2,000자 최고급 마스터 칼럼 1회 집필 (본문 상단 대표 사진 1장)"""
        return self.blog_engine.write_master_korean_article(directive_pkg, landing_url, hashtags, thumb_url, thumb_url_1, thumb_url_2)

    def write_full_blog_article(self, directive_pkg: Dict[str, Any], target_lang: str = "ko", landing_url: str = "", hashtags: str = "", thumb_url: str = "") -> Dict[str, str]:
        """하위 호환성 유지"""
        return self.blog_engine.write_master_korean_article(directive_pkg, landing_url, hashtags, thumb_url, thumb_url)

    def generate_reddit_reply(self, post_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        return self.reddit_engine.generate_reddit_reply(post_data)

    def generate_shorts_script(self, theme_pkg: Dict[str, Any]) -> Dict[str, Any]:
        return self.shorts_engine.generate_shorts_script(theme_pkg)
