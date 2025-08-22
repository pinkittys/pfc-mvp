-- 개발용 Supabase 기본 테이블 생성

-- 1. 꽃 카탈로그 테이블
CREATE TABLE IF NOT EXISTS flower_catalog (
    id BIGSERIAL PRIMARY KEY,
    flower_id VARCHAR(100) UNIQUE NOT NULL,
    flower_slug VARCHAR(100),
    color_code VARCHAR(10),
    name_ko VARCHAR(100),
    name_en VARCHAR(100),
    scientific_name VARCHAR(100),
    is_main BOOLEAN DEFAULT false,
    base_color VARCHAR(50),
    alt_colors TEXT,
    moods TEXT,
    emotions TEXT,
    contexts TEXT,
    season_months VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 스토리 추천 로그 테이블
CREATE TABLE IF NOT EXISTS stories (
    id BIGSERIAL PRIMARY KEY,
    story_id VARCHAR(50) UNIQUE NOT NULL,
    story TEXT NOT NULL,
    emotions JSONB,
    matched_flower JSONB,
    composition JSONB,
    recommendation_reason TEXT,
    flower_card_message TEXT,
    season_info VARCHAR(100),
    keywords JSONB,
    hashtags JSONB,
    color_keywords JSONB,
    excluded_keywords JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 꽃 이미지 테이블
CREATE TABLE IF NOT EXISTS flower_images (
    id BIGSERIAL PRIMARY KEY,
    flower_id VARCHAR(100) NOT NULL,
    color VARCHAR(50) NOT NULL,
    image_data TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(flower_id, color)
);

-- 4. RLS 비활성화 (개발용)
ALTER TABLE flower_catalog DISABLE ROW LEVEL SECURITY;
ALTER TABLE stories DISABLE ROW LEVEL SECURITY;
ALTER TABLE flower_images DISABLE ROW LEVEL SECURITY;
