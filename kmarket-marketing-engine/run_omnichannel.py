import os
import sys
import time
import argparse
from pathlib import Path

# UTF-8 출력 보장
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager
from core.omnichannel_campaign_engine import OmnichannelCampaignEngine

def main():
    parser = argparse.ArgumentParser(description="Omnichannel 360 Marketing Runner")
    parser.add_argument("--service", type=str, default="all", choices=["kmarket", "easytax", "all"], help="대상 서비스 (kmarket / easytax / all)")
    parser.add_argument("--lang", type=str, default="en", help="타깃 언어 (기본: en)")
    args = parser.parse_args()

    print("\n========================================================")
    print("🎬 [Omnichannel 360 Engine] 숏폼 & 카드뉴스 5대 플랫폼 동시 배포")
    print("========================================================")
    print("• 배포 플랫폼: YouTube Shorts + TikTok + Instagram + Facebook + Reddit + Telegram")
    print("• 제작 콘텐츠: 9:16 고화질 세로 비디오(MP4) + 1080x1080 4장 캐러셀 카드뉴스(PNG)")
    print(f"• 타깃 서비스: {args.service.upper()} / 타깃 언어: {args.lang.upper()}\n")

    db_mgr = DBManager()
    supabase_mgr = SupabaseManager(db_mgr)
    engine = OmnichannelCampaignEngine(db_mgr, supabase_mgr)

    services_to_run = ["kmarket", "easytax"] if args.service == "all" else [args.service]

    for s_id in services_to_run:
        print(f"[{time.strftime('%H:%M:%S')}] 🚀 [{s_id.upper()}] 옴니채널 캠페인 제작 및 패키징 가동...")
        result = engine.execute_campaign(service_id=s_id, target_lang=args.lang)
        
        print(f"\n✨ [{s_id.upper()}] 제작 완료 내역:")
        if result["shorts_video"]:
            print(f"   🎥 숏폼 영상: {result['shorts_video']['file_path']}")
            print(f"   🏷️ 제목: {result['shorts_video']['hook_title']}")
        print(f"   🖼️ 카드뉴스: {len(result['cardnews_slides'])}장 생성 완료")
        print(f"   📦 배포 준비 채널: 6개 플랫폼 (YouTube, TikTok, Instagram, Facebook, Reddit, Telegram)")
        print("--------------------------------------------------------")

    print("\n🎉 모든 옴니채널 패키징이 성공적으로 완료되었습니다!")
    print("👉 대시보드(http://localhost:8000)에서 실시간 영상 및 카드뉴스를 바로 확인하실 수 있습니다.\n")

if __name__ == "__main__":
    main()
