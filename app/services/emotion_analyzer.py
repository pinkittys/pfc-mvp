"""
LLM 기반 감정 분석 서비스
"""
import os
import json
from typing import List
from dotenv import load_dotenv
from app.models.schemas import EmotionAnalysis

class EmotionAnalyzer:
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
        else:
            print(f"✅ OpenAI API 키 로드됨: {self.openai_api_key[:10]}...")
    
    def analyze(self, story: str) -> List[EmotionAnalysis]:
        """LLM 기반 감정 분석"""
        if not self.openai_api_key:
            return self._fallback_analysis(story)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._create_emotion_prompt(story)
            
            response = client.chat.completions.create(
                model="gpt-4",  # GPT-4로 업그레이드 (더 정교한 감정 분석)
                messages=[
                    {"role": "system", "content": "당신은 고객의 이야기에서 감정을 정확히 분석하는 전문가입니다. 반드시 3가지 감정을 블렌딩하여 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            result = response.choices[0].message.content
            print(f"🤖 LLM 감정 분석 응답: {result}")
            
            # 특별 키워드 체크 제거 - LLM에 맡김
            
            try:
                print(f"🔍 감정 분석 파싱 시도...")
                emotions = self._parse_emotion_response(result)
                print(f"🔍 파싱 성공: {emotions}")
                return emotions
                
            except Exception as e:
                print(f"❌ 감정 분석 파싱 실패: {e}")
                print(f"🔧 폴백 시스템으로 전환")
                return self._fallback_analysis(story)
            
        except Exception as e:
            print(f"❌ LLM 감정 분석 실패: {e}")
            print(f"🔧 폴백 시스템으로 전환")
            return self._fallback_analysis(story)
    
    # 특별 키워드 체크 함수 제거 - LLM에 맡김

    def _create_emotion_prompt(self, story: str) -> str:
        """감정 분석 프롬프트 생성"""
        return f"""
다음 고객의 이야기에서 감정을 분석해주세요:

고객 이야기: "{story}"

다음 JSON 형식으로 정확히 응답해주세요 (반드시 3가지 감정을 포함):

{{
    "emotions": [
        {{
            "emotion": "감정1",
            "percentage": 50.0
        }},
        {{
            "emotion": "감정2", 
            "percentage": 30.0
        }},
        {{
            "emotion": "감정3",
            "percentage": 20.0
        }}
    ]
}}

**중요한 규칙:**
1. **반드시 3가지 감정을 블렌딩하여 분석하세요**
2. **100%를 3개 감정으로 나누세요**
3. **"희망 100%" 같은 단일 감정은 절대 사용하지 마세요**
4. **생일/축하 관련 사연은 "기쁨", "축하", "희망"으로 분류하세요**
5. **"밝고 경쾌한" 요청은 "기쁨", "축하", "희망"으로 분류하세요**

감정 분류 기준:
- 사랑/로맨스: 연인, 고백, 첫사랑, 영원한 사랑 등
- 기쁨: 순수한 기쁨, 행복, 즐거움, 밝은 마음 등
- 축하: 생일, 승진, 합격, 성취, 새로운 시작, 환영 등
- 감사/존경: 부모님, 선생님, 은인에 대한 감사 등
- 그리움/추억: 과거, 회상, 아련함, 떠난 사람, 이사, 동네를 떠남 등
- 위로/따뜻함: 위로, 안정, 포근함, 편안함 등
- 응원/격려: 새로운 시작, 힘내, 화이팅, 지지, 이사 응원 등
- 환영: 새로운 멤버, 신입, 첫 출근 등

주의사항:
1. 반드시 3가지 감정을 추출하세요
2. 비율의 합이 100%가 되도록 조정하세요
3. 한국어로 자연스럽게 표현하세요
4. 꽃다발 추천에 적합한 감정으로 분류하세요
5. "이사", "동네를 떠남" 등은 "그리움/추억"과 "응원/격려"로 분류하세요
6. "환영"은 새로운 멤버가 왔을 때만 사용하세요
7. **병원, 입원, 병실 관련 사연에서는 "환영" 감정을 사용하지 마세요**
8. **병원 관련 사연은 "희망", "위로", "따뜻함"으로 분류하세요**
9. **번아웃/힘든 상황에서는 "기쁨", "감사", "존경" 감정을 사용하지 마세요**
10. **위로/힐링 관련 사연은 "위로", "따뜻함", "응원"으로 분류하세요**
11. **후배가 힘들어하는 상황에서는 "감사", "존경"이 아닌 "위로", "응원"으로 분류하세요**
12. **"힘든 시기", "위로", "응원", "힘들어", "어려운", "고민", "스트레스", "번아웃", "지친", "피곤한" 키워드가 있으면 "사랑/로맨스" 감정을 절대 사용하지 마세요**
13. **위로/응원 사연에서는 "위로", "따뜻함", "응원" 감정만 사용하세요**
"""
    
    def _parse_emotion_response(self, response: str) -> List[EmotionAnalysis]:
        """LLM 응답 파싱"""
        try:
            # JSON 추출
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            emotions_data = data.get("emotions", [])
            
            if not emotions_data or len(emotions_data) < 3:
                print("⚠️ LLM 응답에 3가지 감정이 없음, 폴백 로직 사용")
                return self._fallback_analysis("")
            
            emotions = []
            for emotion_data in emotions_data:
                emotions.append(EmotionAnalysis(
                    emotion=emotion_data["emotion"],
                    percentage=emotion_data["percentage"],
                    description=""  # 감정 설명 제거
                ))
            
            # 비율 합계 확인
            total_percentage = sum(e.percentage for e in emotions)
            if abs(total_percentage - 100) > 1:  # 1% 오차 허용
                print(f"⚠️ 비율 합계가 100%가 아님 ({total_percentage}%), 폴백 로직 사용")
                return self._fallback_analysis("")
            
            return emotions
            
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            print(f"응답 내용: {response}")
            return self._fallback_analysis("")
    
    def _fallback_analysis(self, story: str) -> List[EmotionAnalysis]:
        """LLM 실패 시 룰 기반 폴백"""
        # 기존 룰 기반 로직을 폴백으로 사용
        emotion_keywords = {
            "그리움": ["그리움", "추억", "과거", "아련함", "회상", "이사", "떠남"],
            "따뜻함": ["따뜻함", "위로", "안정", "편안함", "포근함"],
            "애뜻함": ["애뜻함", "사랑", "정성", "마음", "진심"],
            "기쁨": ["기쁨", "행복", "즐거움", "밝", "싱그럽"],
            "축하": ["축하", "성취", "희망", "생일", "경쾌", "신입", "첫 출근"],
            "감사": ["감사", "고마움", "은인에 대한 감사", "축복", "보답"],
            "응원": ["응원", "힘내", "화이팅", "격려", "지지", "후원", "새로운 시작", "번아웃"],
            "희망": ["희망", "새로운 시작", "미래", "꿈", "병원", "입원", "회복"],
            "위로": ["위로", "슬픔", "애도", "상실", "반려견", "강아지", "고양이", "애완동물", "병실", "삭막", "힘들어", "스트레스"],
            "환영": ["환영", "신입", "첫 출근", "새로운 멤버"]  # 병원 관련 키워드 제거
        }
        
        detected_emotions = []
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in story)
            if score > 0:
                detected_emotions.append((emotion, score))
        
        if not detected_emotions:
            detected_emotions = [("따뜻함", 1), ("기쁨", 1), ("축하", 1)]
        
        # 병원 관련 사연 (가장 우선 처리)
        if "병원" in story or "입원" in story or "병실" in story or "삭막" in story:
            detected_emotions = [("희망", 2), ("위로", 1), ("따뜻함", 1)]  # 희망 50%, 위로 25%, 따뜻함 25%
        
        # 반려견 관련 사연 (위로가 필요한 경우)
        elif "반려견" in story or "강아지" in story or "고양이" in story or "애완동물" in story:
            detected_emotions = [("위로", 2), ("슬픔", 1), ("따뜻함", 1)]  # 위로 50%, 슬픔 25%, 따뜻함 25%
        
        # 이사나 동네를 떠나는 경우
        elif "이사" in story or "동네를 떠나" in story or "떠나는" in story:
            detected_emotions = [("응원", 2), ("그리움", 1), ("희망", 1)]  # 응원 50%, 그리움 25%, 희망 25%
        
        # 신입 환영이나 첫 출근이 있으면 3가지 감정으로 분류
        elif "신입" in story or "첫 출근" in story or "환영" in story:
            detected_emotions = [("축하", 2), ("환영", 1), ("기쁨", 1)]  # 축하 50%, 환영 25%, 기쁨 25%
        
        # 생일/축하 관련 사연 (최우선 처리)
        elif "생일" in story or "베프" in story or "밝고 경쾌" in story:
            detected_emotions = [("기쁨", 2), ("축하", 1), ("희망", 1)]  # 기쁨 50%, 축하 25%, 희망 25%
            print(f"🎂 생일/베프 감정 감지: {detected_emotions}")
        
        # 디자인 중심 사연 (우드톤/내추럴/인테리어) - 최우선 처리
        if "우드톤" in story or "내추럴" in story or "인테리어" in story:
            detected_emotions = [("따뜻함", 2), ("평온", 1), ("자연", 1)]  # 따뜻함 50%, 평온 25%, 자연 25%
            print(f"🌿 우드톤/내추럴 감정 감지: {detected_emotions}")
        
        # 합격/성취/축하 관련 사연
        elif "합격" in story or "성취" in story or "축하" in story or "자격증" in story:
            detected_emotions = [("축하", 2), ("기쁨", 1), ("희망", 1)]  # 축하 50%, 기쁨 25%, 희망 25%
        
        # 번아웃/힘든 상황 관련 사연 (최우선 처리)
        elif "번아웃" in story or "힘들어" in story or "스트레스" in story:
            detected_emotions = [("위로", 2), ("응원", 1), ("따뜻함", 1)]  # 위로 50%, 응원 25%, 따뜻함 25%
        
        # 위로/응원 관련 사연 (최우선 처리)
        elif any(keyword in story for keyword in ["힘든 시기", "위로", "응원", "힘들어", "어려운", "고민", "스트레스", "번아웃", "지친", "피곤한"]):
            detected_emotions = [("위로", 2), ("따뜻함", 1), ("응원", 1)]  # 위로 50%, 따뜻함 25%, 응원 25%
            print(f"🤗 위로/응원 감정 감지: {detected_emotions}")
        
        # 해외 유학 완료 환영 사연 (최우선 처리)
        elif any(keyword in story for keyword in ["해외 유학", "유학 완료", "돌아왔어", "알록달록", "여행지"]):
            detected_emotions = [("기쁨", 2), ("축하", 1), ("환영", 1)]  # 기쁨 50%, 축하 25%, 환영 25%
            print(f"🎉 해외 유학 완료 환영 감정 감지: {detected_emotions}")
        
        # 가벼워지는/힐링 관련 사연
        elif "가벼워지는" in story or "한결" in story or "힐링" in story:
            detected_emotions = [("위로", 2), ("따뜻함", 1), ("응원", 1)]  # 위로 50%, 따뜻함 25%, 응원 25%
        
        # 응원 감정이 있으면 우선순위 부여
        if any(emotion == "응원" for emotion, _ in detected_emotions):
            detected_emotions = sorted(detected_emotions, key=lambda x: x[0] != "응원")
        
        total_score = sum(score for _, score in detected_emotions)
        emotions = []
        
        for emotion, score in detected_emotions:
            percentage = round((score / total_score) * 100, 1)
            emotions.append(EmotionAnalysis(
                emotion=emotion,
                percentage=percentage,
                description=""  # 감정 설명 제거
            ))
        
        total_percentage = sum(e.percentage for e in emotions)
        if total_percentage != 100:
            emotions[0].percentage += (100 - total_percentage)
            emotions[0].percentage = round(emotions[0].percentage, 1)
        
        return emotions[:3]
    
    def _get_emotion_description(self, emotion: str) -> str:
        # 감정 설명 제거 - 추천 이유에서 풍부하게 설명
        return ""
