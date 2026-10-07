# -*- coding: utf-8 -*-
"""
InsuranceHookVariator - 🛡️ [보험 리밸런스 전용 훅 변주기]
=========================================================
- 보험 22초 숏폼 전용 글자수 규격:
  · 훅 합산(hook_p1+p2): 55~65자 (검증 게이트 45~70자)
  · 앱 시연(app_speech): 75~100자 (검증 게이트 65~115자)
  · CTA: 18~25자 (공식 검색어 '보험 리밸런스' 필수)
  · 전체 합산: 150~185자 (검증 게이트 135~195자)
  · Wan S2V 10초 립싱크: 58~64자 (Part1 30자 + Part2 30자)
- 8개 주제 범위 이탈 방지 (앱 시뮬레이터 UI 정합성 보장)
- 기존 insurance_shorts_script_writer.py에 1줄 import로 연결
- 캐릭터/의상/배경 프롬프트에 일절 관여하지 않음
"""

import logging
from typing import Dict, Any
from core.variation_engine.hook_archetype_rotator import HookArchetypeRotator

logger = logging.getLogger("InsuranceHookVariator")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 보험 리밸런스 전용 설정 (코드 전수 조사 확정)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSURANCE_CONFIG = {
    "display_name": "보험 리밸런스",
    "official_keyword": "보험 리밸런스",
    "cta_template": "네이버에 보험 리밸런스 검색해보세요",
    "forbidden_topics": "데이팅, 소개팅, 주식, 투자, 연애, 매칭, 종목",
    "forbidden_claims": "한정 무료 이벤트, 선착순 마감, 사은품 증정, 오늘만 특가, 캐시백 당첨",
    "duration_sec": 22,
    # 보험 22초 글자수 규격 (코드 전수 조사 확정)
    # ── 구간별 제미나이 목표 ──
    "hook_p1_target_min": 25,
    "hook_p1_target_max": 32,
    "hook_p2_target_min": 25,
    "hook_p2_target_max": 32,
    "hook_total_target_min": 55,
    "hook_total_target_max": 65,
    "app_speech_target_min": 75,
    "app_speech_target_max": 100,
    "cta_target_min": 18,
    "cta_target_max": 25,
    "full_target_min": 150,
    "full_target_max": 185,
    # ── 무결성 게이트 검증 범위 ──
    "hook_total_gate_min": 45,
    "hook_total_gate_max": 70,
    "app_speech_gate_min": 65,
    "app_speech_gate_max": 115,
    "full_gate_min": 135,
    "full_gate_max": 195,
    # ── Wan S2V 10초 립싱크 ──
    "wan_s2v_min": 58,
    "wan_s2v_max": 64,
}


class InsuranceHookVariator:
    """
    보험 리밸런스 전용 훅 변주기.
    기존 InsuranceShortsScriptWriter의 제미나이 프롬프트에 '훅 아키타입 지시'를 주입하여
    같은 주제 안에서 매일 다른 말투의 대본을 생성하게 함.

    [절대 규칙]
    - 주제의 컨셉/기능 설명은 그대로 유지
    - 앱 시뮬레이터 UI와 불일치하는 내용 생성 금지
    - 허위 이벤트/선착순/사은품 등 가짜 마케팅 문구 날조 절대 금지
    - 캐릭터/의상/배경 프롬프트에는 일절 관여하지 않음
    - 구간별 글자수 규격 칼같이 준수
    """

    def build_hook_injection(
        self,
        topic_id: int,
        topic_title: str,
        topic_concept: str,
        app_sim_visual: str,
    ) -> str:
        """
        기존 제미나이 프롬프트에 '추가 삽입'할 훅 아키타입 지시문을 생성.

        Args:
            topic_id: 주제 번호 (1~8)
            topic_title: 주제 제목 (예: "실손의료비 4세대 전환 절약")
            topic_concept: 주제 상세 설명
            app_sim_visual: 앱 시연 화면 설명 (이 범위를 벗어나면 안 됨)

        Returns:
            제미나이 프롬프트에 추가할 훅 지시 텍스트
        """
        archetype = HookArchetypeRotator.get_today_archetype("insurance", topic_id)
        cfg = INSURANCE_CONFIG

        injection = f"""
## ⚡ [오늘의 훅 스타일 지시] — 반드시 이 구조로 작성하세요!

### 오늘의 훅 아키타입: "{archetype['name']}"
- 구조: {archetype['structure']}
- 핵심 지시: {archetype['gemini_instruction']}

### 📏 [글자수 규격 — Wan S2V 립싱크 & TTS 타이밍 절대 준수]
⚠️ 아래 글자수를 벗어나면 Wan 2.2 S2V 10.12초 립싱크에서 입 모양과 음성이 어긋납니다!

| 구간 | 글자수 (공백 포함) | 설명 |
|:---|:---:|:---|
| hook_p1 (0~5초) | **{cfg['hook_p1_target_min']}~{cfg['hook_p1_target_max']}자** | 킬러 훅 첫 줄 |
| hook_p2 (5~10초) | **{cfg['hook_p2_target_min']}~{cfg['hook_p2_target_max']}자** | 훅 확장 |
| hook 합산 (0~10초) | **{cfg['hook_total_target_min']}~{cfg['hook_total_target_max']}자** | hook_p1 + hook_p2 (칼검증) |
| app_speech (10~20초) | **{cfg['app_speech_target_min']}~{cfg['app_speech_target_max']}자** | 앱 시연 나레이션 (8~9초 발화) |
| cta_speech (20~22초) | **{cfg['cta_target_min']}~{cfg['cta_target_max']}자** | 네이버 검색 CTA |
| **전체 합산** | **{cfg['full_target_min']}~{cfg['full_target_max']}자** | 전체 발화 (절대 초과/미달 금지) |

⚠️ Wan S2V 10초 립싱크: Part1 30자 + Part2 30자 = **{cfg['wan_s2v_min']}~{cfg['wan_s2v_max']}자**. 이 범위 밖이면 입이 안 맞음!

### 🚨 [허위 마케팅 및 가짜 이벤트 날조 전면 금지 (절대 위반 금지)]
- 보험 리밸런스는 대한민국 34개 보험사 비교 플랫폼입니다.
- **절대 '한정 이벤트', '선착순 마감', '사은품 증정', '오늘만 특가' 등의 거짓말 문구를 지어내지 마세요.**
- 오직 제공된 "{topic_title}"의 실제 기능({topic_concept})만을 객관적이고 신뢰감 있는 금융 아나운서 어조로 소개하세요.

### 🚨 [주제 범위 이탈 절대 금지]
- 이 대본은 반드시 "{topic_title}" 주제에 대한 것이어야 합니다.
- 앱 시연 구간(app_speech)의 내용은 반드시 다음 화면과 일치해야 합니다:
  → 시연 화면: {app_sim_visual}
- 다른 주제({cfg['forbidden_topics']})로 절대 넘어가지 마세요.

### 🎯 [훅 파괴력 강화 규칙]
1. hook_p1의 **첫 문장은 반드시 0.5초 만에 시선을 잡는 킬러 한 줄**이어야 합니다.
2. 기존의 "~하신 적 있으시죠?", "~하고 계신가요?" 같은 부드러운 질문형 시작을 **전면 금지**합니다.
3. 위의 "{archetype['name']}" 구조를 따라 **결론/수치/반전/스토리/팩트** 중 하나로 강렬하게 시작하세요.
4. CTA는 반드시 "{cfg['cta_template']}" 문구를 포함하세요.
5. **글자수가 위 규격을 벗어나면 TTS/립싱크가 깨지므로 절대 초과하거나 미달하지 마세요.**
"""
        logger.info(
            f"🎣 [보험 변주 엔진] 주제#{topic_id} '{topic_title}' "
            f"→ 오늘의 훅: {archetype['name']}"
        )
        return injection
