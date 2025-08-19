#!/usr/bin/env python3
"""
누락된 색상들을 추가하는 스크립트
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

def add_missing_colors():
    """누락된 색상들을 추가"""
    print("🔄 누락된 색상 추가 중...")
    
    # 누락된 색상 매핑 (기존 파일을 복사하여 새로운 색상 생성)
    missing_color_mappings = [
        # (꽃폴더, 기존색상, 새색상)
        ("dahlia", "핑크", "네이비 블루"),
        ("rose", "블루", "네이비 블루"),
        ("alstroemeria-spp", "화이트", "크림색"),
        ("lisianthus", "화이트", "크림색"),
        ("marguerite-daisy", "화이트", "크림색"),
        ("lily", "화이트", "크림색"),
        ("baby's-breath", "화이트", "크림색"),
        ("stock-flower", "퍼플", "크림색"),
        ("ammi-majus", "화이트", "크림색"),
        ("bouvardia", "화이트", "크림색"),
        ("cotton-plant", "화이트", "크림색"),
        ("cymbidium-spp", "화이트", "크림색"),
        ("cymbidium-spp.", "화이트", "크림색"),
        ("iberis-sempervirens", "화이트", "크림색"),
        ("veronica-spicata", "화이트", "크림색"),
        ("scabiosa", "화이트", "크림색"),
        ("globe-amaranth", "베이지", "크림색"),
        ("globe-amaranth-퍼플", "베이지", "크림색"),
        ("gerbera-daisy-노랑", "베이지", "크림색"),
        ("anemone-coronaria", "오렌지", "크림색"),
        ("anemone-coronaria-pu", "오렌지", "크림색"),
        ("anemone-coronaria-rd", "오렌지", "크림색"),
        ("garden-peony-화이트", "레드", "크림색"),
        ("garden-peony-핑크", "레드", "크림색"),
        ("bouvardia-화이트", "레드", "크림색"),
        ("astilbe-japonica-pk", "베이지", "크림색")
    ]
    
    source_dir = "data/images_webp"
    converted_count = 0
    
    for flower_folder, source_color, target_color in missing_color_mappings:
        source_path = os.path.join(source_dir, flower_folder, f"{source_color}.webp")
        target_path = os.path.join(source_dir, flower_folder, f"{target_color}.webp")
        
        if os.path.exists(source_path) and not os.path.exists(target_path):
            # 파일 복사
            shutil.copy2(source_path, target_path)
            print(f"✅ 색상 추가: {flower_folder}/{target_color}.webp")
            converted_count += 1
        elif os.path.exists(target_path):
            print(f"⚠️  이미 존재: {flower_folder}/{target_color}.webp")
        else:
            print(f"❌ 소스 파일 없음: {source_path}")
    
    print(f"✅ 누락된 색상 추가 완료: {converted_count}개 파일")
    return converted_count

def main():
    """메인 함수"""
    print("🔄 누락된 색상 추가 도구")
    print("=" * 50)
    
    # 누락된 색상 추가
    converted_count = add_missing_colors()
    
    print(f"\n✅ 추가 완료! 총 {converted_count}개 파일이 추가되었습니다.")
    print("📝 다음 단계:")
    print("1. base64_images.json을 업데이트하세요")
    print("2. 서버를 재시작하세요")

if __name__ == "__main__":
    main()

