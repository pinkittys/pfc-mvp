#!/usr/bin/env python3
"""
Supabase Storage의 flowers 버킷에 있는 모든 파일 확인 (v2)
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

def check_storage_files_v2():
    """Storage 파일 목록 확인 (v2)"""
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
        
        logger.info("🔍 Storage 파일 목록 확인 중... (v2)")
        
        # 방법 1: REST API로 파일 목록 가져오기
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/storage_objects?bucket_id=eq.flowers",
                headers=headers
            )
            
            if response.status_code == 200:
                files = response.json()
                logger.info(f"📁 Storage에 총 {len(files)}개 파일이 있습니다:")
                
                for file in files:
                    name = file.get('name', '')
                    size = file.get('metadata', {}).get('size', 0)
                    created_at = file.get('created_at', '')
                    logger.info(f"📄 {name} ({size} bytes) - {created_at}")
                
                # cream/cr 패턴 찾기
                file_names = [f.get('name', '') for f in files]
                cream_files = [f for f in file_names if 'cream' in f]
                cr_files = [f for f in file_names if '-cr.' in f and 'cream' not in f]
                
                if cream_files:
                    logger.info(f"🍦 cream 파일들: {cream_files}")
                
                if cr_files:
                    logger.info(f"🔴 cr 파일들: {cr_files}")
                
                return
                
        except Exception as e:
            logger.warning(f"⚠️ REST API 방법 실패: {e}")
        
        # 방법 2: 직접 파일 접근 테스트
        logger.info("🔍 직접 파일 접근 테스트...")
        
        # 알려진 중복 파일들 테스트
        test_files = [
            'alstroemeria-spp-cream.webp',
            'alstroemeria-spp-cr.webp',
            'cymbidium-spp-cream.webp',
            'cymbidium-spp-cr.webp',
            'rose-cream.webp',
            'rose-cr.webp'
        ]
        
        existing_files = []
        
        for filename in test_files:
            try:
                response = requests.head(
                    f"{supabase_url}/storage/v1/object/public/flowers/{filename}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    existing_files.append(filename)
                    logger.info(f"✅ 존재: {filename}")
                else:
                    logger.info(f"❌ 없음: {filename} ({response.status_code})")
                    
            except Exception as e:
                logger.info(f"❌ 오류: {filename} - {e}")
        
        if existing_files:
            logger.info(f"📁 발견된 파일들: {existing_files}")
            
            # cream vs cr 중복 확인
            cream_files = [f for f in existing_files if 'cream' in f]
            cr_files = [f for f in existing_files if '-cr.' in f and 'cream' not in f]
            
            if cream_files and cr_files:
                logger.info("🔍 cream/cr 중복 발견!")
                logger.info(f"🍦 cream 파일들: {cream_files}")
                logger.info(f"🔴 cr 파일들: {cr_files}")
                
                # 중복 제거 대상 파일들
                duplicates_to_remove = []
                
                for cream_file in cream_files:
                    # cream 파일에 대응하는 cr 파일이 있는지 확인
                    base_name = cream_file.replace('-cream.webp', '')
                    cr_file = f"{base_name}-cr.webp"
                    
                    if cr_file in cr_files:
                        duplicates_to_remove.append(cream_file)
                        logger.info(f"🗑️ 제거 대상: {cream_file} (대신 {cr_file} 사용)")
                
                if duplicates_to_remove:
                    logger.info(f"🗑️ 총 {len(duplicates_to_remove)}개 중복 파일 제거 필요")
                    return duplicates_to_remove
        
        logger.info("✅ Storage 파일 확인 완료")
        return []
        
    except Exception as e:
        logger.error(f"❌ 오류: {e}")
        return []

if __name__ == "__main__":
    check_storage_files_v2()
