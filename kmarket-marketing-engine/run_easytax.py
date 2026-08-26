import os
import sys
import time
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.easytax_bot import EasyTaxRefundBot

def main():
    print("\n========================================================")
    print("💰 [EasyTax] 국세청 외국인 세금 환급 100% 전담 봇")
    print("========================================================")
    print("• 모드: 100% EasyTax 전력 질주 모드 (Anti-Ban 세무 가드레일)")
    print("• 콘텐츠: E-9 90% 감면 숏폼 + 5개년 환급 카드뉴스 + 세무 레딧 답변")
    print("• 주기: 10분 간격 정밀 순회\n")

    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = EasyTaxRefundBot(db_mgr, supabase_mgr)

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
