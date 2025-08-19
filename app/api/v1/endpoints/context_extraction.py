"""
실시간 맥락 추출 API 엔드포인트 (LLM 기반 정밀 버전)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.realtime_context_extractor import RealtimeContextExtractor

router = APIRouter()

class ContextExtractionRequest(BaseModel):
    story: str

class ContextExtractionResponse(BaseModel):
    emotions: List[str]
    situations: List[str]
    moods: List[str]
    colors: List[str]
    confidence: float
    total_extracted: int
    all_tags: List[str]  # 프론트엔드 태그용

@router.post("/extract-context", response_model=ContextExtractionResponse)
async def extract_context_realtime(request: ContextExtractionRequest):
    """입력이 멈췄을 때 사용하는 정밀 LLM 추출"""
    try:
        extractor = RealtimeContextExtractor()
        context = extractor.extract_context_realtime(request.story)
        
        all_tags = context.emotions + context.situations + context.moods + context.colors
        
        return ContextExtractionResponse(
            emotions=context.emotions,
            situations=context.situations,
            moods=context.moods,
            colors=context.colors,
            confidence=context.confidence,
            total_extracted=len(all_tags),
            all_tags=all_tags
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"맥락 추출 실패: {str(e)}")
