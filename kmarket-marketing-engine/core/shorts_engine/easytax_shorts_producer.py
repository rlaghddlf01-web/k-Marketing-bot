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
            "speech": "Tôi vừa nhận lại tiền hoàn thuế tại Hàn Quốc! Kiểm tra ngay nhé!"
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
            "speech": "ខ្ញុំបានទទួលប្រាក់ពន្ធមកវិញហើយ! សូមពិនិត្យមើលឥឡូវនេះ!"
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
            "speech": "Saya baru dapat pengembalian pajak di Korea! Yuk cek sekarang!"
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
            "speech": "Кореяда салық қайтарымын алдым! Қазір тексеріп көріңіз!"
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
            "speech": "I just got my tax refund in Korea! Check yours right now!"
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
            "speech": "Koreyada soliq qaytarib oldim! Hoziroq tekshiring!"
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
            "speech": "ကိုရီးယားမှာ အခွန်ငွေ ပြန်ရခဲ့ပါပြီ! အခုပဲ စစ်ဆေးကြည့်ပါ!"
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
            "speech": "ผมได้เงินคืนภาษีในเกาหลีแล้ว! เช็คสิทธิ์ฟรีตอนนี้เลยครับ!"
        }
    }

    def __init__(self):
        super().__init__(brand_name="이지텍스")
        self.ui_template = RefundReceiptTemplate()
        self.app_recorder = EasyTaxAppRecorder()
        self.script_director = ShortsScenarioScriptDirector()

    def get_character_prompt(
        self,
        lang: str,
        custom_char_desc: Optional[str] = None,
        custom_bg_desc: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (시나리오 디렉터 테마 맞춤 인물 & 배경)"""
        cfg = self.COUNTRY_CONFIG.get(lang, self.COUNTRY_CONFIG["vi"])
        char_desc = custom_char_desc or cfg["char_desc"]
        bg_desc = custom_bg_desc or cfg["bg_desc"]

        positive = (
            f"candid authentic vertical iPhone mobile photo taken by a friend, {char_desc}, "
            f"sitting comfortably in {bg_desc}, "
            f"holding a sleek modern smartphone naturally in one hand at chest level, showing the vertical black display screen directly facing forward to camera, "
            f"relaxed comfortable one-handed grip, the other arm resting naturally and still, "
            f"calm neutral resting face, lips completely closed together, mouth gently shut, strictly no smile, no teeth showing, "
            f"looking directly into the camera lens with sincere trustworthy friendly eye contact, "
            f"warm muted everyday indoor room lighting, natural realistic skin tones, subtle real skin texture with pores, "
            f"natural soft ambient shadows, grounded realistic contrast, sharp crisp focus, authentic mobile phone capture"
        )

        negative = (
            "overexposed, blown out highlights, washed out, harsh white lighting, excessive brightness, pale bleached skin, "
            "beauty filter, airbrushed, porcelain skin, plastic skin, glamour lighting, studio flash, "
            "smiling, laughing, grinning, toothy smile, open mouth, parted lips, visible teeth, teeth, "
            "holding phone with two hands, phone to ear, making phone call, talking on phone, phone obscuring face, "
            "back of phone, silver phone back, rear camera, phone case back, deformed hands, extra fingers, claw fingers, "
            "cartoon, 3d render, anime, illustration, blurry, low quality"
        )

        return {"positive": positive, "negative": negative}

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
        **kwargs
    ) -> Dict[str, Any]:
        """EasyTax 완제품 22초 하이브리드 숏폼 비디오 원클릭 생산 (제미나이 언어/인물/대본 올인원 디렉팅)"""
        # 1. ComfyUI 엔진 확인
        self.ensure_engine_ready()

        # 2. [시나리오 & 22초 대본 생성] (lang이 None 또는 'auto'면 제미나이가 테마에 최적화된 언어 직접 선택)
        scenario = self.script_director.get_full_scenario(lang=lang, amount=amount or 3100000, theme_id=theme_id)
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

        # 3. [음성 합성] 0~11초 훅 음성(S2V용) + 22초 풀 음성(최종 영상용) - 제미나이 지정 성별 신경망 보이스
        logger.info(f"🎙️ [Step 1] Edge-TTS 다국어 신경망 음성 합성 ({gender}, 10초 이상 여유 있는 호흡)...")
        hook_wav_path = self.tts.generate_speech_wav(
            text=speech_hook,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_hook_{effective_lang}"
        )
        full_wav_path = self.tts.generate_speech_wav(
            text=full_speech,
            lang=effective_lang,
            gender=gender,
            rate="+0%",
            filename_prefix=f"easytax_full_{effective_lang}"
        )
        audio_name = os.path.basename(hook_wav_path)

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
                err_msg = f"❌ [품질 게이트 탈락] 스마트폰 정면 액정 화면 검출 실패 ({e}). 작업을 안전하게 즉시 중단합니다."
                logger.error(err_msg)
                raise ValueError(err_msg)

        embedded_save_path = out_folder / f"03_embedded_start_frame_{effective_lang}.png"
        embedded_img.save(str(embedded_save_path))

        # 5. [Step 3] Wan 2.2 S2V 10초 이상 립싱크 모션 생성 (177프레임 @ 16fps = 11.06초)
        framed_img = self.prepare_framed_input_image(embedded_img, target_w=480, target_h=832)
        comfy_input_name = f"easytax_s2v_input_{effective_lang}_{dt_str}.png"
        comfy_input_path = os.path.join(self.wan_client.comfy_input_dir, comfy_input_name)
        framed_img.save(comfy_input_path)

        person_clip_path = str(out_folder / f"temp_person_s2v_{effective_lang}.mp4")
        logger.info("🎬 [Step 3] Wan 2.2 S2V 10초 이상(177프레임, 11.06초) 립싱크 비디오 렌더링 시작...")
        self.wan_client.generate_s2v_video(
            image_name=comfy_input_name,
            audio_name=audio_name,
            prompt_text="a friendly attractive person holding smartphone, talking to camera with natural gentle smile, clear lip sync, stable hands",
            output_mp4_path=person_clip_path,
            frames=177,
            prefix=f"easytax_s2v_{effective_lang}_{dt_str}"
        )

        # 6. [Step 4] EasyTax 실시간 웹앱 시뮬레이션 라이브 녹화 (10~18초, 8초 분량)
        app_clip_path = str(out_folder / f"04_app_sim_{effective_lang}.mp4")
        logger.info("📱 [Step 4] EasyTax 라이브 앱 시뮬레이션 실시간 레코딩 (8초 분량)...")
        self.app_recorder.record_simulation_clip(
            lang=effective_lang,
            duration_sec=8.0,
            output_mp4_path=app_clip_path
        )

        # 7. [Step 5] 22초 하이브리드 완제품 컴포징 (3단 Concat + 22초 단일 음성 + 오버레이 자막)
        final_mp4_name = f"이지텍스_22초숏폼_{country_name}_{effective_amount:,}원_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)

        logger.info("✨ [Step 5] 1080p 세로 풀HD 22초 하이브리드 비디오 최종 컴포징...")
        self.composer.compose_hybrid_22s_shorts(
            clip_person_path=person_clip_path,
            clip_app_path=app_clip_path,
            full_audio_path=full_wav_path,
            visual_direction=visual_dir,
            output_mp4_path=final_mp4_path,
            lang=effective_lang
        )


        # 8. [Step 6] 4대 숏폼 SNS 포스팅 가이드 파일 생성 및 저장
        guide_filename = f"SNS_포스팅_가이드_{lang.upper()}.txt"
        guide_path = out_folder / guide_filename
        self._write_sns_guide(
            file_path=guide_path,
            lang=lang,
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
