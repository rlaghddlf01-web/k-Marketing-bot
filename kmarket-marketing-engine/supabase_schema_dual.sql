-- ======================================================================
-- 🛸 Universal Expat Growth Engine - Supabase 2대 전용 테이블 스키마
-- ======================================================================

-- 1. 🛒 K-Market 전용 자가학습 & 골든 카피 테이블
CREATE TABLE IF NOT EXISTS kmarket_golden_copies (
    id BIGSERIAL PRIMARY KEY,
    content_type TEXT NOT NULL,       -- 'reddit_reply', 'shorts', 'cardnews', 'briefing'
    service_id TEXT DEFAULT 'kmarket',
    target_lang TEXT NOT NULL,        -- 'en', 'vi', 'zh', 'ko', 'uz', etc.
    title TEXT,
    content_text TEXT NOT NULL,
    target_url TEXT,
    external_id TEXT UNIQUE,          -- 레딧 submission_id, 소셜 ID (중복 방지)
    score REAL DEFAULT 0.0,           -- 100점 만점 스코어
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 인덱스 생성 (고속 Few-Shot 조회용)
CREATE INDEX IF NOT EXISTS idx_kmarket_score_lang 
ON kmarket_golden_copies (target_lang, score DESC);


-- 2. 💰 EasyTax (KTRS) 전용 자가학습 & 골든 카피 테이블
CREATE TABLE IF NOT EXISTS easytax_golden_copies (
    id BIGSERIAL PRIMARY KEY,
    content_type TEXT NOT NULL,       -- 'reddit_reply', 'shorts', 'cardnews', 'briefing'
    service_id TEXT DEFAULT 'easytax',
    target_lang TEXT NOT NULL,        -- 'en', 'vi', 'zh', 'ko', etc.
    title TEXT,
    content_text TEXT NOT NULL,
    target_url TEXT,
    external_id TEXT UNIQUE,          -- 레딧 submission_id, 소셜 ID (중복 방지)
    score REAL DEFAULT 0.0,           -- 100점 만점 스코어
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 인덱스 생성 (고속 Few-Shot 조회용)
CREATE INDEX IF NOT EXISTS idx_easytax_score_lang 
ON easytax_golden_copies (target_lang, score DESC);
