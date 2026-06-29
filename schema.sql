-- Supabase Table Initialization SQL
-- Execute this script in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    fact_text TEXT NOT NULL UNIQUE,
    caption TEXT,
    category TEXT,
    instagram_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for checking duplicate facts quickly
CREATE INDEX IF NOT EXISTS idx_posts_fact_text ON posts (fact_text);
-- Index for ordering history
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts (created_at DESC);
