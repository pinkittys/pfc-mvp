from fastapi import APIRouter, Depends
from app.models.schemas import KeywordRequest, KeywordResponse
from app.services.keyword_extractor import KeywordExtractor

router = APIRouter()

def get_extractor() -> KeywordExtractor:
    return KeywordExtractor()

@router.post("/extract_keywords", response_model=KeywordResponse)
def extract_keywords(req: KeywordRequest, extractor: KeywordExtractor = Depends(get_extractor)):
    return extractor.run(req.story)
