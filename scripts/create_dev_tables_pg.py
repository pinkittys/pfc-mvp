#!/usr/bin/env python3
"""
PostgreSQL 연결로 개발용 Supabase 테이블 생성
"""
import os
import psycopg2
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dev_tables():
    """PostgreSQL 연결로 개발용 Supabase에 테이블 생성"""
    
    # 개발용 Supabase PostgreSQL 연결 정보
    # Supabase 대시보드 → Settings → Database → Connection string에서 확인
    DATABASE_URL = "postgresql://postgres.gwpqvveinnzyaeathpdj:[YOUR-PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
    
    # 또는 개별 정보로 연결
    DB_HOST = "aws-0-ap-northeast-1.pooler.supabase.com"
    DB_PORT = "6543"
    DB_NAME = "postgres"
    DB_USER = "postgres.gwpqvveinnzyaeathpdj"
    DB_PASSWORD = "your-password-here"  # 실제 비밀번호 필요
    
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # 테이블 생성 SQL
        create_tables_sql = """
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
            image_data TEXT,
            image_url VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(flower_id, color)
        );

        -- 4. RLS 비활성화 (개발용)
        ALTER TABLE flower_catalog DISABLE ROW LEVEL SECURITY;
        ALTER TABLE stories DISABLE ROW LEVEL SECURITY;
        ALTER TABLE flower_images DISABLE ROW LEVEL SECURITY;
        """
        
        # SQL 실행
        cursor.execute(create_tables_sql)
        conn.commit()
        
        logger.info("✅ 개발용 Supabase 테이블 생성 성공!")
        
        # 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('flower_catalog', 'stories', 'flower_images')
        """)
        
        tables = cursor.fetchall()
        logger.info(f"생성된 테이블: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 테이블 생성 오류: {e}")
        return False

if __name__ == "__main__":
    create_dev_tables()
