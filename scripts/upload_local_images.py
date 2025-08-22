#!/usr/bin/env python3
"""
로컬 이미지 파일들을 개발용 Supabase Storage에 직접 업로드하는 스크립트
"""

import os
import json
import requests
import logging
import re
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

def sanitize_filename(filename):
    """파일명을 구글 스프레드시트 flower_id 형식으로 변환"""
    # 구글 스프레드시트의 flower_id 형식에 맞춰 변환

    # 1. 파일 경로에서 꽃 이름과 색상 추출
    # 예: "zantedeschia-aethiopica/화이트.webp" → "zantedeschia-aethiopica-wh.webp"

    # 디렉토리와 파일명 분리
    parts = filename.split('/')
    if len(parts) != 2:
        return None  # 잘못된 형식이면 None 반환

    flower_dir = parts[0]
    color_file = parts[1]

    # 색상 추출 (파일명에서 .webp 제거)
    color_with_ext = color_file.replace('.webp', '')

    # 색상 코드 매핑 (구글 스프레드시트 D열 형식만 허용)
    color_mapping = {
        '화이트': 'wh', '하양': 'wh', '흰색': 'wh',
        '핑크': 'pk', '분홍': 'pk',
        '레드': 'rd', '빨강': 'rd',
        '옐로우': 'yl', '노랑': 'yl', '노란색': 'yl',
        '오렌지': 'or',
        '블루': 'bl', '파랑': 'bl',
        '퍼플': 'pu', '보라': 'pu',
        '그린': 'gr', '초록': 'gr',
        '크림색': 'cr',
        '베이지': 'be',
        '라일락': 'll',
        '네이비 블루': 'nv',
        'white': 'wh', 'pink': 'pk', 'red': 'rd', 'yellow': 'yl',
        'orange': 'or', 'blue': 'bl', 'purple': 'pu', 'green': 'gr',
        'cream': 'cr', 'beige': 'be', 'lilac': 'll', 'navy': 'nv'
    }

    # 색상 코드 찾기 - 매핑되지 않은 색상이면 None 반환
    color_code = color_mapping.get(color_with_ext)
    if color_code is None:
        logger.warning(f"⚠️ 매핑되지 않은 색상: {color_with_ext} (파일: {filename})")
        return None  # 매핑되지 않은 색상이면 None 반환

    # flower_id 형식으로 변환 (구글 스프레드시트 B열 형식)
    flower_id = f"{flower_dir}-{color_code}.webp"

    return flower_id

def check_file_exists(filename):
    """파일이 이미 존재하는지 확인"""
    try:
        check_url = f"{SUPABASE_URL}/storage/v1/object/public/flowers/{filename}"
        response = requests.head(check_url)
        return response.status_code == 200
    except Exception:
        return False

def delete_file(filename):
    """기존 파일 삭제"""
    try:
        delete_url = f"{SUPABASE_URL}/storage/v1/object/flowers/{filename}"
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
        }
        response = requests.delete(delete_url, headers=headers)
        if response.status_code == 200:
            logger.info(f"🗑️ 기존 파일 삭제: {filename}")
            return True
        else:
            logger.warning(f"⚠️ 파일 삭제 실패: {filename} - {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ 파일 삭제 오류: {filename} - {str(e)}")
        return False

def upload_image_file(file_path, filename):
    """개별 이미지 파일을 Supabase Storage에 업로드 (중복 스킵 포함)"""
    try:
        # 1. 기존 파일 존재 여부 확인
        if check_file_exists(filename):
            logger.info(f"⏭️ 기존 파일 스킵: {filename}")
            return True  # 이미 존재하므로 성공으로 처리
        
        # 2. 파일 읽기
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 3. 업로드 URL
        upload_url = f"{SUPABASE_URL}/storage/v1/object/flowers/{filename}"
        
        # 4. 파일 업로드
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
    skipped_count = 0
    
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
            original_filename = str(relative_path)
            # 파일명을 Supabase Storage에 적합한 형태로 변환
            filename = sanitize_filename(original_filename)
            total_count += 1
            
            # 매핑되지 않은 색상이거나 잘못된 형식이면 스킵
            if filename is None:
                logger.warning(f"⏭️ 스킵: {original_filename} (매핑되지 않은 색상 또는 잘못된 형식)")
                skipped_count += 1
                continue
            
            logger.info(f"📋 업로드 중: {original_filename} -> {filename}")
            
            if upload_image_file(file_path, filename):
                uploaded_count += 1
    
    logger.info(f"🎉 업로드 완료! {uploaded_count}/{total_count}개 파일 업로드됨 (스킵: {skipped_count}개)")

if __name__ == "__main__":
    main()
