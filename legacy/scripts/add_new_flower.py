#!/usr/bin/env python3
"""
새로운 꽃을 자동으로 추가하는 스크립트
"""
import os
import json
from typing import Dict, List

def add_new_flower(
    flower_name: str,
    korean_name: str,
    scientific_name: str,
    colors: List[str],
    keywords: List[str],
    emotions: List[str],
    folder_name: str = None
):
    """새로운 꽃을 시스템에 추가"""
    
    if folder_name is None:
        # 영어 이름을 폴더명으로 변환
        folder_name = flower_name.lower().replace(" ", "-")
    
    print(f"🌸 새로운 꽃 추가: {flower_name} ({korean_name})")
    print(f"📁 폴더명: {folder_name}")
    print(f"🎨 색상: {', '.join(colors)}")
    
    # 1. 폴더 생성
    folder_path = f"data/images_webp/{folder_name}"
    os.makedirs(folder_path, exist_ok=True)
    print(f"✅ 폴더 생성: {folder_path}")
    
    # 2. 색상별 이미지 파일 확인
    for color in colors:
        image_path = f"{folder_path}/{color}.webp"
        if not os.path.exists(image_path):
            print(f"⚠️  이미지 파일이 없습니다: {image_path}")
        else:
            print(f"✅ 이미지 파일 확인: {image_path}")
    
    # 3. 코드 수정 가이드 출력
    print("\n📝 다음 코드를 수정해야 합니다:")
    print(f"""
# app/services/flower_matcher.py의 available_colors에 추가:
"{folder_name}": {colors}

# app/services/flower_matcher.py의 folder_mapping에 추가:
"{flower_name}": "{folder_name}"

# app/services/flower_matcher.py의 flower_database에 추가:
"{flower_name}": {{
    "korean_name": "{korean_name}",
    "scientific_name": "{scientific_name}",
    "image_url": self.base64_images.get("{folder_name}", {{}}).get("{colors[0] if colors else '화이트'}", ""),
    "keywords": {keywords},
    "colors": {colors},
    "emotions": {emotions}
}}

# LLM 프롬프트에 추가:
"{len(colors) + 17}. {flower_name} ({korean_name}): {', '.join(keywords[:2])} - {', '.join(colors)}"
    """)

if __name__ == "__main__":
    # 사용 예시
    add_new_flower(
        flower_name="Sunflower",
        korean_name="해바라기", 
        scientific_name="Helianthus annuus",
        colors=["노랑", "화이트"],
        keywords=["희망", "긍정", "따뜻함", "자연스러움"],
        emotions=["희망", "긍정", "따뜻함", "자연스러움"]
    )


