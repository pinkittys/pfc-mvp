"""
Supabase Storage에서 꽃 이미지 데이터를 가져오는 간단한 서비스
"""
import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class FlowerImage:
    """꽃 이미지 정보"""
    filename: str
    flower_name: str
    color: str
    url: str

class SupabaseImageFetcher:
    """Supabase Storage 이미지 가져오기 서비스"""
    
    def __init__(self):
        self.base_url = "https://uylrydyjbnacbjumtxue.supabase.co"
        self.bucket_name = "flowers"
        
    def get_available_images(self) -> List[FlowerImage]:
        """사용 가능한 이미지 목록 반환 (하드코딩된 목록)"""
        # 실제 Supabase Storage에 있는 이미지들을 기반으로 목록 생성
        images = [
            # 라넌큘러스
            FlowerImage("ranunculus-pk.webp", "ranunculus", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/ranunculus-pk.webp"),
            FlowerImage("ranunculus-wh.webp", "ranunculus", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/ranunculus-wh.webp"),
            FlowerImage("ranunculus-or.webp", "ranunculus", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/ranunculus-or.webp"),
            
            # 알스트로메리아
            FlowerImage("alstroemeria-pk.webp", "alstroemeria", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/alstroemeria-pk.webp"),
            FlowerImage("alstroemeria-wh.webp", "alstroemeria", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/alstroemeria-wh.webp"),
            FlowerImage("alstroemeria-or.webp", "alstroemeria", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/alstroemeria-or.webp"),
            
            # 장미
            FlowerImage("rose-pk.webp", "rose", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/rose-pk.webp"),
            FlowerImage("rose-rd.webp", "rose", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/rose-rd.webp"),
            FlowerImage("rose-wh.webp", "rose", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/rose-wh.webp"),
            FlowerImage("rose-bl.webp", "rose", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/rose-bl.webp"),
            FlowerImage("rose-or.webp", "rose", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/rose-or.webp"),
            
            # 수국
            FlowerImage("hydrangea-bl.webp", "hydrangea", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-bl.webp"),
            
            # 용담
            FlowerImage("gentiana-andrewsii-bl.webp", "gentiana", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/gentiana-andrewsii-bl.webp"),
            
            # 스카비오사
            FlowerImage("scabiosa-bl.webp", "scabiosa", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/scabiosa-bl.webp"),
            
            # 스위트피
            FlowerImage("sweet-pea-bl.webp", "sweet-pea", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/sweet-pea-bl.webp"),
            FlowerImage("sweet-pea-pk.webp", "sweet-pea", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/sweet-pea-pk.webp"),
            
            # 튤립
            FlowerImage("tulip-pk.webp", "tulip", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tulip-pk.webp"),
            FlowerImage("tulip-rd.webp", "tulip", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tulip-rd.webp"),
            FlowerImage("tulip-wh.webp", "tulip", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tulip-wh.webp"),
            FlowerImage("tulip-pu.webp", "tulip", "퍼플", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tulip-pu.webp"),
            
            # 거베라
            FlowerImage("gerbera-daisy-rd.webp", "gerbera-daisy", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/gerbera-daisy-rd.webp"),
            FlowerImage("gerbera-daisy-yl.webp", "gerbera-daisy", "옐로우", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/gerbera-daisy-yl.webp"),
            FlowerImage("gerbera-daisy-or.webp", "gerbera-daisy", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/gerbera-daisy-or.webp"),
            
            # 백합
            FlowerImage("lily-wh.webp", "lily", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/lily-wh.webp"),
            
            # 수국
            FlowerImage("hydrangea-pk.webp", "hydrangea", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-pk.webp"),
            FlowerImage("hydrangea-wh.webp", "hydrangea", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-wh.webp"),
            FlowerImage("hydrangea-pu.webp", "hydrangea", "퍼플", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-pu.webp"),
            FlowerImage("hydrangea-bl.webp", "hydrangea", "블루", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-bl.webp"),
            FlowerImage("hydrangea-gr.webp", "hydrangea", "그린", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/hydrangea-gr.webp"),
            
            # 태게테스 (마리골드)
            FlowerImage("tagetes-erecta-yl.webp", "tagetes-erecta", "옐로우", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tagetes-erecta-yl.webp"),
            FlowerImage("tagetes-erecta-or.webp", "tagetes-erecta", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/tagetes-erecta-or.webp"),
            
            # 마리골드 (태게테스의 다른 이름)
            FlowerImage("marigold-yl.webp", "marigold", "옐로우", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/marigold-yl.webp"),
            FlowerImage("marigold-or.webp", "marigold", "오렌지", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/marigold-or.webp"),
            
            # 해바라기
            FlowerImage("sunflower-yl.webp", "sunflower", "옐로우", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/sunflower-yl.webp"),
            
            # 카네이션
            FlowerImage("carnation-pk.webp", "carnation", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/carnation-pk.webp"),
            FlowerImage("carnation-rd.webp", "carnation", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/carnation-rd.webp"),
            
            # 스토크
            FlowerImage("stock-flower-wh.webp", "stock-flower", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/stock-flower-wh.webp"),
            FlowerImage("stock-flower-pu.webp", "stock-flower", "퍼플", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/stock-flower-pu.webp"),
            
            # 리시안셔스
            FlowerImage("lisianthus-pk.webp", "lisianthus", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/lisianthus-pk.webp"),
            FlowerImage("lisianthus-wh.webp", "lisianthus", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/lisianthus-wh.webp"),
            
            # 아네모네
            FlowerImage("anemone-pu.webp", "anemone", "퍼플", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/anemone-pu.webp"),
            FlowerImage("anemone-rd.webp", "anemone", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/anemone-rd.webp"),
            
            # 아스틸베
            FlowerImage("astilbe-pk.webp", "astilbe", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/astilbe-pk.webp"),
            FlowerImage("astilbe-wh.webp", "astilbe", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/astilbe-wh.webp"),
            
            # 부바르디아
            FlowerImage("bouvardia-wh.webp", "bouvardia", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/bouvardia-wh.webp"),
            
            # 베이비스브레스
            FlowerImage("babys-breath-wh.webp", "babys-breath", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/babys-breath-wh.webp"),
            
            # 칼라릴리
            FlowerImage("calla-lily-wh.webp", "calla-lily", "화이트", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/calla-lily-wh.webp"),
            
            # 안스리움
            FlowerImage("anthurium-gr.webp", "anthurium", "그린", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/anthurium-gr.webp"),
            FlowerImage("anthurium-pk.webp", "anthurium", "핑크", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/anthurium-pk.webp"),
            FlowerImage("anthurium-rd.webp", "anthurium", "빨강", f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/anthurium-rd.webp"),
        ]
        
        return images
    
    def find_image(self, flower_name: str, color: str) -> Optional[FlowerImage]:
        """꽃 이름과 색상에 맞는 이미지 찾기"""
        images = self.get_available_images()
        
        # 꽃 이름 매핑 (한글 -> 영문)
        flower_mapping = {
            '라넌큘러스': 'ranunculus',
            '알스트로메리아': 'alstroemeria', 
            '장미': 'rose',
            '튤립': 'tulip',
            '거베라': 'gerbera-daisy',
            'gerbera': 'gerbera-daisy',  # 영문 이름도 매핑
            '백합': 'lily',
            '수국': 'hydrangea',
            '태게테스': 'marigold',  # 마리골드로 매핑
            '해바라기': 'sunflower',
            '카네이션': 'carnation',
            '스토크': 'stock-flower',
            '리시안셔스': 'lisianthus',
            '아네모네': 'anemone',
            '아스틸베': 'astilbe',
            '부바르디아': 'bouvardia',
            '베이비스브레스': 'babys-breath',
            '칼라릴리': 'calla-lily',
            '안스리움': 'anthurium',
            '스위트피': 'sweet-pea',  # 스위트피 매핑 추가
            'Lathyrus Odoratus': 'sweet-pea',  # 학명도 매핑
            'sweet': 'sweet-pea'  # 기존 sweet도 매핑
        }
        
        # 색상 매핑 (한글 -> 한글)
        color_mapping = {
            '핑크': '핑크', 'pink': '핑크', 'pk': '핑크',
            '빨강': '빨강', 'red': '빨강', 'rd': '빨강',
            '화이트': '화이트', 'white': '화이트', 'wh': '화이트',
            '옐로우': '옐로우', 'yellow': '옐로우', 'yl': '옐로우',
            '퍼플': '퍼플', 'purple': '퍼플', 'pu': '퍼플',
            '블루': '블루', 'blue': '블루', 'bl': '블루',
            '그린': '그린', 'green': '그린', 'gr': '그린',
            '오렌지': '오렌지', 'orange': '오렌지', 'or': '오렌지',
            '연보라': '연보라', 'll': '연보라'
        }
        
        # 매핑된 이름으로 변환
        mapped_flower = flower_mapping.get(flower_name, flower_name.lower())
        mapped_color = color_mapping.get(color, color)
        
        print(f"🔍 이미지 검색: {flower_name} ({mapped_flower}) - {color} ({mapped_color})")
        
        # 정확한 꽃+색상 매칭 시도
        for image in images:
            if image.flower_name == mapped_flower and image.color == mapped_color:
                print(f"✅ 정확한 꽃+색상 매칭: {image.filename}")
                return image
        
        # 디버깅: 매칭된 꽃 이름과 색상 출력
        print(f"🔍 매칭 시도: {mapped_flower} - {mapped_color}")
        print(f"🔍 사용 가능한 이미지들:")
        for image in images:
            if image.color == mapped_color:
                print(f"  - {image.flower_name} ({image.color}): {image.filename}")
        
        # 색상 대체 매칭 시도 (요청된 색상이 없을 때 유사한 색상으로 대체)
        color_alternatives = self._get_color_alternatives(mapped_color)
        for alternative_color in color_alternatives:
            for image in images:
                if image.flower_name == mapped_flower and image.color == alternative_color:
                    print(f"🔄 색상 대체 매칭: {image.filename} (요청: {mapped_color} → 대체: {alternative_color})")
                    return image
        
        # 꽃 이름만 매칭 시도 (색상은 무시)
        for image in images:
            if image.flower_name == mapped_flower:
                print(f"⚠️ 꽃 이름만 매칭: {image.filename} (요청 색상: {mapped_color}, 실제 색상: {image.color})")
                return image
        
        print(f"❌ 매칭 실패: {mapped_flower}-{mapped_color}")
        return None
    
    def _get_color_alternatives(self, requested_color: str) -> List[str]:
        """요청된 색상이 없을 때 대체할 수 있는 색상들 반환"""
        color_alternatives = {
            '핑크': ['레드', '빨강', '오렌지'],  # 핑크 → 레드 우선
            '레드': ['핑크', '빨강', '오렌지'],
            '빨강': ['레드', '핑크', '오렌지'],
            '화이트': ['크림', '연보라', '라벤더'],
            '옐로우': ['오렌지', '크림', '화이트'],
            '오렌지': ['옐로우', '레드', '핑크'],
            '블루': ['퍼플', '연보라', '라벤더'],
            '퍼플': ['블루', '연보라', '라벤더'],
            '연보라': ['퍼플', '블루', '라벤더'],
            '라벤더': ['연보라', '퍼플', '블루'],
            '크림': ['화이트', '옐로우', '연보라'],
            '그린': ['화이트', '크림']
        }
        
        return color_alternatives.get(requested_color, [])
    
    def get_available_flowers(self) -> Dict[str, List[str]]:
        """사용 가능한 꽃과 색상 목록 반환"""
        images = self.get_available_images()
        
        flower_colors = {}
        for image in images:
            if image.flower_name not in flower_colors:
                flower_colors[image.flower_name] = []
            if image.color not in flower_colors[image.flower_name]:
                flower_colors[image.flower_name].append(image.color)
        
        return flower_colors

# 사용 예시
if __name__ == "__main__":
    fetcher = SupabaseImageFetcher()
    
    # 1. 사용 가능한 꽃들 확인
    available = fetcher.get_available_flowers()
    print("사용 가능한 꽃들:")
    for flower, colors in available.items():
        print(f"  {flower}: {colors}")
    
    # 2. 특정 꽃과 색상으로 매칭 테스트
    match = fetcher.find_image("라넌큘러스", "핑크")
    if match:
        print(f"매칭된 이미지: {match.url}")
    else:
        print("매칭 실패")
