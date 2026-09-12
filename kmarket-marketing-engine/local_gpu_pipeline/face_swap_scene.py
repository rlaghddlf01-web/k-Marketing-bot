# -*- coding: utf-8 -*-
"""
local_gpu_pipeline/face_swap_scene.py
InsightFace 페이스 스왑:
  소스: 씬 5번 원본 얼굴
  타겟: 첫 번째 생성된 공원버스 씬
  결과: 씬 5번 얼굴 + 자연스러운 공원버스 씬
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


def main():
    print("=" * 60)
    print("[Face Swap] InsightFace 페이스 스왑 시작")
    print("=" * 60)

    # 소스 이미지: 씬 5번 원본 (교체할 얼굴)
    source_path = Path(
        r"c:\Users\zkfnt\OneDrive\Desktop\ktrs 마케팅 봇"
        r"\kmarket-marketing-engine\data\gemini_generated_media"
        r"\kmarket\kmarket_ko_univ_cau_heukseok_s5_m_9x16.png"
    )
    # 타겟 이미지: 첫 번째 생성된 자연스러운 공원버스 씬
    target_path = Path(r"C:\Users\zkfnt\OneDrive\Desktop\5060Ti_직접렌더링_씬5_공원버스.jpg")

    if not source_path.exists():
        print("소스 이미지 없음:", source_path)
        return
    if not target_path.exists():
        print("타겟 이미지 없음:", target_path)
        return

    print("[1/4] FaceAnalysis 모델 로드 중...")
    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("[1/4] 완료")

    print("[2/4] inswapper_128 모델 로드 중...")
    swapper = insightface.model_zoo.get_model(
        "inswapper_128.onnx",
        download=True,
        download_zip=False
    )
    print("[2/4] 완료")

    # 소스 얼굴 감지
    print("[3/4] 소스(씬5) 얼굴 감지 중...")
    src_img = cv2.imread(str(source_path))
    src_faces = app.get(src_img)
    if not src_faces:
        print("  소스 얼굴 감지 실패")
        return
    src_face = sorted(src_faces, key=lambda x: x.bbox[2] * x.bbox[3], reverse=True)[0]
    print("  소스 얼굴 감지 성공:", src_face.bbox.astype(int))

    # 타겟 얼굴 감지
    print("[4/4] 타겟(공원버스씬) 얼굴 감지 + 스왑 중...")
    tgt_img = cv2.imread(str(target_path))
    tgt_faces = app.get(tgt_img)
    if not tgt_faces:
        print("  타겟 얼굴 감지 실패")
        return
    tgt_face = sorted(tgt_faces, key=lambda x: x.bbox[2] * x.bbox[3], reverse=True)[0]
    print("  타겟 얼굴 감지 성공:", tgt_face.bbox.astype(int))

    # 페이스 스왑 실행
    result = tgt_img.copy()
    result = swapper.get(result, tgt_face, src_face, paste_back=True)
    print("[완료] 페이스 스왑 완료!")

    # 저장
    out_desktop = Path(r"C:\Users\zkfnt\OneDrive\Desktop\FaceSwap_씬5_공원버스.jpg")
    out_artifact = Path(
        r"C:\Users\zkfnt\.gemini\antigravity-ide\brain"
        r"\a9a6db25-d3f1-4ca8-8b12-b98e2235f511\faceswap_result.jpg"
    )
    cv2.imwrite(str(out_desktop), result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(str(out_artifact), result, [cv2.IMWRITE_JPEG_QUALITY, 95])

    print("=" * 60)
    print("[SUCCESS] 페이스 스왑 완료!")
    print("바탕화면:", out_desktop)
    print("=" * 60)


if __name__ == "__main__":
    main()
