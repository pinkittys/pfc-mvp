-- Supabase 테이블 스키마 정의
-- 꽃 카탈로그, 스토리 로그, 이미지 데이터를 위한 테이블들

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
    image_data TEXT, -- Base64 인코딩된 이미지 데이터
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(flower_id, color)
);

-- 4. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_flower_catalog_flower_id ON flower_catalog(flower_id);
CREATE INDEX IF NOT EXISTS idx_flower_catalog_name_ko ON flower_catalog(name_ko);
CREATE INDEX IF NOT EXISTS idx_flower_catalog_name_en ON flower_catalog(name_en);
CREATE INDEX IF NOT EXISTS idx_stories_story_id ON stories(story_id);
CREATE INDEX IF NOT EXISTS idx_stories_created_at ON stories(created_at);
CREATE INDEX IF NOT EXISTS idx_flower_images_flower_id ON flower_images(flower_id);
CREATE INDEX IF NOT EXISTS idx_flower_images_color ON flower_images(color);

-- 5. RLS (Row Level Security) 설정
ALTER TABLE flower_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE flower_images ENABLE ROW LEVEL SECURITY;

-- 6. 정책 설정 (모든 사용자가 읽기 가능, 인증된 사용자만 쓰기 가능)
-- 꽃 카탈로그 정책
CREATE POLICY "flower_catalog_read_policy" ON flower_catalog
    FOR SELECT USING (true);

CREATE POLICY "flower_catalog_write_policy" ON flower_catalog
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "flower_catalog_update_policy" ON flower_catalog
    FOR UPDATE USING (auth.role() = 'authenticated');

-- 스토리 정책
CREATE POLICY "stories_read_policy" ON stories
    FOR SELECT USING (true);

CREATE POLICY "stories_write_policy" ON stories
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "stories_update_policy" ON stories
    FOR UPDATE USING (auth.role() = 'authenticated');

-- 이미지 정책
CREATE POLICY "flower_images_read_policy" ON flower_images
    FOR SELECT USING (true);

CREATE POLICY "flower_images_write_policy" ON flower_images
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "flower_images_update_policy" ON flower_images
    FOR UPDATE USING (auth.role() = 'authenticated');

-- 7. 함수 생성 (업데이트 시간 자동 설정)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. 트리거 생성
CREATE TRIGGER update_flower_catalog_updated_at 
    BEFORE UPDATE ON flower_catalog 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. 뷰 생성 (자주 사용되는 조인 쿼리)
CREATE OR REPLACE VIEW flower_catalog_with_images AS
SELECT 
    fc.*,
    fi.image_data,
    fi.image_url
FROM flower_catalog fc
LEFT JOIN flower_images fi ON fc.flower_id = fi.flower_id;

-- 10. 통계 뷰 생성
CREATE OR REPLACE VIEW flower_recommendation_stats AS
SELECT 
    fc.flower_id,
    fc.name_ko,
    fc.name_en,
    COUNT(s.id) as recommendation_count,
    AVG(EXTRACT(EPOCH FROM (NOW() - s.created_at))/86400) as avg_days_since_recommendation
FROM flower_catalog fc
LEFT JOIN stories s ON s.matched_flower->>'flower_name' = fc.name_ko 
    OR s.matched_flower->>'flower_name' = fc.name_en
GROUP BY fc.id, fc.flower_id, fc.name_ko, fc.name_en
ORDER BY recommendation_count DESC;
