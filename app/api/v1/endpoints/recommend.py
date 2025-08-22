from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Any, Dict
import os
import json
import asyncio
from app.models.schemas import (
    RecommendRequest,
    RecommendResponse,
    EmotionAnalysisResponse,
    EmotionAnalysis,
    FlowerMatch,
    FlowerComposition,
    StoryCreateRequest
)
from app.pipelines.integrated_recommendation_chain import IntegratedRecommendationChain
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.flower_matcher import FlowerMatcher
from app.services.enhanced_flower_matcher import EnhancedFlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.services.story_classifier import StoryClassifier
from app.services.design_flower_matcher import DesignFlowerMatcher
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.story_manager import story_manager
from app.utils.request_deduplication import request_deduplicator

router = APIRouter()

def get_chain():
    return IntegratedRecommendationChain()

@router.post("/recommendations", response_model=RecommendResponse)
def recommendations(req: RecommendRequest, chain: IntegratedRecommendationChain = Depends(get_chain)):
    """통합 추천 엔드포인트 (중복 요청 방지 포함)"""
    try:
        # 요청 ID 생성
        request_id = request_deduplicator.generate_request_id(
            req.story, 
            req.preferred_colors, 
            req.excluded_flowers
        )
        
        print(f"🔍 요청 ID 생성: {request_id}")
        
        # 캐시된 결과가 있는지 확인
        cached_result = request_deduplicator.get_cached_result(request_id)
        if cached_result:
            print(f"📋 캐시된 결과 반환: {request_id}")
            return RecommendResponse(**cached_result)
        
        # 중복 요청인지 확인
        if not request_deduplicator.should_process_request(request_id):
            print(f"⏳ 중복 요청 대기 중: {request_id}")
            # 잠시 대기 후 다시 확인
            import time
            time.sleep(0.1)
            cached_result = request_deduplicator.get_cached_result(request_id)
            if cached_result:
                return RecommendResponse(**cached_result)
            else:
                raise HTTPException(status_code=429, detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
        
        # 실제 요청 처리
        print(f"🚀 새로운 요청 처리 시작: {request_id}")
        result = chain.run(req)
        
        # 결과 캐시에 저장
        request_deduplicator.mark_request_completed(request_id, result.dict())
        
        return result
        
    except Exception as e:
        print(f"❌ 추천 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/emotion-analysis", response_model=EmotionAnalysisResponse)
def emotion_analysis(req: RecommendRequest):
    """감정 분석 + 꽃 매칭 + 구성 추천 (사연 유형 분류 포함) - 중복 요청 방지 포함"""
    
    try:
        # 요청 ID 생성 (emotion-analysis용)
        request_id = request_deduplicator.generate_request_id(
            req.story, 
            req.preferred_colors, 
            req.excluded_flowers
        ) + "_emotion"  # emotion-analysis와 구분
        
        print(f"🔍 Emotion Analysis 요청 ID 생성: {request_id}")
        
        # 캐시된 결과가 있는지 확인
        cached_result = request_deduplicator.get_cached_result(request_id)
        if cached_result:
            print(f"📋 Emotion Analysis 캐시된 결과 반환: {request_id}")
            return EmotionAnalysisResponse(**cached_result)
        
        # 중복 요청인지 확인
        if not request_deduplicator.should_process_request(request_id):
            print(f"⏳ Emotion Analysis 중복 요청 대기 중: {request_id}")
            # 잠시 대기 후 다시 확인
            import time
            time.sleep(0.1)
            cached_result = request_deduplicator.get_cached_result(request_id)
            if cached_result:
                return EmotionAnalysisResponse(**cached_result)
            else:
                raise HTTPException(status_code=429, detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
        
        # 실제 요청 처리
        print(f"🚀 Emotion Analysis 새로운 요청 처리 시작: {request_id}")
        # 1. 감정 분석 (사연에 맞는 감정 비중)
        emotion_analyzer = EmotionAnalyzer()
        emotions = emotion_analyzer.analyze(req.story)
        
        # 2. 컨텍스트 추출 (제외된 키워드 고려)
        context_extractor = RealtimeContextExtractor()
        excluded_keywords = req.excluded_keywords if hasattr(req, 'excluded_keywords') and req.excluded_keywords else []
        context = context_extractor.extract_context_realtime(req.story, emotions, excluded_keywords)
        print(f"📊 추출된 맥락: {context}")
        
        # 3. 선택된 키워드나 업데이트된 컨텍스트가 있으면 컨텍스트 업데이트
        if hasattr(req, 'selected_keywords') and req.selected_keywords:
            print(f"🎯 선택된 키워드: {req.selected_keywords}")
            # 선택된 키워드로 컨텍스트 업데이트
            if req.selected_keywords.get('emotions'):
                context.emotions = req.selected_keywords['emotions']
            if req.selected_keywords.get('situations'):
                context.situations = req.selected_keywords['situations']
            if req.selected_keywords.get('moods'):
                context.moods = req.selected_keywords['moods']
            if req.selected_keywords.get('colors'):
                context.colors = req.selected_keywords['colors']
            print(f"🔄 업데이트된 컨텍스트: {context}")
        
        # 업데이트된 컨텍스트가 있으면 우선 적용
        if hasattr(req, 'updated_context') and req.updated_context:
            print(f"🔄 업데이트된 컨텍스트: {req.updated_context}")
            # 업데이트된 컨텍스트로 덮어쓰기
            if req.updated_context.get('emotions'):
                context.emotions = req.updated_context['emotions']
            if req.updated_context.get('situations'):
                context.situations = req.updated_context['situations']
            if req.updated_context.get('moods'):
                context.moods = req.updated_context['moods']
            if req.updated_context.get('colors'):
                context.colors = req.updated_context['colors']
            print(f"🔄 최종 업데이트된 컨텍스트: {context}")
        
        # 4. 제외된 키워드가 있으면 컨텍스트에서 제거
        if hasattr(req, 'excluded_keywords') and req.excluded_keywords:
            print(f"🚫 제외된 키워드: {req.excluded_keywords}")
            
            # 제외된 키워드들을 각 카테고리에서 제거
            excluded_texts = [kw.get('text', '') for kw in req.excluded_keywords]
            
            context.emotions = [emotion for emotion in context.emotions if emotion not in excluded_texts]
            context.situations = [situation for situation in context.situations if situation not in excluded_texts]
            context.moods = [mood for mood in context.moods if mood not in excluded_texts]
            context.colors = [color for color in context.colors if color not in excluded_texts]
            
            print(f"🔄 제외 키워드 제거 후 컨텍스트: {context}")
        
        # 4. 꽃 매칭 (제외 조건 반영)
        flower_matcher = FlowerMatcher()
        
        # 언급된 꽃 정보 전달
        mentioned_flower = context.mentioned_flower if hasattr(context, 'mentioned_flower') else None
        matched_flower = flower_matcher.match(emotions, req.story, context.user_intent, excluded_keywords, mentioned_flower, context)
        
        # 5. 꽃 구성 추천
        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(matched_flower, emotions)
        
        # 6. LLM 기반 추천 이유 생성 (제외 조건 반영)
        reason = _generate_unified_recommendation_reason(matched_flower, composition, emotions, req.story, context, excluded_keywords)
        
        # 7. 꽃카드 메시지 생성
        flower_card_message = _generate_flower_card_message(matched_flower, emotions, req.story)
        
        # 8. 계절 정보 가져오기
        season_info = _get_season_info(matched_flower.flower_name)
        
        # 9. 스토리 데이터베이스에 저장
        try:
            story_request = StoryCreateRequest(
                story=req.story,
                emotions=emotions,
                matched_flower=matched_flower,
                composition=composition,
                recommendation_reason=reason,
                flower_card_message=flower_card_message,
                season_info=season_info,
                keywords=context.emotions + context.situations + context.moods + context.colors if hasattr(context, 'emotions') else [],
                hashtags=matched_flower.hashtags,
                color_keywords=matched_flower.color_keywords,
                excluded_keywords=excluded_keywords or []
            )
            
            story_data = story_manager.create_story(story_request)
            print(f"✅ 스토리 저장 완료: {story_data.story_id}")
            
        except Exception as e:
            print(f"⚠️ 스토리 저장 실패: {e}")
            # 스토리 저장 실패해도 추천 결과는 반환
        
        # 결과 생성
        result = EmotionAnalysisResponse(
            emotions=emotions,
            matched_flower=matched_flower,
            composition=composition,
            recommendation_reason=reason,
            flower_card_message=flower_card_message,
            story_id=story_data.story_id if 'story_data' in locals() else None
        )
        
        # 결과 캐시에 저장
        request_deduplicator.mark_request_completed(request_id, result.dict())
        
        return result
        
    except Exception as e:
        print(f"❌ 감정 분석 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"감정 분석 실패: {str(e)}")

@router.get("/flower-season/{flower_name}")
def get_flower_season(flower_name: str):
    """꽃별 계절 정보 반환"""
    try:
        # flower_dictionary.json에서 꽃 정보 찾기
        with open("data/flower_dictionary.json", "r", encoding="utf-8") as f:
            flower_data = json.load(f)
        
        # 꽃 이름으로 검색 (한글명, 영문명, 또는 flower_id의 일부)
        for flower_id, flower_info in flower_data["flowers"].items():
            # flower_id에서 꽃 이름 부분 추출 (색상 제외)
            flower_name_from_id = flower_id.split('-')[0] if '-' in flower_id else flower_id
            
            if (flower_info.get("korean_name") == flower_name or 
                flower_info.get("scientific_name") == flower_name or
                flower_name.lower() in flower_info.get("korean_name", "").lower() or
                flower_name.lower() in flower_name_from_id.lower() or
                flower_name_from_id.lower() in flower_name.lower()):
                
                seasonality = flower_info.get("seasonality", [])
                return {"seasonality": seasonality}
        
        # 찾지 못한 경우 기본값 반환
        return {"seasonality": ["봄", "여름"]}
        
    except Exception as e:
        print(f"❌ 꽃 계절 정보 조회 실패: {e}")
        return {"seasonality": ["봄", "여름"]}

def _generate_unified_recommendation_reason(matched_flower: FlowerMatch, composition: FlowerComposition, emotions: List[EmotionAnalysis], story: str, context: Any, excluded_keywords: List[Dict[str, str]] = None) -> str:
    """통합 추천 이유 생성 (사연에 맞는 공감가는 설명, 제외된 키워드 고려)"""
    if not os.getenv("OPENAI_API_KEY"):
        return _fallback_recommendation_reason(matched_flower, composition, emotions, story)
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        emotion_text = ", ".join([f"{e.emotion}({e.percentage}%)" for e in emotions])
        
        # 실제 선택된 꽃의 색상 사용 (제외된 색상 피하기)
        flower_colors = matched_flower.color_keywords if matched_flower.color_keywords and len(matched_flower.color_keywords) > 0 else []
        
        # 제외된 색상 필터링
        excluded_colors = [kw.get('text', '') for kw in (excluded_keywords or []) if kw.get('type') == 'color']
        filtered_colors = [color for color in flower_colors if color not in excluded_colors]
        
        color_text = ", ".join(filtered_colors) if filtered_colors else "자연스러운 색감"
        
        print(f"🎨 원본 색상: {flower_colors}")
        print(f"🚫 제외된 색상: {excluded_colors}")
        print(f"✅ 필터링된 색상: {filtered_colors}")
        
        # 제외된 키워드 정보 추가
        excluded_text = ""
        if excluded_keywords:
            excluded_texts = [kw.get('text', '') for kw in excluded_keywords]
            excluded_text = f"\n제외된 키워드: {', '.join(excluded_texts)} (이 키워드들은 언급하지 마세요)"
        
        prompt = f"""
당신은 꽃 추천 전문가입니다. 고객의 사연과 감정을 깊이 이해하고, 선택된 메인 꽃의 의미를 설명해주세요.

고객 사연: "{story}"
고객 감정: {emotion_text}

선택된 메인 꽃: {matched_flower.flower_name} ({matched_flower.korean_name})
꽃 색상: {color_text}
꽃의 특성/꽃말: {matched_flower.keywords}{excluded_text}

다음 조건을 만족하는 개인적이고 따뜻한 추천 이유를 작성해주세요:

1. **첫 문장**: 고객의 구체적인 상황과 감정을 이해하고, 꽃의 색상/특성을 연결
2. **두 번째 문장**: 이 꽃이 고객의 마음을 어떻게 표현해주는지 개인적으로 설명
3. **전체적으로**: 
   - "해요" 체 사용
   - 2문장으로 구성 (총 120-150자 내외)
   - 개인적이고 공감가는 어투
   - **중요**: 고객의 구체적인 상황(생일, 이직, 위로 등)을 명시적으로 언급
   - 꽃의 색상과 무드를 통해 고객의 감정을 어떻게 표현할지 설명
   - 마케팅적이거나 일반적인 문장은 피하고, 진정성 있는 개인적 조언

예시 구조:
- "[고객 상황]에 [꽃 색상] [꽃이름]이 [어떤 의미]를 담아줘요."
- "[고객 감정]을 [꽃의 특성]으로 표현하면 [어떤 효과]를 얻을 수 있어요."

**주의사항**:
- 고객의 구체적인 상황을 반드시 언급하세요
- 개인적이고 진정성 있는 톤을 유지하세요
- 마케팅적이거나 일반적인 문장은 피하세요
- 2문장을 넘지 마세요

한국어로 자연스럽고 전문적으로 작성해주세요.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 꽃 추천 전문가입니다. 고객의 사연과 감정을 깊이 이해하고, 선택된 메인 꽃의 의미를 설명하여 개인적이고 진정성 있는 추천 이유를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ 통합 추천 이유 생성 실패: {e}")
        return _fallback_recommendation_reason(matched_flower, composition, emotions, story)



def _fallback_recommendation_reason(matched_flower: FlowerMatch, composition: FlowerComposition, emotions: List[EmotionAnalysis], story: str) -> str:
    """폴백 추천 이유"""
    flower_name = matched_flower.korean_name
    flower_color = matched_flower.color_keywords[0] if matched_flower.color_keywords and len(matched_flower.color_keywords) > 0 else "자연스러운"
    
    # 사연 기반 맞춤형 추천 이유 (구체적이고 개성 있게)
    if "시험" in story and ("떨어졌" in story or "실패" in story):
        return f"{flower_color} {flower_name}의 밝은 에너지가 '다음 기회가 있어'라고 말해줘요."
    elif "병원" in story or "병실" in story:
        return f"{flower_color} 톤의 부드러운 매력이 삭막한 공간을 따뜻하게 채워줘요."
    elif "결혼" in story or "축하" in story:
        return f"{flower_color} {flower_name}의 우아한 매력이 특별한 순간을 더욱 빛나게 해줘요."
    elif "응원" in story or "격려" in story:
        return f"{flower_color} {flower_name}의 강인한 생명력이 힘내라고 응원해줘요."
    elif "생일" in story:
        return f"{flower_color} {flower_name}의 따뜻한 매력이 생일을 더욱 특별하게 만들어줘요."
    else:
        return f"{flower_color} {flower_name}의 아름다움이 마음을 담아 전해줘요."


def _generate_flower_card_message(matched_flower: FlowerMatch, emotions: List[EmotionAnalysis], story: str) -> str:
    """꽃카드 메시지 생성 (영어 시적 문구)"""
    if not os.getenv("OPENAI_API_KEY"):
        return _fallback_flower_card_message(matched_flower, emotions, story)
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        emotion_text = ", ".join([f"{e.emotion}({e.percentage}%)" for e in emotions])
        
        prompt = f"""
Create a poetic English message for a flower card using famous quotes from movies, literature, songs, or dramas.

Customer's Story: "{story}"
Customer's Emotions: {emotion_text}
Flower: {matched_flower.flower_name} ({matched_flower.korean_name})

**Requirements**:
- **Line 1**: A famous quote (40 characters max) that EXACTLY matches the customer's situation and emotions
- **Line 2**: The source in format "- Source Name -" (with spaces around the dash)
- **Style**: Choose quotes that directly relate to love, gratitude, support, or the specific emotion mentioned
- **Format**: Two lines separated by \\n

**Context Analysis**:
- If the story mentions "고맙고 사랑한다" → Choose love/gratitude quotes
- If the story mentions "지쳐보여요" → Choose supportive/comforting quotes
- If the story mentions "아내/남편" → Choose romantic/marriage quotes
- If the story mentions "회사일" → Choose supportive/encouraging quotes

**Examples for Love/Gratitude**:
- "You make me want to be a better man."\\n- As Good As It Gets -
- "Thank you for being you."\\n- Friends -
- "You are my sunshine."\\n- You Are My Sunshine -
- "I love you more than words."\\n- The Notebook -

**Examples for Support/Comfort**:
- "I'll be there for you."\\n- Friends -
- "You are stronger than you know."\\n- The Princess Diaries -
- "I believe in you always.\\n- The Little Engine That Could -
- "You make every day beautiful.\\n- The Sound of Music -

Choose a quote that DIRECTLY matches the customer's specific situation and emotions. Write only the message text in English with line break.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a poetic message writer for flower cards. Create short, touching English messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ 꽃카드 메시지 생성 실패: {e}")
        return _fallback_flower_card_message(matched_flower, emotions, story)


def _fallback_flower_card_message(matched_flower: FlowerMatch, emotions: List[EmotionAnalysis], story: str) -> str:
    """폴백 꽃카드 메시지 (인용문구 형식)"""
    flower_name = matched_flower.flower_name.lower()
    
    # 스토리 내용 기반으로 더 구체적인 메시지 선택
    story_lower = story.lower()
    
    # 아내/남편 관련 (결혼/로맨스)
    if any(word in story_lower for word in ["아내", "남편", "와이프", "부인", "남편님"]):
        if any(word in story_lower for word in ["고맙", "감사", "사랑"]):
            return "I love you more than words.\n- The Notebook -"
        elif any(word in story_lower for word in ["지쳐", "피곤", "힘들"]):
            return "I'll be there for you.\n- Friends -"
        else:
            return "You make me want to be a better man.\n- As Good As It Gets -"
    
    # 감사/사랑 관련
    elif any(word in story_lower for word in ["고맙", "감사", "사랑"]):
        return "Thank you for being you.\n- Friends -"
    
    # 지침/위로 관련
    elif any(word in story_lower for word in ["지쳐", "피곤", "힘들", "스트레스"]):
        return "You are stronger than you know.\n- The Princess Diaries -"
    
    # 응원/격려 관련
    elif any(word in story_lower for word in ["응원", "격려", "힘내"]):
        return "I believe in you always.\n- The Little Engine That Could -"
    
    # 기쁨/행복 관련
    elif any(word in story_lower for word in ["기쁨", "행복", "즐거"]):
        return "You are my sunshine.\n- You Are My Sunshine -"
    
    # 감정 분석 결과 기반
    elif any("사랑" in e.emotion for e in emotions):
        return "I love you more than words.\n- The Notebook -"
    elif any("감사" in e.emotion for e in emotions):
        return "Thank you for being you.\n- Friends -"
    elif any("위로" in e.emotion for e in emotions):
        return "You are stronger than you know.\n- The Princess Diaries -"
    elif any("응원" in e.emotion for e in emotions):
        return "I believe in you always.\n- The Little Engine That Could -"
    else:
        return "You make every day beautiful.\n- The Sound of Music -"


def _get_season_info(flower_name: str) -> str:
    """꽃의 계절 정보 가져오기"""
    try:
        # flower_dictionary.json에서 꽃 정보 찾기
        with open("data/flower_dictionary.json", "r", encoding="utf-8") as f:
            flower_data = json.load(f)
        
        # 꽃 이름으로 검색 (한글명 또는 영문명)
        for flower_id, flower_info in flower_data["flowers"].items():
            if (flower_info.get("korean_name") == flower_name or 
                flower_info.get("scientific_name") == flower_name or
                flower_name.lower() in flower_info.get("korean_name", "").lower()):
                
                seasonality = flower_info.get("seasonality", [])
                if seasonality:
                    return ", ".join(seasonality)
                break
        
        # 찾지 못한 경우 기본값 반환
        return "봄, 여름"
        
    except Exception as e:
        print(f"❌ 꽃 계절 정보 조회 실패: {e}")
        return "봄, 여름"


@router.post("/extract-context")
def extract_context(req: RecommendRequest):
    """맥락 키워드 추출 엔드포인트 (중복 요청 방지 포함)"""
    try:
        # 요청 ID 생성 (extract-context용)
        request_id = request_deduplicator.generate_request_id(
            req.story, 
            req.preferred_colors, 
            req.excluded_flowers
        ) + "_context"  # extract-context와 구분
        
        print(f"🔍 Extract Context 요청 ID 생성: {request_id}")
        
        # 캐시된 결과가 있는지 확인
        cached_result = request_deduplicator.get_cached_result(request_id)
        if cached_result:
            print(f"📋 Extract Context 캐시된 결과 반환: {request_id}")
            return cached_result
        
        # 중복 요청인지 확인
        if not request_deduplicator.should_process_request(request_id):
            print(f"⏳ Extract Context 중복 요청 대기 중: {request_id}")
            # 잠시 대기 후 다시 확인
            import time
            time.sleep(0.1)
            cached_result = request_deduplicator.get_cached_result(request_id)
            if cached_result:
                return cached_result
            else:
                raise HTTPException(status_code=429, detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
        
        # 실제 요청 처리
        print(f"🚀 Extract Context 새로운 요청 처리 시작: {request_id}")
        context_extractor = RealtimeContextExtractor()
        context = context_extractor.extract_context_realtime(req.story)
        
        # 결과 캐시에 저장
        request_deduplicator.mark_request_completed(request_id, context.dict())
        
        return context
        
    except Exception as e:
        print(f"❌ Extract Context API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extract-context-stream")
async def extract_context_stream(story: str):
    """실시간 맥락 추출 SSE 엔드포인트"""
    async def generate():
        try:
            # 실시간 맥락 추출
            context_extractor = RealtimeContextExtractor()
            context = context_extractor.extract_context_realtime(story)
            
            # SSE 형식으로 데이터 전송
            data = {
                "type": "context_extracted",
                "data": context
            }
            
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
