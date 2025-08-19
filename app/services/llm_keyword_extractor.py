"""
LLM 기반 키워드 추출 서비스
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.models.schemas import KeywordResponse

@dataclass
class ExtractedInfo:
    """추출된 정보"""
    # 주요 디멘전 4개 (프론트로 전송)
    emotion: List[str] = None
    situation: List[str] = None  
    mood: List[str] = None
    color_direction: List[str] = None
    
    # 추가 맥락 (추천 이유 생성용)
    season: Optional[str] = None
    relationship: Optional[str] = None
    budget_preference: Optional[str] = None
    size_preference: Optional[str] = None
    
    # 선호도 강도 (가중치 계산용)
    color_intensity: float = 0.0  # 0.0-1.0
    emotion_intensity: float = 0.0
    mood_intensity: float = 0.0
    situation_intensity: float = 0.0

class LLMKeywordExtractor:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다. 기본 추출기를 사용합니다.")
    
    def extract_with_llm(self, story: str) -> ExtractedInfo:
        """LLM을 사용한 키워드 추출"""
        if not self.openai_api_key:
            return self._fallback_extraction(story)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._create_extraction_prompt(story)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 꽃다발 추천을 위한 전문 키워드 추출기입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result)
            
        except Exception as e:
            print(f"❌ LLM 추출 실패: {e}")
            return self._fallback_extraction(story)
    
    def _create_extraction_prompt(self, story: str) -> str:
        """LLM 추출 프롬프트 생성"""
        return f"""
다음 고객의 이야기에서 꽃다발 추천에 필요한 정보를 추출해주세요:

고객 이야기: "{story}"

다음 JSON 형식으로 응답해주세요:

{{
    "emotion": ["감정1", "감정2"],  // 기쁨, 위로, 사랑, 감사, 슬픔, 분노 등
    "situation": ["상황1", "상황2"],  // 생일, 축하, 사과, 데이트, 위로, 감사 등
    "mood": ["무드1", "무드2"],  // 밝은, 로맨틱, 차분한, 경쾌한, 우아한, 귀여운 등
    "color_direction": ["색상방향1", "색상방향2"],  // warm, cool, pastel, vibrant, monochrome 등
    
    "season": "계절",  // 봄, 여름, 가을, 겨울, null
    "relationship": "관계",  // 연인, 친구, 가족, 동료, null
    "budget_preference": "가격대",  // 저렴, 중간, 고급, null
    "size_preference": "크기",  // 작은, 중간, 큰, null
    
    "intensity": {{
        "color": 0.8,  // 0.0-1.0, 색상 선호 강도
        "emotion": 0.6,  // 감정 표현 강도
        "mood": 0.7,  // 무드 표현 강도
        "situation": 0.9  // 상황 명확도
    }}
}}

주의사항:
1. 고객이 명시적으로 언급한 요소의 intensity를 높게 설정
2. "빨간 장미를 꼭 원해요" → color intensity: 0.9
3. "어떤 꽃이든 괜찮아요" → 모든 intensity: 0.3
4. null 값은 해당 정보가 없을 때만 사용
"""
    
    def _parse_llm_response(self, response: str) -> ExtractedInfo:
        """LLM 응답 파싱"""
        try:
            data = json.loads(response)
            
            intensity = data.get("intensity", {})
            
            return ExtractedInfo(
                emotion=data.get("emotion", []),
                situation=data.get("situation", []),
                mood=data.get("mood", []),
                color_direction=data.get("color_direction", []),
                season=data.get("season"),
                relationship=data.get("relationship"),
                budget_preference=data.get("budget_preference"),
                size_preference=data.get("size_preference"),
                color_intensity=intensity.get("color", 0.5),
                emotion_intensity=intensity.get("emotion", 0.5),
                mood_intensity=intensity.get("mood", 0.5),
                situation_intensity=intensity.get("situation", 0.5)
            )
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            return self._fallback_extraction("")
    
    def _fallback_extraction(self, story: str) -> ExtractedInfo:
        """기본 추출기 (LLM 실패 시)"""
        # 기존 키워드 추출기 로직 활용
        from app.services.keyword_extractor import KeywordExtractor
        basic_extractor = KeywordExtractor()
        basic_result = basic_extractor.run(story)
        
        return ExtractedInfo(
            emotion=basic_result.mood_tags,
            situation=[basic_result.occasion] if basic_result.occasion else [],
            mood=basic_result.mood_tags,
            color_direction=[],
            color_intensity=0.5,
            emotion_intensity=0.5,
            mood_intensity=0.5,
            situation_intensity=0.5
        )
    
    def run(self, story: str) -> KeywordResponse:
        """기존 인터페이스 호환"""
        extracted = self.extract_with_llm(story)
        
        # 기존 KeywordResponse 형식으로 변환
        keywords = []
        keywords.extend(extracted.emotion or [])
        keywords.extend(extracted.situation or [])
        keywords.extend(extracted.mood or [])
        keywords.extend(extracted.color_direction or [])
        
        return KeywordResponse(
            keywords=keywords,
            mood_tags=extracted.mood or [],
            occasion=extracted.situation[0] if extracted.situation else None
        )
