-- Supabase Storage 설정
-- Supabase SQL Editor에서 실행

-- 1. flowers 버킷 생성
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('flowers', 'flowers', true, 5242880, ARRAY['image/jpeg', 'image/png', 'image/webp'])
ON CONFLICT (id) DO NOTHING;

-- 2. Storage 정책 설정 (모든 사용자가 읽기 가능)
CREATE POLICY "flowers_read_policy" ON storage.objects
    FOR SELECT USING (bucket_id = 'flowers');

-- 3. Storage 정책 설정 (모든 사용자가 쓰기 가능 - 테스트용)
CREATE POLICY "flowers_write_policy" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'flowers');

-- 4. Storage 정책 설정 (모든 사용자가 업데이트 가능 - 테스트용)
CREATE POLICY "flowers_update_policy" ON storage.objects
    FOR UPDATE USING (bucket_id = 'flowers');

-- 5. 확인
SELECT * FROM storage.buckets WHERE id = 'flowers';
