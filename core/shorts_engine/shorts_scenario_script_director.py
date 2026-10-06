# -*- coding: utf-8 -*-
"""
ShortsScenarioScriptDirector - [이지텍스 22초 3단계 다국어 대본 및 비주얼 오버레이 디렉터]
- 시나리오 디렉터 60대 테마 및 7대 페르소나 연계
- 1명의 주인공이 이끄는 22초 3단계 단일 스토리라인 생성:
  1) [0초 ~ 10초] 인물 립싱크 킬러 훅 (모국어 1분 조회 + 310만원 입금 체감)
  2) [10초 ~ 18초] 라이브 앱 조작 안내 (12개월 슬라이더 + 월급 250만 원 + 310만원 계산 연출)
  3) [18초 ~ 22초] 100% 후불제 안심 보증 및 행동 촉구 CTA
- 100% 제미나이 AI 실시간 자율 창작 (하드코딩 사전 SCRIPTS_22S 전면 배제)
"""

import os
import random
import logging
from typing import Dict, Any, Optional

from core.gemini_shorts_copywriter import GeminiShortsCopywriter
from config import LANGUAGES

logger = logging.getLogger("ShortsScenarioScriptDirector")


class ShortsScenarioScriptDirector:
    """이지텍스 22초 완결형 숏폼 제미나이 100% 실시간 대본 및 화면 오버레이 디렉터 엔진"""

    def __init__(self):
        self.copywriter = GeminiShortsCopywriter(service_id="easytax")
        logger.info("🎬 [ShortsScenarioScriptDirector] 제미나이 실시간 숏폼 카피라이터 엔진 초기화 완료")

    def get_full_scenario(
        self,
        lang: Optional[str] = None,
        amount: Optional[int] = None,
        theme_id: Optional[str] = None,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        제미나이 AI와 60대 시나리오 테마를 연동하여 실시간으로 22초 대본과 박스 자막, 배지, CTA 생성
        (하드코딩 사전 0%, 100% 실시간 제미나이 자율 직작문)
        """
        effective_lang = lang or "vi"

        # 1. 시나리오 테마 추출
        chosen_theme = None
        try:
            from core.scenario_director_shorts_easytax import EASYTAX_60_THEMES
            if theme_id:
                chosen_theme = next((t for t in EASYTAX_60_THEMES if t.get("id") == theme_id), None)
            if not chosen_theme:
                chosen_theme = random.choice(EASYTAX_60_THEMES)
        except Exception as e:
            logger.warning(f"테마 매트릭스 로드 예외: {e}")
            chosen_theme = {
                "name": "한국 세금 90% 소득세 감면 및 환급",
                "target": "외국인 근로자",
                "persona_type": "E-9/E-7 근로자",
                "refund_est": 3100000
            }

        # 🎯 [금액 100% 원천 동기화] 지정된 amount 우선 적용, 없으면 테마 고유 refund_est (최종 기본값 3,100,000)
        effective_amount = amount if amount is not None else chosen_theme.get("refund_est", 3100000)
        amount_fmt = f"{effective_amount:,} KRW"

        # 🎯 [성별 50:50 완벽 랜덤 균등 분배]
        if gender in ("male", "female"):
            effective_gender = gender
        else:
            effective_gender = random.choice(["male", "female"])

        # 2. 구글 제미나이 실시간 22초 3단계 대본, 자막 및 배지 직작문 호출
        script_data = self.copywriter.generate_shorts_script(
            service_id="easytax",
            lang=effective_lang,
            scenario=chosen_theme,
            refund_formatted=amount_fmt
        )

        country_name = LANGUAGES.get(effective_lang, {}).get("name", effective_lang.upper())
        speech_hook = script_data.get("hook_0_10s", "")
        speech_app = script_data.get("app_10_18s", "")
        speech_cta = script_data.get("cta_18_22s", "")
        full_speech = f"{speech_hook} {speech_app} {speech_cta}".strip()

        # 1씬 5초+5초 립싱크 듀얼 클립 분할: 5초(81프레임) 꽉 차게 단어 수 기준 50:50 정밀 균등 분할
        words = speech_hook.split()
        if len(words) >= 4:
            mid = len(words) // 2
            speech_hook_p1 = " ".join(words[:mid]).strip()
            speech_hook_p2 = " ".join(words[mid:]).strip()
        else:
            speech_hook_p1 = speech_hook
            speech_hook_p2 = speech_hook

        return {
            "country_name": country_name,
            "lang": effective_lang,
            "gender": effective_gender,
            "amount": effective_amount,
            "amount_formatted": amount_fmt,
            "speech_hook": speech_hook,
            "speech_hook_part1": speech_hook_p1,
            "speech_hook_part2": speech_hook_p2,
            "speech_app": speech_app,
            "speech_cta": speech_cta,
            "full_speech": full_speech,
            "visual_direction": {
                "top_header": script_data.get("top_header", "90% INCOME TAX REFUND • KTRS"),
                "domain_text": "ktrs-service.vercel.app" if effective_lang != "kmarket" else "ktrs-market.vercel.app",
                "cta_button_text": script_data.get("cta_button_text", "CHECK FOR FREE >"),
                "dynamic_scenes": script_data.get("dynamic_scenes", [])
            }
        }
