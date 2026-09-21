import os
import sys
import time
import logging
from pathlib import Path

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright
from core.reddit_browser_driver import RedditBrowserDriver

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RedditProfileSetup")

PROFILES = {
    "kmarket": {
        "display_name": "K-Market Korea Official",
        "about": "🛒 South Korea Expat Secondhand & $0 Free Giveaway Marketplace. Auto-translated in 17 languages for foreign students & workers in Korea.",
        "link_title": "K-Market Official Web",
        "url": "https://ktrs-market.vercel.app"
    },
    "easytax": {
        "display_name": "EasyTax Korea Official",
        "about": "💰 Korea Expat Tax Refund & Article 30 Exemption Simulator. Reclaim overpaid income taxes for foreign teachers & workers in Korea.",
        "link_title": "EasyTax Official Web",
        "url": "https://ktrs-service.vercel.app"
    }
}

def setup_reddit_profile(service_id: str = "kmarket"):
    info = PROFILES.get(service_id, PROFILES["kmarket"])
    driver = RedditBrowserDriver(service_id=service_id)
    account_info = driver.get_account_karma()
    username = account_info.get("username")
    
    print(f"\n========================================================")
    print(f"🔧 [{service_id.upper()}] u/{username} 프로필 맞춤 설정 시작")
    print(f"🌐 정확한 공식 URL: {info['url']}")
    print(f"========================================================\n")
    
    with sync_playwright() as p:
        context = driver._create_persistent_context(p, headless=True)
        page = context.pages[0] if context.pages else context.new_page()
        
        # 1. 프로필 설정 페이지 접속
        page.goto("https://www.reddit.com/settings/profile", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        
        # 2. '소셜 링크' 메뉴 클릭 및 다이렉트 공식 URL 입력
        try:
            logger.info("🔗 소셜 링크 메뉴 클릭...")
            page.locator("text='소셜 링크'").first.click()
            page.wait_for_timeout(2000)
            
            # '맞춤' 항목 클릭
            custom_item = page.locator("[data-testid='ITEM-CUSTOM']").first
            if custom_item.count() > 0:
                custom_item.click()
            else:
                page.locator("text='맞춤'").last.click()
            page.wait_for_timeout(2000)
            
            # 모달 인풋 입력
            inputs = page.locator("shreddit-modal input, dialog input, faceplate-text-input input, input[type='text']")
            if inputs.count() >= 3:
                # 첫번째: 표시 텍스트
                inputs.nth(1).fill(info["link_title"])
                page.wait_for_timeout(500)
                # 두번째: 맞춤 URL
                inputs.nth(2).fill(info["url"])
                page.wait_for_timeout(500)
                
                # 맞춤 링크 추가 내부 저장 버튼 클릭
                save_inner_btn = page.locator("button:has-text('저장')").last
                save_inner_btn.click()
                page.wait_for_timeout(2000)
                
                # 최종 소셜 링크 모달의 '저장' 버튼 클릭
                save_final_btn = page.locator("button:has-text('저장')").last
                if save_final_btn.count() > 0:
                    save_final_btn.click()
                    page.wait_for_timeout(3000)
                
                logger.info(f"✅ [{service_id.upper()}] 공식 웹사이트 URL({info['url']}) 링크 등록 완료!")
        except Exception as e:
            logger.warning(f"소셜 링크 등록 중 알림: {e}")
            
        # 3. 최종 프로필 페이지로 이동하여 스크린샷 캡처
        page.goto(f"https://www.reddit.com/user/{username}/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        screenshot_path = f"final_user_profile_{service_id}.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 최종 프로필 스크린샷 저장: {screenshot_path}")
        
        context.close()
    print(f"\n🎉 [{service_id.upper()}] 프로필 공식 링크 연동 완료!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", type=str, default="easytax")
    args = parser.parse_args()
    setup_reddit_profile(args.service)
