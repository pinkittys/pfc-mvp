#!/usr/bin/env python3
"""
새로운 색상 코드 시스템으로 이미지를 변환하고 정리하는 스크립트
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

def get_color_from_filename(filename: str) -> Tuple[str, str]:
    """파일명에서 색상 코드와 색상명 추출"""
    filename_lower = filename.lower()
    
    # 색상 코드 찾기
    for code in COLOR_CODE_MAPPING.values():
        if code in filename_lower:
            color_name = CODE_TO_COLOR[code]
            return code, color_name
    
    # 색상명 직접 찾기
    for color_name in COLOR_CODE_MAPPING.keys():
        if color_name.lower() in filename_lower:
            code = COLOR_CODE_MAPPING[color_name]
            return code, color_name
    
    return None, None

def organize_flower_images(source_dir: str, target_dir: str = "data/images_webp"):
    """꽃 이미지를 정리하고 변환"""
    print(f"🌸 꽃 이미지 정리 및 변환 시작")
    print(f"📁 소스 디렉토리: {source_dir}")
    print(f"📁 타겟 디렉토리: {target_dir}")
    
    # 지원하는 이미지 확장자
    supported_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    
    # 소스 디렉토리에서 모든 파일 검색
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1]
            
            # 지원하는 이미지 파일만 처리
            if file_ext not in supported_extensions:
                continue
            
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
                print(f"📁 저장: {webp_path}")

def update_flower_matcher_code():
    """flower_matcher.py의 색상 매핑을 새로운 코드 시스템으로 업데이트"""
    print("\n🔧 flower_matcher.py 코드 업데이트 가이드:")
    print("""
# app/services/flower_matcher.py의 _get_flower_color_mapping 메서드에서:

# 기본 색상 매핑 업데이트
base_mapping = {
    "화이트": "화이트", "white": "화이트", "흰색": "화이트",
    "아이보리": "아이보리", "ivory": "아이보리", "iv": "아이보리",
    "베이지": "베이지", "beige": "베이지", "be": "베이지",
    "옐로우": "옐로우", "yellow": "옐로우", "yl": "옐로우",
    "오렌지": "오렌지", "orange": "오렌지", "or": "오렌지",
    "코랄": "코랄", "coral": "코랄", "cr": "코랄",
    "핑크": "핑크", "pink": "핑크", "pk": "핑크",
    "레드": "레드", "red": "레드", "rd": "레드",
    "라일락": "라일락", "lilac": "라일락", "ll": "라일락",
    "퍼플": "퍼플", "purple": "퍼플", "pu": "퍼플",
    "블루": "블루", "blue": "블루", "bl": "블루",
    "그린": "그린", "green": "그린", "gn": "그린"
}

# available_colors 딕셔너리 업데이트 (실제 파일에 맞게)
available_colors = {
    "flower-name": ["화이트", "아이보리", "베이지", "옐로우", "오렌지", "코랄", "핑크", "레드", "라일락", "퍼플", "블루", "그린"]
}
    """)

def create_color_mapping_script():
    """새로운 색상 매핑을 자동으로 생성하는 스크립트"""
    script_content = f'''#!/usr/bin/env python3
"""
새로운 색상 코드 시스템 매핑
"""
COLOR_CODE_MAPPING = {COLOR_CODE_MAPPING}

CODE_TO_COLOR = {CODE_TO_COLOR}

def get_color_from_code(code: str) -> str:
    """색상 코드를 색상명으로 변환"""
    return CODE_TO_COLOR.get(code.lower(), "화이트")

def get_code_from_color(color: str) -> str:
    """색상명을 색상 코드로 변환"""
    return COLOR_CODE_MAPPING.get(color, "wh")

def get_available_colors_for_flower(flower_folder: str) -> List[str]:
    """꽃 폴더에서 사용 가능한 색상 목록 반환"""
    import os
    flower_path = f"data/images_webp/{{flower_folder}}"
    if not os.path.exists(flower_path):
        return []
    
    colors = []
    for file in os.listdir(flower_path):
        if file.endswith('.webp'):
            color_name = file.replace('.webp', '')
            colors.append(color_name)
    
    return colors
'''
    
    with open("app/utils/color_mapping.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✅ 색상 매핑 유틸리티 생성: app/utils/color_mapping.py")

def main():
    """메인 함수"""
    print("🎨 새로운 색상 코드 시스템 이미지 변환 도구")
    print("=" * 50)
    
    # 1. 색상 매핑 정보 출력
    print("📋 색상 코드 매핑:")
    for color, code in COLOR_CODE_MAPPING.items():
        print(f"  {color} → {code}")
    
    # 2. 사용자 입력 받기
    source_dir = input("\n📁 변환할 이미지가 있는 디렉토리 경로를 입력하세요: ").strip()
    
    if not os.path.exists(source_dir):
        print(f"❌ 디렉토리가 존재하지 않습니다: {source_dir}")
        return
    
    # 3. 이미지 변환 및 정리
    organize_flower_images(source_dir)
    
    # 4. 색상 매핑 유틸리티 생성
    create_color_mapping_script()
    
    # 5. 코드 업데이트 가이드 출력
    update_flower_matcher_code()
    
    print("\n✅ 변환 완료!")
    print("📝 다음 단계:")
    print("1. flower_matcher.py의 색상 매핑을 업데이트하세요")
    print("2. 새로운 꽃들을 flower_database에 추가하세요")
    print("3. 서버를 재시작하세요")

if __name__ == "__main__":
    main()


