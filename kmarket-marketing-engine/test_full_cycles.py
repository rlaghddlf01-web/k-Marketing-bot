import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.kmarket_bot import KMarketGrowthBot
from core.easytax_bot import EasyTaxRefundBot

print("==================================================")
print("🚀 [1/2] K-Market 성장 봇 1회 사이클 실시간 테스트")
print("==================================================")
db = DBManager()
sm = SupabaseManager(db)

km_bot = KMarketGrowthBot(db, sm)
km_res = km_bot.run_kmarket_cycle()

print("\n🎉 [K-Market 사이클 완료]:")
print(f"  • 0원 나눔 숏폼: {km_res['shorts_count']}건")
print(f"  • 실물 매물 카드뉴스: {km_res['cardnews_count']}장")
print(f"  • 텔레그램 브리핑: {km_res['telegram_count']}건")
print(f"  • 레딧 스캔/답변: {km_res['reddit_count']}건")
print(f"  • SEO 블로그 발행: {km_res['blog_count']}건")

print("\n==================================================")
print("💰 [2/2] EasyTax 세무 봇 1회 사이클 실시간 테스트")
print("==================================================")
tax_bot = EasyTaxRefundBot(db, sm)
tax_res = tax_bot.run_easytax_cycle()

print("\n🎉 [EasyTax 사이클 완료]:")
print(f"  • 세무 환급 숏폼: {tax_res['shorts_count']}건")
print(f"  • Anti-Ban 카드뉴스: {tax_res['cardnews_count']}장")
print(f"  • 텔레그램 브리핑: {tax_res['telegram_count']}건")
print(f"  • 레딧 스캔/답변: {tax_res['reddit_count']}건")
print(f"  • 세무 블로그 발행: {tax_res['blog_count']}건")
print("==================================================")
