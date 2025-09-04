from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from app.models.schemas import FlowerMatch, EmotionAnalysis, FlowerComposition
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason, _generate_flower_card_message
import random

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
        
        # 이미지 URL에서 spp 제거
        image_url = matched_flower.image_url
        if image_url and "-spp-" in image_url:
            image_url = image_url.replace("-spp-", "-")
        
        # 스토리 ID 생성 (S{순번}만 사용)
        story_number = story_id.replace("story_", "").replace("S", "")
        formatted_story_id = f"S{story_number}"  # T01 제거
        
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
        
        # 응답 생성 (수정된 구조)
        response = {
            "story_id": formatted_story_id,
            "original_story": story["story"],
            
            # 해시태그 (감정과 무드 중심 3개)
            "hashtags": hashtags[:3],
            
            # 감정 분석 결과 (3개로 확장, 100을 3개로 분리)
            "emotions": [
                {
                    "emotion": emotion.emotion,
                    "percentage": emotion.percentage
                } for emotion in emotions[:3]  # 최대 3개
            ],
            
            # 꽃 정보
            "flower_name": matched_flower.korean_name,
            "flower_name_en": matched_flower.flower_name,
            "scientific_name": matched_flower.scientific_name,
            "flower_card_message": flower_card_message,
            "flower_image_url": image_url,  # spp 제거된 URL 사용
            
            # 꽃 조합 정보 (메인꽃 한글로 통일, 서브 플라워 2개로 확장)
            "flower_blend": {
                "main_flower": matched_flower.korean_name,  # 한글로 통일
                "sub_flowers": _ensure_two_sub_flowers(composition.sub_flowers),  # 2개로 확장
                "composition_name": composition.composition_name
            },
            
            # 계절 정보
            "season_info": season_info,
            
            # 추천 코멘트 (필드명 변경)
            "comment": recommendation_reason
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

