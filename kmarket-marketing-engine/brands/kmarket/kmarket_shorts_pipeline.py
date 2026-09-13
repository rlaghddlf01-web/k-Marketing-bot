# -*- coding: utf-8 -*-
"""
KMarketShortsPipeline - 🎬 [케이마켓 전용 숏폼 동영상 생산 공장]
- 1단계: '입을 부드럽게 다문 미소' 마스터컷 인물 사진 생성 (Wan2.1 T2I)
- 2단계: 케이마켓 송금/나눔 UI 생성 후 OpenCV 서브픽셀 정밀 매립
- 3단계: 5.06초(81프레임) 맞춤형 다국어 음성 생성 (Edge-TTS)
- 4단계: Wan 2.2 S2V 립싱크 렌더링 및 FFmpeg 오디오 결합
- 5단계: 로컬 바탕화면 전용 완성본 출력
"""

import os
from pathlib import Path
from PIL import Image

from core.engine.phone_screen_embedder import PhoneScreenEmbedder
from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.tts_voice_synthesizer import TTSVoiceSynthesizer
from .ui_templates.remittance_template import RemittanceTemplate
from .scenarios.prompt_director_shorts import PromptDirectorShortsKMarket


class KMarketShortsPipeline:
    """케이마켓 숏폼 자동 생산 파이프라인"""

    def __init__(self):
        self.embedder = PhoneScreenEmbedder()
        self.wan_client = WanPipelineClient()
        self.tts = TTSVoiceSynthesizer()
        self.ui_template = RemittanceTemplate()
        self.desktop = Path(r"C:\Users\zkfnt\Desktop")

    def produce(
        self,
        nationality_code: str = "vi",
        custom_master_image: Image.Image = None,
        output_filename: str = "kmarket_shorts_5s.mp4"
    ) -> str:
        """케이마켓 5초 숏폼 1회 완성 실행"""
        # 1. 케이마켓 UI 렌더링
        ui_img = self.ui_template.render(title="K-MARKET 무료 나눔", amount=1500000)

        # 2. 마스터 인물 컷 준비 (입을 부드럽게 다문 미소 컷)
        if custom_master_image is not None:
            master_img = custom_master_image
        else:
            cached_master = self.desktop / f"kmarket_closed_mouth_{nationality_code}.png"
            if cached_master.exists():
                master_img = Image.open(str(cached_master))
            else:
                print(f"🎨 [입 다문 미소 컷 생성] Wan 2.1 T2I로 {nationality_code} 전용 마스터 컷 생성 중...")
                t2i_prompt = PromptDirectorShortsKMarket.get_t2i_prompt(nationality_code)
                gen_frame = self.wan_client.generate_t2i_master(
                    positive_prompt=t2i_prompt["positive"],
                    negative_prompt=t2i_prompt["negative"],
                    prefix=f"kmarket_closed_{nationality_code}"
                )
                master_img = Image.open(gen_frame)
                master_img.save(str(cached_master))

        # 3. OpenCV 액정 정밀 매립
        embedded_img = self.embedder.embed_screen(base_image=master_img, ui_image=ui_img)

        # 4. 9:16 세로 숏폼 규격(480x832) 프레이밍
        W, H = embedded_img.size
        scaled_w = int(W * (832 / H))
        scaled_img = embedded_img.resize((scaled_w, 832), Image.Resampling.LANCZOS)
        crop_left = max(0, min(10, scaled_w - 480))
        framed_img = scaled_img.crop((crop_left, 0, crop_left + 480, 832))

        input_img_name = f"kmarket_input_{nationality_code}.png"
        input_img_path = os.path.join(self.wan_client.comfy_input_dir, input_img_name)
        framed_img.save(input_img_path)

        # 5. 음성 합성 (81프레임 = 5.06초)
        script = PromptDirectorShortsKMarket.get_speech_script(nationality_code)
        wav_path = self.tts.generate_speech_wav(
            text=script,
            lang=nationality_code,
            rate="+18%",
            filename_prefix=f"kmarket_speech_{nationality_code}"
        )
        audio_name = os.path.basename(wav_path)

        # 6. Wan 2.2 S2V 영상 렌더링
        output_desktop = self.desktop / output_filename
        self.wan_client.generate_s2v_video(
            image_name=input_img_name,
            audio_name=audio_name,
            prompt_text="a smart attractive woman holding smartphone, talking enthusiastically to camera with natural gentle smile, clear lip sync",
            output_mp4_path=str(output_desktop),
            prefix="kmarket_s2v"
        )

        return str(output_desktop)
