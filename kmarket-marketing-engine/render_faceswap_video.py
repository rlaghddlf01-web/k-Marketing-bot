# -*- coding: utf-8 -*-
"""
render_faceswap_video.py - 고화질 실제 비디오 기반 페이스스왑 동영상 렌더링
원본의 자연스러운 손짓, 스마트폰, 호흡, 움직임을 100% 유지하면서 인물 얼굴만 교체
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import numpy as np
import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo.inswapper import INSwapper
import imageio_ffmpeg

# 윈도우 UTF-8 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DRIVING_VIDEO = r"D:\다운로드\Tax Refund Ad for Thai Workers in Korea_1080p.mp4"
TARGET_IMAGE = r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇\kmarket-marketing-engine\scratch\test_viet.jpg"
MODEL_PATH = r"D:\faceswap_models\inswapper_128.onnx"

OUTPUT_DIR = Path(r"C:\Users\zkfnt\Desktop")
OUTPUT_VIDEO = OUTPUT_DIR / "페이스스왑_실제비디오_인물교체_성공.mp4"
TEMP_VIDEO = OUTPUT_DIR / "temp_swap_no_audio.mp4"

def main():
    print("=" * 65)
    print("🎬 [FaceSwap] 고화질 실제 비디오 기반 인물 얼굴 교체 렌더링 시작")
    print("=" * 65)
    start_time = time.time()

    # 1. 모델 초기화
    print("⏳ [1/5] 얼굴 감지기 및 페이스스왑 모델 초기화 중...")
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=0, det_size=(640, 640))
    swapper = INSwapper(MODEL_PATH)
    print("✅ 모델 초기화 완료!")

    # 2. 타깃 인물 사진 얼굴 추출
    print(f"⏳ [2/5] 타깃 얼굴 분석 중: {Path(TARGET_IMAGE).name}")
    target_data = np.fromfile(TARGET_IMAGE, dtype=np.uint8)
    target_img = cv2.imdecode(target_data, cv2.IMREAD_COLOR)
    target_faces = app.get(target_img)
    if not target_faces:
        print("❌ 타깃 이미지에서 얼굴을 찾지 못했습니다.")
        return
    source_face = sorted(target_faces, key=lambda x: (x['bbox'][2]-x['bbox'][0])*(x['bbox'][3]-x['bbox'][1]), reverse=True)[0]
    print("✅ 타깃 인물 얼굴 임베딩 추출 완료!")

    # 3. 원본 비디오 열기
    print(f"⏳ [3/5] 원본 비디오 로드 중: {Path(DRIVING_VIDEO).name}")
    cap = cv2.VideoCapture(DRIVING_VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 6초 분량 (150 프레임) 데모 렌더링
    max_frames = 150
    print(f"• 규격: {width}x{height} | {fps} FPS | 렌더링 프레임: {max_frames}프레임 ({max_frames/fps:.1f}초)")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(str(TEMP_VIDEO), fourcc, fps, (width, height))

    # 4. 프레임 단위 페이스스왑 처리
    print("⏳ [4/5] 프레임 단위 초정밀 얼굴 교체 연산 중 (손짓·호흡·움직임 완벽 보존)...")
    frame_idx = 0
    while cap.isOpened() and frame_idx < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        faces = app.get(frame)
        if faces:
            # 가장 큰 얼굴 (주인공) 감지 및 교체
            main_face = sorted(faces, key=lambda x: (x['bbox'][2]-x['bbox'][0])*(x['bbox'][3]-x['bbox'][1]), reverse=True)[0]
            frame = swapper.get(frame, main_face, source_face, paste_back=True)

        out_writer.write(frame)
        frame_idx += 1
        if frame_idx % 25 == 0:
            sys.stdout.write(f" [{frame_idx}/{max_frames} 프레임 ({frame_idx/max_frames*100:.0f}%)]")
            sys.stdout.flush()

    cap.release()
    out_writer.release()
    print("\n✅ 비디오 프레임 변환 완료!")

    # 5. 오디오 결합 (FFmpeg)
    print("⏳ [5/5] 오디오 합성 및 H.264 인코딩 마스터링 중...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(TEMP_VIDEO),
        "-ss", "0", "-t", f"{max_frames/fps:.2f}",
        "-i", DRIVING_VIDEO,
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(OUTPUT_VIDEO)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 임시 비디오 삭제
    if TEMP_VIDEO.exists():
        try:
            TEMP_VIDEO.unlink()
        except Exception:
            pass

    elapsed = time.time() - start_time
    print("=" * 65)
    print(f"🎉 [페이스스왑 렌더링 대성공!] 총 {elapsed:.1f}초 소요")
    print(f"🏆 [바탕화면 완성 파일]:")
    print(f"   ➔ {OUTPUT_VIDEO} ({OUTPUT_VIDEO.stat().st_size / (1024*1024):.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    main()
