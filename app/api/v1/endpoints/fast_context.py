"""
매우 간단하고 빠른 실시간 키워드 추출 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

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
    """매우 간단하고 빠른 키워드 추출"""
    try:
        story = request.story.lower()
        
        # 매우 간단한 규칙 기반 추출
        emotions = ["기쁨"]
        situations = ["일상"]
        moods = ["따뜻한"]
        colors = ["화이트"]
        
        # 간단한 키워드 매칭
        if "생일" in story or "축하" in story:
            emotions = ["기쁨"]
            situations = ["생일"]
            moods = ["밝은"]
            colors = ["핑크"]
        elif "고백" in story or "사랑" in story or "연인" in story:
            emotions = ["사랑"]
            situations = ["연인"]
            moods = ["로맨틱한"]
            colors = ["레드"]
        elif "위로" in story or "슬픔" in story or "아픔" in story:
            emotions = ["위로"]
            situations = ["위로"]
            moods = ["따뜻한"]
            colors = ["화이트"]
        elif "감사" in story or "고마워" in story or "감사해" in story:
            emotions = ["감사"]
            situations = ["감사"]
            moods = ["따뜻한"]
            colors = ["옐로우"]
        elif "친구" in story or "우정" in story:
            emotions = ["우정"]
            situations = ["친구"]
            moods = ["따뜻한"]
            colors = ["옐로우"]
        elif "가족" in story or "부모" in story or "어머니" in story or "아버지" in story:
            emotions = ["사랑"]
            situations = ["가족"]
            moods = ["따뜻한"]
            colors = ["핑크"]
        elif "취업" in story or "승진" in story or "성공" in story:
            emotions = ["희망"]
            situations = ["성공"]
            moods = ["밝은"]
            colors = ["옐로우"]
        elif "졸업" in story or "입학" in story:
            emotions = ["희망"]
            situations = ["졸업"]
            moods = ["밝은"]
            colors = ["화이트"]
        elif "결혼" in story or "결혼식" in story:
            emotions = ["사랑"]
            situations = ["결혼"]
            moods = ["로맨틱한"]
            colors = ["화이트"]
        elif "핑크" in story or "분홍" in story:
            colors = ["핑크"]
        elif "빨간" in story or "레드" in story:
            colors = ["레드"]
        elif "노란" in story or "옐로우" in story or "노랑" in story:
            colors = ["옐로우"]
        elif "파란" in story or "블루" in story or "파랑" in story:
            colors = ["블루"]
        elif "보라" in story or "퍼플" in story:
            colors = ["퍼플"]
        elif "주황" in story or "오렌지" in story:
            colors = ["오렌지"]
        elif "고급" in story or "우아" in story:
            moods = ["고급스러운"]
        elif "화려" in story or "밝은" in story:
            moods = ["화려한"]
        elif "심플" in story or "간단" in story:
            moods = ["심플한"]
        elif "부드러운" in story or "따뜻한" in story:
            moods = ["따뜻한"]
        
        return FastContextResponse(
            emotions=emotions,
            situations=situations,
            moods=moods,
            colors=colors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")
