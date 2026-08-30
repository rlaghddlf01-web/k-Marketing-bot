"""
setup_telethon_session.py — 서브폰 Telethon 세션 안전 1회 설정 스크립트
"""

import os
import sys
import shutil
from pathlib import Path

# UTF-8 Encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass


def main():
    api_id = int(os.getenv("TELEGRAM_API_ID", os.getenv("KMARKET_TELETHON_API_ID", "23659525")))
    api_hash = os.getenv("TELEGRAM_API_HASH", os.getenv("KMARKET_TELETHON_API_HASH", "9e69ea7dabc401002552face69b56e4f"))

    print("\n" + "=" * 65)
    print("  📱 [KTRS] 텔레그램 스텔스 홍보/초대 계정 1회 세션 등록 도구")
    print("=" * 65)
    print(f"  API ID: {api_id}")
    print(f"  API Hash: {api_hash[:8]}************************")
    print("=" * 65)

    try:
        from telethon.sync import TelegramClient
        from telethon.errors import SessionPasswordNeededError

        master_session_path = str(BASE_DIR / "telegram_stealth_master")
        client = TelegramClient(master_session_path, api_id, api_hash)
        client.connect()

        if not client.is_user_authorized():
            print("\n👉 스텔스 홍보/초대에 사용할 전화번호를 입력하세요.")
            print("👉 형식: +821012345678 (국가번호 +82 필수)")
            phone = input("\n📱 전화번호 입력: ").strip()

            if not phone:
                print("❌ 전화번호가 입력되지 않았습니다.")
                input("\n엔터를 누르면 창이 닫힙니다...")
                return

            print(f"\n📩 {phone} 번호로 텔레그램 인증코드를 발송 중입니다...")
            sent_code = client.send_code_request(phone)
            print("✅ 텔레그램 앱으로 인증코드가 발송되었습니다!")

            code = input("\n🔑 텔레그램 앱에 온 인증코드(5자리 숫자) 입력: ").strip()
            try:
                client.sign_in(phone, code)
            except SessionPasswordNeededError:
                pwd = input("\n🔒 텔레그램 2단계 인증(2FA) 비밀번호 입력: ").strip()
                client.sign_in(password=pwd)

        me = client.get_me()
        print("\n" + "=" * 65)
        print("  🎉 [축하합니다] 텔레그램 계정 인증이 100% 완료되었습니다!")
        print(f"  계정 이름: {me.first_name} {me.last_name or ''}")
        print(f"  전화번호: +{me.phone}")
        print("=" * 65)
        client.disconnect()

        # 4개 세션 파일로 자동 복제
        master_file = BASE_DIR / "telegram_stealth_master.session"
        if master_file.exists():
            target_sessions = [
                "kmarket_outreach.session",
                "kmarket_worker.session",
                "easytax_outreach.session",
                "easytax_worker.session"
            ]
            for s_name in target_sessions:
                target_path = BASE_DIR / s_name
                shutil.copy2(master_file, target_path)
                print(f"  ✅ 세션 동기화 완료: {s_name}")

        print("\n🚀 이제 대시보드에서 타 그룹 홍보 및 스텔스 초대가 즉시 활성화됩니다!\n")

    except ImportError:
        print("\n❌ Telethon 라이브러리가 설치되어 있지 않습니다. 설치 중...")
        os.system("pip install telethon")
        print("설치 완료! 다시 실행해 주세요.")
    except Exception as e:
        print(f"\n❌ 세션 생성 중 오류 발생: {e}")

    input("\n엔터(Enter)를 누르면 안전하게 창이 닫힙니다...")


if __name__ == "__main__":
    main()
