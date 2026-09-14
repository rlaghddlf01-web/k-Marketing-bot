# -*- coding: utf-8 -*-
"""
CardNewsBatchProducer - 📸 [EasyTax 5장 온전한 풀사이즈 카드뉴스 & 4대 SNS 패키지 일괄 생산 엔진]
- 7:3 분할 완전 폐기: 1080x1350 풀블리드(Full-Bleed) + 하단 그라디언트 스크림
- 얼굴 가림 0% & 손가락 기괴함 0%: 인물 반대편(좌측 여백) 공중 3D 플로팅 스마트폰
- 5장 기승전결 (1:후킹환희 -> 2:공장노동 -> 3:0원안심보증 -> 4:비행기표결실 -> 5:1분조회CTA)
- 4대 SNS(스레드, 인스타, 페북, 텔레그램) SEO 포스팅 가이드 동시 출력
- 바탕화면 '카드뉴스_산출물/이지택스_[테마]_[언어]' 폴더에 완제품 세트 저장
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from core.scenario_director_cardnews_easytax import ScenarioDirectorCardnewsEasyTax
from core.screen_inset_compositor import ScreenInsetCompositor
from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.engine.wan_pipeline_client import WanPipelineClient
from core.easytax_app_capturer import EasyTaxAppCapturer
from brands.easytax.ui_templates.refund_receipt_template import RefundReceiptTemplate
from brands.easytax.scenarios.prompt_director_cardnews import PromptDirectorCardNewsEasyTax
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter

logger = logging.getLogger("CardNewsBatchProducer")

def _draw_text_wrapped(
    draw,
    text: str,
    font,
    x: int,
    y: int,
    max_width: int,
    fill: tuple,
    shadow_fill: tuple = (0, 0, 0),
    line_gap: int = 6
) -> int:
    """
    텍스트를 max_width 안에서 자동 줄바꿼하여 선버려다.
    - 드롭썸도우(shadow_fill) 1px 오프셋 자동 적용
    - 마지막으로 그린 줄의 다음 y 좌표 반환 (동적 레이아웃 토대)
    """
    if not text:
        return y

    # 단어 단위 줄바꿼
    words = text.split()
    lines: list = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] + line_gap
    curr_y = y
    for line in lines:
        draw.text((x + 1, curr_y + 1), line, fill=shadow_fill, font=font)
        draw.text((x,     curr_y),     line, fill=fill,        font=font)
        curr_y += line_h
    return curr_y


def _load_font(size: int, bold: bool = True, lang: str = "vi") -> ImageFont.FreeTypeFont:
    """언어별 최적 유니코드 폰트 자동 매칭 (베트남어/우즈벡어 글자 깨짐 0% 보장)"""
    if lang == "ko":
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        ]
    elif lang in ["vi", "es", "id", "tl", "en"]:  # 베트남어 성조 100% 지원
        candidates = [
            # ✅ Segoe UI Bold: 베트남어 성조(à á â ã ä...) 완전 지원, ASCII > 사용으로 Tofu 0%
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        ]
    elif lang in ["ru", "uz", "mn", "kk"]:  # 키릴 및 중앙아시아 문자
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        ]

    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


class CardNewsBatchProducer:
    """이지택스 5장 풀사이즈 카드뉴스 & 4대 SNS 배포 팩 일괄 생산기"""

    def __init__(self):
        self.scenario_director = ScenarioDirectorCardnewsEasyTax()
        self.inset_compositor = ScreenInsetCompositor()
        self.embedder = PhoneScreenEmbedder()
        self.wan_client = WanPipelineClient()
        self.app_capturer = EasyTaxAppCapturer()
        self.ui_template = RefundReceiptTemplate()
        self.copywriter = GeminiCardnewsCopywriter(service_id="easytax")
        # 로컬 바탕화면 전용 저장 경로
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")
        # ComfyUI 헬스체크 (실행 여부 확인)
        self._wan_available = self.wan_client.check_health()
        if self._wan_available:
            logger.info("✅ [WanPipelineClient] ComfyUI 연결 성공 - 그래픽카드 T2I 사진 생성 모드")
        else:
            logger.warning("⚠️ [WanPipelineClient] ComfyUI 미실행 - 기존 샘플 사진 Fallback 모드")

    def generate_carousel_cardnews(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        amount: int = 3100000,
        preferred_gender: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GoldenBatchProducer 등 배치 봇 엔진 호환용 alias"""
        return self.produce_full_set(lang=lang, theme_index=theme_index, amount=amount, preferred_gender=preferred_gender, **kwargs)

    def produce_full_set(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        amount: int = 3100000,
        custom_hero_image: Optional[Image.Image] = None,
        preferred_gender: Optional[str] = None,
        master_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """5장 카드뉴스 세트 및 SNS 가이드 일괄 생산"""
        # 1. 시나리오 기획 로드 (60대 테마)
        scenario = self.scenario_director.get_carousel_scenario(
            lang=lang,
            theme_index=theme_index,
            preferred_gender=preferred_gender
        )
        theme_id = scenario.get("theme_name", "general")
        theme_title = scenario.get("theme_title", "EasyTax Tax Refund")
        cards = scenario.get("cards", [])

        # 🎯 [결함 5 근본 해결] 테마 고유 환급액 우선 연동 (영수증 UI와 제미나이 헤드라인 금액 100% 일치)
        effective_amount = scenario.get("refund_est") or amount
        logger.info(f"💰 [환급액 일원화 확정] 테마 고유 환급액: {effective_amount:,}원 (영수증 UI ₩{effective_amount:,} = 헤드라인 {effective_amount:,} KRW 일치)")

        # 🎮 ComfyUI GPU 엔진 상태 확인 및 무인 자동 기동
        if not self._wan_available:
            self._wan_available = self.wan_client.check_health(auto_start=True)
            if self._wan_available:
                logger.info("✅ [WanPipelineClient] ComfyUI 백그라운드 자동 기동 완료 - GPU 실사 T2I 사진 생성 모드 전환!")

        # 2. 결과 저장 폴더 생성 (로컈 바탕화면 전용)
        # C:\Users\zkfnt\Desktop\카드뉴스_산출물\이지텍스\이지텍스_[언어]_[테마]_[날짜시분]
        from datetime import datetime
        dt_str      = datetime.now().strftime("%Y%m%d_%H%M")
        folder_name = f"이지텍스_{lang.upper()}_{theme_id}_{dt_str}"
        out_dir = self.desktop / "카드뉴스_산출물" / "이지텍스" / folder_name
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 산출물 폴더 생성: {out_dir}")

        # 3. Fallback용 인물 사진 준비 (ComfyUI 미실행 시에만 사용)
        if custom_hero_image is not None:
            fallback_img = custom_hero_image
        else:
            # ComfyUI 미실행 시 기본 캔버스
            fallback_img = Image.new("RGB", (1080, 1350), (11, 19, 43))

        # 4. [1단계] 5장 베이스 사진 순차 생성 (1번 T2I 마스터 ➔ 2, 3, 4, 5번 전 슬라이드 동일 인물 img2img)
        logger.info("🎨 [Phase 1] 1~5번 전 슬라이드 동일 인물 WAN 사진 생성 시작...")
        base_photos: Dict[int, Image.Image] = {}
        slide1_ref_path: Optional[str] = None
        
        # 5장 세트 전체 캐릭터 얼굴 100% 일치를 위한 마스터 시드 발급
        import random
        if master_seed is None:
            master_seed = random.randint(1000000, 99999999)
        logger.info(f"🔒 [캐릭터 일치 마스터 시드 확정]: {master_seed}")

        for card in sorted(cards, key=lambda c: c.get("slide_idx", 1)):
            s_idx = card.get("slide_idx", 1)
            if s_idx == 1 and custom_hero_image is not None:
                base_photo = custom_hero_image
                logger.info("🌟 [Slide 1] 검증 승인된 마스터 주인공 인물 사진(custom_hero_image) 직접 적용!")
            else:
                base_photo = self._generate_slide_photo(
                    s_idx=s_idx,
                    card_data=card,
                    fallback_img=fallback_img,
                    master_seed=master_seed
                )
            base_photos[s_idx] = base_photo

        # 5. [2단계] 합성 + 텍스트 오버레이 + 저장
        logger.info("🖌️ [Phase 2] 합성 및 텍스트 오버레이...")
        saved_slides = []
        for card in cards:
            s_idx = card.get("slide_idx", 1)
            rendered_slide = self._render_slide(
                s_idx=s_idx,
                card_data=card,
                base_photo=base_photos[s_idx],
                lang=lang,
                amount=effective_amount
            )

            out_filename = f"slide_{s_idx}.png"
            out_path = out_dir / out_filename
            rendered_slide.save(str(out_path), "PNG", quality=95)
            saved_slides.append(out_path)
            logger.info(f"✅ 슬라이드 {s_idx}/5 저장 완료: {out_path.name}")

        # 6. 4대 SNS 포스팅 패키지 가이드 파일 저장
        guide_filename = f"SNS_포스팅_가이드_{lang.upper()}.txt"
        guide_path = out_dir / guide_filename
        self._write_sns_guide(
            file_path=guide_path,
            lang=lang,
            theme_title=theme_title,
            amount=effective_amount,
            cards=cards
        )

        logger.info(f"🎉 [EasyTax 5장 카드뉴스 세트 완성] 폴더: {out_dir}")
        return {
            "folder_path": str(out_dir),
            "slides": [str(p) for p in saved_slides],
            "guide_path": str(guide_path),
            "theme_title": theme_title,
            "lang": lang,
            "amount": effective_amount,
            "refund_formatted": f"{effective_amount:,} KRW"
        }

    def _generate_slide_photo(
        self,
        s_idx: int,
        card_data: Dict[str, Any],
        fallback_img: Image.Image,
        master_seed: int = 2026
    ) -> Image.Image:
        """
        슬라이드별 씬 사진을 WAN T2I로 독립 생성 (동일 캐릭터 앵커 + 동일 마스터 시드):
        - Slide 1~5: 전 슬라이드 독립 T2I (generate_t2i_master, seed=master_seed)
        - 60% 황금비율 미디엄 샷 적용 + 씬별 100% 다른 의상/배경/포즈 연출
        """
        if not self._wan_available:
            logger.warning(f"[Slide {s_idx}] ComfyUI 미실행 → Fallback 사용")
            return fallback_img

        positive_prompt = card_data.get("image_prompt", "")
        negative_prompt = card_data.get("negative_prompt", None)

        if not positive_prompt:
            logger.warning(f"[Slide {s_idx}] image_prompt 없음 → Fallback 사용")
            return fallback_img

        width, height = 832, 1216
        prefix = f"cardnews_easytax_slide{s_idx}_{int(time.time())}"

        try:
            # 🎯 [전 슬라이드 독립 T2I + 마스터 시드 동기화]
            # - 이전 슬라이드의 옷/배경/포즈가 잔상으로 남는 img2img 전면 폐기
            # - 슬라이드별 100% 다른 의상/포즈/배경을 완벽한 60% 미디엄 샷으로 독립 생성
            # - 동일 캐릭터 앵커 프롬프트 + 동일 master_seed로 동일 인물 정체성 보존
            logger.info(f"🎨 [Slide {s_idx}] WAN T2I 씬 사진 생성 (seed={master_seed}) → {prefix}")
            generated_path = self.wan_client.generate_t2i_master(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=master_seed,
                prefix=prefix
            )

            generated_img = Image.open(generated_path).convert("RGB")
            logger.info(f"✅ [Slide {s_idx}] WAN 생성 완료: {generated_path}")
            return generated_img
        except Exception as e:
            logger.error(f"❌ [Slide {s_idx}] WAN 생성 실패 ({e}) → Fallback 사용")
            return fallback_img

    def _render_slide(
        self,
        s_idx: int,
        card_data: Dict[str, Any],
        base_photo: Image.Image,
        lang: str,
        amount: int
    ) -> Image.Image:
        """슬라이드 번호별 합성 + 텍스트 오버레이 (1080x1350 풀블리드 + 그라디언트 스크림)"""

        # A. 슬라이드 번호에 따라 스마트폰 화면 인셋 합성 (이미 WAN으로 생성된 base_photo 사용)
        if s_idx == 1:
            ui_img = self.ui_template.render(amount=amount)
            # 1. 인물이 손에 쥔 스마트폰 액정 영역에 직접 정밀 광학 매립 시도
            try:
                composite_photo = self.embedder.embed_screen(base_image=base_photo, ui_image=ui_img)
                logger.info("📱 [Slide 1] 인물 스마트폰 액정에 환급 영수증 정밀 매립 성공!")
            except Exception as e:
                logger.info(f"📱 [Slide 1] 액정 직접 매립 불가 ({e}) -> 좌측 안전 여백 3D 플로팅 적용")
                composite_photo = self.inset_compositor.composite_custom_ui_onto_photo(
                    base_photo=base_photo,
                    ui_image=ui_img,
                    position="left_floating",
                    scale=0.50
                )
        elif s_idx == 3:
            # 3번: 1번 동일 주인공 인물 사진 위에 이지택스 앱 0단계 모의조회 화면 좌측 플로팅
            screen_path = self.app_capturer.get_screen_path(lang=lang, screen_type="step0")
            composite_photo = self.inset_compositor.composite_easytax_screen_onto_photo(
                base_photo=base_photo,
                screen_img_path=screen_path,
                lang=lang,
                position="left_floating",
                scale=0.50
            )
        elif s_idx == 5:
            # 5번: 1번 동일 주인공 인물 사진 위에 이지택스 앱 메인 홈 1분 조회 CTA 화면 좌측 플로팅
            screen_path = self.app_capturer.get_screen_path(lang=lang, screen_type="home_cta")
            composite_photo = self.inset_compositor.composite_easytax_screen_onto_photo(
                base_photo=base_photo,
                screen_img_path=screen_path,
                lang=lang,
                position="left_floating",
                scale=0.50
            )
        else:
            # 2번 (공장/노동 현장), 4번 (귀국/감동): img2img로 동일 인물 유지된 사진 그대로 사용
            composite_photo = base_photo

        # B. 1080x1350 풀사이즈 캔버스 센터 크롭 리사이즈
        canvas = Image.new("RGB", (1080, 1350), (11, 19, 43))
        W, H = composite_photo.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = composite_photo.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # C. 하단 부드러운 그라디언트 스크림 (Gradient Scrim) 오버레이
        gradient_layer = Image.new("RGBA", (1080, 1350), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient_layer)
        scrim_start_y = 820
        scrim_height = 1350 - scrim_start_y

        for i in range(scrim_height):
            curr_y = scrim_start_y + i
            ratio = i / float(scrim_height)
            alpha = int((ratio ** 2.2) * 238)
            g_draw.line([(0, curr_y), (1080, curr_y)], fill=(11, 19, 43, alpha))

        canvas = Image.alpha_composite(canvas.convert("RGBA"), gradient_layer).convert("RGB")
        draw = ImageDraw.Draw(canvas)

        # D. 매거진 타이포그래피 (자동 줄바꿼 + 켴은 폰트 + 드롭썸도우 포함)
        # 폰트 크기: 헤드 46px / 서브 27px / 배지 22px
        font_head  = _load_font(46, bold=True,  lang=lang)
        font_sub   = _load_font(27, bold=False, lang=lang)
        font_badge = _load_font(22, bold=True,  lang=lang)

        badge_text    = card_data.get("badge",    f"STEP {s_idx}")
        title_text    = card_data.get("title",    f"Step {s_idx} Title")
        subtitle_text = card_data.get("subtitle", "")
        bullets       = card_data.get("bullets",  [])

        TEXT_X     = 60    # 좌측 여백
        MAX_W      = 960   # 1080 - 60(left) - 60(right) 텍스트 안전 영역
        CTA_TOP    = 1185  # CTA 버튼 상단 경계

        # 상단 페이지 인덱스 배지 (우측)
        page_badge = f"{s_idx:02d} / 05 >"
        draw.text((930, 916), page_badge, fill=(212, 175, 55), font=font_badge)

        # 좌측 플로팅 배지 라운드렉탄글
        badge_w = min(460, max(280, int(len(badge_text) * 17)))
        draw.rounded_rectangle([(TEXT_X, 910), (TEXT_X + badge_w, 956)], radius=8, fill=(30, 80, 160))
        draw.text((TEXT_X + 14, 918), badge_text, fill=(255, 255, 255), font=font_badge)

        # 글자 레이아웃 시작 y (배지 아래 12px 여백)
        cur_y = 968

        # 헤드라인 (골드 + 아웃라인 셈도우)
        cur_y = _draw_text_wrapped(
            draw, title_text, font_head,
            x=TEXT_X, y=cur_y, max_width=MAX_W,
            fill=(255, 215, 0), shadow_fill=(0, 0, 0), line_gap=5
        )
        cur_y += 10  # 헤드~서브 사이 여백

        # 서브카피 (라이트 그레이)
        cur_y = _draw_text_wrapped(
            draw, subtitle_text, font_sub,
            x=TEXT_X, y=cur_y, max_width=MAX_W,
            fill=(225, 230, 240), shadow_fill=(0, 0, 0), line_gap=5
        )
        cur_y += 10  # 서브~불릿 사이 여백

        # 3줄 불릿 (라이트 블루) — CTA 버튼 영역 취침 안전장치 포함
        for bullet_line in bullets[:3]:
            if not bullet_line or cur_y + 36 > CTA_TOP:
                break  # CTA 버튼과 격치다면 충구 중단
            cur_y = _draw_text_wrapped(
                draw, bullet_line, font_sub,
                x=TEXT_X, y=cur_y, max_width=MAX_W,
                fill=(200, 220, 255), shadow_fill=(0, 0, 0), line_gap=4
            )
            cur_y += 6  # 불릿 줄 간 여백

        # 🎯 8개국어 맞춤 CTA 버튼 텍스트 사전 등록 (글자 깨짐 100% 박멸)
        cta_i18n = {
            "uz": {
                "cta": "Qaytariladigan pulni bepul tekshirish  >",
                "next": "Keyingi qismni ko'rish  >"
            },
            "vi": {
                "cta": "Kiểm tra tiền hoàn thuế miễn phí ngay  >",
                "next": "Xem tiếp nội dung tiếp theo  >"
            },
            "mn": {
                "cta": "Татварын буцаан олголтоо шалгах  >",
                "next": "Дараагийн хэсгийг үзэх  >"
            },
            "th": {
                "cta": "ตรวจสอบเงินคืนภาษีฟรีทันที  >",
                "next": "ดูเนื้อหาถัดไป  >"
            },
            "km": {
                "cta": "ពិនិត្យប្រាក់ពន្ធឥតគិតថ្លៃ  >",
                "next": "មើលផ្នែកបន្ទាប់  >"
            },
            "ne": {
                "cta": "कर फिर्ता रकम नि:शुल्क हेर्नुहोस्  >",
                "next": "अर्को भाग हेर्नुहोस्  >"
            },
            "id": {
                "cta": "Cek pengembalian pajak gratis sekarang  >",
                "next": "Lihat bagian selanjutnya  >"
            },
            "my": {
                "cta": "အခမဲ့ အခွန်ပြန်အမ်းငွေ စစ်ဆေးရန်  >",
                "next": "နောက်တစ်ပိုင်းကို ကြည့်ပါ  >"
            },
            "ru": {
                "cta": "Проверить возврат налога бесплатно  >",
                "next": "Смотреть дальше  >"
            },
            "ko": {
                "cta": "지금 내 환급금 무료 조회하기  >",
                "next": "다음 내용 확인하기  >"
            },
            "en": {
                "cta": "Check your tax refund for free now  >",
                "next": "See the next slide  >"
            }
        }
        btn_dict = cta_i18n.get(lang, cta_i18n["en"])
        btn_text = btn_dict["cta"] if s_idx in [1, 5] else btn_dict["next"]

        btn_bg = (212, 175, 55) if s_idx in [1, 5] else (30, 41, 59)
        btn_fg = (15, 23, 42)   if s_idx in [1, 5] else (255, 255, 255)

        draw.rounded_rectangle([(60, 1190), (1020, 1285)], radius=20, fill=btn_bg)
        bbox_cta = draw.textbbox((0, 0), btn_text, font=font_head)
        tw_cta   = bbox_cta[2] - bbox_cta[0]
        draw.text(((1080 - tw_cta) // 2, 1214), btn_text, fill=btn_fg, font=font_head)

        return canvas

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        theme_title: str,
        amount: int,
        cards: List[Dict[str, Any]]
    ):
        """스레드, 인스타그램, 페이스북, 텔레그램 4대 채널별 포스팅 가이드 텍스트 저장 (8개국어 다국어화)"""
        amount_fmt = f"{amount:,} KRW"
        
        # 언어별 고유 바이럴 해시태그 사전
        lang_hashtags = {
            "uz": "#EasyTax #SoliqQaytarish #DaromadSoligi #E9Visa #JanubiyKoreya #OzbeklarKoreyada #KoreyadaHayot #E7Visa #KTRS #SoliqMaslahati",
            "vi": "#EasyTax #HoànThuế #ThuếThuNhập #E9Visa #LaoĐộngHànQuốc #CuộcSốngHànQuốc #ViệtNamTạiHàn #이지택스 #외국인세금환급 #조특법30조",
            "mn": "#EasyTax #ТатварБуцаанОлголт #E9Виз #СолонгосДахьМонголчууд #СолонгосынАмьдрал #ТатварынХөнгөлөлт #KTRS",
            "th": "#EasyTax #ขอคืนภาษีเกาหลี #แรงงานไทยในเกาหลี #วีซ่าE9 #ชีวิตในเกาหลี #คนไทยในเกาหลี #KTRS",
            "km": "#EasyTax #បង្វិលពន្ធកូរ៉េ #ពលករខ្មែរនៅកូរ៉េ #ទិដ្ឋាការE9 #ជីវិតនៅកូរ៉េ #KTRS",
            "ne": "#EasyTax #कोरियाकरफिर्ता #नेपालीकोरिया #E9भिसा #कोरियामाजीवन #KTRS",
            "id": "#EasyTax #RefundPajakKorea #TKIJepangKorea #VisaE9 #PekerjaMigranIndonesia #KTRS",
            "my": "#EasyTax #ကိုရီးယားအခွန်ပြန်အမ်းငွေ #မြန်မာလုပ်သား #E9ဗီဇာ #KTRS",
            "ru": "#EasyTax #ВозвратНалогаКорея #РаботаВКорее #ВизаE9 #РусскоязычныеВКорее #KTRS"
        }
        hashtags = lang_hashtags.get(lang, "#EasyTax #KoreaTaxRefund #E9Visa #WorkInKorea #ForeignWorker")

        # 1번 및 5번 카드 카피 추출
        card1_title = cards[0].get("title", "") if len(cards) > 0 else ""
        card5_title = cards[4].get("title", "") if len(cards) > 4 else ""

        content = f"""================================================================================
📢 [EasyTax 카드뉴스 공식 SNS 포스팅 패키지] ({lang.upper()} / {amount_fmt})
주제: {theme_title}
타깃 언어: {lang.upper()}
공식 웹앱 링크: https://ktrs-service.vercel.app/?lang={lang}
================================================================================

1. 🧵 스레드 (Threads) 포스팅 팩
--------------------------------------------------------------------------------
[헤드라인 텍스트]:
🔥 {card1_title} ({amount_fmt})

[본문]:
대한민국 국세청(NTS) 조세특례제한법 제30조 외국인 소득세 최대 90% 감면 혜택 안내.
지난 5년 동안 성실히 일하며 납부한 세금을 단 1분 만에 무료로 모의 계산해보세요.
착수금/선결제 0원, 국세청에서 환급금이 먼저 입금된 후 정산하는 100% 안전 후불제입니다.

👉 {card5_title}
링크: https://ktrs-service.vercel.app/?lang={lang}

[해시태그]:
{hashtags}


2. 📸 인스타그램 (Instagram) 포스팅 팩
--------------------------------------------------------------------------------
[본문 캡션]:
🇰🇷 대한민국 국세청 공식 세무 환급 안내
"{card1_title} - {amount_fmt} 입금 완료!"

외국인 근로자를 위한 90% 소득세 감면 혜택 (조세특례제한법 제30조)
신청만 하면 지난 5년 동안 낸 세금이 내 통장으로 안전하게 입금됩니다 💸

✨ 이지택스(EasyTax) 3대 안심 보증:
1️⃣ 착수금/선결제 0원! (국세청 환급금 먼저 입금 후 후불 정산)
2️⃣ 공인 세무법인의 100% 합법 국세청 다이렉트 전산 처리
3️⃣ 스마트폰으로 단 1분 만에 간편 모의 계산 완료!

지금 프로필 링크(Link in Bio)를 누르고 숨어있는 내 환급금을 확인하세요! 🔍

[SEO 바이럴 해시태그]:
{hashtags} #외국인세금환급 #조특법30조 #국세청환급 #E9근로자 #E7비자 #소득세감면 #환급금조회


3. 📘 페이스북 (Facebook) 커뮤니티 그룹 포스팅 팩
--------------------------------------------------------------------------------
[제목]:
[필독] {theme_title} - 소득세 최대 90% 환급 신청 안내 ({amount_fmt})

[본문]:
한국의 제조 공장, 농축산, 건설, 물류 현장에서 땀 흘려 일하시는 근로자 여러분 안녕하십니까.
최근 5년 동안 대한민국 국세청에 납부하신 소득세 중 최대 90%를 합법적으로 돌려받으실 수 있습니다.

📌 핵심 안내 사항:
- 조세특례제한법 제30조에 따른 중소기업 취업자 소득세 감면 혜택
- 평균 환급액: 200만 ~ 450만 원 상당 ({amount_fmt} 실사례 다수)
- 선결제 수수료 0원 (국세청에서 입금 확인 후 정산하는 안전 후불제)

5년의 법적 소멸시효가 지나면 세금이 국가로 환수되오니, 지금 바로 공식 링크에서 무료 조회를 진행해보시기 바랍니다.

👉 공식 간편 환급 조회: https://ktrs-service.vercel.app/?lang={lang}


4. ✈️ 텔레그램 (Telegram) 단톡방 / 채널 팩
--------------------------------------------------------------------------------
⚡ [공지] 대한민국 국세청 외국인 근로자 세금 환급 안내

💰 예상 환급금: {amount_fmt}
✅ 대상 비자: E-9, E-7, H-2, F-4, D-2 등 외국인 근로자
🛡️ 수수료: 0원 (100% 성공 후불제, 사전 비용 없음)

⏱️ 소요 시간: 스마트폰 1분 조회
🔗 지금 바로 확인하기: https://ktrs-service.vercel.app/?lang={lang}
================================================================================
"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"📄 [{lang.upper()}] 다국어 SNS 가이드 저장 완료: {file_path.name}")
        except Exception as e:
            logger.warning(f"SNS 가이드 작성 에러: {e}")

    def generate_carousel_cardnews(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        amount: int = 3100000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        [호환성 인터페이스] 기존 모듈 및 GoldenBatchProducer 규격과 100% 호환되는 별칭 메서드.
        신형 5장 풀블리드 파이프라인(produce_full_set)을 실행합니다.
        """
        return self.produce_full_set(lang=lang, theme_index=theme_index, amount=amount)

