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
from core.i18n_sns_labels import get_sns_guide_labels

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
각 플랫폼의 알고리즘을 100% 해킹하여 영상 조회수와 링크 클릭률(CTR)을 동시에 5배 폭증시키는 [4대 숏폼 채널별 맞춤 포스팅 팩]을 반드시 100% [{lang_info['name']} ({lang_info['native_name']})] 언어로 작성해라.

### 대상 서비스: {service_id.upper()}
[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} (페르소나: {persona_name})
[영상 후킹 제목]: {hook_title}
[서비스 핵심 내용]:
{service_desc}
[공식 링크]: {landing_url}
[바이럴 해시태그]: {formatted_hashtags}

### 🚨 [언어 무결성 절대 수칙 (STRICT LOCALIZATION)]:
1. 모든 출력(제목, 설명문, 고정댓글, 캡션, 페북본문, 첫댓글)은 100% 순수 [{lang_info['name']} ({lang_info['native_name']})] 언어로만 작성해야 한다!
2. 어떠한 경우에도 한국어 단어(예: 조특법, 조특법 30조, 세금환급, 경정청구, 연말정산, 선입금, 후불제 등)를 한국어 글자(한글) 그대로 외국어 문장 속에 노출하지 마라!
   - '조특법 30조' ➔ 타깃 언어의 법률/세금 감면 규정 용어로 번역 (예: Điều 30 Luật RTT, Soliq qonuni 30-moddasi, Section 30 Tax Relief)
   - '착수금 0원 / 후불제' ➔ 타깃 언어 표현 (예: 0 đồng phí trước, trả sau khi nhận tiền / Oldindan to'lov 0 von, pul tushgach to'lov)
3. 해시태그는 제공된 [{formatted_hashtags}]를 그대로 사용하고, 타깃 언어가 한국어(ko)가 아닌 이상 임의로 한글 해시태그를 추가하지 마라!

### 4대 숏폼 플랫폼별 알고리즘 해킹 규칙:
1. youtube_shorts (유튜브 쇼츠):
   - 제목: 30자 이내 강력한 팩트 후킹 + 맨 끝에 '#Shorts' 필수 in {lang_info['name']}.
   - 설명란: 숏폼 설명란에는 외부 링크 클릭이 불가능하므로, 2문장 요약 후 반드시 채널 프로필 링크 유도 문구를 {lang_info['name']}로 작성.
   - 고정 댓글 (pinned_comment): 영상 게시 직후 고정할 공식 안내 텍스트 ({landing_url} 포함) in {lang_info['name']}.
2. tiktok (틱톡 비디오):
   - 캡션: 첫 1초 후킹 텍스트 + 프로필 바이오 링크(Bio Link) 유도 + 바이럴 태그 in {lang_info['name']}.
3. instagram_reels (인스타그램 릴스):
   - 캡션: 감동 스토리 요약 + 프로필 상단 링크(@{service_id}_official) 유도 in {lang_info['name']}.
4. facebook_reels (페이스북 릴스):
   - 릴스 본문: 본문에 링크를 넣지 말고 "무료 신청 링크는 첫 번째 댓글(1st comment)을 확인하세요!" 유도 in {lang_info['name']}.
   - 첫 번째 댓글 (first_comment): 봇이 릴스 게시 직후 0.1초 만에 달아줄 스텔스 링크 ({landing_url} 포함) in {lang_info['name']}.

### 출력 형식 (반드시 아래 JSON 포맷으로만 엄격히 출력):
{{
  "youtube_shorts": {{
    "title": "Title in {lang_info['name']} (#Shorts)",
    "description": "Description in {lang_info['name']}",
    "pinned_comment": "Pinned comment in {lang_info['name']} ({landing_url})"
  }},
  "tiktok": {{
    "caption": "TikTok caption in {lang_info['name']}"
  }},
  "instagram_reels": {{
    "caption": "Instagram Reels caption in {lang_info['name']}"
  }},
  "facebook_reels": {{
    "post_content": "Facebook Reels post in {lang_info['name']}",
    "first_comment": "First comment stealth link in {lang_info['name']} ({landing_url})"
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
            if lang == "vi":
                yt_title = f"{hook_title} ({amount_str}) #Shorts"
                yt_desc = f"Người lao động nước ngoài tại Hàn Quốc có thể được hoàn lại tới 90% thuế thu nhập!\n\n✅ 0 đồng phí trước: Nhận tiền về tài khoản rồi mới thanh toán\n✅ Thời hạn yêu cầu 5 năm\n\n🔗 Bấm link ở đầu kênh để kiểm tra miễn phí trong 1 phút!"
                yt_pin = f"👉 Kiểm tra hoàn thuế miễn phí trong 1 phút: {landing_url}"
                tt_cap = f"Đừng bỏ lỡ {amount_str} tiền hoàn thuế tại Hàn Quốc! ✈️ Bấm link Bio ngay! #fyp #EasyTax"
                ig_cap = f"{hook_title}\n\nNhận lại tiền thuế trước thời hạn 5 năm!\n\n🔗 Link in Bio! (@easytax_official)"
                fb_post = f"{hook_title}\n\nBạn có biết người lao động có thể lấy lại tới 90% thuế thu nhập?\n\n👇 Xem bình luận đầu tiên để lấy link kiểm tra miễn phí!"
                fb_comm = f"👉 Tính số tiền hoàn thuế miễn phí: {landing_url}"
            elif lang == "uz":
                yt_title = f"{hook_title} ({amount_str}) #Shorts"
                yt_desc = f"Janubiy Koreyadagi chet ellik ishchilar daromad solig'ining 90% gacha qismini qaytarib olishlari mumkin!\n\n✅ Boshlang'ich to'lov 0 von: Pul tushgach to'laysiz\n✅ 5 yillik muddat\n\n🔗 Profil havolasi orqali 1 daqiqada bepul tekshiring!"
                yt_pin = f"👉 Soliq qaytarishni bepul hisoblang: {landing_url}"
                tt_cap = f"Koreyadagi {amount_str} soliq qaytarmangizni boy bermang! ✈️ Bio havolasini bosing! #fyp"
                ig_cap = f"{hook_title}\n\n5 yillik muddat o'tmasdan soliqlaringizni qayтариб oling!\n\n🔗 Link in Bio! (@easytax_official)"
                fb_post = f"{hook_title}\n\nChet ellik ishchilar 90% gacha soliq imtiyoziga ega ekanligini bilasizmi?\n\n👇 Bepul hisoblash uchun birinchi izohni ko'ring!"
                fb_comm = f"👉 Soliq qaytarishni bepul tekshiring: {landing_url}"
            else:
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
            if lang == "vi":
                yt_title = f"{hook_title} (0 Won Miễn Phí) #Shorts"
                yt_desc = f"Trang bị đồ đạc phòng trọ tại Hàn Quốc với giá 0 Won!\n\n✅ Đồ gia dụng, nội thất sạch đẹp từ các tiền bối\n✅ Chat dịch tự động 17 ngôn ngữ\n\n🔗 Xem các món đồ 0 Won gần bạn qua link Bio!"
                yt_pin = f"👉 Nhận đồ 0 Won miễn phí ngay: {landing_url}"
                tt_cap = f"Nhận đồ gia dụng miễn phí 0 Won tại Hàn Quốc! ✨ Link trên Bio! #fyp"
                ig_cap = f"{hook_title}\n\nTiết kiệm 1.500.000 KRW chi phí sinh hoạt với KTRS Market!\n\n🔗 Link in Bio! (@kmarket_official)"
                fb_post = f"{hook_title}\n\nCác tiền bối tốt nghiệp đang tặng lại đồ gia dụng sạch đẹp 0 Won!\n\n👇 Xem bình luận đầu tiên để nhận đồ hôm nay!"
                fb_comm = f"👉 Nhận các món đồ 0 Won hôm nay: {landing_url}"
            elif lang == "uz":
                yt_title = f"{hook_title} (0 Von Bepul) #Shorts"
                yt_desc = f"Koreyada xonangizni 0 vonga jihozlang!\n\n✅ Bitiruvchilar qoldirgan toza maishiy texnika va mebellar\n✅ 17 tilda avtomatik tarjima chat\n\n🔗 Profil havolasi orqali yaqiningizdagi 0 vonlik buyumlarni ko'ring!"
                yt_pin = f"👉 0 vonlik bepul buyumlarni oling: {landing_url}"
                tt_cap = f"Koreyada 0 vonga bepul buyumlar oling! ✨ Bio havolasini bosing! #fyp"
                ig_cap = f"{hook_title}\n\nKTRS Market bilan 1,500,000 von tejab qoling!\n\n🔗 Link in Bio! (@kmarket_official)"
                fb_post = f"{hook_title}\n\nBitiruvchilar bepul maishiy texnikalarni 0 vonga berishmoqda!\n\n👇 Bugungi bepul buyumlarni olish uchun birinchi izohni ko'ring!"
                fb_comm = f"👉 Bugungi 0 vonlik buyumlarni oling: {landing_url}"
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
한국에 거주하는 외국인 근로자(E-9/E-7)를 위해, 국세청 세금 환급(소득세 90% 감면) 22초 숏폼 대본과 [시간대별 6단 역동적 화면 자막 & 배지 & 카드 그래픽 설계도]를 100% [{lang_info['name']} ({lang_info['native_name']})] 언어로 자율 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제]: {theme_name} (환급 예상액: {amount_str})
[페르소나]: {persona_name}

### 🚨 [언어 무결성 절대 수칙]:
1. 대본(hook_0_10s, app_10_18s, cta_18_22s)과 6개 씬의 모든 배지(badge), 헤드라인(headline_lines), 서브 텍스트(sub_text)는 100% [{lang_info['name']}] 언어로만 작성할 것!
2. 어떠한 한국어 단어(한글 문자열)도 외국어 자막이나 대본에 그대로 유출되지 않도록 타깃 언어로 완벽히 번역할 것!
3. 화폐 표기는 '{amount_str}' 또는 '{amount_str.replace("KRW", "Won")}'으로 표기할 것!

### 🎬 22초 3단계 음성 발화 대본 규칙 (in {lang_info['name']}):
1. 0~10초 (킬러 후킹): 매달 월급에서 떼인 세금을 KTRS로 {amount_str} 돌려받았다는 실제 감동과 놀라움 발화 (자연스러운 2문장 구어체)
2. 10~18초 (앱 조작 안내): 앱에서 월급만 선택하면 환급금이 1초 만에 계산되어 나온다는 쉬운 조작법 설명 발화
3. 18~22초 (안심 CTA): 선입금 0원, 통장에 돈 들어온 후 정산하는 100% 후불제이며 프로필 링크로 지금 무료 확인하라는 발화

### 💥 [핵심] 22초 6단 역동적 비주얼 아트 디렉팅 (dynamic_scenes in {lang_info['name']}):
1. Scene 1 (0.0s ~ 3.5s) [layout_type: "center_white_card"]: 인사/후킹 배지 + 메인 헤드라인 2단 + 서브설명
2. Scene 2 (3.5s ~ 7.0s) [layout_type: "top_left_stacked"]: 혜택 배지 + 3단 볼드 스택 텍스트 (예: HOÀN / 90% / THUẾ) + 세금감면 서브설명
3. Scene 3 (7.0s ~ 10.5s) [layout_type: "phone_side_popup"]: 1단계 배지 + Korea Tax Refund Service + 인증성공 서브설명
4. Scene 4 (10.5s ~ 15.0s) [layout_type: "bottom_vibrant_card"]: 환급액 배지 + 초대형 {amount_str} + 통장입금확인 서브설명 + confetti: true
5. Scene 5 (15.0s ~ 18.5s) [layout_type: "trust_badge_card"]: 100% 후불제/안심 배지 + 선입금 0원 안내문 + 안심신청 서브설명
6. Scene 6 (18.5s ~ 22.0s) [layout_type: "ending_cta_card"]: 무료조회 배지 + 프로필 링크 확인 헤드라인 + 소급신청 서브설명

### 아래 JSON 형식으로만 정확히 출력할 것:
```json
{{
  "hook_0_10s": "Narrative speech 0-10s in {lang_info['name']}",
  "app_10_18s": "App guide speech 10-18s in {lang_info['name']}",
  "cta_18_22s": "CTA speech 18-22s in {lang_info['name']}",
  "top_header": "KTRS TAX REFUND • {amount_str}",
  "cta_button_text": "CHECK NOW >",
  "dynamic_scenes": [
    {{
      "scene_index": 1,
      "start_sec": 0.0,
      "end_sec": 3.5,
      "layout_type": "center_white_card",
      "badge": {{
        "text": "Greeting badge in {lang_info['name']}",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Headline line 1 in {lang_info['name']}", "color": [15, 23, 42]}},
        {{"text": "Headline line 2 in {lang_info['name']}", "color": [14, 165, 233]}}
      ],
      "sub_text": "Sub text in {lang_info['name']}",
      "decorations": {{
        "emojis": ["🇰🇷", "✨"],
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
        "text": "Special benefit badge in {lang_info['name']}",
        "bg_color": [37, 99, 235],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "REFUND", "color": [34, 197, 94]}},
        {{"text": "90%", "color": [59, 130, 246]}},
        {{"text": "TAX", "color": [34, 197, 94]}}
      ],
      "sub_text": "90% Income tax relief in {lang_info['name']}",
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
        "text": "STEP 1",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Korea Tax Refund Service", "color": [255, 255, 255]}}
      ],
      "sub_text": "Verified in {lang_info['name']}",
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
        "text": "TOTAL REFUND",
        "bg_color": [16, 185, 129],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "{amount_str}", "color": [255, 255, 255]}}
      ],
      "sub_text": "Bank account deposit confirmed in {lang_info['name']}",
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
        "text": "100% POST-PAY",
        "bg_color": [251, 146, 60],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Zero upfront fee, pay after refund in {lang_info['name']}", "color": [255, 255, 255]}}
      ],
      "sub_text": "Safe legal tax service in {lang_info['name']}",
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
        "text": "CHECK FREE",
        "bg_color": [250, 204, 21],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Click the link in bio now in {lang_info['name']}", "color": [255, 255, 255]}}
      ],
      "sub_text": "5-Year tax retro claim in {lang_info['name']}",
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
한국에 거주하는 외국인 유학생 및 근로자를 위해, KTRS 마켓 0원 무료 나눔 22초 숏폼 대본과 [시간대별 6단 역동적 화면 자막 & 배지 & 카드 그래픽 설계도]를 100% [{lang_info['name']} ({lang_info['native_name']})] 언어로 자율 창작해라.

[타깃 언어]: {lang_info['name']} ({lang_info['native_name']})
[주제/지역]: {theme_name} ({target_area})
[무료 품목]: {item}
[페르소나]: {persona_name}

### 🚨 [언어 무결성 절대 수칙]:
1. 대본(hook_0_10s, app_10_18s, cta_18_22s)과 6개 씬의 모든 배지(badge), 헤드라인(headline_lines), 서브 텍스트(sub_text)는 100% [{lang_info['name']}] 언어로만 작성할 것!
2. 어떠한 한국어 단어(한글 문자열)도 외국어 자막이나 대본에 그대로 유출되지 않도록 타깃 언어로 완벽히 번역할 것!
3. 화폐 표기는 '0 Won' 또는 '0 KRW'로 표기할 것!

### 🎬 22초 3단계 음성 발화 대본 규칙 (in {lang_info['name']}):
1. 0~10초 (킬러 후킹): 한국에서 깨끗한 {item}을 0원에 직접 무료로 나눔받았다는 감동 실화 발화 (자연스러운 2문장 구어체)
2. 10~18초 (앱 조작 안내): KTRS 마켓 앱에서 0원 매물 피드를 보고 17개 언어 실시간 자동번역 채팅으로 약속 잡는 법 설명 발화
3. 18~22초 (안심 CTA): 150만원 아끼는 꿀팁이며 프로필 링크에서 지금 바로 0원 매물을 확인하라는 발화

### 아래 JSON 형식으로만 정확히 출력할 것:
```json
{{
  "hook_0_10s": "Narrative speech 0-10s in {lang_info['name']}",
  "app_10_18s": "App guide speech 10-18s in {lang_info['name']}",
  "cta_18_22s": "CTA speech 18-22s in {lang_info['name']}",
  "top_header": "100% FREE GIVEAWAY • K-MARKET",
  "cta_button_text": "GET FREE ITEMS >",
  "dynamic_scenes": [
    {{
      "scene_index": 1,
      "start_sec": 0.0,
      "end_sec": 3.5,
      "layout_type": "center_white_card",
      "badge": {{
        "text": "FREE GIVEAWAY",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "0 WON {item.upper()}", "color": [15, 23, 42]}},
        {{"text": "Free in Korea in {lang_info['name']}", "color": [14, 165, 233]}}
      ],
      "sub_text": "Free items in {lang_info['name']}",
      "decorations": {{
        "emojis": ["🇰🇷", "🎁"],
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
        "text": "SAVE 1.5M WON",
        "bg_color": [37, 99, 235],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "0 WON", "color": [250, 204, 21]}},
        {{"text": "FREE", "color": [52, 211, 153]}},
        {{"text": "SHARING", "color": [255, 255, 255]}}
      ],
      "sub_text": "Room items for 0 Won in {lang_info['name']}",
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
        "text": "17-LANG CHAT",
        "bg_color": [52, 211, 153],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Real-time AI Chat", "color": [255, 255, 255]}}
      ],
      "sub_text": "Reservation Confirmed in {lang_info['name']}",
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
        "text": "TOTAL SAVED",
        "bg_color": [16, 185, 129],
        "text_color": [255, 255, 255]
      }},
      "headline_lines": [
        {{"text": "0 KRW / FREE", "color": [255, 255, 255]}}
      ],
      "sub_text": "Free feed near campus in {lang_info['name']}",
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
        "text": "SAFE TRADE",
        "bg_color": [251, 146, 60],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Clean items from seniors in {lang_info['name']}", "color": [255, 255, 255]}}
      ],
      "sub_text": "Verified student community in {lang_info['name']}",
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
        "text": "CLAIM 0 WON ITEM",
        "bg_color": [250, 204, 21],
        "text_color": [15, 23, 42]
      }},
      "headline_lines": [
        {{"text": "Click profile link now in {lang_info['name']}", "color": [255, 255, 255]}}
      ],
      "sub_text": "First-come giveaway in {lang_info['name']}",
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
            if lang == "uz":
                return {
                    "hook_0_10s": f"Koreyada har oy oyligingizdan ushlab qolingan soliqlarni qaytarib olishingiz mumkinligini bilasizmi? KTRS orqali {amount_str} qaytarib oldim!",
                    "app_10_18s": f"Juda oson! Ilovada oyligingizni kiritsangiz, {amount_str} miqdoridagi soliq qaytarmasi 1 daqiqada hisoblanadi!",
                    "cta_18_22s": "Boshlang'ich to'lov 0 von, faqat pul tushgach to'laysiz! Profil havolasi orqali bepul tekshiring!",
                    "top_header": f"KTRS TAX REFUND • {amount_str}",
                    "cta_button_text": "BEPUL TEKSHIRISH >",
                    "dynamic_scenes": [
                        {
                            "scene_index": 1, "start_sec": 0.0, "end_sec": 3.5, "layout_type": "center_white_card",
                            "badge": {"text": "SALOM!", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                            "headline_lines": [
                                {"text": "YURTDOSHLAR DIQQATIGA", "color": [15, 23, 42]},
                                {"text": "O'ZBEKISTON!", "color": [14, 165, 233]}
                            ],
                            "sub_text": "Koreyada soliqni qaytarib olish imkoniyati",
                            "decorations": {"emojis": ["🇺🇿", "🇰🇷"], "bottom_heart": True, "show_dots_pattern": True, "confetti": False}
                        },
                        {
                            "scene_index": 2, "start_sec": 3.5, "end_sec": 7.0, "layout_type": "top_left_stacked",
                            "badge": {"text": "MAXSUS IMTIYOZ", "bg_color": [37, 99, 235], "text_color": [255, 255, 255]},
                            "headline_lines": [
                                {"text": "QAYTARISH", "color": [34, 197, 94]},
                                {"text": "90%", "color": [59, 130, 246]},
                                {"text": "SOLIQ", "color": [34, 197, 94]}
                            ],
                            "sub_text": "Daromad solig'idan 90% imtiyoz",
                            "decorations": {"confetti": False}
                        },
                        {
                            "scene_index": 3, "start_sec": 7.0, "end_sec": 10.5, "layout_type": "phone_side_popup",
                            "badge": {"text": "1-QADAM", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                            "headline_lines": [
                                {"text": "Korea Tax Refund Service", "color": [255, 255, 255]}
                            ],
                            "sub_text": "Muvaffaqiyatli",
                            "decorations": {"confetti": False}
                        },
                        {
                            "scene_index": 4, "start_sec": 10.5, "end_sec": 15.0, "layout_type": "bottom_vibrant_card",
                            "badge": {"text": "UMUMIY QAYTARMA", "bg_color": [16, 185, 129], "text_color": [255, 255, 255]},
                            "headline_lines": [
                                {"text": f"{amount_str}", "color": [255, 255, 255]}
                            ],
                            "sub_text": "Bank hisobiga to'g'ridan-to'g'ri o'tkaziladi",
                            "decorations": {"confetti": True}
                        },
                        {
                            "scene_index": 5, "start_sec": 15.0, "end_sec": 18.5, "layout_type": "trust_badge_card",
                            "badge": {"text": "100% KAFOLAT", "bg_color": [251, 146, 60], "text_color": [15, 23, 42]},
                            "headline_lines": [
                                {"text": "Oldindan to'lov 0 von, pul tushgach to'lov", "color": [255, 255, 255]}
                            ],
                            "sub_text": "Koreyada qonuniy va ishonchli xizmat",
                            "decorations": {"confetti": False}
                        },
                        {
                            "scene_index": 6, "start_sec": 18.5, "end_sec": 22.0, "layout_type": "ending_cta_card",
                            "badge": {"text": "BEPUL TEKSHIRISH", "bg_color": [250, 204, 21], "text_color": [15, 23, 42]},
                            "headline_lines": [
                                {"text": "Profil havolasini hoziroq bosing!", "color": [255, 255, 255]}
                            ],
                            "sub_text": "1 daqiqada soliq qaytarmasini hisoblang",
                            "decorations": {"confetti": False}
                        }
                    ]
                }
            else: # vi or generic
                return {
                    "hook_0_10s": f"Bạn có biết tiền thuế bị trừ hàng tháng tại Hàn Quốc có thể được hoàn lại không? Tôi vừa nhận lại {amount_str} qua KTRS!",
                    "app_10_18s": f"Rất đơn giản! Chỉ cần nhập lương trong ứng dụng, số tiền hoàn {amount_str} sẽ xuất hiện ngay lập tức!",
                    "cta_18_22s": "0 đồng phí trước, nhận tiền rồi mới trả! Bấm vào link trang cá nhân để kiểm tra miễn phí!",
                    "top_header": f"KTRS TAX REFUND • {amount_str}",
                    "cta_button_text": "KIỂM TRA MIỄN PHÍ >",
                    "dynamic_scenes": [
                        {
                            "scene_index": 1, "start_sec": 0.0, "end_sec": 3.5, "layout_type": "center_white_card",
                            "badge": {"text": "XIN CHÀO!", "bg_color": [52, 211, 153], "text_color": [15, 23, 42]},
                            "headline_lines": [
                                {"text": "CHÀO CÁC BẠN", "color": [15, 23, 42]},
                                {"text": "VIỆT NAM!", "color": [14, 165, 233]}
                            ],
                            "sub_text": "Cơ hội nhận lại tiền thuế tại Hàn Quốc",
                            "decorations": {"emojis": ["🇻🇳", "🇰🇷"], "bottom_heart": True, "show_dots_pattern": True, "confetti": False}
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
                                {"text": f"{amount_str}", "color": [255, 255, 255]}
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
        🎬 4대 숏폼(유튜브 쇼츠, 틱톡, 인스타그램 릴스, 페이스북 릴스) 100% 현지어 배포 가이드 텍스트 렌더링
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

        labels = get_sns_guide_labels(lang)

        doc = f"""================================================================================
🎬 [{service_id} - {labels['header_title']}]
================================================================================
{labels['target_lang']}: {lang_info.get('native_name', lang_info.get('name', lang.upper()))} ({lang_info.get('name', lang.upper())})
{labels['hook_title']}: {hook_title}
{labels['landing_url']}: {landing_url}
{labels['video_spec']}
🏷️ {labels['hashtags_label']}: 
{hashtags_str}
================================================================================

{labels['yt_section']}
--------------------------------------------------------------------------------
{labels['yt_title']}
{yt.get('title', '')}

{labels['yt_desc']}
{yt.get('description', '')}
👉 {landing_url}
{yt.get('hashtags', hashtags_str)}

{labels['yt_pinned']}
{yt.get('pinned_comment', landing_url)}


{labels['tt_section']}
--------------------------------------------------------------------------------
{labels['tt_caption']}
{tt.get('caption', '')}

{tt.get('hashtags', hashtags_str)}

{labels['tt_bio_guide']}
{labels['official_link_label']}: {landing_url}


{labels['ig_section']}
--------------------------------------------------------------------------------
{labels['ig_caption']}
{ig.get('caption', '')}

{ig.get('hashtags', hashtags_str)}

{labels['ig_bio_guide']}
🔗 Bio Link: @{service_id.lower()}_official -> {landing_url}


{labels['fb_section']}
--------------------------------------------------------------------------------
{labels['fb_post']}
{fb.get('post_content', '')}

{fb.get('hashtags', hashtags_str)}

{labels['fb_first_comment']}
{fb.get('first_comment', landing_url)}
================================================================================
"""
        return doc

