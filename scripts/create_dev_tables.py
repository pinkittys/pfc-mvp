#!/usr/bin/env python3
"""
개발용 Supabase 테이블 생성 스크립트
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dev_tables():
    """개발용 Supabase에 테이블 생성"""
    
    # 개발용 Supabase 설정
    supabase_url = "https://gwpqvveinnzyaeathpdj.supabase.co"
    service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3cHF2dmVpbm56eWFlYXRocGRqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTc2OTk0NSwiZXhwIjoyMDcxMzQ1OTQ1fQ.8yD8LAGr0od71uNkTuiNy1k22cMC6E6-hGJsIYVmIeQ"
    
    headers = {
        'apikey': service_role_key,
        'Authorization': f'Bearer {service_role_key}',
        'Content-Type': 'application/json'
    }
    
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
    
    try:
        # SQL 실행을 위한 API 호출
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": create_tables_sql}
        )
        
        if response.status_code == 200:
            logger.info("✅ 개발용 Supabase 테이블 생성 성공!")
            return True
        else:
            logger.error(f"❌ 테이블 생성 실패: {response.status_code}")
            logger.error(f"응답: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 테이블 생성 오류: {e}")
        return False

if __name__ == "__main__":
    create_dev_tables()
