# -*- coding: utf-8 -*-
"""
[신규 모듈] GeminiDomesticSNSCopywriter (core/gemini_domestic_sns_copywriter.py)
=============================================================================
• 역할: 국내 3대 브랜드(💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)의
        숏폼 및 카드뉴스 송출 시, 4대 SNS 채널(인스타그램, 페이스북, 유튜브 쇼츠, 네이버 클립)의
        알고리즘 도달률과 전환율을 극대화하는 [고관여 스토리텔링 캡션 + 실시간 급상승 트렌드 해시태그] 실시간 패키징 엔진
• 핵심 원칙:
  1. [실시간 트렌드 결합]: Google Trends KR + Naver 실시간 검색어와 브랜드 4단 매트릭스를 융합하여 15~20개 바이럴 해시태그 조립
  2. [제미나이 4단계 고관여 카피]:
     - 🎣 1단계: 시선 강탈 상황 후킹 & 현실 공감대 형성
     - 💡 2단계: 핵심 실전 인사이트 & 흥미 유발 3줄 브리핑
     - ✨ 3단계: 자연스러운 서비스 해결책 연결
     - 🔍 4단계: 공식 네이버 검색 키워드 유도 (Zero URL 원칙 & 명칭 철통 준수)
  3. [금지어 필터링 100% 무결성]: '한정 이벤트', '선착순 마감' 등 근거 없는 프로모션 할루시네이션 전면 차단
"""

import os
import re
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("GeminiDomesticSNSCopywriter")

FORBIDDEN_WORDS = [
    "한정 이벤트", "선착순 마감", "파격 할인", "수강생 모집",
    "VIP 리딩방", "원금 보장", "수익률 100% 보장", "사은품 증정",
    "오늘만 이 가격", "마감 임박", "선착순 100명", "선착순 50명"
]

BRAND_SPECS = {
    "aura": {
        "name": "💖 Aura AI 데이팅",
        "official_keyword": "아우라AI데이팅",
        "url": "https://aura-ai-dating.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/zkfnth01",
        "cta_label": "공식 라운지(체험)",
        "ig_handle": "@aura_ai_dating",
        "core_value": "유령회원 없는 50:50 황금 성비 청정 라운지, Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개) 현재 100% 무료 지원 중",
        "target": "2030 직장인 및 대학생 싱글 남녀",
        "search_phrase": "네이버에 [아우라AI데이팅] 한번 검색해보세요"
    },
    "insurance": {
        "name": "🛡️ 보험 리밸런스",
        "official_keyword": "보험 리밸런스",
        "url": "https://insure-rebalance.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/thefirst-life",
        "cta_label": "0.1초 비교(진단)",
        "ig_handle": "@goldmomofficial",
        "core_value": "34개 보험사 실시간 비교 견적, 숨은 중복 특약 정리, 월 15만원 보험료 다이어트 자가진단",
        "target": "2040 직장인 및 가계부 고정지출 절약이 필요한 금융 소비자",
        "search_phrase": "네이버에 [보험 리밸런스] 검색해보세요"
    },
    "stock": {
        "name": "📈 StockMaster AI",
        "official_keyword": "스톡마스터 AI",
        "url": "https://stockmaster-ai.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/stockmaster_ai",
        "cta_label": "AI 수급 분석(체험)",
        "ig_handle": "@stockmaster_ai",
        "core_value": "세력 체결강도 120% 수급 포착, 외인/기관 실시간 순매수 레이더, AI 자동 리스크가드 손절 공식",
        "target": "스마트한 퀀트 데이터 기반 국내/해외 주식 투자자",
        "search_phrase": "네이버에 [스톡마스터 AI] 검색해보세요"
    }
}


class GeminiDomesticSNSCopywriter:
    """국내 3대 브랜드 전용 제미나이 4대 SNS 고관여 캡션 & 실시간 트렌드 해시태그 카피라이터"""

    def __init__(self, brand: str = "aura"):
        self.brand = brand.lower()
        self.spec = BRAND_SPECS.get(self.brand, BRAND_SPECS["aura"])
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        try:
            from core.gemini_smart_client import GeminiSmartClient
            self.client = GeminiSmartClient(service_id=self.brand)
        except Exception as e:
            logger.warning(f"[{self.brand.upper()}] GeminiSmartClient 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        for fw in FORBIDDEN_WORDS:
            text = text.replace(fw, "")
        return text.strip()

    def fetch_live_trend_keywords(self) -> List[str]:
        """Google Trends KR 및 Naver 자동완성 실시간 인기 키워드 수집"""
        trends = []
        try:
            url = "https://trends.google.com/trending/rss?geo=KR"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                xml_text = resp.read().decode("utf-8", errors="ignore")
                root = ET.fromstring(xml_text)
                for item in root.findall("./channel/item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        w = title.text.strip().replace(" ", "").replace("#", "")
                        if w and len(w) < 12 and f"#{w}" not in trends:
                            trends.append(f"#{w}")
                    if len(trends) >= 5:
                        break
        except Exception:
            pass

        fallback = ["#실시간트렌드", "#인기급상승", "#2030트렌드", "#일상꿀팁", "#핫이슈"]
        for fb in fallback:
            if fb not in trends and len(trends) < 5:
                trends.append(fb)

        return trends[:5]

    def build_hybrid_hashtags(self, topic_id: int, count: int = 18) -> List[str]:
        """실시간 트렌드 + 브랜드 전용 4단 매트릭스 결합 해시태그 풀 생성"""
        tags = []
        # 1. 브랜드 공식 태그
        kw = self.spec["official_keyword"].replace(" ", "")
        tags.append(f"#{kw}")
        if self.brand == "aura":
            tags.extend(["#아우라AI데이팅", "#소개팅", "#연애꿀팁"])
        elif self.brand == "insurance":
            tags.extend(["#보험리밸런스", "#보험비교", "#재테크꿀팁"])
        else:
            tags.extend(["#스톡마스터AI", "#주식투자", "#퀀트투자"])

        # 2. 브랜드별 매트릭스 롱테일 태그 로드
        try:
            if self.brand == "aura":
                from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
                matrix_tags = AuraHashtagMatrix.get_instagram_hashtags(topic_id=topic_id, count=10)
                tags.extend(matrix_tags)
            elif self.brand == "insurance":
                from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix
                matrix_tags = InsuranceHashtagMatrix.get_instagram_hashtags(topic_id=topic_id, count=10)
                tags.extend(matrix_tags)
            elif self.brand == "stock":
                from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
                matrix_tags = StockHashtagMatrix.get_instagram_hashtags(topic_id=topic_id, count=10)
                tags.extend(matrix_tags)
        except Exception as me:
            logger.warning(f"매트릭스 태그 로드 경고: {me}")

        # 3. 실시간 트렌드 태그 융합
        live_trends = self.fetch_live_trend_keywords()
        tags.extend(live_trends)

        # 4. 중복 제거
        seen = set()
        unique = []
        for t in tags:
            clean_t = t.strip()
            if not clean_t.startswith("#"):
                clean_t = f"#{clean_t}"
            if clean_t not in seen:
                seen.add(clean_t)
                unique.append(clean_t)
            if len(unique) >= count:
                break
        return unique

    def generate_full_package(
        self,
        topic_id: int,
        topic_title: str,
        media_type: str = "shorts"
    ) -> Dict[str, Any]:
        """
        🚀 제미나이 4대 플랫폼 맞춤 캡션 + 실시간 트렌드 해시태그 패키지 생성
        """
        hashtags = self.build_hybrid_hashtags(topic_id=topic_id, count=18)
        hashtag_str = " ".join(hashtags)
        short_hashtag_str = " ".join(hashtags[:8])

        # 제미나이 호출 프롬프트 구성
        prompt = f"""
당신은 대한민국 최고의 2030 바이럴 SNS 마케팅 총괄 크리에이티브 디렉터입니다.
아래 브랜드와 주제를 바탕으로 사람들의 호기심과 공감을 강하게 자극하여 조회수와 댓글을 폭발시키는 [4대 SNS 채널별 고관여 카피 패키지]를 작성하십시오.

### [브랜드 규격]
- 브랜드: {self.spec['name']}
- 공식 네이버 검색 키워드: [{self.spec['official_keyword']}]
- 핵심 가치 및 특장점: {self.spec['core_value']}
- 타깃층: {self.spec['target']}
- 공식 검색 유도 문구: "{self.spec['search_phrase']}"

### [콘텐츠 정보]
- 유형: {'9:16 숏폼 영상' if media_type == 'shorts' else '1080x1350 5장 카드뉴스 매거진'}
- 주제 #{topic_id}: {topic_title}

### [절대 수칙 - 위반 시 실격]
1. 단순 3줄 요약 금지! 독자가 몰입할 수 있도록 현실감 넘치는 상황 묘사, 공감대 후킹, 3가지 핵심 실전 팁을 스토리텔링으로 구성하십시오.
2. 금지어 절대 사용 금지: {', '.join(FORBIDDEN_WORDS)}
3. 네이버 공식 검색어는 무조건 정확히 [{self.spec['official_keyword']}]를 각인시키십시오.

### [출력 JSON 형식] (반드시 순수 JSON만 반환):
{{
  "ig_caption": "인스타그램용 매력적인 스토리텔링 본문 (이모지 풍부, 상황 공감 ➔ 3대 꿀팁 ➔ 검색 CTA)",
  "fb_caption": "페이스북용 몰입형 피드 본문 (긴 호흡 서사, 높은 체류시간 유도 ➔ 첫 댓글 링크 안내)",
  "fb_comment": "페이스북 첫 댓글용 안내 문구 (검색어 강조 + 링크 안내)",
  "yt_desc": "유튜브 쇼츠용 검색 최적화 설명문 (후킹 + 3줄 요약 + 공식 검색어 안내)",
  "yt_pinned": "유튜브 고정 댓글 문구 (시청자 반응 유도 + 검색어 안내)",
  "clip_desc": "네이버 클립용 300자 이내 고밀도 압축 카피"
}}
"""
        if self.client:
            try:
                from google.genai import types
                cfg = types.GenerateContentConfig(temperature=0.7, max_output_tokens=1500)
                response = self.client.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=cfg
                )
                text = response.text.strip() if hasattr(response, "text") else ""
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    raw_data = json.loads(json_match.group(0))
                    ig_c = self._clean_text(raw_data.get("ig_caption", ""))
                    fb_c = self._clean_text(raw_data.get("fb_caption", ""))
                    fb_cm = self._clean_text(raw_data.get("fb_comment", ""))
                    yt_d = self._clean_text(raw_data.get("yt_desc", ""))
                    yt_p = self._clean_text(raw_data.get("yt_pinned", ""))
                    cl_d = self._clean_text(raw_data.get("clip_desc", ""))

                    if ig_c and fb_c:
                        return {
                            "main_title": topic_title,
                            "hashtags": hashtags,
                            "youtube": {
                                "title": f"{topic_title} #{self.spec['official_keyword'].replace(' ', '')} #Shorts",
                                "desc": f"{yt_d}\n\n🔍 {self.spec['search_phrase']}\n공식 웹: {self.spec['url']}\n\n{short_hashtag_str}",
                                "pinned": yt_p or f"👇 3초 무료 진단 바로가기: [채널 홈 상단 링크] 클릭!\n🔍 네이버 검색: [{self.spec['official_keyword']}] (공식: {self.spec['url']})"
                            },
                            "naver_clip": {
                                "title": topic_title,
                                "desc": f"{cl_d}\n\n📝 상세 칼럼(블로그): {self.spec['naver_blog_url']}\n🚀 {self.spec['cta_label']}: {self.spec['url']}\n🔍 네이버 검색창: [{self.spec['official_keyword']}]\n\n{short_hashtag_str}"[:295]
                            },
                            "meta": {
                                "ig_caption": f"{ig_c}\n\n👇 3초 무료 자가진단 바로가기\n👉 상단 프로필({self.spec['ig_handle']}) 링크를 터치하세요!\n🔍 {self.spec['search_phrase']}\n\n{hashtag_str}",
                                "fb_caption": f"{fb_c}\n\n👉 3초 자가진단 바로가기: {self.spec['url']}\n🔍 {self.spec['search_phrase']}\n\n{hashtag_str}",
                                "fb_comment": fb_cm or f"👉 {self.spec['name']} 공식 바로가기: {self.spec['url']}\n네이버에 [{self.spec['official_keyword']}] 검색하셔도 바로 나옵니다!"
                            }
                        }
            except Exception as ge:
                logger.warning(f"[{self.brand.upper()}] 제미나이 캡션 생성 예외 ({ge}) -> 프리미엄 고관여 폴백 가동")

        # Fallback (오프라인/에러 시에도 성의 있는 4단계 고관여 스토리텔링 생성)
        return self._generate_rich_fallback(topic_id, topic_title, media_type, hashtags, hashtag_str, short_hashtag_str)

    def _generate_rich_fallback(
        self,
        topic_id: int,
        topic_title: str,
        media_type: str,
        hashtags: List[str],
        hashtag_str: str,
        short_hashtag_str: str
    ) -> Dict[str, Any]:
        """제미나이 미응답 시 고품격 4단계 스토리텔링 폴백 패키지"""
        if self.brand == "aura":
            ig_c = (
                f"💖 [Aura 데이팅 매거진] {topic_title}\n\n"
                f"소개팅 나가서 ‘아차… 망했다’ 싶은 순간, 다들 한 번쯤 있으시죠? 🤦‍♀️\n"
                f"사진이랑 실물이 너무 달라서 당황스럽거나 대화가 뚝뚝 끊겨 어색할 때,\n"
                f"눈치 보며 2차까지 억지로 끌려가지 않고 매너 있게 탈출하는 실전 치트키를 공개합니다!\n\n"
                f"✨ 실전 핵심 포인트 3가지:\n"
                f"1. 어색한 침묵을 3초 만에 깨는 센스 있는 오프너 대화법\n"
                f"2. 상대방 자존심 안 상하게 정중히 빠져나오는 '긴급 업무 호출' 명분\n"
                f"3. 유령회원 제로! 50:50 남녀 황금 성비 청정 라운지 활용법\n\n"
                f"외모보다 통하는 대화와 자연스러운 매력 어필로 솔로 탈출 성공하세요 ✨\n\n"
                f"👉 {topic_title.split(' ')[0]}은 물론! Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개)을 현재 100% 무료 지원 중!\n"
                f"👉 상단 프로필({self.spec['ig_handle']}) 링크를 터치하세요!\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_c = (
                f"💖 [2030 소개팅 필독] {topic_title}\n\n"
                f"주말 황금 같은 시간, 불편한 소개팅 자리에서 억지로 버티고 계신가요?\n"
                f"마음에도 없는 밥값 내고 어색함에 고통받는 솔로들을 위한 세련된 매너 탈출 꿀팁 📖\n\n"
                f"✔️ 소개팅 어색함 깨는 실전 대화 치트키\n"
                f"✔️ 50:50 황금 성비 청정 라운지에서 진짜 통하는 인연 찾기\n\n"
                f"👉 {topic_title.split(' ')[0]}은 물론! Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개)을 현재 100% 무료 지원 중!\n"
                f"👉 공식 라운지 바로가기: {self.spec['url']}\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_cm = f"👉 Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개) 현재 100% 무료 지원 중! 공식: {self.spec['url']}\n네이버에 [{self.spec['official_keyword']}] 검색하셔도 바로 나옵니다!"
            yt_d = (
                f"{topic_title}\n\n"
                f"2030 솔로 남녀를 위한 현실 연애 & 소개팅 실전 치트키 🎬\n"
                f"{topic_title.split(' ')[0]}은 물론! Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개)을 현재 100% 무료 지원 중!\n\n"
                f"🔍 네이버에 👉 [{self.spec['official_keyword']}] 검색해보세요!\n"
                f"공식 라운지: {self.spec['url']}\n\n"
                f"{short_hashtag_str}"
            )
            yt_p = f"📌 {topic_title.split(' ')[0]}은 물론! Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개)을 현재 100% 무료 지원 중! 네이버에 [{self.spec['official_keyword']}] 검색해보세요! (공식: {self.spec['url']})"
            cl_d = (
                f"💖 {topic_title}\n\n"
                f"{topic_title.split(' ')[0]}은 물론! Aura의 모든 기능(AI 화보, 매칭, 쪽지, 번개)을 현재 100% 무료 지원 중!\n\n"
                f"📝 상세 칼럼(블로그): {self.spec['naver_blog_url']}\n"
                f"🚀 {self.spec['cta_label']}: {self.spec['url']}\n"
                f"🔍 네이버 검색창: [{self.spec['official_keyword']}]\n\n"
                f"{short_hashtag_str}"
            )[:295]

        elif self.brand == "insurance":
            ig_c = (
                f"🛡️ [보험 리밸런스 금융 리포트] {topic_title}\n\n"
                f"매달 꼬박꼬박 빠져나가는 보험료, 제대로 보장받고 계신가요? 💸\n"
                f"내가 어떤 특약에 가입되어 있는지도 모른 채 불필요한 중복 가입으로\n"
                f"월 수십만 원의 소중한 월급이 줄줄 새고 있는 분들이 정말 많습니다.\n\n"
                f"💡 지금 바로 점검해야 할 핵심 3가지:\n"
                f"1. 4세대 실손 전환 손익 분석 및 비급여 특약 실속 체크\n"
                f"2. 운전자보험 1만원대로 민식이법/변호사 선임비용 완벽 대비\n"
                f"3. 34개 국내 전 보험사 실시간 비교 견적으로 월 15만원 다이어트\n\n"
                f"👇 34개 보험사 실시간 최저가 비교 & 새는 돈 계산기\n"
                f"👉 상단 프로필({self.spec['ig_handle']}) 링크를 터치하세요! (스팸전화 0건)\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_c = (
                f"🛡️ [직장인 재테크 꿀팁] {topic_title}\n\n"
                f"월급은 그대로인데 고정지출만 늘어난다면? 가장 먼저 '보험료'부터 다이어트해야 합니다!\n"
                f"중복 가입된 특약만 깔끔하게 정리해도 매달 10~15만 원의 여유 자금이 생깁니다.\n\n"
                f"✔️ 34개 전 보험사 실시간 객관적 비교 견적\n"
                f"✔️ 불필요한 거품 싹 뺀 가성비 실손/운전자/암보험 설계\n\n"
                f"👉 34개사 실시간 가격표 바로가기: {self.spec['url']}\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_cm = f"👉 34개 보험사 실시간 최저가 비교견적: {self.spec['url']}\n네이버에 [{self.spec['official_keyword']}] 검색해보세요!"
            yt_d = (
                f"{topic_title}\n\n"
                f"가계부 고정지출 1위 보험료 싹 다이어트하는 실전 공식 📊\n"
                f"34개 보험사 실시간 데이터 기반 최저가 분석!\n\n"
                f"🔍 네이버 검색창에 👉 [{self.spec['official_keyword']}] 검색!\n"
                f"공식 진단: {self.spec['url']}\n\n"
                f"{short_hashtag_str}"
            )
            yt_p = f"📌 34개 보험사 실시간 비교 견적 데이터는 네이버에 [{self.spec['official_keyword']}] 검색하시면 바로 확인하실 수 있습니다."
            cl_d = (
                f"🛡️ {topic_title}\n\n"
                f"📝 상세 칼럼(블로그): {self.spec['naver_blog_url']}\n"
                f"🚀 {self.spec['cta_label']}: {self.spec['url']}\n"
                f"🔍 네이버 검색창: [{self.spec['official_keyword']}]\n\n"
                f"{short_hashtag_str}"
            )[:295]

        else:  # stock
            ig_c = (
                f"📈 [StockMaster AI 퀀트 리포트] {topic_title}\n\n"
                f"급등주 따라 들어갔다가 고점에 물려 고통받고 계신가요? 📉\n"
                f"개인 투자자가 시장에서 승리하려면 '감'이 아닌 '수급 데이터'를 봐야 합니다.\n"
                f"외인과 기관의 실시간 쌍끌이 순매수와 세력 체결강도 120% 돌파 종목을 정밀 포착합니다.\n\n"
                f"📊 퀀트 실전 핵심 포인트 3가지:\n"
                f"1. 코스피/코스닥 실시간 외인·기관 자금 유입 레이더 분석\n"
                f"2. 물타기 금지! AI 리스크 가드 자동 손절매 공식 확립\n"
                f"3. 저PBR 밸류업 & 고배당 금융주 실시간 스크리닝\n\n"
                f"👇 당일 실시간 퀀트 1위 종목 무료 확인\n"
                f"👉 상단 프로필({self.spec['ig_handle']}) 링크를 터치하세요!\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_c = (
                f"📈 [스마트한 퀀트 투자 가이드] {topic_title}\n\n"
                f"외인과 기관이 지금 몰래 쓸어 담고 있는 진짜 주도주는 무엇일까요?\n"
                f"빅데이터 퀀트 알고리즘이 분석하는 실시간 수급 포착과 리스크 관리 치트키 🚀\n\n"
                f"✔️ 체결강도 120% 돌파 급등 유망주 포착\n"
                f"✔️ 하락장에서도 계좌를 지키는 AI 자동 손절 공식\n\n"
                f"👉 실시간 퀀트 전광판 바로가기: {self.spec['url']}\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]\n\n"
                f"{hashtag_str}"
            )
            fb_cm = f"👉 StockMaster AI 실시간 수급 레이더 바로가기: {self.spec['url']}\n네이버에 [{self.spec['official_keyword']}] 검색해보세요!"
            yt_d = (
                f"{topic_title}\n\n"
                f"외인·기관 실시간 수급 포착 및 AI 퀀트 리스크 관리 시스템 📈\n"
                f"세력 체결강도 120% 돌파 종목을 데이터로 확인하세요!\n\n"
                f"🔍 네이버 검색창에 👉 [{self.spec['official_keyword']}] 검색!\n"
                f"공식 대시보드: {self.spec['url']}\n\n"
                f"{short_hashtag_str}"
            )
            yt_p = f"📌 실시간 외인/기관 수급 레이더 및 퀀트 종목 분석은 네이버에 [{self.spec['official_keyword']}] 검색해보세요!"
            cl_d = (
                f"📈 {topic_title}\n\n"
                f"📝 상세 칼럼(블로그): {self.spec['naver_blog_url']}\n"
                f"🚀 {self.spec['cta_label']}: {self.spec['url']}\n"
                f"🔍 네이버 검색창: [{self.spec['official_keyword']}]\n\n"
                f"{short_hashtag_str}"
            )[:295]

        return {
            "main_title": topic_title,
            "hashtags": hashtags,
            "youtube": {"title": f"{topic_title} #{self.spec['official_keyword'].replace(' ', '')} #Shorts", "desc": yt_d, "pinned": yt_p},
            "naver_clip": {"title": topic_title, "desc": cl_d},
            "meta": {"ig_caption": ig_c, "fb_caption": fb_c, "fb_comment": fb_cm}
        }
