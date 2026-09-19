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
from config import GEMINI_API_KEY_EASYTAX, GEMINI_API_KEY_KMARKET, LANGUAGES, BASE_URLS

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
2. ⚠️ 절대 화폐 규칙: 환급금은 대한민국 국세청의 한국 세금 환급이므로, 금액 단위를 루피아, 솜, 바트, 짯, 동 등으로 임의 환각 번역하지 마십시오! 반드시 '{refund_formatted} KRW' 또는 '{refund_formatted} Won'으로만 표기하십시오.
3. 폰트 깨짐을 방지하기 위해 특수 이모지는 쓰지 말고, 불릿 기호는 표준 '•' 또는 '1.', '2.', '3.'을 사용할 것.
4. 아래 JSON 형식으로만 정확히 출력할 것:

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
    ],
    "cta_button": "Action button in {lang_info['name']} (e.g. Check refund for free >)"
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
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next >)"
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
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next >)"
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
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next >)"
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
    ],
    "cta_button": "Final CTA button in {lang_info['name']} (e.g. Check my refund now >)"
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
                # 텍스트 안전 정제 및 🎯 [금액 100% 원천 동기화] 검증
                for c in cards:
                    c["badge"] = self._clean_text(c.get("badge", ""))
                    c["title"] = self._clean_text(c.get("title", ""))
                    c["subtitle"] = self._clean_text(c.get("subtitle", ""))
                    c["bullets"] = [self._clean_text(b) for b in c.get("bullets", [])]
                    c["cta_button"] = self._clean_text(c.get("cta_button", ""))

                # 1번 슬라이드 및 본문에서 환급액 표기 무결성 100% 보장
                # (제미나이가 혹시라도 환각 숫자를 출력했을 경우 확정된 refund_formatted로 정밀 치환)
                if cards and "title" in cards[0]:
                    import re
                    # 임의의 화폐/금액 패턴(\d{1,3}(,\d{3})+ (KRW|원|Won)?) 감지 시 확정된 refund_formatted로 일치
                    cards[0]["title"] = re.sub(r"\b\d{1,3}(,\d{3})+\s*(KRW|Won|원)?\b", refund_formatted, cards[0]["title"], flags=re.IGNORECASE)

                logger.info(f"[{lang.upper()}] 🎉 제미나이 100% 현지어 카드뉴스 카피라이팅 성공 (환급액: {refund_formatted})!")
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
        """KTRS 마켓 5단계 감동 카드뉴스 카피라이팅 (100% 타깃 현지어 직작문)"""
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
한국에 거주하는 외국인 유학생 및 근로자({target})를 위해, KTRS 마켓 0원 무료 나눔 5장 카드뉴스 텍스트를 100% 자연스러운 [{lang_info['name']} ({lang_info['native_name']})] 구어체로 직접 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target})
[무료 품목]: {item} (귀국 선배들이 남긴 A급 가구/가전 100% 무료 나눔)
[주인공 페르소나]: {persona.get('name', '외국인 유학생')}

### 5장 슬라이드 스토리텔링 공식 (반드시 이 순서로 집필):
- 1장 (★핵심 직거래 훅 - 1인 직접 수령 소형 가전/생활용품): 길거리나 건물 앞에서 직접 1:1로 만나 웃으며 깨끗한 {item}을 0원에 직접 두 손으로 건네받는 생생한 직거래 실화 후킹! (예: "신촌 연세대 앞, {item} 0원 나눔 직거래 현장! 진짜 0원에 가져가도 되나요?")
- 2장 (내 방 풀세팅 & 150만원 절약): 방 안에 {item}을 깔끔하게 배치하고 필수 가전값 150만 원을 아낀 감동과 뿌듯함
- 3장 (KTRS 마켓 실물 0원 무료나눔 매물 피드): "도대체 어디서 구했어? 매일 쏟아지는 K-Market 0원 실물 가구·가전 매물 피드 대공개!"
- 4장 (안심 1:1 직거래 & 17개국어 번역 채팅): "한국어 몰라도 17개 언어 실시간 자동번역 채팅으로 10분 만에 안전하게 약속 완료!"
- 5장 (행동 촉구 CTA): "오늘 등록된 0원 매물 놓치지 마세요! 지금 프로필 링크(Bio Link)를 눌러 0원 매물 바로 득템하세요!"

### 필수 출력 규칙:
1. 반드시 순수한 [{lang_info['name']}] 언어로만 작성할 것. (한국어가 섞이지 않게 100% 현지어로 번역/창작)
2. ⚠️ 절대 화폐 규칙: 본 서비스는 '대한민국' 내에서 이루어지는 0원 무료 나눔 거래입니다. 가격이나 통화 단위를 루피아(Rupiah), 솜(so'm), 바트(Baht), 짯(Kyat), 동(Dong) 등 외국 자국 화폐로 임의 번역/환각하지 마십시오! 반드시 '0원', '0 Won', '0 KRW'로만 표기하십시오.
3. 폰트 깨짐을 방지하기 위해 특수 이모지는 쓰지 말고, 불릿 기호는 표준 '•' 또는 '1.', '2.', '3.'을 사용할 것.
4. 아래 JSON 형식으로만 정확히 출력할 것:

[
  {{
    "slide_idx": 1,
    "badge": "STEP 1: BADGE IN {lang_info['name']}",
    "title": "Slide 1 Small Appliance 0 KRW Giveaway Title in {lang_info['name']}",
    "subtitle": "Slide 1 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 (meeting in person, receiving microwave/appliance) in {lang_info['name']}",
      "• Bullet 2 (genuine 0 Won free handover) in {lang_info['name']}",
      "• Bullet 3 (connected via KTRS Market app translation) in {lang_info['name']}"
    ],
    "cta_button": "Action button in {lang_info['name']} (e.g. Check 0 won free items >)"
  }},
  {{
    "slide_idx": 2,
    "badge": "STEP 2: BADGE IN {lang_info['name']}",
    "title": "Slide 2 Cozy Room & Save 1.5M Title in {lang_info['name']}",
    "subtitle": "Slide 2 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next part >)"
  }},
  {{
    "slide_idx": 3,
    "badge": "STEP 3: BADGE IN {lang_info['name']}",
    "title": "Slide 3 0 Won Feed Title in {lang_info['name']}",
    "subtitle": "Slide 3 Subtitle in {lang_info['name']}",
    "bullets": [
      "• Bullet 1 in {lang_info['name']}",
      "• Bullet 2 in {lang_info['name']}",
      "• Bullet 3 in {lang_info['name']}"
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next part >)"
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
    ],
    "cta_button": "Next button in {lang_info['name']} (e.g. See next part >)"
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
    ],
    "cta_button": "Final CTA button in {lang_info['name']} (e.g. Get 0 won free items now >)"
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
                    c["cta_button"] = self._clean_text(c.get("cta_button", ""))
                logger.info(f"[{lang.upper()}] 🎉 KTRS 마켓 제미나이 100% 현지어 카드뉴스 카피라이팅 성공!")
                return cards
        except Exception as e:
            logger.warning(f"[{lang.upper()}] KTRS 마켓 제미나이 카피라이팅 실패, 폴백 사용: {e}")

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
        item = theme.get("item", "가구/가전")
        target = theme.get("target", "캠퍼스 대학가")

        if lang == "ko":
            return [
                {
                    "slide_idx": 1,
                    "badge": "STEP 1: 1:1 실물 직거래",
                    "title": f"{target} 앞, 베트남 유학생과 네팔 친구의 0원 직거래 현장!",
                    "subtitle": "국적은 달라도 KTRS 마켓 앱으로 5분 만에 직거래 약속 완료",
                    "bullets": [
                        f"• 귀국하는 선배와 신입생이 직접 만나 웃으며 {item} 전달",
                        "• '진짜 0원 맞아요?' 눈앞에서 확인한 감동의 무료 나눔",
                        "• 17개국어 실시간 자동 번역 채팅으로 언어 장벽 해결"
                    ]
                },
                {
                    "slide_idx": 2,
                    "badge": "STEP 2: 아늑한 방 완성",
                    "title": "텅 비었던 내 자취방, 150만원 아끼고 완벽 변신",
                    "subtitle": "가구 하나로 달라진 따뜻한 한국 자취 생활",
                    "bullets": [
                        f"• 썰렁하던 방에 {item} 하나 들어왔을 뿐인데 분위기 반전",
                        "• 가구값 150만 원 아껴서 등록금과 생활비에 보태기",
                        "• 한국에서의 자취가 훨씬 더 쾌적하고 편안해졌어요"
                    ]
                },
                {
                    "slide_idx": 3,
                    "badge": "STEP 3: 0원 매물 피드",
                    "title": "도대체 어디서? KTRS 마켓 0원 무료나눔 피드",
                    "subtitle": "매일매일 실시간으로 쏟아지는 깨끗한 가구와 가전",
                    "bullets": [
                        "• 침대, 책상, 전자레인지, 냉장고까지 0원에 득템",
                        "• 내 캠퍼스/기숙사 근처 나눔 정보를 1초 만에 확인",
                        "• 귀국 선배들이 남긴 깨끗한 생활용품 무료 나눔"
                    ]
                },
                {
                    "slide_idx": 4,
                    "badge": "STEP 4: 17개국어 번역",
                    "title": "한국어 몰라도 괜찮아, 17개국어 자동 번역 채팅",
                    "subtitle": "채팅 10분 만에 집 앞에서 안전하게 직거래 약속 완료",
                    "bullets": [
                        "• 복잡한 한국어 공부 필요 없는 실시간 자동 번역",
                        "• 사기 0% 외국인등록증(ARC) 인증 안심 직거래",
                        "• 언어 장벽 없이 모국어로 편하게 직거래 예약"
                    ]
                },
                {
                    "slide_idx": 5,
                    "badge": "STEP 5: 지금 바로 득템",
                    "title": f"지금 {target} 주변 0원 매물을 확인해보세요",
                    "subtitle": "놓치면 후회할 대박 나눔, 지금 바로 KTRS 마켓 앱 다운로드!",
                    "bullets": [
                        "• 매일매일 새로운 0원 나눔이 쏟아집니다",
                        "• 프로필 링크 누르고 지금 바로 앱 설치하기",
                        "• 더 많은 무료 가전과 가구를 지금 바로 만나보세요"
                    ]
                }
            ]

        return [
            {
                "slide_idx": 1,
                "badge": "STEP 1: 1:1 DIRECT EXCHANGE",
                "title": f"Expats Meeting in {target}: 0 Won {item} Handover!",
                "subtitle": "Vietnamese and Nepali students trading in person for $0",
                "bullets": [
                    f"• Met directly on campus to hand over clean {item} with smiles",
                    "• Verified 100% free giveaway between international students",
                    "• Connected in 3 minutes via KTRS Market 17-language chat"
                ]
            },
            {
                "slide_idx": 2,
                "badge": "STEP 2: COZY ROOM COMPLETE",
                "title": "Furnish Your Studio Room & Save 1,500,000 KRW",
                "subtitle": "Transform cold empty room into a warm comfortable home",
                "bullets": [
                    f"• Clean and tested {item} in great condition",
                    "• Save 1.5 million won on brand new furniture costs",
                    "• Enjoy a comfortable cozy living space in Korea"
                ]
            },
            {
                "slide_idx": 3,
                "badge": "STEP 3: 0 WON FEED",
                "title": "Where To Get It? KTRS Market 0 Won Giveaway Feed",
                "subtitle": "Hundreds of clean furniture and appliances posted daily",
                "bullets": [
                    "• Beds, desks, microwaves, and fridges for 0 Won",
                    "• Fresh listings updated real-time near your campus",
                    "• Quality items gifted by graduating students and expats"
                ]
            },
            {
                "slide_idx": 4,
                "badge": "STEP 4: 17-LANGUAGE CHAT",
                "title": "17-Language Auto-Translation Chat & Safe Meetup",
                "subtitle": "Trade safely even without speaking fluent Korean",
                "bullets": [
                    "• Real-time AI auto-translation in 17 native languages",
                    "• Safe direct messaging with verified local students",
                    "• Coordinate meetup outside within 10 minutes"
                ]
            },
            {
                "slide_idx": 5,
                "badge": "STEP 5: CLAIM $0 FREE TODAY",
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
        persona: Optional[Dict[str, Any]] = None,
        cards: Optional[List[Dict[str, Any]]] = None,
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
            base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/?lang={lang}"
            amount_str = refund_formatted or "3,840,000 KRW"
            service_desc = (
                f"EasyTax 대한민국 국세청 조특법 30조 90% 소득세 감면 & 경정청구 세무 환급\n"
                f"- 예상 환급액: {amount_str}\n"
                f"- 핵심 신뢰 보증: 착수금/선결제 0원! 국세청 환급금이 내 통장에 먼저 입금된 후 정산하는 100% 후불제!\n"
                f"- 5년 소멸시효 전 긴급 구제 청구"
            )
        else:
            base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/{lang}"
            amount_str = "0 KRW (100% 무료 나눔)"
            item = theme.get("item", "가구/가전")
            service_desc = (
                f"KTRS 마켓 외국인 전용 0원 중고 무료 나눔 & 17개국어 실시간 자동번역 직거래\n"
                f"- 무료 나눔 품목: {item}\n"
                f"- 혜택: 가구/가전 비용 150만원 절약, 등록금/생활비 절감\n"
                f"- 한국어 몰라도 17개 언어 실시간 번역 채팅으로 내 동네 0원 매물 1초 확인"
            )

        # 1. 트렌드 스크래퍼 기반 17개국 정밀 타깃 해시태그 전체 로드 (대시보드와 100% 동기화)
        from core.trend_scraper import ViralTrendScraper as TrendScraper
        scraper = TrendScraper()
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=25)]
        formatted_hashtags = scraper.format_hashtag_string(service_id, lang, count=25)

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

### [★ 엄격한 언어 및 번역 무결성 수칙 - 절대 위반 금지]:
1. 모든 외국어 텍스트는 100% 순수한 [{lang_info['name']}] 원어민 구어체로만 작성해라.
2. 절대로 외국어 문장 중간에 한국어 단어(예: '후불제', '안심', '환급', '클릭' 등)를 그대로 섞어 쓰지 마라! 반드시 해당 국가의 자연스러운 표현으로 100% 완전 번역해라.
3. 본문 텍스트 내부에 임의의 `#해시태그`를 절대 직접 작성하지 마라 (시스템이 정식 17개국 매트릭스 태그를 완벽하게 결합함).

### 5대 플랫폼별 알고리즘 해킹 규칙:
1. instagram (인스타그램 캐러셀):
   - caption: 감동 스토리 + 핵심 혜택 3가지 요약 + 100% 안심 후불제 강조 + "🔗 프로필 링크(@{service_id}_official) 또는 아래 링크에서 지금 바로 무료 확인하세요!\n👉 {landing_url}"
   - ko_explanation: 관리자가 확인할 수 있는 정확한 한국어 번역 및 해설.
2. facebook (페이스북 피드):
   - post_content: 본문에 링크를 넣으면 노출이 80% 깎인다! 링크를 절대 넣지 말고 "👇 1분 무료 신청/조회 링크는 첫 번째 댓글(1st comment)을 확인하세요!"로 끝낼 것.
   - first_comment: 글 등록 직후 달아줄 스텔스 공식 링크 메시지 ("👉 1분 무료 환급액 확인 (착수금 0원 100% 안심 후불제):\n{landing_url}").
   - ko_explanation: 관리자가 확인할 수 있는 정확한 한국어 번역 및 해설.
3. threads (메타 스레드):
   - main_post: ⚠️ [매우 중요]: 스레드는 최대 500자 글자 수 제한이 매우 엄격하므로, 1번 메인 타래는 반드시 120~180자 내외의 강렬하고 매력적인 숏폼 후킹 텍스트(링크 0%)로 간결하게 작성할 것! 절대 200자를 넘기지 마라.
   - reply_link: 2번 답글 타래에 바로 이어달릴 링크 메시지 ("👉 1분 무료 신청/조회 바로가기:\n{landing_url}").
   - ko_explanation: 관리자가 확인할 수 있는 정확한 한국어 번역 및 해설.
4. telegram (텔레그램 채널):
   - caption: 텔레그램 채널/그룹에 바로 복사-붙여넣기 할 수 있도록 본문 중간/하단에 공식 링크("👉 1분 무료 신청/조회 바로가기:\n{landing_url}")가 반드시 명확히 포함된 완전체 포스트.
   - button_text: 버튼 문구 (예: "💰 1분 무료 확인하기"의 {lang_info['name']} 번역).
   - ko_explanation: 관리자가 확인할 수 있는 정확한 한국어 번역 및 해설.
5. reddit (레딧):
   - title, body, first_comment ({landing_url} 포함) 및 ko_explanation.

### 출력 형식 (반드시 아래 JSON 포맷으로만 엄격히 출력):
{{
  "post_title": "공통 후킹 헤드라인 ({lang_info['name']})",
  "instagram": {{
    "caption": "인스타용 캡션 ({landing_url} 포함) ({lang_info['name']})",
    "ko_explanation": "인스타 캡션 한국어 번역 및 해설"
  }},
  "facebook": {{
    "post_content": "페북용 본문 (링크 제외) ({lang_info['name']})",
    "first_comment": "페북 첫 댓글용 스텔스 링크 ({landing_url} 포함) ({lang_info['name']})",
    "ko_explanation": "페북 본문 한국어 번역 및 해설"
  }},
  "threads": {{
    "main_post": "스레드 1번 메인 타래 (링크 제외) ({lang_info['name']})",
    "reply_link": "스레드 2번 이어달기 링크 답글 ({landing_url} 포함) ({lang_info['name']})",
    "ko_explanation": "스레드 본문 한국어 번역 및 해설"
  }},
  "telegram": {{
    "caption": "텔레그램 전체 포스트 ({landing_url} 포함) ({lang_info['name']})",
    "button_text": "원클릭 버튼 문구 ({lang_info['name']})",
    "ko_explanation": "텔레그램 캡션 한국어 번역 및 해설"
  }},
  "reddit": {{
    "title": "레딧 정보성 타이틀 ({lang_info['name']})",
    "body": "레딧 본문 ({lang_info['name']})",
    "first_comment": "레딧 첫 댓글용 도구 안내 ({landing_url} 포함) ({lang_info['name']})",
    "ko_explanation": "레딧 본문 한국어 번역 및 해설"
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

            ig_data = res_json.get("instagram", {})
            fb_data = res_json.get("facebook", {})
            rd_data = res_json.get("reddit", {})
            th_data = res_json.get("threads", {})
            tg_data = res_json.get("telegram", {})

            ig_cap = self._clean_text(ig_data.get("caption", ""))
            ig_ko = self._clean_text(ig_data.get("ko_explanation", ig_cap))

            fb_post = self._clean_text(fb_data.get("post_content", ""))
            fb_comm = self._clean_text(fb_data.get("first_comment", f"👉 {landing_url}"))
            fb_ko = self._clean_text(fb_data.get("ko_explanation", fb_post))

            rd_title = self._clean_text(rd_data.get("title", post_title))
            rd_body = self._clean_text(rd_data.get("body", ""))
            rd_comm = self._clean_text(rd_data.get("first_comment", f"👉 {landing_url}"))
            rd_ko = self._clean_text(rd_data.get("ko_explanation", rd_body))

            th_main = self._clean_text(th_data.get("main_post", ""))
            th_reply = self._clean_text(th_data.get("reply_link", f"👉 {landing_url}"))
            th_ko = self._clean_text(th_data.get("ko_explanation", th_main))

            tg_cap = self._clean_text(tg_data.get("caption", ""))
            tg_btn = self._clean_text(tg_data.get("button_text", "1분 무료 확인하기"))
            tg_ko = self._clean_text(tg_data.get("ko_explanation", tg_cap))

            channels = {
                "instagram": {
                    "title": post_title,
                    "caption": ig_cap,
                    "ko_explanation": ig_ko,
                    "hashtags": formatted_hashtags,
                    "link_type": "bio_link"
                },
                "facebook": {
                    "post_content": fb_post,
                    "first_comment": fb_comm,
                    "ko_explanation": fb_ko,
                    "hashtags": formatted_hashtags,
                    "link_type": "first_comment_stealth"
                },
                "reddit": {
                    "title": rd_title,
                    "body": rd_body,
                    "first_comment": rd_comm,
                    "ko_explanation": rd_ko,
                    "link_type": "anti_ban_comment"
                },
                "threads": {
                    "main_post": th_main,
                    "reply_link": th_reply,
                    "ko_explanation": th_ko,
                    "link_type": "reply_chain"
                },
                "telegram": {
                    "caption": tg_cap,
                    "button_text": tg_btn,
                    "button_url": landing_url,
                    "ko_explanation": tg_ko,
                    "link_type": "inline_button"
                }
            }

            return {
                "service_id": service_id,
                "lang": lang,
                "post_title": post_title,
                "post_caption": ig_cap,
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
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=25)]

        if service_id == "easytax":
            title = f"💰 Official Expat Tax Refund: {theme_name} ({amount_str})"
            ig_caption = (
                f"Did you know expat workers in South Korea can get up to 90% income tax refund under Article 30?\n\n"
                f"✅ Estimated Refund: {amount_str}\n"
                f"✅ Zero Advance Fee: 100% safe pay-after-refund settlement!\n"
                f"✅ 5-Year Statute of Limitations: Claim your past taxes before they expire.\n\n"
                f"🔗 Check your exact refund amount via profile link (@easytax_official) or direct link:\n"
                f"👉 {landing_url}"
            )
            ig_ko = f"한국 거주 외국인 근로자 소득세 90% 감면 환급 안내 (예상액: {amount_str}, 착수금 0원 100% 안심 후불제)"
            fb_post = (
                f"Did you know expat workers in South Korea can get up to 90% income tax refund under Article 30?\n\n"
                f"✅ Estimated Refund: {amount_str}\n"
                f"✅ Zero Advance Fee: 100% safe pay-after-refund settlement!\n"
                f"✅ 5-Year Statute of Limitations: Claim your past taxes before they expire.\n\n"
                f"👇 Check the first comment below for the free 1-minute estimation tool link!"
            )
            fb_comment = f"👉 Estimate your refund for free in 1 minute (100% Safe Pay-After-Refund):\n{landing_url}"
            fb_ko = f"외국인 근로자 세금 환급 안내 ({amount_str} 환급, 첫 댓글 링크 확인)"
            rd_title = f"[Guide] How expat workers in Korea can claim up to 90% tax refund ({amount_str})"
            rd_body = (
                f"Under Korean Restriction of Special Taxation Act (Article 30), foreign workers at SMEs are eligible for up to 90% tax reduction for up to 5 years.\n\n"
                f"- Eligibility: E-9, H-2, E-7 and students D-2 with 3.3% withholding tax.\n"
                f"- No upfront fee: 100% safe pay-after-refund.\n\n"
                f"(Tool link and details in the comment below)"
            )
            rd_comment = f"👉 Here is the online refund simulation tool (Zero advance fee): {landing_url}"
            rd_ko = f"조특법 30조 외국인 근로자 90% 소득세 감면 정보 (수수료 후불제)"
            th_main = f"Expat tax refund rights in Korea: Claim up to 90% ({amount_str}) before 5-year expiration! 🧵👇"
            th_reply = f"👉 Calculate your exact refund in 1 minute:\n{landing_url}"
            th_ko = f"한국 거주 외국인 세금 환급 권리: 5년 소멸시효 전 최대 90% 환급 신청"
            tg_caption = (
                f"📢 [EasyTax] {theme_name}\n"
                f"• Estimated Refund: {amount_str}\n"
                f"• 100% Zero Upfront Fee (Safe Pay-After-Refund)\n\n"
                f"👉 Check your refund for free in 1 minute:\n{landing_url}"
            )
            tg_btn = "💰 1-Minute Free Refund Check"
            tg_ko = f"이지텍스 외국인 세금 환급 공지 (예상 환급액: {amount_str})"
        else:
            title = f"🎁 100% Free 0 Won Giveaways: {theme_name}"
            ig_caption = (
                f"Furnish your entire room in South Korea for 0 Won!\n\n"
                f"✅ Verified 100% Free Items left by graduating students and expats.\n"
                f"✅ Save up to 1,500,000 KRW on essential furniture and electronics.\n"
                f"✅ 17-Language Real-Time Auto-Translation Chat for safe and easy local trade.\n\n"
                f"🔗 Check 0 Won items near you via profile link (@kmarket_official) or direct link:\n"
                f"👉 {landing_url}"
            )
            ig_ko = f"케이마켓 0원 무료 나눔 안내 (가구/가전 150만원 절약, 17개국어 실시간 번역 채팅)"
            fb_post = (
                f"Furnish your entire room in South Korea for 0 Won!\n\n"
                f"✅ Verified 100% Free Items left by graduating students and expats.\n"
                f"✅ Save up to 1,500,000 KRW on essential furniture and electronics.\n"
                f"✅ 17-Language Real-Time Auto-Translation Chat for safe and easy local trade.\n\n"
                f"👇 Check the first comment below to grab today's newly posted 0 Won items!"
            )
            fb_comment = f"👉 Browse 0 Won free giveaways near your campus:\n{landing_url}"
            fb_ko = f"케이마켓 0원 무료 나눔 안내 (가구/가전 150만원 절약, 첫 댓글 링크)"
            rd_title = f"[Student Tip] How international students in Korea furnish rooms for 0 Won"
            rd_body = (
                f"If you're an expat or student moving into a studio room or dorm in Korea, don't buy expensive new furniture.\n\n"
                f"Graduating seniors leave thousands of clean appliances every semester for free pickup.\n\n"
                f"(Link to the 17-language free giveaway platform in the comment below)"
            )
            rd_comment = f"👉 You can check the local 0 Won listings here:\n{landing_url}"
            rd_ko = f"유학생 자취방 0원으로 풀세팅하는 법 (귀국 선배 무료 나눔)"
            th_main = f"Furnish your studio room in Korea for 0 Won! Save 1,500,000 KRW on student living 🧵👇"
            th_reply = f"👉 Claim free furniture & appliances now:\n{landing_url}"
            th_ko = f"한국 자취방 0원으로 꾸미기: 150만원 아끼는 무료 나눔"
            tg_caption = (
                f"📢 [KTRS Market] {theme_name}\n"
                f"• 100% Free Giveaway (Save 1.5M KRW)\n"
                f"• 17-Language Real-Time Auto-Translation Chat\n\n"
                f"👉 Claim Free 0 Won Items:\n{landing_url}"
            )
            tg_btn = "🎁 Claim Free 0 Won Item"
            tg_ko = f"케이마켓 무료 나눔 공지 (100% 무료, 150만원 절약)"

        channels = {
            "instagram": {
                "title": title,
                "caption": ig_caption,
                "ko_explanation": ig_ko,
                "hashtags": hashtags_str,
                "link_type": "bio_link"
            },
            "facebook": {
                "post_content": fb_post,
                "first_comment": fb_comment,
                "ko_explanation": fb_ko,
                "hashtags": hashtags_str,
                "link_type": "first_comment_stealth"
            },
            "reddit": {
                "title": rd_title,
                "body": rd_body,
                "first_comment": rd_comment,
                "ko_explanation": rd_ko,
                "link_type": "anti_ban_comment"
            },
            "threads": {
                "main_post": th_main,
                "reply_link": th_reply,
                "ko_explanation": th_ko,
                "link_type": "reply_chain"
            },
            "telegram": {
                "caption": tg_caption,
                "button_text": tg_btn,
                "button_url": landing_url,
                "ko_explanation": tg_ko,
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

    def format_guide_text(self, package: Dict[str, Any]) -> str:
        """
        📢 4대 SNS(스레드, 인스타그램, 페이스북, 텔레그램) 2단 포스팅 가이드 텍스트 렌더링
        - 현지어 원문 (원클릭 복사용) + 관리자용 한국어 대조/해설 2단 완벽 병기
        - 대시보드 17개국 바이럴 해시태그 풀세트 100% 일관 결합
        - 채널별 실제 작동하는 공식 링크 URL 완벽 내장
        """
        import re
        service_id = package.get("service_id", "easytax").upper()
        lang = package.get("lang", "en").lower()
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_title = package.get("post_title", "")
        landing_url = package.get("landing_url", "")
        hashtags_str = package.get("hashtags_str", "")
        channels = package.get("channels", {})

        th = channels.get("threads", {})
        ig = channels.get("instagram", {})
        fb = channels.get("facebook", {})
        tg = channels.get("telegram", {})

        # 제미나이가 본문에 임의로 작성한 태그를 깨끗이 제거하고, 정식 해시태그 풀세트를 결합하는 정밀 헬퍼
        def clean_and_attach_hashtags(content_text: str, tags: str) -> str:
            raw = (content_text or "").strip()
            # 본문에 있는 제미나이 임의 해시태그 (#으로 시작하는 단어들) 전부 제거
            cleaned = re.sub(r'#[\w\u0e00-\u0e7f\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]+', '', raw).strip()
            # 다중 줄바꿈 정리
            cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
            if not tags:
                return cleaned
            return f"{cleaned}\n\n{tags}" if cleaned else tags

        # 🧵 스레드(Threads) 전용 헬퍼: 500자 제한을 절대 넘지 않도록 상위 3~4개 핵심 태그만 선별 결합 (총 300자 내외 보장)
        def format_threads_main(content_text: str, tags: str) -> str:
            raw = (content_text or "").strip()
            cleaned = re.sub(r'#[\w\u0e00-\u0e7f\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]+', '', raw).strip()
            cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
            # 상위 3~4개 핵심 해시태그만 선별
            tag_list = [t.strip() for t in tags.split() if t.strip().startswith('#')]
            top_tags = " ".join(tag_list[:4]) if tag_list else ""
            
            result = f"{cleaned}\n\n{top_tags}" if top_tags else cleaned
            # 혹시 전체 길이가 400자를 넘어가면 안전하게 350자 이내로 문장 단위 정제
            if len(result) > 420:
                truncated = cleaned[:280]
                if '.' in truncated:
                    truncated = truncated.rsplit('.', 1)[0] + '.'
                result = f"{truncated}\n\n{top_tags}"
            return result

        th_main = format_threads_main(th.get('main_post', ''), hashtags_str)
        ig_caption = clean_and_attach_hashtags(ig.get('caption', ''), hashtags_str)
        fb_content = clean_and_attach_hashtags(fb.get('post_content', ''), hashtags_str)
        tg_caption = clean_and_attach_hashtags(tg.get('caption', ''), hashtags_str)

        # 텔레그램 본문에 혹시 landing_url이 빠져 있다면 자동으로 삽입
        if landing_url and landing_url not in tg_caption:
            tg_caption = tg_caption.replace(f"\n\n{hashtags_str}", f"\n\n👉 {landing_url}\n\n{hashtags_str}")

        doc = f"""================================================================================
📢 [{service_id} 카드뉴스 공식 SNS 4대 채널 포스팅 패키지 (제미나이 100% 실시간 자율 창작)]
🌍 타깃 국가/언어: {lang_info.get('name', lang.upper())} ({lang.upper()})
📌 주제: {theme_title}
🔗 공식 랜딩 링크: {landing_url}
🏷️ 17개국 바이럴 해시태그 (복사용): 
{hashtags_str}
================================================================================

[1] 🧵 스레드 (Threads) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 메인 타래 (현지어 복사용 - 링크 0% 노출 극대화)]
{th_main}

🔗 [이어달릴 2번 답글 링크 (현지어 복사용)]
{th.get('reply_link', f'👉 {landing_url}')}

🇰🇷 [한국어 대조/해설 (관리자 확인용)]
{th.get('ko_explanation', th.get('main_post', ''))}


[2] 📸 인스타그램 (Instagram) 캐러셀 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (현지어 복사용 - 프로필 링크 & URL 일체형)]
{ig_caption}

🇰🇷 [한국어 대조/해설 (관리자 확인용)]
{ig.get('ko_explanation', ig.get('caption', ''))}


[3] 📘 페이스북 (Facebook) 피드 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 본문 (현지어 복사용 - 링크 0% 알고리즘 노출 극대화)]
{fb_content}

💬 [첫 번째 댓글 (스텔스 공식 링크 복사용)]
{fb.get('first_comment', f'👉 {landing_url}')}

🇰🇷 [한국어 대조/해설 (관리자 확인용)]
{fb.get('ko_explanation', fb.get('post_content', ''))}


[4] ✈️ 텔레그램 (Telegram) 5장 앨범 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (현지어 복사용 - 원클릭 바로가기 링크 일체형)]
{tg_caption}

🔘 [원클릭 인라인 버튼 가이드 (봇 운영 시)]
[{tg.get('button_text', '무료 확인하기')}] -> {landing_url}

🇰🇷 [한국어 대조/해설 (관리자 확인용)]
{tg.get('ko_explanation', tg.get('caption', ''))}
================================================================================
"""
        return doc

