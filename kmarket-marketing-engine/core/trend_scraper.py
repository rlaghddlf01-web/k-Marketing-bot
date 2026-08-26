import json
import logging
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any
from config import DATA_DIR, LANGUAGES

logger = logging.getLogger("TrendScraper")

class ViralTrendScraper:
    """
    📈 17개국 틱톡/인스타그램/쇼츠 실시간 바이럴 해시태그 & 국내 체류 외국인 정밀 타깃팅 엔진
    
    1. 대한민국(KR) 실시간 급상승 트렌드 (Google Trends / TikTok KR)
    2. 17개국 언어별 '한국 체류/생활(In-Korea)' 고유 타깃 키워드
    3. 서비스별(K-Market 0원나눔 / EasyTax 세금환급 등) 전환 키워드
    """
    def __init__(self):
        self.cache_file = DATA_DIR / "trending_hashtags.json"
        self.hashtag_db = self._load_or_init_trends()

    def _load_or_init_trends(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 17개국 모두 포함되어 있는지 확인
                    if len(data.get("countries", {})) >= 17:
                        return data
            except Exception as e:
                logger.warning(f"해시태그 캐시 로드 실패: {e}")
        return self.refresh_daily_trends()

    def fetch_korea_live_trends(self) -> List[str]:
        """
        🇰🇷 대한민국 영토 내(Geo: KR) 실시간 급상승 검색어/트렌드 태그 수집
        - Google Trends KR RSS 피드를 통해 대한민국 실시간 핫 토픽 수집
        - 실패 시 안전한 Fallback 트렌드 제공 (무중단 보장)
        """
        trends = []
        try:
            url = "https://trends.google.com/trending/rss?geo=KR"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_text = response.read().decode("utf-8", errors="ignore")
                root = ET.fromstring(xml_text)
                for item in root.findall("./channel/item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        clean_word = title.text.strip().replace(" ", "").replace("#", "")
                        if clean_word and len(clean_word) < 15:
                            trends.append(f"#{clean_word}")
                    if len(trends) >= 8:
                        break
        except Exception as e:
            logger.info(f"Google Trends KR 실시간 피드 일시 접근 불가(Fallback 가동): {e}")

        # 기본/Fallback 대한민국 실시간 인기 바이럴 태그
        fallback_kr = ["#한국트렌드", "#실시간급상승", "#서울핫플", "#쇼츠인기", "#koreatrend", "#seoulvibes", "#fyp", "#korea"]
        for t in fallback_kr:
            if t not in trends:
                trends.append(t)

        return trends[:10]

    def _build_full_17_countries_matrix(self, live_kr_trends: List[str]) -> Dict[str, Any]:
        """17개국 전체 국내 체류(In-Korea) 정밀 타깃팅 해시태그 매트릭스"""
        matrix = {
            "vi": {
                "name": "Tiếng Việt (베트남)",
                "flag": "🇻🇳",
                "target_group": "전국 30개 대학 유학생(1위), 시화/반월/평택 공단 근로자",
                "in_korea_common": ["#cuocsonghanquoc", "#duhockorea", "#vietnamhanquoc", "#xuatkhaulaodonghq", "#hoctaptaihan", "#nguoiviettaihan", "#fyp"],
                "kmarket": ["#muabandohan", "#chototkorea", "#thanhlidohanquoc", "#tietkiemtienkorea", "#kmarket0won", "#choxanhhanquoc"],
                "easytax": ["#hoanthuekorea", "#thuelaodonghq", "#thuetncnkorea", "#tienhoanthuekorea", "#easytaxhq", "#baohiemkorea"],
                "hot_districts": ["#ansan_vietnam", "#suwon_duhoc", "#seoul_life"]
            },
            "zh": {
                "name": "中文 (중국)",
                "flag": "🇨🇳",
                "target_group": "전국 유학생, 서울 어학당, 대림/안산 체류 교민",
                "in_korea_common": ["#在韩留学生", "#在韩华人", "#韩国生活", "#首尔日常", "#留学生日常", "#在韩打工人", "#fyp"],
                "kmarket": ["#韩国二手闲置", "#韩国免费赠送", "#首尔二手家具", "#在韩出闲置", "#韩国跳蚤市场", "#kmarket二手"],
                "easytax": ["#韩国退税指南", "#在韩年终结算", "#韩国打工退税", "#韩国四大保险", "#韩国所得税退税", "#easytax退税"],
                "hot_districts": ["#大林洞", "#建大中国街", "#首尔大学圈"]
            },
            "en": {
                "name": "English (글로벌 익스팟)",
                "flag": "🇺🇸",
                "target_group": "교환학생, 원어민 강사(EPIK/학원), 주한미군, IT 스타트업 직장인",
                "in_korea_common": ["#expatsinkorea", "#lifeinkorea", "#seoullife", "#livinginkorea", "#studyinkorea", "#foreignerinkorea", "#fyp"],
                "kmarket": ["#seoulsecondhand", "#movingoutkorea", "#freeinkorea", "#koreangiveaway", "#kmarketexpat", "#buyandsellseoul"],
                "easytax": ["#koreataxrefund", "#expatfinanceskorea", "#koreanyearendtax", "#withholdingtaxkorea", "#easytaxkorea", "#seoultax"],
                "hot_districts": ["#itaewon_life", "#hongdae_expats", "#pyeongtaek_usfk"]
            },
            "uz": {
                "name": "O'zbek (우즈베키스탄)",
                "flag": "🇺🇿",
                "target_group": "동대문, 평택, 광주, 청주 등 우즈벡 유학생/근로자 커뮤니티",
                "in_korea_common": ["#koreyadahayot", "#koreyadagiuzbeklar", "#uzbeklar_koreyada", "#koreyatalabalari", "#koreyadaish", "#fyp"],
                "kmarket": ["#arzonkoreya", "#bepulkoreya", "#telefonkoreya", "#mebelkoreya", "#kmarketuz", "#bozorkoreya"],
                "easytax": ["#soliqkoreya", "#koreyasoliqqaytarish", "#mehnatshartnomasi", "#easytaxuz", "#straxovkakoreya"],
                "hot_districts": ["#dongdaemun_uzb", "#pyeongtaek_uz", "#gwangju_uzb"]
            },
            "mn": {
                "name": "Монгол (몽골)",
                "flag": "🇲🇳",
                "target_group": "안산 원곡동, 동대문 몽골타운, 수원 거주 몽골인 커뮤니티",
                "in_korea_common": ["#солонгост_байгаа_монголчууд", "#солонгос_амьдрал", "#солонгос_сургууль", "#солонгос_ажил", "#fyp"],
                "kmarket": ["#солонгос_хямд_бараа", "#солонгос_үнэгүй_өгнө", "#солонгос_тавилга", "#солонгос_утас", "#kmarketmn"],
                "easytax": ["#солонгос_татвар_буцаан_авалт", "#татвар_буцаалт", "#солонгос_даатгал", "#easytaxmn"],
                "hot_districts": ["#dongdaemun_mongol", "#ansan_mongol", "#suwon_life"]
            },
            "ru": {
                "name": "Русский (러시아/고려인)",
                "flag": "🇷🇺",
                "target_group": "안산 땟골마을, 인천 연수구, 김포/화성 고려인 및 러시아어권 체류자",
                "in_korea_common": ["#жизньвкорее", "#кореядлянас", "#работавкорее", "#учебавкорее", "#русскиевинчхоне", "#сеулгид", "#fyp"],
                "kmarket": ["#барахолкакорея", "#бесплатнокорея", "#букорея", "#вещисеул", "#kmarketru", "#отдамдаромсеул"],
                "easytax": ["#налогивкорее", "#возвратналоговкорея", "#пенсионныекорея", "#страховкакорея", "#easytaxru"],
                "hot_districts": ["#ansan_rus", "#incheon_yeonsu", "#dongdaemun_rus"]
            },
            "th": {
                "name": "ไทย (태국)",
                "flag": "🇹🇭",
                "target_group": "경기 화성/포천, 경남 김해 등 전국 산업단지 근로자 및 유학생",
                "in_korea_common": ["#คนไทยในเกาหลี", "#ชีวิตในเกาหลี", "#เรียนต่อเกาหลี", "#ทำงานเกาหลี", "#สะใภ้เกาหลี", "#fyp"],
                "kmarket": ["#ของมือสองเกาหลี", "#ของฟรีเกาหลี", "#แจกฟรีเกาหลี", "#ซื้อขายเกาหลี", "#kmarketth"],
                "easytax": ["#ขอคืนภาษีเกาหลี", "#ภาษีเกาหลี", "#เงินคืนภาษีเกาหลี", "#ประกันเกาหลี", "#easytaxth"],
                "hot_districts": ["#hwaseong_thai", "#ansan_thai", "#gimhae_thai"]
            },
            "id": {
                "name": "Bahasa Indonesia (인도네시아)",
                "flag": "🇮🇩",
                "target_group": "안산, 부산, 시흥, 거제 해양/제조업 근로자 및 대학 유학생",
                "in_korea_common": ["#tki_korea", "#pejuangkorea", "#hidupdikorea", "#kuliahdikorea", "#wargaindonesiadikorea", "#fyp"],
                "kmarket": ["#barangbekaskorea", "#gratisankorea", "#pasarbekaskorea", "#belanjakorea", "#kmarketid"],
                "easytax": ["#taxrefundkorea", "#pajakkorea", "#pengembalianpajakkorea", "#asuransikorea", "#easytaxid"],
                "hot_districts": ["#ansan_indonesia", "#busan_indonesia", "#siheung_life"]
            },
            "km": {
                "name": "ភាសាខ្មែរ (캄보디아)",
                "flag": "🇰🇭",
                "target_group": "경기 안성/평택, 충남 천안/논산 제조업 및 농축산업 근로자",
                "in_korea_common": ["#ពលករខ្មែរនៅកូរ៉េ", "#ជីវិតនៅកូរ៉េ", "#ការងារនៅកូរ៉េ", "#ខ្មែរនៅកូរ៉េ", "#fyp"],
                "kmarket": ["#ទំនិញជជុះកូរ៉េ", "#របស់ហ្វ្រីកូរ៉េ", "#ផ្សារខ្មែរកូរ៉េ", "#kmarketkh"],
                "easytax": ["#ពន្ធកូរ៉េ", "#ដកលុយពន្ធកូរ៉េ", "#ធានារ៉ាប់រងកូរ៉េ", "#easytaxkh"],
                "hot_districts": ["#cheonan_khmer", "#pyeongtaek_khmer", "#anseong_khmer"]
            },
            "ne": {
                "name": "नेपाली (네팔)",
                "flag": "🇳🇵",
                "target_group": "동대문, 대구, 포천 등 유학생 및 EPS 근로자 커뮤니티",
                "in_korea_common": ["#koreamanepali", "#nepaliinkorea", "#koreajindagii", "#nepalikoreaeps", "#fyp"],
                "kmarket": ["#koreansaman", "#freenepalikorea", "#kmarketnepal", "#secondhandkorea"],
                "easytax": ["#koreataxreturn", "#nepalieasytax", "#koreabima", "#taxnepalikorea"],
                "hot_districts": ["#dongdaemun_nepal", "#daegu_nepali", "#pocheon_eps"]
            },
            "my": {
                "name": "မြန်မာ (미얀마)",
                "flag": "🇲🇲",
                "target_group": "부평, 김포, 안산 어학당 및 산업단지 근로자",
                "in_korea_common": ["#ကိုရီးယားရောက်မြန်မာများ", "#ကိုရီးယားအလုပ်", "#ကိုရီးယားကျောင်းသား", "#fyp"],
                "kmarket": ["#ကိုရီးယားအသုံးအဆောင်", "#အခမဲ့ပစ္စည်း", "#kmarketmyanmar"],
                "easytax": ["#ကိုရီးယားအခွန်ပြန်အမ်း", "#ကိုရီးယားအာမခံ", "#easytaxmm"],
                "hot_districts": ["#bupyeong_myanmar", "#gimpo_myanmar", "#ansan_myanmar"]
            },
            "ja": {
                "name": "日本語 (일본)",
                "flag": "🇯🇵",
                "target_group": "신촌/홍대 어학당, 교환학생, 동부이촌동 체류 일본인",
                "in_korea_common": ["#韓国留学", "#韓国生活", "#在韓日本人", "#ソウル暮らし", "#韓国ワーホリ", "#韓国日常", "#fyp"],
                "kmarket": ["#韓国フリマ", "#韓国不用品譲渡", "#ソウル家具譲り", "#韓国無料譲渡", "#kmarketjp"],
                "easytax": ["#韓国年末調整", "#韓国還付金", "#在韓税金手続き", "#韓国所得税還付", "#easytaxjp"],
                "hot_districts": ["#sinchon_japan", "#ichon_seoul", "#hongdae_japan"]
            },
            "tl": {
                "name": "Filipino / Tagalog (필리핀)",
                "flag": "🇵🇭",
                "target_group": "혜화동 필리핀 마켓, 원어민 강사, 전국 대학 유학생/근로자",
                "in_korea_common": ["#pinoysakorea", "#ofwkorea", "#buhaykorea", "#filipinoinkorea", "#seoulpinoy", "#fyp"],
                "kmarket": ["#gamitsakorea", "#freeitemsseoul", "#kmarketpinoy", "#secondhandkorea"],
                "easytax": ["#koreataxrefundpinoy", "#easytaxph", "#withholdingtaxkorea", "#insuranceseoul"],
                "hot_districts": ["#hyehwa_pinoy", "#itaewon_filipino", "#pyeongtaek_pinoy"]
            },
            "bn": {
                "name": "বাংলা (방글라데시)",
                "flag": "🇧🇩",
                "target_group": "이태원, 안산, KAIST/POSTECH 등 유학생/연구원/근로자",
                "in_korea_common": ["#bangladeshiinkorea", "#korearprokash", "#korealifebd", "#studyinkoreabd", "#fyp"],
                "kmarket": ["#koreasecondhandbd", "#freeinkoreabd", "#kmarketbd"],
                "easytax": ["#taxrefundkoreabd", "#easytaxbd", "#koreataxreturn"],
                "hot_districts": ["#itaewon_bd", "#ansan_bd", "#daejeon_research"]
            },
            "ar": {
                "name": "العربية (아랍/중동)",
                "flag": "🇸🇦",
                "target_group": "이태원 모스크 인근, 서울 주요 대학 의학/공학 유학생",
                "in_korea_common": ["#العرب_في_كوريا", "#الدراسة_في_كوريا", "#الحياة_في_كوريا", "#كوريا_الجنوبية", "#fyp"],
                "kmarket": ["#مستعمل_كوريا", "#مجاني_كوريا", "#سوق_كوريا", "#kmarketar"],
                "easytax": ["#استرداد_الضرائب_كوريا", "#ضرائب_كوريا", "#easytaxar"],
                "hot_districts": ["#itaewon_arab", "#seoul_arab_students", "#gangnam_medical"]
            },
            "es": {
                "name": "Español (스페인/남미)",
                "flag": "🇪🇸",
                "target_group": "고려대/연세대/서울대 교환학생, 중남미 유학생 커뮤니티",
                "in_korea_common": ["#latinosenkorea", "#estudiarencorea", "#vidaencorea", "#espanolesencorea", "#seoulvida", "#fyp"],
                "kmarket": ["#segundamanocorea", "#gratiscorea", "#mueblesseoul", "#kmarketes"],
                "easytax": ["#devolucionimpuestoscorea", "#impuestoscorea", "#easytaxes"],
                "hot_districts": ["#hongdae_latinos", "#sinchon_expats", "#korea_univ_exchange"]
            },
            "ko": {
                "name": "한국어 (국내)",
                "flag": "🇰🇷",
                "target_group": "외국인 커뮤니티 관리자, 다문화 가족, 글로벌 룸메이트 구하는 내국인",
                "in_korea_common": ["#외국인유학생", "#한국생활꿀팁", "#외국인근로자", "#다문화가족", "#쇼츠추천", "#한국트렌드", "#fyp"],
                "kmarket": ["#외국인중고거래", "#무료나눔", "#0원나눔", "#자취방정리", "#케이마켓", "#이사정리나눔"],
                "easytax": ["#외국인연말정산", "#소득세환급", "#퇴직금환급", "#출국만기보험", "#이지택스", "#세금환급"],
                "hot_districts": ["#안산원곡동", "#이태원", "#홍대신촌"]
            }
        }
        return matrix

    def get_viral_hashtags(self, service_id: str = "kmarket", lang: str = "en", count: int = 8) -> List[str]:
        """
        3단 하이브리드 황금 조합 반환:
        [1] 🇰🇷 대한민국 실시간 급상승 트렌드 (2개) -> 알고리즘 1차 노출 폭발
        [2] 🎯 해당 언어 '국내 체류 외국인' 타깃 태그 (3개) -> 국내 거주자 정밀 도달
        [3] 💎 서비스 전용 전환 태그 (3개) -> 환급/0원나눔 클릭 전환
        """
        kr_trends = self.hashtag_db.get("korea_live_trends", ["#koreatrend", "#fyp"])
        countries = self.hashtag_db.get("countries", {})
        lang_data = countries.get(lang, countries.get("en", {}))

        live_tags = kr_trends[:2]
        in_korea_tags = lang_data.get("in_korea_common", ["#lifeinkorea", "#expatsinkorea"])[:3]
        service_tags = lang_data.get(service_id, ["#kmarket", "#koreatips"])[:3]

        combined = live_tags + in_korea_tags + service_tags
        unique_tags = list(dict.fromkeys(combined))
        return unique_tags[:count]

    def format_hashtag_string(self, service_id: str = "kmarket", lang: str = "en", count: int = 8) -> str:
        """SNS 본문/설명란에 바로 붙일 수 있는 문자열 형식 반환"""
        tags = self.get_viral_hashtags(service_id, lang, count)
        return " ".join(tags)

    def refresh_daily_trends(self) -> Dict[str, Any]:
        """매일 아침 대한민국 실시간 트렌드 및 17개국 매트릭스 갱신 및 캐시 저장"""
        live_kr_trends = self.fetch_korea_live_trends()
        countries_matrix = self._build_full_17_countries_matrix(live_kr_trends)
        
        full_db = {
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "geo_scope": "대한민국(KR) 영토 내 거주 외국인 한정",
            "korea_live_trends": live_kr_trends,
            "countries_count": len(countries_matrix),
            "countries": countries_matrix
        }

        self.hashtag_db = full_db
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(full_db, f, ensure_ascii=False, indent=2)
        logger.info(f"17개국 전체 국내 체류 바이럴 해시태그 매트릭스 갱신 완료 ({len(countries_matrix)}개국)")
        return self.hashtag_db
