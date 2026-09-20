# -*- coding: utf-8 -*-
"""
CardnewsKMarket - 🛒 [K-Market 전담 5장 풀사이즈 0원 나눔 카드뉴스 생성 공장]
- 7:3 분할 완전 폐기 ➔ 1080x1350 풀블리드(Full-Bleed) + 하단 그라디언트 스크림
- 스마트폰 화면 매립 / 플로팅 UI 전면 배제 (1~5장 모두 깨끗한 라이프스타일 실사 사진)
- ComfyUI Wan 2.1 Q4_0 GGUF (RTX 5060 Ti 로컬 GPU 무과금 T2I 엔진)
- 1~5장 전 슬라이드 동일 인물 마스터 시드 동기화 + 8대 국가 고유 앵커
- 4대 SNS(스레드, 인스타, 페북, 텔레그램) 현지어 원문 + 한국어 해설 2단 포스팅 가이드 동시 출력
- 바탕화면 '카드뉴스_산출물/케이마켓/케이마켓_[언어]_[테마]_[날짜시분]' 자동 저장
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import OUTPUTS_DIR, DATA_DIR, LANGUAGES, DESKTOP_CARDNEWS_KMARKET
from core.engine.cardnews_batch_producer_kmarket import CardNewsBatchProducerKMarket
from core.auto_publishers.cardnews_multi_publisher import CardnewsMultiPublisher

logger = logging.getLogger("CardnewsKMarket")


class CardnewsKMarket:
    """K-Market 전담 5장 풀블리드 카드뉴스 무인 생산 공장"""

    def __init__(self):
        self.service_id = "kmarket"
        self.output_dir = OUTPUTS_DIR / "cardnews" / "kmarket"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_dir = Path(r"C:\Users\zkfnt\Desktop\카드뉴스_산출물\케이마켓")
        self.desktop_dir.mkdir(parents=True, exist_ok=True)

        self.producer = CardNewsBatchProducerKMarket()
        self.publisher = CardnewsMultiPublisher()

    def generate_carousel_cardnews(
        self,
        lang: str = "uz",
        theme_index: Optional[int] = None,
        custom_hero_image: Optional[Any] = None,
        preferred_gender: Optional[str] = None,
        master_seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        K-Market 전용 5장 풀사이즈 카드뉴스 (1080x1350) 완제품 및 SNS 가이드 생성
        (GoldenBatchProducer 및 대시보드 호환 규격)
        """
        logger.info(f"🛒 [K-Market 카드뉴스 파이프라인 가동] 언어: {lang.upper()} (Wan 2.1 GPU T2I)")

        result = self.producer.produce_full_set(
            lang=lang,
            theme_index=theme_index,
            custom_hero_image=custom_hero_image,
            preferred_gender=preferred_gender,
            master_seed=master_seed,
            **kwargs
        )

        folder_path = Path(result["folder_path"])
        slide_paths = [Path(p) for p in result["slides"]]
        guide_path = Path(result["guide_path"])

        # 자동 배포용 metadata.json 생성 (호환성 유지)
        metadata_payload = {
            "service_id": "kmarket",
            "lang": lang,
            "theme_title": result.get("theme_title"),
            "total_slides": len(slide_paths),
            "image_paths": [str(p) for p in slide_paths],
            "guide_file": str(guide_path),
            "folder_path": str(folder_path),
            "timestamp": int(time.time())
        }
        try:
            meta_path = folder_path / "metadata.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata_payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"metadata.json 저장 경고: {e}")

        # 🧹 [1개국 K-Market 카드뉴스 완료 즉각 VRAM 및 모델 완전 방출]
        try:
            from core.engine.gpu_memory_flusher import GPUMemoryFlusher
            GPUMemoryFlusher.flush_gpu_vram(unload_models=True)
        except Exception:
            pass


        return {
            "success": True,
            "service_id": "kmarket",
            "lang": lang,
            "theme_title": result.get("theme_title"),
            "total_slides": len(slide_paths),
            "image_paths": [str(p) for p in slide_paths],
            "slides": [str(p) for p in slide_paths],
            "caption_file": str(guide_path),
            "guide_path": str(guide_path),
            "folder_path": str(folder_path),
            "desktop_dir": str(folder_path),
            "master_seed": result.get("master_seed")
        }

    def produce_full_set(self, **kwargs) -> Dict[str, Any]:
        """직접 프로듀서 위임 alias"""
        return self.generate_carousel_cardnews(**kwargs)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    lang = sys.argv[1] if len(sys.argv) > 1 else "uz"
    bot = CardnewsKMarket()
    logger.info(f"🤖 [K-Market 마케팅 봇] {lang.upper()} 카드뉴스 5장 무인 자율 생산 가동...")
    res = bot.generate_carousel_cardnews(lang=lang)
    print("\n" + "=" * 60)
    print(f"🎉 [K-Market 마케팅 봇 무인 생산 완료] 폴더: {res.get('folder_path')}")
    for idx, s in enumerate(res.get('slides', []), 1):
        print(f"  🖼️ 슬라이드 {idx}: {s}")
    print(f"📄 SNS 가이드: {res.get('guide_path')}")
    print("=" * 60)

