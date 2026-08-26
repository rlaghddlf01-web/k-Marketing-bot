import os
import sys
import time
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.kmarket_bot import KMarketGrowthBot

def main():
    print("\n========================================================")
    print("🛒 [K-Market] 외국인 로컬 라이프 & 0원 나눔 100% 전담 봇")
    print("========================================================")
    print("• 모드: 100% K-Market 전력 질주 모드")
    print("• 콘텐츠: 270개 실물 매물 숏폼 + 0원 나눔 카드뉴스 + 레딧 가구 답변")
    print("• 주기: 5분 간격 자동 순회\n")

    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    bot = KMarketGrowthBot(db_mgr, supabase_mgr)

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🛒 K-Market 사이클 #{cycle} 실행 중...")
            res = bot.run_kmarket_cycle()
            print(f"✅ 사이클 #{cycle} 완료: 숏폼 {res['shorts_count']}건 / 카드뉴스 {res['cardnews_count']}장 / 레딧 {res['reddit_count']}건")
            print("⏳ 다음 사이클까지 5분간 대기합니다... (Ctrl+C 누르면 종료)")
            time.sleep(300)
    except KeyboardInterrupt:
        print("\n⏹️ K-Market 봇이 안전하게 종료되었습니다.")

if __name__ == "__main__":
    main()
