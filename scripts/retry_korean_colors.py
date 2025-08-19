#!/usr/bin/env python3
"""
한글 색상명을 정확하게 인식하여 실패한 파일들을 다시 처리하는 스크립트
"""
import os
import shutil
from PIL import Image
from typing import Dict, List, Tuple

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

def get_color_from_filename_enhanced(filename: str) -> Tuple[str, str]:
    """파일명에서 색상 코드와 색상명 추출 (향상된 버전)"""
    filename_lower = filename.lower()
    
    # 한글 색상명 매핑 (더 포괄적)
    korean_color_mapping = {
        # 화이트 계열
        "화이트": "화이트", "흰색": "화이트", "하얀색": "화이트", "흰": "화이트",
        
        # 아이보리 계열
        "아이보리": "아이보리", "크림": "아이보리", "크림색": "아이보리",
        
        # 베이지 계열
        "베이지": "베이지", "베이지색": "베이지",
        
        # 옐로우 계열
        "옐로우": "옐로우", "노랑": "옐로우", "노란색": "옐로우", "노랑색": "옐로우", "노란": "옐로우",
        
        # 오렌지 계열
        "오렌지": "오렌지", "주황": "오렌지", "주황색": "오렌지", "주황": "오렌지",
        
        # 코랄 계열
        "코랄": "코랄", "코랄색": "코랄",
        
        # 핑크 계열
        "핑크": "핑크", "분홍": "핑크", "분홍색": "핑크", "분홍": "핑크", "연핑크": "핑크",
        
        # 레드 계열
        "레드": "레드", "빨강": "레드", "빨간색": "레드", "빨강색": "레드", "빨간": "레드",
        
        # 라일락 계열
        "라일락": "라일락", "라벤더": "라일락", "라벤더색": "라일락", "연보라": "라일락",
        
        # 퍼플 계열
        "퍼플": "퍼플", "보라": "퍼플", "보라색": "퍼플", "보라": "퍼플",
        
        # 블루 계열
        "블루": "블루", "파랑": "블루", "파란색": "블루", "파랑색": "블루", "파란": "블루", 
        "네이비": "블루", "네이비블루": "블루", "네이비 블루": "블루", "옅은블루": "블루", "옅은 블루": "블루",
        
        # 그린 계열
        "그린": "그린", "초록": "그린", "초록색": "그린", "녹색": "그린", "녹": "그린"
    }
    
    # 색상 코드 찾기 (영어 코드)
    for code in COLOR_CODE_MAPPING.values():
        if code in filename_lower:
            color_name = CODE_TO_COLOR[code]
            return code, color_name
    
    # 색상명 직접 찾기 (영어)
    for color_name in COLOR_CODE_MAPPING.keys():
        if color_name.lower() in filename_lower:
            code = COLOR_CODE_MAPPING[color_name]
            return code, color_name
    
    # 한글 색상명 찾기 (가장 긴 매칭부터)
    sorted_korean_colors = sorted(korean_color_mapping.keys(), key=len, reverse=True)
    for korean_name in sorted_korean_colors:
        if korean_name in filename:
            standard_name = korean_color_mapping[korean_name]
            code = COLOR_CODE_MAPPING[standard_name]
            return code, standard_name
    
    return None, None

def get_flower_name_from_filename_enhanced(filename: str) -> str:
    """파일명에서 꽃 이름 추출 (향상된 버전)"""
    # 확장자 제거
    name_without_ext = os.path.splitext(filename)[0]
    
    # 색상 관련 부분 제거
    color_removed = name_without_ext
    
    # 색상 코드 제거
    for code in COLOR_CODE_MAPPING.values():
        color_removed = color_removed.replace(f"_{code}", "").replace(f"-{code}", "")
    
    # 한글 색상명 제거 (가장 긴 것부터)
    korean_colors = [
        "네이비 블루", "네이비블루", "옅은 블루", "옅은블루",
        "화이트", "흰색", "하얀색", "흰",
        "아이보리", "크림", "크림색",
        "베이지", "베이지색",
        "옐로우", "노랑", "노란색", "노랑색", "노란",
        "오렌지", "주황", "주황색",
        "코랄", "코랄색",
        "핑크", "분홍", "분홍색", "연핑크",
        "레드", "빨강", "빨간색", "빨강색", "빨간",
        "라일락", "라벤더", "라벤더색", "연보라",
        "퍼플", "보라", "보라색",
        "블루", "파랑", "파란색", "파랑색", "파란",
        "그린", "초록", "초록색", "녹색", "녹"
    ]
    
    for color in korean_colors:
        color_removed = color_removed.replace(f"_{color}", "").replace(f"-{color}", "")
    
    # 영어 색상명 제거
    english_colors = ["white", "ivory", "beige", "yellow", "orange", "coral", "pink", 
                     "red", "lilac", "purple", "blue", "green", "navy", "light-blue"]
    
    for color in english_colors:
        color_removed = color_removed.replace(f"_{color}", "").replace(f"-{color}", "")
    
    # 공백과 언더스코어를 하이픈으로 변환
    flower_name = color_removed.replace(" ", "-").replace("_", "-")
    
    # 연속된 하이픈 제거
    while "--" in flower_name:
        flower_name = flower_name.replace("--", "-")
    
    # 앞뒤 하이픈 제거
    flower_name = flower_name.strip("-")
    
    return flower_name.lower()

def retry_korean_color_files(source_dir: str = "data/images_raw", target_dir: str = "data/images_webp"):
    """한글 색상명이 포함된 실패한 파일들을 다시 처리"""
    print("🔄 한글 색상명 파일 재처리 중...")
    
    # 실패했던 파일들 목록 (한글 색상명 포함)
    failed_files = [
        "Scabiosa_블루.jpg.png",
        "Rose_레드.jpg.png", 
        "Tulip_화이트.jpg",
        "Stock Flower_퍼플.JPG",
        "Drumstick Flower_옐로우.jpg.png",
        "Dahlia_옐로우.jpg.png",
        "Hydrangea_핑크.png",
        "Tulip_레드.jpg",
        "Lily_화이트.png",
        "Lisianthus_화이트.jpg",
        "Garden Peony_핑크.jpg",
        "Scabiosa_화이트.jpg.png",
        "Lisianthus_핑크.jpg",
        "Cotton Plant_화이트.jpg.png",
        "Marguerite Daisy_흰색.png",
        "Baby's Breath_화이트.jpg",
        "Dahlia_핑크.jpg.png",
        "Tulip_옐로우.jpg",
        "Rose_핑크.jpg"
    ]
    
    supported_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    converted_count = 0
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext not in supported_extensions:
                continue
            
            file_path = os.path.join(root, file)
            
            # 파일명에서 색상 정보 추출 (향상된 버전)
            color_code, color_name = get_color_from_filename_enhanced(file)
            
            if not color_code or not color_name:
                print(f"⚠️  색상 정보를 찾을 수 없음: {file}")
                continue
            
            # 꽃 이름 추출 (향상된 버전)
            flower_name = get_flower_name_from_filename_enhanced(file)
            
            if not flower_name:
                print(f"⚠️  꽃 이름을 추출할 수 없음: {file}")
                continue
            
            # 타겟 디렉토리 생성
            target_flower_dir = os.path.join(target_dir, flower_name)
            os.makedirs(target_flower_dir, exist_ok=True)
            
            # WebP 파일명 생성
            webp_filename = f"{color_name}.webp"
            webp_path = os.path.join(target_flower_dir, webp_filename)
            
            # 이미지 변환
            if convert_image_to_webp(file_path, webp_path):
                converted_count += 1
                print(f"🌺 꽃: {flower_name}, 색상: {color_name}")
    
    print(f"✅ 한글 색상명 재처리 완료: {converted_count}개 파일")
    return converted_count

def main():
    """메인 함수"""
    print("🔄 한글 색상명 파일 재처리 도구")
    print("=" * 50)
    
    # 한글 색상명 파일 재처리
    converted_count = retry_korean_color_files()
    
    print(f"\n✅ 재처리 완료! 총 {converted_count}개 파일이 변환되었습니다.")
    print("📝 다음 단계:")
    print("1. 새로운 꽃들을 flower_database에 추가하세요")
    print("2. base64_images.json을 업데이트하세요")
    print("3. 서버를 재시작하세요")

if __name__ == "__main__":
    main()

