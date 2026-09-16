# -*- coding: utf-8 -*-
"""
FactoryService - 🏭 [대시보드 원클릭 마케팅 팩토리 실행 전담 서비스]
- 웹 대시보드(/api/factory/run)에서 요청받은 작업을 비동기 스레드로 실행
- 이지택스 / 케이마켓 듀얼 파이프라인 및 카드뉴스 / 숏폼 모드 완벽 연동
- 실시간 로그 중계 및 바탕화면 출력 보장
"""

import os
import random
import threading
import traceback
from typing import Dict, Any, Optional, Callable, Union
from pathlib import Path

from brands.easytax.easytax_cardnews_pipeline import EasyTaxCardNewsPipeline
from brands.easytax.easytax_shorts_pipeline import EasyTaxShortsPipeline
from brands.kmarket.kmarket_cardnews_pipeline import KMarketCardNewsPipeline
from brands.kmarket.kmarket_shorts_pipeline import KMarketShortsPipeline


class FactoryService:
    """대시보드 원클릭 콘텐츠 생성 서비스"""

    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None):
        self.log_callback = log_callback
        self.active_jobs = {}
        self.lock = threading.Lock()

    def _log(self, text: str, log_type: str = "info"):
        if self.log_callback:
            try:
                self.log_callback(text, log_type)
            except Exception:
                pass
        print(f"[{log_type.upper()}] {text}")

    def run_factory_task(
        self,
        brand: str = "easytax",
        mode: str = "cardnews",
        lang: str = "vi",
        amount: Union[int, str] = 3100000
    ) -> Dict[str, Any]:
        """
        비동기 백그라운드 스레드로 마케팅 콘텐츠 제작 태스크 구동
        """
        brand = brand.lower()
        mode = mode.lower()
        lang = lang.lower()

        # 금액 유연성 지원 (랜덤 실사 금액 또는 지정 금액)
        REALISTIC_AMOUNTS = [1850000, 2140000, 2480000, 2850000, 3100000, 3420000, 3850000, 4280000]
        if isinstance(amount, str) and (amount.lower() == "random" or amount.strip() == ""):
            resolved_amount = random.choice(REALISTIC_AMOUNTS)
        else:
            try:
                resolved_amount = int(amount)
                if resolved_amount <= 0:
                    resolved_amount = random.choice(REALISTIC_AMOUNTS)
            except Exception:
                resolved_amount = random.choice(REALISTIC_AMOUNTS)

        job_id = f"{brand}_{mode}_{lang}_{int(resolved_amount)}"
        
        with self.lock:
            if self.active_jobs.get(job_id, False):
                return {
                    "success": False,
                    "message": f"현재 동일한 제작 작업({job_id})이 이미 진행 중입니다."
                }
            self.active_jobs[job_id] = True

        def _worker():
            try:
                brand_label = "EasyTax (세금 환급)" if brand == "easytax" else "K-Market (생활 커뮤니티)"
                mode_label = "1080x1350 카드뉴스" if mode == "cardnews" else "22초 완성 숏폼"
                self._log(f"🚀 [원클릭 팩토리] {brand_label} {mode_label} ({lang.upper()}) 제작을 시작합니다...", "info")

                output_path = ""
                if brand == "easytax":
                    if mode == "cardnews":
                        # 1. ComfyUI 자동 기동 보장
                        from core.engine.comfy_process_manager import ComfyProcessManager
                        ComfyProcessManager.ensure_running(log_callback=self._log)

                        # 2. 신형 5장 풀사이즈 카드뉴스 세트 일괄 제작 (모듈 실시간 리로드 보장)
                        import importlib
                        import core.character_anchor_cardnews_easytax
                        import core.scenario_director_cardnews_easytax
                        import core.engine.cardnews_batch_producer
                        importlib.reload(core.character_anchor_cardnews_easytax)
                        importlib.reload(core.scenario_director_cardnews_easytax)
                        importlib.reload(core.engine.cardnews_batch_producer)

                        from core.engine.cardnews_batch_producer import CardNewsBatchProducer
                        producer = CardNewsBatchProducer()
                        res = producer.produce_full_set(lang=lang, amount=resolved_amount)
                        output_path = res.get("folder_path", "")
                        self._log(f"🎉 [EasyTax 5장 카드뉴스 세트 완성] 환급액: {res.get('refund_formatted')} | 저장 폴더: {output_path}", "success")
                        return
                    elif mode == "shorts":
                        # ComfyUI 자동 기동 보장
                        from core.engine.comfy_process_manager import ComfyProcessManager
                        ComfyProcessManager.ensure_running(log_callback=self._log)

                        import importlib
                        import core.shorts_engine
                        import core.shorts_engine.easytax_app_recorder
                        import core.shorts_engine.shorts_scenario_script_director
                        import core.shorts_engine.shorts_video_composer
                        import core.shorts_engine.easytax_shorts_producer
                        importlib.reload(core.shorts_engine.easytax_app_recorder)
                        importlib.reload(core.shorts_engine.shorts_scenario_script_director)
                        importlib.reload(core.shorts_engine.shorts_video_composer)
                        importlib.reload(core.shorts_engine.easytax_shorts_producer)
                        importlib.reload(core.shorts_engine)

                        from core.shorts_engine import EasyTaxShortsProducer
                        producer = EasyTaxShortsProducer()
                        self._log(f"🎬 [EasyTax 숏폼] 1080p 고화질 숏폼 & SNS 배포팩 제작 시작 (언어: {lang.upper()}, 금액: ₩{resolved_amount:,})", "info")
                        res = producer.produce(lang=lang, amount=resolved_amount)
                        output_path = res.get("output_mp4", "")
                        folder_path = res.get("folder_path", "")
                        self._log(f"🎉 [EasyTax 숏폼 완제품 & SNS 배포팩 완성] 폴더: {folder_path}", "success")
                        return
                elif brand == "kmarket":
                    if mode == "cardnews":
                        # 케이마켓 신형 5장 세트 일괄 제작
                        from modules.cardnews_kmarket import CardnewsKMarket
                        res = CardnewsKMarket().generate_carousel_cardnews(lang=lang)
                        output_path = res.get("desktop_dir", "")
                        self._log(f"🎉 [K-Market 5장 카드뉴스 세트 완성] 저장 폴더: {output_path}", "success")
                        return
                    elif mode == "shorts":
                        # ComfyUI 자동 기동 보장
                        from core.engine.comfy_process_manager import ComfyProcessManager
                        ComfyProcessManager.ensure_running(log_callback=self._log)

                        import importlib
                        import core.shorts_engine
                        import core.shorts_engine.kmarket_shorts_producer
                        importlib.reload(core.shorts_engine.kmarket_shorts_producer)
                        importlib.reload(core.shorts_engine)

                        from core.shorts_engine import KMarketShortsProducer
                        producer = KMarketShortsProducer()
                        self._log(f"🎬 [K-Market 숏폼] 1080p 고화질 숏폼 & SNS 배포팩 제작 시작 (언어: {lang.upper()})", "info")
                        res = producer.produce(lang=lang)
                        output_path = res.get("output_mp4", "")
                        folder_path = res.get("folder_path", "")
                        self._log(f"🎉 [K-Market 숏폼 완제품 & SNS 배포팩 완성] 폴더: {folder_path}", "success")
                        return
                else:
                    raise ValueError(f"지원하지 않는 브랜드입니다: {brand}")

                self._log(f"🎉 [원클릭 팩토리] {brand_label} {mode_label} 완성! 바탕화면 저장 완료: {output_path}", "success")

            except Exception as e:
                err_msg = str(e)
                traceback.print_exc()
                self._log(f"❌ [원클릭 팩토리 오류] {err_msg}", "danger")
            finally:
                with self.lock:
                    self.active_jobs[job_id] = False

        threading.Thread(target=_worker, daemon=True).start()

        return {
            "success": True,
            "job_id": job_id,
            "message": f"[{brand.upper()}] {mode.upper()} ({lang.upper()}) 원클릭 제작 작업이 백그라운드에서 시작되었습니다."
        }
