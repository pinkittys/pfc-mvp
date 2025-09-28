from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime

from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.services.smart_websocket_extractor import SmartWebSocketExtractor
from app.utils.request_deduplication import request_deduplicator
from app.services.supabase_client import get_supabase_manager
from app.models.recommendation_schemas import (
    RecommendationRequest, RecommendationResponse, SnapshotResponse
)

router = APIRouter()

# 꽃별 추천 횟수 추적을 위한 전역 변수 (※ /recommend/final 에서만 사용 중)
_flower_recommendation_counts = {}

def _get_flower_recommendation_count(flower_code: str) -> int:
    """꽃별 추천 횟수 증가 및 반환 (메모리 카운터 - /recommend 최종 저장은 DB+1 방식을 사용)"""
    if flower_code not in _flower_recommendation_counts:
        _flower_recommendation_counts[flower_code] = 0
    _flower_recommendation_counts[flower_code] += 1
    return _flower_recommendation_counts[flower_code]

# ===== 요청/응답 모델 =====

class ExtractKeywordsRequest(BaseModel):
    """키워드 추출 요청 모델"""
    story: str

class UnifiedRecommendRequest(BaseModel):
    """통합 추천 요청 모델"""
    story: str
    preferred_colors: List[str] = []
    excluded_flowers: List[str] = []
    updated_context: Optional[Dict[str, Any]] = None

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
    story_id: Optional[str] = None

@router.post("/extract-keywords")
async def extract_keywords(req: ExtractKeywordsRequest):
    """통합 키워드 추출 엔드포인트 - 스마트 추출 방식으로 통합"""
    try:
        return await extract_smart(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")

async def extract_smart(req: ExtractKeywordsRequest):
    """스마트 키워드 추출 - 실시간/최종 통합 방식"""
    smart_extractor = SmartWebSocketExtractor()
    smart_context = await smart_extractor.extract_with_confidence(req.story)

    story_lower = req.story.lower()
    extraction_stage = _determine_extraction_stage(story_lower)

    # 중복 제거 및 3개 맞추기 로직
    def ensure_three_alternatives(main_keyword, alt_list, default_alternatives):
        """메인 키워드와 중복 제거 후 정확히 3개의 대안 키워드 제공"""
        if not alt_list:
            alt_list = []
        filtered_alt = [kw for kw in alt_list if kw not in [main_keyword]]
        while len(filtered_alt) < 3:
            for default in default_alternatives:
                if default not in filtered_alt and default != main_keyword:
                    filtered_alt.append(default)
                    if len(filtered_alt) >= 3:
                        break
        return filtered_alt[:3]

    emotions_main = smart_context.emotions[0] if smart_context.emotions else "기쁨"
    emotions_alt = ensure_three_alternatives(
        emotions_main,
        smart_context.emotions_alternatives,
        ["행복", "즐거움", "설렘", "감사", "희망"]
    )

    situations_main = smart_context.situations[0] if smart_context.situations else "일상"
    situations_alt = ensure_three_alternatives(
        situations_main,
        smart_context.situations_alternatives,
        ["축하", "성취", "기념일", "위로", "일상"]
    )

    moods_main = smart_context.moods[0] if smart_context.moods else "화려한"
    moods_alt = ensure_three_alternatives(
        moods_main,
        smart_context.moods_alternatives,
        ["따뜻한", "부드러운", "차분한", "우아한", "밝은"]
    )

    colors_main = smart_context.colors[0] if smart_context.colors else "레드"
    colors_alt = ensure_three_alternatives(
        colors_main,
        smart_context.colors_alternatives,
        ["핑크", "화이트", "오렌지", "퍼플", "블루"]
    )

    return {
        "success": True,
        "keywords": [
            {"type": "emotions", "main": emotions_main, "alternatives": emotions_alt},
            {"type": "situations", "main": situations_main, "alternatives": situations_alt},
            {"type": "moods", "main": moods_main, "alternatives": moods_alt},
            {"type": "colors", "main": colors_main, "alternatives": colors_alt},
        ],
        "confidence": smart_context.confidence,
        "extraction_method": smart_context.extraction_method,
        "extraction_stage": extraction_stage
    }

async def extract_realtime(req: ExtractKeywordsRequest):
    """실시간 키워드 추출 (빠른 응답) - 점진적 표시 지원"""
    smart_extractor = SmartWebSocketExtractor()
    smart_context = await smart_extractor.extract_with_confidence(req.story)

    story_lower = req.story.lower()
    extraction_stage = _determine_extraction_stage(story_lower)

    return {
        "success": True,
        "mode": "realtime",
        "extraction_stage": extraction_stage,
        "keywords": [
            {"type": "emotions", "main": smart_context.emotions[0] if smart_context.emotions else "기쁨", "alternatives": smart_context.emotions_alternatives},
            {"type": "situations", "main": smart_context.situations[0] if smart_context.situations else "일상", "alternatives": smart_context.situations_alternatives},
            {"type": "moods", "main": smart_context.moods[0] if smart_context.moods else "화려한", "alternatives": smart_context.moods_alternatives},
            {"type": "colors", "main": smart_context.colors[0] if smart_context.colors else "레드", "alternatives": smart_context.colors_alternatives},
        ],
        "confidence": smart_context.confidence,
        "extraction_method": smart_context.extraction_method
    }

def _determine_extraction_stage(story: str) -> dict:
    """텍스트 내용에 따른 추출 단계 결정"""
    stage = {
        "has_subject": False,
        "has_situation": False,
        "has_mood": False,
        "has_complete_context": False,
        "stage_number": 0,
    }

    subjects = ['친구', '어머니', '아버지', '나', '저', '우리', '가족', '연인', '동료']
    if any(subject in story for subject in subjects):
        stage["has_subject"] = True
        stage["stage_number"] = max(stage["stage_number"], 1)

    situations = ['번아웃', '힘들', '스트레스', '생일', '이직', '합격', '결혼', '졸업', '기념일']
    if any(situation in story for situation in situations):
        stage["has_situation"] = True
        stage["stage_number"] = max(stage["stage_number"], 2)

    moods = ['위로', '힐링', '조용', '따뜻', '부드럽', '차분', '로맨틱', '활기']
    if any(mood in story for mood in moods):
        stage["has_mood"] = True
        stage["stage_number"] = max(stage["stage_number"], 3)

    if len(story) > 30 and stage["has_subject"] and stage["has_situation"] and stage["has_mood"]:
        stage["has_complete_context"] = True
        stage["stage_number"] = 4

    return stage

def _extract_keywords_from_story(story: str) -> tuple:
    """스토리 내용을 분석하여 키워드를 추출"""
    story_lower = story.lower()
    emotions = _extract_emotions(story_lower)
    situations = _extract_situations(story_lower)
    moods = _extract_moods(story_lower)
    colors = _extract_colors(story_lower)
    return emotions, situations, moods, colors

def _extract_emotions(story_lower: str) -> dict:
    """감정 키워드 추출 - 내가 느끼는 마음"""
    if any(word in story_lower for word in ['편찮', '병원', '입원', '아프', '안부', '병문안']):
        return {"main": "위로", "alternatives": ["안타까움", "걱정", "따뜻함"]}
    elif any(word in story_lower for word in ['축하', '기쁘', '행복', '즐거워', '신나']):
        return {"main": "기쁨", "alternatives": ["행복", "즐거움", "신남"]}
    elif any(word in story_lower for word in ['사랑', '연인', 'अ내', '남편', '여자친구', '남자친구']):
        return {"main": "사랑", "alternatives": ["따뜻함", "애정", "로맨틱"]}
    elif any(word in story_lower for word in ['감사', '고마워', '고생', '애써']):
        return {"main": "감사", "alternatives": ["고마움", "따뜻함", "애정"]}
    elif any(word in story_lower for word in ['위로', '힘들어', '괴로워', '슬퍼', '안타까워']):
        return {"main": "위로", "alternatives": ["안타까움", "따뜻함", "희망"]}
    elif any(word in story_lower for word in ['자랑', '대단해', '멋져', '훌륭해']):
        return {"main": "자랑", "alternatives": ["감탄", "존경", "기쁨"]}
    else:
        return {"main": "기쁨", "alternatives": ["행복", "즐거움", "신남"]}

def _extract_situations(story_lower: str) -> dict:
    """상황 키워드 추출 - 어떤 일이 일어나고 있는지"""
    if any(word in story_lower for word in ['편찮', '병원', '입원', '아프', '안부', '병문안']):
        return {"main": "병문안", "alternatives": ["입원", "치료", "회복"]}
    elif any(word in story_lower for word in ['합격', '성공', '졸업', '승진', '취업']):
        return {"main": "합격", "alternatives": ["성취", "성공", "졸업"]}
    elif any(word in story_lower for word in ['기념일', '주년', '결혼', '만난지']):
        return {"main": "기념일", "alternatives": ["결혼", "주년", "특별한날"]}
    elif any(word in story_lower for word in ['생일', '탄생일']):
        return {"main": "생일", "alternatives": ["탄생일", "기념일", "파티"]}
    elif any(word in story_lower for word in ['위로', '힘들어', '괴로워', '슬퍼']):
        return {"main": "위로", "alternatives": ["힘듦", "괴로움", "슬픔"]}
    elif any(word in story_lower for word in ['축하', '파티', '잔치']):
        return {"main": "축하", "alternatives": ["파티", "잔치", "기념"]}
    else:
        return {"main": "일상", "alternatives": ["특별한날", "기념일", "축하"]}

def _extract_moods(story_lower: str) -> dict:
    """무드 키워드 추출"""
    if any(word in story_lower for word in ['편찮', '병원', '입원', '아프', '안부', '병문안']):
        return {"main": "차분한", "alternatives": ["따뜻한", "편안한", "평온한"]}
    elif any(word in story_lower for word in ['축하', '합격', '성공', '기쁨', '파티']):
        return {"main": "화려한", "alternatives": ["활발한", "기쁜", "축하하는"]}
    elif any(word in story_lower for word in ['로맨틱', '사랑', '연인', '아내', '남편']):
        return {"main": "로맨틱한", "alternatives": ["따뜻한", "부드러운", "감성적인"]}
    elif any(word in story_lower for word in ['차분한', '조용한', '평온한']):
        return {"main": "차분한", "alternatives": ["평온한", "조용한", "편안한"]}
    else:
        return {"main": "화려한", "alternatives": ["활발한", "기쁜", "축하하는"]}

def _extract_colors(story_lower: str) -> dict:
    """색상 키워드 추출"""
    if any(word in story_lower for word in ['편찮', '병원', '입원', '아프', '안부', '병문안']):
        return {"main": "화이트", "alternatives": ["크림", "라벤더", "블루"]}
    elif any(word in story_lower for word in ['축하', '합격', '성공', '기쁨', '파티']):
        return {"main": "레드", "alternatives": ["핑크", "옐로우", "오렌지"]}
    elif any(word in story_lower for word in ['로맨틱', '사랑', '연인', '아내', '남편']):
        return {"main": "핑크", "alternatives": ["레드", "크림", "화이트"]}
    elif any(word in story_lower for word in ['차분한', '조용한', '평온한']):
        return {"main": "화이트", "alternatives": ["크림", "라벤더", "블루"]}
    else:
        return {"main": "레드", "alternatives": ["핑크", "옐로우", "오렌지"]}

async def extract_final(req: ExtractKeywordsRequest):
    """최종 맥락 파악 + 사용자 수정 지원 (정확한 분석)"""
    smart_extractor = SmartWebSocketExtractor()
    smart_context = await smart_extractor.extract_with_confidence(req.story)

    if req.updated_context:
        if req.updated_context.get('emotions'):
            smart_context.emotions = req.updated_context['emotions']
        if req.updated_context.get('situations'):
            smart_context.situations = req.updated_context['situations']
        if req.updated_context.get('moods'):
            smart_context.moods = req.updated_context['moods']
        if req.updated_context.get('colors'):
            smart_context.colors = req.updated_context['colors']

    return {
        "success": True,
        "mode": "final",
        "keywords": [
            {"type": "emotions", "main": smart_context.emotions[0] if smart_context.emotions else "기쁨", "alternatives": smart_context.emotions_alternatives},
            {"type": "situations", "main": smart_context.situations[0] if smart_context.situations else "일상", "alternatives": smart_context.situations_alternatives},
            {"type": "moods", "main": smart_context.moods[0] if smart_context.moods else "화려한", "alternatives": smart_context.moods_alternatives},
            {"type": "colors", "main": smart_context.colors[0] if smart_context.colors else "레드", "alternatives": smart_context.colors_alternatives},
        ],
        "confidence": smart_context.confidence,
        "extraction_method": smart_context.extraction_method
    }

@router.post("/recommend/final")
async def final_recommend(req: UnifiedRecommendRequest):
    """최종 키워드를 받아서 꽃 추천하는 엔드포인트 (저장은 하지 않음)"""
    try:
        emotion_analyzer = EmotionAnalyzer()
        emotions = emotion_analyzer.analyze(req.story)

        # 실시간 컨텍스트 추출
        context_extractor = RealtimeContextExtractor()
        excluded_keywords = req.excluded_flowers if req.excluded_flowers else []
        context = context_extractor.extract_context_realtime(req.story, emotions, excluded_keywords)

        if req.updated_context:
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']

        # 스프레드시트 기반 매칭 시스템 사용 (LLM 없이)
        from app.services.spreadsheet_flower_matcher import SpreadsheetFlowerMatcher
        spreadsheet_matcher = SpreadsheetFlowerMatcher()

        final_emotions = context.emotions if context.emotions else []
        final_situations = context.situations if context.situations else []
        final_moods = context.moods if context.moods else []
        final_colors = req.preferred_colors if req.preferred_colors else (context.colors if context.colors else [])
        mentioned_flower = context.mentioned_flower if hasattr(context, 'mentioned_flower') else None

        print("🎯 최종 매칭 컨텍스트:")
        print(f"   감정: {final_emotions}")
        print(f"   상황: {final_situations}")
        print(f"   무드: {final_moods}")
        print(f"   색상: {final_colors}")
        print(f"   요청 색상: {req.preferred_colors}")
        print(f"   컨텍스트 색상: {context.colors if context else 'None'}")

        print("🔍 스프레드시트 매칭 시작...")
        try:
            spreadsheet_match_result = spreadsheet_matcher.match_flower(
                story=req.story,
                emotions=final_emotions,
                situations=final_situations,
                moods=final_moods,
                preferred_colors=final_colors,
                mentioned_flower=mentioned_flower
            )

            if spreadsheet_match_result:
                print(f"✅ 스프레드시트 매칭 성공: {spreadsheet_match_result.flower_data.name_ko}")
                from app.models.schemas import MatchedFlower
                matched_flower = MatchedFlower(
                    flower_name=spreadsheet_match_result.flower_data.name_en,
                    korean_name=spreadsheet_match_result.flower_data.name_ko,
                    scientific_name=spreadsheet_match_result.flower_data.scientific_name,
                    image_url=spreadsheet_match_result.image_url,
                    confidence=spreadsheet_match_result.confidence,
                    match_reason=spreadsheet_match_result.match_reason,
                    color_keywords=[spreadsheet_match_result.flower_data.base_color] + spreadsheet_match_result.flower_data.alt_colors,
                    keywords=spreadsheet_match_result.flower_data.flower_language_short or spreadsheet_match_result.flower_data.flower_language_long or "아름다움과 마음을 담아 전해요"
                )
            else:
                print("⚠️ 스프레드시트 매칭 실패, 기존 시스템 사용")
                flower_matcher = FlowerMatcher()
                mentioned_flower = getattr(context, 'mentioned_flower', None)
                matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        except Exception as e:
            print(f"❌ 스프레드시트 매칭 오류: {e}")
            print("⚠️ 오류로 인해 기존 시스템 사용")
            flower_matcher = FlowerMatcher()
            mentioned_flower = getattr(context, 'mentioned_flower', None)
            matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)

        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(matched_flower, emotions)

        from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason
        reason = _generate_unified_recommendation_reason(matched_flower, composition, emotions, req.story, context, excluded_keywords)

        from app.api.v1.endpoints.recommend import _generate_flower_card_message
        flower_card_message = _generate_flower_card_message(matched_flower, emotions, req.story)

        from app.api.v1.endpoints.recommend import _get_season_info
        season_info = _get_season_info(matched_flower.flower_name)

        flower_code = matched_flower.flower_name.upper()[:3]
        sequence_number = _get_flower_recommendation_count(flower_code)
        story_id = f"S{datetime.now().strftime('%y%m%d')}-{flower_code}-{sequence_number:06d}"

        return {
            "success": True,
            "story_id": story_id,
            "your_story": req.story,
            "flower_name": matched_flower.flower_name,
            "korean_name": matched_flower.korean_name,
            "scientific_name": matched_flower.scientific_name,
            "flower_blend": {
                "main_flower": matched_flower.korean_name,
                "sub_flowers": composition.sub_flowers,
                "composition_name": composition.composition_name
            },
            "flower_image_url": matched_flower.image_url,
            "calligraphy_image_url": matched_flower.image_url,
            "flower_card_message": {
                "quote": getattr(flower_card_message, 'quote', ''),
                "source": getattr(flower_card_message, 'source', '')
            },
            "emotions": [
                {"emotion": e.emotion, "percentage": e.percentage}
                for e in emotions
            ],
            "season_info": {
                "availability": season_info.get("season", "Spring/Summer"),
                "best_season": season_info.get("months", "03-08"),
            },
            "comment": reason,
            "hashtags": [f"#{e.emotion}" for e in emotions[:3]],
            "created_at": datetime.now().strftime('%Y.%m.%d.')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최종 추천 실패: {str(e)}")

# ===== 유틸리티 =====

def to_plain(obj):
    """Pydantic 모델/리스트/딕트/기본형을 Supabase insert 가능한 평범한 타입으로 변환"""
    from pydantic import BaseModel
    if isinstance(obj, BaseModel):
        # Pydantic v2
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        # v1 fallback
        if hasattr(obj, "dict"):
            return obj.dict()
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    return obj  # str, int, float, bool, None

# ===== 핵심 로직 함수들 =====

async def unified_recommend_logic(req: UnifiedRecommendRequest):
    """통합 추천 결과 로직 - 저장은 하지 않고 추천 결과만 생성"""
    print(f"🔍 unified_recommend_logic 시작: {req}")
    try:
        print("🔍 감정 분석 시작")
        emotion_analyzer = EmotionAnalyzer()
        print("🔍 EmotionAnalyzer 생성 완료")
        emotions = emotion_analyzer.analyze(req.story)
        print(f"✅ 감정 분석 완료: {emotions}")

        print("🔍 컨텍스트 추출 시작")
        context_extractor = RealtimeContextExtractor()
        excluded_keywords = req.excluded_flowers if req.excluded_flowers else []
        context = context_extractor.extract_context_realtime(req.story, emotions, excluded_keywords)
        print(f"✅ 컨텍스트 추출 완료: {context}")

        if req.updated_context:
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']

        from app.services.spreadsheet_flower_matcher import SpreadsheetFlowerMatcher
        spreadsheet_matcher = SpreadsheetFlowerMatcher()

        final_emotions = context.emotions if context.emotions else []
        final_situations = context.situations if context.situations else []
        final_moods = context.moods if context.moods else []
        final_colors = req.preferred_colors if req.preferred_colors else (context.colors if context.colors else [])
        mentioned_flower = context.mentioned_flower if hasattr(context, 'mentioned_flower') else None

        print("🎯 최종 매칭 컨텍스트:")
        print(f"   감정: {final_emotions}")
        print(f"   상황: {final_situations}")
        print(f"   무드: {final_moods}")
        print(f"   색상: {final_colors}")
        print(f"   언급된 꽃: {mentioned_flower}")

        try:
            spreadsheet_match_result = spreadsheet_matcher.match_flower_with_explicit(
                story=req.story,
                emotions=final_emotions,
                situations=final_situations,
                moods=final_moods,
                colors=final_colors,
                excluded_flowers=excluded_keywords,
                mentioned_flower=mentioned_flower
            )

            if spreadsheet_match_result and spreadsheet_match_result.flower_data:
                print(f"✅ 스프레드시트 매칭 성공: {spreadsheet_match_result.flower_data.korean_name}")
                matched_flower = spreadsheet_match_result.flower_data
            else:
                print("⚠️ 스프레드시트 매칭 실패, 기존 시스템 사용")
                flower_matcher = FlowerMatcher()
                matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        except Exception as e:
            print(f"❌ 스프레드시트 매칭 오류: {e}")
            print("⚠️ 오류로 인해 기존 시스템 사용")
            flower_matcher = FlowerMatcher()
            matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)

        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(matched_flower, emotions)

        from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason
        reason = _generate_unified_recommendation_reason(matched_flower, composition, emotions, req.story, context, excluded_keywords)

        from app.api.v1.endpoints.recommend import _generate_flower_card_message
        flower_card_message = _generate_flower_card_message(matched_flower, emotions, req.story)

        from app.api.v1.endpoints.recommend import _get_season_info
        season_info = _get_season_info(matched_flower.flower_name)

        # UnifiedRecommendResponse 형식으로 변환
        from app.models.schemas import UnifiedRecommendResponse

        return UnifiedRecommendResponse(
            flower_name=matched_flower.flower_name,
            korean_name=matched_flower.korean_name,
            scientific_name=matched_flower.scientific_name,
            image_url=matched_flower.image_url,
            calligraphy_image_url=f"https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/{matched_flower.flower_name.lower()}.png",
            hashtags=[f"#{emotion}" for emotion in final_emotions[:3]],
            english_description=f"Beautiful {matched_flower.flower_name} flower",
            emotions=[{"emotion": emotion, "percentage": 100.0 / len(final_emotions)} for emotion in final_emotions] if final_emotions else [],
            season_detail=season_info,
            composition=composition,
            created_at=datetime.now().strftime("%Y.%m.%d."),
            your_story=req.story,
            comment=reason
        )

    except Exception as e:
        print(f"❌ unified_recommend_logic에서 예외 발생: {e}")
        print(f"❌ 오류 타입: {type(e)}")
        print(f"❌ 오류 상세: {str(e)}")
        import traceback
        print(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise

def _generate_english_description(flower: Any, context: Any) -> str:
    """영문 설명 생성 (폴백 포함)"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"""
Create a brief, elegant English description for this flower recommendation:
Flower: {flower.flower_name}
Context: {context}
Make it poetic and meaningful.
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"A beautiful {flower.flower_name} that perfectly matches your emotions and preferences."

def _generate_hashtags(flower: Any, context: Any) -> List[str]:
    """해시태그 생성"""
    hashtags = []
    hashtags.append(f"#{flower.flower_name.replace(' ', '')}")
    for color in context.colors:
        hashtags.append(f"#{color}")
    for emotion in context.emotions:
        hashtags.append(f"#{emotion}")
    for situation in context.situations:
        hashtags.append(f"#{situation}")
    if hasattr(flower, 'seasonality'):
        for season in flower.seasonality:
            hashtags.append(f"#{season}")
    return hashtags[:10]

def _convert_season_format(season_months: str) -> List[str]:
    """스프레드시트의 season_months 형식을 배열로 변환"""
    if not season_months:
        return ["봄", "여름"]
    season_mapping = {"Spring": "봄", "Summer": "여름", "Fall": "가을", "Winter": "겨울"}
    seasons = []
    for season in season_months.split("/"):
        season = season.strip()
        if season in season_mapping:
            seasons.append(season_mapping[season])
    return seasons if seasons else ["봄", "여름"]

def _save_story(story: str, emotions: List, flower: Any, composition: Any, reason: str) -> Optional[str]:
    """스토리 저장 (레거시 경로 - 현재는 미사용)"""
    try:
        from app.api.v1.endpoints.recommend import _save_story_to_database
        return _save_story_to_database(story, emotions, flower, composition, reason)
    except Exception as e:
        print(f"스토리 저장 실패: {e}")
        return None

# ===== 새로운 스냅샷 추천 엔드포인트 =====

@router.post("/recommend", response_model=RecommendationResponse)
async def create_recommendation_snapshot(request: RecommendationRequest):
    """새로운 추천 요청 - 스냅샷 저장 후 응답 (story_id는 DB 기준 +1 자동 생성)"""
    try:
        # 1) 기존 추천 로직 사용
        unified_request = UnifiedRecommendRequest(
            story=request.story,
            preferred_colors=[request.selected_keywords.colors],
            excluded_flowers=request.excluded_keywords,
            updated_context={
                "emotions": [request.selected_keywords.emotions],
                "situations": [request.selected_keywords.situations],
                "moods": [request.selected_keywords.moods],
                "colors": [request.selected_keywords.colors],
            },
        )

        print("🔍 추천 로직 실행 시작")
        try:
            print("🔍 unified_recommend_logic 호출 전")
            recommendation_result = await unified_recommend_logic(unified_request)
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
            "selected_keywords": to_plain({
                "emotions": request.selected_keywords.emotions,
                "situations": request.selected_keywords.situations,
                "moods": request.selected_keywords.moods,
                "colors": request.selected_keywords.colors
            }),
            "excluded_keywords": to_plain(request.excluded_keywords),
            "flower_name": recommendation_result.flower_name,
            "korean_name": recommendation_result.korean_name,
            "scientific_name": recommendation_result.scientific_name,
            "image_url": recommendation_result.image_url,
            "calligraphy_image_url": recommendation_result.calligraphy_image_url,
            "hashtags": to_plain(recommendation_result.hashtags),
            "english_description": recommendation_result.english_description,
            "emotions": to_plain(recommendation_result.emotions),
            "season_detail": to_plain(recommendation_result.season_detail),
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
        snapshot = supabase_manager.get_recommendation_snapshot(story_id)

        if not snapshot:
            raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")

        return SnapshotResponse(
            success=True,
            created_at=snapshot["created_at"][:10].replace("-", ".") + ".",
            story_id=snapshot["id"],
            your_story=snapshot["story"],
            flower_info={
                "korean_name": snapshot["korean_name"],
                "english_name": snapshot["flower_name"],
                "scientific_name": snapshot["scientific_name"],
            },
            flower_blend=snapshot["composition"],
            flower_image_url=snapshot["image_url"],
            calligraphy_image_url=snapshot["calligraphy_image_url"],
            flower_card_message={"quote": "인용구", "source": "출처"},
            emotions=snapshot["emotions"],
            season_detail=snapshot["season_detail"],
            comment=snapshot["recommendation_reason"],
            hashtags=snapshot["hashtags"],
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 스냅샷 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스냅샷 조회 실패: {str(e)}")

def _get_flower_code_from_name(korean_name: str) -> str:
    """한글 꽃 이름을 영문 코드로 변환"""
    flower_mapping = {
        "지니아": "ZIN",
        "장미": "ROS",
        "튤립": "TUL",
        "해바라기": "SUN",
        "프리지아": "FRE",
        "카네이션": "CAR",
        "백합": "LIL",
        "수국": "HYD",
        "아네모네": "ANE",
        "안스리움": "ANT",
    }
    return flower_mapping.get(korean_name, "DEF")
