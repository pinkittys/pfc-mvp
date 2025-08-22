#!/usr/bin/env python3
"""
새로운 데이터만 Supabase에 추가하는 스크립트
기존 데이터는 유지하고 새로운 데이터만 추가
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/add_new_data.log'),
        logging.StreamHandler()
    ]
)

class AddNewDataOnly:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수가 필요합니다")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
    
    def get_existing_flower_ids(self) -> set:
        """기존 꽃 ID 목록 가져오기"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/flower_catalog?select=flower_id",
                headers=self.headers
            )
            
            if response.status_code == 200:
                existing_ids = {item['flower_id'] for item in response.json()}
                logging.info(f"기존 꽃 ID {len(existing_ids)}개 발견")
                return existing_ids
            else:
                logging.warning(f"기존 꽃 ID 조회 실패: {response.status_code}")
                return set()
                
        except Exception as e:
            logging.error(f"기존 꽃 ID 조회 오류: {e}")
            return set()
    
    def add_new_flowers(self) -> bool:
        """새로운 꽃만 추가"""
        try:
            logging.info("🔄 새로운 꽃 데이터 추가 시작...")
            
            # 기존 꽃 ID 목록 가져오기
            existing_ids = self.get_existing_flower_ids()
            
            # flower_dictionary.json 로드
            flower_dict_path = Path("data/flower_dictionary.json")
            if not flower_dict_path.exists():
                logging.error("flower_dictionary.json 파일이 없습니다")
                return False
            
            with open(flower_dict_path, 'r', encoding='utf-8') as f:
                flower_data = json.load(f)
            
            added_count = 0
            skipped_count = 0
            
            for flower_id, flower_info in flower_data.items():
                if flower_id in existing_ids:
                    skipped_count += 1
                    continue
                
                catalog_data = {
                    "flower_id": flower_id,
                    "name_ko": flower_info.get("korean_name", ""),
                    "name_en": flower_info.get("flower_name", ""),
                    "scientific_name": flower_info.get("scientific_name", ""),
                    "color_code": flower_info.get("color", ""),
                    "season_months": flower_info.get("season", ""),
                    "moods": json.dumps(flower_info.get("moods", {}), ensure_ascii=False),
                    "emotions": json.dumps(flower_info.get("emotions", {}), ensure_ascii=False),
                    "contexts": json.dumps(flower_info.get("contexts", {}), ensure_ascii=False),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/flower_catalog",
                    headers=self.headers,
                    json=catalog_data
                )
                
                if response.status_code == 201:
                    logging.info(f"✅ 새로운 꽃 추가: {flower_id}")
                    added_count += 1
                else:
                    logging.warning(f"⚠️ 꽃 추가 실패 ({flower_id}): {response.status_code}")
            
            logging.info(f"🎉 꽃 데이터 추가 완료: {added_count}개 추가, {skipped_count}개 스킵")
            return True
            
        except Exception as e:
            logging.error(f"꽃 데이터 추가 실패: {e}")
            return False
    
    def get_existing_image_ids(self) -> set:
        """기존 이미지 ID 목록 가져오기"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/flower_images?select=flower_id,color",
                headers=self.headers
            )
            
            if response.status_code == 200:
                existing_ids = {f"{item['flower_id']}-{item['color']}" for item in response.json()}
                logging.info(f"기존 이미지 ID {len(existing_ids)}개 발견")
                return existing_ids
            else:
                logging.warning(f"기존 이미지 ID 조회 실패: {response.status_code}")
                return set()
                
        except Exception as e:
            logging.error(f"기존 이미지 ID 조회 오류: {e}")
            return set()
    
    def add_new_images(self) -> bool:
        """새로운 이미지만 추가"""
        try:
            logging.info("🔄 새로운 이미지 데이터 추가 시작...")
            
            # 기존 이미지 ID 목록 가져오기
            existing_ids = self.get_existing_image_ids()
            
            # base64_images.json 로드
            images_path = Path("base64_images.json")
            if not images_path.exists():
                logging.info("base64_images.json 파일이 없습니다. 스킵합니다.")
                return True
            
            with open(images_path, 'r', encoding='utf-8') as f:
                images_data = json.load(f)
            
            added_count = 0
            skipped_count = 0
            
            for flower_id, color_data in images_data.items():
                for color, base64_data in color_data.items():
                    image_key = f"{flower_id}-{color}"
                    
                    if image_key in existing_ids:
                        skipped_count += 1
                        continue
                    
                    image_data = {
                        "flower_id": flower_id,
                        "color": color,
                        "image_data": base64_data,
                        "image_url": "",
                        "created_at": datetime.now().isoformat()
                    }
                
                    response = requests.post(
                        f"{self.supabase_url}/rest/v1/flower_images",
                        headers=self.headers,
                        json=image_data
                    )
                
                    if response.status_code == 201:
                        logging.info(f"✅ 새로운 이미지 추가: {image_key}")
                        added_count += 1
                    else:
                        logging.warning(f"⚠️ 이미지 추가 실패 ({image_key}): {response.status_code}")
            
            logging.info(f"🎉 이미지 데이터 추가 완료: {added_count}개 추가, {skipped_count}개 스킵")
            return True
            
        except Exception as e:
            logging.error(f"이미지 데이터 추가 실패: {e}")
            return False
    
    def add_all_new_data(self) -> bool:
        """모든 새로운 데이터 추가"""
        logging.info("🚀 새로운 데이터만 추가 시작...")
        
        success = True
        
        # 1. 새로운 꽃 데이터 추가
        if not self.add_new_flowers():
            success = False
        
        # 2. 새로운 이미지 데이터 추가
        if not self.add_new_images():
            success = False
        
        if success:
            logging.info("🎉 새로운 데이터 추가 완료!")
        else:
            logging.error("❌ 새로운 데이터 추가 실패")
        
        return success

def main():
    """메인 실행 함수"""
    try:
        adder = AddNewDataOnly()
        success = adder.add_all_new_data()
        
        if success:
            print("✅ 새로운 데이터 추가 성공!")
        else:
            print("❌ 새로운 데이터 추가 실패")
            exit(1)
            
    except Exception as e:
        print(f"❌ 새로운 데이터 추가 오류: {e}")
        exit(1)

if __name__ == "__main__":
    main()
