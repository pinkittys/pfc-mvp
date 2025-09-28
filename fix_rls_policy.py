#!/usr/bin/env python3
"""
Supabase RLS 정책 수정 스크립트
INSERT 권한을 추가합니다.
"""

import os
from supabase import create_client, Client

def fix_rls_policy():
    """RLS 정책 수정"""
    try:
        # Supabase 클라이언트 생성
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Supabase 환경변수가 설정되지 않았습니다.")
            return False
            
        supabase: Client = create_client(url, key)
        
        # INSERT 정책 추가
        insert_policy_sql = """
        CREATE POLICY "Allow public insert access" ON recommendation_snapshots
          FOR INSERT WITH CHECK (true);
        """
        
        print("🔧 RLS 정책 수정 중...")
        result = supabase.rpc('exec_sql', {'sql': insert_policy_sql}).execute()
        print("✅ INSERT 정책 추가 완료")
        
        # 기존 정책 확인
        check_policy_sql = """
        SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
        FROM pg_policies 
        WHERE tablename = 'recommendation_snapshots';
        """
        
        print("🔍 현재 정책 확인 중...")
        policies = supabase.rpc('exec_sql', {'sql': check_policy_sql}).execute()
        print(f"📋 현재 정책: {policies.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ RLS 정책 수정 실패: {e}")
        return False

if __name__ == "__main__":
    fix_rls_policy()
