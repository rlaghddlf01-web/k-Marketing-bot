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

# 🎯 17개국 20초 나레이션 대본 템플릿 생성 엔진
def get_i18n_script(lang: str, theme: Dict[str, Any]) -> Dict[str, Any]:
    name = theme["name"]
    target = theme["target"]
    item = theme["item"]

    scripts = {
        "vi": {
            "title": f"K-Market 0 Won: {name}",
            "voice_text": f"Bạn đang ở khu vực {target}? Đừng mua đồ nội thất đắt đỏ! Trên app K-Market hôm nay đang tặng miễn phí {item} và hàng trăm đồ dùng 0 Won từ sinh viên và người chuyển nhà. Tải K-Market nhận ngay hôm nay!",
            "captions": ["🎁 0 Won MIỄN PHÍ!", f"📍 {target}"],
            "s1_badge": "PHÒNG TRỌ MỚI TẠI HÀN",
            "s1_main": f"Phòng Trống Tại {target}",
            "s1_sub": f"Mua {item} mới quá đắt đỏ",
            "s2_badge": "ÁP LỰC CHI PHÍ",
            "s2_main": f"Giá {item} Quá Cao?",
            "s2_sub": f"Tốn hàng trăm nghìn Won...",
            "s3_badge": "KHÁM PHÁ K-MARKET",
            "s3_main": f"Tặng {item} 0 Won!",
            "s3_sub": "Đồ dùng còn rất mới từ người tốt nghiệp",
            "s4_badge": "GIAO DỊCH ẤM ÁP",
            "s4_main": "Giao Dịch 1:1 An Toàn",
            "s4_sub": "Chat tự động dịch 17 ngôn ngữ",
            "s5_badge": "CĂN PHÒNG HOÀN HẢO",
            "s5_main": "Nhấp Vào Link Bio",
            "s5_sub": f"Nhận ngay {item} 0 Won hôm nay!"
        },
        "uz": {
            "title": f"K-Market 0 Von: {name}",
            "voice_text": f"Siz {target} atrofida yashaysizmi? Qimmat mebel sotib olmang! Bugun K-Market ilovasida {item} va yuzlab buyumlar 0 von bepul berilmoqda. 17 tildagi avtomatik tarjima bilan hoziroq bepul oling!",
            "captions": ["🎁 0 Von BEPUL!", f"📍 {target}"],
            "s1_badge": "YANGI XONA KOREYADA",
            "s1_main": f"{target} Bo'm-bo'sh Xona",
            "s1_sub": f"Yangi {item} juda qimmat",
            "s2_badge": "XARAJAT TASHVISHI",
            "s2_main": f"{item} Narxi Qimmatmi?",
            "s2_sub": "Yuz minglab von turadi...",
            "s3_badge": "K-MARKETNI TOPDIK",
            "s3_main": f"0 Vonlik Bepul {item}!",
            "s3_sub": "Yangi holatdagi tekin mebellar",
            "s4_badge": "SAMIMIY UCHRASHUV",
            "s4_main": "Xavfsiz 1:1 Qabul Qilish",
            "s4_sub": "17 tildagi avtomatik tarjima",
            "s5_badge": "SHINNAM XONA TAYYOR",
            "s5_main": "Profil Havolasini Bosing",
            "s5_sub": f"Bugun {item}ni bepul oling!"
        },
        "ru": {
            "title": f"K-Market 0 Вон: {name}",
            "voice_text": f"Живете в районе {target}? Не тратьте деньги на дорогую мебель! В приложении K-Market прямо сейчас бесплатно отдают {item} и сотни других вещей за 0 вон. Скачайте K-Market и заберите даром!",
            "captions": ["🎁 0 Вон БЕСПЛАТНО!", f"📍 {target}"],
            "s1_badge": "НОВАЯ КОМНАТА В КОРЕЕ",
            "s1_main": f"Пустая Комната в {target}",
            "s1_sub": f"Новая {item} стоит дорого",
            "s2_badge": "ДОРОГИЕ РАСХОДЫ",
            "s2_main": f"Где Взять {item}?",
            "s2_sub": "Тратить сотни тысяч вон...",
            "s3_badge": "ОТКРЫТИЕ K-MARKET",
            "s3_main": f"Бесплатная {item} За 0 Вон!",
            "s3_sub": "Отличные вещи отдают даром",
            "s4_badge": "ТЕПЛАЯ ВСТРЕЧА",
            "s4_main": "Безопасная 1:1 Сделка",
            "s4_sub": "Авто-переводчик на 17 языков",
            "s5_badge": "УЮТНЫЙ ДОМ ГОТОВ",
            "s5_main": "Жми На Ссылку В Профиле",
            "s5_sub": f"Забирай {item} за 0 вон прямо сейчас!"
        },
        "en": {
            "title": f"K-Market $0 Free: {name}",
            "voice_text": f"Living near {target}? Don't waste money on expensive furniture! On K-Market app today, clean {item} and hundreds of items are given away 100% free. Download K-Market and grab yours now!",
            "captions": ["🎁 $0 Won 100% FREE!", f"📍 {target}"],
            "s1_badge": "FIRST STUDIO IN KOREA",
            "s1_main": f"Empty Room in {target}",
            "s1_sub": f"Brand new {item} is too expensive",
            "s2_badge": "BUDGET OVERLOAD",
            "s2_main": f"Where To Get {item}?",
            "s2_sub": "Costs hundreds of thousands of Won...",
            "s3_badge": "DISCOVERED K-MARKET",
            "s3_main": f"$0 Free {item} Giveaways!",
            "s3_sub": "Graduating seniors giving away neat items",
            "s4_badge": "HEARTWARMING MEETUP",
            "s4_main": "Safe 1:1 Direct Meetup",
            "s4_sub": "Instant auto-translated chat in 17 languages",
            "s5_badge": "DREAM COZY ROOM",
            "s5_main": "Click Link In Bio Now",
            "s5_sub": f"Claim your $0 free {item} today!"
        },
        "zh": {
            "title": f"K-Market 0韩元好物: {name}",
            "voice_text": f"住在 {target} 附近吗？千万别花大钱买家具！今天在 K-Market App 上，有毕业前辈免费赠送九成新 {item} 和海量 0元好物。支持 17 种语言自动翻译，快来免费领取吧！",
            "captions": ["🎁 0 韩元免费赠送!", f"📍 {target}"],
            "s1_badge": "韩国租房第一天",
            "s1_main": f"{target} 空荡荡的房间",
            "s1_sub": f"买全新 {item} 实在太贵",
            "s2_badge": "沉重开销压力",
            "s2_main": f"买不起 {item} 怎么办？",
            "s2_sub": f"到处都要花几十万韩元...",
            "s3_badge": "发现K-MARKET",
            "s3_main": f"海量 0元免费赠送 {item}！",
            "s3_sub": "毕业回国前辈免费赠送九成新好物",
            "s4_badge": "温馨安全直交易",
            "s4_main": "校门口 1:1 当面安全交接",
            "s4_sub": "17国语言实时自动翻译",
            "s5_badge": "打造温馨小窝",
            "s5_main": "立即点击主页简介链接",
            "s5_sub": f"马上领取今日 0元 {item}！"
        },
        "ko": {
            "title": f"K-Market 0원 나눔: {name}",
            "voice_text": f"{target} 근처 자취생·유학생 여러분! 비싼 가구 사지 마세요. 오늘 K-Market 앱에서 깨끗한 {item}을 포함한 수백 개의 0원 무료나눔 매물이 올라왔습니다. 지금 바로 0원에 득템하세요!",
            "captions": ["🎁 0원 무료 나눔!", f"📍 {target}"],
            "s1_badge": "STEP 1: 차가운 방바닥",
            "s1_main": f"{target} 원룸 입주 첫날",
            "s1_sub": f"새 {item} 사기엔 너무 비싼 자취 생활",
            "s2_badge": "STEP 2: 가격 부담",
            "s2_main": "가구 살 돈이 부족할 때?",
            "s2_sub": f"{item} 가격만 수십만 원...",
            "s3_badge": "STEP 3: 0원 득템 발견",
            "s3_main": f"K-Market 0원 무료나눔!",
            "s3_sub": f"{target} 이웃이 선물하는 깨끗한 {item}",
            "s4_badge": "STEP 4: 안심 직거래",
            "s4_main": "따뜻한 이웃과 1:1 직거래",
            "s4_sub": "17개 언어 자동번역으로 100% 안심",
            "s5_badge": "STEP 5: 아늑한 내 방",
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
            # 🎭 [B타입 (50%)]: 5단계 헐리웃 감동 드라마 모드 (1~5씬 동일 인물 완전 고정)
            scenes = [
                {
                    "scene_idx": 1,
                    "name": "텅 빈 원룸의 막막함",
                    "duration_sec": 4.5,
                    "badge": script_meta["s1_badge"],
                    "main_text": script_meta["s1_main"],
                    "sub_text": script_meta["s1_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=1, char=char,
                        scene_action=f"sitting on the yellow linoleum floor of a real empty Korean studio apartment room surrounded by open cardboard moving boxes and packing tape near {theme['target']}, wiping forehead looking exhausted and overwhelmed by moving costs",
                        extra_detail="unposed candid shot, natural room lighting through window, looking away at the empty room NOT at camera"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "floating furniture, instagram model pose, glamour shoot")
                },
                {
                    "scene_idx": 2,
                    "name": "비싼 가구 가격에 좌절",
                    "duration_sec": 4.5,
                    "badge": script_meta["s2_badge"],
                    "main_text": script_meta["s2_main"],
                    "sub_text": script_meta["s2_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=2, char=char,
                        scene_action=f"leaning against the plain wallpaper in the studio apartment room, looking distressed and troubled by high prices of {theme['item']}, open taped cardboard boxes on floor",
                        extra_detail="authentic candid lifestyle documentary, natural stressed expression, room interior visible"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "extra fingers, deformed hands, posing for camera")
                },
                {
                    "scene_idx": 3,
                    "name": "K-Market 0원 나눔 발견",
                    "duration_sec": 4.5,
                    "badge": script_meta["s3_badge"],
                    "main_text": script_meta["s3_main"],
                    "sub_text": script_meta["s3_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=3, char=char,
                        scene_action=f"sitting on floor next to moving boxes, holding modern smartphone securely with both hands, looking down at the glowing screen discovering 0 KRW free {theme['item']} on K-Market app",
                        extra_detail="eyes wide with genuine surprise and joy, looking down at phone screen NOT at camera, authentic candid capture"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "deformed hands, claw hands, floating phone, creepy smile")
                },
                {
                    "scene_idx": 4,
                    "name": "따뜻한 이웃 무료 직거래",
                    "duration_sec": 5.5,
                    "badge": script_meta["s4_badge"],
                    "main_text": script_meta["s4_main"],
                    "sub_text": script_meta["s4_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=4, char=char,
                        scene_action=f"standing in a real Korean residential villa alley street near {theme['target']}, receiving clean {theme['item']} from a friendly neighbor, real outdoor street direct trade moment",
                        extra_detail="candid documentary medium shot, genuine gratitude and warm gentle smile, natural Korean street background"
                    ),
                    "negative_prompt": build_negative_prompt(lang, "bad anatomy, distorted hands, fashion model photoshoot")
                },
                {
                    "scene_idx": 5,
                    "name": "아늑한 방 완성 & 행복한 미소",
                    "duration_sec": 5.0,
                    "badge": script_meta["s5_badge"],
                    "main_text": script_meta["s5_main"],
                    "sub_text": script_meta["s5_sub"],
                    "image_prompt": build_scene_prompt(
                        scene_idx=5, char=char,
                        scene_action=f"arranging and wiping clean the newly received {theme['item']} in the cozy Korean studio apartment room, sitting comfortably on floor with a proud relieved happy smile, realistic furnished student room interior",
                        extra_detail="warm cozy room ambience, authentic candid moment of settled student life, master documentary photography"
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

