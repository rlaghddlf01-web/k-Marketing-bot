# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/generate_ipadapter_v3.py
IP-Adapter v3 - InsightFace 정밀 얼굴 감지/정렬 + 고품질 렌더링

InsightFace가 하는 일:
  - 얼굴 바운딩 박스 정밀 감지
  - 눈/코/입 기준점으로 얼굴 정렬(align)
  - 512x512 정규화된 얼굴 이미지 추출
→ IP-Adapter에 정확한 얼굴 특징 전달
"""
import sys, time
from pathlib import Path
import cv2
import numpy as np
import torch
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from diffusers import StableDiffusionPipeline


def get_face_insightface(img_pil: Image.Image, size: int = 512) -> Image.Image:
    """InsightFace로 얼굴 감지 + 정렬 후 512x512 크롭 반환"""
    import insightface
    from insightface.app import FaceAnalysis

    app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))

    img_bgr = cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    faces = app.get(img_bgr)

    if not faces:
        print("  [WARN] InsightFace 얼굴 감지 실패 - 수동 크롭 사용")
        w, h = img_pil.size
        face = img_pil.crop((int(w*0.15), int(h*0.05), int(w*0.85), int(h*0.50)))
        return face.resize((size, size), Image.LANCZOS)

    # 가장 큰 얼굴 선택
    face = sorted(faces, key=lambda x: x.bbox[2] * x.bbox[3], reverse=True)[0]
    bbox = face.bbox.astype(int)
    x1, y1, x2, y2 = bbox

    # 패딩 추가 (얼굴 + 어깨 포함)
    pad_x = int((x2 - x1) * 0.5)
    pad_y = int((y2 - y1) * 0.5)
    h_img, w_img = img_bgr.shape[:2]
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w_img, x2 + pad_x)
    y2 = min(h_img, y2 + pad_y)

    face_crop = img_pil.crop((x1, y1, x2, y2)).resize((size, size), Image.LANCZOS)
    print("  [OK] InsightFace 얼굴 감지 성공:", x1, y1, x2, y2)
    return face_crop


def main():
    print("=" * 65)
    print("[IP-Adapter v3] InsightFace + 고품질 렌더링")
    print("디바이스:", torch.cuda.get_device_name(0))
    vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    print("VRAM:", round(vram, 1), "GB")
    print("=" * 65)

    # 1. 베이스 모델 로드
    print("[1/4] 베이스 모델 로드 중...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "SG161222/Realistic_Vision_V5.1_noVAE",
        torch_dtype=torch.float16,
        safety_checker=None,
    ).to("cuda")
    print("[1/4] 완료")

    # 2. IP-Adapter 로드 (attention_slicing 없이)
    print("[2/4] IP-Adapter Face 로드 중...")
    pipe.load_ip_adapter(
        "h94/IP-Adapter",
        subfolder="models",
        weight_name="ip-adapter-plus-face_sd15.bin",
    )
    pipe.set_ip_adapter_scale(0.90)
    print("[2/4] 완료 (scale=0.90)")

    # 3. InsightFace로 얼굴 정밀 크롭
    ref_path = Path(
        r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇"
        r"\kmarket-marketing-engine\data\gemini_generated_media"
        r"\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"
    )
    if not ref_path.exists():
        print("씬5 원본 없음:", ref_path)
        return

    print("[3/4] InsightFace 얼굴 감지 중:", ref_path.name)
    ref_img = Image.open(ref_path).convert("RGB")
    face_img = get_face_insightface(ref_img, size=512)

    crop_save = Path(r"C:\Users\zkfnt\OneDrive\Desktop\insightface_crop_check.jpg")
    face_img.save(str(crop_save), "JPEG", quality=95)
    print("  얼굴 크롭 저장:", crop_save)

    # 4. 고품질 렌더링
    prompt = (
        "masterpiece, best quality, photorealistic 8k, ultra-detailed, "
        "a beautiful Korean woman, same person, identical face, "
        "standing at a park bus stop with a modern city bus in background, "
        "lush green trees, warm daylight, casual chic outfit, "
        "natural warm smile, sharp focus on face, 8k uhd, film grain"
    )
    negative_prompt = (
        "deformed, bad anatomy, bad hands, missing fingers, extra fingers, "
        "blurry face, distorted face, ugly face, mutation, disfigured, "
        "lowres, cartoon, 3d, illustration, painting, watermark, "
        "text, logo, cropped, out of frame, duplicate"
    )

    print("[4/4] 40 steps GPU 렌더링 시작...")
    start = time.time()
    generator = torch.Generator(device="cuda").manual_seed(42)
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        ip_adapter_image=face_img,
        num_inference_steps=40,
        guidance_scale=7.5,
        height=768,
        width=512,
        generator=generator,
    ).images[0]
    elapsed = round(time.time() - start, 2)
    print("[완료] 렌더링 시간:", elapsed, "초")

    # 5. 저장
    out_desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop\5060Ti_IPAdapter_v3_InsightFace.jpg")
    out_artifact = Path(
        r"C:\Users\zkfnt\.gemini\antigravity-ide\brain"
        r"\a9a6db25-d3f1-4ca8-8b12-b98e2235f511\ipadapter_v3.jpg"
    )
    result.save(str(out_desktop), "JPEG", quality=95)
    result.save(str(out_artifact), "JPEG", quality=95)

    print("=" * 65)
    print("[SUCCESS] IP-Adapter v3 InsightFace 렌더링 완료!")
    print("바탕화면:", out_desktop)
    print("=" * 65)


if __name__ == "__main__":
    main()
