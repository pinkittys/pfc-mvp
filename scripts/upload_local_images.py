#!/usr/bin/env python3
"""
로컬 이미지 파일들을 개발용 Supabase Storage에 직접 업로드하는 스크립트
"""

import os
import json
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv('env.dev')

# 개발용 Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.error("❌ 환경변수가 설정되지 않았습니다!")
    exit(1)

headers = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
    'Content-Type': 'application/json'
}

def upload_image_file(file_path, filename):
    """개별 이미지 파일을 Supabase Storage에 업로드"""
    try:
        # 파일 읽기
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 업로드 URL
        upload_url = f"{SUPABASE_URL}/storage/v1/object/flowers/{filename}"
        
        # 파일 업로드
        upload_headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'image/webp'
        }
        
        response = requests.post(
            upload_url,
            headers=upload_headers,
            data=file_content
        )
        
        if response.status_code == 200:
            logger.info(f"✅ 업로드 성공: {filename}")
            return True
        else:
            logger.warning(f"⚠️ 업로드 실패: {filename} - {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 업로드 오류: {filename} - {str(e)}")
        return False

def main():
    """메인 함수"""
    logger.info("🚀 로컬 이미지 파일 업로드 시작...")
    
    # 이미지 디렉토리 경로들
    image_dirs = [
        'data/images_webp',
        'images/flowers',
        'images/flowers_webp',
        'data/images'
    ]
    
    uploaded_count = 0
    total_count = 0
    
    # 각 디렉토리에서 이미지 파일 찾기
    for image_dir in image_dirs:
        if not os.path.exists(image_dir):
            logger.warning(f"⚠️ 디렉토리가 존재하지 않습니다: {image_dir}")
            continue
            
        logger.info(f"📁 디렉토리 검색 중: {image_dir}")
        
        # WebP 파일들 찾기
        for file_path in Path(image_dir).rglob("*.webp"):
            # 전체 경로에서 상대 경로 추출
            relative_path = file_path.relative_to(Path(image_dir))
            # 파일명을 경로 포함으로 생성 (예: zantedeschia-aethiopica/화이트.webp)
            filename = str(relative_path)
            total_count += 1
            
            logger.info(f"📋 업로드 중: {filename}")
            
            if upload_image_file(file_path, filename):
                uploaded_count += 1
    
    logger.info(f"🎉 업로드 완료! {uploaded_count}/{total_count}개 파일 업로드됨")

if __name__ == "__main__":
    main()
