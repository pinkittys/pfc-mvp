#!/usr/bin/env python3
"""
간단한 Google Drive 동기화 스크립트 (서비스 계정 사용)
OAuth 인증 없이 서비스 계정 키로 직접 접근
"""

import os
import json
import requests
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import csv
import io
import base64

# Google Drive API
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    print("⚠️ Google Drive API 라이브러리가 설치되지 않았습니다.")
    GOOGLE_DRIVE_AVAILABLE = False

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_drive_sync.log'),
        logging.StreamHandler()
    ]
)

class SimpleDriveSync:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.raw_images_dir = self.base_dir / "data" / "images_raw"
        self.webp_images_dir = self.base_dir / "data" / "images_webp"
        self.logs_dir = self.base_dir / "logs"
        
        # 디렉토리 생성
        self.raw_images_dir.mkdir(exist_ok=True)
        self.webp_images_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 설정
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY/export?format=csv&gid=2100622490"
        self.drive_folder_id = "12TMGRn5DBul8g2WzJsHICS0daoieiZre"
        self.last_sync_file = self.base_dir / "last_simple_sync.json"
        self.service_account_file = self.base_dir / "service-account-key.json"
        
        # Google Drive API 초기화
        self.drive_service = None
        if GOOGLE_DRIVE_AVAILABLE:
            self.drive_service = self._init_google_drive()
        
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
    
    def _init_google_drive(self):
        """Google Drive API 초기화 (서비스 계정 사용)"""
        if not GOOGLE_DRIVE_AVAILABLE:
            return None
        
        try:
            if not self.service_account_file.exists():
                logging.error("service-account-key.json 파일이 필요합니다.")
                logging.info("Google Cloud Console에서 서비스 계정 키를 다운로드하세요.")
                return None
            
            # 서비스 계정 인증 정보 로드
            credentials = service_account.Credentials.from_service_account_file(
                str(self.service_account_file),
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            return build('drive', 'v3', credentials=credentials)
            
        except Exception as e:
            logging.error(f"Google Drive API 초기화 실패: {e}")
            return None
    
    def get_spreadsheet_data(self) -> List[Dict]:
        """스프레드시트에서 데이터 가져오기"""
        try:
            response = requests.get(self.spreadsheet_url)
            response.raise_for_status()
            
            # CSV 파싱
            csv_data = response.text.split('\n')
            reader = csv.DictReader(csv_data)
            
            rows = []
            for row in reader:
                if row.get('image_url'):  # image_url이 있는 행만
                    rows.append(row)
            
            logging.info(f"스프레드시트에서 {len(rows)}개 행 가져옴 (image_url 있음)")
            return rows
            
        except Exception as e:
            logging.error(f"스프레드시트 데이터 가져오기 실패: {e}")
            return []
    
    def parse_image_url(self, image_url: str) -> Optional[Dict]:
        """이미지 URL에서 파일명 파싱"""
        try:
            # URL에서 파일명 추출
            filename = image_url.split('/')[-1]
            
            # 파일명에서 꽃명과 색상 추출
            name_without_ext = os.path.splitext(filename)[0]
            parts = name_without_ext.split('-')
            
            if len(parts) >= 2:
                flower_name = '-'.join(parts[:-1])
                color_code = parts[-1]
                
                # 색상 코드를 한글 색상명으로 변환
                color_name = self.color_mapping.get(color_code.lower(), color_code)
                
                return {
                    "filename": filename,
                    "flower_name": flower_name,
                    "color_code": color_code,
                    "color_name": color_name,
                    "image_url": image_url
                }
            
            return None
            
        except Exception as e:
            logging.error(f"이미지 URL 파싱 실패: {image_url} - {e}")
            return None
    
    def find_drive_file(self, filename: str) -> Optional[Dict]:
        """구글 드라이브에서 파일 찾기"""
        if not self.drive_service:
            return None
        
        try:
            query = f"name='{filename}' and '{self.drive_folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]
            
            return None
            
        except Exception as e:
            logging.error(f"구글 드라이브 파일 검색 실패: {filename} - {e}")
            return None
    
    def download_from_drive(self, file_info: Dict, target_path: Path) -> bool:
        """구글 드라이브에서 파일 다운로드"""
        if not self.drive_service:
            return False
        
        try:
            request = self.drive_service.files().get_media(fileId=file_info['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logging.info(f"다운로드 진행률: {int(status.progress() * 100)}%")
            
            # 파일 저장
            with open(target_path, 'wb') as f:
                f.write(fh.getvalue())
            
            logging.info(f"파일 다운로드 완료: {target_path}")
            return True
            
        except Exception as e:
            logging.error(f"파일 다운로드 실패: {file_info['name']} - {e}")
            return False
    
    def convert_to_webp(self, input_path: Path) -> Optional[Path]:
        """PNG를 WebP로 변환"""
        try:
            from PIL import Image
            
            # WebP 파일 경로
            webp_path = input_path.with_suffix('.webp')
            
            # 이미지 열기 및 변환
            with Image.open(input_path) as img:
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
            logging.error(f"WebP 변환 실패: {input_path} - {e}")
            return None
    
    def encode_to_base64(self, file_path: Path) -> str:
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
            base64_file = self.base_dir / "base64_images.json"
            
            # 기존 base64 데이터 로드
            base64_data = {}
            if base64_file.exists():
                with open(base64_file, 'r', encoding='utf-8') as f:
                    base64_data = json.load(f)
            
            # WebP 이미지 폴더 스캔
            for flower_folder in os.listdir(self.webp_images_dir):
                flower_path = self.webp_images_dir / flower_folder
                
                if flower_path.is_dir():
                    if flower_folder not in base64_data:
                        base64_data[flower_folder] = {}
                    
                    flower_data = base64_data[flower_folder]
                    
                    for webp_file in os.listdir(flower_path):
                        if webp_file.endswith('.webp'):
                            color_name = os.path.splitext(webp_file)[0]
                            file_path = flower_path / webp_file
                            
                            # Base64 인코딩 (이미 있는 경우 건너뛰기)
                            if color_name not in flower_data:
                                base64_string = self.encode_to_base64(file_path)
                                if base64_string:
                                    flower_data[color_name] = base64_string
                                    logging.info(f"Base64 인코딩 완료: {flower_folder} - {color_name}")
            
            # JSON 파일 저장
            with open(base64_file, 'w', encoding='utf-8') as f:
                json.dump(base64_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"base64_images.json 업데이트 완료: {len(base64_data)}개 꽃")
            
        except Exception as e:
            logging.error(f"base64_images.json 업데이트 실패: {e}")
    
    def get_last_sync_data(self) -> Dict:
        """마지막 동기화 데이터 가져오기"""
        try:
            if self.last_sync_file.exists():
                with open(self.last_sync_file, 'r') as f:
                    return json.load(f)
            return {"processed_urls": [], "last_sync": None}
        except Exception:
            return {"processed_urls": [], "last_sync": None}
    
    def save_sync_data(self, processed_urls: List[str]):
        """동기화 데이터 저장"""
        try:
            with open(self.last_sync_file, 'w') as f:
                json.dump({
                    "processed_urls": processed_urls,
                    "last_sync": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logging.error(f"동기화 데이터 저장 실패: {e}")
    
    def sync_new_images(self) -> bool:
        """새로운 이미지 동기화"""
        logging.info("🔄 새로운 이미지 동기화 시작...")
        
        try:
            # 1. 스프레드시트 데이터 가져오기
            spreadsheet_data = self.get_spreadsheet_data()
            if not spreadsheet_data:
                logging.warning("스프레드시트에서 데이터를 가져올 수 없습니다.")
                return False
            
            # 2. 마지막 동기화 데이터 확인
            last_sync_data = self.get_last_sync_data()
            processed_urls = set(last_sync_data.get("processed_urls", []))
            
            # 3. 새로운 이미지 URL 찾기
            new_images = []
            for row in spreadsheet_data:
                image_url = row.get('image_url', '').strip()
                if image_url and image_url not in processed_urls:
                    parsed = self.parse_image_url(image_url)
                    if parsed:
                        new_images.append({
                            "row_data": row,
                            "parsed": parsed
                        })
            
            if not new_images:
                logging.info("새로운 이미지가 없습니다.")
                return True
            
            logging.info(f"새로운 이미지 {len(new_images)}개 발견")
            
            # 4. 각 새로운 이미지 처리
            success_count = 0
            for image_info in new_images:
                try:
                    row_data = image_info["row_data"]
                    parsed = image_info["parsed"]
                    
                    image_url = row_data['image_url']
                    filename = parsed['filename']
                    flower_name = parsed['flower_name']
                    color_name = parsed['color_name']
                    
                    # 구글 드라이브에서 파일 찾기
                    drive_file = self.find_drive_file(filename)
                    if not drive_file:
                        logging.warning(f"구글 드라이브에서 파일을 찾을 수 없음: {filename}")
                        continue
                    
                    # 꽃별 폴더 생성
                    flower_raw_dir = self.raw_images_dir / flower_name
                    flower_webp_dir = self.webp_images_dir / flower_name
                    flower_raw_dir.mkdir(exist_ok=True)
                    flower_webp_dir.mkdir(exist_ok=True)
                    
                    # 파일 경로
                    raw_path = flower_raw_dir / filename
                    webp_path = flower_webp_dir / f"{color_name}.webp"
                    
                    # 이미 존재하는지 확인
                    if webp_path.exists():
                        logging.info(f"이미 존재하는 파일: {webp_path}")
                        processed_urls.add(image_url)
                        success_count += 1
                        continue
                    
                    # 다운로드
                    if self.download_from_drive(drive_file, raw_path):
                        # WebP 변환
                        converted_path = self.convert_to_webp(raw_path)
                        if converted_path:
                            # WebP 파일을 올바른 위치로 이동
                            converted_path.rename(webp_path)
                            processed_urls.add(image_url)
                            success_count += 1
                            logging.info(f"이미지 처리 완료: {flower_name} - {color_name}")
                        else:
                            # 변환 실패 시 원본 파일 삭제
                            raw_path.unlink(missing_ok=True)
                    else:
                        logging.error(f"다운로드 실패: {filename}")
                
                except Exception as e:
                    logging.error(f"이미지 처리 실패: {image_url} - {e}")
            
            # 5. 시스템 업데이트
            if success_count > 0:
                logging.info("🔄 시스템 업데이트 시작...")
                self.update_base64_images()
                logging.info("✅ 시스템 업데이트 완료")
            
            # 6. 동기화 데이터 저장
            self.save_sync_data(list(processed_urls))
            
            logging.info(f"🎉 동기화 완료! 성공: {success_count}/{len(new_images)}개")
            return True
            
        except Exception as e:
            logging.error(f"동기화 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    syncer = SimpleDriveSync()
    syncer.sync_new_images()

if __name__ == "__main__":
    main()

