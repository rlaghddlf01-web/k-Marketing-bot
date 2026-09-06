"""
ScenarioDirectorShortsKMarket - 🛒 [K-Market 전용 9:16 숏폼 AI 마스터 시나리오 작가 엔진]
- 50대 초정밀 대본 테마 매트릭스 (대학가 20개 + 품목별 15개 + 자취 에피소드 15개 + 산단 10개 = 총 60개 테마)
- 100% 동일 인물 캐릭터 앵커 (1~5씬 동일 인물 완전 고정)
- 50:50 듀얼 파이프라인:
  1) [A타입 (50%)]: 실시간 270개 매물 웹 아이프레임 스무스 스크롤 + 60대 테마별 17개국 20초 나레이션 대본
  2) [B타입 (50%)]: 5단계 헐리웃 감동 자취/이사/0원 나눔 드라마 대본 (동일 주인공 100% 일관성)
- 7대 외국인 페르소나 매트릭스 × 60대 로컬라이징 = 5,950가지 무한 순환 스토리텔링
"""

import json
import random
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import LANGUAGES, DATA_DIR
from core.character_anchor_kmarket import (
    build_char_anchor,
    build_scene_prompt,
    build_negative_prompt,
    LANG_ETHNIC_MAP
)

# ======================================================================
# 🎯 60대 초정밀 K-Market 숏폼 대본 테마 매트릭스
# ======================================================================

KMARKET_60_THEMES = [
    # ── [1. 전국 20대 대학가 캠퍼스 0원 나눔편 (20개)] ──
    {"id": "univ_yonsei_sinchon", "cat": "campus", "name": "신촌 연세대 원룸 선배들의 0원 책상 나눔", "target": "신촌 연세대/서강대/이대", "item": "원목 공부책상 & 의자"},
    {"id": "univ_korea_anam", "cat": "campus", "name": "안암 고려대 자취방 미니냉장고 득템 라이브", "target": "안암 고려대 캠퍼스", "item": "원룸 소형 미니냉장고"},
    {"id": "univ_skku_hyehwa", "cat": "campus", "name": "혜화 성균관대 석박사 연구실 스탠드 0원 나눔", "target": "혜화 성균관대/대학로", "item": "LED 스탠드 & 수납장"},
    {"id": "univ_khu_hoegi", "cat": "campus", "name": "회기 경희대·외대 유학생 원룸 침대 0원 득템", "target": "회기 경희대/한국외대", "item": "슈퍼싱글 침대 & 매트리스"},
    {"id": "univ_hanyang_wangsimni", "cat": "campus", "name": "왕십리 한양대 공대생 전자레인지 0원 릴레이", "target": "왕십리 한양대 원룸촌", "item": "전자레인지 & 토스터기"},
    {"id": "univ_snu_gwanak", "cat": "campus", "name": "신림·서울대입구 원룸 풀세트 무료 나눔 피드", "target": "관악 서울대입구/낙성대", "item": "자취방 가구 풀세트"},
    {"id": "univ_cau_heukseok", "cat": "campus", "name": "흑석 중앙대 자취촌 귀국 선배 생활가전 나눔", "target": "흑석 중앙대/노량진", "item": "쿠쿠 전기밥솥 & 식기"},
    {"id": "univ_sogang_sinchon", "cat": "campus", "name": "서강대 정문 앞 3초 번개 직거래 성공 현장", "target": "마포 신촌/서강대", "item": "3단 서랍장 & 행거"},
    {"id": "univ_ewha_daehyeon", "cat": "campus", "name": "이화여대 앞 원룸 화장대 & 전신거울 0원 득템", "target": "이대역/대현동 원룸", "item": "화장대 & 전신거울"},
    {"id": "univ_kwangwoon_nowon", "cat": "campus", "name": "노원 광운대 원룸 게이밍 모니터 꿀매물 피드", "target": "노원 광운대/과기대", "item": "컴퓨터 의자 & 모니터"},
    {"id": "univ_uos_dongdaemun", "cat": "campus", "name": "동대문 서울시립대 정문 앞 매트리스 나눔", "target": "전농동 서울시립대", "item": "라텍스 토퍼 매트리스"},
    {"id": "univ_skku_suwon", "cat": "campus", "name": "수원 율전 성균관대 자연캠 무빙세일 라이브", "target": "수원 율전동/성대역", "item": "소형 세탁기 & 청소기"},
    {"id": "univ_ajou_suwon", "cat": "campus", "name": "수원 아주대 삼거리 원룸 0원 가전 득템기", "target": "수원 아주대/원천동", "item": "에어프라이어 & 커피포트"},
    {"id": "univ_inha_incheon", "cat": "campus", "name": "인천 인하대 후문 원룸 책꽂이 무료 나눔", "target": "인천 인하대 후문가", "item": "5단 원목 책꽂이"},
    {"id": "univ_kaist_daejeon", "cat": "campus", "name": "대전 카이스트·충남대 궁동 0원 가구 피드", "target": "대전 유성구 궁동", "item": "인체공학 사무용 의자"},
    {"id": "univ_pnu_busan", "cat": "campus", "name": "부산대 정문 앞 원룸 이사 0원 나눔 대방출", "target": "부산 금정구 장전동", "item": "원룸 2인용 소파"},
    {"id": "univ_knu_daegu", "cat": "campus", "name": "대구 경북대 복현동 원룸 전기장판 0원 나눔", "target": "대구 북구 복현동", "item": "극세사 전기장판"},
    {"id": "univ_jnu_gwangju", "cat": "campus", "name": "광주 전남대 후문 유학생 무빙세일 핫딜", "target": "광주 북구 용봉동", "item": "미니 청소기 & 제습기"},
    {"id": "univ_cnu_cheongju", "cat": "campus", "name": "청주 충북대 중문 원룸 행거 0원 무료 득템", "target": "청주 서원구 사창동", "item": "스탠드 시스템 행거"},
    {"id": "univ_jbnu_jeonju", "cat": "campus", "name": "전주 전북대 구정문 앞 생활용품 무료 나눔", "target": "전주 덕진동 전북대", "item": "수납박스 & 접이식 테이블"},

    # ── [2. 가구·가전 품목별 득템편 (15개)] ──
    {"id": "item_queen_bed", "cat": "item", "name": "퀸사이즈 침대 & 프레임 0원 득템 꿀팁", "target": "전국 대학가/원룸촌", "item": "퀸사이즈 호텔식 침대"},
    {"id": "item_mini_fridge", "cat": "item", "name": "자취생 1순위 소형 냉장고 0원 직거래", "target": "서울/경기 원룸 밀집지역", "item": "1등급 에너지 소형 냉장고"},
    {"id": "item_study_desk", "cat": "item", "name": "깨끗한 1200 공부책상 0원 무료 수령기", "target": "대학가 자취방", "item": "1200x600 모던 책상"},
    {"id": "item_comfy_chair", "cat": "item", "name": "허리 편한 게이밍/사무용 메쉬 의자 0원", "target": "유학생 거주지역", "item": "고급 메쉬 사무용 의자"},
    {"id": "item_microwave", "cat": "item", "name": "자취 필수 전자레인지 0원 득템 현장", "target": "전국 외국인 커뮤니티", "item": "디지털 전자레인지"},
    {"id": "item_cuckoo_cooker", "cat": "item", "name": "쿠쿠 IH 6인용 압력밥솥 무료 나눔", "target": "수도권 원룸촌", "item": "쿠쿠 압력밥솥"},
    {"id": "item_warm_mat", "cat": "item", "name": "겨울철 필수 온수매트·전기장판 0원 나눔", "target": "전국 자취촌", "item": "프리미엄 온수매트"},
    {"id": "item_heater_fan", "cat": "item", "name": "강력 미니 온풍기 & 히터 무료 득템 피드", "target": "서울/경기 외국인 타운", "item": "초절전 PTC 온풍기"},
    {"id": "item_3tier_drawer", "cat": "item", "name": "원룸 정리 끝판왕 3단 서랍장 0원 꿀매물", "target": "대학가 원룸", "item": "화이트 3단 수납서랍장"},
    {"id": "item_system_hanger", "cat": "item", "name": "옷 정리 깔끔 시스템 이동식 행거 나눔", "target": "전국 원룸촌", "item": "2단 드레스룸 행거"},
    {"id": "item_airfryer", "cat": "item", "name": "대용량 에어프라이어 0원 득템 요리생활", "target": "외국인 유학생 커뮤니티", "item": "디지털 5L 에어프라이어"},
    {"id": "item_floor_lamp", "cat": "item", "name": "감성 자취방 인테리어 장스탠드 조명 0원", "target": "2030 자취생", "item": "북유럽풍 장스탠드 조명"},
    {"id": "item_full_mirror", "cat": "item", "name": "외출 필수 전신거울 0원 직거래 수령기", "target": "원룸 밀집지역", "item": "원목 스탠딩 전신거울"},
    {"id": "item_cordless_vacuum", "cat": "item", "name": "무선 싸이클론 청소기 0원 무료 나눔", "target": "전국 자취방", "item": "스틱형 무선 청소기"},
    {"id": "item_toaster_kettle", "cat": "item", "name": "모닝 토스터기 & 유리 전기주전자 세트 0원", "target": "유학생 기숙사촌", "item": "토스터기 & 무선포트 세트"},

    # ── [3. 이사 & 자취 리얼 에피소드편 (15개)] ──
    {"id": "story_senior_farewell", "cat": "story", "name": "졸업 귀국 선배가 통째로 물려준 0원 가구", "target": "대학교 정문 앞 직거래", "item": "선배가 아끼던 가구 5종"},
    {"id": "story_sticker_zero_fee", "cat": "story", "name": "원룸 방빼기 대형폐기물 스티커 비용 0원 절약", "target": "이사 준비 자취생", "item": "폐기 직전 깨끗한 가구"},
    {"id": "story_first_room_setup", "cat": "story", "name": "0원으로 풀세팅한 한국 첫 자취방 랜선집들이", "target": "한국 입국 신입생", "item": "0원 인테리어 풀세트"},
    {"id": "story_roommate_deal", "cat": "story", "name": "룸메이트와 둘이서 0원으로 방 꾸민 썰", "target": "2인 거주 유학생", "item": "공동생활 가전/가구"},
    {"id": "story_rainy_day_warmth", "cat": "story", "name": "비오는 날 이웃이 우산 씌워주며 침대 나눔해준 실화", "target": "동네 이웃 직거래", "item": "따뜻한 정이 담긴 침대"},
    {"id": "story_lightning_meetup", "cat": "story", "name": "채팅하고 10분 만에 집 앞 직거래 성공기", "target": "동네 생활권 직거래", "item": "10분 컷 무료 나눔"},
    {"id": "story_safe_campus_gate", "cat": "story", "name": "학생증 인증으로 100% 안전한 대학교 정문 거래", "target": "여학생 안심 직거래", "item": "안심 인증 0원 물품"},
    {"id": "story_empty_floor_tears", "cat": "story", "name": "차가운 방바닥에서 울던 날 K-Market을 만났다", "target": "외국인 입국 초기", "item": "첫날 구원해 준 매트리스"},
    {"id": "story_friendly_korean_uncle", "cat": "story", "name": "한국인 집주인 아저씨가 추천해 준 0원 나눔 앱", "target": "원룸 거주자", "item": "집주인 추천 필수 가구"},
    {"id": "story_weekend_flea_market", "cat": "story", "name": "주말 동네 주민 무빙세일에서 0원으로 득템하기", "target": "주말 벼룩시장", "item": "생활 소품 & 주방기구"},
    {"id": "story_saving_millions", "cat": "story", "name": "가구값 150만원 아껴서 학비 보탠 유학생 후기", "target": "알뜰 유학생", "item": "150만원 상당 0원 가구"},
    {"id": "story_subway_exit_trade", "cat": "story", "name": "지하철 2호선 역세권 출구 앞 1분 직거래", "target": "지하철역 출구", "item": "간편 캐리어 수령 물품"},
    {"id": "story_clean_state_shock", "cat": "story", "name": "새것 같은 상태에 깜짝 놀란 0원 나눔 후기", "target": "상태 A급 매물", "item": "거의 새것 같은 A급 가구"},
    {"id": "story_korean_culture_gift", "cat": "story", "name": "나눔 받으며 한국의 정을 처음 배운 외국인", "target": "다문화 이웃", "item": "따뜻한 나눔의 선물"},
    {"id": "story_graduating_relief", "cat": "story", "name": "귀국 전날 모든 짐 0원 나눔으로 완벽 정리 완료", "target": "귀국 예정자", "item": "전체 이삿짐 홀가분 정리"},

    # ── [4. 전국 10대 산업단지 기숙사 & 원룸편 (10개)] ──
    {"id": "ind_ansan_wongok", "cat": "industry", "name": "안산 원곡동 다문화거리 근로자 원룸 0원 가전", "target": "안산 반월공단/원곡동", "item": "원룸 소형 세탁기 & 냉장고"},
    {"id": "ind_suwon_yeongtong", "cat": "industry", "name": "수원 영통 테크노밸리 기숙사 무빙세일 핫딜", "target": "수원 영통/삼성전자 산단", "item": "전자레인지 & 미니 청소기"},
    {"id": "ind_pyeongtaek_godeok", "cat": "industry", "name": "평택 고덕 삼성캠퍼스 앞 원룸 방빼기 0원 피드", "target": "평택 고덕/서정리역", "item": "원목 수납 침대"},
    {"id": "ind_hwaseong_hyangnam", "cat": "industry", "name": "화성 향남 제약공단 외국인 근로자 0원 나눔", "target": "화성 향남/발안 산단", "item": "온풍기 & 전기장판"},
    {"id": "ind_guro_gasan", "cat": "industry", "name": "구로·가산 디지털단지 오피스텔 무빙세일", "target": "구로디지털/가산디지털", "item": "사무용 메쉬 의자 & 책상"},
    {"id": "ind_asan_tangjeong", "cat": "industry", "name": "아산 탕정 디스플레이단지 원룸 생활용품 나눔", "target": "아산 탕정/천안 불당", "item": "수납장 & 밥솥 세트"},
    {"id": "ind_cheonan_baekseok", "cat": "industry", "name": "천안 백석·성성공단 기숙사 0원 가구 대방출", "target": "천안 백석공단/두정동", "item": "미니 냉장고 & 옷장"},
    {"id": "ind_cheongju_ochang", "cat": "industry", "name": "청주 오창 과학산단 원룸 0원 나눔 라이브", "target": "청주 오창산단/오송", "item": "에어프라이어 & 식탁"},
    {"id": "ind_ulsan_onsan", "cat": "industry", "name": "울산 온산 국가산단 엔지니어 기숙사 무빙세일", "target": "울산 온산/남구 달동", "item": "퀸 침대 & 가전 풀세트"},
    {"id": "ind_changwon_national", "cat": "industry", "name": "창원 국가산단 외국인 근로자 따뜻한 0원 나눔", "target": "창원 성산구/마산 원룸", "item": "온수매트 & 수납 행거"}
]

# 🎯 7대 외국인 페르소나별 100% 동일 인물 고정 앵커 (외모, 헤어, 의상 완전 고정)
KMARKET_PERSONA_ANCHORS = [
    {
        "persona_id": "sinchon_female_d2",
        "name": "동양인 신입 유학생 (신촌 연세대 원룸)",
        "gender": "female",
        "age_group": "20대 초반",
        "town": "서울 신촌 대학가",
        "anchor_desc": "a specific 21-year-old Asian female college student with shoulder-length black straight bob haircut, gentle dark brown eyes, fair skin, wearing an oversized pastel beige knit sweater and neat blue denim pants"
    },
    {
        "persona_id": "anam_male_d2",
        "name": "동양인 어학연수생 (안암 고려대 자취방)",
        "gender": "male",
        "age_group": "20대 초반",
        "town": "서울 안암 대학가",
        "anchor_desc": "a specific 22-year-old Asian male college student with neat short black side-part haircut, clean-shaven face, warm cheerful smile, wearing a dark green university hoodie"
    },
    {
        "persona_id": "ansan_female_e9",
        "name": "동양인 제조공단 근로자 (안산 원곡동 원룸)",
        "gender": "female",
        "age_group": "20대 후반",
        "town": "안산 다문화 타운",
        "anchor_desc": "a specific 27-year-old Asian woman with a clean black ponytail, kind dark eyes, wearing a simple comfortable navy zip-up fleece jacket and grey casual trousers"
    },
    {
        "persona_id": "suwon_male_e9",
        "name": "동양인 산업단지 근로자 (수원 영통 기숙사)",
        "gender": "male",
        "age_group": "20대 후반",
        "town": "수원 영통 공단",
        "anchor_desc": "a specific 28-year-old Asian man with short athletic black haircut, honest friendly facial features, wearing a comfortable heather grey crewneck sweatshirt"
    },
    {
        "persona_id": "hyehwa_male_d2",
        "name": "동양인 석박사 대학원생 (혜화 성균관대)",
        "gender": "male",
        "age_group": "20대 후반",
        "town": "서울 혜화 대학가",
        "anchor_desc": "a specific 26-year-old Asian male graduate researcher wearing modern slim black wire-frame glasses, tidy black hair, wearing an olive brown corduroy button-up shirt"
    },
    {
        "persona_id": "gangnam_female_e7",
        "name": "동양인 IT 엔지니어 (판교/강남 직거래)",
        "gender": "female",
        "age_group": "30대 초반",
        "town": "서울 강남/역삼",
        "anchor_desc": "a specific 30-year-old Asian career woman with elegant wavy dark brown hair, bright intelligent eyes, wearing a stylish light blue tailored casual blouse"
    },
    {
        "persona_id": "guro_male_f4",
        "name": "동포/동양인 전문직 (구로/대림 원룸)",
        "gender": "male",
        "age_group": "30대 초반",
        "town": "서울 구로 디지털",
        "anchor_desc": "a specific 31-year-old Asian man with neatly styled parted dark hair, confident warm smile, wearing a clean black smart casual polo shirt"
    }
]

# 🎯 17개국 20초 나레이션 대본 템플릿 생성 엔진 (카드뉴스 감동 첫 만남 공식 동기화)
def get_i18n_script(lang: str, theme: Dict[str, Any]) -> Dict[str, Any]:
    name = theme["name"]
    target = theme["target"]
    item = theme["item"]

    scripts = {
        "vi": {
            "title": f"K-Market 0 Won: {name}",
            "voice_text": f"Đừng mua đồ nội thất đắt đỏ tại {target}! Hôm nay tôi đã nhận miễn phí {item} từ người hàng xóm tốt bụng, tiết kiệm hơn 1,5 triệu Won. Bí quyết là ứng dụng K-Market! Hàng trăm đồ dùng 0 Won được tặng mỗi ngày với dịch tự động 17 ngôn ngữ. Nhấp vào link bio nhận ngay hôm nay!",
            "captions": ["🎁 0 Won MIỄN PHÍ!", f"📍 {target}"],
            "s1_badge": "GIAO DỊCH ẤM ÁP",
            "s1_main": f"Nhận {item} 0 Won Tại {target}",
            "s1_sub": "Được hàng xóm tốt bụng tặng miễn phí",
            "s2_badge": "CĂN PHÒNG HOÀN HẢO",
            "s2_main": "Tiết Kiệm 1.500.000 Won!",
            "s2_sub": "Căn phòng trở nên ấm cúng và đầy đủ",
            "s3_badge": "BÍ QUYẾT Ở ĐÂU?",
            "s3_main": "Ứng Dụng K-Market 0 Won",
            "s3_sub": "Hàng trăm món đồ 0 Won từ người chuyển nhà",
            "s4_badge": "AN TÂM 1:1",
            "s4_main": "Tự Động Dịch 17 Ngôn Ngữ",
            "s4_sub": "Chat và hẹn gặp an toàn chỉ trong 10 phút",
            "s5_badge": "NHẬN 0 WON NGAY",
            "s5_main": "Nhấp Vào Link Trong Bio",
            "s5_sub": f"Nhận ngay {item} 0 Won hôm nay!"
        },
        "uz": {
            "title": f"K-Market 0 Von: {name}",
            "voice_text": f"{target}da qimmat mebel sotib olmang! Bugun saxiy qo'shnimdan {item}ni 0 vonga bepul olib, 1.5 million von tejab qoldim. Sirri K-Market ilovasida! Har kuni yuzlab 0 vonlik buyumlar berilmoqda. 17 tildagi avtomatik tarjima bilan profil havolasidan hoziroq bepul oling!",
            "captions": ["🎁 0 Von BEPUL!", f"📍 {target}"],
            "s1_badge": "SAMIMIY UCHRASHUV",
            "s1_main": f"{target}da 0 Vonga {item} Oldim",
            "s1_sub": "Mehribon qo'shnidan tekinga sovg'a",
            "s2_badge": "SHINNAM XONA TAYYOR",
            "s2_main": "1.500.000 Von Tejandi!",
            "s2_sub": "Xonam bir kunda shinam holga keldi",
            "s3_badge": "SIRRI NIMADA?",
            "s3_main": "K-Market 0 Von Ilovasi",
            "s3_sub": "Ko'chib ketuvchilardan bepul buyumlar",
            "s4_badge": "XAVFSIZ 1:1 CHAT",
            "s4_main": "17 Tildagi Avtomatik Tarjima",
            "s4_sub": "10 daqiqada xavfsiz uchrashuv belgilandi",
            "s5_badge": "BEPUL OLING",
            "s5_main": "Profil Havolasini Bosing",
            "s5_sub": f"Bugun {item}ni bepul olib keting!"
        },
        "ru": {
            "title": f"K-Market 0 Вон: {name}",
            "voice_text": f"Не тратьте деньги на дорогую мебель в {target}! Сегодня я бесплатно забрал отличный {item} у доброго соседа, сэкономив 1.5 миллиона вон. Секрет в приложении K-Market! Сотни бесплатных вещей отдают каждый день с автопереводом на 17 языков. Жмите ссылку в профиле и забирайте даром!",
            "captions": ["🎁 0 Вон БЕСПЛАТНО!", f"📍 {target}"],
            "s1_badge": "ТЕПЛАЯ ВСТРЕЧА",
            "s1_main": f"Забрал {item} За 0 Вон в {target}",
            "s1_sub": "Подарок от доброго соседа по району",
            "s2_badge": "УЮТНЫЙ ДОМ ГОТОВ",
            "s2_main": "Сэкономил 1.500.000 Вон!",
            "s2_sub": "Комната преобразилась всего за один день",
            "s3_badge": "В ЧЕМ СЕКРЕТ?",
            "s3_main": "Приложение K-Market 0 Вон",
            "s3_sub": "Сотни вещей за 0 вон от выпускников",
            "s4_badge": "БЕЗОПАСНАЯ СДЕЛКА",
            "s4_main": "Авто-Переводчик На 17 Языков",
            "s4_sub": "Встреча возле дома за 10 минут",
            "s5_badge": "ЗАБИРАЙТЕ ДАРОМ",
            "s5_main": "Жми Ссылку В Профиле",
            "s5_sub": f"Заберите {item} за 0 вон прямо сейчас!"
        },
        "en": {
            "title": f"K-Market $0 Free: {name}",
            "voice_text": f"Don't waste money on expensive furniture in {target}! Today I got a clean {item} 100% free from a kind neighbor, saving over 1.5 million Won. The secret is K-Market app! Hundreds of $0 free items posted daily with instant 17-language chat translation. Check the link in bio to grab your $0 free items today!",
            "captions": ["🎁 $0 Won 100% FREE!", f"📍 {target}"],
            "s1_badge": "HEARTWARMING MEETUP",
            "s1_main": f"Claimed Free {item} in {target}",
            "s1_sub": "Gifted by a wonderful local neighbor",
            "s2_badge": "DREAM COZY ROOM",
            "s2_main": "Saved 1,500,000 KRW!",
            "s2_sub": "Turned empty studio into cozy sweet home",
            "s3_badge": "HOW TO GET IT?",
            "s3_main": "K-Market $0 Free App Feed",
            "s3_sub": "Hundreds of $0 free giveaways from moving expats",
            "s4_badge": "SAFE 1:1 TRADING",
            "s4_main": "17 Languages Instant Auto-Chat",
            "s4_sub": "Coordinated meetup outside within 10 minutes",
            "s5_badge": "CLAIM $0 FREE TODAY",
            "s5_main": "Click Link In Bio Now",
            "s5_sub": f"Get your $0 free {item} today!"
        },
        "zh": {
            "title": f"K-Market 0韩元好物: {name}",
            "voice_text": f"在 {target} 千万别花大钱买家具！今天我在好心邻居那免费领到了九成新 {item}，立省 150万韩元。秘诀就是 K-Market App！毕业前辈每天发布海量 0元好物，支持 17 种语言自动翻译。快点击主页链接免费领取吧！",
            "captions": ["🎁 0 韩元免费赠送!", f"📍 {target}"],
            "s1_badge": "温馨暖心直交",
            "s1_main": f"在 {target} 免费领到 {item}",
            "s1_sub": "好心邻居前辈免费赠送九成新好物",
            "s2_badge": "温馨小窝完成",
            "s2_main": "立省 1,500,000 韩元！",
            "s2_sub": "空荡荡的房间瞬间变身温馨小窝",
            "s3_badge": "从哪里找到的？",
            "s3_main": "K-Market 0韩元好物 App",
            "s3_sub": "海量毕业回国前辈 0元大方赠送",
            "s4_badge": "安全 1:1 直交",
            "s4_main": "17国语言实时自动翻译",
            "s4_sub": "无语言障碍 10分钟校门口安全交接",
            "s5_badge": "立即免费领取",
            "s5_main": "点击主页简介链接",
            "s5_sub": f"马上领取今日 0元 {item}！"
        },
        "ko": {
            "title": f"K-Market 0원 나눔: {name}",
            "voice_text": f"{target}에서 비싼 가구 사지 마세요! 오늘 이웃에게 깨끗한 {item}을 0원에 무료 나눔받아 가구값 150만 원을 아꼈습니다. 비결은 바로 K-Market 앱! 매일 쏟아지는 0원 매물과 17개 언어 실시간 자동 번역으로 10분 만에 안심 직거래 완료. 지금 프로필 링크에서 0원 매물을 확인하세요!",
            "captions": ["🎁 0원 무료 나눔!", f"📍 {target}"],
            "s1_badge": "따뜻한 이웃 나눔",
            "s1_main": f"{target} 0원 직거래 수령",
            "s1_sub": f"선배와 이웃이 선물하는 깨끗한 {item}",
            "s2_badge": "아늑한 방 완성",
            "s2_main": "가구값 150만원 절약 성공!",
            "s2_sub": "텅 빈 방이 하루 만에 완벽한 스위트룸으로",
            "s3_badge": "도대체 어디서?",
            "s3_main": "K-Market 0원 무료나눔 피드",
            "s3_sub": "매일 쏟아지는 0원 실물 가구·가전 매물",
            "s4_badge": "안심 1:1 직거래",
            "s4_main": "17개 언어 실시간 자동번역",
            "s4_sub": "채팅 10분 만에 집 앞에서 안전하게 약속 완료",
            "s5_badge": "지금 0원 득템",
            "s5_main": "프로필 링크에서 지금 받기",
            "s5_sub": f"K-Market 앱에서 오늘 0원 {item} 바로 신청하세요!"
        }
    }

    return scripts.get(lang, scripts.get("en", scripts["en"]))


class ScenarioDirectorShortsKMarket:
    """
    🛒 K-Market 숏폼 비디오 전담 시나리오 작가 엔진 (60대 테마 50:50 듀얼 파이프라인)
    - 1~5씬 동일 인물 캐릭터 앵커 (Character Consistency 100%)
    - 60대 테마 × 7대 페르소나 = 420가지 스토리 × 17개 언어 = 7,140개 무한 대본
    - 50% [A타입]: 실시간 270개 매물 웹 아이프레임 스크롤 + 60대 테마 20초 맞춤 나레이션
    - 50% [B타입]: 5단계 헐리웃 감동 자취/이사 드라마 대본 (동일 인물 일관성)
    """
    def __init__(self):
        self.themes = KMARKET_60_THEMES
        self.personas = KMARKET_PERSONA_ANCHORS

    def plan_daily_scenario(self, lang: str = "en", force_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        60개 테마 중 하나를 무작위 선택하여 50:50 듀얼 파이프라인 시나리오 대본 집필
        """
        theme = random.choice(self.themes)
        persona = random.choice(self.personas)
        script_meta = get_i18n_script(lang, theme)

        # 🌍 캐릭터 앵커 빌더로 1~5씬 완전 동일 인물 액션 문자열 실시간 조합
        char = build_char_anchor(
            lang=lang,
            gender=persona["gender"],
            age_group_ko=persona["age_group"],
            persona_anchor_desc=persona["anchor_desc"]
        )

        # 50:50 모드 결정 (force_mode 없으면 50% 랜덤)
        if force_mode:
            is_feed_mode = (force_mode == "A_feed_scroll" or force_mode == "iframe")
        else:
            is_feed_mode = (random.random() < 0.50)

        if is_feed_mode:
            # 📱 [A타입 (50%)]: 실물 270개 매물 아이프레임 스크롤 모드
            return {
                "service_id": "kmarket",
                "content_mix_type": "A_feed_scroll",
                "theme_id": theme["id"],
                "theme_name": theme["name"],
                "hook_title": script_meta["title"],
                "voice_text": script_meta["voice_text"],
                "captions": script_meta["captions"],
                "badge_text": f"0원 나눔 LIVE ({theme['target']})",
                "persona_name": persona["name"],
                "town": theme["target"],
                "item": theme["item"],
                "gender": persona["gender"],
                "age_group": persona["age_group"],
                "action_prompt": f"authentic smartphone screen recording of {theme['name']} in {theme['target']}, clean Korean UI",
                "negative_prompt": "caucasian, white person, blonde hair, distorted text, creepy smile, bad anatomy"
            }

        else:
            # 🎭 [B타입 (50%)]: 5단계 헐리웃 감동 드라마 모드 (카드뉴스 첫 만남 감동 공식 + 씬 3,4 실물 웹 하이브리드)
            scenes = [
                {
                    "scene_idx": 1,
                    "name": "따뜻한 이웃 0원 나눔 만남",
                    "duration_sec": 3.8,
                    "badge": script_meta["s1_badge"],
                    "main_text": script_meta["s1_main"],
                    "sub_text": script_meta["s1_sub"],
                    "image_prompt": (
                        f"cinematic authentic two-shot medium shot of two diverse foreign residents in South Korea "
                        f"(one friendly Southeast Asian Vietnamese student and one warm Central Asian Uzbek expat neighbor) "
                        f"standing facing each other outdoors on a clean authentic Korean residential street near {theme['target']}. "
                        f"Both people are completely visible from the waist up, both faces and warm friendly smiles clearly visible, "
                        f"making pleasant eye contact as they respectfully hand over and exchange a clean {theme['item']} or neatly wrapped gift box between them. "
                        f"Natural daytime lighting, real Korean residential neighborhood background with quiet storefronts, authentic heartwarming community meetup, masterpiece 8k"
                    ),
                    "negative_prompt": (
                        "disembodied hands, only hands visible, headless person, cropped heads, cropped face, single person portrait, "
                        "bad anatomy, extra limbs, deformed fingers, floating objects, blurry"
                    )
                },
                {
                    "scene_idx": 2,
                    "name": "아늑한 방 완성 & 150만원 절약",
                    "duration_sec": 3.8,
                    "badge": script_meta["s2_badge"],
                    "main_text": script_meta["s2_main"],
                    "sub_text": script_meta["s2_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=2, char=char,
                        scene_action=f"cinematic authentic bust-shot portrait, peaceful relieved warm smile relaxing in cozy beautifully furnished Korean studio room with {theme['item']} under warm interior lamp lighting, content happy mood, comfortable home atmosphere",
                        extra_detail="natural cozy room interior, warm soft lighting, authentic student lifestyle relief"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "extra fingers, deformed hands, stressed expression")
                },
                {
                    "scene_idx": 3,
                    "name": "실물 K-Market 0원 피드 탐방",
                    "duration_sec": 3.5,
                    "badge": script_meta["s3_badge"],
                    "main_text": script_meta["s3_main"],
                    "sub_text": script_meta["s3_sub"],
                    "image_prompt": None,  # 📱 씬 3: 스마트폰 실물 피드 스크롤 비디오 클립 대체
                    "negative_prompt": ""
                },
                {
                    "scene_idx": 4,
                    "name": "실시간 1:1 자동번역 채팅 & 예약",
                    "duration_sec": 3.5,
                    "badge": script_meta["s4_badge"],
                    "main_text": script_meta["s4_main"],
                    "sub_text": script_meta["s4_sub"],
                    "image_prompt": None,  # 📱 씬 4: 실시간 1:1 채팅 및 예약 확정 비디오 클립 대체
                    "negative_prompt": ""
                },
                {
                    "scene_idx": 5,
                    "name": "자신감 넘치는 최종 추천 & CTA",
                    "duration_sec": 4.0,
                    "badge": script_meta["s5_badge"],
                    "main_text": script_meta["s5_main"],
                    "sub_text": script_meta["s5_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=5, char=char,
                        scene_action=f"cinematic authentic direct-gaze portrait in the warmly furnished Korean room with {theme['item']}, looking directly into camera with an encouraging and decisive confident smile, pointing forward with friendly inviting gesture motivating viewer to get free items",
                        extra_detail="high charisma, strong direct eye contact, sharp focus, professional creator lifestyle portrait"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "extra limbs, creepy face, distorted furniture, instagram selfie")
                }
            ]

            return {
                "service_id": "kmarket",
                "content_mix_type": "B_gemini_story5",
                "theme_id": theme["id"],
                "theme_name": theme["name"],
                "hook_title": script_meta["title"],
                "voice_text": script_meta["voice_text"],
                "captions": script_meta["captions"],
                "target": theme["target"],
                "item": theme["item"],
                "persona_name": persona["name"],
                "town": theme["target"],
                "gender": persona["gender"],
                "age_group": persona["age_group"],
                "scenes": scenes,
                "action_prompt": f"cinematic authentic 9:16 story of {char} getting 0 KRW free {theme['item']} in {theme['target']}",
                "negative_prompt": "caucasian, white person, blonde hair, creepy smile, distorted fingers, non-asian, character change"
            }

    def get_shorts_scenario(self, lang: str = "en") -> Dict[str, Any]:
        """하위 호환용 숏폼 시나리오 호출 별칭"""
        return self.plan_daily_scenario(lang=lang)

