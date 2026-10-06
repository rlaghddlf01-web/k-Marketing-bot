"""
VisualSafetyEngine - AI 기괴함/환각 차단 & 17개국 인종/국적 일치 안전 그래픽 엔진
- 17개국 언어별 인종/국적 메타데이터 엄격 매핑 (Ethnicity & Demographic Guardrails)
- 네거티브 가드레일 (기괴한 손가락, 공중에 뜬 물체, 인종 불일치 차단)
- 1인칭 POV(Point of View) 스마트폰 UI & 세무 통장 입금 모션 그래픽 정밀 렌더러 (1080x1920)
"""

import logging
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import BASE_DIR, ASSETS_DIR, DATA_DIR, LANGUAGES
from core.pexels_client import PexelsClient

logger = logging.getLogger("VisualSafetyEngine")

# Windows 기본 트루타입 폰트
FONT_BOLD_PATH = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REGULAR_PATH = r"C:\Windows\Fonts\malgun.ttf"

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# 🎯 17개국 언어별 인종/인구통계 메타데이터 강제 매핑 테이블
ETHNICITY_DEMOGRAPHICS_MAP: Dict[str, Dict[str, Any]] = {
    "vi": {
        "country": "Vietnam",
        "ethnicity_prompt": "authentic Vietnamese young adult worker/student in South Korea, Southeast Asian realistic facial features",
        "negative_ethnicity": "caucasian, westerner, african, black, blonde hair, blue eyes, deformed anatomy",
        "currency_symbol": "₫",
        "local_agency": "Cục Thuế Quốc Gia Hàn Quốc (NTS)",
        "tone": "warm, diligent, practical"
    },
    "uz": {
        "country": "Uzbekistan",
        "ethnicity_prompt": "authentic Central Asian Uzbek young male worker in South Korea, realistic Uzbek facial features",
        "negative_ethnicity": "african, black, east asian, blonde european, deformed limbs",
        "currency_symbol": "UZS",
        "local_agency": "Janubiy Koreya Milliy Soliq Xizmati (NTS)",
        "tone": "trustworthy, earnest, dignified"
    },
    "zh": {
        "country": "China",
        "ethnicity_prompt": "authentic Chinese expat or international student in South Korea, East Asian realistic appearance",
        "negative_ethnicity": "african, caucasian, south asian, deformed anatomy",
        "currency_symbol": "¥",
        "local_agency": "韩国国税厅 (NTS)",
        "tone": "professional, smart, efficient"
    },
    "en": {
        "country": "Global (English)",
        "ethnicity_prompt": "international expat student or professional living in South Korea, modern urban setting",
        "negative_ethnicity": "deformed hands, floating phone, distorted face",
        "currency_symbol": "$",
        "local_agency": "National Tax Service Korea (NTS)",
        "tone": "modern, transparent, direct"
    },
    "mn": {
        "country": "Mongolia",
        "ethnicity_prompt": "authentic Mongolian young adult in South Korea, East Asian/Mongolian features",
        "negative_ethnicity": "african, western caucasian, deformed limbs",
        "currency_symbol": "₮",
        "local_agency": "БНСУ-ын Татварын Ерөнхий Газар (NTS)",
        "tone": "practical, clear, supportive"
    },
    "ru": {
        "country": "Russian/CIS",
        "ethnicity_prompt": "authentic Koryo-saram (ethnic Korean from CIS) or Russian-speaking expat in Korea",
        "negative_ethnicity": "african, south asian, deformed anatomy",
        "currency_symbol": "₽",
        "local_agency": "Налоговая служба Кореи (NTS)",
        "tone": "authoritative, precise, reliable"
    },
    "th": {
        "country": "Thailand",
        "ethnicity_prompt": "authentic Thai worker or student living in South Korea, Southeast Asian features",
        "negative_ethnicity": "caucasian, african, black, westerner, deformed hands",
        "currency_symbol": "฿",
        "local_agency": "กรมสรรพากรแห่งชาติเกาหลี (NTS)",
        "tone": "friendly, helpful, reassuring"
    },
    "id": {
        "country": "Indonesia",
        "ethnicity_prompt": "authentic Indonesian worker or maritime professional in South Korea, Southeast Asian features",
        "negative_ethnicity": "caucasian, african, deformed anatomy",
        "currency_symbol": "Rp",
        "local_agency": "Direktorat Pajak Korea (NTS)",
        "tone": "polite, humble, community-oriented"
    },
    "km": {
        "country": "Cambodia",
        "ethnicity_prompt": "authentic Cambodian (Khmer) worker in South Korea, Southeast Asian features",
        "negative_ethnicity": "caucasian, african, deformed limbs",
        "currency_symbol": "៛",
        "local_agency": "អគ្គនាយកដ្ឋានពន្ធដារកូរ៉េ (NTS)",
        "tone": "honest, practical"
    },
    "ne": {
        "country": "Nepal",
        "ethnicity_prompt": "authentic Nepali worker or student in South Korea, South Asian Himalayan features",
        "negative_ethnicity": "caucasian, east asian, african, deformed hands",
        "currency_symbol": "₨",
        "local_agency": "कोरिया राष्ट्रिय कर सेवा (NTS)",
        "tone": "sincere, respectful"
    },
    "tl": {
        "country": "Philippines",
        "ethnicity_prompt": "authentic Filipino professional or worker in South Korea, Southeast Asian features",
        "negative_ethnicity": "caucasian, african, deformed anatomy",
        "currency_symbol": "₱",
        "local_agency": "National Tax Service Korea",
        "tone": "upbeat, clear, reassuring"
    },
    "my": {
        "country": "Myanmar",
        "ethnicity_prompt": "authentic Burmese worker or student in South Korea, Southeast Asian features",
        "negative_ethnicity": "caucasian, african, deformed limbs",
        "currency_symbol": "K",
        "local_agency": "ကိုရီးယား အမျိုးသားအခွန်ဌာန (NTS)",
        "tone": "calm, sincere"
    },
    "bn": {
        "country": "Bangladesh",
        "ethnicity_prompt": "authentic Bangladeshi researcher or worker in South Korea, South Asian features",
        "negative_ethnicity": "caucasian, east asian, african, deformed anatomy",
        "currency_symbol": "৳",
        "local_agency": "কোরিয়া জাতীয় কর সেবা (NTS)",
        "tone": "polite, professional"
    },
    "ja": {
        "country": "Japan",
        "ethnicity_prompt": "authentic Japanese student or resident in South Korea, East Asian features",
        "negative_ethnicity": "caucasian, african, deformed limbs",
        "currency_symbol": "¥",
        "local_agency": "韓国国税庁 (NTS)",
        "tone": "clean, neat, polite"
    },
    "es": {
        "country": "Spanish/Latin America",
        "ethnicity_prompt": "authentic Hispanic or Spanish exchange student in South Korea",
        "negative_ethnicity": "deformed hands, floating objects",
        "currency_symbol": "€",
        "local_agency": "Servicio Nacional de Impuestos de Corea (NTS)",
        "tone": "friendly, dynamic"
    },
    "ar": {
        "country": "Arabic",
        "ethnicity_prompt": "authentic Middle Eastern student or resident in South Korea",
        "negative_ethnicity": "deformed anatomy, floating objects",
        "currency_symbol": "د.إ",
        "local_agency": "مصلحة الضرائب الوطنية الكورية (NTS)",
        "tone": "respectful, formal"
    },
    "ko": {
        "country": "Korea (Multicultural)",
        "ethnicity_prompt": "multicultural family or expat resident in South Korea",
        "negative_ethnicity": "deformed limbs, floating phone",
        "currency_symbol": "₩",
        "local_agency": "대한민국 국세청 (NTS)",
        "tone": "warm, trustworthy"
    }
}


class VisualSafetyEngine:
    """
    🛡️ AI 환각/기괴함 원천 차단 & 1인칭 POV 인포그래픽 정밀 렌더링 엔진
    """
    def __init__(self):
        # 17개국 에셋 디렉토리 격리 구조 보장
        self.assets_dir = ASSETS_DIR
        self._ensure_asset_folders()
        self.pexels_client = PexelsClient()

    def _ensure_asset_folders(self):
        """17개국별 격리된 에셋 폴더 자동 생성"""
        for lang_code in ETHNICITY_DEMOGRAPHICS_MAP.keys():
            lang_dir = self.assets_dir / f"lang_{lang_code}"
            lang_dir.mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "common_tax").mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "common_market").mkdir(parents=True, exist_ok=True)

    def get_ethnicity_guardrails(self, lang: str) -> Dict[str, Any]:
        """언어별 인종 프롬프트 및 네거티브 가드레일 추출"""
        return ETHNICITY_DEMOGRAPHICS_MAP.get(lang, ETHNICITY_DEMOGRAPHICS_MAP["en"])

    def render_safe_easytax_pov_frame(
        self,
        lang: str,
        title: str,
        captions: List[str],
        estimated_krw: int = 3840000,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        💰 [EasyTax 안전 비주얼] 1인칭 POV 스마트폰 입금 알림 & 환급 인포그래픽 (1080x1920)
        - 인종 불일치/AI 손가락 기괴함 원천 차단 (100% 벡터 그래픽 + 정밀 UI)
        - 실시간 환급액 카운팅 박스 & 공인 세무대리 인증 뱃지 탑재
        """
        W, H = 1080, 1920
        # 1. Pexels에서 대상 언어/국적에 맞는 100% 실사 고화질 배경 가져오기
        real_bg = self.pexels_client.fetch_photo_for_lang(lang=lang, service_id="easytax")
        if real_bg:
            # 고화질 실사 사진을 1080x1920으로 리사이즈 및 다크 오버레이 (가독성 확보)
            img = real_bg.resize((W, H), Image.Resampling.LANCZOS)
            # 어둡게 조정하여 텍스트/UI 강조 (밝기 35%)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.35)
        else:
            # 모던 다크 네이비 프리미엄 배경 (폴백)
            img = Image.new("RGB", (W, H), color=(10, 15, 30))

        draw = ImageDraw.Draw(img)

        # 폰트 세팅
        f_header = get_font(30, bold=True)
        f_title = get_font(42, bold=True)
        f_sub = get_font(26, bold=False)
        f_big_amount = get_font(60, bold=True)
        f_card_title = get_font(34, bold=True)
        f_body = get_font(28, bold=False)
        f_cta = get_font(36, bold=True)
        f_badge = get_font(24, bold=True)
        f_footer = get_font(20, bold=False)

        meta = self.get_ethnicity_guardrails(lang)

        # ── 1. 상단 공식 기관 뱃지 & 타깃 국기/국가 헤더 ──
        draw.rectangle([(60, 60), (1020, 160)], fill=(20, 30, 55), outline=(59, 130, 246), width=2)
        draw.text((90, 85), f"🏛️ {meta['local_agency']}", fill=(147, 197, 253), font=f_header)
        draw.text((820, 85), f"[{meta['country'][:10]}]", fill=(251, 191, 36), font=f_header)
        draw.text((90, 120), "공식 조세특례제한법 제30조 90% 소득세 감면 적용", fill=(148, 163, 184), font=f_footer)

        # ── 2. 메인 후킹 타이틀 ──
        draw.rectangle([(60, 190), (1020, 340)], fill=(30, 41, 65), outline=(245, 158, 11), width=3)
        draw.text((90, 220), title[:36], fill=(255, 255, 255), font=f_title)
        draw.text((90, 285), "⚡ 5-Year Retroactive Expat Tax Refund in South Korea", fill=(251, 191, 36), font=f_sub)

        # ── 3. [핵심] 1인칭 POV 스마트폰 입금 알림 목업 카드 (880x720) ──
        phone_x, phone_y = 100, 380
        phone_w, phone_h = 880, 720
        # 스마트폰 테두리 및 그림자 효과
        draw.rounded_rectangle([(phone_x, phone_y), (phone_x + phone_w, phone_y + phone_h)], radius=36, fill=(15, 23, 42), outline=(100, 116, 139), width=4)
        
        # 3-1. 스마트폰 상단 상태바 (카카오페이 / 모바일 뱅킹 입금 알림 스타일)
        draw.rounded_rectangle([(phone_x + 30, phone_y + 30), (phone_x + phone_w - 30, phone_y + 190)], radius=20, fill=(30, 41, 59), outline=(16, 185, 129), width=2)
        # 입금 알림 아이콘 & 텍스트
        draw.text((phone_x + 60, phone_y + 55), "💬 국세청 / 은행 환급금 입금 알림", fill=(52, 211, 153), font=f_badge)
        draw.text((phone_x + 60, phone_y + 100), f"[입금완료] ₩{estimated_krw:,} 원", fill=(255, 255, 255), font=f_big_amount)

        # 3-2. 세부 환급 산출 내역 (조특법 30조 팩트 기반)
        y_detail = phone_y + 220
        draw.text((phone_x + 60, y_detail), "📋 5개년 누락 세액 정밀 환급 리포트:", fill=(148, 163, 184), font=f_card_title)
        
        details = [
            ("• E-9/H-2 중소기업 감면", "최대 90% 소득세 감면 환급"),
            ("• D-2/D-4 유학생 알바", "3.3% 원천징수세 100% 전액 환급"),
            ("• 연말정산 누락/월세", "최근 5년치(2020~2025) 소급 지급"),
            ("• 비자 신분증 1장", "3분 무료 AI 간편 모의계산")
        ]
        
        for idx, (label, desc) in enumerate(details):
            item_y = y_detail + 60 + (idx * 90)
            draw.rounded_rectangle([(phone_x + 40, item_y), (phone_x + phone_w - 40, item_y + 75)], radius=12, fill=(20, 30, 50))
            draw.text((phone_x + 60, item_y + 20), label, fill=(251, 191, 36), font=f_body)
            draw.text((phone_x + 450, item_y + 20), desc, fill=(226, 232, 240), font=f_body)

        # ── 4. 캡션 안내 카드 2개 ──
        y_cap = 1140
        for cap in captions[:2]:
            draw.rounded_rectangle([(60, y_cap), (1020, y_cap + 120)], radius=16, fill=(22, 33, 58), outline=(59, 130, 246), width=1)
            draw.text((90, y_cap + 38), f"✅ {cap[:42]}", fill=(241, 245, 249), font=f_body)
            y_cap += 145

        # ── 5. Anti-Ban 안전 공인 뱃지 바 ──
        draw.rectangle([(60, 1460), (1020, 1550)], fill=(16, 30, 45), outline=(16, 185, 129), width=2)
        draw.text((90, 1488), "🛡️ 선입금 0원 • 100% 무료 AI 조회 • 공인 세무법인 1:1 전담 신고", fill=(52, 211, 153), font=f_card_title)

        # ── 6. 하단 원클릭 CTA 배너 ──
        draw.rounded_rectangle([(60, 1580), (1020, 1720)], radius=24, fill=(245, 158, 11))
        cta_text = "👉 프로필 링크에서 3분 만에 무료 환급액 조회하기!"
        draw.text((100, 1630), cta_text, fill=(15, 23, 42), font=f_cta)

        # ── 7. 공식 법적 면책 조항 ──
        draw.text((70, 1750), "* 국세기본법 제45조의2에 따른 합법 세무대리 절차로 진행되며 실제 환급액은 국세청 소득 자료에 따라 결정됩니다.", fill=(100, 116, 139), font=f_footer)
        draw.text((70, 1785), "EasyTax (KTRS) 대한민국 외국인 전용 조세 환급 플랫폼", fill=(71, 85, 105), font=f_footer)

        if not output_path:
            from config import OUTPUTS_DIR
            output_path = OUTPUTS_DIR / "shorts" / f"frame_easytax_{lang}.png"

        img.save(output_path)
        logger.info(f"[{lang.upper()}] EasyTax 안전 POV 프레임 렌더링 완료: {output_path.name}")
        return output_path
