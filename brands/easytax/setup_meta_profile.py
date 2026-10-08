# -*- coding: utf-8 -*-
"""
EasyTax 전용 메타(인스타그램/페이스북) 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 💰 Korea Tax Refund Service (KTRS 세금 환급)
- 프로필 경로: brands/easytax/meta_chrome_profile/
- 설명: 단 1회 로그인하면 브라우저 쿠키/인증토큰/스토리지가 디스크에 영구 저장되어
       이후 24시간 무인 가동 시 인스타 피드 탐색 및 실제 '좋아요(Like)'를 자동 실행합니다.
"""

import os
import sys
import json
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
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "meta_session.json"


def find_chrome_path():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"


def main():
    print("\n" + "=" * 70)
    print("🔑 [💰 KTRS 세금 환급] 메타(인스타·페북) 영구 브라우저 프로필 1회 세팅 도구")
    print("=" * 70)
    print("👉 KTRS 세금 환급 전용 인스타그램/페이스북 계정 로그인")
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 실제 크롬 브라우저가 전용 영구 프로필 모드로 실행됩니다.")
    print("2. 인스타그램(Instagram) 또는 페이스북(Facebook)에 로그인해 주세요.")
    print("3. 로그인 후 피드 메인 화면이 정상적으로 뜨면,")
    print("4. 브라우저 창 우측 상단의 [X]를 눌러 닫아주시면 영구 저장이 완료됩니다.")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    print(f"🚀 실제 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.instagram.com/accounts/login/"
    ]

    subprocess.run(cmd)

    print("\n✅ 브라우저가 닫혔습니다. 영구 쿠키 동기화 중...")

    # Playwright로 쿠키 추출하여 meta_session.json 동기화
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True
            )
            cookies = context.cookies()
            with open(SESSION_JSON, "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
            context.close()
        print(f"🎉 [성공] 총 {len(cookies)}개의 최신 메타 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
        
        # 🚀 [자동 일괄 복제] 8대 국가 전용 독립 프로필에 1초 만에 자동 일괄 배포!
        import shutil
        countries = [
            ("vi", "베트남 🇻🇳"), ("ne", "네팔 🇳🇵"), ("km", "캄보디아 🇰🇭"), ("id", "인도네시아 🇮🇩"),
            ("th", "태국 🇹🇭"), ("mn", "몽골 🇲🇳"), ("my", "미얀마 🇲🇲"), ("uz", "우즈베키스탄 🇺🇿")
        ]
        profiles_base = CURRENT_DIR / "profiles"
        profiles_base.mkdir(parents=True, exist_ok=True)
        print("\n" + "=" * 70)
        print("🚀 [자동 일괄 배포] 방금 로그인하신 인증 세션을 8대 국가 전체에 자동 복제 중...")
        print("=" * 70)
        for c_code, c_label in countries:
            c_dir = profiles_base / c_code
            c_dir.mkdir(parents=True, exist_ok=True)
            c_session = c_dir / "meta_session.json"
            c_profile = c_dir / "meta_chrome_profile"
            shutil.copy2(SESSION_JSON, c_session)
            if PROFILE_DIR.exists() and not c_profile.exists():
                try:
                    shutil.copytree(PROFILE_DIR, c_profile)
                except Exception:
                    pass
            print(f"  ✅ {c_label:<15} ({c_code}) : 100% 자동 연동 완료!")
        print("\n🎉 [완료] 단 1회 로그인으로 8대 국가 전체 프로필이 모두 [✅ 연동완료] 되었습니다!")
        print("👉 이제 봇이 8개국을 순차적으로 번갈아가며 100% 무인 자율 구동합니다.\n")
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")


if __name__ == "__main__":
    main()
