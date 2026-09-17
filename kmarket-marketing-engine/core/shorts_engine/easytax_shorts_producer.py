# -*- coding: utf-8 -*-
"""
EasyTaxShortsProducer - 💼 [이지텍스(세금 환급) 전용 AI 숏폼 영상 생산 엔진]
- 타겟 8개국 (베트남, 캄보디아, 인도네시아, 카자흐스탄, 필리핀, 우즈베키스탄, 미얀마, 태국)
- [1단계] Wan 2.1 T2I 마스터 인물 컷 생성 (스마트폰 액정을 정면으로 들고 입을 다문 채 미소 짓는 모델)
- [2단계] 국세청 환급 영수증 UI 생성 및 PhoneScreenEmbedder 액정 정밀 매립 (원근 왜곡 + 손가락 피부 보존)
- [3단계] 8개국 맞춤형 세금 환급 스피치 음성 합성 (Edge-TTS) & Wan 2.2 S2V 립싱크 모션 생성
- [4단계] 1080x1920 세로 풀HD 업스케일링 + 마케팅 뱃지(후불제, 0원) + 엔딩 CTA 결합 완성본 출력
- 산출물 경로: C:/Users/zkfnt/Desktop/숏폼_산출물/이지텍스
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .base_shorts_producer import BaseShortsProducer
from brands.easytax.ui_templates.refund_receipt_template import RefundReceiptTemplate
from .easytax_app_recorder import EasyTaxAppRecorder
from .shorts_scenario_script_director import ShortsScenarioScriptDirector
from .s2v_clip_stitcher import S2VClipStitcher

logger = logging.getLogger("EasyTaxShortsProducer")


class EasyTaxShortsProducer(BaseShortsProducer):
    """이지텍스 세금 환급 숏폼 자동 생산 엔진"""

    # 8개국 국가별 에스닉 및 페르소나 정의
    COUNTRY_CONFIG = {
        "vi": {
            "name": "Vietnam",
            "gender": "female",
            "char_desc": "a lovely 25-year-old Vietnamese woman, friendly calm face, gentle dark eyes, sleek black ponytail, casual neat navy blue top",
            "bg_desc": "modern warm cozy Seoul apartment living room, wooden bookshelf, soft indoor daylight",
            "badge_primary": "HOÀN 90% THUẾ",
            "badge_secondary": "Miễn phí ban đầu",
            "cta_text": "KIỂM TRA NGAY >",
            "default_amount": 3100000,
            "speech": "Tôi vừa nhận lại tiền hoàn thuế từ lương tại Hàn Quốc! Kiểm tra ngay nhé!"
        },
        "km": {
            "name": "Cambodia",
            "gender": "male",
            "char_desc": "a handsome 27-year-old Cambodian young man, warm dark eyes, clean-shaven smooth skin, strictly no beard, no mustache, neat modern haircut, casual dark grey shirt",
            "bg_desc": "bright modern Seoul studio apartment, neat wooden shelves, soft natural window light",
            "badge_primary": "បានលុយមកវិញ!",
            "badge_secondary": "សេវាគិតក្រោយ 100%",
            "cta_text": "ចុច Link ខាងក្រោម >",
            "default_amount": 2450000,
            "speech": "ខ្ញុំបានទទួលការបង្វិលពន្ធកាត់ពីប្រាក់ខែមកវិញហើយ! សូមពិនិត្យមើលឥឡូវនេះ!"
        },
        "id": {
            "name": "Indonesia",
            "gender": "male",
            "char_desc": "a handsome 28-year-old Indonesian young man, calm pleasant expression, clean-shaven, short neat black hair, casual navy blue polo shirt",
            "bg_desc": "modern cozy living room with indoor green plants, soft warm lighting",
            "badge_primary": "100% TANPA BIAYA DI AWAL",
            "badge_secondary": "Bayar Setelah Cair",
            "cta_text": "CEK SEKARANG >",
            "default_amount": 1420000,
            "speech": "Saya baru dapat pengembalian pajak yang dipotong dari gaji di Korea! Yuk cek sekarang!"
        },
        "kk": {
            "name": "Kazakhstan",
            "gender": "male",
            "char_desc": "a handsome 29-year-old Kazakh man, Central Asian features, calm confident expression, short black hair, casual dark olive bomber jacket",
            "bg_desc": "modern clean apartment living room, grey sofa, warm indoor lamp light",
            "badge_primary": "100% КЕЙІН ТӨЛЕУ",
            "badge_secondary": "Қазір 0 вон!",
            "cta_text": "ҚАЗІР ТЕКСЕРУ >",
            "default_amount": 2150000,
            "speech": "В Корее я вернул налог, удержанный с зарплаты! Проверьте прямо сейчас!"
        },
        "tl": {
            "name": "Philippines",
            "gender": "female",
            "char_desc": "a pleasant 26-year-old Filipina woman, calm composed expression, neat casual dark striped blouse, clean tied hair",
            "bg_desc": "bright cozy apartment interior, modern desk with notebook, sunny window",
            "badge_primary": "ZERO UPFRONT FEE",
            "badge_secondary": "Pay Only When Received",
            "cta_text": "CHECK YOUR REFUND >",
            "default_amount": 2780000,
            "speech": "I just got a refund on taxes deducted from my salary in Korea! Check yours right now!"
        },
        "uz": {
            "name": "Uzbekistan",
            "gender": "male",
            "char_desc": "a handsome 27-year-old Uzbek man, friendly attractive face, clean-shaven, calm confident look, navy blue crewneck sweater",
            "bg_desc": "comfortable modern living room, warm indoor atmosphere, bookshelf",
            "badge_primary": "100% OLDINDAN TO'LOV YO'Q",
            "badge_secondary": "Pul tushgach to'lang",
            "cta_text": "HOZIROQ TEKSHIRING >",
            "default_amount": 2600000,
            "speech": "Koreyada oylikdan ushlab qolingan soliqni qaytarib oldim! Hoziroq tekshiring!"
        },
        "my": {
            "name": "Myanmar",
            "gender": "male",
            "char_desc": "a polite 26-year-old Myanmar young man, kind composed face, clean-shaven smooth skin, neat dark hair, casual dark blue collared shirt",
            "bg_desc": "peaceful modern apartment living room, warm sunlight, clean interior",
            "badge_primary": "အခမဲ့စစ်ဆေးပါ",
            "badge_secondary": "ငွေဝင်မှ ဝန်ဆောင်ခပေး",
            "cta_text": "အခုပဲ စစ်ဆေးကြည့်ပါ >",
            "default_amount": 2300000,
            "speech": "ကိုရီးယားမှာ လစာမှ ဖြတ်တောက်ခံရသော အခွန်ငွေ ပြန်ရခဲ့ပါပြီ! အခုပဲ စစ်ဆေးကြည့်ပါ!"
        },
        "th": {
            "name": "Thailand",
            "gender": "male",
            "char_desc": "a cheerful 27-year-old Thai young man, calm pleasant expression, clean-shaven, neat modern haircut, casual charcoal grey sweatshirt",
            "bg_desc": "modern warm living space, soft background lighting, cozy atmosphere",
            "badge_primary": "ฟรีค่าบริการล่วงหน้า",
            "badge_secondary": "เงินเข้าจริงค่อยจ่าย",
            "cta_text": "เช็คเงินคืนทันที >",
            "default_amount": 2500000,
            "speech": "ผมได้เงินคืนภาษีที่ถูกหักจากเงินเดือนในเกาหลีแล้ว! เช็คสิทธิ์ฟรีตอนนี้เลยครับ!"
        }
    }

    def __init__(self):
        super().__init__(brand_name="이지텍스")
        self.ui_template = RefundReceiptTemplate()
        self.app_recorder = EasyTaxAppRecorder()
        self.script_director = ShortsScenarioScriptDirector()
        self.stitcher = S2VClipStitcher(wan_client=self.wan_client, tts_synthesizer=self.tts)

    def get_character_prompt(
        self,
        lang: str,
        custom_char_desc: Optional[str] = None,
        custom_bg_desc: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (카드뉴스 에스닉 앵커 100% 연동)"""
        from core.shorts_engine.shorts_character_anchor_easytax import build_shorts_t2i_character_prompt
        cfg = self.COUNTRY_CONFIG.get(lang, self.COUNTRY_CONFIG["vi"])
        return build_shorts_t2i_character_prompt(
            lang=lang,
            custom_char_desc=custom_char_desc,
            custom_bg_desc=custom_bg_desc,
            default_char_desc=cfg.get("char_desc", ""),
            default_bg_desc=cfg.get("bg_desc", "")
        )

    def render_ui_image(self, lang: str, amount: int = 3100000, **kwargs) -> Image.Image:
        """국세청 환급 영수증 UI 렌더링"""
        return self.ui_template.render(amount=amount)

    def get_speech_script(self, lang: str, amount: int = 3100000, **kwargs) -> str:
        """다국어 나레이션 스크립트"""
        cfg = self.COUNTRY_CONFIG.get(lang, self.COUNTRY_CONFIG["vi"])
        return cfg["speech"]

    def produce(
        self,
        lang: Optional[str] = None,
        amount: Optional[int] = None,
        custom_hero_image: Optional[Image.Image] = None,
        seed: int = 2026,
        theme_id: Optional[str] = None,
        gender: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """EasyTax 완제품 22초 하이브리드 숏폼 비디오 원클릭 생산 (제미나이 언어/인물/대본 올인원 디렉팅)"""
        # 1. ComfyUI 엔진 확인
        self.ensure_engine_ready()

        # 2. [시나리오 & 22초 대본 생성] (lang이 None 또는 'auto'면 제미나이가 테마에 최적화된 언어 직접 선택, 성별 50:50 분배)
        scenario = self.script_director.get_full_scenario(lang=lang, amount=amount or 3100000, theme_id=theme_id, gender=gender)
        effective_lang = scenario.get("lang", "vi")
        cfg = self.COUNTRY_CONFIG.get(effective_lang, self.COUNTRY_CONFIG["vi"])
        country_name = scenario.get("country_name", cfg["name"])
        effective_amount = amount or scenario.get("amount", cfg["default_amount"])
        gender = scenario.get("gender", cfg.get("gender", "female"))

        speech_hook = scenario["speech_hook"]
        full_speech = scenario["full_speech"]
        visual_dir = scenario["visual_direction"]

        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"이지텍스_{country_name}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [이지텍스 22초 숏폼] 생산 시작: {country_name} ({effective_lang.upper()}) | 성별: {gender} | 환급액: ₩{effective_amount:,}")

        # 3. [음성 합성] 3단 독립 씬 오디오 분리 합성 (1씬 인물 훅 / 2씬 앱 시연 / 3씬 엔딩 CTA)
        logger.info(f"🎙️ [Step 1] Edge-TTS 3단 다국어 신경망 음성 합성 ({gender}, 10초 이상 여유 있는 호흡)...")
        hook_wav_path = self.tts.generate_speech_wav(
            text=speech_hook,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_hook_{effective_lang}_{dt_str}"
        )
        app_speech = scenario.get("speech_app", cfg.get("speech", ""))
        app_wav_path = self.tts.generate_speech_wav(
            text=app_speech,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_app_{effective_lang}_{dt_str}"
        )
        cta_speech = scenario.get("speech_cta", "")
        cta_wav_path = self.tts.generate_speech_wav(
            text=cta_speech,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_cta_{effective_lang}_{dt_str}"
        )
        full_wav_path = self.tts.generate_speech_wav(
            text=full_speech,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_full_{effective_lang}_{dt_str}"
        )
        audio_name = os.path.basename(hook_wav_path)

        # 1씬 인사말 실제 음성 길이 측정 및 Wan 2.2 S2V 최적 프레임 수 동적 계산 (최소 10초 보장)
        dur_hook = self.composer._get_video_duration(hook_wav_path)
        target_s2v_dur = max(10.06, dur_hook + 0.6)  # 발화 후 0.6초 자연스러운 여운 확보
        raw_frames = int(target_s2v_dur * 16)
        n_steps = (raw_frames - 1 + 3) // 4
        s2v_frames = max(161, 4 * n_steps + 1)  # Wan 3D VAE 4n+1 규격 엄수 (161, 177, 193...)
        actual_s2v_sec = s2v_frames * 0.0625
        logger.info(f"⏱️ [1씬 호흡 정밀 계산] 인사말 발화: {dur_hook:.2f}초 -> S2V 할당: {s2v_frames}프레임 ({actual_s2v_sec:.2f}초, 10초 이상 여유)")

        # 4. [Step 2] 숏폼 인물 사진 생성 및 액정 매립 (Wan 2.1 T2I)
        if custom_hero_image is not None:
            embedded_img = custom_hero_image
            logger.info("🌟 [Step 2] 전달받은 마스터 인물 사진 사용")
        else:
            t2i_prompt = self.get_character_prompt(
                lang=effective_lang,
                custom_char_desc=scenario.get("character_desc"),
                custom_bg_desc=scenario.get("background_desc")
            )
            pos_prompt = t2i_prompt["positive"]
            neg_prompt = t2i_prompt["negative"]

            logger.info(f"🎨 [Step 2] 시나리오 테마 맞춤형 UGC 인물 사진 생성 (seed={seed})")
            gen_path = self.wan_client.generate_t2i_master(
                positive_prompt=pos_prompt,
                negative_prompt=neg_prompt,
                width=832,
                height=1216,
                seed=seed,
                prefix=f"shorts_easytax_ugc_{effective_lang}"
            )
            master_img = Image.open(gen_path)
            master_save_path = out_folder / f"01_master_t2i_{effective_lang}.png"
            master_img.save(str(master_save_path))

            logger.info("📱 [Step 2] 스마트폰 정면 액정 화면 검출 및 환급 영수증 UI 정밀 매립...")
            ui_img = self.render_ui_image(lang=effective_lang, amount=effective_amount)
            ui_save_path = out_folder / f"02_receipt_ui_{effective_lang}.png"
            ui_img.save(str(ui_save_path))

            try:
                embedded_img = self.embedder.embed_screen(base_image=master_img, ui_image=ui_img)
                logger.info("✅ [Step 2] 스마트폰 액정 정밀 매립 100% 성공! (영상 시작 프레임 무결성 통과)")
            except Exception as e:
                logger.warning(f"⚠️ [Step 2 안내] 스마트폰 액정 검출 미매칭 ({e}) -> 고화질 마스터 인물 사진 직접 채택으로 자연스럽게 전환합니다.")
                embedded_img = master_img

        embedded_save_path = out_folder / f"03_embedded_start_frame_{effective_lang}.png"
        embedded_img.save(str(embedded_save_path))

        # [VRAM 클린업] 1단계 T2I 완료 후 GPU VRAM 완전 초기화 (이전 T2I 모델 방출하여 S2V 전용 14.7GB 클린 확보)
        logger.info("🧹 [Step 2 완료] T2I 마스터 사진 모델 VRAM 완전 방출 및 클린업...")
        self.wan_client.free_vram()

        # 5. [Step 3] Wan 2.2 S2V 5초+5초 무결점 모션 연속 결합 렌더링 (81프레임 x 2 = 10.12초)
        framed_img = self.prepare_framed_input_image(embedded_img, target_w=384, target_h=672)
        s2v_motion_prompt = scenario.get("s2v_motion_prompt") or "a friendly foreign worker sitting comfortably in a clean room, holding a smartphone steadily in one hand facing forward to camera, looking directly into camera lens with attentive eye contact, stable hands, still posture, speaking sincerely and naturally with clear lip sync and subtle natural head movement, no rapid hand gestures, clean realistic motion"
        logger.info("🎬 [Step 3] Wan 2.2 S2V 384x672 5초+5초 10초 원테이크 렌더링 시작 (81프레임 x 2, 0.15s xfade)...")
        person_clip_path, person_audio_path = self.stitcher.render_seamless_dual_clip(
            base_framed_img=framed_img,
            speech_hook_full=speech_hook,
            lang=effective_lang,
            gender=gender,
            out_folder=out_folder,
            dt_str=dt_str,
            motion_prompt=s2v_motion_prompt,
            seed=seed,
            speech_hook_part1=scenario.get("speech_hook_part1"),
            speech_hook_part2=scenario.get("speech_hook_part2")
        )

        # 6. [Step 4] EasyTax 웹앱 시뮬레이션 고화질 직결 (말이 끝남과 동시에 영상 정지)
        dur_app_audio = self.composer._get_video_duration(app_wav_path)
        app_target_dur = max(5.0, dur_app_audio + 0.3)  # 나레이션 완결 후 0.3초 미세 여운 후 즉시 종료
        app_clip_path = str(out_folder / f"04_app_sim_{effective_lang}.mp4")
        logger.info(f"📱 [Step 4] EasyTax 앱 시연 비디오 준비 (오디오 {dur_app_audio:.2f}s ➡️ 할당 {app_target_dur:.2f}s, 말 끝남과 동시 정지)...")
        self.app_recorder.record_simulation_clip(
            lang=effective_lang,
            duration_sec=app_target_dur,
            output_mp4_path=app_clip_path
        )

        # 7. [Step 5] 22초 하이브리드 완제품 컴포징 (3단 비디오 + 3단 무결점 씬 오디오 싱크)
        final_mp4_name = f"이지텍스_22초숏폼_{country_name}_{effective_amount:,}원_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)

        logger.info("✨ [Step 5] 1080p 세로 풀HD 22초 하이브리드 비디오 최종 컴포징...")
        scene_audios = {
            "hook": person_audio_path,
            "app": app_wav_path,
            "cta": cta_wav_path
        }
        self.composer.compose_hybrid_22s_shorts(
            clip_person_path=person_clip_path,
            clip_app_path=app_clip_path,
            full_audio_path=full_wav_path,
            visual_direction=visual_dir,
            output_mp4_path=final_mp4_path,
            lang=effective_lang,
            scene_audios=scene_audios
        )

        # 8. [Step 6] 4대 숏폼 SNS 포스팅 가이드 파일 생성 및 저장
        guide_filename = f"SNS_포스팅_가이드_{effective_lang.upper()}.txt"
        guide_path = out_folder / guide_filename
        self._write_sns_guide(
            file_path=guide_path,
            lang=effective_lang,
            country_name=country_name,
            amount=effective_amount,
            speech=full_speech,
            cfg=cfg
        )
        logger.info(f"📝 [SNS 가이드] 숏폼 배포 패키지 가이드 저장 완료: {guide_filename}")

        # 임시 원본 비디오 정리
        if os.path.exists(person_clip_path):
            try:
                os.remove(person_clip_path)
            except Exception:
                pass

        logger.info(f"🎉 [이지텍스 22초 숏폼 완성] 최종 완제품: {final_mp4_path}")
        return {
            "output_mp4": final_mp4_path,
            "folder_path": str(out_folder),
            "guide_path": str(guide_path),
            "country": country_name,
            "lang": lang,
            "amount": effective_amount,
            "speech": full_speech
        }

    def _write_sns_guide(
        self,
        file_path: Path,
        lang: str,
        country_name: str,
        amount: int,
        speech: str,
        cfg: Dict[str, Any]
    ):
        """인스타그램 릴스, 틱톡, 유튜브 쇼츠, 페이스북 릴스 전용 다국어 배포 가이드 작성"""
        amount_fmt = f"{amount:,} KRW"
        badge_p = cfg.get("badge_primary", "HOÀN 90% THUẾ")
        cta = cfg.get("cta_text", "CHECK LINK >")

        hashtags = (
            f"#{country_name}InKorea #EasyTax #KoreaTaxRefund #TaxRefund #E9Visa #E7Visa "
            f"#WorkInKorea #LifeInKorea #외국인세금환급 #국세청환급 #{lang.upper()}"
        )

        content = f"""================================================================================
🎬 [EasyTax 숏폼 영상 4대 SNS 배포 가이드 & 카피라이트]
================================================================================
타깃 국가: {country_name} ({lang.upper()})
환급 인증 금액: {amount_fmt} (₩{amount:,})
영상 규격: 1080x1920 (9:16 세로 풀HD 숏폼)
발화 나레이션: {speech}
================================================================================

[1] 🎵 틱톡 (TikTok) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{badge_p}! 💸 {speech}
👇 {cta} (Link in Bio / Profile)

{hashtags} #TikTokShorts #ViralVideo #KoreaLife

📌 [고정 댓글 (Pinned Comment)]
👉 Check your tax refund for free now! (Profile link)
(선입금 0원, 환급금 입금 후 수수료 차감되는 100% 안전 후불제입니다)


[2] 📸 인스타그램 릴스 (Instagram Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
🇰🇷 {country_name} workers in Korea!
"{amount_fmt} received directly from National Tax Service!"

{speech}

✨ EasyTax Guarantees:
1️⃣ ZERO upfront fee! (100% 후불제)
2️⃣ 1-minute free estimation on mobile!
3️⃣ Certified legal tax refund in Korea!

👉 Click the link in bio to check your refund right now!

{hashtags} #Reels #KoreaLife #TaxBack


[3] 🔴 유튜브 쇼츠 (YouTube Shorts) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [쇼츠 제목 (Title)]
{amount_fmt} Tax Refund in Korea! {badge_p} 🇰🇷 #Shorts

📌 [쇼츠 설명 (Description)]
{speech}
👉 Free Check Link: (프로필/고정댓글 링크 입력)
{hashtags} #Shorts #KoreaTaxRefund


[4] 📘 페이스북 릴스 (Facebook Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션]
📢 [공식 환급 안내] {country_name} 근로자 세금 환급 인증 ({amount_fmt})
{speech}
지금 바로 프로필 링크를 눌러 무료로 환급 예상액을 확인하세요!
================================================================================
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
