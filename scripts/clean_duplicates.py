#!/usr/bin/env python3
"""
중복 색상명 파일들을 정리하는 스크립트
"""
import os
import hashlib

def get_file_hash(file_path):
    """파일의 MD5 해시 반환"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def clean_duplicate_colors():
    """중복 색상명 파일들을 정리"""
    
    target_dir = "data/images_webp"
    
    # 색상명 매핑 (중복 제거)
    color_mapping = {
        "화이트": "화이트",
        "흰색": "화이트",
        "옐로우": "옐로우", 
        "노랑": "옐로우",
        "라일락": "라일락",
        "라벤더": "라일락"
    }
    
    for folder in os.listdir(target_dir):
        folder_path = os.path.join(target_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        print(f"🔍 검사 중: {folder}")
        
        # 폴더 내 파일들의 해시와 색상명 매핑
        file_hashes = {}
        color_files = {}
        
        for file in os.listdir(folder_path):
            if not file.endswith('.webp'):
                continue
                
            file_path = os.path.join(folder_path, file)
            color_name = file.replace('.webp', '')
            
            # 파일 해시 계산
            file_hash = get_file_hash(file_path)
            
            # 해시별 파일 그룹핑
            if file_hash not in file_hashes:
                file_hashes[file_hash] = []
            file_hashes[file_hash].append((file_path, color_name))
            
            # 색상명별 파일 그룹핑
            if color_name not in color_files:
                color_files[color_name] = []
            color_files[color_name].append(file_path)
        
        # 중복 파일 처리
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                print(f"  🔄 중복 파일 발견: {[f[1] for f in files]}")
                
                # 첫 번째 파일만 남기고 나머지 삭제
                keep_file = files[0]
                for file_path, color_name in files[1:]:
                    print(f"    삭제: {color_name}")
                    os.remove(file_path)
        
        # 중복 색상명 처리
        for color_name, files in color_files.items():
            if len(files) > 1:
                print(f"  🔄 중복 색상명 발견: {color_name} ({len(files)}개)")
                
                # 첫 번째 파일만 남기고 나머지 삭제
                for file_path in files[1:]:
                    print(f"    삭제: {os.path.basename(file_path)}")
                    os.remove(file_path)

if __name__ == "__main__":
    clean_duplicate_colors()


