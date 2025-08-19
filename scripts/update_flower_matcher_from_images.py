#!/usr/bin/env python3
"""
실제 이미지 폴더를 스캔해서 flower_matcher.py 자동 업데이트 스크립트
"""

import os
import json
import re
from typing import Dict, List, Any
from datetime import datetime

class FlowerMatcherUpdater:
    def __init__(self):
        self.flower_matcher_path = "app/services/flower_matcher.py"
        self.images_path = "data/images_webp"
        
    def scan_image_folders(self) -> Dict[str, List[str]]:
        """이미지 폴더를 스캔해서 꽃별 색상 목록 생성"""
        flower_colors = {}
        
        if not os.path.exists(self.images_path):
            print(f"❌ 이미지 경로가 존재하지 않습니다: {self.images_path}")
            return flower_colors
            
        for folder_name in os.listdir(self.images_path):
            folder_path = os.path.join(self.images_path, folder_name)
            if os.path.isdir(folder_path):
                # 폴더명을 꽃 이름으로 변환
                flower_name = self._convert_folder_to_flower_name(folder_name)
                
                # 해당 폴더의 이미지 파일들 확인
                image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                
                # 색상 추출 (파일명에서)
                colors = []
                for img_file in image_files:
                    color = self._extract_color_from_filename(img_file)
                    if color and color not in colors:
                        colors.append(color)
                
                if colors:
                    flower_colors[flower_name] = colors
                    print(f"✅ {flower_name}: {colors}")
        
        return flower_colors
    
    def _convert_folder_to_flower_name(self, folder_name: str) -> str:
        """폴더명을 꽃 이름으로 변환"""
        # 하이픈을 공백으로 변환하고 각 단어의 첫 글자를 대문자로
        words = folder_name.replace('-', ' ').split()
        flower_name = ' '.join(word.capitalize() for word in words)
        
        # 특별한 매핑
        name_mapping = {
            'Alstroemeria Spp': 'Alstroemeria Spp',
            'Ammi Majus': 'Ammi Majus',
            'Anemone Coronaria': 'Anemone Coronaria',
            'Anthurium Andraeanum': 'Anthurium Andraeanum',
            'Astilbe Japonica': 'Astilbe Japonica',
            'Babys Breath': 'Babys Breath',
            'Bouvardia': 'Bouvardia',
            'Cockscomb': 'Cockscomb',
            'Cotton Plant': 'Cotton Plant',
            'Cymbidium Spp': 'Cymbidium Spp',
            'Dahlia': 'Dahlia',
            'Dianthus Caryophyllus': 'Dianthus Caryophyllus',
            'Drumstick Flower': 'Drumstick Flower',
            'Freesia Refracta': 'Freesia Refracta',
            'Garden Peony': 'Garden Peony',
            'Gentiana Andrewsii': 'Gentiana Andrewsii',
            'Gerbera Daisy': 'Gerbera Daisy',
            'Gladiolus': 'Gladiolus',
            'Globe Amaranth': 'Globe Amaranth',
            'Hydrangea': 'Hydrangea',
            'Iberis Sempervirens': 'Iberis Sempervirens',
            'Iris Sanguinea': 'Iris Sanguinea',
            'Lathyrus Odoratus': 'Lathyrus Odoratus',
            'Lily': 'Lily',
            'Lisianthus': 'Lisianthus',
            'Marguerite Daisy': 'Marguerite Daisy',
            'Ranunculus Asiaticus': 'Ranunculus Asiaticus',
            'Ranunculus': 'Ranunculus',
            'Rose': 'Rose',
            'Scabiosa': 'Scabiosa',
            'Stock Flower': 'Stock Flower',
            'Tagetes Erecta': 'Tagetes Erecta',
            'Tulip': 'Tulip',
            'Veronica Spicata': 'Veronica Spicata',
            'Zinnia Elegans': 'Zinnia Elegans'
        }
        
        return name_mapping.get(flower_name, flower_name)
    
    def _extract_color_from_filename(self, filename: str) -> str:
        """파일명에서 색상 추출"""
        # 파일명에서 색상 패턴 찾기
        color_patterns = [
            r'red', r'blue', r'yellow', r'white', r'pink', r'purple', r'orange',
            r'레드', r'블루', r'옐로우', r'화이트', r'핑크', r'퍼플', r'오렌지'
        ]
        
        filename_lower = filename.lower()
        for pattern in color_patterns:
            if re.search(pattern, filename_lower):
                # 영어 색상을 한국어로 변환
                color_mapping = {
                    'red': '레드',
                    'blue': '블루', 
                    'yellow': '옐로우',
                    'white': '화이트',
                    'pink': '핑크',
                    'purple': '퍼플',
                    'orange': '오렌지'
                }
                return color_mapping.get(pattern, pattern)
        
        return '화이트'  # 기본값
    
    def update_flower_matcher(self, flower_colors: Dict[str, List[str]]):
        """flower_matcher.py 파일 업데이트"""
        # 백업 생성
        backup_path = f"{self.flower_matcher_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(self.flower_matcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 백업 생성: {backup_path}")
        
        # 새로운 꽃 데이터베이스 생성
        new_flower_database = {}
        
        for flower_name, colors in flower_colors.items():
            # 기본 정보 설정
            flower_data = {
                "korean_name": self._get_korean_name(flower_name),
                "scientific_name": flower_name,
                "image_url": f'self.base64_images.get("{flower_name.lower().replace(" ", "-")}", {{}}).get("{colors[0] if colors else "화이트"}", "")',
                "keywords": self._get_default_keywords(flower_name),
                "colors": colors,
                "emotions": self._get_default_emotions(flower_name),
                "default_color": colors[0] if colors else "화이트"
            }
            
            new_flower_database[flower_name] = flower_data
        
        # flower_matcher.py 파일 업데이트
        self._write_flower_matcher_file(new_flower_database)
        
        print(f"✅ flower_matcher.py 업데이트 완료 - {len(new_flower_database)}개 꽃")
    
    def _get_korean_name(self, flower_name: str) -> str:
        """꽃의 한국어 이름 반환"""
        korean_names = {
            'Alstroemeria Spp': '알스트로메리아',
            'Ammi Majus': '아미 마주스',
            'Anemone Coronaria': '아네모네',
            'Anthurium Andraeanum': '안스리움',
            'Astilbe Japonica': '아스틸베',
            'Babys Breath': '베이비 브레스',
            'Bouvardia': '부바르디아',
            'Cockscomb': '맨드라미',
            'Cotton Plant': '목화',
            'Cymbidium Spp': '심비디움',
            'Dahlia': '달리아',
            'Dianthus Caryophyllus': '카네이션',
            'Drumstick Flower': '드럼스틱 플라워',
            'Freesia Refracta': '프리지아',
            'Garden Peony': '가든 피오니',
            'Gentiana Andrewsii': '젠티아나',
            'Gerbera Daisy': '거베라 데이지',
            'Gladiolus': '글라디올러스',
            'Globe Amaranth': '천일홍',
            'Hydrangea': '수국',
            'Iberis Sempervirens': '이베리스',
            'Iris Sanguinea': '아이리',
            'Lathyrus Odoratus': '스위트피',
            'Lily': '릴리',
            'Lisianthus': '리시안서스',
            'Marguerite Daisy': '마거리트 데이지',
            'Ranunculus Asiaticus': '라넌큘러스',
            'Ranunculus': '라넌큘러스',
            'Rose': '장미',
            'Scabiosa': '스카비오사',
            'Stock Flower': '스톡 플라워',
            'Tagetes Erecta': '태게테스',
            'Tulip': '튤립',
            'Veronica Spicata': '베로니카',
            'Zinnia Elegans': '백일홍'
        }
        
        return korean_names.get(flower_name, flower_name)
    
    def _get_default_keywords(self, flower_name: str) -> List[str]:
        """기본 키워드 반환"""
        return ['아름다움', '자연스러움', '사랑']
    
    def _get_default_emotions(self, flower_name: str) -> List[str]:
        """기본 감정 반환"""
        return ['사랑', '기쁨', '희망']
    
    def _write_flower_matcher_file(self, flower_database: Dict[str, Any]):
        """flower_matcher.py 파일에 새로운 데이터베이스 작성"""
        # 파일의 시작 부분 읽기
        with open(self.flower_matcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # flower_database 부분 찾기
        start_pattern = r'self\.flower_database = \{'
        end_pattern = r'\n\s*\}'
        
        start_match = re.search(start_pattern, content)
        if not start_match:
            print("❌ flower_database 시작 부분을 찾을 수 없습니다")
            return
        
        # 새로운 데이터베이스 문자열 생성
        new_db_str = "self.flower_database = {\n"
        
        for flower_name, flower_data in flower_database.items():
            new_db_str += f'            "{flower_name}": {{\n'
            new_db_str += f'                "korean_name": "{flower_data["korean_name"]}",\n'
            new_db_str += f'                "scientific_name": "{flower_data["scientific_name"]}",\n'
            new_db_str += f'                "image_url": {flower_data["image_url"]},\n'
            new_db_str += f'                "keywords": {flower_data["keywords"]},\n'
            new_db_str += f'                "colors": {flower_data["colors"]},\n'
            new_db_str += f'                "emotions": {flower_data["emotions"]},\n'
            new_db_str += f'                "default_color": "{flower_data["default_color"]}"\n'
            new_db_str += '            },\n'
        
        new_db_str += '        }'
        
        # 기존 데이터베이스 부분 교체
        pattern = r'self\.flower_database = \{.*?\n\s*\}'
        new_content = re.sub(pattern, new_db_str, content, flags=re.DOTALL)
        
        # 파일에 쓰기
        with open(self.flower_matcher_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def run(self):
        """메인 실행 함수"""
        print("🔄 꽃 매칭 시스템 업데이트 시작...")
        
        # 이미지 폴더 스캔
        flower_colors = self.scan_image_folders()
        
        if not flower_colors:
            print("❌ 스캔된 꽃이 없습니다")
            return
        
        print(f"✅ {len(flower_colors)}개 꽃 폴더 스캔 완료")
        
        # flower_matcher.py 업데이트
        self.update_flower_matcher(flower_colors)
        
        print("🎉 꽃 매칭 시스템 업데이트 완료!")

if __name__ == "__main__":
    updater = FlowerMatcherUpdater()
    updater.run()

