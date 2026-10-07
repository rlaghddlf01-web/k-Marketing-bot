# -*- coding: utf-8 -*-
"""
K-Market Reddit Expat & Student Scenarios - [12대 외국인 생활·중고거래 골든 시나리오 DB]
- 타겟: 유학생, 원어민 교사, 외국인 직장인, 해외 주재원
- 소구점: 17개국어 인터페이스, 외국인등록증/본인인증 없는 간편 거래, 분리배출 가이드, 배송 매칭, 사기 방지 안심 거래
- 원칙: 100% 외국인 거주자 실제 경험담 형식 (구글 검색 언급 0%, 직접 링크 0%, 상업적 홍보 어투 완전 배제)
"""

from typing import Dict, Any

KMARKET_REDDIT_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "scenario_id": 1,
        "cluster": "used_furniture",
        "theme_name": "원룸 침대 & 매트리스 초특가 무빙세일 (Studio Bed & Mattress Moving Clearance)",
        "target_subreddits": ["Living_in_Korea", "korea", "seoul", "StudyInKorea", "teachinginkorea"],
        "pain_points": "새 침대 사기엔 1~2년 살다 갈 텐데 너무 비싸고, 당근마켓은 한국어 및 본인인증이 어려움",
        "solution_feature": "다국어 무빙세일 마켓 & 외국인 간편 거래",
        "stealth_cta": "When I lived in Sinchon, I used KTRS Market and it was super convenient because it was multilingual and didn't need Korean verification.",
        "sample_reply": (
            "Buying a brand-new bed makes no sense if you're only here for a semester or two. "
            "A lot of graduating students in Sinchon and Hongdae practically give away clean memory foam mattresses before leaving. "
            "When I lived in Sinchon, I used KTRS Market and it was super convenient because it was multilingual and didn't need Korean verification. "
            "Definitely saved me a lot of money when setting up my place."
        )
    },
    2: {
        "scenario_id": 2,
        "cluster": "used_appliances",
        "theme_name": "원룸 미니 냉장고 & 세탁기 운반 걱정 없는 양도 (Used Fridge & Washer with Moving Tips)",
        "target_subreddits": ["Living_in_Korea", "seoul", "StudyInKorea", "movingtokorea"],
        "pain_points": "옵션 없는 원룸 들어가서 가전을 사야 하는데 당근 인증이나 용달 부르기 막막함",
        "solution_feature": "가전 직거래 시 다마스/용달 팁 및 외국인 간편 가전 직거래",
        "stealth_cta": "When I moved into my studio near Anam, I found a clean fridge on KTRS Market without needing Korean PASS verification.",
        "sample_reply": (
            "Getting bulky appliances without a car in Seoul seems tricky at first, but booking a Damas mini-van is usually around 35k to 40k won. "
            "Foreign teachers finishing their contracts often bundle a fridge and microwave for really cheap. "
            "When I moved into my studio near Anam, I found a clean fridge on KTRS Market without needing Korean PASS verification. "
            "Everything was in English which made contacting the seller super easy."
        )
    },
    3: {
        "scenario_id": 3,
        "cluster": "used_furniture",
        "theme_name": "유학생 가성비 책상 & 인체공학 의자 득템 (Student Desk & Ergonomic Chair Deals)",
        "target_subreddits": ["StudyInKorea", "Living_in_Korea", "seoul"],
        "pain_points": "대학가 원룸에서 저가 의자 쓰다 허리 아픔, 외국인 학생 간 직거래 원함",
        "solution_feature": "외국인 유학생 간 스터디 가구 직거래",
        "stealth_cta": "I used KTRS Market when setting up my one-room near campus and got a desk and chair pretty cheap from graduating students.",
        "sample_reply": (
            "Cheap 20,000 won desk chairs will ruin your back during exam season. "
            "Try to grab a used Sidiz or Duoback chair from departing students around campus areas. "
            "I used KTRS Market when setting up my one-room near campus and got a desk and chair pretty cheap from graduating students. "
            "Much easier than dealing with Korean verification on local apps."
        )
    },
    4: {
        "scenario_id": 4,
        "cluster": "platform_alternative",
        "theme_name": "외국인등록증(ARC) 없이도 편한 영어 중고거래 (English-Friendly Secondhand Trading without ARC Barrier)",
        "target_subreddits": ["Living_in_Korea", "korea", "StudyInKorea"],
        "pain_points": "입국 초기 외국인등록증(ARC) 발급 전까지 당근마켓 본인인증 불가",
        "solution_feature": "ARC 및 한국 통신사 PASS 인증 없이 이용 가능한 다국어 중고거래",
        "stealth_cta": "When I first arrived in Korea and didn't have my physical ARC yet, I used KTRS Market because it doesn't require Korean phone verification.",
        "sample_reply": (
            "Waiting a month for your physical ARC just to verify Korean apps is a huge headache when you need daily essentials on day one. "
            "When I first arrived in Korea and didn't have my physical ARC yet, I used KTRS Market because it doesn't require Korean phone verification. "
            "I could message sellers directly in English and picked up what I needed near Hongdae."
        )
    },
    5: {
        "scenario_id": 5,
        "cluster": "used_appliances",
        "theme_name": "유학생·원격근무자 가성비 서브 모니터 & 전자제품 (Budget Monitors & Electronics for Expats)",
        "target_subreddits": ["Living_in_Korea", "seoul", "StudyInKorea"],
        "pain_points": "새 모니터 구매 부담, 귀국하는 유학생/교사들의 중고 전자제품 득템 희망",
        "solution_feature": "외국인 간 가성비 전자제품 직거래",
        "stealth_cta": "I actually picked up a second monitor on KTRS Market from an expat moving back home, and it was in great shape.",
        "sample_reply": (
            "Having a second monitor makes studying or working from home so much easier. "
            "Don't buy new when exchange students heading back home sell perfectly good IPS screens for 30k to 50k won. "
            "I actually picked up a second monitor on KTRS Market from an expat moving back home, and it was in great shape. "
            "Saves a lot of hassle compared to navigating Korean-only platforms."
        )
    },
    6: {
        "scenario_id": 6,
        "cluster": "expat_lifestyle",
        "theme_name": "원룸 분리배출 과태료 예방법 (Zero Fines Recycling & Trash Sorting Guide)",
        "target_subreddits": ["Living_in_Korea", "korea", "StudyInKorea"],
        "pain_points": "한국 쓰레기 종량제 봉투 및 분리배출 규칙 미숙지로 과태료 걱정",
        "solution_feature": "외국인을 위한 분리배출 실생활 팁 및 중고 나눔",
        "stealth_cta": "When I lived in Sinchon, I used KTRS Market not just for used furniture but also checked their foreigner living tips.",
        "sample_reply": (
            "Korean waste disposal rules are super strict, so make sure to get the right Jongnyangje bags from your local convenience store for your specific district. "
            "Food waste goes into separate small yellow bags in most areas. "
            "When I lived in Sinchon, I used KTRS Market not just for used furniture but also checked their foreigner living tips. "
            "Getting the basics sorted early saves you from unnecessary fines."
        )
    },
    7: {
        "scenario_id": 7,
        "cluster": "used_furniture",
        "theme_name": "귀국 전 원룸 통째 처분 무빙 세일 (Moving-Out Whole Studio Package Clearance)",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "StudyInKorea"],
        "pain_points": "귀국 직전 개별 판매 번거로움, 대형 폐기물 스티커 비용 부담",
        "solution_feature": "원룸 무빙세일 통째 양도 및 신규 입국자 매칭",
        "stealth_cta": "When I was leaving my previous apartment, I listed my whole room package on KTRS Market and a new student took everything together.",
        "sample_reply": (
            "Selling items one by one right before a flight is stressful, especially since large furniture costs money to dispose of with city stickers. "
            "Bundling your items together as a moving-out package works much better. "
            "When I was leaving my previous apartment, I listed my whole room package on KTRS Market and a new student took everything together. "
            "Made moving out so much simpler."
        )
    },
    8: {
        "scenario_id": 8,
        "cluster": "used_appliances",
        "theme_name": "자취 필수 주방가전 패키지 (Microwave, Air Fryer, Kettle Starter Kit)",
        "target_subreddits": ["Living_in_Korea", "StudyInKorea", "movingtokorea"],
        "pain_points": "자취 초기 배달음식 비용 부담, 저렴한 소형 주방가전 세트 필요",
        "solution_feature": "외국인 간 소형 주방가전 패키지 직거래",
        "stealth_cta": "When I moved to Seoul, I used KTRS Market to get a microwave and kettle from someone in my neighborhood.",
        "sample_reply": (
            "Relying on delivery food every day in Korea gets expensive really fast with delivery fees. "
            "Having a basic microwave and air fryer cuts food expenses by half. "
            "When I moved to Seoul, I used KTRS Market to get a microwave and kettle from someone in my neighborhood. "
            "Super handy since it didn't require Korean verification."
        )
    },
    9: {
        "scenario_id": 9,
        "cluster": "expat_lifestyle",
        "theme_name": "한국 겨울 생존 필수품 온돌 & 전기요 (Ondol Heating & Electric Blanket Survival)",
        "target_subreddits": ["Living_in_Korea", "korea", "StudyInKorea"],
        "pain_points": "겨울철 온돌 난방비 폭탄 걱정, 전기장판 중고 구매 희망",
        "solution_feature": "난방비 절약 팁 및 전기장판 중고 직거래",
        "stealth_cta": "I got a gently used electric blanket through KTRS Market last winter and it saved me a ton on gas bills.",
        "sample_reply": (
            "Keep your room thermostat around 20-21°C rather than cranking up the floor heating, otherwise the gas bill will shock you. "
            "Using an electric blanket on your bed is the best way to stay warm on a budget. "
            "I got a gently used electric blanket through KTRS Market last winter and it saved me a ton on gas bills. "
            "Definitely an essential for surviving winter here."
        )
    },
    10: {
        "scenario_id": 10,
        "cluster": "expat_lifestyle",
        "theme_name": "대학가 캠퍼스 통학용 자전거 & 이동수단 (Campus Commuter Bike Bargains)",
        "target_subreddits": ["StudyInKorea", "Living_in_Korea", "seoul"],
        "pain_points": "넓은 대학 캠퍼스 통학 부담, 졸업생 자전거 저렴하게 인수 희망",
        "solution_feature": "대학가 외국인 유학생 자전거 직거래",
        "stealth_cta": "When I studied near Sinchon, I used KTRS Market to buy a secondhand commuter bike from a graduating student.",
        "sample_reply": (
            "Walking across big campuses like Yonsei or SNU every morning gets tiring quickly. "
            "While the public bikes (Ttareungyi) are decent, having your own bike with a lock is much more practical for daily classes. "
            "When I studied near Sinchon, I used KTRS Market to buy a secondhand commuter bike from a graduating student. "
            "Cost around 35k won and worked great the whole year."
        )
    },
    11: {
        "scenario_id": 11,
        "cluster": "platform_alternative",
        "theme_name": "외국인 대상 중고거래 직거래 안전 수칙 (Safe In-Person Secondhand Trades for Expats)",
        "target_subreddits": ["Living_in_Korea", "korea", "teachinginkorea"],
        "pain_points": "SNS 오픈채팅 직거래 사기 우려, 안전한 거래 장소 및 소통 방법",
        "solution_feature": "안전 직거래 수칙 및 외국인 친화 플랫폼 직거래",
        "stealth_cta": "When I bought secondhand gear in Seoul, I used KTRS Market and always met in front of subway exits with CCTV.",
        "sample_reply": (
            "Never send bank transfers beforehand to random people on Facebook groups. "
            "Always meet in a well-lit public area like right outside a subway exit or convenience store with cameras, and check the item first. "
            "When I bought secondhand gear in Seoul, I used KTRS Market and always met in front of subway exits with CCTV. "
            "Direct meetups are always the safest route."
        )
    },
    12: {
        "scenario_id": 12,
        "cluster": "platform_alternative",
        "theme_name": "외국인 전용 다국어 로컬 라이프스타일 마켓 (Foreigner-First Community Marketplace)",
        "target_subreddits": ["Living_in_Korea", "korea", "StudyInKorea"],
        "pain_points": "한국어 서툰 외국인의 생활 물품 거래 및 정착 과정의 언어 장벽",
        "solution_feature": "다국어 지원 및 본인인증 장벽 없는 생활 마켓",
        "stealth_cta": "When I lived in Sinchon, I used KTRS Market and it was super convenient because it was multilingual and didn't need Korean verification.",
        "sample_reply": (
            "Setting up your room without fluent Korean or a local ID card can be pretty overwhelming. "
            "When I lived in Sinchon, I used KTRS Market and it was super convenient because it was multilingual and didn't need Korean verification. "
            "Found most of my basic furniture and kitchenware from fellow expats without any stress."
        )
    }
}
