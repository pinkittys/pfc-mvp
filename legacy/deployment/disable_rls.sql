-- 모든 테이블의 RLS 비활성화 (테스트용)
-- Supabase SQL Editor에서 실행

-- flower_catalog 테이블 RLS 비활성화
ALTER TABLE flower_catalog DISABLE ROW LEVEL SECURITY;

-- stories 테이블 RLS 비활성화
ALTER TABLE stories DISABLE ROW LEVEL SECURITY;

-- flower_images 테이블 RLS 비활성화
ALTER TABLE flower_images DISABLE ROW LEVEL SECURITY;

-- 확인
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('flower_catalog', 'stories', 'flower_images');
