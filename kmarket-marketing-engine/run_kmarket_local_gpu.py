# -*- coding: utf-8 -*-
"""
run_kmarket_local_gpu.py - KTRS 마켓 분리형 로컬 5단계 정품 숏폼 1클릭 실행기
기존 modules/shorts_kmarket.py는 100% 무손실 보존된 상태에서 독립 실행
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from modules.shorts_kmarket_local_gpu import ShortsKMarketLocalGPU

if __name__ == "__main__":
    factory = ShortsKMarketLocalGPU()
    res = factory.produce_shorts(lang="ko")
    if res.get("success"):
        print("모든 공정이 정상 완료되었습니다.")
    else:
        print("실패:", res.get("error"))
