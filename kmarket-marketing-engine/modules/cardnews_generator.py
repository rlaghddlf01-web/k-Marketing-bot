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
from core.gemini_media_generator import GeminiMediaGenerator
from core.media_quality_verifier import MediaQualityVerifier
from core.scenario_director import ScenarioDirector

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
    ★ K-Market: Supabase 270개 실제 매물 사진 직접 합성
    ★ EasyTax: Gemini Imagen 3 직접 실사 사진 생성 + 사전 품질 검증
    """

    def __init__(self, db_mgr: DBManager, router: ServiceRouter):
        self.db_mgr = db_mgr
        self.router = router
        self.output_dir = OUTPUTS_DIR / "cardnews"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._image_cache: Dict[str, Image.Image] = {}
        # Supabase에서 실제 매물 사진 로드 (핵심)
        self.kmarket_items = self._load_items_from_supabase()
        self.gemini_media_gen = GeminiMediaGenerator()
        self.quality_verifier = MediaQualityVerifier()
        self.scenario_director = ScenarioDirector()

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
            # 100% 현지어 지원 카드뉴스 슬라이드 데이터
            from core.motion_video_composer import SCENE_I18N
            i18n = SCENE_I18N.get(lang, SCENE_I18N["en"])
            slides_data = [
                {"badge": i18n["header_tag"], "title": i18n["scene1_hook_main"], "desc": i18n["scene1_hook_sub"], "cta": i18n["scene4_cta_btn"]},
                {"badge": i18n["push_bank"], "title": i18n["push_title"], "desc": i18n["scene2_caption_1"], "cta": i18n["scene4_cta_btn"]},
                {"badge": i18n["scene3_trust_badge"], "title": i18n["scene3_trust_main"], "desc": i18n["scene3_trust_sub"], "cta": i18n["scene4_cta_btn"]},
                {"badge": "EasyTax", "title": i18n["scene4_cta_sub"], "desc": i18n["disclaimer"], "cta": i18n["scene4_cta_btn"]},
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

            # ── EasyTax: Gemini 2.5 Flash Image 실사 사진 직접 생성 및 풀스크린 합성 ──
            scenario = self.scenario_director.plan_daily_scenario(lang=lang, service_id="easytax")
            gen_img_path = self.gemini_media_gen.generate_theme_image(
                lang=lang,
                theme_id=scenario["theme_id"],
                scenario_plan=scenario,
                aspect_ratio="1:1"
            )
            if gen_img_path and gen_img_path.exists():
                try:
                    easytax_img = Image.open(gen_img_path).convert("RGB")
                    # 카드 전체에 풀스크린 실사 사진 배치
                    easytax_resized = easytax_img.resize((W, H), Image.Resampling.LANCZOS)
                    img.paste(easytax_resized, (0, 0))
                    
                    # 어두운 그라디언트 오버레이 (자막 가독성 확보)
                    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    d_over = ImageDraw.Draw(overlay)
                    # 상단/하단 다크 비네팅
                    d_over.rectangle([(0, 0), (W, 160)], fill=(0, 0, 0, 180))
                    d_over.rectangle([(0, 680), (W, H)], fill=(0, 0, 0, 220))
                    img.paste(Image.alpha_composite(Image.new("RGBA", (W, H), (0,0,0,0)), overlay), (0, 0), overlay)
                    
                    # 사진 위 환급액 하이라이트 골드 뱃지 오버레이
                    draw.rectangle([(50, 180), (580, 260)], fill=(245, 158, 11))
                    draw.text((70, 195), f"💰 ₩{scenario['refund_amount_krw']:,} KRW", fill=(15, 23, 42), font=font_price)
                    photo_loaded = True
                except Exception as e:
                    logger.warning(f"EasyTax 카드뉴스 실사 합성 에러: {e}")

        if not photo_loaded:
            # 사진 로드 실패 시 폴백 그라디언트 카드
            draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)],
                           fill=(20, 28, 58), outline=(59, 130, 246), width=3)
            if service_id == "easytax":
                draw.text((photo_x + 60, photo_y + 100), "국세청 외국인 소득세 환급", fill=(255, 255, 255), font=font_title)
                draw.text((photo_x + 60, photo_y + 200), "조특법 제30조 90% 소득세 감면 적용", fill=(250, 204, 21), font=font_price)
                draw.text((photo_x + 60, photo_y + 290), "1인 평균 150만 ~ 400만원 과오납 세금 환급", fill=(52, 211, 153), font=font_desc)
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
