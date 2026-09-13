# -*- coding: utf-8 -*-
"""
run_kmarket_factory.py - 🛒 [케이마켓 전용 마케팅 콘텐츠 원클릭 생산 팩토리]
- 모드 1: --mode cardnews (치아 보이는 활짝 웃는 환희 컷 + 케이마켓 송금/나눔 UI 정밀 매립)
- 모드 2: --mode shorts (입 다문 단정한 컷 + 5초 립싱크 Wan 2.2 S2V 동영상)
- 옵션: --lang (언어, 기본 vi)
"""

import sys
import argparse
from pathlib import Path

# UTF-8 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brands.kmarket.kmarket_cardnews_pipeline import KMarketCardNewsPipeline
from brands.kmarket.kmarket_shorts_pipeline import KMarketShortsPipeline


def main():
    parser = argparse.ArgumentParser(description="케이마켓 자동화 마케팅 콘텐츠 팩토리")
    parser.add_argument("--mode", choices=["cardnews", "shorts", "all"], default="cardnews", help="생성할 콘텐츠 유형")
    parser.add_argument("--lang", type=str, default="vi", help="타깃 국가 코드 (vi, uz, ko)")
    args = parser.parse_args()

    print(f"\n============================================================")
    print(f"🛒 [K-Market 팩토리 가동] 모드: {args.mode} | 언어: {args.lang}")
    print(f"============================================================")

    if args.mode in ["cardnews", "all"]:
        print("\n📸 [1/2] 케이마켓 1080x1350 스마트 에메랄드 카드뉴스 제작 시작...")
        card_pipe = KMarketCardNewsPipeline()
        card_path = card_pipe.produce(
            nationality_code=args.lang,
            output_filename=f"kmarket_cardnews_{args.lang}.png"
        )
        print(f"✅ 카드뉴스 생성 완료! -> {card_path}")

    if args.mode in ["shorts", "all"]:
        print("\n🎬 [2/2] 케이마켓 5초 립싱크 숏폼 비디오 제작 시작...")
        shorts_pipe = KMarketShortsPipeline()
        video_path = shorts_pipe.produce(
            nationality_code=args.lang,
            output_filename=f"kmarket_shorts_{args.lang}.mp4"
        )
        print(f"✅ 숏폼 동영상 생성 완료! -> {video_path}")

    print(f"\n🎉 모든 케이마켓 콘텐츠 생산 공정이 성공적으로 완료되었습니다!")


if __name__ == "__main__":
    main()
