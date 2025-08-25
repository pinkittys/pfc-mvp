#!/usr/bin/env python3
"""
Supabase Storage 복사 스크립트
실서버 Storage → 개발용 Storage
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def copy_supabase_storage():
    """실서버 Storage를 개발용으로 복사"""
    
    # 실서버 Supabase 설정
    prod_url = "https://uylrydyjbnacbjumtxue.supabase.co"
    prod_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5bHJ5ZHlqYm5hY2JqdW10eHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxMDQzODIsImV4cCI6MjA3MDY4MDM4Mn0.8koZmaOIKt9y03YHmHLps81XPGfWpAVRXkBnhCuCgmw"
    
    # 개발용 Supabase 설정
    dev_url = "https://gwpqvveinnzyaeathpdj.supabase.co"
    dev_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3cHF2dmVpbm56eWFlYXRocGRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3Njk5NDUsImV4cCI6MjA3MTM0NTk0NX0.QzEwxiAh9Krx0Bo5pK-LIHRQpzQZZ-JbejV9oSz9yTg"
    
    prod_headers = {
        'apikey': prod_key,
        'Authorization': f'Bearer {prod_key}'
    }
    
    dev_headers = {
        'apikey': dev_key,
        'Authorization': f'Bearer {dev_key}'
    }
    
    try:
        # 1. 로컬 이미지 파일 목록 사용 (base64_images.json 기반)
        logger.info("📂 로컬 이미지 파일 목록 사용...")
        
        import json
        with open('base64_images.json', 'r', encoding='utf-8') as f:
            images_data = json.load(f)
        
        files = []
        for flower_id, color_data in images_data.items():
            for color in color_data.keys():
                # 파일명 생성 (flower_id-color.webp 형식)
                file_name = f"{flower_id}-{color}.webp"
                files.append({'name': file_name, 'flower_id': flower_id, 'color': color})
        
        logger.info(f"📁 총 {len(files)}개 파일 발견")
        
        # 2. 각 파일을 개발용으로 복사
        success_count = 0
        for file_info in files:
            file_name = file_info.get('name')
            flower_id = file_info.get('flower_id')
            color = file_info.get('color')
            
            if not file_name:
                continue
                
            logger.info(f"📋 복사 중: {file_name}")
            
            # 실서버에서 파일 다운로드 시도
            download_response = requests.get(
                f"{prod_url}/storage/v1/object/public/flowers/{file_name}",
                headers=prod_headers
            )
            
            if download_response.status_code != 200:
                logger.warning(f"⚠️ 실서버에서 파일 다운로드 실패: {file_name}")
                # 로컬 base64 데이터 사용
                base64_data = images_data[flower_id][color]
                if base64_data.startswith('data:image/webp;base64,'):
                    base64_data = base64_data.split(',')[1]
                
                import base64
                file_content = base64.b64decode(base64_data)
            else:
                file_content = download_response.content
            
            # 개발용으로 업로드
            upload_response = requests.post(
                f"{dev_url}/storage/v1/object/flowers/{file_name}",
                headers=dev_headers,
                data=file_content
            )
            
            if upload_response.status_code == 200:
                success_count += 1
                logger.info(f"✅ 복사 완료: {file_name}")
            else:
                logger.warning(f"⚠️ 업로드 실패: {file_name} - {upload_response.status_code}")
        
        logger.info(f"🎉 Storage 복사 완료! {success_count}/{len(files)}개 파일 복사됨")
        return True
        
    except Exception as e:
        logger.error(f"❌ Storage 복사 오류: {e}")
        return False

if __name__ == "__main__":
    copy_supabase_storage()
