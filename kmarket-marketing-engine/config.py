import os
from pathlib import Path
from dotenv import load_dotenv

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

# 17 Languages & Edge-TTS Voice Mapping
LANGUAGES = {
    "ko": {
        "name": "Korean",
        "native_name": "한국어",
        "voice": "ko-KR-SunHiNeural",
        "target": "국내 거주 다문화 및 외국인 공통"
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "voice": "en-US-JennyNeural",
        "target": "교환학생, 원어민 강사, 주한미군, 글로벌 IT 직장인"
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
    "mn": {
        "name": "Mongolian",
        "native_name": "Монгол",
        "voice": "mn-MN-YesuiNeural",
        "target": "안산, 수원, 동대문 거주 몽골인 커뮤니티"
    },
    "uz": {
        "name": "Uzbek",
        "native_name": "O'zbek",
        "voice": "uz-UZ-MadinaNeural",
        "target": "이태원, 광주, 평택 등 우즈벡 유학생/근로자"
    },
    "ru": {
        "name": "Russian",
        "native_name": "Русский",
        "voice": "ru-RU-SvetlanaNeural",
        "target": "중앙아시아 고려인 및 러시아어권 체류자"
    },
    "th": {
        "name": "Thai",
        "native_name": "ไทย",
        "voice": "th-TH-PremwadeeNeural",
        "target": "전국 산업 단지 및 문화 교류자"
    },
    "id": {
        "name": "Indonesian",
        "native_name": "Bahasa Indonesia",
        "voice": "id-ID-GadisNeural",
        "target": "해양/제조업 근로자 및 유학생"
    },
    "km": {
        "name": "Khmer",
        "native_name": "ភាសាខ្មែរ",
        "voice": "km-KH-SreymomNeural",
        "target": "제조업/농축산업 근로자"
    },
    "ne": {
        "name": "Nepali",
        "native_name": "नेपाली",
        "voice": "ne-NP-HemkalaNeural",
        "target": "유학생 및 외국인 근로자"
    },
    "my": {
        "name": "Burmese",
        "native_name": "မြန်မာ",
        "voice": "my-MM-NilarNeural",
        "target": "어학당 및 유학생"
    },
    "ja": {
        "name": "Japanese",
        "native_name": "日本語",
        "voice": "ja-JP-NanamiNeural",
        "target": "교환학생 및 국내 거주 일본인"
    },
    "tl": {
        "name": "Tagalog",
        "native_name": "Filipino",
        "voice": "fil-PH-BlessicaNeural",
        "target": "영어 강사 및 유학생"
    },
    "bn": {
        "name": "Bengali",
        "native_name": "বাংলা",
        "voice": "bn-BD-NabanitaNeural",
        "target": "방글라데시 유학생/연구원"
    },
    "ar": {
        "name": "Arabic",
        "native_name": "العربية",
        "voice": "ar-SA-ZariyahNeural",
        "target": "중동 유학생 및 의료 관광객",
        "rtl": True
    },
    "es": {
        "name": "Spanish",
        "native_name": "Español",
        "voice": "es-ES-ElviraNeural",
        "target": "남미/스페인 교환학생"
    }
}

# 🎯 17개국 인구통계 & 비자 유형 기반 맞춤 가중치 (총합 100%)
KMARKET_LANGUAGE_WEIGHTS = {
    "zh": 25.0,  # 중국/중화권 (85만 유학생/거주자)
    "vi": 22.0,  # 베트남 (유학생 1위, 0원 나눔 최다 수요)
    "en": 15.0,  # 글로벌 영어 (대학가 유학생/원어민)
    "uz": 8.0,   # 우즈베키스탄 (공단/대학가 밀집)
    "mn": 7.0,   # 몽골 (수도권 대학가 0원 나눔 높은 반응)
    "ru": 5.0,   # 러시아/CIS (고려인 밀집촌)
    "th": 3.0,   # 태국
    "id": 3.0,   # 인도네시아
    "ja": 2.0,   # 일본
    "tl": 2.0,   # 필리핀
    "ne": 2.0,   # 네팔
    "km": 2.0,   # 캄보디아
    "my": 1.0,   # 미얀마
    "bn": 1.0,   # 방글라데시
    "es": 1.0,   # 스페인어권
    "ar": 0.5,   # 아랍권
    "ko": 0.5    # 한국어/다문화
}

EASYTAX_LANGUAGE_WEIGHTS = {
    "vi": 25.0,  # 베트남 (E-9 근로자 1위 + 유학생 알바 1위, 최다 환급액)
    "uz": 14.0,  # 우즈베키스탄 (E-9 제조업 90% 소득세 감면 핵심)
    "zh": 12.0,  # 중국/중화권 (F-4/H-2 및 유학생)
    "en": 8.0,   # 글로벌 영어 (원어민 강사/IT 전문직 5개년 경정청구)
    "th": 8.0,   # 태국 (E-9 근로자 퇴직금/소득세 환급)
    "ru": 7.0,   # 러시아/CIS (고려인 및 공단 근로자)
    "id": 6.0,   # 인도네시아 (E-9 제조업/선원 환급)
    "ne": 5.0,   # 네팔 (E-9 성실 근로자)
    "tl": 3.0,   # 필리핀 (E-9 및 전문인력)
    "km": 3.0,   # 캄보디아 (E-9 농축산/제조업)
    "mn": 4.0,   # 몽골 (유학생 알바 소득세 환급)
    "my": 2.0,   # 미얀마 (E-9 근로자)
    "bn": 1.0,   # 방글라데시 (E-9 근로자)
    "ja": 0.5,   # 일본
    "es": 0.5,   # 스페인어권
    "ar": 0.5,   # 아랍권
    "ko": 0.5    # 한국어/다문화
}

def get_weighted_language(brand: str = "kmarket") -> str:
    """브랜드별 인구통계 가중치 기반으로 최적 언어 코드 1개 추출"""
    import random
    weights_dict = EASYTAX_LANGUAGE_WEIGHTS if brand == "easytax" else KMARKET_LANGUAGE_WEIGHTS
    langs = list(weights_dict.keys())
    weights = list(weights_dict.values())
    return random.choices(langs, weights=weights, k=1)[0]

# API Keys and External Services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEY_EASYTAX = os.getenv("GEMINI_API_KEY_EASYTAX", GEMINI_API_KEY)
GEMINI_API_KEY_KMARKET = os.getenv("GEMINI_API_KEY_KMARKET", GEMINI_API_KEY)

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
    "kmarket": os.getenv("KMARKET_BASE_URL", "https://k-market.app"),
    "easytax": os.getenv("EASYTAX_BASE_URL", "https://easy-tax.app"),
    "ktelecom": os.getenv("KTELECOM_BASE_URL", "https://k-telecom.app"),
    "loan": os.getenv("LOAN_BASE_URL", "https://expat-loan.app"),
    "housing": os.getenv("HOUSING_BASE_URL", "https://expat-housing.app"),
    "remit": os.getenv("REMIT_BASE_URL", "https://global-remit.app"),
}

# Autopilot & Anti-Ban Safety Parameters
AUTOPILOT_MODE = os.getenv("AUTOPILOT_MODE", "1") == "1"
REDDIT_AUTO_REPLY = os.getenv("REDDIT_AUTO_REPLY", "1") == "1"
REPLY_DELAY_MIN_SEC = int(os.getenv("REPLY_DELAY_MIN_SEC", "180"))
REPLY_DELAY_MAX_SEC = int(os.getenv("REPLY_DELAY_MAX_SEC", "420"))
DAILY_REDDIT_LIMIT = int(os.getenv("DAILY_REDDIT_LIMIT", "20"))
HOURLY_REDDIT_LIMIT = int(os.getenv("HOURLY_REDDIT_LIMIT", "3"))

# SQLite Database Path
DB_PATH = DATA_DIR / "history.db"
