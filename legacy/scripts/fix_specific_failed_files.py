#!/usr/bin/env python3
"""
구체적으로 실패한 파일들을 직접 처리하는 스크립트
"""
import os
import shutil
from PIL import Image
from typing import Dict, List, Tuple

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

def process_specific_failed_files():
    """구체적으로 실패한 파일들을 직접 처리"""
    print("🔄 구체적 실패 파일 처리 중...")
    
    # 실패한 파일들과 그들의 올바른 매핑
    failed_file_mappings = [
        # 파일명: (꽃이름, 색상)
        ("Scabiosa_블루.jpg.png", ("scabiosa", "블루")),
        ("Rose_레드.jpg.png", ("rose", "레드")),
        ("Tulip_화이트.jpg", ("tulip", "화이트")),
        ("Stock Flower_퍼플.JPG", ("stock-flower", "퍼플")),
        ("Drumstick Flower_옐로우.jpg.png", ("drumstick-flower", "옐로우")),
        ("Dahlia_옐로우.jpg.png", ("dahlia", "옐로우")),
        ("Hydrangea_핑크.png", ("hydrangea", "핑크")),
        ("Tulip_레드.jpg", ("tulip", "레드")),
        ("Lily_화이트.png", ("lily", "화이트")),
        ("Lisianthus_화이트.jpg", ("lisianthus", "화이트")),
        ("Garden Peony_핑크.jpg", ("garden-peony", "핑크")),
        ("Scabiosa_화이트.jpg.png", ("scabiosa", "화이트")),
        ("Lisianthus_핑크.jpg", ("lisianthus", "핑크")),
        ("Cotton Plant_화이트.jpg.png", ("cotton-plant", "화이트")),
        ("Marguerite Daisy_흰색.png", ("marguerite-daisy", "화이트")),
        ("Baby's Breath_화이트.jpg", ("baby's-breath", "화이트")),
        ("Dahlia_핑크.jpg.png", ("dahlia", "핑크")),
        ("Tulip_옐로우.jpg", ("tulip", "옐로우")),
        ("Rose_핑크.jpg", ("rose", "핑크")),
        ("Cockscomb_레드.jpg", ("cockscomb", "레드")),
        ("Lisianthus_라벤더.jpg", ("lisianthus", "라일락")),
        ("Gerbera Daisy_노랑.png", ("gerbera-daisy", "옐로우")),
        ("anthurium-andraeanum-gr.png", ("anthurium-andraeanum", "그린")),
        ("cymbidium-spp.-gr.png", ("cymbidium-spp.", "그린")),
        ("hydrangea-gr.png", ("hydrangea", "그린")),
        ("lathyrus-odoratus-pk.png", ("lathyrus-odoratus", "핑크")),
        ("anemone-coronaria-rd.png", ("anemone-coronaria", "레드")),
        ("anemone-coronaria-pu.png", ("anemone-coronaria", "퍼플"))
    ]
    
    source_dir = "data/images_raw"
    target_dir = "data/images_webp"
    converted_count = 0
    
    for filename, (flower_name, color_name) in failed_file_mappings:
        file_path = os.path.join(source_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  파일이 존재하지 않음: {filename}")
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
    
    print(f"✅ 구체적 실패 파일 처리 완료: {converted_count}개 파일")
    return converted_count

def main():
    """메인 함수"""
    print("🔄 구체적 실패 파일 처리 도구")
    print("=" * 50)
    
    # 구체적 실패 파일 처리
    converted_count = process_specific_failed_files()
    
    print(f"\n✅ 처리 완료! 총 {converted_count}개 파일이 변환되었습니다.")
    print("📝 다음 단계:")
    print("1. 새로운 꽃들을 flower_database에 추가하세요")
    print("2. base64_images.json을 업데이트하세요")
    print("3. 서버를 재시작하세요")

if __name__ == "__main__":
    main()

