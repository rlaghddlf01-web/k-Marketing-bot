# -*- coding: utf-8 -*-
"""
KMarketShortsProducer - 🛒 [케이마켓(중고거래/나눔) 전용 AI 숏폼 영상 생산 엔진]
- 60대 소형 가전/가구 실거래 테마 연동 (에어프라이어, 전기밥솥, 전자레인지 등)
- 타겟 8개국 (베트남, 캄보디아, 인도네시아, 카자흐스탄, 필리핀, 우즈베키스탄, 미얀마, 태국)
- [1단계] Wan 2.1 T2I 마스터 인물 컷 생성 (스마트폰을 들고 있는 현지인 주인공)
- [2단계] 케이마켓 앱 UI / 거래 화면 렌더링 및 PhoneScreenEmbedder 액정 정밀 매립
- [3단계] 8개국 맞춤형 중고거래/나눔 득템 후기 음성 합성 (Edge-TTS) & Wan 2.2 S2V 립싱크 모션 생성
- [4단계] 1080x1920 세로 풀HD 업스케일링 + 마케팅 뱃지(무료 나눔, 직거래 0원) + 엔딩 CTA 결합 완성본 출력
- 산출물 경로: C:/Users/zkfnt/Desktop/숏폼_산출물/케이마켓
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .base_shorts_producer import BaseShortsProducer
from brands.kmarket.ui_templates.remittance_template import RemittanceTemplate
from core.scenario_director_shorts_kmarket import ScenarioDirectorShortsKMarket
from core.gemini_shorts_copywriter import GeminiShortsCopywriter

logger = logging.getLogger("KMarketShortsProducer")


class KMarketShortsProducer(BaseShortsProducer):
    """케이마켓 중고거래 및 나눔 숏폼 자동 생산 엔진"""

    # 8개국 국가별 페르소나 및 카피 정의
    COUNTRY_CONFIG = {
        "vi": {
            "name": "Vietnam",
            "gender": "female",
            "char_desc": "a lovely 24-year-old Vietnamese young woman, calm friendly face, sleek dark hair, neat modern casual navy blue top",
            "bg_desc": "cozy modern Seoul studio apartment, soft warm ambient window light, wooden shelves",
            "default_theme": 30, # 에어프라이어
        },
        "km": {
            "name": "Cambodia",
            "gender": "male",
            "char_desc": "a handsome 26-year-old Cambodian young man, warm bright eyes, clean-shaven smooth skin, strictly no beard, no mustache, neat modern haircut, casual dark grey shirt",
            "bg_desc": "clean modern Seoul studio room, neat study desk, soft warm room light",
            "default_theme": 30,
        },
        "id": {
            "name": "Indonesia",
            "gender": "male",
            "char_desc": "a friendly 25-year-old Indonesian young man, neat black hair, clean-shaven, calm composed face, casual charcoal polo shirt",
            "bg_desc": "modern warm living room, wooden shelves, soft warm ambient light",
            "default_theme": 30,
        },
        "kk": {
            "name": "Kazakhstan",
            "gender": "male",
            "char_desc": "a handsome 27-year-old Kazakh young man, Central Asian features, calm confident expression, short black hair, modern dark olive bomber",
            "bg_desc": "modern clean apartment living room, warm indoor lamp light",
            "default_theme": 30,
        },
        "tl": {
            "name": "Philippines",
            "gender": "female",
            "char_desc": "a pleasant 25-year-old Filipina young woman, calm pleasant expression, clean tied hair, casual dark striped t-shirt",
            "bg_desc": "bright cozy apartment interior, soft warm ambient lighting",
            "default_theme": 30,
        },
        "uz": {
            "name": "Uzbekistan",
            "gender": "male",
            "char_desc": "a handsome 26-year-old Uzbek young man, clean-shaven, calm pleasant face, neat dark hair, casual navy blue knit",
            "bg_desc": "comfortable modern studio apartment, cozy warm lighting",
            "default_theme": 30,
        },
        "my": {
            "name": "Myanmar",
            "gender": "male",
            "char_desc": "a polite 25-year-old Myanmar young man, kind composed face, clean-shaven smooth skin, neat hairstyle, casual dark green shirt",
            "bg_desc": "clean bright apartment room, soft warm indoor lighting",
            "default_theme": 30,
        },
        "th": {
            "name": "Thailand",
            "gender": "male",
            "char_desc": "a cheerful 26-year-old Thai young man, calm pleasant expression, clean-shaven, modern short haircut, casual dark grey t-shirt",
            "bg_desc": "modern warm living space, tidy bookshelf, pleasant warm atmosphere",
            "default_theme": 30,
        },
        "ne": {
            "name": "Nepal",
            "gender": "male",
            "char_desc": "a warm 26-year-old Nepalese young man, friendly calm face, clean-shaven, neat dark hair, casual comfortable navy blue sweater",
            "bg_desc": "clean sunny apartment living room, neat bookshelf, warm indoor lighting",
            "default_theme": 30,
        },
        "mn": {
            "name": "Mongolia",
            "gender": "male",
            "char_desc": "a strong 27-year-old Mongolian young man, healthy sun-bronzed look, clean-shaven, modern short haircut, casual charcoal hoodie",
            "bg_desc": "cozy modern Seoul studio apartment, soft warm ambient window light",
            "default_theme": 30,
        },
    }

    def __init__(self):
        super().__init__(brand_name="케이마켓")
        self.scenario_director = ScenarioDirectorShortsKMarket()
        self.ui_template = RemittanceTemplate()
        self.copywriter = GeminiShortsCopywriter(service_id="kmarket")

    def get_character_prompt(self, lang: str, **kwargs) -> Dict[str, str]:
        """Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (8개국 고유 골격 + iPhone 실사 질감 + 한 손 그립 + 닫힌 입술)"""
        from core.character_phenotype_definitions import get_character_phenotype, get_negative_phenotype
        cfg = self.COUNTRY_CONFIG.get(lang, self.COUNTRY_CONFIG["vi"])
        ethnic_desc = get_character_phenotype(lang)
        ethnic_neg = get_negative_phenotype(lang)
        char_desc = cfg["char_desc"]
        bg_desc = cfg["bg_desc"]

        positive = (
            f"candid authentic vertical iPhone mobile photo taken by a friend, {ethnic_desc}, {char_desc}, "
            f"sitting comfortably in {bg_desc}, "
            f"holding a sleek modern smartphone naturally in one hand at chest level, showing the vertical black display screen directly facing forward to camera, "
            f"relaxed comfortable one-handed grip, the other arm resting naturally and still, "
            f"calm neutral resting face, lips completely closed together, mouth gently shut, strictly no smile, no teeth showing, "
            f"looking directly into the camera lens with sincere trustworthy friendly eye contact, "
            f"warm muted everyday indoor room lighting, natural realistic skin tones, subtle real skin texture with pores, "
            f"natural soft ambient shadows, grounded realistic contrast, sharp crisp focus, authentic mobile phone capture"
        )

        negative = (
            f"{ethnic_neg}, "
            "overexposed, blown out highlights, washed out, harsh white lighting, excessive brightness, pale bleached skin, "
            "beauty filter, airbrushed, porcelain skin, plastic skin, glamour lighting, studio flash, "
            "smiling, laughing, grinning, toothy smile, open mouth, parted lips, visible teeth, teeth, "
            "holding phone with two hands, phone to ear, making phone call, talking on phone, phone obscuring face, "
            "back of phone, silver phone back, rear camera, phone case back, deformed hands, extra fingers, claw fingers, "
            "cartoon, 3d render, anime, illustration, blurry, low quality"
        )

        return {"positive": positive, "negative": negative}

    def render_ui_image(self, lang: str, theme_title: str = "Air Fryer 5L", **kwargs) -> Image.Image:
        """케이마켓 앱 거래 화면 렌더링"""
        return self.ui_template.render(title=f"K-MARKET {theme_title}", amount=0)

    def get_speech_script(self, lang: str, scenario: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """다국어 나레이션 스크립트 (제미나이 100% 실시간 생성)"""
        script_data = self.copywriter.generate_shorts_script(
            service_id="kmarket",
            lang=lang,
            scenario=scenario or {"theme_name": "K-Market 0 Won Giveaway"}
        )
        return script_data.get("hook_0_10s", "K-Market 0 Won Free Giveaway")

    def produce(
        self,
        lang: str = "vi",
        theme_index: Optional[int] = None,
        custom_hero_image: Optional[Image.Image] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """케이마켓 1080p 상용급 숏폼 동영상 1회 완제 생산"""
        cfg = self.COUNTRY_CONFIG.get(lang, self.COUNTRY_CONFIG["vi"])
        country_name = cfg["name"]
        effective_theme = theme_index if theme_index is not None else cfg["default_theme"]

        # 테마 메타데이터 로드
        scenario = self.scenario_director.get_shorts_scenario(lang=lang, theme_index=effective_theme)
        theme_title = scenario.get("theme_name", "Air Fryer 5L")

        # 🤖 제미나이 AI 실시간 22초 숏폼 대본/배지/CTA 창작
        script_data = self.copywriter.generate_shorts_script(
            service_id="kmarket",
            lang=lang,
            scenario=scenario
        )
        speech_text = script_data.get("hook_0_10s") or "K-Market 0 Won Free Giveaway"
        badge_p = script_data.get("badge_primary") or "0 WON FREE"
        badge_s = script_data.get("badge_secondary") or "Direct Pickup"
        cta_t = script_data.get("cta_button_text") or "DOWNLOAD APP >"

        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"케이마켓_{country_name}_{theme_title}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [케이마켓 숏폼] 생산 시작: {country_name} ({lang.upper()}) | 테마: {theme_title}")

        # 1. ComfyUI 엔진 확인
        self.ensure_engine_ready()

        # 2. [Step 1 & Step 2] 케이마켓 카드뉴스 1번 슬라이드 생성 및 액정 매립 코드 100% 그대로 실행
        if custom_hero_image is not None:
            embedded_img = custom_hero_image
            logger.info("🌟 [Step 1] 전달받은 마스터 인물 사진 사용")
        else:
            # 🎯 [100% 숏폼 독자 프롬프트] 카드뉴스 의존성 완전 분리: 1인칭 한 손 그립 + 립싱크용 닫힌 입술 적용
            t2i_prompt = self.get_character_prompt(lang=lang, theme_title=theme_title)
            pos_prompt = t2i_prompt["positive"]
            neg_prompt = t2i_prompt["negative"]

            logger.info(f"🎨 [Step 1] 자연스러운 숏폼 UGC 씬 사진 생성 (한 손 그립, 입술 닫힘, seed={seed})")
            gen_path = self.wan_client.generate_t2i_master(
                positive_prompt=pos_prompt,
                negative_prompt=neg_prompt,
                width=832,
                height=1216,
                seed=seed,
                prefix=f"shorts_kmarket_ugc_{lang}"
            )
            master_img = Image.open(gen_path)
            master_save_path = out_folder / f"01_master_t2i_{lang}.png"
            master_img.save(str(master_save_path))

            # C. 스마트폰 실제 액정 매립 (엄격 품질 게이트: 물리 액정 직접 검출 실패 시 즉시 작업 중단)
            logger.info("📱 [Step 2] 스마트폰 정면 액정 화면 검출 및 거래 UI 정밀 매립...")
            ui_img = self.render_ui_image(lang=lang, theme_title=theme_title)
            ui_save_path = out_folder / f"02_app_ui_{lang}.png"
            ui_img.save(str(ui_save_path))

            try:
                embedded_img = self.embedder.embed_screen(base_image=master_img, ui_image=ui_img)
                logger.info("✅ [Step 2] 스마트폰 액정 정밀 매립 100% 성공! (영상 시작 프레임 무결성 통과)")
            except Exception as e:
                err_msg = (
                    f"❌ [품질 게이트 탈락] 스마트폰 정면 액정 화면 검출 실패 ({e}). "
                    "숏폼 영상에서 3D 플로팅 합성을 사용할 경우 AI가 공중에 뜬 스마트폰을 왜곡/변형시키므로, "
                    "불량 영상 렌더링 및 자동 업로드를 원천 방지하기 위해 작업을 안전하게 즉시 중단합니다."
                )
                logger.error(err_msg)
                raise ValueError(err_msg)

        embedded_save_path = out_folder / f"03_embedded_start_frame_{lang}.png"
        embedded_img.save(str(embedded_save_path))

        # 4. [Step 3] 다국어 TTS 음성 합성 & Wan 2.2 S2V 립싱크 렌더링
        logger.info("🎙️ [Step 3] Edge-TTS 다국어 음성 생성...")
        wav_path = self.tts.generate_speech_wav(
            text=speech_text,
            lang=lang,
            gender=cfg.get("gender", "male"),
            rate="+0%",  # 🎯 차분하고 편안한 보통 대화 속도 (수다쟁이 입 파닥거림 원천 차단)
            filename_prefix=f"kmarket_audio_{lang}"
        )
        audio_name = os.path.basename(wav_path)

        # S2V 최적 프레이밍 (480x832) 저장
        framed_img = self.prepare_framed_input_image(embedded_img, target_w=480, target_h=832)
        comfy_input_name = f"kmarket_s2v_input_{lang}_{dt_str}.png"
        comfy_input_path = os.path.join(self.wan_client.comfy_input_dir, comfy_input_name)
        framed_img.save(comfy_input_path)

        raw_video_path = str(out_folder / f"temp_raw_s2v_{lang}.mp4")
        logger.info("🎬 [Step 3] Wan 2.2 S2V 립싱크 비디오 렌더링 시작...")
        self.wan_client.generate_s2v_video(
            image_name=comfy_input_name,
            audio_name=audio_name,
            prompt_text=f"a cheerful friendly person holding smartphone, talking enthusiastically to camera with natural gentle smile, clear lip sync, stable hands",
            output_mp4_path=raw_video_path,
            prefix=f"kmarket_s2v_{lang}"
        )

        # 5. [Step 4] 1080x1920 세로 풀HD 업스케일 & 마케팅 오버레이 결합
        final_mp4_name = f"케이마켓_숏폼_{country_name}_{theme_title}_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)

        logger.info("✨ [Step 4] 1080p 세로 풀HD 컴포징 및 마케팅 뱃지 결합...")
        self.composer.finalize_1080p_shorts(
            raw_video_path=raw_video_path,
            output_mp4_path=final_mp4_path,
            badge_text_primary=badge_p,
            badge_text_secondary=badge_s,
            cta_text=cta_t,
            lang=lang
        )

        # 6. [Step 5] 4대 숏폼 SNS 포스팅 가이드 파일 생성 및 저장
        guide_filename = f"SNS_포스팅_가이드_{lang.upper()}.txt"
        guide_path = out_folder / guide_filename
        self._write_sns_guide(
            file_path=guide_path,
            lang=lang,
            country_name=country_name,
            theme_title=theme_title,
            speech=speech_text,
            cfg=cfg,
            scenario=scenario
        )
        logger.info(f"📝 [SNS 가이드] 숏폼 배포 패키지 가이드 저장 완료: {guide_filename}")

        # 임시 원본 비디오 정리
        if os.path.exists(raw_video_path):
            try:
                os.remove(raw_video_path)
            except Exception:
                pass

        logger.info(f"🎉 [케이마켓 숏폼 완성] 최종 산출물: {final_mp4_path}")
        
        # 🧹 [1개국 K-Market 숏폼 완성 즉각 VRAM 캐시 방출]
        try:
            from core.engine.gpu_memory_flusher import GPUMemoryFlusher
            GPUMemoryFlusher.flush_gpu_vram(unload_models=False)
        except Exception:
            pass

        return {
            "output_mp4": final_mp4_path,
            "folder_path": str(out_folder),
            "guide_path": str(guide_path),
            "country": country_name,
            "lang": lang,
            "theme_title": theme_title,
            "speech": speech_text
        }

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        country_name: str,
        theme_title: str,
        speech: str,
        cfg: Dict[str, Any],
        scenario: Optional[Dict[str, Any]] = None
    ):
        """인스타그램 릴스, 틱톡, 유튜브 쇼츠, 페이스북 릴스 전용 다국어 배포 가이드 작성 (제미나이 100% 동적 생성)"""
        # 🤖 제미나이 AI 4대 숏폼 플랫폼 맞춤 팩 생성
        scen = scenario or {"theme_name": theme_title, "item": theme_title}
        sns_pack = self.copywriter.generate_shorts_post_package(
            service_id="kmarket",
            lang=lang,
            scenario=scen
        )
        content = self.copywriter.format_guide_text(sns_pack)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
