import json
import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import openai
from app.models.schemas import FlowerDictionary

class FlowerDictionaryService:
    """꽃 사전 서비스"""
    
    def __init__(self):
        self.dictionary_file = "data/flower_dictionary.json"
        self.api_base_url = "http://localhost:8002/api/v1/admin/dictionary"
        self.dictionary_data = self._load_dictionary()
        
    def _load_dictionary(self) -> Dict[str, Any]:
        """꽃 사전 데이터 로드 (API 우선, 파일 폴백)"""
        try:
            # API에서 데이터 로드 시도
            response = requests.get(f"{self.api_base_url}/flowers", timeout=5)
            if response.status_code == 200:
                flowers_data = response.json()
                # API 응답을 내부 형식으로 변환
                flowers_dict = {}
                for flower in flowers_data:
                    if isinstance(flower, dict) and 'id' in flower:
                        flowers_dict[flower['id']] = flower
                
                return {
                    "flowers": flowers_dict,
                    "metadata": {"total_count": len(flowers_dict), "last_updated": datetime.now().isoformat()}
                }
        except Exception as e:
            print(f"⚠️ API 로드 실패, 파일에서 로드: {e}")
        
        # 파일에서 로드 (폴백)
        if os.path.exists(self.dictionary_file):
            try:
                with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 파일 로드 실패: {e}")
        
        return {"flowers": {}, "metadata": {"total_count": 0, "last_updated": ""}}
    
    def _save_dictionary(self):
        """꽃 사전 데이터 저장"""
        os.makedirs(os.path.dirname(self.dictionary_file), exist_ok=True)
        with open(self.dictionary_file, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary_data, f, ensure_ascii=False, indent=2)
    
    def generate_flower_id(self, scientific_name: str, color: str) -> str:
        """꽃 ID 생성 (학명-컬러 기준)"""
        return f"{scientific_name}-{color}"
    
    def get_flower_info(self, flower_id: str) -> Optional[FlowerDictionary]:
        """특정 꽃 정보 조회"""
        if flower_id in self.dictionary_data["flowers"]:
            return FlowerDictionary(**self.dictionary_data["flowers"][flower_id])
        return None
    
    def search_flowers(self, query: str, context: Optional[str] = None, limit: int = 10) -> List[FlowerDictionary]:
        """꽃 사전 검색"""
        results = []
        query_lower = query.lower()
        
        for flower_data in self.dictionary_data["flowers"].values():
            flower = FlowerDictionary(**flower_data)
            
            # 검색 대상 필드들
            searchable_text = [
                flower.scientific_name.lower(),
                flower.korean_name.lower(),
                flower.color.lower(),
                " ".join([meaning for meanings in flower.flower_meanings.values() for meaning in meanings]).lower(),
                " ".join([mood for moods in flower.moods.values() for mood in moods]).lower(),
                " ".join([char for chars in flower.characteristics.values() for char in chars]).lower(),
                " ".join([ref for refs in flower.cultural_references.values() for ref in refs]).lower()
            ]
            
            # 검색어와 매칭 확인
            if any(query_lower in text for text in searchable_text):
                results.append(flower)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def update_flower_info(self, flower_id: str, update_fields: Dict[str, Any]) -> bool:
        """꽃 정보 업데이트"""
        if flower_id not in self.dictionary_data["flowers"]:
            return False
        
        flower_data = self.dictionary_data["flowers"][flower_id]
        
        # 중첩된 키 처리 (예: "flower_meanings.primary")
        for key, value in update_fields.items():
            if "." in key:
                # 중첩된 키 처리
                parts = key.split(".")
                current = flower_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                # 일반 키 처리
                flower_data[key] = value
        
        flower_data["updated_at"] = datetime.now().isoformat()
        
        self._save_dictionary()
        return True
    
    def create_flower_entry(self, flower_data: Dict[str, Any]) -> str:
        """새로운 꽃 항목 생성"""
        flower_id = self.generate_flower_id(flower_data["scientific_name"], flower_data["color"])
        
        if flower_id in self.dictionary_data["flowers"]:
            raise ValueError(f"꽃 ID {flower_id}가 이미 존재합니다")
        
        flower_data["id"] = flower_id
        flower_data["created_at"] = datetime.now().isoformat()
        flower_data["updated_at"] = datetime.now().isoformat()
        
        self.dictionary_data["flowers"][flower_id] = flower_data
        self.dictionary_data["metadata"]["total_count"] = len(self.dictionary_data["flowers"])
        self.dictionary_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._save_dictionary()
        return flower_id
    
    def delete_flower_entry(self, flower_id: str) -> bool:
        """꽃 항목 삭제"""
        if flower_id not in self.dictionary_data["flowers"]:
            return False
        
        del self.dictionary_data["flowers"][flower_id]
        self.dictionary_data["metadata"]["total_count"] = len(self.dictionary_data["flowers"])
        self.dictionary_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._save_dictionary()
        return True
    
    def get_all_flowers(self) -> List[FlowerDictionary]:
        """모든 꽃 정보 조회"""
        flowers = []
        for flower_id, flower_data in self.dictionary_data["flowers"].items():
            try:
                # 빈 데이터 체크
                if not flower_data or not isinstance(flower_data, dict):
                    print(f"⚠️ 빈 데이터 건너뛰기: {flower_id}")
                    continue
                
                # 필수 필드가 있는지 확인
                required_fields = ['id', 'scientific_name', 'korean_name', 'color', 'flower_meanings', 'moods']
                missing_fields = [field for field in required_fields if field not in flower_data]
                
                if missing_fields:
                    print(f"⚠️ 필수 필드 누락된 꽃 데이터: {flower_id} (누락: {missing_fields})")
                    continue
                
                # 빈 값 체크
                if not flower_data['id'] or not flower_data['scientific_name'] or not flower_data['korean_name']:
                    print(f"⚠️ 빈 값이 있는 꽃 데이터: {flower_id}")
                    continue
                
                flower = FlowerDictionary(**flower_data)
                flowers.append(flower)
                print(f"✅ 꽃 데이터 로드 성공: {flower_id}")
                
            except Exception as e:
                print(f"❌ 꽃 데이터 파싱 실패 ({flower_id}): {e}")
                continue
        
        print(f"✅ 유효한 꽃 데이터: {len(flowers)}개")
        return flowers
    
    def get_metadata(self) -> Dict[str, Any]:
        """사전 메타데이터 조회"""
        return self.dictionary_data["metadata"]
