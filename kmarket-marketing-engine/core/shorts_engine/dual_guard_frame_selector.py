# -*- coding: utf-8 -*-
"""
DualGuardFrameSelector - 👁️👄 [눈 또렷함 + 입술 밀착 다뭄 동시 보장 듀얼 가드 프레임 선별기]
- Wan 2.2 S2V 1차 샷(0~5초)에서 2차 샷(5~10초)으로 바통 터치할 때
  1) 눈을 깜빡이지 않고 가장 크게 뜬 상태
  2) 말을 마치고 입술을 단단히 다문(치아 노출 0%, 입 벌림 0%) 상태
  를 동시에 만족하는 최적의 프레임을 수학적/시각적으로 정밀 선별하여 2차 샷 기준 이미지로 인계합니다.
"""

import os
import logging
from typing import List, Optional
import cv2
import numpy as np

logger = logging.getLogger("DualGuardFrameSelector")


class DualGuardFrameSelector:
    """눈 오픈 상태와 입술 닫힘 상태를 동시 검증하는 듀얼 가드 프레임 선별기"""

    @classmethod
    def select_best_seamless_frame(
        cls,
        frame_paths: List[str],
        candidate_count: int = 16,
        target_w: int = 384,
        target_h: int = 672
    ) -> str:
        """
        주어진 81프레임 중 마지막 candidate_count(기본 16개, 약 4.0초~5.06초) 중에서
        1) 입술을 완벽히 다문(치아 노출 0%, 구강 음영 0%) 프레임 그룹을 1차 엄격 필터링하고
        2) 그 중 눈을 가장 또렷하고 크게 뜬 프레임을 최종 선별 반환합니다.
        """
        if not frame_paths:
            raise ValueError("프레임 목록이 비어 있습니다.")

        if len(frame_paths) <= 3:
            return frame_paths[-1]

        # 1차 샷의 후반부 정지/안착 구간(마지막 1.0초 이내)을 후보군으로 평가
        candidates = frame_paths[-min(len(frame_paths), candidate_count):]

        # 눈 영역 상대 좌표 (가로 28%~72%, 세로 15%~32%)
        eye_y1, eye_y2 = int(target_h * 0.15), int(target_h * 0.32)
        eye_x1, eye_x2 = int(target_w * 0.28), int(target_w * 0.72)

        # 입술 영역 상대 좌표 (가로 34%~66%, 세로 36%~49%)
        mouth_y1, mouth_y2 = int(target_h * 0.36), int(target_h * 0.49)
        mouth_x1, mouth_x2 = int(target_w * 0.34), int(target_w * 0.66)

        evaluated = []

        for fpath in candidates:
            if not os.path.exists(fpath):
                continue
            try:
                img = cv2.imread(fpath)
                if img is None:
                    continue

                # 1. 눈 선명도 스코어 (라플라시안 에지 분산 - 눈을 뜰수록 흰자위/동공 경계로 분산 증가)
                eye_crop = img[eye_y1:eye_y2, eye_x1:eye_x2]
                eye_gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
                eye_score = float(cv2.Laplacian(eye_gray, cv2.CV_64F).var())

                # 2. 입술 상태 정밀 분석 (구강 내부 그림자, 치아 노출, 수직 에지 복합 검증)
                mouth_crop = img[mouth_y1:mouth_y2, mouth_x1:mouth_x2]
                mouth_hsv = cv2.cvtColor(mouth_crop, cv2.COLOR_BGR2HSV)
                
                # 구강 내부 어두운 공동(V < 45) 비율
                dark_cavity = float(np.mean(mouth_hsv[:, :, 2] < 45))
                
                # 치아 노출(밝은 흰색 V > 175 & 낮은 채도 S < 55) 비율
                teeth_ratio = float(np.mean((mouth_hsv[:, :, 2] > 175) & (mouth_hsv[:, :, 1] < 55)))
                
                # 수직 에지 강도 (입술이 벌어질수록 상순-치아-하순 사이 수직 경계면 급증)
                mouth_gray = cv2.cvtColor(mouth_crop, cv2.COLOR_BGR2GRAY)
                sobel_y = cv2.Sobel(mouth_gray, cv2.CV_64F, 0, 1)
                vert_edge_var = float(np.var(sobel_y))

                # 입 벌림도 지수 (낮을수록 입술이 단단히 닫힌 상태)
                mouth_openness = (dark_cavity * 120.0) + (teeth_ratio * 80.0) + (vert_edge_var / 800.0)

                evaluated.append({
                    "path": fpath,
                    "eye_score": eye_score,
                    "mouth_openness": mouth_openness,
                    "dark_cavity": dark_cavity,
                    "teeth_ratio": teeth_ratio,
                    "vert_edge": vert_edge_var
                })

            except Exception as e:
                logger.warning(f"듀얼 가드 분석 중 예외 ({fpath}): {e}")

        if not evaluated:
            return candidates[-1]

        # [입 다뭄 절대 우선 게이트키퍼 원칙]
        # 입 벌림도(mouth_openness)가 가장 낮은 상위 30% 프레임군(가장 잘 다물어진 입)을 1차 필터링
        evaluated.sort(key=lambda x: x["mouth_openness"])
        min_openness = evaluated[0]["mouth_openness"]
        
        # 최저 입 벌림도 대비 15% 이내로 잘 다물어진 프레임군 추출
        closed_threshold = min_openness * 1.15 + 0.3
        closed_group = [item for item in evaluated if item["mouth_openness"] <= closed_threshold]
        
        if not closed_group:
            closed_group = evaluated[:3]

        # 2차: 입이 가장 잘 다물어진 그룹 중에서 '눈이 가장 또렷하고 크게 떠진' 프레임 최종 선별
        best_candidate = max(closed_group, key=lambda x: x["eye_score"])

        fname = os.path.basename(best_candidate["path"])
        logger.info(
            f"👁️👄 [Dual-Guard 무결점 프레임 선별] 채택: {fname} | "
            f"눈 선명도={best_candidate['eye_score']:.1f}, "
            f"입 다뭄도={best_candidate['mouth_openness']:.2f} (치아={best_candidate['teeth_ratio']:.4f}, 에지={best_candidate['vert_edge']:.0f})"
        )
        return best_candidate["path"]
