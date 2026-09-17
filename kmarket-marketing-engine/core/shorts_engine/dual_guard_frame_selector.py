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
    """
    👁️👄 [눈 150점 + 입 100점 = 총 250점 만점 듀얼 가드 프레임 선별기]
    - 눈 점수 (0~150점): 눈을 깜빡이지 않고 시원하고 또렷하게 크게 뜰수록 고득점
    - 입 점수 (0~100점): 벌어지는 간격(치아/음영/에지)에 비례하여 균등하게 감점 (완전 밀착 시 100점 만점)
    - 총점 (0~250점): 두 점수를 합산하여 가장 조화롭고 완벽한 프레임을 2차 샷 기준 이미지로 채택
    """

    @classmethod
    def calculate_eye_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        👁️ [눈 점수 산출: 0 ~ 150점 만점]
        얼굴 상단 눈 영역(세로 16%~30%, 가로 25%~75%)의 라플라시안 에지 분산을 측정하여
        눈을 감지 않고 동공과 흰자위가 가장 시원하고 또렷하게 열려 있을수록 150점에 근접
        """
        eye_y1, eye_y2 = int(target_h * 0.16), int(target_h * 0.30)
        eye_x1, eye_x2 = int(target_w * 0.25), int(target_w * 0.75)

        eye_crop = img[eye_y1:eye_y2, eye_x1:eye_x2]
        eye_gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
        eye_var = float(cv2.Laplacian(eye_gray, cv2.CV_64F).var())

        # 눈 깜빡임/감김(70 이하: 0점) ~ 시원하게 뜬 상태(200 이상: 150점 만점) 정규화
        score = min(150.0, max(0.0, ((eye_var - 70.0) / (200.0 - 70.0)) * 150.0))
        return round(score, 1)

    @classmethod
    def calculate_mouth_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        👄 [입 점수 산출: 0 ~ 100점 만점]
        얼굴 하단 입술 영역(세로 36%~45%, 가로 38%~62%)을 정밀 분석하여
        입이 벌어지는 간격(구강 그림자 + 수직 경계 에지)에 비례해 균등하게 감점
        - 두 입술이 완벽히 닿아 있고 치아 노출 0%일 때: 100점 만점
        - 입이 벌어질수록 선형적으로 균등 감점 (말하는 중 크게 벌어지면 0~30점)
        """
        mouth_y1, mouth_y2 = int(target_h * 0.36), int(target_h * 0.45)
        mouth_x1, mouth_x2 = int(target_w * 0.38), int(target_w * 0.62)

        mouth_crop = img[mouth_y1:mouth_y2, mouth_x1:mouth_x2]
        mouth_hsv = cv2.cvtColor(mouth_crop, cv2.COLOR_BGR2HSV)
        
        # 1) 구강 내부 어두운 공동(V < 45) 비율
        dark_cavity = float(np.mean(mouth_hsv[:, :, 2] < 45))
        
        # 2) 수직 에지 강도 (입술이 벌어질수록 상순-치아-하순 사이 수직 경계면 급증)
        mouth_gray = cv2.cvtColor(mouth_crop, cv2.COLOR_BGR2GRAY)
        vert_edge = float(np.var(cv2.Sobel(mouth_gray, cv2.CV_64F, 0, 1)))

        # 벌어진 간격에 비례하는 균등 패널티 산출
        gap_penalty = (dark_cavity * 100.0) + max(0.0, (vert_edge - 3800.0) / 40.0)
        score = min(100.0, max(0.0, 100.0 - gap_penalty))
        return round(score, 1)

    @classmethod
    def select_best_seamless_frame(
        cls,
        frame_paths: List[str],
        candidate_count: int = 10,
        target_w: int = 384,
        target_h: int = 672
    ) -> str:
        """
        81프레임이 끝나고 2차 81프레임으로 넘어가기 직전(마지막 candidate_count개 프레임)에서
        눈 점수(150점)와 입 점수(100점)를 독립 측정하고 합산하여 총점(250점 만점)이 가장 높은 프레임을 채택합니다.
        """
        if not frame_paths:
            raise ValueError("프레임 목록이 비어 있습니다.")

        if len(frame_paths) <= 3:
            return frame_paths[-1]

        # 1차 샷의 맨 끝부분(마지막 0.5~0.6초 이내)을 후보군으로 엄격 제한 (위치 점프 0% 보장)
        candidates = frame_paths[-min(len(frame_paths), candidate_count):]

        best_score = -1.0
        best_candidate = candidates[-1]
        best_details = {}

        for fpath in candidates:
            if not os.path.exists(fpath):
                continue
            try:
                img = cv2.imread(fpath)
                if img is None:
                    continue

                # 독립된 눈 점수와 입 점수 각각 산출
                eye_score = cls.calculate_eye_score(img, target_w=target_w, target_h=target_h)
                mouth_score = cls.calculate_mouth_score(img, target_w=target_w, target_h=target_h)
                
                # 총점 합산 (250점 만점)
                total_score = eye_score + mouth_score

                fname = os.path.basename(fpath)
                logger.info(
                    f"📊 [후보 프레임 평가] {fname} | "
                    f"눈: {eye_score:5.1f}/150, 입: {mouth_score:5.1f}/100 => 총점: {total_score:5.1f}/250"
                )

                if total_score > best_score:
                    best_score = total_score
                    best_candidate = fpath
                    best_details = {
                        "name": fname,
                        "eye_score": eye_score,
                        "mouth_score": mouth_score,
                        "total_score": total_score
                    }

            except Exception as e:
                logger.warning(f"듀얼 가드 분석 중 예외 ({fpath}): {e}")

        logger.info(
            f"🏆 [Dual-Guard 최종 채택 완료] {best_details.get('name', os.path.basename(best_candidate))} | "
            f"눈: {best_details.get('eye_score', 0)}/150 + 입: {best_details.get('mouth_score', 0)}/100 = "
            f"총점: {best_details.get('total_score', 0):.1f}/250"
        )
        return best_candidate
