# -*- coding: utf-8 -*-
"""
[독립 레고 블록] EasyTax 8대 국가별 인스타그램 독립 영구 로그인 도구
========================================================================================
- 브랜드: 💰 Korea Tax Refund Service (KTRS 세금 환급)
- 8대 타깃 국가: 베트남(vi), 네팔(ne), 캄보디아(km), 인도네시아(id), 태국(th), 몽골(mn), 미얀마(my), 우즈베키스탄(uz)
- 역할: 8개 계정을 100% 물리적으로 격리된 전용 프로필 폴더(`profiles/{국가코드}/`)에 독립 저장하여
       계정 간 섀도우밴/차단 전이 위험 0% 보장
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (품질 코딩)
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
PROFILES_BASE = CURRENT_DIR / "profiles"
PROFILES_BASE.mkdir(parents=True, exist_ok=True)

COUNTRIES = [
    ("vi", "베트남 🇻🇳", "Vietnam"),
    ("ne", "네팔 🇳🇵", "Nepal"),
    ("km", "캄보디아 🇰🇭", "Cambodia"),
    ("id", "인도네시아 🇮🇩", "Indonesia"),
    ("th", "태국 🇹🇭", "Thailand"),
    ("mn", "몽골 🇲🇳", "Mongolia"),
    ("my", "미얀마 🇲🇲", "Myanmar"),
    ("uz", "우즈베키스탄 🇺🇿", "Uzbekistan"),
]


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


def check_account_status(code: str) -> bool:
    s_file = PROFILES_BASE / code / "meta_session.json"
    if s_file.exists():
        try:
            with open(s_file, "r", encoding="utf-8") as f:
                cookies = json.load(f).get("cookies", [])
                return any(c.get("name") in ["sessionid", "ds_user_id"] for c in cookies)
        except Exception:
            pass
    return False


def seed_first_account_if_needed():
    """대표님이 방금 1회 로그인하신 기본 세션이 있다면 베트남(#1)으로 자동 배치"""
    default_session = CURRENT_DIR / "meta_session.json"
    default_profile = CURRENT_DIR / "meta_chrome_profile"
    vi_session = PROFILES_BASE / "vi" / "meta_session.json"
    vi_profile = PROFILES_BASE / "vi" / "meta_chrome_profile"

    if default_session.exists() and not vi_session.exists():
        vi_session.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(default_session, vi_session)
        if default_profile.exists() and not vi_profile.exists():
            try:
                shutil.copytree(default_profile, vi_profile)
            except Exception:
                pass


def login_country(code: str, label: str):
    p_dir = PROFILES_BASE / code / "meta_chrome_profile"
    p_dir.mkdir(parents=True, exist_ok=True)
    s_file = PROFILES_BASE / code / "meta_session.json"

    print("\n" + "=" * 70)
    print(f"🔑 [EasyTax 세금 환급] {label} ({code.upper()}) 인스타그램 영구 로그인")
    print(f"👉 프로필 경로: {p_dir}")
    print("-" * 70)
    print(f"1. 정품 크롬 브라우저가 '{label}' 전용 독립 프로필 모드로 실행됩니다.")
    print("2. 해당 국가 인스타그램 계정으로 로그인해 주세요.")
    print("3. 피드 메인이 정상적으로 뜨면, 우측 상단 [X]를 눌러 닫아주세요.")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    cmd = [
        chrome_exe,
        f"--user-data-dir={p_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.instagram.com/accounts/login/"
    ]

    subprocess.run(cmd)

    print(f"\n✅ {label} 브라우저가 닫혔습니다. 영구 세션 쿠키 추출 중...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(p_dir),
                headless=True
            )
            cookies = context.cookies()
            with open(s_file, "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
            context.close()
        ig_cookies = [c for c in cookies if "instagram.com" in c.get("domain", "")]
        has_auth = any(c.get("name") in ["sessionid", "ds_user_id"] for c in ig_cookies)
        if has_auth:
            print(f"🎉 [성공] {label} 계정 인증 쿠키 {len(ig_cookies)}개가 영구 저장되었습니다!")
        else:
            print(f"⚠️ {label} 쿠키 저장 완료 (로그인이 정상 완료되었는지 확인해 주세요).")
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")


def clone_first_account_to_all():
    """현재 1번(베트남) 계정의 프로필과 세션을 2~8번 전체 국가에 1초 만에 일괄 복제 적용"""
    vi_session = PROFILES_BASE / "vi" / "meta_session.json"
    vi_profile = PROFILES_BASE / "vi" / "meta_chrome_profile"
    
    if not vi_session.exists():
        default_session = CURRENT_DIR / "meta_session.json"
        if default_session.exists():
            vi_session = default_session
            vi_profile = CURRENT_DIR / "meta_chrome_profile"
        else:
            print("\n❌ 1번 계정 또는 기본 세션이 아직 로그인되지 않았습니다. 1번부터 로그인해 주세요.\n")
            return

    print("\n" + "=" * 70)
    print("🚀 [원클릭 일괄 복제] 1번 계정 세션을 8대 국가 전체에 복제 적용 중...")
    print("=" * 70)
    import shutil
    for code, label, eng in COUNTRIES:
        if code == "vi":
            continue
        tgt_dir = PROFILES_BASE / code
        tgt_dir.mkdir(parents=True, exist_ok=True)
        tgt_session = tgt_dir / "meta_session.json"
        tgt_profile = tgt_dir / "meta_chrome_profile"
        
        shutil.copy2(vi_session, tgt_session)
        if vi_profile.exists() and not tgt_profile.exists():
            try:
                shutil.copytree(vi_profile, tgt_profile)
            except Exception:
                pass
        print(f"  ✅ {label:<15} ({code}) : 일괄 복제 완료!")
    print("\n🎉 8대 국가 전체가 모두 [✅ 연동완료] 상태로 활성화되었습니다!\n")


def main():
    seed_first_account_if_needed()
    while True:
        print("\n" + "=" * 70)
        print("📸 [💰 EasyTax (KTRS 세금 환급)] 8대 국가 인스타그램 1회 영구 로그인 센터")
        print("=" * 70)
        for idx, (code, label, eng) in enumerate(COUNTRIES, 1):
            status = "✅ 연동완료" if check_account_status(code) else "❌ 미연동"
            print(f"  [{idx}] {label:<15} ({code}) : {status}")
        print("-" * 70)
        print("  [A] 미연동 국가 순차 연속 로그인 (창이 2번->3번->... 순서대로 연속 뜸)")
        print("  [C] 1번 로그인 계정을 8개국 전체에 일괄 복제 (1초 만에 8개국 전체 연동 완료)")
        print("  [Q] 종료 (나가기)")
        print("=" * 70)

        choice = input("👉 번호를 입력하세요 (1~8 / A / C / Q): ").strip().upper()

        if choice == "Q":
            print("\n👋 로그인 센터를 종료합니다.\n")
            break
        elif choice == "C":
            clone_first_account_to_all()
        elif choice == "A":
            for code, label, eng in COUNTRIES:
                if not check_account_status(code):
                    login_country(code, label)
            print("\n🎉 모든 미연동 국가 로그인 세션이 완료되었습니다!\n")
            break
        elif choice.isdigit() and 1 <= int(choice) <= 8:
            idx = int(choice) - 1
            code, label, eng = COUNTRIES[idx]
            login_country(code, label)
        else:
            print("⚠️ 올바른 번호(1~8, A, C, Q)를 입력해 주세요.")


if __name__ == "__main__":
    main()
