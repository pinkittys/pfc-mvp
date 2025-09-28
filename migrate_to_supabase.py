#!/usr/bin/env python3
"""
JSON 데이터를 Supabase 테이블로 이관하는 스크립트
"""

import json
import os
from supabase import create_client, Client
from typing import Dict, Any

def load_json_data() -> Dict[str, Any]:
    """JSON 파일에서 샘플 스토리 데이터 로드"""
    try:
        with open('data/sample_stories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return {}

def transform_story_data(story: Dict[str, Any]) -> Dict[str, Any]:
    """JSON 스토리 데이터를 Supabase 테이블 형식으로 변환"""
    predefined_keywords = story.get('predefined_keywords', {})
    
    return {
        'id': story.get('id'),
        'title': story.get('title'),
        'story': story.get('story'),
        'category': story.get('category'),
        'emotions': predefined_keywords.get('emotions', []),
        'situations': predefined_keywords.get('situations', []),
        'moods': predefined_keywords.get('moods', []),
        'colors': predefined_keywords.get('colors', [])
    }

def migrate_to_supabase():
    """JSON 데이터를 Supabase로 이관"""
    
    # Supabase 클라이언트 초기화
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수를 설정해주세요.")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase 클라이언트 연결 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return
    
    # JSON 데이터 로드
    json_data = load_json_data()
    if not json_data:
        return
    
    stories = json_data.get('sample_stories', [])
    print(f"📊 총 {len(stories)}개 스토리 발견")
    
    # 데이터 변환 및 삽입
    success_count = 0
    error_count = 0
    
    for story in stories:
        try:
            # 데이터 변환
            transformed_data = transform_story_data(story)
            
            # Supabase에 삽입
            result = supabase.table('sample_stories').insert(transformed_data).execute()
            
            if result.data:
                success_count += 1
                print(f"✅ {transformed_data['id']}: {transformed_data['title']}")
            else:
                error_count += 1
                print(f"❌ {transformed_data['id']}: 삽입 실패")
                
        except Exception as e:
            error_count += 1
            print(f"❌ {story.get('id', 'Unknown')}: {e}")
    
    print(f"\n📊 이관 완료: 성공 {success_count}개, 실패 {error_count}개")

def verify_migration():
    """이관된 데이터 검증"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ 환경변수 설정 필요")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 전체 개수 확인
        result = supabase.table('sample_stories').select('id', count='exact').execute()
        total_count = result.count
        print(f"📊 Supabase 테이블 총 레코드 수: {total_count}")
        
        # 샘플 데이터 확인
        sample_result = supabase.table('sample_stories').select('*').limit(3).execute()
        print(f"📋 샘플 데이터:")
        for item in sample_result.data:
            print(f"  - {item['id']}: {item['title']}")
            
    except Exception as e:
        print(f"❌ 검증 실패: {e}")

if __name__ == "__main__":
    print("🚀 JSON → Supabase 이관 시작")
    print("=" * 50)
    
    # 1. 이관 실행
    migrate_to_supabase()
    
    print("\n" + "=" * 50)
    print("🔍 이관 결과 검증")
    
    # 2. 검증
    verify_migration()
    
    print("\n✅ 이관 완료!")
