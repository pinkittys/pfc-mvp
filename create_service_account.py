#!/usr/bin/env python3
"""
Google Cloud 서비스 계정 키 생성 스크립트
"""

import json
import os
from pathlib import Path

def create_service_account_key():
    """서비스 계정 키 JSON 파일 생성"""
    
    # 기본 템플릿
    service_account_key = {
        "type": "service_account",
        "project_id": "floiy-reco-project",  # 프로젝트 ID
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "floiy-reco@floiy-reco-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/floiy-reco%40floiy-reco-project.iam.gserviceaccount.com"
    }
    
    # 파일 저장
    output_file = Path("service-account-key.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(service_account_key, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 서비스 계정 키 템플릿 생성 완료: {output_file}")
    print("\n📝 다음 단계:")
    print("1. Google Cloud Console에서 실제 서비스 계정 키 정보를 확인")
    print("2. 위 파일의 'YOUR_XXX' 부분을 실제 값으로 교체")
    print("3. Google Drive 폴더를 서비스 계정과 공유")

if __name__ == "__main__":
    create_service_account_key()
