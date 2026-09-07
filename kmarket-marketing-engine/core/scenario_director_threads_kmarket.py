# -*- coding: utf-8 -*-
"""
ScenarioDirectorThreadsKMarket - 🛒 K-Market 17개국어 Threads 구어체 타래 바이럴 전담 시나리오 디렉터
- 3대 시간대(아침 11:00, 오후 16:30, 저녁 21:30)별 바이럴 스토리텔링 소스 제공
- 17개 언어권 재한 외국인의 실생활 밀착 주제 완비
"""

import random
from typing import Dict, Any, List

THREADS_KMARKET_THEMES: List[Dict[str, Any]] = [
    {
        "name": "원룸 이사 0원 풀세팅 나눔",
        "title": "신촌/안암 대학가 원룸 자취방 가구 0원 나눔 득템 비결",
        "item": "침대, 책상, 전자레인지, 미니 냉장고 0원 나눔",
        "target": "재한 외국인 유학생 및 사회초년생",
        "hook": "한국 원룸 이사할 때 가구 사지 마세요! 0원에 방 풀세팅한 썰",
        "tag": "giveaway_moving"
    },
    {
        "name": "한국 대형폐기물 스티커비 절약",
        "title": "대형폐기물 스티커비 10만원 아끼고 무료 나눔으로 처리하는 법",
        "item": "가구/가전 무료 수거 및 나눔",
        "target": "원룸 퇴거 및 본국 귀국 유학생/근로자",
        "hook": "버릴 때 돈 드는 침대/서랍장, 0원에 이웃에게 넘기고 칭찬받은 사연",
        "tag": "waste_sticker_saving"
    },
    {
        "name": "외국인 알뜰폰 무제한 요금제 개통",
        "title": "외국인등록증으로 월 1만원대 무제한 알뜰폰 셀프 개통 꿀팁",
        "item": "1만원대 데이터 무제한 USIM",
        "target": "입국 초기 외국인 유학생/노동자",
        "hook": "통신사 매장 가서 호갱 되지 않고 알뜰폰 유심 1만원대에 무제한 뚫은 썰",
        "tag": "sim_savings"
    },
    {
        "name": "종량제 봉투 & 분리수거 과태료 방어",
        "title": "쓰레기 종량제 봉투 잘못 버려 10만원 벌금 물 뻔한 위기 탈출법",
        "item": "한국 생활 분리수거 필수 가이드",
        "target": "한국 거주 1년 차 외국인",
        "hook": "한국 쓰레기 분리배출 몰라서 10만원 과태료 통지서 받을 뻔한 실화",
        "tag": "trash_rule_tips"
    },
    {
        "name": "중고 직거래 언어 장벽 제로",
        "title": "17개국어 자동번역 채팅으로 한국어 한마디 못해도 중고 직거래 성공",
        "item": "17개국 실시간 자동번역 직거래 마켓",
        "target": "한국어가 서툰 외국인 및 교환학생",
        "hook": "한국어 1도 못하는데 신촌 직거래에서 아이패드 꿀매 득템한 비결",
        "tag": "auto_translate_trade"
    },
    {
        "name": "중고 사기 방지 및 안전 직거래",
        "title": "외국인 대상 선입금 택배 사기 100% 피하고 캠퍼스 안전 직거래하기",
        "item": "캠퍼스/역세권 공인 대면 직거래",
        "target": "재한 외국인 커뮤니티 전원",
        "hook": "외국인이라고 무시하고 선입금 사기 치려던 판매자 참교육한 썰",
        "tag": "anti_scam_safety"
    }
]

class ScenarioDirectorThreadsKMarket:
    """K-Market Threads 전담 시나리오 디렉터"""
    def __init__(self):
        self.themes = THREADS_KMARKET_THEMES

    def get_thread_scenario(self) -> Dict[str, Any]:
        return random.choice(self.themes)
