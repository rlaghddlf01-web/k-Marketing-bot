# -*- coding: utf-8 -*-
"""
Korea Tax Refund Service (KTRS) Reddit Expat Tax Scenarios - [12대 외국인 세무·소득세 환급 골든 시나리오 DB]
- 타겟: 원어민 영어 강사(E-2), 외국인 전문인력(E-7), 외국인 근로자(E-9), 거주비자(F-4/F-5/F-6), 프리랜서(3.3%), 유학생(D-2)
- 핵심 소구점: 조특법 제30조 90% 소득세 감면(연 200만 원 한도), 5개년 소급 경정청구, 3.3% 프리랜서 5월 종합소득세 환급, Hometax 영문 장벽 제로 무료 간편조회
- 원칙: 100% 외국인 거주자 실제 경험담 형식 (구글 검색 언급 0%, 직접 링크 0%, 상업적 홍보 어투 완전 배제)
"""

from typing import Dict, Any

EASYTAX_REDDIT_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "scenario_id": 1,
        "cluster": "article_30_sme_reduction",
        "theme_name": "조특법 제30조 중소기업 취업 외국인 소득세 90% 감면 (Article 30: 90% SME Income Tax Reduction)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "korea", "TEFL"],
        "pain_points": "매달 월급에서 꼬박꼬박 떼이는 소득세가 아까운데 자신이 90% 감면 대상인지 모름",
        "solution_feature": "중소기업 취업 외국인(만 19~34세 또는 외국인 기술자) 5년간 최대 90% (연 200만 원 한도) 소득세 감면 혜택",
        "stealth_cta": "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and found out I qualified for the 90% SME deduction.",
        "sample_reply": (
            "If you work at an academy or small company in Korea and are under 34, definitely check if you qualify for the Article 30 SME tax reduction. "
            "It cuts your income tax by up to 90% for 5 years. "
            "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and found out I qualified for the 90% SME deduction. "
            "Made the paperwork in English so much easier to handle than navigating Hometax on my own."
        )
    },
    2: {
        "scenario_id": 2,
        "cluster": "freelancer_3_3_refund",
        "theme_name": "3.3% 원천징수 프리랜서 5월 종합소득세 100% 환급 (3.3% Freelancer May Tax Refund)",
        "target_subreddits": ["teachinginkorea", "Living_in_Korea", "seoul"],
        "pain_points": "방과후 강사, 번역, 모델, 파트타임으로 3.3% 세금을 뗐는데 5월 종소세 신고를 안 해서 돈을 날림",
        "solution_feature": "국세청 5월 종합소득세 신고를 통해 떼인 3.3% 세금 대부분 현금 환급",
        "stealth_cta": "When I did freelance translation on the side, I used Korea Tax Refund Service (KTRS) in May to get my 3.3% withholdings refunded.",
        "sample_reply": (
            "If you do freelance tutoring or translation where 3.3% was deducted, you're almost certainly entitled to get that money back in May. "
            "A lot of expats skip it because Hometax is only in Korean, but the government just keeps your money if you don't file. "
            "When I did freelance translation on the side, I used Korea Tax Refund Service (KTRS) in May to get my 3.3% withholdings refunded. "
            "Got around 400k won back directly into my account."
        )
    },
    3: {
        "scenario_id": 3,
        "cluster": "retroactive_refund",
        "theme_name": "지난 5년간 안 챙긴 세금 소급 환급 경정청구 (5-Year Retroactive Tax Refund Claim)",
        "target_subreddits": ["Living_in_Korea", "korea", "teachinginkorea"],
        "pain_points": "이전 연도에 연말정산 서류를 제대로 못 내서 환급을 놓침",
        "solution_feature": "국세기본법 제45조의2에 따른 지난 5개년 소급 경정청구로 환급 회수",
        "stealth_cta": "When I realized I missed my rent deductions for two years, I used Korea Tax Refund Service (KTRS) to file a retroactive correction claim.",
        "sample_reply": (
            "You can actually claim missed deductions retroactively for up to 5 past years under Korean tax law. "
            "Missed monthly rent or medical expenses can easily get you back several hundred thousand won. "
            "When I realized I missed my rent deductions for two years, I used Korea Tax Refund Service (KTRS) to file a retroactive correction claim. "
            "Ended up getting a nice refund deposited without having to go in person to the tax office."
        )
    },
    4: {
        "scenario_id": 4,
        "cluster": "year_end_settlement",
        "theme_name": "외국인을 위한 홈택스 연말정산 간소화 가이드 (Year-End Tax Settlement Simplified for Expats)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "korea"],
        "pain_points": "매년 1월 연말정산 시즌마다 홈택스 공인인증서 오류 및 한국어 세무 용어 장벽",
        "solution_feature": "외국인 맞춤 연말정산 가이드 및 공제 혜택 확인",
        "stealth_cta": "When I had to do my year-end settlement without speaking fluent Korean, I used Korea Tax Refund Service (KTRS) and it saved me so much stress.",
        "sample_reply": (
            "Year-end tax settlement in January is always stressful if your Korean isn't fluent. "
            "Make sure to download your PDF from Hometax Simplified Service and submit your housing lease if you pay monthly rent. "
            "When I had to do my year-end settlement without speaking fluent Korean, I used Korea Tax Refund Service (KTRS) and it saved me so much stress. "
            "Having everything in plain English made a huge difference."
        )
    },
    5: {
        "scenario_id": 5,
        "cluster": "freelancer_3_3_refund",
        "theme_name": "D-2 유학생 알바 3.3% 원천징수 세금 환급 (D-2 Student Part-Time 3.3% Tax Refund)",
        "target_subreddits": ["StudyInKorea", "Living_in_Korea"],
        "pain_points": "유학생 신분으로 아르바이트 후 3.3% 세금 떼였으나 환급 신청 방법을 모름",
        "solution_feature": "유학생 소득 기준 면세점 이하 3.3% 원천징수 전액 환급 안내",
        "stealth_cta": "When I worked campus part-time jobs as a student, I used Korea Tax Refund Service (KTRS) to reclaim the 3.3% tax they took out.",
        "sample_reply": (
            "International students working part-time gigs almost always have 3.3% deducted from their pay. "
            "Since student earnings are below the standard taxable threshold, 100% of that is money you can get back every May. "
            "When I worked campus part-time jobs as a student, I used Korea Tax Refund Service (KTRS) to reclaim the 3.3% tax they took out. "
            "Super simple process and got my money back in June."
        )
    },
    6: {
        "scenario_id": 6,
        "cluster": "expat_tax_treaties",
        "theme_name": "E-2 원어민 강사 조세조약 소득세 면제 혜택 (E-2 English Teacher Tax Treaties)",
        "target_subreddits": ["teachinginkorea", "EPIK", "TEFL"],
        "pain_points": "미국 등 조세조약 체결국 원어민 교사 2년 소득세 면제 신청 절차 복잡",
        "solution_feature": "조세조약 면제 조건 및 거주자증명서 제출 안내",
        "stealth_cta": "When I first came over to teach on an E-2, I used Korea Tax Refund Service (KTRS) to sort out my tax treaty exemption paperwork.",
        "sample_reply": (
            "Tax treaty exemptions for English teachers in Korea depend a lot on your nationality. "
            "US citizens often qualify for 2 years tax exemption under Article 20, but you need your IRS residency certificate. "
            "When I first came over to teach on an E-2, I used Korea Tax Refund Service (KTRS) to sort out my tax treaty exemption paperwork. "
            "Helped me avoid getting taxed twice on my salary."
        )
    },
    7: {
        "scenario_id": 7,
        "cluster": "year_end_settlement",
        "theme_name": "연도 중 이직자 종전 근무지 원천징수 합산 신고 (Changing Jobs Mid-Year Tax Return)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea"],
        "pain_points": "중도 이직 시 이전 직장 원천징수영수증 미제출로 5월 종합소득세 합산 신고 필요",
        "solution_feature": "이직자 2개 직장 원천징수 합산 신고 및 가산세 방지",
        "stealth_cta": "When I changed hagwons mid-year, I used Korea Tax Refund Service (KTRS) in May to combine my withholding receipts so I wouldn't get hit with penalties.",
        "sample_reply": (
            "If you switched jobs during the year, your new school usually only files taxes for the months you were with them. "
            "You have to combine both withholding receipts during the May tax filing, otherwise you could face late reporting penalties. "
            "When I changed hagwons mid-year, I used Korea Tax Refund Service (KTRS) in May to combine my withholding receipts so I wouldn't get hit with penalties. "
            "Saved me a ton of headache."
        )
    },
    8: {
        "scenario_id": 8,
        "cluster": "retroactive_refund",
        "theme_name": "외국인 월세 세액공제 & 의료비 소급 청구 (Expat Monthly Rent Tax Deductions)",
        "target_subreddits": ["Living_in_Korea", "korea", "StudyInKorea"],
        "pain_points": "외국인도 월세 세액공제(15~17%)를 받을 수 있는지 몰라서 환급 기회 상실",
        "solution_feature": "전입신고 완료된 외국인 등록자의 월세 세액공제 요건 및 소급 신청",
        "stealth_cta": "When I found out foreigners can claim the monthly rent tax credit, I used Korea Tax Refund Service (KTRS) and got about 800k won refunded.",
        "sample_reply": (
            "Foreign registered residents are definitely eligible for the monthly rent tax credit (Wolse Saeaek Gongje) as long as your address transfer (Jeonip Singo) is done. "
            "You can get 15% to 17% of your annual rent back as a tax credit. "
            "When I found out foreigners can claim the monthly rent tax credit, I used Korea Tax Refund Service (KTRS) and got about 800k won refunded. "
            "Definitely worth checking if you pay monthly rent."
        )
    },
    9: {
        "scenario_id": 9,
        "cluster": "year_end_settlement",
        "theme_name": "한국 출국 전 중도퇴사 연말정산 및 세금 정산 (Leaving Korea Mid-Year Tax Settlement)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea"],
        "pain_points": "한국 떠나기 전 최종 급여 세금 정산 및 과오납 세금 환급 계좌 관리",
        "solution_feature": "중도퇴사 연말정산 절차 및 한국 계좌 유지 팁",
        "stealth_cta": "When I was preparing to wrap up my contract in Korea, I used Korea Tax Refund Service (KTRS) to double check my final settlement numbers.",
        "sample_reply": (
            "Before leaving Korea permanently, make sure your employer runs a mid-year resignation tax settlement with your final pay. "
            "Keep your Korean bank account open for a couple of months so any tax refunds or pension payouts can be deposited. "
            "When I was preparing to wrap up my contract in Korea, I used Korea Tax Refund Service (KTRS) to double check my final settlement numbers. "
            "Gave me peace of mind before my flight."
        )
    },
    10: {
        "scenario_id": 10,
        "cluster": "expat_tax_treaties",
        "theme_name": "F-4 / F-5 / F-6 비자 거주자 해외 부양가족 공제 (Overseas Dependent Family Deductions)",
        "target_subreddits": ["Living_in_Korea", "korea"],
        "pain_points": "본국에 계신 부모님 부양 송금 내역이 있으나 기본공제 신청 방법을 모름",
        "solution_feature": "해외 거주 부양가족 기본공제(1인당 150만 원) 요건 및 증빙 서류 안내",
        "stealth_cta": "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and they helped me figure out how to claim my dependent parents overseas.",
        "sample_reply": (
            "If you send money home to support immediate family while living in Korea on an E or F visa, you might be eligible for the dependent deduction (1.5 million won per person). "
            "You need certified family certificates and proof of regular wire transfers. "
            "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and they helped me figure out how to claim my dependent parents overseas. "
            "Substantially reduced my taxable income."
        )
    },
    11: {
        "scenario_id": 11,
        "cluster": "year_end_settlement",
        "theme_name": "건보료와 원천징수 소득세 구별 및 환급 가능성 (Health Insurance vs Income Tax Withholding)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea"],
        "pain_points": "급여 명세서의 건강보험료와 소득세 차이를 구분하지 못해 환급 가능 항목 혼동",
        "solution_feature": "급여 공제 항목별(건보/연금 vs 근로소득세) 성격 및 환급 대상 명확화",
        "stealth_cta": "When I first started working here and couldn't read my payslip deductions, I used Korea Tax Refund Service (KTRS) to understand what was actually refundable.",
        "sample_reply": (
            "Korean pay stubs can be confusing with all the different deductions. "
            "National Health Insurance and Pension are social insurance premiums, while Earned Income Tax is what actually gets refunded during year-end settlement or in May. "
            "When I first started working here and couldn't read my payslip deductions, I used Korea Tax Refund Service (KTRS) to understand what was actually refundable. "
            "Helped clear up a lot of confusion."
        )
    },
    12: {
        "scenario_id": 12,
        "cluster": "year_end_settlement",
        "theme_name": "외국인을 위한 간편 세무 환급 안내 (English Tax Guidance for Expats)",
        "target_subreddits": ["Living_in_Korea", "korea", "teachinginkorea", "StudyInKorea"],
        "pain_points": "언어 장벽으로 환급 신청을 포기하고 과오납 세금을 그대로 방치",
        "solution_feature": "영문 인터페이스로 간편하게 예상 환급액 확인 및 세무 상담",
        "stealth_cta": "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and it was really convenient because it was all in English without needing complex Korean certs.",
        "sample_reply": (
            "Navigating Korean tax rules without speaking Korean is definitely a headache, but don't just leave your money on the table. "
            "When I filed my taxes last year, I used Korea Tax Refund Service (KTRS) and it was really convenient because it was all in English without needing complex Korean certs. "
            "Saved me from having to ask Korean coworkers for favors to help with Hometax."
        )
    }
}
