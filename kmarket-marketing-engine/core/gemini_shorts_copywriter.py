# -*- coding: utf-8 -*-
"""
[신규 모듈] GeminiShortsCopywriter (core/gemini_shorts_copywriter.py)
• 역할: 숏폼 비디오(9:16) 완성 즉시 4대 글로벌 숏폼 플랫폼
        (유튜브 쇼츠, 틱톡, 인스타그램 릴스, 페이스북 릴스)의 알고리즘 규제와 링크 전환 동선을 100% 해킹하는
        [맞춤 제목 + 설명문/캡션 + 첫댓글/고정댓글 + 바이럴 해시태그 + 전환 링크] 팩 실시간 17개국 현지어 창작
• 알고리즘 해킹 규칙:
  1. 유튜브 쇼츠 (YouTube Shorts): 설명란 링크 클릭 불가 우회 ➔ 프로필 채널 링크 유도 + 고정 댓글(Pinned Comment) 안내
  2. 틱톡 (TikTok): 캡션 링크 클릭 불가 ➔ 프로필 바이오 링크(Bio Link) 시각적 유도
  3. 인스타그램 릴스 (Instagram Reels): 캡션 링크 클릭 불가 ➔ 프로필 상단 링크(@계정) 유도 + 릴스 해시태그
  4. 페이스북 릴스 (Facebook Reels): 본문 링크 0%(도달률 5배 극대화) + 0.1초 첫 번째 댓글(First-Comment) 스텔스 링크
• 원칙: 모듈 분리 원칙(Rule 1), 땜질 코딩 금지(Rule 5) 준수
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY_EASYTAX, GEMINI_API_KEY_KMARKET, LANGUAGES, BASE_URLS

logger = logging.getLogger("GeminiShortsCopywriter")


class GeminiShortsCopywriter:
    """제미나이 기반 17개국 4대 숏폼 플랫폼 카피라이팅 전담 엔진"""
    def __init__(self, service_id: str = "easytax"):
        self.service_id = service_id
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        try:
            from core.gemini_smart_client import GeminiSmartClient
            self.client = GeminiSmartClient(service_id=self.service_id)
            logger.info(f"[{self.service_id.upper()}] 제미나이 숏폼 스마트 카피라이터 초기화 성공 (무료키 1순위)")
        except Exception as e:
            logger.warning(f"제미나이 스마트 클라이언트 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        """폰트 깨짐을 유발하는 비표준 특수 이모지 제거 및 표준 기호 정제"""
        if not text:
            return ""
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        cleaned = emoji_pattern.sub("", text)
        return cleaned.strip()

    def generate_shorts_post_package(
        self,
        service_id: str,
        lang: str,
        scenario: Dict[str, Any],
        refund_formatted: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📢 4대 숏폼 플랫폼(유튜브 쇼츠, 틱톡, 인스타 릴스, 페북 릴스) 맞춤 포스팅 팩 동시 창작
        """
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_name = scenario.get("theme_name", "스페셜 숏폼")
        hook_title = scenario.get("hook_title", "Korea Expat Guide")
        persona_name = scenario.get("persona_name", "외국인 거주자")

        if service_id == "easytax":
            base_domain = BASE_URLS.get("easytax", "https://ktrs-service.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/?lang={lang}"
            amount_str = refund_formatted or "3,840,000 KRW"
            service_desc = (
                f"EasyTax 국세청 조특법 30조 90% 소득세 감면 & 경정청구 세무 환급\n"
                f"- 예상 환급액: {amount_str}\n"
                f"- 핵심 신뢰: 착수금 0원, 환급금 통장 입금 후 정산하는 100% 후불제\n"
                f"- 5년 소멸시효 전 긴급 구제 청구"
            )
        else:
            base_domain = BASE_URLS.get("kmarket", "https://ktrs-market.vercel.app").rstrip("/")
            landing_url = f"{base_domain}/{lang}"
            amount_str = "0 KRW (100% 무료 나눔)"
            item = scenario.get("item", "가구/가전")
            service_desc = (
                f"KTRS Market 외국인 전용 0원 중고 무료 나눔 & 17개국어 실시간 자동번역 직거래\n"
                f"- 무료 나눔 품목: {item}\n"
                f"- 혜택: 150만원 생활비 절약, 한국어 몰라도 17개 언어 실시간 번역 채팅"
            )

        # 트렌드 스크래퍼 해시태그 로드
        from core.trend_scraper import ViralTrendScraper as TrendScraper
        scraper = TrendScraper()
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=10)]
        formatted_hashtags = scraper.format_hashtag_string(service_id, lang, count=10)

        if not self.client:
            return self._fallback_shorts_package(service_id, lang, theme_name, hook_title, landing_url, formatted_hashtags, amount_str)

        prompt = f"""
너는 세계 최고의 4대 숏폼(유튜브 쇼츠, 틱톡, 인스타그램 릴스, 페이스북 릴스) 알고리즘 바이럴 마케팅 거장 디렉터야.
숏폼 플랫폼마다 링크 규제와 클릭 유도 동선이 완전히 다르다!
각 플랫폼의 알고리즘을 100% 해킹하여 영상 조회수와 링크 클릭률(CTR)을 동시에 5배 폭증시키는 [4대 숏폼 채널별 맞춤 포스팅 팩]을 [{lang_info['name']} ({lang_info['native_name']})] 언어로 작성해라.

### 대상 서비스: {service_id.upper()}
[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} (페르소나: {persona_name})
[영상 후킹 제목]: {hook_title}
[서비스 핵심 설명]:
{service_desc}
[공식 링크]: {landing_url}

### [★ 대한민국 체류 외국인 근로자(E-9/E-7) 및 유학생(D-2) 초타깃 규칙]:
- 한국의 공장, 농축산업, 건설업, 제조업 등에서 땀 흘려 일하는 외국인 근로자들이 영상을 보자마자 자기 이야기임을 직감하도록 강력한 현실 공감 후킹을 사용할 것!
- EasyTax: "매달 떼이는 3.3%와 소득세, 조특법 30조로 90% 돌려받는 법", "평균 184만~380만원 통장에 꽂힌 실제 환급 실화"
- KTRS-Market: "원룸/기숙사 가구, 비싼 돈 주고 사지 말고 0원으로 풀세팅하는 법", "150만원 생활비 아끼는 무료나눔 꿀팁"
- 해시태그: 모든 캡션/설명란 맨 끝에 #E9비자 #외국인근로자 #E9visa 등 외국인 근로자 필수 검색 태그가 자연스럽게 녹아들도록 할 것!

### 4대 숏폼 플랫폼별 알고리즘 해킹 규칙:
1. youtube_shorts (유튜브 쇼츠):
   - 제목: 30자 이내 강력한 팩트 후킹 + 맨 끝에 '#Shorts' 필수.
   - 설명란: 숏폼 설명란에는 외부 링크 클릭이 유튜브 정책상 전면 차단되어 있으므로, 2문장 요약 후 반드시 "🔗 프로필 상단 채널 링크를 클릭하면 1분 만에 무료 조회 가능!" 채널 바이오 유도 문구를 넣을 것.
   - 고정 댓글 (pinned_comment): 영상 게시 직후 고정할 공식 안내 텍스트 ({landing_url} 포함).
2. tiktok (틱톡 비디오):
   - 캡션: 첫 1초 후킹 텍스트 + "👉 프로필 링크(Bio Link)에서 지금 확인하세요!" + #fyp #tiktokkorea 등 바이럴 태그.
3. instagram_reels (인스타그램 릴스):
   - 캡션: 감동 스토리 요약 + "🔗 프로필 상단 링크(@{service_id}_official) 클릭 시 1분 만에 확인!" 바이오 링크 유도.
4. facebook_reels (페이스북 릴스):
   - 릴스 본문: 본문에 링크를 넣으면 알고리즘이 노출을 80% 깎아버린다! 본문에는 링크를 절대 넣지 말고 "👇 무료 신청 링크는 첫 번째 댓글(1st comment)을 확인하세요!"로 끝낼 것.
   - 첫 번째 댓글 (first_comment): 봇이 릴스 게시 직후 0.1초 만에 달아줄 스텔스 링크 ({landing_url} 포함).

### 출력 형식 (반드시 아래 JSON 포맷으로만 엄격히 출력):
{{
  "youtube_shorts": {{
    "title": "유튜브 쇼츠 제목 (#Shorts 포함) ({lang_info['name']})",
    "description": "설명란 (채널 프로필 링크 유도) ({lang_info['name']})",
    "pinned_comment": "유튜브 고정 댓글 ({landing_url} 포함) ({lang_info['name']})"
  }},
  "tiktok": {{
    "caption": "틱톡 캡션 (바이오 링크 유도) ({lang_info['name']})"
  }},
  "instagram_reels": {{
    "caption": "인스타 릴스 캡션 (바이오 링크 유도) ({lang_info['name']})"
  }},
  "facebook_reels": {{
    "post_content": "페북 릴스 본문 (링크 0%, 첫댓글 유도) ({lang_info['name']})",
    "first_comment": "페북 릴스 첫 댓글 스텔스 링크 ({landing_url} 포함) ({lang_info['name']})"
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

            yt = res_json.get("youtube_shorts", {})
            tt = res_json.get("tiktok", {})
            ig = res_json.get("instagram_reels", {})
            fb = res_json.get("facebook_reels", {})

            yt_title = self._clean_text(yt.get("title", f"{hook_title} #Shorts"))
            yt_desc = self._clean_text(yt.get("description", ""))
            yt_pin = self._clean_text(yt.get("pinned_comment", f"👉 {landing_url}"))
            tt_cap = self._clean_text(tt.get("caption", ""))
            ig_cap = self._clean_text(ig.get("caption", ""))
            fb_post = self._clean_text(fb.get("post_content", ""))
            fb_comm = self._clean_text(fb.get("first_comment", f"👉 {landing_url}"))

            channels = {
                "youtube_shorts": {
                    "title": yt_title,
                    "description": yt_desc,
                    "pinned_comment": yt_pin,
                    "hashtags": formatted_hashtags,
                    "link_type": "channel_bio_and_pinned"
                },
                "tiktok": {
                    "caption": tt_cap,
                    "hashtags": f"{formatted_hashtags} #fyp #viral",
                    "link_type": "bio_link"
                },
                "instagram_reels": {
                    "caption": ig_cap,
                    "hashtags": f"{formatted_hashtags} #reels #viral",
                    "link_type": "bio_link"
                },
                "facebook_reels": {
                    "post_content": fb_post,
                    "first_comment": fb_comm,
                    "hashtags": formatted_hashtags,
                    "link_type": "first_comment_stealth"
                }
            }

            return {
                "service_id": service_id,
                "lang": lang,
                "hook_title": hook_title,
                "landing_url": landing_url,
                "hashtags": tags_list,
                "hashtags_str": formatted_hashtags,
                "channels": channels
            }
        except Exception as e:
            logger.warning(f"제미나이 숏폼 포스트 패키지 생성 실패, 폴백 사용: {e}")

        return self._fallback_shorts_package(service_id, lang, theme_name, hook_title, landing_url, formatted_hashtags, amount_str)

    def _fallback_shorts_package(
        self,
        service_id: str,
        lang: str,
        theme_name: str,
        hook_title: str,
        landing_url: str,
        hashtags_str: str,
        amount_str: str
    ) -> Dict[str, Any]:
        """API 통신 지연 시 무중단 클린 폴백 숏폼 패키지"""
        from core.trend_scraper import ViralTrendScraper as TrendScraper
        scraper = TrendScraper()
        tags_list = [t.lstrip('#') for t in scraper.get_viral_hashtags(service_id, lang, count=10)]

        if service_id == "easytax":
            yt_title = f"{hook_title} ({amount_str}) #Shorts"
            yt_desc = (
                f"Expat workers in South Korea can claim up to 90% income tax refund under Article 30!\n\n"
                f"✅ Zero Advance Fee: 100% success-based settlement\n"
                f"✅ 5-Year Statute of Limitations\n\n"
                f"🔗 Check your refund in 1 minute via our Channel Bio link!"
            )
            yt_pin = f"👉 Certified Tax Agent Free 1-Minute Calculation: {landing_url}"
            tt_cap = f"Don't lose your {amount_str} tax refund in Korea! ✈️ Check the link in our bio! #fyp"
            ig_cap = f"{hook_title}\n\nClaim your tax refund before the 5-year expiration!\n\n🔗 Link in Bio! (@easytax_official)"
            fb_post = f"{hook_title}\n\nDid you know foreign workers can get up to 90% tax relief?\n\n👇 Check the first comment for the free 1-minute calculation link!"
            fb_comm = f"👉 Estimate your refund for free in 1 minute: {landing_url}"
        else:
            yt_title = f"{hook_title} (0 Won Free) #Shorts"
            yt_desc = (
                f"Furnish your studio room in Korea for 0 Won!\n\n"
                f"✅ Clean furniture & appliances left by graduating students\n"
                f"✅ 17-Language Auto-Translation Chat\n\n"
                f"🔗 Browse 0 Won items near your campus via our Channel Bio link!"
            )
            yt_pin = f"👉 Browse 0 Won free giveaways near you: {landing_url}"
            tt_cap = f"Get free furniture in Korea for 0 Won! ✨ Check the link in our bio! #fyp #korea"
            ig_cap = f"{hook_title}\n\nSave 1,500,000 KRW on room expenses with KTRS Market!\n\n🔗 Link in Bio! (@kmarket_official)"
            fb_post = f"{hook_title}\n\nGraduating students are giving away clean appliances for 0 Won!\n\n👇 Check the first comment to claim today's free items!"
            fb_comm = f"👉 Grab today's free 0 Won items here: {landing_url}"

        channels = {
            "youtube_shorts": {
                "title": yt_title,
                "description": yt_desc,
                "pinned_comment": yt_pin,
                "hashtags": hashtags_str,
                "link_type": "channel_bio_and_pinned"
            },
            "tiktok": {
                "caption": tt_cap,
                "hashtags": f"{hashtags_str} #fyp #viral",
                "link_type": "bio_link"
            },
            "instagram_reels": {
                "caption": ig_cap,
                "hashtags": f"{hashtags_str} #reels #viral",
                "link_type": "bio_link"
            },
            "facebook_reels": {
                "post_content": fb_post,
                "first_comment": fb_comm,
                "hashtags": hashtags_str,
                "link_type": "first_comment_stealth"
            }
        }

        return {
            "service_id": service_id,
            "lang": lang,
            "hook_title": hook_title,
            "landing_url": landing_url,
            "hashtags": tags_list,
            "hashtags_str": hashtags_str,
            "channels": channels
        }

    def generate_shorts_script(
        self,
        service_id: str,
        lang: str,
        scenario: Dict[str, Any],
        refund_formatted: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🎬 [제미나이 100% 자율 AI 디렉터] 숏폼 22초 5~6단 동적 씬 타임라인 자막, 네온 테두리, 배지 및 대본 실시간 창작
        - 다운로드 폴더 고품질 레퍼런스처럼 22초 동안 화면 설명과 배너, 테두리, 하이라이트가 계속 역동적으로 전환
        """
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        theme_name = scenario.get("theme_name", scenario.get("theme_title", "Korea Guide"))
        persona_name = scenario.get("persona_name", "외국인 거주자")

        if service_id == "easytax":
            amount_str = refund_formatted or scenario.get("amount_str") or "3,100,000 KRW"
            prompt = f"""
너는 세계 최고의 바이럴 숏폼 영상 총괄 아트 디렉터이자 카피라이터야.
한국에 거주하는 외국인 근로자(E-9/E-7)를 위해, 국세청 세금 환급(소득세 90% 감면) 22초 숏폼 대본과 [시간대별 6단 역동적 화면 자막 & 배지 & 카드 그래픽 설계도]를 [{lang_info['name']} ({lang_info['native_name']})] 언어로 100% 자율 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제]: {theme_name} (환급 예상액: {amount_str})
[페르소나]: {persona_name}

### 🎬 22초 3단계 음성 발화 대본 규칙:
1. 0~10초 (킬러 후킹): 매달 월급에서 떼인 세금을 KTRS로 {amount_str} 돌려받았다는 실제 감동과 놀라움 발화 (자연스러운 2문장 구어체)
2. 10~18초 (앱 조작 안내): 앱에서 월급만 선택하면 환급금이 1초 만에 계산되어 나온다는 쉬운 조작법 설명 발화
3. 18~22초 (안심 CTA): 선입금 0원, 통장에 돈 들어온 후 정산하는 100% 후불제이며 프로필 링크로 지금 무료 확인하라는 발화

### 💥 [핵심] 22초 6단 역동적 비주얼 아트 디렉팅 (dynamic_scenes) 규칙:
영상이 진행되는 22초 동안 화면 설명이 멈춰있지 않고, 시간대별로 6가지 상이한 비주얼 레이아웃과 배지, 멀티컬러 텍스트, 이모지 스티커, 컨페티 파티클이 쉴 새 없이 전환되어야 한다!
1. Scene 1 (0.0s ~ 3.5s) [layout_type: "center_white_card"]:
   - 화면 중앙(가슴 부위) 화이트 글래스 카드 + 하늘색 네온 테두리 + 상단 캡슐 배지 + 타깃 국가 국기와 한국 국기(예: 🇻🇳 🇰🇷 또는 🇺🇿 🇰🇷) + 블루 하트(💙)
2. Scene 2 (3.5s ~ 7.0s) [layout_type: "top_left_stacked"]:
   - 좌상단 3단 멀티컬러 볼드 스택 텍스트 (예: 1단 초록, 2단 파랑 '90%', 3단 초록) + 상단 혜택 캡슐 배지
3. Scene 3 (7.0s ~ 10.5s) [layout_type: "phone_side_popup"]:
   - 스마트폰 옆 미니 다크 글래스 인증 팝업 카드 (스텝 배지 + 국세청 환급 안내 + 인증 성공 체크마크)
4. Scene 4 (10.5s ~ 15.0s) [layout_type: "bottom_vibrant_card"]:
   - 하단 로열 블루 와이드 카드 + 상단 상승 아이콘(📈) + 초대형 골드/화이트 환급액 ({amount_str}) + 주변 금화 코인(🪙) + 축하 컨페티 파티클(confetti: true)
5. Scene 5 (15.0s ~ 18.5s) [layout_type: "trust_badge_card"]:
   - 딥 앰버/에메랄드 안심 신뢰 카드 (선입금 0원, 통장 입금 후 안심 정산 100% 후불제)
6. Scene 6 (18.5s ~ 22.0s) [layout_type: "ending_cta_card"]:
   - 크림슨 레드 전환 카드 + 골드 글로우 테두리 (프로필 상단 채널 링크 즉시 확인 안내)

⚠️ 모든 자막과 배지 텍스트는 반드시 순수 [{lang_info['name']}] 언어로 작성할 것!
⚠️ 화폐 표기는 반드시 '{amount_str}' 또는 'Won'으로만 표기할 것!

### 아래 JSON 형식으로만 정확히 출력할 것:
```json
{{
  "hook_0_10s": "0~10초 인물 발화 대사 in {lang_info['name']}",
  "app_10_18s": "10~18초 앱 조작 발화 대사 in {lang_info['name']}",
  "cta_18_22s": "18~22초 CTA 발화 대사 in {lang_info['name']}",
  "top_header": "KTRS TAX REFUND • {amount_str}",
  "cta_button_text": "CHECK NOW >",
  "dynamic_scenes": [
    {{
      "scene_index": 1,
      "start_sec": 0.0,
      "end_sec": 3.5,
      "layout_type": "center_white_card",
      "badge": {{
        "text": "인사/후킹 배지 in {lang_info['name']}",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "1행 인사/메인 헤드라인 in {lang_info['name']}", "color": [15, 23, 42]}},
        {{"text": "2행 국가명/타깃 강조 in {lang_info['name']}", "color": [14, 165, 233]}}
      ],
      "sub_text": "서브 설명",
      "decorations": {{
        "emojis": ["국기1", "국기2"],
        "bottom_heart": true,
        "show_dots_pattern": true,
        "confetti": false
      }}
    }},
    {{
      "scene_index": 2,
      "start_sec": 3.5,
      "end_sec": 7.0,
      "layout_type": "top_left_stacked",
      "badge": {{
        "text": "특별 혜택 in {lang_info['name']}",
        "bg_color": [37, 99, 235],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "1단 혜택단어 (예: HOÀN)", "color": [34, 197, 94]}},
        {{"text": "2단 90% (예: 90%)", "color": [59, 130, 246]}},
        {{"text": "3단 세금단어 (예: THUẾ)", "color": [34, 197, 94]}}
      ],
      "sub_text": "조특법 제30조 90% 감면 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 3,
      "start_sec": 7.0,
      "end_sec": 10.5,
      "layout_type": "phone_side_popup",
      "badge": {{
        "text": "1단계 in {lang_info['name']}",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Korea Tax Refund Service", "color": [255, 255, 255]}}
      ],
      "sub_text": "인증 완료 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 4,
      "start_sec": 10.5,
      "end_sec": 15.0,
      "layout_type": "bottom_vibrant_card",
      "badge": {{
        "text": "총 환급액 in {lang_info['name']}",
        "bg_color": [16, 185, 129],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "{amount_str}", "color": [255, 255, 255]}}
      ],
      "sub_text": "국세청 통장 입금 확인 in {lang_info['name']}",
      "decorations": {{
        "confetti": true
      }}
    }},
    {{
      "scene_index": 5,
      "start_sec": 15.0,
      "end_sec": 18.5,
      "layout_type": "trust_badge_card",
      "badge": {{
        "text": "100% 후불제 in {lang_info['name']}",
        "bg_color": [251, 146, 60],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "선입금 0원, 입금 후 정산", "color": [255, 255, 255]}}
      ],
      "sub_text": "안심하고 신청하세요 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 6,
      "start_sec": 18.5,
      "end_sec": 22.0,
      "layout_type": "ending_cta_card",
      "badge": {{
        "text": "지금 무료 확인 in {lang_info['name']}",
        "bg_color": [250, 204, 21],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "프로필 상단 링크를 클릭하세요!", "color": [255, 255, 255]}}
      ],
      "sub_text": "5년 누락 세금 소급 신청 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }}
  ]
}}
```
"""
        else:
            item = scenario.get("item", "가구/가전")
            target_area = scenario.get("target", "대학가")
            prompt = f"""
너는 세계 최고의 바이럴 숏폼 영상 총괄 아트 디렉터이자 카피라이터야.
한국에 거주하는 외국인 유학생 및 근로자를 위해, KTRS 마켓 0원 무료 나눔 22초 숏폼 대본과 [시간대별 6단 역동적 화면 자막 & 배지 & 카드 그래픽 설계도]를 [{lang_info['name']} ({lang_info['native_name']})] 언어로 100% 자율 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target_area})
[무료 품목]: {item} (귀국 선배들이 남긴 100% 무료 나눔)
[페르소나]: {persona_name}

### 🎬 22초 3단계 음성 발화 대본 규칙:
1. 0~10초 (킬러 후킹): 한국에서 깨끗한 {item}을 0원에 직접 무료로 나눔받았다는 감동 실화 발화 (자연스러운 2문장 구어체)
2. 10~18초 (앱 조작 안내): KTRS 마켓 앱에서 0원 매물 피드를 보고 17개 언어 실시간 자동번역 채팅으로 약속 잡는 법 설명 발화
3. 18~22초 (안심 CTA): 150만원 아끼는 꿀팁이며 프로필 링크에서 지금 바로 0원 매물을 확인하라는 발화

### 💥 [핵심] 22초 6단 역동적 비주얼 아트 디렉팅 (dynamic_scenes) 규칙:
영상이 진행되는 22초 동안 화면 설명이 멈춰있지 않고, 시간대별로 6가지 상이한 비주얼 레이아웃과 배지, 멀티컬러 텍스트, 이모지 스티커, 컨페티 파티클이 쉴 새 없이 전환되어야 한다!
1. Scene 1 (0.0s ~ 3.5s) [layout_type: "center_white_card"]:
   - 화면 중앙 화이트 글래스 카드 + 하늘색 네온 테두리 + 0원 무료나눔 배지 + 타깃 국가 국기와 한국 국기 + 블루 하트(💙)
2. Scene 2 (3.5s ~ 7.0s) [layout_type: "top_left_stacked"]:
   - 좌상단 3단 멀티컬러 볼드 스택 텍스트 (예: 1단 '0 WON', 2단 'FREE', 3단 'SHARING') + 150만원 절약 배지
3. Scene 3 (7.0s ~ 10.5s) [layout_type: "phone_side_popup"]:
   - 스마트폰 옆 미니 다크 글래스 인증 팝업 카드 (17개국어 실시간 번역 배지 + 모국어 1:1 직거래 채팅 + 예약 완료 체크마크)
4. Scene 4 (10.5s ~ 15.0s) [layout_type: "bottom_vibrant_card"]:
   - 하단 로열 블루 와이드 카드 + 상단 상승 아이콘(📈) + 초대형 0원/150만원 절약 텍스트 + 주변 금화 코인(🪙) + 축하 컨페티 파티클(confetti: true)
5. Scene 5 (15.0s ~ 18.5s) [layout_type: "trust_badge_card"]:
   - 딥 앰버 안심 직거래 카드 (귀국 선배들이 물려준 깨끗한 나눔 / 캠퍼스 인근 직거래)
6. Scene 6 (18.5s ~ 22.0s) [layout_type: "ending_cta_card"]:
   - 크림슨 레드 전환 카드 + 골드 글로우 테두리 (프로필 상단 링크에서 0원 매물 선착순 가져가기)

⚠️ 모든 자막과 배지 텍스트는 반드시 순수 [{lang_info['name']}] 언어로 작성할 것!
⚠️ 화폐 표기는 반드시 '0원', '0 Won', '0 KRW'로만 표기할 것!

### 아래 JSON 형식으로만 정확히 출력할 것:
```json
{{
  "hook_0_10s": "0~10초 인물 발화 대사 in {lang_info['name']}",
  "app_10_18s": "10~18초 앱 조작 발화 대사 in {lang_info['name']}",
  "cta_18_22s": "18~22초 CTA 발화 대사 in {lang_info['name']}",
  "top_header": "100% FREE GIVEAWAY • K-MARKET",
  "cta_button_text": "GET FREE ITEMS >",
  "dynamic_scenes": [
    {{
      "scene_index": 1,
      "start_sec": 0.0,
      "end_sec": 3.5,
      "layout_type": "center_white_card",
      "badge": {{
        "text": "0원 무료 나눔 in {lang_info['name']}",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "{item} 0원 나눔 in {lang_info['name']}", "color": [15, 23, 42]}},
        {{"text": "한국 생활비 절약 in {lang_info['name']}", "color": [14, 165, 233]}}
      ],
      "sub_text": "귀국 선배들의 무료 나눔",
      "decorations": {{
        "emojis": ["국기1", "국기2"],
        "bottom_heart": true,
        "show_dots_pattern": true,
        "confetti": false
      }}
    }},
    {{
      "scene_index": 2,
      "start_sec": 3.5,
      "end_sec": 7.0,
      "layout_type": "top_left_stacked",
      "badge": {{
        "text": "150만원 절약 in {lang_info['name']}",
        "bg_color": [37, 99, 235],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "0 WON", "color": [250, 204, 21]}},
        {{"text": "FREE", "color": [52, 211, 153]}},
        {{"text": "SHARING", "color": [255, 255, 255]}}
      ],
      "sub_text": "원룸 가구 0원 풀세팅 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 3,
      "start_sec": 7.0,
      "end_sec": 10.5,
      "layout_type": "phone_side_popup",
      "badge": {{
        "text": "17개 언어 번역 in {lang_info['name']}",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Real-time Chat", "color": [255, 255, 255]}}
      ],
      "sub_text": "나눔 예약 완료 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 4,
      "start_sec": 10.5,
      "end_sec": 15.0,
      "layout_type": "bottom_vibrant_card",
      "badge": {{
        "text": "100% 무료 나눔 in {lang_info['name']}",
        "bg_color": [16, 185, 129],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "0 KRW / FREE", "color": [255, 255, 255]}}
      ],
      "sub_text": "캠퍼스 근처 0원 피드 in {lang_info['name']}",
      "decorations": {{
        "confetti": true
      }}
    }},
    {{
      "scene_index": 5,
      "start_sec": 15.0,
      "end_sec": 18.5,
      "layout_type": "trust_badge_card",
      "badge": {{
        "text": "안심 직거래 in {lang_info['name']}",
        "bg_color": [251, 146, 60],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "검증된 선배들의 깨끗한 물품", "color": [255, 255, 255]}}
      ],
      "sub_text": "안전하게 직거래하세요 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }},
    {{
      "scene_index": 6,
      "start_sec": 18.5,
      "end_sec": 22.0,
      "layout_type": "ending_cta_card",
      "badge": {{
        "text": "0원 매물 가져가기 in {lang_info['name']}",
        "bg_color": [250, 204, 21],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "프로필 링크에서 지금 무료 신청!", "color": [255, 255, 255]}}
      ],
      "sub_text": "선착순 무료 나눔 in {lang_info['name']}",
      "decorations": {{
        "confetti": false
      }}
    }}
  ]
}}
```
"""
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt
                )
                raw_text = response.text.strip()
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()
                data = json.loads(raw_text)
                if isinstance(data, dict) and "hook_0_10s" in data:
                    # 정제 및 🎯 [금액 100% 원천 동기화] 검증
                    for k, v in data.items():
                        if isinstance(v, str):
                            data[k] = self._clean_text(v)

                    # 🎯 [3대 요소 금액 100% 원천 동기화] 영수증 = 음성 대본 = 화면 설명/자막 = 상단 헤더
                    if service_id == "easytax" and amount_str:
                        import re
                        # 1. 음성 발화 대본 금액 동기화
                        for field in ["hook_0_10s", "app_10_18s", "cta_18_22s"]:
                            if field in data and isinstance(data[field], str):
                                data[field] = re.sub(r"\b\d{1,3}(,\d{3})+\s*(KRW|Won|원)?\b", amount_str, data[field], flags=re.IGNORECASE)

                        # 2. 상단 헤더 금액 동기화
                        data["top_header"] = f"KTRS TAX REFUND • {amount_str}"

                        # 3. 씬별 자막/헤드라인/설명문 금액 동기화
                        if "dynamic_scenes" in data and isinstance(data["dynamic_scenes"], list):
                            for sc in data["dynamic_scenes"]:
                                if "headline_lines" in sc and isinstance(sc["headline_lines"], list):
                                    for line in sc["headline_lines"]:
                                        if "text" in line and isinstance(line["text"], str):
                                            line["text"] = re.sub(r"\b\d{1,3}(,\d{3})+\s*(KRW|Won|원)?\b", amount_str, line["text"], flags=re.IGNORECASE)
                                if "sub_text" in sc and isinstance(sc["sub_text"], str):
                                    sc["sub_text"] = re.sub(r"\b\d{1,3}(,\d{3})+\s*(KRW|Won|원)?\b", amount_str, sc["sub_text"], flags=re.IGNORECASE)

                    logger.info(f"[{service_id.upper()}:{lang.upper()}] 🎉 제미나이 숏폼 22초 6단 레퍼런스급 동적 씬 타임라인 자막/설계도 실시간 창작 완료 (3대 요소 100% 동기화 금액: {amount_str})!")
                    return data
        except Exception as e:
            logger.warning(f"제미나이 숏폼 동적 대본 생성 에러 ({e}), 기본 스크립트 폴백")

        # 안전 폴백
        return self._fallback_script(service_id, lang, scenario, refund_formatted)

    def _fallback_script(
        self,
        service_id: str,
        lang: str,
        scenario: Dict[str, Any],
        refund_formatted: Optional[str] = None
    ) -> Dict[str, Any]:
        """네트워크 장애 시 최소 안전 폴백 (6단 레퍼런스급 동적 씬 포함)"""
        lang_flags = {"vi": ["🇻🇳", "🇰🇷"], "uz": ["🇺🇿", "🇰🇷"], "km": ["🇰🇭", "🇰🇷"], "th": ["🇹🇭", "🇰🇷"], "id": ["🇮🇩", "🇰🇷"], "ph": ["🇵🇭", "🇰🇷"], "my": ["🇲🇲", "🇰🇷"]}
        emojis = lang_flags.get(lang, ["🇰🇷", "✨"])

        if service_id == "easytax":
            amount_str = refund_formatted or "3,100,000 KRW"
            return {
                "hook_0_10s": f"Did you know taxes deducted from your salary in Korea can be refunded? I just received {amount_str} back via KTRS!",
                "app_10_18s": f"It is so simple! Just enter your salary in the app, and your estimated refund of {amount_str} appears instantly!",
                "cta_18_22s": "Zero upfront fee, 100% pay after refund received! Click the link below to check your refund for free!",
                "top_header": f"KTRS TAX REFUND • {amount_str}",
                "cta_button_text": "CHECK FOR FREE >",
                "dynamic_scenes": [
                    {
                        "scene_index": 1, "start_sec": 0.0, "end_sec": 3.5, "layout_type": "center_white_card",
                        "badge": {"text": "XIN CHÀO!", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "CHÀO CÁC BẠN", "color": [15, 23, 42]},
                            {"text": "VIỆT NAM!", "color": [14, 165, 233]}
                        ],
                        "sub_text": "Cơ hội nhận lại tiền thuế tại Hàn Quốc",
                        "decorations": {"emojis": emojis, "bottom_heart": True, "show_dots_pattern": True, "confetti": False}
                    },
                    {
                        "scene_index": 2, "start_sec": 3.5, "end_sec": 7.0, "layout_type": "top_left_stacked",
                        "badge": {"text": "ƯU ĐÃI ĐẶC BIỆT", "bg_color": [37, 99, 235], "text_color": [255, 255, 255]},
                        "headline_lines": [
                            {"text": "HOÀN", "color": [34, 197, 94]},
                            {"text": "90%", "color": [59, 130, 246]},
                            {"text": "THUẾ", "color": [34, 197, 94]}
                        ],
                        "sub_text": "Điều 30 Luật Thuế: Giảm 90% thuế thu nhập",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 3, "start_sec": 7.0, "end_sec": 10.5, "layout_type": "phone_side_popup",
                        "badge": {"text": "BƯỚC 1", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "Korea Tax Refund Service", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Thành công",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 4, "start_sec": 10.5, "end_sec": 15.0, "layout_type": "bottom_vibrant_card",
                        "badge": {"text": "TỔNG THU NHẬP", "bg_color": [16, 185, 129], "text_color": [255, 255, 255]},
                        "headline_lines": [
                            {"text": f"{amount_str} Won", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Tiền chuyển thẳng vào tài khoản ngân hàng",
                        "decorations": {"confetti": True}
                    },
                    {
                        "scene_index": 5, "start_sec": 15.0, "end_sec": 18.5, "layout_type": "trust_badge_card",
                        "badge": {"text": "100% HẬU MÃI", "bg_color": [251, 146, 60], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "0 Won phí trước, nhận tiền mới trả", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Dịch vụ thuế hợp pháp uy tín tại Hàn Quốc",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 6, "start_sec": 18.5, "end_sec": 22.0, "layout_type": "ending_cta_card",
                        "badge": {"text": "KIỂM TRA MIỄN PHÍ", "bg_color": [250, 204, 21], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "Nhấn vào link trang cá nhân ngay!", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Tra cứu hoàn thuế trong vòng 1 phút",
                        "decorations": {"confetti": False}
                    }
                ]
            }
        else:
            item = scenario.get("item", "가구/가전")
            return {
                "hook_0_10s": f"I just got {item} completely free for 0 Won in Korea! Check the K-Market app right now!",
                "app_10_18s": "It is so easy! Browse daily 0 Won free item feeds and chat safely with 17-language real-time translation!",
                "cta_18_22s": "Save over 1,500,000 Won on living costs! Click the link below to claim free items today!",
                "top_header": "100% FREE GIVEAWAY • K-MARKET",
                "cta_button_text": "GET FREE ITEMS >",
                "dynamic_scenes": [
                    {
                        "scene_index": 1, "start_sec": 0.0, "end_sec": 3.5, "layout_type": "center_white_card",
                        "badge": {"text": "0 WON GIVEAWAY", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": f"0 WON {item.upper()}", "color": [15, 23, 42]},
                            {"text": "FREE IN KOREA!", "color": [14, 165, 233]}
                        ],
                        "sub_text": "100% Free furniture and appliances",
                        "decorations": {"emojis": emojis, "bottom_heart": True, "show_dots_pattern": True, "confetti": False}
                    },
                    {
                        "scene_index": 2, "start_sec": 3.5, "end_sec": 7.0, "layout_type": "top_left_stacked",
                        "badge": {"text": "SAVE 1.5M WON", "bg_color": [37, 99, 235], "text_color": [255, 255, 255]},
                        "headline_lines": [
                            {"text": "0 WON", "color": [250, 204, 21]},
                            {"text": "FREE", "color": [52, 211, 153]},
                            {"text": "SHARING", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Furnish your room without paying money",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 3, "start_sec": 7.0, "end_sec": 10.5, "layout_type": "phone_side_popup",
                        "badge": {"text": "17-LANG CHAT", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "Real-time AI Chat", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Reservation Confirmed",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 4, "start_sec": 10.5, "end_sec": 15.0, "layout_type": "bottom_vibrant_card",
                        "badge": {"text": "TOTAL SAVED", "bg_color": [16, 185, 129], "text_color": [255, 255, 255]},
                        "headline_lines": [
                            {"text": "0 KRW / FREE", "color": [255, 255, 255]}
                        ],
                        "sub_text": "Verified free items near your campus",
                        "decorations": {"confetti": True}
                    },
                    {
                        "scene_index": 5, "start_sec": 15.0, "end_sec": 18.5, "layout_type": "trust_badge_card",
                        "badge": {"text": "SAFE TRADE", "bg_color": [251, 146, 60], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "Clean items from graduating seniors", "color": [255, 255, 255]}
                        ],
                        "sub_text": "100% verified student community",
                        "decorations": {"confetti": False}
                    },
                    {
                        "scene_index": 6, "start_sec": 18.5, "end_sec": 22.0, "layout_type": "ending_cta_card",
                        "badge": {"text": "CLAIM 0 WON ITEM", "bg_color": [250, 204, 21], "text_color": [15, 23, 42]},
                        "headline_lines": [
                            {"text": "Click the link in profile now!", "color": [255, 255, 255]}
                        ],
                        "sub_text": "First-come, first-served free giveaway",
                        "decorations": {"confetti": False}
                    }
                ]
            }

    def format_guide_text(self, package: Dict[str, Any]) -> str:
        """
        🎬 4대 숏폼(유튜브 쇼츠, 틱톡, 인스타그램 릴스, 페이스북 릴스) 배포 가이드 텍스트 렌더링
        """
        service_id = package.get("service_id", "easytax").upper()
        lang = package.get("lang", "en").lower()
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        hook_title = package.get("hook_title", "")
        landing_url = package.get("landing_url", "")
        hashtags_str = package.get("hashtags_str", "")
        channels = package.get("channels", {})

        yt = channels.get("youtube_shorts", {})
        tt = channels.get("tiktok", {})
        ig = channels.get("instagram_reels", {})
        fb = channels.get("facebook_reels", {})

        doc = f"""================================================================================
🎬 [{service_id} 숏폼 영상 4대 SNS 공식 배포 가이드 (제미나이 100% 실시간 자율 창작)]
================================================================================
타깃 언어/국가: {lang_info.get('name', lang.upper())} ({lang.upper()})
영상 후킹 타이틀: {hook_title}
공식 랜딩 링크: {landing_url}
영상 규격: 1080x1920 (9:16 세로 풀HD 숏폼)
🏷️ 17개국 바이럴 해시태그 (복사용): 
{hashtags_str}
================================================================================

[1] 🔴 유튜브 쇼츠 (YouTube Shorts) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [쇼츠 제목 (Title)]
{yt.get('title', '')}

📌 [쇼츠 설명 (Description)]
{yt.get('description', '')}
👉 {landing_url}
{yt.get('hashtags', hashtags_str)}

📌 [고정 댓글 (Pinned Comment)]
{yt.get('pinned_comment', landing_url)}


[2] 🎵 틱톡 (TikTok) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{tt.get('caption', '')}

{tt.get('hashtags', hashtags_str)}

📌 [프로필 바이오 유도]
👉 공식 링크: {landing_url}


[3] 📸 인스타그램 릴스 (Instagram Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{ig.get('caption', '')}

{ig.get('hashtags', hashtags_str)}

📌 [프로필 바이오 유도]
🔗 Bio Link: @{service_id.lower()}_official -> {landing_url}


[4] 📘 페이스북 릴스 (Facebook Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 본문 (링크 0% 노출 극대화)]
{fb.get('post_content', '')}

{fb.get('hashtags', hashtags_str)}

💬 [첫 번째 댓글 (스텔스 링크)]
{fb.get('first_comment', landing_url)}
================================================================================
"""
        return doc

