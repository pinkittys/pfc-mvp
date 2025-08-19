from typing import Dict, List, Any, Optional, Tuple
from app.services.flower_matcher import FlowerMatcher
from app.services.flower_dictionary import FlowerDictionaryService
from app.services.realtime_context_extractor import RealtimeContextExtractor
import json

class EnhancedFlowerMatcher:
    """꽃 사전 정보를 활용한 향상된 꽃 매칭 서비스"""
    
    def __init__(self):
        self.flower_matcher = FlowerMatcher()
        self.dictionary_service = FlowerDictionaryService()
        self.context_extractor = RealtimeContextExtractor()
    
    def match_flowers_with_context(self, story: str, emotions: List[str] = None) -> Dict[str, Any]:
        """고객의 이야기와 맥락을 기반으로 가장 적합한 꽃 매칭"""
        
        # 1. 맥락 추출
        context = self.context_extractor.extract_context_realtime(story, emotions)
        
        # 2. 꽃 사전에서 유사한 꽃들 검색
        search_queries = self._generate_search_queries(context, story)
        candidate_flowers = []
        
        for query in search_queries:
            flowers = self.dictionary_service.search_flowers(query, story, limit=5)
            candidate_flowers.extend(flowers)
        
        # 3. 유사도 점수 계산
        scored_flowers = []
        for flower in candidate_flowers:
            score = self._calculate_similarity_score(flower, context, story)
            scored_flowers.append((flower, score))
        
        # 4. 점수 순으로 정렬
        scored_flowers.sort(key=lambda x: x[1], reverse=True)
        
        # 5. 상위 3개 꽃 선택
        top_flowers = scored_flowers[:3]
        
        # 6. 추천 이유 생성
        recommendation_reason = self._generate_recommendation_reason(
            top_flowers[0][0], context, story
        )
        
        return {
            "matched_flower": {
                "id": top_flowers[0][0].id,
                "scientific_name": top_flowers[0][0].scientific_name,
                "korean_name": top_flowers[0][0].korean_name,
                "color": top_flowers[0][0].color,
                "similarity_score": top_flowers[0][1]
            },
            "alternative_flowers": [
                {
                    "id": flower.id,
                    "scientific_name": flower.scientific_name,
                    "korean_name": flower.korean_name,
                    "color": flower.color,
                    "similarity_score": score
                }
                for flower, score in top_flowers[1:]
            ],
            "context": {
                "emotions": context.emotions,
                "situations": context.situations,
                "moods": context.moods,
                "colors": context.colors
            },
            "recommendation_reason": recommendation_reason,
            "flower_details": {
                "meanings": top_flowers[0][0].flower_meanings,
                "moods": top_flowers[0][0].moods,
                "characteristics": top_flowers[0][0].characteristics,
                "cultural_references": top_flowers[0][0].cultural_references,
                "design_compatibility": top_flowers[0][0].design_compatibility
            }
        }
    
    def _generate_search_queries(self, context, story: str) -> List[str]:
        """검색 쿼리 생성"""
        queries = []
        
        # 감정 기반 쿼리
        for emotion in context.emotions:
            queries.append(emotion)
        
        # 상황 기반 쿼리
        for situation in context.situations:
            queries.append(situation)
        
        # 무드 기반 쿼리
        for mood in context.moods:
            queries.append(mood)
        
        # 색상 기반 쿼리
        for color in context.colors:
            queries.append(color)
        
        # 스토리에서 키워드 추출
        story_keywords = self._extract_keywords_from_story(story)
        queries.extend(story_keywords)
        
        return list(set(queries))  # 중복 제거
    
    def _extract_keywords_from_story(self, story: str) -> List[str]:
        """스토리에서 키워드 추출"""
        keywords = []
        
        # 간단한 키워드 매핑
        keyword_mapping = {
            "사랑": ["사랑", "연인", "로맨스", "첫사랑", "아내", "남편"],
            "감사": ["감사", "고마워", "진심", "고생"],
            "그리움": ["그리움", "보고싶", "그립", "추억", "기억"],
            "기쁨": ["기쁨", "행복", "즐거워", "밝음", "축하"],
            "위로": ["위로", "힘들어", "아픈", "슬픈", "우울증"],
            "격려": ["격려", "응원", "할 수 있어", "힘내", "화이팅"],
            "희망": ["희망", "새로운", "시작", "미래"],
            "만남": ["만남", "기념", "첫만남", "주년"],
            "발표": ["발표", "시험", "면접", "프레젠테이션"],
            "후배": ["후배", "동료", "친구", "가족"]
        }
        
        story_lower = story.lower()
        for category, words in keyword_mapping.items():
            if any(word in story_lower for word in words):
                keywords.append(category)
        
        return keywords
    
    def _calculate_similarity_score(self, flower, context, story: str) -> float:
        """꽃과 맥락 간의 유사도 점수 계산"""
        score = 0.0
        
        # 1. 감정 매칭 (40%)
        emotion_score = self._calculate_emotion_similarity(flower, context.emotions)
        score += emotion_score * 0.4
        
        # 2. 상황 매칭 (30%)
        situation_score = self._calculate_situation_similarity(flower, context.situations)
        score += situation_score * 0.3
        
        # 3. 무드 매칭 (20%)
        mood_score = self._calculate_mood_similarity(flower, context.moods)
        score += mood_score * 0.2
        
        # 4. 색상 매칭 (10%)
        color_score = self._calculate_color_similarity(flower, context.colors)
        score += color_score * 0.1
        
        return score
    
    def _calculate_emotion_similarity(self, flower, emotions: List[str]) -> float:
        """감정 유사도 계산"""
        if not emotions:
            return 0.0
        
        flower_emotions = []
        for meanings in flower.flower_meanings.values():
            flower_emotions.extend(meanings)
        
        matches = 0
        for emotion in emotions:
            if any(emotion in flower_emotion for flower_emotion in flower_emotions):
                matches += 1
        
        return matches / len(emotions)
    
    def _calculate_situation_similarity(self, flower, situations: List[str]) -> float:
        """상황 유사도 계산"""
        if not situations:
            return 0.0
        
        flower_situations = []
        for meanings in flower.flower_meanings.values():
            flower_situations.extend(meanings)
        
        matches = 0
        for situation in situations:
            if any(situation in flower_situation for flower_situation in flower_situations):
                matches += 1
        
        return matches / len(situations)
    
    def _calculate_mood_similarity(self, flower, moods: List[str]) -> float:
        """무드 유사도 계산"""
        if not moods:
            return 0.0
        
        flower_moods = []
        for mood_list in flower.moods.values():
            flower_moods.extend(mood_list)
        
        matches = 0
        for mood in moods:
            if any(mood in flower_mood for flower_mood in flower_moods):
                matches += 1
        
        return matches / len(moods)
    
    def _calculate_color_similarity(self, flower, colors: List[str]) -> float:
        """색상 유사도 계산"""
        if not colors:
            return 0.0
        
        flower_color = flower.color.lower()
        matches = 0
        
        for color in colors:
            if color.lower() in flower_color or flower_color in color.lower():
                matches += 1
        
        return matches / len(colors)
    
    def _generate_recommendation_reason(self, flower, context, story: str) -> str:
        """추천 이유 생성"""
        
        # 꽃의 주요 의미들
        primary_meanings = flower.flower_meanings.get("primary", [])
        primary_moods = flower.moods.get("primary", [])
        
        # 맥락과 매칭되는 요소들
        matching_elements = []
        
        for emotion in context.emotions:
            if any(emotion in meaning for meaning in primary_meanings):
                matching_elements.append(f"'{emotion}'의 감정")
        
        for situation in context.situations:
            if any(situation in meaning for meaning in primary_meanings):
                matching_elements.append(f"'{situation}'의 상황")
        
        for mood in context.moods:
            if any(mood in flower_mood for flower_mood in primary_moods):
                matching_elements.append(f"'{mood}'의 분위기")
        
        # 추천 이유 구성
        if matching_elements:
            reason = f"{flower.korean_name}은 {', '.join(matching_elements)}에 완벽하게 어울리는 꽃이에요. "
        else:
            reason = f"{flower.korean_name}은 고객님의 상황에 특별히 의미있는 꽃이에요. "
        
        # 꽃의 특징 추가
        if flower.characteristics.get("features"):
            features = flower.characteristics["features"][:2]  # 상위 2개 특징만
            reason += f"{', '.join(features)}의 특징을 가지고 있어요. "
        
        # 문화적 참조 추가 (있는 경우)
        cultural_refs = []
        for category, refs in flower.cultural_references.items():
            if refs:
                cultural_refs.extend(refs[:1])  # 각 카테고리에서 1개씩
        
        if cultural_refs:
            reason += f"'{cultural_refs[0]}'에서도 등장하는 의미있는 꽃이에요. "
        
        reason += "고객님의 마음을 가장 잘 전달할 수 있는 꽃을 선택해드렸어요."
        
        return reason

