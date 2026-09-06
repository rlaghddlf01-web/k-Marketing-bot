# -*- coding: utf-8 -*-
"""
[신규 모듈] GeminiSmartClient (core/gemini_smart_client.py)
• 역할: 구글 Gemini API 호출 시 [1순위: 전담 무료키 ➔ 2순위: 보조 무료키 ➔ 3순위: 유료키 ➔ 4순위: 기본키]
        순으로 실시간 감지하여 자동 전환(Smart Failover)하는 고가용성 클라이언트
• 특징:
  1. 429 RESOURCE_EXHAUSTED (선불 크레딧 소진 / 무료 분당 15회 초과) 발생 시 즉시 다음 키로 무중단 롤오버
  2. 평상시 비용 0원 무료키를 100% 우선 활용하여 마케팅 API 비용 절감
  3. 모든 키 실패 시 예외를 투명하게 전달하여 각 모듈의 오프라인 템플릿(Fallback)으로 최종 안전 착륙
• 원칙: 모듈 분리 원칙(Rule 1), 땜질 코딩 금지(Rule 5) 준수
"""

import logging
from typing import List, Optional, Any
from config import (
    GEMINI_FREE_API_KEY_EASYTAX,
    GEMINI_FREE_API_KEY_KMARKET,
    GEMINI_API_KEY_EASYTAX,
    GEMINI_API_KEY_KMARKET,
    GEMINI_API_KEY
)

logger = logging.getLogger("GeminiSmartClient")


class GeminiSmartClient:
    """
    구글 Gemini 멀티티어 자동 롤오버 스마트 클라이언트
    [무료키 1순위 -> 보조 무료키 -> 유료키 -> 기본키]
    """
    def __init__(self, service_id: str = "easytax"):
        self.service_id = service_id.lower()
        self.key_chain: List[dict] = []
        self._build_key_chain()
        self._active_key_index = 0

    def _build_key_chain(self):
        """서비스 ID에 맞춤화된 우선순위 키 체인 구성"""
        if self.service_id == "easytax":
            candidates = [
                {"name": "EASYTAX_FREE (무료 1순위)", "key": GEMINI_FREE_API_KEY_EASYTAX},
                {"name": "KMARKET_FREE (무료 2순위)", "key": GEMINI_FREE_API_KEY_KMARKET},
                {"name": "EASYTAX_PAID (유료 3순위)", "key": GEMINI_API_KEY_EASYTAX},
                {"name": "KMARKET_PAID (유료 4순위)", "key": GEMINI_API_KEY_KMARKET},
                {"name": "DEFAULT_KEY (기본 5순위)", "key": GEMINI_API_KEY},
            ]
        else:
            candidates = [
                {"name": "KMARKET_FREE (무료 1순위)", "key": GEMINI_FREE_API_KEY_KMARKET},
                {"name": "EASYTAX_FREE (무료 2순위)", "key": GEMINI_FREE_API_KEY_EASYTAX},
                {"name": "KMARKET_PAID (유료 3순위)", "key": GEMINI_API_KEY_KMARKET},
                {"name": "EASYTAX_PAID (유료 4순위)", "key": GEMINI_API_KEY_EASYTAX},
                {"name": "DEFAULT_KEY (기본 5순위)", "key": GEMINI_API_KEY},
            ]

        # 중복 제거 및 빈 키 필터링
        seen_keys = set()
        self.key_chain = []
        for c in candidates:
            k = c.get("key", "").strip() if c.get("key") else ""
            if k and k not in seen_keys:
                seen_keys.add(k)
                self.key_chain.append({"name": c["name"], "key": k})

        names = [k["name"] for k in self.key_chain]
        logger.info(f"[{self.service_id.upper()}] GeminiSmartClient 키 체인 구성 완료 (총 {len(self.key_chain)}개): {' ➔ '.join(names)}")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @property
    def models(self):
        """models.generate_content 인터페이스 투명 호환 래퍼"""
        return self

    def generate_content(self, model: str, contents: Any, **kwargs):
        """
        우선순위 키 체인을 순회하며 429 / 인증 에러 발생 시 자동으로 다음 키로 전환 호출
        """
        if not self.key_chain:
            raise RuntimeError(f"[{self.service_id.upper()}] 사용 가능한 Gemini API 키가 없습니다.")

        last_error = None
        # 현재 활성 키부터 시작하여 모든 키 순회
        start_idx = self._active_key_index
        total_keys = len(self.key_chain)

        for i in range(total_keys):
            idx = (start_idx + i) % total_keys
            key_info = self.key_chain[idx]
            key_name = key_info["name"]
            api_key = key_info["key"]

            try:
                client = self._get_genai_client(api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    **kwargs
                )
                # 성공 시 해당 키를 활성 키로 유지
                self._active_key_index = idx
                return response

            except Exception as e:
                err_msg = str(e)
                last_error = e
                is_quota_or_billing = any(k in err_msg for k in ["429", "RESOURCE_EXHAUSTED", "depleted", "quota", "quotaExceeded"])

                if is_quota_or_billing:
                    next_idx = (idx + 1) % total_keys
                    next_name = self.key_chain[next_idx]["name"] if total_keys > 1 else "None"
                    logger.warning(
                        f"⚠️ [{self.service_id.upper()}] {key_name} 할당량/크레딧 초과 감지 -> 다음 키({next_name})로 자동 롤오버!"
                    )
                else:
                    logger.warning(
                        f"⚠️ [{self.service_id.upper()}] {key_name} 호출 에러: {err_msg[:120]} -> 다음 키 시도"
                    )

        logger.error(f"❌ [{self.service_id.upper()}] 모든 Gemini API 키 체인 호출 실패: {last_error}")
        raise last_error
