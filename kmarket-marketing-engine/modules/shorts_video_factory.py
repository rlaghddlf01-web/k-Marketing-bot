import json
import logging
import time
import urllib.request
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, BASE_DIR, SUPABASE_URL, SUPABASE_KEY
from core.service_router import ServiceRouter
from core.gemini_engine import GeminiEngine
from core.tts_engine import TTSEngine
from core.db_manager import DBManager
from core.utm_tracker import UTMTracker
from core.trend_scraper import ViralTrendScraper
from core.video_composer import VideoComposer
from core.visual_safety_engine import VisualSafetyEngine

logger = logging.getLogger("ShortsFactory")

class ShortsVideoFactory:
    """
    [무인 자동화 2] 17개국 숏폼 무인 제작 공장
    (실제 K-Market 270개 실물 매물 사진/EasyTax 팩트 연동 -> 네이티브 TTS -> 9:16 비주얼 합성)
    """
    def __init__(self, db_mgr: DBManager, router: ServiceRouter, gemini: GeminiEngine, tts: TTSEngine):
        self.db_mgr = db_mgr
        self.router = router
        self.gemini = gemini
        self.tts = tts
        self.output_dir = OUTPUTS_DIR / "shorts"
        self.cache_img_dir = DATA_DIR / "image_cache"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_img_dir.mkdir(parents=True, exist_ok=True)
        self.kmarket_items = self._load_items_from_supabase()
        self.video_composer = VideoComposer()
        self.safety_engine = VisualSafetyEngine()

    def _load_items_from_supabase(self) -> List[Dict[str, Any]]:
        """Supabase kmarket_items 테이블에서 실제 270개 매물 사진 직접 조회"""
        if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
            try:
                from supabase import create_client
                client = create_client(SUPABASE_URL, SUPABASE_KEY)
                response = client.table("kmarket_items") \
                    .select("id,title,price,images,region,category") \
                    .order("created_at", desc=True) \
                    .limit(300) \
                    .execute()
                if response.data:
                    items_with_photos = [
                        item for item in response.data
                        if item.get("images") and len(item["images"]) > 0
                    ]
                    logger.info("Supabase에서 매물 사진 {}개 로드 완료".format(len(items_with_photos)))
                    if items_with_photos:
                        return items_with_photos
            except Exception as e:
                logger.warning("Supabase 조회 실패, 로컬 폴백: {}".format(e))

        # 폴백: 로컬 JSON
        items_path = DATA_DIR / "kmarket_items.json"
        if items_path.exists():
            try:
                with open(items_path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    return [i for i in items if i.get("images") and len(i["images"]) > 0] or items
            except Exception as e:
                logger.warning("로컬 kmarket_items.json 로드 실패: {}".format(e))
        return []

    def produce_shorts(self, service_id: str = "kmarket", target_langs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """지정된 언어별 숏폼 패키지 일괄 무인 렌더링"""
        if not target_langs:
            target_langs = ["ko", "en", "vi", "zh", "uz"]

        service_data = self.router.get_service(service_id)
        scraper = ViralTrendScraper()
        results = []

        for lang in target_langs:
            try:
                # 1. AI 대본 생성
                script = self.gemini.generate_shorts_script(service_id, service_data, target_lang=lang)
                hook_title = script.get("hook_title", f"Korea Expat Tip: {service_data.get('name')}")
                voice_text = script.get("voiceover_text", "")
                captions = script.get("captions", [])

                # 2. 17개국 실시간 바이럴 해시태그 자동 추출
                hashtags = scraper.get_viral_hashtags(service_id, lang, count=8)
                hashtag_str = " ".join(hashtags)
                script["hashtags"] = hashtags
                script["hashtag_str"] = hashtag_str

                # 3. 동적 UTM 랜딩 링크
                campaign = UTMTracker.generate_campaign_tag(service_id, "shorts", lang)
                landing_url = UTMTracker.build_url(
                    base_url=service_data.get("landing_url", "https://k-market.app"),
                    source="shorts",
                    medium="video_cta",
                    campaign=campaign,
                    lang=lang
                )

                # 4. TTS 음성 파일 생성 (.mp3)
                audio_filename = "shorts_{}_{}.mp3".format(service_id, lang)
                audio_path = self.tts.generate_speech(voice_text, lang=lang, filename=audio_filename)

                # 5. 케이마켓 Supabase 실물 사진 연동 9:16 비주얼 프레임 렌더링 (1080x1920)
                frame_path = self._render_vertical_frame(service_id, service_data, lang, hook_title, captions)

                # 6. ★ 이미지 + 음성 + BGM → 최종 .mp4 숏폼 영상 합성
                mp4_path = self.video_composer.compose(
                    frame_path=frame_path,
                    audio_path=audio_path,
                    service_id=service_id,
                    lang=lang,
                    bgm_volume=0.07,
                )

                # 7. DB 기록 (유니크 ID 생성)
                unique_ext_id = "shorts_{}_{}_{}".format(service_id, lang, int(time.time() * 1000))
                hist_id = self.db_mgr.record_history(
                    content_type="shorts",
                    service_id=service_id,
                    target_lang=lang,
                    title=hook_title,
                    content_text=json.dumps(script, ensure_ascii=False),
                    target_url=landing_url,
                    external_id=unique_ext_id
                )

                results.append({
                    "history_id": hist_id,
                    "service_id": service_id,
                    "lang": lang,
                    "title": hook_title,
                    "audio_path": str(audio_path) if audio_path else "",
                    "frame_path": str(frame_path),
                    "mp4_path": str(mp4_path) if mp4_path else "",
                    "landing_url": landing_url,
                    "hashtags": hashtags
                })
                logger.info(f"[{lang.upper()}] 숏폼 패키지 렌더링 완료: {hook_title}")
            except Exception as e:
                logger.error(f"[{lang}] 숏폼 렌더링 실패: {e}")

        return results

    def _get_real_item_for_lang(self, lang: str) -> Optional[Dict[str, Any]]:
        """해당 언어 또는 0원 나눔에 적합한 실제 케이마켓 실물 매물 선정"""
        if not self.kmarket_items:
            return None
        
        # 0원 무료 나눔 또는 실물 사진이 있는 매물 우선 검색
        for item in self.kmarket_items:
            if item.get("images") and len(item["images"]) > 0:
                if item.get("price") == 0:
                    return item
        return self.kmarket_items[0]

    def _fetch_or_cache_image(self, url: str) -> Optional[Image.Image]:
        """실제 매물 사진 다운로드 및 Pillow Image 객체 반환 (캐시 지원)"""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                return Image.open(io.BytesIO(data)).convert("RGB")
        except Exception as e:
            logger.info(f"실물 이미지 다운로드 실패(대체 그래픽 생성): {e}")
            return None

    def _render_vertical_frame(self, service_id: str, service_data: Dict[str, Any], lang: str, 
                               title: str, captions: List[str]) -> Path:
        """Pillow 기반 9:16 (1080x1920) 세로형 비주얼 프레임 생성 (실제 K-Market 실물 사진 합성)"""
        width, height = 1080, 1920
        # 모던 다크 블루-슬레이트 배경
        image = Image.new("RGB", (width, height), color=(10, 15, 30))
        draw = ImageDraw.Draw(image)

        # 1. 상단 서비스 & 브랜드 헤더
        draw.rectangle([(80, 80), (1000, 180)], fill=(20, 30, 50), outline=(59, 130, 246), width=2)
        draw.text((110, 115), f"🛸 {service_data.get('name', 'Korea Expat Engine')}", fill=(96, 165, 250))
        draw.text((820, 115), f"[{lang.upper()}]", fill=(148, 163, 184))

        # 2. 메인 후킹 타이틀 카드
        draw.rectangle([(80, 210), (1000, 360)], fill=(30, 41, 59), outline=(239, 68, 68), width=3)
        draw.text((110, 245), f"🔥 {title[:38]}", fill=(255, 255, 255))
        draw.text((110, 300), f"⚡ Real Verified Expat Benefit in Korea", fill=(251, 191, 36))

        # 3. 중앙: 케이마켓 실제 실물 매물 사진 카드 합성!
        if service_id == "kmarket":
            real_item = self._get_real_item_for_lang(lang)
            if real_item and real_item.get("images"):
                img_url = real_item["images"][0]
                item_img = self._fetch_or_cache_image(img_url)
                
                # 실물 사진 컨테이너 박스 (840x840)
                card_x, card_y = 120, 400
                card_w, card_h = 840, 840
                
                if item_img:
                    item_resized = item_img.resize((card_w, card_h))
                    image.paste(item_resized, (card_x, card_y))
                else:
                    draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill=(40, 55, 80))
                    draw.text((card_x + 200, card_y + 400), "📷 Real Item Photo", fill=(255, 255, 255))

                # 실물 사진 위 0원 나눔 & 가격 뱃지 오버레이
                item_price = real_item.get("price", 0)
                price_label = "🎁 0원 무료 나눔 (FREE)" if item_price == 0 else f"🏷️ ₩{item_price:,}"
                draw.rectangle([(card_x + 20, card_y + 20), (card_x + 480, card_y + 100)], fill=(16, 185, 129))
                draw.text((card_x + 40, card_y + 45), price_label, fill=(255, 255, 255))

                # 판매자 실명 인증 & 동네 위치 태그 오버레이
                region_name = real_item.get("region", "안산/시흥/수원")
                draw.rectangle([(card_x + 20, card_y + card_h - 100), (card_x + card_w - 20, card_y + card_h - 20)], fill=(0, 0, 0, 200))
                draw.text((card_x + 40, card_y + card_h - 75), f"📍 {region_name} • 100% 외국인등록증 인증 실매물", fill=(255, 255, 255))
        else:
            # 💰 EasyTax: VisualSafetyEngine을 통한 1인칭 POV 스마트폰 입금 알림 & 인포그래픽 프레임 렌더링
            output_path = self.output_dir / "frame_easytax_{}.png".format(lang)
            return self.safety_engine.render_safe_easytax_pov_frame(
                lang=lang,
                title=title,
                captions=captions,
                estimated_krw=3840000,
                output_path=output_path
            )

        # 4. 하단 캡션 안내 (K-Market 공통)
        y_pos = 1300
        for cap in captions[:2]:
            draw.rectangle([(80, y_pos), (1000, y_pos + 100)], fill=(30, 41, 59), outline=(59, 130, 246), width=1)
            draw.text((120, y_pos + 30), f"✅ {cap}", fill=(226, 232, 240))
            y_pos += 120

        # 5. Anti-Ban 안전 공인 뱃지 바 (선입금 일절 없음 + 공인 세무대리)
        if service_id == "easytax":
            draw.rectangle([(80, 1540), (1000, 1610)], fill=(30, 41, 59), outline=(16, 185, 129), width=1)
            draw.text((100, 1565), "🛡️ 선입금 0원 • 100% 무료 AI 조회 • 국세청 공인 세무대리 진행", fill=(52, 211, 153))

        # 6. 하단 원클릭 CTA 배너
        cta_bg = (16, 185, 129) if service_id == "kmarket" else (37, 99, 235)
        cta_label = "👉 프로필 링크 클릭 시 실물 매물 / 0원 나눔 바로 확인!" if service_id == "kmarket" else "👉 프로필 링크에서 3분 만에 무료 환급액 확인하기!"
        draw.rectangle([(80, 1630), (1000, 1750)], fill=cta_bg)
        draw.text((130, 1675), cta_label, fill=(255, 255, 255))

        # 7. 공식 법적 면책 조항 (Legal Disclaimer)
        draw.text((100, 1770), "* 국세기본법에 따른 공인 세무대리 절차로 진행되며 실제 환급액은 소득에 따라 상이할 수 있습니다.", fill=(100, 116, 139))

        output_path = self.output_dir / f"frame_{service_id}_{lang}.png"
        image.save(output_path)
        return output_path
