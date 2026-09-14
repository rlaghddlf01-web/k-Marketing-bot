"""
WanFaceMaskInpaintService - 🎭 [Wan 2.1 공식 논문 기반 얼굴 100% 보존 인페인팅 엔진]
- 알리바바 Wan 2.1 공식 논문 (Section 5.4 Video Personalization) VAE Latent Mask Inpainting 원리 구현
- 1번 슬라이드 마스터 사진에서 얼굴/헤어 영역을 분리 (Denoise = 0, 100% 무결 보존)
- 목 아래 몸통(의상/포즈)과 배경은 완전 백지 상태에서 새로 생성 (Denoise = 1.0, 100% 자유 전환)
- 독립 모듈로 분리되어 기존 파이프라인의 안정성을 100% 유지
"""

import os
import cv2
import json
import time
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter
import insightface
from insightface.app import FaceAnalysis

logger = logging.getLogger("WanFaceMaskInpaintService")


class WanFaceMaskInpaintService:
    """Wan 2.1 전용 얼굴 100% 보존 + 의상/배경 100% 자유 전환 인페인팅 서비스"""

    def __init__(self, comfy_input_dir: str = r"D:\ComfyUI_Wan_Engine\ComfyUI\input"):
        self.comfy_input_dir = comfy_input_dir
        os.makedirs(self.comfy_input_dir, exist_ok=True)
        # InsightFace CPU 검출기 초기화 (가볍고 정확함)
        self._face_app = None

    def _get_face_app(self) -> FaceAnalysis:
        if self._face_app is None:
            self._face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
            self._face_app.prepare(ctx_id=0, det_size=(640, 640))
        return self._face_app

    def create_face_mask(
        self,
        ref_image: Image.Image,
        target_width: int = 832,
        target_height: int = 1216
    ) -> Tuple[Image.Image, Image.Image, bool]:
        """
        1번 마스터 이미지에서 얼굴 영역을 검출하여 인페인팅용 마스크 생성:
        - mask = 0 (검정색): 얼굴 및 머리카락 영역 ➔ Denoise 0 (100% 원본 유지)
        - mask = 255 (흰색): 턱 아래 몸통 및 배경 ➔ Denoise 1.0 (새로운 옷/배경 생성)
        반환값: (리사이즈된 레퍼런스 이미지, 마스크 이미지, 얼굴 검출 성공 여부)
        """
        # 리사이즈
        ref_resized = ref_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        ref_bgr = cv2.cvtColor(np.array(ref_resized), cv2.COLOR_RGB2BGR)

        app = self._get_face_app()
        faces = app.get(ref_bgr)

        # 마스크 기본값: 255 (전부 새로 그리기)
        mask_img = Image.new("L", (target_width, target_height), 255)

        if not faces:
            logger.warning("⚠️ [WanFaceMaskInpaint] 얼굴 검출 실패 → 기본 상단 마스크 폴백")
            # 폴백: 상단 중앙 20% 영역을 얼굴로 가정하여 타원 마스크
            draw = ImageDraw.Draw(mask_img)
            cx, cy = target_width // 2, int(target_height * 0.28)
            rx, ry = int(target_width * 0.18), int(target_height * 0.16)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=0)
            mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=15))
            return ref_resized, mask_img, False

        face = faces[0]
        bbox = face.bbox.astype(int) # [x1, y1, x2, y2]
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]

        # 머리카락 상단 및 양옆은 포함하되, 턱 아래 옷깃은 제외하는 정밀 타원 영역 계산
        pad_x = int(bw * 0.18)
        pad_y_top = int(bh * 0.35)
        pad_y_bottom = int(bh * 0.05)

        fx1 = max(0, bbox[0] - pad_x)
        fy1 = max(0, bbox[1] - pad_y_top)
        fx2 = min(target_width, bbox[2] + pad_x)
        fy2 = min(target_height, bbox[3] + pad_y_bottom)

        draw = ImageDraw.Draw(mask_img)
        draw.ellipse([fx1, fy1, fx2, fy2], fill=0)
        # 15px 가우시안 블러로 목둘레 경계선 자연스러운 블렌딩
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=15))

        logger.info(f"🎭 [WanFaceMaskInpaint] 얼굴 마스크 정밀 생성 완료 (bbox: {bbox})")
        return ref_resized, mask_img, True

    def build_inpaint_workflow(
        self,
        ref_filename: str,
        mask_filename: str,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        prefix: str,
        width: int = 832,
        height: int = 1216,
        steps: int = 25,
        cfg: float = 3.8
    ) -> dict:
        """
        ComfyUI Wan 2.1 SetLatentNoiseMask 기반 인페인팅 워크플로우 딕셔너리 구성:
        - VAEEncode(Slide 1) ➔ SetLatentNoiseMask(Face Mask) ➔ KSampler(denoise=1.0)
        """
        return {
            "1":  {"class_type": "UnetLoaderGGUF",  "inputs": {"unet_name": "wan2.1-t2v-14b-Q4_0.gguf"}},
            "2":  {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
            "3":  {"class_type": "CLIPLoader",       "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "4":  {"class_type": "VAELoader",        "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
            "5":  {"class_type": "CLIPTextEncode",   "inputs": {"text": positive_prompt, "clip": ["3", 0]}},
            "6":  {"class_type": "CLIPTextEncode",   "inputs": {"text": negative_prompt, "clip": ["3", 0]}},
            "7":  {
                "class_type": "WanImageToVideo",
                "inputs": {
                    "positive": ["5", 0], "negative": ["6", 0], "vae": ["4", 0],
                    "width": width, "height": height, "length": 1, "batch_size": 1
                }
            },
            "11": {"class_type": "LoadImage",  "inputs": {"image": ref_filename}},
            "12": {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["11", 0], "width": width, "height": height,
                    "upscale_method": "lanczos", "crop": "center"
                }
            },
            "13": {"class_type": "VAEEncode", "inputs": {"pixels": ["12", 0], "vae": ["4", 0]}},
            "14": {"class_type": "LoadImageMask", "inputs": {"image": mask_filename, "channel": "red"}},
            "15": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["13", 0], "mask": ["14", 0]}},
            "8":  {
                "class_type": "KSampler",
                "inputs": {
                    "model":        ["2", 0],
                    "positive":     ["7", 0],
                    "negative":     ["7", 1],
                    "latent_image": ["15", 0],
                    "seed": seed, "steps": steps, "cfg": cfg,
                    "sampler_name": "uni_pc", "scheduler": "simple",
                    "denoise": 1.0  # 마스크 외부(몸통/배경) 100% 완전 백지 재창조
                }
            },
            "9":  {"class_type": "VAEDecode",  "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
            "10": {"class_type": "SaveImage",  "inputs": {"images": ["9", 0], "filename_prefix": prefix}}
        }
