"""
추천 API용 Pydantic 모델들
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# ===== 요청 모델 =====

class SelectedKeywords(BaseModel):
    """최종 선택된 키워드"""
    emotions: str
    situations: str
    moods: str
    colors: str

class RecommendationRequest(BaseModel):
    """추천 요청 모델"""
    story: str
    selected_keywords: SelectedKeywords
    excluded_keywords: List[str] = []

# ===== 응답 모델 =====

class FlowerInfo(BaseModel):
    """꽃 정보"""
    korean_name: str
    english_name: str
    scientific_name: str

class SeasonDetail(BaseModel):
    """계절 정보"""
    availability: str
    best_season: str

class EmotionAnalysis(BaseModel):
    """감정 분석 결과"""
    primary_emotion: str
    confidence: float
    related_emotions: List[str]

class FlowerComposition(BaseModel):
    """꽃다발 구성"""
    main_flower: str
    sub_flowers: List[str]
    accent_flowers: List[str]
    total_flowers: int

class RecommendationResponse(BaseModel):
    """추천 응답 모델 (샘플 스토리와 동일한 구조)"""
    success: bool = True
    created_at: str  # "2025.09.17." 형식
    story_id: str
    your_story: str
    
    # 꽃 정보
    flower_info: Dict[str, str]  # {"korean_name": "지니아", "english_name": "zinnia", "scientific_name": "Zinnia elegans"}
    
    # 꽃다발 구성
    flower_blend: Dict[str, Any]  # {"main_flower": "지니아", "sub_flowers": [...], "composition_name": "구성명"}
    
    # 이미지 URL
    flower_image_url: str
    calligraphy_image_url: str
    
    # 꽃카드 메시지
    flower_card_message: Dict[str, str]  # {"quote": "인용구", "source": "출처"}
    
    # 감정 분석
    emotions: List[Dict[str, Any]]  # [{"emotion": "기쁨", "percentage": 40.0}, ...]
    
    # 계절 정보
    season_detail: Dict[str, str]  # {"availability": "Spring/Summer", "best_season": "03-08"}
    
    # 추천 이유
    comment: str
    hashtags: List[str]

class SnapshotResponse(BaseModel):
    """스냅샷 조회 응답 모델 (RecommendationResponse와 동일한 구조)"""
    success: bool = True
    created_at: str
    story_id: str
    your_story: str
    
    # 꽃 정보
    flower_info: Dict[str, str]
    
    # 꽃다발 구성
    flower_blend: Dict[str, Any]
    
    # 이미지 URL
    flower_image_url: str
    calligraphy_image_url: str
    
    # 꽃카드 메시지
    flower_card_message: Dict[str, str]
    
    # 감정 분석
    emotions: List[Dict[str, Any]]
    
    # 계절 정보
    season_detail: Dict[str, str]
    
    # 추천 이유
    comment: str
    hashtags: List[str]

# ===== 내부 모델 =====

class RecommendationSnapshot(BaseModel):
    """Supabase 저장용 스냅샷 모델"""
    id: str
    story: str
    selected_keywords: Dict[str, str]
    excluded_keywords: List[str]
    
    # 추천 결과
    flower_name: Optional[str] = None
    korean_name: Optional[str] = None
    scientific_name: Optional[str] = None
    image_url: Optional[str] = None
    calligraphy_image_url: Optional[str] = None
    hashtags: Optional[List[str]] = None
    english_description: Optional[str] = None
    emotions: Optional[List[Dict[str, Any]]] = None
    season_detail: Optional[Dict[str, str]] = None
    composition: Optional[Dict[str, Any]] = None
    recommendation_reason: Optional[str] = None
    
    # 메타데이터
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
