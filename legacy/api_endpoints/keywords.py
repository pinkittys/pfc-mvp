from fastapi import APIRouter, Depends
from app.models.schemas import KeywordRequest, KeywordExtractionResponse, KeywordWithAlternatives, KeywordDimension
from app.services.realtime_context_extractor import RealtimeContextExtractor

router = APIRouter()

def get_realtime_extractor() -> RealtimeContextExtractor:
    return RealtimeContextExtractor()

@router.post("/extract_keywords", response_model=KeywordExtractionResponse)
def extract_keywords(req: KeywordRequest, extractor: RealtimeContextExtractor = Depends(get_realtime_extractor)):
    """통합된 키워드 추출 API (메인 키워드 + 대안 키워드)"""
    try:
        # 실시간 컨텍스트 추출
        context = extractor.extract_context_realtime(req.story)
        
        # 새로운 키워드 구조로 변환
        from app.models.schemas import KeywordWithAlternatives, KeywordDimension
        
        # 감정 키워드 변환
        emotions = []
        if context.emotions and context.emotions_alternatives:
            emotions.append(KeywordWithAlternatives(
                main=context.emotions[0],
                alternatives=context.emotions_alternatives
            ))
        
        # 상황 키워드 변환
        situations = []
        if context.situations and context.situations_alternatives:
            situations.append(KeywordWithAlternatives(
                main=context.situations[0],
                alternatives=context.situations_alternatives
            ))
        
        # 무드 키워드 변환
        moods = []
        if context.moods and context.moods_alternatives:
            moods.append(KeywordWithAlternatives(
                main=context.moods[0],
                alternatives=context.moods_alternatives
            ))
        
        # 색상 키워드 변환
        colors = []
        if context.colors and context.colors_alternatives:
            colors.append(KeywordWithAlternatives(
                main=context.colors[0],
                alternatives=context.colors_alternatives
            ))
        
        # 키워드 디멘션 생성
        keyword_dimension = KeywordDimension(
            emotions=emotions,
            situations=situations,
            moods=moods,
            colors=colors
        )
        
        return KeywordExtractionResponse(
            success=True,
            keywords=keyword_dimension,
            confidence=context.confidence,
            message="키워드 추출 완료"
        )
        
    except Exception as e:
        return KeywordExtractionResponse(
            success=False,
            keywords=KeywordDimension(),
            confidence=0.0,
            message=f"키워드 추출 실패: {str(e)}"
        )
