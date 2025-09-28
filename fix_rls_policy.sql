-- RLS 정책 수정: INSERT 권한 추가
-- 모든 사용자가 INSERT 가능하도록 정책 설정
CREATE POLICY "Allow public insert access" ON recommendation_snapshots
  FOR INSERT WITH CHECK (true);

-- 기존 정책 확인
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'recommendation_snapshots';
