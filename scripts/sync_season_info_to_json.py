#!/usr/bin/env python3
"""
스프레드시트의 계절 정보를 flower_dictionary.json에 동기화하는 스크립트
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime

class SeasonInfoSyncer:
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY/export?format=csv&gid=2100622490"
        self.flower_dict_path = "data/flower_dictionary.json"
        
        # 새로운 계절 형식을 기존 seasonality 배열로 변환하는 매핑
        self.season_format_mapping = {
            'Spring 03-05': ['봄'],
            'Summer 06-08': ['여름'],
            'Fall 09-11': ['가을'],
            'Winter 12-02': ['겨울'],
            'Spring/Summer 03-08': ['봄', '여름'],
            'Summer/Fall 06-11': ['여름', '가을'],
            'Fall/Winter 09-02': ['가을', '겨울'],
            'Winter/Spring 12-05': ['겨울', '봄'],
            'All Season 01-12': ['봄', '여름', '가을', '겨울']
        }
        
        # 색상 코드 매핑 (스프레드시트 → flower_dictionary.json)
        self.color_mapping = {
            'll': '라일락', 'pk': '핑크', 'rd': '레드', 'wh': '화이트', 
            'yl': '옐로우', 'pu': '퍼플', 'bl': '블루', 'or': '오렌지', 
            'gr': '그린', 'cr': '코랄', 'be': '베이지', 'iv': '아이보리'
        }
    
    def fetch_spreadsheet_data(self) -> List[Dict]:
        """구글 스프레드시트에서 데이터 가져오기"""
        try:
            response = requests.get(self.spreadsheet_url)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                print("❌ 스프레드시트 데이터가 충분하지 않음")
                return []
            
            headers = [h.strip().strip('"') for h in lines[0].split(',')]
            print(f"📋 스프레드시트 헤더: {headers}")
            
            data = []
            for line in lines[1:]:
                if line.strip():
                    # CSV 파싱 (쉼표로 분리, 따옴표 처리)
                    values = []
                    current_value = ""
                    in_quotes = False
                    
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            values.append(current_value.strip().strip('"'))
                            current_value = ""
                        else:
                            current_value += char
                    
                    # 마지막 값 추가
                    values.append(current_value.strip().strip('"'))
                    
                    if len(values) >= len(headers):
                        row = dict(zip(headers, values))
                        data.append(row)
            
            print(f"✅ 스프레드시트에서 {len(data)}개 행 데이터 가져옴")
            return data
            
        except Exception as e:
            print(f"❌ 스프레드시트 데이터 가져오기 실패: {e}")
            return []
    
    def load_flower_dictionary(self) -> Dict:
        """flower_dictionary.json 로드"""
        try:
            with open(self.flower_dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ flower_dictionary.json 로드 실패: {e}")
            return {}
    
    def save_flower_dictionary(self, data: Dict):
        """flower_dictionary.json 저장"""
        try:
            # 백업 생성
            backup_path = f"{self.flower_dict_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(self.flower_dict_path, 'r', encoding='utf-8') as f:
                with open(backup_path, 'w', encoding='utf-8') as backup_f:
                    backup_f.write(f.read())
            print(f"✅ 백업 생성: {backup_path}")
            
            # 새 파일 저장
            with open(self.flower_dict_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ {self.flower_dict_path} 업데이트 완료")
            
        except Exception as e:
            print(f"❌ flower_dictionary.json 저장 실패: {e}")
    
    def parse_season_format(self, season_str: str) -> List[str]:
        """새로운 계절 형식을 기존 seasonality 배열로 변환"""
        if not season_str or season_str.strip() == '':
            return ['봄', '여름']  # 기본값
        
        season_str = season_str.strip()
        return self.season_format_mapping.get(season_str, ['봄', '여름'])
    
    def convert_flower_id_to_dict_key(self, flower_id: str) -> str:
        """스프레드시트 flower_id를 flower_dictionary.json 키 형식으로 변환"""
        # flower_id 예시: "alstroemeria-spp.-or"
        # 목표 형식: "Alstroemeria Spp-오렌지"
        
        if not flower_id:
            return ""
        
        # 마지막 부분이 색상 코드인지 확인
        parts = flower_id.split('-')
        if len(parts) < 2:
            return ""
        
        color_code = parts[-1]
        flower_base = '-'.join(parts[:-1])
        
        # 색상 코드 변환
        korean_color = self.color_mapping.get(color_code, color_code)
        
        # 꽃 이름 변환 (첫 글자 대문자, 하이픈을 공백으로)
        flower_name_parts = flower_base.split('-')
        flower_name = ' '.join([part.capitalize() for part in flower_name_parts if part])
        
        # 특수 케이스 처리
        flower_name = flower_name.replace('Spp.', 'Spp')  # "Spp." → "Spp"
        
        return f"{flower_name}-{korean_color}"
    
    def find_matching_dict_key(self, flower_id: str, flower_dict: Dict) -> str:
        """flower_id에 해당하는 flower_dictionary.json의 키를 찾기"""
        # 1. 정확한 변환 시도
        exact_key = self.convert_flower_id_to_dict_key(flower_id)
        if exact_key in flower_dict:
            return exact_key
        
        # 2. 꽃 이름과 색상 모두 매칭 시도
        parts = flower_id.split('-')
        if len(parts) >= 2:
            flower_base = '-'.join(parts[:-1])  # 색상 제외한 꽃 이름
            color_code = parts[-1]  # 색상 코드
            
            # 꽃 이름 변환
            flower_name_parts = flower_base.split('-')
            flower_name = ' '.join([part.capitalize() for part in flower_name_parts if part])
            flower_name = flower_name.replace('Spp.', 'Spp')
            
            # 색상 변환
            korean_color = self.color_mapping.get(color_code, color_code)
            
            # 정확한 매칭 시도
            target_key = f"{flower_name}-{korean_color}"
            if target_key in flower_dict:
                return target_key
            
            # 꽃 이름만으로 매칭 시도 (같은 꽃의 다른 색상 찾기)
            for dict_key in flower_dict.keys():
                dict_flower_name = dict_key.split('-')[0] if '-' in dict_key else dict_key
                if flower_name.lower() == dict_flower_name.lower():
                    # 같은 꽃이면 색상도 확인
                    dict_color = dict_key.split('-')[-1] if '-' in dict_key else ""
                    if korean_color == dict_color:
                        return dict_key
            
            # 꽃 이름 부분 매칭 시도
            for dict_key in flower_dict.keys():
                dict_flower_name = dict_key.split('-')[0] if '-' in dict_key else dict_key
                if (flower_name.lower() in dict_flower_name.lower() or 
                    dict_flower_name.lower() in flower_name.lower()):
                    # 색상도 확인
                    dict_color = dict_key.split('-')[-1] if '-' in dict_key else ""
                    if korean_color == dict_color:
                        return dict_key
        
        # 3. 마지막 수단: 꽃 이름만으로 매칭 (색상 무시)
        flower_base = flower_id.split('-')[0] if '-' in flower_id else flower_id
        flower_base = flower_base.replace('-', ' ').title()
        flower_base = flower_base.replace('Spp.', 'Spp')
        
        # 같은 꽃의 모든 색상 찾기
        matching_flowers = []
        for dict_key in flower_dict.keys():
            dict_flower_name = dict_key.split('-')[0] if '-' in dict_key else dict_key
            if flower_base.lower() == dict_flower_name.lower():
                matching_flowers.append(dict_key)
        
        if matching_flowers:
            # 우선순위: 화이트 > 기본색 > 첫 번째
            priority_colors = ['화이트', '레드', '핑크', '옐로우', '블루', '퍼플', '오렌지', '그린']
            
            for color in priority_colors:
                for flower_key in matching_flowers:
                    if color in flower_key:
                        return flower_key
            
            # 우선순위 색상이 없으면 첫 번째 반환
            return matching_flowers[0]
        
        return ""
    
    def sync_season_info(self):
        """계절 정보 동기화"""
        print("🔄 계절 정보 동기화 시작...")
        
        # 1. 스프레드시트 데이터 가져오기
        spreadsheet_data = self.fetch_spreadsheet_data()
        if not spreadsheet_data:
            print("❌ 스프레드시트 데이터를 가져올 수 없음")
            return False
        
        # 2. flower_dictionary.json 로드
        flower_dict = self.load_flower_dictionary()
        if not flower_dict or 'flowers' not in flower_dict:
            print("❌ flower_dictionary.json을 로드할 수 없음")
            return False
        
        # 3. 계절 정보 매핑 생성
        season_mapping = {}
        matched_count = 0
        unmatched_count = 0
        
        for row in spreadsheet_data:
            flower_id = row.get('flower_id', '').strip()
            # 헤더 이름 확인 및 매핑
            season_months = row.get('season_months', '').strip()
            if not season_months:
                # 다른 가능한 헤더명 시도
                for key in row.keys():
                    if 'season' in key.lower() and '영문' in key:
                        season_months = row[key].strip()
                        break
            
            if flower_id and season_months and flower_id != '#N/A':
                # 이제 flower_id가 dictionary 키와 직접 매칭됨
                if flower_id in flower_dict['flowers']:
                    seasonality = self.parse_season_format(season_months)
                    season_mapping[flower_id] = seasonality
                    matched_count += 1
                    print(f"✅ {flower_id} → {season_months} → {seasonality}")
                else:
                    unmatched_count += 1
                    print(f"❌ {flower_id} → 매칭 실패")
        
        print(f"📊 매칭 결과: {matched_count}개 성공, {unmatched_count}개 실패")
        
        print(f"✅ {len(season_mapping)}개 꽃의 계절 정보 파싱 완료")
        
        # 4. flower_dictionary.json 업데이트
        updated_count = 0
        for flower_id, flower_info in flower_dict['flowers'].items():
            if flower_id in season_mapping:
                # 기존 seasonality 업데이트
                old_seasonality = flower_info.get('seasonality', [])
                new_seasonality = season_mapping[flower_id]
                
                if old_seasonality != new_seasonality:
                    flower_dict['flowers'][flower_id]['seasonality'] = new_seasonality
                    updated_count += 1
                    print(f"🔄 {flower_id}: {old_seasonality} → {new_seasonality}")
        
        print(f"✅ {updated_count}개 꽃의 계절 정보 업데이트됨")
        
        # 5. 저장
        if updated_count > 0:
            self.save_flower_dictionary(flower_dict)
            print("🎉 계절 정보 동기화 완료!")
        else:
            print("ℹ️ 업데이트할 계절 정보가 없습니다")
        
        return True

def main():
    """메인 실행 함수"""
    syncer = SeasonInfoSyncer()
    
    print("🌸 계절 정보 동기화")
    print("=" * 50)
    
    success = syncer.sync_season_info()
    
    if success:
        print("\n🎉 동기화 성공!")
    else:
        print("\n❌ 동기화 실패")

if __name__ == "__main__":
    main()
