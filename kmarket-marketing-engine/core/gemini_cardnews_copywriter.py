"""
GeminiCardnewsCopywriter - ✍️ [세계 최고 바이럴 카드뉴스 마케팅 거장 카피라이터 엔진]
- 17개국 전 언어로 1~5장 카드뉴스 뱃지/타이틀/서브타이틀/3줄 불릿 실시간 100% 원어민 직작문
- EasyTax & K-Market 공통 지원 (제미나이 이미지 모드 & 무료 GPU 모드 모두 적용)
- 글자 깨짐(□□) 방지를 위한 유니코드 안전 텍스트 정제
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY_EASYTAX, GEMINI_API_KEY_KMARKET, LANGUAGES

logger = logging.getLogger("GeminiCardnewsCopywriter")


class GeminiCardnewsCopywriter:
    """제미나이 기반 17개국 5장 카드뉴스 카피라이팅 전담 엔진"""
    def __init__(self, service_id: str = "easytax"):
        self.service_id = service_id
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        try:
            from core.gemini_smart_client import GeminiSmartClient
            self.client = GeminiSmartClient(service_id=self.service_id)
            logger.info(f"[{self.service_id.upper()}] 제미나이 카드뉴스 스마트 카피라이터 초기화 성공 (무료키 1순위)")
        except Exception as e:
            logger.warning(f"제미나이 스마트 클라이언트 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        """폰트 깨짐을 유발하는 비표준 특수 이모지 제거 및 표준 기호 정제"""
        if not text:
            return ""
        # 4바이트 이상의 특수 이모지 제거 (기본 폰트에서 □로 깨지는 현상 방지)
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        cleaned = emoji_pattern.sub("", text)
        return cleaned.strip()

    def generate_easytax_copy(
        self,
        lang: str,
        theme: Dict[str, Any],
        persona: Dict[str, Any],
        refund_formatted: str
    ) -> List[Dict[str, Any]]:
        """EasyTax 5단계 감동 카드뉴스 카피라이팅 (100% 타깃 현지어 직작문)"""
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_name = theme.get("name", "세금 환급")
        target = theme.get("target", "외국인 근로자")

        if not self.client:
            return self._fallback_easytax_copy(lang, theme, refund_formatted)

        prompt = f"""
너는 세계 최고의 바이럴 카드뉴스 마케팅 거장 카피라이터야.
네 카피는 인스타그램, 페이스북, 레딧에서 첫 1초 만에 독자의 시선을 멈추고 끝까지 넘겨보게 만들지.

### 미션:
한국에 거주하는 외국인({target})을 위해, 한국 국세청(NTS) 세금 환급 5장 카드뉴스 텍스트를 100% 자연스러운 [{lang_info['name']} ({lang_info['native_name']})] 구어체로 직접 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target})
[환급 예상액]: {refund_formatted} KRW (대한민국 국세청 조특법 30조 90% 소득세 감면)
[주인공 페르소나]: {persona.get('visa_name', '외국인 근로자')}

### 5장 슬라이드 감동 스토리텔링 공식 (주제: [{theme_name}] 사연을 바탕으로 영화처럼 몰입감 있게 집필):
- 1장 (실제 입금 인증 훅): 국세청에서 {refund_formatted} KRW 환급금이 본인 스마트폰 통장으로 실제 입금 완료되었다는 강력한 팩트 후킹!
- 2장 (주인공의 진짜 사연 & 공감): {theme_name}의 구체적인 상황 (예: 타지에서 땀 흘려 일하는 고생, 고향 부모님 걱정, 비행기표 티켓값 부담, 학비 고민 등)에 깊이 공감하며 "당신도 이 돈의 정당한 주인"임을 알림.
- 3장 (★핵심 안심 보증 - 100% 후불제): "선결제/착수금 0원! 국세청 환급금이 본인 계좌에 먼저 100% 안전하게 입금된 후에만 수수료를 정산하는 완벽한 후불제 시스템! 돈을 못 받으면 수수료는 0원!"을 강력하게 어필.
- 4장 (환급금으로 이룬 감동의 꿈): 실제로 {refund_formatted} KRW를 받아 고향 부모님께 해외송금으로 효도 / 고향행 비행기표 티켓 구매 / 대학 등록금 완납 등 {theme_name}에 완벽히 부합하는 감동 실화 전개!
- 5장 (행동 촉구 CTA): "5년 지나면 국가로 귀속되어 영영 사라집니다! 지금 프로필 바이오 링크(Bio Link)를 눌러 1분 무료 조회하고 내 돈 찾아가세요!"

### 필수 출력 규칙:
1. 반드시 순수한 [{lang_info['name']}] 언어로만 작성할 것. (한국어가 섞이지 않게 100% 현지어로 번역/창작)
2. 폰트 깨짐을 방지하기 위해 특수 이모지는 쓰지 말고, 불릿 기호는 표준 '•' 또는 '1.', '2.', '3.'을 사용할 것.
3. 아래 JSON 형식으로만 정확히 출력할 것:

[
  {{
    "slide_idx": 1,
    "badge": "STEP 1: BADGE IN {lang_info['name']}",
    "title": "Slide 1 Punchy Title with {refund_formatted} in {lang_info['name']}",
    "subtitle": "Slide 1 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 2,
    "badge": "STEP 2: BADGE IN {lang_info['name']}",
    "title": "Slide 2 Eligibility Title in {lang_info['name']}",
    "subtitle": "Slide 2 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 3,
    "badge": "STEP 3: BADGE IN {lang_info['name']}",
    "title": "Slide 3 Zero Fee & Trust Title in {lang_info['name']}",
    "subtitle": "Slide 3 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 4,
    "badge": "STEP 4: BADGE IN {lang_info['name']}",
    "title": "Slide 4 Dream & Life Title in {lang_info['name']}",
    "subtitle": "Slide 4 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 5,
    "badge": "STEP 5: BADGE IN {lang_info['name']}",
    "title": "Slide 5 CTA Title in {lang_info['name']}",
    "subtitle": "Slide 5 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }}
]
"""
        try:
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            raw_text = response.text.strip()
            # JSON 파싱
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            cards = json.loads(raw_text)
            if isinstance(cards, list) and len(cards) == 5:
                # 텍스트 안전 정제
                for c in cards:
                    c["badge"] = self._clean_text(c.get("badge", ""))
                    c["title"] = self._clean_text(c.get("title", ""))
                    c["subtitle"] = self._clean_text(c.get("subtitle", ""))
                    c["bullets"] = [self._clean_text(b) for b in c.get("bullets", [])]
                logger.info(f"[{lang.upper()}] 🎉 제미나이 100% 현지어 카드뉴스 카피라이팅 성공!")
                return cards
        except Exception as e:
            logger.warning(f"[{lang.upper()}] 제미나이 카피라이팅 실패, 폴백 사용: {e}")

        return self._fallback_easytax_copy(lang, theme, refund_formatted)

    def generate_kmarket_copy(
        self,
        lang: str,
        theme: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """K-Market 5단계 감동 카드뉴스 카피라이팅 (100% 타깃 현지어 직작문)"""
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_name = theme.get("name", "0원 나눔")
        target = theme.get("target", "대학가/원룸")
        item = theme.get("item", "가구/가전")

        if not self.client:
            return self._fallback_kmarket_copy(lang, theme)

        prompt = f"""
너는 세계 최고의 바이럴 카드뉴스 마케팅 거장 카피라이터야.
네 카피는 인스타그램, 페이스북, 레딧에서 첫 1초 만에 독자의 시선을 멈추고 앱 다운로드로 이끌지.

### 미션:
한국에 거주하는 외국인 유학생 및 근로자({target})를 위해, K-Market 0원 무료 나눔 5장 카드뉴스 텍스트를 100% 자연스러운 [{lang_info['name']} ({lang_info['native_name']})] 구어체로 직접 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target})
[무료 품목]: {item} (귀국 선배들이 남긴 A급 가구/가전 100% 무료 나눔)
[주인공 페르소나]: {persona.get('name', '외국인 유학생')}

### 5장 슬라이드 스토리텔링 공식 (반드시 이 순서로 집필):
- 1장 (실물 직거래 수령 득템): 캠퍼스/길거리에서 1:1로 {item}을 0원에 무료로 직접 건네받은 생생한 실화 후킹!
- 2장 (내 방 배치 & 아늑한 행복): 텅 비고 차가웠던 원룸/기숙사를 0원 가구로 따뜻하고 아늑하게 풀세팅한 감동
- 3장 (150만원 절약 & 학비 해결): 가구값 150만 원을 아껴서 대학교 등록금이나 생활비에 보탠 경제적 이득
- 4장 (K-Market 앱 & 17개국어 번역): "한국어 몰라도 17개 언어 실시간 자동번역 채팅으로 내 동네 0원 매물 1초 확인!"
- 5장 (행동 촉구 CTA): "오늘 등록된 0원 매물 놓치지 마세요! 지금 프로필 링크(Bio Link)를 눌러 K-Market 앱을 다운로드하세요!"

### 필수 출력 규칙:
1. 반드시 순수한 [{lang_info['name']}] 언어로만 작성할 것. (한국어가 섞이지 않게 100% 현지어로 번역/창작)
2. 폰트 깨짐을 방지하기 위해 특수 이모지는 쓰지 말고, 불릿 기호는 표준 '•' 또는 '1.', '2.', '3.'을 사용할 것.
3. 아래 JSON 형식으로만 정확히 출력할 것:

[
  {{
    "slide_idx": 1,
    "badge": "STEP 1: BADGE IN {lang_info['name']}",
    "title": "Slide 1 Free {item} Title in {lang_info['name']}",
    "subtitle": "Slide 1 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 2,
    "badge": "STEP 2: BADGE IN {lang_info['name']}",
    "title": "Slide 2 Cozy Room Title in {lang_info['name']}",
    "subtitle": "Slide 2 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 3,
    "badge": "STEP 3: BADGE IN {lang_info['name']}",
    "title": "Slide 3 Save 1.5M KRW Title in {lang_info['name']}",
    "subtitle": "Slide 3 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 4,
    "badge": "STEP 4: BADGE IN {lang_info['name']}",
    "title": "Slide 4 17-Language Chat Title in {lang_info['name']}",
    "subtitle": "Slide 4 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }},
  {{
    "slide_idx": 5,
    "badge": "STEP 5: BADGE IN {lang_info['name']}",
    "title": "Slide 5 App Download CTA in {lang_info['name']}",
    "subtitle": "Slide 5 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ]
  }}
]
"""
        try:
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            cards = json.loads(raw_text)
            if isinstance(cards, list) and len(cards) == 5:
                for c in cards:
                    c["badge"] = self._clean_text(c.get("badge", ""))
                    c["title"] = self._clean_text(c.get("title", ""))
                    c["subtitle"] = self._clean_text(c.get("subtitle", ""))
                    c["bullets"] = [self._clean_text(b) for b in c.get("bullets", [])]
                logger.info(f"[{lang.upper()}] 🎉 K-Market 제미나이 100% 현지어 카드뉴스 카피라이팅 성공!")
                return cards
        except Exception as e:
            logger.warning(f"[{lang.upper()}] K-Market 제미나이 카피라이팅 실패, 폴백 사용: {e}")

        return self._fallback_kmarket_copy(lang, theme)

    def _fallback_easytax_copy(self, lang: str, theme: Dict[str, Any], refund_formatted: str) -> List[Dict[str, Any]]:
        """API 장애 시 깨짐 없는 클린 영문/다국어 기본 템플릿"""
        target = theme.get("target", "Expats in Korea")
        return [
            {
                "slide_idx": 1,
                "badge": "STEP 1: TAX REFUND DEPOSITED",
                "title": f"Received {refund_formatted} Tax Refund!",
                "subtitle": "Official National Tax Service (NTS) Tax Relief",
                "bullets": [
                    f"• {refund_formatted} deposited directly into bank account",
                    "• 90% income tax reduction under Korean tax law",
                    "• 5-year retroactive retroactive tax claim"
                ]
            },
            {
                "slide_idx": 2,
                "badge": "STEP 2: CHECK YOUR ELIGIBILITY",
                "title": "Are You Eligible for Tax Refund?",
                "subtitle": f"Special Tax Relief for {target}",
                "bullets": [
                    "• E-9, E-7, H-2 factory & industrial workers",
                    "• D-2 international students with 3.3% tax withheld",
                    "• Over 95% of foreign workers qualify for refunds"
                ]
            },
            {
                "slide_idx": 3,
                "badge": "STEP 3: 100% SAFE & 0 WON UPFRONT",
                "title": "Certified Tax Agent - 0 Won Upfront Fee",
                "subtitle": "Licensed official Korean tax accounting service",
                "bullets": [
                    "• Direct Hometax National Tax Service integration",
                    "• 100% free preliminary calculation before filing",
                    "• 1:1 consultation in 17 native languages"
                ]
            },
            {
                "slide_idx": 4,
                "badge": "STEP 4: REALIZE YOUR DREAMS",
                "title": "Remittance Home & Family Support",
                "subtitle": "Rewarding your hard work and dedication in Korea",
                "bullets": [
                    f"• Send {refund_formatted} back home to your family",
                    "• Book your long-awaited round-trip flight tickets",
                    "• Pay university tuition or save for the future"
                ]
            },
            {
                "slide_idx": 5,
                "badge": "STEP 5: CLAIM YOUR MONEY NOW",
                "title": "Click The Link In Bio To Claim Now",
                "subtitle": "5-year statute of limitations expires permanently!",
                "bullets": [
                    "• Check your exact refund amount free in 1 minute",
                    "• Money transferred directly to your bank account",
                    "• Apply today before the legal deadline expires"
                ]
            }
        ]

    def _fallback_kmarket_copy(self, lang: str, theme: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 장애 시 깨짐 없는 클린 영문/다국어 기본 템플릿"""
        item = theme.get("item", "Furniture & Appliances")
        target = theme.get("target", "Campus Area")
        return [
            {
                "slide_idx": 1,
                "badge": "STEP 1: $0 FREE GIVEAWAY",
                "title": f"Get Free {item} For 0 Won!",
                "subtitle": f"100% free verified giveaway in {target}",
                "bullets": [
                    f"• High quality clean {item} left by graduating seniors",
                    "• Furnish your studio room completely for 0 Won",
                    "• Direct 1:1 pickup near your campus or station"
                ]
            },
            {
                "slide_idx": 2,
                "badge": "STEP 2: COZY BEAUTIFUL ROOM",
                "title": "Furnish Your Studio Room for 0 Won",
                "subtitle": "Transform cold empty room into a warm comfortable home",
                "bullets": [
                    f"• Clean and tested {item} in great condition",
                    "• Save hundreds of dollars on brand new items",
                    "• Enjoy a comfortable cozy living space in Korea"
                ]
            },
            {
                "slide_idx": 3,
                "badge": "STEP 3: SAVE 1,500,000 WON",
                "title": "Save 1,500,000 Won On Room Expenses",
                "subtitle": "Spend saved money on your tuition and living costs",
                "bullets": [
                    "• Zero expenses for furnishing your entire room",
                    "• Save money for university tuition and rent",
                    "• Smart budgeting for international students and expats"
                ]
            },
            {
                "slide_idx": 4,
                "badge": "STEP 4: 17-LANGUAGE CHAT",
                "title": "17-Language Auto-Translation Chat",
                "subtitle": "Trade safely even without speaking fluent Korean",
                "bullets": [
                    "• Real-time AI auto-translation in 17 native languages",
                    "• Safe direct messaging with verified local students",
                    "• Find 0 Won items closest to your room in 1 second"
                ]
            },
            {
                "slide_idx": 5,
                "badge": "STEP 5: DOWNLOAD K-MARKET APP",
                "title": "Click The Link In Bio To Get Free Items",
                "subtitle": "Check today's freshly posted 0 Won giveaways!",
                "bullets": [
                    "• Hundreds of new 0 Won items updated every day",
                    "• Trusted by over 10,000 expats and students in Korea",
                    "• Click the link in bio and claim your free item now"
                ]
            }
        ]

    def generate_cardnews_post_package(
        self,
        service_id: str,
        lang: str,
        theme: Dict[str, Any],
        persona: Dict[str, Any],
        cards: List[Dict[str, Any]],
        refund_formatted: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📢 SNS(인스타그램 캐러셀, 페이스북 피드, 블로그 등) 공식 포스팅을 위한
        [게시물 제목 + 본문 상세 캡션 + 17개국 바이럴 해시태그 + 공식 랜딩 URL] 100% 무인 생성 엔진
        """
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_name = theme.get("name", "특별 기획")
        target = theme.get("target", "외국인 거주자")

        if service_id == "easytax":
            landing_url = f"https://ktrs-service.vercel.app/?lang={lang}"
            amount_str = refund_formatted or "3,840,000 KRW"
            service_desc = (
                f"EasyTax 대한민국 국세청 조특법 30조 90% 소득세 감면 & 경정청구 세무 환급\n"
                f"- 예상 환급액: {amount_str}\n"
                f"- 핵심 신뢰 보증: 착수금/선결제 0원! 국세청 환급금이 내 통장에 먼저 입금된 후 정산하는 100% 후불제!\n"
                f"- 5년 소멸시효 전 긴급 구제 청구"
            )
        else:
            landing_url = f"https://kmarket-service.vercel.app/?lang={lang}"
            amount_str = "0 KRW (100% 무료 나눔)"
            item = theme.get("item", "가구/가전")
            service_desc = (
                f"K-Market 외국인 전용 0원 중고 무료 나눔 & 17개국어 실시간 자동번역 직거래\n"
                f"- 무료 나눔 품목: {item}\n"
                f"- 혜택: 가구/가전 비용 150만원 절약, 등록금/생활비 절감\n"
                f"- 한국어 몰라도 17개 언어 실시간 번역 채팅으로 내 동네 0원 매물 1초 확인"
            )

        # 1. 트렌드 스크래퍼 기반 기본 해시태그 로드
        from core.trend_scraper import ViralTrendScraper as TrendScraper
        scraper = TrendScraper()
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=12)]
        formatted_hashtags = scraper.format_hashtag_string(service_id, lang, count=12)

        if not self.client:
            return self._fallback_post_package(service_id, lang, theme_name, landing_url, formatted_hashtags, amount_str)

        prompt = f"""
너는 세계 최고의 5대 SNS(인스타그램, 페이스북, 레딧, 스레드, 텔레그램) 알고리즘 바이럴 마케팅 거장 디렉터야.
플랫폼별로 알고리즘 규제와 링크 클릭 동선이 완전히 다르다!
각 플랫폼의 알고리즘을 100% 해킹하여 노출(도달률)과 링크 클릭률(CTR)을 동시에 5배 폭증시키는 [5대 채널별 맞춤 포스팅 팩]을 [{lang_info['name']} ({lang_info['native_name']})] 언어로 작성해라.

### 대상 서비스: {service_id.upper()}
[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target})
[서비스 핵심 설명]:
{service_desc}
[공식 신청 링크]: {landing_url}

### 카드뉴스 5장 슬라이드 내용 요약:
1장: {cards[0].get('title', '') if len(cards) > 0 else ''}
2장: {cards[1].get('title', '') if len(cards) > 1 else ''}
3장: {cards[2].get('title', '') if len(cards) > 2 else ''}
4장: {cards[3].get('title', '') if len(cards) > 3 else ''}
5장: {cards[4].get('title', '') if len(cards) > 4 else ''}

### 5대 플랫폼별 알고리즘 해킹 규칙:
1. instagram_caption (인스타그램 캐러셀):
   - 본문엔 링크 클릭이 안 되므로, 감동 스토리 3문단 끝에 반드시 "🔗 프로필 상단 링크(@{service_id}_official)를 클릭하여 1분 만에 확인하세요!" 바이오 링크 유도 문구를 넣을 것.
2. facebook_post (페이스북 피드):
   - 본문에 링크를 넣으면 페북 알고리즘이 노출을 80% 깎아버린다! 그러므로 본문에는 링크를 절대 넣지 말고 "👇 무료 신청/조회 링크는 첫 번째 댓글(1st comment)을 확인하세요!"로 끝낼 것.
3. facebook_comment (페이스북 첫 번째 댓글 스텔스 링크):
   - 봇이 글 등록 즉시 0.1초 만에 달 첫 댓글. 친절한 안내와 함께 {landing_url} 링크 배치.
4. reddit_title & reddit_body & reddit_comment (레딧 갤러리):
   - 본문에 광고 링크가 있으면 스팸 영구 밴을 당한다! 본문은 100% 유용한 합법 정보 팩트만 쓰고 끝에 "(Tool link in comments)" 추가. 댓글에 자연스럽게 공식 계산기 도구({landing_url}) 소개.
5. threads_main & threads_reply (메타 스레드):
   - 1번 메인 타래는 카드뉴스 5장과 후킹 텍스트(링크 0%). 2번 답글 타래에 바로 이어달릴 링크({landing_url}) 메시지.
6. telegram_caption & telegram_btn (텔레그램 채널):
   - 5장 사진 묶음 앨범용 핵심 요약 캡션과 인라인 버튼 텍스트(예: "💰 무료 환급 조회하기").

### 출력 형식 (반드시 아래 JSON 포맷으로만 엄격히 출력):
{{
  "post_title": "공통 후킹 헤드라인 ({lang_info['name']})",
  "instagram": {{
    "caption": "인스타용 캡션 (바이오 링크 유도 포함) ({lang_info['name']})"
  }},
  "facebook": {{
    "post_content": "페북용 본문 (링크 절대 금지, 첫 댓글 유도) ({lang_info['name']})",
    "first_comment": "페북 첫 댓글용 스텔스 링크 ({landing_url} 포함) ({lang_info['name']})"
  }},
  "reddit": {{
    "title": "레딧 정보성 타이틀 ({lang_info['name']})",
    "body": "레딧 본문 (광고 배제, 팩트 중심) ({lang_info['name']})",
    "first_comment": "레딧 첫 댓글용 도구 안내 ({landing_url} 포함) ({lang_info['name']})"
  }},
  "threads": {{
    "main_post": "스레드 1번 메인 타래 ({lang_info['name']})",
    "reply_link": "스레드 2번 이어달기 링크 답글 ({landing_url} 포함) ({lang_info['name']})"
  }},
  "telegram": {{
    "caption": "텔레그램 5장 앨범 요약 캡션 ({lang_info['name']})",
    "button_text": "원클릭 버튼 문구 ({lang_info['name']})"
  }}
}}
"""
        try:
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            res_json = json.loads(raw_text)
            post_title = self._clean_text(res_json.get("post_title", f"{service_id.upper()} Guide"))

            ig_cap = self._clean_text(res_json.get("instagram", {}).get("caption", ""))
            fb_post = self._clean_text(res_json.get("facebook", {}).get("post_content", ""))
            fb_comm = self._clean_text(res_json.get("facebook", {}).get("first_comment", f"👉 {landing_url}"))
            rd_title = self._clean_text(res_json.get("reddit", {}).get("title", post_title))
            rd_body = self._clean_text(res_json.get("reddit", {}).get("body", ""))
            rd_comm = self._clean_text(res_json.get("reddit", {}).get("first_comment", f"👉 {landing_url}"))
            th_main = self._clean_text(res_json.get("threads", {}).get("main_post", ""))
            th_reply = self._clean_text(res_json.get("threads", {}).get("reply_link", f"👉 {landing_url}"))
            tg_cap = self._clean_text(res_json.get("telegram", {}).get("caption", ""))
            tg_btn = self._clean_text(res_json.get("telegram", {}).get("button_text", "1분 무료 조회하기"))

            channels = {
                "instagram": {
                    "title": post_title,
                    "caption": ig_cap,
                    "hashtags": formatted_hashtags,
                    "link_type": "bio_link"
                },
                "facebook": {
                    "post_content": fb_post,
                    "first_comment": fb_comm,
                    "hashtags": formatted_hashtags,
                    "link_type": "first_comment_stealth"
                },
                "reddit": {
                    "title": rd_title,
                    "body": rd_body,
                    "first_comment": rd_comm,
                    "link_type": "anti_ban_comment"
                },
                "threads": {
                    "main_post": th_main,
                    "reply_link": th_reply,
                    "link_type": "reply_chain"
                },
                "telegram": {
                    "caption": tg_cap,
                    "button_text": tg_btn,
                    "button_url": landing_url,
                    "link_type": "inline_button"
                }
            }

            return {
                "service_id": service_id,
                "lang": lang,
                "post_title": post_title,
                "post_caption": ig_cap,  # 기본 호환용
                "landing_url": landing_url,
                "hashtags": tags_list,
                "hashtags_str": formatted_hashtags,
                "channels": channels
            }
        except Exception as e:
            logger.warning(f"제미나이 5대 채널 포스트 패키지 생성 실패, 폴백 사용: {e}")

        return self._fallback_post_package(service_id, lang, theme_name, landing_url, formatted_hashtags, amount_str)

    def _fallback_post_package(
        self,
        service_id: str,
        lang: str,
        theme_name: str,
        landing_url: str,
        hashtags_str: str,
        amount_str: str
    ) -> Dict[str, Any]:
        """API 통신 지연 시 무중단 클린 폴백 5대 채널 포스트 패키지"""
        from core.trend_scraper import ViralTrendScraper as TrendScraper
        scraper = TrendScraper()
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=12)]

        if service_id == "easytax":
            title = f"💰 Official Expat Tax Refund: {theme_name} ({amount_str})"
            ig_caption = (
                f"Did you know expat workers in South Korea can get up to 90% income tax refund under Article 30?\n\n"
                f"✅ Estimated Refund: {amount_str}\n"
                f"✅ Zero Advance Fee: 100% success-based settlement after refund arrives in your bank account!\n"
                f"✅ 5-Year Statute of Limitations: Claim your past 5 years of taxes before they expire.\n\n"
                f"🔗 Check your exact refund amount in 1 minute via the link in our bio! (@easytax_official)"
            )
            fb_post = (
                f"Did you know expat workers in South Korea can get up to 90% income tax refund under Article 30?\n\n"
                f"✅ Estimated Refund: {amount_str}\n"
                f"✅ Zero Advance Fee: 100% success-based settlement after refund arrives in your bank account!\n"
                f"✅ 5-Year Statute of Limitations: Claim your past 5 years of taxes before they expire.\n\n"
                f"👇 Check the first comment below for the free 1-minute estimation tool link!"
            )
            fb_comment = f"👉 Estimate your refund for free in 1 minute (Certified NTS Agent): {landing_url}"
            rd_title = f"[Guide] How expat workers in Korea can claim up to 90% tax refund ({amount_str})"
            rd_body = (
                f"Under Korean Restriction of Special Taxation Act (Article 30), foreign workers at SMEs are eligible for up to 90% tax reduction for up to 5 years.\n\n"
                f"- Eligibility: E-9, H-2, E-7 and students D-2 with 3.3% withholding tax.\n"
                f"- No upfront fee: Regulated certified tax agents settle only after successful deposit.\n\n"
                f"(Tool link and details in the comment below)"
            )
            rd_comment = f"Here is the certified online refund simulation tool for anyone interested: {landing_url}"
            th_main = f"Expat tax refund rights in Korea: Claim up to 90% ({amount_str}) before 5-year expiration! 🧵👇"
            th_reply = f"🔗 Calculate your exact refund in 1 minute: {landing_url}"
            tg_caption = f"📢 [EasyTax] {theme_name}\n• Estimated Refund: {amount_str}\n• 100% Zero Upfront Fee"
            tg_btn = "💰 1-Minute Free Refund Check"
        else:
            title = f"🎁 100% Free 0 Won Giveaways: {theme_name}"
            ig_caption = (
                f"Furnish your entire room in South Korea for 0 Won!\n\n"
                f"✅ Verified 100% Free Items left by graduating students and expats.\n"
                f"✅ Save up to 1,500,000 KRW on essential furniture and electronics.\n"
                f"✅ 17-Language Real-Time Auto-Translation Chat for safe and easy local trade.\n\n"
                f"🔗 Claim today's free items via the link in our bio! (@kmarket_official)"
            )
            fb_post = (
                f"Furnish your entire room in South Korea for 0 Won!\n\n"
                f"✅ Verified 100% Free Items left by graduating students and expats.\n"
                f"✅ Save up to 1,500,000 KRW on essential furniture and electronics.\n"
                f"✅ 17-Language Real-Time Auto-Translation Chat for safe and easy local trade.\n\n"
                f"👇 Check the first comment below to grab today's newly posted 0 Won items!"
            )
            fb_comment = f"👉 Browse 0 Won free giveaways near your campus: {landing_url}"
            rd_title = f"[Student Tip] How international students in Korea furnish rooms for 0 Won"
            rd_body = (
                f"If you're an expat or student moving into a studio room or dorm in Korea, don't buy expensive new furniture.\n\n"
                f"Graduating seniors leave thousands of clean appliances every semester for free pickup.\n\n"
                f"(Link to the 17-language free giveaway platform in the comment below)"
            )
            rd_comment = f"You can check the local 0 Won listings here: {landing_url}"
            th_main = f"Furnish your studio room in Korea for 0 Won! Save 1,500,000 KRW on student living 🧵👇"
            th_reply = f"🔗 Claim free furniture & appliances now: {landing_url}"
            tg_caption = f"📢 [K-Market] {theme_name}\n• 100% Free Giveaway\n• Save 1.5M KRW"
            tg_btn = "🎁 Claim Free 0 Won Item"

        channels = {
            "instagram": {
                "title": title,
                "caption": ig_caption,
                "hashtags": hashtags_str,
                "link_type": "bio_link"
            },
            "facebook": {
                "post_content": fb_post,
                "first_comment": fb_comment,
                "hashtags": hashtags_str,
                "link_type": "first_comment_stealth"
            },
            "reddit": {
                "title": rd_title,
                "body": rd_body,
                "first_comment": rd_comment,
                "link_type": "anti_ban_comment"
            },
            "threads": {
                "main_post": th_main,
                "reply_link": th_reply,
                "link_type": "reply_chain"
            },
            "telegram": {
                "caption": tg_caption,
                "button_text": tg_btn,
                "button_url": landing_url,
                "link_type": "inline_button"
            }
        }

        return {
            "service_id": service_id,
            "lang": lang,
            "post_title": title,
            "post_caption": ig_caption,
            "landing_url": landing_url,
            "hashtags": tags_list,
            "hashtags_str": hashtags_str,
            "channels": channels
        }

