# -*- coding: utf-8 -*-
"""
[통합 모듈] GeminiSmartClient (core/gemini_smart_client.py)
• 역할: 구글 Gemini API 호출 시 서비스(이지택스/마켓) 구분 없이 통합 키 풀 관리
• 호출 순서:
  1단계 [무료키 풀]: 무료키 1번 ➔ 2번 ➔ 3번 ➔ 4번 순차 호출 (Round-Robin 분산 & 스마트 롤오버)
  2단계 [유료키 풀]: 모든 무료키 소진/실패 시 비로소 유료키 1번 ➔ 2번 순차 호출 & 롤오버
• 특징:
  1. 평상시 비용 0원인 4개의 무료키를 골고루 순차 호출하여 분당 RPM/TPM을 4배로 극대화 (한 계정에 부하 몰림 방지)
  2. 429 RESOURCE_EXHAUSTED / 할당량 초과 시 즉시 다음 순번 키로 무중단 자동 전환
  3. 무료키 4개가 모두 소진되었을 때만 유료키(1번, 2번)로 전환하여 비용 0원 유지 극대화
"""

import logging
import threading
from typing import List, Optional, Any
from config import (
    GEMINI_FREE_KEYS,
    GEMINI_PAID_KEYS,
    GEMINI_FREE_KEY_1,
    GEMINI_FREE_KEY_2,
    GEMINI_FREE_KEY_3,
    GEMINI_FREE_KEY_4,
    GEMINI_PAID_KEY_1,
    GEMINI_PAID_KEY_2
)

logger = logging.getLogger("GeminiSmartClient")


class GeminiSmartClient:
    """
    통합 Gemini 순차 호출 & 스마트 롤오버 클라이언트
    [무료키 1번 -> 2번 -> 3번 -> 4번 순차호출 -> 유료키 1번 -> 2번 순차호출]
    """
    # 전역 순차 인덱스 및 스레드 락 (서비스/스레드 간 공유)
    _free_counter = 0
    _paid_counter = 0
    _lock = threading.Lock()

    def __init__(self, service_id: str = "general"):
        self.service_id = service_id.lower()
        self.free_chain: List[dict] = []
        self.paid_chain: List[dict] = []
        self._build_chains()

    def _build_chains(self):
        """통합 키 풀 구성: 무료 1~4번, 유료 1~2번"""
        raw_free = [
            {"name": "무료키 1번", "key": GEMINI_FREE_KEY_1},
            {"name": "무료키 2번", "key": GEMINI_FREE_KEY_2},
            {"name": "무료키 3번", "key": GEMINI_FREE_KEY_3},
            {"name": "무료키 4번", "key": GEMINI_FREE_KEY_4},
        ]
        raw_paid = [
            {"name": "유료키 1번", "key": GEMINI_PAID_KEY_1},
            {"name": "유료키 2번", "key": GEMINI_PAID_KEY_2},
        ]

        seen = set()
        self.free_chain = []
        for item in raw_free:
            k = item["key"].strip() if item.get("key") else ""
            if k and k not in seen:
                seen.add(k)
                self.free_chain.append({"name": item["name"], "key": k})

        self.paid_chain = []
        for item in raw_paid:
            k = item["key"].strip() if item.get("key") else ""
            if k and k not in seen:
                seen.add(k)
                self.paid_chain.append({"name": item["name"], "key": k})

        free_names = [f["name"] for f in self.free_chain]
        paid_names = [p["name"] for p in self.paid_chain]
        logger.info(
            f"[{self.service_id.upper()}] GeminiSmartClient 통합 풀 준비 완료 "
            f"(무료 {len(self.free_chain)}개: {' ➔ '.join(free_names)} | 유료 {len(self.paid_chain)}개: {' ➔ '.join(paid_names)})"
        )

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @property
    def models(self):
        """models.generate_content 인터페이스 투명 호환"""
        return self

    def generate_content(self, model: str, contents: Any, **kwargs):
        """
        1순위: 무료키 1 -> 2 -> 3 -> 4 순차 호출 및 장애 시 다음 무료키로 순차 롤오버
        2순위: 모든 무료키 실패/소진 시 유료키 1 -> 2 순차 호출
        """
        last_error = None

        # -------------------------------------------------------------
        # 1단계: 무료키 풀 순차 호출 (Round-Robin & Failover)
        # -------------------------------------------------------------
        if self.free_chain:
            with GeminiSmartClient._lock:
                start_free_idx = GeminiSmartClient._free_counter % len(self.free_chain)
                GeminiSmartClient._free_counter += 1

            for offset in range(len(self.free_chain)):
                current_idx = (start_free_idx + offset) % len(self.free_chain)
                key_info = self.free_chain[current_idx]
                key_name = key_info["name"]
                api_key = key_info["key"]

                try:
                    client = self._get_genai_client(api_key)
                    logger.info(f"✨ [{self.service_id.upper()}] {key_name} 호출 중... (모델: {model})")
                    response = client.models.generate_content(
                        model=model,
                        contents=contents,
                        **kwargs
                    )
                    return response

                except Exception as e:
                    err_msg = str(e)
                    last_error = e
                    is_quota = any(k in err_msg for k in ["429", "RESOURCE_EXHAUSTED", "quota", "quotaExceeded", "depleted"])
                    reason = "할당량/속도제한 초과" if is_quota else "일시적 오류"
                    logger.warning(
                        f"⚠️ [{self.service_id.upper()}] {key_name} {reason}: {err_msg[:100]}... -> 다음 무료키로 순차 전환!"
                    )

        # -------------------------------------------------------------
        # 2단계: 유료키 풀 순차 호출 (모든 무료키 소진/실패 시에만 진입)
        # -------------------------------------------------------------
        logger.warning(f"🚨 [{self.service_id.upper()}] 모든 무료키 소진/실패 -> 유료키 풀(1~2번)로 전환 호출합니다.")

        if self.paid_chain:
            with GeminiSmartClient._lock:
                start_paid_idx = GeminiSmartClient._paid_counter % len(self.paid_chain)
                GeminiSmartClient._paid_counter += 1

            for offset in range(len(self.paid_chain)):
                current_idx = (start_paid_idx + offset) % len(self.paid_chain)
                key_info = self.paid_chain[current_idx]
                key_name = key_info["name"]
                api_key = key_info["key"]

                try:
                    client = self._get_genai_client(api_key)
                    logger.info(f"💳 [{self.service_id.upper()}] {key_name} 호출 중... (모델: {model})")
                    response = client.models.generate_content(
                        model=model,
                        contents=contents,
                        **kwargs
                    )
                    return response

                except Exception as e:
                    err_msg = str(e)
                    last_error = e
                    logger.warning(
                        f"⚠️ [{self.service_id.upper()}] {key_name} 오류: {err_msg[:100]}... -> 다음 유료키 시도"
                    )

        logger.error(f"❌ [{self.service_id.upper()}] 무료/유료 모든 Gemini 키 호출 실패: {last_error}")
        raise last_error
