# -*- coding: utf-8 -*-
"""
DualGuardFrameSelector - 👁️👄📐👀 [눈 200점 + 입 150점 + 목직립 75점 + 정면응시 75점 = 총 500점 만점 황금비율 쿼드 가드]
- Wan 2.2 S2V 1차 샷(0~5초)에서 2차 샷(5~10초)으로 바통 터치할 때
  1) 👁️ 눈을 깜빡이지 않고 가장 크게 뜬 상태 (최우선: 200점 만점)
  2) 👄 말을 마치고 입술을 단단히 다문(치아 노출 0%, 입 벌림 0%) 상태 (150점 만점)
  3) 📐 고개와 목이 좌우로 갸웃하지 않고 완벽히 수직 직립(Head Tilt 0도)인 상태 (75점 만점)
  4) 👀 동공이 정중앙에 위치하여 카메라 렌즈를 100% 똑바로 응시하는 상태 (75점 만점)
  를 동시에 만족하는 최적의 프레임을 수학적/시각적으로 정밀 선별하여 2차 샷 기준 이미지로 인계합니다.
"""

import os
import logging
from typing import List, Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger("DualGuardFrameSelector")


class DualGuardFrameSelector:
    """
    👁️👄📐👀 [눈 200점 + 입 150점 + 목직립 75점 + 정면응시 75점 = 총 500점 만점 쿼드 가드 선별기]
    - 👁️ 눈 점수 (0~200점): 눈을 깜빡이지 않고 시원하고 또렷하게 크게 뜰수록 고득점 (가중치 1위, 40%)
    - 👄 입 점수 (0~150점): 벌어지는 간격(치아/음영/에지)에 비례하여 균등하게 감점 (완전 밀착 시 150점 만점, 30%)
    - 📐 목직립 점수 (0~75점): 좌우 눈의 수평 기울기 각도(Head Tilt)가 0도에 가까울수록 75점 만점 (15%)
    - 👀 정면응시 점수 (0~75점): 동공/홍채가 눈 중심에 정확히 안착하여 카메라를 직시할수록 75점 만점 (15%)
    - 🏆 총점 (0~500점): 4개 점수를 합산하여 가장 조화롭고 완벽한 1등 프레임을 2차 샷 기준 이미지로 채택
    """

    @classmethod
    def calculate_eye_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        👁️ [눈 점수 산출: 0 ~ 200점 만점 (최우선)]
        얼굴 상단 눈 영역(세로 16%~30%, 가로 25%~75%)의 라플라시안 에지 분산을 측정하여
        눈을 감지 않고 동공과 흰자위가 가장 시원하고 또렷하게 열려 있을수록 200점에 근접
        """
        eye_y1, eye_y2 = int(target_h * 0.16), int(target_h * 0.30)
        eye_x1, eye_x2 = int(target_w * 0.25), int(target_w * 0.75)

        eye_crop = img[eye_y1:eye_y2, eye_x1:eye_x2]
        eye_gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
        eye_var = float(cv2.Laplacian(eye_gray, cv2.CV_64F).var())

        # 눈 깜빡임/감김(70 이하: 0점) ~ 시원하게 뜬 상태(200 이상: 200점 만점) 정규화
        score = min(200.0, max(0.0, ((eye_var - 70.0) / (200.0 - 70.0)) * 200.0))
        return round(score, 1)

    @classmethod
    def calculate_mouth_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        👄 [입 점수 산출: 0 ~ 150점 만점]
        얼굴 하단 입술 영역(세로 36%~45%, 가로 38%~62%)을 정밀 분석하여
        입이 벌어지는 간격(구강 그림자 + 수직 경계 에지)에 비례해 균등하게 감점
        - 두 입술이 완벽히 닿아 있고 치아 노출 0%일 때: 150점 만점
        - 입이 벌어질수록 선형적으로 균등 감점 (말하는 중 크게 벌어지면 0~45점)
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

        # 벌어진 간격에 비례하는 균등 패널티 산출 (기저 100점 환산 후 1.5배 스케일링)
        gap_penalty = (dark_cavity * 100.0) + max(0.0, (vert_edge - 3800.0) / 40.0)
        base_100 = min(100.0, max(0.0, 100.0 - gap_penalty))
        score = base_100 * 1.5
        return round(score, 1)

    @classmethod
    def calculate_head_tilt_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        📐 [목/고개 직립 점수 산출: 0 ~ 75점 만점]
        좌안과 우안의 동공/어두운 중심 y좌표를 비교하여 수평선 각도(Head Tilt) 측정
        - 양 눈 높낮이 차이가 0픽셀(완전 수평 수직 직립): 75점 만점
        - 고개가 갸웃하여 기울어질수록 감점
        """
        y1, y2 = int(target_h * 0.17), int(target_h * 0.29)
        # 좌안 박스 (화면 기준 좌측)
        left_eye = img[y1:y2, int(target_w * 0.28):int(target_w * 0.48)]
        # 우안 박스 (화면 기준 우측)
        right_eye = img[y1:y2, int(target_w * 0.52):int(target_w * 0.72)]

        def get_eye_vertical_center(eye_crop: np.ndarray) -> float:
            gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
            # 하위 20% 어두운 픽셀(동공/홍채/속눈썹)의 y 무게중심 산출
            thresh = np.percentile(gray, 20)
            y_coords = np.where(gray <= thresh)[0]
            if len(y_coords) > 0:
                return float(np.mean(y_coords))
            return float(gray.shape[0] / 2.0)

        cy_left = get_eye_vertical_center(left_eye)
        cy_right = get_eye_vertical_center(right_eye)

        # 양 눈의 수직 높이 차이 (단위: 픽셀)
        dy = abs(cy_left - cy_right)

        # 0.8픽셀 이하 미세 편차는 75점 만점 인정
        if dy <= 0.8:
            score = 75.0
        else:
            # 1픽셀 증가할 때마다 11.25점씩 균등 감점 (기저 100점 대비 0.75배)
            penalty = (dy - 0.8) * 11.25
            score = max(0.0, min(75.0, 75.0 - penalty))

        return round(score, 1)

    @classmethod
    def calculate_frontal_gaze_score(cls, img: np.ndarray, target_w: int = 384, target_h: int = 672) -> float:
        """
        👀 [정면 응시 점수 산출: 0 ~ 75점 만점]
        좌안과 우안 내부에서 동공(가장 어두운 중심부)의 가로 위치 비율 측정
        - 동공이 눈 박스의 정중앙(45%~55% 구간)에 정확히 위치할 때: 75점 만점
        - 시선이 좌우로 이탈(사시/흘겨봄)할수록 선형 감점
        """
        y1, y2 = int(target_h * 0.17), int(target_h * 0.29)
        left_eye = img[y1:y2, int(target_w * 0.28):int(target_w * 0.48)]
        right_eye = img[y1:y2, int(target_w * 0.52):int(target_w * 0.72)]

        def get_eye_horizontal_ratio(eye_crop: np.ndarray) -> float:
            gray = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2GRAY)
            # 하위 15% 가장 어두운 픽셀(동공 중심)의 x 무게중심
            thresh = np.percentile(gray, 15)
            x_coords = np.where(gray <= thresh)[1]
            if len(x_coords) > 0:
                cx = float(np.mean(x_coords))
                return cx / float(gray.shape[1])
            return 0.50

        ratio_l = get_eye_horizontal_ratio(left_eye)
        ratio_r = get_eye_horizontal_ratio(right_eye)

        # 0.50(정중앙) 대비 편향 오차
        offset_l = abs(ratio_l - 0.50)
        offset_r = abs(ratio_r - 0.50)
        avg_offset = (offset_l + offset_r) / 2.0

        # 편향 오차가 0.03 이내(중앙 47%~53% 범위 안착)이면 75점 만점
        if avg_offset <= 0.03:
            score = 75.0
        else:
            # 0.01 편향마다 7.5점씩 감점 (기저 100점 대비 0.75배)
            penalty = (avg_offset - 0.03) * 750.0
            score = max(0.0, min(75.0, 75.0 - penalty))

        return round(score, 1)

    _face_app = None

    @classmethod
    def get_face_app(cls):
        """InsightFace FaceAnalysis 싱글톤 초기화 (CPU 모드, 초고속 랜드마크 추적)"""
        if cls._face_app is None:
            try:
                import insightface
                from insightface.app import FaceAnalysis
                app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
                app.prepare(ctx_id=0, det_size=(384, 672))
                cls._face_app = app
                logger.info("🎯 [InsightFace 3D 랜드마크 엔진 탑재] 68개 랜드마크 기반 동적 얼굴/치아 추적 준비 완료")
            except Exception as e:
                logger.warning(f"InsightFace 로드 실패 (고정 좌표 폴백 모드 전환): {e}")
                cls._face_app = False
        return cls._face_app if cls._face_app is not False else None

    @classmethod
    def evaluate_frame_with_landmarks(
        cls,
        img: np.ndarray
    ) -> Optional[Tuple[float, float, float, float, bool]]:
        """
        👁️👄📐👀 [InsightFace 68 3D 랜드마크 기반 동적 정밀 평가]
        - 실제 얼굴 위치와 상관없이 68개 랜드마크로 입술 상하 내측(62, 66번) 간격을 마이크로 픽셀 단위로 측정
        - 치아 노출(밝은 비입술 픽셀 군집) 또는 입 벌림 발생 시 즉시 탈락(Reject) 처리
        - 반환값: (eye_score, mouth_score, tilt_score, gaze_score, is_rejected)
        """
        app = cls.get_face_app()
        if app is None:
            return None
        try:
            faces = app.get(img)
            if not faces:
                return None
            f = faces[0]
            lmk = getattr(f, 'landmark_3d_68', None)
            if lmk is None:
                return None

            # 1. 👄 [입술 밀착 & 치아 노출 & 좌우 수평 대칭성(Lip Symmetry) 하드 컷오프]
            gap = float(np.linalg.norm(lmk[62, :2] - lmk[66, :2]))
            mw = float(np.linalg.norm(lmk[48, :2] - lmk[54, :2]))
            open_ratio = gap / mw if mw > 0 else 0.0

            # 📐 [입술 좌우 수평 대칭성(Lip Symmetry) 정밀 측정]
            lip_dy = abs(float(lmk[54, 1] - lmk[48, 1]))  # 좌우 입꼬리 수직 높낮이 편차
            nose_x = float(lmk[30, 0])
            lip_cx = float((lmk[48, 0] + lmk[54, 0]) / 2.0)
            lip_center_offset = abs(lip_cx - nose_x)  # 코 중심축 대비 입술 중심 이탈

            # 구강 내부 치아(고명도 저채도 픽셀) 검출
            cx = int(lmk[62, 0])
            cy = int((lmk[62, 1] + lmk[66, 1]) / 2)
            sample_box = img[max(0, cy - 3):min(img.shape[0], cy + 3), max(0, cx - 8):min(img.shape[1], cx + 8)]
            teeth_pct = 0.0
            if sample_box.size > 0:
                b = sample_box[:, :, 0].astype(float)
                g = sample_box[:, :, 1].astype(float)
                r = sample_box[:, :, 2].astype(float)
                is_teeth = (r > 100) & (g > 90) & (b > 80) & (abs(r - g) < 25) & (abs(r - b) < 25)
                teeth_pct = float(np.mean(is_teeth) * 100)

            # 🚨 [치아 노출 / 입 벌림 / 입술 비대칭 비뚤어짐 하드 컷오프]
            # 1) 입꼬리 높낮이 편차 > 0.8px (비뚤어진 입술 원천 차단)
            # 2) 입술 중심축 이탈 > 2.8px (한쪽으로 쏠린 썩소 원천 차단)
            # 3) 입술 벌림 비율 > 0.11 or 간격 > 3.5px or 치아 15% 이상 감지 시 즉시 탈락 (-9999점)
            is_asym = (lip_dy > 0.8) or (lip_center_offset > 2.8)
            is_rejected = (open_ratio > 0.11) or (gap > 3.5) or (teeth_pct > 15.0) or is_asym
            if is_rejected:
                mouth_score = -9999.0
            else:
                asym_penalty = min(30.0, lip_dy * 25.0)
                open_penalty = min(30.0, (open_ratio / 0.11) * 30.0)
                mouth_score = round(150.0 - asym_penalty - open_penalty, 1)

            # 2. 👁️ [눈 열림 점수 (Eye Aspect Ratio 200점 만점)]
            left_ear = (np.linalg.norm(lmk[37, :2] - lmk[41, :2]) + np.linalg.norm(lmk[38, :2] - lmk[40, :2])) / (2 * np.linalg.norm(lmk[36, :2] - lmk[39, :2]))
            right_ear = (np.linalg.norm(lmk[43, :2] - lmk[47, :2]) + np.linalg.norm(lmk[44, :2] - lmk[46, :2])) / (2 * np.linalg.norm(lmk[42, :2] - lmk[45, :2]))
            ear = (left_ear + right_ear) / 2.0
            eye_score = round(min(200.0, max(0.0, (ear - 0.20) / (0.35 - 0.20) * 200.0)), 1)

            # 3. 📐 [목/고개 직립 점수 (Head Roll 75점 만점)]
            roll = abs(float(f.pose[2])) if hasattr(f, 'pose') else 0.0
            tilt_score = round(max(0.0, min(75.0, 75.0 - roll * 7.5)), 1)

            # 4. 👀 [정면 응시 점수 (Head Yaw 75점 만점)]
            yaw = abs(float(f.pose[1])) if hasattr(f, 'pose') else 0.0
            gaze_score = round(max(0.0, min(75.0, 75.0 - yaw * 5.0)), 1)

            return eye_score, mouth_score, tilt_score, gaze_score, is_rejected
        except Exception as e:
            logger.warning(f"동적 랜드마크 분석 예외: {e}")
            return None

    @classmethod
    def select_best_seamless_frame(
        cls,
        frame_paths: List[str],
        candidate_count: int = 15,
        target_w: int = 384,
        target_h: int = 672,
        fallback_base_img_path: Optional[str] = None
    ) -> str:
        """
        81프레임이 끝나고 2차 81프레임으로 넘어가기 직전(마지막 candidate_count개 프레임)에서
        1) 👁️ 눈 열림 점수 (200점 만점)
        2) 👄 입술 밀착 & 치아 차단 점수 (150점 만점, 치아/입벌림 감지 시 즉시 탈락)
        3) 📐 목 직립 점수 (75점 만점)
        4) 👀 정면 응시 점수 (75점 만점)
        InsightFace 68 랜드마크로 동적 추적하여 무결점 1등 프레임을 선별합니다.
        """
        if not frame_paths:
            raise ValueError("프레임 목록이 비어 있습니다.")

        if len(frame_paths) <= 3:
            return frame_paths[-1]

        candidates = frame_paths[-min(len(frame_paths), candidate_count):]

        best_score = -99999.0
        best_candidate = candidates[-1]
        best_details = {}

        for fpath in candidates:
            if not os.path.exists(fpath):
                continue
            try:
                img = cv2.imread(fpath)
                if img is None:
                    continue

                # 1) InsightFace 랜드마크 기반 동적 정밀 평가
                landmark_res = cls.evaluate_frame_with_landmarks(img)
                if landmark_res is not None:
                    eye_score, mouth_score, tilt_score, gaze_score, is_rejected = landmark_res
                else:
                    # 2) 폴백: 고정 좌표 분석
                    eye_score = cls.calculate_eye_score(img, target_w=target_w, target_h=target_h)
                    mouth_score = cls.calculate_mouth_score(img, target_w=target_w, target_h=target_h)
                    tilt_score = cls.calculate_head_tilt_score(img, target_w=target_w, target_h=target_h)
                    gaze_score = cls.calculate_frontal_gaze_score(img, target_w=target_w, target_h=target_h)
                    is_rejected = False

                total_score = eye_score + mouth_score + tilt_score + gaze_score
                fname = os.path.basename(fpath)

                rej_tag = " [🚨REJECT 치아/입벌림]" if is_rejected else ""
                logger.info(
                    f"📊 [쿼드 가드 후보 평가] {fname} | "
                    f"눈: {eye_score:5.1f}/200, 입: {mouth_score:5.1f}/150, 목직립: {tilt_score:5.1f}/75, 정면: {gaze_score:5.1f}/75 => 총점: {total_score:5.1f}/500{rej_tag}"
                )

                if total_score > best_score:
                    best_score = total_score
                    best_candidate = fpath
                    best_details = {
                        "name": fname,
                        "eye_score": eye_score,
                        "mouth_score": mouth_score,
                        "tilt_score": tilt_score,
                        "gaze_score": gaze_score,
                        "total_score": total_score,
                        "rejected": is_rejected
                    }

            except Exception as e:
                logger.warning(f"쿼드 가드 분석 중 예외 ({fpath}): {e}")

        # 만약 모든 후보 프레임이 입술 비대칭(비뚤어짐) 또는 입벌림으로 탈락한 경우
        if best_score < 0:
            if fallback_base_img_path and os.path.exists(fallback_base_img_path):
                logger.warning(
                    f"🚨 [모든 후보 프레임 입술 비대칭/입벌림 탈락] 안전장치 100% 가동: "
                    f"비뚤어진 프레임을 배제하고 맨 처음의 완벽한 원본 마스터 사진({os.path.basename(fallback_base_img_path)})을 2차 샷 기준 이미지로 채택!"
                )
                return fallback_base_img_path

        logger.info(
            f"🏆 [Quad-Guard 최종 1등 채택] {best_details.get('name', os.path.basename(best_candidate))} | "
            f"눈: {best_details.get('eye_score', 0)}/200 + 입: {best_details.get('mouth_score', 0)}/150 + "
            f"목직립: {best_details.get('tilt_score', 0)}/75 + 정면: {best_details.get('gaze_score', 0)}/75 = "
            f"총점: {best_details.get('total_score', 0):.1f}/500"
        )
        return best_candidate
