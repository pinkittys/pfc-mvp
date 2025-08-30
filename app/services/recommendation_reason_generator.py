"""
추천 이유 생성 서비스 (MVP 버전 - 예산 제외)
"""
import openai
from typing import List, Dict, Any
from app.models.schemas import EmotionAnalysis, FlowerMatch
from .flower_blend_recommender import BlendRecommendation

class RecommendationReasonGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI()
    
    def generate_reason(self, emotion_analysis: List[EmotionAnalysis], 
                                     flower_matches: List, 
                                     blend_recommendation,
                                     customer_story: str,
                                     color_preference: List[str] = None) -> Dict[str, str]:
        """추천 이유 생성"""
        try:
            # 프롬프트 생성
            prompt = self._create_reason_prompt(
                emotion_analysis, 
                flower_matches, 
                blend_recommendation, 
                customer_story, 
                color_preference
            )
            
            # OpenAI API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4",  # GPT-4로 업그레이드 (더 정교한 추천 이유 생성)
                messages=[
                    {"role": "system", "content": "당신은 전문적인 플로리스트입니다. 고객의 사연과 감정을 이해하고, 추천된 꽃의 꽃말과 특징을 고려하여 따뜻하고 담백한 추천 이유를 작성해주세요. 1-2문장으로 간결하게 작성하고, 블렌딩 꽃들에 대한 설명은 제외해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            professional_reason = response.choices[0].message.content.strip()
            
            # 첫 번째 감정의 emotion 속성 사용
            primary_emotion = emotion_analysis[0].emotion if emotion_analysis else "따뜻함"
            
            # blend_recommendation이 CompositionRecommender 결과인지 확인
            if hasattr(blend_recommendation, 'composition_name'):
                style_description = blend_recommendation.composition_name
            elif hasattr(blend_recommendation, 'blend') and hasattr(blend_recommendation.blend, 'style_description'):
                style_description = blend_recommendation.blend.style_description
            else:
                style_description = "Beautiful Arrangement"
            
            return {
                "professional_reason": professional_reason,
                "emotion_summary": f"{primary_emotion}을 중심으로 한 구성",
                "style_description": style_description
            }
            
        except Exception as e:
            print(f"❌ LLM 추천 이유 생성 실패: {e}")
            # 기본 추천 이유 생성
            return self._generate_fallback_reason(emotion_analysis, blend_recommendation)
    
    def _create_reason_prompt(self, emotion_analysis: List[EmotionAnalysis], 
                            flower_matches: List, 
                            blend_recommendation,
                            customer_story: str,
                            color_preference: List[str] = None) -> str:
        """추천 이유 생성 프롬프트"""
        
        # flower_matches에서 첫 번째 꽃 정보 추출
        if flower_matches and len(flower_matches) > 0:
            main_flower = flower_matches[0].flower_name if hasattr(flower_matches[0], 'flower_name') else "꽃"
        else:
            main_flower = "꽃"
        
        # 첫 번째 감정의 emotion 속성 사용
        primary_emotion = emotion_analysis[0].emotion if emotion_analysis else "따뜻함"
        secondary_emotion = emotion_analysis[1].emotion if len(emotion_analysis) > 1 else "감사"
        
        prompt = f"""
고객님의 사연과 감정을 바탕으로 꽃 추천 이유를 작성해주세요.

고객 스토리: {customer_story}

분석된 감정:
- 주요 감정: {primary_emotion}
- 보조 감정: {secondary_emotion}

추천된 꽃: {main_flower}

요구사항:
1. 고객님의 사연과 감정에 공감하는 따뜻한 톤
2. 추천된 꽃의 꽃말과 특징을 고려한 설명
3. 1-2문장으로 간결하게 작성
4. 블렌딩 꽃들에 대한 설명은 제외
5. 담백하고 진정성 있는 메시지

추천 이유를 작성해주세요:

예시:
- 생일 축하: "생일을 축하하는 기쁨과 희망이 담긴 꽃입니다."
- 위로: "마음을 위로하는 따뜻한 꽃입니다."
- 감사: "진심 어린 감사가 담긴 꽃입니다."
"""
        return prompt
    
    def _generate_fallback_reason(self, emotion_analysis: List[EmotionAnalysis], 
                                blend_recommendation) -> Dict[str, str]:
        """기본 추천 이유 생성 (LLM 실패 시)"""
        
        # flower_matches에서 첫 번째 꽃 정보 추출
        if hasattr(blend_recommendation, 'main_flower'):
            main_flower = blend_recommendation.main_flower
        else:
            main_flower = "꽃"
        
        # 첫 번째 감정의 emotion 속성 사용
        primary_emotion = emotion_analysis[0].emotion if emotion_analysis else "따뜻함"
        
        emotion_map = {
            "사랑": "사랑의 마음을 담아",
            "감사": "감사한 마음을 담아",
            "축하": "축하의 마음을 담아",
            "위로": "위로의 마음을 담아",
            "기쁨": "기쁜 마음을 담아",
            "슬픔": "따뜻한 마음을 담아"
        }
        
        emotion_phrase = emotion_map.get(primary_emotion, "진심 어린 마음을 담아")
        
        reason = f"{emotion_phrase} {main_flower}입니다."
        
        # blend_recommendation이 CompositionRecommender 결과인지 확인
        if hasattr(blend_recommendation, 'composition_name'):
            style_description = blend_recommendation.composition_name
        elif hasattr(blend_recommendation, 'blend') and hasattr(blend_recommendation.blend, 'style_description'):
            style_description = blend_recommendation.blend.style_description
        else:
            style_description = "Beautiful Arrangement"
        
        return {
            "professional_reason": reason,
            "emotion_summary": f"{primary_emotion}을 중심으로 한 구성",
            "style_description": style_description
        }
