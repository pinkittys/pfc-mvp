"""
사연 유형 분류 서비스
"""
import os
import json
from typing import Dict, Any
from enum import Enum

class StoryType(Enum):
    EMOTION_FOCUSED = "emotion_focused"  # 감정 중심
    DESIGN_FOCUSED = "design_focused"    # 디자인/스타일 중심
    OCCASION_FOCUSED = "occasion_focused"  # 특별한 날/기념일 중심
    RELATIONSHIP_FOCUSED = "relationship_focused"  # 관계 중심

class StoryClassifier:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
    
    def classify_story(self, story: str) -> Dict[str, Any]:
        """사연 유형 분류 및 특성 추출"""
        if not self.openai_api_key:
            return self._fallback_classification(story)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._create_classification_prompt(story)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 고객의 사연을 분석하여 꽃다발 추천에 필요한 정보를 분류하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            result = response.choices[0].message.content
            print(f"🤖 LLM 응답: {result}")
            classification = self._parse_classification_response(result)
            print(f"🔍 원래 분류: {classification['story_type']}")
            
            # 생일/베프/밝고 경쾌한 사연은 감정 중심으로 강제 분류
            if "생일" in story or "베프" in story or "밝고 경쾌" in story:
                print(f"🔧 생일/베프 강제로 emotion_focused로 변경")
                classification["story_type"] = "emotion_focused"
                classification["primary_focus"] = "생일 축하 (감정 중심)"
            
            # 우드톤/내추럴 키워드가 있으면 강제로 design_focused로 분류
            elif "우드톤" in story or "내추럴" in story or "인테리어" in story:
                print(f"🔧 강제로 design_focused로 변경")
                classification["story_type"] = "design_focused"
                classification["primary_focus"] = "디자인 요구사항 (우드톤/내추럴/인테리어)"
            
            print(f"🔍 최종 분류: {classification['story_type']}")
            return classification
            
        except Exception as e:
            print(f"❌ 사연 분류 실패: {e}")
            print(f"🔧 폴백 시스템으로 전환")
            return self._fallback_classification(story)
        except:
            print(f"❌ 알 수 없는 사연 분류 실패")
            print(f"🔧 폴백 시스템으로 전환")
            return self._fallback_classification(story)
    
    def _create_classification_prompt(self, story: str) -> str:
        """분류 프롬프트 생성"""
        return f"""
다음 고객의 사연을 분석하여 꽃다발 추천에 필요한 정보를 분류해주세요:

고객 사연: "{story}"

다음 JSON 형식으로 응답해주세요:

{{
    "story_type": "emotion_focused|design_focused|occasion_focused|relationship_focused",
    "primary_focus": "주요 관심사 설명",
    "emotions": ["감정1", "감정2"],  // 감정이 주요한 경우만
    "design_preferences": {{
        "colors": ["색상1", "색상2"],
        "style": "스타일 설명",
        "mood": "분위기 설명"
    }},
    "occasion": "기념일/상황",  // 특별한 날인 경우
    "relationship": "관계",  // 특정 관계인 경우
    "confidence": 0.85
}}

분류 기준:
1. emotion_focused: 감정이나 마음이 주요한 사연 (사랑, 감사, 그리움, 응원, 신입 환영, 따뜻함 등)
2. design_focused: 디자인, 색상, 스타일이 주요한 사연 (인테리어, 컬러, 분위기, 그린톤 소파 등)
3. occasion_focused: 특별한 날이나 상황이 주요한 사연 (생일, 결혼, 승진, 첫 출근 등)
4. relationship_focused: 특정 관계가 주요한 사연 (부모님, 연인, 친구 등)

주의사항:
- 여러 요소가 복합적으로 나타날 수 있음
- 가장 중요한 요소를 우선으로 분류
- "신입 환영", "따뜻함", "싱그러움", "병원", "입원", "가족", "위로" 등은 emotion_focused로 분류
- **"우드톤", "내추럴", "인테리어", "어울리는", "가게", "카페" 등이 포함되면 반드시 design_focused로 분류**
- "그린톤 소파", "인테리어", "미니멀", "컬러 포인트" 등은 design_focused로 분류
- "첫 출근"은 occasion_focused로 분류할 수 있지만, "환영"의 의미가 강하면 emotion_focused
- **디자인 요구사항이 명확하면 반드시 design_focused로 분류** (예: "우드톤 인테리어와 어울리는 내추럴한 꽃")
- **기념일이라도 디자인 요구사항이 있으면 design_focused로 분류**
- **"우드톤 인테리어와 어울리는 내추럴한 꽃" → design_focused**
- 감정이 명확하지 않으면 다른 유형으로 분류
- 병원 관련 사연은 감정 중심으로 분류 (가족에 대한 걱정, 위로의 마음)
"""
    
    def _parse_classification_response(self, response: str) -> Dict[str, Any]:
        """분류 응답 파싱"""
        try:
            # JSON 추출
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            return {
                "story_type": data["story_type"],
                "primary_focus": data["primary_focus"],
                "emotions": data.get("emotions", []),
                "design_preferences": data.get("design_preferences", {}),
                "occasion": data.get("occasion", ""),
                "relationship": data.get("relationship", ""),
                "confidence": data.get("confidence", 0.8)
            }
            
        except Exception as e:
            print(f"❌ 분류 응답 파싱 실패: {e}")
            return self._fallback_classification(story)
    
    def _fallback_classification(self, story: str) -> Dict[str, Any]:
        """폴백 분류 로직"""
        # 간단한 키워드 기반 분류
        story_lower = story.lower()
        
        # 디자인 관련 키워드
        design_keywords = ["인테리어", "미니멀", "화이트", "컬러", "색상", "스타일", "분위기", "포인트", "그린톤", "소파", "거실", "우드톤", "내추럴", "가게", "카페", "어울리는"]
        # 감정 관련 키워드
        emotion_keywords = ["사랑", "감사", "그리움", "응원", "기쁨", "슬픔", "마음", "정성", "신입", "환영", "따뜻", "싱그럽", "화병", "책상", "병원", "입원", "병실", "삭막", "가족", "위로", "생일", "베프", "밝고 경쾌"]
        # 기념일 관련 키워드
        occasion_keywords = ["생일", "결혼", "승진", "졸업", "기념일", "축하", "첫 출근"]
        
        design_score = sum(1 for kw in design_keywords if kw in story_lower)
        emotion_score = sum(1 for kw in emotion_keywords if kw in story_lower)
        occasion_score = sum(1 for kw in occasion_keywords if kw in story_lower)
        
        print(f"🔍 폴백 분류 - 디자인: {design_score}, 감정: {emotion_score}, 기념일: {occasion_score}")
        
        # 생일/베프/밝고 경쾌한 사연은 감정 중심으로 분류
        if "생일" in story or "베프" in story or "밝고 경쾌" in story:
            story_type = "emotion_focused"
            print(f"🎂 생일/베프 감정 중심으로 분류됨")
        # 디자인 키워드가 있으면 우선적으로 design_focused로 분류
        elif design_score > 0:
            story_type = "design_focused"
            print(f"🎨 디자인 중심으로 분류됨 (점수: {design_score})")
        elif emotion_score > design_score and emotion_score > occasion_score:
            story_type = "emotion_focused"
            print(f"💝 감정 중심으로 분류됨 (점수: {emotion_score})")
        elif occasion_score > 0:
            story_type = "occasion_focused"
            print(f"🎉 기념일 중심으로 분류됨 (점수: {occasion_score})")
        else:
            story_type = "emotion_focused"  # 기본값
            print(f"💝 기본값으로 감정 중심 분류")
        
        return {
            "story_type": story_type,
            "primary_focus": "키워드 기반 분류",
            "emotions": [],
            "design_preferences": {},
            "occasion": "",
            "relationship": "",
            "confidence": 0.6
        }
