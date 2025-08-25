#!/usr/bin/env python3
"""
꽃 캘리그래피 이미지 동기화 스크립트
Google Drive 폴더에서 꽃 캘리그래피 이미지들을 자동으로 다운로드하고 관리
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import base64
from PIL import Image
import io

# Google Drive API 관련
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    print("⚠️ Google Drive API 라이브러리가 설치되지 않았습니다.")
    print("pip install google-auth google-auth-oauthlib google-api-python-client")
    GOOGLE_DRIVE_AVAILABLE = False

class CalliImageSync:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.calli_dir = self.base_dir / "data" / "calli_images"
        self.calli_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.base_dir / "calli_metadata.json"
        self.folder_id = "1LEyCkYmuhBUwAE7ff5OG1D4ZLSTYyNzq"
        
        # 꽃 이름 매핑 (파일명 → 시스템 꽃명)
        self.flower_name_mapping = {
            "ammi-majus": "Ammi Majus",
            "anemone": "Anemone Coronaria", 
            "baby-breath": "Babys Breath",
            "bouvardia": "Bouvardia",
            "cockscomb": "Cockscomb",
            "cotton-plant": "Cotton Plant",
            "cymbidium": "Cymbidium Spp",
            "dahlia": "Dahlia",
            "drumstick-flower": "Drumstick Flower",
            "garden-peony": "Garden Peony",
            "gerbera-daisy": "Gerbera Daisy",
            "gladiolus": "Gladiolus",
            "globe-amaranth": "Globe Amaranth",
            "hydrangea": "Hydrangea",
            "lily": "Lily",
            "lisianthus": "Lisianthus",
            "marguerite-daisy": "Marguerite Daisy",
            "marigold": "Tagetes Erecta",
            "patrinia": "Gentiana Andrewsii",
            "ranunculus": "Ranunculus",
            "rose": "Rose",
            "scabiosa": "Scabiosa",
            "stock-flower": "Stock Flower",
            "sweet-pea": "Lathyrus Odoratus",
            "tulip": "Tulip",
            "veronica": "Veronica Spicata",
            "zinnia": "Zinnia Elegans"
        }
        
        self.service = None
        self.load_metadata()
    
    def authenticate_google_drive(self):
        """Google Drive API 인증"""
        if not GOOGLE_DRIVE_AVAILABLE:
            print("❌ Google Drive API를 사용할 수 없습니다.")
            return False
        
        creds = None
        token_file = self.base_dir / "token.json"
        credentials_file = self.base_dir / "credentials.json"
        
        # 기존 토큰이 있으면 로드
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), 
                                                        ['https://www.googleapis.com/auth/drive.readonly'])
        
        # 토큰이 없거나 만료되었으면 새로 생성
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    print("❌ credentials.json 파일이 필요합니다.")
                    print("Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 다운로드하세요.")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), 
                    ['https://www.googleapis.com/auth/drive.readonly']
                )
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        return True
    
    def list_folder_files(self) -> List[Dict]:
        """Google Drive 폴더의 파일 목록 가져오기"""
        if not self.service:
            print("❌ Google Drive 서비스가 초기화되지 않았습니다.")
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                fields="files(id,name,mimeType,modifiedTime,size)",
                orderBy="name"
            ).execute()
            
            files = results.get('files', [])
            print(f"📁 Google Drive에서 {len(files)}개 파일을 찾았습니다.")
            return files
            
        except Exception as e:
            print(f"❌ Google Drive 파일 목록 가져오기 실패: {e}")
            return []
    
    def download_file(self, file_id: str, filename: str) -> bool:
        """파일 다운로드"""
        if not self.service:
            return False
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_path = self.calli_dir / filename
            
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"  📥 {filename}: {int(status.progress() * 100)}%")
            
            return True
            
        except Exception as e:
            print(f"❌ 파일 다운로드 실패 {filename}: {e}")
            return False
    
    def process_filename(self, filename: str) -> Optional[str]:
        """파일명에서 꽃 이름 추출"""
        # 파일 확장자 제거
        name = Path(filename).stem.lower()
        
        # 꽃 이름 매핑에서 찾기
        for key, value in self.flower_name_mapping.items():
            if key in name:
                return value
        
        # 직접 매칭 시도
        for key, value in self.flower_name_mapping.items():
            if name == key:
                return value
        
        print(f"⚠️ 매핑되지 않은 파일명: {filename}")
        return None
    
    def sync_images(self):
        """이미지 동기화 실행"""
        print("🔄 꽃 캘리그래피 이미지 동기화 시작...")
        
        if not self.authenticate_google_drive():
            return
        
        # Google Drive 파일 목록 가져오기
        drive_files = self.list_folder_files()
        
        # 이미지 파일만 필터링
        image_files = [f for f in drive_files if f['mimeType'].startswith('image/')]
        
        updated_files = []
        new_files = []
        
        for file_info in image_files:
            filename = file_info['name']
            flower_name = self.process_filename(filename)
            
            if not flower_name:
                continue
            
            file_path = self.calli_dir / filename
            file_exists = file_path.exists()
            
            # 파일이 없거나 수정되었으면 다운로드
            if not file_exists or self.is_file_updated(file_info):
                if self.download_file(file_info['id'], filename):
                    if file_exists:
                        updated_files.append(filename)
                    else:
                        new_files.append(filename)
                    
                    # 메타데이터 업데이트
                    self.update_file_metadata(filename, file_info, flower_name)
        
        # 결과 출력
        if new_files:
            print(f"✅ 새로 다운로드된 파일: {len(new_files)}개")
            for f in new_files:
                print(f"  ➕ {f}")
        
        if updated_files:
            print(f"🔄 업데이트된 파일: {len(updated_files)}개")
            for f in updated_files:
                print(f"  🔄 {f}")
        
        if not new_files and not updated_files:
            print("✅ 모든 파일이 최신 상태입니다.")
        
        # 메타데이터 저장
        self.save_metadata()
        
        print(f"📊 총 {len(self.metadata)}개의 꽃 캘리그래피 이미지가 등록되어 있습니다.")
    
    def is_file_updated(self, file_info: Dict) -> bool:
        """파일이 업데이트되었는지 확인"""
        filename = file_info['name']
        file_path = self.calli_dir / filename
        
        if not file_path.exists():
            return True
        
        # 파일 크기 비교
        local_size = file_path.stat().st_size
        drive_size = int(file_info.get('size', 0))
        
        return local_size != drive_size
    
    def load_metadata(self):
        """메타데이터 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def update_file_metadata(self, filename: str, file_info: Dict, flower_name: str):
        """파일 메타데이터 업데이트"""
        self.metadata[filename] = {
            'flower_name': flower_name,
            'drive_id': file_info['id'],
            'modified_time': file_info['modifiedTime'],
            'size': file_info.get('size', 0),
            'mime_type': file_info['mimeType'],
            'local_path': str(self.calli_dir / filename)
        }
    
    def save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def get_calligraphy_list(self) -> Dict:
        """등록된 캘리그래피 목록 반환"""
        return {
            'total_count': len(self.metadata),
            'flowers': list(set([info['flower_name'] for info in self.metadata.values()])),
            'files': self.metadata
        }
    
    def get_flower_calligraphy(self, flower_name: str) -> Optional[str]:
        """특정 꽃의 캘리그래피 이미지 경로 반환"""
        for filename, info in self.metadata.items():
            if info['flower_name'] == flower_name:
                return info['local_path']
        return None

def main():
    """메인 실행 함수"""
    syncer = CalliImageSync()
    syncer.sync_images()
    
    # 결과 출력
    calli_list = syncer.get_calligraphy_list()
    print(f"\n📋 등록된 꽃 캘리그래피 목록:")
    print(f"총 {calli_list['total_count']}개 파일")
    print(f"꽃 종류: {len(calli_list['flowers'])}개")
    
    for flower in sorted(calli_list['flowers']):
        print(f"  🌸 {flower}")

if __name__ == "__main__":
    main()

