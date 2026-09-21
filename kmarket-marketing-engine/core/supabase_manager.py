import logging
import datetime
from typing import List, Dict, Any, Optional
from config import SUPABASE_URL, SUPABASE_KEY, KST, get_now_kst
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
        import random
        if self.client:
            try:
                query = self.client.table("kmarket_items").select("*")
                
                if free_only or psychology == "free_giveaway_emotional":
                    query = query.eq("price", 0)
                elif psychology == "urgent_moving_discount":
                    query = query.or_("is_moving_sale.eq.true,is_price_dropped.eq.true")
                
                # 실시간 270개 전체에서 무작위 롤링 추출
                response = query.limit(100).execute()
                if response.data:
                    items_pool = response.data
                    random.shuffle(items_pool)
                    return items_pool[:limit]
            except Exception as e:
                logger.warning(f"Supabase kmarket_items 실시간 조회 실패: {e}")

        # Fallback to local items (270개 실물 매물 실시간 롤링)
        from config import DATA_DIR
        import json
        local_path = DATA_DIR / "kmarket_items.json"
        if local_path.exists():
            with open(local_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                if free_only or psychology == "free_giveaway_emotional":
                    items = [it for it in items if it.get("price", 0) == 0]
                random.shuffle(items)
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

    def record_marketing_media_asset(self, payload: Dict[str, Any]) -> Optional[int]:
        """[AI 미디어 자산 등록 & 품질 검증 기록] Supabase marketing_media_assets 테이블에 저장"""
        if self.client:
            try:
                res = self.client.table("marketing_media_assets").insert(payload).execute()
                if res.data:
                    logger.info(f"✅ Supabase 미디어 자산 기록 성공: {payload.get('theme_id')} ({payload.get('quality_score')}점)")
                    return res.data[0].get("id")
            except Exception as e:
                logger.warning(f"Supabase marketing_media_assets 기록 실패: {e}")
        return None

    def fetch_best_learning_theme(self, service_id: str, lang: str) -> Optional[str]:
        """[자가학습 강화 루프] Supabase theme_learning_weights에서 승률 가장 높은 테마 조회"""
        if self.client:
            try:
                res = self.client.table("theme_learning_weights") \
                    .select("theme_id, current_weight, win_rate") \
                    .eq("service_id", service_id) \
                    .eq("target_lang", lang) \
                    .order("current_weight", desc=True) \
                    .limit(1) \
                    .execute()
                if res.data and len(res.data) > 0:
                    best_theme = res.data[0].get("theme_id")
                    logger.info(f"🧠 [자가학습 가중치 적용] {lang.upper()} 최고 성과 테마: {best_theme}")
                    return best_theme
            except Exception as e:
                logger.warning(f"Supabase theme_learning_weights 조회 실패: {e}")
        return None

    def update_theme_conversion_win(self, service_id: str, lang: str, theme_id: str):
        """[성과 기반 가중치 승격] 특정 테마에서 전환 발생 시 해당 테마 가중치 +0.5 자동 상승"""
        if self.client:
            try:
                # 기존 가중치 확인
                res = self.client.table("theme_learning_weights") \
                    .select("current_weight, total_conversions") \
                    .eq("service_id", service_id) \
                    .eq("target_lang", lang) \
                    .eq("theme_id", theme_id) \
                    .execute()
                
                cur_weight = 1.0
                conversions = 1
                if res.data and len(res.data) > 0:
                    cur_weight = float(res.data[0].get("current_weight", 1.0)) + 0.5
                    conversions = int(res.data[0].get("total_conversions", 0)) + 1
                
                self.client.table("theme_learning_weights").upsert({
                    "service_id": service_id,
                    "target_lang": lang,
                    "theme_id": theme_id,
                    "current_weight": cur_weight,
                    "total_conversions": conversions
                }).execute()
                logger.info(f"🏆 [테마 가중치 자가학습 승격] {lang}/{theme_id} -> 가중치 {cur_weight}")
            except Exception as e:
                logger.warning(f"테마 가중치 승격 실패: {e}")

    def upload_blog_article(self, service_id: str, payload: Dict[str, Any]) -> bool:
        """
        🌐 [17개국어 서브경로 블로그 Supabase 실시간 Upsert]
        - K-Market은 kmarket_blogs 테이블에 업로드
        - EasyTax는 easytax_blogs 테이블에 업로드
        - (slug, target_lang) 복합 유니크 키 기준 자동 Upsert
        """
        if not self.client:
            logger.info(f"Supabase 미연동 -> 블로그 로컬 모드로만 저장됩니다. ({service_id}/{payload.get('slug')})")
            return False

        target_table = "easytax_blogs" if service_id == "easytax" else "kmarket_blogs"

        try:
            record = {
                "slug": payload.get("slug"),
                "target_lang": payload.get("target_lang", "en"),
                "title": payload.get("title", ""),
                "excerpt": payload.get("excerpt", ""),
                "content_html": payload.get("content_html", ""),
                "content_md": payload.get("content_md", ""),
                "thumbnail_url": payload.get("thumbnail_url", ""),
                "category": payload.get("category", "guide"),
                "author": payload.get("author", "Expat Editor"),
                "views": payload.get("views", 0),
                "likes": payload.get("likes", 0),
                "published_at": payload.get("published_at") or get_now_kst().isoformat(),
                "updated_at": get_now_kst().isoformat()
            }
            res = self.client.table(target_table).upsert(record, on_conflict="slug,target_lang").execute()
            logger.info(f"✅ [Supabase Blog 업로드 성공] {target_table} -> [{payload.get('target_lang')}] {payload.get('title')}")
            return True
        except Exception as e:
            logger.error(f"❌ [Supabase Blog 업로드 에러] {target_table} ({payload.get('slug')}): {e}")
            return False

    def set_active_gpu_url(self, url: str) -> bool:
        """
        🚀 [구글 코랩 무료 GPU URL 클라우드 실시간 등록]
        - 코랩 서버 가동 즉시 Supabase에 새 터널 URL 자동 등록
        - 로컬 .env 파일도 자동 동기화 갱신
        """
        url = url.strip().rstrip("/")
        if not url:
            return False

        # 1. Supabase system_settings 테이블에 기록
        if self.client:
            try:
                self.client.table("system_settings").upsert({
                    "setting_key": "colab_gpu_api_url",
                    "setting_value": url,
                    "updated_at": get_now_kst().isoformat()
                }, on_conflict="setting_key").execute()
                logger.info(f"☁️ [Supabase GPU URL 동기화 완료]: {url}")
            except Exception as e:
                logger.warning(f"Supabase system_settings 기록 실패 (경고): {e}")

        # 2. 로컬 .env 파일도 자동 갱신
        try:
            from config import BASE_DIR
            env_file = BASE_DIR / ".env"
            if env_file.exists():
                lines = env_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                new_lines = []
                found = False
                for line in lines:
                    if line.startswith("COLAB_GPU_API_URL="):
                        new_lines.append(f"COLAB_GPU_API_URL={url}")
                        found = True
                    else:
                        new_lines.append(line)
                if not found:
                    new_lines.append(f"COLAB_GPU_API_URL={url}")
                env_file.write_text("\n".join(new_lines), encoding="utf-8")
        except Exception as e:
            logger.warning(f".env 파일 GPU URL 갱신 실패: {e}")

        return True

    def get_active_gpu_url(self) -> str:
        """
        🔍 [최신 활성 구글 코랩 GPU URL 실시간 조회]
        - 1순위: Supabase 클라우드 실시간 조회
        - 2순위: 로컬 .env 및 config 조회
        """
        # 1. Supabase 클라우드에서 조회
        if self.client:
            try:
                res = self.client.table("system_settings") \
                    .select("setting_value") \
                    .eq("setting_key", "colab_gpu_api_url") \
                    .execute()
                if res.data and len(res.data) > 0:
                    cloud_url = res.data[0].get("setting_value", "").strip()
                    if cloud_url.startswith("http"):
                        return cloud_url
            except Exception as e:
                pass

        # 2. Fallback: 로컬 환경 변수
        import os
        return os.getenv("COLAB_GPU_API_URL", "").strip()

    def fetch_live_traffic_data(self, brand: str = "all", period: str = "today", limit: int = 150) -> Dict[str, Any]:
        """
        📊 [실시간 유입 트래픽 및 UTM 관제 데이터 통합 집계]
        - Supabase kmarket_traffic_logs, marketing_utm_logs, tax_applications 실데이터 조회
        - UTC -> KST(+9) 시간 변환 및 5단계 기간 필터링:
          1) today (오늘 24H 시간대별)
          2) daily (최근 14일 날짜별)
          3) weekly (최근 8주 주간별)
          4) monthly (당해 12개월 월별)
          5) yearly (2024~2027 연도별)
        - 출처(10대 채널), 17개국 언어/국가, 캠페인, 접속 일시 및 원본 타임스탬프 완벽 구조화
        """
        result = {
            "total_count": 0,
            "period_count": 0,
            "km_count": 0,
            "tax_count": 0,
            "sources_map": {},
            "countries_map": {},
            "visitors_list": [],
            "raw_timestamps": []
        }
        if not self.client:
            return result

        try:
            import re
            now_kst = get_now_kst()
            today_start_kst = datetime.datetime(now_kst.year, now_kst.month, now_kst.day, tzinfo=KST)

            if period == "daily":
                period_start_kst = today_start_kst - datetime.timedelta(days=14)
            elif period == "weekly":
                period_start_kst = today_start_kst - datetime.timedelta(days=56) # 8주
            elif period == "monthly":
                period_start_kst = datetime.datetime(now_kst.year, 1, 1, tzinfo=KST)
            elif period == "yearly":
                period_start_kst = datetime.datetime(2024, 1, 1, tzinfo=KST)
            else: # today (기본 24시간)
                period_start_kst = today_start_kst

            period_start_utc_iso = period_start_kst.astimezone(datetime.timezone.utc).isoformat()

            def to_kst_datetime(ts_str):
                if not ts_str:
                    return now_kst
                try:
                    s = str(ts_str).replace('Z', '+00:00')
                    parsed = datetime.datetime.fromisoformat(s)
                    if parsed.tzinfo is None:
                        return parsed.replace(tzinfo=KST)
                    else:
                        kst_cand = parsed.astimezone(KST)
                        # KST 시간이 +00:00로 잘못 표기되어 미래 시간으로 튀는 현상(+9h 이중 오프셋) 자동 보정
                        if kst_cand > now_kst + datetime.timedelta(minutes=3):
                            reverted = parsed.replace(tzinfo=KST)
                            if reverted <= now_kst + datetime.timedelta(minutes=3):
                                return reverted
                        return kst_cand
                except Exception:
                    return now_kst

            brand_filter = (brand or "all").lower()

            all_visitors = []
            sources_map = {}
            countries_map = {}
            raw_timestamps = []
            period_count = 0
            total_count = 0
            km_period_count = 0
            tax_period_count = 0
            km_visitors_list = []
            tax_visitors_list = []
            km_sources_map = {}
            tax_sources_map = {}
            km_countries_map = {}
            tax_countries_map = {}
            km_raw_timestamps = []
            tax_raw_timestamps = []

            lang_name_map = {
                "mn": ("몽골", "🇲🇳 몽골어", "mn"),
                "km": ("캄보디아", "🇰🇭 캄보디아어", "km"),
                "vi": ("베트남", "🇻🇳 베트남어", "vi"),
                "my": ("미얀마", "🇲🇲 미얀마어", "my"),
                "ne": ("네팔", "🇳🇵 네팔어", "ne"),
                "th": ("태국", "🇹🇭 태국어", "th"),
                "uz": ("우즈베키스탄", "🇺🇿 우즈벡어", "uz"),
                "id": ("인도네시아", "🇮🇩 인도네시아어", "id"),
                "en": ("미국/글로벌", "🇺🇸 영어", "en"),
                "zh": ("중국", "🇨🇳 중국어", "zh"),
                "ru": ("러시아", "🇷🇺 러시아어", "ru"),
                "ja": ("일본", "🇯🇵 일본어", "ja"),
                "si": ("스리랑카", "🇱🇰 스리랑카어", "si"),
                "kk": ("카자흐스탄", "🇰🇿 카자흐어", "kk"),
                "bn": ("방글라데시", "🇧🇩 방글라어", "bn"),
                "ur": ("파키스탄", "🇵🇰 우르두어", "ur"),
                "ko": ("대한민국", "🇰🇷 한국어", "ko")
            }

            # 1. tax_applications (EasyTax 조특법 90% 환급 신청 및 모의계산 완료 - 100% 실제 전환)
            if brand_filter in ["all", "easytax"]:
                try:
                    tot_tax = self.client.table("tax_applications").select("id", count="exact").execute()
                    tax_total = tot_tax.count or 0
                    total_count += tax_total

                    tax_res = self.client.table("tax_applications") \
                        .select("*") \
                        .gte("created_at", period_start_utc_iso) \
                        .order("created_at", desc=True) \
                        .execute()
                    tax_rows = tax_res.data or []

                    for r in tax_rows:
                        meta = r.get("metadata") or {}
                        usrc = (meta.get("utmSource") or "facebook").lower()
                        umed = (meta.get("utmMedium") or "form").lower()
                        ulang = meta.get("userLanguage") or r.get("language") or "vi"
                        refund_est = r.get("estimated_refund_amount") or meta.get("preFilterEstimate") or 0

                        if "facebook" in usrc or "fb" in usrc:
                            channel = "Facebook"
                            ch_icon = "📘"
                        elif "instagram" in usrc or "ig" in usrc:
                            channel = "Instagram"
                            ch_icon = "📸"
                        elif "tiktok" in usrc:
                            channel = "TikTok"
                            ch_icon = "🎵"
                        elif "telegram" in usrc:
                            channel = "Telegram"
                            ch_icon = "📲"
                        elif "reddit" in usrc:
                            channel = "Reddit"
                            ch_icon = "🤖"
                        elif "threads" in usrc:
                            channel = "Threads"
                            ch_icon = "🧵"
                        elif "google" in usrc or "seo" in usrc:
                            channel = "Google SEO"
                            ch_icon = "🌐"
                        else:
                            channel = usrc.capitalize() if usrc else "Facebook"
                            ch_icon = "📘"

                        period_count += 1
                        tax_period_count += 1
                        sources_map[channel] = sources_map.get(channel, 0) + 1
                        tax_sources_map[channel] = tax_sources_map.get(channel, 0) + 1

                        country_info = lang_name_map.get(ulang, ("베트남", f"언어: {ulang}", ulang))
                        c_name = country_info[0]
                        lang_label = country_info[1]
                        countries_map[c_name] = countries_map.get(c_name, 0) + 1
                        tax_countries_map[c_name] = tax_countries_map.get(c_name, 0) + 1

                        target_app = f"EasyTax ({lang_label})"
                        camp = f"💰 예상환급 {refund_est:,.0f}원 모의계산 완료" if refund_est else "세금 환급 신청서 접수"

                        dt_kst = to_kst_datetime(r.get("created_at"))
                        dt_kst_str = dt_kst.strftime("%Y-%m-%d %H:%M:%S")

                        raw_timestamps.append(dt_kst)
                        tax_raw_timestamps.append(dt_kst)
                        v_obj = {
                            "brand": "easytax",
                            "brand_label": "EasyTax",
                            "brand_icon": "💰",
                            "source_name": channel,
                            "channel_icon": ch_icon,
                            "medium": umed,
                            "campaign": camp,
                            "country": c_name,
                            "lang_label": lang_label,
                            "target_app": target_app,
                            "action_stage": "조특법 90% 감면 계산 / 국세청 환급 접수",
                            "ip": "신청 접수 완료 (인증됨)",
                            "created_at": dt_kst_str,
                            "_dt": dt_kst
                        }
                        all_visitors.append(v_obj)
                        tax_visitors_list.append(v_obj)
                except Exception as e:
                    logger.warning(f"Supabase tax_applications 조회 예외: {e}")

            # 2. kmarket_traffic_logs (실제 SNS 마케팅 링크 유입 전수 조회)
            seo_crawler_count = 0
            try:
                # 2-1. utm_source가 있는 실제 마케팅 바이럴 유입 전수 조회
                utm_period_res = self.client.table("kmarket_traffic_logs") \
                    .select("*") \
                    .gte("created_at", period_start_utc_iso) \
                    .not_.is_("utm_source", "null") \
                    .order("created_at", desc=True) \
                    .execute()
                all_traffic_rows = utm_period_res.data or []

                for r in all_traffic_rows:
                    ckey = (r.get("channel_key") or "").lower()
                    cname = r.get("channel_name") or ""
                    surl = r.get("source_url") or ""
                    ref = (r.get("referrer") or "").lower()
                    usrc = (r.get("utm_source") or "").lower()
                    umed = (r.get("utm_medium") or "").lower()

                    # 서비스 판별 (EasyTax vs K-Market)
                    is_easytax = (
                        "ktrs-service" in surl.lower() or 
                        "easy-tax" in surl.lower() or 
                        "easytax" in surl.lower() or 
                        "tax" in surl.lower() or
                        "easytax" in cname.lower() or
                        "이지텍스" in cname or
                        "세무" in cname
                    )
                    record_brand = "easytax" if is_easytax else "kmarket"

                    # 브랜드 필터 적용
                    if brand_filter != "all" and brand_filter != record_brand:
                        continue

                    period_count += 1
                    total_count += 1
                    if is_easytax:
                        tax_period_count += 1
                    else:
                        km_period_count += 1

                    if "threads" in usrc or "threads" in ckey or "threads" in ref or "threads" in surl:
                        channel = "Threads"
                        ch_icon = "🧵"
                    elif "instagram" in ckey or usrc in ["ig", "instagram", "ig_text_post_permalink"] or "instagram" in ref:
                        channel = "Instagram"
                        ch_icon = "📸"
                    elif "tiktok" in ckey or usrc in ["tiktok", "tt"] or "tiktok" in ref:
                        channel = "TikTok"
                        ch_icon = "🎵"
                    elif "facebook" in ckey or usrc in ["fb", "facebook"] or "facebook" in ref or "fbclid" in surl:
                        channel = "Facebook"
                        ch_icon = "📘"
                    elif "telegram" in ckey or usrc == "telegram" or "t.me" in ref:
                        channel = "Telegram"
                        ch_icon = "📲"
                    elif "reddit" in ckey or usrc == "reddit" or "reddit.com" in ref:
                        channel = "Reddit"
                        ch_icon = "🤖"
                    elif "youtube" in ckey or usrc in ["youtube", "yt"] or "youtu.be" in ref:
                        channel = "YouTube"
                        ch_icon = "▶️"
                    elif "google" in ckey or "google" in usrc or "google" in ref:
                        channel = "Google SEO"
                        ch_icon = "🌐"
                    else:
                        channel = usrc.capitalize() if usrc else "SNS 바이럴 링크"
                        ch_icon = "🌐"

                    sources_map[channel] = sources_map.get(channel, 0) + 1
                    if is_easytax:
                        tax_sources_map[channel] = tax_sources_map.get(channel, 0) + 1
                    else:
                        km_sources_map[channel] = km_sources_map.get(channel, 0) + 1

                    lang_code = ""
                    m = re.search(r"(?:ktrs-market|ktrs-service)\.vercel\.app/([a-z]{2})", surl)
                    if m:
                        lang_code = m.group(1)
                    elif "lang=" in surl:
                        m2 = re.search(r"lang=([a-z]{2})", surl)
                        if m2:
                            lang_code = m2.group(1)

                    country_info = lang_name_map.get(lang_code, ("글로벌", f"/{lang_code}" if lang_code else "메인 홈", lang_code or "global"))
                    c_name = country_info[0]
                    lang_label = country_info[1]
                    countries_map[c_name] = countries_map.get(c_name, 0) + 1
                    if is_easytax:
                        tax_countries_map[c_name] = tax_countries_map.get(c_name, 0) + 1
                    else:
                        km_countries_map[c_name] = km_countries_map.get(c_name, 0) + 1

                    b_label = "EasyTax" if is_easytax else "K-Market"
                    b_icon = "💰" if is_easytax else "🛒"
                    target_app = f"{b_label} ({lang_label})"
                    action_stage = "조특법 90% 세무 환급 조회 / 모의계산" if is_easytax else "실물 매물 탐색 / 번역 채팅 진입"
                    camp = r.get("utm_campaign") or f"SNS 바이럴 링크 ({channel})"

                    dt_kst = to_kst_datetime(r.get("created_at"))
                    dt_kst_str = dt_kst.strftime("%Y-%m-%d %H:%M:%S")

                    raw_timestamps.append(dt_kst)
                    if is_easytax:
                        tax_raw_timestamps.append(dt_kst)
                    else:
                        km_raw_timestamps.append(dt_kst)

                    v_obj = {
                        "brand": record_brand,
                        "brand_label": b_label,
                        "brand_icon": b_icon,
                        "source_name": channel,
                        "channel_icon": ch_icon,
                        "medium": umed or "social",
                        "campaign": camp,
                        "country": c_name,
                        "lang_label": lang_label,
                        "target_app": target_app,
                        "action_stage": action_stage,
                        "ip": "클라우드 검증됨 (Vercel)",
                        "created_at": dt_kst_str,
                        "_dt": dt_kst
                    }
                    all_visitors.append(v_obj)
                    if is_easytax:
                        tax_visitors_list.append(v_obj)
                    else:
                        km_visitors_list.append(v_obj)

                # 2-2. 구글 SEO 크롤링 및 다이렉트 탐색 로그 카운트
                seo_cnt_res = self.client.table("kmarket_traffic_logs") \
                    .select("id", count="exact") \
                    .gte("created_at", period_start_utc_iso) \
                    .is_("utm_source", "null") \
                    .execute()
                seo_crawler_count = seo_cnt_res.count or 0

            except Exception as e:
                logger.warning(f"Supabase kmarket_traffic_logs 조회 예외: {e}")

            # 3. marketing_utm_logs (중앙 마케팅 UTM 로그)
            try:
                utm_res = self.client.table("marketing_utm_logs") \
                    .select("*") \
                    .gte("created_at", period_start_utc_iso) \
                    .order("created_at", desc=True) \
                    .execute()
                for r in (utm_res.data or []):
                    srv = (r.get("service_id") or "kmarket").lower()
                    if brand_filter != "all" and srv != brand_filter:
                        continue
                    total_count += 1
                    period_count += 1
                    if srv == "kmarket":
                        km_period_count += 1
                    else:
                        tax_period_count += 1

                    plat = (r.get("platform") or "web").capitalize()
                    ch_icon = "📸" if "instagram" in plat.lower() else ("📘" if "facebook" in plat.lower() else ("🎵" if "tiktok" in plat.lower() else ("📲" if "telegram" in plat.lower() else ("🤖" if "reddit" in plat.lower() else ("🧵" if "threads" in plat.lower() else "🌐")))))
                    sources_map[plat] = sources_map.get(plat, 0) + 1

                    dt_kst = to_kst_datetime(r.get("created_at"))
                    dt_kst_str = dt_kst.strftime("%Y-%m-%d %H:%M:%S")

                    raw_timestamps.append(dt_kst)
                    v_obj = {
                        "brand": srv,
                        "brand_label": "K-Market" if srv == "kmarket" else "EasyTax",
                        "brand_icon": "🛒" if srv == "kmarket" else "💰",
                        "source_name": plat,
                        "channel_icon": ch_icon,
                        "medium": r.get("channel_type") or "link",
                        "campaign": r.get("campaign_id") or "마케팅 봇 링크 클릭",
                        "country": "글로벌 타깃",
                        "lang_label": "다국어 랜딩",
                        "target_app": "K-Market" if srv == "kmarket" else "EasyTax",
                        "action_stage": "외부 캠페인 링크 유입",
                        "ip": r.get("source_ip") or "클라우드 유입",
                        "created_at": dt_kst_str,
                        "_dt": dt_kst
                    }
                    all_visitors.append(v_obj)
                    if srv == "kmarket":
                        km_visitors_list.append(v_obj)
                        km_sources_map[plat] = km_sources_map.get(plat, 0) + 1
                        km_raw_timestamps.append(dt_kst)
                    else:
                        tax_visitors_list.append(v_obj)
                        tax_sources_map[plat] = tax_sources_map.get(plat, 0) + 1
                        tax_raw_timestamps.append(dt_kst)
            except Exception:
                pass

            # 최신순 정렬 및 limit 적용
            all_visitors.sort(key=lambda x: x.get("_dt") or datetime.datetime.min.replace(tzinfo=KST), reverse=True)
            for v in all_visitors:
                v.pop("_dt", None)

            km_visitors_list.sort(key=lambda x: x.get("_dt") or datetime.datetime.min.replace(tzinfo=KST), reverse=True)
            for v in km_visitors_list:
                v.pop("_dt", None)

            tax_visitors_list.sort(key=lambda x: x.get("_dt") or datetime.datetime.min.replace(tzinfo=KST), reverse=True)
            for v in tax_visitors_list:
                v.pop("_dt", None)

            result["total_count"] = total_count
            result["period_count"] = period_count
            result["km_count"] = km_period_count
            result["tax_count"] = tax_period_count
            result["seo_crawler_count"] = seo_crawler_count
            result["sources_map"] = sources_map
            result["countries_map"] = countries_map
            result["visitors_list"] = all_visitors[:limit]
            result["km_visitors_list"] = km_visitors_list[:limit]
            result["tax_visitors_list"] = tax_visitors_list[:limit]
            result["km_sources_map"] = km_sources_map
            result["tax_sources_map"] = tax_sources_map
            result["km_countries_map"] = km_countries_map
            result["tax_countries_map"] = tax_countries_map
            result["raw_timestamps"] = raw_timestamps
            result["km_raw_timestamps"] = km_raw_timestamps
            result["tax_raw_timestamps"] = tax_raw_timestamps

        except Exception as e:
            logger.error(f"fetch_live_traffic_data 실행 중 오류: {e}")

        return result


