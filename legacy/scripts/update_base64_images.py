#!/usr/bin/env python3
"""
새로운 webp 이미지들을 base64로 변환하여 base64_images.json을 업데이트하는 스크립트
"""
import os
import json
import base64
from typing import Dict, List
from pathlib import Path

def encode_image_to_base64(image_path: str) -> str:
    """이미지를 base64로 인코딩"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"❌ Base64 인코딩 실패: {image_path} - {e}")
        return None

def get_flower_images(flower_dir: str) -> Dict[str, str]:
    """꽃 폴더의 모든 이미지를 base64로 변환"""
    flower_images = {}
    
    if not os.path.exists(flower_dir):
        print(f"⚠️  폴더가 존재하지 않음: {flower_dir}")
        return flower_images
    
    # webp 파일들 찾기
    for file in os.listdir(flower_dir):
        if file.endswith('.webp'):
            image_path = os.path.join(flower_dir, file)
            color_name = file.replace('.webp', '')
            
            # base64로 인코딩
            base64_data = encode_image_to_base64(image_path)
            if base64_data:
                flower_images[color_name] = base64_data
                print(f"✅ {os.path.basename(flower_dir)}/{file} → base64 변환 완료")
    
    return flower_images

def update_base64_images(webp_dir: str = "data/images_webp", output_file: str = "base64_images.json"):
    """모든 webp 이미지를 base64로 변환하여 JSON 파일 업데이트"""
    print("🔄 Base64 이미지 업데이트 시작...")
    
    # 기존 base64_images.json 로드
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"📁 기존 데이터 로드: {len(existing_data)}개 꽃")
        except Exception as e:
            print(f"⚠️  기존 파일 로드 실패: {e}")
    
    # 새로운 데이터 수집
    new_data = {}
    flower_count = 0
    total_images = 0
    
    # webp 디렉토리의 모든 꽃 폴더 처리
    for flower_folder in os.listdir(webp_dir):
        flower_path = os.path.join(webp_dir, flower_folder)
        
        if os.path.isdir(flower_path):
            # 꽃 이미지들을 base64로 변환
            flower_images = get_flower_images(flower_path)
            
            if flower_images:
                new_data[flower_folder] = flower_images
                flower_count += 1
                total_images += len(flower_images)
                print(f"🌺 {flower_folder}: {len(flower_images)}개 색상")
    
    # 기존 데이터와 새 데이터 병합
    merged_data = {**existing_data, **new_data}
    
    # JSON 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Base64 이미지 업데이트 완료!")
        print(f"📊 처리된 꽃: {flower_count}개")
        print(f"📊 총 이미지: {total_images}개")
        print(f"📊 전체 꽃: {len(merged_data)}개")
        print(f"💾 저장된 파일: {output_file}")
        
        return merged_data
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return None

def compare_with_flower_database():
    """꽃 데이터베이스와 비교하여 누락된 꽃 확인"""
    print("\n🔍 꽃 데이터베이스와 비교 중...")
    
    # flower_dictionary.json 로드
    try:
        with open("data/flower_dictionary.json", 'r', encoding='utf-8') as f:
            flower_db = json.load(f)
        
        # base64_images.json 로드
        with open("base64_images.json", 'r', encoding='utf-8') as f:
            base64_data = json.load(f)
        
        # 꽃 ID 추출
        flower_db_ids = set()
        for flower in flower_db:
            flower_id = flower.get('id', '')
            if flower_id:
                # 학명-색상 형식에서 학명만 추출
                flower_name = flower_id.split('-')[0].lower()
                flower_db_ids.add(flower_name)
        
        base64_ids = set(base64_data.keys())
        
        # 비교
        missing_in_base64 = flower_db_ids - base64_ids
        extra_in_base64 = base64_ids - flower_db_ids
        
        print(f"📊 꽃 데이터베이스: {len(flower_db_ids)}개")
        print(f"📊 Base64 이미지: {len(base64_ids)}개")
        
        if missing_in_base64:
            print(f"⚠️  Base64에 누락된 꽃: {len(missing_in_base64)}개")
            for flower in sorted(missing_in_base64):
                print(f"  - {flower}")
        
        if extra_in_base64:
            print(f"✅ Base64에만 있는 꽃: {len(extra_in_base64)}개")
            for flower in sorted(extra_in_base64):
                print(f"  - {flower}")
        
        if not missing_in_base64 and not extra_in_base64:
            print("🎉 완벽한 일치!")
            
    except Exception as e:
        print(f"❌ 비교 실패: {e}")

def main():
    """메인 함수"""
    print("🔄 Base64 이미지 업데이트 도구")
    print("=" * 50)
    
    # 1. webp 이미지들을 base64로 변환
    updated_data = update_base64_images()
    
    if updated_data:
        # 2. 꽃 데이터베이스와 비교
        compare_with_flower_database()
        
        print(f"\n✅ 업데이트 완료!")
        print("📝 다음 단계:")
        print("1. 서버를 재시작하세요")
        print("2. 새로운 꽃들로 매칭을 테스트해보세요")

if __name__ == "__main__":
    main()

