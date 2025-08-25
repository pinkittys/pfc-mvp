#!/usr/bin/env python3
"""
Supabase Storage의 flowers 버킷에 있는 모든 파일 확인
"""
import os
import requests
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_storage_files():
    """Storage 파일 목록 확인"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수가 필요합니다")
            return
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        logger.info("🔍 Storage 파일 목록 확인 중...")
        
        # Storage 파일 목록 가져오기
        response = requests.get(
            f"{supabase_url}/storage/v1/object/list/flowers",
            headers=headers
        )
        
        if response.status_code == 200:
            files = response.json()
            
            if not files:
                logger.info("📁 Storage에 파일이 없습니다")
                return
            
            logger.info(f"📁 Storage에 총 {len(files)}개 파일이 있습니다:")
            logger.info("=" * 60)
            
            # 파일명별로 정렬
            sorted_files = sorted(files, key=lambda x: x.get('name', ''))
            
            for file in sorted_files:
                name = file.get('name', '')
                size = file.get('metadata', {}).get('size', 0)
                created_at = file.get('created_at', '')
                
                logger.info(f"📄 {name} ({size} bytes) - {created_at}")
            
            logger.info("=" * 60)
            
            # 중복 파일 패턴 찾기
            logger.info("🔍 중복 파일 패턴 분석...")
            
            file_names = [f.get('name', '') for f in files]
            
            # cream/cr 패턴 찾기
            cream_files = [f for f in file_names if 'cream' in f]
            cr_files = [f for f in file_names if '-cr.' in f and 'cream' not in f]
            
            if cream_files:
                logger.info(f"🍦 cream 파일들: {cream_files}")
            
            if cr_files:
                logger.info(f"🔴 cr 파일들: {cr_files}")
            
            # 다른 중복 패턴들도 찾기
            duplicate_patterns = {}
            
            for name in file_names:
                if '.webp' in name:
                    base_name = name.replace('.webp', '')
                    parts = base_name.split('-')
                    
                    if len(parts) >= 3:
                        flower_base = '-'.join(parts[:-1])  # 마지막 색상 코드 제외
                        color_code = parts[-1]
                        
                        if flower_base not in duplicate_patterns:
                            duplicate_patterns[flower_base] = []
                        
                        duplicate_patterns[flower_base].append(color_code)
            
            # 중복이 있는 패턴들 출력
            logger.info("🔍 중복 가능성이 있는 패턴들:")
            for flower_base, colors in duplicate_patterns.items():
                if len(colors) > 1:
                    logger.info(f"  {flower_base}: {colors}")
            
        else:
            logger.error(f"❌ Storage 파일 목록 가져오기 실패: {response.status_code}")
            logger.error(f"응답: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ 오류: {e}")

if __name__ == "__main__":
    check_storage_files()
