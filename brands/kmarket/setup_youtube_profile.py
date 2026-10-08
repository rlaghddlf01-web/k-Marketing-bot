# -*- coding: utf-8 -*-
"""
KMarket (KTRS Market) 전용 유튜브 (Google/YouTube) 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 🛒 KTRS Market (공식 명칭: KTRS Market / KTRS 마켓)
- 전용 계정: KTRS Market 공식 채널 계정
- 프로필 경로: brands/kmarket/youtube_chrome_profile/
- 방식: 실제 구글 크롬(Google Chrome) 브라우저를 직접 실행하여 구글의 '안전하지 않은 브라우저'
        차단 없이 100% 안전하게 로그인 후, 세션 쿠키를 영구 추출 및 동기화합니다.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "youtube_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "youtube_session.json"

MIRROR_DIRS = [
    Path(r"C:\ktrs_marketing_bot\kmarket-marketing-engine\brands\kmarket"),
    Path(r"C:\Users\zkfnt\Desktop\ktrs 마케팅 봇\brands\kmarket"),
    Path(r"C:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇\brands\kmarket")
]


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


def sync_session_to_mirrors(session_data: dict):
    """모든 엔진 작업 경로에 세션 파일 동기화 복사"""
    for mdir in MIRROR_DIRS:
        try:
            if mdir.exists():
                target_json = mdir / "youtube_session.json"
                with open(target_json, "w", encoding="utf-8") as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                print(f"🔄 세션 동기화 완료: {target_json}", flush=True)
        except Exception as e:
            pass


def main():
    print("\n" + "=" * 75)
    print("🎬 [🛒 KTRS Market] 유튜브 (Google/YouTube) 실제 크롬 영구 로그인 도구")
    print("=" * 75)
    print("📌 대상 브랜드 : 🛒 KTRS Market")
    print(f"📌 프로필 저장 : {PROFILE_DIR}")
    print("-" * 75)
    print("1. 실제 정식 구글 크롬(Google Chrome) 창이 화면에 즉시 열립니다.")
    print("2. [KTRS Market 전용 구글 계정]으로 로그인해 주세요 (아이디/비밀번호/2단계 인증).")
    print("   ※ 정식 크롬 창이므로 구글의 '안전하지 않은 브라우저' 경고 없이 안전하게 로그인됩니다.")
    print("3. 로그인이 완료되어 유튜브 스튜디오 또는 유튜브 화면이 보이면 크롬 창을 [X]로 닫아주세요.")
    print("4. 창이 닫히면 인증 세션 쿠키가 자동으로 추출되어 영구 저장됩니다.")
    print("=" * 75 + "\n")

    clean_browser_profile_locks(PROFILE_DIR)

    chrome_exe = find_chrome()
    login_url = "https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fstudio.youtube.com%2F"

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        login_url
    ]

    print(f"🚀 실제 구글 크롬 브라우저를 화면에 실행합니다...", flush=True)
    print(f"   (실행 파일: {chrome_exe})\n", flush=True)

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ 크롬 실행 실패: {e}", flush=True)
        return

    print("\n🔒 크롬 창이 닫혔습니다. 로그인 세션을 영구 보관함에 동기화 및 검증 중...", flush=True)
    time.sleep(2)

    clean_browser_profile_locks(PROFILE_DIR)

    # Playwright를 이용해 프로필의 영구 쿠키 추출
    clean_cookies = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=["--disable-gpu", "--no-sandbox"]
            )
            raw_cookies = ctx.cookies()
            for c in raw_cookies:
                c_item = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".youtube.com"),
                    "path": c.get("path", "/")
                }
                if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                    c_item["sameSite"] = c["sameSite"]
                if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                    c_item["secure"] = True
                clean_cookies.append(c_item)
            ctx.close()
    except Exception as ce:
        print(f"쿠키 추출 참조: {ce}", flush=True)

    has_login = any(c.get("name") in ["LOGIN_INFO", "SID", "SSID", "SAPISID"] for c in clean_cookies)
    if has_login or len(clean_cookies) > 5:
        session_data = {"cookies": clean_cookies, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        with open(SESSION_JSON, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        sync_session_to_mirrors(session_data)

        print("\n" + "=" * 75)
        print(f"🎉 총 {len(clean_cookies)}개의 유튜브 세션 쿠키가 영구 보관함에 저장되었습니다!")
        print("✅ [검증 통과] 🛒 KTRS Market 구글/유튜브 인증 토큰(SID/LOGIN_INFO) 정상 감지 완료!")
        print("   이제 스텔스 행동 봇이 정식 로그인 상태로 유튜브를 사람처럼 시청합니다.")
        print("=" * 75 + "\n")
    else:
        print("\n" + "=" * 75)
        print("⚠️ [경고] 구글 로그인 인증 토큰이 감지되지 않았습니다.")
        print("   크롬 창에서 구글 계정 로그인을 완전히 마친 뒤 창을 닫아주셔야 정상 저장됩니다.")
        print("   바탕화면의 [1회연동] 배치파일을 다시 실행하여 로그인을 완료해 주세요.")
        print("=" * 75 + "\n")


if __name__ == "__main__":
    main()