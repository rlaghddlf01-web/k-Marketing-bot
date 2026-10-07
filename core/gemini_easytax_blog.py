"""
EasyTaxGeminiBlog - 💰 EasyTax 15개국어 공식 블로그 2,000자 전문 마스터 칼럼 생성 전담 AI 엔진
- 시나리오 디렉터의 안전장치 & 테마 지시 수령
- 100% 동양인(Asian) 실사 사진 2장 본문 자연스러운 배치 (상단 1장 + 본문 중간 1장)
- 한국어 마스터 1회 생성 ➔ BlogTranslator 다국어 초고속 전개 연동
"""

import json
import logging
import markdown
from typing import Dict, Any, Optional, Tuple
from config import GEMINI_API_KEY_EASYTAX_BLOG
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("EasyTaxGeminiBlog")

class EasyTaxGeminiBlog:
    """EasyTax 전용 2,000자 전문 세무 마스터 블로그 집필기"""
    def __init__(self, supabase_mgr: Optional[SupabaseManager] = None):
        self.supabase_mgr = supabase_mgr or SupabaseManager()
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        api_key = GEMINI_API_KEY_EASYTAX_BLOG
        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("EasyTax 블로그 전용 Gemini Client 초기화 완료")
            except Exception as e:
                logger.warning(f"EasyTax 블로그 Gemini 초기화 실패: {e}")
                self.client = None

    def write_master_korean_article(self, directive_pkg: Dict[str, Any], landing_url: str = "", hashtags: str = "", thumb_url: str = "", thumb_url_1: str = "", thumb_url_2: str = "") -> Dict[str, str]:
        """
        🎬 [제미나이 1회 호출] 한국어 2,000자 최고급 마스터 세무 전문 칼럼 집필 + 글 맞춤 visual_prompt 동시 생성
        - 본문 상단 대표 사진 자리에 {{TOP_IMAGE}} 플레이스홀더 또는 thumb_url 배치
        """
        img_url = thumb_url or thumb_url_1 or thumb_url_2 or "{{TOP_IMAGE}}"
        d = directive_pkg.get("directive", {})
        topic_title = d.get("topic_title", directive_pkg.get("title", "2026 외국인 실무 세무 환급 완벽 가이드"))
        key_facts = ", ".join(d.get("key_facts", []))
        guideline = d.get("guideline", "")
        fallback_visual = d.get("visual_prompt", "Asian worker looking at smartphone tax refund notification with happy expression")

        prompt = f"""
당신은 대한민국 최고의 외국인 전문 세무 안내팀 'KTRS EasyTax'의 수석 세무 칼럼니스트입니다.
외국인 근로자, 유학생, 원어민 강사가 읽고 깊은 감동과 신뢰를 느끼며 합법적인 세금 환급을 신청할 수 있도록,
워드프레스 최고급 칼럼 수준의 유려하고 전문적인 2,000자 한국어 마스터 칼럼을 집필해 주십시오.

[주제]: {topic_title}
[핵심 법률 및 실무 팩트]: {key_facts}
[시나리오 디렉터 지침]:
{guideline}

[본문 대표 사진 태그]: `![{topic_title}]({img_url})`
[랜딩 링크]: {landing_url}
[바이럴 해시태그]: {hashtags}

다음 구조를 완벽하게 갖춘 마크다운 전문을 작성해 주십시오:
1. 매력적이고 신뢰감 있는 대제목 (# 제목)
2. 본문 상단 대표 사진 (단 1장): `![{topic_title}]({img_url})`
3. 서론: 대한민국 세법상 외국인의 정당한 권리, 몰라서 못 받는 수백만 원 환급 실태
4. 본론 1: 주민센터(동사무소) 및 무인발급기 세무 서식 1분 발급 실전 가이드
5. 본론 2: 외국인 5대 특화 세금 감면 및 환급 제도 마크다운 비교표 (조특법 30조 90% 감면, 부모님 인적공제 150만 원 등)
6. 본론 3: 중소기업 취업자 소득세 감면신청서(별지 제11호) 작성 및 회사 미협조 시 개별 경정청구 대처법
7. 자주 묻는 질문 (FAQ 2가지)
8. 안심 보장 (선입금 0원, 국세청 세법 기준 100% 안전 접수 지원)
9. 하단 CTA 버튼: `👉 [지금 바로 내 숨은 환급금 무료 조회하기 ({landing_url})]({landing_url})`
10. 최하단 실시간 바이럴 해시태그

[비주얼 프롬프트 지침]:
- visual_prompt 필드에는 본문 속 스토리/상황(예: 공단 야외 현장, 카페 알바, 인천공항 출국장, 안락한 거실 가족통화, 세무서 앞 등)을 가장 생동감 있게 묘사하는 Imagen 3 전용 영문 프롬프트 1문장을 작성하십시오. (반드시 realistic Asian features, photorealistic, 16:9 포함)

출력 형식 (JSON):
{{
  "title": "2026 외국인 실무 세무 가이드: {topic_title}",
  "excerpt": "주민센터 서식 발급부터 조특법 제30조 90% 감면, 부모님 인적공제, 5개년 소급 환급까지 완벽 총정리.",
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
                title = data.get("title", f"2026 외국인 실무 세무 가이드: {topic_title}")
                excerpt = data.get("excerpt", f"외국인을 위한 {topic_title} 실무 세무 총정리 가이드")
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
                logger.warning(f"EasyTax Gemini 한국어 마스터 글 생성 에러 (폴백 가동): {e}")

        # Fallback: 본문 상단 대표 사진 1장 배치
        fallback_dict = self._generate_fallback_master_article(topic_title, key_facts, landing_url, hashtags, img_url)
        fallback_dict["visual_prompt"] = fallback_visual
        return fallback_dict

    def _generate_fallback_master_article(self, topic_title: str, key_facts: str, url: str, hashtags: str, thumb_url: str = "", *args) -> Dict[str, str]:
        """본문 상단 대표 사진 1장 기반 2,000자 최고 품질 마스터 칼럼"""
        title = f"2026 외국인 실무 세무 가이드: {topic_title}"
        excerpt = f"주민센터 서식 발급부터 조특법 제30조 90% 소득세 감면, 부양가족 인적공제, 5개년 소급 환급까지 외국인 세무 권리 완벽 총정리."
        md = f"""# {title}

![EasyTax 외국인 전문 세무 가이드]({thumb_url})

대한민국에서 일하는 외국인 근로자, 유학생, 원어민 강사 여러분, 매달 급여에서 꼬박꼬박 빠져나가는 소득세를 법적으로 돌려받을 수 있다는 사실을 알고 계셨나요? 

국세청 공식 통계에 따르면 수십만 명의 외국인이 **조세특례제한법 제30조(90% 소득세 감면)**와 **본국 부모님 부양가족 인적공제(1인당 150만 원)** 제도를 알지 못해 매년 수백만 원의 소중한 세금을 환급받지 못하고 있습니다.

---

## 1. 주민센터(동사무소) & 무인발급기 세무 서식 1분 발급법
세무 환급이나 비자 연장에 필요한 핵심 증빙 서류는 복잡한 홈택스 인증서 없이도 즉시 발급 가능합니다:
- **근로소득원천징수영수증**: 외국인등록증(ARC)을 지참하고 전국 동사무소 창구 또는 지하철역 무인민원발급기에서 지문인식으로 즉시 발급받을 수 있습니다.
- **소득금액증명원**: 비자 연장(E-7, E-7-4, F-2) 심사에 필수적인 서류로 세무서 민원실에서 1분 만에 무료로 발급됩니다.
- **EasyTax 모바일 간편 연동**: 세무서에 직접 방문하지 않아도 모바일 간편 인증을 통해 국세청 전산 데이터와 안전하게 자동 연동됩니다.

---

## 2. 외국인 5대 특화 세금 감면 및 환급 제도 비교

| 감면 및 공제 항목 | 대상 비자 / 자격 요건 | 연간 절세 및 환급 한도 | 필수 증빙 서류 |
| :--- | :--- | :--- | :--- |
| **조특법 제30조 90% 감면** | 만 15~34세 중소기업 재직자 | 연 최대 200만 원 (5년간 1,000만 원) | 근로계약서, 감면신청서 |
| **본국 부모님 인적공제** | 만 60세 이상 해외 거주 부모님 | 1인당 150만 원 소득공제 | 가족관계증명서, 해외송금 영수증 |
| **D-2 유학생 알바 환급** | 시간제 근로/알바 3.3% 원천징수자 | 기납부 소득세 100% 전액 환급 | 원천징수영수증, 통장 사본 |
| **원어민 강사 2년 면세** | E-2/E-1 조세조약 해당국 국민 | 입국 후 2년간 소득세 100% 면제 | 거주자증명서(COR) |
| **5개년 소급 경정청구** | 지난 5년간 과납부한 모든 외국인 | 5개년 누적분 일괄 통장 입금 | 원천징수영수증 (5개년) |

---

## 3. '중소기업 취업자 소득세 감면신청서' (별지 제11호) 작성 요령
1. **신청인 인적사항**: 외국인등록번호, 성명, 현재 거주지 주소를 정확히 기재합니다.
2. **취업 시 만 나이**: 중소기업 입사일 기준 만 15세 이상 34세 이하인지 확인합니다.
3. **감면 시작일 및 종료일**: 취업일로부터 5년이 되는 날이 속하는 달의 말일까지 90% 감면이 적용됩니다.
4. **회사 미협조 시 대처법**: 회사에서 신청을 누락했더라도 국세기본법 제45조의2에 의거하여 EasyTax 전문 세무 안내팀을 통해 개별 경정청구로 전액 환급받을 수 있습니다.

---

## 4. 자주 묻는 질문 (FAQ)
- **Q1. 세금 환급을 신청하면 비자 연장에 불이익이 있나요?**  
  👉 **전혀 없습니다.** 세금 감면과 환급은 대한민국 세법이 외국인에게 보장하는 정당한 법적 권리이며, 오히려 성실한 소득 신고 기록으로 인정받습니다.
- **Q2. 선입금이나 착수금이 있나요?**  
  👉 **EasyTax는 선입금이 0원입니다.** 국세청에서 환급금이 고객님의 한국 은행 통장으로 정식 입금된 후에만 후정산되므로 안심하고 이용하실 수 있습니다.

---

## 5. 지금 내 환급금 3분 무료 모의계산
🛡️ **EasyTax 3대 안심 보장:**
- 15개국 모국어 1:1 상담 지원
- 국세청 세법 기준 100% 안전 접수 지원
- 개인정보 군사급 암호화 처리

👉 **[지금 바로 내 숨은 환급금 무료 조회하기 ({url})]({url})**

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
