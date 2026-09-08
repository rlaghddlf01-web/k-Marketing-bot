import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

# 🇰🇷 대한민국 표준시 (KST, UTC+9) 고정 타임존
KST = datetime.timezone(datetime.timedelta(hours=9))

def get_now_kst() -> datetime.datetime:
    """현재 한국 표준시(KST) datetime 객체 반환"""
    return datetime.datetime.now(KST)

def get_now_kst_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """현재 한국 표준시(KST) 문자열 반환"""
    return get_now_kst().strftime(fmt)

# Base Directory & Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

(OUTPUTS_DIR / "shorts").mkdir(exist_ok=True)
(OUTPUTS_DIR / "cardnews").mkdir(exist_ok=True)
(OUTPUTS_DIR / "pdf_guides").mkdir(exist_ok=True)
(OUTPUTS_DIR / "briefings").mkdir(exist_ok=True)
(OUTPUTS_DIR / "logs").mkdir(exist_ok=True)
(OUTPUTS_DIR / "seo_pages").mkdir(exist_ok=True)

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# 🎯 공식 17개국(K-Market) 및 15개국(EasyTax) 언어 표준 정의
KMARKET_LANGUAGES = [
    "ko", "vi", "zh", "en", "ja", "ru", "th", "uz", 
    "km", "mn", "ne", "id", "my", "si", "kk", "bn", "ur"
]

EASYTAX_LANGUAGES = [
    "ko", "vi", "zh", "km", "ne", "uz", "my", "id", 
    "th", "en", "si", "mn", "bn", "kk", "ur"
]

# 🎯 8대 황금 타깃 국가 (유료 이미지 생성 채널: shorts, cardnews 선불 최적화 전용)
# 대한민국 체류 E-9 비자 근로자 84.1% 및 조특법 30조 90% 소득세 감면 환급 잠재 고객 90% 집중
GOLDEN_EIGHT_LANGUAGES = [
    "vi", "uz", "km", "ne", "th", "id", "mn", "my"
]

GOLDEN_EIGHT_DETAILS = {
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "flag": "🇻🇳", "reason": "E-9 1위 & D-2 유학생 1위, 최다 환급액"},
    "uz": {"name": "Uzbek", "native": "O'zbek", "flag": "🇺🇿", "reason": "E-9 제조업 2위, 결속력 최상위"},
    "km": {"name": "Khmer", "native": "ភាសាខ្មែរ", "flag": "🇰🇭", "reason": "E-9 농축산/제조업, 미수령 환급 1위"},
    "ne": {"name": "Nepali", "native": "नेपाली", "flag": "🇳🇵", "reason": "E-9 제조업 4.2만, 페이스북 전파력 1위"},
    "th": {"name": "Thai", "native": "ไทย", "flag": "🇹🇭", "reason": "체류자 17만, 단체 환급 신청 최다"},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "flag": "🇮🇩", "reason": "E-9 선원/제조업, 5년 소급 환급 대상 즐비"},
    "mn": {"name": "Mongolian", "native": "Монгол", "flag": "🇲🇳", "reason": "D-2 유학생 2위, 알바 소득세 100% 환급"},
    "my": {"name": "Burmese", "native": "မြန်မာ", "flag": "🇲🇲", "reason": "E-9 신규 쿼터 1위, 빠른 유입 증가세"}
}

# 17 Languages & Edge-TTS Voice Mapping (실제 K-Market 및 EasyTax 서비스 100% 동기화)
LANGUAGES = {
    "ko": {
        "name": "Korean",
        "native_name": "한국어",
        "voice": "ko-KR-SunHiNeural",
        "target": "국내 거주 다문화 및 외국인 공통"
    },
    "vi": {
        "name": "Vietnamese",
        "native_name": "Tiếng Việt",
        "voice": "vi-VN-HoaiMyNeural",
        "target": "전국 대학 유학생(1위), 제조업/농축산업 근로자"
    },
    "zh": {
        "name": "Chinese",
        "native_name": "中文",
        "voice": "zh-CN-XiaoxiaoNeural",
        "target": "국내 유학생, 어학당, 체류 교민"
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "voice": "en-US-JennyNeural",
        "target": "교환학생, 원어민 강사, 주한미군, 글로벌 IT 직장인 및 필리핀 커뮤니티"
    },
    "ja": {
        "name": "Japanese",
        "native_name": "日本語",
        "voice": "ja-JP-NanamiNeural",
        "target": "교환학생 및 국내 거주 일본인 (KTRS 마켓 전용)"
    },
    "ru": {
        "name": "Russian",
        "native_name": "Русский",
        "voice": "ru-RU-SvetlanaNeural",
        "target": "중앙아시아 고려인 및 러시아어권 체류자 (KTRS 마켓 전용)"
    },
    "th": {
        "name": "Thai",
        "native_name": "ไทย",
        "voice": "th-TH-PremwadeeNeural",
        "target": "전국 산업 단지 및 문화 교류자"
    },
    "uz": {
        "name": "Uzbek",
        "native_name": "O'zbek",
        "voice": "uz-UZ-MadinaNeural",
        "target": "이태원, 광주, 평택 등 우즈벡 유학생/근로자"
    },
    "km": {
        "name": "Khmer",
        "native_name": "ភាសាខ្មែរ",
        "voice": "km-KH-SreymomNeural",
        "target": "제조업/농축산업 근로자"
    },
    "mn": {
        "name": "Mongolian",
        "native_name": "Монгол",
        "voice": "mn-MN-YesuiNeural",
        "target": "안산, 수원, 동대문 거주 몽골인 커뮤니티"
    },
    "ne": {
        "name": "Nepali",
        "native_name": "नेपाली",
        "voice": "ne-NP-HemkalaNeural",
        "target": "유학생 및 외국인 근로자"
    },
    "id": {
        "name": "Indonesian",
        "native_name": "Bahasa Indonesia",
        "voice": "id-ID-GadisNeural",
        "target": "해양/제조업 근로자 및 유학생"
    },
    "my": {
        "name": "Burmese",
        "native_name": "မြန်မာ",
        "voice": "my-MM-NilarNeural",
        "target": "어학당 및 유학생"
    },
    "si": {
        "name": "Sinhala",
        "native_name": "සිංහල",
        "voice": "si-LK-ThiliniNeural",
        "target": "스리랑카 근로자 및 유학생"
    },
    "kk": {
        "name": "Kazakh",
        "native_name": "Қазақша",
        "voice": "kk-KZ-AigulNeural",
        "target": "카자흐스탄 유학생 및 중앙아시아 근로자"
    },
    "bn": {
        "name": "Bengali",
        "native_name": "বাংলা",
        "voice": "bn-BD-NabanitaNeural",
        "target": "방글라데시 유학생/연구원/근로자"
    },
    "ur": {
        "name": "Urdu",
        "native_name": "اردو",
        "voice": "ur-PK-UzmaNeural",
        "target": "파키스탄 기술인력 및 유학생/근로자"
    }
}

# 🎯 K-Market 17개국 인구통계 & 비자 유형 기반 맞춤 가중치 (총합 100%)
KMARKET_LANGUAGE_WEIGHTS = {
    "zh": 23.0,  # 중국/중화권 (85만 유학생/거주자)
    "vi": 22.0,  # 베트남 (유학생 1위, 0원 나눔 최다 수요)
    "en": 14.0,  # 글로벌 영어 (대학가 유학생/원어민)
    "uz": 8.0,   # 우즈베키스탄 (공단/대학가 밀집)
    "mn": 6.0,   # 몽골 (수도권 대학가 0원 나눔)
    "ru": 5.0,   # 러시아/CIS (고려인 밀집촌)
    "th": 3.0,   # 태국
    "id": 3.0,   # 인도네시아
    "ja": 3.0,   # 일본 (교환학생/거주민)
    "ne": 2.0,   # 네팔
    "km": 2.0,   # 캄보디아
    "my": 2.0,   # 미얀마
    "si": 2.0,   # 스리랑카
    "kk": 1.5,   # 카자흐스탄
    "bn": 1.5,   # 방글라데시
    "ur": 1.0,   # 파키스탄
    "ko": 1.0    # 한국어/다문화
}

# 🎯 EasyTax 15개국 E-9 고용허가제 및 세무환급 특화 가중치 (총합 100%)
EASYTAX_LANGUAGE_WEIGHTS = {
    "vi": 26.0,  # 베트남 (E-9 근로자 1위 + 알바 1위, 최다 환급액)
    "uz": 15.0,  # 우즈베키스탄 (E-9 제조업 90% 소득세 감면 핵심)
    "zh": 13.0,  # 중국/중화권 (F-4/H-2 및 유학생)
    "en": 8.0,   # 글로벌 영어 (원어민/IT/필리핀 E-9)
    "th": 8.0,   # 태국 (E-9 근로자 퇴직금/소득세 환급)
    "id": 6.0,   # 인도네시아 (E-9 제조업/선원 환급)
    "ne": 5.0,   # 네팔 (E-9 성실 근로자)
    "km": 4.0,   # 캄보디아 (E-9 농축산/제조업)
    "mn": 4.0,   # 몽골 (유학생 알바 소득세 환급)
    "my": 3.0,   # 미얀마 (E-9 근로자)
    "si": 2.5,   # 스리랑카 (E-9 근로자)
    "bn": 2.0,   # 방글라데시 (E-9 근로자)
    "kk": 1.5,   # 카자흐스탄 (근로자/유학생)
    "ur": 1.0,   # 파키스탄 (E-9 기술근로자)
    "ko": 1.0    # 한국어/다문화
}

def get_weighted_language(brand: str = "kmarket") -> str:
    """브랜드별 인구통계 가중치 기반으로 최적 언어 코드 1개 추출"""
    import random
    weights_dict = EASYTAX_LANGUAGE_WEIGHTS if brand == "easytax" else KMARKET_LANGUAGE_WEIGHTS
    langs = list(weights_dict.keys())
    weights = list(weights_dict.values())
    return random.choices(langs, weights=weights, k=1)[0]

def get_next_golden_eight_language(channel_key: str) -> str:
    """8대 황금 타깃 국가 중 다음 순환 언어 1개 추출 및 상태 영구 저장 (선불 잔액 최적화)"""
    import json
    state_file = DATA_DIR / f"golden_rotation_state_{channel_key}.json"
    curr_idx = 0
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                curr_idx = json.load(f).get("index", 0)
        except Exception:
            curr_idx = 0
    selected_lang = GOLDEN_EIGHT_LANGUAGES[curr_idx % len(GOLDEN_EIGHT_LANGUAGES)]
    next_idx = (curr_idx + 1) % len(GOLDEN_EIGHT_LANGUAGES)
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({
                "index": next_idx,
                "current_lang": selected_lang,
                "channel": channel_key,
                "updated_at": get_now_kst_str()
            }, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return selected_lang

def get_golden_rotation_info(channel_key: str) -> dict:
    """해당 채널의 현재 순환 대상 언어 정보 조회 (상태 변경 없음)"""
    import json
    state_file = DATA_DIR / f"golden_rotation_state_{channel_key}.json"
    curr_idx = 0
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                curr_idx = json.load(f).get("index", 0)
        except Exception:
            curr_idx = 0
    current_lang = GOLDEN_EIGHT_LANGUAGES[curr_idx % len(GOLDEN_EIGHT_LANGUAGES)]
    return {
        "index": curr_idx % len(GOLDEN_EIGHT_LANGUAGES),
        "total": len(GOLDEN_EIGHT_LANGUAGES),
        "current_lang": current_lang,
        "detail": GOLDEN_EIGHT_DETAILS.get(current_lang, {}),
        "all_targets": GOLDEN_EIGHT_LANGUAGES
    }

# API Keys and External Services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEY_EASYTAX = os.getenv("GEMINI_API_KEY_EASYTAX", GEMINI_API_KEY)
GEMINI_API_KEY_KMARKET = os.getenv("GEMINI_API_KEY_KMARKET", GEMINI_API_KEY)

# 🎁 전담 무료 API 키 (비용 0원 최적화)
GEMINI_API_KEY_KMARKET_BLOG = os.getenv("GEMINI_API_KEY_KMARKET_BLOG") or GEMINI_API_KEY_KMARKET
GEMINI_API_KEY_EASYTAX_BLOG = os.getenv("GEMINI_API_KEY_EASYTAX_BLOG") or GEMINI_API_KEY_EASYTAX
GEMINI_FREE_API_KEY_KMARKET = os.getenv("GEMINI_FREE_API_KEY_KMARKET") or GEMINI_API_KEY_KMARKET_BLOG
GEMINI_FREE_API_KEY_EASYTAX = os.getenv("GEMINI_FREE_API_KEY_EASYTAX") or GEMINI_API_KEY_EASYTAX_BLOG

# 🚀 구글 무료 GPU (Colab RealVisXL) 서버 URL
COLAB_GPU_API_URL = os.getenv("COLAB_GPU_API_URL", "")

# Supabase Settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Pexels Stock Photo API Key
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Reddit API
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "UniversalExpatGrowthBot/1.0")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

# Target Services Base URLs
BASE_URLS = {
    "kmarket": os.getenv("KMARKET_BASE_URL", "https://ktrs-market.vercel.app"),
    "easytax": os.getenv("EASYTAX_BASE_URL", "https://ktrs-service.vercel.app"),
    "ktelecom": os.getenv("KTELECOM_BASE_URL", "https://k-telecom.app"),
    "loan": os.getenv("LOAN_BASE_URL", "https://expat-loan.app"),
    "housing": os.getenv("HOUSING_BASE_URL", "https://expat-housing.app"),
    "remit": os.getenv("REMIT_BASE_URL", "https://global-remit.app"),
}

# Autopilot & Anti-Ban Safety Parameters
AUTOPILOT_MODE = os.getenv("AUTOPILOT_MODE", "1") == "1"
REDDIT_AUTO_REPLY = os.getenv("REDDIT_AUTO_REPLY", "1") == "1"

# 🛡️ 안전 레딧 파라미터 (영구 정지 방지 — 2026.08 전면 재설계)
DAILY_REDDIT_PROMO_LIMIT = int(os.getenv("DAILY_REDDIT_PROMO_LIMIT", "2"))       # 홍보성 댓글 일일 최대 (절대 초과 금지)
DAILY_REDDIT_ORGANIC_LIMIT = int(os.getenv("DAILY_REDDIT_ORGANIC_LIMIT", "8"))   # 비홍보 댓글 일일 최대
DAILY_REDDIT_UPVOTE_LIMIT = int(os.getenv("DAILY_REDDIT_UPVOTE_LIMIT", "20"))    # 업보트 일일 최대
HOURLY_REDDIT_LIMIT = int(os.getenv("HOURLY_REDDIT_LIMIT", "1"))                 # 시간당 최대 홍보 댓글
REPLY_DELAY_MIN_SEC = int(os.getenv("REPLY_DELAY_MIN_SEC", "600"))               # 홍보 댓글 간 최소 간격 10분
REPLY_DELAY_MAX_SEC = int(os.getenv("REPLY_DELAY_MAX_SEC", "1800"))              # 홍보 댓글 간 최대 간격 30분
ORGANIC_DELAY_MIN_SEC = int(os.getenv("ORGANIC_DELAY_MIN_SEC", "120"))           # 유기적 활동 간 최소 간격 2분
ORGANIC_DELAY_MAX_SEC = int(os.getenv("ORGANIC_DELAY_MAX_SEC", "480"))           # 유기적 활동 간 최대 간격 8분
WARMUP_KARMA_THRESHOLD = int(os.getenv("WARMUP_KARMA_THRESHOLD", "100"))         # 이 카르마 이하면 홍보 댓글 0건

# 하위 호환성 유지 (기존 코드가 참조하는 변수명)
DAILY_REDDIT_LIMIT = DAILY_REDDIT_PROMO_LIMIT

# SQLite Database Path
DB_PATH = DATA_DIR / "history.db"
