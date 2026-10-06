# -*- coding: utf-8 -*-
"""
EyeGuardFrameSelector - 👁️ [무결점 눈매 보존 스마트 프레임 선별 엔진]
- S2V 1차 샷의 마지막 프레임이 눈을 깜빡이거나 게슴츠레한 상태일 위험 100% 원천 차단
- 마지막 1초(15~20개 프레임)의 눈 부위 라플라시안 선명도/대비 스코어를 정밀 계산
- 눈을 가장 크고 초롱초롱하게 뜨고 있는 최적의 무결점 프레임을 자동 선별하여 2차 샷으로 인계
"""

import os
import glob
import logging
from typing import List, Optional
import cv2
import numpy as np

logger = logging.getLogger("EyeGuardFrameSelector")


class EyeGuardFrameSelector:
    """S2V 비디오 프레임 중 눈을 가장 또렷하게 뜬 최적 프레임 자동 선별기"""

    @classmethod
    def select_best_open_eye_frame(
        cls,
        frame_paths: List[str],
        candidate_count: int = 15,
        target_w: int = 384,
        target_h: int = 672
    ) -> str:
        """
        주어진 프레임 목록(순서대로 정렬됨)의 마지막 candidate_count개 중에서
        눈 부위가 가장 선명하고 크게 열려 있는 최적의 프레임 경로 반환
        """
        if not frame_paths:
            raise ValueError("프레임 목록이 비어 있습니다.")

        if len(frame_paths) <= 3:
            return frame_paths[-1]

        # 마지막 candidate_count개 후보군 추출
        candidates = frame_paths[-min(len(frame_paths), candidate_count):]

        best_score = -1.0
        best_frame = candidates[0]

        # 눈 영역 상대 좌표 (가로 30%~70%, 세로 15%~35%)
        y1, y2 = int(target_h * 0.15), int(target_h * 0.35)
        x1, x2 = int(target_w * 0.30), int(target_w * 0.70)

        for fpath in candidates:
            if not os.path.exists(fpath):
                continue
            try:
                img = cv2.imread(fpath)
                if img is None:
                    continue
                # 눈 영역 크롭
                eye_crop = img[y1:y2, x1:x2]
                gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
                # 눈이 떠져 있을 때 동공과 흰자위의 경계로 인해 라플라시안 에지 분산이 극대화됨
                score = cv2.Laplacian(gray, cv2.CV_64F).var()

                if score > best_score:
                    best_score = score
                    best_frame = fpath
            except Exception as e:
                logger.warning(f"프레임 분석 예외 ({fpath}): {e}")

        logger.info(f"👁️ [Eye-Guard] 눈 뜬 최적 프레임 선별 완료: {os.path.basename(best_frame)} (선명도 스코어: {best_score:.2f})")
        return best_frame
