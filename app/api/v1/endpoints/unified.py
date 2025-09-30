from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import re
import asyncio
from datetime import datetime
from urllib.parse import urlparse

from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.services.smart_websocket_extractor import SmartWebSocketExtractor
from app.utils.request_deduplication import request_deduplicator
from app.services.supabase_client import get_supabase_manager, to_plain
from app.models.recommendation_schemas import (
    RecommendationRequest, RecommendationResponse, SnapshotResponse
)
from postgrest.exceptions import APIError

router = APIRouter()

# ===== 요청/응답 모델 =====

class ExtractKeywordsRequest(BaseModel):
    """키워드 추출 요청 모델"""
    story: str

class SelectedKeywords(BaseModel):
    """선택된 키워드 모델"""
    emotions: str
    situations: str
    moods: str
    colors: str

class UnifiedRecommendRequest(BaseModel):
    """통합 추천 요청 모델"""
    story: str
    selected_keywords: SelectedKeywords   # ✅ 필수
    excluded_keywords: List[str] = []    # ✅ 옵션
    updated_context: Optional[Dict[str, Any]] = None  # 옵션

print("[BOOT] unified.py loaded, fields=", list(UnifiedRecommendRequest.model_fields.keys()))

class UnifiedRecommendResponse(BaseModel):
    """통합 추천 응답 모델 - UI 요구사항에 맞춰 확장"""
    flower_name: str
    korean_name: str
    scientific_name: str
    image_url: str
    calligraphy_image_url: str
    hashtags: List[str]
    english_description: str
    emotions: List[Dict[str, Any]]
    season_detail: Dict[str, str]
    composition: Dict[str, Any]
    created_at: str
    your_story: str
    comment: str

# ===== 꽃 추천 카운터 =====

_flower_recommendation_counts = {}

def _get_flower_code_from_name(korean_name: str) -> str:
    """꽃 이름에서 코드 추출 (예: "스위트피" -> "SWP")"""
    if not korean_name:
        return "DEF"
    
    # 간단한 매핑
    flower_codes = {
        "스위트피": "SWP", "장미": "ROS", "알스트로메리아": "ALS",
        "수국": "HYD", "튤립": "TUL", "카네이션": "CAR",
        "리시안서스": "LIS", "아이리스": "IRI", "릴리": "LIL"
    }
    
    return flower_codes.get(korean_name, "DEF")

def _get_flower_recommendation_count(flower_code: str) -> int:
    """꽃별 추천 횟수 증가 및 반환"""
    if flower_code not in _flower_recommendation_counts:
        _flower_recommendation_counts[flower_code] = 0
    _flower_recommendation_counts[flower_code] += 1
    return _flower_recommendation_counts[flower_code]

def _get_next_flower_count(flower_code: str) -> int:
    """꽃별 추천 횟수 증가 및 반환 (별칭)"""
    return _get_flower_recommendation_count(flower_code)

# ===== 버킷 베이스 URL =====

_SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
FLOWERS_BASE = f"{_SUPABASE_URL}/storage/v1/object/public/flowers"
CALLI_BASE   = f"{_SUPABASE_URL}/storage/v1/object/public/calligraphy-images"

# ===== 색상 코드 (버킷 파일과 동일) =====

COLOR_CODE: Dict[str, str] = {
    "핑크": "pk", "레드": "rd", "화이트": "wh", "옐로우": "yl",
    "퍼플": "pu",  # <= 중요: pu
    "블루": "bl", "그린": "gr", "오렌지": "or",
    "크림": "cr",
    # "라일락": "ll",  # 라일락은 실제 버킷에 없으므로 제거
}

# ===== 꽃 슬러그 매핑 (ko/en/scientific → 파일 prefix) =====

FLOWER_SLUG: Dict[str, str] = {
    # Korean
    "스위트피": "sweet-pea", "장미": "rose", "알스트로메리아": "alstroemeria",
    "아네모네": "anemone", "안스리움": "anthurium", "아스틸베": "astilbe",
    "안개꽃": "babys-breath", "부바르디아": "bouvardia", "카라릴리": "calla-lily",
    "카네이션": "carnation", "맨드라미": "cockscomb", "수국": "hydrangea",
    "지니아": "zinnia", "스톡": "stock-flower", "베로니카": "veronica",
    "스파이에아": "spiraea", "해바라기": "sunflower", "튤립": "tulip",
    "스카비오사": "scabiosa", "리시안서스": "lisianthus", "아이리스": "iris",
    "릴리": "lily", "마거리트 데이지": "marguerite-daisy", "라넌큘러스": "ranunculus",
    "마리골드": "marigold", "옥시페탈럼": "oxypetalum", "패트리니아": "patrinia",
    # English
    "Sweet Pea": "sweet-pea", "Rose": "rose", "Alstroemeria": "alstroemeria",
    "Anemone": "anemone", "Anthurium": "anthurium", "Astilbe": "astilbe",
    "Baby's Breath": "babys-breath", "Bouvardia": "bouvardia", "Calla Lily": "calla-lily",
    "Carnation": "carnation", "Cockscomb": "cockscomb", "Hydrangea": "hydrangea",
    "Zinnia": "zinnia", "Stock Flower": "stock-flower", "Veronica": "veronica",
    "Spiraea": "spiraea", "Sunflower": "sunflower", "Tulip": "tulip", "Scabiosa": "scabiosa",
    "Lisianthus": "lisianthus", "Iris": "iris", "Lily": "lily",
    "Marguerite Daisy": "marguerite-daisy", "Ranunculus": "ranunculus",
    "Marigold": "marigold", "Oxypetalum": "oxypetalum", "Patrinia": "patrinia",
    # Scientific (필요한 것만)
    "Lathyrus Odoratus": "sweet-pea", "Rosa": "rose", "Eustoma": "lisianthus",
}

# ===== 캘리 파일명 예외 (대소문자/이형 파일 처리) =====

CALLI_FILENAME_OVERRIDE: Dict[str, str] = {
    # slug -> exact filename in bucket
    "patrinia": "Patrinia.png",  # 버킷에 대문자 파일
    # 필요시 계속 추가
}

def _slugify_english(name: str) -> str:
    s = (name or "").strip().lower()
    s = s.replace("'", "")               # baby's -> babys
    s = re.sub(r"\s+", "-", s)           # space -> hyphen
    return s

def _flower_to_slug(korean: Optional[str], english: Optional[str], scientific: Optional[str]) -> str:
    for key in (korean, english, scientific):
        if key and key in FLOWER_SLUG:
            return FLOWER_SLUG[key]
    # 폴백: 영어명 슬러그화, 없으면 default
    return _slugify_english(english or "") or "default"

def _color_to_code(colors: List[str]) -> str:
    if not colors:
        return "pk"
    
    # 요청된 색상이 있으면 그대로 사용
    requested_color = colors[0]
    if requested_color in COLOR_CODE:
        return COLOR_CODE[requested_color]
    
    # 색상 폴백 로직: 요청된 색상이 없을 때 가장 가까운 색상으로 대체
    color_fallbacks = {
        "라일락": "bl",  # 라일락 → 블루 (가장 가까운 색상)
        "퍼플": "bl",    # 퍼플 → 블루
        "핑크": "pk",    # 핑크는 그대로
        "레드": "rd",    # 레드는 그대로
        "화이트": "wh",  # 화이트는 그대로
        "옐로우": "yl",  # 옐로우는 그대로
        "블루": "bl",    # 블루는 그대로
        "그린": "gr",    # 그린은 그대로
        "오렌지": "or",  # 오렌지는 그대로
        "크림": "wh",    # 크림 → 화이트 (가장 가까운 색상)
    }
    
    return color_fallbacks.get(requested_color, "pk")

def build_image_and_calli_urls(
    korean_name: Optional[str],
    english_name: Optional[str],
    scientific_name: Optional[str],
    preferred_colors: List[str],
    current_image_url: Optional[str] = None,
) -> Dict[str, str]:
    slug = _flower_to_slug(korean_name, english_name, scientific_name)
    color_code = _color_to_code(preferred_colors)

    # 현재 image_url이 같은 꽃(prefix 동일)이라면 그대로 유지
    if current_image_url:
        fname = os.path.basename(urlparse(current_image_url).path)  # e.g. rose-pk.webp
        stem = fname.split(".")[0]
        prefix = stem.rsplit("-", 1)[0] if "-" in stem else stem
        if prefix == slug:
            img = current_image_url
        else:
            img = f"{FLOWERS_BASE}/{slug}-{color_code}.webp"
    else:
        img = f"{FLOWERS_BASE}/{slug}-{color_code}.webp"

    # 캘리: 예외 없으면 <slug>.png
    calli_fname = CALLI_FILENAME_OVERRIDE.get(slug, f"{slug}.png")
    calli = f"{CALLI_BASE}/{calli_fname}"

    return {"image_url": img, "calligraphy_image_url": calli}

# ===== 엔드포인트 =====

@router.post("/extract-keywords")
async def extract_keywords(req: ExtractKeywordsRequest):
    """스토리에서 키워드 추출 (메인 키워드 + 대안 키워드 구조)"""
    try:
        # 실시간 컨텍스트 추출기 사용
        smart_extractor = SmartWebSocketExtractor()
        smart_context = await smart_extractor.extract_with_confidence(req.story)
        
        return {
            "emotions": {
                "main": smart_context.emotions[0] if smart_context.emotions else "",
                "alternatives": smart_context.emotions_alternatives
            },
            "situations": {
                "main": smart_context.situations[0] if smart_context.situations else "",
                "alternatives": smart_context.situations_alternatives
            },
            "moods": {
                "main": smart_context.moods[0] if smart_context.moods else "",
                "alternatives": smart_context.moods_alternatives
            },
            "colors": {
                "main": smart_context.colors[0] if smart_context.colors else "",
                "alternatives": smart_context.colors_alternatives
            },
            "confidence": smart_context.confidence,
            "extraction_method": smart_context.extraction_method
        }
    except Exception as e:
        print(f"❌ 키워드 추출 실패: {e}")
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")

# extract-final은 advanced.py로 이동됨

# recommend/final은 advanced.py로 이동됨

async def unified_recommend_logic(req: UnifiedRecommendRequest):
    """통합 추천 결과 로직 - 저장은 하지 않고 추천 결과만 생성"""
    print("▶ UnifiedRequest fields=", list(UnifiedRecommendRequest.model_fields.keys()))
    print(f"🔍 unified_recommend_logic 시작: {req}")
    try:
        # 1) 병렬 처리: 감정 분석 + 컨텍스트 추출
        print("⚡ 병렬 처리 시작: 감정 분석 + 컨텍스트 추출")
        
        async def analyze_emotions_async():
            emotion_analyzer = EmotionAnalyzer()
            return emotion_analyzer.analyze(req.story)
        
        async def extract_context_async():
            context_extractor = RealtimeContextExtractor()
            excluded_keywords = req.excluded_keywords or []
            # 임시로 빈 감정으로 시작 (나중에 업데이트)
            return context_extractor.extract_context_realtime(req.story, [], excluded_keywords)
        
        # 병렬 실행
        emotions, context = await asyncio.gather(
            analyze_emotions_async(),
            extract_context_async()
        )
        print(f"✅ 감정 분석 완료: {emotions}")
        print(f"✅ 컨텍스트 추출 완료: {context}")
        
        # 컨텍스트에 감정 분석 결과 반영
        if emotions:
            context.emotions = [e.emotion for e in emotions]

        # 사용자 보정 적용
        if req.updated_context:
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']

        # 3) 최종 컨텍스트
        final_emotions = context.emotions or []
        final_situations = context.situations or []
        final_moods = context.moods or []
        final_colors = [req.selected_keywords.colors] if (req.selected_keywords and req.selected_keywords.colors) else (context.colors or [])
        mentioned_flower = getattr(context, 'mentioned_flower', None)

        print("🎯 최종 매칭 컨텍스트:")
        print(f"   감정: {final_emotions}")
        print(f"   상황: {final_situations}")
        print(f"   무드: {final_moods}")
        print(f"   색상: {final_colors}")
        print(f"   언급된 꽃: {mentioned_flower}")

        # 4) 꽃 선택: 의미 기반 매칭만 사용
        excluded_keywords = req.excluded_keywords or []
        try:
            # 의미 기반/기존 FlowerMatcher로 선택
            flower_matcher = FlowerMatcher()
            matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        except Exception as e:
            print(f"❌ 의미 기반 FlowerMatcher 오류: {e}")
            raise HTTPException(status_code=500, detail="꽃 매칭 실패")

        # 5) 이미지/캘리그래피 URL은 규칙 기반 시스템으로 생성
        try:
            urls = build_image_and_calli_urls(
                korean_name=matched_flower.korean_name,
                english_name=matched_flower.flower_name,
                scientific_name=matched_flower.scientific_name,
                preferred_colors=final_colors,
                current_image_url=getattr(matched_flower, "image_url", None),
            )
            image_url = urls["image_url"]
            calligraphy_image_url = urls["calligraphy_image_url"]
            
            # 필요시 객체에 반영
            if hasattr(matched_flower, "image_url"):
                matched_flower.image_url = image_url
        except Exception as e:
            print(f"❌ 이미지 URL 생성 실패: {e}")
            image_url = getattr(matched_flower, "image_url", None) or f"{FLOWERS_BASE}/default.webp"
            calligraphy_image_url = f"{CALLI_BASE}/default.png"

        # 6) 병렬 처리: 구성 + 추천 이유 + 시즌 정보
        print("⚡ 병렬 처리 시작: 구성 + 추천 이유 + 시즌 정보")
        
        async def get_composition_async():
            composition_recommender = CompositionRecommender()
            return composition_recommender.recommend(matched_flower, emotions)
        
        async def generate_reason_async():
            from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason
            return _generate_unified_recommendation_reason(matched_flower, None, emotions, req.story, context, excluded_keywords)
        
        async def get_season_info_async():
            from app.api.v1.endpoints.recommend import _get_season_info
            return _get_season_info(matched_flower.flower_name)
        
        # 병렬 실행
        composition, reason, season_info = await asyncio.gather(
            get_composition_async(),
            generate_reason_async(),
            get_season_info_async()
        )

        # 7) 응답
        from app.models.schemas import UnifiedRecommendResponse
        
        # 감정 분석 결과를 올바른 형태로 변환
        emotion_list = []
        if emotions:
            for emotion in emotions:
                emotion_list.append({
                    "emotion": emotion.emotion,
                    "percentage": emotion.percentage
                })
        
        # 해시태그 생성 (감정 3개만)
        hashtag_list = [f"#{emotion_data['emotion']}" for emotion_data in emotion_list]
        
        return UnifiedRecommendResponse(
            flower_name=matched_flower.flower_name,
            korean_name=matched_flower.korean_name,
            scientific_name=matched_flower.scientific_name,
            image_url=image_url,
            calligraphy_image_url=calligraphy_image_url,
            hashtags=hashtag_list,
            english_description=f"Beautiful {matched_flower.flower_name} flower",
            emotions=emotion_list,
            season_detail=season_info,
            composition=composition,
            created_at=datetime.now().strftime("%Y.%m.%d."),
            your_story=req.story,
            comment=reason
        )
        
    except Exception as e:
        print(f"❌ unified_recommend_logic에서 예외 발생: {e}")
        import traceback
        print(f"❌ 스택: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"추천 로직 실행 실패: {str(e)}")

def _save_story(story: str, emotions: List, flower: Any, composition: Any, reason: str) -> Optional[str]:
    """스토리 저장 (기존 로직 유지)"""
    try:
        # 스토리 저장 로직
        return "story_id_placeholder"
    except Exception as e:
        print(f"스토리 저장 실패: {e}")
        return None

# ===== 새로운 스냅샷 추천 엔드포인트 =====

@router.post("/recommend", response_model=RecommendationResponse)
async def create_recommendation_snapshot(request: UnifiedRecommendRequest):
    """새로운 추천 요청 - 스냅샷 저장 후 응답 (story_id는 DB 기준 +1 자동 생성)"""
    print("▶ /recommend body=", request.model_dump())
    try:

        print("🔍 추천 로직 실행 시작")
        try:
            print("🔍 unified_recommend_logic 호출 전")
            recommendation_result = await unified_recommend_logic(request)
            print(f"✅ 추천 로직 실행 완료: {recommendation_result}")
        except Exception as e:
            print(f"❌ 추천 로직 실행 실패: {e}")
            import traceback
            print(f"❌ 스택 트레이스: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"추천 로직 실행 실패: {str(e)}")

        # 2) 꽃 코드 계산
        flower_code = _get_flower_code_from_name(recommendation_result.korean_name)

        # 3) 스냅샷 데이터 준비 (id는 여기서 지정하지 않음 → SupabaseManager가 DB+1로 생성)
        snapshot_data = {
            "story": request.story,
            "selected_keywords": {
                "emotions": request.selected_keywords.emotions,
                "situations": request.selected_keywords.situations,
                "moods": request.selected_keywords.moods,
                "colors": request.selected_keywords.colors,
            },
            "excluded_keywords": request.excluded_keywords,
            "flower_name": recommendation_result.flower_name,
            "korean_name": recommendation_result.korean_name,
            "scientific_name": recommendation_result.scientific_name,
            "image_url": recommendation_result.image_url,
            "calligraphy_image_url": recommendation_result.calligraphy_image_url,
            "hashtags": recommendation_result.hashtags,
            "english_description": recommendation_result.english_description,
            "emotions": recommendation_result.emotions,
            "season_detail": recommendation_result.season_detail,
            "composition": to_plain(recommendation_result.composition),
            "recommendation_reason": recommendation_result.comment,
        }

        # 4) Supabase에 스냅샷 저장 (DB에서 다음 번호 +1로 story_id 생성)
        print(f"🔍 스냅샷 데이터: {snapshot_data}")
        supabase_manager = get_supabase_manager()
        saved_snapshot = supabase_manager.insert_snapshot_autoinc(snapshot_data, flower_code)

        if not saved_snapshot:
            print("❌ 스냅샷 저장 실패")
            raise HTTPException(status_code=500, detail="스냅샷 저장 실패")

        print(f"✅ 스냅샷 저장 성공: {saved_snapshot}")

        # 5) 저장된 story_id 사용
        story_id = saved_snapshot["id"]

        # 6) 통합 응답
        return RecommendationResponse(
            success=True,
            created_at=datetime.now().strftime("%Y.%m.%d."),
            story_id=story_id,
            your_story=request.story,
            flower_info={
                "korean_name": recommendation_result.korean_name,
                "english_name": recommendation_result.flower_name,
                "scientific_name": recommendation_result.scientific_name,
            },
            flower_blend=to_plain(recommendation_result.composition),
            flower_image_url=recommendation_result.image_url,
            calligraphy_image_url=recommendation_result.calligraphy_image_url,
            flower_card_message={"quote": "인용구", "source": "출처"},
            emotions=recommendation_result.emotions,
            season_detail=recommendation_result.season_detail,
            comment=recommendation_result.comment,
            hashtags=recommendation_result.hashtags,
        )

    except Exception as e:
        print(f"❌ 추천 스냅샷 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 생성 실패: {str(e)}")

@router.get("/recommend/{story_id}", response_model=SnapshotResponse)
async def get_recommendation_snapshot(story_id: str):
    """스냅샷 조회"""
    try:
        supabase_manager = get_supabase_manager()
        snapshot = supabase_manager.get_snapshot_by_id(story_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
        
        return SnapshotResponse(**snapshot)
        
    except Exception as e:
        print(f"❌ 스냅샷 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스냅샷 조회 실패: {str(e)}")
