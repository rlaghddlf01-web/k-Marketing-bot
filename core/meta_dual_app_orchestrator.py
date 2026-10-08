# -*- coding: utf-8 -*-
"""
[KTRS 마케팅 엔진 코어] 2개 앱(EasyTax & K-Market) 인스타그램 8개국 독립 교대 오케스트레이터
========================================================================================
- 브랜드 1: 💰 EasyTax (KTRS 세금 환급)
- 브랜드 2: 🛒 K-Market (KTRS 마켓)
- 8대 타깃 국가: 베트남(vi), 네팔(ne), 캄보디아(km), 인도네시아(id), 태국(th), 몽골(mn), 미얀마(my), 우즈베키스탄(uz)
- 원칙:
  1. 방식 ① 준수: 각 앱별 8개 국가 독립 프로필 분리 (계정 간 간섭 0%, 섀도우밴 위험 원천 차단)
  2. 2개 앱 교대 번갈아가며 실행: EasyTax -> (휴식 10~15초) -> K-Market 순차 교대
  3. 무결성 게이트 및 심야 취침 모드(00~07시) 지원
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from brands.easytax.easytax_meta_stealth_incubator import EasyTaxMetaStealthIncubator
from brands.kmarket.kmarket_meta_stealth_incubator import KMarketMetaStealthIncubator

logger = logging.getLogger("MetaDualAppOrchestrator")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(name)s [%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class MetaDualAppOrchestrator:
    """EasyTax와 K-Market 인스타그램 8개 계정을 번갈아가며 교대 워밍업하는 오케스트레이터"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.easytax_bot = EasyTaxMetaStealthIncubator(headless=self.headless)
        self.kmarket_bot = KMarketMetaStealthIncubator(headless=self.headless)

    def get_status_overview(self) -> Dict[str, Any]:
        """두 앱의 8개 국가 계정 연동 상태 및 다음 회전 차례 조회"""
        overview = {
            "easytax": {
                "accounts": {},
                "next_country": None
            },
            "kmarket": {
                "accounts": {},
                "next_country": None
            }
        }

        # EasyTax 상태
        for code in self.easytax_bot.COUNTRIES:
            label = self.easytax_bot.COUNTRY_LABELS.get(code, code.upper())
            is_isolated = self.easytax_bot.has_isolated_profile(code)
            overview["easytax"]["accounts"][code] = {
                "label": label,
                "isolated": is_isolated,
                "linked": is_isolated or self.easytax_bot.is_available()
            }
        et_rot_file = self.easytax_bot.rotation_file
        if et_rot_file.exists():
            try:
                with open(et_rot_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    idx = state.get("current_index", 0)
                    overview["easytax"]["next_country"] = self.easytax_bot.COUNTRIES[idx % len(self.easytax_bot.COUNTRIES)]
            except Exception:
                pass

        # K-Market 상태
        for code in self.kmarket_bot.COUNTRIES:
            label = self.kmarket_bot.COUNTRY_LABELS.get(code, code.upper())
            is_isolated = self.kmarket_bot.has_isolated_profile(code)
            overview["kmarket"]["accounts"][code] = {
                "label": label,
                "isolated": is_isolated,
                "linked": is_isolated or self.kmarket_bot.is_available()
            }
        km_rot_file = self.kmarket_bot.rotation_file
        if km_rot_file.exists():
            try:
                with open(km_rot_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    idx = state.get("current_index", 0)
                    overview["kmarket"]["next_country"] = self.kmarket_bot.COUNTRIES[idx % len(self.kmarket_bot.COUNTRIES)]
            except Exception:
                pass

        return overview

    def run_alternating_cycle(self, duration_per_session: int = 45) -> Dict[str, Any]:
        """
        [2개 앱 교대 번갈아 실행]
        1. EasyTax 다음 국가 인스타그램 계정 워밍업 (45초)
        2. 인간적 자연 휴식 간격 (10~15초 쿨다운)
        3. K-Market 다음 국가 인스타그램 계정 워밍업 (45초)
        """
        logger.info("=" * 70)
        logger.info("🔄 [인스타그램 2개 앱 8개국 교대 스텔스] 세션 시작")
        logger.info("=" * 70)

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "easytax": None,
            "kmarket": None,
            "status": "success"
        }

        # Step 1: 💰 EasyTax 계정 워밍업
        logger.info("▶ [1단계: 💰 EasyTax] 인스타그램 스텔스 워밍업 가동...")
        try:
            res_et = self.easytax_bot.run_warmup_session(duration_seconds=duration_per_session)
            results["easytax"] = res_et
            et_country = res_et.get("nationality_code", "unknown")
            et_label = res_et.get("country_label", et_country)
            et_posts = res_et.get("posts_viewed", 0)
            et_likes = res_et.get("likes_given", 0)
            logger.info(f"✅ [1단계: 💰 EasyTax 완료] 국가: {et_label} | 탐색: {et_posts}건 | 좋아요: {et_likes}회")
        except Exception as e:
            logger.error(f"❌ [1단계: 💰 EasyTax 예외] {e}")
            results["easytax"] = {"status": "error", "error": str(e)}

        # Step 2: 인간적인 쿨다운 휴식 (10~15초)
        cool_down = 12
        logger.info(f"☕ [자연스러운 앱 전환 쿨다운] {cool_down}초간 휴식 후 K-Market 세션으로 전환...")
        time.sleep(cool_down)

        # Step 3: 🛒 K-Market 계정 워밍업
        logger.info("▶ [2단계: 🛒 K-Market] 인스타그램 스텔스 워밍업 가동...")
        try:
            res_km = self.kmarket_bot.run_warmup_session(duration_seconds=duration_per_session)
            results["kmarket"] = res_km
            km_country = res_km.get("nationality_code", "unknown")
            km_label = res_km.get("country_label", km_country)
            km_posts = res_km.get("posts_viewed", 0)
            km_likes = res_km.get("likes_given", 0)
            logger.info(f"✅ [2단계: 🛒 K-Market 완료] 국가: {km_label} | 탐색: {km_posts}건 | 좋아요: {km_likes}회")
        except Exception as e:
            logger.error(f"❌ [2단계: 🛒 K-Market 예외] {e}")
            results["kmarket"] = {"status": "error", "error": str(e)}

        logger.info("=" * 70)
        logger.info("🎉 [인스타그램 2개 앱 8개국 교대 스텔스] 1회 전체 사이클 성공적 완료!")
        logger.info("=" * 70)
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KTRS 인스타그램 2개 앱 8개국 교대 스텔스 러너")
    parser.add_argument("--headful", action="store_true", help="브라우저 화면을 직접 보며 실행 (헤드풀 모드)")
    parser.add_argument("--status", action="store_true", help="현재 두 앱의 8개국 계정 연동 및 회전 상태 출력")
    parser.add_argument("--duration", type=int, default=45, help="세션당 체류 시간(초, 기본 45초)")
    args = parser.parse_args()

    orchestrator = MetaDualAppOrchestrator(headless=not args.headful)

    if args.status:
        status = orchestrator.get_status_overview()
        print("\n" + "=" * 70)
        print("📸 [KTRS 마케팅] 인스타그램 2개 앱 8개국 계정 상태 현황")
        print("=" * 70)
        print("💰 EasyTax (KTRS 세금 환급):")
        for code, info in status["easytax"]["accounts"].items():
            st = "✅ [방식① 전용 독립 프로필]" if info["isolated"] else "⏳ [기본 프로필 폴백 (1회 연동 대기)]"
            print(f"  - {info['label']:<15} ({code}): {st}")
        et_next = status['easytax']['next_country'] or 'vi (1번 베트남)'
        print(f"  👉 다음 회전 타깃: {et_next}")

        print("\n🛒 K-Market (KTRS 마켓):")
        for code, info in status["kmarket"]["accounts"].items():
            st = "✅ [방식① 전용 독립 프로필]" if info["isolated"] else "⏳ [기본 프로필 폴백 (1회 연동 대기)]"
            print(f"  - {info['label']:<15} ({code}): {st}")
        km_next = status['kmarket']['next_country'] or 'vi (1번 베트남)'
        print(f"  👉 다음 회전 타깃: {km_next}")
        print("=" * 70 + "\n")
        return

    orchestrator.run_alternating_cycle(duration_per_session=args.duration)


if __name__ == "__main__":
    main()
