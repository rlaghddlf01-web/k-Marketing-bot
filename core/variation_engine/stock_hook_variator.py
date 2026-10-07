# -*- coding: utf-8 -*-
"""
StockHookVariator - 📈 [StockMaster AI 전용 훅 변주기]
=====================================================
- Stock 30초 실시간 퀀트 전광판 숏폼 전용 글자수 규격:
  · 전체 대본: 210~230자 (발화속도 +10%)
  · 검증 게이트: 200 ≤ len ≤ 245
  · 공식 검색어 '스톡마스터 AI' 포함 필수 검증
- 5개 주제 범위 이탈 방지 (앱 시뮬레이터 UI 정합성 보장)
- 기존 stock_gemini_30s_script_writer.py에 1줄 import로 연결
- 캐릭터/의상/배경 프롬프트에 일절 관여하지 않음
"""

import logging
from typing import Dict, Any
from core.variation_engine.hook_archetype_rotator import HookArchetypeRotator

logger = logging.getLogger("StockHookVariator")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# StockMaster AI 전용 설정 (코드 전수 조사 확정)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STOCK_CONFIG = {
    "display_name": "StockMaster AI",
    "official_keyword": "스톡마스터 AI",
    "cta_template": "네이버에 스톡마스터 AI 검색해보세요",
    "forbidden_topics": "배당, 월배당, 배당금, 배당주, 배당수익률, 배당락, 배당 계산기, 저PBR, PBR, 적립식, 복리, 보험, 데이팅, 소개팅, 연애, 세금, 매칭, 환급",
    "forbidden_claims": "한정 무료 이벤트, 선착순 마감, 쿠폰, 사은품, 특가, 캐시백, 원금보장, 100% 급등 보장",
    "duration_sec": 32,
    # Stock 32초 글자수 규격 (코드 전수 조사 확정)
    # - 제미나이 목표: 160~185자 (30~32초 완독 규격)
    # - 무결성 게이트: 145 ≤ len ≤ 195
    "char_target_min": 160,
    "char_target_max": 185,
    "char_gate_min": 145,
    "char_gate_max": 195,
    # 공식 검색어 필수 포함 검증
    "keyword_check": "스톡마스터 AI",
}


class StockHookVariator:
    """
    StockMaster AI 전용 훅 변주기.
    기존 StockGemini30sScriptWriter의 제미나이 프롬프트에 '훅 아키타입 지시'를 주입하여
    같은 주제 안에서 매일 다른 말투의 대본을 생성하게 함.

    [절대 규칙]
    - 주제의 컨셉/기능 설명은 그대로 유지
    - 앱 시뮬레이터 UI와 불일치하는 내용 생성 금지
    - 허위 수익률 보장/이벤트 날조 절대 금지 (객관적 퀀트 데이터 원칙)
    - 캐릭터/의상/배경 프롬프트에는 일절 관여하지 않음
    - 30초 발화 기준 210~230자 규격 칼같이 준수
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
            topic_title: 주제 제목 (예: "삼성전자 vs SK하이닉스 HBM 수급 대결")
            topic_concept: 주제 상세 설명
            app_sim_visual: 앱 시연 화면 설명 (이 범위를 벗어나면 안 됨)

        Returns:
            제미나이 프롬프트에 추가할 훅 지시 텍스트
        """
        archetype = HookArchetypeRotator.get_today_archetype("stock", topic_id)
        cfg = STOCK_CONFIG

        injection = f"""
## ⚡ [오늘의 훅 스타일 지시] — 반드시 이 구조로 작성하세요!

### 오늘의 훅 아키타입: "{archetype['name']}"
- 구조: {archetype['structure']}
- 핵심 지시: {archetype['gemini_instruction']}

### 📏 [글자수 규격 — 30초 발화 타이밍 절대 준수]
- 전체 대본: **공백 포함 {cfg['char_target_min']}~{cfg['char_target_max']}자** (30초 발화속도 +10% 기준)
- 검증 허용 범위: {cfg['char_gate_min']}~{cfg['char_gate_max']}자
- 이 범위를 벗어나면 30초 안에 발화가 불가능하거나 영상과 음성이 불일치합니다.
- 반드시 공식 검색어 '{cfg['official_keyword']}'를 포함하세요.

### 🚨 [허위 마케팅 및 가짜 이벤트 날조 전면 금지 (절대 위반 금지)]
- StockMaster AI는 객관적 퀀트 데이터 분석 플랫폼입니다.
- **절대 '원금보장', '100% 급등 보장', '한정 무료 이벤트', '선착순 마감', '사은품' 등의 거짓말 문구를 지어내지 마세요.**
- 오직 제공된 "{topic_title}"의 실제 퀀트 기능({topic_concept})만을 객관적이고 스마트한 금융 아나운서 어조로 소개하세요.

### 🚨 [주제 범위 이탈 절대 금지]
- 이 대본은 반드시 "{topic_title}" 주제에 대한 것이어야 합니다.
- 앱 시연 구간의 내용은 반드시 다음 화면과 일치해야 합니다:
  → 시연 화면: {app_sim_visual}
- 다른 주제({cfg['forbidden_topics']})로 절대 넘어가지 마세요.

### 🎯 [훅 파괴력 강화 규칙]
1. 대본 시작 부분의 **첫 문장은 반드시 0.5초 만에 시선을 잡는 킬러 한 줄**이어야 합니다.
2. 기존의 "~하신 적 있으시죠?", "~하고 계신가요?" 같은 부드러운 질문형 시작을 **전면 금지**합니다.
3. 위의 "{archetype['name']}" 구조를 따라 **결론/수치/반전/스토리/팩트** 중 하나로 강렬하게 시작하세요.
4. CTA는 반드시 "{cfg['cta_template']}" 문구를 포함하세요.
5. **글자수가 위 규격을 벗어나면 TTS가 깨지므로 절대 초과하거나 미달하지 마세요.**
"""
        logger.info(
            f"🎣 [Stock 변주 엔진] 주제#{topic_id} '{topic_title}' "
            f"→ 오늘의 훅: {archetype['name']}"
        )
        return injection
