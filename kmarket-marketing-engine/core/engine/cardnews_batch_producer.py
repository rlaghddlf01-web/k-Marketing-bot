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
from PIL import Image

from core.scenario_director_cardnews_easytax import ScenarioDirectorCardnewsEasyTax
from core.screen_inset_compositor import ScreenInsetCompositor
from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.engine.wan_pipeline_client import WanPipelineClient
from core.easytax_app_capturer import EasyTaxAppCapturer
from brands.easytax.ui_templates.refund_receipt_template import RefundReceiptTemplate
from brands.easytax.scenarios.prompt_director_cardnews import PromptDirectorCardNewsEasyTax
from core.gemini_cardnews_copywriter import GeminiCardnewsCopywriter
from core.cardnews_typography_easytax import CardnewsTypographyEasyTax

logger = logging.getLogger("CardNewsBatchProducer")


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
        self.typography_engine = CardnewsTypographyEasyTax()
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
        master_seed: Optional[int] = None,
        abort_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """5장 카드뉴스 세트 및 SNS 가이드 일괄 생산"""
        # 1. 시나리오 기획 로드 (60대 테마 및 단일 환급액 100% 동기화)
        scenario = self.scenario_director.get_carousel_scenario(
            lang=lang,
            theme_index=theme_index,
            preferred_gender=preferred_gender,
            amount=amount
        )
        theme_id = scenario.get("theme_name", "general")
        theme_title = scenario.get("theme_title", "EasyTax Tax Refund")
        cards = scenario.get("cards", [])

        # 🎯 [금액 100% 원천 일치] 테마와 카피라이팅에 확정된 단일 환급액 추출
        effective_amount = scenario.get("refund_est", amount)
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

            # 🛑 [비상 정지 킬스위치 감시] 대시보드 정지 요청 시 즉각 루프 올스톱(Abort)
            from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException
            if GenerationAbortGuard.is_abort_requested(scope=abort_scope):
                logger.warning(f"🛑 [EasyTax Slide {s_idx}] 정지 요청({abort_scope or '전역'}) 감지 → 전체 루프 즉각 탈출(Abort)!")
                raise GenerationAbortedException("정지 요청으로 EasyTax 카드뉴스 생성이 즉각 중단되었습니다.")

            if s_idx == 1 and custom_hero_image is not None:
                base_photo = custom_hero_image
                logger.info("🌟 [Slide 1] 검증 승인된 마스터 주인공 인물 사진(custom_hero_image) 직접 적용!")
            else:
                base_photo = self._generate_slide_photo(
                    s_idx=s_idx,
                    card_data=card,
                    fallback_img=fallback_img,
                    master_seed=master_seed,
                    abort_scope=abort_scope
                )
                # ⏸️ [GPU 안전 가드레일: 슬라이드 간 쿨다운 & 화면 렌더링 양보]
                from core.engine.gpu_memory_flusher import GPUMemoryFlusher
                GPUMemoryFlusher.yield_slide_cooldown(yield_sec=2.5)
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
            cards=cards,
            scenario=scenario
        )

        logger.info(f"🎉 [EasyTax 5장 카드뉴스 세트 완성] 폴더: {out_dir}")
        
        # 🧹 [1개국 5장 세트 완료 즉각 VRAM 캐시 방출]
        try:
            from core.engine.gpu_memory_flusher import GPUMemoryFlusher
            GPUMemoryFlusher.flush_gpu_vram(unload_models=False)
        except Exception:
            pass

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
        master_seed: int = 2026,
        abort_scope: Optional[str] = None
    ) -> Image.Image:
        """
        슬라이드별 씬 사진을 WAN T2I로 독립 생성 (동일 캐릭터 앵커 + 동일 마스터 시드):
        - Slide 1~5: 전 슬라이드 독립 T2I (generate_t2i_master, seed=master_seed)
        - 60% 황금비율 미디엄 샷 적용 + 씬별 100% 다른 의상/배경/포즈 연출
        """
        from core.engine.generation_abort_guard import GenerationAbortGuard, GenerationAbortedException
        if GenerationAbortGuard.is_abort_requested(scope=abort_scope):
            raise GenerationAbortedException(f"[Slide {s_idx}] 정지 요청({abort_scope or '전역'})으로 생성을 취소합니다.")

        if not self._wan_available:
            logger.info(f"[Slide {s_idx}] ComfyUI 미실행 → 마스터 베이스 사진 적용")
            return fallback_img

        positive_prompt = card_data.get("image_prompt", "")
        negative_prompt = card_data.get("negative_prompt", None)

        if not positive_prompt:
            logger.warning(f"[Slide {s_idx}] image_prompt 없음 → 마스터 베이스 사진 적용")
            return fallback_img

        width, height = 832, 1216
        prefix = f"cardnews_easytax_slide{s_idx}_{int(time.time())}"

        try:
            # 🎯 [전 슬라이드 독립 T2I + 마스터 시드 동기화]
            # - 프롬프트 최전방(Token 0)에 100% 동일한 주인공 인물 앵커 고정
            # - 동일 캐릭터 앵커 프롬프트 + 동일 master_seed로 1~5번 전원 동일 인물 정체성 보존
            logger.info(f"🎨 [Slide {s_idx}] WAN T2I 씬 사진 생성 (seed={master_seed}) → {prefix}")
            generated_path = self.wan_client.generate_t2i_master(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=master_seed,
                prefix=prefix,
                abort_scope=abort_scope
            )

            generated_img = Image.open(generated_path).convert("RGB")
            logger.info(f"✅ [Slide {s_idx}] WAN 생성 완료: {generated_path}")
            return generated_img
        except Exception as e:
            if isinstance(e, GenerationAbortedException) or GenerationAbortGuard.is_abort_requested(scope=abort_scope):
                logger.warning(f"🛑 [Slide {s_idx}] 정지 요청 감지 → Fallback 무시 및 루프 즉각 올스톱!")
                raise
            logger.error(f"❌ [Slide {s_idx}] WAN 생성 실패 ({e}) → 1번 주인공 마스터 베이스 사진 안전 유지")
            return fallback_img

    def _render_slide(
        self,
        s_idx: int,
        card_data: Dict[str, Any],
        base_photo: Image.Image,
        lang: str,
        amount: int
    ) -> Image.Image:
        """
        EasyTax 전용 Playwright HarfBuzz 타이포그래피 합성:
        - 1, 3, 5번 인물/앱 화면 합성 (PhoneScreenEmbedder / ScreenInsetCompositor)
        - 제미나이 100% 동적 card_data(로열 네이비 & 골드 헤드라인, 부제, 3줄 불릿, CTA버튼) 오버레이 합성
        """
        # A. 슬라이드 번호에 따라 스마트폰 화면 인셋 합성 (이미 WAN으로 생성된 base_photo 사용)
        if s_idx == 1:
            ui_img = self.ui_template.render(amount=amount)
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

        return self.typography_engine.composite_slide(
            composite_photo=composite_photo,
            card_data=card_data,
            s_idx=s_idx,
            lang=lang
        )

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        theme_title: str,
        amount: int,
        cards: List[Dict[str, Any]],
        scenario: Optional[Dict[str, Any]] = None
    ):
        """스레드, 인스타그램, 페이스북, 텔레그램 4대 채널별 포스팅 가이드 텍스트 저장 (제미나이 100% 실시간 2단 세트)"""
        try:
            package = self.copywriter.generate_cardnews_post_package(
                service_id="easytax",
                lang=lang,
                theme={"name": theme_title},
                persona=scenario.get("character_anchor", {}) if scenario else {},
                cards=cards,
                refund_formatted=f"{amount:,} KRW"
            )
            content = self.copywriter.format_guide_text(package)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"📄 [{lang.upper()}] 다국어 2단 SNS 가이드(현지어+한국어) 저장 완료: {file_path.name}")
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

