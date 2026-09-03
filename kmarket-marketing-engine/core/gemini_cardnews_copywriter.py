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
        api_key = GEMINI_API_KEY_EASYTAX if self.service_id == "easytax" else GEMINI_API_KEY_KMARKET
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info(f"[{self.service_id.upper()}] 제미나이 카드뉴스 카피라이터 초기화 성공")
            except Exception as e:
                logger.warning(f"제미나이 초기화 실패: {e}")
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

### 5장 슬라이드 스토리텔링 공식 (반드시 이 순서로 집필):
- 1장 (실제 입금 인증): 국세청에서 {refund_formatted} KRW 세금 환급금이 본인 통장에 입금 완료되었다는 강력한 팩트 후킹!
- 2장 (독자 자격 확인): "당신도 받을 수 있는지 확인해보세요! (E-9, E-7, D-2 등 외국인 95% 해당)"
- 3장 (안심 보증): "선입금 0원, 17개국어 모국어 상담, 국세청 등록 공인 대리라 100% 안전!"
- 4장 (환급금으로 이루는 꿈): 환급받은 {refund_formatted} KRW로 고향 부모님 효도 송금 / 고향 비행기표 / 학비 해결 등의 감동 스토리
- 5장 (행동 촉구 CTA): "5년 지나면 국가로 귀속됩니다! 지금 프로필 링크(Bio Link)를 눌러 1분 무료 조회하고 수령하세요!"

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
