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
from PIL import Image

from core.scenario_director_cardnews_kmarket import ScenarioDirectorCardnewsKMarket
from core.engine.wan_pipeline_client import WanPipelineClient
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter
from core.engine.kmarket_cardnews_app_capturer import KMarketCardNewsAppCapturer
from core.cardnews_typography_kmarket import CardnewsTypographyKMarket

logger = logging.getLogger("CardNewsBatchProducerKMarket")


class CardNewsBatchProducerKMarket:
    """K-Market 5장 풀사이즈 카드뉴스 & 4대 SNS 배포 팩 일괄 생산기"""

    def __init__(self):
        self.scenario_director = ScenarioDirectorCardnewsKMarket()
        self.wan_client = WanPipelineClient()
        self.app_capturer = KMarketCardNewsAppCapturer()
        self.typography_engine = CardnewsTypographyKMarket()
        self.copywriter = GeminiCardnewsCopywriter(service_id="kmarket")
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

        item_name = scenario.get("item", "3단 서랍장")
        target_area = scenario.get("target", "신촌")

        slide1_base_photo: Optional[Image.Image] = None

        for card in sorted(cards, key=lambda c: c.get("slide_idx", 1)):
            s_idx = card.get("slide_idx", 1)

            # 🛑 [비상 정지 킬스위치 감시] 대시보드 정지 요청 시 즉각 루프 올스톱(Abort)
            from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException
            if GenerationAbortGuard.is_abort_requested():
                logger.warning(f"🛑 [K-Market Slide {s_idx}] 대시보드 정지 요청 감지 → 전체 루프 즉각 탈출(Abort)!")
                raise GenerationAbortedException("대시보드 정지 요청으로 K-Market 카드뉴스 생성이 즉각 중단되었습니다.")

            # 🌟 [3번 슬라이드] 실제 케이마켓 0원 무료나눔 매물 피드 앱 화면 캡처
            if s_idx == 3:
                logger.info(f"📱 [Slide 3] 실제 케이마켓 0원 매물 피드 고화질 캡처 적용! ({item_name})")
                base_photo = self.app_capturer.capture_giveaway_feed(
                    lang=lang,
                    item_name=item_name,
                    dynamic_title=card.get("title")
                )

            # 🌟 [4번 슬라이드] 실제 0원 매물 상세 & 17개 언어 실시간 직거래 순정 모바일 화면 (팝업 0% 전체 뷰)
            elif s_idx == 4:
                logger.info(f"💬 [Slide 4] 실제 0원 매물 상세 순정 화면 고화질 캡처 적용! ({item_name}, {target_area})")
                base_photo = self.app_capturer.capture_item_detail_view(
                    lang=lang,
                    item_name=item_name,
                    target_area=target_area,
                    dynamic_title=card.get("title"),
                    dynamic_desc=card.get("subtitle")
                )

            # 🌟 [1, 2, 5번 슬라이드] 배경·가구 중심 WAN T2I 실사 라이프스타일 사진 생성 (1~5번 전 슬라이드 동일 인물 마스터 시드 100% 동기화)
            elif s_idx == 1 and custom_hero_image is not None:
                base_photo = custom_hero_image
                logger.info("🌟 [Slide 1] 검증 승인된 마스터 주인공 인물 사진(custom_hero_image) 직접 적용!")
            else:
                slide_seed = master_seed
                base_photo = self._generate_slide_photo(
                    s_idx=s_idx,
                    card_data=card,
                    fallback_img=fallback_img,
                    master_seed=slide_seed
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
            cards=cards,
            item_name=item_name,
            target_area=target_area,
            scenario=scenario
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
        from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException
        if GenerationAbortGuard.is_abort_requested():
            raise GenerationAbortedException(f"[Slide {s_idx}] 대시보드 정지 요청으로 생성을 취소합니다.")

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
            if isinstance(e, GenerationAbortedException) or GenerationAbortGuard.is_abort_requested():
                logger.warning(f"🛑 [Slide {s_idx}] 대시보드 정지 감지 → Fallback 무시 및 루프 즉각 올스톱!")
                raise
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
        K-Market 전용 Playwright HarfBuzz 타이포그래피 합성:
        - Slide 1, 2, 5: 순수 라이프스타일 실사 사진 + 하단 그라디언트 스크림 + 카테고리 배지 + 골드 헤드라인 + 서브 + 3줄 불릿 + 동적 CTA
        - Slide 3, 4: 실제 0원 무료나눔 매물 피드 및 1:1 번역 직거래 순정 앱 화면 + 상단 슬림 글래스모피즘 헤더
        - 제미나이 100% 실시간 card_data + Playwright HarfBuzz 무결점 텍스트 셰이핑 적용
        """
        return self.typography_engine.composite_slide(
            base_photo=base_photo,
            card_data=card_data,
            s_idx=s_idx,
            lang=lang
        )

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        theme_title: str,
        cards: List[Dict[str, Any]],
        item_name: str = "가구/가전",
        target_area: str = "신촌",
        scenario: Optional[Dict[str, Any]] = None
    ):
        """K-Market 4대 SNS 채널별 포스팅 가이드 텍스트 저장 (제미나이 100% 실시간 2단 창작)"""
        try:
            package = self.copywriter.generate_cardnews_post_package(
                service_id="kmarket",
                lang=lang,
                theme={"name": theme_title, "item": item_name, "target": target_area},
                persona=scenario.get("character_anchor", {}) if scenario else {},
                cards=cards
            )
            content = self.copywriter.format_guide_text(package)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"📄 [{lang.upper()}] K-Market 2단 SNS 가이드 저장 완료: {file_path.name}")
        except Exception as e:
            logger.warning(f"K-Market SNS 가이드 작성 에러: {e}")
