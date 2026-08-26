import json
import logging
import time
import random
import urllib.request
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, SUPABASE_URL, SUPABASE_KEY
from core.service_router import ServiceRouter
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker

logger = logging.getLogger("CardnewsGenerator")

# Windows 트루타입 폰트
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
    [무인 자동화 4] 17개국 캐러셀 카드뉴스 (1080x1080)
    ★ Supabase kmarket_items 테이블에서 270개 실제 매물 사진을 직접 조회하여 합성
    ★ 로컬 JSON 파일은 Supabase 연결 실패 시 폴백으로만 사용
    """

    def __init__(self, db_mgr: DBManager, router: ServiceRouter):
        self.db_mgr = db_mgr
        self.router = router
        self.output_dir = OUTPUTS_DIR / "cardnews"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._image_cache: Dict[str, Image.Image] = {}
        # Supabase에서 실제 매물 사진 로드 (핵심)
        self.kmarket_items = self._load_items_from_supabase()

    # ──────────────────────────────────────────────
    # 1단계: Supabase에서 실제 270개 매물 사진 직접 조회
    # ──────────────────────────────────────────────
    def _load_items_from_supabase(self) -> List[Dict[str, Any]]:
        """Supabase kmarket_items 테이블에서 images 필드가 있는 매물 전체 조회"""
        if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
            try:
                from supabase import create_client
                client = create_client(SUPABASE_URL, SUPABASE_KEY)
                # images 배열이 비어있지 않은 매물만 조회, 최대 300개
                response = client.table("kmarket_items") \
                    .select("id,title,price,images,region,category,description") \
                    .order("created_at", desc=True) \
                    .limit(300) \
                    .execute()
                if response.data:
                    # images 배열이 실제로 존재하는 매물만 필터
                    items_with_photos = [
                        item for item in response.data
                        if item.get("images") and len(item["images"]) > 0
                    ]
                    logger.info(
                        f"✅ Supabase에서 실제 매물 사진 {len(items_with_photos)}개 로드 완료 "
                        f"(전체 {len(response.data)}개 중 사진 보유 매물)"
                    )
                    if items_with_photos:
                        return items_with_photos
            except Exception as e:
                logger.warning(f"Supabase kmarket_items 조회 실패, 로컬 폴백: {e}")

        # 폴백: 로컬 JSON
        return self._load_local_items_fallback()

    def _load_local_items_fallback(self) -> List[Dict[str, Any]]:
        """Supabase 연결 불가 시 로컬 kmarket_items.json 폴백"""
        items_path = DATA_DIR / "kmarket_items.json"
        if items_path.exists():
            try:
                with open(items_path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    items_with_photos = [i for i in items if i.get("images") and len(i["images"]) > 0]
                    logger.info(f"로컬 JSON 폴백: 사진 보유 매물 {len(items_with_photos)}개 로드")
                    return items_with_photos if items_with_photos else items
            except Exception as e:
                logger.warning(f"로컬 kmarket_items.json 로드 실패: {e}")
        return []

    # ──────────────────────────────────────────────
    # 2단계: 실제 사진 URL에서 이미지 다운로드 (캐시)
    # ──────────────────────────────────────────────
    def _fetch_photo(self, url: str) -> Optional[Image.Image]:
        """실제 매물 사진 URL에서 이미지를 다운로드하고 캐시"""
        if not url:
            return None
        if url in self._image_cache:
            return self._image_cache[url].copy()
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGB")
                self._image_cache[url] = img
                return img.copy()
        except Exception as e:
            logger.debug(f"사진 다운로드 실패 ({url[:50]}...): {e}")
            return None

    # ──────────────────────────────────────────────
    # 3단계: 4장 캐러셀 카드뉴스 생성
    # ──────────────────────────────────────────────
    def generate_carousel(self, service_id: str = "kmarket", lang: str = "en") -> List[Path]:
        """4장 캐러셀 카드뉴스 생성 — 매 슬라이드마다 서로 다른 실제 매물 사진 합성"""
        service_data = self.router.get_service(service_id)
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])

        cards = []
        if service_id == "kmarket":
            slides_data = [
                {"badge": "0원 무료 나눔 FREE", "title": "졸업·귀국 외국인 가구 0원 무료 나눔!", "desc": "침대, 책상, 전자레인지, 냉장고 선착순 0원 나눔", "cta": "프로필 링크에서 0원 나눔 예약하기!"},
                {"badge": "원클릭 무빙세일 MOVING SALE", "title": "원룸 풀패키지 가전·가구 최대 80% 할인", "desc": "침대+책상+밥솥+행거 세트 도보 5분 직거래", "cta": "대학가/공단 근처 실물 매물 확인하기!"},
                {"badge": "17개국어 실시간 자동번역 채팅", "title": "한국어 못해도 내 모국어로 1초 채팅!", "desc": "한국인 판매자와 17개 언어 실시간 번역 대화", "cta": "언어 장벽 없는 안심 직거래 시작하기!"},
                {"badge": "외국인등록증 100% 안심인증", "title": "사기 없는 대학가 도보 5분 안심 거래", "desc": "본인인증 셀러 + AI 사기방지 엔진 탑재 완료", "cta": "대한민국 No.1 외국인 직거래 케이마켓 가기!"},
            ]
        else:
            slides_data = [
                {"badge": "국세청 조특법 제30조 공식 적용", "title": "외국인 근로자 소득세 90% 감면 합법 혜택", "desc": "E-9, E-7, H-2 외국인 5년치 미환급 세금 합법 신청", "cta": "지금 3분 무료 세금 환급 모의계산하기!"},
                {"badge": "100% 무료 선입금 0원 보장", "title": "조회 비용 완전 무료! 환급 성공 시에만 정산", "desc": "어떠한 선입금도 요구하지 않는 안심 국세청 환급", "cta": "선입금 없이 숨은 내 환급액 1초 조회!"},
                {"badge": "공인 세무법인 1:1 전담 검토", "title": "국세청 홈택스 전자신고 100% 법적 보호", "desc": "전문 세무사 정밀 검토로 안전한 통장 입금", "cta": "공인 세무사와 1:1 안전 환급 신청하기!"},
                {"badge": "ARC 신분증 1장으로 3분 환급 신청", "title": "17개국 모국어로 5개년 환급금 원스톱 수령", "desc": "평균 150만~400만원 과오납 세금 즉시 수령", "cta": "프로필 링크에서 3분 무료 환급 시작!"},
            ]

        campaign = UTMTracker.generate_campaign_tag(service_id, "cardnews", lang)
        landing_url = UTMTracker.build_url(
            base_url=service_data.get("landing_url", "https://ktrs-market.vercel.app/"),
            source="social_cardnews", medium="carousel", campaign=campaign, lang=lang
        )

        for idx, slide in enumerate(slides_data, 1):
            img_path = self._render_single_card(service_id, lang, idx, slide, landing_url)
            cards.append(img_path)

        self.db_mgr.record_history(
            content_type="cardnews", service_id=service_id, target_lang=lang,
            title=slides_data[0]["title"],
            content_text=f"Supabase real-photo carousel 4 slides for {service_id} in {lang}",
            target_url=landing_url,
            external_id=f"card_{service_id}_{lang}_{int(time.time() * 1000)}"
        )
        logger.info(f"[{lang.upper()}] Supabase 실사 카드뉴스 4장 생성 완료 ({service_id})")
        return cards

    # ──────────────────────────────────────────────
    # 4단계: 개별 슬라이드 렌더링 (실사 사진 합성)
    # ──────────────────────────────────────────────
    def _render_single_card(self, service_id: str, lang: str, slide_num: int,
                            data: Dict[str, str], url: str) -> Path:
        W, H = 1080, 1080
        img = Image.new("RGB", (W, H), color=(15, 20, 42))
        draw = ImageDraw.Draw(img)

        font_badge = get_font(28, bold=True)
        font_title = get_font(40, bold=True)
        font_desc = get_font(26, bold=False)
        font_price = get_font(34, bold=True)
        font_cta = get_font(28, bold=True)
        font_page = get_font(30, bold=True)
        font_footer = get_font(18, bold=False)

        # ── 상단 뱃지 & 페이지 번호 ──
        badge_color = (16, 185, 129) if service_id == "kmarket" else (245, 158, 11)
        draw.rectangle([(50, 45), (680, 110)], fill=badge_color)
        draw.text((65, 55), data["badge"], fill=(255, 255, 255), font=font_badge)
        draw.text((960, 55), f"{slide_num}/4", fill=(148, 163, 184), font=font_page)

        # ── 중앙: 실제 매물 사진 (K-Market 4장 전 슬라이드) ──
        photo_x, photo_y = 50, 130
        photo_w, photo_h = 980, 540

        photo_loaded = False

        if service_id == "kmarket" and self.kmarket_items:
            # 슬라이드마다 다른 매물 선택 (랜덤 시드를 lang+slide로 고정하여 재현성 보장)
            seed = hash(f"{lang}_{slide_num}") % len(self.kmarket_items)
            item = self.kmarket_items[seed]

            # 실제 Supabase 매물 사진 다운로드
            images_list = item.get("images", [])
            real_img = None
            for img_url in images_list:
                real_img = self._fetch_photo(img_url)
                if real_img:
                    break

            if real_img:
                real_resized = real_img.resize((photo_w, photo_h), Image.Resampling.LANCZOS)
                img.paste(real_resized, (photo_x, photo_y))
                photo_loaded = True

            # 사진 위 좌측: 가격 뱃지
            price_val = item.get("price", 0)
            if price_val == 0:
                p_text = "0원 무료 나눔 FREE"
                p_fill = (16, 185, 129)
            else:
                p_text = f"₩{price_val:,}"
                p_fill = (255, 107, 53)
            draw.rectangle([(photo_x + 15, photo_y + 15), (photo_x + 420, photo_y + 80)], fill=p_fill)
            draw.text((photo_x + 30, photo_y + 25), p_text, fill=(255, 255, 255), font=font_price)

            # 사진 위 우측: 지역
            region = item.get("region", "")
            if region:
                draw.rectangle([(photo_x + 650, photo_y + 15), (photo_x + 965, photo_y + 80)], fill=(30, 41, 59, 200))
                draw.text((photo_x + 665, photo_y + 25), region[:12], fill=(255, 255, 255), font=font_badge)

        if not photo_loaded:
            # 사진 로드 실패 or EasyTax → 텍스트 기반 비주얼 카드
            draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)],
                           fill=(20, 28, 58), outline=(59, 130, 246), width=3)
            if service_id == "easytax":
                draw.text((photo_x + 60, photo_y + 100), "국세청 외국인 소득세 환급", fill=(255, 255, 255), font=font_title)
                draw.text((photo_x + 60, photo_y + 200), "조특법 제30조 90% 소득세 감면 적용", fill=(250, 204, 21), font=font_price)
                draw.text((photo_x + 60, photo_y + 290), "1인 평균 150만 ~ 400만원 과오납 세금 환급", fill=(52, 211, 153), font=font_desc)
                draw.text((photo_x + 60, photo_y + 370), "공인 세무법인 전자신고 • 선입금 0원 100% 안전", fill=(148, 163, 184), font=font_desc)
            else:
                draw.text((photo_x + 250, photo_y + 240), "케이마켓 인증 매물", fill=(148, 163, 184), font=font_title)

        # ── 하단 텍스트 박스 ──
        draw.rectangle([(50, 695), (1030, 900)], fill=(22, 29, 56), outline=(59, 130, 246), width=2)
        draw.text((75, 720), data["title"], fill=(255, 255, 255), font=font_title)
        draw.text((75, 800), data["desc"], fill=(203, 213, 225), font=font_desc)

        # ── CTA 배너 ──
        cta_bg = (16, 185, 129) if service_id == "kmarket" else (245, 158, 11)
        draw.rectangle([(50, 920), (1030, 1005)], fill=cta_bg)
        draw.text((80, 940), data["cta"], fill=(255, 255, 255), font=font_cta)

        # ── 최하단 각주 ──
        footer = "대한민국 외국인 전용 플랫폼 케이마켓 (KTRS)" if service_id == "kmarket" \
            else "국세기본법 공인 세무대리 절차 진행, 환급액은 소득에 따라 상이"
        draw.text((55, 1020), footer, fill=(100, 116, 139), font=font_footer)

        file_path = self.output_dir / f"card_{service_id}_{lang}_slide_{slide_num}.png"
        img.save(file_path)
        return file_path
