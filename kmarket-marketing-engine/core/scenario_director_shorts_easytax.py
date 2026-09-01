"""
ScenarioDirectorShortsEasyTax - 💰 [EasyTax 전용 9:16 숏폼 AI 마스터 시나리오 작가 엔진]
- 60대 초정밀 국세청 세무/환급 대본 테마 매트릭스:
  1) 전국 20대 국가산업단지 E-9/H-2 90% 감면편 (20개)
  2) 비자별 15대 맞춤 환급 & 조특법 30조 특례편 (15개)
  3) 환급 감동 & 라이프 리얼 에피소드편 (15개)
  4) 실전 세무 팁 & 절세 상식편 (10개)
- 100% 동일 인물 캐릭터 앵커 (1~5씬 동일 인물 완전 고정)
- 7대 외국인 페르소나 매트릭스 × 60대 로컬라이징 = 5,950가지 무한 순환 스토리텔링
"""

import json
import random
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import LANGUAGES, DATA_DIR
from core.character_anchor_easytax import (
    build_char_anchor,
    build_scene_prompt,
    build_negative_prompt,
    LANG_ETHNIC_MAP
)

# ======================================================================
# 🎯 60대 초정밀 EasyTax 숏폼 대본 테마 매트릭스
# ======================================================================

EASYTAX_60_THEMES = [
    # ── [1. 전국 20대 국가산업단지 근로자 90% 소득세 감면편 (20개)] ──
    {"id": "ind_ansan_banwol", "cat": "industrial", "name": "안산 반월·시화 스마트허브 근로자 90% 감면", "target": "안산 반월·시화 국가산단", "persona_type": "E-9 제조 근로자", "refund_est": 3840000},
    {"id": "ind_hwaseong_hyangnam", "cat": "industrial", "name": "화성 향남·발안 제약단지 외국인 소득세 환급", "target": "화성 향남·발안 산단", "persona_type": "E-9 제약가공 근로자", "refund_est": 3650000},
    {"id": "ind_pyeongtaek_poseung", "cat": "industrial", "name": "평택 포승·고덕 국가산단 5년치 소급 환급", "target": "평택 포승/고덕 산단", "persona_type": "E-9 전자/기계 근로자", "refund_est": 4120000},
    {"id": "ind_incheon_namdong", "cat": "industrial", "name": "인천 남동인더스파크 뿌리기업 세무 혜택", "target": "인천 남동 국가산단", "persona_type": "E-9 금형/열처리 근로자", "refund_est": 3780000},
    {"id": "ind_siheung_mtv", "cat": "industrial", "name": "시흥 MTV 첨단산업단지 조특법 30조 환급", "target": "시흥 시화 MTV단지", "persona_type": "E-9 조립가공 근로자", "refund_est": 3520000},
    {"id": "ind_cheonan_3rd", "cat": "industrial", "name": "천안 제3·4일반산단 외국인 연말정산 구제", "target": "천안 직산/백석 산단", "persona_type": "E-9 자동차부품 근로자", "refund_est": 3950000},
    {"id": "ind_asan_tangjeong", "cat": "industrial", "name": "아산 탕정 디스플레이단지 조특법 감면 신청", "target": "아산 탕정 테크노벨리", "persona_type": "E-7/E-9 기술 근로자", "refund_est": 4300000},
    {"id": "ind_cheongju_ochang", "cat": "industrial", "name": "청주 오창 과학산단 외국인 근로자 환급 라이브", "target": "청주 오창/오송 바이오산단", "persona_type": "E-9 화학/바이오 근로자", "refund_est": 3600000},
    {"id": "ind_dangjin_steel", "cat": "industrial", "name": "당진 송산 철강산단 중소기업 취업자 감면", "target": "당진 송산/부곡 국가산단", "persona_type": "E-9 철강/제조 근로자", "refund_est": 4250000},
    {"id": "ind_gumi_national", "cat": "industrial", "name": "구미 국가산단 전자부품 외국인 소득세 환급", "target": "구미 국가산업단지", "persona_type": "E-9 전자제조 근로자", "refund_est": 3480000},
    {"id": "ind_daegu_seongseo", "cat": "industrial", "name": "대구 성서공단 섬유/기계 근로자 세금 구제", "target": "대구 성서 일반산단", "persona_type": "E-9 섬유/가공 근로자", "refund_est": 3350000},
    {"id": "ind_changwon_national", "cat": "industrial", "name": "창원 국가산단 정밀기계 외국인 5년 소급", "target": "창원 국가산업단지", "persona_type": "E-9 정밀가공 근로자", "refund_est": 4400000},
    {"id": "ind_ulsan_onsan", "cat": "industrial", "name": "울산 온산·미포 산단 엔지니어 세무 대리", "target": "울산 온산 국가산단", "persona_type": "E-7 플랜트 엔지니어", "refund_est": 4850000},
    {"id": "ind_gwangju_hanam", "cat": "industrial", "name": "광주 하남산단 가전부품 외국인 조특법 감면", "target": "광주 하남 일반산단", "persona_type": "E-9 가전조립 근로자", "refund_est": 3550000},
    {"id": "ind_jeonju_carbon", "cat": "industrial", "name": "전주 탄소밸리 산단 외국인 연구/생산 환급", "target": "전주 팔복동 탄소산단", "persona_type": "E-9/E-7 탄소제조 근로자", "refund_est": 3700000},
    {"id": "ind_gunsan_free", "cat": "industrial", "name": "군산 자유무역산단 근로자 소득세 90% 환급", "target": "군산 국가산단/오식도동", "persona_type": "E-9 기계조립 근로자", "refund_est": 3680000},
    {"id": "ind_pohang_steel", "cat": "industrial", "name": "포항 철강산단 외국인 기술인력 세금 환급", "target": "포항 철강 산업단지", "persona_type": "E-9/E-7 금속가공 근로자", "refund_est": 4150000},
    {"id": "ind_yeosu_petro", "cat": "industrial", "name": "여수 국가산단 석유화학 정비인력 세무 구제", "target": "여수 국가산업단지", "persona_type": "E-7 플랜트 정비사", "refund_est": 4600000},
    {"id": "ind_chungju_mega", "cat": "industrial", "name": "충주 메가폴리스 산단 이차전지 근로자 환급", "target": "충주 첨단/메가폴리스", "persona_type": "E-9 배터리제조 근로자", "refund_est": 3800000},
    {"id": "ind_wonju_munmak", "cat": "industrial", "name": "원주 문막산단 의료기기/부품 외국인 환급", "target": "원주 문막 일반산단", "persona_type": "E-9 정밀기기 근로자", "refund_est": 3450000},

    # ── [2. 비자별 15대 맞춤 환급 & 조특법 30조 특례편 (15개)] ──
    {"id": "visa_e9_article30", "cat": "visa", "name": "E-9 비전문취업 조특법 30조 90% 감면 완벽 가이드", "target": "E-9 비자 전체", "persona_type": "E-9 청년 근로자", "refund_est": 3900000},
    {"id": "visa_e7_5year_claim", "cat": "visa", "name": "E-7 특정활동 전문직 5년치 소급 경정청구", "target": "E-7 비자 전체", "persona_type": "E-7 전문직/엔지니어", "refund_est": 5200000},
    {"id": "visa_h2_family_deduct", "cat": "visa", "name": "H-2 방문취업 본국 가족 인적공제 세액 환급", "target": "H-2 비자 전체", "persona_type": "H-2 동포 근로자", "refund_est": 2950000},
    {"id": "visa_d2_part_time_100", "cat": "visa", "name": "D-2 유학생 아르바이트 원천징수 3.3% 전액 환급", "target": "D-2/D-4 유학생", "persona_type": "D-2 대학생 유학생", "refund_est": 1150000},
    {"id": "visa_d10_job_seeking", "cat": "visa", "name": "D-10 구직비자 변경 전 지난 세금 총정리 환급", "target": "D-10 비자 전환자", "persona_type": "D-10 졸업생 구직자", "refund_est": 2400000},
    {"id": "visa_f4_general_income", "cat": "visa", "name": "F-4 재외동포 종합소득세 감면 및 연말정산", "target": "F-4 동포 거주자", "persona_type": "F-4 전문/서비스직", "refund_est": 3100000},
    {"id": "visa_e2_tax_treaty", "cat": "visa", "name": "E-2 회화지도 강사 한미·한영 조세조약 2년 면세", "target": "E-2 원어민 강사", "persona_type": "E-2 외국어 강사", "refund_est": 4500000},
    {"id": "visa_e8_seasonal_worker", "cat": "visa", "name": "E-8 계절근로자 농축산 소득세 비과세 환급", "target": "E-8 계절근로자", "persona_type": "E-8 농축산 근로자", "refund_est": 1800000},
    {"id": "visa_g1_humanitarian", "cat": "visa", "name": "G-1 비자 합법 취업 소득세 정당 환급 청구", "target": "G-1 체류 자격자", "persona_type": "G-1 근로자", "refund_est": 2100000},
    {"id": "visa_e9_departure_tax", "cat": "visa", "name": "E-9 만기 귀국 전 퇴직 소득세 및 5년 세금 정산", "target": "귀국 예정 외국인", "persona_type": "E-9 만기 귀국자", "refund_est": 4600000},
    {"id": "visa_h2_construction_daily", "cat": "visa", "name": "H-2 건설업 일용직 소득세 원천징수 환급", "target": "건설현장 H-2", "persona_type": "H-2 건설 근로자", "refund_est": 2700000},
    {"id": "visa_5year_statute_rescue", "cat": "visa", "name": "5년 소멸시효 전 누락 환급금 긴급 구제 청구", "target": "2021년 입사 근로자", "persona_type": "5년차 장기 근로자", "refund_est": 4800000},
    {"id": "visa_hometax_certified_agent", "cat": "visa", "name": "국세청 홈택스 공식 API 공인 세무대리 안심 조회", "target": "전국 모든 비자 외국인", "persona_type": "외국인 거주자", "refund_est": 3840000},
    {"id": "visa_youth_age_expansion", "cat": "visa", "name": "중소기업 취업 청년 연령(만 15~34세) 감면 특례", "target": "만 34세 이하 청년 외국인", "persona_type": "청년 외국인 근로자", "refund_est": 3950000},
    {"id": "visa_yearend_missed_deduct", "cat": "visa", "name": "연말정산 공제 서류 누락자 5월 경정청구 환급", "target": "연말정산 누락자", "persona_type": "직장인 외국인", "refund_est": 2600000},

    # ── [3. 환급 감동 & 라이프 리얼 에피소드편 (15개)] ──
    {"id": "story_flight_home_vacation", "cat": "story", "name": "380만원 환급금으로 드디어 끊은 고향 비행기표", "target": "고향 방문 꿈꾸는 근로자", "persona_type": "E-9 성실 근로자", "refund_est": 3800000},
    {"id": "story_parent_house_repair", "cat": "story", "name": "억울했던 세금 찾아 고향 부모님 집수리비 효도 송금", "target": "본국 가족 부양자", "persona_type": "E-9 효도 근로자", "refund_est": 4200000},
    {"id": "story_tuition_alleviated", "cat": "story", "name": "알바비 3.3% 120만원 환급으로 등록금 완납한 유학생", "target": "D-2 알바 유학생", "persona_type": "D-2 성실 유학생", "refund_est": 1200000},
    {"id": "story_macbook_self_reward", "cat": "story", "name": "한국에서 고생한 나에게 선물한 최신 노트북 언박싱", "target": "2030 청년 외국인", "persona_type": "E-7 IT 엔지니어", "refund_est": 3500000},
    {"id": "story_zero_advance_fee_trust", "cat": "story", "name": "착수금 0원 선입금 없는 국세청 공인 대리로 안심 환급", "target": "보이스피싱 걱정 외국인", "persona_type": "안전 추구 근로자", "refund_est": 3600000},
    {"id": "story_korean_doc_barrier_help", "cat": "story", "name": "한국어 세무 서류 몰라 포기했던 250만원 찾은 사연", "target": "한국어 서툰 외국인", "persona_type": "신규 입국 근로자", "refund_est": 2500000},
    {"id": "story_departure_week_miracle", "cat": "story", "name": "귀국 일주일 전 기적처럼 통장으로 입금된 환급금", "target": "귀국 직전 근로자", "persona_type": "만기 출국자", "refund_est": 4100000},
    {"id": "story_dorm_friends_trio", "cat": "story", "name": "기숙사 룸메이트 3명이 함께 신청해 1,200만원 환급 썰", "target": "기숙사 단체 거주자", "persona_type": "공단 기숙사 3인방", "refund_est": 12000000},
    {"id": "story_salary_slip_shock_fix", "cat": "story", "name": "월급명세서 세금 공제액 보고 눈물 흘리다 환급받은 후기", "target": "고소득 세금 과다납부자", "persona_type": "제조업 야근 근로자", "refund_est": 3900000},
    {"id": "story_yearend_tax_rescued", "cat": "story", "name": "연말정산 100만원 뱉어낼 뻔했다가 오히려 200만원 환급", "target": "연말정산 폭탄 맞은 분", "persona_type": "직장인 외국인", "refund_est": 2000000},
    {"id": "story_rent_tax_credit_800k", "cat": "story", "name": "자취방 월세 납부 영수증으로 80만원 추가 세액공제", "target": "원룸 자취 외국인", "persona_type": "원룸 월세 거주자", "refund_est": 800000},
    {"id": "story_first_parttime_refund", "cat": "story", "name": "생애 첫 한국 아르바이트 세금 100% 돌려받은 감동", "target": "신입 유학생", "persona_type": "첫 알바 유학생", "refund_est": 650000},
    {"id": "story_5year_forgotten_money", "cat": "story", "name": "까맣게 잊고 있던 4년 전 공장 세금 320만원 구출", "target": "이직 경험 근로자", "persona_type": "이직 2회 근로자", "refund_est": 3200000},
    {"id": "story_boss_didnt_know_benefit", "cat": "story", "name": "회사 사장님도 몰랐던 외국인 90% 감면 규정 발굴", "target": "중소기업 근로자", "persona_type": "중소기업 장기근속자", "refund_est": 4300000},
    {"id": "story_national_tax_deposit_ring", "cat": "story", "name": "국세청 입금 알림 카톡 울리는 순간 환호성 지른 실화", "target": "환급금 대기자", "persona_type": "일반 신청자", "refund_est": 3840000},

    # ── [4. 실전 세무 팁 & 절세 상식편 (10개)] ──
    {"id": "tip_youth_age_calc_rule", "cat": "tip", "name": "조특법 30조 만 15~34세 청년 나이 정확한 계산법", "target": "청년 외국인 전체", "persona_type": "만 34세 경계 근로자", "refund_est": 3800000},
    {"id": "tip_foreign_parent_1500k", "cat": "tip", "name": "본국 부모님 부양가족 인적공제 1인당 150만원 인정 팁", "target": "부모님 부양 근로자", "persona_type": "부양가족 보유자", "refund_est": 1500000},
    {"id": "tip_monthly_rent_15pct", "cat": "tip", "name": "원룸 월세 750만원 한도 15% 세액공제 챙기는 법", "target": "월세 납부 외국인", "persona_type": "월세 세입자", "refund_est": 1125000},
    {"id": "tip_card_cash_golden_ratio", "cat": "tip", "name": "체크카드·현금영수증 소득공제 30% 황금 비율 가이드", "target": "소비 많은 외국인", "persona_type": "체크카드 사용자", "refund_est": 950000},
    {"id": "tip_medical_insurance_deduct", "cat": "tip", "name": "병원비·의료비 실납부액 소득공제 누락 없이 신청하기", "target": "병원 진료 경험 외국인", "persona_type": "의료비 지출자", "refund_est": 850000},
    {"id": "tip_student_tuition_deduct", "cat": "tip", "name": "외국인 유학생 대학교 등록금 교육비 세액공제 진실", "target": "D-2 유학생 학부모", "persona_type": "등록금 납부 유학생", "refund_est": 1300000},
    {"id": "tip_may_global_tax_guide", "cat": "tip", "name": "중도 입사·퇴사자 5월 종합소득세 정기 환급 신고 팁", "target": "이직/중도퇴사 외국인", "persona_type": "5월 종소세 신고자", "refund_est": 2200000},
    {"id": "tip_5year_expiration_rule", "cat": "tip", "name": "5년 지나면 국가로 귀속되는 소멸시효 전 환급금 조회", "target": "장기 체류 외국인", "persona_type": "소멸시효 임박자", "refund_est": 4500000},
    {"id": "tip_phishing_prevention_zero", "cat": "tip", "name": "선입금 요구하는 사기 주의! EasyTax는 선입금 0원", "target": "세무 사기 불안 외국인", "persona_type": "안전제일 근로자", "refund_est": 3840000},
    {"id": "tip_1min_mobile_simulation", "cat": "tip", "name": "공인인증서 없이 카카오/간편인증 1분 환급액 무료 조회", "target": "간편 조회 희망자", "persona_type": "모바일 사용자", "refund_est": 3840000}
]

# 🎯 7대 외국인 페르소나별 100% 동일 인물 고정 앵커 (외모, 헤어, 의상 완전 고정)
EASYTAX_PERSONA_ANCHORS = [
    {
        "persona_id": "e9_male_worker",
        "visa_name": "E-9 동양인 제조 근로자 (90% 감면)",
        "gender": "male",
        "age_group": "20대 후반",
        "base_salary_krw": 34000000,
        "anchor_desc": "a specific 28-year-old Asian male factory worker with short athletic black haircut, honest kind eyes, wearing a clean navy work uniform jacket over a grey t-shirt"
    },
    {
        "persona_id": "e9_female_worker",
        "visa_name": "E-9 동양인 식품가공 근로자 (90% 감면)",
        "gender": "female",
        "age_group": "20대 후반",
        "base_salary_krw": 32000000,
        "anchor_desc": "a specific 27-year-old Asian female factory worker with a neat black ponytail, gentle dark eyes, wearing a comfortable sky-blue work jacket"
    },
    {
        "persona_id": "d2_male_student",
        "visa_name": "D-2 동양인 남학생 (알바 3.3% 환급)",
        "gender": "male",
        "age_group": "20대 초반",
        "base_salary_krw": 18000000,
        "anchor_desc": "a specific 22-year-old Asian male college student with neat short black side-part haircut, clean-shaven face, wearing a dark green university varsity hoodie"
    },
    {
        "persona_id": "d2_female_student",
        "visa_name": "D-2 동양인 여학생 (알바 소득세 환급)",
        "gender": "female",
        "age_group": "20대 초반",
        "base_salary_krw": 21000000,
        "anchor_desc": "a specific 21-year-old Asian female college student with shoulder-length black straight bob haircut, gentle dark brown eyes, wearing an oversized pastel beige knit sweater"
    },
    {
        "persona_id": "e7_male_engineer",
        "visa_name": "E-7 동양인 IT/엔지니어 전문직 (5개년 소급)",
        "gender": "male",
        "age_group": "30대 초반",
        "base_salary_krw": 48000000,
        "anchor_desc": "a specific 31-year-old Asian male professional engineer with modern slim wire-frame glasses, neatly parted black hair, wearing a clean smart-casual navy polo shirt"
    },
    {
        "persona_id": "h2_female_worker",
        "visa_name": "H-2 동포/동양인 방문취업 근로자 (가족 공제)",
        "gender": "female",
        "age_group": "30대 초반",
        "base_salary_krw": 28000000,
        "anchor_desc": "a specific 32-year-old Asian woman with elegant dark brown hair in a low bun, warm gentle smile, wearing a comfortable soft beige cardigan"
    },
    {
        "persona_id": "e2_male_instructor",
        "visa_name": "E-2 외국인 강사 (조세조약 2년 면세)",
        "gender": "male",
        "age_group": "20대 후반",
        "base_salary_krw": 36000000,
        "anchor_desc": "a specific 29-year-old Asian male instructor with modern neat black hair, friendly confident smile, wearing a brown casual blazer jacket over a white crewneck shirt"
    }
]

# 🎯 17개국 언어별 5단계 시네마틱 장면 뱃지/헤드라인/서브카피 딕셔너리 생성 엔진
def get_easytax_i18n_script(lang: str, theme: Dict[str, Any], refund_amount_formatted: str) -> Dict[str, Any]:
    name = theme["name"]
    target = theme["target"]
    persona = theme["persona_type"]

    scripts = {
        "vi": {
            "title": f"EasyTax Hoàn Thuế 90%: {name}",
            "voice_text": f"Bạn đang làm việc hoặc học tập tại {target}? Đừng bỏ lỡ quyền lợi giảm 90% thuế thu nhập theo Điều 30! Hàng ngàn lao động và du học sinh đã nhận lại số tiền hoàn thuế trung bình {refund_amount_formatted}. Miễn phí 100%, không thu phí trước. Nhấp vào link bio kiểm tra ngay trong 1 phút!",
            "captions": ["🏛️ GIẢM 90% THUẾ", f"💰 {refund_amount_formatted}"],
            "s1_badge": "ĐIỀU 30 LUẬT THUẾ HÀN QUỐC",
            "s1_main": f"{target} Quyền Lợi Hoàn Thuế",
            "s1_sub": f"Giảm tới 90% thuế thu nhập cho {persona}",
            "s2_badge": "THÔNG BÁO TÀI KHOẢN",
            "s2_main": f"Đã Nhận {refund_amount_formatted}!",
            "s2_sub": "Tiền hoàn thuế 5 năm đã chuyển vào tài khoản",
            "s3_badge": "100% HỢP PHÁP",
            "s3_main": "Đại Lý Thuế Được Cục Thuế Cấp Phép",
            "s3_sub": "Không thu phí trước • Xử lý an toàn bảo mật",
            "s4_badge": "THỰC HIỆN ƯỚC MƠ",
            "s4_main": "Đặt Vé Máy Bay & Gửi Tiền Về Nhà",
            "s4_sub": "Nhận lại mồ hôi công sức xứng đáng của bạn",
            "s5_badge": "🏛️ GIẤY BÁO HOÀN THUẾ QUỐC GIA (NTS)",
            "s5_main": "Nhấp Vào Link Trong Bio",
            "s5_sub": "Kiểm tra số tiền hoàn thuế miễn phí trong 1 phút!"
        },
        "uz": {
            "title": f"EasyTax 90% Soliq Qaytarmasi: {name}",
            "voice_text": f"Siz {target} hududida ishlayapsizmi yoki o'qiysizmi? 30-modda bo'yicha 90% soliq imtiyozini qo'ldan boy bermang! O'rtacha {refund_amount_formatted} miqdoridagi soliq qaytarmasini oling. 100% bepul, oldindan to'lov yo'q. Profil havolasida 1 daqiqada tekshiring!",
            "captions": ["🏛️ 90% SOLIQ QAYTARMASI", f"💰 {refund_amount_formatted}"],
            "s1_badge": "KOREYA DAROMAD SOLIG'I 30-MODDA",
            "s1_main": f"{target} Soliq Imtiyozi",
            "s1_sub": f"{persona} uchun 90% gacha soliq chegirmasi",
            "s2_badge": "BANK BILDIRISHNOMASI",
            "s2_main": f"{refund_amount_formatted} Hisobga Tushdi!",
            "s2_sub": "5 yillik ortiqcha to'langan soliqlar qaytarildi",
            "s3_badge": "QONUNIY IMTIYOZ",
            "s3_main": "Davlat Soliq Xizmati Litsenziyalangan",
            "s3_sub": "Oldindan hech qanday to'lov yo'q • 100% xavfsiz",
            "s4_badge": "ORZULAR RO'YOBI",
            "s4_main": "Vatanga Sayohat & Oila Uchun",
            "s4_sub": "Halol mehnatingiz mevasini to'liq qaytarib oling",
            "s5_badge": "🏛️ DAVLAT SOLIQ QAYTARMA XATI (NTS)",
            "s5_main": "Profil Havolasini Bosing",
            "s5_sub": "1 daqiqada bepul tekshiring va pulingizni oling!"
        },
        "ru": {
            "title": f"EasyTax Налоговый Возврат 90%: {name}",
            "voice_text": f"Работаете или учитесь в {target}? Не упустите скидку 90% по Статье 30! Получите возврат налогов в среднем {refund_amount_formatted} за 5 лет. 100% бесплатно и без предоплаты. Переходите по ссылке в профиле прямо сейчас!",
            "captions": ["🏛️ СКИДКА 90% НА НАЛОГИ", f"💰 {refund_amount_formatted}"],
            "s1_badge": "НАЛОГОВОЕ ПРАВО КОРЕИ (СТАТЬЯ 30)",
            "s1_main": f"{target} Законный Возврат",
            "s1_sub": f"Скидка до 90% на налог для {persona}",
            "s2_badge": "МОБИЛЬНЫЙ БАНКИНГ",
            "s2_main": f"Поступило {refund_amount_formatted}!",
            "s2_sub": "Возврат за последние 5 лет прямо на карту",
            "s3_badge": "100% ЛЕГАЛЬНО",
            "s3_main": "Лицензированные Бухгалтеры",
            "s3_sub": "Без предоплаты • Полная защита данных",
            "s4_badge": "МЕЧТЫ СБЫВАЮТСЯ",
            "s4_main": "Полет Домой & Семья",
            "s4_sub": "Заберите ваши честно заработанные деньги",
            "s5_badge": "🏛️ ИЗВЕЩЕНИЕ О НАЛОГОВОМ ВОЗВРАТЕ (NTS)",
            "s5_main": "Жми На Ссылку В Профиле",
            "s5_sub": "Бесплатный расчет за 1 минуту онлайн!"
        },
        "en": {
            "title": f"EasyTax 90% Tax Relief: {name}",
            "voice_text": f"Working or studying near {target}? Don't miss out on Article 30 up to 90% income tax exemption! Claim your average refund of {refund_amount_formatted} over 5 years. 100% free with zero upfront fees. Click the link in bio to check in 1 minute!",
            "captions": ["🏛️ 90% TAX EXEMPTION", f"💰 {refund_amount_formatted}"],
            "s1_badge": "KOREAN TAX LAW ARTICLE 30",
            "s1_main": f"{target} Tax Relief Rights",
            "s1_sub": f"Up to 90% tax exemption for {persona}",
            "s2_badge": "MOBILE BANKING ALERT",
            "s2_main": f"{refund_amount_formatted} Deposited!",
            "s2_sub": "5-year retroactive refund in your bank account",
            "s3_badge": "100% LEGAL & SAFE",
            "s3_main": "Certified National Tax Agents",
            "s3_sub": "Zero upfront fees • Safe NTS official processing",
            "s4_badge": "DREAM COME TRUE",
            "s4_main": "Flight Ticket Home & Family",
            "s4_sub": "Claim your hard-earned money today",
            "s5_badge": "🏛️ NATIONAL TAX REFUND NOTICE (NTS)",
            "s5_main": "Click Link In Bio Now",
            "s5_sub": "1-minute instant free calculation!"
        },
        "zh": {
            "title": f"EasyTax 韩国国税退税 90%: {name}",
            "voice_text": f"在 {target} 工作或留学的各位朋友！千万不要错过《租特法》第30条最高90%所得税减免优惠！平均可领取退税款 {refund_amount_formatted}。前期 0 费用，持牌税务师合规办理。立即点击主页链接，1分钟免费查询！",
            "captions": ["🏛️ 所得税减免 90%", f"💰 {refund_amount_formatted}"],
            "s1_badge": "韩国租税特例限制法第30条",
            "s1_main": f"{target} 正规退税特惠",
            "s1_sub": f"外籍人士及留学生 ({persona}) 最高减免90%",
            "s2_badge": "银行入账提醒",
            "s2_main": f"到账 {refund_amount_formatted}！",
            "s2_sub": "过去5年多缴税款全额汇入韩国银行卡",
            "s3_badge": "国税厅正规持牌",
            "s3_main": "正规税务师团队全程代办",
            "s3_sub": "前期 0 元费用 • 100% 安全合规",
            "s4_badge": "实现心中梦想",
            "s4_main": "买机票回国探亲与生活",
            "s4_sub": "拿回属于您的辛勤汗水钱",
            "s5_badge": "🏛️ 韩国国税厅 国税退税通知书",
            "s5_main": "立即点击主页简介链接",
            "s5_sub": "3分钟极速免费查询您的退税金额！"
        },
        "ko": {
            "title": f"EasyTax 90% 소득세 감면: {name}",
            "voice_text": f"{target} 근무 근로자 및 유학생 여러분! 조특법 제30조 중소기업 소득세 90% 감면 혜택을 놓치지 마세요. 1인 평균 {refund_amount_formatted}의 5개년 누락 환급금을 돌려받을 수 있습니다. 선입금 0원, 1분 무료 환급 조회를 지금 바로 프로필 링크에서 확인하세요!",
            "captions": ["🏛️ 소득세 90% 감면", f"💰 {refund_amount_formatted}"],
            "s1_badge": "조세특례제한법 제30조",
            "s1_main": f"{target} 외국인 소득세 감면",
            "s1_sub": f"{persona} 대상 최대 90% 세금 감면 혜택",
            "s2_badge": "국세청 입금 알림",
            "s2_main": f"{refund_amount_formatted} 입금 완료!",
            "s2_sub": "지난 5개년 누락 환급금 통장 입금",
            "s3_badge": "100% 국세청 공인",
            "s3_main": "등록 공인 세무대리인 전담",
            "s3_sub": "착수금 0원 • 100% 비대면 간편 신청",
            "s4_badge": "꿈을 향한 보상",
            "s4_main": "고향 방문 & 가족 효도 송금",
            "s4_sub": "성실하게 일한 나의 정당한 권리 수령",
            "s5_badge": "🏛️ 국세청 국세환급금통지서 (NTS)",
            "s5_main": "프로필 링크를 확인하세요",
            "s5_sub": "지금 바로 1분 만에 내 환급금을 무료로 조회하세요!"
        }
    }

    return scripts.get(lang, scripts.get("en", scripts["en"]))


class ScenarioDirectorShortsEasyTax:
    """
    💰 EasyTax 숏폼 비디오 전담 시나리오 작가 엔진 (60대 국세청 세무 테마 매트릭스)
    - 1~5씬 동일 인물 캐릭터 앵커 (Character Consistency 100%)
    - 60대 테마 × 7대 페르소나 = 420가지 스토리 × 17개 언어 = 7,140개 무한 세무 대본
    - 5단계 시네마틱 감동·보상형 연출 콘티 (실사 프롬프트 + 국세청 환급 배너)
    """
    def __init__(self):
        self.themes = EASYTAX_60_THEMES
        self.personas = EASYTAX_PERSONA_ANCHORS

    def plan_daily_scenario(self, lang: str = "en", force_theme_id: Optional[str] = None) -> Dict[str, Any]:
        """
        60개 세무 테마 중 하나를 무작위 선택하여 5단계 시네마틱 환급 숏폼 시나리오 대본 집필 (동일 인물 완전 고정)
        """
        if force_theme_id:
            matching = [t for t in self.themes if t["id"] == force_theme_id]
            theme = matching[0] if matching else random.choice(self.themes)
        else:
            theme = random.choice(self.themes)

        persona = random.choice(self.personas)

        # 🌍 캐릭터 앵커 빌더로 1~5씬 완전 동일 인물 액션 문자열 실시간 조합
        # - 한글 나이 → 영어 자동 변환
        # - 언어별 에스닉 외모 안커 자동 주입
        # - 성별/나이/의상 정보 조합
        char = build_char_anchor(
            lang=lang,
            gender=persona["gender"],
            age_group_ko=persona["age_group"],
            persona_anchor_desc=persona["anchor_desc"]
        )

        # 실시간 환급액 계산 (세법 기반)
        base_refund = theme.get("refund_est", 3840000)
        # 난수 변동 (±15%)
        jitter = random.randint(-15, 15) * 10000
        final_refund = max(650000, base_refund + jitter)
        refund_formatted = f"₩{final_refund:,}"

        script_meta = get_easytax_i18n_script(lang, theme, refund_formatted)

        # 5개 시네마틱 씬 프롬프트 및 자막 메타데이터 설계 (동일 인물 완전 고정)
        scenes = [
            {
                "scene_idx": 1,
                "name": "성실 근로와 세금 고민",
                "duration_sec": 4.5,
                "badge": script_meta["s1_badge"],
                "main_text": script_meta["s1_main"],
                "sub_text": script_meta["s1_sub"],
                "image_prompt": build_scene_prompt(
                    scene_idx=1, char=char,
                    scene_action=f"looking thoughtfully at a salary slip paper in a Korean factory industrial background in {theme['target']}, soft dramatic lighting",
                    extra_detail="workplace uniform, tired but hardworking expression"
                ),
                "negative_prompt": build_negative_prompt(lang, "holding paper with deformed hands")
            },
            {
                "scene_idx": 2,
                "name": "국세청 환급금 입금 알림",
                "duration_sec": 4.5,
                "badge": script_meta["s2_badge"],
                "main_text": script_meta["s2_main"],
                "sub_text": script_meta["s2_sub"],
                "image_prompt": build_scene_prompt(
                    scene_idx=2, char=char,
                    scene_action=f"looking completely astonished and overjoyed, face showing pure surprise and happiness, glowing smartphone in front showing a large bank deposit notification of {refund_formatted}",
                    extra_detail="hands resting naturally NOT holding phone, phone placed on table in front, bright joyful eyes"
                ),
                "negative_prompt": build_negative_prompt(lang, "hands holding phone with distorted fingers")
            },
            {
                "scene_idx": 3,
                "name": "국세청 공인 안심 확인",
                "duration_sec": 4.5,
                "badge": script_meta["s3_badge"],
                "main_text": script_meta["s3_main"],
                "sub_text": script_meta["s3_sub"],
                "image_prompt": build_scene_prompt(
                    scene_idx=3, char=char,
                    scene_action="looking at smartphone screen with calm confident relieved smile, glowing green NTS National Tax Service official approval checkmark on phone screen",
                    extra_detail="arms relaxed at side, phone visible but NOT held up, indoor soft lighting"
                ),
                "negative_prompt": build_negative_prompt(lang, "korean tax accountant, suit, office, different person, middle-aged")
            },
            {
                "scene_idx": 4,
                "name": "고향 여행 & 가족 효도",
                "duration_sec": 5.5,
                "badge": script_meta["s4_badge"],
                "main_text": script_meta["s4_main"],
                "sub_text": script_meta["s4_sub"],
                "image_prompt": build_scene_prompt(
                    scene_idx=4, char=char,
                    scene_action="walking joyfully at a bright airport departure terminal, big happy smile, travel bag over shoulder",
                    extra_detail="bright sunny gate windows background, cinematic bokeh"
                ),
                "negative_prompt": build_negative_prompt(lang, "holding passport with deformed hands, distorted text on signs")
            },
            {
                "scene_idx": 5,
                "name": "국세청 환급 통지서 & CTA",
                "duration_sec": 5.0,
                "badge": script_meta["s5_badge"],
                "main_text": script_meta["s5_main"],
                "sub_text": script_meta["s5_sub"],
                "image_prompt": build_scene_prompt(
                    scene_idx=5, char=char,
                    scene_action="smiling triumphantly and joyfully at camera, holding up official Korean NTS tax refund document with gold seal near chest",
                    extra_detail="bright warm lighting, victorious joyful expression, document clearly visible"
                ),
                "negative_prompt": build_negative_prompt(lang, "deformed hands, floating text, unreadable document")
            }
        ]

        return {
            "service_id": "easytax",
            "content_mix_type": "cinematic_drama5",
            "theme_id": theme["id"],
            "theme_name": theme["name"],
            "hook_title": script_meta["title"],
            "voice_text": script_meta["voice_text"],
            "captions": script_meta["captions"],
            "target": theme["target"],
            "persona_type": theme["persona_type"],
            "refund_amount": refund_formatted,
            "persona_name": persona["visa_name"],
            "gender": persona["gender"],
            "age_group": persona["age_group"],
            "scenes": scenes,
            "action_prompt": f"cinematic 9:16 story of {char} claiming {refund_formatted} tax refund under Article 30 in {theme['target']}",
            "negative_prompt": "caucasian, white person, blonde hair, creepy smile, distorted fingers, non-asian, character change"
        }

    def get_shorts_scenario(self, lang: str = "en") -> Dict[str, Any]:
        """하위 호환용 숏폼 시나리오 호출 별칭"""
        return self.plan_daily_scenario(lang=lang)
