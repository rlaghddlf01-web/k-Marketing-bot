# -*- coding: utf-8 -*-
"""
CardNewsBatchProducerKMarket - 🛒 [K-Market 5장 온전한 풀사이즈 카드뉴스 & 4대 SNS 패키지 일괄 생산 엔진]
- 7:3 분할 완전 폐기: 1080x1350 풀블리드(Full-Bleed) + 하단 그라디언트 스크림
- 스마트폰 화면 매립 및 3D 플로팅 UI 전면 제외: 1~5장 모두 100% 깨끗한 감성 라이프스타일 실사 사진
- 5장 기승전결 (1:0원나눔수령 -> 2:자취방배치뿌듯 -> 3:150만원절약안도 -> 4:가족사랑감동 -> 5:케이마켓추천CTA)
- 1~5번 전 슬라이드 동일 인물 마스터 시드 동기화 + 8대 국가 고유 앵커
- 4대 SNS(스레드, 인스타, 페북, 텔레그램) 현지어 원문 + 한국어 해설 2단 포스팅 가이드 동시 출력
- 바탕화면 '카드뉴스_산출물/케이마켓/케이마켓_[언어]_[테마]_[날짜시분]' 폴더에 완제품 세트 저장
"""

import os
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont

from core.scenario_director_cardnews_kmarket import ScenarioDirectorCardnewsKMarket
from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.sns_guide_generator import SNSGuideGenerator

logger = logging.getLogger("CardNewsBatchProducerKMarket")


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
    텍스트를 max_width 안에서 자동 줄바꿈하여 렌더링.
    - 드롭섀도우(shadow_fill) 1px 오프셋 자동 적용
    - 마지막으로 그린 줄의 다음 y 좌표 반환 (동적 레이아웃)
    """
    if not text:
        return y

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


def _load_font(size: int, bold: bool = True, lang: str = "uz") -> ImageFont.FreeTypeFont:
    """언어별 최적 유니코드 폰트 자동 매칭 (베트남어 성조/우즈벡어/몽골어 키릴 글자 깨짐 0% 보장)"""
    if lang == "ko":
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        ]
    elif lang in ["vi", "es", "id", "tl", "en"]:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        ]
    elif lang in ["ru", "uz", "mn", "kk"]:
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


class CardNewsBatchProducerKMarket:
    """K-Market 5장 풀사이즈 카드뉴스 & 4대 SNS 배포 팩 일괄 생산기"""

    def __init__(self):
        self.scenario_director = ScenarioDirectorCardnewsKMarket()
        self.wan_client = WanPipelineClient()
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")
        # ComfyUI 헬스체크
        self._wan_available = self.wan_client.check_health()
        if self._wan_available:
            logger.info("✅ [CardNewsBatchProducerKMarket] ComfyUI 연결 성공 - RTX 5060 Ti T2I 모드")
        else:
            logger.warning("⚠️ [CardNewsBatchProducerKMarket] ComfyUI 미실행 - Fallback 모드 대기")

    def generate_carousel_cardnews(
        self,
        lang: str = "uz",
        theme_index: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GoldenBatchProducer 및 대시보드 호환용 alias 메서드"""
        return self.produce_full_set(lang=lang, theme_index=theme_index, **kwargs)

    def produce_full_set(
        self,
        lang: str = "uz",
        theme_index: Optional[int] = None,
        custom_hero_image: Optional[Image.Image] = None,
        preferred_gender: Optional[str] = None,
        master_seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """5장 케이마켓 카드뉴스 완제품 세트 및 4대 SNS 가이드 일괄 생산"""
        # 1. 시나리오 기획 로드
        scenario = self.scenario_director.get_carousel_scenario(
            lang=lang,
            theme_index=theme_index
        )
        theme_id = scenario.get("theme_name", "general")
        theme_title = scenario.get("theme_title", "K-Market 0 Won Giveaway")
        cards = scenario.get("cards", [])

        # 2. ComfyUI GPU 엔진 상태 확인 및 무인 자동 기동
        if not self._wan_available:
            self._wan_available = self.wan_client.check_health(auto_start=True)
            if self._wan_available:
                logger.info("✅ [CardNewsBatchProducerKMarket] ComfyUI 백그라운드 자동 기동 완료")

        # 3. 결과 저장 폴더 생성 (로컬 바탕화면 전용)
        # C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓\케이마켓_[언어]_[테마]_[날짜시분]
        from datetime import datetime
        dt_str = datetime.now().strftime("%Y%m%d_%H%M")
        folder_name = f"케이마켓_{lang.upper()}_{theme_id}_{dt_str}"
        out_dir = self.desktop / "카드뉴스_산출물" / "케이마켓" / folder_name
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 [K-Market] 산출물 폴더 생성: {out_dir}")

        # 4. Fallback용 캔버스 (ComfyUI 미실행 시)
        if custom_hero_image is not None:
            fallback_img = custom_hero_image
        else:
            fallback_img = Image.new("RGB", (1080, 1350), (15, 23, 42))

        # 5. [1단계] 5장 베이스 사진 순차 생성 (1~5번 전 슬라이드 동일 인물 마스터 시드 동기화)
        logger.info("🎨 [Phase 1] K-Market 1~5번 전 슬라이드 동일 인물 WAN 라이프스타일 사진 생성 시작...")
        base_photos: Dict[int, Image.Image] = {}

        if master_seed is None:
            master_seed = random.randint(1000000, 99999999)
        logger.info(f"🔒 [K-Market 캐릭터 일치 마스터 시드 확정]: {master_seed}")

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

        # 6. [2단계] 풀블리드 합성 + 하단 그라디언트 스크림 + 매거진 타이포그래피 오버레이
        logger.info("🖌️ [Phase 2] K-Market 1080x1350 풀블리드 합성 및 텍스트 오버레이...")
        saved_slides = []
        for card in cards:
            s_idx = card.get("slide_idx", 1)
            rendered_slide = self._render_slide(
                s_idx=s_idx,
                card_data=card,
                base_photo=base_photos[s_idx],
                lang=lang
            )

            out_filename = f"slide_{s_idx}.png"
            out_path = out_dir / out_filename
            rendered_slide.save(str(out_path), "PNG", quality=95)
            saved_slides.append(out_path)
            logger.info(f"✅ [K-Market] 슬라이드 {s_idx}/5 저장 완료: {out_path.name}")

        # 7. 4대 SNS 포스팅 패키지 가이드 파일 저장 (현지어 원문 + 한국어 해설 2단)
        guide_filename = f"SNS_포스팅_가이드_{lang.upper()}.txt"
        guide_path = out_dir / guide_filename
        self._write_sns_guide(
            file_path=guide_path,
            lang=lang,
            theme_title=theme_title,
            cards=cards
        )

        logger.info(f"🎉 [K-Market 5장 카드뉴스 세트 완성] 폴더: {out_dir}")
        return {
            "folder_path": str(out_dir),
            "slides": [str(p) for p in saved_slides],
            "guide_path": str(guide_path),
            "theme_title": theme_title,
            "lang": lang,
            "master_seed": master_seed
        }

    def _generate_slide_photo(
        self,
        s_idx: int,
        card_data: Dict[str, Any],
        fallback_img: Image.Image,
        master_seed: int = 2026
    ) -> Image.Image:
        """
        슬라이드별 씬 사진을 WAN T2I로 독립 생성:
        - Slide 1~5: 전 슬라이드 독립 T2I (generate_t2i_master, seed=master_seed)
        - 100% 라이프스타일 실사 연출 (스마트폰 화면 매립 / 플로팅 UI 일체 배제)
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
        prefix = f"cardnews_kmarket_slide{s_idx}_{int(time.time())}"

        try:
            logger.info(f"🎨 [Slide {s_idx}] K-Market WAN T2I 사진 생성 (seed={master_seed}) → {prefix}")
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
        lang: str
    ) -> Image.Image:
        """
        순수 라이프스타일 실사 사진 기반 1080x1350 풀블리드 + 그라디언트 스크림 + 매거진 타이포 렌더링
        (스마트폰 액정 매립 및 3D 플로팅 UI 전면 배제)
        """
        # A. 1080x1350 풀사이즈 캔버스 센터 크롭 리사이즈
        canvas = Image.new("RGB", (1080, 1350), (15, 23, 42))
        W, H = base_photo.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = base_photo.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # B. 하단 부드러운 그라디언트 스크림 (Gradient Scrim) 오버레이
        gradient_layer = Image.new("RGBA", (1080, 1350), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient_layer)
        scrim_start_y = 820
        scrim_height = 1350 - scrim_start_y

        for i in range(scrim_height):
            curr_y = scrim_start_y + i
            ratio = i / float(scrim_height)
            alpha = int((ratio ** 2.2) * 242)
            g_draw.line([(0, curr_y), (1080, curr_y)], fill=(15, 23, 42, alpha))

        canvas = Image.alpha_composite(canvas.convert("RGBA"), gradient_layer).convert("RGB")
        draw = ImageDraw.Draw(canvas)

        # C. 타이포그래피 (헤드 46px / 서브 27px / 배지 22px)
        font_head = _load_font(46, bold=True, lang=lang)
        font_sub = _load_font(27, bold=False, lang=lang)
        font_badge = _load_font(22, bold=True, lang=lang)

        badge_text = card_data.get("badge", f"STEP {s_idx}")
        title_text = card_data.get("title", f"Step {s_idx} Title")
        subtitle_text = card_data.get("subtitle", "")
        bullets = card_data.get("bullets", [])

        TEXT_X = 60
        MAX_W = 960
        CTA_TOP = 1185

        # 상단 페이지 인덱스 배지 (우측)
        page_badge = f"{s_idx:02d} / 05 >"
        draw.text((930, 916), page_badge, fill=(255, 160, 0), font=font_badge)

        # 좌측 플로팅 배지 (글자 실측 기반 100% 자동 반응형 라운드 사각형)
        b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
        text_w = b_bbox[2] - b_bbox[0]
        pad_x = 16
        max_safe_w = 850 - TEXT_X
        badge_w = min(max_safe_w, max(140, text_w + pad_x * 2))
        
        # 케이마켓 브랜드 포인트 배지 컬러: 비비드 오렌지 (249, 115, 22)
        draw.rounded_rectangle([(TEXT_X, 910), (TEXT_X + badge_w, 956)], radius=8, fill=(249, 115, 22))
        draw.text((TEXT_X + pad_x, 918), badge_text, fill=(255, 255, 255), font=font_badge)

        # 글자 레이아웃 시작 y
        cur_y = 968

        # 헤드라인 (골드/옐로우 + 아웃라인 섀도우)
        cur_y = _draw_text_wrapped(
            draw, title_text, font_head,
            x=TEXT_X, y=cur_y, max_width=MAX_W,
            fill=(255, 215, 0), shadow_fill=(0, 0, 0), line_gap=5
        )
        cur_y += 10

        # 서브카피 (라이트 그레이)
        cur_y = _draw_text_wrapped(
            draw, subtitle_text, font_sub,
            x=TEXT_X, y=cur_y, max_width=MAX_W,
            fill=(225, 230, 240), shadow_fill=(0, 0, 0), line_gap=5
        )
        cur_y += 10

        # 3줄 불릿 (라이트 블루/아이보리)
        for bullet_line in bullets[:3]:
            if not bullet_line or cur_y + 36 > CTA_TOP:
                break
            cur_y = _draw_text_wrapped(
                draw, bullet_line, font_sub,
                x=TEXT_X, y=cur_y, max_width=MAX_W,
                fill=(200, 225, 255), shadow_fill=(0, 0, 0), line_gap=4
            )
            cur_y += 6

        # D. 8개국어 맞춤형 K-Market CTA 버튼 텍스트
        cta_i18n = {
            "uz": {
                "cta": "0 so'mlik bepul buyumlarni ko'rish  >",
                "next": "Keyingi qismni ko'rish  >"
            },
            "vi": {
                "cta": "Nhận đồ miễn phí 0đ ngay  >",
                "next": "Xem tiếp nội dung tiếp theo  >"
            },
            "mn": {
                "cta": "0 воны үнэгүй бараа шалгах  >",
                "next": "Дараагийн хэсгийг үзэх  >"
            },
            "th": {
                "cta": "ดูของแจกฟรี 0 วอนทันที  >",
                "next": "ดูเนื้อหาถัดไป  >"
            },
            "km": {
                "cta": "ពិនិត្យមើលរបស់ឥតគិតថ្លៃ 0 វ៉ុន  >",
                "next": "មើលផ្នែកបន្ទាប់  >"
            },
            "ne": {
                "cta": "० वनका निःशुल्क सामान हेर्नुहोस्  >",
                "next": "अर्को भाग हेर्नुहोस्  >"
            },
            "id": {
                "cta": "Cek barang gratis 0 won sekarang  >",
                "next": "Lihat bagian selanjutnya  >"
            },
            "my": {
                "cta": "၀ ဝမ် အခမဲ့ပစ္စည်းများ ကြည့်ရန်  >",
                "next": "နောက်တစ်ပိုင်းကို ကြည့်ပါ  >"
            },
            "ru": {
                "cta": "Смотреть бесплатные вещи (0 вон)  >",
                "next": "Смотреть дальше  >"
            },
            "ko": {
                "cta": "0원 무료 나눔 물품 확인하기  >",
                "next": "다음 내용 확인하기  >"
            },
            "en": {
                "cta": "Check 0-won free items now  >",
                "next": "See the next slide  >"
            }
        }
        btn_dict = cta_i18n.get(lang, cta_i18n["en"])
        btn_text = btn_dict["cta"] if s_idx in [1, 5] else btn_dict["next"]

        # 케이마켓 1, 5번 CTA: 비비드 네온 오렌지, 2~4번: 다크 슬레이트
        btn_bg = (235, 87, 34) if s_idx in [1, 5] else (30, 41, 59)
        btn_fg = (255, 255, 255)

        draw.rounded_rectangle([(60, 1190), (1020, 1285)], radius=20, fill=btn_bg)
        bbox_cta = draw.textbbox((0, 0), btn_text, font=font_head)
        tw_cta = bbox_cta[2] - bbox_cta[0]
        draw.text(((1080 - tw_cta) // 2, 1214), btn_text, fill=btn_fg, font=font_head)

        return canvas

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        theme_title: str,
        cards: List[Dict[str, Any]]
    ):
        """K-Market 4대 SNS 채널별 포스팅 가이드 텍스트 저장 (현지어 원문 + 한국어 해설 2단 병기)"""
        try:
            content = SNSGuideGenerator.generate_kmarket_guide_content(
                lang=lang,
                theme_title=theme_title,
                cards=cards
            )
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"📄 [{lang.upper()}] K-Market 2단 SNS 가이드 저장 완료: {file_path.name}")
        except Exception as e:
            logger.warning(f"K-Market SNS 가이드 작성 에러: {e}")
