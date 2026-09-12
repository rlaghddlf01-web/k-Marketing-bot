# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/generate_ipadapter_v2.py
IP-Adapter v2 - mediapipe 얼굴 정밀 감지 + 고품질 렌더링
- mediapipe 얼굴 감지로 정밀 크롭
- IP-Adapter scale 0.92
- 40 inference steps
- 강화된 negative prompt
"""
import sys, time
from pathlib import Path
import torch
from PIL import Image
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from diffusers import StableDiffusionPipeline


def crop_face_mediapipe(img: Image.Image, padding: float = 0.35) -> Image.Image:
    """mediapipe로 얼굴 영역 감지 후 padding 포함 정밀 크롭"""
    try:
        import mediapipe as mp
        mp_face = mp.solutions.face_detection
        with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.4) as detector:
            img_rgb = np.array(img.convert("RGB"))
            results = detector.process(img_rgb)
            if results.detections:
                det = results.detections[0]
                bb = det.location_data.relative_bounding_box
                h, w = img_rgb.shape[:2]
                x1 = max(0, int((bb.xmin - padding * bb.width) * w))
                y1 = max(0, int((bb.ymin - padding * bb.height) * h))
                x2 = min(w, int((bb.xmin + bb.width * (1 + padding)) * w))
                y2 = min(h, int((bb.ymin + bb.height * (1 + padding)) * h))
                face_crop = img.crop((x1, y1, x2, y2)).resize((512, 512), Image.LANCZOS)
                print("  [OK] mediapipe 얼굴 감지 성공:", x1, y1, x2, y2)
                return face_crop
    except Exception as e:
        print("  [WARN] mediapipe 실패, 수동 크롭 사용:", e)

    # fallback: 세로 사진 기준 얼굴 위치 추정
    w, h = img.size
    face_crop = img.crop((int(w * 0.15), int(h * 0.05), int(w * 0.85), int(h * 0.50)))
    face_crop = face_crop.resize((512, 512), Image.LANCZOS)
    print("  [INFO] 수동 크롭 사용 완료")
    return face_crop


def main():
    print("=" * 65)
    print("[IP-Adapter v2] 얼굴 정밀 주입 + 고품질 렌더링")
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
    pipe.set_ip_adapter_scale(0.92)
    print("[2/4] IP-Adapter 완료 (scale=0.92)")

    # 3. 씬 5번 얼굴 정밀 크롭
    ref_path = Path(
        r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇"
        r"\kmarket-marketing-engine\data\gemini_generated_media"
        r"\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"
    )
    if not ref_path.exists():
        print("씬5 원본 없음:", ref_path)
        return

    print("[3/4] 얼굴 감지 중:", ref_path.name)
    ref_img = Image.open(ref_path).convert("RGB")
    face_img = crop_face_mediapipe(ref_img, padding=0.35)

    crop_save = Path(r"C:\Users\zkfnt\OneDrive\Desktop\face_crop_check.jpg")
    face_img.save(str(crop_save), "JPEG", quality=95)
    print("  얼굴 크롭 확인용 저장:", crop_save)

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
    generator = torch.Generator(device="cuda").manual_seed(1234)
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
    out_desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop\5060Ti_IPAdapter_v2.jpg")
    out_artifact = Path(
        r"C:\Users\zkfnt\.gemini\antigravity-ide\brain"
        r"\a9a6db25-d3f1-4ca8-8b12-b98e2235f511\ipadapter_v2.jpg"
    )
    result.save(str(out_desktop), "JPEG", quality=95)
    result.save(str(out_artifact), "JPEG", quality=95)

    print("=" * 65)
    print("[SUCCESS] IP-Adapter v2 렌더링 완료!")
    print("바탕화면:", out_desktop)
    print("=" * 65)


if __name__ == "__main__":
    main()
