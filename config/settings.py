"""
이미지 생성 실험용 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# NanoBana API 설정  
NANOBANA_API_KEY = os.getenv('NANOBANA_API_KEY')
NANOBANA_BASE_URL = "https://api.nanobana.com/v1"

# 실험 설정
EXPERIMENT_CONFIG = {
    "test_flowers": [
        {"name": "장미", "emotion": "사랑", "color": "핑크"},
        {"name": "해바라기", "emotion": "기쁨", "color": "옐로우"},
        {"name": "라벤더", "emotion": "평온", "color": "퍼플"}
    ],
    "image_styles": [
        "photorealistic",
        "artistic",
        "minimalist",
        "vintage"
    ]
}
