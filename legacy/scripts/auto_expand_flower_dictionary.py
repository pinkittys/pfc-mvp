#!/usr/bin/env python3
"""
등록된 이미지 기준으로 꽃 사전 자동 확장 스크립트
"""

import os
import json
import re
from typing import Dict, List, Any
from datetime import datetime

class FlowerDictionaryAutoExpander:
    def __init__(self):
        self.images_path = "data/images_webp"
        self.dictionary_service_path = "app/services/flower_dictionary.py"
        
    def scan_image_combinations(self) -> List[Dict[str, str]]:
        """이미지 폴더를 스캔해서 꽃-색깔 조합 목록 생성"""
        combinations = []
        
        if not os.path.exists(self.images_path):
            print(f"❌ 이미지 경로가 존재하지 않습니다: {self.images_path}")
            return combinations
            
        for folder_name in os.listdir(self.images_path):
            folder_path = os.path.join(self.images_path, folder_name)
            if os.path.isdir(folder_path):
                # 폴더명을 꽃 이름으로 변환
                flower_name = self._convert_folder_to_flower_name(folder_name)
                
                # 해당 폴더의 이미지 파일들 확인
                image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                
                # 각 색상별로 조합 생성
                for img_file in image_files:
                    color = self._extract_color_from_filename(img_file)
                    if color:
                        combinations.append({
                            "scientific_name": flower_name,
                            "korean_name": self._get_korean_name(flower_name),
                            "color": color,
                            "folder": folder_name
                        })
                        print(f"✅ {flower_name} ({color})")
        
        return combinations
    
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
        color_patterns = {
            'red': '레드', 'blue': '블루', 'yellow': '옐로우', 'white': '화이트', 
            'pink': '핑크', 'purple': '퍼플', 'orange': '오렌지', 'green': '그린',
            '레드': '레드', '블루': '블루', '옐로우': '옐로우', '화이트': '화이트',
            '핑크': '핑크', '퍼플': '퍼플', '오렌지': '오렌지', '그린': '그린'
        }
        
        filename_lower = filename.lower()
        for pattern, korean_color in color_patterns.items():
            if pattern.lower() in filename_lower:
                return korean_color
        
        return '화이트'  # 기본값
    
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
    
    def check_existing_dictionary(self) -> List[str]:
        """현재 꽃 사전에 등록된 꽃 ID 목록 반환"""
        try:
            # 꽃 사전 서비스에서 등록된 꽃 목록 가져오기
            import sys
            sys.path.append('.')
            
            from app.services.flower_dictionary import FlowerDictionaryService
            service = FlowerDictionaryService()
            existing_flowers = service.get_all_flowers()
            
            return [flower.id for flower in existing_flowers]
        except Exception as e:
            print(f"⚠️ 꽃 사전 확인 중 오류: {e}")
            return []
    
    def auto_expand_dictionary(self):
        """꽃 사전 자동 확장"""
        print("🔄 꽃 사전 자동 확장 시작...")
        
        # 1. 이미지 조합 스캔
        combinations = self.scan_image_combinations()
        
        if not combinations:
            print("❌ 스캔된 꽃 조합이 없습니다")
            return
        
        print(f"✅ {len(combinations)}개 꽃-색깔 조합 스캔 완료")
        
        # 2. 현재 꽃 사전 확인
        existing_ids = self.check_existing_dictionary()
        print(f"📚 현재 꽃 사전: {len(existing_ids)}개")
        
        # 3. 새로운 조합 필터링
        new_combinations = []
        for combo in combinations:
            flower_id = f"{combo['scientific_name']}-{combo['color']}"
            if flower_id not in existing_ids:
                new_combinations.append(combo)
        
        if not new_combinations:
            print("✅ 모든 꽃 조합이 이미 꽃 사전에 등록되어 있습니다!")
            return
        
        print(f"🆕 새로 추가할 꽃 조합: {len(new_combinations)}개")
        
        # 4. LLM을 통한 정보 수집 (선택적)
        self._collect_info_for_new_combinations(new_combinations)
        
        print("🎉 꽃 사전 자동 확장 완료!")
    
    def _collect_info_for_new_combinations(self, combinations: List[Dict[str, str]]):
        """새로운 조합에 대한 정보 수집"""
        try:
            import sys
            sys.path.append('.')
            
            from app.services.flower_info_collector import FlowerInfoCollector
            from app.services.flower_dictionary import FlowerDictionaryService
            
            # OpenAI API 키 확인
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️ OpenAI API 키가 설정되지 않아 정보 수집을 건너뜁니다")
                return
            
            collector = FlowerInfoCollector(api_key)
            service = FlowerDictionaryService()
            
            success_count = 0
            for combo in combinations:
                try:
                    print(f"📝 정보 수집 중: {combo['scientific_name']} ({combo['color']})")
                    
                    # LLM을 통한 정보 수집
                    flower_info = collector.collect_flower_info(
                        combo['scientific_name'], 
                        combo['korean_name'], 
                        combo['color']
                    )
                    
                    # 꽃 사전에 추가
                    flower_id = service.create_flower_entry(flower_info)
                    print(f"✅ 추가 완료: {flower_id}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ 정보 수집 실패: {combo['scientific_name']} ({combo['color']}) - {e}")
            
            print(f"📊 정보 수집 완료: {success_count}/{len(combinations)}개 성공")
            
        except Exception as e:
            print(f"❌ 정보 수집 중 오류: {e}")
    
    def run(self):
        """메인 실행 함수"""
        self.auto_expand_dictionary()

if __name__ == "__main__":
    expander = FlowerDictionaryAutoExpander()
    expander.run()

