#!/usr/bin/env python3
"""
새로운 이미지들을 webp로 변환하는 스크립트
"""

import os
import subprocess
from pathlib import Path

def convert_to_webp(input_path, output_path, quality=85):
    """이미지를 webp로 변환"""
    try:
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # cwebp 명령어로 변환
        cmd = [
            'cwebp',
            '-q', str(quality),
            '-m', '6',  # 압축 메서드
            input_path,
            '-o', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 변환 완료: {input_path} → {output_path}")
            return True
        else:
            print(f"❌ 변환 실패: {input_path}")
            print(f"에러: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 변환 중 오류: {input_path} - {e}")
        return False

def get_color_from_filename(filename):
    """파일명에서 색상 추출"""
    filename_lower = filename.lower()
    
    # 색상 매핑
    color_mapping = {
        'wh': '화이트', 'white': '화이트', '흰색': '화이트',
        'rd': '레드', 'red': '레드', '빨강': '레드',
        'pk': '핑크', 'pink': '핑크', '분홍': '핑크',
        'yl': '옐로우', 'yellow': '옐로우', '노랑': '옐로우',
        'or': '오렌지', 'orange': '오렌지', '주황': '오렌지',
        'bl': '블루', 'blue': '블루', '파랑': '블루',
        'pu': '퍼플', 'purple': '퍼플', '보라': '퍼플',
        'gr': '그린', 'green': '그린', '초록': '그린',
        'iv': '아이보리', 'ivory': '아이보리',
        'be': '베이지', 'beige': '베이지'
    }
    
    for eng, kor in color_mapping.items():
        if eng in filename_lower or kor in filename_lower:
            return kor
    
    return None

def main():
    """메인 변환 함수"""
    raw_dir = Path("data/images_raw")
    webp_dir = Path("data/images_webp")
    
    # 변환할 이미지 목록
    images_to_convert = [
        # Rose (장미) - 오렌지 추가
        ("Rose_or.jpg", "rose/오렌지.webp"),
        ("Rose_orange.jpg", "rose/오렌지.webp"),
        
        # Ranunculus (라넌큘러스) - 오렌지 추가
        ("Ranunculus_or.jpg", "ranunculus/오렌지.webp"),
        ("Ranunculus_orange.jpg", "ranunculus/오렌지.webp"),
        
        # Zinnia (지니아) - 오렌지 추가
        ("zinnia-elegans-or.png", "zinnia-elegans/오렌지.webp"),
        ("zinnia-elegans-orange.png", "zinnia-elegans/오렌지.webp"),
        
        # 기존 파일들도 확인
        ("Rose_rd.jpg", "rose/레드.webp"),
        ("Rose_pk.jpg", "rose/핑크.webp"),
        ("Rose_wh.jpg", "rose/화이트.webp"),
        ("Ranunculus_wh.jpg", "ranunculus/화이트.webp"),
        ("Ranunculus_pk.png", "ranunculus/핑크.webp"),
        ("zinnia-elegans-rd.png", "zinnia-elegans/레드.webp"),
        ("zinnia-elegans-pk.png", "zinnia-elegans/핑크.webp"),
    ]
    
    success_count = 0
    total_count = len(images_to_convert)
    
    print(f"🔄 {total_count}개 이미지 변환 시작...")
    
    for input_file, output_file in images_to_convert:
        input_path = raw_dir / input_file
        output_path = webp_dir / output_file
        
        if input_path.exists():
            if convert_to_webp(str(input_path), str(output_path)):
                success_count += 1
        else:
            print(f"⚠️ 파일 없음: {input_path}")
    
    print(f"\n📊 변환 완료: {success_count}/{total_count}")
    
    # 실제 존재하는 파일들 확인
    print("\n🔍 실제 존재하는 파일들:")
    for input_file, output_file in images_to_convert:
        input_path = raw_dir / input_file
        if input_path.exists():
            print(f"  ✅ {input_file}")
        else:
            print(f"  ❌ {input_file}")

if __name__ == "__main__":
    main()

