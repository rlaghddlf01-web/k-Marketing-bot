# -*- coding: utf-8 -*-
"""
InsuranceShortsProducer - 🛡️ [보험 리밸런스 전용 AI 숏폼 영상 생산 엔진]
- AuraShortsProducer의 완벽한 Wan 2.1 T2I + Wan 2.2 S2V 10초 원테이크 + 앱시뮬 8초 + CTA 4초 아키텍처 100% 동일 계승
- [1단계] Wan 2.1 T2I 마스터 인물 컷 생성 (30대 스마트 금융/보험 어드바이저 & 소비자, 입 다문 신뢰감 있는 미소)
- [2단계] 객관적 AI 5대 보장(암/뇌/심/실비/수술) 레이더 차트 & 중복/공백 탐지 시연 (8.0초)
- [3단계] 맞춤형 스피치 음성 합성 (Google Gemini 2.5 Flash TTS) & Wan 2.2 S2V 10초 원테이크 립싱크 (5s+5s xfade)
- [4단계] 1080x1920 세로 풀HD 업스케일링 + 공식 네이버 검색 CTA ['보험 리밸런스'] 결합 (심의 100% 프리패스 클린 뷰)
- 산출물 경로: C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Insurance
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .base_shorts_producer import BaseShortsProducer
from .insurance_app_recorder import InsuranceAppRecorder
from brands.insurance.ui_templates.insurance_cta_card import InsuranceCTACard
from .insurance_shorts_scenario_director import InsuranceShortsScenarioDirector
from .shorts_character_anchor_insurance import build_insurance_shorts_t2i_character_prompt
from .s2v_clip_stitcher import S2VClipStitcher
from brands.insurance.insurance_voice_cloner import InsuranceVoiceCloner

logger = logging.getLogger("InsuranceShortsProducer")


class InsuranceShortsProducer(BaseShortsProducer):
    """🛡️ 보험 리밸런스 숏폼 자동 생산 엔진 (알리바바 CosyVoice 서연 보이스 + 실물 웹앱 Playwright 녹화 + Wan 2.2 S2V)"""

    def __init__(self, use_voice_cloner: bool = True):
        super().__init__("Insurance")
        # 산출물 절대 경로: 바탕화면/한국 숏폼_산출물/Insurance
        self.output_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance")
        self.output_base.mkdir(parents=True, exist_ok=True)

        self.app_simulator = InsuranceAppRecorder()
        self.cta_card = InsuranceCTACard()
        self.script_director = InsuranceShortsScenarioDirector()
        
        # 🎙️ 알리바바 CosyVoice 서연(Seoyeon) 보이스 복제기 (1순위 알리바바 -> 2순위 Typecast -> 3순위 Edge-TTS)
        self.voice_cloner = InsuranceVoiceCloner(output_dir=str(self.output_base))
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
        """보험 100대 주제 전용 T2I 캐릭터 및 배경 프롬프트 생성"""
        return build_insurance_shorts_t2i_character_prompt(
            topic_id=topic_id,
            custom_char_desc=custom_char_desc,
            custom_bg_desc=custom_bg_desc,
            gender=gender
        )

    def render_ui_image(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> Image.Image:
        """보험 스마트폰 액정 화면 렌더링 (5대 보장 진단 리포트)"""
        frames = self.app_simulator.generate_simulation_frames(topic_id=topic_id, fps=1, duration_sec=1.0)
        return frames[0] if frames else Image.new("RGB", (1080, 1920), (15, 23, 42))

    def get_speech_script(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> str:
        """보험 맞춤형 나레이션 스크립트 반환"""
        scenario = self.script_director.get_full_scenario(topic_id=topic_id)
        return scenario["full_speech"]

    # 🔒 [주제 순환 모드 (None: 1~100번 자율 순환 / 숫자 지정 시 특정 주제 고정)]
    FIXED_TOPIC_ID: Optional[int] = None

    def _get_next_topic_id(self) -> int:
        """1번부터 100번까지 주제를 자율 순환(Rotation)하며 상태 파일에 영구 기록"""
        if self.FIXED_TOPIC_ID is not None:
            logger.info(f"🔒 [보험 숏폼] 대표님 지시로 주제 #{self.FIXED_TOPIC_ID} 고정 생산 모드 가동 중")
            return self.FIXED_TOPIC_ID

        state_file = self.output_base / "insurance_shorts_state.json"
        last_id = 0
        if state_file.exists():
            try:
                import json
                data = json.loads(state_file.read_text(encoding="utf-8"))
                last_id = data.get("last_topic_id", 0)
            except Exception:
                pass
        next_id = (last_id % 100) + 1
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
        보험 100대 주제별 Wan 2.1 실사 마스터 사진 단독 생산 파이프라인
        - 832x1216 해상도 Wan 2.1 14B Q4_0 T2I 마스터컷 렌더링
        - C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance\Topic_XX 폴더에 저장
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

        logger.info(f"🎨 [보험 마스터 사진] 주제 {topic_id} [{theme_name}] Wan 2.1 T2I 렌더링 시작 (seed={seed})")

        gen_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos_prompt,
            negative_prompt=neg_prompt,
            width=832,
            height=1216,
            seed=seed,
            prefix=f"insurance_master_{topic_id}"
        )
        master_img = Image.open(gen_path)
        master_save_path = out_folder / f"master_t2i_{topic_id:02d}_seed{seed}.png"
        master_img.save(str(master_save_path))

        self.wan_client.free_vram()

        # SNS 포스팅 가이드 자동 생성
        try:
            from brands.insurance.insurance_sns_guide_generator import InsuranceSNSGuideGenerator
            InsuranceSNSGuideGenerator.save_guide_file(
                output_folder=out_folder,
                topic_id=topic_id,
                speech_hook=scenario.get("speech_hook")
            )
        except Exception as e:
            logger.warning(f"SNS 포스팅 가이드 생성 실패: {e}")

        logger.info(f"🎉 [보험 마스터 사진 완료] 파일 저장: {master_save_path}")
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
        **kwargs
    ) -> Dict[str, Any]:
        """
        보험 리밸런스 숏폼 풀 프로덕션:
        - topic_id 미지정 시 1~100번 자율 순환
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

        # 2. 시나리오 대본 생성
        scenario = self.script_director.get_full_scenario(topic_id=topic_id, gender=gender)
        theme_name = scenario["theme_name"]
        theme_code = scenario["theme_code"]
        effective_gender = scenario.get("gender", gender or "female")
        speech_hook = scenario["speech_hook"]
        speech_app = scenario["speech_app"]
        speech_cta = scenario["speech_cta"]
        full_speech = scenario["full_speech"]
        visual_dir = scenario["visual_direction"]

        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"Insurance_{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [보험 숏폼] 생산 시작: 주제 {topic_id} [{theme_name}] | 성별: {effective_gender} | seed: {seed}")

        # 3. [Step 1] 알리바바 CosyVoice / 초실사 음성 합성 (여성: 서연 / 남성: 진우)
        voice_lang = "ko"
        voice_rate = scenario.get("voice_rate", "+3%")
        voice_pitch = scenario.get("voice_pitch", "+2Hz")
        logger.info(f"🎙️ [Step 1] 초실사 음성 복제 합성 (성별: {effective_gender})...")
        hook_wav_path = self.tts.generate_speech_wav(
            text=speech_hook,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"insure_hook_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        app_wav_path = self.tts.generate_speech_wav(
            text=speech_app,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"insure_app_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        cta_wav_path = self.tts.generate_speech_wav(
            text=speech_cta,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"insure_cta_{topic_id}_{dt_str}",
            output_dir=str(out_folder)
        )
        full_wav_path = self.tts.generate_speech_wav(
            text=full_speech,
            lang=voice_lang,
            gender=effective_gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"insure_full_{topic_id}_{dt_str}",
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
                prefix=f"shorts_insure_{topic_id}"
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
                speech_hook_part1=scenario.get("speech_hook_part1"),
                speech_hook_part2=scenario.get("speech_hook_part2"),
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

        # 6. [Step 4] 보험 리밸런스 실제 웹앱 실시간 시연 클립 (표준 12.0초)
        app_clip_path = str(out_folder / f"04_app_sim_insure_{topic_id}.mp4")
        logger.info(f"📱 [Step 4] 보험 리밸런스 실제 웹앱 시연 비디오 준비 (12.00s)...")
        self.app_simulator.record_simulation_clip(
            topic_id=topic_id,
            duration_sec=12.0,
            output_mp4_path=app_clip_path
        )

        # 7. [Step 5] 네이버 검색 공식 4초 럭셔리 에디토리얼 CTA 비디오 준비 (표준 4.0초)
        cta_clip_path = str(out_folder / f"05_cta_debate_insure_{topic_id}.mp4")
        logger.info(f"🏷️ [Step 5] 네이버 검색 4초 공식 검색어 에디토리얼 CTA 비디오 준비 (4.00s)...")
        self.cta_card.create_cta_segment_mp4(
            output_path=cta_clip_path,
            duration_sec=4.0,
            topic_title=theme_name,
            debate_question=scenario.get("debate_question", "내 보험에 뇌출혈만 있다 vs 뇌혈관질환 있다?"),
            search_keyword="보험 리밸런스",
            hero_copy=scenario.get("hero_copy", "객관적 5대 보장 AI 분석!")
        )

        # 8. [Step 6] 22초 하이브리드 완제품 컴포징 (상단 좌측 다크 에메랄드 캡슐 뱃지 탑재)
        final_mp4_name = f"Insurance_22초숏폼_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)
        from .shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
        insure_logo_overlay = ShortsBrandCapsuleBadge.get_overlay_path("insurance")

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
            logo_overlay_path=insure_logo_overlay
        )

        # 9. [순수 100% 인물 클로즈업 원테이크 1080x1920 세로 풀HD 단독 완제품 생성] (상단 캡슐 뱃지 일체형)
        pure_one_take_name = f"Insurance_10초_순수인물_원테이크_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        pure_one_take_path = str(out_folder / pure_one_take_name)
        cmd_pure = [
            self.composer.ffmpeg_exe, "-y",
            "-i", person_clip_path,
            "-i", insure_logo_overlay,
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

        # 10. [SNS 포스팅 가이드 자동 생성] (댓글창 찬반 논쟁 유발 고정 댓글 탑재)
        sns_guide_path = None
        try:
            from brands.insurance.insurance_sns_guide_generator import InsuranceSNSGuideGenerator
            sns_guide_path = str(InsuranceSNSGuideGenerator.save_guide_file(
                output_folder=out_folder,
                topic_id=topic_id,
                speech_hook=speech_hook,
                debate_question=scenario.get("debate_question")
            ))
        except Exception as e:
            logger.warning(f"SNS 포스팅 가이드 생성 실패: {e}")

        logger.info(f"🎉 [보험 숏폼 생산 완료] 완제품 저장: {final_mp4_path}")
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
