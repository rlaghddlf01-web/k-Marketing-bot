"""
🚀 [EasyTax 전용 공식 프로필 핀 포스트 단독 발행기]
- 100% EasyTax 전용 분리 실행기
- u/easytax 계정 프로필에 조특법 제30조 & 90% 소득세 감면 & 세무환급 공식 가이드 포스트 발행 및 상단 핀(Pin) 고정
"""

import sys
from pathlib import Path

# 윈도우 콘솔 UTF-8 강제 설정 (CP949 이모지 인코딩 충돌 방지)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import logging

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.reddit_easytax_showcase import get_easytax_pinned_showcase
from modules.reddit_easytax_publisher import EasyTaxRedditPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PublishEasyTaxPinned")

def main():
    print("\n========================================================")
    print("💰 [EasyTax] 공식 프로필 핀(Pinned) 포스트 발행 시작")
    print("========================================================")
    
    content = get_easytax_pinned_showcase()
    print(f"📝 [Title]: {content['title']}\n")
    print(f"📄 [Body Snippet]:\n{content['body'][:250]}...\n")
    
    publisher = EasyTaxRedditPublisher()
    result = publisher.publish_profile_post(
        title=content["title"],
        body=content["body"],
        pin_to_profile=True
    )
    
    if result.get("success"):
        print("\n========================================================")
        print("🎉 [EasyTax] 프로필 포스트 발행 성공!")
        print(f"🔗 포스트 URL: {result.get('post_url')}")
        print(f"📌 상단 핀 고정 완료: {result.get('pinned')}")
        print("========================================================\n")
    else:
        print("\n========================================================")
        print(f"❌ [EasyTax] 프로필 포스트 발행 실패: {result.get('error')}")
        print("========================================================\n")

if __name__ == "__main__":
    main()
