# -*- coding: utf-8 -*-
"""
레딧(Reddit) 실제 크롬 계정 1회 영구 연동 도구
- 실제 구글 크롬 브라우저를 실행하여 구글/이메일로 1회 로그인
- 창이 닫히면 프로필의 세션 및 LocalStorage/LevelDB OAuth 토큰을 자동 검증·추출하여 영구 동기화
"""

import os
import sys
import re
import json
import time
import subprocess
import urllib.request
from pathlib import Path

# UTF-8 Console
os.system("chcp 65001 > nul")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / "brands").name != "brands" and BASE_DIR.parent.name == "brands":
    BASE_DIR = BASE_DIR.parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SERVICE_ID = "kmarket"
DISPLAY_NAME = "K-Market"


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


def verify_oauth_token(token_str: str) -> dict:
    req = urllib.request.Request(
        "https://oauth.reddit.com/api/v1/me",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Authorization": f"Bearer {token_str}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("name"):
                return {
                    "valid": True,
                    "username": data.get("name"),
                    "karma": data.get("total_karma", (data.get("comment_karma", 0) + data.get("link_karma", 0)))
                }
    except Exception:
        pass
    return {"valid": False}


def extract_leveldb_user_token(profile_dir: Path) -> dict:
    leveldb_dir = profile_dir / "Default" / "Local Storage" / "leveldb"
    if not leveldb_dir.exists():
        return {"token": None, "username": None, "karma": 0}

    for log_file in leveldb_dir.glob("*.log"):
        try:
            content = log_file.read_bytes()
            tokens = re.findall(b'eyJhbGciOiJSUzI1NiIsImtpZCI6[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', content)
            for t_bytes in reversed(tokens):
                t_str = t_bytes.decode("ascii")
                v_res = verify_oauth_token(t_str)
                if v_res.get("valid"):
                    return {
                        "token": t_str,
                        "username": v_res.get("username"),
                        "karma": v_res.get("karma", 0)
                    }
        except Exception:
            pass

    return {"token": None, "username": None, "karma": 0}


def main():
    print("\n" + "=" * 74)
    print(f"🔑 [{DISPLAY_NAME}] 레딧(Reddit) 실제 크롬 계정 1회 영구 연동 도구")
    print("=" * 74)
    print(f" 1. 순수 구글 크롬 브라우저 창이 열립니다 ({DISPLAY_NAME} 전용 영구 프로필).")
    print(" 2. 화면에서 [Log In] -> [Continue with Google]을 눌러 로그인해 주세요.")
    print(" 3. 화면 우측 상단에 내 아바타 프로필 아이콘이 확인되면 크롬 창을 [X]로 닫아주세요.")
    print("=" * 74 + "\n")

    profile_dir = BASE_DIR / "data" / "reddit_profiles" / SERVICE_ID
    profile_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = profile_dir.parent / f"{SERVICE_ID}_cookies.json"
    health_file = profile_dir.parent / f"{SERVICE_ID}_health.json"

    # 기존 토큰 검증
    level_check = extract_leveldb_user_token(profile_dir)
    if level_check.get("token"):
        print(f"💡 기존에 연동된 인증 세션이 확인되었습니다: u/{level_check['username']} (카르마: {level_check['karma']}점)")
        print("   계정을 변경하시려면 새로 열리는 창에서 다른 계정으로 로그인해 주세요.\n")

    chrome_exe = find_chrome()
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.reddit.com/login"
    ]

    subprocess.run(cmd)

    print("\n🔒 크롬 창이 닫혔습니다. 로그인 세션을 영구 보관함에 동기화 및 검증 중...")
    time.sleep(2)

    # 1. LevelDB에서 유효 OAuth 토큰 정밀 추출
    token_info = extract_leveldb_user_token(profile_dir)
    username = token_info.get("username")
    karma = token_info.get("karma", 0)
    auth_token = token_info.get("token")

    # 2. Playwright를 통한 추가 쿠키 백업
    cookies = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=True,
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            cookies = [c for c in context.cookies() if "reddit" in c.get("domain", "")]
            context.close()
    except Exception:
        pass

    # 3. 토큰 주입 및 쿠키 파일 영구 보관
    if auth_token:
        found = False
        for c in cookies:
            if c.get("name") == "token_v2":
                c["value"] = auth_token
                found = True
                break
        if not found:
            cookies.append({
                "name": "token_v2",
                "value": auth_token,
                "domain": ".reddit.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            })

    if cookies:
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

    # 4. 헬스 모니터 동기화
    if username:
        health_data = {}
        if health_file.exists():
            try:
                with open(health_file, "r", encoding="utf-8") as hf:
                    health_data = json.load(hf)
            except Exception:
                pass

        health_data["service_id"] = SERVICE_ID
        health_data["username"] = username
        health_data["karma"] = karma
        health_data["alert_level"] = 0
        health_data["cooldown_until"] = None
        with open(health_file, "w", encoding="utf-8") as hf:
            json.dump(health_data, hf, indent=2, ensure_ascii=False)

    print("\n" + "=" * 74)
    if username and auth_token:
        print(f"🎉 [성공] {DISPLAY_NAME} 레딧 영구 로그인 연동이 100% 완료되었습니다!")
        print(f"   • 실제 연동 계정: u/{username}")
        print(f"   • 현재 보유 카르마: {karma}점")
        print(f"   • 영구 인증 토큰: {auth_token[:25]}... (정상 유효)")
        print(f"   • 인증 쿠키 보관: {len(cookies)}개 ({cookie_file.name})")
        print(f"   • 영구 세션 보관소: {profile_dir}")
        print("=" * 74)
        print("✨ 이제부터 크롬 창을 닫아두셔도 봇이 24시간 365일 무인으로 자동 활동합니다.\n")
    else:
        print(f"⚠️ [알림] 로그인 세션이 아직 완전히 발급되지 않았습니다.")
        print(f"   • 해결 방법: 배치 파일을 다시 실행하신 후, 구글 로그인 완료 후 화면 우측 상단에")
        print(f"               내 프로필 아바타가 완전히 보일 때까지 3~5초만 기다리신 뒤 창을 닫아주세요.\n")
        print("=" * 74 + "\n")


if __name__ == "__main__":
    main()
