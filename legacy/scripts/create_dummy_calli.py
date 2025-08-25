#!/usr/bin/env python3
"""
테스트용 더미 캘리그래피 데이터 생성 스크립트
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def create_dummy_calligraphy():
    """더미 캘리그래피 이미지와 메타데이터 생성"""
    
    base_dir = Path(__file__).parent.parent
    calli_dir = base_dir / "data" / "calli_images"
    calli_dir.mkdir(exist_ok=True)
    
    metadata_file = base_dir / "calli_metadata.json"
    
    # 꽃 이름 목록
    flower_names = [
        "Ammi Majus",
        "Anemone Coronaria", 
        "Babys Breath",
        "Bouvardia",
        "Cockscomb",
        "Cotton Plant",
        "Cymbidium Spp",
        "Dahlia",
        "Drumstick Flower",
        "Garden Peony",
        "Gerbera Daisy",
        "Gladiolus",
        "Globe Amaranth",
        "Hydrangea",
        "Lily",
        "Lisianthus",
        "Marguerite Daisy",
        "Tagetes Erecta",
        "Gentiana Andrewsii",
        "Ranunculus",
        "Rose",
        "Scabiosa",
        "Stock Flower",
        "Lathyrus Odoratus",
        "Tulip",
        "Veronica Spicata",
        "Zinnia Elegans"
    ]
    
    metadata = {}
    
    for i, flower_name in enumerate(flower_names):
        # 파일명 생성
        filename = f"{flower_name.lower().replace(' ', '-')}.png"
        file_path = calli_dir / filename
        
        # 더미 이미지 생성 (텍스트 기반)
        create_text_image(flower_name, file_path)
        
        # 메타데이터 생성
        metadata[filename] = {
            'flower_name': flower_name,
            'drive_id': f'dummy_id_{i}',
            'modified_time': '2024-01-15T10:00:00.000Z',
            'size': file_path.stat().st_size if file_path.exists() else 1024,
            'mime_type': 'image/png',
            'local_path': str(file_path)
        }
    
    # 메타데이터 저장
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 더미 캘리그래피 데이터 생성 완료: {len(metadata)}개 파일")
    print(f"📁 저장 위치: {calli_dir}")
    print(f"📄 메타데이터: {metadata_file}")

def create_text_image(text, file_path):
    """텍스트 기반 더미 이미지 생성"""
    # 이미지 크기
    width, height = 400, 300
    
    # 배경색 (랜덤)
    bg_colors = [
        (255, 248, 220),  # 코랄
        (255, 228, 196),  # 베이지
        (255, 255, 240),  # 아이보리
        (255, 255, 255),  # 화이트
        (255, 218, 185),  # 피치
    ]
    bg_color = random.choice(bg_colors)
    
    # 이미지 생성
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 폰트 설정 (기본 폰트 사용)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # 텍스트 색상
    text_color = (70, 130, 180)  # 스틸 블루
    
    # 텍스트 중앙 정렬
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 텍스트 그리기
    draw.text((x, y), text, fill=text_color, font=font)
    
    # 장식선 추가
    line_color = (200, 200, 200)
    draw.line([(50, y-20), (width-50, y-20)], fill=line_color, width=2)
    draw.line([(50, y+text_height+20), (width-50, y+text_height+20)], fill=line_color, width=2)
    
    # 이미지 저장
    image.save(file_path, 'PNG')
    print(f"  📝 생성: {file_path.name}")

if __name__ == "__main__":
    create_dummy_calligraphy()
