# -*- coding: utf-8 -*-
"""
StockShortsScenarioDirector - 🎬 [StockMaster AI 국내 주식 5대 실시간 숏폼 마스터 시나리오 디렉터]
===================================================================================================
- 국내 주식 100% 독립 전담 (KOSPI/KOSDAQ 350개 우량주 실시간 퀀트)
- 5대 실시간 마스터 라인업:
  1) [주제 1] 삼성전자 실시간 4대 모달 퀀트 수급 (30초)
  2) [주제 2] SK하이닉스 실시간 4대 모달 퀀트 수급 (30초)
  3) [주제 3] 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드 (30초)
  4) [주제 4] 당일 10분 계량 전광판 실시간 1위 주도주 발굴 (30초)
  5) [주제 5] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트 (30초)
- 공식 검색어 불변: ['스톡마스터 AI'] (띄어쓰기 100% 준수)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("StockShortsScenarioDirector")


class StockShortsScenarioDirector:
    """📈 StockMaster AI 국내 주식 5대 실시간 30초 숏폼 시나리오 디렉터"""

    SCRIPTS_30S = {
        1: {
            "topic_id": 1,
            "theme_name": "삼성전자 실시간 4대 모달 퀀트 수급",
            "theme_code": "samsung_quant_modal",
            "stock_target": "삼성전자",
            "hero_copy": "삼성전자 4대 퀀트 지표 실시간 1초 분석!",
            "debate_question": "삼성전자 지금 구간, 추격 매수 vs 조정 대기?",
            "visual_direction": "전광판 ➔ 삼성전자 검색 ➔ 4대 탭(수급/기술/리스크/기본정보) 스크롤 다운"
        },
        2: {
            "topic_id": 2,
            "theme_name": "SK하이닉스 실시간 4대 모달 퀀트 수급",
            "theme_code": "hynix_quant_modal",
            "stock_target": "SK하이닉스",
            "hero_copy": "SK하이닉스 HBM 퀀트 수급 실시간 1초 분석!",
            "debate_question": "SK하이닉스 HBM 독주 지속 vs 고점 차익 실현?",
            "visual_direction": "전광판 ➔ SK하이닉스 검색 ➔ 4대 탭(수급/기술/리스크/기본정보) 스크롤 다운"
        },
        3: {
            "topic_id": 3,
            "theme_name": "뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드",
            "theme_code": "anti_fomo_risk_guard",
            "stock_target": "리스크센터",
            "hero_copy": "감정 배제! AI 기계적 손절가 & 리스크 가드",
            "debate_question": "급등주 추격 매수 vs AI 리스크 안전 구간 매매?",
            "visual_direction": "전광판 ➔ AI 리스크 센터 ➔ VETO 배제 종목 및 안전 구간 스크롤"
        },
        4: {
            "topic_id": 4,
            "theme_name": "당일 10분 계량 전광판 실시간 1위 주도주 발굴",
            "theme_code": "top1_leader_radar",
            "stock_target": "전광판1위",
            "hero_copy": "10분마다 갱신되는 당일 실시간 1위 주도주!",
            "debate_question": "오늘 10분 전광판 1위 주도주, 내일까지 이어질까?",
            "visual_direction": "전광판 상단 ➔ 당일 1위 종목 클릭 ➔ 실시간 퀀트 모달 스크롤"
        },
        5: {
            "topic_id": 5,
            "theme_name": "KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트",
            "theme_code": "macro_stress_report",
            "stock_target": "매크로스트레스",
            "hero_copy": "시장 종합 스트레스 지수 & 4대 계량 매크로 리포트",
            "debate_question": "코스피 현 구간, 반등 랠리 vs 하방 압력?",
            "visual_direction": "메인 상단 글로벌 매크로 ➔ 시장 종합 스트레스 10점 국면 ➔ 4대 지표 스크롤"
        },
        6: {
            "topic_id": 6,
            "theme_name": "국내 최초 자기학습 AI 퀀트 비서! Stock Master AI 총괄 소개",
            "theme_code": "stockmaster_official_overview",
            "stock_target": "전광판1위",
            "hero_copy": "10분 퀀트 스캔 • 30분 Gemini AI • 실시간 손절 알림!",
            "debate_question": "감정 매매 vs 24시간 자기학습 AI 퀀트 비서?",
            "visual_direction": "시장 스트레스 ➔ 10분 계량 전광판 ➔ 1등주 4대 모달 ➔ 실시간 손절 기능"
        }
    }

    def get_full_scenario(self, topic_id: int = 1, gender: Optional[str] = None) -> Dict[str, Any]:
        """주제 ID에 해당하는 국내 5대 실시간 시나리오 메타데이터 반환 (1~5번 순환)"""
        norm_id = ((topic_id - 1) % len(self.SCRIPTS_30S)) + 1
        s = dict(self.SCRIPTS_30S.get(norm_id, self.SCRIPTS_30S[1]))

        visual_dir = {
            "brand_name": "stock",
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "top_header": f"스톡마스터 AI • {s['theme_name']}",
            "bottom_step1_title": s["hero_copy"],
            "bottom_step1_sub": "10분 계량 전광판 • 실시간 퀀트 분석",
            "domain_text": "stockmaster-ai.vercel.app",
            "search_keyword": "스톡마스터 AI"
        }

        return {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "stock_target": s["stock_target"],
            "hero_copy": s["hero_copy"],
            "debate_question": s["debate_question"],
            "visual_direction": visual_dir,
            "search_keyword": "스톡마스터 AI"
        }
