-- Storage RLS 정책 수정 - 파일 삭제 권한 추가
-- 기존 정책 삭제
DROP POLICY IF EXISTS "flowers_read_policy" ON storage.objects;
DROP POLICY IF EXISTS "flowers_write_policy" ON storage.objects;
DROP POLICY IF EXISTS "flowers_update_policy" ON storage.objects;

-- 새로운 정책 생성 (모든 작업 허용)
CREATE POLICY "flowers_full_access_policy" ON storage.objects
    FOR ALL USING (bucket_id = 'flowers')
    WITH CHECK (bucket_id = 'flowers');

-- 또는 더 구체적으로 각 작업별로 정책 생성
CREATE POLICY "flowers_select_policy" ON storage.objects
    FOR SELECT USING (bucket_id = 'flowers');

CREATE POLICY "flowers_insert_policy" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'flowers');

CREATE POLICY "flowers_update_policy" ON storage.objects
    FOR UPDATE USING (bucket_id = 'flowers')
    WITH CHECK (bucket_id = 'flowers');

CREATE POLICY "flowers_delete_policy" ON storage.objects
    FOR DELETE USING (bucket_id = 'flowers');

-- 정책 확인
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';

-- 버킷 정보 확인
SELECT * FROM storage.buckets WHERE id = 'flowers';
