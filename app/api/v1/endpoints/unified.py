from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime

from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.utils.request_deduplication import request_deduplicator

router = APIRouter()

class UnifiedRecommendRequest(BaseModel):
    """통합 추천 요청 모델"""
    story: str
    preferred_colors: Optional[List[str]] = []
    excluded_flowers: Optional[List[str]] = []
    updated_context: Optional[Dict[str, Any]] = None

class UnifiedRecommendResponse(BaseModel):
    """통합 추천 응답 모델"""
    # 기본 정보
    flower_name: str
    korean_name: str
    scientific_name: str
    image_url: str
    
    # 해시태그
    hashtags: List[str]
    
    # 추천 영문 문구
    english_description: str
    
    # 감정 비율
    emotions: List[Dict[str, Any]]
    
    # 시즌 정보
    seasonality: List[str]
    
    # 블렌드 구성
    composition: Dict[str, Any]
    
    # 스토리 정보
    your_story: str
    
    # 추천 이유
    comment: str
    
    # 스토리 ID
    story_id: Optional[str] = None

@router.post("/sample-stories")
async def get_sample_stories():
    """샘플 사연 시연 엔드포인트"""
    try:
        # 샘플 사연 데이터 로드
        sample_stories = [
            {
                "id": "sample_1",
                "title": "첫 손자 태어남",
                "story": "첫 손자가 태어난 날이에요. 병실 분위기가 환해지는 꽃바구니를 준비하고 싶어요.",
                "emotions": ["기쁨", "감사"],
                "situations": ["축하"],
                "colors": ["핑크", "화이트"]
            },
            {
                "id": "sample_2", 
                "title": "친구 이직",
                "story": "오랫동안 함께 일한 친구가 이직하게 되었어요. 새로운 시작을 응원하는 마음을 담아 꽃을 선물하고 싶어요.",
                "emotions": ["응원", "감사"],
                "situations": ["이직"],
                "colors": ["옐로우", "화이트"]
            },
            {
                "id": "sample_3",
                "title": "어머니 생신",
                "story": "어머니 생신이에요. 평소 고생하시는 어머니께 감사한 마음을 담아 꽃을 드리고 싶어요.",
                "emotions": ["감사", "사랑"],
                "situations": ["생일"],
                "colors": ["핑크", "레드"]
            }
        ]
        
        return {
            "success": True,
            "stories": sample_stories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"샘플 사연 로드 실패: {str(e)}")

@router.post("/extract-keywords")
async def extract_keywords(req: UnifiedRecommendRequest):
    """실시간 키워드 추출 엔드포인트"""
    try:
        # 감정 분석
        emotion_analyzer = EmotionAnalyzer()
        emotions = emotion_analyzer.analyze(req.story)
        
        # 컨텍스트 추출
        context_extractor = RealtimeContextExtractor()
        excluded_keywords = req.excluded_flowers if req.excluded_flowers else []
        context = context_extractor.extract_context_realtime(req.story, emotions, excluded_keywords)
        
        # 업데이트된 컨텍스트가 있으면 적용
        if req.updated_context:
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']
        
        return {
            "success": True,
            "keywords": {
                "emotions": context.emotions,
                "situations": context.situations,
                "moods": context.moods,
                "colors": context.colors
            },
            "confidence": context.confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")

@router.post("/recommend")
async def unified_recommend(req: UnifiedRecommendRequest):
    """통합 추천 결과 엔드포인트"""
    try:
        # 요청 ID 생성
        request_id = request_deduplicator.generate_request_id(
            req.story, 
            req.preferred_colors, 
            req.excluded_flowers
        ) + "_unified"
        
        # 캐시된 결과 확인
        cached_result = request_deduplicator.get_cached_result(request_id)
        if cached_result:
            return UnifiedRecommendResponse(**cached_result)
        
        # 중복 요청 확인
        if not request_deduplicator.should_process_request(request_id):
            raise HTTPException(status_code=429, detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
        
        # 1. 감정 분석
        emotion_analyzer = EmotionAnalyzer()
        emotions = emotion_analyzer.analyze(req.story)
        
        # 2. 컨텍스트 추출
        context_extractor = RealtimeContextExtractor()
        excluded_keywords = req.excluded_flowers if req.excluded_flowers else []
        context = context_extractor.extract_context_realtime(req.story, emotions, excluded_keywords)
        
        # 3. 업데이트된 컨텍스트 적용
        if req.updated_context:
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']
        
        # 4. 꽃 매칭
        flower_matcher = FlowerMatcher()
        mentioned_flower = context.mentioned_flower if hasattr(context, 'mentioned_flower') else None
        matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        
        # 5. 구성 추천
        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(matched_flower, emotions)
        
        # 6. 추천 이유 생성
        from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason
        reason = _generate_unified_recommendation_reason(matched_flower, composition, emotions, req.story, context, excluded_keywords)
        
        # 7. 영문 설명 생성
        english_description = _generate_english_description(matched_flower, context)
        
        # 8. 해시태그 생성
        hashtags = _generate_hashtags(matched_flower, context)
        
        # 9. 스토리 저장
        story_id = _save_story(req.story, emotions, matched_flower, composition, reason)
        
        # 10. 응답 구성
        response = UnifiedRecommendResponse(
            flower_name=matched_flower.flower_name,
            korean_name=matched_flower.korean_name,
            scientific_name=matched_flower.scientific_name,
            image_url=matched_flower.image_url,
            hashtags=hashtags,
            english_description=english_description,
            emotions=[{"emotion": e.emotion, "percentage": e.percentage} for e in emotions],
            seasonality=matched_flower.seasonality if hasattr(matched_flower, 'seasonality') else ["봄", "여름"],
            composition={
                "main_flower": composition.main_flower,
                "accent_flowers": composition.accent_flowers,
                "greenery": composition.greenery
            },
            your_story=req.story,
            comment=reason,
            story_id=story_id
        )
        
        # 결과 캐시
        request_deduplicator.mark_request_completed(request_id, response.dict())
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 실패: {str(e)}")

def _generate_english_description(flower: Any, context: Any) -> str:
    """영문 설명 생성"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""
Create a brief, elegant English description for this flower recommendation:

Flower: {flower.flower_name} ({flower.scientific_name})
Context: {context.colors}, {context.emotions}, {context.situations}

Write a 1-2 sentence description that captures the essence of this flower recommendation.
Make it poetic and meaningful.
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # 폴백 영문 설명
        return f"A beautiful {flower.flower_name} that perfectly matches your emotions and preferences."

def _generate_hashtags(flower: Any, context: Any) -> List[str]:
    """해시태그 생성"""
    hashtags = []
    
    # 꽃 이름
    hashtags.append(f"#{flower.flower_name.replace(' ', '')}")
    
    # 색상
    for color in context.colors:
        hashtags.append(f"#{color}")
    
    # 감정
    for emotion in context.emotions:
        hashtags.append(f"#{emotion}")
    
    # 상황
    for situation in context.situations:
        hashtags.append(f"#{situation}")
    
    # 계절
    if hasattr(flower, 'seasonality'):
        for season in flower.seasonality:
            hashtags.append(f"#{season}")
    
    return hashtags[:10]  # 최대 10개

def _save_story(story: str, emotions: List, flower: Any, composition: Any, reason: str) -> str:
    """스토리 저장"""
    try:
        from app.api.v1.endpoints.recommend import _save_story_to_database
        return _save_story_to_database(story, emotions, flower, composition, reason)
    except Exception as e:
        print(f"스토리 저장 실패: {e}")
        return None
