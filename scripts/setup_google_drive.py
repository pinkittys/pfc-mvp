#!/usr/bin/env python3
"""
구글 드라이브 API 설정 도우미 스크립트
"""

import os
import json
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Google Drive API 스코프
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def setup_google_drive():
    """구글 드라이브 API 설정"""
    print("🔧 구글 드라이브 API 설정을 시작합니다...")
    print()
    
    # 1. credentials.json 파일 확인
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json 파일이 없습니다.")
        print()
        print("📋 다음 단계를 따라주세요:")
        print("1. Google Cloud Console (https://console.cloud.google.com/) 에 접속")
        print("2. 새 프로젝트 생성 또는 기존 프로젝트 선택")
        print("3. Google Drive API 활성화")
        print("4. 사용자 인증 정보 생성")
        print("5. OAuth 2.0 클라이언트 ID 생성")
        print("6. JSON 키 다운로드 후 'credentials.json'으로 이름 변경")
        print("7. 이 스크립트를 다시 실행")
        print()
        
        # 브라우저에서 Google Cloud Console 열기
        response = input("Google Cloud Console을 지금 열까요? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://console.cloud.google.com/')
        
        return False
    
    print("✅ credentials.json 파일을 찾았습니다.")
    print()
    
    # 2. OAuth 인증 플로우 실행
    try:
        print("🔐 Google 계정 인증을 시작합니다...")
        print("브라우저가 열리면 Google 계정으로 로그인하고 권한을 허용해주세요.")
        print()
        
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # 3. 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("✅ 인증이 완료되었습니다!")
        print("✅ token.json 파일이 생성되었습니다.")
        print()
        
        # 4. 테스트
        print("🧪 Google Drive API 연결을 테스트합니다...")
        from googleapiclient.discovery import build
        
        service = build('drive', 'v3', credentials=creds)
        
        # 폴더 정보 가져오기
        folder_id = "12TMGRn5DBul8g2WzJsHICS0daoieiZre"
        try:
            folder = service.files().get(fileId=folder_id).execute()
            print(f"✅ 폴더 접근 성공: {folder.get('name', 'Unknown')}")
            
            # 파일 목록 가져오기
            query = f"'{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                pageSize=10,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ 파일 목록 가져오기 성공: {len(files)}개 파일 발견")
            
            if files:
                print("📁 발견된 파일들:")
                for file in files[:5]:  # 처음 5개만 표시
                    print(f"  - {file['name']} ({file['mimeType']})")
                if len(files) > 5:
                    print(f"  ... 그리고 {len(files) - 5}개 더")
            
        except Exception as e:
            print(f"❌ 폴더 접근 실패: {e}")
            print("폴더 ID가 올바른지 확인해주세요.")
            return False
        
        print()
        print("🎉 구글 드라이브 API 설정이 완료되었습니다!")
        print("이제 관리자 페이지에서 구글 드라이브 동기화를 사용할 수 있습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return False

def check_setup():
    """설정 상태 확인"""
    print("🔍 구글 드라이브 API 설정 상태를 확인합니다...")
    print()
    
    # 파일 존재 확인
    has_credentials = os.path.exists('credentials.json')
    has_token = os.path.exists('token.json')
    
    print(f"📄 credentials.json: {'✅ 있음' if has_credentials else '❌ 없음'}")
    print(f"🔑 token.json: {'✅ 있음' if has_token else '❌ 없음'}")
    print()
    
    if has_credentials and has_token:
        print("✅ 모든 설정 파일이 준비되었습니다.")
        
        # 토큰 유효성 확인
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            if creds.expired and creds.refresh_token:
                print("🔄 토큰이 만료되었습니다. 갱신 중...")
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("✅ 토큰이 갱신되었습니다.")
            
            # API 테스트
            service = build('drive', 'v3', credentials=creds)
            folder_id = "12TMGRn5DBul8g2WzJsHICS0daoieiZre"
            
            try:
                folder = service.files().get(fileId=folder_id).execute()
                print(f"✅ API 연결 성공: {folder.get('name', 'Unknown')} 폴더에 접근 가능")
                return True
            except Exception as e:
                print(f"❌ API 연결 실패: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 토큰 확인 실패: {e}")
            return False
    else:
        print("❌ 설정이 완료되지 않았습니다.")
        return False

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='구글 드라이브 API 설정')
    parser.add_argument('--check', action='store_true', help='설정 상태 확인')
    parser.add_argument('--setup', action='store_true', help='새로 설정')
    
    args = parser.parse_args()
    
    if args.check:
        check_setup()
    elif args.setup:
        setup_google_drive()
    else:
        print("구글 드라이브 API 설정 도우미")
        print()
        print("사용법:")
        print("  python setup_google_drive.py --check    # 설정 상태 확인")
        print("  python setup_google_drive.py --setup    # 새로 설정")
        print()
        
        # 기본적으로 상태 확인
        if not check_setup():
            print()
            response = input("설정을 시작하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                setup_google_drive()

if __name__ == "__main__":
    main()


