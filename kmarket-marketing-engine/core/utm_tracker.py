import urllib.parse
import datetime
from typing import Dict, Any, Optional

class UTMTracker:
    """
    동적 UTM 링크 빌더 및 성과 기여도 추적 엔진
    """
    
    @staticmethod
    def build_url(base_url: str, source: str, medium: str, campaign: str, 
                  content: Optional[str] = None, lang: Optional[str] = None) -> str:
        """
        동적 UTM 파라미터가 부착된 최종 랜딩 URL 생성
        예: https://easy-tax.app?utm_source=reddit&utm_medium=lead_bot&utm_campaign=easytax_vi_2026&utm_content=comment_reply&lang=vi
        """
        params = {
            "utm_source": source.lower().replace(" ", "_"),
            "utm_medium": medium.lower().replace(" ", "_"),
            "utm_campaign": campaign.lower().replace(" ", "_"),
        }
        
        if content:
            params["utm_content"] = content.lower().replace(" ", "_")
        if lang:
            params["lang"] = lang.lower()

        # 기존 base_url에 파라미터 결합
        url_parts = urllib.parse.urlparse(base_url)
        query = dict(urllib.parse.parse_qsl(url_parts.query))
        query.update(params)
        
        new_query = urllib.parse.urlencode(query)
        new_url_parts = url_parts._replace(query=new_query)
        
        return urllib.parse.urlunparse(new_url_parts)

    @classmethod
    def generate_campaign_tag(cls, service_id: str, channel: str, lang: str) -> str:
        """표준 캠페인 태그 생성 (예: easytax_reddit_vi_202608)"""
        now_str = datetime.datetime.now().strftime("%Y%m")
        return f"{service_id}_{channel}_{lang}_{now_str}"
