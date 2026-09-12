# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/generate_faceid.py
IP-Adapter FaceID PlusV2 - 올바른 얼굴 ID 보존 모델
  모델: h94/IP-Adapter-FaceID / ip-adapter-faceid-plusv2_sd15.bin
  InsightFace normed_embedding으로 얼굴 ID 주입
  3개 씬 (버스/공원/집) 동시 생성
"""
import sys, time, cv2, numpy as np
from pathlib import Path
import torch
from PIL import Image
import insightface
from insightface.app import FaceAnalysis
from diffusers import StableDiffusionPipeline

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def imread_u(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def main():
    print("=" * 65)
    print("[IP-Adapter FaceID PlusV2] 얼굴 ID 보존 3씬 생성")
    print("디바이스:", torch.cuda.get_device_name(0))
    print("=" * 65)

    art = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\a9a6db25-d3f1-4ca8-8b12-b98e2235f511")
    ref_path = Path(
        r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇"
        r"\kmarket-marketing-engine\data\gemini_generated_media"
        r"\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"
    )

    # 1. InsightFace로 얼굴 ID 임베딩 추출
    print("[1/4] InsightFace 얼굴 ID 임베딩 추출...")
    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    app.prepare(ctx_id=0, det_size=(640, 640))
    src_bgr = imread_u(ref_path)
    faces = app.get(src_bgr)
    if not faces:
        print("  얼굴 감지 실패"); return
    face = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]
    cond = torch.from_numpy(face.normed_embedding).unsqueeze(0).unsqueeze(0).to(dtype=torch.float16, device="cuda")
    uncond = torch.zeros_like(cond)
    combined_faceid_embeds = torch.cat([uncond, cond], dim=0)
    print("  얼굴 ID 임베딩 추출 완료 (uncond+cond 결합):", combined_faceid_embeds.shape)

    # 2. 베이스 모델 로드
    print("[2/4] 베이스 모델 로드...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "SG161222/Realistic_Vision_V5.1_noVAE",
        torch_dtype=torch.float16,
        safety_checker=None,
    ).to("cuda")
    print("  완료")

    # 3. IP-Adapter FaceID 로드
    print("[3/4] IP-Adapter FaceID 로드...")
    pipe.load_ip_adapter(
        "h94/IP-Adapter-FaceID",
        subfolder="",
        weight_name="ip-adapter-faceid_sd15.bin",
        image_encoder_folder=None,
    )
    pipe.set_ip_adapter_scale(0.65)
    print("  완료 (ip-adapter-faceid_sd15, scale=0.65)")

    # 4. 3개 씬 생성
    scenes = [
        {
            "name": "버스씬",
            "prompt": (
                "masterpiece, best quality, photorealistic 8k, raw photo, "
                "a 30s beautiful Korean woman, natural skin, medium shot, waist up, facing camera, "
                "standing at Korean bus stop, green Seoul city bus in background, "
                "park trees, warm daylight, casual outfit, gentle smile"
            ),
        },
        {
            "name": "공원씬",
            "prompt": (
                "masterpiece, best quality, photorealistic 8k, raw photo, "
                "a 30s beautiful Korean woman, natural skin, medium shot, waist up, facing camera, "
                "walking in Korean public park, trees, sunny afternoon, "
                "casual chic outfit, happy natural expression, soft bokeh background"
            ),
        },
        {
            "name": "실내씬",
            "prompt": (
                "masterpiece, best quality, photorealistic 8k, raw photo, "
                "a 30s beautiful Korean woman, natural skin, medium shot, waist up, facing camera, "
                "inside modern Korean apartment living room, bright interior, "
                "cozy home, natural light from window, relaxed warm smile"
            ),
        },
    ]
    negative = (
        "deformed, bad anatomy, bad hands, missing fingers, blurry face, "
        "distorted face, ugly face, mutation, lowres, cartoon, 3d, "
        "illustration, plastic skin, oversaturated, shiny skin, glowing forehead"
    )

    desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop")
    print("[4/4] 3개 씬 생성 시작...")
    for i, scene in enumerate(scenes):
        print(f"  [{i+1}/3] {scene['name']} 생성 중...")
        start = time.time()
        generator = torch.Generator(device="cuda").manual_seed(42 + i)

        result = pipe(
            prompt=scene["prompt"],
            negative_prompt=negative,
            ip_adapter_image_embeds=[combined_faceid_embeds],
            num_inference_steps=30,
            guidance_scale=6.5,
            height=768,
            width=512,
            generator=generator,
        ).images[0]

        elapsed = round(time.time() - start, 2)
        fname = f"FaceID_3씬_{i+1}_{scene['name']}.jpg"
        out_art = art / fname
        out_desk = desktop / fname
        result.save(str(out_art), "JPEG", quality=95)
        result.save(str(out_desk), "JPEG", quality=95)
        print(f"    완료: {elapsed}초 → {fname} (바탕화면 및 아티팩트 저장)")

    print("=" * 65)
    print("[SUCCESS] IP-Adapter FaceID 3씬 생성 완료!")
    print("=" * 65)


if __name__ == "__main__":
    main()
