"""
간단하고 빠른 실시간 키워드 추출 서비스 (원래 버전)
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
    print("⚠️  python-dotenv가 설치되지 않았습니다.")

@dataclass
class ExtractedContext:
    """추출된 맥락 정보"""
    emotions: List[str]  # 감정
    situations: List[str]  # 상황
    moods: List[str]  # 무드
    colors: List[str]  # 컬러
    confidence: float  # 신뢰도
    user_intent: str = "meaning_based"  # 사용자 의도

class SimpleRealtimeContextExtractor:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
    
    def extract_context_realtime(self, story: str) -> ExtractedContext:
        """간단하고 빠른 실시간 키워드 추출"""
        if not self.openai_api_key:
            return self._fallback_extraction(story)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # 간단한 프롬프트
            prompt = f"""
다음 이야기에서 꽃 추천에 필요한 키워드를 추출해주세요:

"{story}"

다음 형식으로만 응답하세요:
emotions: [감정1개]
situations: [상황1개]
moods: [무드1개]
colors: [색상1개]

예시:
emotions: [기쁨]
situations: [생일]
moods: [밝은]
colors: [핑크]
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "꽃 추천 키워드 추출 전문가입니다. 간단하고 정확하게 추출해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content
            return self._parse_simple_response(result)
            
        except Exception as e:
            print(f"❌ 실시간 키워드 추출 실패: {e}")
            return self._fallback_extraction(story)
    
    def _parse_simple_response(self, response: str) -> ExtractedContext:
        """간단한 응답 파싱"""
        try:
            emotions = []
            situations = []
            moods = []
            colors = []
            
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('emotions:'):
                    emotions = self._extract_brackets(line)
                elif line.startswith('situations:'):
                    situations = self._extract_brackets(line)
                elif line.startswith('moods:'):
                    moods = self._extract_brackets(line)
                elif line.startswith('colors:'):
                    colors = self._extract_brackets(line)
            
            return ExtractedContext(
                emotions=emotions[:1] if emotions else ["기쁨"],
                situations=situations[:1] if situations else ["일상"],
                moods=moods[:1] if moods else ["따뜻한"],
                colors=colors[:1] if colors else ["화이트"],
                confidence=0.9
            )
            
        except Exception as e:
            print(f"❌ 응답 파싱 실패: {e}")
            return self._fallback_extraction("")
    
    def _extract_brackets(self, text: str) -> List[str]:
        """대괄호 안의 내용 추출"""
        try:
            start = text.find('[')
            end = text.find(']')
            if start != -1 and end != -1:
                content = text[start+1:end].strip()
                return [item.strip() for item in content.split(',') if item.strip()]
        except:
            pass
        return []
    
    def _fallback_extraction(self, story: str) -> ExtractedContext:
        """폴백 추출 (간단한 규칙 기반)"""
        emotions = ["기쁨"]
        situations = ["일상"]
        moods = ["따뜻한"]
        colors = ["화이트"]
        
        story_lower = story.lower()
        
        # 간단한 키워드 매칭
        if "생일" in story_lower or "축하" in story_lower:
            emotions = ["기쁨"]
            situations = ["생일"]
            moods = ["밝은"]
            colors = ["핑크"]
        elif "고백" in story_lower or "사랑" in story_lower:
            emotions = ["사랑"]
            situations = ["연인"]
            moods = ["로맨틱한"]
            colors = ["레드"]
        elif "위로" in story_lower or "슬픔" in story_lower:
            emotions = ["위로"]
            situations = ["위로"]
            moods = ["따뜻한"]
            colors = ["화이트"]
        elif "감사" in story_lower or "고마워" in story_lower:
            emotions = ["감사"]
            situations = ["감사"]
            moods = ["따뜻한"]
            colors = ["옐로우"]
        
        return ExtractedContext(
            emotions=emotions,
            situations=situations,
            moods=moods,
            colors=colors,
            confidence=0.7
        )

