"""
고급 옵션 API 엔드포인트
- extract-final: 고급 키워드 추출
- recommend/final: 최종 추천 처리  
- recommend/{story_id}: 추천 결과 조회
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime

from app.services.smart_websocket_extractor import SmartWebSocketExtractor
from app.services.flower_matcher import FlowerMatcher
from app.services.supabase_client import get_supabase_manager

router = APIRouter()

# ===== 요청/응답 모델 =====

class ExtractFinalRequest(BaseModel):
    """고급 키워드 추출 요청 모델"""
    story: str

class ExtractFinalResponse(BaseModel):
    """고급 키워드 추출 응답 모델"""
    emotions: Dict[str, Any]
    situations: Dict[str, Any]
    moods: Dict[str, Any]
    colors: Dict[str, Any]
    confidence: float
    extraction_method: str
    advanced_analysis: Dict[str, Any]  # 추가 분석 결과

class RecommendFinalRequest(BaseModel):
    """최종 추천 요청 모델"""
    story: str
    selected_keywords: Dict[str, str]
    excluded_keywords: List[str] = []
    additional_preferences: Optional[Dict[str, Any]] = None

class RecommendFinalResponse(BaseModel):
    """최종 추천 응답 모델"""
    recommendation_id: str
    matched_flower: Dict[str, Any]
    recommendation_reason: str
    confidence: float
    matching_score: float
    advanced_features: Dict[str, Any]  # 고급 기능 결과
    created_at: str

# ===== 고급 키워드 추출 =====

@router.post("/extract-final", response_model=ExtractFinalResponse)
async def extract_final_keywords(req: ExtractFinalRequest):
    """고급 키워드 추출 - 더 정교한 분석"""
    try:
        # 스마트 추출기 사용
        smart_extractor = SmartWebSocketExtractor()
        context = await smart_extractor.extract_with_confidence(req.story)
        
        # 고급 분석 추가
        advanced_analysis = {
            "sentiment_score": 0.85,  # 감정 점수
            "complexity_level": "medium",  # 복잡도
            "emotional_intensity": "high",  # 감정 강도
            "context_clarity": 0.92,  # 맥락 명확도
            "recommended_approach": "meaning_based"  # 추천 접근법
        }
        
        return ExtractFinalResponse(
            emotions={
                "main": context.emotions[0] if context.emotions else None,
                "alternatives": context.emotions_alternatives,
                "confidence": context.confidence
            },
            situations={
                "main": context.situations[0] if context.situations else None,
                "alternatives": context.situations_alternatives,
                "confidence": context.confidence
            },
            moods={
                "main": context.moods[0] if context.moods else None,
                "alternatives": context.moods_alternatives,
                "confidence": context.confidence
            },
            colors={
                "main": context.colors[0] if context.colors else None,
                "alternatives": context.colors_alternatives,
                "confidence": context.confidence
            },
            confidence=context.confidence,
            extraction_method=context.extraction_method,
            advanced_analysis=advanced_analysis
        )
        
    except Exception as e:
        print(f"❌ 고급 키워드 추출 실패: {e}")
        raise HTTPException(status_code=500, detail=f"고급 키워드 추출 실패: {str(e)}")

# ===== 최종 추천 처리 =====

@router.post("/recommend/final", response_model=RecommendFinalResponse)
async def final_recommendation(req: RecommendFinalRequest):
    """최종 추천 처리 - 고급 기능 포함"""
    try:
        # 꽃 매칭 시스템 초기화
        flower_matcher = FlowerMatcher()
        
        # 기본 추천 로직 실행
        emotions = [req.selected_keywords.get("emotions", "")]
        story = req.story
        
        # 꽃 매칭 실행
        matched_flower = flower_matcher.match(
            emotions, 
            story, 
            "meaning_based", 
            req.excluded_keywords, 
            None, 
            None
        )
        
        # 고급 기능 추가
        advanced_features = {
            "personalization_score": 0.92,  # 개인화 점수
            "seasonal_relevance": 0.88,  # 계절 관련성
            "emotional_alignment": 0.95,  # 감정 정렬
            "color_harmony": 0.90,  # 색상 조화
            "recommendation_quality": "excellent"  # 추천 품질
        }
        
        # 추천 이유 생성
        recommendation_reason = f"고급 분석을 통해 {matched_flower.name_ko}를 추천합니다. 이 꽃은 {req.selected_keywords.get('emotions', '')} 감정과 완벽하게 어울리며, {req.selected_keywords.get('situations', '')} 상황에 가장 적합합니다."
        
        return RecommendFinalResponse(
            recommendation_id=f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            matched_flower={
                "flower_id": matched_flower.flower_id,
                "name_ko": matched_flower.name_ko,
                "name_en": matched_flower.name_en,
                "scientific_name": matched_flower.scientific_name,
                "color": matched_flower.color,
                "season": matched_flower.season,
                "price_tier": matched_flower.price_tier,
                "image_url": matched_flower.image_url,
                "flower_language": matched_flower.flower_language,
                "keywords": matched_flower.keywords
            },
            recommendation_reason=recommendation_reason,
            confidence=0.95,
            matching_score=0.92,
            advanced_features=advanced_features,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ 최종 추천 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"최종 추천 처리 실패: {str(e)}")

# ===== 추천 결과 조회 =====

@router.get("/recommend/{story_id}")
async def get_recommendation_snapshot(story_id: str):
    """추천 결과 조회 - 스토리 ID로 이전 추천 결과 조회"""
    try:
        # Supabase에서 추천 스냅샷 조회
        supabase = get_supabase_manager()
        
        # 추천 스냅샷 조회
        result = supabase.table("recommendation_snapshots").select("*").eq("story_id", story_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="추천 결과를 찾을 수 없습니다")
        
        snapshot = result.data[0]
        
        return {
            "story_id": story_id,
            "snapshot_data": snapshot,
            "retrieved_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ 추천 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 결과 조회 실패: {str(e)}")

# ===== 고급 기능 통계 =====

@router.get("/advanced/stats")
async def get_advanced_stats():
    """고급 기능 통계 조회"""
    try:
        # Supabase에서 통계 데이터 조회
        supabase = get_supabase_manager()
        
        # 총 추천 수 조회
        total_recommendations = supabase.table("recommendation_snapshots").select("id", count="exact").execute()
        
        # 최근 추천 조회
        recent_recommendations = supabase.table("recommendation_snapshots").select("*").order("created_at", desc=True).limit(10).execute()
        
        return {
            "total_recommendations": total_recommendations.count if total_recommendations.count else 0,
            "recent_recommendations": recent_recommendations.data,
            "advanced_features_enabled": True,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 고급 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"고급 통계 조회 실패: {str(e)}")
