# -*- coding: utf-8 -*-
"""
HookArchetypeRotator - 🎣 [7가지 훅 심리 아키타입 매일 자동 로테이션]
====================================================================
- 결론먼저 / 숫자팩트 / 반전대비 / 스토리텔링 / 권위뉴스 / 도발질문 / 긴급시한
- 날짜 + 브랜드 + 주제 기반 결정론적 로테이션 (같은 날 같은 주제 → 항상 같은 훅)
- 기존 코드 0% 훼손 — 독립 레고 블록
"""

import hashlib
from datetime import date
from typing import Dict, Any, List

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7가지 훅 아키타입 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOOK_ARCHETYPES: Dict[str, Dict[str, Any]] = {

    "conclusion_first": {
        "name": "결론_먼저형",
        "structure": "첫 문장에 결론/핵심 팩트 → 왜 그런지 이유 → 명쾌한 해결책",
        "gemini_instruction": (
            "반드시 첫 문장(hook_p1)에서 주제의 핵심 결론이나 팩트를 먼저 제시하세요. "
            "'~하신 적 있으시죠?' 같은 진부한 질문으로 시작하지 말고, 핵심 팩트 결론부터 직관적으로 전달하세요. "
            "절대 '한정 이벤트', '선착순 마감' 등의 허위 마케팅 문구를 지어내지 마세요."
        ),
    },

    "number_fact": {
        "name": "숫자_팩트형",
        "structure": "구체적인 숫자 팩트(%, 금액, 시간, 비율 등) → 현실 문제 → 해결책",
        "gemini_instruction": (
            "반드시 첫 문장(hook_p1)에 주제와 관련된 구체적인 숫자(비율, 시간, 인원수 등)를 포함하여 팩트로 시작하세요. "
            "막연한 표현을 배제하고 정확하고 객관적인 수치로 현실감을 부여하세요."
        ),
    },

    "contrast_reversal": {
        "name": "반전_대비형",
        "structure": "같은 상황인데 결과나 방식이 극과극인 A vs B 대비 → 이유 → 해결책",
        "gemini_instruction": (
            "같은 상황이나 조건에서 결과나 대처 방식이 극과 극으로 갈리는 두 사례를 대비시켜 시작하세요. "
            "시청자의 호기심과 공감을 자극하는 직관적인 대비를 연출하세요."
        ),
    },

    "story": {
        "name": "스토리텔링형",
        "structure": "실제 겪을 법한 1인의 생생한 현실 경험/고민 → 상황 전개 → 해결책",
        "gemini_instruction": (
            "실제 겪을 법한 한 사람의 현실적인 고민이나 에피소드로 시작하세요. "
            "과장하지 않고 누구나 '맞아, 저런 적 있지' 하고 깊이 공감할 수 있는 담백한 일상 어조를 유지하세요."
        ),
    },

    "authority_news": {
        "name": "권위_뉴스형",
        "structure": "객관적 데이터/통계/리포트 팩트 → 나에게 주는 시사점 → 해결책",
        "gemini_instruction": (
            "공식 통계, 설문조사 결과, 객관적 데이터 리포트 팩트로 시작하세요. "
            "신뢰도 높은 팩트를 바탕으로 시청자가 체감할 수 있는 실질적인 가치를 전달하세요."
        ),
    },

    "provocative_question": {
        "name": "도발_질문형",
        "structure": "현실 공감 또는 뼈 때리는 질문 1줄 → 명쾌한 답변 → 스마트한 해결책",
        "gemini_instruction": (
            "시청자의 깊은 현실 공감을 자극하는 세련된 질문 한 줄로 시작하세요. "
            "가짜 이벤트나 억지 긴급성을 지어내지 말고, 실제 겪는 불편한 상황이나 딜레마를 짚어주세요."
        ),
    },

    "trend_insight": {
        "name": "트렌드_인사이트형",
        "structure": "2030 라이프스타일 트렌드 및 데이터 팩트 → 왜 그런지 → 해결책",
        "gemini_instruction": (
            "요즘 세대의 실제 트렌드와 라이프스타일 팩트로 시작하세요. "
            "절대 '한정 이벤트'나 '선착순 마감' 같은 허위 마케팅 문구를 지어내지 마세요."
        ),
    }
}

ARCHETYPE_KEYS: List[str] = list(HOOK_ARCHETYPES.keys())


class HookArchetypeRotator:
    """날짜 + 브랜드 + 주제 기반으로 7가지 훅 아키타입을 결정론적 로테이션

    사용법:
        archetype = HookArchetypeRotator.get_today_archetype("aura", 1)
        print(archetype["name"])  # → "결론_먼저형" (날짜에 따라 다름)
    """

    @classmethod
    def get_today_archetype(cls, brand: str, topic_id: int) -> Dict[str, Any]:
        """
        같은 날 + 같은 브랜드 + 같은 주제 → 항상 같은 훅 반환 (결정론적)
        다른 날 → 다른 훅 반환
        같은 날이라도 브랜드/주제가 다르면 → 다른 훅 반환

        Args:
            brand: "aura" | "insurance" | "stock"
            topic_id: 주제 번호 (1~8)

        Returns:
            {"key": "conclusion_first", "name": "결론_먼저형", "structure": ..., "gemini_instruction": ...}
        """
        seed = f"{date.today().isoformat()}_{brand}_{topic_id}"
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(ARCHETYPE_KEYS)
        key = ARCHETYPE_KEYS[idx]
        return {
            "key": key,
            **HOOK_ARCHETYPES[key]
        }

    @classmethod
    def get_all_archetypes(cls) -> Dict[str, Dict]:
        """전체 7가지 아키타입 반환 (디버깅/프리뷰용)"""
        return HOOK_ARCHETYPES

    @classmethod
    def preview_week(cls, brand: str, topic_id: int) -> List[Dict[str, str]]:
        """향후 7일간의 훅 로테이션 미리보기 (디버깅용)

        Returns:
            [{"date": "2026-09-29", "archetype": "결론_먼저형"}, ...]
        """
        from datetime import timedelta
        results = []
        today = date.today()
        for i in range(7):
            d = today + timedelta(days=i)
            seed = f"{d.isoformat()}_{brand}_{topic_id}"
            idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(ARCHETYPE_KEYS)
            key = ARCHETYPE_KEYS[idx]
            results.append({
                "date": d.isoformat(),
                "archetype": HOOK_ARCHETYPES[key]["name"]
            })
        return results
