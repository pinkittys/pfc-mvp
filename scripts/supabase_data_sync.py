#!/usr/bin/env python3
"""
Supabase 데이터 동기화 스크립트
구글 스프레드시트와 로컬 데이터를 Supabase에 자동 동기화
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
        logging.FileHandler('logs/supabase_sync.log'),
        logging.StreamHandler()
    ]
)

class SupabaseDataSync:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수가 필요합니다")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        self.service_headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json'
        }
    
    def sync_flower_catalog(self) -> bool:
        """꽃 카탈로그 동기화"""
        try:
            logging.info("🔄 꽃 카탈로그 동기화 시작...")
            
            # flower_dictionary.json 로드
            flower_dict_path = Path("data/flower_dictionary.json")
            if not flower_dict_path.exists():
                logging.error("flower_dictionary.json 파일이 없습니다")
                return False
            
            with open(flower_dict_path, 'r', encoding='utf-8') as f:
                flower_data = json.load(f)
            
            # 기존 데이터 삭제 (전체 교체)
            logging.info("기존 꽃 카탈로그 데이터 삭제 중...")
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/flower_catalog",
                headers=self.service_headers
            )
            
            if response.status_code not in [200, 204]:
                logging.warning(f"기존 데이터 삭제 실패: {response.status_code}")
            
            # 새 데이터 삽입
            logging.info(f"새로운 꽃 카탈로그 데이터 {len(flower_data)}개 삽입 중...")
            
            for flower_id, flower_info in flower_data.items():
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
                
                if response.status_code != 201:
                    logging.error(f"꽃 카탈로그 삽입 실패 ({flower_id}): {response.status_code}")
                    return False
            
            logging.info("✅ 꽃 카탈로그 동기화 완료")
            return True
            
        except Exception as e:
            logging.error(f"꽃 카탈로그 동기화 실패: {e}")
            return False
    
    def sync_stories(self) -> bool:
        """스토리 데이터 동기화"""
        try:
            logging.info("🔄 스토리 데이터 동기화 시작...")
            
            # stories.json 로드
            stories_path = Path("data/stories.json")
            if not stories_path.exists():
                logging.info("stories.json 파일이 없습니다. 스킵합니다.")
                return True
            
            with open(stories_path, 'r', encoding='utf-8') as f:
                stories_data = json.load(f)
            
            # 기존 데이터 삭제 (전체 교체)
            logging.info("기존 스토리 데이터 삭제 중...")
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/stories",
                headers=self.service_headers
            )
            
            if response.status_code not in [200, 204]:
                logging.warning(f"기존 스토리 데이터 삭제 실패: {response.status_code}")
            
            # 새 데이터 삽입
            logging.info(f"새로운 스토리 데이터 {len(stories_data)}개 삽입 중...")
            
            for story_id, story_info in stories_data.items():
                story_data = {
                    "story_id": story_id,
                    "story": story_info.get("original_story", ""),
                    "emotions": json.dumps(story_info.get("emotions", []), ensure_ascii=False),
                    "matched_flower": json.dumps(story_info.get("matched_flower", {}), ensure_ascii=False),
                    "composition": json.dumps(story_info.get("flower_blend", {}), ensure_ascii=False),
                    "recommendation_reason": story_info.get("recommendation_reason", ""),
                    "flower_card_message": story_info.get("flower_card_message", ""),
                    "season_info": story_info.get("season_info", ""),
                    "keywords": json.dumps(story_info.get("keywords", []), ensure_ascii=False),
                    "hashtags": json.dumps(story_info.get("hashtags", []), ensure_ascii=False),
                    "color_keywords": json.dumps(story_info.get("color_keywords", []), ensure_ascii=False),
                    "excluded_keywords": json.dumps(story_info.get("excluded_keywords", []), ensure_ascii=False),
                    "created_at": story_info.get("created_at", datetime.now().isoformat())
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/stories",
                    headers=self.headers,
                    json=story_data
                )
                
                if response.status_code != 201:
                    logging.error(f"스토리 삽입 실패 ({story_id}): {response.status_code}")
                    return False
            
            logging.info("✅ 스토리 데이터 동기화 완료")
            return True
            
        except Exception as e:
            logging.error(f"스토리 데이터 동기화 실패: {e}")
            return False
    
    def sync_flower_images(self) -> bool:
        """꽃 이미지 데이터 동기화"""
        try:
            logging.info("🔄 꽃 이미지 데이터 동기화 시작...")
            
            # base64_images.json 로드
            images_path = Path("base64_images.json")
            if not images_path.exists():
                logging.info("base64_images.json 파일이 없습니다. 스킵합니다.")
                return True
            
            with open(images_path, 'r', encoding='utf-8') as f:
                images_data = json.load(f)
            
            # 기존 데이터 삭제 (전체 교체)
            logging.info("기존 꽃 이미지 데이터 삭제 중...")
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/flower_images",
                headers=self.service_headers
            )
            
            if response.status_code not in [200, 204]:
                logging.warning(f"기존 이미지 데이터 삭제 실패: {response.status_code}")
            
            # 새 데이터 삽입
            logging.info(f"새로운 꽃 이미지 데이터 {len(images_data)}개 삽입 중...")
            
            for flower_id, color_data in images_data.items():
                for color, base64_data in color_data.items():
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
                
                if response.status_code != 201:
                    logging.error(f"이미지 삽입 실패 ({flower_id}-{color}): {response.status_code}")
                    return False
            
            logging.info("✅ 꽃 이미지 데이터 동기화 완료")
            return True
            
        except Exception as e:
            logging.error(f"꽃 이미지 데이터 동기화 실패: {e}")
            return False
    
    def sync_all(self) -> bool:
        """전체 데이터 동기화"""
        logging.info("🚀 Supabase 전체 데이터 동기화 시작...")
        
        success = True
        
        # 1. 꽃 카탈로그 동기화
        if not self.sync_flower_catalog():
            success = False
        
        # 2. 스토리 데이터 동기화
        if not self.sync_stories():
            success = False
        
        # 3. 꽃 이미지 데이터 동기화
        if not self.sync_flower_images():
            success = False
        
        if success:
            logging.info("🎉 Supabase 전체 데이터 동기화 완료!")
        else:
            logging.error("❌ Supabase 데이터 동기화 실패")
        
        return success

def main():
    """메인 실행 함수"""
    try:
        syncer = SupabaseDataSync()
        success = syncer.sync_all()
        
        if success:
            print("✅ Supabase 데이터 동기화 성공!")
        else:
            print("❌ Supabase 데이터 동기화 실패")
            exit(1)
            
    except Exception as e:
        print(f"❌ Supabase 동기화 오류: {e}")
        exit(1)

if __name__ == "__main__":
    main()
