-- ======================================================================
-- 🛸 Universal Expat Growth Engine - 17개국어 서브경로 블로그 Supabase 테이블
-- ======================================================================

-- 1. 🛒 K-Market 전용 17개국어 블로그 테이블
CREATE TABLE IF NOT EXISTS kmarket_blogs (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    target_lang TEXT NOT NULL DEFAULT 'en',
    title TEXT NOT NULL,
    excerpt TEXT,
    content_html TEXT NOT NULL,
    content_md TEXT,
    thumbnail_url TEXT,
    category TEXT DEFAULT 'campus_tips',
    author TEXT DEFAULT 'K-Market Expat Editor',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_kmarket_blog_slug_lang UNIQUE (slug, target_lang)
);

CREATE INDEX IF NOT EXISTS idx_kmarket_blogs_lang_slug ON kmarket_blogs(target_lang, slug);
CREATE INDEX IF NOT EXISTS idx_kmarket_blogs_published ON kmarket_blogs(target_lang, published_at DESC);

ALTER TABLE kmarket_blogs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "kmarket_blogs_read_policy" ON kmarket_blogs FOR SELECT USING (true);
CREATE POLICY "kmarket_blogs_insert_policy" ON kmarket_blogs FOR INSERT WITH CHECK (true);
CREATE POLICY "kmarket_blogs_update_policy" ON kmarket_blogs FOR UPDATE USING (true);


-- 2. 💰 EasyTax (KTRS) 전용 17개국어 세무·환급 블로그 테이블
CREATE TABLE IF NOT EXISTS easytax_blogs (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    target_lang TEXT NOT NULL DEFAULT 'en',
    title TEXT NOT NULL,
    excerpt TEXT,
    content_html TEXT NOT NULL,
    content_md TEXT,
    thumbnail_url TEXT,
    category TEXT DEFAULT 'tax_reduction',
    author TEXT DEFAULT 'EasyTax Certified Tax Team',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_easytax_blog_slug_lang UNIQUE (slug, target_lang)
);

CREATE INDEX IF NOT EXISTS idx_easytax_blogs_lang_slug ON easytax_blogs(target_lang, slug);
CREATE INDEX IF NOT EXISTS idx_easytax_blogs_published ON easytax_blogs(target_lang, published_at DESC);

ALTER TABLE easytax_blogs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "easytax_blogs_read_policy" ON easytax_blogs FOR SELECT USING (true);
CREATE POLICY "easytax_blogs_insert_policy" ON easytax_blogs FOR INSERT WITH CHECK (true);
CREATE POLICY "easytax_blogs_update_policy" ON easytax_blogs FOR UPDATE USING (true);
