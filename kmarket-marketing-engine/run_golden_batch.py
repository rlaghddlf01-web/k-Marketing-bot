# -*- coding: utf-8 -*-
"""
[독립형 골든배치 실행기] run_golden_batch.py
• 역할: 브랜드별(EasyTax / K-Market) 8대 황금 타깃 국가 대량 생산 독립 실행
• 지원 모드:
  1. --mode daemon: 24시간 무인 루프 (매일 오전 11:30 & 저녁 18:30 정시 자동 생산)
  2. --mode once  : 지금 즉시 8대 국가 숏폼(8) + 카드뉴스(8) 1회 일괄 생산 후 종료
• 100% 브랜드 격리: EasyTax와 K-Market이 서로 간섭 없이 독립 프로세스로 구동
"""

import os
import sys
import time
import datetime
import argparse
from pathlib import Path

# Windows UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import GOLDEN_EIGHT_LANGUAGES, GOLDEN_EIGHT_DETAILS
from core.golden_batch_producer import GoldenBatchProducer

def run_once(producer: GoldenBatchProducer, brand: str, slot_name: str = "manual"):
    brand_title = "💰 EasyTax (KTRS 외국인 세무환급)" if brand == "easytax" else "🛒 K-Market (외국인 커머스/라이프)"
    print("\n" + "=" * 62)
    print(f"🌟 [{brand.upper()}] 8대 황금 타깃 국가 1회 즉시 생산 가동")
    print(f"• 브랜드: {brand_title}")
    print(f"• 대상국: 8개국 (베트남, 우즈벡, 캄보디아, 네팔, 태국, 인도네시아, 몽골, 미얀마)")
    print(f"• 생산목록: 8개국 숏폼 8편 + 8개국 5장 카드뉴스 8세트 (총 16건)")
    print("=" * 62 + "\n")
    
    res = producer.execute_slot(slot_name=slot_name, brand=brand)
    print("\n" + "=" * 62)
    print(f"🎉 [{brand.upper()}] 생산 완료 요약")
    print(f"• 총 생산 콘텐츠: {res.get('total_items', 0)}건 (소요 시간: {res.get('elapsed_seconds', 0)}초)")
    print(f"• 숏폼: {res.get('shorts_success', 0)}/{res.get('shorts_total', 8)}편 성공")
    print(f"• 카드뉴스: {res.get('cardnews_success', 0)}/{res.get('cardnews_total', 8)}세트 성공")
    print(f"• 저장 폴더:")
    if brand == "easytax":
        print(r"  - 숏폼: C:\Users\zkfnt\Desktop\숏폼_산출물\이지텍스")
        print(r"  - 카드뉴스: C:\Users\zkfnt\Desktop\카드뉴스_산출물\이지텍스")
    else:
        print(r"  - 숏폼: C:\Users\zkfnt\Desktop\숏폼_산출물\케이마켓")
        print(r"  - 카드뉴스: C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓")
    print("=" * 62 + "\n")

def run_daemon(producer: GoldenBatchProducer, brand: str):
    brand_title = "💰 EasyTax (KTRS 세무)" if brand == "easytax" else "🛒 K-Market (커머스)"
    print("\n" + "=" * 64)
    print(f"🔄 [{brand.upper()}] 8대 황금 타깃 국가 24시간 무인 오토파일럿 데몬 가동")
    print(f"• 브랜드: {brand_title}")
    print(f"• 골든 슬롯: 매일 오전 11:30 & 저녁 18:30 (하루 2회 자동 생산)")
    print(f"• 1회 생산량: 8개국 숏폼 8편 + 8개국 카드뉴스 8세트")
    print(f"• 하루 총합: 숏폼 16편 + 카드뉴스 16세트 (바탕화면 자동 정리)")
    print("• 모니터링: 60초 주기로 현재 시각 감시 중... (Ctrl+C 누르면 정지)")
    print("=" * 64 + "\n")

    executed_slots = set()

    while True:
        try:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            hour = now.hour
            minute = now.minute

            is_morning_slot = (hour == 11 and minute >= 30) or (hour == 12 and minute < 30)
            is_evening_slot = (hour == 18 and minute >= 30) or (hour == 19 and minute < 30)

            slot_to_run = None
            if is_morning_slot and f"{today_str}_morning" not in executed_slots:
                slot_to_run = "morning"
            elif is_evening_slot and f"{today_str}_evening" not in executed_slots:
                slot_to_run = "evening"

            if slot_to_run:
                slot_name_kr = "오전 11:30 피크" if slot_to_run == "morning" else "저녁 18:30 피크"
                print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⏰ [{brand.upper()}] {slot_name_kr} 정시 도달! 8개국 대량 생산 시작...")
                res = producer.execute_slot(slot_name=slot_to_run, brand=brand)
                executed_slots.add(f"{today_str}_{slot_to_run}")
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ [{brand.upper()}] {slot_name_kr} 생산 완료! (총 {res.get('total_items',0)}건 생성)")
                print(f"⏳ 다음 슬롯 대기 중...\n")

            time.sleep(30)
        except KeyboardInterrupt:
            print(f"\n⏹️ [{brand.upper()}] 오토파일럿 데몬이 사용자에 의해 안전하게 정지되었습니다.")
            break
        except Exception as e:
            print(f"\n⚠️ 데몬 루프 예외 발생 ({e}), 30초 후 재시도...")
            time.sleep(30)

def main():
    parser = argparse.ArgumentParser(description="Brand-Specific 8 Golden Countries Batch Runner")
    parser.add_argument("--brand", type=str, choices=["easytax", "kmarket", "all"], default="easytax", help="대상 브랜드")
    parser.add_argument("--mode", type=str, choices=["daemon", "once"], default="daemon", help="실행 모드 (daemon: 24시간 감시, once: 1회 즉시 실행)")
    parser.add_argument("--slot", type=str, default="manual", help="슬롯 이름 (once 모드 시)")
    args = parser.parse_args()

    producer = GoldenBatchProducer()

    if args.mode == "once":
        run_once(producer, brand=args.brand, slot_name=args.slot)
    else:
        run_daemon(producer, brand=args.brand)

if __name__ == "__main__":
    main()
