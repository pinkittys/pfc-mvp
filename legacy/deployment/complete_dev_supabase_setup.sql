-- 개발용 Supabase 완전 설정

-- 4. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_flower_catalog_flower_id ON flower_catalog(flower_id);
CREATE INDEX IF NOT EXISTS idx_flower_catalog_name_ko ON flower_catalog(name_ko);
CREATE INDEX IF NOT EXISTS idx_flower_catalog_name_en ON flower_catalog(name_en);
CREATE INDEX IF NOT EXISTS idx_stories_story_id ON stories(story_id);
CREATE INDEX IF NOT EXISTS idx_stories_created_at ON stories(created_at);
CREATE INDEX IF NOT EXISTS idx_flower_images_flower_id ON flower_images(flower_id);
CREATE INDEX IF NOT EXISTS idx_flower_images_color ON flower_images(color);

-- 7. 함수 생성 (업데이트 시간 자동 설정)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. 트리거 생성
DROP TRIGGER IF EXISTS update_flower_catalog_updated_at ON flower_catalog;
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
