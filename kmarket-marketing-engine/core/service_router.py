import json
from typing import Dict, Any, Tuple
from config import DATA_DIR, BASE_URLS

class ServiceRouter:
    """
    AI 및 키워드 기반 지능형 서비스 라우터
    (다국어 질문/트렌드를 분석하여 6대 서비스 중 최적의 솔루션 자동 매핑)
    """
    def __init__(self):
        self.services = self._load_services()

    def _load_services(self) -> Dict[str, Any]:
        services_file = DATA_DIR / "services.json"
        if services_file.exists():
            with open(services_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def route_query(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        질문 텍스트를 분석하여 가장 적합한 서비스 ID와 서비스 메타데이터를 반환
        기본값은 kmarket 또는 easytax
        """
        text_lower = text.lower()
        best_service_id = "kmarket"
        max_matches = 0

        for s_id, s_info in self.services.items():
            keywords = s_info.get("keywords", [])
            matches = sum(1 for kw in keywords if kw.lower() in text_lower)
            
            # 활성 상태인 서비스에 기본 가중치 부여
            if s_info.get("active", False):
                matches += 1

            if matches > max_matches:
                max_matches = matches
                best_service_id = s_id

        service_data = self.services.get(best_service_id, {})
        # 최신 Base URL 보정
        service_data["landing_url"] = BASE_URLS.get(best_service_id, service_data.get("landing_url", "https://k-market.app"))
        
        return best_service_id, service_data

    def get_service(self, service_id: str) -> Dict[str, Any]:
        """특정 서비스 정보 조회"""
        service_data = self.services.get(service_id, {})
        service_data["landing_url"] = BASE_URLS.get(service_id, service_data.get("landing_url", "https://ktrs-market.vercel.app"))
        return service_data

    def get_service_landing_url(self, service_id: str, lang: str = "ko", path: str = "") -> str:
        """
        1:1 매칭 서비스 및 언어별 실시간 접속 주소 생성:
        - kmarket: https://ktrs-market.vercel.app/{lang}
        - easytax: https://ktrs-service.vercel.app/?lang={lang}
        """
        base_domain = BASE_URLS.get(service_id, "https://ktrs-market.vercel.app")
        if service_id == "kmarket" or "ktrs-market" in base_domain:
            return f"{base_domain.rstrip('/')}/{lang}/{path.strip('/')}" if path else f"{base_domain.rstrip('/')}/{lang}"
        else:
            sub = f"/{path.strip('/')}" if path else ""
            return f"{base_domain.rstrip('/')}{sub}?lang={lang}"
