"""
매우 간단하고 빠른 실시간 키워드 추출 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.utils.request_deduplication import request_deduplicator

router = APIRouter()

class FastContextRequest(BaseModel):
    story: str

class FastContextResponse(BaseModel):
    emotions: List[str]
    situations: List[str]
    moods: List[str]
    colors: List[str]

@router.post("/fast-context", response_model=FastContextResponse)
async def fast_context_extraction(request: FastContextRequest):
    """매우 간단하고 빠른 키워드 추출 (중복 요청 방지 포함)"""
    try:
        # 요청 ID 생성 (fast-context용)
        request_id = request_deduplicator.generate_request_id(
            request.story, 
            [], 
            []
        ) + "_fast_context"  # fast-context와 구분
        
        print(f"🔍 Fast Context 요청 ID 생성: {request_id}")
        
        # 캐시된 결과가 있는지 확인
        cached_result = request_deduplicator.get_cached_result(request_id)
        if cached_result:
            print(f"📋 Fast Context 캐시된 결과 반환: {request_id}")
            return FastContextResponse(**cached_result)
        
        # 중복 요청인지 확인
        if not request_deduplicator.should_process_request(request_id):
            print(f"⏳ Fast Context 중복 요청 대기 중: {request_id}")
            # 잠시 대기 후 다시 확인
            import time
            time.sleep(0.1)
            cached_result = request_deduplicator.get_cached_result(request_id)
            if cached_result:
                return FastContextResponse(**cached_result)
            else:
                raise HTTPException(status_code=429, detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
        
        # 실제 요청 처리
        print(f"🚀 Fast Context 새로운 요청 처리 시작: {request_id}")
        
        # RealtimeContextExtractor 사용
        from app.services.realtime_context_extractor import RealtimeContextExtractor
        
        extractor = RealtimeContextExtractor()
        result = extractor.extract_context_realtime(request.story)
        
        # 결과 생성
        response = FastContextResponse(
            emotions=result.emotions,
            situations=result.situations,
            moods=result.moods,
            colors=result.colors
        )
        
        # 결과 캐시에 저장
        request_deduplicator.mark_request_completed(request_id, response.dict())
        
        return response
        
    except Exception as e:
        print(f"❌ Fast Context API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")
