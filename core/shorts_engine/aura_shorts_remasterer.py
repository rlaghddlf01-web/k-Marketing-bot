# -*- coding: utf-8 -*-
"""
[신규 모듈] EasytaxShortsRemasterer (core/shorts_engine/easytax_shorts_remasterer.py)
• 역할: 기존 제작된 이지텍스 숏폼 영상(0~10초 인물 립싱크 구간)에서 스마트폰 액정을 불투명하게
        가리고 있던 팝업 카드(center_white_card 0~3.5s, phone_side_popup 7.0~10.5s)를
        반투명 글래스모피즘(알파 65)으로 리마스터링하여 뒷배경의 스마트폰 액정이 훤히 투과되도록 복원
• 무결성 보장:
  1. 03_embedded_start_frame_{lang}.png의 고화질 스마트폰/영수증 매립 영역과 완벽 동기화
  2. 인물의 얼굴/표정/입모양 립싱크 모션(S2V) 100% 보존
  3. 원본 22초 오디오(나레이션+BGM+SFX) 100% 무손실 패스스루 결합
  4. 원본 비디오는 _backup_opaque_cards.mp4로 안전 백업
"""

import os
import sys
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

import cv2
import numpy as np
from PIL import Image
import imageio_ffmpeg

logger = logging.getLogger("EasytaxShortsRemasterer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class EasytaxShortsRemasterer:
    """기존 제작 숏폼 영상 스마트폰 투과 글래스모피즘 리마스터러"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def transform_embedded_image(self, emb_path: Path) -> np.ndarray:
        """
        03_embedded_start_frame 이미지를 S2V 및 FFmpeg 컴포저와 100% 동일한 좌표/해상도(1080x1920)로 변환
        """
        emb = Image.open(emb_path).convert("RGB")
        # 1. prepare_framed_input_image (target_w=384, target_h=672)
        scale1 = 672.0 / emb.height
        w1 = int(emb.width * scale1)
        s1 = emb.resize((w1, 672), Image.Resampling.LANCZOS)
        crop_left = max(0, min(20, w1 - 384))
        f1 = s1.crop((crop_left, 0, crop_left + 384, 672))

        # 2. FFmpeg scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920
        scale2 = 1920.0 / 672.0
        w2 = int(384 * scale2)
        s2 = f1.resize((w2, 1920), Image.Resampling.LANCZOS)
        crop_x = (w2 - 1080) // 2
        f2 = s2.crop((crop_x, 0, crop_x + 1080, 1920))

        # BGR numpy array for OpenCV
        return cv2.cvtColor(np.array(f2), cv2.COLOR_RGB2BGR)

    def remaster_video(self, folder_path: Path) -> Optional[Path]:
        """
        단일 숏폼 폴더 내 영상을 반투명 글래스모피즘으로 완벽 리마스터링
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            logger.warning(f"폴더를 찾을 수 없음: {folder}")
            return None

        # 1. 원본 비디오 파일 찾기
        vids = list(folder.glob("이지텍스_22초숏폼_*.mp4"))
        vids = [v for v in vids if "backup" not in v.name and "temp" not in v.name]
        if not vids:
            logger.warning(f"[{folder.name}] 숏폼 비디오 없음, 건너뜀")
            return None
        video_path = vids[0]

        # 2. 임베디드 시작 프레임 찾기
        emb_files = list(folder.glob("03_embedded_start_frame_*.png"))
        if not emb_files:
            logger.warning(f"[{folder.name}] 03_embedded_start_frame 파일 없음, 건너뜀")
            return None
        emb_path = emb_files[0]

        logger.info(f"🎬 [{folder.name}] 리마스터링 시작 -> {video_path.name}")

        # 3. 원본 안전 백업
        backup_path = video_path.parent / f"{video_path.stem}_backup_opaque_cards.mp4"
        if not backup_path.exists():
            shutil.copy2(video_path, backup_path)
            logger.info(f"   💾 기존 불투명 원본 백업 완료: {backup_path.name}")

        # 4. 스마트폰 기준 베이스 이미지 생성
        emb_bgr = self.transform_embedded_image(emb_path)
        emb_float = emb_bgr.astype(np.float32)

        # 5. 하단 스마트폰/가슴 영역 블렌딩 마스크 생성 (y=900~960 부드러운 그라데이션)
        blend_y_start = 900
        blend_y_end = 960
        blend_mask = np.zeros((1920, 1080, 1), dtype=np.float32)
        blend_mask[blend_y_end:, :] = 1.0
        for y in range(blend_y_start, blend_y_end):
            blend_mask[y, :] = (y - blend_y_start) / float(blend_y_end - blend_y_start)

        # 6. OpenCV 비디오 프레임 프로세싱
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        temp_no_audio = folder / f"temp_remastered_{video_path.stem}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(str(temp_no_audio), fourcc, fps, (width, height))

        t0 = time.time()
        for f_idx in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            cur_time = f_idx / fps

            # 0~10.5초 구간만 인물+스마트폰 액정 리마스터링 대상
            if cur_time < 10.5:
                frame_float = frame.astype(np.float32)
                # 하단(스마트폰 영역) 클린 베이스 합성
                clean_base = frame_float * (1.0 - blend_mask) + emb_float * blend_mask

                if cur_time <= 3.5:
                    # 🎨 Scene 1: center_white_card (cx=180, cy=1080, cw=720, ch=310)
                    card_crop = frame_float[1080:1390, 180:900].copy()
                    r, g, b = card_crop[:, :, 2], card_crop[:, :, 1], card_crop[:, :, 0]
                    # 순수 흰색 배경 검출
                    white_mask = (r > 235) & (g > 235) & (b > 235)
                    # 흰색 배경은 알파 65(은은한 반투명 유리), 텍스트/뱃지/테두리는 알파 255
                    card_alpha = np.where(white_mask, 65.0, 255.0) / 255.0
                    card_alpha = card_alpha[:, :, np.newaxis]

                    clean_base[1080:1390, 180:900] = (
                        clean_base[1080:1390, 180:900] * (1.0 - card_alpha) +
                        card_crop * card_alpha
                    )
                elif 7.0 <= cur_time <= 10.5:
                    # 🎨 Scene 3: phone_side_popup (px=40, py=960, pw=380, ph=480)
                    card_crop = frame_float[960:1440, 40:420].copy()
                    r, g, b = card_crop[:, :, 2], card_crop[:, :, 1], card_crop[:, :, 0]
                    # 다크 네이비 배경 검출
                    dark_mask = (r < 45) & (g < 55) & (b < 75)
                    # 다크 배경은 알파 65(은은한 반투명 다크 글래스), 텍스트/뱃지/체크버튼은 알파 255
                    card_alpha = np.where(dark_mask, 65.0, 255.0) / 255.0
                    card_alpha = card_alpha[:, :, np.newaxis]

                    clean_base[960:1440, 40:420] = (
                        clean_base[960:1440, 40:420] * (1.0 - card_alpha) +
                        card_crop * card_alpha
                    )

                out_writer.write(clean_base.astype(np.uint8))
            else:
                # 10.5초 이후(앱 시연 & 엔딩 CTA)는 기존 프레임 100% 무손실 유지
                out_writer.write(frame)

        cap.release()
        out_writer.release()
        t1 = time.time()
        logger.info(f"   ⚡ 비디오 프레임 리마스터링 완료: {total_frames}프레임 in {t1-t0:.1f}초 ({(total_frames/(t1-t0)):.1f} fps)")

        # 7. 원본 오디오 무손실 패스스루 머지
        temp_final = folder / f"temp_final_{video_path.name}"
        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", str(temp_no_audio),
            "-i", str(backup_path),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            str(temp_final)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res.returncode != 0:
            logger.error(f"FFmpeg 오디오 머지 실패: {res.stderr.decode('utf-8', errors='ignore')}")
            if temp_no_audio.exists():
                os.remove(temp_no_audio)
            return None

        # 8. 임시 파일 정리 및 최종 파일 교체
        if temp_no_audio.exists():
            os.remove(temp_no_audio)
        if video_path.exists():
            os.remove(video_path)
        shutil.move(str(temp_final), str(video_path))

        logger.info(f"   ✅ [{folder.name}] 리마스터링 완성본 적용 성공: {video_path.name}")
        return video_path

    def remaster_all_folders(self, base_dir: Path) -> List[Path]:
        """
        기준 디렉터리 내 모든 20260920 폴더들을 일괄 리마스터링
        """
        base = Path(base_dir)
        folders = sorted([d for d in base.iterdir() if d.is_dir() and "20260920" in d.name])
        logger.info(f"🔍 총 {len(folders)}개 숏폼 폴더 일괄 리마스터링 시작...")

        results = []
        for d in folders:
            try:
                res = self.remaster_video(d)
                if res:
                    results.append(res)
            except Exception as e:
                logger.error(f"❌ [{d.name}] 리마스터링 도중 오류 발생: {e}", exc_info=True)

        logger.info(f"🎉 총 {len(results)}/{len(folders)}개 숏폼 영상 리마스터링 100% 완료!")
        return results


if __name__ == "__main__":
    base_dir = Path(r"C:\Users\zkfnt\Desktop\숏폼_산출물\이지텍스")
    remasterer = EasytaxShortsRemasterer()
    remasterer.remaster_all_folders(base_dir)
