# -*- coding: utf-8 -*-
"""
DebateEngagementBooster - 💬 [알고리즘 조회수 3배 폭발: 댓글창 자동 논쟁 유발 고정 댓글 엔진]
=======================================================================================
• 역할: 3대 브랜드(Aura, 보험 리밸런스, StockMaster AI) 숏폼 영상 생성/업로드 시
        [시청자 찬반 논쟁 유발 고정 댓글(Pinned Comment)]을 자동 합성하여
        시청 지속 시간(AVD 150%~200% 무한 루프)과 댓글 인게이지먼트를 극대화
• 특징:
  1. 제미나이 대본 엔진의 실시간 debate_question을 1순위로 계승
  2. 미입력 시 브랜드별 8대/100대 주제 전용 킬러 찬반 논쟁 템플릿 자동 매칭
  3. 플랫폼별(유튜브 쇼츠 고정댓글, 인스타 릴스, 틱톡, 스레드, 페이스북) 최적화 텍스트 생성
  4. 네이버 공식 검색어(아우라AI데이팅 / 보험 리밸런스 / 스톡마스터 AI)와 직결
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("DebateEngagementBooster")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3대 브랜드 공식 규격 & 기본 논쟁 DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BRAND_SPECS = {
    "aura": {
        "name": "Aura AI 데이팅",
        "official_keyword": "아우라AI데이팅",
        "landing_url": "https://aura-ai-dating.vercel.app/",
        "default_debates": {
            1: "소개팅 자리에서 가짜 업무 전화로 탈출하는 것, 센스다 vs 예의없다?",
            2: "언어 안 통해도 AI 자막 통화로 외국인 연애 가능? 가능하다 vs 무리다",
            3: "소개팅 앱 남녀 성비 50:50 안 맞으면 입장 제한하는 정원제, 찬성 vs 반대?",
            4: "소개팅 프로필 사진 AI 스튜디오 화보 보정, 자기관리다 vs 사진 사기다?",
            5: "연애할 때 연락 빈도 & 데이트 비용 가치관, 얼굴보다 중요하다 vs 얼굴이 먼저다?",
            6: "소개팅 앱 첫마디 AI 추천 멘트 사용하는 것, 스마트하다 vs 진정성 없다?",
            7: "AI가 분석해주는 내 매력상 & 얼굴형 진단, 신뢰한다 vs 재미로만 본다?",
            8: "동네 친구 만날 때 500m 위치 랜덤 안심 보안, 필수다 vs 굳이?"
        }
    },
    "insurance": {
        "name": "보험 리밸런스",
        "official_keyword": "보험 리밸런스",
        "landing_url": "https://insure-rebalance.vercel.app/",
        "default_debates": {
            1: "병원 1년에 한두 번 가는데, 4세대 실비로 갈아탄다 vs 옛날 1·2세대 유지한다?",
            2: "운전자보험은 월 1만 3천 원이면 충분하다 vs 비싸도 상해 특약 다 넣어야 한다?",
            3: "암보험 들 때 유사암(갑상선 등) 진단비 비율, 꼭 따져봐야 한다 vs 일반암만 많으면 된다?",
            4: "뇌출혈만 보장되는 옛날 보험, 뇌혈관질환 전체 보장으로 리밸런싱 해야 한다 vs 그냥 둔다?",
            5: "임플란트/크라운 치료 계획 없으면 치아보험 해지한다 vs 혹시 모르니 유지한다?",
            6: "약 먹고 있어도 335 간편 심사로 갈아타야 한다 vs 거절될까 봐 기존 것 유지한다?",
            7: "부모님 간병비 일당 15만원 간병인 보험, 필수다 vs 나중에 생각한다?",
            8: "보험 가입 전 33개사 무료 비교 자가진단, 필수 코스다 vs 아는 설계사한테 그냥 든다?"
        }
    },
    "stock": {
        "name": "StockMaster AI",
        "official_keyword": "스톡마스터 AI",
        "landing_url": "https://stockmaster-ai.vercel.app/",
        "default_debates": {
            1: "지금 반도체 대장주 매수한다면? 1번 삼성전자 vs 2번 SK하이닉스",
            2: "매달 배당 100만원 포트폴리오, 1번 배당성장 SCHD vs 2번 고배당 JEPQ",
            3: "주식 계좌 -5% 손실 터치 시, AI 원칙 손절한다 vs 반등 믿고 존버한다?",
            4: "당일 체결강도 150% 수급 1위 주도주 매매, 따라붙는다 vs 관망한다?",
            5: "코스피 현 시장 국면, 바닥 반등 랠리다 vs 추가 조정 하락장이다?",
            6: "주식 매매할 때 AI 퀀트 지표로 객관적 판단, 필수다 vs 내 직관과 차트가 낫다?"
        }
    }
}


class DebateEngagementBooster:
    """💬 숏폼 댓글창 찬반 논쟁 유발 고정 댓글 생성기"""

    @classmethod
    def get_debate_question(cls, brand: str, topic_id: int = 1, custom_question: Optional[str] = None) -> str:
        """주제별 찬반 논쟁 질문 텍스트 확보"""
        if custom_question and len(custom_question.strip()) > 5:
            return custom_question.strip()

        brand_key = brand.lower().strip()
        spec = BRAND_SPECS.get(brand_key, BRAND_SPECS["aura"])
        debates = spec.get("default_debates", {})
        norm_id = ((topic_id - 1) % len(debates)) + 1 if debates else 1
        return debates.get(norm_id, "여러분의 생각은 어떠신가요? 찬성 vs 반대?")

    @classmethod
    def generate_all_pinned_comments(
        cls,
        brand: str,
        topic_id: int = 1,
        custom_question: Optional[str] = None
    ) -> Dict[str, str]:
        """
        플랫폼별 찬반 논쟁 유발 1등 고정 댓글 패키지 생성
        - YouTube Shorts, Instagram Reels, TikTok, Threads, Facebook Reels
        """
        brand_key = brand.lower().strip()
        spec = BRAND_SPECS.get(brand_key, BRAND_SPECS["aura"])
        keyword = spec["official_keyword"]
        url = spec["landing_url"]
        question = cls.get_debate_question(brand, topic_id, custom_question)

        # 1. 🔴 YouTube Shorts 고정 댓글 (질문 투표 유도 + 네이버 검색 각인)
        if brand_key == "aura":
            yt_pinned = (
                f"💬 [긴급 찬반 투표] {question}\n"
                f"👉 1번 찬성 (이유는?) vs 2번 반대 (이유는?)\n"
                f"여러분의 솔직한 생각을 댓글로 남겨주세요! 👇\n\n"
                f"✨ 50:50 안심 데이팅은 네이버에 '{keyword}' 검색!"
            )
        elif brand_key == "insurance":
            yt_pinned = (
                f"💬 [보험 팩트 논쟁] {question}\n"
                f"👉 1번 갈아탄다 vs 2번 유지한다\n"
                f"여러분의 선택과 경험을 댓글로 알려주세요! 👇\n\n"
                f"✨ 33개사 실시간 비교는 네이버에 '{keyword}' 검색!"
            )
        else:
            yt_pinned = (
                f"💬 [실시간 투자 토론] {question}\n"
                f"👉 1번 매수/찬성 vs 2번 관망/반대\n"
                f"여러분의 투자 판단을 댓글로 남겨주세요! 👇\n\n"
                f"✨ 10분 계량 전광판은 네이버에 '{keyword}' 검색!"
            )

        # 2. 📸 Instagram Reels 고정 댓글
        reels_comment = (
            f"여러분의 선택은? 💬 {question}\n"
            f"댓글로 1번 vs 2번 남겨주세요! 👇\n"
            f"🔗 프로필 링크(@{brand_key}_official)에서 무료 확인 가능!"
        )

        # 3. 🎵 TikTok 1등 댓글
        tiktok_comment = (
            f"💬 {question}\n"
            f"투표는 댓글로! 👇 (링크는 프로필 Bio 클릭)"
        )

        # 4. 🧵 Threads 첫 댓글
        threads_comment = (
            f"다들 어떻게 생각하시나요? 🤔\n"
            f"{question}\n\n"
            f"솔직한 의견 댓글로 토론해봐요! 👇\n"
            f"👉 바로가기: {url}"
        )

        # 5. 📘 Facebook Reels 첫 댓글
        fb_comment = (
            f"💬 {question}\n"
            f"여러분의 의견을 댓글로 들려주세요! 👇\n"
            f"👉 네이버 검색 [{keyword}] 또는 바로가기: {url}"
        )

        return {
            "debate_question": question,
            "youtube_pinned": yt_pinned,
            "reels_comment": reels_comment,
            "tiktok_comment": tiktok_comment,
            "threads_comment": threads_comment,
            "facebook_comment": fb_comment,
            "official_keyword": keyword,
            "landing_url": url
        }
