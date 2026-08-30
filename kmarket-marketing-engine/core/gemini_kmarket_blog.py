"""
KMarketGeminiBlog - 🛒 K-Market 17개국어 공식 블로그 2,000자 실전 마스터 칼럼 생성 전담 AI 엔진
- 시나리오 디렉터의 안전장치 & 테마 지시 수령
- 100% 동양인/한국 로컬 실사 사진 2장 본문 자연스러운 배치 (상단 1장 + 본문 중간 1장)
- 한국어 마스터 1회 생성 ➔ BlogTranslator 다국어 초고속 전개 연동
"""

import json
import logging
import markdown
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY_KMARKET_BLOG
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("KMarketGeminiBlog")

class KMarketGeminiBlog:
    """K-Market 전용 2,000자 실전 라이프스타일 마스터 블로그 집필기"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_KMARKET_BLOG
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("K-Market 블로그 전용 Gemini Client 초기화 완료")
            except Exception as e:
                logger.warning(f"K-Market 블로그 Gemini 초기화 실패: {e}")
                self.client = None

    def write_master_korean_article(self, directive_pkg: Dict[str, Any], landing_url: str = "", hashtags: str = "", thumb_url: str = "", thumb_url_1: str = "", thumb_url_2: str = "") -> Dict[str, str]:
        """
        🎬 [제미나이 1회 호출] 한국어 2,000자 최고급 마스터 실전 생활 칼럼 집필 + 글 맞춤 visual_prompt 동시 생성
        - 본문 상단 대표 사진 자리에 {{TOP_IMAGE}} 플레이스홀더 또는 thumb_url 배치
        """
        img_url = thumb_url or thumb_url_1 or thumb_url_2 or "{{TOP_IMAGE}}"
        d = directive_pkg.get("directive", {})
        topic_title = d.get("topic_title", directive_pkg.get("title", "2026 외국인 한국 생활 꿀팁 가이드"))
        key_facts = ", ".join(d.get("key_facts", []))
        guideline = d.get("guideline", "")
        fallback_visual = d.get("visual_prompt", "Asian student smiling in cozy neat Korean studio apartment with arranged furniture")

        prompt = f"""
당신은 대한민국 거주 250만 외국인의 필수 라이프 플랫폼 'K-Market'의 수석 에디터입니다.
외국인 유학생, 근로자, 다문화 가정이 읽고 낯선 한국 생활에 큰 용기와 실질적인 절약 도움을 얻을 수 있도록,
워드프레스 최고급 칼럼 수준의 유려하고 전문적인 2,000자 한국어 마스터 칼럼을 집필해 주십시오.

[주제]: {topic_title}
[핵심 생활 팩트 및 노하우]: {key_facts}
[시나리오 디렉터 지침]:
{guideline}

[본문 대표 사진 태그]: `![{topic_title}]({img_url})`
[랜딩 링크]: {landing_url}
[바이럴 해시태그]: {hashtags}

다음 구조를 완벽하게 갖춘 마크다운 전문을 작성해 주십시오:
1. 매력적이고 유용한 대제목 (# 제목)
2. 본문 상단 대표 사진 (단 1장): `![{topic_title}]({img_url})`
3. 서론: 신학기 원룸 이사, 가구 장만 비용 부담과 외국인이 겪는 정착 현실
4. 본론 1: 원룸 이사 & 정착 비용 100만 원 아끼는 핵심 노하우 (대형폐기물 스티커 0원화, 분리배출 과태료 예방)
5. 본론 2: 신품 구매 vs K-Market 알뜰 직거래 비용 비교표 (매트리스, 전자레인지, 책상, 밥솥 등)
6. 본론 3: 외국인을 위한 100% 안전 직거래 3대 수칙 (ARC 인증, 지하철역 대면 거래, 17개국 자동번역 채팅)
7. 하단 CTA 버튼: `👉 [지금 바로 내 주변 0원 나눔 및 알뜰 매물 확인하기 ({landing_url})]({landing_url})`
8. 최하단 실시간 바이럴 해시태그

[비주얼 프롬프트 지침]:
- visual_prompt 필드에는 본문 속 스토리/장면(예: 화창한 한강 자전거 도로 라이딩, 대학 도서관 노트북 타이핑, 아파트/기숙사 정문 앞 훈훈한 중고 직거래, 깔끔한 주방 가전 세팅 등)을 가장 생동감 있게 묘사하는 Imagen 3 전용 영문 프롬프트 1문장을 작성하십시오. (반드시 realistic Asian features, photorealistic, 16:9 포함)

출력 형식 (JSON):
{{
  "title": "2026 외국인 한국 생활 꿀팁 가이드: {topic_title}",
  "excerpt": "신학기 원룸 이사부터 대형폐기물 0원 나눔, 분리배출 과태료 예방, 17개국 안심 직거래까지 완벽 총정리.",
  "visual_prompt": "...",
  "content_md": "..."
}}
"""
        if self.client:
            try:
                result = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt
                )
                text = result.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                import re
                text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text.strip())
                data = json.loads(text)
                title = data.get("title", f"2026 외국인 한국 생활 꿀팁 가이드: {topic_title}")
                excerpt = data.get("excerpt", f"외국인을 위한 {topic_title} 실전 생활 꿀팁")
                content_md = data.get("content_md", "")
                visual_prompt = data.get("visual_prompt", fallback_visual)
                
                content_html = markdown.markdown(content_md, extensions=['extra', 'tables', 'nl2br'])
                return {
                    "title": title,
                    "excerpt": excerpt,
                    "visual_prompt": visual_prompt,
                    "content_md": content_md,
                    "content_html": content_html
                }
            except Exception as e:
                logger.warning(f"K-Market Gemini 한국어 마스터 글 생성 에러 (폴백 가동): {e}")

        # Fallback: 본문 상단 대표 사진 1장 배치
        fallback_dict = self._generate_fallback_master_article(topic_title, key_facts, landing_url, hashtags, img_url)
        fallback_dict["visual_prompt"] = fallback_visual
        return fallback_dict

    def _generate_fallback_master_article(self, topic_title: str, key_facts: str, url: str, hashtags: str, thumb_url: str = "", *args) -> Dict[str, str]:
        """본문 상단 대표 사진 1장 기반 2,000자 최고 품질 K-Market 마스터 칼럼"""
        title = f"2026 외국인 한국 생활 꿀팁 가이드: {topic_title}"
        excerpt = f"신학기 원룸 이사부터 대형폐기물 스티커 0원 절약, 분리배출 과태료 예방, 17개국 안심 직거래까지 실전 한국 생활 완벽 마스터."
        md = f"""# {title}

<img src="{thumb_url_1}" alt="K-Market 외국인 생활 꿀팁" style="width:100%;max-width:850px;height:auto;display:block;margin:20px auto;border-radius:12px;">

한국에 처음 정착하는 유학생, 외국인 근로자, 교환학생 여러분! 원룸 이사, 가구·가전 마련, 분리배출 규정 때문에 큰돈을 쓰거나 당황하셨던 경험이 있으신가요?

K-Market은 전국 270개 이상의 실제 매물과 **0원 무료나눔**, **17개국 실시간 자동번역 채팅**을 통해 외국인이 한국에서 매년 100만 원 이상의 생활비를 아낄 수 있도록 돕고 있습니다.

---

## 1. 원룸 이사 & 정착 비용 100만 원 아끼는 핵심 노하우
- **대형폐기물 스티커 비용 0원화**: 졸업이나 이사로 방을 뺄 때 매트리스, 책상, 서랍장을 버리려면 구청 스티커 비용만 10~20만 원이 듭니다. K-Market 0원 나눔에 올리면 1시간 만에 이웃이 직접 수거해 갑니다.
- **종량제 봉투 & 음식물 쓰레기 과태료(10만 원) 완벽 예방**: 일반 쓰레기봉투에 음식물을 섞어 배출하면 무거운 과태료가 부과됩니다. 지정된 요일과 배출 장소를 꼭 확인하세요.
- **전입신고와 확정일자**: 소중한 원룸 보증금을 지키기 위해 이사 후 14일 이내 관할 주민센터에서 전입신고를 마치고 확정일자를 받아야 합니다.

<img src="{thumb_url_2}" alt="원룸 가구 배치 및 알뜰 인테리어" style="width:100%;max-width:850px;height:auto;display:block;margin:24px auto;border-radius:12px;">

---

## 2. 신품 구매 vs K-Market 알뜰 직거래 비용 비교표

| 생활 필수 품목 | 일반 매장 신품 가격 | K-Market 중고 / 0원 나눔 가격 | 절약할 수 있는 금액 |
| :--- | :--- | :--- | :--- |
| **원룸 침대 매트리스 + 프레임** | 250,000 ~ 400,000원 | **0원 (무료 나눔)** | **약 300,000원 절약** |
| **자취용 미니 전자레인지** | 80,000 ~ 120,000원 | **10,000 ~ 20,000원** | **약 80,000원 절약** |
| **공부용 책상 & 의자 세트** | 150,000 ~ 220,000원 | **0원 ~ 15,000원** | **약 150,000원 절약** |
| **전기밥솥 & 소형 가전** | 90,000 ~ 150,000원 | **10,000 ~ 25,000원** | **약 100,000원 절약** |
| **총 초기 정착 절약 비용** | **약 700,000 ~ 1,000,000원** | **10,000 ~ 50,000원** | **총 80만 원 이상 절약!** |

---

## 3. 외국인을 위한 100% 안전 직거래 3대 수칙
1. **외국인등록증(ARC) 본인인증 뱃지 확인**: 신원이 확인된 인증 회원 간에만 안심 거래하세요.
2. **기숙사 로비 및 지하철역 앞 대면 직거래**: 택배 선입금 사기를 피하고, 지하철역 출구 앞이나 밝은 공공장소에서 만나 물품 상태를 직접 확인하세요.
3. **17개국 양방향 실시간 자동번역 채팅**: 한국어를 유창하게 하지 못해도 베트남어, 중국어, 영어, 몽골어, 우즈벡어 등 모국어로 편안하게 채팅하세요.

---

## 4. 지금 바로 K-Market에서 0원 매물 둘러보기
🛒 **K-Market 외국인 특화 서비스:**
- 17개 언어 실시간 양방향 자동번역
- 매일 쏟아지는 0원 무료나눔 매물
- 전국 대학가 & 공단 로컬 GPS 기반 거래

👉 **[지금 바로 내 주변 0원 나눔 및 알뜰 매물 확인하기 ({url})]({url})**

---

**🔥 실시간 바이럴 해시태그:**  
{hashtags}
"""
        html = markdown.markdown(md, extensions=['extra', 'tables', 'nl2br'])
        return {
            "title": title,
            "excerpt": excerpt,
            "content_md": md,
            "content_html": html
        }
