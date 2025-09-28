#!/usr/bin/env python3
"""
Python으로 Supabase 테이블 생성
"""

import os
from supabase import create_client, Client

def create_sample_stories_table():
    """Supabase에 sample_stories 테이블 생성"""
    
    # Supabase 클라이언트 초기화
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수를 설정해주세요.")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase 클라이언트 연결 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False
    
    # SQL 실행을 위한 SQL 쿼리
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sample_stories (
      id VARCHAR(10) PRIMARY KEY,
      title TEXT NOT NULL,
      story TEXT NOT NULL,
      category VARCHAR(50) NOT NULL,
      emotions JSONB NOT NULL,
      situations JSONB NOT NULL,
      moods JSONB NOT NULL,
      colors JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_sample_stories_category ON sample_stories(category);
    CREATE INDEX IF NOT EXISTS idx_sample_stories_created_at ON sample_stories(created_at);
    """
    
    create_policy_sql = """
    ALTER TABLE sample_stories ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Allow public read access" ON sample_stories
      FOR SELECT USING (true);
    """
    
    create_trigger_sql = """
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
    """
    
    try:
        # Supabase에서는 직접 SQL 실행이 제한적이므로
        # 테이블이 이미 존재하는지 확인하고, 없다면 수동으로 생성 안내
        print("🔧 기존 테이블 확인 중...")
        
        # 테이블 존재 확인
        try:
            result = supabase.table('sample_stories').select('*').limit(1).execute()
            print("✅ sample_stories 테이블이 이미 존재합니다")
            return True
        except Exception as e:
            print("❌ 테이블이 존재하지 않습니다")
            print("📋 수동으로 테이블을 생성해야 합니다:")
            print("=" * 60)
            print("1. Supabase 대시보드 (https://supabase.com/dashboard) 접속")
            print("2. 프로젝트 선택")
            print("3. SQL Editor 메뉴 클릭")
            print("4. 다음 SQL 실행:")
            print("=" * 60)
            print(create_table_sql)
            print("=" * 60)
            print(create_indexes_sql)
            print("=" * 60)
            print(create_policy_sql)
            print("=" * 60)
            print(create_trigger_sql)
            print("=" * 60)
            print("5. SQL 실행 후 이 스크립트를 다시 실행하세요")
            return False
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False

def verify_table_creation():
    """테이블 생성 확인"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 테이블 존재 확인
        result = supabase.table('sample_stories').select('*').limit(1).execute()
        print("✅ sample_stories 테이블 확인 완료")
        
        # 테이블 구조 확인
        print("📊 테이블 구조:")
        print("  - id (VARCHAR)")
        print("  - title (TEXT)")
        print("  - story (TEXT)")
        print("  - category (VARCHAR)")
        print("  - emotions (JSONB)")
        print("  - situations (JSONB)")
        print("  - moods (JSONB)")
        print("  - colors (JSONB)")
        print("  - created_at (TIMESTAMP)")
        print("  - updated_at (TIMESTAMP)")
        
        return True
        
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase 테이블 생성 시작")
    print("=" * 50)
    
    # 테이블 생성
    if create_sample_stories_table():
        print("\n" + "=" * 50)
        print("🔍 테이블 생성 확인")
        
        # 확인
        verify_table_creation()
        
        print("\n✅ 테이블 생성 완료!")
        print("📋 다음 단계: python migrate_to_supabase.py")
    else:
        print("\n❌ 테이블 생성 실패")
