# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/test_ipadapter_download.py
5060 Ti 그래픽카드 전용 Diffusers + IP-Adapter Face 로딩 및 첫 생성 테스트
"""
import sys
import os
import time
from pathlib import Path
import torch
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from diffusers import StableDiffusionPipeline

def main():
    print("=" * 65)
    print("🚀 [5060 Ti 16GB] 로컬 AI 디퓨전 + IP-Adapter Face 로딩 시작")
    print(f"• 디바이스: {torch.cuda.get_device_name(0)} (VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB)")
    print("=" * 65)

    base_model_id = "SG161222/Realistic_Vision_V5.1_noVAE"
    print(f"⏳ [1/4] 실사 베이스 모델 로드 중: {base_model_id} (FP16)...")
    pipe = StableDiffusionPipeline.from_pretrained(
        base_model_id,
        torch_dtype=torch.float16,
        safety_checker=None
    ).to("cuda")
    # 16GB VRAM 충분 → 메모리 최적화 옵션 불필요, 모두 제거
    print("✅ [1/4] 베이스 실사 모델 5060 Ti VRAM 로드 완료!")

    print("⏳ [2/4] IP-Adapter Face 가중치 로드 중 (h94/IP-Adapter)...")
    pipe.load_ip_adapter(
        "h94/IP-Adapter",
        subfolder="models",
        weight_name="ip-adapter-plus-face_sd15.bin"
    )
    pipe.set_ip_adapter_scale(0.75)
    print("✅ [2/4] IP-Adapter Face 결합 완료!")

    # 3. 씬 5번 얼굴 사진 로드 및 얼굴 중심 크롭
    ref_path = Path(r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇\kmarket-marketing-engine\data\gemini_generated_media\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png")
    if not ref_path.exists():
        print(f"❌ 씬 5번 사진을 찾을 수 없습니다: {ref_path}")
        return

    print(f"⏳ [3/4] 씬 5번 원본 사진 특징 추출 준비: {ref_path.name}")
    ref_img = Image.open(ref_path).convert("RGB")
    # 상단 50% 영역 (얼굴 및 어깨) 크롭하여 전달
    w, h = ref_img.size
    face_crop = ref_img.crop((int(w * 0.1), int(h * 0.05), int(w * 0.9), int(h * 0.65))).resize((512, 512))

    # 4. 5060 Ti CUDA 렌더링: 공원에서 버스 타는 사진
    prompt = (
        "masterpiece, photorealistic 8k, a beautiful Korean woman in her early 30s, "
        "stepping onto and boarding a modern green city bus at an outdoor bus stop near a sunny park, "
        "green park trees and lush lawn in the background, bright morning sunlight, "
        "wearing casual clothing, looking slightly back with a warm smile, highly detailed face, sharp focus, 8k uhd"
    )
    negative_prompt = (
        "deformed, bad anatomy, bad hands, missing fingers, extra fingers, blurry, lowres, "
        "cartoon, 3d, illustration, painting, distorted face, indoor, kitchen"
    )

    print("🎨 [4/4] 5060 Ti 그래픽카드가 직접 25단계 디퓨전 노이즈 제거 렌더링 실행 중...")
    start_gen = time.time()
    generator = torch.Generator(device="cuda").manual_seed(42)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        ip_adapter_image=face_crop,
        num_inference_steps=28,
        guidance_scale=7.0,
        height=768,
        width=512,
        generator=generator
    ).images[0]

    gen_elapsed = round(time.time() - start_gen, 2)
    print(f"⚡ [렌더링 완료] 5060 Ti CUDA 소요 시간: {gen_elapsed}초!")

    # 5. 바탕화면으로 직접 저장
    out_name = "5060Ti_직접생성_씬5_공원버스.jpg"
    dest_onedrive = Path(r"C:\Users\zkfnt\OneDrive\Desktop") / out_name
    dest_local = Path(r"C:\Users\zkfnt\Desktop") / out_name
    dest_artifact = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\a9a6db25-d3f1-4ca8-8b12-b98e2235f511") / out_name

    result.save(str(dest_onedrive), "JPEG", quality=95)
    result.save(str(dest_local), "JPEG", quality=95)
    result.save(str(dest_artifact), "JPEG", quality=95)

    print("=" * 65)
    print("🎉 [대성공!] 5060 Ti 그래픽카드로 '공원 버스 탑승' 실사 사진 직접 렌더링 완료!")
    print(f"🏆 [바탕화면 완성 파일]: {dest_onedrive}")
    print("=" * 65)

if __name__ == "__main__":
    main()
