#!/usr/bin/env python3
"""
색상명을 통일하는 스크립트
"""
import os

def rename_color_files():
    """색상명을 통일된 이름으로 변경"""
    
    target_dir = "data/images_webp"
    
    # 색상명 매핑 (통일)
    color_mapping = {
        "흰색": "화이트",
        "노랑": "옐로우",
        "라벤더": "라일락"
    }
    
    for folder in os.listdir(target_dir):
        folder_path = os.path.join(target_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        print(f"🔍 검사 중: {folder}")
        
        for file in os.listdir(folder_path):
            if not file.endswith('.webp'):
                continue
                
            file_path = os.path.join(folder_path, file)
            color_name = file.replace('.webp', '')
            
            # 색상명 변경이 필요한지 확인
            if color_name in color_mapping:
                new_color_name = color_mapping[color_name]
                new_file = f"{new_color_name}.webp"
                new_file_path = os.path.join(folder_path, new_file)
                
                # 이미 같은 이름의 파일이 있는지 확인
                if os.path.exists(new_file_path):
                    print(f"  ⚠️  이미 존재: {new_file} (삭제: {file})")
                    os.remove(file_path)
                else:
                    print(f"  📝 이름 변경: {file} → {new_file}")
                    os.rename(file_path, new_file_path)

if __name__ == "__main__":
    rename_color_files()


