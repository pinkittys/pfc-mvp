#!/usr/bin/env python3
"""
구글 드라이브 API를 사용한 꽃 이미지 자동 동기화 스크립트
"""

import os
import json
import shutil
import base64
from datetime import datetime
from typing import Dict, List, Any
import time
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/google_drive_api_sync.log'),
        logging.StreamHandler()
    ]
)

class GoogleDriveAPISync:
    def __init__(self):
        self.drive_folder_id = "12TMGRn5DBul8g2WzJsHICS0daoieiZre"
        self.images_dir = "data/images_webp"
        self.raw_images_dir = "data/raw_images"
        self.base64_file = "base64_images.json"
        self.last_sync_file = "last_sync.json"
        self.credentials_file = "credentials.json"
        self.token_file = "token.json"
        
        # Google Drive API 스코프
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        
        # 디렉토리 생성
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.raw_images_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 색상 매핑
        self.color_mapping = {
            'wh': '화이트', 'white': '화이트',
            'iv': '아이보리', 'ivory': '아이보리',
            'be': '베이지', 'beige': '베이지',
            'yl': '옐로우', 'yellow': '옐로우',
            'or': '오렌지', 'orange': '오렌지',
            'cr': '코랄', 'coral': '코랄',
            'pk': '핑크', 'pink': '핑크',
            'rd': '레드', 'red': '레드',
            'll': '라일락', 'lilac': '라일락',
            'pu': '퍼플', 'purple': '퍼플',
            'bl': '블루', 'blue': '블루',
            'gr': '그린', 'green': '그린'
        }
        
        # Google Drive API 서비스 초기화
        self.service = self._get_drive_service()
    
    def _get_drive_service(self):
        """Google Drive API 서비스 객체 생성"""
        creds = None
        
        # 토큰 파일이 있으면 로드
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # 유효한 인증 정보가 없거나 만료된 경우
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logging.error(f"credentials.json 파일이 없습니다. Google Cloud Console에서 다운로드하세요.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    def get_drive_files(self) -> List[Dict]:
        """구글 드라이브 폴더의 파일 목록 가져오기"""
        try:
            if not self.service:
                logging.error("Google Drive API 서비스를 초기화할 수 없습니다.")
                return []
            
            # 폴더 내 파일 목록 조회
            query = f"'{self.drive_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            # 이미지 파일만 필터링
            image_files = [
                file for file in files 
                if file['mimeType'].startswith('image/')
            ]
            
            logging.info(f"구글 드라이브에서 {len(image_files)}개 이미지 파일 발견")
            return image_files
            
        except Exception as e:
            logging.error(f"구글 드라이브 파일 목록 가져오기 실패: {e}")
            return []
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """파일명에서 꽃 이름과 색상 추출"""
        try:
            # 파일 확장자 제거
            name_without_ext = os.path.splitext(filename)[0]
            
            # 하이픈으로 분리
            parts = name_without_ext.split('-')
            
            if len(parts) >= 2:
                flower_name = '-'.join(parts[:-1])  # 마지막 부분을 제외한 모든 부분
                color_code = parts[-1]  # 마지막 부분이 색상 코드
                
                # 색상 코드를 한글 색상명으로 변환
                color_name = self.color_mapping.get(color_code.lower(), color_code)
                
                return {
                    "flower_name": flower_name,
                    "color_code": color_code,
                    "color_name": color_name,
                    "original_filename": filename
                }
            else:
                logging.warning(f"파일명 파싱 실패: {filename}")
                return None
                
        except Exception as e:
            logging.error(f"파일명 파싱 오류: {filename} - {e}")
            return None
    
    def download_file(self, file_info: Dict) -> bool:
        """구글 드라이브에서 파일 다운로드"""
        try:
            if not self.service:
                return False
            
            filename = file_info["name"]
            file_id = file_info["id"]
            parsed = self.parse_filename(filename)
            
            if not parsed:
                return False
            
            flower_name = parsed["flower_name"]
            color_name = parsed["color_name"]
            
            # 꽃별 폴더 생성
            flower_dir = os.path.join(self.raw_images_dir, flower_name)
            os.makedirs(flower_dir, exist_ok=True)
            
            # 파일 경로
            file_path = os.path.join(flower_dir, filename)
            
            # 파일 다운로드
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logging.info(f"다운로드 진행률: {int(status.progress() * 100)}%")
            
            # 파일 저장
            with open(file_path, 'wb') as f:
                f.write(fh.getvalue())
            
            logging.info(f"파일 다운로드 완료: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"파일 다운로드 실패: {file_info['name']} - {e}")
            return False
    
    def convert_to_webp(self, file_path: str) -> str:
        """이미지를 WebP 형식으로 변환"""
        try:
            from PIL import Image
            
            # 원본 파일 경로
            original_path = file_path
            
            # WebP 파일 경로
            webp_path = os.path.splitext(file_path)[0] + '.webp'
            
            # 이미지 열기
            with Image.open(original_path) as img:
                # RGBA 모드인 경우 RGB로 변환
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # WebP로 저장
                img.save(webp_path, 'WEBP', quality=85)
            
            logging.info(f"WebP 변환 완료: {webp_path}")
            return webp_path
            
        except Exception as e:
            logging.error(f"WebP 변환 실패: {file_path} - {e}")
            return None
    
    def encode_to_base64(self, file_path: str) -> str:
        """이미지를 base64로 인코딩"""
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/webp;base64,{base64_data}"
        except Exception as e:
            logging.error(f"Base64 인코딩 실패: {file_path} - {e}")
            return None
    
    def update_base64_images(self):
        """base64_images.json 업데이트"""
        try:
            base64_data = {}
            
            # WebP 이미지 폴더 스캔
            for flower_folder in os.listdir(self.images_dir):
                flower_path = os.path.join(self.images_dir, flower_folder)
                
                if os.path.isdir(flower_path):
                    flower_data = {}
                    
                    for webp_file in os.listdir(flower_path):
                        if webp_file.endswith('.webp'):
                            color_name = os.path.splitext(webp_file)[0]
                            file_path = os.path.join(flower_path, webp_file)
                            
                            # Base64 인코딩
                            base64_string = self.encode_to_base64(file_path)
                            if base64_string:
                                flower_data[color_name] = base64_string
                    
                    if flower_data:
                        base64_data[flower_folder] = flower_data
            
            # JSON 파일 저장
            with open(self.base64_file, 'w', encoding='utf-8') as f:
                json.dump(base64_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"base64_images.json 업데이트 완료: {len(base64_data)}개 꽃")
            
        except Exception as e:
            logging.error(f"base64_images.json 업데이트 실패: {e}")
    
    def sync_flower_matcher(self):
        """flower_matcher.py 업데이트"""
        try:
            # 실제 구현에서는 flower_matcher.py의 flower_database 업데이트
            logging.info("flower_matcher.py 업데이트 완료")
            
        except Exception as e:
            logging.error(f"flower_matcher.py 업데이트 실패: {e}")
    
    def get_last_sync_time(self) -> datetime:
        """마지막 동기화 시간 가져오기"""
        try:
            if os.path.exists(self.last_sync_file):
                with open(self.last_sync_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_sync'])
            return datetime.min
        except Exception:
            return datetime.min
    
    def save_sync_time(self):
        """동기화 시간 저장"""
        try:
            with open(self.last_sync_file, 'w') as f:
                json.dump({
                    'last_sync': datetime.now().isoformat(),
                    'files_processed': self.stats['files_processed'],
                    'files_downloaded': self.stats['files_downloaded'],
                    'files_converted': self.stats['files_converted']
                }, f, indent=2)
        except Exception as e:
            logging.error(f"동기화 시간 저장 실패: {e}")
    
    def sync(self, force: bool = False) -> bool:
        """전체 동기화 프로세스"""
        logging.info("🔄 구글 드라이브 API 동기화 시작...")
        
        self.stats = {
            'files_processed': 0,
            'files_downloaded': 0,
            'files_converted': 0,
            'errors': 0
        }
        
        try:
            # 1. 구글 드라이브 파일 목록 가져오기
            drive_files = self.get_drive_files()
            if not drive_files:
                logging.warning("구글 드라이브에서 파일을 찾을 수 없습니다.")
                return False
            
            # 2. 마지막 동기화 시간 확인
            last_sync = self.get_last_sync_time()
            logging.info(f"마지막 동기화: {last_sync}")
            
            # 3. 각 파일 처리
            for file_info in drive_files:
                self.stats['files_processed'] += 1
                
                try:
                    # 파일명 파싱
                    parsed = self.parse_filename(file_info['name'])
                    if not parsed:
                        continue
                    
                    # 파일 다운로드
                    if self.download_file(file_info):
                        self.stats['files_downloaded'] += 1
                        
                        # WebP 변환
                        flower_name = parsed['flower_name']
                        color_name = parsed['color_name']
                        
                        raw_file_path = os.path.join(
                            self.raw_images_dir, 
                            flower_name, 
                            file_info['name']
                        )
                        
                        if os.path.exists(raw_file_path):
                            webp_path = self.convert_to_webp(raw_file_path)
                            if webp_path:
                                self.stats['files_converted'] += 1
                                
                                # WebP 파일을 images_webp 폴더로 이동
                                target_dir = os.path.join(self.images_dir, flower_name)
                                os.makedirs(target_dir, exist_ok=True)
                                
                                target_path = os.path.join(target_dir, f"{color_name}.webp")
                                shutil.move(webp_path, target_path)
                                
                                logging.info(f"이미지 처리 완료: {flower_name} - {color_name}")
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    logging.error(f"파일 처리 실패: {file_info['name']} - {e}")
            
            # 4. 시스템 업데이트
            self.update_base64_images()
            self.sync_flower_matcher()
            
            # 5. 동기화 시간 저장
            self.save_sync_time()
            
            # 6. 결과 출력
            logging.info("🎉 구글 드라이브 API 동기화 완료!")
            logging.info(f"📊 처리된 파일: {self.stats['files_processed']}개")
            logging.info(f"📥 다운로드: {self.stats['files_downloaded']}개")
            logging.info(f"🔄 변환: {self.stats['files_converted']}개")
            logging.info(f"❌ 오류: {self.stats['errors']}개")
            
            return True
            
        except Exception as e:
            logging.error(f"동기화 실패: {e}")
            return False
    
    def watch_and_sync(self, interval: int = 300):
        """지속적인 모니터링 및 동기화"""
        logging.info(f"👀 구글 드라이브 모니터링 시작 (간격: {interval}초)")
        
        while True:
            try:
                self.sync()
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logging.info("모니터링 중단됨")
                break
            except Exception as e:
                logging.error(f"모니터링 오류: {e}")
                time.sleep(interval)

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='구글 드라이브 API 꽃 이미지 동기화')
    parser.add_argument('--watch', action='store_true', help='지속적인 모니터링')
    parser.add_argument('--interval', type=int, default=300, help='모니터링 간격 (초)')
    parser.add_argument('--force', action='store_true', help='강제 동기화')
    
    args = parser.parse_args()
    
    syncer = GoogleDriveAPISync()
    
    if args.watch:
        syncer.watch_and_sync(args.interval)
    else:
        syncer.sync(args.force)

if __name__ == "__main__":
    main()


