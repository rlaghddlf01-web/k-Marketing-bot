"""
ScenarioDirectorBlogEasyTax - 💰 EasyTax 15개국어 공식 블로그 전담 시나리오 디렉터 (총괄 지휘자)
- [단일 책임 원칙] 모든 글의 기획, 구성, 톤앤매너, CTA 규칙, 비주얼(사진 2장), 컴플라이언스(국가공인 배제) 지시를 전담 하달
- 38대 초정밀 실무 세무·서식·환급 테마 전수 탑재
- 100% 동양인(Asian) 실사 가드레일 & 사진 2장 배치 명령
- 깨끗한 CTA 버튼 포맷 및 과장 문구 배제 가드레일 하달
- Supabase 유입 점수 자가학습 랭킹 기반 고성과 테마 우선 선정
"""

import random
import logging
from typing import Dict, Any, Optional
from core.blog_score_tracker import BlogScoreTracker

logger = logging.getLogger("ScenarioDirectorBlogEasyTax")

EASYTAX_BLOG_THEMES = [
    # 1. 🏛️ [동사무소/세무서 필수 서식 발급 매뉴얼 (1~4)]
    {
        "id": "tax_doc_withholding_center",
        "title": "동사무소(주민센터) & 무인민원발급기에서 근로소득원천징수영수증 발급받는 법",
        "category": "practical_docs",
        "key_facts": ["외국인등록증(ARC) 지참", "무인발급기 지문인식 500원", "세무서 민원실 1분 발급", "공인인증서 불필요"],
        "visual_prompt": "Asian foreign worker smiling holding official tax documents at modern South Korean public service center, realistic Asian facial features"
    },
    {
        "id": "tax_doc_hometax_speed",
        "title": "홈택스/정부24 공인인증서 없이 세무서 민원봉사실에서 1분 만에 세무 서류 떼는 법",
        "category": "practical_docs",
        "key_facts": ["홈택스 비밀번호 분실 해결", "세무서 창구 대면 즉시 발급", "EasyTax 모바일 간편 연동"],
        "visual_prompt": "Young Asian professional walking out of Korean National Tax Service building with clean documents"
    },
    {
        "id": "tax_doc_income_certificate",
        "title": "비자 연장용 '소득금액증명원' 및 '원천징수확인서' 완벽 발급 가이드",
        "category": "practical_docs",
        "key_facts": ["E-7/E-7-4/F-2 비자 연장 필수", "출입국관리사무소 제출 기준", "5개년 소득금액 정합성"],
        "visual_prompt": "Asian office worker organizing visa and tax certificates on desk in Seoul"
    },
    {
        "id": "tax_doc_apostille_guide",
        "title": "본국 가족관계증명서 / 출생증명서 번역공증 및 아포스티유 인정 기준",
        "category": "practical_docs",
        "key_facts": ["베트남/우즈벡/몽골 등 본국 서류", "공증처 번역공증 기준", "부양가족 150만원 공제 증빙"],
        "visual_prompt": "Asian tax consultant explaining family deduction documents with Asian client in Seoul office"
    },

    # 2. 🏢 [중소기업 청년 취업자 소득세 90% 감면 (조특법 제30조) (5~12)]
    {
        "id": "tax_sme_form_filling",
        "title": "신청 서식 작성법: '중소기업 취업자 소득세 감면신청서' (별지 제11호 서식) 빈칸 채우는 법",
        "category": "article_30",
        "key_facts": ["별지 제11호 서식 다운로드", "중소기업 취업일자 기재요령", "감면율 90% (연 200만원 한도)"],
        "visual_prompt": "Asian worker filling out Korean tax application form at clean office desk"
    },
    {
        "id": "tax_sme_previous_company",
        "title": "회사 이직/퇴사 후 이전 직장 5개년 분할 환급받는 실전 요령",
        "category": "article_30",
        "key_facts": ["퇴사한 이전 직장 세금 환급", "이전 직장 원천징수영수증 합산", "5개년 소급 경정청구"],
        "visual_prompt": "Young Asian factory engineer looking at smartphone refund calculation with relieved happy smile"
    },
    {
        "id": "tax_sme_max_2million",
        "title": "연간 200만 원 한도 꽉 채워 돌려받는 절세 계산법",
        "category": "article_30",
        "key_facts": ["소득세 90% 감면 한도 200만원", "5년간 최대 1,000만원 절세", "급여 명세서 원천징수세액 비교"],
        "visual_prompt": "Happy Asian professional looking at smartphone banking app showing tax refund payout"
    },
    {
        "id": "tax_sme_article_30_first",
        "title": "조특법 제30조 90% 소득세 감면 첫 발견 (연 200만 원 절세 혜택)",
        "category": "article_30",
        "key_facts": ["조세특례제한법 제30조 법적 근거", "중소기업 재직 외국인 권리", "모르면 매년 200만원 손해"],
        "visual_prompt": "Confident Asian worker standing in front of modern Korean workplace, genuine smile"
    },
    {
        "id": "tax_sme_youth_criteria",
        "title": "만 15~34세 청년 외국인 근로자 소득세 90% 감면 완벽 조건",
        "category": "article_30",
        "key_facts": ["취업 당시 만 나이 기준", "군복무 기간 차감 요건", "E-9/E-7/F-4 비자 적용"],
        "visual_prompt": "Smiling 20s Asian technician wearing clean uniform looking at mobile tax calculator"
    },
    {
        "id": "tax_sme_manufacturing_retroactive",
        "title": "중소 제조/뿌리공단 재직 외국인 5개년 소급 경정청구 성공기",
        "category": "article_30",
        "key_facts": ["시화/반월/남동공단 재직자", "5개년 누락 세금 일괄 소급", "평균 380만원 통장 입금"],
        "visual_prompt": "Asian industrial employee celebrating refund news with smartphone, documentary style"
    },
    {
        "id": "tax_sme_individual_claim",
        "title": "회사에서 90% 감면 신청 안 해줬을 때 개별 신청하는 법",
        "category": "article_30",
        "key_facts": ["회사 미협조 시 개별 경정청구", "국세청 홈택스/세무지원팀 접수", "회사 통보 없이 안전 접수"],
        "visual_prompt": "Asian young person consulting with Korean tax consultant, realistic Asian faces"
    },
    {
        "id": "tax_sme_past_5years_claim",
        "title": "이직하거나 퇴사한 후에도 지난 5년간 낸 세금 돌려받는 법",
        "category": "article_30",
        "key_facts": ["국세기본법 제45조의2 경정청구권", "2021~2025년 납부 세액 대상", "선입금 0원 국세청 정산"],
        "visual_prompt": "Asian worker walking outdoors in Seoul with cheerful expression checking phone"
    },

    # 3. 👨‍👩‍👧 [본국 부모님/가족 부양가족 인적공제 감면 (1인당 150만 원) (13~16)]
    {
        "id": "tax_family_parent_registration",
        "title": "본국(베트남, 몽골, 우즈벡 등)에 계신 만 60세 이상 부모님 부양가족 등록법",
        "category": "family_deduction",
        "key_facts": ["만 60세 이상 부모님 대상", "가족관계증명서 + 송금증빙", "1인당 150만원 기본공제"],
        "visual_prompt": "Asian worker video calling family on smartphone with warm emotional smile in cozy room"
    },
    {
        "id": "tax_family_remittance_1500k",
        "title": "해외 송금 영수증 + 가족관계증명서 제출로 1명당 150만 원 공제",
        "category": "family_deduction",
        "key_facts": ["해외송금 앱 영수증 합산 인정", "환급금 50~180만원 증가", "공제 서류 제출 기한"],
        "visual_prompt": "Asian person checking overseas bank transfer receipt and tax calculation on mobile"
    },
    {
        "id": "tax_family_double_refund_secret",
        "title": "본국 가족(부모님, 자녀) 인적공제 추가하여 환급액 2배 늘리기",
        "category": "family_deduction",
        "key_facts": ["부모님 2분 등록 시 300만원 공제", "미성년 자녀 추가 공제", "환급액 200만원 돌파 실화"],
        "visual_prompt": "Asian woman holding coffee cup and smiling happily looking at tablet screen"
    },
    {
        "id": "tax_family_medical_education",
        "title": "외국인 근로자 의료비, 교육비, 기부금 소득공제 비법",
        "category": "family_deduction",
        "key_facts": ["국내 병원비 3% 초과분 공제", "어학원/대학 학비 교육비 공제", "신용카드/체크카드 소득공제"],
        "visual_prompt": "Asian student organizing receipts and tax papers neatly on desk"
    },

    # 4. ☕ [3.3% 프리랜서 / 단기 알바 세금 환급 (17~23)]
    {
        "id": "tax_d2_freelance_3_3_full",
        "title": "식당, 카페, 물류센터, 단기 통역 알바에서 3.3% 떼인 세금 100% 환급법",
        "category": "student_3_3",
        "key_facts": ["D-2 유학생 알바 3.3% 원천징수", "소득금액 1,500만원 이하 전액 환급", "5월 종합소득세 정기신고"],
        "visual_prompt": "Asian college student working part-time at cafe smiling looking at phone notification"
    },
    {
        "id": "tax_d2_simple_expense_may",
        "title": "단순경비율 적용으로 5월 종합소득세 신고 시 전액 통장으로 돌려받기",
        "category": "student_3_3",
        "key_facts": ["단순경비율 자동 적용", "원천징수된 소득세 100% 입금", "국세청 환급금 통장 입금일"],
        "visual_prompt": "Asian international student celebrating with friends at restaurant, genuine laughter"
    },
    {
        "id": "tax_d2_restaurant_cafe_refund",
        "title": "D-2 유학생 식당/카페 알바 3.3% 원천징수 100% 전액 환급",
        "category": "student_3_3",
        "key_facts": ["시간제 근로허가 소득", "3.3% 사업소득세 전액 환급", "비자 불이익 없는 합법 권리"],
        "visual_prompt": "Asian young woman with backpack on university campus in Seoul checking smartphone"
    },
    {
        "id": "tax_d2_weekend_delivery_guide",
        "title": "주말 단기 알바/배달 3.3% 소득세 5월 종합소득세 환급 가이드",
        "category": "student_3_3",
        "key_facts": ["배달/물류 단기 알바 원천징수", "5개년 소급 환급 가능", "선입금 0원 무료 모의계산"],
        "visual_prompt": "Young Asian delivery worker taking a break looking at mobile screen happily"
    },
    {
        "id": "tax_d2_tuition_earned_back",
        "title": "학비 벌려고 투잡 뛰었던 유학생 세금 120만 원 돌려받은 실화",
        "category": "student_3_3",
        "key_facts": ["실제 환급 성공 사례", "알바비 3.3% 120만원 환급", "등록금 마련 성공 스토리"],
        "visual_prompt": "Asian college student in library smiling brightly while holding laptop"
    },
    {
        "id": "tax_d2_language_exchange_tips",
        "title": "어학연수생/교환학생 단기 근로 세무 환급 꿀팁",
        "category": "student_3_3",
        "key_facts": ["D-4 어학연수생 단기 알바", "귀국 전 세무 환급 신청", "해외 계좌 송금 수령"],
        "visual_prompt": "Asian student walking with luggage at Incheon airport terminal smiling"
    },
    {
        "id": "tax_d2_visa_extension_benefit",
        "title": "유학생 알바 정당한 세무 환급이 비자 연장에 미치는 긍정적 효과",
        "category": "student_3_3",
        "key_facts": ["소득세 정식 신고 증빙", "출입국 소득금액증명원 제출", "D-10/E-7 비자 전환 가산점"],
        "visual_prompt": "Asian student receiving certificate from university office with proud expression"
    },

    # 5. 👨‍🏫 [외국인 원어민 강사 / 교수 조세조약 세금 면세제도 (24~26)]
    {
        "id": "tax_e2_treaty_countries",
        "title": "국가별 조세조약 면세 조항 (미국, 캐나다, 영국, 호주, 남아공 등 E-2/E-1 비자)",
        "category": "foreign_teacher",
        "key_facts": ["조세조약 제20조 교원조항", "2년간 소득세 100% 면제", "기납부 세금 전액 소급 환급"],
        "visual_prompt": "Asian instructor explaining notes enthusiastically in modern classroom in Korea"
    },
    {
        "id": "tax_e2_treaty_2year_exempt",
        "title": "입국 후 2년간 소득세 100% 전액 면제 신청법",
        "category": "foreign_teacher",
        "key_facts": ["소득세 면제신청서 작성법", "본국 거주자증명서 첨부", "월급 실수령액 20~40만원 상승"],
        "visual_prompt": "Asian instructor holding tablet smiling in modern school hallway"
    },
    {
        "id": "tax_e2_residency_certificate",
        "title": "본국 국세청 거주자증명서(Certificate of Residency) 제출 및 이미 낸 세금 환급받기",
        "category": "foreign_teacher",
        "key_facts": ["IRS/HMRC 거주자증명서 발급", "5개년 지난 세금 소급 신청", "평균 400만원대 환급"],
        "visual_prompt": "Asian consultant reviewing residency certificates at neat desk"
    },

    # 6. 🛂 [E-9 / E-7 / F-4 / H-2 비자별 맞춤 세무 (27~31)]
    {
        "id": "tax_e9_overtime_retroactive",
        "title": "E-9 비자 근로자 야근/특근 수당 소득세 정밀 환급 노하우",
        "category": "visa_tax",
        "key_facts": ["연장/야간/휴일근로수당 소득세", "생산직 비과세 급여 적용", "5개년 최대 450만원 환급"],
        "visual_prompt": "Asian manufacturing team smiling together in clean workplace"
    },
    {
        "id": "tax_e7_single_rate_19pct",
        "title": "E-7 비자 IT/엔지니어 전문인력 소득세 감면 및 연말정산",
        "category": "visa_tax",
        "key_facts": ["단일세율 19% vs 90% 감면 비교", "IT/기술 전문인력 절세법", "연봉 5,000만원 기준 수백만원 절세"],
        "visual_prompt": "Asian software engineer coding on laptop in modern office in Seoul"
    },
    {
        "id": "tax_f4_hometax_amendment",
        "title": "F-4 재외동포 종합소득세 신고 및 놓친 공제금 소급 환급",
        "category": "visa_tax",
        "key_facts": ["F-4 재외동포 개인사업/근로소득", "놓친 카드/부양가족 공제 소급", "5개년 환급금 일괄 수령"],
        "visual_prompt": "Asian business owner smiling in front of store in Korea"
    },
    {
        "id": "tax_h2_visit_employment_rights",
        "title": "H-2 방문취업 근로자 필수 세무 권리 찾기 총정리",
        "category": "visa_tax",
        "key_facts": ["H-2 방문취업 세금 감면", "출국만기보험/국민연금 반환 연계", "세무서 환급 팩트체크"],
        "visual_prompt": "Asian worker in clean work attire smiling warmly looking at smartphone"
    },
    {
        "id": "tax_e74_points_income_proof",
        "title": "E-7-4 숙련기능인력 점수제 비자용 소득금액증명원 세무 정합성",
        "category": "visa_tax",
        "key_facts": ["E-7-4 점수제 소득 요건 충족", "소득금액증명원 발급 및 세무 정합", "비자 변경 성공 가이드"],
        "visual_prompt": "Asian skilled technician proudly holding certified documents in workshop"
    },

    # 7. 🛡️ [신청 프로세스 & 안심 신뢰 (32~34)]
    {
        "id": "tax_process_3min_mobile_ai",
        "title": "공인인증서/홈택스 비밀번호 없이 모바일 3분 간편 모의계산",
        "category": "process_trust",
        "key_facts": ["복잡한 인증서 불필요", "모바일 3분 즉시 환급액 계산", "15개국 모국어 지원"],
        "visual_prompt": "Asian young person using smartphone easily in bright cafe"
    },
    {
        "id": "tax_process_zero_prepayment",
        "title": "선입금 0원 & EasyTax 1:1 안전 접수 안심 보장",
        "category": "process_trust",
        "key_facts": ["선입금 일체 없음 (환급 후 정산)", "국세청 세법 기준 100% 안전 접수", "개인정보 100% 암호화"],
        "visual_prompt": "Asian tax consultant wearing suit smiling reassuringly"
    },
    {
        "id": "tax_process_5year_amendment",
        "title": "5월 정기신고 놓쳐도 1년 365일 가능한 5개년 경정청구 가이드",
        "category": "process_trust",
        "key_facts": ["1년 365일 언제든 접수", "2021~2025년 세금 전액 소급", "신청 후 1~2개월 내 통장 입금"],
        "visual_prompt": "Asian young worker checking bank deposit confirmation on smartphone outdoors"
    },

    # 8. 💌 [감동 사연 & 라이프 임팩트 (35~38)]
    {
        "id": "tax_life_remit_to_parents",
        "title": "환급금 380만 원 받아 본국 가족에게 송금하고 효도한 사연",
        "category": "life_impact",
        "key_facts": ["실제 380만원 환급 후기", "본국 가족에게 송금", "EasyTax 모바일 간편 신청"],
        "visual_prompt": "Happy Asian family portrait, warm emotional home atmosphere"
    },
    {
        "id": "tax_life_factory_group_claim",
        "title": "기숙사 동료들에게 알려주고 공장 전체가 단체 환급 성공한 후기",
        "category": "life_impact",
        "key_facts": ["기숙사 동료 단체 환급", "1인당 평균 300만원 수령", "다국어 1:1 세무 상담 후기"],
        "visual_prompt": "Group of diverse Asian workers cheering happily together in break room"
    },
    {
        "id": "tax_life_flight_ticket_vacation",
        "title": "세금 환급금으로 고향 왕복 비행기 표 마련하고 휴가 다녀온 실화",
        "category": "life_impact",
        "key_facts": ["환급금으로 고향 휴가 여행", "280만원 깜짝 목돈 마련", "합법적인 세금 환급 권리"],
        "visual_prompt": "Asian traveler looking at airplane ticket and smartphone smiling brightly at airport"
    },
    {
        "id": "tax_life_15lang_comfort_consult",
        "title": "세무서 방문 없이 스마트폰 터치 몇 번으로 한국 통장 입금 성공 후기",
        "category": "life_impact",
        "key_facts": ["15개국 모국어 상담 편안함", "세무서 방문 0회", "한국 은행 통장 자동 입금"],
        "visual_prompt": "Asian woman relaxing on cozy sofa looking at smartphone with happy expression"
    }
]

class ScenarioDirectorBlogEasyTax:
    """
    💰 EasyTax 15개국어 공식 블로그 전담 시나리오 디렉터 (총괄 지휘자)
    - 제미나이에게 완벽한 글의 구성, 100% 동양인 사진 2장 배치, 깨끗한 CTA 링크, 컴플라이언스(국가공인 배제) 명령을 전담 하달
    """
    def __init__(self, score_tracker: Optional[BlogScoreTracker] = None):
        self.themes = EASYTAX_BLOG_THEMES
        self.score_tracker = score_tracker or BlogScoreTracker()

    def get_directive(self, theme_index: Optional[int] = None, lang: str = "ko") -> Dict[str, Any]:
        """
        🎯 [50% 실유입 가중치 + 50% 랜덤 탐색] 균형 테마 선정
        - 50% 확률: 실제 방문자 유입/전환 점수가 가장 높은 1위 세무 테마 우선 채택
        - 50% 확률: 38개 전체 테마 중에서 무작위로 새로운 세무 테마 탐색 (다양성 100% 보장)
        """
        if theme_index is not None:
            theme = self.themes[theme_index % len(self.themes)]
        else:
            best_theme_id = self.score_tracker.get_top_performing_theme_id("easytax", lang)
            matched_themes = [t for t in self.themes if t["id"] == best_theme_id]

            if matched_themes and random.random() < 0.5:
                theme = matched_themes[0]
                logger.info(f"🏆 [가중치 50% 채택] 실유입 1위 테마 선정: '{theme['title']}'")
            else:
                theme = random.choice(self.themes)
                logger.info(f"🎲 [랜덤 50% 채택] 38개 테마 중 새로운 테마 탐색: '{theme['title']}'")

        writing_directive = {
            "topic_title": theme["title"],
            "category": theme["category"],
            "key_facts": theme["key_facts"],
            "guideline": (
                "1. [분량 & 필력] 워드프레스 최고급 칼럼 수준의 유려하고 깊이 있는 2,000자 한국어 마스터 칼럼으로 집필할 것.\n"
                "2. [대표 사진 연동] 본문 맨 위(대제목 # 바로 아래)에 상단 대표 사진 1장만 배치하고, 본문 중간에는 임의의 가짜 이미지 태그나 style 텍스트를 절대 삽입하지 말 것.\n"
                "3. [CTA 링크 엄격 규칙] 링크 텍스트 안에 URL 주소를 괄호로 중복 노출하지 말 것! 반드시 다음과 같이 깔끔하게 작성할 것:\n"
                "   - 올바른 예: 👉 **[지금 바로 내 숨은 환급금 3분 무료 조회하기]({landing_url})**\n"
                "   - 절대 금지: 👉 [지금 바로 조회하기 (https://...)] (URL 중복 노출 절대 금지)\n"
                "4. [컴플라이언스 절대 수칙] '국가 공인', '공인 세무사 그룹' 등의 과장/허위 표현을 절대 사용하지 말 것. 'EasyTax 전문 세무 지원팀', '공식 세무 안내 가이드'로 표현할 것.\n"
                "5. [구성 요소] 서론(외국인 세무 현실 공감) -> 1. 주민센터 서식 발급법 -> 2. 외국인 5대 세무 감면 비교표 -> 3. 별지 제11호 서식 작성요령 -> 4. FAQ -> 5. 선입금 0원 안심보장 & 깔끔한 CTA 버튼 -> 실시간 바이럴 해시태그."
            ),
            "visual_prompt": theme["visual_prompt"]
        }

        return {
            "id": theme["id"],
            "title": theme["title"],
            "category": theme["category"],
            "directive": writing_directive
        }

    # 호환성 별칭
    def get_scenario(self, theme_index: Optional[int] = None) -> Dict[str, Any]:
        return self.get_directive(theme_index)
