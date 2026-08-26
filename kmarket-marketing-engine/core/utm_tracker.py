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
    def build_service_landing_url(cls, service_id: str, base_domain: str, lang: str = "en",
                                  path: str = "", source: str = "direct", 
                                  medium: str = "marketing", campaign: str = "", 
                                  content: Optional[str] = None) -> str:
        """
        서비스별 실제 라우팅 방식에 100% 맞춘 최종 랜딩 URL 생성:
        - K-Market: Path 기반 (예: https://ktrs-market.vercel.app/vi)
        - EasyTax: Query 기반 (예: https://ktrs-service.vercel.app/?lang=vi 또는 https://ktrs-service.vercel.app/welcome?lang=vi)
        """
        base = base_domain.rstrip("/")
        subpath = path.strip("/")
        
        if service_id == "kmarket" or "ktrs-market" in base:
            # K-Market: Path 기반 /{lang}
            full_base = f"{base}/{lang}/{subpath}" if subpath else f"{base}/{lang}"
            return cls.build_url(
                base_url=full_base,
                source=source,
                medium=medium,
                campaign=campaign,
                content=content,
                lang=None
            )
        else:
            # EasyTax (KTRS Service): Query 기반 ?lang={lang}
            full_base = f"{base}/{subpath}" if subpath else base
            return cls.build_url(
                base_url=full_base,
                source=source,
                medium=medium,
                campaign=campaign,
                content=content,
                lang=lang
            )

    @classmethod
    def build_landing_url(cls, base_domain: str, lang: str = "en", path: str = "",
                          source: str = "direct", medium: str = "marketing", 
                          campaign: str = "", content: Optional[str] = None,
                          service_id: str = "kmarket") -> str:
        """하위 호환용 래퍼 함수"""
        return cls.build_service_landing_url(
            service_id=service_id,
            base_domain=base_domain,
            lang=lang,
            path=path,
            source=source,
            medium=medium,
            campaign=campaign,
            content=content
        )

    @classmethod
    def generate_campaign_tag(cls, service_id: str, channel: str, lang: str) -> str:
        """표준 캠페인 태그 생성 (예: easytax_reddit_vi_202608)"""
        now_str = datetime.datetime.now().strftime("%Y%m")
        return f"{service_id}_{channel}_{lang}_{now_str}"
