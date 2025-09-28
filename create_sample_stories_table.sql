-- 샘플 스토리 테이블 생성
CREATE TABLE IF NOT EXISTS sample_stories (
  id VARCHAR(10) PRIMARY KEY,           -- S01, S02, S03, ...
  title TEXT NOT NULL,                  -- "아빠 정년퇴직", "언니 박사학위", ...
  story TEXT NOT NULL,                  -- 전체 스토리 내용
  category VARCHAR(50) NOT NULL,        -- "기념일·축하", "사랑·고백·감사", "위로·응원·격려"
  emotions JSONB NOT NULL,              -- ["감사", "존경", "자랑스러움"]
  situations JSONB NOT NULL,             -- ["정년퇴직", "축하", "성취", "용기"]
  moods JSONB NOT NULL,                 -- ["고급스러운", "존경하는", "품격있는", "용기있는"]
  colors JSONB NOT NULL,                 -- ["빨강", "레드"]
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_sample_stories_category ON sample_stories(category);
CREATE INDEX IF NOT EXISTS idx_sample_stories_created_at ON sample_stories(created_at);

-- RLS (Row Level Security) 설정 (공개 읽기 허용)
ALTER TABLE sample_stories ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 정책 설정
CREATE POLICY "Allow public read access" ON sample_stories
  FOR SELECT USING (true);

-- 업데이트 시간 자동 갱신을 위한 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sample_stories_updated_at 
  BEFORE UPDATE ON sample_stories 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
