# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/generate_instantid.py
InstantID (SDXL 1024px) 기반 동일인물 3씬 초고화질 생성 파이프라인
  - 기반 엔진: SDXL (RealVisXL_V4.0 / 1024x1024)
  - 얼굴 보존: InstantID (InsightFace 임베딩 + 5대 랜드마크 ControlNet)
  - 출력: 버스씬 / 공원씬 / 실내씬 3장 자동 생성 -> OneDrive 바탕화면 저장
"""
import sys, os, time
from pathlib import Path
import numpy as np
import cv2
import torch
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# local_gpu_pipeline 경로를 최우선 import 경로로 등록
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from huggingface_hub import hf_hub_download
from diffusers.models import ControlNetModel
from diffusers import EulerDiscreteScheduler
import insightface
from insightface.app import FaceAnalysis

from pipeline_stable_diffusion_xl_instantid import StableDiffusionXLInstantIDPipeline, draw_kps


def imread_u(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def attach_lora_modular_slot(pipe, lora_path=None, lora_weight=0.5):
    """
    [LoRA 플러그인 모듈러 슬롯] (2단계 대비 확장 슬롯)
    - lora_path가 지정되면 pipe.load_lora_weights()를 통해 안전하게 결합
    - lora_path가 None이면 순수 베이스 파이프라인(1단계 SDXL 네이티브 정밀 모드) 가동
    """
    if lora_path and os.path.exists(lora_path):
        print(f"  🔌 [LoRA Slot] 한국 배경 LoRA 장착 완료: {lora_path} (가중치: {lora_weight})")
        pipe.load_lora_weights(lora_path, adapter_name="korean_bg")
        pipe.set_adapters(["korean_bg"], adapter_weights=[lora_weight])
    else:
        print("  ℹ️ [LoRA Slot] LoRA 슬롯 대기 중 (1단계: SDXL 네이티브 정밀 타격 프롬프트 모드로 가동)")
    return pipe


def main():
    print("=" * 65)
    print("🚀 [InstantID + SDXL 1024px] 한국형 동일인물 3씬 렌더링 시작")
    print("디바이스:", torch.cuda.get_device_name(0))
    print("=" * 65)

    desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop")
    art = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\a9a6db25-d3f1-4ca8-8b12-b98e2235f511")
    ref_path = current_dir / "favorite_reference.jpg"

    # 1. InsightFace 얼굴 및 랜드마크 분석 (InstantID 순정 규격 antelopev2 사용)
    print(f"\n⏳ [1/4] 대표님 지정 선호 인물({ref_path.name}) 얼굴 및 랜드마크 분석 중 (antelopev2)...")
    models_root = current_dir / "models"
    app = FaceAnalysis(name="antelopev2", root=str(models_root.parent), providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))

    src_bgr = imread_u(ref_path)
    faces = app.get(src_bgr)
    if not faces:
        print("❌ 기준 인물 사진에서 얼굴을 찾지 못했습니다.")
        return
    face = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]
    face_emb = face.embedding
    print(f"  ✅ 지정 인물 antelopev2 순정 임베딩 추출 완료 (shape: {face_emb.shape})")

    # 768x1344 비율에 맞춘 왜곡 없는 랜드마크 키포인트 이미지 생성
    target_w, target_h = 768, 1344
    src_h, src_w = src_bgr.shape[:2]
    scale_x = target_w / src_w
    scale_y = target_h / src_h

    scaled_kps = face.kps.copy()
    scaled_kps[:, 0] = scaled_kps[:, 0] * scale_x
    scaled_kps[:, 1] = scaled_kps[:, 1] * scale_y

    canvas_pil = Image.new("RGB", (target_w, target_h), (0, 0, 0))
    face_kps = draw_kps(canvas_pil, scaled_kps)
    print(f"  ✅ 눈동자·코·입 5대 랜드마크 맵 768x1344 정밀 매핑 완료!")

    # 2. InstantID 가중치 및 ControlNet 로드
    print("\n⏳ [2/4] InstantID 어댑터 및 ControlNet 로드 중...")
    t0 = time.time()
    face_adapter = hf_hub_download(repo_id="InstantX/InstantID", filename="ip-adapter.bin")
    controlnet = ControlNetModel.from_pretrained(
        "InstantX/InstantID",
        subfolder="ControlNetModel",
        torch_dtype=torch.float16,
    ).to("cuda")
    print(f"  ✅ ControlNet 로드 완료 ({time.time()-t0:.1f}초)")

    # 3. SDXL 베이스 파이프라인 구성
    print("\n⏳ [3/4] SDXL 극실사 베이스 파이프라인 (RealVisXL V4.0) 로드 중...")
    t0 = time.time()
    pipe = StableDiffusionXLInstantIDPipeline.from_pretrained(
        "SG161222/RealVisXL_V4.0",
        controlnet=controlnet,
        torch_dtype=torch.float16,
        variant="fp16",
    ).to("cuda")

    # 빠른 Euler 스케줄러 적용
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)

    # InstantID 어댑터 로드 (얼굴 정체성 0.85로 강력 유지)
    pipe.load_ip_adapter_instantid(face_adapter)
    pipe.set_ip_adapter_scale(0.85)

    # LoRA 플러그인 모듈러 슬롯 연결
    pipe = attach_lora_modular_slot(pipe, lora_path=None, lora_weight=0.5)
    print(f"  ✅ SDXL + InstantID 파이프라인 가동 준비 완료 ({time.time()-t0:.1f}초)")

    # 4. 씬별 '다채로운 손동작 & 행동 포즈' 및 부드러운 일상 자연광 세팅
    common_style = (
        "looking directly at camera, friendly eye contact, natural gentle smile, "
        "soft balanced natural lighting, perfectly exposed, realistic smooth Korean skin texture, "
        "clear sharp iris, sparkling catchlight in eyes, 8k uhd portrait, "
    )

    scenes = [
        {
            "name": "버스씬",
            "en_name": "Bus_Phone",
            "prompt": (
                f"crisp clean 8k portrait photography of the identical Korean woman from reference, {common_style}"
                "medium shot, waist up, holding a modern smartphone in one hand in front of chest, "
                "standing at Seoul bus stop, modern green Seoul transit bus arriving in background, "
                "wearing olive green coat with shearling collar"
            ),
        },
        {
            "name": "공원씬",
            "en_name": "Park_Waving",
            "prompt": (
                f"crisp clean 8k portrait photography of the identical Korean woman from reference, {common_style}"
                "medium shot, waist up, raising one hand cheerfully waving at viewer, dynamic pleasant posture, "
                "walking in beautiful green Seoul public park, soft lush trees background, "
                "wearing elegant casual beige cardigan"
            ),
        },
        {
            "name": "실내씬",
            "en_name": "Indoor_Coffee",
            "prompt": (
                f"crisp clean 8k portrait photography of the identical Korean woman from reference, {common_style}"
                "medium shot, waist up, sitting cozy by sunlit window in modern Seoul apartment, "
                "holding a warm ceramic coffee mug with both hands, relaxed warm smile, "
                "wearing soft ribbed beige knit sweater"
            ),
        },
    ]

    # 햇빛 과다/환경광 오염/시선 이탈 원천 차단 네거티브
    negative = (
        "(lowres, low quality, worst quality:1.2), deformed, bad anatomy, bad hands, bad fingers, "
        "missing fingers, extra fingers, blurry eyes, plastic skin, doll eyes, oversaturated, watermark, text, "
        "looking down, downcast eyes, looking away, averted gaze, closed eyes, "
        "(overexposed, blown out highlights, harsh sun glare, bleached skin, excessive brightness, high contrast blowout, harsh shadows:1.3), "
        "green tint on skin, green color cast, yellowish skin, sickly skin tone, jaundiced, green bounce light on face, "
        "dull lighting, hazy, foggy, desaturated, "
        "glasses, old, elderly, mature, wrinkles, vintage, retro, analog film, sepia, faded, grainy, 1950s, 1970s, indian, dark skin, "
        "double-decker, trolley, vintage tram, cable car, western bus, European street"
    )

    print("\n⏳ [4/4] 768x1344 지정 인물 다채로운 3동작 포즈 렌더링 시작...")
    W, H = target_w, target_h
    d2 = Path(r"C:\Users\zkfnt\Desktop")

    for i, scene in enumerate(scenes):
        print(f"\n  🎬 [{i+1}/3] {scene['name']} ({scene['en_name']}) 렌더링 중...")
        start_time = time.time()
        generator = torch.Generator(device="cuda").manual_seed(3030 + i * 25)

        # ControlNet 강도를 0.35로 완화하여 고개/몸통 족쇄를 풀고 자유로운 손동작 허용
        image = pipe(
            prompt=scene["prompt"],
            negative_prompt=negative,
            image_embeds=face_emb,
            image=face_kps,
            controlnet_conditioning_scale=0.35,
            num_inference_steps=30,
            guidance_scale=5.0,
            width=W,
            height=H,
            generator=generator,
        ).images[0]

        elapsed = round(time.time() - start_time, 2)
        fname = f"FavoritePose_0{i+1}_{scene['en_name']}.jpg"

        image.save(str(art / fname), "JPEG", quality=95)
        image.save(str(desktop / fname), "JPEG", quality=95)
        if d2.exists():
            image.save(str(d2 / fname), "JPEG", quality=95)
        print(f"    ✨ 완료: {elapsed}초 소요! -> {fname} (바탕화면 저장 완료)")

    print("\n" + "=" * 65)
    print("🎉 [SUCCESS] 대표님 지정 인물 3개 다채로운 포즈 생성 100% 완료!")
    print("=" * 65)

if __name__ == "__main__":
    main()
