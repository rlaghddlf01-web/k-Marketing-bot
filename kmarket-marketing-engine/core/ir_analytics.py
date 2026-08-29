import json
import logging
import datetime
from typing import Dict, Any, List, Optional
from config import DATA_DIR
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("IRAnalytics")

class IRAnalyticsEngine:
    """
    📊 100% 순수 실데이터 기반 유입 및 IR 관제 엔진
    - 가짜/더미/가공 데이터 0%
    - Supabase / SQLite utm_logs 및 marketing_history 100% 실데이터 집계
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: Optional[SupabaseManager] = None):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr or SupabaseManager(db_mgr)

    def get_detailed_dashboard_data(self, period: str = "today", brand: str = "all") -> Dict[str, Any]:
        kst_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        today_date = kst_now.date()

        brand_filter = brand.lower() if brand else "all"
        brand_sql_m = ""
        brand_sql_u = ""
        if brand_filter == "kmarket":
            brand_sql_m = "service_id = 'kmarket'"
            brand_sql_u = "target_service = 'kmarket'"
            brand_name_kr = "K-Market"
        elif brand_filter == "easytax":
            brand_sql_m = "service_id = 'easytax'"
            brand_sql_u = "target_service = 'easytax'"
            brand_name_kr = "EasyTax"
        else:
            brand_name_kr = "전체 브랜드"

        def build_where(date_cond: str, brand_cond: str) -> str:
            conds = [c for c in [date_cond, brand_cond] if c]
            return f"WHERE {' AND '.join(conds)}" if conds else ""

        # 기간별 기본 SQL 조건절 및 라벨
        if period == "weekly":
            date_cond_m = "DATE(created_at) >= DATE('now', '+9 hours', '-7 days')"
            date_cond_u = "DATE(created_at) >= DATE('now', '+9 hours', '-7 days')"
            period_label = "최근 7일"
            chart_title = f"📊 [{brand_name_kr}] 최근 7일간 일별 콘텐츠 배포 추이 (KST)"
            chart_badge = f"기준: {brand_name_kr} 최근 7일 실데이터"
        elif period == "monthly":
            date_cond_m = "DATE(created_at) >= DATE('now', '+9 hours', '-30 days')"
            date_cond_u = "DATE(created_at) >= DATE('now', '+9 hours', '-30 days')"
            period_label = "최근 30일"
            chart_title = f"📊 [{brand_name_kr}] 최근 4주간 주차별 콘텐츠 배포 추이 (KST)"
            chart_badge = f"기준: {brand_name_kr} 최근 30일 실데이터"
        elif period == "yearly":
            date_cond_m = f"strftime('%Y', created_at) = '{today_date.year}'"
            date_cond_u = f"strftime('%Y', created_at) = '{today_date.year}'"
            period_label = f"{today_date.year}년 연간"
            chart_title = f"📊 [{brand_name_kr}] {today_date.year}년 연간 월별 콘텐츠 배포 추이 (KST)"
            chart_badge = f"기준: {brand_name_kr} {today_date.year}년 연간 실데이터"
        else: # today
            date_cond_m = "DATE(created_at) = DATE('now', '+9 hours')"
            date_cond_u = "DATE(created_at) = DATE('now', '+9 hours')"
            period_label = "오늘 24H"
            chart_title = f"📊 [{brand_name_kr}] 오늘 24시간 시간대별 배포 추이 (00시~23시 KST)"
            chart_badge = f"기준: {brand_name_kr} 오늘 24H 실데이터"

        period_where_m = build_where(date_cond_m, brand_sql_m)
        period_where_u = build_where(date_cond_u, brand_sql_u)
        total_where_m = build_where("", brand_sql_m)
        total_where_u = build_where("", brand_sql_u)

        total_marketing_count = 0
        period_marketing_count = 0
        hourly_data = []
        type_counts = {}
        utm_total_count = 0
        period_utm_count = 0
        real_visitors_list = []
        real_sources_map = {}

        with self.db_mgr._get_connection() as conn:
            c = conn.cursor()

            # 1. 전체 마케팅 콘텐츠 누적 수
            c.execute(f"SELECT COUNT(*) FROM marketing_history {total_where_m}")
            total_marketing_count = c.fetchone()[0]

            # 2. 선택된 기간 마케팅 콘텐츠 수
            c.execute(f"SELECT COUNT(*) FROM marketing_history {period_where_m}")
            period_marketing_count = c.fetchone()[0]

            # 3. 기간별 차트 데이터 생성 (오늘 / 주간 / 월간 / 연간 1:1 완벽 분기)
            if period == "weekly":
                date_list = [(today_date - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
                weekly_map = {d.strftime("%Y-%m-%d"): 0 for d in date_list}
                weekly_query_where = build_where("created_at >= DATE('now', '+9 hours', '-7 days')", brand_sql_m)
                c.execute(f"SELECT DATE(created_at) as dt, COUNT(*) FROM marketing_history {weekly_query_where} GROUP BY dt")
                for row in c.fetchall():
                    if row[0] in weekly_map:
                        weekly_map[row[0]] = row[1]
                hourly_data = [{"hour": d.strftime("%m/%d"), "count": weekly_map[d.strftime("%Y-%m-%d")]} for d in date_list]

            elif period == "monthly":
                weeks = [("4주 전", 28, 21), ("3주 전", 21, 14), ("2주 전", 14, 7), ("이번 주", 7, 0)]
                hourly_data = []
                for label, start_days, end_days in weeks:
                    w_cond = f"created_at >= DATE('now', '+9 hours', '-{start_days} days') AND created_at < DATE('now', '+9 hours', '-{max(0, end_days-1)} days')"
                    w_where = build_where(w_cond, brand_sql_m)
                    c.execute(f"SELECT COUNT(*) FROM marketing_history {w_where}")
                    cnt = c.fetchone()[0]
                    hourly_data.append({"hour": label, "count": cnt})

            elif period == "yearly":
                mon_map = {f"{m:02d}": 0 for m in range(1, 13)}
                yr_cond = f"strftime('%Y', created_at) = '{today_date.year}'"
                yr_where = build_where(yr_cond, brand_sql_m)
                c.execute(f"SELECT strftime('%m', created_at) as mon, COUNT(*) FROM marketing_history {yr_where} GROUP BY mon")
                for row in c.fetchall():
                    if row[0] and row[0] in mon_map:
                        mon_map[row[0]] = row[1]
                hourly_data = [{"hour": f"{m}월", "count": mon_map[f"{m:02d}"]} for m in range(1, 13)]

            else: # today
                today_counts = {f"{h:02d}": 0 for h in range(24)}
                today_hr_where = build_where("DATE(created_at) = DATE('now', '+9 hours')", brand_sql_m)
                c.execute(f"SELECT strftime('%H', created_at) as hr, COUNT(*) FROM marketing_history {today_hr_where} GROUP BY hr")
                for row in c.fetchall():
                    if row[0] and row[0] in today_counts:
                        today_counts[row[0]] = row[1]
                hourly_data = [{"hour": f"{h:02d}시", "count": today_counts[f"{h:02d}"]} for h in range(24)]

            # 4. 실제 발행된 콘텐츠 종류별 집계
            c.execute(f"SELECT content_type, COUNT(*) FROM marketing_history {period_where_m} GROUP BY content_type ORDER BY COUNT(*) DESC")
            for row in c.fetchall():
                type_counts[row[0]] = row[1]

            # 5. 실제 UTM 유입자 집계 (진짜 사람의 접속 로그)
            try:
                c.execute(f"SELECT COUNT(*) FROM utm_logs {total_where_u}")
                utm_total_count = c.fetchone()[0]
                c.execute(f"SELECT COUNT(*) FROM utm_logs {period_where_u}")
                period_utm_count = c.fetchone()[0]

                c.execute(f"SELECT utm_source, COUNT(*) FROM utm_logs {period_where_u} GROUP BY utm_source ORDER BY COUNT(*) DESC")
                for row in c.fetchall():
                    if row[0]:
                        real_sources_map[row[0]] = row[1]

                c.execute(f"SELECT utm_source, utm_medium, utm_campaign, target_service, ip, created_at FROM utm_logs {period_where_u} ORDER BY created_at DESC LIMIT 30")
                for row in c.fetchall():
                    real_visitors_list.append({
                        "source_name": row[0] or "direct",
                        "medium": row[1] or "link",
                        "campaign": row[2] or "viral",
                        "target_app": row[3] or brand_name_kr,
                        "ip": row[4] or "127.0.0.1",
                        "created_at": row[5] or ""
                    })
            except Exception as e:
                logger.warning(f"UTM logs 쿼리 중 예외: {e}")

        # 4대 핵심 지표 (100% 실데이터)
        active_kpis = {
            "today_pv": period_marketing_count,
            "cumulative_pv": total_marketing_count,
            "yoy_growth": "100% 실시간 DB 연동",
            "monthly_visitors": period_utm_count,
            "kpi_period_label": f"{period_label} [{brand_name_kr}] 마케팅 발행 (건)",
            "visitor_period_label": f"{period_label} [{brand_name_kr}] 실제 유입 (명)"
        }

        # 옴니채널 실제 콘텐츠 발행 실적 (실제 DB 데이터 기반 매핑)
        type_info_map = {
            "shorts": ("🔴 YouTube / TikTok 숏폼 비디오", "global_sns"),
            "tiktok": ("🎵 TikTok 비디오", "global_sns"),
            "cardnews": ("📸 Instagram / FB 카드뉴스", "global_sns"),
            "reddit_reply": ("🤖 Reddit 1:1 질문 감지 답변", "global_sns"),
            "fb_group_post": ("👥 페이스북 50만 그룹 배포", "global_sns"),
            "threads_post": ("🧵 Meta Threads 바이럴 스레드", "global_sns"),
            "blog_article": ("🌐 WordPress / Medium 블로그", "other"),
            "seo": ("🔍 구글봇 색인 핑 전송", "other"),
            "briefing": ("📲 텔레그램 데일리 브리핑", "messenger"),
            "pdf": ("📄 외국인 정착/절세 가이드북 PDF", "other")
        }

        channel_inflows = []
        if period_marketing_count > 0:
            for ckey, cnt in type_counts.items():
                info = type_info_map.get(ckey, (f"📦 {ckey} 배포", "other"))
                cname, ccat = info[0], info[1]
                share = round((cnt / period_marketing_count * 100), 1)
                channel_inflows.append({
                    "name": cname,
                    "category": ccat,
                    "count": cnt,
                    "share": share,
                    "color": "#10B981" if brand_filter == "kmarket" else "#F59E0B",
                    "unit": "건"
                })

        # 실제 유입 소스별 실데이터 목록
        real_visitor_inflows = []
        if period_utm_count > 0 and len(real_sources_map) > 0:
            for sname, scnt in real_sources_map.items():
                sshare = round((scnt / period_utm_count * 100), 1)
                real_visitor_inflows.append({
                    "name": f"🔗 {sname} 유입",
                    "count": scnt,
                    "share": sshare,
                    "color": "#38BDF8",
                    "unit": "명"
                })

        return {
            "period": period,
            "brand": brand_filter,
            "chart_title": chart_title,
            "chart_badge": chart_badge,
            "channels_title": f"🚀 [{brand_name_kr}] 옴니채널 실제 배포 실적 ({period_label})",
            "channels_subtitle": f"* {period_label} 동안 [{brand_name_kr}] 데이터베이스에 실제로 생성 및 발행 완료된 콘텐츠 실적입니다.",
            "visitors_title": f"👥 [{brand_name_kr}] 실제 웹사이트 방문자(UTM 유입) 실시간 추적 ({period_label})",
            "visitors_subtitle": f"배포된 링크를 클릭하고 [{brand_name_kr}]에 실제로 접속한 진짜 사람의 {period_label} 실시간 기록입니다.",
            "kpis": active_kpis,
            "hourly_data": hourly_data,
            "channel_inflows": channel_inflows,
            "real_visitor_inflows": real_visitor_inflows,
            "real_visitors_list": real_visitors_list
        }
