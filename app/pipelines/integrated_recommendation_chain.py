"""
통합 추천 체인 (LLM 기반 실시간 맥락 추출 + 꽃 추천)
"""
import time
from typing import List, Dict, Any
from app.services.realtime_context_extractor import RealtimeContextExtractor, ExtractedContext
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.services.recommendation_reason_generator import RecommendationReasonGenerator
from app.services.image_matcher import ImageMatcher
from app.services.recommendation_logger import RecommendationLogger
from app.services.story_manager import StoryManager
from app.models.schemas import RecommendRequest, RecommendResponse, RecommendationItem

class IntegratedRecommendationChain:
    def __init__(self):
        self.context_extractor = RealtimeContextExtractor()
        self.emotion_analyzer = EmotionAnalyzer()
        self.flower_matcher = FlowerMatcher()
        self.composition_recommender = CompositionRecommender()
        self.reason_generator = RecommendationReasonGenerator()
        self.image_matcher = ImageMatcher()
        self.logger = RecommendationLogger()
        self.story_manager = StoryManager()
    
    def run(self, request: RecommendRequest) -> RecommendResponse:
        """통합 추천 체인 실행"""
        start_time = time.time()
        
        print(f"🚀 통합 추천 체인 시작")
        print(f"   고객 스토리: {request.story[:50]}...")
        
        # 1단계: LLM 기반 실시간 맥락 추출
        print(f"🔍 1단계: LLM 실시간 맥락 추출")
        extracted_context = self.context_extractor.extract_context_realtime(request.story)
        
        print(f"   추출된 맥락:")
        print(f"     감정: {extracted_context.emotions}")
        print(f"     상황: {extracted_context.situations}")
        print(f"     무드: {extracted_context.moods}")
        print(f"     컬러: {extracted_context.colors}")
        print(f"     신뢰도: {extracted_context.confidence:.2f}")
        
        # 2단계: 감정 분석 (기존 시스템과 호환)
        print(f"🎯 2단계: 감정 분석")
        emotion_analysis = self._convert_context_to_emotion_analysis(extracted_context)
        
        # 첫 번째 감정의 emotion 속성 사용
        primary_emotion = emotion_analysis[0].emotion if emotion_analysis else "따뜻함"
        print(f"   주요 감정: {primary_emotion}")
        print(f"   감정 비율: {[f'{e.emotion}({e.percentage}%)' for e in emotion_analysis]}")
        
        # 3단계: 꽃 매칭
        print(f"🌺 3단계: 꽃 매칭")
        matched_flower = self.flower_matcher.match(emotion_analysis, request.story, "meaning_based")
        
        print(f"   매칭된 꽃: {matched_flower.flower_name}")
        
        # 4단계: 꽃 구성 추천
        print(f"🌿 4단계: 꽃 구성 추천")
        composition = self.composition_recommender.recommend(matched_flower, emotion_analysis)
        
        print(f"   구성: {composition.composition_name}")
        
        # 5단계: 추천 이유 생성
        print(f"💭 5단계: 추천 이유 생성")
        
        # 추천 이유 생성
        recommendation_reason = self.reason_generator.generate_reason(
            emotion_analysis,
            [matched_flower],  # 단일 꽃을 리스트로 변환
            composition,  # CompositionRecommender 결과 사용
            request.story,
            extracted_context.colors
        )
        
        # 6단계: 스토리 ID 생성
        print(f"📝 6단계: 스토리 ID 생성")
        story_id = self.story_manager._generate_story_id(matched_flower.flower_name)
        print(f"   생성된 스토리 ID: {story_id}")
        
        # 단일 추천 아이템 생성
        item = RecommendationItem(
            id="R001",
            template_id=matched_flower.flower_name,
            name="추천 꽃다발",
            main_flowers=[matched_flower.flower_name],
            sub_flowers=composition.sub_flowers,
            color_theme=extracted_context.colors,
            reason=recommendation_reason["professional_reason"],
            image_url=matched_flower.image_url
        )
        
        print(f"     📸 최종 추천: {matched_flower.flower_name} → {matched_flower.image_url}")
        
        # 로깅
        processing_time_ms = int((time.time() - start_time) * 1000)
        tags = extracted_context.emotions + extracted_context.situations + extracted_context.moods + extracted_context.colors
        
        final_recommendation = {
            "main_flower": matched_flower.flower_name,
            "image_url": matched_flower.image_url,
            "reason": recommendation_reason["professional_reason"],
            "confidence": 0.8,
            "style_description": composition.composition_name,
            "color_theme": extracted_context.colors
        }
        
        self.logger.log_recommendation_process(
            customer_story=request.story,
            budget=None,  # MVP에서는 예산 제외
            extracted_context=extracted_context,
            emotion_analysis=emotion_analysis,
            flower_matches=[matched_flower],
            blend_recommendations=[composition],
            final_recommendation=final_recommendation,
            processing_time_ms=processing_time_ms,
            tags=tags
        )
        
        return RecommendResponse(
            recommendations=[item],
            emotions=emotion_analysis,  # 감정 분석 결과 포함
            story_id=story_id  # 스토리 ID 포함
        )
    
    def _convert_context_to_emotion_analysis(self, context: ExtractedContext):
        """추출된 맥락을 감정 분석 형식으로 변환"""
        from app.services.emotion_analyzer import EmotionAnalysis
        
        # 감정 점수 계산
        emotion_scores = {}
        total_score = 0
        
        # 감정 카테고리별 점수 할당
        for emotion in context.emotions:
            emotion_scores[emotion] = 1.0
            total_score += 1.0
        
        # 무드를 감정으로 매핑
        mood_to_emotion = {
            "차분한": "평화",
            "진지한": "진실",
            "은은한": "따뜻함",
            "따뜻한": "따뜻함",
            "로맨틱한": "사랑",
            "경쾌한": "기쁨"
        }
        
        for mood in context.moods:
            emotion = mood_to_emotion.get(mood, mood)
            if emotion in emotion_scores:
                emotion_scores[emotion] += 0.5
            else:
                emotion_scores[emotion] = 0.5
            total_score += 0.5
        
        # 비율로 변환
        if total_score > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = emotion_scores[emotion] / total_score
        
        # 상위 감정 선택
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_emotions[0][0] if sorted_emotions else "기쁨"
        secondary = sorted_emotions[1][0] if len(sorted_emotions) > 1 else "사랑"
        tertiary = sorted_emotions[2][0] if len(sorted_emotions) > 2 else "감사"
        
        # EmotionAnalysis는 List[EmotionAnalysis] 형태로 반환해야 함
        emotions = []
        for emotion, score in sorted_emotions[:3]:  # 상위 3개 감정만
            emotions.append(EmotionAnalysis(
                emotion=emotion,
                percentage=score * 100,  # 비율을 퍼센트로 변환
                description=f"{emotion} 감정이 {score * 100:.1f}%로 나타남"
            ))
        
        return emotions
    
    def run_with_details(self, request: RecommendRequest) -> Dict[str, Any]:
        """상세 정보와 함께 추천 체인 실행 (디버깅용)"""
        start_time = time.time()
        print(f"🔍 통합 추천 체인 상세 실행")
        
        # 1. 맥락 추출
        extracted_context = self.context_extractor.extract_context_realtime(request.story)
        
        # 2. 감정 분석
        emotion_analysis = self._convert_context_to_emotion_analysis(extracted_context)
        
        # 3. 꽃 매칭
        matched_flower = self.flower_matcher.match(emotion_analysis, request.story, "meaning_based")
        
        # 4. 꽃 구성
        composition = self.composition_recommender.recommend(matched_flower, emotion_analysis)
        
        # 5. 이미지 매칭 및 이유 생성
        detailed_items = []
        img = self.image_matcher.match(matched_flower)
        recommendation_reason = self.reason_generator.generate_reason(
            emotion_analysis,
            [matched_flower],
            composition,
            request.story,
            extracted_context.colors
        )
        
        detailed_items.append({
            "composition": composition,
            "image": {
                "url": img.url,
                "confidence": img.confidence,
                "image_id": img.image_id
            },
            "reason": recommendation_reason
        })
        
        # 최고 점수 구성 선택
        best_composition = composition
        best_img = img
        best_reason = recommendation_reason
        
        # 최종 추천 정보
        final_recommendation = {
            "main_flower": matched_flower.flower_name,
            "image_url": img.url,
            "reason": recommendation_reason["professional_reason"],
            "confidence": img.confidence,
            "style_description": composition.composition_name,
            "color_theme": extracted_context.colors
        }
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        tags = extracted_context.emotions + extracted_context.situations + extracted_context.moods + extracted_context.colors
        
        return {
            "extracted_context": extracted_context,
            "emotion_analysis": emotion_analysis,
            "flower_matches": [matched_flower],
            "blend_recommendations": [composition],
            "detailed_items": detailed_items,
            "final_recommendation": final_recommendation,
            "processing_time_ms": processing_time_ms,
            "tags": tags,
            "request": request
        }
