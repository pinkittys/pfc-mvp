#!/usr/bin/env python3
"""
잘못된 폴더명을 수정하는 스크립트
"""
import os
import shutil

def fix_folder_names():
    """잘못된 폴더명을 수정"""
    
    target_dir = "data/images_webp"
    
    # 폴더명 매핑
    folder_mapping = {
        "baby's-breathjpg": "babys-breath",
        "bouvardiajpg": "bouvardia",
        "cockscombjpg": "cockscomb",
        "cotton-plantjpg": "cotton-plant",
        "dahliajpg": "dahlia",
        "drumstick-flowerjpg": "drumstick-flower",
        "garden-peonyjpg": "garden-peony",
        "gerbera-daisyjpg": "gerbera-daisy",
        "gladiolusjpg": "gladiolus",
        "globe-amaranthjpg": "globe-amaranth",
        "hydrangeajpg": "hydrangea",
        "lilyjpg": "lily",
        "lisianthusjpg": "lisianthus",
        "marguerite-daisyjpg": "marguerite-daisy",
        "ranunculusjpg": "ranunculus",
        "rosejpg": "rose",
        "scabiosajpg": "scabiosa",
        "stock-flowerjpg": "stock-flower",
        "tulipjpg": "tulip",
        "ranunculuspng": "ranunculus"
    }
    
    for old_name, new_name in folder_mapping.items():
        old_path = os.path.join(target_dir, old_name)
        new_path = os.path.join(target_dir, new_name)
        
        if os.path.exists(old_path):
            # 기존 폴더가 있으면 파일들을 병합
            if os.path.exists(new_path):
                print(f"🔄 병합: {old_name} → {new_name}")
                # 기존 폴더의 파일들을 새 폴더로 이동
                for file in os.listdir(old_path):
                    old_file = os.path.join(old_path, file)
                    new_file = os.path.join(new_path, file)
                    if not os.path.exists(new_file):
                        shutil.move(old_file, new_file)
                    else:
                        os.remove(old_file)  # 중복 파일 삭제
                # 빈 폴더 삭제
                os.rmdir(old_path)
            else:
                print(f"📁 이름 변경: {old_name} → {new_name}")
                shutil.move(old_path, new_path)

if __name__ == "__main__":
    fix_folder_names()


