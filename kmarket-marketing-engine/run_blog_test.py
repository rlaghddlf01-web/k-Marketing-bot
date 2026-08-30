import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dotenv import load_dotenv
load_dotenv()

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from modules.blog_easytax import EasyTaxBlogPublisher
from modules.blog_kmarket import KMarketBlogPublisher

def main():
    print("========================================================")
    print("🚀 [100% 전문 번역 엔진 탑재] 블로그 풀 사이클 가동 테스트")
    print("========================================================\n")

    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)

    # 1. Supabase 이전 글 삭제
    print("🧹 [1/3] Supabase 이전 블로그 글 초기화...")
    if supabase_mgr.client:
        try:
            supabase_mgr.client.table("easytax_blogs").delete().neq("slug", "keep_schema_anchor").execute()
            supabase_mgr.client.table("kmarket_blogs").delete().neq("slug", "keep_schema_anchor").execute()
            print("✅ Supabase easytax_blogs & kmarket_blogs 초기화 완료.")
        except Exception as e:
            print(f"⚠️ 초기화 에러: {e}")

    # 2. EasyTax 블로그 발행 (15개국어 본문 전문 100% 번역)
    print("\n" + "━" * 50)
    print("💰 [2/3] EasyTax 블로그 15개국어 전문 발행 시작...")
    print("━" * 50)
    t0 = time.time()
    easytax_pub = EasyTaxBlogPublisher(db_mgr, supabase_mgr)
    res_e = easytax_pub.publish_multilingual_articles()
    elapsed_e = time.time() - t0
    print(f"✅ EasyTax 완료! ({elapsed_e:.1f}초, {res_e.get('supabase_uploaded')}건 Supabase 업로드)")

    # 3. K-Market 블로그 발행 (17개국어 본문 전문 100% 번역)
    print("\n" + "━" * 50)
    print("🛒 [3/3] K-Market 블로그 17개국어 전문 발행 시작...")
    print("━" * 50)
    t0 = time.time()
    kmarket_pub = KMarketBlogPublisher(db_mgr, supabase_mgr)
    res_k = kmarket_pub.publish_multilingual_articles()
    elapsed_k = time.time() - t0
    print(f"✅ K-Market 완료! ({elapsed_k:.1f}초, {res_k.get('supabase_uploaded')}건 Supabase 업로드)")

    print("\n========================================================")
    print(f"🎉 전체 사이클 완료! 총 소요 시간: {elapsed_e + elapsed_k:.1f}초")
    print("========================================================")

if __name__ == "__main__":
    main()
