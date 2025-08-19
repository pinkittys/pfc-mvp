"""
사연 샘플 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import random
from pydantic import BaseModel

router = APIRouter()

class StorySample(BaseModel):
    id: str
    text: str
    category: str
    tags: List[str]

# 사연 샘플 데이터
STORY_SAMPLES = [
    {
        "id": "sample_1",
        "text": "예전에 이 친구랑 파리 여행 갔던 게 기억나. 그때 분위기를 담고 싶어.",
        "category": "추억",
        "tags": ["여행", "추억", "로맨틱", "파리"]
    },
    {
        "id": "sample_2", 
        "text": "조용하고 차분한 성격에 책 읽는 걸 좋아하는 친구에게 선물하고 싶어.",
        "category": "친구",
        "tags": ["차분한", "책", "친구", "은은한"]
    },
    {
        "id": "sample_3",
        "text": "첫사랑에게 고백하려고 해요. 수줍고 설레는 마음을 담아서 핑크나 화이트 톤이 좋겠어요.",
        "category": "사랑",
        "tags": ["고백", "첫사랑", "설렘", "핑크", "화이트"]
    },
    {
        "id": "sample_4",
        "text": "부모님께 감사한 마음을 전하고 싶어요. 따뜻하고 진심어린 느낌으로 빨간색이나 핑크 톤이 좋겠어요.",
        "category": "감사",
        "tags": ["부모님", "감사", "진심", "따뜻한", "레드", "핑크"]
    },
    {
        "id": "sample_5",
        "text": "친구가 갑작스럽게 반려견을 떠나보냈어요. 차분하고 위로가 되는 색감이면 좋겠어요.",
        "category": "위로",
        "tags": ["반려견", "위로", "슬픔", "차분한", "따뜻한"]
    },
    {
        "id": "sample_6",
        "text": "베프 생일이에요! 밝고 경쾌한 느낌으로 노랑이나 오렌지 톤의 꽃다발을 원해요.",
        "category": "축하",
        "tags": ["생일", "베프", "기쁨", "밝은", "옐로우", "오렌지"]
    },
    {
        "id": "sample_7",
        "text": "새로운 직장에 입사하는 동생에게 응원의 마음을 담아서 선물하고 싶어요.",
        "category": "응원",
        "tags": ["입사", "동생", "응원", "새로운 시작", "희망"]
    },
    {
        "id": "sample_8",
        "text": "오랜 시간 함께한 연인과의 기념일을 위해 특별한 꽃다발을 준비하고 싶어요.",
        "category": "기념일",
        "tags": ["연인", "기념일", "특별한", "로맨틱", "사랑"]
    },
    {
        "id": "sample_9",
        "text": "힘든 시기를 겪고 있는 친구에게 따뜻한 위로와 응원을 전하고 싶어요.",
        "category": "위로",
        "tags": ["힘든 시기", "친구", "위로", "응원", "따뜻한"]
    },
    {
        "id": "sample_10",
        "text": "할머니께 드릴 선물로 차분하고 고급스러운 느낌의 꽃다발을 원해요.",
        "category": "경로",
        "tags": ["할머니", "경로", "고급스러운", "차분한", "존경"]
    }
]

@router.get("/samples", response_model=List[StorySample])
async def get_story_samples(count: Optional[int] = 10):
    """
    사연 샘플 목록을 반환합니다.
    
    Args:
        count: 반환할 샘플 개수 (기본값: 10, 최대: 50)
    
    Returns:
        랜덤으로 선택된 사연 샘플 목록
    """
    if count > 50:
        count = 50
    
    # 랜덤으로 샘플 선택
    selected_samples = random.sample(STORY_SAMPLES, min(count, len(STORY_SAMPLES)))
    
    return [StorySample(**sample) for sample in selected_samples]

@router.get("/samples/random", response_model=StorySample)
async def get_random_story_sample():
    """
    랜덤 사연 샘플 1개를 반환합니다.
    
    Returns:
        랜덤으로 선택된 사연 샘플
    """
    sample = random.choice(STORY_SAMPLES)
    return StorySample(**sample)

@router.get("/samples/category/{category}", response_model=List[StorySample])
async def get_story_samples_by_category(category: str, count: Optional[int] = 10):
    """
    카테고리별 사연 샘플을 반환합니다.
    
    Args:
        category: 카테고리명
        count: 반환할 샘플 개수
    
    Returns:
        해당 카테고리의 사연 샘플 목록
    """
    filtered_samples = [s for s in STORY_SAMPLES if s["category"] == category]
    
    if not filtered_samples:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    selected_samples = random.sample(filtered_samples, min(count, len(filtered_samples)))
    return [StorySample(**sample) for sample in selected_samples]


