import json
import logging
import time
import urllib.request
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES
from core.service_router import ServiceRouter
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker

logger = logging.getLogger("CardnewsGenerator")

class CardnewsGenerator:
    """
    [무인 자동화 4] 17개국 캐러셀 카드뉴스 (1080x1080) 무인 렌더러
    (K-Market 실제 270개 매물 실물 사진 & EasyTax 5개년 환급 팩트 직접 합성)
    """
    def __init__(self, db_mgr: DBManager, router: ServiceRouter):
        self.db_mgr = db_mgr
        self.router = router
        self.output_dir = OUTPUTS_DIR / "cardnews"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kmarket_items = self._load_kmarket_items()

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
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                return Image.open(io.BytesIO(data)).convert("RGB")
        except Exception:
            return None

    def generate_carousel(self, service_id: str = "kmarket", lang: str = "en") -> List[Path]:
        """4장 구성의 정사각 캐러셀 카드뉴스 생성 (실물 매물 사진 연동)"""
        service_data = self.router.get_service(service_id)
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        
        cards = []
        if service_id == "kmarket":
            slides_data = [
                {"badge": "🎁 $0 FREE GIVEAWAY", "title": "Free Furniture & Appliances in Korea!", "desc": "Graduating expats giving away desks, microwaves & fridges for ₩0.", "type": "real_photo"},
                {"badge": "📦 1-CLICK MOVING SALE", "title": "Moving Out Sale Packages", "desc": "Full room packages (Bed + Desk + Rice Cooker) at 80% discount.", "type": "real_photo"},
                {"badge": "🗣️ 17 LANGUAGES CHAT", "title": "Real-Time Auto-Translation Chat", "desc": "Speak in your native language with Korean sellers. Zero language barrier!", "type": "info"},
                {"badge": "🛡️ 100% VERIFIED", "title": "Safe Neighborhood Meetups", "desc": "Alien Registration Card verified sellers + AI Anti-Scam protection. Link in bio!", "type": "cta"}
            ]
        else:
            slides_data = [
                {"badge": "🏛️ NTS OFFICIAL TAX LAW", "title": "Korean Expat Tax Relief: Article 30", "desc": "E-9/H-2 SME workers and expats: Legal 90% income tax reduction under Korean tax law.", "type": "info"},
                {"badge": "🛡️ 100% FREE • NO UPFRONT FEE", "title": "Zero Pre-payments & 100% Safe", "desc": "100% Free AI refund calculation. No hidden costs or upfront money requests.", "type": "info"},
                {"badge": "⚖️ LICENSED TAX PARTNER", "title": "Handled via Certified Tax Agents", "desc": "National Tax Service (Hometax) electronic filing with full legal protection.", "type": "info"},
                {"badge": "⚡ 3-MIN AI FREE CHECK", "title": "Check Your 5-Year Overpaid Tax", "desc": "1 photo of ARC. Free simulation in 17 languages. Link in bio!", "type": "cta"}
            ]

        campaign = UTMTracker.generate_campaign_tag(service_id, "cardnews", lang)
        landing_url = UTMTracker.build_url(
            base_url=service_data.get("landing_url", "https://k-market.app"),
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
            content_text=f"Carousel 4 slides with real photos for {service_id} in {lang}",
            target_url=landing_url,
            external_id=f"card_{service_id}_{lang}_{int(time.time() * 1000)}"
        )
        logger.info(f"[{lang.upper()}] 실물 사진 결합 카드뉴스 4장 세트 생성 완료 ({service_id})")
        return cards

    def _render_single_card(self, service_id: str, lang: str, slide_num: int, 
                            data: Dict[str, str], url: str) -> Path:
        width, height = 1080, 1080
        img = Image.new("RGB", (width, height), color=(10, 15, 30))
        draw = ImageDraw.Draw(img)

        # 1. 상단 뱃지 & 슬라이드 넘버
        draw.rectangle([(60, 60), (520, 140)], fill=(37, 99, 235))
        draw.text((80, 85), data["badge"], fill=(255, 255, 255))
        draw.text((960, 75), f"{slide_num}/4", fill=(148, 163, 184))

        # 2. 케이마켓 실물 사진 슬라이드 렌더링
        if service_id == "kmarket" and data.get("type") == "real_photo" and self.kmarket_items:
            item_idx = (slide_num - 1) % len(self.kmarket_items)
            item = self.kmarket_items[item_idx]
            
            # 실물 사진 로드 (중앙 배치: 500x500)
            img_url = item["images"][0] if item.get("images") else ""
            real_img = self._fetch_or_cache_image(img_url) if img_url else None
            
            photo_x, photo_y = 60, 170
            photo_w, photo_h = 960, 520
            
            if real_img:
                real_resized = real_img.resize((photo_w, photo_h))
                img.paste(real_resized, (photo_x, photo_y))
            else:
                draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill=(30, 41, 59))
                draw.text((photo_x + 350, photo_y + 240), "📷 Real Verified Item", fill=(255, 255, 255))

            # 사진 위 실물 가격표 & 0원 나눔 뱃지
            price_val = item.get("price", 0)
            p_text = "🎁 0원 무료 나눔 (FREE)" if price_val == 0 else f"🏷️ ₩{price_val:,}"
            draw.rectangle([(photo_x + 20, photo_y + 20), (photo_x + 400, photo_y + 90)], fill=(16, 185, 129))
            draw.text((photo_x + 35, photo_y + 40), p_text, fill=(255, 255, 255))

            # 하단 텍스트 정보 카드
            draw.rectangle([(60, 720), (1020, 920)], fill=(20, 30, 50), outline=(59, 130, 246), width=2)
            draw.text((90, 750), data["title"], fill=(255, 255, 255))
            draw.text((90, 820), f"📍 {item.get('region', '안산/시흥/수원')} • {data['desc'][:50]}", fill=(148, 163, 184))
        else:
            # 텍스트 강조 카드 슬라이드
            draw.rectangle([(60, 180), (1020, 900)], fill=(20, 30, 50), outline=(59, 130, 246), width=3)
            draw.text((100, 260), data["title"], fill=(255, 255, 255))
            draw.text((100, 400), data["desc"], fill=(203, 213, 225))

            # 추가 팩트 포인트
            draw.rectangle([(100, 550), (980, 720)], fill=(15, 23, 42), outline=(16, 185, 129), width=1)
            draw.text((130, 590), "✅ 100% Free & Legal Expat Service in Korea", fill=(52, 211, 153))
            draw.text((130, 650), "✅ 17 Languages Live Support • Direct Link in Bio", fill=(148, 163, 184))

        # 3. 최하단 CTA 배너 & 법적 면책 조항
        cta_text = "👉 프로필 링크 클릭 시 실물 매물 / 0원 나눔 바로 확인!" if service_id == "kmarket" else "👉 프로필 링크에서 3분 무료 세금 모의계산 확인!"
        draw.rectangle([(60, 940), (1020, 1010)], fill=(16, 185, 129))
        draw.text((100, 965), cta_text, fill=(255, 255, 255))
        
        draw.text((80, 1025), "* 국세기본법 공인 세무대리 절차로 진행되며 환급액은 개인 소득에 따라 상이할 수 있습니다.", fill=(100, 116, 139))

        file_path = self.output_dir / f"card_{service_id}_{lang}_slide_{slide_num}.png"
        img.save(file_path)
        return file_path
