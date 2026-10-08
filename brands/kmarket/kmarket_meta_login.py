# -*- coding: utf-8 -*-
"""
KMarket Meta Login Helper (🛒 KTRS Market 메타 1회 영구 로그인 연동기 - 정품 크롬 전용)
=============================================================================
- 브랜드: 🛒 KTRS Market
- 프로필 디렉터리: brands/kmarket/meta_chrome_profile/
- 역할:
  1. 실제 정품 구글 크롬(Chrome)을 전용 프로필 모드로 실행 (봇 탐지 0%, 팝업 0%)
  2. 인스타그램/페이스북에 평소처럼 정상 로그인 수행
  3. 로그인 완료 후 크롬 창을 닫으면 해당 프로필 폴더에 세션이 영구 보존됨
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from .setup_meta_profile import main

if __name__ == "__main__":
    main()
