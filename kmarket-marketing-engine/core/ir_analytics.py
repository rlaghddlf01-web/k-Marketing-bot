import json
import logging
import datetime
from typing import Dict, Any, List, Optional
from config import DATA_DIR, KST, get_now_kst
from core.db_manager import DBManager
from core.supabase_manager import SupabaseManager

logger = logging.getLogger("IRAnalytics")

class IRAnalyticsEngine:
    """
    📊 100% 순수 실데이터 기반 유입 및 IR 관제 엔진
    - 가짜/더미/가공 데이터 0%
    - Supabase / SQLite utm_logs 및 marketing_history 100% 실데이터 집계
    - 5단 기간별(시간별, 날짜별, 주간별, 월별, 년도별) 듀얼 막대그래프 분석
    - 이지텍스(EasyTax) & 케이마켓(K-Market) 듀얼 브랜드 및 10대 채널, 17개국 정밀 집계
    """
    def __init__(self, db_mgr: DBManager, supabase_mgr: Optional[SupabaseManager] = None):
        self.db_mgr = db_mgr
        self.supabase_mgr = supabase_mgr or SupabaseManager(db_mgr)

    def get_detailed_dashboard_data(self, period: str = "today", brand: str = "all") -> Dict[str, Any]:
        kst_now = get_now_kst()
        today_date = kst_now.date()
        today_start_kst = datetime.datetime(kst_now.year, kst_now.month, kst_now.day, tzinfo=KST)

        brand_filter = brand.lower() if brand else "all"
        brand_sql_m = ""
        brand_sql_u = ""
        if brand_filter == "kmarket":
            brand_sql_m = "service_id = 'kmarket'"
            brand_sql_u = "target_service = 'kmarket'"
            brand_name_kr = "K-Market"
            brand_icon = "🛒"
        elif brand_filter == "easytax":
            brand_sql_m = "service_id = 'easytax'"
            brand_sql_u = "target_service = 'easytax'"
            brand_name_kr = "EasyTax"
            brand_icon = "💰"
        else:
            brand_name_kr = "전체 듀얼 브랜드"
            brand_icon = "🌐"

        def build_where(date_cond: str, brand_cond: str) -> str:
            conds = [c for c in [date_cond, brand_cond] if c]
            return f"WHERE {' AND '.join(conds)}" if conds else ""

        # 1. 5대 기간별 SQL 조건절 및 메타데이터 정의
        if period == "daily":
            # 📅 날짜별: 최근 14일 일자별
            date_cond_m = "DATE(created_at) >= DATE('now', '+9 hours', '-13 days')"
            date_cond_u = "DATE(created_at) >= DATE('now', '+9 hours', '-13 days')"
            period_label = "최근 14일 일자별"
            period_start_kst = today_start_kst - datetime.timedelta(days=13)
            chart_title = f"📅 [{brand_name_kr}] 최근 14일 일자별 유입 및 배포 추이 (KST)"
            chart_badge = f"기준: {brand_name_kr} 최근 14일 실데이터"
        elif period == "weekly":
            # 📊 주간별: 최근 8주 주차별
            date_cond_m = "DATE(created_at) >= DATE('now', '+9 hours', '-55 days')"
            date_cond_u = "DATE(created_at) >= DATE('now', '+9 hours', '-55 days')"
            period_label = "최근 8주 주간별"
            period_start_kst = today_start_kst - datetime.timedelta(days=55)
            chart_title = f"📊 [{brand_name_kr}] 최근 8주 주차별 유입 및 배포 추이 (KST)"
            chart_badge = f"기준: {brand_name_kr} 최근 8주 실데이터"
        elif period == "monthly":
            # 📈 월별: 당해 1월~12월 월별
            date_cond_m = f"strftime('%Y', created_at) = '{today_date.year}'"
            date_cond_u = f"strftime('%Y', created_at) = '{today_date.year}'"
            period_label = f"{today_date.year}년 월별"
            period_start_kst = datetime.datetime(today_date.year, 1, 1, tzinfo=KST)
            chart_title = f"📈 [{brand_name_kr}] {today_date.year}년 연간 월별 유입 및 배포 추이 (1월~12월)"
            chart_badge = f"기준: {brand_name_kr} {today_date.year}년 월별 실데이터"
        elif period == "yearly":
            # 🏆 연도별: 2024~2027 연간 IR
            date_cond_m = "strftime('%Y', created_at) >= '2024'"
            date_cond_u = "strftime('%Y', created_at) >= '2024'"
            period_label = "2024~2027 연도별 (IR)"
            period_start_kst = datetime.datetime(2024, 1, 1, tzinfo=KST)
            chart_title = f"🏆 [{brand_name_kr}] 연도별 누적 성장 및 비교 추이 (Yearly IR)"
            chart_badge = f"기준: {brand_name_kr} 연도별 실데이터"
        else: # today (기본 시간별)
            period = "today"
            date_cond_m = "DATE(created_at) = DATE('now', '+9 hours')"
            date_cond_u = "DATE(created_at) = DATE('now', '+9 hours')"
            period_label = "오늘 24H 시간별"
            period_start_kst = today_start_kst
            chart_title = f"⏰ [{brand_name_kr}] 오늘 24시간 시간대별 유입 및 배포 추이 (00시~23시 KST)"
            chart_badge = f"기준: {brand_name_kr} 오늘 24H 실데이터"

        period_where_m = build_where(date_cond_m, brand_sql_m)
        period_where_u = build_where(date_cond_u, brand_sql_u)
        total_where_m = build_where("", brand_sql_m)
        total_where_u = build_where("", brand_sql_u)

        total_marketing_count = 0
        period_marketing_count = 0
        type_counts = {}
        marketing_chart_data = []

        # 2. 로컬 SQLite DB에서 마케팅 콘텐츠 배포 실적 집계
        with self.db_mgr._get_connection() as conn:
            c = conn.cursor()

            # 전체 마케팅 콘텐츠 누적 수
            c.execute(f"SELECT COUNT(*) FROM marketing_history {total_where_m}")
            total_marketing_count = c.fetchone()[0] or 0

            # 선택 기간 마케팅 콘텐츠 수
            c.execute(f"SELECT COUNT(*) FROM marketing_history {period_where_m}")
            period_marketing_count = c.fetchone()[0] or 0

            # 실제 발행된 콘텐츠 종류별 집계
            c.execute(f"SELECT content_type, COUNT(*) FROM marketing_history {period_where_m} GROUP BY content_type ORDER BY COUNT(*) DESC")
            for row in c.fetchall():
                type_counts[row[0]] = row[1]

            # 마케팅 콘텐츠 배포 차트 데이터 구축 (5개 기간 분기)
            if period == "daily":
                date_list = [(today_date - datetime.timedelta(days=i)) for i in range(13, -1, -1)]
                d_map = {d.strftime("%Y-%m-%d"): 0 for d in date_list}
                w_cond = build_where("created_at >= DATE('now', '+9 hours', '-13 days')", brand_sql_m)
                c.execute(f"SELECT DATE(created_at) as dt, COUNT(*) FROM marketing_history {w_cond} GROUP BY dt")
                for row in c.fetchall():
                    if row[0] in d_map:
                        d_map[row[0]] = row[1]
                marketing_chart_data = [{"hour": d.strftime("%m/%d"), "label": d.strftime("%m/%d"), "count": d_map[d.strftime("%Y-%m-%d")]} for d in date_list]

            elif period == "weekly":
                w_list = []
                for i in range(7, -1, -1):
                    w_end = today_date + datetime.timedelta(days=1) - datetime.timedelta(days=i*7)
                    w_start = w_end - datetime.timedelta(days=7)
                    w_cond = f"created_at >= '{w_start}' AND created_at < '{w_end}'"
                    w_where = build_where(w_cond, brand_sql_m)
                    c.execute(f"SELECT COUNT(*) FROM marketing_history {w_where}")
                    cnt = c.fetchone()[0] or 0
                    label = "이번 주" if i == 0 else f"{i}주 전"
                    marketing_chart_data.append({"hour": label, "label": label, "count": cnt})

            elif period == "monthly":
                mon_map = {f"{m:02d}": 0 for m in range(1, 13)}
                yr_cond = f"strftime('%Y', created_at) = '{today_date.year}'"
                yr_where = build_where(yr_cond, brand_sql_m)
                c.execute(f"SELECT strftime('%m', created_at) as mon, COUNT(*) FROM marketing_history {yr_where} GROUP BY mon")
                for row in c.fetchall():
                    if row[0] and row[0] in mon_map:
                        mon_map[row[0]] = row[1]
                marketing_chart_data = [{"hour": f"{m}월", "label": f"{m}월", "count": mon_map[f"{m:02d}"]} for m in range(1, 13)]

            elif period == "yearly":
                years = [2024, 2025, 2026, 2027]
                for y in years:
                    y_cond = f"strftime('%Y', created_at) = '{y}'"
                    y_where = build_where(y_cond, brand_sql_m)
                    c.execute(f"SELECT COUNT(*) FROM marketing_history {y_where}")
                    cnt = c.fetchone()[0] or 0
                    marketing_chart_data.append({"hour": f"{y}년", "label": f"{y}년", "count": cnt})

            else: # today
                today_counts = {f"{h:02d}": 0 for h in range(24)}
                today_hr_where = build_where("DATE(created_at) = DATE('now', '+9 hours')", brand_sql_m)
                c.execute(f"SELECT strftime('%H', created_at) as hr, COUNT(*) FROM marketing_history {today_hr_where} GROUP BY hr")
                for row in c.fetchall():
                    if row[0] and row[0] in today_counts:
                        today_counts[row[0]] = row[1]
                marketing_chart_data = [{"hour": f"{h:02d}시", "label": f"{h:02d}시", "count": today_counts[f"{h:02d}"]} for h in range(24)]

        # 3. 실시간 유입 트래픽 집계 (Supabase 1순위 실데이터 + 로컬 SQLite Fallback)
        utm_total_count = 0
        period_utm_count = 0
        km_visitors_count = 0
        tax_visitors_count = 0
        real_sources_map = {}
        real_countries_map = {}
        real_visitors_list = []
        raw_traffic_timestamps = []

        # 3-1. Supabase 실시간 클라우드 트래픽 조회
        km_visitors_list = []
        tax_visitors_list = []
        if self.supabase_mgr:
            try:
                sb_traffic = self.supabase_mgr.fetch_live_traffic_data(brand=brand_filter, period=period, limit=100)
                if sb_traffic:
                    utm_total_count = sb_traffic.get("total_count", 0)
                    period_utm_count = sb_traffic.get("period_count", 0)
                    km_visitors_count = sb_traffic.get("km_count", 0)
                    tax_visitors_count = sb_traffic.get("tax_count", 0)
                    real_sources_map = dict(sb_traffic.get("sources_map", {}))
                    real_countries_map = dict(sb_traffic.get("countries_map", {}))
                    real_visitors_list = list(sb_traffic.get("visitors_list", []))
                    km_visitors_list = list(sb_traffic.get("km_visitors_list", []))
                    tax_visitors_list = list(sb_traffic.get("tax_visitors_list", []))
                    raw_traffic_timestamps = list(sb_traffic.get("raw_timestamps", []))
            except Exception as e:
                logger.warning(f"Supabase 실시간 트래픽 조회 예외: {e}")

        # 3-2. 로컬 SQLite DB utm_logs 병합
        try:
            with self.db_mgr._get_connection() as conn:
                c = conn.cursor()
                c.execute(f"SELECT COUNT(*) FROM utm_logs {total_where_u}")
                local_tot = c.fetchone()[0] or 0
                c.execute(f"SELECT COUNT(*) FROM utm_logs {period_where_u}")
                local_per = c.fetchone()[0] or 0

                if local_tot > 0:
                    utm_total_count += local_tot
                    period_utm_count += local_per

                    c.execute(f"SELECT utm_source, COUNT(*) FROM utm_logs {period_where_u} GROUP BY utm_source ORDER BY COUNT(*) DESC")
                    for row in c.fetchall():
                        if row[0]:
                            s_name = row[0].capitalize()
                            real_sources_map[s_name] = real_sources_map.get(s_name, 0) + row[1]

                    c.execute(f"SELECT utm_source, utm_medium, utm_campaign, target_service, ip, created_at FROM utm_logs {period_where_u} ORDER BY created_at DESC LIMIT 30")
                    for row in c.fetchall():
                        target_srv = (row[3] or "kmarket").lower()
                        b_label = "K-Market" if target_srv == "kmarket" else "EasyTax"
                        b_icon = "🛒" if target_srv == "kmarket" else "💰"
                        if target_srv == "kmarket":
                            km_visitors_count += 1
                        else:
                            tax_visitors_count += 1

                        c_dt = None
                        if row[5]:
                            try:
                                c_dt = datetime.datetime.fromisoformat(str(row[5]))
                                if not c_dt.tzinfo:
                                    c_dt = c_dt.replace(tzinfo=KST)
                                raw_traffic_timestamps.append(c_dt)
                            except Exception:
                                pass

                        local_v_obj = {
                            "brand": target_srv,
                            "brand_label": b_label,
                            "brand_icon": b_icon,
                            "source_name": row[0] or "Direct",
                            "channel_icon": "🔗" if (row[0] or "").lower() == "direct" else "🌐",
                            "medium": row[1] or "link",
                            "campaign": row[2] or "로컬 실시간 테스트",
                            "country": "대한민국",
                            "lang_label": "한국어 🇰🇷",
                            "target_app": f"{b_label} (로컬 접수)",
                            "action_stage": "실시간 접속 감지됨",
                            "ip": row[4] or "127.0.0.1",
                            "created_at": str(row[5] or "")
                        }
                        real_visitors_list.append(local_v_obj)
                        if target_srv == "kmarket":
                            km_visitors_list.append(local_v_obj)
                        else:
                            tax_visitors_list.append(local_v_obj)
        except Exception as e:
            logger.warning(f"UTM logs 로컬 조회 중 예외: {e}")

        # 4. 실시간 유입자(Visitor) 기준 5단계 기간별 막대 차트 데이터 구축
        visitor_chart_data = []
        if period == "daily":
            date_list = [(today_date - datetime.timedelta(days=i)) for i in range(13, -1, -1)]
            v_dmap = {d.strftime("%Y-%m-%d"): 0 for d in date_list}
            for ts in raw_traffic_timestamps:
                if ts:
                    d_str = ts.strftime("%Y-%m-%d")
                    if d_str in v_dmap:
                        v_dmap[d_str] += 1
            visitor_chart_data = [{"hour": d.strftime("%m/%d"), "label": d.strftime("%m/%d"), "count": v_dmap[d.strftime("%Y-%m-%d")]} for d in date_list]

        elif period == "weekly":
            for i in range(7, -1, -1):
                w_end = today_start_kst + datetime.timedelta(days=1) - datetime.timedelta(days=i*7)
                w_start = w_end - datetime.timedelta(days=7)
                cnt = sum(1 for ts in raw_traffic_timestamps if ts and w_start <= ts < w_end)
                label = "이번 주" if i == 0 else f"{i}주 전"
                visitor_chart_data.append({"hour": label, "label": label, "count": cnt})

        elif period == "monthly":
            v_mon_map = {f"{m:02d}": 0 for m in range(1, 13)}
            for ts in raw_traffic_timestamps:
                if ts and ts.year == today_date.year:
                    m_str = f"{ts.month:02d}"
                    if m_str in v_mon_map:
                        v_mon_map[m_str] += 1
            visitor_chart_data = [{"hour": f"{m}월", "label": f"{m}월", "count": v_mon_map[f"{m:02d}"]} for m in range(1, 13)]

        elif period == "yearly":
            years = [2024, 2025, 2026, 2027]
            for y in years:
                cnt = sum(1 for ts in raw_traffic_timestamps if ts and ts.year == y)
                visitor_chart_data.append({"hour": f"{y}년", "label": f"{y}년", "count": cnt})

        else: # today (00시~23시)
            v_hr_map = {f"{h:02d}": 0 for h in range(24)}
            for ts in raw_traffic_timestamps:
                if ts and ts.date() == today_date:
                    h_str = f"{ts.hour:02d}"
                    if h_str in v_hr_map:
                        v_hr_map[h_str] += 1
            visitor_chart_data = [{"hour": f"{h:02d}시", "label": f"{h:02d}시", "count": v_hr_map[f"{h:02d}"]} for h in range(24)]

        # 5. 10대 채널별 상세 랭킹 및 비중 계산
        channel_icon_map = {
            "Instagram": ("📸", "#E1306C"),
            "Facebook": ("📘", "#1877F2"),
            "TikTok": ("🎵", "#00F2FE"),
            "Telegram": ("📲", "#0088CC"),
            "Reddit": ("🤖", "#FF4500"),
            "Google SEO": ("🌐", "#34A853"),
            "Threads": ("🧵", "#FFFFFF"),
            "YouTube": ("▶️", "#FF0000"),
            "Direct / 북마크": ("🔗", "#10B981")
        }

        channel_rankings = []
        if period_utm_count > 0 and len(real_sources_map) > 0:
            sorted_sources = sorted(real_sources_map.items(), key=lambda x: x[1], reverse=True)
            for sname, scnt in sorted_sources:
                icon, color = channel_icon_map.get(sname, ("🌐", "#38BDF8"))
                share = round((scnt / period_utm_count * 100), 1)
                channel_rankings.append({
                    "name": sname,
                    "icon": icon,
                    "count": scnt,
                    "share": share,
                    "color": color,
                    "unit": "명"
                })

        # 6. 17개국 국가별 유입 분포(Country Distribution) 계산
        country_flag_map = {
            "베트남": "🇻🇳", "몽골": "🇲🇳", "캄보디아": "🇰🇭", "우즈베키스탄": "🇺🇿",
            "인도네시아": "🇮🇩", "미얀마": "🇲🇲", "중국": "🇨🇳", "미국/글로벌": "🇺🇸",
            "러시아": "🇷🇺", "일본": "🇯🇵", "태국": "🇹🇭", "네팔": "🇳🇵",
            "스리랑카": "🇱🇰", "카자흐스탄": "🇰🇿", "방글라데시": "🇧🇩", "파키스탄": "🇵🇰",
            "대한민국": "🇰🇷", "글로벌": "🌐"
        }

        country_distribution = []
        if period_utm_count > 0 and len(real_countries_map) > 0:
            sorted_countries = sorted(real_countries_map.items(), key=lambda x: x[1], reverse=True)
            for cname, ccnt in sorted_countries:
                flag = country_flag_map.get(cname, "🌐")
                cshare = round((ccnt / period_utm_count * 100), 1)
                country_distribution.append({
                    "country": cname,
                    "flag": flag,
                    "count": ccnt,
                    "share": cshare,
                    "unit": "명"
                })

        # 7. 옴니채널 콘텐츠 제작/발행 실적 매핑
        type_info_map = {
            "blog_article": ("🌐 17개국어 자율 SEO 블로그 발행", "seo_blog", "#38BDF8"),
            "shorts": ("🎬 실물 숏폼 영상 렌더링 (MP4)", "global_sns", "#F43F5E"),
            "tiktok": ("🎵 틱톡 숏폼 영상 렌더링 (MP4)", "global_sns", "#00F2FE"),
            "cardnews": ("📸 실물 4장 카드뉴스 생성 (PNG)", "global_sns", "#8B5CF6"),
            "fb_group_post": ("👥 페이스북 그룹 스텔스 콘텐츠 조립", "community", "#1877F2"),
            "threads_post": ("🧵 Meta Threads 타래 스레드 생성", "community", "#E2E8F0"),
            "reddit_reply": ("🤖 Reddit 타깃 질문 감지 및 답변 조립", "community", "#FF4500"),
            "seo": ("🔍 구글봇 색인 핑 전송 (Googlebot)", "seo_blog", "#10B981"),
            "briefing": ("📲 텔레그램 데일리 브리핑 파일 생성", "messenger", "#0088CC"),
            "pdf": ("📄 외국인 가이드북 PDF 생성", "other", "#F59E0B")
        }

        channel_inflows = []
        if period_marketing_count > 0:
            for ckey, cnt in type_counts.items():
                info = type_info_map.get(ckey, (f"📦 {ckey} 배포", "other", "#94A3B8"))
                cname, ccat, ccol = info[0], info[1], info[2]
                share = round((cnt / period_marketing_count * 100), 1)
                channel_inflows.append({
                    "name": cname,
                    "category": ccat,
                    "count": cnt,
                    "share": share,
                    "color": ccol,
                    "unit": "건"
                })

        # 8. 6대 종합 KPI 카드
        top_c_str = f"{channel_rankings[0]['icon']} {channel_rankings[0]['name']} ({channel_rankings[0]['share']}%)" if channel_rankings else "실시간 집계 중"
        top_k_str = f"{country_distribution[0]['flag']} {country_distribution[0]['country']} ({country_distribution[0]['share']}%)" if country_distribution else "17개국 분산"

        active_kpis = {
            "today_pv": period_marketing_count,
            "cumulative_pv": total_marketing_count,
            "yoy_growth": "100% 슈퍼베이스 실시간 연동",
            "period_visitors": period_utm_count,
            "total_visitors": utm_total_count,
            "km_visitors": km_visitors_count,
            "tax_visitors": tax_visitors_count,
            "top_channel": top_c_str,
            "top_country": top_k_str,
            "kpi_period_label": f"{period_label} [{brand_name_kr}] 콘텐츠 배포 (건)",
            "visitor_period_label": f"{period_label} [{brand_name_kr}] 실제 유입자 (명)"
        }

        return {
            "period": period,
            "brand": brand_filter,
            "brand_name_kr": brand_name_kr,
            "brand_icon": brand_icon,
            "period_label": period_label,
            "chart_title": chart_title,
            "chart_badge": chart_badge,
            "channels_title": f"🚀 [{brand_name_kr}] 옴니채널 실제 배포 실적 ({period_label})",
            "channels_subtitle": f"* {period_label} 동안 [{brand_name_kr}] 데이터베이스에 실제로 생성 및 발행 완료된 콘텐츠 실적입니다.",
            "visitors_title": f"👥 [{brand_name_kr}] 실제 웹사이트 방문자(UTM 유입) 실시간 추적 ({period_label})",
            "visitors_subtitle": f"배포된 링크를 클릭하고 [{brand_name_kr}]에 실제로 접속한 진짜 사람의 {period_label} 실시간 기록입니다.",
            "kpis": active_kpis,
            "hourly_data": visitor_chart_data, # 기본 차트: 실제 유입자 수
            "visitor_chart_data": visitor_chart_data,
            "marketing_chart_data": marketing_chart_data,
            "channel_rankings": channel_rankings,
            "country_distribution": country_distribution,
            "channel_inflows": channel_inflows,
            "real_visitors_list": real_visitors_list,
            "km_visitors_list": km_visitors_list,
            "tax_visitors_list": tax_visitors_list
        }

