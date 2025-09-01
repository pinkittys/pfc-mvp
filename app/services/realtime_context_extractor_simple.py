"""
간소화된 실시간 컨텍스트 추출기
빠르고 안정적인 키워드 추출을 위한 최적화된 버전
"""

import os
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from openai import OpenAI
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ExtractedContext:
    """추출된 컨텍스트 정보"""
    emotions: List[str] = field(default_factory=list)
    emotions_alternatives: List[str] = field(default_factory=list)
    situations: List[str] = field(default_factory=list)
    situations_alternatives: List[str] = field(default_factory=list)
    moods: List[str] = field(default_factory=list)
    moods_alternatives: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    colors_alternatives: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def is_valid(self) -> bool:
        """컨텍스트가 유효한지 확인"""
        return (len(self.emotions) > 0 or len(self.situations) > 0 or 
                len(self.moods) > 0 or len(self.colors) > 0)

class SimpleRealtimeContextExtractor:
    """간소화된 실시간 컨텍스트 추출기"""
    
    def __init__(self):
        self.openai_client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._init_openai()
        
        # 간단한 키워드 매핑 (fallback용)
        self.simple_keywords = {
            'emotions': ['사랑', '기쁨', '감사', '그리움', '위로', '축하', '희망'],
            'situations': ['고백', '생일', '축하', '위로', '이사', '합격', '결혼'],
            'moods': ['로맨틱한', '따뜻한', '밝은', '우아한', '활기찬'],
            'colors': ['핑크', '레드', '화이트', '옐로우', '퍼플', '블루']
        }
    
    def _init_openai(self):
        """OpenAI 클라이언트 초기화"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                print("✅ OpenAI 클라이언트 초기화 완료")
            else:
                print("⚠️ OPENAI_API_KEY가 설정되지 않음")
        except Exception as e:
            print(f"❌ OpenAI 초기화 실패: {e}")
    
    async def extract_context_realtime_async(self, story: str) -> ExtractedContext:
        """비동기 실시간 컨텍스트 추출"""
        try:
            # 비동기로 LLM 처리
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._extract_with_llm, 
                story
            )
            
            if result and result.is_valid():
                return result
            
            # LLM 실패 시 간단한 규칙 기반
            return self._extract_with_rules(story)
            
        except Exception as e:
            print(f"❌ 비동기 추출 실패: {e}")
            return self._extract_with_rules(story)
    
    def extract_context_realtime(self, story: str) -> ExtractedContext:
        """동기 실시간 컨텍스트 추출 (기존 호환성)"""
        try:
            # LLM 시도
            result = self._extract_with_llm(story)
            if result and result.is_valid():
                return result
            
            # 실패 시 규칙 기반
            return self._extract_with_rules(story)
            
        except Exception as e:
            print(f"❌ 동기 추출 실패: {e}")
            return self._extract_with_rules(story)
    
    def _extract_with_llm(self, story: str) -> Optional[ExtractedContext]:
        """LLM을 사용한 키워드 추출 (간소화된 프롬프트)"""
        if not self.openai_client or len(story.strip()) < 5:
            return None
        
        try:
            # 간소화된 프롬프트
            prompt = f"""
사용자의 이야기에서 다음 4가지 정보를 추출해주세요:

**이야기**: {story}

**추출할 정보**:
1. 감정 (1개): 사랑, 기쁨, 감사, 그리움, 위로, 축하, 희망 중에서
2. 상황 (1개): 고백, 생일, 축하, 위로, 이사, 합격, 결혼 중에서  
3. 무드 (1개): 로맨틱한, 따뜻한, 밝은, 우아한, 활기찬 중에서
4. 색상 (1개): 핑크, 레드, 화이트, 옐로우, 퍼플, 블루 중에서

**응답 형식** (JSON):
{{
    "emotion": "감정명",
    "situation": "상황명", 
    "mood": "무드명",
    "color": "색상명"
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "꽃 추천을 위한 키워드 추출 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result)
            
        except Exception as e:
            print(f"❌ LLM 추출 실패: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[ExtractedContext]:
        """LLM 응답 파싱"""
        try:
            # JSON 추출 시도
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                data = json.loads(json_str)
                
                # 대안 키워드 생성
                emotion = data.get('emotion', '')
                situation = data.get('situation', '')
                mood = data.get('mood', '')
                color = data.get('color', '')
                
                return ExtractedContext(
                    emotions=[emotion] if emotion else [],
                    emotions_alternatives=self._get_alternatives(emotion, 'emotions'),
                    situations=[situation] if situation else [],
                    situations_alternatives=self._get_alternatives(situation, 'situations'),
                    moods=[mood] if mood else [],
                    moods_alternatives=self._get_alternatives(mood, 'moods'),
                    colors=[color] if color else [],
                    colors_alternatives=self._get_alternatives(color, 'colors'),
                    confidence=0.9
                )
            
            return None
            
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            return None
    
    def _extract_with_rules(self, story: str) -> ExtractedContext:
        """규칙 기반 키워드 추출 (fallback)"""
        story_lower = story.lower()
        
        # 간단한 키워드 매칭
        emotions = [kw for kw in self.simple_keywords['emotions'] if kw in story_lower]
        situations = [kw for kw in self.simple_keywords['situations'] if kw in story_lower]
        moods = [kw for kw in self.simple_keywords['moods'] if kw in story_lower]
        colors = [kw for kw in self.simple_keywords['colors'] if kw in story_lower]
        
        # 기본값 설정
        if not emotions:
            emotions = ['따뜻함']
        if not situations:
            situations = ['일반']
        if not moods:
            moods = ['따뜻한']
        if not colors:
            colors = ['핑크']
        
        return ExtractedContext(
            emotions=emotions[:1],
            emotions_alternatives=self._get_alternatives(emotions[0], 'emotions'),
            situations=situations[:1],
            situations_alternatives=self._get_alternatives(situations[0], 'situations'),
            moods=moods[:1],
            moods_alternatives=self._get_alternatives(moods[0], 'moods'),
            colors=colors[:1],
            colors_alternatives=self._get_alternatives(colors[0], 'colors'),
            confidence=0.6
        )
    
    def _get_alternatives(self, main_keyword: str, category: str) -> List[str]:
        """메인 키워드에 대한 대안 키워드 생성"""
        if not main_keyword:
            return []
        
        # 간단한 대안 매핑
        alternatives_map = {
            '사랑': ['애정', '로맨틱', '따뜻함'],
            '기쁨': ['행복', '즐거움', '설렘'],
            '감사': ['고마움', '은혜', '축복'],
            '그리움': ['추억', '아련함', '회상'],
            '위로': ['격려', '힐링', '안심'],
            '축하': ['경사', '축하파티', '기념'],
            '희망': ['미래', '새로운 시작', '꿈'],
            '핑크': ['라일락', '화이트', '로즈'],
            '레드': ['크림슨', '버건디', '코랄'],
            '화이트': ['아이보리', '크림', '실버'],
            '옐로우': ['골드', '크림', '오렌지'],
            '퍼플': ['라벤더', '바이올렛', '인디고'],
            '블루': ['네이비', '스카이', '터콰이즈']
        }
        
        return alternatives_map.get(main_keyword, [])[:3]
    
    def cleanup(self):
        """리소스 정리"""
        if self.executor:
            self.executor.shutdown(wait=False)

