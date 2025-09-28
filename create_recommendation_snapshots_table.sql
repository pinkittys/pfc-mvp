-- 추천 결과 스냅샷 테이블 생성
CREATE TABLE IF NOT EXISTS recommendation_snapshots (
  id VARCHAR(20) PRIMARY KEY,                    -- S250927-ZIN-00001
  story TEXT NOT NULL,                           -- 사용자 스토리
  selected_keywords JSONB NOT NULL,              -- 최종 선택된 키워드
  excluded_keywords JSONB NOT NULL,              -- 제외된 키워드
  
  -- 추천 결과
  flower_name VARCHAR(50),                       -- 꽃 이름 (영문)
  korean_name VARCHAR(50),                       -- 꽃 이름 (한글)
  scientific_name VARCHAR(100),                   -- 학명
  image_url TEXT,                                -- 꽃 이미지 URL
  calligraphy_image_url TEXT,                    -- 캘리그래피 이미지 URL
  hashtags JSONB,                                -- 해시태그 배열
  english_description TEXT,                      -- 영어 설명
  emotions JSONB,                                -- 감정 분석 결과
  season_detail JSONB,                           -- 계절 정보
  composition JSONB,                             -- 꽃다발 구성
  recommendation_reason TEXT,                    -- 추천 이유
  
  -- 메타데이터
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_recommendation_snapshots_created_at ON recommendation_snapshots(created_at);
CREATE INDEX IF NOT EXISTS idx_recommendation_snapshots_flower_name ON recommendation_snapshots(flower_name);

-- RLS 정책 설정
ALTER TABLE recommendation_snapshots ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 정책 설정
CREATE POLICY "Allow public read access" ON recommendation_snapshots
  FOR SELECT USING (true);

-- 업데이트 시간 자동 갱신을 위한 트리거
CREATE OR REPLACE FUNCTION update_recommendation_snapshots_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_recommendation_snapshots_updated_at 
  BEFORE UPDATE ON recommendation_snapshots 
  FOR EACH ROW EXECUTE FUNCTION update_recommendation_snapshots_updated_at();
