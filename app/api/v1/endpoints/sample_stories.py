from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from app.models.schemas import FlowerMatch, EmotionAnalysis, FlowerComposition
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason, _generate_flower_card_message

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

@router.get("/sample-stories")
async def get_sample_stories():
    """샘플 사연 목록을 반환합니다."""
    stories = load_sample_stories()
    return {
        "stories": stories,
        "total_count": len(stories)
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
        
        # EmotionAnalysis 객체 생성
        emotions = []
        if predefined_keywords.get("emotions"):
            for emotion in predefined_keywords["emotions"]:
                emotions.append(EmotionAnalysis(
                    emotion=emotion,
                    percentage=50.0,  # 기본값
                    description=f"{emotion}한 마음"
                ))
        else:
            # 기본 감정 설정
            emotions.append(EmotionAnalysis(
                emotion="기쁨",
                percentage=50.0,
                description="기쁜 마음"
            ))
        
        # 꽃 매칭 서비스 초기화
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
        
        # 스토리 ID 생성 (S{YYYYMMDD}{꽃이름앞3글자}{6자리순번})
        current_date = datetime.now().strftime("%y%m%d")
        flower_prefix = matched_flower.korean_name[:3] if len(matched_flower.korean_name) >= 3 else matched_flower.korean_name
        import random
        random_suffix = f"{random.randint(100000, 999999)}"
        story_id = f"S{current_date}-{flower_prefix.upper()}-{random_suffix}"
        
        # 계절 정보 생성
        season_info = "All Season 01-12"  # 기본값, 실제로는 꽃 데이터에서 가져와야 함
        
        # 응답 생성 (실제 사용자 추천과 동일한 구조)
        response = {
            "story_id": story_id,
            "original_story": story["story"],
            "created_at": datetime.now().isoformat(),
            
            # 감정 분석 결과
            "emotions": [
                {
                    "emotion": emotion.emotion,
                    "percentage": emotion.percentage
                } for emotion in emotions
            ],
            
            # 꽃 정보
            "flower_name": matched_flower.korean_name,
            "flower_name_en": matched_flower.flower_name,
            "scientific_name": matched_flower.scientific_name,
            "flower_card_message": flower_card_message,
            "flower_image_url": matched_flower.image_url,
            
            # 꽃 조합 정보
            "flower_blend": {
                "main_flower": composition.main_flower,
                "sub_flowers": composition.sub_flowers,
                "composition_name": composition.composition_name
            },
            
            # 계절 정보
            "season_info": season_info,
            
            # 추천 코멘트
            "recommendation_reason": recommendation_reason,
            
            # 추가 메타데이터
            "keywords": matched_flower.keywords,
            "hashtags": matched_flower.hashtags,
            "color_keywords": matched_flower.color_keywords,
            "excluded_keywords": [],
            
            # 샘플 사연 정보
            "sample_story": {
                "id": story["id"],
                "title": story["title"],
                "category": story["category"],
                "predefined_keywords": predefined_keywords
            }
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

