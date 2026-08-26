import logging
from typing import List, Dict, Any, Optional
from config import SUPABASE_URL, SUPABASE_KEY
from core.db_manager import DBManager

logger = logging.getLogger("SupabaseManager")

class SupabaseManager:
    """
    Supabase 클라우드 중앙 데이터 저장 & Few-Shot 고득점 카피 추출기
    - 🛒 K-Market 전용 테이블: kmarket_golden_copies
    - 💰 EasyTax 전용 테이블: easytax_golden_copies
    (미설정 시 로컬 DB Fallback 지원으로 무중단 가동)
    """
    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db_manager = db_manager or DBManager()
        self.client = None
        self._init_client()

    def _init_client(self):
        if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
            try:
                from supabase import create_client
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("Supabase 클라우드 연동 성공! (kmarket_golden_copies & easytax_golden_copies 2개 테이블 분리 모드)")
            except Exception as e:
                logger.warning(f"Supabase 클라이언트 초기화 실패 (로컬 모드 가동): {e}")
                self.client = None
        else:
            logger.info("Supabase 미설정 -> 로컬 SQLite 자가학습 2개 테이블 모드로 가동.")

    def sync_histories_to_cloud(self) -> int:
        """로컬 미동기화 레코드를 Supabase 2개 독립 테이블로 분리 업로드"""
        if not self.client:
            return 0

        unsynced = self.db_manager.get_unsynced_histories()
        if not unsynced:
            return 0

        synced_ids = []
        for record in unsynced:
            service_id = record.get("service_id", "kmarket")
            target_table = "easytax_golden_copies" if service_id == "easytax" else "kmarket_golden_copies"

            try:
                payload = {
                    "content_type": record["content_type"],
                    "service_id": service_id,
                    "target_lang": record["target_lang"],
                    "title": record.get("title", ""),
                    "content_text": record["content_text"],
                    "target_url": record.get("target_url", ""),
                    "external_id": record.get("external_id"),
                    "score": record.get("score", 0.0),
                    "views": record.get("views", 0),
                    "clicks": record.get("clicks", 0),
                    "conversions": record.get("conversions", 0),
                    "created_at": record.get("created_at")
                }
                # 브랜드별 전용 테이블에 격리 upsert
                self.client.table(target_table).upsert(payload).execute()
                synced_ids.append(record["id"])
            except Exception as e:
                logger.error(f"Supabase {target_table} 동기화 에러 (ID {record['id']}): {e}")

        if synced_ids:
            self.db_manager.mark_synced_supabase(synced_ids)
            logger.info(f"Supabase 2개 테이블({len(synced_ids)}건) 분리 동기화 완료")

        return len(synced_ids)

    def fetch_golden_few_shots(self, service_id: str, lang: str, min_score: float = 80.0, limit: int = 3) -> List[str]:
        """
        자가학습용 고득점 베스트 골든 카피 추출 (2개 테이블 엄격 분리 쿼리)
        - K-Market은 kmarket_golden_copies 테이블만 조회
        - EasyTax는 easytax_golden_copies 테이블만 조회
        """
        target_table = "easytax_golden_copies" if service_id == "easytax" else "kmarket_golden_copies"

        # 1. Supabase 브랜드 전용 테이블에서 조회
        if self.client:
            try:
                response = self.client.table(target_table) \
                    .select("content_text") \
                    .eq("target_lang", lang) \
                    .gte("score", min_score) \
                    .order("score", desc=True) \
                    .limit(limit) \
                    .execute()
                if response.data:
                    return [item["content_text"] for item in response.data]
            except Exception as e:
                logger.warning(f"Supabase {target_table} 조회 실패, 로컬 DB 대체: {e}")

        # 2. 로컬 DB Fallback
        return self.db_manager.get_top_performing_copies(service_id, lang, min_score, limit)

    def fetch_easytax_proven_scripts(self, psychology: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        """
        [EasyTax 자가학습 고도화] Supabase refund_scripts 테이블에서
        검증된 S등급 성공 가중치(success_weight) 상위 스크립트 실시간 추출
        """
        if self.client:
            try:
                query = self.client.table("refund_scripts") \
                    .select("id, refund_step, target_psychology, script_text, success_weight, conversion_rate")
                
                if psychology:
                    query = query.eq("target_psychology", psychology)
                
                response = query.order("success_weight", desc=True).limit(limit).execute()
                if response.data:
                    return response.data
            except Exception as e:
                logger.warning(f"Supabase refund_scripts 고도화 스크립트 조회 실패: {e}")
        return []

    def fetch_live_kmarket_items(self, free_only: bool = False, psychology: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        [K-Market 자가학습 고도화] 3대 심리 유형별 최적 매물 실시간 추출
        - free_giveaway_emotional: 0원 무료 나눔 물품 우선
        - urgent_moving_discount: is_moving_sale 또는 가격 인하(is_price_dropped) 매물 우선
        - multi_lang_comfort: 번역(translations) 완료 매물 우선
        """
        if self.client:
            try:
                query = self.client.table("kmarket_items").select("*")
                
                if free_only or psychology == "free_giveaway_emotional":
                    query = query.eq("price", 0)
                elif psychology == "urgent_moving_discount":
                    query = query.or_("is_moving_sale.eq.true,is_price_dropped.eq.true")
                
                query = query.order("created_at", desc=True).limit(limit)
                response = query.execute()
                if response.data:
                    return response.data
            except Exception as e:
                logger.warning(f"Supabase kmarket_items 실시간 조회 실패: {e}")

        # Fallback to local items
        from config import DATA_DIR
        import json
        local_path = DATA_DIR / "kmarket_items.json"
        if local_path.exists():
            with open(local_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                if free_only or psychology == "free_giveaway_emotional":
                    items = [it for it in items if it.get("price", 0) == 0]
                return items[:limit]
        return []

    def record_feedback_and_weight(self, service_id: str, external_id: str, score: float, is_conversion: bool = False):
        """
        [실시간 자가 보정 루프] 성과 피드백에 따라 Supabase 골든 카피 테이블 및 가중치 갱신
        """
        target_table = "easytax_golden_copies" if service_id == "easytax" else "kmarket_golden_copies"
        if self.client and external_id:
            try:
                update_data = {"score": score}
                if is_conversion:
                    update_data["conversions"] = 1
                self.client.table(target_table).update(update_data).eq("external_id", external_id).execute()
                logger.info(f"Supabase {target_table} 성과 가중치 자가 보정 완료: {external_id} -> {score}점")
            except Exception as e:
                logger.warning(f"Supabase 가중치 갱신 실패: {e}")

    def fetch_live_funnel_stats(self) -> Dict[str, Any]:
        """
        [실시간 전환 퍼널 분석] Supabase 클라우드 실데이터 집계
        - K-Market: 총 회원수, 활성 매물수, 0원 나눔 예약수
        - EasyTax: 총 환급 신청서, 환급 완료 건수, 누적 환급 금액(KRW)
        """
        stats = {
            "kmarket": {
                "total_users": 0,
                "total_items": 0,
                "free_items": 0,
                "total_appointments": 0
            },
            "easytax": {
                "total_applications": 0,
                "completed_applications": 0,
                "total_refund_krw": 0,
                "in_progress_applications": 0
            }
        }

        if not self.client:
            return stats

        try:
            # 1. K-Market 유저 수
            u_res = self.client.table("kmarket_users").select("id", count="exact").execute()
            stats["kmarket"]["total_users"] = u_res.count or len(u_res.data or [])

            # 2. K-Market 매물 수
            i_res = self.client.table("kmarket_items").select("id", count="exact").execute()
            stats["kmarket"]["total_items"] = i_res.count or len(i_res.data or [])

            # 3. K-Market 0원 나눔 수
            f_res = self.client.table("kmarket_items").select("id", count="exact").eq("price", 0).execute()
            stats["kmarket"]["free_items"] = f_res.count or len(f_res.data or [])

            # 4. K-Market 거래/예약 수
            a_res = self.client.table("kmarket_appointments").select("id", count="exact").execute()
            stats["kmarket"]["total_appointments"] = a_res.count or len(a_res.data or [])

            # 5. EasyTax 환급 신청서 전체
            tax_res = self.client.table("tax_applications").select("id, status, estimated_refund_amount").execute()
            if tax_res.data:
                stats["easytax"]["total_applications"] = len(tax_res.data)
                completed = [t for t in tax_res.data if str(t.get("status", "")).lower() in ["completed", "approved", "done", "환급완료"]]
                stats["easytax"]["completed_applications"] = len(completed)
                stats["easytax"]["in_progress_applications"] = len(tax_res.data) - len(completed)
                
                total_refund = sum([int(t.get("estimated_refund_amount") or 0) for t in completed])
                if total_refund == 0:
                    total_refund = sum([int(t.get("estimated_refund_amount") or 0) for t in tax_res.data])
                stats["easytax"]["total_refund_krw"] = total_refund
        except Exception as e:
            logger.warning(f"Supabase 퍼널 통계 집계 중 오류: {e}")

        return stats

    def promote_conversion_golden_copy(self, service_id: str, campaign_tag: str, conversion_type: str = "signup"):
        """
        [비즈니스 전환 자가학습 루프] 회원가입(+50점) 또는 환급완료(+100점) 발생 시
        해당 캠페인 카피를 즉시 S등급(85~98점) 골든 카피로 자동 승격!
        """
        target_table = "easytax_golden_copies" if service_id == "easytax" else "kmarket_golden_copies"
        bonus_score = 98.0 if conversion_type in ["refund_completed", "trade_completed"] else 92.0

        if self.client and campaign_tag:
            try:
                # 해당 캠페인 태그가 포함된 카피 검색 후 승격
                rows = self.client.table(target_table).select("id, score, conversions").like("external_id", f"%{campaign_tag}%").execute()
                if rows.data:
                    for r in rows.data:
                        new_conversions = (r.get("conversions") or 0) + 1
                        self.client.table(target_table).update({
                            "score": bonus_score,
                            "conversions": new_conversions
                        }).eq("id", r["id"]).execute()
                        logger.info(f"🏆 [골든 카피 자동 승격] {target_table} ID {r['id']} -> {bonus_score}점 (전환유형: {conversion_type})")
            except Exception as e:
                logger.warning(f"골든 카피 전환 승격 실패: {e}")

