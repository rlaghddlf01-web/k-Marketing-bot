import os
import sys
import time
from pathlib import Path

# UTF-8 출력 보장 (Windows 콘솔 이모지 지원)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.easytax_bot import EasyTaxRefundBot

def main():
    import argparse
    parser = argparse.ArgumentParser(description="EasyTax Bot Executor")
    parser.add_argument("--loop", action="store_true", help="10분 간격 무한 반복 모드 (기본: 1회 실행 후 즉시 종료)")
    args = parser.parse_args()

    print("\n========================================================")
    print("💰 [EasyTax] 국세청 외국인 세금 환급 100% 전담 봇")
    print("========================================================")
    print("• 모드: 100% EasyTax 전력 질주 모드 (Anti-Ban 세무 가드레일)")
    print("• 콘텐츠: E-9 90% 감면 숏폼 + 5개년 환급 카드뉴스 + 세무 레딧 답변")
    print(f"• 실행: {'10분 간격 연속 실행 모드' if args.loop else '1회 정밀 실행 후 즉시 완료 모드'}\n")

    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = EasyTaxRefundBot(db_mgr, supabase_mgr)

    if not args.loop:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 💰 EasyTax 1회 정밀 사이클 가동...")
        res = bot.run_easytax_cycle()
        print(f"\n🎉 [성공 완료] 숏폼 {res['shorts_count']}건 / 카드뉴스 {res['cardnews_count']}장 / 레딧 {res['reddit_count']}건")
        print("✅ 모든 작업이 완료되어 봇이 정상 종료되었습니다.")
        return

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 💰 EasyTax 사이클 #{cycle} 실행 중...")
            res = bot.run_easytax_cycle()
            print(f"✅ 사이클 #{cycle} 완료: 숏폼 {res['shorts_count']}건 / 카드뉴스 {res['cardnews_count']}장 / 레딧 {res['reddit_count']}건")
            print("⏳ 다음 사이클까지 10분간 대기합니다... (Ctrl+C 누르면 종료)")
            time.sleep(600)
    except KeyboardInterrupt:
        print("\n⏹️ EasyTax 봇이 안전하게 종료되었습니다.")

if __name__ == "__main__":
    main()
