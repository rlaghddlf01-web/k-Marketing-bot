# -*- coding: utf-8 -*-
"""
Test 3 Brands SNS Guide Masters & 4-Tier Hashtag Matrices
"""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
from brands.aura.aura_sns_guide_master import AuraSNSGuideMaster

from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix
from brands.insurance.insurance_sns_guide_master import InsuranceSNSGuideMaster

from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
from brands.stock.stock_sns_guide_master import StockSNSGuideMaster


def main():
    print("=" * 80)
    print("🚀 [한국 마케팅봇 3대 브랜드] 4단 티어 해시태그 & SNS 포스팅 가이드 마스터 전수 검증")
    print("=" * 80)

    # 1. 💖 Aura 데이팅
    print("\n[1] 💖 Aura AI 데이팅 검증")
    aura_matrix = AuraHashtagMatrix()
    aura_insta_tags = aura_matrix.get_instagram_hashtags(topic_id=1, count=18)
    print(f"✅ Aura 인스타 해시태그 ({len(aura_insta_tags)}개): {' '.join(aura_insta_tags[:6])} ...")
    assert "#아우라AI데이팅" in aura_insta_tags, "Aura official keyword missing"

    aura_card_guide = AuraSNSGuideMaster.build_cardnews_guide(
        topic_id=1,
        theme_name="소개팅 긴급 탈출 전화",
        theme_code="escape_call",
        copy_data={
            "slide1": {"headline_line1": "사진과 실물 불일치에 당황했다면?", "headline_line2": "이 어색함, 언제까지 참아야 해?", "subtitle": "Aura의 긴급 탈출 전화로 매너 있게 1차 탈출!", "bullets": ["1차 정중 귀가", "합법 탈출"]},
            "slide2": {"headline_line1": "어색한 소개팅 억지 버티기?", "subtitle": "시간 낭비 제로", "bullets": []},
            "slide3": {"headline_line1": "30분 뒤 팀장님 긴급 전화", "subtitle": "자연스러운 명분", "bullets": []},
            "slide4": {"headline_line1": "실제 통화 대본 화면 표출", "subtitle": "보고 읽으면 끝", "bullets": []},
            "slide5": {"debate_question": "노잼 소개팅 긴급 탈출, 센스다 vs 비매너다?", "debate_opt1_title": "센스다", "debate_opt2_title": "비매너다"},
            "sns_caption": "소개팅 나갔는데 분위기 싸할 때 1초 만에 탈출하는 꿀팁 대방출! ✨"
        }
    )
    assert "[1] 📸 인스타그램" in aura_card_guide
    assert "[2] 🧵 스레드" in aura_card_guide
    assert "[3] 📘 페이스북" in aura_card_guide
    assert "[4] 📰 네이버 포스트" in aura_card_guide
    assert "[5] 📗 네이버 블로그" in aura_card_guide
    assert "[6] ☕ 네이버 카페" in aura_card_guide
    assert "Zero-URL" in aura_card_guide
    print(f"🎉 Aura 카드뉴스 7대 채널 가이드 생성 성공 ({len(aura_card_guide)}자)")

    # 2. 🛡️ 보험 리밸런스
    print("\n[2] 🛡️ 보험 리밸런스 검증")
    ins_matrix = InsuranceHashtagMatrix()
    ins_insta_tags = ins_matrix.get_instagram_hashtags(topic_id=1, count=18)
    print(f"✅ 보험 인스타 해시태그 ({len(ins_insta_tags)}개): {' '.join(ins_insta_tags[:6])} ...")
    assert "#보험리밸런스" in ins_insta_tags, "Insurance official keyword missing"

    ins_card_guide = InsuranceSNSGuideMaster.build_cardnews_guide(
        topic_id=1,
        theme_name="실손의료비 4세대 전환 손익",
        theme_code="silbi_gen4",
        copy_data={
            "slide1": {"headline_line1": "병원도 안 가는데 옛날 실비 8만원?", "headline_line2": "4세대로 월 1만원대 다이어트!", "subtitle": "34개 보험사 실시간 손익 계산", "bullets": ["고정지출 80% 절감", "중복특약 삭제"]},
            "slide2": {"headline_line1": "병원 자주 안 가면 옛날 실비 손해?", "subtitle": "보험료 낭비 방지", "bullets": []},
            "slide3": {"headline_line1": "4세대 실손의료비 핵심 장점", "subtitle": "착한 실손 전환", "bullets": []},
            "slide4": {"headline_line1": "0.1초 실시간 34개사 비교표", "subtitle": "익명 자가진단", "bullets": []},
            "slide5": {"debate_question": "실비보험 전환, 지금 하는 게 이득일까?", "debate_opt1_title": "당장 전환", "debate_opt2_title": "일단 유지"},
            "sns_caption": "병원 안 가는데 매달 나가는 실비보험료 아까우셨죠? 4세대 전환 손익 1초 비교! 💡"
        }
    )
    assert "[1] 📸 인스타그램" in ins_card_guide
    assert "[2] 🧵 스레드" in ins_card_guide
    assert "[3] 📘 페이스북" in ins_card_guide
    assert "[4] 📰 네이버 포스트" in ins_card_guide
    assert "[5] 📗 네이버 블로그" in ins_card_guide
    assert "[6] ☕ 네이버 카페" in ins_card_guide
    assert "보험 리밸런스" in ins_card_guide
    print(f"🎉 보험 리밸런스 7대 채널 가이드 생성 성공 ({len(ins_card_guide)}자)")

    # 3. 📈 StockMaster AI
    print("\n[3] 📈 StockMaster AI 검증")
    stock_matrix = StockHashtagMatrix()
    stock_insta_tags = stock_matrix.get_instagram_hashtags(topic_id=1, count=18)
    print(f"✅ 주식 인스타 해시태그 ({len(stock_insta_tags)}개): {' '.join(stock_insta_tags[:6])} ...")
    assert "#스톡마스터AI" in stock_insta_tags, "Stock official keyword missing"

    stock_card_guide = StockSNSGuideMaster.build_cardnews_guide(
        topic_id=1,
        theme_name="삼성전자 vs SK하이닉스 HBM 수급 대결",
        theme_code="samsung_vs_hynix_hbm",
        copy_data={
            "slide1": {"headline_line1": "삼성전자 vs SK하이닉스 지금 뭘 살까?", "headline_line2": "외국인 수급과 퀀트 적정주가로 본 승자는?", "subtitle": "실시간 퀀트 데이터 팩트체크", "bullets": ["외인 순매수 추이", "HBM 공급망 분석"]},
            "slide2": {"headline_line1": "깜깜이 뇌동매매는 이제 그만!", "subtitle": "객관적 수급 지표", "bullets": []},
            "slide3": {"headline_line1": "외국인/기관 쌍끌이 레이더", "subtitle": "실시간 수급 포착", "bullets": []},
            "slide4": {"headline_line1": "AI 퀀트 적정 밸류에이션", "subtitle": "적정 목표주가 산출", "bullets": []},
            "slide5": {"debate_question": "삼성전자 vs SK하이닉스, 당신의 선택은?", "debate_opt1_title": "삼성전자 반등", "debate_opt2_title": "하이닉스 독주"},
            "sns_caption": "반도체 대장주 투자 고민 끝! 실시간 외국인 수급과 퀀트 적정주가로 확인하세요 🚀"
        }
    )
    assert "[1] 📸 인스타그램" in stock_card_guide
    assert "[2] 🧵 스레드" in stock_card_guide
    assert "[3] 📘 페이스북" in stock_card_guide
    assert "[4] 📰 네이버 포스트" in stock_card_guide
    assert "[5] 📗 네이버 블로그" in stock_card_guide
    assert "[6] ☕ 네이버 카페" in stock_card_guide
    assert "스톡마스터 AI" in stock_card_guide
    print(f"🎉 StockMaster AI 7대 채널 가이드 생성 성공 ({len(stock_card_guide)}자)")

    print("\n" + "=" * 80)
    print("🏆 [3개 브랜드 전수 검증 100% 통과!] 4단 해시태그 & 7대 채널 SNS 가이드 완벽 작동!")
    print("=" * 80)


if __name__ == "__main__":
    main()
