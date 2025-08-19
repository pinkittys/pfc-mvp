#!/usr/bin/env python3
"""
빠른 이미지 변환 스크립트
"""
import os
import shutil
from PIL import Image

def quick_convert():
    """새로운 색상 코드 파일들을 빠르게 변환"""
    
    # 색상 코드 매핑
    color_mapping = {
        "wh": "화이트", "iv": "아이보리", "be": "베이지",
        "yl": "옐로우", "or": "오렌지", "cr": "코랄",
        "pk": "핑크", "rd": "레드", "ll": "라일락",
        "pu": "퍼플", "bl": "블루", "gn": "그린"
    }
    
    source_dir = "data/images_raw"
    target_dir = "data/images_webp"
    
    # 새로운 색상 코드 파일들만 찾기
    new_files = []
    for file in os.listdir(source_dir):
        if any(f"_{code}." in file for code in color_mapping.keys()):
            new_files.append(file)
    
    print(f"🎨 변환할 파일 {len(new_files)}개 발견")
    
    for file in new_files:
        # 색상 코드 추출
        color_code = None
        for code in color_mapping.keys():
            if f"_{code}." in file:
                color_code = code
                break
        
        if not color_code:
            continue
        
        # 꽃 이름 추출
        flower_name = file.replace(f"_{color_code}.", "").replace(f"_{color_code}.", "")
        flower_name = os.path.splitext(flower_name)[0]
        
        # 폴더명 생성
        folder_name = flower_name.lower().replace(" ", "-").replace("'", "")
        
        # 타겟 경로
        target_folder = os.path.join(target_dir, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        
        # WebP 파일명
        color_name = color_mapping[color_code]
        webp_filename = f"{color_name}.webp"
        webp_path = os.path.join(target_folder, webp_filename)
        
        # 원본 파일 경로
        source_path = os.path.join(source_dir, file)
        
        # 이미 존재하는지 확인
        if os.path.exists(webp_path):
            print(f"⚠️  이미 존재: {webp_path}")
            continue
        
        try:
            # 이미지 변환
            with Image.open(source_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(webp_path, 'WEBP', quality=85, optimize=True)
                print(f"✅ 변환 완료: {file} → {webp_path}")
                
        except Exception as e:
            print(f"❌ 변환 실패: {file} - {e}")

if __name__ == "__main__":
    quick_convert()


