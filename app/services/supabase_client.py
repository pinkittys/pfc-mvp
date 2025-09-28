"""
Supabase 클라이언트 설정 및 샘플 스토리 관리
"""

import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

class SupabaseSampleStoriesManager:
    """Supabase 샘플 스토리 관리 클래스"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수가 필요합니다")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        """모든 샘플 스토리 조회"""
        try:
            result = self.client.table('sample_stories').select('*').order('id').execute()
            return result.data
        except Exception as e:
            print(f"❌ 샘플 스토리 조회 실패: {e}")
            return []
    
    def get_story_by_id(self, story_id: str) -> Optional[Dict[str, Any]]:
        """특정 스토리 조회"""
        try:
            result = self.client.table('sample_stories').select('*').eq('id', story_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ 스토리 조회 실패 ({story_id}): {e}")
            return None
    
    def get_stories_by_category(self, category: str) -> List[Dict[str, Any]]:
        """카테고리별 스토리 조회"""
        try:
            result = self.client.table('sample_stories').select('*').eq('category', category).order('id').execute()
            return result.data
        except Exception as e:
            print(f"❌ 카테고리별 스토리 조회 실패 ({category}): {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """사용 가능한 카테고리 목록 조회"""
        try:
            result = self.client.table('sample_stories').select('category').execute()
            categories = list(set([item['category'] for item in result.data]))
            return sorted(categories)
        except Exception as e:
            print(f"❌ 카테고리 조회 실패: {e}")
            return []
    
    def get_total_count(self) -> int:
        """전체 스토리 개수 조회"""
        try:
            result = self.client.table('sample_stories').select('id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            print(f"❌ 총 개수 조회 실패: {e}")
            return 0

# 전역 인스턴스 (싱글톤 패턴)
_supabase_manager: Optional[SupabaseSampleStoriesManager] = None

def get_supabase_manager() -> SupabaseSampleStoriesManager:
    """Supabase 매니저 인스턴스 반환 (싱글톤)"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseSampleStoriesManager()
    return _supabase_manager
