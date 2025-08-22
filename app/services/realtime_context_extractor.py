"""
실시간 LLM 기반 맥락 추출 서비스
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv가 설치되지 않았습니다. pip install python-dotenv")

@dataclass
class ExtractedContext:
    """추출된 맥락 정보"""
    emotions: List[str]  # 감정
    situations: List[str]  # 상황
    moods: List[str]  # 무드
    colors: List[str]  # 컬러
    confidence: float  # 신뢰도
    user_intent: str = "meaning_based"  # 사용자 의도 (meaning_based 또는 design_based)
    mentioned_flower: Optional[str] = None  # 언급된 꽃 이름

class RealtimeContextExtractor:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
        
        # 꽃 이름 매핑 데이터 로드
        self.flower_names = self._load_flower_names()
    
    def _load_flower_names(self) -> Dict[str, str]:
        """꽃 이름 매핑 데이터 로드"""
        try:
            with open("data/flower_dictionary.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                flowers = data.get("flowers", {})
                
                flower_mapping = {}
                for flower_id, flower_data in flowers.items():
                    korean_name = flower_data.get("korean_name", "")
                    scientific_name = flower_data.get("scientific_name", "")
                    color = flower_data.get("color", "")
                    
                    # 한국어 이름 매핑
                    if korean_name:
                        flower_mapping[korean_name] = flower_id
                        # 부분 매칭을 위한 키워드도 추가
                        for word in korean_name.split():
                            if len(word) > 1:
                                flower_mapping[word] = flower_id
                    
                    # 학명 매핑
                    if scientific_name:
                        flower_mapping[scientific_name] = flower_id
                        # 부분 매칭을 위한 키워드도 추가
                        for word in scientific_name.split():
                            if len(word) > 2:
                                flower_mapping[word] = flower_id
                
                return flower_mapping
        except Exception as e:
            print(f"❌ 꽃 이름 매핑 로드 실패: {e}")
            return {}
    
    def _detect_mentioned_flower(self, story: str) -> Optional[str]:
        """사용자가 언급한 꽃 이름 감지"""
        if not self.flower_names:
            return None
        
        story_lower = story.lower()
        
        # 꽃 이름 매칭 (긴 이름부터 매칭)
        sorted_flowers = sorted(self.flower_names.keys(), key=len, reverse=True)
        
        for flower_name in sorted_flowers:
            if flower_name.lower() in story_lower:
                print(f"🌸 언급된 꽃 감지: {flower_name} -> {self.flower_names[flower_name]}")
                return self.flower_names[flower_name]
        
        return None
    
    def extract_context_realtime(self, story: str, emotions: List[dict] = None, excluded_keywords: List[Dict[str, str]] = None) -> ExtractedContext:
        """실시간으로 고객 이야기에서 맥락 추출 (감정 분석 결과 반영, 제외된 키워드 고려)"""
        # 꽃 이름 감지
        mentioned_flower = self._detect_mentioned_flower(story)
        
        if not self.openai_api_key:
            result = self._fallback_extraction(story, emotions, excluded_keywords)
            result.mentioned_flower = mentioned_flower
            return result
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._create_extraction_prompt(story, emotions)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 더 빠르고 저렴한 모델로 변경
                messages=[
                    {"role": "system", "content": "꽃 추천 키워드 추출 전문가입니다. 간단하고 정확하게 추출해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100,  # 토큰 수 더 줄여서 속도 개선
                timeout=3  # 3초 타임아웃 설정
            )
            
            result = response.choices[0].message.content
            parsed_result = self._parse_llm_response(result)
            
            # 감정 분석 결과가 있으면 emotions를 감정 분석 결과로 대체
            if emotions and len(emotions) > 0:
                # 감정 분석 결과에서 감정명만 추출
                emotion_names = []
                for emotion in emotions:
                    if hasattr(emotion, 'emotion'):
                        emotion_names.append(emotion.emotion)
                    elif isinstance(emotion, dict) and 'emotion' in emotion:
                        emotion_names.append(emotion['emotion'])
                
                if emotion_names:  # 감정명이 실제로 추출된 경우에만 적용
                    parsed_result.emotions = emotion_names[:3]  # 최대 3개 감정 사용
                    print(f"🔧 감정 분석 결과 적용: {emotion_names[:3]}")
                else:
                    # 감정 분석 결과가 없으면 기본 감정 추출
                    parsed_result.emotions = self._extract_basic_emotions(story)
                    print(f"🔧 기본 감정 추출: {parsed_result.emotions}")
            else:
                # 감정 분석 결과가 없으면 기본 감정 추출
                parsed_result.emotions = self._extract_basic_emotions(story)
                print(f"🔧 기본 감정 추출: {parsed_result.emotions}")
            
            # LLM 응답 후처리: 점진적 추출
            text_length = len(story.strip())
            
            # 텍스트 길이에 따라 키워드 수 조절
            if text_length <= 10:
                # 매우 짧은 텍스트: 확실한 것만
                parsed_result.emotions = parsed_result.emotions[:1] if parsed_result.emotions else []
                parsed_result.situations = parsed_result.situations[:1] if parsed_result.situations else []
                parsed_result.moods = parsed_result.moods[:1] if parsed_result.moods else []
                parsed_result.colors = parsed_result.colors[:1] if parsed_result.colors else []
            elif text_length <= 30:
                # 중간 텍스트: 적당한 수
                parsed_result.emotions = parsed_result.emotions[:2] if parsed_result.emotions else []
                parsed_result.situations = parsed_result.situations[:1] if parsed_result.situations else []
                parsed_result.moods = parsed_result.moods[:1] if parsed_result.moods else []
                parsed_result.colors = parsed_result.colors[:1] if parsed_result.colors else []
            else:
                # 긴 텍스트: 더 많은 키워드
                parsed_result.emotions = parsed_result.emotions[:3] if parsed_result.emotions else []
                parsed_result.situations = parsed_result.situations[:2] if parsed_result.situations else []
                parsed_result.moods = parsed_result.moods[:2] if parsed_result.moods else []
                parsed_result.colors = parsed_result.colors[:2] if parsed_result.colors else []
            
            print(f"🔧 후처리된 키워드: emotions={parsed_result.emotions}, situations={parsed_result.situations}, moods={parsed_result.moods}, colors={parsed_result.colors}")
            
            # 언급된 꽃 정보 추가
            parsed_result.mentioned_flower = mentioned_flower
            
            return parsed_result
            
        except Exception as e:
            print(f"❌ LLM 맥락 추출 실패: {e}")
            return self._fallback_extraction(story, emotions)
    
    def _create_extraction_prompt(self, story: str, emotions: List[dict] = None) -> str:
        """LLM 추출 프롬프트 생성"""
        # 감정 분석 결과가 있으면 우선적으로 사용
        emotion_priority = ""
        if emotions and len(emotions) > 0:
            # 감정 분석 결과를 강력하게 우선 사용
            emotion_names = []
            for emotion in emotions:
                if hasattr(emotion, 'emotion'):
                    emotion_names.append(emotion.emotion)
                elif isinstance(emotion, dict) and 'emotion' in emotion:
                    emotion_names.append(emotion['emotion'])
            
            if emotion_names:
                emotion_priority = f"\n\n⚠️ 매우 중요: 감정 분석 결과가 이미 완료되었습니다. emotions 필드에는 반드시 다음 중 하나만 사용하세요: {emotion_names[:3]}"
                emotion_priority += f"\n\n절대 다른 감정을 추출하지 마세요. 감정 분석 결과를 그대로 사용하세요."
        
        return f"""
다음 이야기에서 꽃 추천 키워드를 추출해주세요:

"{story}"

**추출 규칙**:
- emotions: 사용자가 현재 느끼는 감정 1개 (우울, 슬픔, 스트레스, 피곤, 외로움, 불안, 감사, 기쁨, 사랑 등)
- situations: 구체적인 상황/목적 1개 (기분전환, 자기위로, 방꾸미기, 일상, 휴식공간, 스트레스해소, 합격, 생일, 위로 등)
- moods: 원하는 분위기/무드 1개 (활기찬, 편안한, 부드러운, 따뜻한, 밝은, 심플한, 자연스러운, 우아한 등)
- colors: 선호하는 색상 1개 (핑크, 레드, 블루, 화이트, 그린, 옐로우, 오렌지, 퍼플 등)

**중요**: 
- emotions: 현재 감정 (예: "우울해서" → "우울")
- situations: 목적/상황 (예: "활력을 주는" → "기분전환", "스스로에게" → "자기위로")
- moods: 원하는 분위기 (예: "밝은 꽃" → "밝은", "활력" → "활기찬")
- 각 카테고리별로 1개씩만 추출

다음 JSON 형식으로만 응답:
{{
    "emotions": ["감정1"],
    "situations": ["상황1"],
    "moods": ["무드1"],
    "colors": ["색상1"],
    "confidence": 0.85
}}
"""
    
    def _parse_llm_response(self, response: str) -> ExtractedContext:
        """LLM 응답 파싱"""
        try:
            # JSON 추출 (```json ... ``` 형태일 수도 있음)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            return ExtractedContext(
                emotions=data.get("emotions", []),
                situations=data.get("situations", []),
                moods=data.get("moods", []),
                colors=data.get("colors", []),
                confidence=data.get("confidence", 0.5)
            )
            
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            return self._fallback_extraction("")
    
    def _fallback_extraction(self, story: str, emotions: List[dict] = None, excluded_keywords: List[Dict[str, str]] = None) -> ExtractedContext:
        """기본 추출기 (LLM 실패 시)"""
        # 간단한 키워드 매칭으로 fallback
        emotions = []
        situations = []
        moods = []
        colors = []
        
        # 감정 키워드 (현재 느끼는 감정) - 우선순위 높음
        emotion_keywords = {
            "우울": ["우울", "우울해", "우울한", "우울함", "우울해서"],
            "슬픔": ["슬프", "슬픈", "슬퍼", "슬픔"],
            "스트레스": ["스트레스", "스트레스받", "스트레스 받", "스트레스받아"],
            "피곤": ["피곤", "피곤해", "피곤한", "지쳐", "지쳤어"],
            "외로움": ["외로워", "외로운", "외로움"],
            "불안": ["불안", "불안해", "불안한", "걱정", "걱정해"],
            "감사": ["감사", "고마워", "은혜", "도움", "중요한", "소중한"],
            "기쁨": ["기쁘", "행복", "즐거", "신나", "웃음"],
            "희망": ["희망", "새로운", "시작", "미래"],
            "사랑": ["사랑", "좋아", "애정", "정", "마음"],
            "따뜻함": ["따뜻한", "포근한", "안정적인"],
            "격려": ["격려", "응원", "힘내", "화이팅", "도전", "다시", "괜찮아"],
            "진심": ["진심", "진짜", "정말", "어린", "가볍지만 진심"],
            "우정": ["친구", "우정", "동료", "친한", "오래된"]
        }
        
        # 상황/목적 키워드 - 구체적인 상황/목적 우선
        situation_keywords = {
            "방꾸미기": ["방", "집", "공간", "꾸미", "인테리어"],
            "일상": ["일상", "평소", "매일", "일상적인"],
            "휴식공간": ["휴식", "쉬고", "편하게", "편안하게"],
            "기분전환": ["기분 전환", "기분전환", "기분 바꿔", "새로운", "활력을", "활력이", "밝은", "밝게"],
            "스트레스해소": ["스트레스", "스트레스 해소", "스트레스해소", "힘들", "지쳐", "피곤"],
            "자기위로": ["자기위로", "스스로에게", "나에게", "내가", "저에게", "제가"],
            "합격": ["합격", "성공", "창업", "졸업", "승리", "성취"],
            "생일": ["생일", "기념일", "축하", "파티"],
            "위로": ["위로", "달래", "안아", "보듬", "쓰다듬", "어루만"],
            "조카": ["조카", "아이", "딸", "아들", "어린이"],
            "창업": ["창업", "사업", "비즈니스", "회사"],
            "아내": ["아내", "와이프", "부인"],
            "남편": ["남편", "남편님"],
            "부모님": ["엄마", "아빠", "부모님"],
            "친구": ["친구", "동료", "친한", "오래된 친구"],
            "사과": ["사과", "미안", "용서"],
            "환영": ["환영", "신입사원", "파티", "입사"],
            "우정": ["친구", "우정", "동료", "친한", "오래된 친구", "인생에서 중요한"]
        }
        
        # 무드 키워드 (원하는 감정/목표/분위기) - 의미 기반 매핑 (확장)
        mood_keywords = {
            "따뜻한": ["따뜻한", "포근한", "편안한", "안정적인", "고마워", "든든한"],
            "부드러운": ["부드러운", "은은한", "조용한", "차분한", "부드러운 꽃"],
            "로맨틱한": ["로맨틱", "달콤한", "사랑스러운", "아름다운", "사랑"],
            "활기찬": ["활기찬", "경쾌한", "밝은", "즐거운", "활력", "활력을", "활력이"],
            "우아한": ["우아한", "세련된", "고급스러운", "품격 있는"],
            "자연스러운": ["자연스러운", "내추럴한", "깔끔한", "심플한"],
            "화려한": ["화려한", "비비드한", "알록달록한", "형형색색", "눈부신", "빛나는"],
            "심플한": ["심플한", "가벼운", "간단한", "가볍지만", "가벼운 마음"],
            "가벼운": ["가벼운", "가볍지만", "간단한", "심플한"],
            "감사한": ["감사", "고마워", "은혜", "도움", "든든한"],
            "사랑스러운": ["사랑", "좋아", "애정", "정", "마음", "남편", "아내"],
            "편안한": ["편안", "편하게", "쉬고", "휴식", "편안하게", "편안히", "쉬고 싶어"],
            "평온한": ["평온", "차분", "조용한", "고요한", "잔잔한"],
            "기분전환": ["기분 전환", "기분전환", "기분 바꿔", "새로운", "기분 바꾸고 싶어"],
            "밝은": ["밝은", "밝게", "밝아지고 싶어", "밝아지고 싶은"],
            "기쁜": ["기쁜", "기쁘고 싶어", "기쁘고 싶은", "행복하고 싶어"],
            "위로받고 싶은": ["위로", "달래", "안아", "보듬", "쓰다듬", "어루만", "위로받고 싶어"]
        }
        
        # 색상 키워드 (확장)
        color_keywords = {
            "블루": ["블루", "파랑", "푸른", "시원한", "바닷가", "여행"],
            "퍼플": ["퍼플", "보라", "라벤더", "그리움", "추억"],
            "핑크": ["핑크", "분홍", "로즈", "로맨틱", "사랑", "부드러운"],
            "레드": ["레드", "빨강", "빨간", "열정", "사랑"],
            "화이트": ["화이트", "흰색", "화이트", "순수", "깨끗한", "부드러운"],
            "노랑": ["노랑", "옐로우", "골드", "밝은"],
            "오렌지": ["오렌지", "주황", "따뜻한", "활기"],
            "그린": ["그린", "초록", "자연", "내추럴"],
            # "파스텔톤": ["파스텔톤", "파스텔", "부드러운 색", "연한 색", "부드러운"]  # 파스텔톤은 색상이 아닌 톤이므로 제외
        }
        
        # 명시적 색상 요청 우선 처리
        story_lower = story.lower()
        
        # 명시적 색상 요청이 있으면 최우선 처리
        if any(keyword in story_lower for keyword in ["옅은 핑크", "부드러운 색감", "연한 핑크"]):
            colors = ["핑크"]  # 파스텔톤 대신 핑크로 매핑
        # 성공/창업 관련 키워드 (최우선) - 맥락에 따라 색상 결정
        elif any(keyword in story_lower for keyword in ["성공", "창업", "합격", "졸업", "승리", "성취", "축하"]):
            # 화려한 + 합격/성공 → 레드 (화려한 축하)
            if any(keyword in story_lower for keyword in ["화려한", "비비드한", "알록달록한", "형형색색", "눈부신", "빛나는"]):
                colors = ["레드"]  # 화려한 축하
            # 새로운 시작, 응원, 희망 키워드가 함께 있으면 옐로우/화이트
            elif any(keyword in story_lower for keyword in ["새로운 시작", "응원", "희망", "미래", "앞으로", "시작"]):
                colors = ["옐로우"]  # 새로운 시작과 희망
            else:
                colors = ["레드"]  # 성공 축하
        # 새로운 시작/응원 관련 키워드
        elif any(keyword in story_lower for keyword in ["새로운 시작", "응원", "희망", "미래", "앞으로", "시작", "도전", "다시", "괜찮아", "격려", "힘내", "화이팅"]):
            # 명시적 색상 요청이 있으면 우선
            if any(keyword in story_lower for keyword in ["핑크", "부드러운", "옅은"]):
                colors = ["핑크"]  # 파스텔톤 대신 핑크로 매핑
            else:
                colors = ["옐로우"]
        # 사랑 관련 키워드 - 세분화된 매핑
        elif any(keyword in story_lower for keyword in ["사랑", "로맨틱", "연인", "남자친구", "여자친구", "프로포즈", "결혼", "데이트"]):
            # 신비로운/깊은 사랑 → 퍼플
            if any(keyword in story_lower for keyword in ["신비로운", "깊은", "영원한", "운명적인", "숙명적인", "이루지 못한", "비밀", "숨겨진"]):
                colors = ["퍼플"]  # 신비로운 사랑
            # 귀여운/따뜻한 사랑 → 핑크
            elif any(keyword in story_lower for keyword in ["귀여운", "따뜻한", "포근한", "부드러운", "은은한", "아랫사람", "조카", "아이", "딸", "아들"]):
                colors = ["핑크"]  # 귀여운 사랑
            # 열정적인/강렬한 사랑 → 레드
            elif any(keyword in story_lower for keyword in ["열정적인", "강렬한", "불타는", "화끈한", "뜨거운", "비비드한"]):
                colors = ["레드"]  # 열정적인 사랑
            # 기본 로맨틱 사랑 → 핑크
            else:
                colors = ["핑크"]  # 기본 로맨틱 사랑
        # 우아함/고급스러움/신비로움 관련 키워드 → 퍼플
        elif any(keyword in story_lower for keyword in ["우아한", "고급스러운", "세련된", "품격 있는", "신비로운", "아름다운", "유니크한", "특별한", "독특한"]):
            colors = ["퍼플"]
        # 위로/따뜻함 관련 키워드 → 핑크 (명시적 색상 요청이 없을 때만)
        elif any(keyword in story_lower for keyword in ["위로", "지쳐", "힘들", "피곤", "스트레스", "야근", "고생", "고민", "걱정", "따뜻한", "부드러운", "포근한", "부드러운 색감", "옅은 핑크"]) and not any(color in story_lower for color in ["블루", "파랑", "푸른", "블루톤", "핑크", "레드", "화이트", "노랑", "옐로우", "오렌지", "퍼플", "보라", "그린", "초록"]):
            colors = ["핑크"]  # 부드럽고 따뜻한 위로
        # 파스텔톤 관련 키워드 → 핑크로 매핑
        elif any(keyword in story_lower for keyword in ["파스텔톤", "파스텔", "부드러운 색", "연한 색"]):
            colors = ["핑크"]  # 파스텔톤 대신 핑크로 매핑
        # 강렬한/비비드 색상 관련 키워드
        elif any(keyword in story_lower for keyword in ["강렬한", "알록달록", "화려한", "형형색색", "비비드", "선명한", "포인트"]):
            colors = ["노랑"]  # 가장 비비드한 색상
        # 시원한 컬러 관련 키워드
        elif any(keyword in story_lower for keyword in ["시원한", "블루톤", "푸른색", "바닷가", "여행"]):
            colors = ["블루"]
        # 따뜻한 컬러 관련 키워드
        elif any(keyword in story_lower for keyword in ["따뜻한", "핑크톤", "로맨틱"]):
            colors = ["핑크"]
        # 밝은 컬러 관련 키워드
        elif any(keyword in story_lower for keyword in ["밝은", "옐로우톤", "희망"]):
            colors = ["노랑"]
        else:
            # 일반적인 키워드 매칭 (첫 번째 매칭된 것만)
            for category, keywords in color_keywords.items():
                if any(keyword in story for keyword in keywords):
                    colors = [category]  # 1개만 추가
                    break  # 첫 번째 매칭에서 중단
        
        # 사용자 의도 분석 (의미 기반 vs 디자인 기반)
        meaning_based_keywords = ["의미", "꽃말", "상징", "메시지", "마음", "감정", "사랑", "감사", "위로", "격려", "축하", "응원", "희망", "우정", "사과", "용서"]
        design_based_keywords = ["색상", "컬러", "무드", "분위기", "디자인", "화려한", "부드러운", "따뜻한", "우아한", "세련된", "핑크", "레드", "블루", "옐로우", "화이트", "퍼플"]
        
        meaning_based_count = sum(1 for keyword in meaning_based_keywords if keyword in story_lower)
        design_based_count = sum(1 for keyword in design_based_keywords if keyword in story_lower)
        
        user_intent = "meaning_based" if meaning_based_count > design_based_count else "design_based"
        
        print(f"🔍 사용자 의도 분석: {user_intent} (의미: {meaning_based_count}, 디자인: {design_based_count})")
        
        # 감정 분석 결과가 있으면 우선적으로 사용
        if emotions and len(emotions) > 0:
            # 감정 분석 결과에서 감정명만 추출
            emotion_names = []
            for emotion in emotions:
                if hasattr(emotion, 'emotion'):
                    emotion_names.append(emotion.emotion)
                elif isinstance(emotion, dict) and 'emotion' in emotion:
                    emotion_names.append(emotion['emotion'])
            
            if emotion_names:  # 감정명이 실제로 추출된 경우에만 적용
                emotions = emotion_names[:3]  # 최대 3개 감정 사용
                print(f"🔧 Fallback에서 감정 분석 결과 적용: {emotion_names[:3]}")
            else:
                # 감정명이 추출되지 않은 경우 기본 감정 추출
                emotions = self._extract_basic_emotions(story)
                print(f"🔧 Fallback에서 기본 감정 추출: {emotions}")
        else:
            # 기본 감정 추출
            emotions = self._extract_basic_emotions(story)
            print(f"🔧 Fallback에서 기본 감정 추출: {emotions}")
        
        # 감정이 적으면 관련 감정 추가 (강화)
        if len(emotions) < 3:
            story_lower = story.lower()
            if "고마워" in story_lower or "감사" in story_lower:
                if "감사" not in emotions:
                    emotions.append("감사")
                if "사랑" not in emotions:
                    emotions.append("사랑")
                if "기쁨" not in emotions:
                    emotions.append("기쁨")
            elif "남편" in story_lower or "아내" in story_lower:
                if "사랑" not in emotions:
                    emotions.append("사랑")
                if "감사" not in emotions:
                    emotions.append("감사")
                if "기쁨" not in emotions:
                    emotions.append("기쁨")
            elif "부드러운" in story_lower:
                if "사랑" not in emotions:
                    emotions.append("사랑")
                if "감사" not in emotions:
                    emotions.append("감사")
                if "따뜻함" not in emotions:
                    emotions.append("따뜻함")
        
        # 제외된 키워드 필터링
        excluded_texts = [kw.get('text', '') for kw in excluded_keywords] if excluded_keywords else []
        emotions = [e for e in emotions if e not in excluded_texts]
        print(f"🚫 제외된 키워드로 인한 감정 필터링: {excluded_texts}")
        
        # 감정이 여전히 적으면 기본 감정 추가 (제외된 키워드 제외)
        if len(emotions) < 2:
            # 현재 감정 위주로 기본값 설정
            default_emotions = ["사랑", "감사", "기쁨", "희망", "따뜻함"]
            for emotion in default_emotions:
                if emotion not in emotions and emotion not in excluded_texts and len(emotions) < 3:
                    emotions.append(emotion)
        
        # 상황 키워드 매칭 (가장 정확한 매칭 우선)
        situations = []
        for category, keywords in situation_keywords.items():
            if any(keyword in story for keyword in keywords):
                situations.append(category)  # 여러 개 추가 가능
        
        # 야근/스트레스 관련 특별 처리
        if any(keyword in story_lower for keyword in ["야근", "스트레스", "지쳐", "피곤", "과로"]):
            if "아내" in story_lower or "와이프" in story_lower or "부인" in story_lower:
                situations = ["아내"]  # 아내가 야근/스트레스로 지쳐있음
            elif "남편" in story_lower:
                situations = ["남편"]  # 남편이 야근/스트레스로 지쳐있음
            elif "친구" in story_lower or "동료" in story_lower:
                situations = ["친구"]  # 친구가 야근/스트레스로 지쳐있음
            else:
                situations = ["걱정"]  # 일반적인 걱정 상황
        
        # 맥락 기반 감정/상황 구분
        story_lower = story.lower()
        
        # 받는 사람의 상황 키워드 (상대방이 겪고 있는 것)
        receiver_situation_keywords = ["스트레스", "피곤", "지쳐", "힘들", "야근", "과로", "고생"]
        
        # 사용자의 감정 키워드 (본인이 느끼는 것)
        user_emotion_keywords = ["위로", "걱정", "사랑", "감사", "기쁨", "희망", "따뜻함", "외로움", "불안", "슬픔", "축하"]
        
        # 맥락 분석: 누구의 스트레스/피곤인지 구분
        for keyword in receiver_situation_keywords:
            if keyword in story_lower:
                # "~가 스트레스로" → 받는 사람의 상황
                if any(pronoun in story_lower for pronoun in ["가", "이", "도", "는", "을", "를"]):
                    # 이미 situations에 추가되어 있는지 확인
                    if keyword not in [s.lower() for s in situations]:
                        situations.append(keyword)
                # "저도 스트레스가" → 사용자의 감정
                elif any(pronoun in story_lower for pronoun in ["저", "나", "제가", "내가"]):
                    if keyword not in [e.lower() for e in emotions]:
                        emotions.append(keyword)
        
        # 슬래시 제거: 감정과 상황에서 슬래시가 있으면 첫 번째 키워드만 사용
        emotions = [e.split('/')[0] if '/' in e else e for e in emotions]
        situations = [s.split('/')[0] if '/' in s else s for s in situations]
        
        # 무드 키워드 매칭 (더 많은 옵션 제공)
        for category, keywords in mood_keywords.items():
            if any(keyword in story for keyword in keywords):
                moods.append(category)  # 여러 개 추가 가능
        
        # 무드 추출 전략: 무드 명시 여부와 확실성에 따라 분기
        story_lower = story.lower()
        
        # 명시적 무드 키워드 체크
        explicit_mood_keywords = ["부드러운", "따뜻한", "로맨틱한", "우아한", "화려한", "자연스러운", "심플한", "가벼운", "활기찬", "감사한", "사랑스러운"]
        has_explicit_mood = any(mood in story_lower for mood in explicit_mood_keywords)
        
        # 확실한 무드 표현 체크 (매우 구체적)
        certain_mood_expressions = ["부드러운 꽃", "따뜻한 느낌", "로맨틱한 분위기", "우아한 스타일", "화려한 색상"]
        has_certain_mood = any(expression in story_lower for expression in certain_mood_expressions)
        
        if has_explicit_mood and has_certain_mood:
            # 무드가 명시되고 확실한 경우: 1개만 유지
            moods = moods[:1]
            print(f"🎭 확실한 무드 감지: {moods[0]} (1개만 유지)")
        elif has_explicit_mood and not has_certain_mood:
            # 무드가 명시되었지만 모호한 경우: 3개 옵션 제안
            if len(moods) < 3:
                if "부드러운" in story_lower:
                    if "부드러운" not in moods:
                        moods.append("부드러운")
                    if "따뜻한" not in moods:
                        moods.append("따뜻한")
                    if "로맨틱한" not in moods:
                        moods.append("로맨틱한")
                elif "남편" in story_lower or "아내" in story_lower:
                    if "로맨틱한" not in moods:
                        moods.append("로맨틱한")
                    if "따뜻한" not in moods:
                        moods.append("따뜻한")
                    if "사랑스러운" not in moods:
                        moods.append("사랑스러운")
                elif "고마워" in story_lower or "감사" in story_lower:
                    if "감사한" not in moods:
                        moods.append("감사한")
                    if "따뜻한" not in moods:
                        moods.append("따뜻한")
                    if "부드러운" not in moods:
                        moods.append("부드러운")
                elif "따뜻한" in story_lower:
                    if "따뜻한" not in moods:
                        moods.append("따뜻한")
                    if "부드러운" not in moods:
                        moods.append("부드러운")
                    if "로맨틱한" not in moods:
                        moods.append("로맨틱한")
                elif "로맨틱한" in story_lower:
                    if "로맨틱한" not in moods:
                        moods.append("로맨틱한")
                    if "사랑스러운" not in moods:
                        moods.append("사랑스러운")
                    if "따뜻한" not in moods:
                        moods.append("따뜻한")
            print(f"🎭 모호한 무드: {moods} (3개 옵션 제안)")
        else:
            # 무드가 명시되지 않은 경우: 기본 무드 추가
            if len(moods) < 2:
                default_moods = ["따뜻한", "부드러운", "로맨틱한", "우아한", "자연스러운"]
                for mood in default_moods:
                    if mood not in moods and len(moods) < 3:
                        moods.append(mood)
            print(f"🎭 기본 무드: {moods} (기본값 추가)")
        
        # 중복 제거: emotions와 situations에서 같은 키워드 제거
        # situations를 우선하고 emotions에서 중복 제거
        emotions = [e for e in emotions if e not in situations]
        
        # emotions가 비어있으면 기본값 추가
        if not emotions:
            emotions = ["기쁨"]
        
        # 상황 키워드가 적으면 기본값 추가
        if len(situations) < 2:
            story_lower = story.lower()
            if "남편" in story_lower or "아내" in story_lower:
                if "남편" not in situations and "아내" not in situations:
                    situations.append("남편" if "남편" in story_lower else "아내")
                if "로맨틱" not in situations:
                    situations.append("로맨틱")
            elif "친구" in story_lower:
                if "친구" not in situations:
                    situations.append("친구")
                if "우정" not in situations:
                    situations.append("우정")
            else:
                default_situations = ["친구", "가족", "로맨틱"]
                for situation in default_situations:
                    if situation not in situations and len(situations) < 3:
                        situations.append(situation)
        
        # 색상 우선순위 처리 (여러 색상이 추출된 경우)
        if len(colors) > 1:
            # 핑크가 있으면 우선 (로맨틱/부드러운 느낌)
            if "핑크" in colors:
                colors = ["핑크"]
            # 옐로우가 있으면 우선 (희망/기쁨)
            elif "옐로우" in colors:
                colors = ["옐로우"]
            # 레드가 있으면 우선 (열정/축하)
            elif "레드" in colors:
                colors = ["레드"]
            # 그 외에는 첫 번째 색상 사용
            else:
                colors = colors[:1]
        
        # 색상 추출 전략: 컬러톤 명시 여부에 따라 분기
        story_lower = story.lower()
        
        # 관용어/비유 표현 제외 체크
        idiom_expressions = ["무지개다리를 건넜다", "무지개다리를 건넜어", "무지개다리를 건넜습니다", "무지개다리를 건넜어요"]
        has_idiom = any(idiom in story for idiom in idiom_expressions)
        
        # 명시적 컬러 키워드 체크 (관용어 제외)
        explicit_color_keywords = ["핑크", "레드", "블루", "화이트", "노랑", "옐로우", "퍼플", "보라", "오렌지", "그린", "초록"]
        has_explicit_color = any(color in story_lower for color in explicit_color_keywords)
        
        # 관용어가 있으면 색상 추출 제외하고 위로/슬픔 감정으로 분류
        if has_idiom:
            print(f"⚠️ 관용어 감지: 색상 추출 제외, 위로/슬픔 감정으로 분류")
            colors = ["화이트"]  # 위로를 위한 화이트
            if "위로" not in emotions:
                emotions.insert(0, "위로")
            if "슬픔" not in emotions:
                emotions.append("슬픔")
            return ExtractedContext(
                emotions=emotions[:1],
                situations=situations[:1],
                moods=moods[:1],
                colors=colors[:1],
                confidence=0.9
            )
        
        # 분위기 키워드 체크
        mood_color_keywords = ["부드러운", "따뜻한", "로맨틱한", "우아한", "화려한", "자연스러운", "심플한", "가벼운"]
        has_mood_only = any(mood in story_lower for mood in mood_color_keywords) and not has_explicit_color
        
        if has_explicit_color:
            # 컬러톤이 명시된 경우: 1개만 유지 (고객이 원하는 색상이 명확함)
            colors = colors[:1]
            print(f"🎨 명시적 컬러 감지: {colors[0]} (1개만 유지)")
        elif has_mood_only:
            # 분위기만 지정된 경우: 3개 옵션 제안
            if len(colors) < 3:
                if "부드러운" in story_lower or "부드러운 꽃" in story_lower:
                    if "핑크" not in colors:
                        colors.append("핑크")
                    if "화이트" not in colors:
                        colors.append("화이트")
                elif "남편" in story_lower or "아내" in story_lower:
                    if "핑크" not in colors:
                        colors.append("핑크")
                    if "레드" not in colors:
                        colors.append("레드")
                elif "고마워" in story_lower or "감사" in story_lower:
                    if "핑크" not in colors:
                        colors.append("핑크")
                    if "화이트" not in colors:
                        colors.append("화이트")
                elif "따뜻한" in story_lower:
                    if "핑크" not in colors:
                        colors.append("핑크")
                    if "오렌지" not in colors:
                        colors.append("오렌지")
                elif "로맨틱한" in story_lower:
                    if "핑크" not in colors:
                        colors.append("핑크")
                    if "레드" not in colors:
                        colors.append("레드")
                    if "퍼플" not in colors:
                        colors.append("퍼플")
                elif "화려한" in story_lower:
                    if "오렌지" not in colors:
                        colors.append("오렌지")
                    if "레드" not in colors:
                        colors.append("레드")
                    if "옐로우" not in colors:
                        colors.append("옐로우")
                elif "우아한" in story_lower:
                    if "화이트" not in colors:
                        colors.append("화이트")
                    if "퍼플" not in colors:
                        colors.append("퍼플")
            print(f"🎭 분위기만 지정: {colors} (3개 옵션 제안)")
        else:
            # 기본 색상이 추출된 경우: 기본 색상 추가 (긴 텍스트에서만)
            if len(colors) < 2 and len(story.strip()) > 30:
                default_colors = ["핑크", "화이트", "레드", "블루"]
                for color in default_colors:
                    if color not in colors and len(colors) < 3:
                        colors.append(color)
                print(f"🎨 기본 색상: {colors} (기본값 추가)")
            elif len(colors) == 0:
                print(f"🎨 색상 미추출: 명시적 색상 요청이 없음")
        
        # 최대 개수 제한 (각 카테고리별 1~3개, 전체 12개 이하로 제한)
        emotions = emotions[:3]  # 최대 3개로 확장
        situations = situations[:3]  # 최대 3개로 확장
        moods = moods[:3]  # 최대 3개로 확장
        colors = colors[:3]  # 최대 3개로 확장
        
        # 전체 키워드 개수 확인 및 조정 (최대 12개)
        total_keywords = len(emotions) + len(situations) + len(moods) + len(colors)
        if total_keywords > 12:
            # 우선순위: colors > moods > situations > emotions
            if total_keywords > 12 and len(emotions) > 3:
                emotions = emotions[:3]
            if total_keywords > 12 and len(situations) > 3:
                situations = situations[:3]
            if total_keywords > 12 and len(moods) > 3:
                moods = moods[:3]
            if total_keywords > 12 and len(colors) > 3:
                colors = colors[:3]
        
        # 점진적 키워드 추출: 텍스트 길이에 따라 키워드 수 조절
        text_length = len(story.strip())
        
        # 텍스트가 짧으면 감정만 추출 (색상은 명시적 요청이 있을 때만)
        if text_length <= 10:
            emotions = emotions[:1] if emotions else []
            situations = []  # 상황은 추출하지 않음
            moods = []  # 무드는 추출하지 않음
            # 색상은 명시적 색상 키워드가 있을 때만
            explicit_colors = ["블루", "파랑", "푸른", "블루톤", "핑크", "레드", "화이트", "노랑", "옐로우", "오렌지", "퍼플", "보라", "그린", "초록"]
            if any(color in story.lower() for color in explicit_colors):
                colors = colors[:1] if colors else []
            else:
                colors = []  # 명시적 색상 요청이 없으면 색상 추출하지 않음
            print(f"📝 짧은 텍스트 ({text_length}자): 감정만 추출, 색상은 명시적 요청시만")
        
        # 텍스트가 중간이면 감정+상황 추출
        elif text_length <= 30:
            emotions = emotions[:2] if emotions else []
            situations = situations[:1] if situations else []
            moods = []  # 무드는 추출하지 않음
            # 색상은 명시적 색상 키워드가 있을 때만
            explicit_colors = ["블루", "파랑", "푸른", "블루톤", "핑크", "레드", "화이트", "노랑", "옐로우", "오렌지", "퍼플", "보라", "그린", "초록"]
            if any(color in story.lower() for color in explicit_colors):
                colors = colors[:1] if colors else []
            else:
                colors = []  # 명시적 색상 요청이 없으면 색상 추출하지 않음
            print(f"📝 중간 텍스트 ({text_length}자): 감정+상황 추출, 색상은 명시적 요청시만")
        
        # 텍스트가 길면 모든 키워드 추출
        else:
            emotions = emotions[:3] if emotions else []
            situations = situations[:2] if situations else []
            moods = moods[:2] if moods else []
            colors = colors[:2] if colors else []
            print(f"📝 긴 텍스트 ({text_length}자): 모든 키워드 추출")
        
        print(f"🔧 최종 키워드: emotions={emotions}, situations={situations}, moods={moods}, colors={colors}")
        
        return ExtractedContext(
            emotions=emotions[:3],  # 최대 3개로 확장
            situations=situations[:3],  # 최대 3개로 확장
            moods=moods[:3],  # 최대 3개로 확장
            colors=colors[:3],  # 최대 3개로 확장
            confidence=0.3,  # 낮은 신뢰도
            user_intent=user_intent  # 사용자 의도 추가
        )
    
    def _extract_basic_emotions(self, story: str) -> List[str]:
        """기본 감정 추출 (단계별 추출)"""
        emotions = []
        story_lower = story.lower()
        
        # 1단계: 명확한 감정 키워드 우선 매칭
        clear_emotion_keywords = {
            "우울": ["우울", "우울해", "우울한", "우울함", "우울해서"],
            "슬픔": ["슬프", "슬픈", "슬퍼", "슬픔"],
            "스트레스": ["스트레스", "스트레스받", "스트레스 받", "스트레스받아"],
            "피곤": ["피곤", "피곤해", "피곤한", "지쳐", "지쳤어"],
            "외로움": ["외로워", "외로운", "외로움"],
            "불안": ["불안", "불안해", "불안한", "걱정", "걱정해"],
            "감사": ["감사", "고마워", "은혜", "도움"],
            "기쁨": ["기쁘", "행복", "즐거", "신나", "웃음"],
            "사랑": ["사랑", "좋아", "애정", "정", "마음"],
            "희망": ["희망", "새로운", "시작", "미래"]
        }
        
        # 명확한 감정 키워드 매칭 (우선순위 높음)
        for emotion, keywords in clear_emotion_keywords.items():
            if any(keyword in story_lower for keyword in keywords):
                emotions.append(emotion)
                print(f"💭 명확한 감정 감지: {emotion}")
                break  # 첫 번째 매칭에서 중단 (단계별 추출)
        
        # 명확한 감정이 없으면 기본값 추가
        if not emotions:
            # 텍스트 길이에 따라 다른 기본값
            if len(story.strip()) <= 5:  # 매우 짧은 텍스트
                emotions = ["사랑"]  # 최소한의 기본값
            else:
                emotions = ["사랑", "감사"]
        
        print(f"🎯 최종 감정 추출: {emotions}")
        return emotions
    
    def get_extraction_summary(self, context: ExtractedContext) -> Dict[str, Any]:
        """추출 결과 요약"""
        return {
            "emotions": context.emotions,
            "situations": context.situations,
            "moods": context.moods,
            "colors": context.colors,
            "confidence": context.confidence,
            "total_extracted": len(context.emotions) + len(context.situations) + len(context.moods) + len(context.colors)
        }
