# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/face_swap_hd.py
페이스 스왑 + GFPGAN 얼굴 고화질 복원 파이프라인
  1. InsightFace inswapper로 얼굴 스왑
  2. GFPGAN으로 얼굴 영역 고화질 복원 (128px → 512px급)
"""
import sys, cv2, numpy as np
from pathlib import Path
import insightface
from insightface.app import FaceAnalysis

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def imread_u(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)

def imwrite_u(path, img, quality=95):
    ext = Path(path).suffix
    ret, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    buf.tofile(str(path))


def enhance_face_gfpgan(img_bgr):
    """GFPGAN으로 얼굴 복원 (고화질)"""
    from gfpgan import GFPGANer
    enhancer = GFPGANer(
        model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
        upscale=1,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=None
    )
    _, _, restored = enhancer.enhance(
        img_bgr,
        has_aligned=False,
        only_center_face=False,
        paste_back=True
    )
    return restored


def main():
    print("=" * 60)
    print("[Face Swap HD] InsightFace + GFPGAN 고화질 복원")
    print("=" * 60)

    art = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\a9a6db25-d3f1-4ca8-8b12-b98e2235f511")
    source_path = Path(
        r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇"
        r"\kmarket-marketing-engine\data\gemini_generated_media"
        r"\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"
    )
    target_path = art / "5060Ti_직접렌더링_씬5_공원버스.jpg"
    model_path = r"C:\Users\zkfnt\.insightface\models\inswapper_128.onnx"

    # 1. FaceAnalysis 로드
    print("[1/5] FaceAnalysis 로드...")
    app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider","CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))

    # 2. inswapper 로드
    print("[2/5] inswapper 로드...")
    swapper = insightface.model_zoo.get_model(model_path, providers=["CUDAExecutionProvider","CPUExecutionProvider"])

    # 3. 소스 얼굴 감지
    print("[3/5] 소스(씬5) 얼굴 감지...")
    src_img = imread_u(source_path)
    src_faces = app.get(src_img)
    if not src_faces:
        print("  소스 얼굴 감지 실패"); return
    src_face = sorted(src_faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]
    print("  소스 얼굴 OK")

    # 4. 타겟 스왑
    print("[4/5] 타겟 얼굴 스왑...")
    tgt_img = imread_u(target_path)
    tgt_faces = app.get(tgt_img)
    if not tgt_faces:
        print("  타겟 얼굴 감지 실패"); return
    tgt_face = sorted(tgt_faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]
    result = tgt_img.copy()
    result = swapper.get(result, tgt_face, src_face, paste_back=True)
    print("  스왑 완료")

    # 5. GFPGAN 고화질 복원
    print("[5/5] GFPGAN 얼굴 고화질 복원 중...")
    result_hd = enhance_face_gfpgan(result)
    print("  GFPGAN 복원 완료!")

    # 저장
    out_hd = art / "faceswap_hd_result.jpg"
    out_desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop\FaceSwap_HD_씬5_공원버스.jpg")
    imwrite_u(out_hd, result_hd, quality=95)
    imwrite_u(out_desktop, result_hd, quality=95)

    print("=" * 60)
    print("[SUCCESS] 페이스 스왑 + GFPGAN 고화질 복원 완료!")
    print("바탕화면:", out_desktop)
    print("=" * 60)


if __name__ == "__main__":
    main()
