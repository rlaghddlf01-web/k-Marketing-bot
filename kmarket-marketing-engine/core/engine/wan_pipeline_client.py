# -*- coding: utf-8 -*-
"""
WanPipelineClient - 🎬 [ComfyUI Wan2.1 T2I & Wan2.2 S2V 통합 클라이언트]
- Wan 2.1 14B Q4_0 (1-frame T2I 마스터컷 생성: 극실사 인물 사진)
- Wan 2.2 S2V 14B Q4_0 (81프레임 립싱크 숏폼 영상 생성)
- FFmpeg 16fps 무손실 오디오/비디오 Muxing 및 바탕화면 출력
"""

import os
import sys
import glob
import json
import time
import urllib.request
import urllib.parse
import subprocess
from typing import Dict, Any, List, Optional
from PIL import Image
import imageio_ffmpeg


class WanPipelineClient:
    """로컬 ComfyUI Wan 영상/이미지 생성 클라이언트"""

    def __init__(self, host: str = "http://127.0.0.1:8188"):
        self.host = host
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.comfy_input_dir = r"D:\ComfyUI_Wan_Engine\ComfyUI\input"
        self.comfy_output_dir = r"D:\ComfyUI_Wan_Engine\ComfyUI\output"
        os.makedirs(self.comfy_input_dir, exist_ok=True)
        os.makedirs(self.comfy_output_dir, exist_ok=True)

    def check_health(self, auto_start: bool = False) -> bool:
        try:
            with urllib.request.urlopen(f"{self.host}/system_stats", timeout=3) as resp:
                stats = json.loads(resp.read().decode('utf-8'))
                if stats.get("system", {}).get("os") is not None:
                    return True
        except Exception:
            pass

        if auto_start:
            from core.engine.comfy_process_manager import ComfyProcessManager
            return ComfyProcessManager.ensure_running()
        return False

    def submit_and_wait(self, prompt_dict: Dict[str, Any], prefix: str, timeout_sec: int = 1800) -> List[str]:
        """ComfyUI에 작업을 제출하고 완료될 때까지 대기 후 생성된 이미지 경로 반환"""
        # 이전 프레임 정리
        for f in glob.glob(os.path.join(self.comfy_output_dir, f"{prefix}_*.png")):
            try:
                os.remove(f)
            except Exception:
                pass

        data = json.dumps({"prompt": prompt_dict}).encode('utf-8')
        req = urllib.request.Request(f"{self.host}/prompt", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            prompt_id = res.get("prompt_id")

        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            time.sleep(3)
            try:
                with urllib.request.urlopen(f"{self.host}/history/{prompt_id}") as resp:
                    hist = json.loads(resp.read().decode('utf-8'))
                    if prompt_id in hist:
                        status = hist[prompt_id].get("status", {})
                        if status.get("completed", False):
                            break
                        if status.get("status_str") == "error":
                            raise RuntimeError(f"ComfyUI Job Error: {status.get('messages')}")
            except urllib.error.URLError:
                pass

        frames = sorted(glob.glob(os.path.join(self.comfy_output_dir, f"{prefix}_*.png")))
        return frames

    def generate_t2i_master(
        self,
        positive_prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 832,
        height: int = 1216,
        seed: Optional[int] = None,
        prefix: str = "wan_t2i_master"
    ) -> str:
        """Wan 2.1 14B Q4_0 1-Frame Native T2I 고화질 마스터 사진 생성"""
        if seed is None:
            seed = int(time.time()) % 100000000

        neg = negative_prompt or (
            "blurry hair, out of focus hair, smudged hair, back of phone, rear camera lenses, back cover, "
            "phone case back, cartoon, drawing, anime, 3d render, illustration, blurry, low quality, bad lighting, "
            "chinese influencer, pale white skin, sharp triangular chin, deformed hands, extra fingers"
        )

        workflow = {
            "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "wan2.1-t2v-14b-Q4_0.gguf"}},
            "2": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
            "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "4": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"text": positive_prompt, "clip": ["3", 0]}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["3", 0]}},
            "7": {
                "class_type": "WanImageToVideo",
                "inputs": {
                    "positive": ["5", 0], "negative": ["6", 0], "vae": ["4", 0],
                    "width": width, "height": height, "length": 1, "batch_size": 1
                }
            },
            "8": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["2", 0], "positive": ["7", 0], "negative": ["7", 1],
                    "latent_image": ["7", 2], "seed": seed, "steps": 25, "cfg": 3.2,
                    "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0
                }
            },
            "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
            "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}}
        }

        frames = self.submit_and_wait(workflow, prefix=prefix)
        if not frames:
            raise RuntimeError("Wan 2.1 T2I 마스터 컷 생성에 실패했습니다.")
        return frames[0]

    def generate_t2i_img2img(
        self,
        positive_prompt: str,
        reference_image_path: str,
        negative_prompt: Optional[str] = None,
        denoise: float = 0.70,
        width: int = 832,
        height: int = 1216,
        seed: Optional[int] = None,
        prefix: str = "wan_img2img"
    ) -> str:
        """
        WAN img2img - 동일 인물 유지 씬 전환기:
        - 슬라이드 1번 생성 사진을 레퍼런스로 받아 VAEEncode
        - denoise=0.70: 인물 외모(얼굴/헤어/피부) 유지 + 배경/자세 변경 최적 구간
        - 슬라이드 2번(공장 현장), 4번(귀국/감동) 전용
        """
        import shutil as _shutil

        if seed is None:
            seed = int(time.time()) % 100000000

        neg = negative_prompt or (
            "blurry, out of focus, cartoon, drawing, anime, 3d render, illustration, "
            "bad lighting, pale white skin, deformed hands, extra fingers, different person, "
            "character change, inconsistent face"
        )

        # 레퍼런스 이미지를 ComfyUI input 폴더로 복사
        ref_filename = f"ref_{prefix}.png"
        ref_dest = os.path.join(self.comfy_input_dir, ref_filename)
        _shutil.copy2(reference_image_path, ref_dest)

        workflow = {
            "1":  {"class_type": "UnetLoaderGGUF",  "inputs": {"unet_name": "wan2.1-t2v-14b-Q4_0.gguf"}},
            "2":  {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
            "3":  {"class_type": "CLIPLoader",       "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "4":  {"class_type": "VAELoader",        "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
            "5":  {"class_type": "CLIPTextEncode",   "inputs": {"text": positive_prompt, "clip": ["3", 0]}},
            "6":  {"class_type": "CLIPTextEncode",   "inputs": {"text": neg,             "clip": ["3", 0]}},
            # WanImageToVideo: positive/negative conditioning 전용 (latent은 아래 VAEEncode로 대체)
            "7":  {
                "class_type": "WanImageToVideo",
                "inputs": {
                    "positive": ["5", 0], "negative": ["6", 0], "vae": ["4", 0],
                    "width": width, "height": height, "length": 1, "batch_size": 1
                }
            },
            # 레퍼런스 이미지 로드 → 리사이즈 → VAEEncode (img2img 시작 레이턴트)
            "11": {"class_type": "LoadImage",  "inputs": {"image": ref_filename}},
            "12": {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["11", 0], "width": width, "height": height,
                    "upscale_method": "lanczos", "crop": "center"
                }
            },
            "13": {"class_type": "VAEEncode", "inputs": {"pixels": ["12", 0], "vae": ["4", 0]}},
            # KSampler: WanImageToVideo conditioning + VAEEncode latent + denoise
            "8":  {
                "class_type": "KSampler",
                "inputs": {
                    "model":        ["2", 0],
                    "positive":     ["7", 0],
                    "negative":     ["7", 1],
                    "latent_image": ["13", 0],  # T2I noise latent 대신 레퍼런스 VAE latent
                    "seed": seed, "steps": 25, "cfg": 3.2,
                    "sampler_name": "uni_pc", "scheduler": "simple",
                    "denoise": denoise
                }
            },
            "9":  {"class_type": "VAEDecode",  "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
            "10": {"class_type": "SaveImage",  "inputs": {"images": ["9", 0], "filename_prefix": prefix}}
        }

        frames = self.submit_and_wait(workflow, prefix=prefix)
        if not frames:
            raise RuntimeError("WAN img2img 동일 인물 씬 전환 생성 실패")
        return frames[0]

    def generate_face_inpaint_photo(
        self,
        reference_image: Image.Image,
        positive_prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 832,
        height: int = 1216,
        seed: Optional[int] = None,
        prefix: str = "wan_face_inpaint"
    ) -> str:
        """
        알리바바 Wan 2.1 공식 논문 기반 얼굴 100% 보존 인페인팅:
        - 얼굴/헤어는 1번 사진 100% 고정 (Denoise 0)
        - 몸통(옷/포즈)과 배경은 새 프롬프트대로 100% 재창조 (Denoise 1.0)
        """
        from core.engine.wan_face_mask_inpaint_service import WanFaceMaskInpaintService
        service = WanFaceMaskInpaintService(comfy_input_dir=self.comfy_input_dir)

        if seed is None:
            seed = int(time.time()) % 100000000

        neg = negative_prompt or (
            "bobblehead, big head, oversized head, disproportionate body, "
            "extreme close-up, macro shot, cropped head, zoomed-in face, face taking up entire frame, "
            "blurry, out of focus, cartoon, drawing, anime, 3d render, illustration, "
            "bad lighting, pale white skin, deformed hands, extra fingers"
        )

        ref_filename = f"ref_{prefix}.png"
        mask_filename = f"mask_{prefix}.png"

        # 1. 마스크 생성 및 ComfyUI input 저장
        ref_resized, mask_img, _ = service.create_face_mask(
            ref_image=reference_image,
            target_width=width,
            target_height=height
        )
        ref_dest = os.path.join(self.comfy_input_dir, ref_filename)
        mask_dest = os.path.join(self.comfy_input_dir, mask_filename)

        ref_resized.save(ref_dest, "PNG")
        mask_img.save(mask_dest, "PNG")

        # 2. 워크플로우 구성
        workflow = service.build_inpaint_workflow(
            ref_filename=ref_filename,
            mask_filename=mask_filename,
            positive_prompt=positive_prompt,
            negative_prompt=neg,
            seed=seed,
            prefix=prefix,
            width=width,
            height=height
        )

        # 3. 제출 및 대기
        frames = self.submit_and_wait(workflow, prefix=prefix)
        if not frames:
            raise RuntimeError("WAN 얼굴 보존 인페인팅 생성 실패")
        return frames[0]

    def generate_s2v_video(
        self,
        image_name: str,
        audio_name: str,
        prompt_text: str,
        output_mp4_path: str,
        negative_text: Optional[str] = None,
        seed: int = 2026,
        width: int = 480,
        height: int = 832,
        frames: int = 81,
        prefix: str = "s2v_run"
    ) -> str:
        """Wan 2.2 S2V 립싱크 렌더링 후 MP4 완성 파일 생성"""
        neg = negative_text or "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景"

        workflow = {
            "61": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "Wan2.2-S2V-14B-Q4_0.gguf"}},
            "54": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["61", 0], "shift": 8.0}},
            "57": {"class_type": "AudioEncoderLoader", "inputs": {"audio_encoder_name": "wav2vec2_large_english_fp16.safetensors"}},
            "58": {"class_type": "LoadAudio", "inputs": {"audio": audio_name}},
            "56": {"class_type": "AudioEncoderEncode", "inputs": {"audio_encoder": ["57", 0], "audio": ["58", 0]}},
            "62": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["62", 0], "text": prompt_text}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["62", 0], "text": neg}},
            "63": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
            "52": {"class_type": "LoadImage", "inputs": {"image": image_name}},
            "55": {
                "class_type": "WanSoundImageToVideo",
                "inputs": {
                    "positive": ["6", 0], "negative": ["7", 0], "vae": ["63", 0],
                    "width": width, "height": height, "length": frames, "batch_size": 1,
                    "audio_encoder_output": ["56", 0], "ref_image": ["52", 0]
                }
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["54", 0], "positive": ["55", 0], "negative": ["55", 1],
                    "latent_image": ["55", 2], "seed": seed, "steps": 20, "cfg": 6.0,
                    "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0
                }
            },
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["63", 0]}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}}
        }

        generated_frames = self.submit_and_wait(workflow, prefix=prefix)
        if not generated_frames:
            raise RuntimeError("Wan 2.2 S2V 렌더링 프레임이 생성되지 않았습니다.")

        # FFmpeg Muxing
        list_file = os.path.join(self.comfy_output_dir, f"concat_{prefix}.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for frame in generated_frames:
                clean_f = frame.replace("\\", "/")
                f.write(f"file '{clean_f}'\n")
                f.write("duration 0.0625\n")
            last_frame = generated_frames[-1].replace("\\", "/")
            f.write(f"file '{last_frame}'\n")

        audio_full_path = os.path.join(self.comfy_input_dir, audio_name)
        os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)

        cmd = [
            self.ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-i", audio_full_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_mp4_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_mp4_path
