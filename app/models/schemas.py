from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 새로운 키워드 구조 스키마 추가
class KeywordWithAlternatives(BaseModel):
    """메인 키워드와 대안 키워드를 포함하는 구조"""
    main: str  # 메인 키워드
    alternatives: List[str]  # 대안 키워드 2-3개

class KeywordDimension(BaseModel):
    """각 디멘션별 키워드 구조"""
    emotions: List[KeywordWithAlternatives] = []      # 감정 디멘션
    situations: List[KeywordWithAlternatives] = []    # 상황 디멘션
    moods: List[KeywordWithAlternatives] = []         # 무드 디멘션
    colors: List[KeywordWithAlternatives] = []        # 색상 디멘션

class KeywordExtractionResponse(BaseModel):
    """키워드 추출 응답"""
    success: bool
    keywords: KeywordDimension
    confidence: float
    message: str = ""

class FlowerCardMessage(BaseModel):
    """꽃 카드 메시지 구조 (인용구 + 출처 분리)"""
    quote: str      # 인용구
    source: str     # 출처

class KeywordRequest(BaseModel):
    story: str

class KeywordResponse(BaseModel):
    keywords: List[str]
    mood_tags: List[str] = []
    occasion: Optional[str] = None

class RecommendRequest(BaseModel):
    story: str
    preferred_colors: List[str] = []
    excluded_flowers: List[str] = []
    top_k: int = Field(default=1, ge=1, le=3)  # MVP에서는 1개만 추천
    selected_keywords: Optional[Dict[str, List[str]]] = None  # 선택된 키워드 (emotions, situations, moods, colors)
    excluded_keywords: Optional[List[Dict[str, str]]] = None  # 제외된 키워드 (text, type)
    updated_context: Optional[Dict[str, List[str]]] = None  # 업데이트된 컨텍스트 (emotions, situations, moods, colors)

class RecommendationItem(BaseModel):
    id: str
    template_id: Optional[str] = None
    name: str
    main_flowers: List[str]
    sub_flowers: List[str] = []
    color_theme: List[str] = []
    reason: str
    image_url: str
    # 추가 정보들
    original_story: Optional[str] = None  # 원본 스토리
    extracted_keywords: Optional[List[str]] = None  # 추출된 키워드 (해시태그)
    flower_keywords: Optional[List[str]] = None  # 꽃 키워드 (꽃말)
    season_info: Optional[Dict[str, str]] = None  # 시즌 정보 (시즌과 월 분리)
    english_message: Optional[str] = None  # 영어 메시지
    recommendation_reason: Optional[str] = None  # 상세 추천 이유

class EmotionAnalysis(BaseModel):
    emotion: str
    percentage: float

class RecommendResponse(BaseModel):
    recommendations: List[RecommendationItem]
    emotions: Optional[List[EmotionAnalysis]] = None  # 감정 분석 결과 추가
    story_id: Optional[str] = None  # 스토리 ID 추가
    
    # 새로운 키워드 구조 추가
    extracted_keywords: Optional[KeywordDimension] = None  # 추출된 키워드 (메인 + 대안)
    final_keywords: Optional[Dict[str, List[str]]] = None  # 최종 선택된 키워드

class FlowerMatch(BaseModel):
    flower_name: str
    korean_name: str
    scientific_name: str
    image_url: str
    keywords: List[str]
    hashtags: List[str]
    color_keywords: List[str] = []  # 색상 키워드 추가

class FlowerComposition(BaseModel):
    main_flower: str
    sub_flowers: List[str]
    composition_name: str

class EmotionAnalysisResponse(BaseModel):
    emotions: List[EmotionAnalysis]
    matched_flower: FlowerMatch
    composition: FlowerComposition
    recommendation_reason: str
    flower_card_message: Optional[FlowerCardMessage] = None  # 인용구 + 출처 분리
    story_id: Optional[str] = None  # 스토리 ID 추가
    
    # 새로운 키워드 구조 추가
    extracted_keywords: Optional[KeywordDimension] = None  # 추출된 키워드 (메인 + 대안)
    final_keywords: Optional[str] = None  # 최종 선택된 키워드

class FlowerInfo(BaseModel):
    """꽃 정보 모델"""
    name: str
    display_name: str
    colors: List[str]
    image_count: int
    images: List[Dict[str, str]] = []
    folder: str  # 폴더명
    default_color: str  # 기본 색상

class AdminResponse(BaseModel):
    """관리자 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class FlowerDictionary(BaseModel):
    """꽃 사전 모델"""
    id: str  # 학명-컬러 기준 ID (예: "Rosa-Red", "Tulipa-White")
    scientific_name: str  # 학명
    korean_name: str  # 한국어 이름
    color: str  # 색상
    flower_meanings: Dict[str, List[str]]  # 꽃말 (주의미, 보조의미, 기타의미, 문장형꽃말)
    moods: Dict[str, List[str]]  # 무드 (주무드, 보조무드, 기타무드)
    characteristics: Dict[str, List[str]]  # 기타 (주의점, 향기, 특징)
    cultural_references: Dict[str, List[str]]  # 꽃 관련 일화 (영화, 책, 문학, 고전, 연예, 드라마)
    design_compatibility: List[str]  # 디자인적 궁합이 좋은 꽃 목록
    design_incompatibility: List[str]  # 궁합이 좋지 않은 꽃 목록
    seasonality: List[str]  # 계절성
    care_level: str  # 관리 난이도
    lifespan: str  # 수명
    created_at: str  # 생성일
    updated_at: str  # 업데이트일
    source: str  # 정보 출처
    
    # 새로운 필드들 - 상황별 사용 빈도 및 관계별 적합성
    usage_contexts: Dict[str, Dict[str, str]] = {}  # 상황별 사용 빈도 (예: graduation, parents_day, wedding)
    relationship_suitability: Dict[str, Dict[str, str]] = {}  # 관계별 적합성 (예: parent_child, teacher_student, romantic)
    seasonal_events: List[str] = []  # 계절별 주요 이벤트 (예: spring_graduation, autumn_entrance)
    cultural_significance: Dict[str, List[str]] = {}  # 문화적 의미 (예: korean_tradition, western_culture)
    popularity_by_occasion: Dict[str, str] = {}  # 행사별 인기도 (예: "graduation": "very_popular", "wedding": "popular")

class FlowerDictionarySearchRequest(BaseModel):
    """꽃 사전 검색 요청"""
    query: str  # 검색 쿼리
    context: Optional[str] = None  # 추가 컨텍스트
    limit: int = 10  # 검색 결과 제한

class FlowerDictionaryUpdateRequest(BaseModel):
    """꽃 사전 업데이트 요청"""
    flower_id: str
    update_fields: Dict[str, Any]  # 업데이트할 필드들

class FlowerDictionaryResponse(BaseModel):
    """꽃 사전 응답"""
    success: bool
    message: str
    data: Optional[FlowerDictionary] = None
    total_count: Optional[int] = None

class StoryData(BaseModel):
    """스토리 데이터 모델 - URL 공유를 위한 완전한 정보"""
    story_id: str  # S{YYYYMMDD}{꽃이름앞3글자}{6자리순번}
    original_story: str  # 사용자가 입력한 원본 스토리
    created_at: datetime  # 생성 시간
    updated_at: Optional[datetime] = None  # 수정 시간
    
    # 감정 분석 결과
    emotions: List[EmotionAnalysis]
    
    # 꽃 정보
    flower_name: str  # 한글 이름
    flower_name_en: str  # 영문 이름
    scientific_name: str  # 학명
    flower_card_message: FlowerCardMessage  # 인용구 + 출처 분리
    
    # 꽃 조합 정보
    flower_blend: FlowerComposition
    
    # 계절 정보
    season_info: Dict[str, str]
    
    # 추천 코멘트
    recommendation_reason: str
    
    # 이미지 정보
    flower_image_url: str
    
    # 추가 메타데이터
    keywords: List[str] = []  # 추출된 키워드들
    hashtags: List[str] = []  # 해시태그
    color_keywords: List[str] = []  # 색상 키워드
    excluded_keywords: List[Dict[str, str]] = []  # 제외된 키워드들

class StoryCreateRequest(BaseModel):
    """스토리 생성 요청"""
    story: str
    emotions: List[EmotionAnalysis]
    matched_flower: FlowerMatch
    composition: FlowerComposition
    recommendation_reason: str
    flower_card_message: Optional[FlowerCardMessage] = None
    season_info: Optional[Dict[str, str]] = None
    keywords: List[str] = []
    hashtags: List[str] = []
    color_keywords: List[str] = []
    excluded_keywords: List[Dict[str, str]] = []

class StoryResponse(BaseModel):
    """스토리 응답"""
    success: bool
    message: str
    data: Optional[StoryData] = None

class StoryShareRequest(BaseModel):
    """스토리 공유 요청"""
    story_id: str

class StoryShareResponse(BaseModel):
    """스토리 공유 응답"""
    success: bool
    message: str
    data: Optional[StoryData] = None
    share_url: Optional[str] = None
