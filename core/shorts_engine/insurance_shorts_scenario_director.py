# -*- coding: utf-8 -*-
"""
InsuranceShortsScenarioDirector - 🎬 [보험 리밸런스 22초 실전 2단 직결 숏폼 대본 디렉터]
- 심의 100% 프리패스 (특정 보험사/상품 0% 언급, 팩트 기반 약관 원리 분석, 자가점검 유도)
- 군더더기 없는 실전 2단 직결 구조:
  1) [0초 ~ 10초] 실제 타깃 연령 일반인 인물 립싱크 킬러 훅 (내돈내산 현실 썰)
  2) [10초 ~ 20초] 우리 앱 아이프레임 실제 시연 및 무료 점검 해결책 나레이션
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceShortsScenarioDirector")


class InsuranceShortsScenarioDirector:
    """🛡️ 보험 리밸런스 8대 국민 보험 22초 완결형 숏폼 대본 엔진"""

    SCRIPTS_22S = {
        1: {
            "topic_id": 1,
            "theme_name": "실손의료비 4세대 전환 손익",
            "theme_code": "silbi_gen4",
            "gender": "female",
            "hook_p1_5s": "병원도 안 가는데 옛날 실비보험 계속 유지해야 할까요?",
            "hook_p2_5s": "4세대 전환 시 내 조건별 실시간 손익을 바로 확인해보세요!",
            "hook_0_10s": "병원도 안 가는데 옛날 실비보험 계속 유지해야 할까요? 4세대 전환 시 내 조건별 실시간 손익을 바로 확인해보세요!",
            "app_10_20s": "보험 리밸런스에서 익명으로 내 4세대 전환 손익을 1초 만에 확인해보세요.",
            "hero_copy": "비급여 이용량에 맞춘 실손 손익 자가진단!",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "s2v_motion_prompt": (
                "a relatable 42-year-old Korean woman in clean stylish civilian casual clothes sitting comfortably in a bright room, looking directly into camera with genuine friendly expression, "
                "speaking clearly with precise lip sync and articulate mouth motion, gentle head nodding, subtle hand gestures explaining facts, "
                "no phone in hand, confident trustworthy motion"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        },
        2: {
            "topic_id": 2,
            "theme_name": "운전자보험 1만원의 법칙",
            "theme_code": "driver_insurance",
            "gender": "male",
            "hook_p1_5s": "운전자보험 매달 3, 4만 원씩 내시나요?",
            "hook_p2_5s": "필수 3대 특약만 챙기면 월 1만 원대 설계가 가능합니다!",
            "hook_0_10s": "운전자보험 매달 3, 4만 원씩 내시나요? 필수 3대 특약만 챙기면 월 1만 원대 설계가 가능합니다!",
            "app_10_20s": "보험 리밸런스에서 증권만 스캔하면 쓸데없이 새는 중복 특약을 1초 만에 싹 정리해 줍니다.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "필수 3대 특약으로 월 13,000원 완성!",
            "s2v_motion_prompt": (
                "a sharp 36-year-old Korean male commuter driver standing on a modern city street, looking directly into camera with honest relatable gaze, "
                "speaking articulately with realistic mouth movements and natural lip synchronization, subtle head nodding in urban city background"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+4%"
        },
        3: {
            "topic_id": 3,
            "theme_name": "암보험 일반암 vs 유사암 진실",
            "theme_code": "cancer_coverage",
            "gender": "female",
            "hook_p1_5s": "암보험 5천만 원 든 줄 알았는데 갑상선암은 소액암으로 분류된다는 사실 아셨나요?",
            "hook_p2_5s": "약관상 보장 비율과 보장 범위를 꼭 점검해보세요!",
            "hook_0_10s": "암보험 5천만 원 든 줄 알았는데 갑상선암은 소액암으로 분류된다는 사실 아셨나요? 약관상 보장 비율과 보장 범위를 꼭 점검해보세요!",
            "app_10_20s": "보험 리밸런스에서 국내 34개 보험사의 진짜 일반암 보장 범위를 1초 만에 비교해보세요.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "내가 원하는 진단금으로 34개 암보험 실시간 비교!",
            "s2v_motion_prompt": (
                "a sensible 45-year-old Korean woman in cream knit sweater, looking directly into camera with articulate trustworthy eyes, "
                "speaking articulate words with natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        },
        4: {
            "topic_id": 4,
            "theme_name": "뇌경색 100% 뇌혈관질환 최저가 다이렉트 비교",
            "theme_code": "brain_vascular",
            "gender": "male",
            "hook_p1_5s": "뇌경색까지 든든하게 보장하는 뇌혈관 보험, 내 증권의 보장 범위는 안전할까요?",
            "hook_p2_5s": "내 조건만 넣으면 전 보험사 객관적 요율이 바로 나옵니다!",
            "hook_0_10s": "뇌경색까지 든든하게 보장하는 뇌혈관 보험, 내 증권의 보장 범위는 안전할까요? 내 조건만 넣으면 전 보험사 객관적 요율이 바로 나옵니다!",
            "app_10_20s": "보험 리밸런스에서 나이만 넣으면 국내 33개 보험사 실시간 최저가 순위가 1초 만에 나옵니다.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "뇌경색까지 보장하는 뇌혈관보험 객관적 비교!",
            "s2v_motion_prompt": (
                "a trustworthy 48-year-old Korean family man in stylish neat casual daily clothes, looking directly into camera with sincere honest eyes, "
                "speaking clearly with smooth natural lip sync, precise mouth movements and subtle head nods"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+3%"
        },
        5: {
            "topic_id": 5,
            "theme_name": "아는 사람 부탁으로 가입한 보험 손익 분석",
            "theme_code": "whole_life_vs_term",
            "gender": "male",
            "hook_p1_5s": "아는 사람 부탁으로 들었던 보험, 내 증권의 실제 보장 범위를 알고 계신가요?",
            "hook_p2_5s": "불필요한 적립금과 갱신형 특약을 객관적으로 점검해보세요!",
            "hook_0_10s": "아는 사람 부탁으로 들었던 보험, 내 증권의 실제 보장 범위를 알고 계신가요? 불필요한 적립금과 갱신형 특약을 객관적으로 점검해보세요!",
            "app_10_20s": "보험 리밸런스에서 전화번호 없이 내 나이 기준 불필요한 중복 특약을 1초 만에 확인하세요.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "지인 권유 보험, 객관적 약관 팩트 1초 분석!",
            "s2v_motion_prompt": (
                "a sincere, polite, and handsome 33-year-old Korean male professional in crisp white oxford shirt, looking directly into camera with genuine engaging expression, "
                "speaking clearly with smooth natural lip sync, articulate facial articulation, subtle posture shifts"
            ),
            "voice_pitch": "+1Hz",
            "voice_rate": "+4%"
        },
        6: {
            "topic_id": 6,
            "theme_name": "어린이·어른이 100세 만기 리모델링",
            "theme_code": "child_to_adult",
            "gender": "female",
            "hook_p1_5s": "어릴 때 부모님이 들어준 보험, 성인이 된 지금 보장 범위가 충분할까요?",
            "hook_p2_5s": "비갱신형으로 깔끔하게 리모델링할 수 있습니다!",
            "hook_0_10s": "어릴 때 부모님이 들어준 보험, 성인이 된 지금 보장 범위가 충분할까요? 비갱신형으로 깔끔하게 리모델링할 수 있습니다!",
            "app_10_20s": "보험 리밸런스에서 비갱신형 최저가 상품을 전화번호 없이 1초 만에 무료로 비교해보세요.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "성인 질환 보장 공백 점검 & 비갱신형 리모델링!",
            "s2v_motion_prompt": (
                "a bright 32-year-old Korean young mother in cozy ivory sweater, looking directly into camera with relatable friendly demeanor, "
                "speaking naturally with realistic lip sync and dynamic mouth movements, gentle nodding"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        },
        7: {
            "topic_id": 7,
            "theme_name": "내 보험 정밀 비교 & 새는 보험료 다이어트",
            "theme_code": "duplicate_coverage_diet",
            "gender": "female",
            "hook_p1_5s": "매달 나가는 내 보험료, 과연 동일 보장 기준 최적의 조건일까요?",
            "hook_p2_5s": "불필요한 중복 특약부터 스마트하게 다이어트해보세요!",
            "hook_0_10s": "매달 나가는 내 보험료, 과연 동일 보장 기준 최적의 조건일까요? 불필요한 중복 특약부터 스마트하게 다이어트해보세요!",
            "app_10_20s": "보험 리밸런스에서 국내 34개 보험사를 1초 만에 비교하고 불필요한 특약을 싹 다이어트하세요.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "동일 보장 기준 34개사 최저가 정밀 비교!",
            "s2v_motion_prompt": (
                "a sharp and sensible 37-year-old Korean woman in clean stylish smart-casual daily outfit, looking directly into camera with articulate relatable gaze, "
                "speaking clearly with smooth natural lip sync and dynamic mouth movements, subtle head gestures, natural confident posture"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+4%"
        },
        8: {
            "topic_id": 8,
            "theme_name": "AI 보험료 역추정 비교 & 가성비 리모델링",
            "theme_code": "coverage_score_gap_diagnosis",
            "gender": "female",
            "hook_p1_5s": "매달 내는 보험료, 과연 내 연령에 꼭 맞게 알뜰하게 설계되었을까요?",
            "hook_p2_5s": "전화번호 없이 최적의 비교 견적을 확인해보세요!",
            "hook_0_10s": "매달 내는 보험료, 과연 내 연령에 꼭 맞게 알뜰하게 설계되었을까요? 전화번호 없이 최적의 비교 견적을 확인해보세요!",
            "app_10_20s": "보험 리밸런스 AI가 내 보험료를 역추정해서 가장 가성비 높은 최적의 플랜을 1초 만에 찾아줍니다.",
            "cta_18_22s": "지금 네이버에 보험 리밸런스 검색해보세요!",
            "hero_copy": "같은 가격엔 더 큰 보장, 같은 보장엔 더 알뜰한 보험!",
            "s2v_motion_prompt": (
                "a poised 39-year-old Korean woman in clean stylish smart-casual daily outfit, looking directly into camera with genuine reassuring expression, "
                "speaking clearly with smooth natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        }
    }

    def get_full_scenario(self, topic_id: int = 1, gender: Optional[str] = None, use_ai_script: bool = True) -> Dict[str, Any]:
        """주제 ID에 해당하는 22초 실전 아나운서 숏폼 대본 반환 (1~8번 순환, 제미나이 2.5 자율 집필 탑재)"""
        norm_id = ((topic_id - 1) % len(self.SCRIPTS_22S)) + 1
        s = dict(self.SCRIPTS_22S.get(norm_id, self.SCRIPTS_22S[1]))
        effective_gender = gender or s.get("gender", "female")

        hook_p1 = s.get("hook_p1_5s", "")
        hook_p2 = s.get("hook_p2_5s", "")
        hook_full = s.get("hook_0_10s", f"{hook_p1} {hook_p2}")
        app_speech = s.get("app_10_20s", "")
        cta_speech = s.get("cta_18_22s", "")
        hero_copy = s.get("hero_copy", "객관적 5대 보장 AI 분석")
        debate_q = s.get("debate_question", "내 보험 보장 범위는 안전할까?")

        # 🤖 [제미나이 2.5 Flash 실시간 자율 대본 생성 (매번 참신한 아나운서 멘트)]
        if use_ai_script:
            try:
                from brands.insurance.insurance_shorts_script_writer import InsuranceShortsScriptWriter
                ai_script = InsuranceShortsScriptWriter().generate_dynamic_script(topic_id=norm_id)
                if ai_script:
                    hook_p1 = ai_script.get("hook_p1_5s", hook_p1)
                    hook_p2 = ai_script.get("hook_p2_5s", hook_p2)
                    hook_full = ai_script.get("hook_0_10s", hook_full)
                    app_speech = ai_script.get("app_10_20s", app_speech)
                    cta_speech = ai_script.get("cta_18_22s", cta_speech)
                    hero_copy = ai_script.get("hero_copy", hero_copy)
                    debate_q = ai_script.get("debate_question", debate_q)
                    logger.info(f"🎉 [보험 시나리오] 주제 #{norm_id} 제미나이 100% 순수 자율 창작 아나운서 대본 탑재 완료")
            except Exception as e:
                logger.warning(f"⚠️ [보험 시나리오] 제미나이 대본 생성 중 예외 발생, 골든 대본 유지: {e}")

        full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

        visual_dir = {
            "brand_name": "insurance",
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "top_header": f"보험 리밸런스 • {s['theme_name']}",
            "bottom_step1_title": hero_copy,
            "bottom_step1_sub": "특정 보험사 영업 0% • 무료 자가진단",
            "domain_text": "insure-rebalance.vercel.app",
            "search_keyword": "보험 리밸런스"
        }

        return {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "gender": effective_gender,
            "speech_hook": hook_full,
            "speech_hook_part1": hook_p1,
            "speech_hook_part2": hook_p2,
            "speech_app": app_speech,
            "speech_cta": cta_speech,
            "debate_question": debate_q,
            "hero_copy": hero_copy,
            "full_speech": full_speech,
            "visual_direction": visual_dir,
            "s2v_motion_prompt": s["s2v_motion_prompt"],
            "character_desc": s.get("char_desc", ""),
            "background_desc": s.get("bg_desc", ""),
            "voice_pitch": s.get("voice_pitch", "+2Hz"),
            "voice_rate": s.get("voice_rate", "+5%")
        }
