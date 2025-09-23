"""
실시간 LLM 기반 맥락 추출 서비스
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv가 설치되지 않았습니다. pip install python-dotenv")

@dataclass
class ExtractedContext:
    """추출된 맥락 정보"""
    emotions: List[str]  # 감정 (메인 키워드 1개)
    situations: List[str]  # 상황 (메인 키워드 1개)
    moods: List[str]  # 무드 (메인 키워드 1개)
    colors: List[str]  # 컬러 (메인 키워드 1개)
    confidence: float  # 신뢰도
    user_intent: str = "meaning_based"  # 사용자 의도 (meaning_based 또는 design_based)
    mentioned_flower: Optional[str] = None  # 언급된 꽃 이름
    
    # 대안 키워드 제안
    emotions_alternatives: List[str] = field(default_factory=list)  # 감정 대안 키워드 2-3개
    situations_alternatives: List[str] = field(default_factory=list)  # 상황 대안 키워드 2-3개
    moods_alternatives: List[str] = field(default_factory=list)  # 무드 대안 키워드 2-3개
    colors_alternatives: List[str] = field(default_factory=list)  # 색상 대안 키워드 2-3개
    
    def dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "emotions": self.emotions,
            "situations": self.situations,
            "moods": self.moods,
            "colors": self.colors,
            "confidence": self.confidence,
            "user_intent": self.user_intent,
            "mentioned_flower": self.mentioned_flower,
            "emotions_alternatives": self.emotions_alternatives,
            "situations_alternatives": self.situations_alternatives,
            "moods_alternatives": self.moods_alternatives,
            "colors_alternatives": self.colors_alternatives
        }

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
            # 하드코딩된 꽃 이름 매핑 사용
            return {
                '거베라': 'gerbera',
                '해바라기': 'sunflower', 
                '장미': 'rose',
                '백합': 'lily',
                '튤립': 'tulip',
                '수국': 'hydrangea',
                '프리지아': 'freesia',
                '마리골드': 'marigold',
                '태게테스': 'tagetes',
                '알스트로메리아': 'alstroemeria',
                '리시안셔스': 'lisianthus'
            }
    
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
            print("🔧 OPENAI_API_KEY가 없어서 fallback_extraction 사용")
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
            parsed_result = self._parse_llm_response(result, mentioned_flower)
            
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
            
            # 색상이 비어있으면 fallback 로직으로 색상 추출
            if not parsed_result.colors:
                print("🔧 색상이 비어있어 fallback 로직으로 색상 추출")
                fallback_result = self._fallback_extraction(story, emotions, excluded_keywords)
                parsed_result.colors = fallback_result.colors
            else:
                print(f"🎨 LLM에서 색상 추출됨: {parsed_result.colors}")
            
            # 중복 키워드 제거 및 후처리
            parsed_result = self._remove_duplicates_and_postprocess(parsed_result, story)
            
            print(f"🔧 후처리된 키워드: emotions={parsed_result.emotions}, situations={parsed_result.situations}, moods={parsed_result.moods}, colors={parsed_result.colors}")
            
            # 언급된 꽃 정보 추가
            parsed_result.mentioned_flower = mentioned_flower
            
            return parsed_result
            
        except Exception as e:
            print(f"❌ LLM 맥락 추출 실패: {e}")
            return self._fallback_extraction(story, emotions)
    
    def _remove_duplicates_and_postprocess(self, context: ExtractedContext, story: str) -> ExtractedContext:
        """중복 키워드 제거 및 후처리"""
        # 모든 키워드를 하나의 리스트로 수집
        all_keywords = []
        all_keywords.extend(context.emotions)
        all_keywords.extend(context.situations)
        all_keywords.extend(context.moods)
        all_keywords.extend(context.colors)
        
        # 중복 제거 (첫 번째 발견된 것만 유지)
        seen_keywords = set()
        unique_keywords = []
        for keyword in all_keywords:
            if keyword not in seen_keywords:
                seen_keywords.add(keyword)
                unique_keywords.append(keyword)
        
        # 텍스트 길이에 따라 키워드 수 조절
        text_length = len(story.strip())
        
        # 꽃 매칭을 위해 최소 4개 차원 모두 필요
        # 텍스트 길이에 관계없이 최소 4개 키워드 보장
        if text_length <= 15:
            # 매우 짧은 텍스트: 4개 차원 모두 추출 (중복 허용)
            max_keywords = 4
        elif text_length <= 40:
            # 중간 텍스트: 4개 차원 모두 추출
            max_keywords = 4
        else:
            # 긴 텍스트: 더 많은 키워드 (4개 이상)
            max_keywords = 6
        
        # 키워드 수 제한
        unique_keywords = unique_keywords[:max_keywords]
        
        # 카테고리별로 재분배 (우선순위: emotions > situations > moods > colors)
        result = ExtractedContext(
            emotions=[],
            situations=[],
            moods=[],
            colors=[],
            confidence=context.confidence,
            emotions_alternatives=context.emotions_alternatives,
            situations_alternatives=context.situations_alternatives,
            moods_alternatives=context.moods_alternatives,
            colors_alternatives=context.colors_alternatives
        )
        
        # 색상은 항상 색상 카테고리에 보존
        original_colors = context.colors.copy()
        other_keywords = [kw for kw in unique_keywords if kw not in original_colors]
        
        # 색상 먼저 할당
        for color in original_colors:
            if color not in result.colors:
                result.colors.append(color)
        
        # 나머지 키워드를 우선순위에 따라 분배 (4개 차원 모두 보장)
        for i, keyword in enumerate(other_keywords):
            if i == 0 and len(result.emotions) == 0:
                result.emotions.append(keyword)
            elif i == 1 and len(result.situations) == 0:
                result.situations.append(keyword)
            elif i == 2 and len(result.moods) == 0:
                result.moods.append(keyword)
            elif i == 3 and len(result.emotions) == 0:
                result.emotions.append(keyword)  # emotions가 비어있으면 추가
            elif i == 4 and len(result.situations) == 0:
                result.situations.append(keyword)  # situations가 비어있으면 추가
            elif i == 5 and len(result.moods) == 0:
                result.moods.append(keyword)  # moods가 비어있으면 추가
        
        print(f"🔧 중복 제거 후 키워드: {unique_keywords}")
        
        # 4개 차원 모두 보장 (비어있으면 기본값 제공)
        if not result.emotions:
            result.emotions = self._get_default_emotions(story)
            print(f"🔧 기본 감정 제공: {result.emotions}")
        
        if not result.situations:
            result.situations = self._get_default_situations(story)
            print(f"🔧 기본 상황 제공: {result.situations}")
        
        if not result.moods:
            result.moods = self._get_default_moods(story)
            print(f"🔧 기본 무드 제공: {result.moods}")
        
        if not result.colors:
            recommended_color = self._recommend_color_based_on_context(
                result.emotions, result.situations, result.moods, story
            )
            if recommended_color:
                result.colors.append(recommended_color)
                print(f"🎨 컨텍스트 기반 색상 추천: {recommended_color}")
        
        return result
    
    def _recommend_color_based_on_context(self, emotions: List[str], situations: List[str], moods: List[str], story: str) -> str:
        """컨텍스트 기반 색상 추천"""
        # 감정 기반 색상 매핑
        emotion_color_map = {
            # 부정적 감정 → 차분하고 위로되는 색상
            "우울": "블루",
            "슬픔": "블루", 
            "스트레스": "그린",
            "피곤": "그린",
            "외로움": "블루",
            "불안": "그린",
            "답답함": "블루",
            "지침": "그린",
            "허전함": "블루",
            "그리움": "라일락",
            "미안함": "화이트",
            "후회": "블루",
            "분노": "그린",
            "지루함": "옐로우",
            
            # 긍정적 감정 → 밝고 따뜻한 색상
            "기쁨": "옐로우",
            "설렘": "핑크",
            "감사": "핑크",
            "만족": "그린",
            "희망": "옐로우",
            "자신감": "레드",
            "용기": "레드",
            "열정": "오렌지",
            "애정": "핑크",
            "따뜻함": "핑크",
            "안정감": "그린",
            "활력": "옐로우",
            "격려": "핑크",
            "진심": "화이트",
            "우정": "핑크"
        }
        
        # 상황 기반 색상 매핑
        situation_color_map = {
            # 개인적 상황
            "방꾸미기": "화이트",
            "일상": "그린",
            "휴식공간": "블루",
            "기분전환": "옐로우",
            "스트레스해소": "그린",
            "자기위로": "블루",
            "힐링": "그린",
            "명상": "블루",
            "독서": "화이트",
            "운동": "그린",
            "취미활동": "옐로우",
            "자기계발": "블루",
            "새로운시작": "옐로우",
            
            # 대인관계 상황
            "위로": "블루",
            "격려": "핑크",
            "축하": "레드",
            "감사": "핑크",
            "사과": "화이트",
            "고백": "핑크",
            "프로포즈": "레드",
            "생일": "핑크",
            "기념일": "레드",
            "졸업": "블루",
            "합격": "옐로우",
            "취업": "블루",
            "이사": "그린",
            "여행": "옐로우",
            "선물": "핑크",
            "우정": "핑크",
            "사랑": "핑크",
            "가족": "핑크",
            "동료": "블루",
            "선생님": "핑크",
            "의사": "화이트",
            "간호사": "핑크"
        }
        
        # 무드 기반 색상 매핑
        mood_color_map = {
            "활기찬": "옐로우",
            "편안한": "그린",
            "부드러운": "핑크",
            "따뜻한": "핑크",
            "밝은": "옐로우",
            "심플한": "화이트",
            "자연스러운": "그린",
            "우아한": "라일락",
            "신비로운": "퍼플",
            "로맨틱한": "핑크",
            "차분한": "블루",
            "고급스러운": "퍼플",
            "귀여운": "핑크",
            "성숙한": "퍼플",
            "청춘다운": "핑크",
            "힘있는": "레드",
            "신뢰감있는": "블루",
            "희망찬": "옐로우",
            "평화로운": "그린",
            "열정적인": "오렌지"
        }
        
        # 우선순위: 감정 > 상황 > 무드
        for emotion in emotions:
            if emotion in emotion_color_map:
                return emotion_color_map[emotion]
        
        for situation in situations:
            if situation in situation_color_map:
                return situation_color_map[situation]
        
        for mood in moods:
            if mood in mood_color_map:
                return mood_color_map[mood]
        
        # 기본값: 상황에 따라
        if any(word in story for word in ["위로", "슬픔", "우울", "힘들"]):
            return "블루"
        elif any(word in story for word in ["사랑", "로맨틱", "고백", "프로포즈"]):
            return "핑크"
        elif any(word in story for word in ["축하", "생일", "기념일"]):
            return "레드"
        elif any(word in story for word in ["힐링", "휴식", "편안"]):
            return "그린"
        else:
            return "핑크"  # 가장 범용적인 색상
    
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
        
        # 텍스트 길이에 따른 프롬프트 조정
        text_length = len(story.strip())
        
        if text_length <= 15:
            # 짧은 텍스트: 더 자세한 분석 요청
            context_instruction = f"""
**짧은 텍스트 분석 가이드**:
텍스트가 짧아서 맥락 파악이 어려울 수 있습니다. 다음을 고려해주세요:

1. **감정 추론**: "위로하고 싶어" → 슬픔/우울/스트레스 중 하나
2. **상황 추론**: "친구가 반려견을 잃었어" → 위로/격려 상황
3. **무드 추론**: 위로 상황이면 → 따뜻한/부드러운 무드
4. **색상 추론**: 위로/따뜻함이면 → 블루/화이트 우선, 핑크는 축하/기쁨 상황에서만

**추출 규칙**:
- emotions: 현재 느끼는 감정 1개 (우울, 슬픔, 스트레스, 피곤, 외로움, 불안, 감사, 기쁨, 사랑 등)
- situations: 구체적인 상황/목적 1개 (기분전환, 자기위로, 방꾸미기, 일상, 휴식공간, 스트레스해소, 합격, 생일, 위로 등)
- moods: 원하는 분위기/무드 1개 (활기찬, 편안한, 부드러운, 따뜻한, 밝은, 심플한, 자연스러운, 우아한 등)
- colors: 선호하는 색상 1개 (핑크, 레드, 블루, 화이트, 그린, 옐로우, 오렌지, 퍼플 등)
"""
        else:
            # 긴 텍스트: 더 다양하고 구체적인 키워드 추출
            context_instruction = f"""
**다양한 키워드 추출 가이드**:
사용자의 고유한 상황과 감정을 정확히 파악하여 다양한 키워드를 추출해주세요.

**감정 (emotions) - 더 구체적으로**:
- 부정적: 우울, 슬픔, 스트레스, 피곤, 외로움, 불안, 걱정, 답답함, 지침, 허전함, 그리움, 미안함, 후회, 분노, 짜증, 지루함
- 긍정적: 기쁨, 행복, 설렘, 설렘, 감사, 만족, 희망, 자신감, 용기, 열정, 애정, 사랑, 따뜻함, 편안함, 안정감, 활력

**상황 (situations) - 더 구체적으로**:
- 개인적: 자기위로, 기분전환, 스트레스해소, 휴식, 힐링, 명상, 독서, 운동, 취미활동, 자기계발, 새로운시작, 변화
- 대인관계: 위로, 격려, 축하, 감사, 사과, 화해, 재회, 이별, 고백, 프로포즈, 결혼, 생일, 졸업, 합격, 취업, 창업
- 공간: 방꾸미기, 거실, 침실, 사무실, 카페, 정원, 발코니, 베란다, 인테리어, 홈데코, 공간분위기, 조명

**무드 (moods) - 더 다양하게**:
- 따뜻한: 따뜻한, 포근한, 편안한, 안정적인, 부드러운, 은은한, 차분한, 조용한
- 활기찬: 활기찬, 경쾌한, 밝은, 즐거운, 신나는, 에너지넘치는, 생동감있는, 역동적인
- 우아한: 우아한, 세련된, 고급스러운, 품격있는, 클래식한, 모던한, 미니멀한, 심플한
- 자연스러운: 자연스러운, 내추럴한, 깔끔한, 산뜻한, 시원한, 청량한, 상쾌한
- 로맨틱한: 로맨틱한, 달콤한, 사랑스러운, 아름다운, 환상적인, 꿈꾸는, 몽환적인

**색상 (colors) - 상황별 색상 우선순위**:
- **위로/슬픔/스트레스 상황**: 화이트(wh) → 블루(bl) → 라일락(ll) 순으로 우선
- **축하/기쁨/생일 상황**: 옐로우(yl) → 핑크(pk) → 오렌지(or) 순으로 우선
- **사랑/로맨틱 상황**: 핑크(pk) → 레드(rd) → 퍼플(pu) 순으로 우선
- **일반/중립 상황**: 화이트(wh) → 블루(bl) → 핑크(pk) 순으로 우선

**색상 코드**:
- **화이트 (wh)**: "화이트", "흰색", "순수", "깨끗한"
- **오렌지 (or)**: "오렌지", "주황", "따뜻한", "활기"
- **레드 (rd)**: "레드", "빨강", "열정", "사랑"
- **옐로우 (yl)**: "옐로우", "노랑", "골드", "밝은"
- **핑크 (pk)**: "핑크", "분홍", "로즈", "로맨틱"
- **라일락 (ll)**: "라일락", "연보라", "은은한", "부드러운"
- **블루 (bl)**: "블루", "파랑", "시원한", "차분한"
- **퍼플 (pu)**: "퍼플", "보라", "신비로운", "우아한"

**중요**: 위 8개 색상 중에서만 선택하세요. 다른 색상은 사용하지 마세요.
**중요**: 번아웃/위로/슬픔 상황에서는 반드시 화이트를 우선 선택하세요.
"""
        
        return f"""
다음 이야기에서 꽃 추천 키워드를 추출해주세요:

"{story}"

{context_instruction}

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
    
    def _parse_llm_response(self, response: str, mentioned_flower: Optional[str] = None) -> ExtractedContext:
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
            
            # LLM에서 추출된 키워드에 대한 대안 키워드 생성
            emotions = data.get("emotions", [])
            situations = data.get("situations", [])
            moods = data.get("moods", [])
            colors = data.get("colors", [])
            
            # 각 디멘션에서 첫 번째 키워드만 메인 키워드로 사용
            emotions = emotions[:1] if emotions else []
            situations = situations[:1] if situations else []
            moods = moods[:1] if moods else []
            colors = colors[:1] if colors else []
            
            # 대안 키워드 생성
            emotions_alternatives = []
            situations_alternatives = []
            moods_alternatives = []
            colors_alternatives = []
            
            print(f"🎯 LLM 경로에서 대안 키워드 생성:")
            print(f"  emotions: {emotions}")
            print(f"  situations: {situations}")
            print(f"  moods: {moods}")
            print(f"  colors: {colors}")
            
            if emotions and len(emotions) > 0:
                emotions_alternatives = self._generate_emotion_alternatives(emotions[0])
                print(f"  감정 대안: {emotions_alternatives}")
            
            if situations and len(situations) > 0:
                situations_alternatives = self._generate_situation_alternatives(situations[0])
                print(f"  상황 대안: {situations_alternatives}")
            
            if moods and len(moods) > 0:
                moods_alternatives = self._generate_mood_alternatives(moods[0])
                print(f"  무드 대안: {moods_alternatives}")
            
            if colors and len(colors) > 0:
                colors_alternatives = self._generate_color_alternatives(colors[0])
                print(f"  색상 대안: {colors_alternatives}")
            
            result = ExtractedContext(
                emotions=emotions,
                situations=situations,
                moods=moods,
                colors=colors,
                confidence=data.get("confidence", 0.5),
                emotions_alternatives=emotions_alternatives,
                situations_alternatives=situations_alternatives,
                moods_alternatives=moods_alternatives,
                colors_alternatives=colors_alternatives
            )
            result.mentioned_flower = mentioned_flower
            return result
            
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            return self._fallback_extraction("", emotions, None)
    
    def _fallback_extraction(self, story: str, emotions: List[dict] = None, excluded_keywords: List[Dict[str, str]] = None) -> ExtractedContext:
        """기본 추출기 (LLM 실패 시)"""
        # 간단한 키워드 매칭으로 fallback
        emotions = []
        situations = []
        moods = []
        colors = []
        
        # 감정 키워드 (현재 느끼는 감정) - 더 다양하게
        emotion_keywords = {
            # 부정적 감정
            "우울": ["우울", "우울해", "우울한", "우울함", "우울해서", "침울", "우울증"],
            "슬픔": ["슬프", "슬픈", "슬퍼", "슬픔", "애도", "비통", "서럽"],
            "스트레스": ["스트레스", "스트레스받", "스트레스 받", "스트레스받아", "압박", "부담"],
            "피곤": ["피곤", "피곤해", "피곤한", "지쳐", "지쳤어", "허기", "무기력"],
            "외로움": ["외로워", "외로운", "외로움", "고독", "쓸쓸", "허전"],
            "불안": ["불안", "불안해", "불안한", "걱정", "걱정해", "근심", "조마조마"],
            "답답함": ["답답", "답답해", "답답한", "막막", "막막해", "막막한"],
            "지침": ["지침", "지쳐", "지쳤어", "무기력", "의욕없"],
            "허전함": ["허전", "허전해", "허전한", "빈", "텅빈", "쓸쓸"],
            "그리움": ["그리워", "그리운", "그리움", "보고싶", "보고싶어"],
            "미안함": ["미안", "미안해", "미안한", "죄송", "죄송해", "죄송한"],
            "후회": ["후회", "후회해", "후회한", "아깝", "아깝다"],
            "분노": ["화나", "화나서", "분노", "짜증", "짜증나", "열받"],
            "지루함": ["지루", "지루해", "지루한", "심심", "심심해", "재미없"],
            
            # 긍정적 감정
            "기쁨": ["기쁘", "기뻐", "기쁜", "행복", "즐거", "신나", "웃음", "웃겨"],
            "설렘": ["설렘", "설레", "설레는", "두근", "두근거려", "떨려"],
            "감사": ["감사", "고마워", "은혜", "도움", "중요한", "소중한", "고맙"],
            "만족": ["만족", "만족해", "만족한", "충족", "충족해", "충족한"],
            "희망": ["희망", "새로운", "시작", "미래", "꿈", "꿈꿔", "꿈꾸"],
            "자신감": ["자신감", "자신있", "자신있어", "확신", "확신있"],
            "용기": ["용기", "용감", "용감해", "용감한", "대담", "대담해"],
            "열정": ["열정", "열정적", "열심", "열심히", "투지", "투지있"],
            "애정": ["애정", "사랑", "좋아", "정", "마음", "애틋"],
            "따뜻함": ["따뜻한", "포근한", "안정적인", "편안", "편안해"],
            "안정감": ["안정", "안정감", "안정적", "차분", "차분해", "차분한"],
            "활력": ["활력", "활기", "활기찬", "생기", "생기있", "에너지"],
            "격려": ["격려", "응원", "힘내", "화이팅", "도전", "다시", "괜찮아"],
            "진심": ["진심", "진짜", "정말", "어린", "가볍지만 진심", "성실"],
            "우정": ["친구", "우정", "동료", "친한", "오래된", "절친"]
        }
        
        # 상황/목적 키워드 - 더 다양하고 구체적으로
        situation_keywords = {
            # 개인적 상황
            "방꾸미기": ["방", "집", "공간", "꾸미", "인테리어", "가구", "소품", "장식"],
            "일상": ["일상", "평소", "매일", "일상적인", "루틴", "습관"],
            "휴식공간": ["휴식", "쉬고", "편하게", "편안하게", "쉬는", "휴가", "여행"],
            "기분전환": ["기분 전환", "기분전환", "기분 바꿔", "새로운", "활력을", "활력이", "밝은", "밝게", "환기"],
            "스트레스해소": ["스트레스", "스트레스 해소", "스트레스해소", "힘들", "지쳐", "피곤", "압박", "부담"],
            "자기위로": ["자기위로", "스스로에게", "나에게", "내가", "저에게", "제가", "혼자", "혼자서"],
            "힐링": ["힐링", "치유", "마음", "마음치유", "상처", "아픔", "회복"],
            "명상": ["명상", "요가", "마음챙김", "집중", "집중력", "명상공간"],
            "독서": ["독서", "책", "읽기", "도서관", "서점", "지식"],
            "운동": ["운동", "헬스", "요가", "필라테스", "조깅", "걷기", "등산"],
            "취미활동": ["취미", "취미활동", "그림", "그리기", "악기", "음악", "요리", "베이킹"],
            "자기계발": ["자기계발", "학습", "공부", "스킬", "능력", "성장", "발전"],
            "새로운시작": ["새로운", "시작", "변화", "전환", "도전", "모험", "새출발"],
            
            # 대인관계 상황
            "위로": ["위로", "달래", "안아", "보듬", "쓰다듬", "어루만", "위안"],
            "격려": ["격려", "응원", "힘내", "화이팅", "도전", "다시", "괜찮아", "버티"],
            "축하": ["축하", "축하해", "축하하는", "경사", "경사스러운", "축하파티"],
            "감사": ["감사", "고마워", "은혜", "도움", "중요한", "소중한", "고맙"],
            "사과": ["사과", "미안", "용서", "잘못", "실수", "죄송"],
            "화해": ["화해", "화해해", "화해하는", "다시", "재회", "만남"],
            "재회": ["재회", "다시", "만남", "화해", "연락", "연락처"],
            "이별": ["이별", "헤어짐", "작별", "안녕", "잘가", "떠남"],
            "고백": ["고백", "고백해", "고백하는", "사랑", "마음", "진심"],
            "프로포즈": ["프로포즈", "청혼", "결혼", "약혼", "반지", "꿈"],
            "결혼": ["결혼", "웨딩", "부부", "신랑", "신부", "결혼식"],
            "생일": ["생일", "기념일", "축하", "파티", "케이크", "선물"],
            "졸업": ["졸업", "졸업식", "학위", "학사모", "캡", "캡스톤"],
            "합격": ["합격", "성공", "합격증", "합격통지", "합격발표", "합격자"],
            "취업": ["취업", "직장", "회사", "근무", "출근", "직장생활"],
            "창업": ["창업", "사업", "비즈니스", "회사", "사장", "CEO"],
            
            # 공간/환경
            "거실": ["거실", "응접실", "리빙룸", "소파", "TV", "가족"],
            "침실": ["침실", "베드룸", "침대", "수면", "잠", "휴식"],
            "사무실": ["사무실", "오피스", "책상", "업무", "일", "직장"],
            "카페": ["카페", "커피", "음료", "분위기", "아늑", "편안"],
            "정원": ["정원", "가든", "화단", "꽃밭", "식물", "자연"],
            "발코니": ["발코니", "베란다", "테라스", "야외", "바람", "햇살"],
            "베란다": ["베란다", "발코니", "테라스", "야외", "바람", "햇살"],
            "인테리어": ["인테리어", "디자인", "스타일", "분위기", "테마", "컨셉"],
            "홈데코": ["홈데코", "장식", "소품", "액세서리", "포인트", "포인트아이템"],
            "공간분위기": ["분위기", "무드", "감성", "느낌", "환경", "공간"],
            "조명": ["조명", "불", "라이트", "밝기", "어둠", "분위기조명"]
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
            "퍼플": ["퍼플", "라벤더", "그리움", "추억"],  # "보라" 제거하여 연보라가 퍼플로 매칭되지 않도록 함
            "라일락": ["라일락", "연보라", "연한 보라", "은은한 보라", "부드러운 보라", "보라"],  # "보라"를 라일락으로 이동
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
        
        # 연보라/라일락 관련 키워드 → 라일락 (최우선)
        if any(keyword in story_lower for keyword in ["연보라", "라일락", "연한 보라", "은은한 보라", "부드러운 보라"]):
            colors = ["라일락"]
        # 명시적 색상 요청이 있으면 최우선 처리
        elif any(keyword in story_lower for keyword in ["옅은 핑크", "부드러운 색감", "연한 핑크"]):
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

        # 위로/힐링 관련 키워드 → 화이트 (명시적 색상 요청이 없을 때만)
        elif any(keyword in story_lower for keyword in ["위로", "지쳐", "힘들", "피곤", "스트레스", "야근", "고생", "고민", "걱정", "힐링", "치유", "회복", "안정", "평온", "차분", "조용", "편안"]) and not any(color in story_lower for color in ["블루", "파랑", "푸른", "블루톤", "핑크", "레드", "화이트", "노랑", "옐로우", "오렌지", "퍼플", "보라", "그린", "초록"]):
            colors = ["화이트"]  # 차분하고 위로가 되는 색상
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
        
        # 감정이 없으면 기본 감정 1개 추가 (제외된 키워드 제외)
        if len(emotions) < 1:
            # 현재 감정 위주로 기본값 설정
            default_emotions = ["사랑", "감사", "기쁨", "희망", "따뜻함", "편안함", "설렘", "우정"]
            for emotion in default_emotions:
                if emotion not in emotions and emotion not in excluded_texts and len(emotions) < 1:
                    emotions.append(emotion)
                    break  # 1개만 추가
        
        # emotions가 비어있으면 기본값 설정
        if not emotions:
            emotions = ["사랑"]
        
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
            # 무드가 명시되고 확실한 경우: 2개까지 유지
            moods = moods[:2]
            print(f"🎭 확실한 무드 감지: {moods} (2개까지 유지)")
        elif has_explicit_mood and not has_certain_mood:
            # 무드가 명시되었지만 모호한 경우: 4개 옵션 제안
            if len(moods) < 4:
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
            if len(moods) < 4:
                default_moods = ["따뜻한", "부드러운", "로맨틱한", "우아한", "자연스러운", "활기찬", "편안한", "세련된"]
                for mood in default_moods:
                    if mood not in moods and len(moods) < 4:
                        moods.append(mood)
            print(f"🎭 기본 무드: {moods} (기본값 추가)")
        
        # 중복 제거: emotions와 situations에서 같은 키워드 제거
        # situations를 우선하고 emotions에서 중복 제거
        emotions = [e for e in emotions if e not in situations]
        
        # emotions가 비어있으면 기본값 추가
        if not emotions:
            emotions = ["사랑"]
        
        # moods가 비어있으면 기본값 추가
        if not moods:
            moods = ["따뜻한"]
        
        # colors가 비어있으면 기본값 추가
        if not colors:
            colors = ["화이트"]
        
        # 상황 키워드가 없으면 기본값 1개 추가
        if len(situations) < 1:
            story_lower = story.lower()
            if "남편" in story_lower or "아내" in story_lower:
                if "남편" not in situations and "아내" not in situations:
                    situations.append("남편" if "남편" in story_lower else "아내")
            elif "친구" in story_lower:
                if "친구" not in situations:
                    situations.append("친구")
            else:
                default_situations = ["친구", "가족", "로맨틱", "일상", "위로", "축하"]
                for situation in default_situations:
                    if situation not in situations and len(situations) < 1:
                        situations.append(situation)
                        break  # 1개만 추가
        
        # situations가 비어있으면 기본값 설정
        if not situations:
            situations = ["일상"]
        
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
            # 컬러톤이 명시된 경우: 2개까지 유지 (고객이 원하는 색상이 명확함)
            colors = colors[:2]
            print(f"🎨 명시적 컬러 감지: {colors} (2개까지 유지)")
        elif has_mood_only:
            # 분위기만 지정된 경우: 4개 옵션 제안
            if len(colors) < 4:
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
            if len(colors) < 4 and len(story.strip()) > 30:
                default_colors = ["핑크", "화이트", "레드", "블루", "옐로우", "퍼플", "오렌지", "그린"]
                for color in default_colors:
                    if color not in colors and len(colors) < 4:
                        colors.append(color)
                print(f"🎨 기본 색상: {colors} (기본값 추가)")
            elif len(colors) == 0:
                print(f"🎨 색상 미추출: 명시적 색상 요청이 없음")
        
        # 메인 키워드는 각 디멘션별로 1개씩만 추출
        emotions = emotions[:1]  # 메인 키워드 1개
        situations = situations[:1]  # 메인 키워드 1개
        moods = moods[:1]  # 메인 키워드 1개
        colors = colors[:1]  # 메인 키워드 1개
        
        # 메인 키워드는 이미 1개씩으로 제한됨 (전체 4개)
        total_keywords = len(emotions) + len(situations) + len(moods) + len(colors)
        print(f"🔧 메인 키워드 개수: {total_keywords}개")
        
        # 점진적 키워드 추출: 텍스트 길이에 따라 키워드 수 조절
        text_length = len(story.strip())
        
        # 메인 키워드는 항상 1개씩만 추출 (텍스트 길이와 무관)
        emotions = emotions[:1] if emotions else []
        situations = situations[:1] if situations else []
        moods = moods[:1] if moods else []
        colors = colors[:1] if colors else []
        print(f"📝 메인 키워드 추출: 감정={emotions}, 상황={situations}, 무드={moods}, 색상={colors}")
        
        print(f"🔧 최종 키워드: emotions={emotions}, situations={situations}, moods={moods}, colors={colors}")
        
        # 대안 키워드 생성
        emotions_alternatives = []
        situations_alternatives = []
        moods_alternatives = []
        colors_alternatives = []
        
        print(f"🔍 대안 키워드 생성 시작:")
        print(f"  emotions: {emotions}, len: {len(emotions) if emotions else 0}")
        print(f"  situations: {situations}, len: {len(situations) if situations else 0}")
        print(f"  moods: {moods}, len: {len(moods) if moods else 0}")
        print(f"  colors: {colors}, len: {len(colors) if colors else 0}")
        
        if emotions and len(emotions) > 0:
            print(f"  감정 대안 생성: {emotions[0]}")
            emotions_alternatives = self._generate_emotion_alternatives(emotions[0])
            print(f"  감정 대안 결과: {emotions_alternatives}")
        
        if situations and len(situations) > 0:
            print(f"  상황 대안 생성: {situations[0]}")
            situations_alternatives = self._generate_situation_alternatives(situations[0])
            print(f"  상황 대안 결과: {situations_alternatives}")
        
        if moods and len(moods) > 0:
            print(f"  무드 대안 생성: {moods[0]}")
            moods_alternatives = self._generate_mood_alternatives(moods[0])
            print(f"  무드 대안 결과: {moods_alternatives}")
        
        if colors and len(colors) > 0:
            print(f"  색상 대안 생성: {colors[0]}")
            colors_alternatives = self._generate_color_alternatives(colors[0], None)
            print(f"  색상 대안 결과: {colors_alternatives}")
        
        print(f"🎯 대안 키워드 생성:")
        print(f"  감정: {emotions} → 대안: {emotions_alternatives}")
        print(f"  상황: {situations} → 대안: {situations_alternatives}")
        print(f"  무드: {moods} → 대안: {moods_alternatives}")
        print(f"  색상: {colors} → 대안: {colors_alternatives}")
        
        return ExtractedContext(
            emotions=emotions[:1],  # 메인 키워드 1개
            situations=situations[:1],  # 메인 키워드 1개
            moods=moods[:1],  # 메인 키워드 1개
            colors=colors[:1],  # 메인 키워드 1개
            confidence=0.3,  # 낮은 신뢰도
            user_intent=user_intent,  # 사용자 의도 추가
            emotions_alternatives=emotions_alternatives,  # 감정 대안 키워드
            situations_alternatives=situations_alternatives,  # 상황 대안 키워드
            moods_alternatives=moods_alternatives,  # 무드 대안 키워드
            colors_alternatives=colors_alternatives  # 색상 대안 키워드
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
    
    def _get_default_emotions(self, story: str) -> List[str]:
        """기본 감정 제공"""
        story_lower = story.lower()
        
        # 위로/힐링 관련
        if any(word in story_lower for word in ["위로", "힐링", "편안", "차분", "쉬고", "휴식"]):
            return ["따뜻함"]
        # 축하/기쁨 관련
        elif any(word in story_lower for word in ["축하", "생일", "기쁨", "행복", "합격"]):
            return ["기쁨"]
        # 사랑/감사 관련
        elif any(word in story_lower for word in ["사랑", "감사", "고맙", "은혜"]):
            return ["사랑"]
        # 기본값
        else:
            return ["따뜻함"]
    
    def _get_default_situations(self, story: str) -> List[str]:
        """기본 상황 제공"""
        story_lower = story.lower()
        
        # 위로/힐링 관련
        if any(word in story_lower for word in ["위로", "힐링", "편안", "차분", "쉬고", "휴식"]):
            return ["위로"]
        # 축하/기쁨 관련
        elif any(word in story_lower for word in ["축하", "생일", "기쁨", "행복", "합격"]):
            return ["축하"]
        # 사랑/감사 관련
        elif any(word in story_lower for word in ["사랑", "감사", "고맙", "은혜"]):
            return ["감사"]
        # 기본값
        else:
            return ["일상"]
    
    def _get_default_moods(self, story: str) -> List[str]:
        """기본 무드 제공"""
        story_lower = story.lower()
        
        # 위로/힐링 관련
        if any(word in story_lower for word in ["위로", "힐링", "편안", "차분", "쉬고", "휴식"]):
            return ["따뜻한"]
        # 축하/기쁨 관련
        elif any(word in story_lower for word in ["축하", "생일", "기쁨", "행복", "합격"]):
            return ["밝은"]
        # 사랑/감사 관련
        elif any(word in story_lower for word in ["사랑", "감사", "고맙", "은혜"]):
            return ["로맨틱한"]
        # 기본값
        else:
            return ["따뜻한"]
    
    def _get_default_colors(self, story: str) -> List[str]:
        """기본 색상 제공"""
        story_lower = story.lower()
        
        # 위로/힐링 관련
        if any(word in story_lower for word in ["위로", "힐링", "편안", "차분", "쉬고", "휴식"]):
            return ["화이트"]
        # 축하/기쁨 관련
        elif any(word in story_lower for word in ["축하", "생일", "기쁨", "행복", "합격"]):
            return ["옐로우"]
        # 사랑/감사 관련
        elif any(word in story_lower for word in ["사랑", "감사", "고맙", "은혜"]):
            return ["핑크"]
        # 기본값
        else:
            return ["화이트"]
    
    def _generate_emotion_alternatives(self, main_emotion: str) -> List[str]:
        """감정 대안 키워드 생성"""
        alternatives_map = {
            "사랑": ["애정", "로맨틱", "따뜻함"],
            "감사": ["고마움", "은혜", "소중함"],
            "기쁨": ["행복", "즐거움", "설렘"],
            "희망": ["미래", "새로운 시작", "꿈"],
            "위로": ["안심", "편안함", "차분함"],
            "슬픔": ["애도", "그리움", "외로움"],
            "스트레스": ["피곤", "지침", "불안"],
            "우울": ["침울", "답답함", "허전함"],
            "설렘": ["두근거림", "떨림", "긴장"],
            "감동": ["감사", "뭉클함", "따뜻함"]
        }
        return alternatives_map.get(main_emotion, ["애정", "따뜻함", "편안함"])
    
    def _generate_situation_alternatives(self, main_situation: str) -> List[str]:
        """상황 대안 키워드 생성"""
        alternatives_map = {
            "위로": ["격려", "힐링", "안심"],
            "축하": ["경사", "축하파티", "기념"],
            "사과": ["용서", "화해", "재회"],
            "고백": ["프로포즈", "사랑", "진심"],
            "생일": ["기념일", "파티", "선물"],
            "졸업": ["학위", "성취", "새로운 시작"],
            "합격": ["성공", "축하", "자랑"],
            "친구": ["우정", "동료", "절친"],
            "가족": ["부모", "자식", "형제"],
            "로맨틱": ["데이트", "연인", "사랑"],
            "일상": ["루틴", "편안함", "소소한"],
            "방꾸미기": ["인테리어", "홈데코", "공간"],
            "휴식": ["쉬기", "힐링", "편안함"],
            "기분전환": ["새로운", "활력", "환기"],
            "스트레스해소": ["힐링", "편안함", "안정"],
            "자기위로": ["힐링", "편안함", "안정"],
            "힐링": ["치유", "편안함", "안정"],
            "명상": ["집중", "차분함", "평온"],
            "독서": ["지식", "여유", "편안함"],
            "운동": ["활력", "건강", "에너지"],
            "취미활동": ["즐거움", "창작", "표현"],
            "자기계발": ["성장", "발전", "학습"],
            "새로운시작": ["변화", "도전", "모험"],
            "거실": ["가족", "편안함", "아늑함"],
            "침실": ["휴식", "편안함", "안정"],
            "사무실": ["업무", "집중", "성과"],
            "카페": ["분위기", "아늑함", "편안함"],
            "정원": ["자연", "신선함", "평화"],
            "발코니": ["야외", "바람", "햇살"],
            "베란다": ["야외", "바람", "햇살"],
            "인테리어": ["디자인", "스타일", "분위기"],
            "홈데코": ["장식", "소품", "포인트"],
            "공간분위기": ["무드", "감성", "환경"],
            "조명": ["분위기", "밝기", "환경"]
        }
        return alternatives_map.get(main_situation, ["일상", "편안함", "즐거움"])
    
    def _generate_mood_alternatives(self, main_mood: str) -> List[str]:
        """무드 대안 키워드 생성"""
        alternatives_map = {
            "따뜻한": ["포근한", "편안한", "안정적인"],
            "부드러운": ["은은한", "조용한", "차분한"],
            "로맨틱한": ["달콤한", "사랑스러운", "아름다운"],
            "활기찬": ["경쾌한", "밝은", "즐거운"],
            "우아한": ["세련된", "고급스러운", "품격 있는"],
            "자연스러운": ["내추럴한", "깔끔한", "심플한"],
            "화려한": ["비비드한", "알록달록한", "눈부신"],
            "심플한": ["가벼운", "간단한", "미니멀한"],
            "가벼운": ["가볍지만", "간단한", "심플한"],
            "감사한": ["고마워", "은혜", "도움"],
            "사랑스러운": ["애정", "정", "마음"],
            "편안한": ["편하게", "쉬고", "휴식"],
            "평온한": ["차분", "조용한", "고요한"],
            "기분전환": ["새로운", "활력", "환기"],
            "밝은": ["밝게", "활기찬", "경쾌한"],
            "기쁜": ["행복한", "즐거운", "신나는"],
            "위로받고 싶은": ["안심", "편안함", "차분함"],
            
            # 색상 관련 무드 추가
            "시원한": ["시원한", "차분한", "상쾌한"],
            "신비로운": ["신비로운", "우아한", "고급스러운"],
            "순수한": ["순수한", "깨끗한", "정갈한"],
            "열정적인": ["열정적인", "강렬한", "뜨거운"],
            "은은한": ["은은한", "부드러운", "조용한"]
        }
        return alternatives_map.get(main_mood, ["따뜻한", "편안한", "자연스러운"])
    
    def _generate_color_alternatives(self, main_color: str, context: ExtractedContext = None) -> List[str]:
        """색상 대안 키워드 생성 - 컨텍스트 기반 색상 팔레트 추천"""
        
        # 컨텍스트가 없으면 기본 대안 반환
        if not context:
            basic_alternatives = {
                "화이트": ["핑크", "라일락"],     # wh
                "오렌지": ["옐로우", "레드"],     # or  
                "레드": ["핑크", "오렌지"],       # rd
                "옐로우": ["오렌지", "핑크"],     # yl
                "핑크": ["라일락", "화이트"],    # pk
                "라일락": ["핑크", "퍼플"],      # ll
                "블루": ["퍼플", "화이트"],      # bl
                "퍼플": ["라일락", "블루"]       # pu
            }
            return basic_alternatives.get(main_color, ["화이트", "핑크", "블루"])
        
        # 컨텍스트 기반 색상 팔레트 추천
        emotion = context.emotions[0] if context.emotions else ""
        mood = context.moods[0] if context.moods else ""
        
        # 감정 + 무드 조합에 따른 색상 팔레트
        if emotion == "위로" or "위로" in mood or "따뜻한" in mood:
            # 위로/따뜻함 → 부드럽고 편안한 색상
            warm_palette = {
                "핑크": ["라일락", "화이트"],
                "라일락": ["핑크", "퍼플"],
                "화이트": ["핑크", "라일락"],
                "퍼플": ["라일락", "핑크"],
                "블루": ["라일락", "화이트"],
                "레드": ["핑크", "라일락"],
                "오렌지": ["핑크", "옐로우"],
                "옐로우": ["핑크", "오렌지"]
            }
            return warm_palette.get(main_color, ["핑크", "라일락"])
            
        elif emotion == "기쁨" or "활기찬" in mood or "밝은" in mood:
            # 기쁨/활기찬 → 밝고 경쾌한 색상
            bright_palette = {
                "옐로우": ["오렌지", "핑크"],
                "오렌지": ["옐로우", "레드"],
                "핑크": ["옐로우", "라일락"],
                "레드": ["오렌지", "핑크"],
                "라일락": ["핑크", "퍼플"],
                "퍼플": ["라일락", "핑크"],
                "블루": ["라일락", "퍼플"],
                "화이트": ["핑크", "옐로우"]
            }
            return bright_palette.get(main_color, ["옐로우", "핑크"])
            
        elif emotion == "사랑" or "로맨틱" in mood:
            # 사랑/로맨틱 → 로맨틱한 색상
            romantic_palette = {
                "핑크": ["라일락", "레드"],
                "레드": ["핑크", "라일락"],
                "라일락": ["핑크", "퍼플"],
                "퍼플": ["라일락", "핑크"],
                "화이트": ["핑크", "라일락"],
                "블루": ["라일락", "퍼플"],
                "오렌지": ["핑크", "레드"],
                "옐로우": ["핑크", "오렌지"]
            }
            return romantic_palette.get(main_color, ["핑크", "라일락"])
            
        elif emotion == "우울" or "차분한" in mood or "시원한" in mood:
            # 우울/차분함 → 차분하고 시원한 색상
            cool_palette = {
                "블루": ["퍼플", "라일락"],
                "퍼플": ["블루", "라일락"],
                "라일락": ["블루", "퍼플"],
                "화이트": ["블루", "라일락"],
                "핑크": ["라일락", "퍼플"],
                "레드": ["퍼플", "블루"],
                "오렌지": ["라일락", "블루"],
                "옐로우": ["라일락", "블루"]
            }
            return cool_palette.get(main_color, ["블루", "라일락"])
        
        # 기본 팔레트 (위 조건에 해당하지 않는 경우)
        default_palette = {
            "핑크": ["라일락", "화이트"],
            "블루": ["퍼플", "라일락"],
            "화이트": ["핑크", "라일락"],
            "레드": ["핑크", "오렌지"],
            "옐로우": ["오렌지", "핑크"],
            "오렌지": ["옐로우", "레드"],
            "라일락": ["핑크", "퍼플"],
            "퍼플": ["라일락", "블루"]
        }
        return default_palette.get(main_color, ["화이트", "핑크", "블루"])
