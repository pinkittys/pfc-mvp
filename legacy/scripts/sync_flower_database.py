#!/usr/bin/env python3
"""
구글 스프레드시트와 flower_matcher.py 자동 동기화 스크립트
"""

import os
import json
import re
from typing import Dict, List, Any
import requests
from datetime import datetime

class FlowerDatabaseSync:
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY/edit?gid=2100622490#gid=2100622490"
        self.flower_matcher_path = "app/services/flower_matcher.py"
        self.base64_images_path = "base64_images.json"
        
    def fetch_spreadsheet_data(self) -> List[Dict]:
        """구글 스프레드시트에서 데이터 가져오기"""
        try:
            # CSV 형식으로 내보내기 URL
            csv_url = self.spreadsheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
            response = requests.get(csv_url)
            response.raise_for_status()
            
            # CSV 파싱
            lines = response.text.split('\n')
            headers = lines[0].split(',')
            data = []
            
            for line in lines[1:]:
                if line.strip():
                    values = line.split(',')
                    row = dict(zip(headers, values))
                    data.append(row)
            
            print(f"✅ 스프레드시트에서 {len(data)}개 행 데이터 가져옴")
            return data
            
        except Exception as e:
            print(f"❌ 스프레드시트 데이터 가져오기 실패: {e}")
            return []
    
    def parse_spreadsheet_data(self, data: List[Dict]) -> Dict[str, Any]:
        """스프레드시트 데이터를 flower_matcher.py 형식으로 변환"""
        flower_database = {}
        
        for row in data:
            try:
                # 필수 필드 확인
                if not row.get('name_ko') or not row.get('name_en'):
                    continue
                
                flower_id = row.get('flower_id', '').strip()
                name_ko = row.get('name_ko', '').strip()
                name_en = row.get('name_en', '').strip()
                scientific_name = row.get('scientific_name', '').strip()
                base_color = row.get('base_color', '').strip()
                moods = row.get('moods', '').strip()
                emotions = row.get('emotions', '').strip()
                contexts = row.get('contexts', '').strip()
                flower_language_short = row.get('flower_language_short', '').strip()
                
                # 꽃 이름 매핑 (스프레드시트 → flower_matcher.py)
                flower_name_mapping = {
                    'marguerite-daisy': 'Marguerite Daisy',
                    'alstroemeria-spp': 'Alstroemeria Spp',
                    'rose': 'Rose',
                    'babys-breath': 'Babys Breath',
                    'bouvardia': 'Bouvardia',
                    'cockscomb': 'Cockscomb',
                    'veronica-spicata': 'Veronica Spicata',
                    'zinnia-elegans': 'Zinnia Elegans',
                    'lathyrus-odoratus': 'Lathyrus Odoratus',
                    'cymbidium-spp': 'Cymbidium Spp'
                }
                
                flower_name = flower_name_mapping.get(flower_id, name_en)
                
                # 컬러별 available 여부 확인
                available_colors = self._get_available_colors(flower_id, base_color)
                
                # 컬러별 의미 구성
                color_meanings = self._build_color_meanings(
                    base_color, moods, emotions, contexts, flower_language_short
                )
                
                # 꽃 데이터 구성 (명확한 이름으로 매핑)
                flower_data = {
                    "korean_name": name_ko,
                    "scientific_name": scientific_name,
                    "image_url": f'self.base64_images.get("{flower_id}", {{}}).get("{base_color}", "")',
                    "keywords": self._parse_keywords(emotions, contexts),
                    "colors": [base_color],
                    "emotions": self._parse_list(emotions),
                    "moods": self._parse_list(moods),
                    "available_colors": available_colors,
                    "color_meanings": color_meanings,
                    "flower_meanings": {
                        "meanings": self._parse_list(flower_language_short),  # primary → meanings (꽃말)
                        "moods": self._parse_list(moods),                     # secondary → moods (무드)
                        "emotions": self._parse_list(emotions),               # other → emotions (감정)
                        "phrases": []                                         # 문장형 꽃말 (미사용)
                    }
                }
                
                flower_database[flower_name] = flower_data
                
            except Exception as e:
                print(f"❌ 행 파싱 실패: {row} - {e}")
                continue
        
        return flower_database
    
    def _get_available_colors(self, flower_id: str, base_color: str) -> Dict[str, bool]:
        """실제 이미지 파일이 있는 컬러만 True로 설정"""
        # 실제 이미지 폴더 확인
        image_folder = f"data/images_webp/{flower_id}"
        if not os.path.exists(image_folder):
            return {base_color: False}
        
        available_colors = {}
        for color in [base_color]:  # 현재는 base_color만, 나중에 확장 가능
            color_file = f"{image_folder}/{color}.webp"
            available_colors[color] = os.path.exists(color_file)
        
        return available_colors
    
    def _build_color_meanings(self, base_color: str, moods: str, emotions: str, 
                            contexts: str, meaning: str) -> Dict[str, Dict]:
        """컬러별 의미 구성"""
        return {
            base_color: {
                "emotions": self._parse_list(emotions),
                "moods": self._parse_list(moods),
                "contexts": self._parse_list(contexts),
                "meaning": meaning
            }
        }
    
    def _parse_list(self, text: str) -> List[str]:
        """쉼표로 구분된 텍스트를 리스트로 변환"""
        if not text:
            return []
        return [item.strip() for item in text.split(',') if item.strip()]
    
    def _parse_keywords(self, emotions: str, contexts: str) -> List[str]:
        """키워드 파싱"""
        keywords = []
        keywords.extend(self._parse_list(emotions))
        keywords.extend(self._parse_list(contexts))
        return list(set(keywords))  # 중복 제거
    
    def update_flower_matcher(self, flower_database: Dict[str, Any]):
        """flower_matcher.py 파일 업데이트"""
        try:
            # 기존 파일 읽기
            with open(self.flower_matcher_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # flower_database 딕셔너리 찾기
            start_pattern = r'self\.flower_database\s*=\s*\{'
            end_pattern = r'\s*\}\s*\n\s*def'
            
            start_match = re.search(start_pattern, content)
            if not start_match:
                print("❌ flower_database 딕셔너리를 찾을 수 없음")
                return False
            
            start_pos = start_match.start()
            
            # 끝 위치 찾기
            remaining_content = content[start_pos:]
            brace_count = 0
            end_pos = start_pos
            
            for i, char in enumerate(remaining_content):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = start_pos + i + 1
                        break
            
            # 새로운 flower_database 생성
            new_database = self._generate_flower_database_code(flower_database)
            
            # 파일 내용 교체
            new_content = (
                content[:start_pos] + 
                new_database + 
                content[end_pos:]
            )
            
            # 백업 생성
            backup_path = f"{self.flower_matcher_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 백업 생성: {backup_path}")
            
            # 새 파일 저장
            with open(self.flower_matcher_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ flower_matcher.py 업데이트 완료")
            return True
            
        except Exception as e:
            print(f"❌ flower_matcher.py 업데이트 실패: {e}")
            return False
    
    def _generate_flower_database_code(self, flower_database: Dict[str, Any]) -> str:
        """flower_database 딕셔너리를 Python 코드로 생성"""
        lines = ['self.flower_database = {']
        
        for flower_name, data in flower_database.items():
            lines.append(f'            "{flower_name}": {{')
            lines.append(f'                "korean_name": "{data["korean_name"]}",')
            lines.append(f'                "scientific_name": "{data["scientific_name"]}",')
            lines.append(f'                "image_url": {data["image_url"]},')
            lines.append(f'                "keywords": {data["keywords"]},')
            lines.append(f'                "colors": {data["colors"]},')
            lines.append(f'                "emotions": {data["emotions"]},')
            lines.append(f'                "moods": {data["moods"]},')
            lines.append(f'                "available_colors": {data["available_colors"]},')
            
            # color_meanings 코드 생성
            color_meanings_code = self._generate_color_meanings_code(data["color_meanings"])
            lines.append(f'                "color_meanings": {color_meanings_code}')
            lines.append('            },')
        
        lines.append('        }')
        return '\n'.join(lines)
    
    def _generate_color_meanings_code(self, color_meanings: Dict) -> str:
        """color_meanings를 Python 코드로 생성"""
        lines = ['{']
        for color, meaning in color_meanings.items():
            lines.append(f'                    "{color}": {{')
            lines.append(f'                        "emotions": {meaning["emotions"]},')
            lines.append(f'                        "moods": {meaning["moods"]},')
            lines.append(f'                        "contexts": {meaning["contexts"]},')
            lines.append(f'                        "meaning": "{meaning["meaning"]}"')
            lines.append('                    }')
        lines.append('                }')
        return '\n'.join(lines)
    
    def sync(self):
        """전체 동기화 프로세스 실행"""
        print("🔄 꽃 데이터베이스 동기화 시작...")
        
        # 1. 스프레드시트 데이터 가져오기
        spreadsheet_data = self.fetch_spreadsheet_data()
        if not spreadsheet_data:
            print("❌ 스프레드시트 데이터를 가져올 수 없음")
            return False
        
        # 2. 데이터 파싱
        flower_database = self.parse_spreadsheet_data(spreadsheet_data)
        if not flower_database:
            print("❌ 데이터 파싱 실패")
            return False
        
        print(f"✅ {len(flower_database)}개 꽃 데이터 파싱 완료")
        
        # 3. flower_matcher.py 업데이트
        success = self.update_flower_matcher(flower_database)
        
        if success:
            print("🎉 꽃 데이터베이스 동기화 완료!")
        else:
            print("❌ 동기화 실패")
        
        return success

def main():
    """메인 실행 함수"""
    syncer = FlowerDatabaseSync()
    syncer.sync()

if __name__ == "__main__":
    main()

