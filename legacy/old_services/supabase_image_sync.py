"""
Supabase Storage에서 꽃 이미지 데이터를 동기화하는 서비스
"""
import os
import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SupabaseImageInfo:
    """Supabase 이미지 정보"""
    name: str
    size: int
    last_modified: str
    url: str
    flower_name: str
    color: str

class SupabaseImageSync:
    """Supabase Storage 이미지 동기화 서비스"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://uylrydyjbnacbjumtxue.supabase.co")
        self.bucket_name = "flowers"
        self.images_cache = []
        
    def get_storage_images(self) -> List[SupabaseImageInfo]:
        """Supabase Storage에서 이미지 목록 가져오기"""
        try:
            # Supabase Storage API를 통해 파일 목록 가져오기
            url = f"{self.supabase_url}/storage/v1/object/list/{self.bucket_name}"
            
            headers = {
                "apikey": os.getenv("SUPABASE_ANON_KEY", ""),
                "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY', '')}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                files = response.json()
                print(f"✅ Supabase Storage에서 {len(files)}개 파일 발견")
                
                images = []
                for file_info in files:
                    if file_info.get('name', '').endswith('.webp'):
                        image_info = self._parse_image_info(file_info)
                        if image_info:
                            images.append(image_info)
                
                self.images_cache = images
                return images
            else:
                print(f"❌ Supabase Storage API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Supabase Storage 연결 실패: {e}")
            return []
    
    def _parse_image_info(self, file_info: Dict) -> Optional[SupabaseImageInfo]:
        """파일 정보에서 이미지 정보 파싱"""
        try:
            filename = file_info.get('name', '')
            
            # 파일명에서 꽃 이름과 색상 추출
            # 예: ranunculus-pk.webp -> ranunculus, pk
            if '-' in filename and filename.endswith('.webp'):
                name_part = filename.replace('.webp', '')
                parts = name_part.split('-')
                
                if len(parts) >= 2:
                    flower_name = '-'.join(parts[:-1])  # ranunculus
                    color_code = parts[-1]  # pk
                    
                    # 색상 코드를 한글로 변환
                    color_mapping = {
                        'pk': '핑크', 'pink': '핑크',
                        'rd': '빨강', 'red': '빨강',
                        'wh': '화이트', 'white': '화이트',
                        'yl': '옐로우', 'yellow': '옐로우',
                        'pu': '퍼플', 'purple': '퍼플',
                        'bl': '블루', 'blue': '블루',
                        'gr': '그린', 'green': '그린',
                        'or': '오렌지', 'orange': '오렌지'
                    }
                    
                    color_korean = color_mapping.get(color_code, color_code)
                    
                    return SupabaseImageInfo(
                        name=filename,
                        size=file_info.get('metadata', {}).get('size', 0),
                        last_modified=file_info.get('updated_at', ''),
                        url=f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}",
                        flower_name=flower_name,
                        color=color_korean
                    )
            
            return None
            
        except Exception as e:
            print(f"❌ 이미지 정보 파싱 실패: {e}")
            return None
    
    def find_matching_image(self, flower_name: str, color: str) -> Optional[SupabaseImageInfo]:
        """꽃 이름과 색상에 맞는 이미지 찾기"""
        if not self.images_cache:
            self.get_storage_images()
        
        # 정확한 매칭 시도
        for image in self.images_cache:
            if (image.flower_name.lower() == flower_name.lower() and 
                image.color == color):
                print(f"✅ 정확한 매칭: {image.flower_name}-{image.color}")
                return image
        
        # 부분 매칭 시도 (꽃 이름만)
        for image in self.images_cache:
            if image.flower_name.lower() == flower_name.lower():
                print(f"⚠️ 꽃 이름만 매칭: {image.flower_name}-{image.color} (요청: {color})")
                return image
        
        # 색상만 매칭 시도
        for image in self.images_cache:
            if image.color == color:
                print(f"⚠️ 색상만 매칭: {image.flower_name}-{image.color} (요청: {flower_name})")
                return image
        
        print(f"❌ 매칭 실패: {flower_name}-{color}")
        return None
    
    def get_available_flowers(self) -> Dict[str, List[str]]:
        """사용 가능한 꽃과 색상 목록 반환"""
        if not self.images_cache:
            self.get_storage_images()
        
        flower_colors = {}
        for image in self.images_cache:
            if image.flower_name not in flower_colors:
                flower_colors[image.flower_name] = []
            if image.color not in flower_colors[image.flower_name]:
                flower_colors[image.flower_name].append(image.color)
        
        return flower_colors
    
    def save_image_index(self, filepath: str = "data/supabase_images.json"):
        """이미지 인덱스를 JSON 파일로 저장"""
        try:
            images = self.get_storage_images()
            
            # JSON 직렬화 가능한 형태로 변환
            image_data = []
            for img in images:
                image_data.append({
                    "name": img.name,
                    "size": img.size,
                    "last_modified": img.last_modified,
                    "url": img.url,
                    "flower_name": img.flower_name,
                    "color": img.color
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(image_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 이미지 인덱스 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 이미지 인덱스 저장 실패: {e}")
            return False
    
    def load_image_index(self, filepath: str = "data/supabase_images.json") -> List[SupabaseImageInfo]:
        """저장된 이미지 인덱스 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
            
            images = []
            for data in image_data:
                images.append(SupabaseImageInfo(
                    name=data["name"],
                    size=data["size"],
                    last_modified=data["last_modified"],
                    url=data["url"],
                    flower_name=data["flower_name"],
                    color=data["color"]
                ))
            
            self.images_cache = images
            print(f"✅ 이미지 인덱스 로드 완료: {len(images)}개")
            return images
            
        except Exception as e:
            print(f"❌ 이미지 인덱스 로드 실패: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    sync = SupabaseImageSync()
    
    # 1. Supabase에서 이미지 목록 가져오기
    images = sync.get_storage_images()
    print(f"발견된 이미지: {len(images)}개")
    
    # 2. 사용 가능한 꽃과 색상 목록
    available = sync.get_available_flowers()
    print("사용 가능한 꽃들:")
    for flower, colors in available.items():
        print(f"  {flower}: {colors}")
    
    # 3. 특정 꽃과 색상으로 매칭 테스트
    match = sync.find_matching_image("ranunculus", "핑크")
    if match:
        print(f"매칭된 이미지: {match.url}")
    else:
        print("매칭 실패")
    
    # 4. 인덱스 저장
    sync.save_image_index()
