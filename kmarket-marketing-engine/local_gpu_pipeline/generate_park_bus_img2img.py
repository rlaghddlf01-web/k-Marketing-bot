# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/generate_park_bus_img2img.py
5060 Ti 16GB 그래픽카드 실사 디퓨전(Realistic Vision) 직접 렌더링
씬 5번 인물 원본을 Init 이미지로 전달하여 이목구비를 유지하고,
공원 앞 버스 탑승 배경 및 옷을 5060 Ti CUDA 코어로 직접 생성
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

from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler

def main():
    print("=" * 65)
    print("🚀 [5060 Ti 16GB] 로컬 실사 디퓨전 공원 버스 씬 렌더링 가동")
    print(f"• 그래픽카드: {torch.cuda.get_device_name(0)} (VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB)")
    print("=" * 65)

    # 1. 씬 5번 인물 사진 로드
    ref_path = Path(r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇\kmarket-marketing-engine\data\gemini_generated_media\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png")
    if not ref_path.exists():
        print(f"❌ 씬 5번 사진 없음: {ref_path}")
        return

    print(f"🖼️ [1/3] 씬 5번 인물 원본 로드: {ref_path.name}")
    init_image = Image.open(ref_path).convert("RGB").resize((512, 768))

    # 2. 로컬 캐시된 Realistic Vision 모델 로드 (다운로드 0초, VRAM 즉시 탑재)
    model_id = "SG161222/Realistic_Vision_V5.1_noVAE"
    print(f"⏳ [2/3] 5060 Ti VRAM에 Realistic Vision 모델 탑재 중...")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
        local_files_only=True
    ).to("cuda")
    pipe.enable_attention_slicing()
    print("✅ [2/3] 5060 Ti VRAM 탑재 완료!")

    # 3. 5060 Ti CUDA 직접 렌더링: 공원에서 버스 타는 사진
    prompt = (
        "masterpiece, photorealistic 8k, this exact Korean woman stepping onto and boarding a green city bus "
        "at an outdoor bus stop next to a beautiful sunny green park with tall trees and green lawn, "
        "bright natural daylight, wearing casual outdoor jacket, smiling warmly looking back towards camera, "
        "highly detailed face, natural skin texture, sharp focus, cinematic 8k uhd"
    )
    negative_prompt = (
        "indoor, room, kitchen, rice cooker, furniture, deformed, bad anatomy, bad hands, "
        "blurry, lowres, cartoon, painting, 3d, bad eyes, distorted"
    )

    print("🎨 [3/3] 5060 Ti CUDA 코어가 28단계 디퓨전 노이즈 제거 직접 렌더링 중...")
    start_time = time.time()
    
    # 2가지 강도(0.55, 0.65)로 렌더링하여 얼굴 보존율과 배경 변환 완성도 동시 확보
    generator = torch.Generator(device="cuda").manual_seed(12345)
    
    out_img = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=init_image,
        strength=0.60,
        num_inference_steps=25,
        guidance_scale=7.5,
        generator=generator
    ).images[0]

    elapsed = round(time.time() - start_time, 2)
    print(f"⚡ [렌더링 완료!] 5060 Ti 소요 시간: {elapsed}초")

    # 4. 바탕화면으로 직접 저장
    out_name = "5060Ti_직접렌더링_씬5_공원버스.jpg"
    dest_onedrive = Path(r"C:\Users\zkfnt\OneDrive\Desktop") / out_name
    dest_local = Path(r"C:\Users\zkfnt\Desktop") / out_name
    dest_artifact = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\a9a6db25-d3f1-4ca8-8b12-b98e2235f511") / out_name

    out_img.save(str(dest_onedrive), "JPEG", quality=95)
    out_img.save(str(dest_local), "JPEG", quality=95)
    out_img.save(str(dest_artifact), "JPEG", quality=95)

    print("=" * 65)
    print("🎉 [대성공!] 5060 Ti 그래픽카드로 '공원 버스 탑승' 실사 사진 직접 렌더링 완료!")
    print(f"🏆 [바탕화면 완성 파일]: {dest_onedrive}")
    print("=" * 65)

if __name__ == "__main__":
    main()
