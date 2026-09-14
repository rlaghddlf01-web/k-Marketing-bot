# -*- coding: utf-8 -*-
"""
run_easytax_factory.py - 💰 [이지택스 전용 마케팅 콘텐츠 원클릭 생산 팩토리]
- 모드 1: --mode cardnews (치아 보이는 활짝 웃는 환희 컷 + 국세청 환급 영수증 정밀 매립)
- 모드 2: --mode shorts (입 다문 단정한 컷 + 5초 립싱크 Wan 2.2 S2V 동영상)
- 옵션: --amount (환급금액, 기본 3100000), --lang (언어, 기본 vi)
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

from core.engine.cardnews_batch_producer import CardNewsBatchProducer
from core.engine.comfy_process_manager import ComfyProcessManager
from brands.easytax.easytax_shorts_pipeline import EasyTaxShortsPipeline


def main():
    parser = argparse.ArgumentParser(description="이지택스 자동화 마케팅 콘텐츠 팩토리")
    parser.add_argument("--mode", choices=["cardnews", "shorts", "all"], default="cardnews", help="생성할 콘텐츠 유형")
    parser.add_argument("--amount", type=int, default=3100000, help="환급 금액 (기본: 3100000)")
    parser.add_argument("--lang", type=str, default="vi", help="타깃 국가 코드 (vi, uz, mn, km, ne, th, id, my)")
    args = parser.parse_args()

    print(f"\n============================================================")
    print(f"💰 [EasyTax 팩토리 가동] 모드: {args.mode} | 금액: ₩{args.amount:,} | 언어: {args.lang}")
    print(f"============================================================")

    # 1. ComfyUI GPU 엔진 상태 점검 및 자동 기동
    print("\n⚡ [1/3] ComfyUI Wan2.1 GPU 가속 엔진 상태 점검...")
    ComfyProcessManager.ensure_running(wait_timeout=90)

    if args.mode in ["cardnews", "all"]:
        print(f"\n📸 [2/3] 이지텍스 5장 1080x1350 풀블리드 카드뉴스 세트 생산 시작 (언어: {args.lang.upper()})...")
        producer = CardNewsBatchProducer()
        result = producer.produce_full_set(
            lang=args.lang,
            amount=args.amount
        )
        print(f"✅ 카드뉴스 5장 완제품 생산 완료!")
        print(f"📂 저장 폴더: {result.get('folder_path')}")
        print(f"📄 SNS 가이드: {result.get('guide_path')}")

    if args.mode in ["shorts", "all"]:
        print("\n🎬 [2/2] 이지택스 5초 립싱크 숏폼 비디오 제작 시작...")
        shorts_pipe = EasyTaxShortsPipeline()
        video_path = shorts_pipe.produce(
            nationality_code=args.lang,
            amount=args.amount,
            output_filename=f"easytax_shorts_{args.lang}_{args.amount}.mp4"
        )
        print(f"✅ 숏폼 동영상 생성 완료! -> {video_path}")

    print(f"\n🎉 모든 이지택스 콘텐츠 생산 공정이 성공적으로 완료되었습니다!")


if __name__ == "__main__":
    main()
