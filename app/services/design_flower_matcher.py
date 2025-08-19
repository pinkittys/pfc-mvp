"""
디자인 중심 꽃 매칭 서비스
"""
import os
import json
from typing import List, Dict, Any
from app.models.schemas import FlowerMatch

class DesignFlowerMatcher:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
        
        # 디자인 중심 꽃 데이터베이스
        self.design_flower_database = {
            "Gerbera Daisy": {
                "korean_name": "거베라",
                "scientific_name": "Gerbera × hybrida",
                "image_url": "/images/gerbera-daisy/노랑.webp",
                "keywords": ["활력", "포인트", "강렬함", "현대적"],
                "colors": ["노랑", "오렌지", "빨강", "핑크"],
                "styles": ["모던", "미니멀", "포인트", "강렬"]
            },
            "Dahlia": {
                "korean_name": "다알리아",
                "scientific_name": "Dahlia",
                "image_url": "/images/dahlia/옐로우.webp",
                "keywords": ["화려함", "에너지", "포인트", "현대적"],
                "colors": ["노랑", "오렌지", "빨강", "보라"],
                "styles": ["모던", "화려", "포인트", "강렬"]
            },
            "Rose": {
                "korean_name": "장미",
                "scientific_name": "Rosa",
                "image_url": "/images/rose/핑크.webp",
                "keywords": ["우아함", "클래식", "포인트", "세련됨"],
                "colors": ["핑크", "빨강", "화이트", "보라"],
                "styles": ["클래식", "우아", "세련", "포인트"]
            },
            "Lily": {
                "korean_name": "백합",
                "scientific_name": "Lilium",
                "image_url": "/images/lily/화이트.webp",
                "keywords": ["순수", "미니멀", "클린", "세련됨"],
                "colors": ["화이트", "크림", "연핑크"],
                "styles": ["미니멀", "클린", "세련", "순수"]
            },
            "Tulip": {
                "korean_name": "튤립",
                "scientific_name": "Tulipa",
                "image_url": "/images/tulip/옐로우.webp",
                "keywords": ["봄", "신선함", "모던", "미니멀"],
                "colors": ["노랑", "핑크", "화이트", "보라"],
                "styles": ["미니멀", "모던", "신선", "클린"]
            },
            "Garden Peony": {
                "korean_name": "작약",
                "scientific_name": "Paeonia lactiflora",
                "image_url": "/images/garden-peony/핑크.webp",
                "keywords": ["우아함", "클래식", "세련됨", "포인트"],
                "colors": ["핑크", "화이트", "크림", "연보라"],
                "styles": ["클래식", "우아", "세련", "포인트"]
            }
        }
    
    def match_by_design(self, design_preferences: Dict[str, Any], story: str) -> FlowerMatch:
        """디자인 선호도 기반 꽃 매칭"""
        # 생일/베프/밝고 경쾌한 사연은 감정 중심으로 처리
        if "생일" in story or "베프" in story or "밝고 경쾌" in story:
            print(f"🎂 DesignFlowerMatcher에서 생일/베프 감정 처리")
            from app.services.emotion_analyzer import EmotionAnalyzer
            emotion_analyzer = EmotionAnalyzer()
            emotions = emotion_analyzer.analyze(story)
            print(f"🎂 감정 분석 결과: {emotions}")
        
        if not self.openai_api_key:
            return self._fallback_design_match(design_preferences, story)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._create_design_matching_prompt(design_preferences, story)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 디자인과 스타일 요구사항에 맞는 꽃을 매칭하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            return self._parse_design_matching_response(result, design_preferences)
            
        except Exception as e:
            print(f"❌ 디자인 꽃 매칭 실패: {e}")
            return self._fallback_design_match(design_preferences, story)
    
    def _create_design_matching_prompt(self, design_preferences: Dict[str, Any], story: str) -> str:
        """디자인 매칭 프롬프트 생성"""
        colors = design_preferences.get("colors", [])
        style = design_preferences.get("style", "")
        mood = design_preferences.get("mood", "")
        
        return f"""
다음 디자인 요구사항에 가장 적합한 꽃을 선택해주세요:

고객 사연: "{story}"
색상 선호: {colors}
스타일: {style}
분위기: {mood}

다음 꽃들 중에서 가장 적합한 하나를 선택해주세요:

1. Gerbera Daisy (거베라): 활력, 포인트, 강렬함, 현대적 - 노랑, 오렌지, 빨강, 핑크
2. Dahlia (다알리아): 화려함, 에너지, 포인트, 현대적 - 노랑, 오렌지, 빨강, 보라
3. Rose (장미): 우아함, 클래식, 포인트, 세련됨 - 핑크, 빨강, 화이트, 보라
4. Lily (백합): 순수, 미니멀, 클린, 세련됨 - 화이트, 크림, 연핑크
5. Tulip (튤립): 봄, 신선함, 모던, 미니멀 - 노랑, 핑크, 화이트, 보라
6. Garden Peony (모란): 우아함, 클래식, 세련됨, 포인트 - 핑크, 화이트, 크림, 연보라

다음 JSON 형식으로 응답해주세요:

{{
    "flower_name": "선택된 꽃의 영어 이름",
    "reason": "감성적이고 따뜻한 추천 이유 (2-3문장, 컨시어지 톤)",
    "design_hashtags": ["#해시태그1", "#해시태그2"]
}}

선택 기준:
1. 고객이 요청한 색상과 가장 잘 맞는 꽃 (핑크 요청 시 모란 우선)
2. 스타일과 분위기 요구사항과 일치
3. 인테리어나 디자인 맥락에 적합
4. 포인트 컬러나 강렬함 요구사항 반영

중요한 규칙:
- 핑크 색상 요청이 있으면 Garden Peony (모란)을 우선 선택
- 그린톤과 어울리는 꽃 요청이 있으면 Garden Peony (모란)을 우선 선택
- 강렬한 포인트 컬러 요청이 있으면 Gerbera Daisy (거베라)를 우선 선택
- 미니멀한 요청이 있으면 Lily (백합)를 우선 선택

추천 이유 작성 가이드:
- 감성적이고 따뜻한 어투 사용
- 왜 이 꽃이 선택되었는지 자연스럽게 설명
- 색상과 스타일의 조화를 강조
- 인테리어와의 어울림을 언급
- 최소 2-3문장으로 구성
- 기계적이지 않고 친근한 톤 유지
"""
    
    def _parse_design_matching_response(self, response: str, design_preferences: Dict[str, Any]) -> FlowerMatch:
        """디자인 매칭 응답 파싱"""
        try:
            # JSON 추출
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            flower_name = data["flower_name"]
            
            # 꽃 데이터베이스에서 정보 가져오기
            flower_data = self.design_flower_database.get(flower_name, self.design_flower_database["Gerbera Daisy"])
            
            # 디자인 기반 해시태그 생성
            design_hashtags = data.get("design_hashtags", self._generate_design_hashtags(design_preferences))
            
            return FlowerMatch(
                flower_name=flower_name,
                korean_name=flower_data["korean_name"],
                scientific_name=flower_data["scientific_name"],
                image_url=flower_data["image_url"],
                keywords=flower_data["keywords"],
                hashtags=design_hashtags
            )
            
        except Exception as e:
            print(f"❌ 디자인 매칭 응답 파싱 실패: {e}")
            return self._fallback_design_match(design_preferences, "")
    
    def _fallback_design_match(self, design_preferences: Dict[str, Any], story: str) -> FlowerMatch:
        """폴백 디자인 매칭"""
        colors = design_preferences.get("colors", [])
        style = design_preferences.get("style", "").lower()
        
        # 병원 관련 사연은 밝고 희망적인 꽃 우선
        if "병원" in story or "입원" in story or "병실" in story or "삭막" in story:
            flower_name = "Gerbera Daisy"  # 밝고 희망적인 거베라
        # 그린톤 소파 매칭 (우선순위 높음)
        elif "그린" in story or "green" in story.lower():
            flower_name = "Garden Peony"  # 그린톤과 어울리는 핑크 작약
        # 색상 우선 매칭
        elif "white" in colors or "화이트" in story:
            flower_name = "Lily"  # 화이트 백합
        elif "yellow" in colors or "노랑" in story or "강렬" in story:
            flower_name = "Gerbera Daisy"  # 노란색 거베라
        elif "pink" in colors or "핑크" in story:
            flower_name = "Garden Peony"  # 핑크 작약
        elif "red" in colors or "빨강" in story:
            flower_name = "Rose"  # 빨간 장미
        elif "purple" in colors or "보라" in story:
            flower_name = "Dahlia"  # 보라 다알리아
        else:
            # 스타일 기반 매칭
            if "미니멀" in style or "모던" in style:
                flower_name = "Gerbera Daisy"
            elif "클래식" in style or "우아" in style:
                flower_name = "Garden Peony"
            else:
                flower_name = "Gerbera Daisy"  # 기본값을 거베라로 변경 (밝고 희망적)
        
        flower_data = self.design_flower_database[flower_name]
        design_hashtags = self._generate_design_hashtags(design_preferences)
        
        return FlowerMatch(
            flower_name=flower_name,
            korean_name=flower_data["korean_name"],
            scientific_name=flower_data["scientific_name"],
            image_url=flower_data["image_url"],
            keywords=flower_data["keywords"],
            hashtags=design_hashtags
        )
    
    def _generate_design_hashtags(self, design_preferences: Dict[str, Any]) -> List[str]:
        """디자인 기반 해시태그 생성"""
        hashtags = []
        
        colors = design_preferences.get("colors", [])
        style = design_preferences.get("style", "")
        mood = design_preferences.get("mood", "")
        
        if "강렬" in mood or "포인트" in style:
            hashtags.append("#강렬한컬러")
        if "미니멀" in style:
            hashtags.append("#미니멀")
        if "모던" in style:
            hashtags.append("#모던")
        if "인테리어" in design_preferences.get("situations", []):
            hashtags.append("#인테리어포인트")
        
        return hashtags[:3]  # 최대 3개
    
    def _generate_warm_recommendation_reason(self, flower_name: str, design_preferences: Dict[str, Any], story: str) -> str:
        """감성적이고 따뜻한 추천 이유 생성"""
        colors = design_preferences.get("colors", [])
        style = design_preferences.get("style", "")
        mood = design_preferences.get("mood", "")
        
        # 꽃별 맞춤 추천 이유
        flower_reasons = {
            "Gerbera Daisy": {
                "강렬": "거베라의 생동감 넘치는 노란색이 미니멀한 화이트 공간에 완벽한 포인트가 되어드릴 거예요. 강렬하면서도 현대적인 느낌으로 공간에 활기를 불어넣어줄 거예요.",
                "미니멀": "거베라의 깔끔한 형태와 선명한 색감이 미니멀한 인테리어와 조화롭게 어우러져요. 단순함 속에서도 눈에 띄는 포인트가 되어 공간을 더욱 세련되게 만들어줄 거예요.",
                "기본": "거베라의 밝고 경쾌한 매력이 공간에 생기를 불어넣어줄 거예요. 화이트 배경과 대비되는 선명한 색감으로 완벽한 포인트 컬러 역할을 해드릴 거예요."
            },
            "Dahlia": {
                "강렬": "다알리아의 화려하고 에너지 넘치는 색감이 공간에 강렬한 포인트를 만들어줄 거예요. 미니멀한 배경과 대비되어 더욱 돋보이는 매력을 선사해드릴 거예요.",
                "기본": "다알리아의 풍성하고 우아한 모습이 공간에 세련된 포인트가 되어드릴 거예요. 강렬하면서도 고급스러운 느낌으로 인테리어를 완성해줄 거예요."
            },
            "Rose": {
                "우아": "장미의 클래식하고 우아한 매력이 공간에 세련된 포인트를 만들어줄 거예요. 로맨틱하면서도 고급스러운 느낌으로 인테리어를 더욱 아름답게 완성해드릴 거예요.",
                "기본": "장미의 영원한 아름다움이 공간에 우아한 포인트가 되어드릴 거예요. 클래식하면서도 현대적인 느낌으로 시간이 지나도 변함없는 매력을 선사해드릴 거예요."
            },
            "Lily": {
                "미니멀": "백합의 순수하고 깔끔한 아름다움이 미니멀한 공간과 완벽하게 어우러져요. 화이트의 순백함이 공간에 고요하고 세련된 분위기를 만들어줄 거예요.",
                "기본": "백합의 순수하고 우아한 매력이 공간에 고요한 아름다움을 선사해드릴 거예요. 미니멀하면서도 세련된 느낌으로 공간을 더욱 아름답게 완성해줄 거예요."
            },
            "Garden Peony": {
                "그린톤": "작약의 부드럽고 우아한 핑크 톤이 그린톤과 완벽한 조화를 이루어요. 자연스러운 색상 조합으로 따뜻하고 포근한 분위기를 만들어줄 거예요.",
                "우아": "작약의 클래식하고 우아한 매력이 공간에 세련된 포인트를 만들어줄 거예요. 로맨틱하면서도 고급스러운 느낌으로 인테리어를 더욱 아름답게 완성해드릴 거예요.",
                "기본": "작약의 풍성하고 우아한 아름다움이 공간에 따뜻한 포인트가 되어드릴 거예요. 자연스럽고 편안한 느낌으로 공간을 더욱 아름답게 완성해줄 거예요."
            }
        }
        
        # 생일/베프 사연에 맞는 추천 이유 우선 처리
        if "생일" in story or "베프" in story or "밝고 경쾌" in story:
            if flower_name == "Gerbera Daisy":
                return "베프의 생일을 축하하는 기쁨과 희망이 담긴 밝은 꽃다발입니다. 옐로우 거베라의 활기찬 에너지가 생일의 특별한 순간을 더욱 빛나게 해줄 거예요."
            else:
                return f"{flower_name}의 아름다움이 베프의 생일을 축하하는 마음을 담아 전해줄 거예요. 밝고 경쾌한 분위기로 특별한 순간을 더욱 특별하게 만들어줄 거예요."
        
        # 상황에 맞는 추천 이유 선택
        flower_reason = flower_reasons.get(flower_name, flower_reasons["Gerbera Daisy"])
        
        if "그린" in story or "green" in story.lower():
            return flower_reason.get("그린톤", flower_reason["기본"])
        elif "강렬" in mood:
            return flower_reason.get("강렬", flower_reason["기본"])
        elif "미니멀" in style:
            return flower_reason.get("미니멀", flower_reason["기본"])
        elif "우아" in style:
            return flower_reason.get("우아", flower_reason["기본"])
        else:
            return flower_reason["기본"]
