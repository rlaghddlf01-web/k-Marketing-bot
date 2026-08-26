import json
import logging
import time
import urllib.request
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES
from core.service_router import ServiceRouter
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker

logger = logging.getLogger("CardnewsGenerator")

# Windows 공통 트루타입 폰트
FONT_BOLD_PATH = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REGULAR_PATH = r"C:\Windows\Fonts\malgun.ttf"

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

class CardnewsGenerator:
    """
    [무인 자동화 4] 17개국 캐러셀 카드뉴스 (1080x1080) 고화질 실사 합성 렌더러
    - 4장 전 슬라이드 케이마켓 270개 매물 실사 사진 100% 꽉 채움
    - 대형 고선명 폰트(50px 볼드) 및 럭셔리 가격 뱃지
    """
    def __init__(self, db_mgr: DBManager, router: ServiceRouter):
        self.db_mgr = db_mgr
        self.router = router
        self.output_dir = OUTPUTS_DIR / "cardnews"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kmarket_items = self._load_kmarket_items()
        self._image_cache: Dict[str, Image.Image] = {}

    def _load_kmarket_items(self) -> List[Dict[str, Any]]:
        items_path = DATA_DIR / "kmarket_items.json"
        if items_path.exists():
            try:
                with open(items_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"K-Market 매물 데이터 로드 실패: {e}")
        return []

    def _fetch_or_cache_image(self, url: str) -> Optional[Image.Image]:
        if not url:
            return None
        if url in self._image_cache:
            return self._image_cache[url].copy()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGB")
                self._image_cache[url] = img
                return img.copy()
        except Exception as e:
            logger.debug(f"이미지 다운로드 스킵 ({url[:40]}...): {e}")
            return None

    def generate_carousel(self, service_id: str = "kmarket", lang: str = "en") -> List[Path]:
        """4장 전 슬라이드 실물 사진 결합 고해상도 카드뉴스 생성"""
        service_data = self.router.get_service(service_id)
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        
        cards = []
        if service_id == "kmarket":
            slides_data = [
                {
                    "badge": "🎁 0원 무료 나눔 (FREE GIVEAWAY)",
                    "title": "졸업·귀국 외국인 가구/가전 0원 무료 나눔!",
                    "desc": "침대, 책상, 전자레인지, 냉장고 선착순 0원 나눔 진행 중",
                    "cta": "👉 지금 프로필 링크에서 0원 나눔 예약하기!"
                },
                {
                    "badge": "📦 1초 원클릭 무빙세일 (MOVING SALE)",
                    "title": "원룸 풀패키지 가전·가구 최대 80% 할인",
                    "desc": "침대+책상+밥솥+행거 세트 통째로 득템! 도보 5분 직거래",
                    "cta": "👉 대학가/공단 근처 실물 매물 확인하기!"
                },
                {
                    "badge": "🗣️ 17개국어 실시간 자동번역 채팅",
                    "title": "한국어 못해도 내 모국어로 1초 채팅!",
                    "desc": "한국인 판매자와 17개 언어 실시간 번역으로 안전한 대화",
                    "cta": "👉 언어 장벽 없는 안심 직거래 시작하기!"
                },
                {
                    "badge": "🛡️ 외국인등록증(ARC) 100% 안심인증",
                    "title": "사기 없는 대학가·공단 도보 5분 안심 거래",
                    "desc": "본인 인증 셀러 + AI 사기 방지 엔진 탑재 완료",
                    "cta": "👉 대한민국 No.1 외국인 직거래 케이마켓 가기!"
                }
            ]
        else:
            slides_data = [
                {
                    "badge": "🏛️ 국세청 조특법 제30조 공식 적용",
                    "title": "외국인 근로자 소득세 90% 감면 합법 혜택",
                    "desc": "E-9, E-7, H-2 외국인 5년 치 미환급 세금 합법 신청",
                    "cta": "👉 지금 3분 무료 세금 환급 모의계산하기!"
                },
                {
                    "badge": "🛡️ 100% 무료 • 선입금 0원 보장",
                    "title": "조회 비용 완전 무료! 환급 성공 시에만 정산",
                    "desc": "어떠한 선입금도 요구하지 않는 안심 국세청 환급 연계",
                    "cta": "👉 선입금 없이 숨은 내 환급액 1초 조회!"
                },
                {
                    "badge": "⚖️ 공인 세무법인 1:1 전담 검토",
                    "title": "국세청 홈택스 전자신고 100% 법적 보호",
                    "desc": "전문 세무사의 정밀 검토로 안전하고 신속한 통장 입금",
                    "cta": "👉 공인 세무사와 1:1 안전 환급 신청하기!"
                },
                {
                    "badge": "⚡ ARC 신분증 1장으로 3분 환급 신청",
                    "title": "17개국 모국어로 5개년 환급금 원스톱 수령",
                    "desc": "평균 150만~400만원 과오납 세금 통장으로 즉시 수령",
                    "cta": "👉 프로필 링크에서 3분 무료 환급 시작!"
                }
            ]

        campaign = UTMTracker.generate_campaign_tag(service_id, "cardnews", lang)
        landing_url = UTMTracker.build_url(
            base_url=service_data.get("landing_url", "https://ktrs-market.vercel.app/"),
            source="social_cardnews",
            medium="carousel",
            campaign=campaign,
            lang=lang
        )

        for idx, slide in enumerate(slides_data, 1):
            img_path = self._render_single_card(service_id, lang, idx, slide, landing_url)
            cards.append(img_path)

        self.db_mgr.record_history(
            content_type="cardnews",
            service_id=service_id,
            target_lang=lang,
            title=slides_data[0]["title"],
            content_text=f"High-res 4 slides with real photos for {service_id} in {lang}",
            target_url=landing_url,
            external_id=f"card_{service_id}_{lang}_{int(time.time() * 1000)}"
        )
        logger.info(f"[{lang.upper()}] 고화질 실사 카드뉴스 4장 세트 생성 완료 ({service_id})")
        return cards

    def _render_single_card(self, service_id: str, lang: str, slide_num: int, 
                            data: Dict[str, str], url: str) -> Path:
        width, height = 1080, 1080
        img = Image.new("RGB", (width, height), color=(15, 20, 42))
        draw = ImageDraw.Draw(img)

        font_badge = get_font(30, bold=True)
        font_title = get_font(44, bold=True)
        font_desc = get_font(28, bold=False)
        font_price = get_font(38, bold=True)
        font_cta = get_font(32, bold=True)
        font_page = get_font(32, bold=True)

        # 1. 상단 헤더 뱃지 & 페이지 번호 (1/4, 2/4 등)
        header_color = (16, 185, 129) if service_id == "kmarket" else (245, 158, 11)
        draw.rectangle([(50, 45), (600, 115)], fill=header_color)
        draw.text((70, 60), data["badge"], fill=(255, 255, 255), font=font_badge)
        draw.text((960, 60), f"{slide_num}/4", fill=(148, 163, 184), font=font_page)

        # 2. 케이마켓 4장 모든 슬라이드에 실제 매물 사진 큼직하게 렌더링
        photo_x, photo_y = 50, 135
        photo_w, photo_h = 980, 560

        if service_id == "kmarket" and self.kmarket_items:
            # 슬라이드 번호에 맞춰 서로 다른 실물 매물 사진 추출
            item_idx = (slide_num * 7 + 3) % len(self.kmarket_items)
            item = self.kmarket_items[item_idx]
            
            img_url = item["images"][0] if (item.get("images") and len(item["images"]) > 0) else ""
            real_img = self._fetch_or_cache_image(img_url) if img_url else None

            if real_img:
                real_resized = real_img.resize((photo_w, photo_h), Image.Resampling.LANCZOS)
                img.paste(real_resized, (photo_x, photo_y))
            else:
                # 사진이 없을 경우 그라데이션 박스
                draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill=(30, 41, 69))
                draw.text((photo_x + 320, photo_y + 250), "📷 케이마켓 인증 실물 매물", fill=(255, 255, 255), font=font_title)

            # 실사 사진 위 좌측 상단: 대형 가격표 / 0원 나눔 뱃지
            price_val = item.get("price", 0)
            if price_val == 0 or slide_num == 1:
                p_text = "🎁 0원 무료 나눔 (FREE)"
                p_fill = (16, 185, 129)
            else:
                p_text = f"🏷️ ₩{price_val:,}"
                p_fill = (255, 107, 53)

            draw.rectangle([(photo_x + 20, photo_y + 20), (photo_x + 480, photo_y + 95)], fill=p_fill)
            draw.text((photo_x + 35, photo_y + 35), p_text, fill=(255, 255, 255), font=font_price)

            # 실사 사진 위 우측 상단: 지역 뱃지
            region_text = f"📍 {item.get('region', '안산/평택/신촌')}"
            draw.rectangle([(photo_x + 680, photo_y + 20), (photo_x + 960, photo_y + 95)], fill=(30, 41, 59))
            draw.text((photo_x + 700, photo_y + 35), region_text, fill=(255, 255, 255), font=font_badge)

        else:
            # EasyTax 세무 전용 비주얼 카드
            draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill=(20, 28, 58))
            draw.rectangle([(photo_x + 40, photo_y + 40), (photo_x + photo_w - 40, photo_y + photo_h - 40)], outline=(245, 158, 11), width=4)
            
            draw.text((photo_x + 80, photo_y + 120), "💰 대한민국 국세청 외국인 소득세 환급", fill=(255, 255, 255), font=font_title)
            draw.text((photo_x + 80, photo_y + 220), "📌 조특법 제30조 90% 소득세 감면 적용", fill=(250, 204, 21), font=font_price)
            draw.text((photo_x + 80, photo_y + 320), "📌 1인 평균 150만 ~ 400만원 과오납 세금 환급", fill=(52, 211, 153), font=font_desc)
            draw.text((photo_x + 80, photo_y + 400), "📌 공인 세무법인 전자신고 • 선입금 0원 100% 안전", fill=(148, 163, 184), font=font_desc)

        # 3. 하단 텍스트 정보 박스 (720px ~ 920px)
        draw.rectangle([(50, 715), (1030, 915)], fill=(22, 29, 56), outline=(59, 130, 246), width=2)
        draw.text((80, 745), data["title"], fill=(255, 255, 255), font=font_title)
        draw.text((80, 825), data["desc"], fill=(203, 213, 225), font=font_desc)

        # 4. 최하단 CTA 배너 (935px ~ 1025px)
        cta_bg = (16, 185, 129) if service_id == "kmarket" else (245, 158, 11)
        draw.rectangle([(50, 935), (1030, 1025)], fill=cta_bg)
        draw.text((90, 955), data["cta"], fill=(255, 255, 255), font=font_cta)

        # 5. 최하단 안내 각주
        footer_note = "* 대한민국 외국인 전용 플랫폼 케이마켓 (KTRS 연계)" if service_id == "kmarket" else "* 국세기본법 공인 세무대리 절차로 진행되며 환급액은 소득에 따라 상이할 수 있습니다."
        draw.text((60, 1040), footer_note, fill=(100, 116, 139), font=get_font(20, bold=False))

        file_path = self.output_dir / f"card_{service_id}_{lang}_slide_{slide_num}.png"
        img.save(file_path)
        return file_path
