"""
YouTube OAuth 2.0 인증 및 채널 연동 매니저
- 최초 1회 브라우저 로그인을 통해 refresh_token을 획득하고 data/youtube_token.json 에 영구 보관
- 이후 자동 토큰 갱신(Refresh) 지원
- 연결된 채널 정보 조회 및 테스트 영상 비공개(private) 업로드 지원
"""

import os
import sys
import json
from pathlib import Path

# Windows cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from google_auth_oauthlib.flow import InstalledAppFlow

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_PATH = BASE_DIR / "data" / "youtube_token.json"

def get_client_secrets_file(brand: str = None) -> Path:
    """브랜드별 전용 client_secrets 파일 반환 (client_secrets_kmarket.json 우선)"""
    if brand:
        brand_secrets = BASE_DIR / f"client_secrets_{brand.lower().strip()}.json"
        if brand_secrets.exists():
            return brand_secrets
    return CLIENT_SECRETS_FILE

def get_token_path(brand: str = None) -> Path:
    """브랜드별 독립 토큰 경로 반환 (kmarket -> youtube_token_kmarket.json)"""
    if brand:
        return BASE_DIR / "data" / f"youtube_token_{brand.lower().strip()}.json"
    return TOKEN_PATH

class CustomFlow(InstalledAppFlow):
    """보안 state 토큰 단일 일치 보장 및 URL 자동 추출 플로우"""
    def authorization_url(self, **kwargs):
        url, state = super().authorization_url(**kwargs)
        auth_file = BASE_DIR / "data" / "auth_url.txt"
        try:
            with open(auth_file, "w", encoding="utf-8") as af:
                af.write(url)
        except Exception:
            pass
        print(f"\n👉 [Google 승인 URL]:\n{url}\n", flush=True)
        try:
            import subprocess
            subprocess.Popen(f'start "" "{url}"', shell=True)
        except Exception:
            pass
        return url, state

def authenticate_youtube(brand: str = "kmarket", force: bool = False, port: int = 8080) -> Credentials:
    """OAuth 2.0 브라우저 로그인 플로우 실행 및 브랜드별 토큰 독립 저장"""
    creds = None
    target_token_path = get_token_path(brand)
    
    # 1. 기존 저장된 브랜드 토큰이 있는 경우 로드 (force가 아닐 때)
    if not force and target_token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(target_token_path), SCOPES)
        except Exception as e:
            print(f"⚠️ 기존 [{brand}] 토큰 로드 실패 (재인증 필요): {e}")
            creds = None

    # 2. 토큰이 없거나 유효하지 않은 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print(f"🔄 [{brand}] 토큰 만료됨 -> refresh_token으로 자동 갱신 중...")
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ [{brand}] 토큰 자동 갱신 실패: {e} -> 브라우저 로그인 실행")
                creds = None
        
        if not creds:
            secrets_file = get_client_secrets_file(brand)
            if not secrets_file.exists():
                raise FileNotFoundError(f"인증 파일이 없습니다: {secrets_file.name} (client_secrets_kmarket.json 또는 client_secrets.json)")
            
            flow = CustomFlow.from_client_secrets_file(
                str(secrets_file),
                SCOPES
            )
            # 단일 state 생성 및 로컬 서버 리디렉션 수신
            creds = flow.run_local_server(
                port=port,
                prompt="consent",
                access_type="offline",
                open_browser=False
            )
        
        # 3. 신규 토큰 저장 (브랜드 전용 파일)
        target_token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"✅ [인증 성공] [{brand}] 전용 토큰이 안전하게 저장되었습니다: {target_token_path.name}")
        
        # 호환성을 위해 youtube_token.json도 갱신
        if brand == "kmarket" or not TOKEN_PATH.exists():
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

    return creds

def get_channel_info(creds: Credentials):
    """연동된 유튜브 채널 정보 조회"""
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    req = youtube.channels().list(part="snippet,statistics", mine=True)
    res = req.execute()
    
    items = res.get("items", [])
    if not items:
        print("⚠️ 연결된 채널을 찾을 수 없습니다.")
        return None
    
    ch = items[0]
    title = ch["snippet"]["title"]
    ch_id = ch["id"]
    custom_url = ch["snippet"].get("customUrl", "")
    print("=" * 60)
    print(f"🎉 [연동 성공] 연결된 유튜브 채널: {title}")
    print(f"📌 채널 ID: {ch_id} | 핸들: {custom_url}")
    print("=" * 60)
    return ch

def upload_test_short(creds: Credentials, video_path: str = None, brand: str = "kmarket") -> dict:
    """비공개(private) 테스트 쇼츠 업로드 및 링크 검증"""
    if not video_path:
        if brand == "kmarket":
            # K-Market 베트남 숏폼 샘플 찾기
            km_candidates = [
                BASE_DIR / "outputs" / "shorts_kmarket" / "kmarket_story5_vi_ind_ulsan_onsan_1788242706.mp4",
                Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\KTRS마켓\kmarket_story5_ko_ind_ansan_wongok_1788679301.mp4"),
            ]
            for c in km_candidates:
                if c.exists():
                    video_path = str(c)
                    break
        else:
            outputs_dir = BASE_DIR / "outputs" / "shorts"
            samples = list(outputs_dir.glob("easytax_story5_vi_*.mp4"))
            if samples:
                video_path = str(samples[0])

        if not video_path or not Path(video_path).exists():
            raise FileNotFoundError(f"업로드할 [{brand}] 테스트 숏폼 비디오를 찾을 수 없습니다.")

    print(f"🚀 [{brand.upper()} 비공개 테스트 업로드 시작] 파일: {Path(video_path).name}")
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    
    if brand == "kmarket":
        title = "K-Market Vietnam - Đồ dùng 0 Won tại Hàn Quốc #Shorts"
        desc = "Mua sắm đặc sản và nhận đồ dùng 0 Won tại Hàn Quốc cùng K-Market.\n\n👉 Nhận đồ 0 Won ngay tại: https://ktrs-market.vercel.app/vi\n\n#Shorts #KMarket #Vietnam #0Won"
        pinned_comment = "🛒 Mua sắm và nhận đồ dùng 0 Won tại Hàn Quốc ngay: https://ktrs-market.vercel.app/vi"
        tags = ["KMarket", "Shorts", "Vietnam", "0Won", "Korea"]
    else:
        title = "KTRS Vietnam Tax Refund Test #Shorts"
        desc = "Hỗ trợ hoàn thuế thu nhập 90% cho lao động E-9 tại Hàn Quốc (KTRS)\n\n#Shorts #KTRS #E9TaxRefund"
        pinned_comment = "👉 Nhận hoàn thuế E-9 ngay tại: https://ktrs-service.vercel.app/?lang=vi"
        tags = ["KTRS", "Shorts", "E9Tax", "Vietnam"]
    
    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": tags,
            "categoryId": "22"  # People & Blogs / Shopping
        },
        "status": {
            "privacyStatus": "private",  # 비공개로 안전하게 테스트!
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    insert_req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    print("⏳ 유튜브 비디오 전송 중...")
    response = insert_req.execute()
    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"✅ [업로드 성공!] 비디오 ID: {video_id}")
    print(f"🔗 비공개 영상 링크: {video_url}")
    
    # 고정 댓글 등록 시도
    try:
        comm_req = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": pinned_comment
                        }
                    }
                }
            }
        )
        comm_res = comm_req.execute()
        print(f"💬 [고정 댓글 성공] 내용: {pinned_comment}")
    except Exception as e:
        print(f"⚠️ 댓글 등록 알림 (비공개 영상 상태에선 댓글 제한 가능): {e}")

    return {
        "success": True,
        "video_id": video_id,
        "url": video_url
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube OAuth 2.0 브랜드별 연동 도구")
    parser.add_argument("--brand", type=str, default="kmarket", help="연동할 브랜드 (kmarket 또는 easytax)")
    parser.add_argument("--force", action="store_true", help="기존 토큰 무시하고 새 채널로 브라우저 재인증 실행")
    parser.add_argument("--test-upload", action="store_true", help="인증 후 비공개 테스트 영상 업로드까지 실행")
    args = parser.parse_args()
    
    creds = authenticate_youtube(brand=args.brand, force=args.force)
    get_channel_info(creds)
    
    if args.test_upload:
        upload_test_short(creds, brand=args.brand)
