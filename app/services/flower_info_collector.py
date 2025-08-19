import openai
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.services.flower_dictionary import FlowerDictionaryService

class FlowerInfoCollector:
    """LLM 기반 꽃 정보 수집 서비스"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.dictionary_service = FlowerDictionaryService()
        
    def collect_flower_info(self, scientific_name: str, korean_name: str, color: str) -> Dict[str, Any]:
        """특정 꽃의 정보를 LLM으로 수집"""
        
        prompt = f"""
다음 꽃에 대한 상세한 정보를 수집해주세요:

꽃 정보:
- 학명: {scientific_name}
- 한국어 이름: {korean_name}
- 색상: {color}

다음 형식으로 JSON 응답을 제공해주세요:

{{
    "flower_meanings": {{
        "primary": ["주요 꽃말 1", "주요 꽃말 2"],
        "secondary": ["보조 꽃말 1", "보조 꽃말 2"],
        "other": ["기타 꽃말 1", "기타 꽃말 2"],
        "phrases": ["문장형 꽃말 1", "문장형 꽃말 2", "문장형 꽃말 3"]
    }},
    "moods": {{
        "primary": ["주요 무드 1", "주요 무드 2"],
        "secondary": ["보조 무드 1", "보조 무드 2"],
        "other": ["기타 무드 1", "기타 무드 2"]
    }},
    "characteristics": {{
        "care_tips": ["관리 주의점 1", "관리 주의점 2"],
        "fragrance": ["향기 특징 1", "향기 특징 2"],
        "features": ["특별한 특징 1", "특별한 특징 2"]
    }},
    "cultural_references": {{
        "movies": ["영화 제목 - 구체적인 장면 설명 (예: '타이타닉' - 잭이 로즈에게 장미를 선물하며 '내 마음을 담아'라고 말하는 장면)"],
        "books": ["책 제목 - 구체적인 문장이나 장면 (예: '리틀 프린스' - '네가 장미를 아름답게 만든 거야'라는 대사)"],
        "literature": ["시나 문학 작품 - 구체적인 구절 (예: '백년을 살아도 장미를 사랑하리라' - '장미는 사랑의 상징이요'라는 구절)"],
        "classics": ["고전 작품 - 구체적인 장면 (예: '로미오와 줄리엣' - 줄리엣이 '장미는 다른 이름으로 불러도 향기롭다'라고 말하는 장면)"],
        "entertainment": ["드라마/예능 - 구체적인 장면 (예: '꽃보다 남자' - 구준표가 금잔디에게 장미를 선물하며 '내 마음을 받아줘'라고 말하는 장면)"]
    }},
    "design_compatibility": ["궁합이 좋은 꽃 1", "궁합이 좋은 꽃 2", "궁합이 좋은 꽃 3"],
    "design_incompatibility": ["궁합이 좋지 않은 꽃 1", "궁합이 좋지 않은 꽃 2"],
    "seasonality": ["봄", "여름", "가을", "겨울"],
    "care_level": "쉬움/보통/어려움",
    "lifespan": "1주일/2주일/3주일/1개월",
    "source": "정보 출처",
    
    "usage_contexts": {{
        "graduation": {{"frequency": "high/medium/low", "description": "졸업식에서의 사용 빈도와 이유"}},
        "parents_day": {{"frequency": "high/medium/low", "description": "어버이날에서의 사용 빈도와 이유"}},
        "wedding": {{"frequency": "high/medium/low", "description": "웨딩에서의 사용 빈도와 이유"}},
        "entrance_ceremony": {{"frequency": "high/medium/low", "description": "입학식에서의 사용 빈도와 이유"}},
        "funeral": {{"frequency": "high/medium/low", "description": "장례식에서의 사용 빈도와 이유"}},
        "birthday": {{"frequency": "high/medium/low", "description": "생일에서의 사용 빈도와 이유"}},
        "anniversary": {{"frequency": "high/medium/low", "description": "기념일에서의 사용 빈도와 이유"}},
        "apology": {{"frequency": "high/medium/low", "description": "사과할 때의 사용 빈도와 이유"}},
        "encouragement": {{"frequency": "high/medium/low", "description": "격려할 때의 사용 빈도와 이유"}},
        "business": {{"frequency": "high/medium/low", "description": "비즈니스 상황에서의 사용 빈도와 이유"}}
    }},
    "relationship_suitability": {{
        "parent_child": {{"suitability": "excellent/good/neutral/poor", "context": "부모-자식 관계에서의 적합성과 이유"}},
        "teacher_student": {{"suitability": "excellent/good/neutral/poor", "context": "선생님-학생 관계에서의 적합성과 이유"}},
        "romantic": {{"suitability": "excellent/good/neutral/poor", "context": "연인 관계에서의 적합성과 이유"}},
        "friend": {{"suitability": "excellent/good/neutral/poor", "context": "친구 관계에서의 적합성과 이유"}},
        "colleague": {{"suitability": "excellent/good/neutral/poor", "context": "동료 관계에서의 적합성과 이유"}},
        "senior_junior": {{"suitability": "excellent/good/neutral/poor", "context": "선후배 관계에서의 적합성과 이유"}}
    }},
    "seasonal_events": ["봄 졸업식", "가을 입학식", "여름 생일", "겨울 연말"],
    "cultural_significance": {{
        "korean_tradition": ["한국 전통에서의 의미 1", "한국 전통에서의 의미 2"],
        "western_culture": ["서양 문화에서의 의미 1", "서양 문화에서의 의미 2"],
        "modern_korea": ["현대 한국에서의 의미 1", "현대 한국에서의 의미 2"]
    }},
    "popularity_by_occasion": {{
        "graduation": "very_popular/popular/neutral/unpopular",
        "wedding": "very_popular/popular/neutral/unpopular",
        "parents_day": "very_popular/popular/neutral/unpopular",
        "birthday": "very_popular/popular/neutral/unpopular",
        "anniversary": "very_popular/popular/neutral/unpopular"
    }}
}}

주의사항:
1. 실제 존재하는 정보만 제공하세요
2. 한국어로 응답하세요
3. 꽃말은 감정이나 상황과 관련된 의미를 중심으로 작성하세요 (예: 사랑, 감사, 그리움, 기쁨, 위로, 격려, 희망, 만남, 발표, 후배 등)
4. 문장형 꽃말(phrases)에는 "당신의 시작을 응원해", "나를 기억해주세요", "넌 할 수 있어", "오늘도 힘내세요" 같은 문장 형태의 의미를 포함하세요
5. 무드는 디자인이나 분위기와 관련된 느낌을 중심으로 작성하세요 (예: 우아한, 내추럴한, 심플한, 강렬한, 청초한, 따뜻한, 유니크한, 격식있는, 경쾌한, 트렌디한, 로맨틱한, 차분한 등)
6. 문화적 참조는 단순히 제목에 꽃 이름이 들어간 것이 아니라, 실제 장면에서 꽃이 어떻게 사용되었는지 구체적으로 설명하세요
7. 궁합 정보는 실제 꽃 이름을 사용하세요
8. usage_contexts는 실제 상황에서의 사용 빈도를 정확히 반영하세요 (예: 프리지아는 졸업식에서 매우 인기, 카네이션은 어버이날 대표 꽃)
9. relationship_suitability는 관계별 적합성을 현실적으로 평가하세요 (예: 카네이션은 부모님께는 excellent, 연인에게는 poor)
10. seasonal_events는 계절과 이벤트의 조합을 구체적으로 작성하세요 (예: "봄 졸업식", "가을 입학식")
11. cultural_significance는 한국과 서양 문화에서의 차이점을 명확히 구분하세요
12. popularity_by_occasion는 실제 인기도를 반영하세요 (very_popular > popular > neutral > unpopular)
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 꽃 전문가입니다. 정확하고 상세한 꽃 정보를 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # JSON 파싱
            flower_info = json.loads(content)
            
            # 기본 정보 추가
            flower_info.update({
                "scientific_name": scientific_name,
                "korean_name": korean_name,
                "color": color
            })
            
            return flower_info
            
        except Exception as e:
            print(f"❌ 꽃 정보 수집 실패 ({scientific_name}-{color}): {e}")
            return self._get_default_flower_info(scientific_name, korean_name, color)
    
    def _get_default_flower_info(self, scientific_name: str, korean_name: str, color: str) -> Dict[str, Any]:
        """기본 꽃 정보 템플릿"""
        return {
            "scientific_name": scientific_name,
            "korean_name": korean_name,
            "color": color,
            "flower_meanings": {
                "primary": ["아름다움"],
                "secondary": ["자연스러움"],
                "other": [],
                "phrases": []
            },
            "moods": {
                "primary": ["아름다움"],
                "secondary": ["자연스러움"],
                "other": []
            },
            "characteristics": {
                "care_tips": ["적절한 온도 유지"],
                "fragrance": ["자연스러운 향"],
                "features": ["아름다운 형태"]
            },
            "cultural_references": {
                "movies": [],
                "books": [],
                "literature": [],
                "classics": [],
                "entertainment": []
            },
            "design_compatibility": [],
            "design_incompatibility": [],
            "seasonality": ["봄", "여름", "가을", "겨울"],
            "care_level": "보통",
            "lifespan": "1주일",
            "source": "기본 정보",
            
            # 새로운 필드들
            "usage_contexts": {
                "graduation": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "parents_day": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "wedding": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "entrance_ceremony": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "funeral": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "birthday": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "anniversary": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "apology": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "encouragement": {"frequency": "neutral", "description": "기본적인 사용 가능"},
                "business": {"frequency": "neutral", "description": "기본적인 사용 가능"}
            },
            "relationship_suitability": {
                "parent_child": {"suitability": "neutral", "context": "기본적인 적합성"},
                "teacher_student": {"suitability": "neutral", "context": "기본적인 적합성"},
                "romantic": {"suitability": "neutral", "context": "기본적인 적합성"},
                "friend": {"suitability": "neutral", "context": "기본적인 적합성"},
                "colleague": {"suitability": "neutral", "context": "기본적인 적합성"},
                "senior_junior": {"suitability": "neutral", "context": "기본적인 적합성"}
            },
            "seasonal_events": [],
            "cultural_significance": {
                "korean_tradition": [],
                "western_culture": [],
                "modern_korea": []
            },
            "popularity_by_occasion": {
                "graduation": "neutral",
                "wedding": "neutral",
                "parents_day": "neutral",
                "birthday": "neutral",
                "anniversary": "neutral"
            }
        }
    
    def batch_collect_flower_info(self, flower_list: List[Dict[str, str]]) -> List[str]:
        """여러 꽃의 정보를 일괄 수집"""
        created_ids = []
        
        for flower in flower_list:
            try:
                print(f"🔄 {flower['scientific_name']}-{flower['color']} 정보 수집 중...")
                
                flower_info = self.collect_flower_info(
                    flower['scientific_name'],
                    flower['korean_name'],
                    flower['color']
                )
                
                flower_id = self.dictionary_service.create_flower_entry(flower_info)
                created_ids.append(flower_id)
                
                print(f"✅ {flower_id} 정보 수집 완료")
                
            except Exception as e:
                print(f"❌ {flower['scientific_name']}-{flower['color']} 정보 수집 실패: {e}")
        
        return created_ids
    
    def update_existing_flower_info(self, flower_id: str) -> bool:
        """기존 꽃 정보 업데이트"""
        try:
            flower = self.dictionary_service.get_flower_info(flower_id)
            if not flower:
                return False
            
            print(f"🔄 {flower_id} 정보 업데이트 중...")
            
            updated_info = self.collect_flower_info(
                flower.scientific_name,
                flower.korean_name,
                flower.color
            )
            
            # ID 제거 (업데이트 시에는 불필요)
            updated_info.pop("id", None)
            
            success = self.dictionary_service.update_flower_info(flower_id, updated_info)
            
            if success:
                print(f"✅ {flower_id} 정보 업데이트 완료")
            else:
                print(f"❌ {flower_id} 정보 업데이트 실패")
            
            return success
            
        except Exception as e:
            print(f"❌ {flower_id} 정보 업데이트 중 오류: {e}")
            return False
