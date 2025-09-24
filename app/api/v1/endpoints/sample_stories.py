from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from app.models.schemas import FlowerMatch, EmotionAnalysis, FlowerComposition
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason, _generate_flower_card_message
from app.api.v1.endpoints.unified import _get_flower_recommendation_count
import random

def _generate_flower_image_url(korean_name: str, color_keywords: List[str]) -> str:
    """꽃 이미지 URL 생성 (색상 키워드 기반)"""
    base_url = "https://uylrydyjbnacbjumtxue.supabase.co"
    bucket_name = "flowers"
    
    # 꽃 이름을 영문으로 변환
    flower_mapping = {
        '라넌큘러스': 'ranunculus',
        '알스트로메리아': 'alstroemeria', 
        '장미': 'rose',
        '튤립': 'tulip',
        '거베라': 'gerbera-daisy',
        '백합': 'lily',
        '수국': 'hydrangea',
        '리시안서스': 'lisianthus',
        '스위트피': 'sweet-pea',
        '아스틸베': 'astilbe',
        '부바르디아': 'bouvardia',
        '베이비 브레스': 'babys-breath',
        '아이리스': 'iris',
        '아이리': 'iris',
        '스카비오사': 'scabiosa',
        '프리지아': 'freesia',
        '드럼스틱 플라워': 'drumstick-flower',
        '마거리트 데이지': 'marguerite-daisy'
    }
    
    # 색상을 영문 코드로 변환
    color_mapping = {
        '핑크': 'pk', 'pink': 'pk',
        '빨강': 'rd', 'red': 'rd', '레드': 'rd',
        '화이트': 'wh', 'white': 'wh',
        '옐로우': 'yl', 'yellow': 'yl',
        '퍼플': 'pu', 'purple': 'pu',
        '블루': 'bl', 'blue': 'bl',
        '그린': 'gr', 'green': 'gr',
        '오렌지': 'or', 'orange': 'or',
        '라벤더': 'll', 'lavender': 'll',
        '연보라': 'll', '크림': 'wh'
    }
    
    mapped_flower = flower_mapping.get(korean_name, korean_name.lower())
    
    # 색상 키워드가 있으면 첫 번째 색상 사용, 없으면 화이트
    if color_keywords:
        color = color_keywords[0]
        mapped_color = color_mapping.get(color, 'wh')
    else:
        mapped_color = 'wh'  # 기본값: 화이트
    
    return f"{base_url}/storage/v1/object/public/{bucket_name}/{mapped_flower}-{mapped_color}.webp"

def _get_predefined_flower_for_sample_story(story_id: str) -> dict:
    """샘플 스토리별 미리 정의된 꽃 정보"""
    predefined_flowers = {
        "S01": {
            "korean_name": "카네이션",
            "flower_name_en": "Carnation",
            "scientific_name": "Dianthus caryophyllus",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/carnation-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/carnation.png"
        },
        "S02": {
            "korean_name": "가든 피오니",
            "flower_name_en": "Garden Peony",
            "scientific_name": "Paeonia lactiflora",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/garden-peony-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/garden-peony.png"
        },
        "S03": {
            "korean_name": "달리아",
            "flower_name_en": "Dahlia",
            "scientific_name": "Dahlia pinnata",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/dahlia-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/dahlia.png"
        },
        "S04": {
            "korean_name": "라넌큘러스",
            "flower_name_en": "Ranunculus",
            "scientific_name": "Ranunculus asiaticus",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/ranunculus-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/ranunculus.png"
        },
        "S05": {
            "korean_name": "드럼스틱 플라워",
            "flower_name_en": "Drumstick Flower",
            "scientific_name": "Craspedia globosa",
            "color_keywords": ["옐로우"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/drumstick-flower-yl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/drumstick-flower.png"
        },
        "S06": {
            "korean_name": "장미",
            "flower_name_en": "Rose",
            "scientific_name": "Rosa hybrida",
            "color_keywords": ["오렌지"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-or.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/rose.png"
        },
        "S07": {
            "korean_name": "글라디올러스",
            "flower_name_en": "Gladiolus",
            "scientific_name": "Gladiolus spp",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/gladiolus-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/gladiolus.png"
        },
        "S08": {
            "korean_name": "스톡 플라워",
            "flower_name_en": "Stock Flower",
            "scientific_name": "Matthiola incana",
            "color_keywords": ["화이트"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/stock-flower-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/stock-flower.png"
        },
        "S09": {
            "korean_name": "안스리움",
            "flower_name_en": "Anthurium",
            "scientific_name": "Anthurium andraeanum",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/anthurium-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/anthurium.png"
        },
        "S10": {
            "korean_name": "아스틸베",
            "flower_name_en": "Astilbe",
            "scientific_name": "Astilbe chinensis",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/astilbe-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/astilbe.png"
        },
        "S11": {
            "korean_name": "리시안서스",
            "flower_name_en": "Lisianthus",
            "scientific_name": "Eustoma grandiflorum",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/lisianthus-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/lisianthus.png"
        },
        "S12": {
            "korean_name": "부바르디아",
            "flower_name_en": "Bouvardia",
            "scientific_name": "Bouvardia ternifolia",
            "color_keywords": ["화이트"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/bouvardia-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/bouvardia.png"
        },
        "S13": {
            "korean_name": "스위트피",
            "flower_name_en": "Sweet Pea",
            "scientific_name": "Lathyrus odoratus",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/sweet-pea-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/sweet-pea.png"
        },
        "S14": {
            "korean_name": "스위트피",
            "flower_name_en": "Sweet Pea",
            "scientific_name": "Lathyrus odoratus",
            "color_keywords": ["블루"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/sweet-pea-bl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/sweet-pea.png"
        },
        "S15": {
            "korean_name": "프리지아",
            "flower_name_en": "Freesia",
            "scientific_name": "Freesia refracta",
            "color_keywords": ["옐로우"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/freesia-yl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/freesia.png"
        },
        "S16": {
            "korean_name": "가든 피오니",
            "flower_name_en": "Garden Peony",
            "scientific_name": "Paeonia lactiflora",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/garden-peony-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/garden-peony.png"
        },
        "S17": {
            "korean_name": "마거리트 데이지",
            "flower_name_en": "Marguerite Daisy",
            "scientific_name": "Argyranthemum frutescens",
            "color_keywords": ["화이트", "크림"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/marguerite-daisy-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/marguerite-daisy.png"
        },
        "S18": {
            "korean_name": "장미",
            "flower_name_en": "Rose",
            "scientific_name": "Rosa hybrida",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/rose.png"
        },
        "S19": {
            "korean_name": "카네이션",
            "flower_name_en": "Carnation",
            "scientific_name": "Dianthus caryophyllus",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/carnation-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/carnation.png"
        },
        "S20": {
            "korean_name": "코튼 플랜트",
            "flower_name_en": "Cotton Plant",
            "scientific_name": "Gossypium hirsutum",
            "color_keywords": ["화이트"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/cotton-plant-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/cotton-plant.png"
        },
        "S21": {
            "korean_name": "아이리스",
            "flower_name_en": "Iris",
            "scientific_name": "Iris germanica",
            "color_keywords": ["퍼플"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/iris-pu.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/iris.png"
        },
        "S22": {
            "korean_name": "장미",
            "flower_name_en": "Rose",
            "scientific_name": "Rosa hybrida",
            "color_keywords": ["블루"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-bl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/rose.png"
        },
        "S23": {
            "korean_name": "스카비오사",
            "flower_name_en": "Scabiosa",
            "scientific_name": "Scabiosa columbaria",
            "color_keywords": ["블루"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/scabiosa-bl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/scabiosa.png"
        },
        "S24": {
            "korean_name": "프리지아",
            "flower_name_en": "Freesia",
            "scientific_name": "Freesia refracta",
            "color_keywords": ["옐로우"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/freesia-yl.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/freesia.png"
        },
        "S25": {
            "korean_name": "튤립",
            "flower_name_en": "Tulip",
            "scientific_name": "Tulipa gesneriana",
            "color_keywords": ["화이트"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/tulip-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/tulip.png"
        },
        "S26": {
            "korean_name": "튤립",
            "flower_name_en": "Tulip",
            "scientific_name": "Tulipa gesneriana",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/tulip-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/tulip.png"
        },
        "S27": {
            "korean_name": "안스리움",
            "flower_name_en": "Anthurium",
            "scientific_name": "Anthurium andraeanum",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/anthurium-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/anthurium.png"
        },
        "S28": {
            "korean_name": "이베리스",
            "flower_name_en": "Iberis",
            "scientific_name": "Iberis sempervirens",
            "color_keywords": ["화이트"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/iberis-wh.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/iberis.png"
        },
        "S29": {
            "korean_name": "지니아",
            "flower_name_en": "Zinnia",
            "scientific_name": "Zinnia elegans",
            "color_keywords": ["빨강", "레드"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/zinnia-rd.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/zinnia.png"
        },
        "S30": {
            "korean_name": "지니아",
            "flower_name_en": "Zinnia",
            "scientific_name": "Zinnia elegans",
            "color_keywords": ["핑크"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/zinnia-pk.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/zinnia.png"
        },
        "S31": {
            "korean_name": "글로브 아마란스",
            "flower_name_en": "Globe Amaranth",
            "scientific_name": "Gomphrena globosa",
            "color_keywords": ["퍼플"],
            "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/globe-amaranth-pu.webp",
            "calligraphy_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/globe-amaranth.png"
        }
    }
    return predefined_flowers.get(story_id, None)

def _generate_calligraphy_url(korean_name: str) -> str:
    """캘리그래피 이미지 URL 생성"""
    base_url = "https://uylrydyjbnacbjumtxue.supabase.co"
    bucket_name = "calligraphy-images"
    
    # 꽃 이름을 영문으로 변환
    flower_mapping = {
        '라넌큘러스': 'ranunculus',
        '알스트로메리아': 'alstroemeria', 
        '장미': 'rose',
        '튤립': 'tulip',
        '거베라': 'gerbera-daisy',
        '백합': 'lily',
        '수국': 'hydrangea',
        '리시안서스': 'lisianthus',
        '스위트피': 'sweet-pea',
        '아스틸베': 'astilbe',
        '부바르디아': 'bouvardia',
        '베이비 브레스': 'babysbreath',
        '아이리스': 'iris',
        '아이리': 'iris',
        '스카비오사': 'scabiosa',
        '프리지아': 'freesia',
        '드럼스틱 플라워': 'drumstick-flower',
        '마거리트 데이지': 'marguerite-daisy'
    }
    
    mapped_flower = flower_mapping.get(korean_name, korean_name.lower())
    return f"{base_url}/storage/v1/object/public/{bucket_name}/{mapped_flower}.png"

router = APIRouter()

# 샘플 사연 데이터 로드
def load_sample_stories():
    """샘플 사연 데이터를 로드합니다."""
    try:
        with open("data/sample_stories.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("sample_stories", [])
    except Exception as e:
        print(f"❌ 샘플 사연 데이터 로드 실패: {e}")
        return []

def _ensure_two_sub_flowers(sub_flowers: List[str]) -> List[str]:
    """서브 플라워를 항상 2개로 확장 (중복 방지)"""
    if not sub_flowers:
        return ["화이트 베이비 브레스", "그린 유칼립투스"]
    
    if len(sub_flowers) == 1:
        # 1개만 있는 경우 다른 소재 추가
        existing_flower = sub_flowers[0]
        if "베이비 브레스" in existing_flower:
            return sub_flowers + ["그린 유칼립투스"]
        else:
            return sub_flowers + ["화이트 베이비 브레스"]
    
    # 2개 이상인 경우 앞의 2개만 사용
    return sub_flowers[:2]

@router.get("/sample-stories")
async def get_sample_stories():
    """샘플 사연 목록을 반환합니다."""
    stories = load_sample_stories()
    
    # ID 형식을 S01, S02 형식으로 변경
    formatted_stories = []
    for i, story in enumerate(stories, 1):
        formatted_story = {
            "id": f"S{i:02d}",  # S01, S02, S03 형식
            "title": story.get("title", ""),
            "category": story.get("category", "기타"),
            "predefined_keywords": story.get("predefined_keywords", {})
        }
        formatted_stories.append(formatted_story)
    
    return {
        "stories": formatted_stories,
        "total_count": len(formatted_stories)
    }

@router.get("/sample-stories/{story_id}")
async def get_sample_story(story_id: str):
    """특정 샘플 사연을 반환합니다."""
    stories = load_sample_stories()
    story = next((s for s in stories if s["id"] == story_id), None)
    
    if not story:
        raise HTTPException(status_code=404, detail="사연을 찾을 수 없습니다.")
    
    return story

@router.post("/sample-stories/{story_id}/recommend")
async def recommend_from_sample_story(story_id: str):
    """샘플 사연의 미리 설정된 키워드로 꽃을 추천합니다."""
    try:
        # 샘플 사연 로드
        stories = load_sample_stories()
        story = next((s for s in stories if s["id"] == story_id), None)
        
        if not story:
            raise HTTPException(status_code=404, detail="사연을 찾을 수 없습니다.")
        
        # 미리 설정된 키워드 추출
        predefined_keywords = story["predefined_keywords"]
        
        # EmotionAnalysis 객체 생성 (3개로 확장)
        emotions = []
        if predefined_keywords.get("emotions"):
            emotion_list = predefined_keywords["emotions"]
            # 최대 3개까지 처리
            for i, emotion in enumerate(emotion_list[:3]):
                if i == 0:
                    percentage = 40.0  # 첫 번째 감정
                elif i == 1:
                    percentage = 35.0  # 두 번째 감정
                else:
                    percentage = 25.0  # 세 번째 감정
                
                emotions.append(EmotionAnalysis(
                    emotion=emotion,
                    percentage=percentage,
                    description=f"{emotion}한 마음"
                ))
            
            # 감정이 2개만 있는 경우 3번째 감정 추가
            if len(emotions) == 2:
                emotions.append(EmotionAnalysis(
                    emotion="차분함",
                    percentage=25.0,
                    description="차분한 마음"
                ))
        else:
            # 기본 감정 설정 (3개)
            emotions = [
                EmotionAnalysis(emotion="기쁨", percentage=40.0, description="기쁜 마음"),
                EmotionAnalysis(emotion="감사", percentage=35.0, description="감사한 마음"),
                EmotionAnalysis(emotion="희망", percentage=25.0, description="희망찬 마음")
            ]
        
        # 먼저 룰셋으로 미리 정의된 꽃이 있는지 확인
        predefined_flower = _get_predefined_flower_for_sample_story(story_id)
        
        if predefined_flower:
            # 룰셋으로 미리 정의된 꽃 사용
            matched_flower = type('MatchedFlower', (), {
                'korean_name': predefined_flower['korean_name'],
                'flower_name': predefined_flower['korean_name'],  # flower_name 추가
                'flower_name_en': predefined_flower['flower_name_en'],
                'scientific_name': predefined_flower['scientific_name'],
                'image_url': predefined_flower['image_url'],
                'color_keywords': predefined_flower['color_keywords']  # color_keywords 추가
            })()
            color_keywords = predefined_flower['color_keywords']
        else:
            # 기존 로직: 꽃 매칭 서비스 초기화
            flower_matcher = FlowerMatcher()
            
            # 색상 키워드 추출
            color_keywords = predefined_keywords.get("colors", [])
            
            # 꽃 추천 실행 (기존 match() 메서드 사용)
            matched_flower = flower_matcher.match(
                emotions=emotions,
                story=story["story"],
                user_intent="meaning_based",  # 의미 기반 매칭
                excluded_keywords=None,
                mentioned_flower=None,
                context=None
            )
            
            if not matched_flower:
                raise HTTPException(status_code=404, detail="적합한 꽃을 찾을 수 없습니다.")
        
        # 꽃 조합 추천
        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(
            matched_flower=matched_flower,
            emotions=emotions
        )
        
        # 추천 이유 생성 (GPT 사용)
        recommendation_reason = _generate_unified_recommendation_reason(
            matched_flower=matched_flower,
            composition=composition,
            emotions=emotions,
            story=story["story"],
            context=None,
            excluded_keywords=[]
        )
        
        # 꽃 카드 메시지 생성 (GPT 사용)
        flower_card_message = _generate_flower_card_message(
            matched_flower=matched_flower,
            emotions=emotions,
            story=story["story"]
        )
        
        # 이미지 URL 생성
        if predefined_flower:
            # 룰셋으로 미리 정의된 이미지 URL 사용
            image_url = predefined_flower['image_url']
            calligraphy_image_url = predefined_flower['calligraphy_url']
        else:
            # 기존 로직: 직접 이미지 URL 생성 (색상 키워드 기반)
            image_url = _generate_flower_image_url(matched_flower.korean_name, color_keywords)
            calligraphy_image_url = _generate_calligraphy_url(matched_flower.korean_name)
        
        # 스토리 ID 생성 (샘플 스토리 전용 형식: S250924-ZIN-S2901)
        # 꽃 이름을 영문으로 변환하여 약어 생성
        flower_name_en = getattr(matched_flower, 'flower_name_en', matched_flower.korean_name)
        if hasattr(matched_flower, 'flower_name_en') and matched_flower.flower_name_en:
            flower_code = matched_flower.flower_name_en.upper()[:3]
        else:
            # 한글 꽃 이름을 영문으로 매핑
            korean_to_english = {
                '지니아': 'ZIN', '장미': 'ROS', '튤립': 'TUL', '라넌큘러스': 'RAN',
                '카네이션': 'CAR', '가든 피오니': 'PEA', '달리아': 'DAH', '드럼스틱 플라워': 'DRU',
                '글라디올러스': 'GLA', '스톡 플라워': 'STO', '안스리움': 'ANT', '아스틸베': 'AST',
                '리시안서스': 'LIS', '부바르디아': 'BOU', '스위트피': 'SWE', '프리지아': 'FRE',
                '마거리트 데이지': 'MAR', '코튼 플랜트': 'COT', '아이리스': 'IRI', '스카비오사': 'SCA',
                '이베리스': 'IBE', '글로브 아마란스': 'GLO'
            }
            flower_code = korean_to_english.get(matched_flower.korean_name, 'UNK')
        
        sequence_number = _get_flower_recommendation_count(flower_code)
        story_number = story_id.replace("story_", "").replace("S", "")
        formatted_story_id = f"S{datetime.now().strftime('%y%m%d')}-{flower_code}-S{story_number}{sequence_number:02d}"
        
        # 계절 정보 생성 (시즌과 월 분리)
        season_info = {"season": "All Season", "months": "01-12"}  # 기본값, 실제로는 꽃 데이터에서 가져와야 함
        
        # 해시태그 생성 (감정 2개, 무드 1개)
        hashtags = []
        
        # 감정 2개 추가
        if predefined_keywords.get("emotions"):
            emotions_list = predefined_keywords["emotions"]
            for i, emotion in enumerate(emotions_list[:2]):  # 최대 2개
                hashtags.append(f"#{emotion}")
        
        # 무드 1개 추가
        if predefined_keywords.get("moods"):
            moods_list = predefined_keywords["moods"]
            if moods_list:
                hashtags.append(f"#{moods_list[0]}")
        
        # 3개가 안 되면 기본값 추가
        while len(hashtags) < 3:
            hashtags.append("#특별한")
        
        # 응답 생성 (unified.py와 동일한 구조로 통일)
        response = {
            "success": True,
            "created_at": datetime.now().strftime('%Y.%m.%d.'),
            "story_id": formatted_story_id,
            "your_story": story["story"],
            
            # 꽃 정보 (예전 구조로 개선)
            "flower_info": {
                "korean_name": matched_flower.korean_name,
                "english_name": getattr(matched_flower, 'flower_name_en', matched_flower.korean_name),
                "scientific_name": matched_flower.scientific_name
            },
            
            # 꽃 조합 정보 (unified.py와 동일한 구조)
            "flower_blend": {
                "main_flower": matched_flower.korean_name,
                "sub_flowers": _ensure_two_sub_flowers(composition.sub_flowers),
                "composition_name": composition.composition_name
            },
            
            # 이미지 URL (unified.py와 동일한 필드명)
            "flower_image_url": image_url,
            "calligraphy_image_url": calligraphy_image_url,
            
            # 꽃 카드 메시지 (예전 구조로 개선)
            "flower_card_message": {
                "quote": getattr(flower_card_message, 'quote', ''),
                "source": getattr(flower_card_message, 'source', '')
            },
            
            # 감정 분석 결과 (unified.py와 동일한 구조)
            "emotions": [
                {
                    "emotion": emotion.emotion,
                    "percentage": emotion.percentage
                } for emotion in emotions[:3]
            ],
            
            # 계절 정보 (예전 구조로 개선)
            "season_detail": {
                "availability": season_info.get("season", "Spring/Summer"),
                "best_season": season_info.get("months", "03-08")
            },
            
            # 추천 코멘트 (unified.py와 동일한 필드명)
            "comment": recommendation_reason,
            
            # 해시태그 (예전 구조로 개선)
            "hashtags": hashtags[:3]
        }
        
        return response
        
    except Exception as e:
        print(f"❌ 샘플 사연 추천 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/sample-stories/categories")
async def get_sample_story_categories():
    """샘플 사연 카테고리 목록을 반환합니다."""
    stories = load_sample_stories()
    categories = {}
    
    for story in stories:
        category = story.get("category", "기타")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": story["id"],
            "title": story["title"],
            "story": story["story"]
        })
    
    return {
        "categories": categories,
        "category_count": len(categories)
    }

@router.get("/sample-stories/category/{category}")
async def get_sample_stories_by_category(category: str):
    """특정 카테고리의 샘플 사연들을 반환합니다."""
    stories = load_sample_stories()
    category_stories = [s for s in stories if s.get("category") == category]
    
    if not category_stories:
        raise HTTPException(status_code=404, detail="해당 카테고리의 사연을 찾을 수 없습니다.")
    
    return {
        "category": category,
        "stories": category_stories,
        "count": len(category_stories)
    }

