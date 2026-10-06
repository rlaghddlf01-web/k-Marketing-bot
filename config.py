import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

KST = datetime.timezone(datetime.timedelta(hours=9))

def get_now_kst() -> datetime.datetime:
    return datetime.datetime.now(KST)

def get_now_kst_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return get_now_kst().strftime(fmt)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

(OUTPUTS_DIR / "shorts").mkdir(exist_ok=True)
(OUTPUTS_DIR / "cardnews").mkdir(exist_ok=True)
(OUTPUTS_DIR / "threads").mkdir(exist_ok=True)
(OUTPUTS_DIR / "pdf_guides").mkdir(exist_ok=True)
(OUTPUTS_DIR / "briefings").mkdir(exist_ok=True)
(OUTPUTS_DIR / "logs").mkdir(exist_ok=True)
(OUTPUTS_DIR / "seo_pages").mkdir(exist_ok=True)

def get_real_desktop_dir() -> Path:
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        val, _ = winreg.QueryValueEx(k, "Desktop")
        val_expanded = os.path.expandvars(val)
        if os.path.exists(val_expanded):
            return Path(val_expanded)
    except Exception:
        pass
    userprofile = os.environ.get("USERPROFILE", r"C:\Users\zkfnt")
    onedrive_dt = Path(userprofile) / "OneDrive" / "Desktop"
    if onedrive_dt.exists():
        return onedrive_dt
    return Path(userprofile) / "Desktop"

DESKTOP_DIR = get_real_desktop_dir()

DESKTOP_CARDNEWS_DIR = DESKTOP_DIR / "카드뉴스_산출물"
DESKTOP_SHORTS_DIR = DESKTOP_DIR / "숏폼_산출물"
DESKTOP_THREADS_DIR = DESKTOP_DIR / "스레드_산출물"

DESKTOP_CARDNEWS_KMARKET = DESKTOP_CARDNEWS_DIR / "케이마켓"
DESKTOP_CARDNEWS_EASYTAX = DESKTOP_CARDNEWS_DIR / "이지텍스"

DESKTOP_SHORTS_KMARKET = DESKTOP_SHORTS_DIR / "케이마켓"
DESKTOP_SHORTS_EASYTAX = DESKTOP_SHORTS_DIR / "이지텍스"

DESKTOP_THREADS_KMARKET = DESKTOP_THREADS_DIR / "케이마켓"
DESKTOP_THREADS_EASYTAX = DESKTOP_THREADS_DIR / "이지텍스"

for d in [
    DESKTOP_CARDNEWS_DIR, DESKTOP_SHORTS_DIR, DESKTOP_THREADS_DIR,
    DESKTOP_CARDNEWS_KMARKET, DESKTOP_CARDNEWS_EASYTAX,
    DESKTOP_SHORTS_KMARKET, DESKTOP_SHORTS_EASYTAX,
    DESKTOP_THREADS_KMARKET, DESKTOP_THREADS_EASYTAX
]:
    d.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

COMFY_HOST = os.environ.get("COMFY_HOST", "http://192.168.0.29:8188").strip().rstrip("/")
COMFY_LOCAL_DIR = Path(os.environ.get("COMFY_LOCAL_DIR", r"D:\ComfyUI_Wan_Engine"))

KMARKET_LANGUAGES = [
    "ko", "vi", "zh", "en", "ja", "ru", "th", "uz", 
    "km", "mn", "ne", "id", "my", "si", "kk", "bn", "ur"
]

EASYTAX_LANGUAGES = [
    "ko", "vi", "zh", "km", "ne", "uz", "my", "id", 
    "th", "en", "si", "mn", "bn", "kk", "ur"
]

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

LANGUAGES = {
    "ko": {"name": "Korean", "native_name": "한국어", "voice": "ko-KR-SunHiNeural", "target": "국내 거주 다문화 및 외국인 공통"},
    "vi": {"name": "Vietnamese", "native_name": "Tiếng Việt", "voice": "vi-VN-HoaiMyNeural", "target": "전국 대학 유학생(1위), 제조업/농축산업 근로자"},
    "zh": {"name": "Chinese", "native_name": "中文", "voice": "zh-CN-XiaoxiaoNeural", "target": "국내 유학생, 어학당, 체류 교민"},
    "en": {"name": "English", "native_name": "English", "voice": "en-US-JennyNeural", "target": "교환학생, 원어민 강사, 주한미군, 글로벌 IT 직장인 및 필리핀 커뮤니티"},
    "ja": {"name": "Japanese", "native_name": "日本語", "voice": "ja-JP-NanamiNeural", "target": "교환학생 및 국내 거주 일본인 (KTRS 마켓 전용)"},
    "ru": {"name": "Russian", "native_name": "Русский", "voice": "ru-RU-SvetlanaNeural", "target": "중앙아시아 고려인 및 러시아어권 체류자 (KTRS 마켓 전용)"},
    "th": {"name": "Thai", "native_name": "ไทย", "voice": "th-TH-PremwadeeNeural", "target": "전국 산업 단지 및 문화 교류자"},
    "uz": {"name": "Uzbek", "native_name": "O'zbek", "voice": "uz-UZ-MadinaNeural", "target": "이태원, 광주, 평택 등 우즈벡 유학생/근로자"},
    "km": {"name": "Khmer", "native_name": "ភាសាខ្មែរ", "voice": "km-KH-SreymomNeural", "target": "제조업/농축산업 근로자"},
    "mn": {"name": "Mongolian", "native_name": "Монгол", "voice": "mn-MN-YesuiNeural", "target": "안산, 수원, 동대문 거주 몽골인 커뮤니티"},
    "ne": {"name": "Nepali", "native_name": "नेपाली", "voice": "ne-NP-HemkalaNeural", "target": "유학생 및 외국인 근로자"},
    "id": {"name": "Indonesian", "native_name": "Bahasa Indonesia", "voice": "id-ID-GadisNeural", "target": "해양/제조업 근로자 및 유학생"},
    "my": {"name": "Burmese", "native_name": "မြန်မာ", "voice": "my-MM-NilarNeural", "target": "어학당 및 유학생"},
    "si": {"name": "Sinhala", "native_name": "සිංහල", "voice": "si-LK-ThiliniNeural", "target": "스리랑카 근로자 및 유학생"},
    "kk": {"name": "Kazakh", "native_name": "Қазақша", "voice": "kk-KZ-AigulNeural", "target": "카자흐스탄 유학생 및 중앙아시아 근로자"},
    "bn": {"name": "Bengali", "native_name": "বাংলা", "voice": "bn-BD-NabanitaNeural", "target": "방글라데시 유학생/연구원/근로자"},
    "ur": {"name": "Urdu", "native_name": "اردو", "voice": "ur-PK-UzmaNeural", "target": "파키스탄 기술인력 및 유학생/근로자"}
}

KMARKET_LANGUAGE_WEIGHTS = {
    "zh": 23.0, "vi": 22.0, "en": 14.0, "uz": 8.0,
    "mn": 6.0, "ru": 5.0, "th": 3.0, "id": 3.0,
    "ja": 3.0, "ne": 2.0, "km": 2.0, "my": 2.0,
    "si": 2.0, "kk": 1.5, "bn": 1.5, "ur": 1.0, "ko": 1.0
}

EASYTAX_LANGUAGE_WEIGHTS = {
    "vi": 26.0, "uz": 15.0, "zh": 13.0, "en": 8.0,
    "th": 8.0, "id": 6.0, "ne": 5.0, "km": 4.0,
    "mn": 4.0, "my": 3.0, "si": 2.5, "bn": 2.0,
    "kk": 1.5, "ur": 1.0, "ko": 1.0
}

def get_weighted_language(brand: str = "kmarket") -> str:
    import random
    weights_dict = EASYTAX_LANGUAGE_WEIGHTS if brand == "easytax" else KMARKET_LANGUAGE_WEIGHTS
    langs = list(weights_dict.keys())
    weights = list(weights_dict.values())
    return random.choices(langs, weights=weights, k=1)[0]

def get_next_golden_eight_language(channel_key: str) -> str:
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

# 🛸 통합 Gemini 키 풀 (무료 1~4번 순차호출 -> 유료 1~2번 순차호출)
GEMINI_FREE_KEY_1 = os.getenv("GEMINI_FREE_KEY_1", "")
GEMINI_FREE_KEY_2 = os.getenv("GEMINI_FREE_KEY_2", "")
GEMINI_FREE_KEY_3 = os.getenv("GEMINI_FREE_KEY_3", "")
GEMINI_FREE_KEY_4 = os.getenv("GEMINI_FREE_KEY_4", "")

GEMINI_PAID_KEY_1 = os.getenv("GEMINI_PAID_KEY_1", "")
GEMINI_PAID_KEY_2 = os.getenv("GEMINI_PAID_KEY_2", "")

GEMINI_FREE_KEYS = [k for k in [GEMINI_FREE_KEY_1, GEMINI_FREE_KEY_2, GEMINI_FREE_KEY_3, GEMINI_FREE_KEY_4] if k]
GEMINI_PAID_KEYS = [k for k in [GEMINI_PAID_KEY_1, GEMINI_PAID_KEY_2] if k]

# 레거시 하위 호환
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", GEMINI_PAID_KEY_1)
GEMINI_API_KEY_EASYTAX = os.getenv("GEMINI_API_KEY_EASYTAX", GEMINI_PAID_KEY_1)
GEMINI_API_KEY_KMARKET = os.getenv("GEMINI_API_KEY_KMARKET", GEMINI_PAID_KEY_2)
GEMINI_API_KEY_KMARKET_BLOG = os.getenv("GEMINI_API_KEY_KMARKET_BLOG") or GEMINI_FREE_KEY_1
GEMINI_API_KEY_EASYTAX_BLOG = os.getenv("GEMINI_API_KEY_EASYTAX_BLOG") or GEMINI_FREE_KEY_2
GEMINI_FREE_API_KEY_KMARKET = os.getenv("GEMINI_FREE_API_KEY_KMARKET") or GEMINI_FREE_KEY_1
GEMINI_FREE_API_KEY_EASYTAX = os.getenv("GEMINI_FREE_API_KEY_EASYTAX") or GEMINI_FREE_KEY_2
GEMINI_FREE_API_KEY_EXTRA = os.getenv("GEMINI_FREE_API_KEY_EXTRA") or GEMINI_FREE_KEY_3

COLAB_GPU_API_URL = os.getenv("COLAB_GPU_API_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "UniversalExpatGrowthBot/1.0")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

BASE_URLS = {
    "kmarket": os.getenv("KMARKET_BASE_URL", "https://ktrs-market.vercel.app"),
    "easytax": os.getenv("EASYTAX_BASE_URL", "https://ktrs-service.vercel.app"),
    "ktelecom": os.getenv("KTELECOM_BASE_URL", "https://k-telecom.app"),
    "loan": os.getenv("LOAN_BASE_URL", "https://expat-loan.app"),
    "housing": os.getenv("HOUSING_BASE_URL", "https://expat-housing.app"),
    "remit": os.getenv("REMIT_BASE_URL", "https://global-remit.app"),
}

AUTOPILOT_MODE = os.getenv("AUTOPILOT_MODE", "1") == "1"
REDDIT_AUTO_REPLY = os.getenv("REDDIT_AUTO_REPLY", "1") == "1"

DAILY_REDDIT_PROMO_LIMIT = int(os.getenv("DAILY_REDDIT_PROMO_LIMIT", "2"))
DAILY_REDDIT_ORGANIC_LIMIT = int(os.getenv("DAILY_REDDIT_ORGANIC_LIMIT", "8"))
DAILY_REDDIT_UPVOTE_LIMIT = int(os.getenv("DAILY_REDDIT_UPVOTE_LIMIT", "20"))
HOURLY_REDDIT_LIMIT = int(os.getenv("HOURLY_REDDIT_LIMIT", "1"))
REPLY_DELAY_MIN_SEC = int(os.getenv("REPLY_DELAY_MIN_SEC", "600"))
REPLY_DELAY_MAX_SEC = int(os.getenv("REPLY_DELAY_MAX_SEC", "1800"))
ORGANIC_DELAY_MIN_SEC = int(os.getenv("ORGANIC_DELAY_MIN_SEC", "120"))
ORGANIC_DELAY_MAX_SEC = int(os.getenv("ORGANIC_DELAY_MAX_SEC", "480"))
WARMUP_KARMA_THRESHOLD = int(os.getenv("WARMUP_KARMA_THRESHOLD", "100"))

DAILY_REDDIT_LIMIT = DAILY_REDDIT_PROMO_LIMIT
DB_PATH = DATA_DIR / "history.db"
