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

        # 4) 꽃 선택: SpreadsheetFlowerMatcher 사용 (정교한 매칭)
        excluded_keywords = req.excluded_keywords or []
        alternative_flower_notice = None  # 대체 꽃 안내 메시지
        
        try:
            # SpreadsheetFlowerMatcher 사용 (문자열 리스트 지원)
            from app.services.spreadsheet_flower_matcher import SpreadsheetFlowerMatcher
            
            spreadsheet_matcher = SpreadsheetFlowerMatcher()
            
            # 스프레드시트 매칭 실행
            match_result = spreadsheet_matcher.match_flower(
                story=req.story,
                emotions=final_emotions,
                situations=final_situations,
                moods=final_moods,
                preferred_colors=final_colors,
                mentioned_flower=mentioned_flower
            )
            
            if match_result:
                print(f"✅ 스프레드시트 매칭 성공: {match_result.flower_data.name_ko}")
                
                # 언급된 꽃과 매칭된 꽃이 다른 경우 안내 메시지 추가
                # (한글 이름과 영어 이름 모두 비교)
                if mentioned_flower:
                    mentioned_lower = mentioned_flower.lower()
                    matched_ko = match_result.flower_data.name_ko.lower()
                    matched_en = match_result.flower_data.name_en.lower()
                    
                    # 언급된 꽃이 매칭된 꽃의 한글/영어 이름과 모두 다른 경우에만 안내
                    if mentioned_lower != matched_ko and mentioned_lower != matched_en:
                        # 라벤더 특별 처리
                        if mentioned_flower.lower() in ['라벤더', '라벤다', 'lavender']:
                            alternative_flower_notice = f"💜 '{mentioned_flower}'은(는) 현재 준비 중이에요. 비슷한 진정 효과를 가진 '{match_result.flower_data.name_ko}'을(를) 추천드려요. 라벤더의 차분한 향기처럼 마음을 진정시켜줄 거예요."
                        else:
                            alternative_flower_notice = f"💡 '{mentioned_flower}'은(는) 현재 준비 중이에요. 비슷한 느낌의 '{match_result.flower_data.name_ko}'을(를) 추천드려요."
                        print(f"💡 대체 꽃 추천: {mentioned_flower} → {match_result.flower_data.name_ko}")
                    else:
                        print(f"✅ 언급된 꽃과 매칭된 꽃이 동일: {mentioned_flower} = {match_result.flower_data.name_ko}")
                
                # SpreadsheetMatchResult를 MatchedFlower로 변환
                from app.models.schemas import MatchedFlower
                matched_flower = MatchedFlower(
                    flower_name=match_result.flower_data.name_en,
                    korean_name=match_result.flower_data.name_ko,
                    scientific_name=match_result.flower_data.scientific_name,
                    image_url=match_result.image_url,
                    confidence=match_result.confidence,
                    match_reason=match_result.match_reason,
                    color_keywords=[match_result.flower_data.base_color] + match_result.flower_data.alt_colors,
                    keywords=match_result.flower_data.flower_language_short or match_result.flower_data.flower_language_long or "아름다움과 마음을 담아 전해요"
                )
            else:
                print("⚠️ 스프레드시트 매칭 실패, 기본 꽃 사용")
                # 폴백: 기본 꽃 선택
                from app.models.schemas import MatchedFlower
                matched_flower = MatchedFlower(
                    flower_name="Lavender",
                    korean_name="라벤더", 
                    scientific_name="Lavandula spp.",
                    image_url="https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/lavender-purple.webp",
                    confidence=0.8,
                    match_reason="위로와 평온을 상징하는 라벤더",
                    color_keywords=["퍼플", "라벤더"],
                    keywords="위로, 평온, 힐링"
                )
            
        except Exception as e:
            print(f"❌ 꽃 매칭 오류: {e}")
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
            # 원래 CompositionRecommender 사용
            from app.services.composition_recommender import CompositionRecommender
            from app.models.schemas import EmotionAnalysis
            
            # EmotionAnalysis 객체 생성
            emotion_objects = []
            for i, emotion in enumerate(final_emotions[:3]):  # 상위 3개 감정만 사용
                emotion_objects.append(EmotionAnalysis(
                    emotion=emotion,
                    percentage=100.0 / len(final_emotions[:3])  # 균등 분배
                ))
            
            # CompositionRecommender로 구성 생성
            composition_recommender = CompositionRecommender()
            composition = composition_recommender.recommend(matched_flower, emotion_objects)
            
            return {
                "main_flower": matched_flower.korean_name,
                "sub_flowers": composition.sub_flowers,
                "composition_name": composition.composition_name
            }
        
        async def generate_reason_async():
            # GPT를 사용한 추천 이유 생성
            from openai import AsyncOpenAI
            import os
            
            try:
                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # 프롬프트 구성
                prompt = f"""당신은 꽃집 전문가입니다. 고객의 사연에 맞춰 왜 이 꽃을 추천하는지 따뜻하고 진심 어린 이유를 2-3문장으로 작성해주세요.

**고객 사연**: {req.story}

**선택된 감정**: {", ".join(final_emotions[:3]) if final_emotions else "특별한 마음"}
**상황**: {final_situations[0] if final_situations else "소중한 순간"}
**무드**: {final_moods[0] if final_moods else "따뜻한"}

**추천 꽃**: {matched_flower.korean_name}
**꽃말**: {matched_flower.keywords if matched_flower.keywords else "아름다움과 진심"}

**중요**: 
- 반말이 아닌 "~에요", "~예요" 존댓말 사용
- "~습니다" 같은 격식 있는 어투 사용 금지
- 담백하고 진솔하게, 친구에게 말하듯 편안한 어조
- 불필요하게 과장하지 말고 진심 어린 추천"""

                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 감성적이고 따뜻한 꽃집 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=200
                )
                
                base_reason = response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"❌ GPT 추천 이유 생성 실패: {e}")
                # 폴백: 간단한 템플릿 사용
                emotion_text = ", ".join(final_emotions[:2]) if final_emotions else "특별한 마음"
                base_reason = f"{matched_flower.korean_name}은(는) {emotion_text}을 담기에 완벽한 꽃입니다. {matched_flower.keywords if matched_flower.keywords else '진심을 전하기에 좋은 선택'}입니다."
            
            # 대체 꽃 안내 메시지가 있으면 앞에 추가
            if alternative_flower_notice:
                return f"{alternative_flower_notice}\n\n{base_reason}"
            
            return base_reason
        
        async def get_season_info_async():
            # 간단한 계절 정보
            return {
                "season": "Spring/Summer",
                "months": "04-09"
            }
        
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
        for emotion in final_emotions:
            emotion_list.append({
                "emotion": emotion,
                "percentage": 100.0 / len(final_emotions) if final_emotions else 100.0
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
    """스냅샷 조회 - story_id로 저장된 추천 결과 조회"""
    try:
        supabase_manager = get_supabase_manager()
        
        # Supabase에서 스냅샷 조회
        result = supabase_manager.read.table("recommendation_snapshots").select("*").eq("id", story_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="추천 결과를 찾을 수 없습니다")
        
        snapshot = result.data[0]
        
        # SnapshotResponse 형식으로 변환
        return SnapshotResponse(
            success=True,
            created_at=snapshot.get("created_at", ""),
            story_id=snapshot.get("id", story_id),
            your_story=snapshot.get("story", ""),
            flower_info={
                "korean_name": snapshot.get("korean_name", ""),
                "english_name": snapshot.get("english_name", ""),
                "scientific_name": snapshot.get("scientific_name", "")
            },
            flower_blend=snapshot.get("composition", {}),
            flower_image_url=snapshot.get("image_url", ""),
            calligraphy_image_url=snapshot.get("calligraphy_image_url", ""),
            flower_card_message=snapshot.get("flower_card_message", {"quote": "", "source": ""}),
            emotions=snapshot.get("emotions", []),
            season_detail=snapshot.get("season_detail", {}),
            comment=snapshot.get("recommendation_reason", ""),
            hashtags=snapshot.get("hashtags", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 스냅샷 조회 실패: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"스냅샷 조회 실패: {str(e)}")
