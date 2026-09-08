# -*- coding: utf-8 -*-
"""
[신규 모듈] GoldenBatchProducer (core/golden_batch_producer.py)
• 역할: 8대 황금 국가 (vi, uz, km, ne, th, id, mn, my) 전 채널 일괄 대량 생산 엔진
• 기능:
  1. 하루 2회 골든 타임 (오전 11:30 / 저녁 18:30) 자동 일괄 배치 구동
  2. 회차당:
     - 💰 EasyTax: 8개국 숏폼 8편 + 8개국 5장 카드뉴스 8세트
     - 🛒 K-Market: 8개국 숏폼 8편 + 8개국 5장 카드뉴스 8세트
  3. 하루 총합: 숏폼 32편 + 카드뉴스 32세트 (총 64건)
  4. 바탕화면 '숏폼_산출물' 및 '카드뉴스_산출물' 폴더에 브랜드/언어별 실시간 분류 및 복사용 메모장 생성
  5. 특정 국가 지연/오류 시에도 중단 없는 무장애 격리 실행(Fault-Tolerant Loop)
• 원칙: 모듈 분리 원칙(Rule 1), 원천 파이프라인 무결성(Rule 5) 준수
"""

import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from config import (
    GOLDEN_EIGHT_LANGUAGES,
    GOLDEN_EIGHT_DETAILS,
    DATA_DIR,
    OUTPUTS_DIR
)
from modules.shorts_easytax import ShortsEasyTax
from modules.shorts_kmarket import ShortsKMarket
from modules.cardnews_easytax import CardnewsEasyTax
from modules.cardnews_kmarket import CardnewsKMarket
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("GoldenBatchProducer")


class GoldenBatchProducer:
    """
    8대 황금 국가 전용 일괄 대량 생산 배치 마스터
    """
    def __init__(self):
        self.db_mgr = DBManager()
        self.supabase_mgr = SupabaseManager(self.db_mgr)
        
        # 4대 생산 공장 인스턴스화
        self.shorts_easytax = ShortsEasyTax()
        self.shorts_kmarket = ShortsKMarket()
        self.cardnews_easytax = CardnewsEasyTax()
        self.cardnews_kmarket = CardnewsKMarket()
        
        self.stats_file = DATA_DIR / "golden_batch_stats.json"

    def _record_batch_stat(self, slot_name: str, brand: str, content_type: str, lang: str, success: bool):
        """배치 실행 기록 영구 보관"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        stats = {}
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    stats = json.load(f)
            except Exception:
                stats = {}
                
        if today_str not in stats:
            stats[today_str] = {
                "morning": {"shorts": 0, "cardnews": 0, "details": []},
                "evening": {"shorts": 0, "cardnews": 0, "details": []},
                "manual": {"shorts": 0, "cardnews": 0, "details": []}
            }
            
        slot_data = stats[today_str].setdefault(slot_name, {"shorts": 0, "cardnews": 0, "details": []})
        if success:
            if content_type == "shorts":
                slot_data["shorts"] += 1
            elif content_type == "cardnews":
                slot_data["cardnews"] += 1
                
        slot_data["details"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "brand": brand,
            "type": content_type,
            "lang": lang,
            "success": success
        })
        
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"배치 통계 저장 경고: {e}")

    def produce_brand_shorts_batch(self, brand: str = "easytax", slot_name: str = "manual") -> Dict[str, Any]:
        """
        특정 브랜드의 8대 황금 국가 숏폼 8편 일괄 생산
        """
        producer = self.shorts_easytax if brand == "easytax" else self.shorts_kmarket
        brand_name = "EasyTax (KTRS 세무)" if brand == "easytax" else "K-Market (쇼핑몰)"
        logger.info(f"🎬 [{brand_name}] 8대 황금 국가 숏폼 일괄 생산 시작 (슬롯: {slot_name})")
        
        results = []
        success_count = 0
        
        for lang in GOLDEN_EIGHT_LANGUAGES:
            info = GOLDEN_EIGHT_DETAILS.get(lang, {})
            flag = info.get("flag", "🌐")
            country_name = info.get("name", lang)
            
            logger.info(f"   ▶ [{flag} {country_name} ({lang.upper()})] 숏폼 렌더링 시작...")
            try:
                res = producer.produce_shorts(lang=lang)
                success_count += 1
                results.append({"lang": lang, "success": True, "res": res})
                self._record_batch_stat(slot_name, brand, "shorts", lang, True)
                logger.info(f"   ✅ [{flag} {country_name}] 숏폼 완성 및 바탕화면 저장 완료")
            except Exception as e:
                logger.error(f"   ❌ [{flag} {country_name}] 숏폼 렌더링 실패: {e}")
                results.append({"lang": lang, "success": False, "error": str(e)})
                self._record_batch_stat(slot_name, brand, "shorts", lang, False)
                
            time.sleep(1.0)  # 안정적 파일 쓰기를 위한 미세 딜레이
            
        return {
            "brand": brand,
            "type": "shorts",
            "slot": slot_name,
            "total_target": len(GOLDEN_EIGHT_LANGUAGES),
            "success_count": success_count,
            "results": results
        }

    def produce_brand_cardnews_batch(self, brand: str = "easytax", slot_name: str = "manual") -> Dict[str, Any]:
        """
        특정 브랜드의 8대 황금 국가 5장 카드뉴스 8세트 일괄 생산
        """
        producer = self.cardnews_easytax if brand == "easytax" else self.cardnews_kmarket
        brand_name = "EasyTax (KTRS 세무)" if brand == "easytax" else "K-Market (쇼핑몰)"
        logger.info(f"📰 [{brand_name}] 8대 황금 국가 5장 카드뉴스 일괄 생산 시작 (슬롯: {slot_name})")
        
        results = []
        success_count = 0
        
        for lang in GOLDEN_EIGHT_LANGUAGES:
            info = GOLDEN_EIGHT_DETAILS.get(lang, {})
            flag = info.get("flag", "🌐")
            country_name = info.get("name", lang)
            
            logger.info(f"   ▶ [{flag} {country_name} ({lang.upper()})] 5장 카드뉴스 합성 시작...")
            try:
                res = producer.generate_carousel_cardnews(lang=lang)
                success_count += 1
                results.append({"lang": lang, "success": True, "res": res})
                self._record_batch_stat(slot_name, brand, "cardnews", lang, True)
                logger.info(f"   ✅ [{flag} {country_name}] 5장 카드뉴스 완성 및 바탕화면 저장 완료")
            except Exception as e:
                logger.error(f"   ❌ [{flag} {country_name}] 카드뉴스 합성 실패: {e}")
                results.append({"lang": lang, "success": False, "error": str(e)})
                self._record_batch_stat(slot_name, brand, "cardnews", lang, False)
                
            time.sleep(1.0)
            
        return {
            "brand": brand,
            "type": "cardnews",
            "slot": slot_name,
            "total_target": len(GOLDEN_EIGHT_LANGUAGES),
            "success_count": success_count,
            "results": results
        }

    def execute_slot(self, slot_name: str = "morning", brand: str = "all") -> Dict[str, Any]:
        """
        정기 골든 타임 슬롯 (오전 11:30 또는 저녁 18:30) 독립/통합 배치 실행
        - brand="easytax": 이지텍스 8개국 숏폼 8편 + 8개국 카드뉴스 8세트 (16건)
        - brand="kmarket": KTRS 마켓 8개국 숏폼 8편 + 8개국 카드뉴스 8세트 (16건)
        - brand="all": 양대 브랜드 모두 실행 (총 32건)
        """
        start_time = time.time()
        slot_title = "오전 11:30 피크 슬롯" if slot_name == "morning" else "저녁 18:30 피크 슬롯" if slot_name == "evening" else f"수동 실행 ({slot_name})"
        target_name = "이지텍스 전용" if brand == "easytax" else "KTRS 마켓 전용" if brand == "kmarket" else "듀얼 채널 통합"
        logger.info(f"🚀 [골든 타임 배치 가동: {target_name}] {slot_title} - 8대 국가 대량 생산 돌입!")
        
        tax_shorts = {"success_count": 0}
        tax_cards = {"success_count": 0}
        km_shorts = {"success_count": 0}
        km_cards = {"success_count": 0}

        # 1. EasyTax 독립 실행
        if brand in ["easytax", "all"]:
            logger.info("💰 [EasyTax] 8개국 숏폼 8편 + 카드뉴스 8세트 생산 시작...")
            tax_shorts = self.produce_brand_shorts_batch(brand="easytax", slot_name=slot_name)
            tax_cards = self.produce_brand_cardnews_batch(brand="easytax", slot_name=slot_name)
        
        # 2. K-Market 독립 실행
        if brand in ["kmarket", "all"]:
            logger.info("🛒 [K-Market] 8개국 숏폼 8편 + 카드뉴스 8세트 생산 시작...")
            km_shorts = self.produce_brand_shorts_batch(brand="kmarket", slot_name=slot_name)
            km_cards = self.produce_brand_cardnews_batch(brand="kmarket", slot_name=slot_name)
        
        elapsed = round(time.time() - start_time, 1)
        total_shorts = tax_shorts["success_count"] + km_shorts["success_count"]
        total_cards = tax_cards["success_count"] + km_cards["success_count"]
        total_items = total_shorts + total_cards
        
        summary_msg = (
            f"🎉 [{slot_title} ({target_name}) 완료 - {elapsed}초 소요] "
            f"총 {total_items}건 완성 (숏폼 {total_shorts}편 + 카드뉴스 {total_cards}세트) "
            f"➔ 바탕화면 산출물 저장 완료!"
        )
        logger.info(summary_msg)
        
        return {
            "success": True,
            "brand": brand,
            "slot_name": slot_name,
            "elapsed_seconds": elapsed,
            "total_items": total_items,
            "shorts_success": total_shorts,
            "shorts_total": 8 if brand in ["easytax", "kmarket"] else 16,
            "cardnews_success": total_cards,
            "cardnews_total": 8 if brand in ["easytax", "kmarket"] else 16,
            "summary": {
                "easytax_shorts": tax_shorts["success_count"],
                "easytax_cardnews": tax_cards["success_count"],
                "kmarket_shorts": km_shorts["success_count"],
                "kmarket_cardnews": km_cards["success_count"],
            },
            "message": summary_msg
        }

    def get_today_production_summary(self) -> Dict[str, Any]:
        """오늘 날짜 기준 8대 국가 생산 현황 집계 조회"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        default_summary = {
            "today": today_str,
            "total_shorts": 0,
            "total_cardnews": 0,
            "total_content": 0,
            "morning_slot_done": False,
            "evening_slot_done": False,
            "golden_languages": GOLDEN_EIGHT_LANGUAGES
        }
        
        if not self.stats_file.exists():
            return default_summary
            
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                stats = json.load(f)
            today_data = stats.get(today_str, {})
            
            m_shorts = today_data.get("morning", {}).get("shorts", 0)
            m_cards = today_data.get("morning", {}).get("cardnews", 0)
            e_shorts = today_data.get("evening", {}).get("shorts", 0)
            e_cards = today_data.get("evening", {}).get("cardnews", 0)
            man_shorts = today_data.get("manual", {}).get("shorts", 0)
            man_cards = today_data.get("manual", {}).get("cardnews", 0)
            
            total_s = m_shorts + e_shorts + man_shorts
            total_c = m_cards + e_cards + man_cards
            
            return {
                "today": today_str,
                "total_shorts": total_s,
                "total_cardnews": total_c,
                "total_content": total_s + total_c,
                "morning_slot_done": m_shorts > 0 or m_cards > 0,
                "evening_slot_done": e_shorts > 0 or e_cards > 0,
                "golden_languages": GOLDEN_EIGHT_LANGUAGES
            }
        except Exception:
            return default_summary
