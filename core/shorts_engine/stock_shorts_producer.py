# -*- coding: utf-8 -*-
"""
StockShortsProducer - 📈 [StockMaster AI 전용 AI 숏폼 영상 생산 엔진]
====================================================================
- Wan 2.1 T2I + Wan 2.2 S2V 10초 원테이크 + 웹앱 시뮬 12초 + CTA 1초 아키텍처 100% 동일 계승
- [1단계] Wan 2.1 T2I 마스터 인물 컷 생성 (2040 스마트 투자자 페르소나, 세련된 한국형 스마트 캐주얼)
- [2단계] 객관적 퀀트 전광판 & 수급/밸류에이션/리스크 가드 웹앱 실시간 시연 (12.0초)
- [3단계] 맞춤형 스피치 음성 합성 (Google Gemini 2.5 Flash TTS Aoede) & Wan 2.2 S2V 10초 원테이크 립싱크 (5s+5s xfade)
- [4단계] 1080x1920 세로 풀HD 업스케일링 + 공식 네이버 검색 CTA ['스톡마스터 AI'] 결합 (심의 100% 프리패스 클린 뷰)
- 산출물 경로: C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Stock
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .base_shorts_producer import BaseShortsProducer
from .stock_app_recorder import StockAppRecorder
from brands.stock.ui_templates.stock_cta_card import StockCTACard
from .stock_shorts_scenario_director import StockShortsScenarioDirector
from brands.stock.stock_shorts_script_writer import StockShortsScriptWriter
from .shorts_character_anchor_stock import build_stock_shorts_t2i_character_prompt
from .s2v_clip_stitcher import S2VClipStitcher
from brands.stock.stock_voice_cloner import StockVoiceCloner

logger = logging.getLogger("StockShortsProducer")


class StockShortsProducer(BaseShortsProducer):
    """📈 StockMaster AI 숏폼 자동 생산 엔진 (알리바바 CosyVoice 진우 보이스 + Wan 2.1/2.2 + 실물 웹앱 녹화)"""

    def __init__(self, use_voice_cloner: bool = True):
        super().__init__("Stock")
        # 산출물 절대 경로: 바탕화면/한국 숏폼_산출물/Stock
        self.output_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")
        self.output_base.mkdir(parents=True, exist_ok=True)

        self.app_simulator = StockAppRecorder()
        self.cta_card = StockCTACard()
        self.script_director = StockShortsScenarioDirector()
        self.script_writer = StockShortsScriptWriter()
        
        # 🎙️ 알리바바 CosyVoice 진우(Jinwoo) 보이스 복제기 (1순위 알리바바 -> 2순위 Typecast -> 3순위 Edge-TTS)
        self.voice_cloner = StockVoiceCloner(output_dir=str(self.output_base))
        self.tts = self.voice_cloner

        self.stitcher = S2VClipStitcher(
            wan_client=self.wan_client,
            tts_synthesizer=self.tts,
            ffmpeg_exe=self.composer.ffmpeg_exe
        )

    def get_character_prompt(
        self,
        topic_id: int = 1,
        custom_char_desc: Optional[str] = None,
        custom_bg_desc: Optional[str] = None,
        gender: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """주식 8대 주제 전용 T2I 캐릭터 및 배경 프롬프트 생성"""
        return build_stock_shorts_t2i_character_prompt(
            topic_id=topic_id,
            custom_char_desc=custom_char_desc,
            custom_bg_desc=custom_bg_desc,
            gender=gender
        )

    def render_ui_image(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> Image.Image:
        """주식 퀀트 화면 렌더링"""
        return Image.new("RGB", (1080, 1920), (15, 23, 42))

    def get_speech_script(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> str:
        """주식 맞춤형 나레이션 스크립트 반환"""
        scenario = self.script_director.get_full_scenario(topic_id=topic_id)
        return scenario["full_speech"]

    # 🔒 [주제 순환 모드 (None: 1~8번 자율 순환 / 숫자 지정 시 특정 주제 고정)]
    FIXED_TOPIC_ID: Optional[int] = None

    def _get_next_topic_id(self) -> int:
        """1번부터 8번까지 주제를 자율 순환(Rotation)하며 상태 파일에 영구 기록"""
        if self.FIXED_TOPIC_ID is not None:
            logger.info(f"🔒 [주식 숏폼] 주제 #{self.FIXED_TOPIC_ID} 고정 생산 모드 가동 중")
            return self.FIXED_TOPIC_ID

        state_file = self.output_base / "stock_shorts_state.json"
        last_id = 0
        if state_file.exists():
            try:
                import json
                data = json.loads(state_file.read_text(encoding="utf-8"))
                last_id = data.get("last_topic_id", 0)
            except Exception:
                pass
        next_id = (last_id % 8) + 1
        try:
            import json
            state_file.write_text(json.dumps({"last_topic_id": next_id}, indent=2), encoding="utf-8")
        except Exception:
            pass
        return next_id

    def produce_master_photo(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        r"""
        주식 8대 주제별 Wan 2.1 실사 마스터 사진 단독 생산 파이프라인
        - 832x1216 해상도 Wan 2.1 14B Q4_0 T2I 마스터컷 렌더링
        - C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\Topic_XX 폴더에 저장
        """
        import random
        if topic_id is None:
            topic_id = self._get_next_topic_id()
        if seed is None or seed <= 0:
            seed = random.randint(100000, 999999999)

        wan_ready = self.ensure_engine_ready()
        if not wan_ready:
            raise RuntimeError("ComfyUI 엔진 기동에 실패했습니다. D:\\ComfyUI_Wan_Engine 설정을 확인해주세요.")

        scenario = self.script_director.get_full_scenario(topic_id=topic_id, gender=gender)
        theme_name = scenario["theme_name"]
        theme_code = scenario["theme_code"]

        t2i_prompt = self.get_character_prompt(
            topic_id=topic_id,
            custom_char_desc=kwargs.get("custom_char_desc"),
            custom_bg_desc=kwargs.get("custom_bg_desc"),
            gender=gender
        )
        pos_prompt = t2i_prompt["positive"]
        neg_prompt = t2i_prompt["negative"]

        safe_name = theme_name.replace(":", "-").replace(" ", "").replace("/", "-")
        out_folder = self.output_base / f"Topic_{topic_id:02d}_{safe_name}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎨 [주식 마스터 사진] 주제 {topic_id} [{theme_name}] Wan 2.1 T2I 렌더링 시작 (seed={seed})")

        gen_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos_prompt,
            negative_prompt=neg_prompt,
            width=832,
            height=1216,
            seed=seed,
            prefix=f"stock_master_{topic_id}"
        )
        master_img = Image.open(gen_path)
        master_save_path = out_folder / f"master_t2i_{topic_id:02d}_seed{seed}.png"
        master_img.save(str(master_save_path))

        self.wan_client.free_vram()

        # SNS 포스팅 가이드 자동 생성
        try:
            from brands.stock.stock_sns_guide_generator import StockSNSGuideGenerator
            StockSNSGuideGenerator.save_guide_file(
                output_folder=out_folder,
                topic_id=topic_id,
                speech_hook=scenario.get("speech_hook")
            )
        except Exception as e:
            logger.warning(f"SNS 포스팅 가이드 생성 실패: {e}")

        logger.info(f"🎉 [주식 마스터 사진 완료] 파일 저장: {master_save_path}")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "theme_code": theme_code,
            "photo_path": str(master_save_path),
            "folder_path": str(out_folder),
            "image_size": f"{master_img.size[0]}x{master_img.size[1]}",
            "seed": seed
        }

    def produce(
        self,
        lang: Optional[str] = "ko",
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        custom_hero_image: Optional[Image.Image] = None,
        seed: Optional[int] = None,
        force_fresh_record: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        StockMaster AI 숏폼 풀 프로덕션:
        - topic_id 미지정 시 1~8번 자율 순환
        - seed 미지정 시 완전 무작위 난수 시드 자동 발급
        - 로고 없는 100% 클린 뷰 (심의 및 신뢰도 극대화)
        """
        import random
        if topic_id is None:
            topic_id = self._get_next_topic_id()
        if seed is None or seed <= 0:
            seed = random.randint(100000, 999999999)

        # 1. ComfyUI 엔진 상태 확인
        wan_ready = self.ensure_engine_ready()

        # 2. 시나리오 대본 준비 (제미나이 자율 최적화 대본 우선 ➔ 실패 시 골든 대본 폴백)
        scenario = self.script_director.get_full_scenario(topic_id=topic_id, gender=gender)
        theme_name = scenario["theme_name"]
        effective_gender = scenario.get("gender", gender or "male")
        voice_rate = scenario.get("voice_rate", "+4%")
        voice_pitch = scenario.get("voice_pitch", "+0Hz")

        # 🌟 Gemini 2.5 Flash 실시간 팩트 최적화 대본 생성 시도
        try:
            dynamic_script = self.script_writer.generate_dynamic_script(topic_id=topic_id)
            if dynamic_script:
                speech_hook = dynamic_script["hook_0_10s"]
                speech_hook_p1 = dynamic_script["hook_p1_5s"]
                speech_hook_p2 = dynamic_script["hook_p2_5s"]
                speech_app = dynamic_script["app_10_20s"]
                speech_cta = dynamic_script["cta_18_22s"]
                full_speech = dynamic_script["full_speech"]
                hero_copy = dynamic_script.get("hero_copy", scenario.get("hero_copy"))
                debate_q = dynamic_script.get("debate_question", scenario.get("debate_question"))
                logger.info(f"✨ [주식 숏폼] Gemini 2.5 Flash 실시간 자율 대본 적용 성공 (주제 #{topic_id})")
            else:
                speech_hook = scenario["speech_hook"]
                speech_hook_p1 = scenario.get("speech_hook_part1")
                speech_hook_p2 = scenario.get("speech_hook_part2")
                speech_app = scenario["speech_app"]
                speech_cta = scenario["speech_cta"]
                full_speech = scenario["full_speech"]
                hero_copy = scenario.get("hero_copy", "실시간 퀀트 데이터 객관적 분석!")
                debate_q = scenario.get("debate_question", "지금 시장의 진짜 주도주는?")
                logger.info(f"📋 [주식 숏폼] 검증된 골든 대본 적용 (주제 #{topic_id})")
        except Exception as e:
            logger.warning(f"대본 생성 예외 발생 -> 골든 대본 적용: {e}")
            speech_hook = scenario["speech_hook"]
            speech_hook_p1 = scenario.get("speech_hook_part1")
            speech_hook_p2 = scenario.get("speech_hook_part2")
            speech_app = scenario["speech_app"]
            speech_cta = scenario["speech_cta"]
            full_speech = scenario["full_speech"]
            hero_copy = scenario.get("hero_copy", "실시간 퀀트 데이터 객관적 분석!")
            debate_q = scenario.get("debate_question", "지금 시장의 진짜 주도주는?")

        visual_dir = scenario["visual_direction"]

        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"Stock_{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [주식 숏폼] 생산 시작: 주제 {topic_id} [{theme_name}] | 성별: {effective_gender} | seed: {seed}")

        # 3. [Step 1] Alibaba CosyVoice 음성 복제 합성 (1순위 알리바바 -> 2순위 Typecast -> 3순위 Edge-TTS)
        voice_lang = "ko"
        logger.info(f"🎙️ [Step 1] 알리바바 CosyVoice 음성 합성 진행 ({effective_gender})...")
        hook_wav_path = self.tts.generate_speech_wav(
            text=speech_hook,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"stock_hook_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        app_wav_path = self.tts.generate_speech_wav(
            text=speech_app,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"stock_app_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        cta_wav_path = self.tts.generate_speech_wav(
            text=speech_cta,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"stock_cta_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        full_wav_path = self.tts.generate_speech_wav(
            text=full_speech,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"stock_full_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )

        # 4. [Step 2] 숏폼 인물 사진 로드 또는 Wan 2.1 T2I 생성 (순수 100% 인물 마스터컷)
        if custom_hero_image is not None:
            master_img = custom_hero_image
            master_save_path = out_folder / f"01_master_t2i_{topic_id}.png"
            master_img.save(str(master_save_path))
            logger.info(f"🌟 [Step 2] 전달받은 마스터 인물 사진 사용: {master_save_path}")
        elif wan_ready:
            t2i_prompt = self.get_character_prompt(
                topic_id=topic_id,
                custom_char_desc=scenario.get("character_desc"),
                custom_bg_desc=scenario.get("background_desc"),
                gender=effective_gender
            )
            pos_prompt = t2i_prompt["positive"]
            neg_prompt = t2i_prompt["negative"]

            logger.info(f"🎨 [Step 2] Wan 2.1 T2I 인물 마스터 사진 생성 (seed={seed})")
            gen_path = self.wan_client.generate_t2i_master(
                positive_prompt=pos_prompt,
                negative_prompt=neg_prompt,
                width=832,
                height=1216,
                seed=seed,
                prefix=f"shorts_stock_{topic_id}"
            )
            master_img = Image.open(gen_path)
            master_save_path = out_folder / f"01_master_t2i_{topic_id}.png"
            master_img.save(str(master_save_path))
            self.wan_client.free_vram()
        else:
            raise RuntimeError("Wan 2.1 엔진이 준비되지 않았습니다.")

        # 5. [Step 3] Wan 2.2 S2V 립싱크 모션 렌더링 (5s+5s 원테이크 10초)
        framed_img = self.prepare_framed_input_image(master_img, target_w=384, target_h=672)
        s2v_motion_prompt = scenario.get("s2v_motion_prompt") or (
            "speaking expressively with articulate words, highly synchronized lip sync matching the spoken audio, "
            "gentle head nodding and subtle head tilts, delicate subtle hand micro-gestures, natural posture, "
            "no exaggerated hand waving, no wild arm movements, calm and trustworthy upper body posture, authentic lifelike human motion"
        )

        if wan_ready:
            logger.info("🎬 [Step 3] Wan 2.2 S2V 384x672 5초+5초 10초 원테이크 렌더링 시작 (81프레임 x 2, 0.15s xfade)...")
            person_clip_path, person_audio_path = self.stitcher.render_seamless_dual_clip(
                base_framed_img=framed_img,
                speech_hook_full=speech_hook,
                lang=voice_lang,
                gender=effective_gender,
                out_folder=out_folder,
                dt_str=dt_str,
                motion_prompt=s2v_motion_prompt,
                seed=seed,
                speech_hook_part1=speech_hook_p1,
                speech_hook_part2=speech_hook_p2,
                voice_pitch=voice_pitch,
                voice_rate=voice_rate
            )
        else:
            person_clip_path = str(out_folder / f"temp_person_clip_{dt_str}.mp4")
            cmd = [
                self.composer.ffmpeg_exe, "-y",
                "-loop", "1", "-i", str(master_save_path),
                "-t", "10.12",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
                "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                person_clip_path
            ]
            import subprocess
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            person_audio_path = hook_wav_path

        # 6. [Step 4] StockMaster AI 실제 웹앱 실시간 시연 클립 (표준 12.0초)
        app_clip_path = str(out_folder / f"04_app_sim_stock_{topic_id}.mp4")
        logger.info(f"📱 [Step 4] StockMaster AI 실제 웹앱 시연 비디오 준비 (12.00s)...")
        self.app_simulator.record_simulation_clip(
            topic_id=topic_id,
            duration_sec=12.0,
            output_mp4_path=app_clip_path,
            force_fresh_record=force_fresh_record
        )

        # 7. [Step 5] 네이버 검색 공식 4초 럭셔리 에디토리얼 CTA 비디오 준비 (표준 4.0초)
        cta_clip_path = str(out_folder / f"05_cta_debate_stock_{topic_id}.mp4")
        logger.info(f"🏷️ [Step 5] 네이버 검색 4초 공식 검색어 에디토리얼 CTA 비디오 준비 (4.00s)...")
        self.cta_card.create_cta_segment_mp4(
            output_path=cta_clip_path,
            duration_sec=4.0,
            topic_title=theme_name,
            debate_question=debate_q,
            search_keyword="스톡마스터 AI",
            hero_copy=hero_copy
        )

        # 8. [Step 6] 22초 하이브리드 완제품 컴포징 (상단 좌측 다크 네이비 캡슐 뱃지 탑재)
        final_mp4_name = f"Stock_22초숏폼_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)
        from .shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
        stock_logo_overlay = ShortsBrandCapsuleBadge.get_overlay_path("stock")

        scene_audios = {
            "hook": person_audio_path,
            "app": app_wav_path,
            "cta": cta_wav_path if (cta_wav_path and os.path.exists(cta_wav_path)) else None
        }

        logger.info("✨ [Step 6] 1080p 세로 풀HD 22초 하이브리드 비디오 최종 컴포징 (씬별 정밀 음성 동기화 + 상단 캡슐 뱃지)...")
        self.composer.compose_hybrid_22s_shorts(
            clip_person_path=person_clip_path,
            clip_app_path=app_clip_path,
            full_audio_path=full_wav_path,
            visual_direction=visual_dir,
            output_mp4_path=final_mp4_path,
            lang=voice_lang,
            scene_audios=scene_audios,
            clip_cta_path=cta_clip_path,
            logo_overlay_path=stock_logo_overlay
        )

        # 9. [순수 100% 인물 클로즈업 원테이크 1080x1920 세로 풀HD 단독 완제품 생성] (상단 캡슐 뱃지 일체형)
        pure_one_take_name = f"Stock_10초_순수인물_원테이크_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        pure_one_take_path = str(out_folder / pure_one_take_name)
        cmd_pure = [
            self.composer.ffmpeg_exe, "-y",
            "-i", person_clip_path,
            "-i", stock_logo_overlay,
            "-filter_complex", "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[bg];[bg][1:v]overlay=0:0[v_out]",
            "-map", "[v_out]",
            "-map", "0:a?",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            pure_one_take_path
        ]
        import subprocess
        subprocess.run(cmd_pure, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"✨ [순수 인물 1080p 원테이크 완료] 저장: {pure_one_take_path}")

        # 10. [SNS 포스팅 가이드 자동 생성]
        sns_guide_path = None
        try:
            from brands.stock.stock_sns_guide_generator import StockSNSGuideGenerator
            sns_guide_path = str(StockSNSGuideGenerator.save_guide_file(
                output_folder=out_folder,
                topic_id=topic_id,
                speech_hook=speech_hook
            ))
        except Exception as e:
            logger.warning(f"SNS 포스팅 가이드 생성 실패: {e}")

        logger.info(f"🎉 [주식 숏폼 생산 완료] 완제품 저장: {final_mp4_path}")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "output_mp4": final_mp4_path,
            "pure_person_mp4": pure_one_take_path,
            "sns_guide_path": sns_guide_path,
            "output_folder": str(out_folder),
            "audio_hook": hook_wav_path,
            "audio_app": app_wav_path,
            "audio_cta": cta_wav_path,
            "audio_full": full_wav_path
        }

    def produce_fullscreen_quant_shorts(
        self,
        topic_id: int = 1,
        force_fresh_record: bool = False
    ) -> Dict[str, Any]:
        """
        📊 [StockMaster AI 25초 완제품 100% 실물 퀀트 전광판 숏폼 단독 생산 파이프라인]
        - 인물 립싱크 배제 (인스타/유튜브 조회수 25배 폭증 검증)
        - [0.0s ~ 24.0s] 10분 계량 전광판 ➔ 삼성전자 모달 4개 탭 상하단 스크롤 풀뷰 (24초)
        - [24.0s ~ 25.0s] 네이버 공식 검색 CTA ['스톡마스터 AI'] 1초 세그먼트 (1초)
        - 175자 Gemini TTS 전문 금융 나레이션 음성 100% 정밀 동기화
        - 1080x1920 세로 풀HD (CRF 18, 30fps) 완제품 렌더링
        """
        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"Stock_FullScreen_Topic{topic_id:02d}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [StockMaster AI] 25초 풀스크린 퀀트 숏폼 생산 시작 (주제 #{topic_id})")

        # 1. 시나리오 대본 준비
        scenario = self.script_director.get_full_scenario(topic_id=topic_id)
        theme_name = scenario["theme_name"]
        full_speech = (
            "뉴스는 좋다는데 내가 사면 왜 매번 떨어질까? 주식 초보가 고점 설거지에 물리는 이유, "
            "체결 강도와 이격도를 모르기 때문입니다. 저희 시스템은 10분마다 국내 350개 핵심 우량주를 실시간 정밀 추적합니다. "
            "삼성전자 수급 현황! 외국인과 기관의 실시간 순매수와 4조 원대 거래대금을 한눈에 확인하고, "
            "기술 지표 탭에서 당일 체결강도 백육십 퍼센트와 이격도, 볼린저밴드 매수 적기를 1초 만에 검증합니다. "
            "AI 리스크 센터가 숨겨진 악재와 아킬레스건을 철저히 걸러내어 안전 구간을 확보하고, "
            "기업 펀더멘털과 최근 실적 추이까지 완벽하게 데이터로 제시합니다. "
            "지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
        )

        # 2. [Step 1] Alibaba CosyVoice 초실사 성우 음성 합성 (24.5초)
        logger.info("🎙️ [Step 1] Alibaba CosyVoice 음성 합성 진행...")
        speech_wav = self.tts.generate_speech_wav(
            text=full_speech,
            lang="ko",
            gender="male",
            rate="+2%",
            pitch="+0Hz",
            filename_prefix=f"stock_quant_speech_{topic_id}_{dt_str}"
        )

        # 3. [Step 2] StockMaster AI 실물 웹앱 라이브 브라우징 24초 녹화
        app_clip_path = str(out_folder / f"01_stock_live_app_24s.mp4")
        logger.info("📱 [Step 2] StockMaster AI 실물 웹앱 24초 상하단 스크롤 라이브 녹화...")
        self.app_simulator.record_simulation_clip(
            topic_id=topic_id,
            duration_sec=24.0,
            output_mp4_path=app_clip_path,
            force_fresh_record=force_fresh_record
        )

        # 4. [Step 3] 1초 네이버 공식 검색 CTA 세그먼트 준비
        cta_clip_path = str(out_folder / f"02_stock_cta_1s.mp4")
        logger.info("🏷️ [Step 3] 1초 네이버 공식 검색 CTA 세그먼트 준비...")
        self.cta_card.create_cta_segment_mp4(
            output_path=cta_clip_path,
            duration_sec=1.0,
            topic_title=theme_name,
            debate_question=scenario.get("debate_question", "삼성전자 지금 구간, 추격 매수 vs 조정 대기?"),
            search_keyword="스톡마스터 AI",
            hero_copy="10분마다 실시간 퀀트 데이터 무료 확인!"
        )

        # 5. [Step 4] 24초 앱 영상 + 1초 CTA 결합 및 음성 믹싱 (총 25.0초 완제품)
        final_mp4_name = f"Stock_25초_풀스크린퀀트_주제{topic_id:02d}_삼성전자4대모달_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)
        logger.info(f"✨ [Step 4] 25.0초 1080p 세로 풀HD 완제품 최종 컴포징: {final_mp4_path}")

        # FFmpeg Concat & Audio Mux
        concat_list = out_folder / "concat_list.txt"
        concat_list.write_text(
            f"file '{Path(app_clip_path).resolve().as_posix()}'\n"
            f"file '{Path(cta_clip_path).resolve().as_posix()}'\n",
            encoding="utf-8"
        )

        import subprocess
        cmd = [
            self.composer.ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-i", str(speech_wav),
            "-t", "25.00",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            final_mp4_path
        ]

        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            err = res.stderr.decode("utf-8", errors="ignore")
            logger.error(f"❌ 최종 컴포징 실패: {err}")
            raise RuntimeError(f"FFmpeg composite failed: {err}")

        # SNS 포스팅 가이드 저장 (댓글창 투자 토론 & 찬반 루프 고정 댓글 탑재)
        sns_guide_path = None
        try:
            from brands.stock.stock_sns_guide_generator import StockSNSGuideGenerator
            sns_guide_path = str(StockSNSGuideGenerator.save_guide_file(
                output_folder=out_folder,
                topic_id=topic_id,
                speech_hook="뉴스는 좋다는데 내가 사면 왜 떨어질까? 주식 초보가 고점 설거지에 물리는 이유, 체결 강도와 이격도를 모르기 때문입니다.",
                debate_question=scenario.get("debate_question")
            ))
        except Exception as e:
            logger.warning(f"SNS 가이드 생성 실패: {e}")

        logger.info(f"🎉 [완제품 숏폼 완료] 파일 저장: {final_mp4_path} ({Path(final_mp4_path).stat().st_size / 1024 / 1024:.2f} MB)")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "output_mp4": final_mp4_path,
            "sns_guide_path": sns_guide_path,
            "output_folder": str(out_folder),
            "speech_wav": str(speech_wav),
            "full_speech": full_speech
        }

