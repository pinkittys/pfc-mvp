#!/usr/bin/env python3
"""
중복 제거 기능이 포함된 이미지 변환 및 정리 스크립트
"""
import os
import shutil
import hashlib
from PIL import Image
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# 색상 코드 매핑
COLOR_CODE_MAPPING = {
    "화이트": "wh",
    "아이보리": "iv", 
    "베이지": "be",
    "옐로우": "yl",
    "오렌지": "or",
    "코랄": "cr",
    "핑크": "pk",
    "레드": "rd",
    "라일락": "ll",
    "퍼플": "pu",
    "블루": "bl",
    "그린": "gn"
}

# 역방향 매핑 (코드 → 색상명)
CODE_TO_COLOR = {v: k for k, v in COLOR_CODE_MAPPING.items()}

def calculate_image_hash(image_path: str) -> str:
    """이미지의 해시값을 계산하여 중복 확인"""
    try:
        with Image.open(image_path) as img:
            # 이미지를 작은 크기로 리사이즈하여 해시 계산
            img_small = img.resize((8, 8), Image.Resampling.LANCZOS)
            img_gray = img_small.convert('L')
            pixels = list(img_gray.getdata())
            
            # 평균 픽셀값 계산
            avg = sum(pixels) / len(pixels)
            
            # 각 픽셀이 평균보다 큰지 작은지로 해시 생성
            bits = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
            
            # 16진수로 변환
            hash_hex = hex(int(bits, 2))[2:].zfill(16)
            return hash_hex
    except Exception as e:
        print(f"❌ 해시 계산 실패: {image_path} - {e}")
        return None

def convert_image_to_webp(input_path: str, output_path: str, quality: int = 85):
    """이미지를 WebP 형식으로 변환"""
    try:
        with Image.open(input_path) as img:
            # RGBA 모드인 경우 RGB로 변환
            if img.mode in ('RGBA', 'LA'):
                # 흰색 배경으로 합성
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # 알파 채널을 마스크로 사용
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # WebP로 저장
            img.save(output_path, 'WEBP', quality=quality, optimize=True)
            print(f"✅ 변환 완료: {input_path} → {output_path}")
            return True
    except Exception as e:
        print(f"❌ 변환 실패: {input_path} - {e}")
        return False

def get_color_from_filename(filename: str) -> Tuple[str, str]:
    """파일명에서 색상 코드와 색상명 추출"""
    filename_lower = filename.lower()
    
    # 한글 색상명 매핑 추가
    korean_color_mapping = {
        "화이트": "화이트", "흰색": "화이트", "하얀색": "화이트",
        "아이보리": "아이보리", 
        "베이지": "베이지",
        "옐로우": "옐로우", "노랑": "옐로우", "노란색": "옐로우", "노랑색": "옐로우",
        "오렌지": "오렌지", "주황": "오렌지", "주황색": "오렌지",
        "코랄": "코랄",
        "핑크": "핑크", "분홍": "핑크", "분홍색": "핑크",
        "레드": "레드", "빨강": "레드", "빨간색": "레드", "빨강색": "레드",
        "라일락": "라일락", "라벤더": "라일락",
        "퍼플": "퍼플", "보라": "퍼플", "보라색": "퍼플",
        "블루": "블루", "파랑": "블루", "파란색": "블루", "파랑색": "블루",
        "그린": "그린", "초록": "그린", "초록색": "그린", "녹색": "그린"
    }
    
    # 색상 코드 찾기
    for code in COLOR_CODE_MAPPING.values():
        if code in filename_lower:
            color_name = CODE_TO_COLOR[code]
            return code, color_name
    
    # 색상명 직접 찾기 (영어)
    for color_name in COLOR_CODE_MAPPING.keys():
        if color_name.lower() in filename_lower:
            code = COLOR_CODE_MAPPING[color_name]
            return code, color_name
    
    # 한글 색상명 찾기
    for korean_name, standard_name in korean_color_mapping.items():
        if korean_name in filename:
            code = COLOR_CODE_MAPPING[standard_name]
            return code, standard_name
    
    return None, None

def find_duplicate_images(source_dir: str) -> Dict[str, List[str]]:
    """중복 이미지 찾기"""
    print("🔍 중복 이미지 검사 중...")
    
    hash_to_files = defaultdict(list)
    supported_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    
    # 모든 이미지 파일의 해시 계산
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext not in supported_extensions:
                continue
            
            file_path = os.path.join(root, file)
            image_hash = calculate_image_hash(file_path)
            
            if image_hash:
                hash_to_files[image_hash].append(file_path)
    
    # 중복된 이미지만 반환
    duplicates = {hash_val: files for hash_val, files in hash_to_files.items() if len(files) > 1}
    
    print(f"📊 중복 이미지 그룹 수: {len(duplicates)}")
    for hash_val, files in duplicates.items():
        print(f"  🔄 중복 그룹 ({len(files)}개):")
        for file in files:
            print(f"    - {os.path.basename(file)}")
    
    return duplicates

def organize_flower_images_with_deduplication(source_dir: str, target_dir: str = "data/images_webp"):
    """중복 제거 후 꽃 이미지를 정리하고 변환"""
    print(f"🌸 꽃 이미지 정리 및 변환 (중복 제거 포함)")
    print(f"📁 소스 디렉토리: {source_dir}")
    print(f"📁 타겟 디렉토리: {target_dir}")
    
    # 1. 중복 이미지 찾기
    duplicates = find_duplicate_images(source_dir)
    
    # 2. 중복 제거 후 변환할 파일 목록 생성
    processed_hashes = set()
    files_to_convert = []
    
    supported_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext not in supported_extensions:
                continue
            
            file_path = os.path.join(root, file)
            image_hash = calculate_image_hash(file_path)
            
            if not image_hash:
                continue
            
            # 중복된 이미지인 경우 첫 번째만 처리
            if image_hash in duplicates:
                if image_hash not in processed_hashes:
                    files_to_convert.append(file_path)
                    processed_hashes.add(image_hash)
                    print(f"🔄 중복 제거: {os.path.basename(file_path)} (대표 파일로 선택)")
            else:
                # 중복되지 않은 이미지는 그대로 처리
                files_to_convert.append(file_path)
    
    print(f"📊 변환할 파일 수: {len(files_to_convert)}")
    
    # 3. 이미지 변환 및 정리
    converted_count = 0
    for file_path in files_to_convert:
        file = os.path.basename(file_path)
        
        # 파일명에서 색상 코드와 색상명 추출
        color_code, color_name = get_color_from_filename(file)
        
        if not color_code or not color_name:
            print(f"⚠️  색상 정보를 찾을 수 없음: {file}")
            continue
        
        # 꽃 이름 추출 (파일명에서 색상 코드 제거)
        flower_name = file.replace(f"_{color_code}", "").replace(f"-{color_code}", "")
        flower_name = os.path.splitext(flower_name)[0]  # 확장자 제거
        
        # 꽃 이름 정규화 (폴더명으로 사용)
        flower_folder = flower_name.lower().replace(" ", "-").replace("_", "-")
        
        # 타겟 디렉토리 생성
        target_flower_dir = os.path.join(target_dir, flower_folder)
        os.makedirs(target_flower_dir, exist_ok=True)
        
        # WebP 파일명 생성
        webp_filename = f"{color_name}.webp"
        webp_path = os.path.join(target_flower_dir, webp_filename)
        
        # 이미지 변환
        if convert_image_to_webp(file_path, webp_path):
            converted_count += 1
    
    print(f"✅ 변환 완료: {converted_count}개 파일")
    return converted_count

def main():
    """메인 함수"""
    print("🎨 중복 제거 이미지 변환 도구")
    print("=" * 50)
    
    # 1. 색상 매핑 정보 출력
    print("📋 색상 코드 매핑:")
    for color, code in COLOR_CODE_MAPPING.items():
        print(f"  {color} → {code}")
    
    # 2. 사용자 입력 받기
    source_dir = input("\n📁 변환할 이미지가 있는 디렉토리 경로를 입력하세요 (기본: data/images_raw): ").strip()
    
    if not source_dir:
        source_dir = "data/images_raw"
    
    if not os.path.exists(source_dir):
        print(f"❌ 디렉토리가 존재하지 않습니다: {source_dir}")
        return
    
    # 3. 이미지 변환 및 정리 (중복 제거 포함)
    converted_count = organize_flower_images_with_deduplication(source_dir)
    
    print(f"\n✅ 변환 완료! 총 {converted_count}개 파일이 변환되었습니다.")
    print("📝 다음 단계:")
    print("1. 새로운 꽃들을 flower_database에 추가하세요")
    print("2. base64_images.json을 업데이트하세요")
    print("3. 서버를 재시작하세요")

if __name__ == "__main__":
    main()
