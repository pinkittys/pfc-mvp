-- stories 테이블 RLS 정책 설정
-- Supabase SQL Editor에서 실행

-- 1. 기존 정책 삭제 (있다면)
DROP POLICY IF EXISTS "stories_read_policy" ON stories;
DROP POLICY IF EXISTS "stories_write_policy" ON stories;
DROP POLICY IF EXISTS "stories_update_policy" ON stories;

-- 2. 모든 사용자가 읽기 가능하도록 설정
CREATE POLICY "stories_read_policy" ON stories
    FOR SELECT USING (true);

-- 3. 모든 사용자가 쓰기 가능하도록 설정 (테스트용)
CREATE POLICY "stories_write_policy" ON stories
    FOR INSERT WITH CHECK (true);

-- 4. 모든 사용자가 업데이트 가능하도록 설정 (테스트용)
CREATE POLICY "stories_update_policy" ON stories
    FOR UPDATE USING (true);

-- 5. 정책 확인
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'stories';
