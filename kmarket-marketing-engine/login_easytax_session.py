import os
import sys
import json
import subprocess
from pathlib import Path

# UTF-8 Encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def find_chrome():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"

def main():
    print("\n" + "=" * 70)
    print("🔑 [EasyTax] 레딧(Reddit) 실제 크롬 계정 1회 로그인 도구")
    print("=" * 70)
    print("1. 순수 크롬 브라우저가 열립니다 (EasyTax 전용 독립 프로필).")
    print("2. 화면에서 [Log In] (또는 구글 로그인)을 진행해 주세요.")
    print("3. 우측 상단에 내 아바타(프로필)가 뜨면 로그인이 완료된 것입니다.")
    print("4. 로그인이 끝나면 크롬 창을 [X] 눌러 닫아주시면 세션이 영구 저장됩니다.")
    print("=" * 70 + "\n")

    profile_dir = BASE_DIR / "data" / "reddit_profiles" / "easytax"
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    chrome_exe = find_chrome()
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")
    
    cmd = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.reddit.com/login"
    ]
    
    # Run Chrome and wait until the user closes the window
    subprocess.run(cmd)
    
    print("\n✅ 크롬 창이 닫혔습니다. 로그인 세션을 영구 보관함에 동기화 중...")
    
    # Extract cookies to JSON via Playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            cookies = context.cookies(["https://www.reddit.com", "https://reddit.com"])
            cookie_file = profile_dir.parent / "easytax_cookies.json"
            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            print(f"🍪 인증 쿠키 {len(cookies)}개 백업 동기화 완료: {cookie_file}")
            context.close()
    except Exception as e:
        print(f"쿠키 동기화 안내: {e}")

    print("\n🎉 [축하합니다] 이지텍스 레딧 로그인 세션 연동이 100% 완료되었습니다!")
    print("이제부터는 크롬 창을 닫아두셔도 이지텍스 봇이 독립 계정으로 안전하게 활동합니다.\n")

if __name__ == "__main__":
    main()
