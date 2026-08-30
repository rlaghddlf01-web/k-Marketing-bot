import sqlite3
import datetime
from typing import Optional, Dict, Any, List
from config import DB_PATH

class DBManager:
    """
    SQLite 기반 로컬 이력 관리 및 중복 방지 엔진
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 콘텐츠 발행 및 댓글 응답 이력 테이블 (한국 표준시 KST UTC+9 기준)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marketing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,       -- 'reddit_reply', 'shorts', 'cardnews', 'seo', 'briefing', 'pdf'
                    service_id TEXT NOT NULL,         -- 'kmarket', 'easytax', 'ktelecom', etc.
                    target_lang TEXT NOT NULL,        -- 'ko', 'en', 'vi', etc.
                    title TEXT,
                    content_text TEXT NOT NULL,
                    target_url TEXT,
                    external_id TEXT UNIQUE,          -- 레딧 submission_id, 소셜 post_id 등 (중복 방지 키)
                    score REAL DEFAULT 0.0,           -- 100점 만점 성과 점수
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT (datetime('now', '+9 hours')),
                    synced_supabase INTEGER DEFAULT 0 -- Supabase 동기화 여부 (0: 미동기화, 1: 완료)
                )
            """)

            # 2. Rate Limit & Anti-Ban 기록 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel TEXT NOT NULL,            -- 'reddit:korea', 'telegram:channel', etc.
                    action_type TEXT NOT NULL,        -- 'reply', 'post'
                    created_at TIMESTAMP DEFAULT (datetime('now', '+9 hours'))
                )
            """)

            # 3. UTM 유입 로그 테이블 (한국 표준시 KST UTC+9 기준)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    utm_source TEXT NOT NULL,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_content TEXT,
                    target_service TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    created_at TIMESTAMP DEFAULT (datetime('now', '+9 hours'))
                )
            """)

            # 기존 테이블 컬럼 마이그레이션 안전 보장
            try:
                cursor.execute("ALTER TABLE utm_logs ADD COLUMN ip TEXT")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE utm_logs ADD COLUMN user_agent TEXT")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE utm_logs ADD COLUMN referrer TEXT")
            except Exception:
                pass

            conn.commit()

    def is_already_processed(self, external_id: str) -> bool:
        """해당 외부 ID(예: 레딧 게시물 ID)가 이미 처리되었는지 확인"""
        if not external_id:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM marketing_history WHERE external_id = ?", (external_id,))
            return cursor.fetchone() is not None

    def record_history(self, content_type: str, service_id: str, target_lang: str,
                       content_text: str, title: str = "", target_url: str = "",
                       external_id: Optional[str] = None) -> int:
        """콘텐츠/댓글 발행 이력 저장"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO marketing_history 
                (content_type, service_id, target_lang, title, content_text, target_url, external_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (content_type, service_id, target_lang, title, content_text, target_url, external_id))
            conn.commit()
            return cursor.lastrowid

    def check_rate_limit(self, channel: str, max_per_hour: int, max_per_day: int) -> bool:
        """Rate limit 초과 여부 확인 (시간당/일일 상한선) -> 초과 시 False 반환"""
        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_ago = (now - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        one_day_ago = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1시간 내 활동 수
            cursor.execute("""
                SELECT COUNT(*) FROM rate_limits 
                WHERE channel = ? AND created_at >= ?
            """, (channel, one_hour_ago))
            hourly_count = cursor.fetchone()[0]
            if hourly_count >= max_per_hour:
                return False

            # 24시간 내 활동 수
            cursor.execute("""
                SELECT COUNT(*) FROM rate_limits 
                WHERE channel = ? AND created_at >= ?
            """, (channel, one_day_ago))
            daily_count = cursor.fetchone()[0]
            if daily_count >= max_per_day:
                return False

        return True

    def record_rate_limit_action(self, channel: str, action_type: str = "reply"):
        """Rate limit 동작 기록"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rate_limits (channel, action_type) VALUES (?, ?)", (channel, action_type))
            conn.commit()

    def can_post_to_channel(self, channel: str, *args, max_per_day: int = 10, **kwargs) -> bool:
        """일일 채널별 발행 한도(Rate Limit) 초과 여부 안전 검사"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM rate_limits 
                WHERE channel = ? AND created_at >= datetime('now', '-1 day')
            """, (str(channel),))
            count = cursor.fetchone()[0]
            limit = args[0] if args and isinstance(args[0], int) else max_per_day
            return count < limit

    def update_metrics(self, history_id: int, views: int = 0, clicks: int = 0, conversions: int = 0, score: float = 0.0):
        """성과 메트릭 및 스코어 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE marketing_history 
                SET views = views + ?, clicks = clicks + ?, conversions = conversions + ?, score = ?
                WHERE id = ?
            """, (views, clicks, conversions, score, history_id))
            conn.commit()

    def get_unsynced_histories(self) -> List[Dict[str, Any]]:
        """Supabase에 아직 동기화되지 않은 레코드 목록 조회"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM marketing_history WHERE synced_supabase = 0 LIMIT 50")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def mark_synced_supabase(self, history_ids: List[int]):
        """Supabase 동기화 완료 마킹"""
        if not history_ids:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in history_ids)
            cursor.execute(f"UPDATE marketing_history SET synced_supabase = 1 WHERE id IN ({placeholders})", history_ids)
            conn.commit()

    def get_top_performing_copies(self, service_id: str, lang: str, min_score: float = 75.0, limit: int = 3) -> List[str]:
        """로컬 DB에서 고득점 카피 상위 N개 추출"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content_text FROM marketing_history
                WHERE service_id = ? AND target_lang = ? AND score >= ?
                ORDER BY score DESC, clicks DESC LIMIT ?
            """, (service_id, lang, min_score, limit))
            rows = cursor.fetchall()
            return [r[0] for r in rows]

    def record_utm_log(self, utm_source: str, utm_medium: str = "", utm_campaign: str = "",
                       utm_content: str = "", target_service: str = "", ip: str = "",
                       user_agent: str = "", referrer: str = "") -> int:
        """실제 사람(외부 유입자)의 실시간 접속 로그 기록"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    utm_source TEXT NOT NULL,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_content TEXT,
                    target_service TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT INTO utm_logs (utm_source, utm_medium, utm_campaign, utm_content, target_service, ip, user_agent, referrer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (utm_source, utm_medium, utm_campaign, utm_content, target_service, ip, user_agent, referrer))
            conn.commit()
            return cursor.lastrowid

    def get_recent_utm_logs(self, limit: int = 20, service_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """최근 실제 유입된 방문자 로그 조회 (브랜드별 필터링 지원)"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                if service_id and service_id.lower() != "all":
                    cursor.execute("""
                        SELECT id, utm_source, utm_medium, utm_campaign, utm_content, target_service, ip, user_agent, referrer, created_at
                        FROM utm_logs
                        WHERE target_service = ?
                        ORDER BY id DESC LIMIT ?
                    """, (service_id.lower(), limit))
                else:
                    cursor.execute("""
                        SELECT id, utm_source, utm_medium, utm_campaign, utm_content, target_service, ip, user_agent, referrer, created_at
                        FROM utm_logs
                        ORDER BY id DESC LIMIT ?
                    """, (limit,))
                return [dict(r) for r in cursor.fetchall()]
            except Exception:
                return []
