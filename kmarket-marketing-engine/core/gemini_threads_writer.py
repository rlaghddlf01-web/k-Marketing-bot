"""
GeminiThreadsWriter - 🧵 [Meta Threads 17개국어 바이럴 스레드 전담 카피라이팅 엔진]
- 제미나이 무료 키(Gemini 3.1 Flash-Lite) 100% 활용 (추가 비용 0원)
- 3대 시간대별 하이브리드 포맷 완벽 생성:
  1. 🌅 아침 (11:00 KST): 📸 [카드뉴스 5장 첨부형] (링크 0% 메인 글 + 0.1초 링크 답글 댓글)
  2. ☕ 오후 (16:30 KST): 📝 [순수 텍스트 리얼 썰형] (광고 티 0% 3단 타래: 썰 -> 꿀팁 팩트 -> 링크 댓글)
  3. 🌙 저녁 (21:30 KST): 📸 [야간 카드뉴스 첨부형] (퇴근/하교 모바일 맞춤 + 0.1초 링크 답글 댓글)
- 17개국 현지어 직작문, 바이럴 해시태그, 무결점 링크 체인 자동 구성
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from config import LANGUAGES, BASE_URLS

logger = logging.getLogger("GeminiThreadsWriter")


class GeminiThreadsWriter:
    """제미나이 3.1 Flash-Lite 기반 17개국어 Threads 바이럴 타래 생성 엔진"""

    def __init__(self, service_id: str = "kmarket"):
        self.service_id = service_id.lower()
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        try:
            from core.gemini_smart_client import GeminiSmartClient
            self.client = GeminiSmartClient(service_id=self.service_id)
            logger.info(f"[{self.service_id.upper()}] 제미나이 Threads 스마트 카피라이터 초기화 성공 (무료키 1순위)")
        except Exception as e:
            logger.warning(f"제미나이 스마트 클라이언트 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        """불필요한 공백 및 따옴표 정제 (스레드 바이럴 이모지 보존)"""
        if not text:
            return ""
        return text.strip()

    def generate_thread_package(
        self,
        lang: str,
        time_slot: str = "morning",
        theme: Optional[Dict[str, Any]] = None,
        landing_url: str = ""
    ) -> Dict[str, Any]:
        """
        시간대별(아침/오후/저녁) 맞춤형 스레드 타래 세트 생성
        - time_slot: "morning" (11:00 카드뉴스), "afternoon" (16:30 순수 썰), "evening" (21:30 카드뉴스)
        """
        lang_info = LANGUAGES.get(lang, LANGUAGES.get("en", {"name": "English", "native_name": "English"}))
        theme = theme or {}
        theme_name = theme.get("name") or theme.get("title") or ("0원 나눔" if self.service_id == "kmarket" else "세무 환급")
        target = theme.get("target", "외국인")
        item_or_refund = theme.get("item", "가구/가전") if self.service_id == "kmarket" else theme.get("refund_formatted", "3,840,000 KRW")

        if not landing_url:
            base = BASE_URLS.get(self.service_id, "https://ktrs-service.vercel.app")
            landing_url = f"{base}/?lang={lang}"

        if not self.client:
            return self._fallback_thread(lang, time_slot, theme_name, item_or_refund, landing_url)

        if time_slot == "afternoon":
            # ☕ [2회차 - 오후]: 순수 텍스트 리얼 썰형 (3단 타래, 광고 티 0%)
            prompt = f"""
너는 세계 최고의 메타 스레드(Threads) 바이럴 스토리텔러야.
스레드 피드에서 한국에 사는 외국인들이 읽자마자 1초 만에 "미쳤다 대박"하며 공감하고 리포스트(공유)하게 만드는 [순수 텍스트 썰 3단 타래]를 창작해라.

[서비스]: {'KTRS 마켓 (재한 외국인 0원 무료나눔 중고마켓)' if self.service_id == 'kmarket' else 'EasyTax (한국 국세청 소득세 90% 감면 및 환급)'}
[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target})
[{'주요 품목' if self.service_id == 'kmarket' else '환급 금액'}]: {item_or_refund}
[랜딩 링크]: {landing_url}

### 📝 [오후 3단 텍스트 썰 작성 수칙 (광고 느낌 0%)]:
1. post_1 (1번 메인 썰): 
   - 절대 광고처럼 쓰지 말고, 한국에 사는 외국인이 직접 겪은 생생한 경험담/썰로 시작! (본문에 링크 절대 금지!)
   - 시작 문구에 '🧵👇'를 넣어 아래 답글이 있음을 자연스럽게 유도.
   - 예시(KTRS 마켓): "나 한국 와서 원룸 이사할 때 150만원 아낀 썰 푼다ㅋㅋ 신촌 자취방 가구 0원으로 맞춘 비결 🧵👇"
   - 예시(이지텍스): "한국 공장에서 일하는 형들 주목! 나 이번에 세금 380만원 통장에 꽂힌 실화 푼다 🧵👇"
2. post_2 (2번 팩트/꿀팁 답글): 
   - 1번 썰을 뒷받침하는 구체적인 실전 노하우 팩트 2~3줄 요약.
   - 예시(KTRS 마켓): "1/ 졸업 시즌 대학가에 멀쩡한 침대, 책상 0원에 엄청 쏟아짐. 2/ 버리는 스티커비 아끼려고 무료 나눔하는 문화임."
   - 예시(이지텍스): "1/ 조특법 30조 중소기업 근로자는 소득세 90% 감면임. 2/ 회사 눈치 볼 필요 없이 지난 5년 치도 소급해서 전액 돌려받음."
3. post_3 (3번 링크 투척 답글): 
   - 친절하고 자연스럽게 "물어보는 사람들 있어서 남겨둠" 뉘앙스로 {landing_url} 링크 안내.
   - 예시: "👉 어디서 보냐고 물어봐서 링크 남겨둠! 실시간 확인: {landing_url}"

반드시 아래 JSON 형식으로만 엄격하게 출력해라 (한국어나 영어 설명 금지, 순수 JSON):
{{
  "hook_title": "타래 전체 제목 ({lang_info['name']})",
  "post_type": "pure_story",
  "posts": [
    "1번 메인 썰 내용 (링크 금지, 해시태그 포함) ({lang_info['name']})",
    "2번 핵심 팩트 및 꿀팁 요약 ({lang_info['name']})",
    "3번 링크 안내 답글 ({landing_url} 포함) ({lang_info['name']})"
  ]
}}
"""
        else:
            # 🌅 [1회차 - 아침 11:00] & 🌙 [3회차 - 저녁 21:30]: 카드뉴스 5장 첨부형 (2단 타래)
            slot_mood = "상쾌한 아침/점심 활기찬 생활 정보" if time_slot == "morning" else "퇴근/하교 후 편안한 저녁 모바일 탐색"
            prompt = f"""
너는 세계 최고의 메타 스레드(Threads) 카드뉴스 바이럴 마케터야.
카드뉴스 5장 이미지와 함께 스레드에 업로드할 [후킹 본문 + 0.1초 링크 답글] 2단 세트를 창작해라.

[서비스]: {'KTRS 마켓 (0원 무료나눔)' if self.service_id == 'kmarket' else 'EasyTax (국세청 세무 환급)'}
[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제]: {theme_name} ({target})
[{'품목' if self.service_id == 'kmarket' else '환급액'}]: {item_or_refund}
[랜딩 링크]: {landing_url}
[시간대 분위기]: {slot_mood}

### 📸 [카드뉴스 첨부형 작성 수칙]:
1. post_1 (1번 메인 타래):
   - 카드뉴스 5장 사진을 함께 올릴 본문입니다.
   - 본문에 외부 링크를 넣으면 알고리즘이 노출을 90% 차단하므로, **본문에는 링크를 절대 넣지 마십시오!**
   - 사진 속 내용을 궁금하게 만드는 강력한 후킹 문구 + "👇 링크는 첫 번째 답글 확인!" 안내 + 바이럴 해시태그 3~4개.
2. post_2 (2번 답글 타래):
   - 1번 글이 올라간 직후 봇이 달아줄 링크 댓글.
   - 친절하고 명확한 전환 문구 + {landing_url} 포함.

반드시 아래 JSON 형식으로만 엄격하게 출력해라:
{{
  "hook_title": "스레드 제목 ({lang_info['name']})",
  "post_type": "cardnews_attached",
  "posts": [
    "1번 메인 포스트 본문 (링크 금지, 카드뉴스 안내 및 해시태그 포함) ({lang_info['name']})",
    "2번 답글 타래 링크 댓글 ({landing_url} 포함) ({lang_info['name']})"
  ]
}}
"""

        try:
            res = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            raw = res.text.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw)
            posts = [self._clean_text(p) for p in parsed.get("posts", [])]

            return {
                "service_id": self.service_id,
                "lang": lang,
                "time_slot": time_slot,
                "post_type": parsed.get("post_type", "cardnews_attached" if time_slot != "afternoon" else "pure_story"),
                "hook_title": self._clean_text(parsed.get("hook_title", f"{self.service_id.upper()} Threads")),
                "posts": posts,
                "landing_url": landing_url
            }

        except Exception as e:
            logger.warning(f"[{self.service_id.upper()}] 제미나이 스레드 생성 실패, 폴백 사용: {e}")
            return self._fallback_thread(lang, time_slot, theme_name, item_or_refund, landing_url)

    def _fallback_thread(
        self,
        lang: str,
        time_slot: str,
        theme_name: str,
        item_or_refund: str,
        landing_url: str
    ) -> Dict[str, Any]:
        """무중단 폴백 스레드 템플릿"""
        if self.service_id == "kmarket":
            if time_slot == "afternoon":
                posts = [
                    f"한국 원룸 이사할 때 가구 사지 마세요! 0원에 방 꾸민 썰 푼다 🧵👇 #{lang} #KTRSMarket #SeoulLife",
                    f"신촌/안암 대학가에서 졸업 선배들이 깨끗한 {item_or_refund}를 0원에 다 넘겨주고 갑니다. 17개 언어로 언어 장벽 없이 직거래 가능!",
                    f"👉 오늘 실시간 0원 나눔 매물 확인하기: {landing_url}"
                ]
                p_type = "pure_story"
            else:
                posts = [
                    f"신촌 대학가 자취방 필수 가구 0원 나눔 현장 포착! 📸 (사진 5장 확인)\n놓치면 후회할 0원 나눔, 링크는 아래 첫 댓글 확인! 🧵👇 #KTRSMarket #0won",
                    f"👉 지금 내 주변 0원 나눔 매물 바로 득템하기: {landing_url}"
                ]
                p_type = "cardnews_attached"
        else:
            if time_slot == "afternoon":
                posts = [
                    f"한국에서 일하는 외국인 형들 주목! 세금 {item_or_refund} 돌려받은 실화 푼다 🧵👇 #VisaE9 #HoanThue #KoreaTax",
                    f"조특법 제30조로 5년간 소득세 90% 감면받을 수 있습니다. 회사에 눈치 볼 필요 없이 지난 5년 치도 소급 환급 가능!",
                    f"👉 내 환급금 1분 무료 조회하기: {landing_url}"
                ]
                p_type = "pure_story"
            else:
                posts = [
                    f"외국인 근로자 국세청 소득세 90% 감면 실화! 📸 (세무 카드뉴스 5장 확인)\n신청 안 하면 못 받는 환급금, 링크는 아래 첫 댓글 확인! 🧵👇 #EasyTax #KTRS",
                    f"👉 내 숨은 환급금 1분 무료 계산하기: {landing_url}"
                ]
                p_type = "cardnews_attached"

        return {
            "service_id": self.service_id,
            "lang": lang,
            "time_slot": time_slot,
            "post_type": p_type,
            "hook_title": f"{self.service_id.upper()} {theme_name}",
            "posts": posts,
            "landing_url": landing_url
        }
