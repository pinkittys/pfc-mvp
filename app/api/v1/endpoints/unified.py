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

router = APIRouter()

# 꽃별 추천 횟수 추적을 위한 전역 변수
_flower_recommendation_counts = {}

def _get_flower_recommendation_count(flower_code: str) -> int:
    """꽃별 추천 횟수 증가 및 반환"""
    if flower_code not in _flower_recommendation_counts:
        _flower_recommendation_counts[flower_code] = 0
    _flower_recommendation_counts[flower_code] += 1
    return _flower_recommendation_counts[flower_code]

# ===== 요청/응답 모델 =====

class ExtractKeywordsRequest(BaseModel):
    """키워드 추출 요청 모델"""
    story: str
    updated_context: Optional[Dict[str, Any]] = None

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
async def extract_keywords(
    req: ExtractKeywordsRequest,
    mode: str = "realtime"
):
    """통합 키워드 추출 엔드포인트 - mode에 따라 실시간/최종 구분"""
    try:
        if mode == "realtime":
            return await extract_realtime(req)
        else:
            return await extract_final(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")

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
            {"type": "colors", "main": smart_context.colors[0] if smart_context.colors else "레드", "alternatives": smart_context.colors_alternatives}
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
        "stage_number": 0
    }

    subjects = ['친구', '어머니', '아버지', '나', '저', '우리', '가족', '연인', '동료']
    if any(subject in story for subject in subjects):
        stage["has_subject"] = True
        stage["stage_number"] = 1

    situations = ['번아웃', '힘들', '스트레스', '생일', '이직', '합격', '결혼', '졸업', '기념일']
    if any(situation in story for situation in situations):
        stage["has_situation"] = True
        stage["stage_number"] = 2

    moods = ['위로', '힐링', '조용', '따뜻', '부드럽', '차분', '로맨틱', '활기']
    if any(mood in story for mood in moods):
        stage["has_mood"] = True
        stage["stage_number"] = 3

    if len(story) > 30 and stage["has_subject"] and stage["has_situation"] and stage["has_mood"]:
        stage["has_complete_context"] = True
        stage["stage_number"] = 4

    return stage

def _extract_keywords_from_story(story: str) -> tuple:
    """스토리 내용을 분석하여 키워드를 추출"""
    story_lower = story.lower()
    
    # 감정 키워드 추출
    emotions = _extract_emotions(story_lower)
    
    # 상황 키워드 추출
    situations = _extract_situations(story_lower)
    
    # 무드 키워드 추출
    moods = _extract_moods(story_lower)
    
    # 색상 키워드 추출
    colors = _extract_colors(story_lower)
    
    return emotions, situations, moods, colors

def _extract_emotions(story_lower: str) -> dict:
    """감정 키워드 추출 - 내가 느끼는 마음"""
    if any(word in story_lower for word in ['편찮', '병원', '입원', '아프', '안부', '병문안']):
        return {"main": "위로", "alternatives": ["안타까움", "걱정", "따뜻함"]}
    elif any(word in story_lower for word in ['축하', '기쁘', '행복', '즐거워', '신나']):
        return {"main": "기쁨", "alternatives": ["행복", "즐거움", "신남"]}
    elif any(word in story_lower for word in ['사랑', '연인', '아내', '남편', '여자친구', '남자친구']):
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
            {"type": "colors", "main": smart_context.colors[0] if smart_context.colors else "레드", "alternatives": smart_context.colors_alternatives}
        ],
        "confidence": smart_context.confidence,
        "extraction_method": smart_context.extraction_method
    }

@router.post("/recommend")
async def final_recommend(req: UnifiedRecommendRequest):
    """최종 키워드를 받아서 꽃 추천하는 엔드포인트"""
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
        
        # 사용자 수정 컨텍스트가 있으면 우선 사용, 없으면 추출된 컨텍스트 사용
        final_emotions = context.emotions if context.emotions else []
        final_situations = context.situations if context.situations else []
        final_moods = context.moods if context.moods else []
        # 색상은 사용자 요청을 우선 사용
        final_colors = req.preferred_colors if req.preferred_colors else (context.colors if context.colors else [])
        # 언급된 꽃 정보
        mentioned_flower = context.mentioned_flower if hasattr(context, 'mentioned_flower') else None
        
        print(f"🎯 최종 매칭 컨텍스트:")
        print(f"   감정: {final_emotions}")
        print(f"   상황: {final_situations}")
        print(f"   무드: {final_moods}")
        print(f"   색상: {final_colors}")
        print(f"   요청 색상: {req.preferred_colors}")
        print(f"   컨텍스트 색상: {context.colors if context else 'None'}")
        
        # 스프레드시트 기반 매칭 (LLM 없이)
        print(f"🔍 스프레드시트 매칭 시작...")
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
                    keywords=spreadsheet_match_result.flower_data.flower_language_short or "아름다움과 마음을 담아 전해요"
                )
            else:
                # 폴백: 기존 시스템 사용
                print(f"⚠️ 스프레드시트 매칭 실패, 기존 시스템 사용")
                flower_matcher = FlowerMatcher()
                mentioned_flower = getattr(context, 'mentioned_flower', None)
                matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        except Exception as e:
            print(f"❌ 스프레드시트 매칭 오류: {e}")
            # 폴백: 기존 시스템 사용
            print(f"⚠️ 오류로 인해 기존 시스템 사용")
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
            "calligraphy_image_url": matched_flower.image_url,  # 캘리그래피 이미지 URL (현재는 동일한 이미지 사용)
            "flower_card_message": {
                "quote": getattr(flower_card_message, 'quote', ''),
                "source": getattr(flower_card_message, 'source', '')
            },
            "emotions": [
                {
                    "emotion": e.emotion,
                    "percentage": e.percentage
                }
                for e in emotions
            ],
            "season_info": {
                "availability": season_info.get("season", "Spring/Summer"),
                "best_season": season_info.get("months", "03-08")
            },
            "comment": reason,
            "hashtags": [f"#{e.emotion}" for e in emotions[:3]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최종 추천 실패: {str(e)}")

# ===== 핵심 로직 함수들 (엔드포인트는 제거했지만 코드는 보존) =====
# 실행되지 않도록 완전히 비활성화
if False:
    def unified_recommend_logic(req: UnifiedRecommendRequest):
        """통합 추천 결과 로직 (엔드포인트 제거, 로직 보존)"""
        # ... (레거시 로직 전체, 필요시 복원)
        pass

def _generate_english_description(flower: Any, context: Any) -> str:
    """영문 설명 생성"""
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

def _save_story(story: str, emotions: List, flower: Any, composition: Any, reason: str) -> str:
    """스토리 저장"""
    try:
        from app.api.v1.endpoints.recommend import _save_story_to_database
        return _save_story_to_database(story, emotions, flower, composition, reason)
    except Exception as e:
        print(f"스토리 저장 실패: {e}")
        return None