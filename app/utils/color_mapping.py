#!/usr/bin/env python3
"""
새로운 색상 코드 시스템 매핑
"""
from typing import List

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

def get_color_from_code(code: str) -> str:
    """색상 코드를 색상명으로 변환"""
    return CODE_TO_COLOR.get(code.lower(), "화이트")

def get_code_from_color(color: str) -> str:
    """색상명을 색상 코드로 변환"""
    return COLOR_CODE_MAPPING.get(color, "wh")

def get_available_colors_for_flower(flower_folder: str) -> List[str]:
    """꽃 폴더에서 사용 가능한 색상 목록 반환"""
    import os
    flower_path = f"data/images_webp/{flower_folder}"
    if not os.path.exists(flower_path):
        return []
    
    colors = []
    for file in os.listdir(flower_path):
        if file.endswith('.webp'):
            color_name = file.replace('.webp', '')
            colors.append(color_name)
    
    return colors

def get_all_available_colors() -> List[str]:
    """모든 사용 가능한 색상 목록 반환"""
    return list(COLOR_CODE_MAPPING.keys())

def get_all_color_codes() -> List[str]:
    """모든 색상 코드 목록 반환"""
    return list(COLOR_CODE_MAPPING.values())

def is_valid_color(color: str) -> bool:
    """색상명이 유효한지 확인"""
    return color in COLOR_CODE_MAPPING

def is_valid_color_code(code: str) -> bool:
    """색상 코드가 유효한지 확인"""
    return code in CODE_TO_COLOR


