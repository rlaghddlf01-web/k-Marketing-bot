-- ======================================================================
-- 👑 Universal Growth Engine - Supabase 완전 분리 전용 DB 스키마 (최신 통합본)
-- ======================================================================

-- 1. 🛒 K-Market 전용 자가학습 & 골든 카피 테이블
CREATE TABLE IF NOT EXISTS kmarket_golden_copies (
    id BIGSERIAL PRIMARY KEY,
    content_type TEXT NOT NULL,       -- 'shorts', 'cardnews', 'reddit_reply', 'threads', 'blog'
    service_id TEXT DEFAULT 'kmarket',
    target_lang TEXT NOT NULL,        -- 'en', 'vi', 'zh', 'ko', 'uz', 'mn', etc.
    title TEXT,
    content_text TEXT NOT NULL,
    target_url TEXT,
    external_id TEXT UNIQUE,          -- 중복 방지 고유 ID
    score REAL DEFAULT 0.0,           -- 100점 만점 AI 평가 점수
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_kmarket_score_lang 
ON kmarket_golden_copies (target_lang, score DESC);


-- 2. 💰 EasyTax (KTRS) 전용 자가학습 & 골든 카피 테이블
CREATE TABLE IF NOT EXISTS easytax_golden_copies (
    id BIGSERIAL PRIMARY KEY,
    content_type TEXT NOT NULL,       -- 'shorts', 'cardnews', 'reddit_reply', 'threads', 'blog'
    service_id TEXT DEFAULT 'easytax',
    target_lang TEXT NOT NULL,        -- 'en', 'vi', 'zh', 'ko', 'uz', 'ru', etc.
    title TEXT,
    content_text TEXT NOT NULL,
    target_url TEXT,
    external_id TEXT UNIQUE,          -- 중복 방지 고유 ID
    score REAL DEFAULT 0.0,           -- 100점 만점 AI 평가 점수
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_easytax_score_lang 
ON easytax_golden_copies (target_lang, score DESC);


-- 3. 🎬 통합 미디어 자산 아카이브 테이블 (숏폼/카드뉴스 파일 및 품질 점수)
CREATE TABLE IF NOT EXISTS marketing_media_assets (
    id BIGSERIAL PRIMARY KEY,
    service_id TEXT NOT NULL,         -- 'kmarket' or 'easytax'
    target_lang TEXT NOT NULL,
    media_type TEXT NOT NULL,         -- 'short_video', 'cardnews_image', 'thumbnail'
    theme_id TEXT,
    age_group TEXT,
    gender TEXT,
    prompt_used TEXT,
    file_path TEXT,
    quality_score REAL DEFAULT 0.0,
    verification_passed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_media_service_lang 
ON marketing_media_assets (service_id, target_lang, created_at DESC);


-- 4. 📊 마케팅 실시간 전환 & UTM 트래픽 로그 테이블
CREATE TABLE IF NOT EXISTS marketing_utm_logs (
    id BIGSERIAL PRIMARY KEY,
    service_id TEXT NOT NULL,         -- 'kmarket', 'easytax', 'insurance'
    platform TEXT,                    -- 'youtube', 'tiktok', 'instagram', 'reddit', 'threads', 'naver'
    channel_type TEXT,                -- 'shorts', 'cardnews', 'blog', 'community'
    target_lang TEXT,
    campaign_id TEXT,
    source_ip TEXT,
    user_agent TEXT,
    conversion_event TEXT,            -- 'view', 'click_cta', 'form_submit', 'download'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_utm_service_platform 
ON marketing_utm_logs (service_id, platform, created_at DESC);
