"""
꽃 캘리그래피 이미지 동기화 서비스
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import time
from datetime import datetime

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
        self.base_dir = Path(__file__).parent.parent.parent
        self.calli_dir = self.base_dir / "data" / "calli_images"
        self.calli_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.base_dir / "calli_metadata.json"
        self.folder_id = "1LEyCkYmuhBUwAE7ff5OG1D4ZLSTYyNzq"  # Google Drive 폴더 ID
        
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
        
        # Google Drive 인증 시도
        if self.authenticate_google_drive():
            # Google Drive에서 파일 목록 가져오기
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
        else:
            # Google Drive 인증 실패 시 더미 데이터 사용
            print("⚠️ Google Drive 인증 실패, 더미 데이터를 사용합니다.")
            if not self.metadata:
                self._create_dummy_data()
        
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
    
    def update_file_metadata(self, filename: str, file_info: Dict, flower_name: str):
        """파일 메타데이터 업데이트"""
        self.metadata[filename] = {
            'flower_name': flower_name,
            'drive_id': file_info.get('id', file_info.get('drive_id', f'manual_{int(time.time())}')),
            'modified_time': file_info.get('modifiedTime', file_info.get('modified_time', datetime.now().isoformat() + "Z")),
            'size': file_info.get('size', 0),
            'mime_type': file_info.get('mimeType', file_info.get('mime_type', 'image/png')),
            'local_path': str(self.calli_dir / filename)
        }
    
    def load_metadata(self):
        """메타데이터 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
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
    
    def _create_dummy_data(self):
        """더미 데이터 생성"""
        flower_names = [
            "Ammi Majus", "Anemone Coronaria", "Babys Breath", "Bouvardia",
            "Cockscomb", "Cotton Plant", "Cymbidium Spp", "Dahlia",
            "Drumstick Flower", "Garden Peony", "Gerbera Daisy", "Gladiolus",
            "Globe Amaranth", "Hydrangea", "Lily", "Lisianthus",
            "Marguerite Daisy", "Tagetes Erecta", "Gentiana Andrewsii",
            "Ranunculus", "Rose", "Scabiosa", "Stock Flower",
            "Lathyrus Odoratus", "Tulip", "Veronica Spicata", "Zinnia Elegans"
        ]
        
        for i, flower_name in enumerate(flower_names):
            filename = f"{flower_name.lower().replace(' ', '-')}.png"
            file_path = self.calli_dir / filename
            
            # 파일이 존재하지 않으면 더미 파일 생성
            if not file_path.exists():
                self._create_dummy_image(flower_name, file_path)
            
            # 메타데이터 생성
            self.metadata[filename] = {
                'flower_name': flower_name,
                'drive_id': f'dummy_id_{i}',
                'modified_time': '2024-01-15T10:00:00.000Z',
                'size': file_path.stat().st_size if file_path.exists() else 1024,
                'mime_type': 'image/png',
                'local_path': str(file_path)
            }
        
        self.save_metadata()
    
    def _create_dummy_image(self, flower_name: str, file_path: Path):
        """더미 이미지 생성"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 이미지 크기
            width, height = 400, 300
            
            # 배경색
            bg_color = (255, 248, 220)  # 코랄
            
            # 이미지 생성
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # 폰트 설정
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # 텍스트 색상
            text_color = (70, 130, 180)  # 스틸 블루
            
            # 텍스트 중앙 정렬
            bbox = draw.textbbox((0, 0), flower_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # 텍스트 그리기
            draw.text((x, y), flower_name, fill=text_color, font=font)
            
            # 장식선 추가
            line_color = (200, 200, 200)
            draw.line([(50, y-20), (width-50, y-20)], fill=line_color, width=2)
            draw.line([(50, y+text_height+20), (width-50, y+text_height+20)], fill=line_color, width=2)
            
            # 이미지 저장
            image.save(file_path, 'PNG')
            print(f"  📝 생성: {file_path.name}")
            
        except ImportError:
            # PIL이 없으면 빈 파일 생성
            file_path.touch()
            print(f"  📝 생성: {file_path.name} (빈 파일)")
    
    def save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def upload_manual_image(self, flower_name: str, file) -> Dict:
        """수동으로 캘리그래피 이미지 업로드"""
        try:
            print(f"🔍 파일 객체 정보: {type(file)}")
            print(f"🔍 파일 객체 속성: {dir(file)}")
            
            # 꽃 이름을 파일명으로 변환
            filename = self._get_filename_from_flower_name(flower_name)
            if not filename:
                raise ValueError(f"지원하지 않는 꽃 이름입니다: {flower_name}")
            
            # 파일 저장
            file_path = self.calli_dir / filename
            
            # 파일 객체에서 내용 읽기 (안전하게)
            try:
                # 파일 객체의 실제 구조 확인
                if hasattr(file, 'file'):
                    content = file.file.read()
                    file.file.seek(0)  # 파일 포인터를 처음으로 되돌리기
                elif hasattr(file, 'read'):
                    content = file.read()
                    file.seek(0)
                else:
                    raise ValueError("파일 객체에서 내용을 읽을 수 없습니다")
                    
            except Exception as e:
                print(f"❌ 파일 읽기 실패: {e}")
                raise ValueError(f"파일을 읽을 수 없습니다: {e}")
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # 메타데이터 업데이트
            file_info = {
                "flower_name": flower_name,
                "drive_id": f"manual_{int(time.time())}",
                "modified_time": datetime.now().isoformat() + "Z",
                "size": len(content),
                "mime_type": getattr(file, 'content_type', 'image/png'),
                "local_path": str(file_path)
            }
            
            self.update_file_metadata(filename, file_info, flower_name)
            self.save_metadata()
            
            print(f"✅ 수동 업로드 완료: {flower_name} -> {filename}")
            return {
                "flower_name": flower_name,
                "filename": filename,
                "file_path": str(file_path),
                "size": len(content)
            }
            
        except Exception as e:
            print(f"❌ 수동 업로드 실패: {e}")
            raise e
    
    def delete_manual_image(self, flower_name: str) -> Dict:
        """수동으로 캘리그래피 이미지 삭제"""
        try:
            # 꽃 이름을 파일명으로 변환
            filename = self._get_filename_from_flower_name(flower_name)
            if not filename:
                raise ValueError(f"지원하지 않는 꽃 이름입니다: {flower_name}")
            
            # 파일 삭제
            file_path = self.calli_dir / filename
            if file_path.exists():
                file_path.unlink()
                print(f"✅ 파일 삭제 완료: {filename}")
            else:
                print(f"⚠️ 파일이 존재하지 않음: {filename}")
            
            # 메타데이터에서 제거
            if filename in self.metadata:
                del self.metadata[filename]
                self.save_metadata()
                print(f"✅ 메타데이터에서 제거 완료: {filename}")
            
            return {
                "flower_name": flower_name,
                "filename": filename,
                "deleted": True
            }
            
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            raise e
    
    def _get_filename_from_flower_name(self, flower_name: str) -> Optional[str]:
        """꽃 이름을 파일명으로 변환"""
        # 역방향 매핑 생성
        reverse_mapping = {v: k for k, v in self.flower_name_mapping.items()}
        
        if flower_name in reverse_mapping:
            return f"{reverse_mapping[flower_name]}.png"
        
        # 직접 매칭 시도
        for key, value in self.flower_name_mapping.items():
            if value.lower() == flower_name.lower():
                return f"{key}.png"
        
        return None
    
    def clear_dummy_data(self) -> Dict:
        """더미 캘리그래피 데이터 모두 삭제"""
        try:
            deleted_count = 0
            
            # 더미 데이터 파일들 삭제
            for filename in self.metadata.keys():
                if filename.endswith('.png'):
                    file_path = self.calli_dir / filename
                    if file_path.exists():
                        file_path.unlink()
                        deleted_count += 1
                        print(f"✅ 더미 파일 삭제: {filename}")
            
            # 메타데이터 초기화
            self.metadata = {}
            self.save_metadata()
            
            print(f"✅ 더미 데이터 삭제 완료: {deleted_count}개 파일")
            return {
                "deleted_count": deleted_count,
                "message": f"{deleted_count}개의 더미 캘리그래피 파일이 삭제되었습니다."
            }
            
        except Exception as e:
            print(f"❌ 더미 데이터 삭제 실패: {e}")
            raise e
    
    def extract_flower_name_from_filename(self, filename: str) -> Optional[str]:
        """파일명에서 꽃 이름 추출"""
        try:
            print(f"🔍 파일명 분석: {filename}")
            
            # 파일 확장자 제거
            name_without_ext = filename.lower().replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('.gif', '').replace('.jpeg', '')
            print(f"🔍 확장자 제거 후: {name_without_ext}")
            
            # 파일명에서 꽃 이름 매칭
            for key, value in self.flower_name_mapping.items():
                if key.lower() in name_without_ext or value.lower() in name_without_ext:
                    print(f"✅ 매칭 성공: {key} -> {value}")
                    return value
            
            # 추가 매칭 규칙
            name_mappings = {
                'ammi': 'Ammi Majus',
                'anemone': 'Anemone Coronaria',
                'baby': 'Babys Breath',
                'babys': 'Babys Breath',
                'bouvardia': 'Bouvardia',
                'cockscomb': 'Cockscomb',
                'cotton': 'Cotton Plant',
                'cymbidium': 'Cymbidium Spp',
                'dahlia': 'Dahlia',
                'drumstick': 'Drumstick Flower',
                'peony': 'Garden Peony',
                'gerbera': 'Gerbera Daisy',
                'gladiolus': 'Gladiolus',
                'globe': 'Globe Amaranth',
                'hydrangea': 'Hydrangea',
                'lily': 'Lily',
                'lisianthus': 'Lisianthus',
                'marguerite': 'Marguerite Daisy',
                'marigold': 'Tagetes Erecta',
                'patrinia': 'Gentiana Andrewsii',
                'gentiana': 'Gentiana Andrewsii',
                'ranunculus': 'Ranunculus',
                'rose': 'Rose',
                'scabiosa': 'Scabiosa',
                'stock': 'Stock Flower',
                'sweet': 'Lathyrus Odoratus',
                'sweet-pea': 'Lathyrus Odoratus',
                'tulip': 'Tulip',
                'veronica': 'Veronica Spicata',
                'zinnia': 'Zinnia Elegans'
            }
            
            for key, value in name_mappings.items():
                if key in name_without_ext:
                    print(f"✅ 추가 매칭 성공: {key} -> {value}")
                    return value
            
            print(f"⚠️ 매칭되지 않은 파일명: {filename}")
            return None
            
        except Exception as e:
            print(f"❌ 파일명에서 꽃 이름 추출 실패: {filename} - {e}")
            return None
