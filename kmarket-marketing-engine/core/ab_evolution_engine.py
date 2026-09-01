"""
ABEvolutionEngine - [AI 자가진화 A/B 테스트 & 동적 비율 자율 조정 엔진]
- 성과 스코어링 공식: 총점 = (좋아요 × 1점) + (댓글 × 2점) + (링크 클릭 × 5점)
- 모드 3종 지원:
  1. 'ab_auto': A/B 자율 학습 모드 (초기 50:50 -> 성과 점수 비율에 따라 60:40, 70:30 등 자율 진화)
  2. 'colab_gpu': 100% 무료 코랩 GPU 고정
  3. 'gemini': 100% 제미나이 Imagen AI 고정
- 데이터 영구 보존: data/ab_evolution_stats.json
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, Any, Tuple
from config import DATA_DIR

logger = logging.getLogger("ABEvolutionEngine")

STATS_FILE = DATA_DIR / "ab_evolution_stats.json"

# 대표님 절대 원칙 가중치 배점
WEIGHT_LIKE = 1       # 좋아요: 1점
WEIGHT_COMMENT = 2    # 댓글: 2점
WEIGHT_CLICK = 5      # 링크 클릭 (전환): 5점

# 🛡️ [대표님 절대 지침: 8:2 안전 가드레일]
# 어느 한쪽 엔진이 아무리 압도적이어도 80%(8할) 초과 금지, 최소 20%(2할) 탐색 보장
MAX_RATIO_LIMIT = 80  # 최대 80% (8:2)
MIN_RATIO_LIMIT = 20  # 최소 20% (2:8)


class ABEvolutionEngine:
    """
    🧬 AI 자가진화 A/B 테스트 오케스트레이터
    """
    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """통계 파일 로드 또는 초기화"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"AB 통계 파일 로드 실패, 초기화: {e}")

        # 기본 통계 구조 초기화
        channels = [
            "kmarket_shorts", "kmarket_cardnews",
            "easytax_shorts", "easytax_cardnews"
        ]
        default_stats = {}
        for ch in channels:
            default_stats[ch] = {
                "turn_count": 0,
                "colab_gpu": {
                    "count": 0,
                    "likes": 0,
                    "comments": 0,
                    "clicks": 0,
                    "score": 0
                },
                "gemini": {
                    "count": 0,
                    "likes": 0,
                    "comments": 0,
                    "clicks": 0,
                    "score": 0
                },
                "current_ratio": {"colab_gpu": 50, "gemini": 50}
            }
        self._save_stats(default_stats)
        return default_stats

    def _save_stats(self, stats: Dict[str, Any]):
        """통계 파일 저장"""
        try:
            STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"AB 통계 파일 저장 실패: {e}")

    def _ensure_channel(self, channel_key: str):
        if channel_key not in self.stats:
            self.stats[channel_key] = {
                "turn_count": 0,
                "colab_gpu": {"count": 0, "likes": 0, "comments": 0, "clicks": 0, "score": 0},
                "gemini": {"count": 0, "likes": 0, "comments": 0, "clicks": 0, "score": 0},
                "current_ratio": {"colab_gpu": 50, "gemini": 50}
            }

    def calculate_score(self, likes: int = 0, comments: int = 0, clicks: int = 0) -> int:
        """점수 계산 공식: (좋아요 x 1) + (댓글 x 2) + (클릭 x 5)"""
        return (likes * WEIGHT_LIKE) + (comments * WEIGHT_COMMENT) + (clicks * WEIGHT_CLICK)

    def record_engagement(
        self,
        channel_key: str,
        engine_used: str,
        likes: int = 0,
        comments: int = 0,
        clicks: int = 0
    ) -> Dict[str, Any]:
        """
        고객 반응(좋아요, 댓글, 클릭) 기록 및 점수/비율 재계산
        """
        self._ensure_channel(channel_key)
        ch_stat = self.stats[channel_key]
        
        target_engine = "gemini" if engine_used == "gemini" else "colab_gpu"
        engine_stat = ch_stat[target_engine]

        engine_stat["likes"] += likes
        engine_stat["comments"] += comments
        engine_stat["clicks"] += clicks
        
        # 총점 재계산
        engine_stat["score"] = self.calculate_score(
            engine_stat["likes"],
            engine_stat["comments"],
            engine_stat["clicks"]
        )

        # 동적 비율 자율 진화 (Auto-Tuning)
        score_colab = ch_stat["colab_gpu"]["score"]
        score_gemini = ch_stat["gemini"]["score"]
        total_score = score_colab + score_gemini

        if total_score == 0:
            ratio_colab = 50
            ratio_gemini = 50
        else:
            # 점수 비율에 따라 20% ~ 80% 안전 가드레일 내에서 비율 분배
            raw_colab_pct = round((score_colab / total_score) * 100)
            raw_colab_pct = max(20, min(80, raw_colab_pct))
            ratio_colab = raw_colab_pct
            ratio_gemini = 100 - ratio_colab

        ch_stat["current_ratio"] = {
            "colab_gpu": ratio_colab,
            "gemini": ratio_gemini
        }

        self._save_stats(self.stats)
        logger.info(
            f"📊 [A/B 진화 업데이트] {channel_key} -> 코랩: {score_colab}점 ({ratio_colab}%) vs "
            f"제미나이: {score_gemini}점 ({ratio_gemini}%)"
        )
        return ch_stat

    def get_next_engine(self, channel_key: str, setting_mode: str = "ab_auto") -> str:
        """
        현재 설정 모드와 승률 데이터에 기반하여 이번에 사용할 이미지 생성 엔진 결정
        """
        self._ensure_channel(channel_key)
        ch_stat = self.stats[channel_key]

        # 1. 수동 고정 모드일 때
        if setting_mode == "colab_gpu":
            ch_stat["colab_gpu"]["count"] += 1
            self._save_stats(self.stats)
            return "colab_gpu"
        elif setting_mode == "gemini":
            ch_stat["gemini"]["count"] += 1
            self._save_stats(self.stats)
            return "gemini"

        # 2. 'ab_auto' 자가학습 모드일 때
        ch_stat["turn_count"] += 1
        turn = ch_stat["turn_count"]
        ratio_colab = ch_stat["current_ratio"].get("colab_gpu", 50)

        # 초기 데이터 축적 전(총점 0점)일 때는 정확하게 1번씩 번갈아 생성 (50:50 Alternating)
        score_colab = ch_stat["colab_gpu"]["score"]
        score_gemini = ch_stat["gemini"]["score"]
        
        if score_colab == 0 and score_gemini == 0:
            selected = "colab_gpu" if turn % 2 == 1 else "gemini"
        else:
            # 점수 기반 가중 확률 분배 (Weighted Random Selection)
            rand_val = random.randint(1, 100)
            selected = "colab_gpu" if rand_val <= ratio_colab else "gemini"

        ch_stat[selected]["count"] += 1
        self._save_stats(self.stats)

        logger.info(
            f"🧬 [A/B 자율 선택] {channel_key} (턴 #{turn}) -> '{selected}' 선정 "
            f"(가중치: 코랩 {ratio_colab}% : 제미나이 {100-ratio_colab}%)"
        )
        return selected

    def get_all_stats(self) -> Dict[str, Any]:
        """대시보드 UI 연동용 전체 통계 반환"""
        return self.stats
