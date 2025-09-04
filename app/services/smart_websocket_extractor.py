"""
스마트 WebSocket 키워드 추출기
텍스트 길이에 따라 다른 추출 전략을 사용하여 효율성과 정확성을 모두 확보
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class SmartExtractedContext:
    """스마트 추출 결과"""
    emotions: List[str]
    emotions_alternatives: List[str]
    situations: List[str]
    situations_alternatives: List[str]
    moods: List[str]
    moods_alternatives: List[str]
    colors: List[str]
    colors_alternatives: List[str]
    confidence: float
    extraction_method: str  # "rule_based", "lightweight_llm", "full_llm"
    
    def is_valid(self) -> bool:
        """결과 유효성 검사"""
        return (
            len(self.emotions) > 0 and
            len(self.situations) > 0 and
            len(self.moods) > 0 and
            len(self.colors) > 0 and
            self.confidence > 0
        )

class SmartWebSocketExtractor:
    """스마트 WebSocket 키워드 추출기"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 규칙 기반 키워드 매핑
        self.rule_keywords = {
            'emotions': ['사랑', '기쁨', '감사', '그리움', '위로', '축하', '희망', '설렘', '따뜻함'],
            'situations': ['생일', '축하', '고백', '위로', '이사', '합격', '결혼', '졸업', '기념일'],
            'moods': ['로맨틱한', '따뜻한', '밝은', '우아한', '활기찬', '사랑스러운', '경쾌한'],
            'colors': ['핑크', '레드', '화이트', '옐로우', '퍼플', '블루', '라일락', '크림']
        }
        
        # 맥락 기반 대안 키워드 매핑
        self.contextual_alternatives = {
            'emotions': {
                '사랑': ['따뜻함', '애정', '로맨틱'],
                '기쁨': ['행복', '즐거움', '설렘'],
                '감사': ['고마움', '은혜', '축복'],
                '그리움': ['추억', '아련함', '회상'],
                '위로': ['격려', '힐링', '안심'],
                '축하': ['경사', '축하파티', '기념'],
                '희망': ['미래', '새로운 시작', '꿈'],
                '힘듦': ['지침', '위로', '따뜻함']
            },
            'moods': {
                '조용한': ['차분한', '부드러운', '은은한'],
                '따뜻한': ['부드러운', '은은한', '차분한'],
                '차분한': ['조용한', '부드러운', '은은한'],
                '부드러운': ['차분한', '은은한', '조용한'],
                '로맨틱한': ['사랑스러운', '따뜻한', '우아한'],
                '활기찬': ['밝은', '경쾌한', '에너지 넘치는'],
                '우아한': ['세련된', '고급스러운', '아름다운']
            },
            'situations': {
                '자기위로': ['힐링', '휴식', '일상'],
                '힐링': ['자기위로', '휴식', '일상'],
                '스트레스': ['힘듦', '일상', '자기위로']
            },
            'colors': {
                '핑크': ['라일락', '화이트', '로즈'],
                '레드': ['크림슨', '버건디', '코랄'],
                '화이트': ['아이보리', '크림', '실버'],
                '옐로우': ['골드', '크림', '오렌지'],
                '퍼플': ['라벤더', '바이올렛', '인디고'],
                '블루': ['네이비', '스카이', '터콰이즈'],
                '라벤더': ['퍼플', '화이트', '크림']
            }
        }
        
        # 색상 매핑 테이블 (추출된 색상을 실제 꽃 데이터 색상으로 매핑)
        self.color_mapping = {
            # 크림 계열 → 화이트/옐로우
            "크림": "화이트",
            "아이보리": "화이트",
            "베이지": "화이트",
            "실버": "화이트",
            
            # 라벤더 계열 → 라벤더 (기존 유지)
            "라벤더": "라벤더",
            "연보라": "라벤더",
            "연한 보라": "라벤더",
            "연보라색": "라벤더",
            
            # 퍼플 계열 → 퍼플 (기존 유지)
            "퍼플": "퍼플",
            "보라": "퍼플",
            "진보라": "퍼플",
            "바이올렛": "퍼플",
            "인디고": "퍼플",
            
            # 기타 매핑
            "로즈": "핑크",
            "코랄": "레드",
            "크림슨": "레드",
            "버건디": "레드",
            "골드": "옐로우",
            "오렌지": "옐로우",
            "라일락": "퍼플",
            "스카이": "블루",
            "터콰이즈": "블루"
        }
    
    async def extract_with_confidence(self, story: str) -> SmartExtractedContext:
        """텍스트 길이에 따라 스마트 추출"""
        story_length = len(story.strip())
        
        if story_length < 10:
            # 빠른 추출 (규칙 기반)
            return self._rule_based_extract(story)
        
        elif story_length < 30:
            # 중간 정확도 (간단한 LLM)
            return await self._lightweight_llm_extract(story)
        
        else:
            # 높은 정확도 (전체 LLM)
            return await self._full_llm_extract(story)
    
    def _rule_based_extract(self, story: str) -> SmartExtractedContext:
        """규칙 기반 빠른 추출 (낮은 정확도, 높은 속도)"""
        story_lower = story.lower()
        
        # 간단한 키워드 매칭
        emotions = [kw for kw in self.rule_keywords['emotions'] if kw in story_lower]
        situations = [kw for kw in self.rule_keywords['situations'] if kw in story_lower]
        moods = [kw for kw in self.rule_keywords['moods'] if kw in story_lower]
        colors = [kw for kw in self.rule_keywords['colors'] if kw in story_lower]
        
        # 기본값 설정
        if not emotions:
            emotions = ['따뜻함']
        if not situations:
            situations = ['일반']
        if not moods:
            moods = ['따뜻한']
        if not colors:
            colors = ['핑크']
        
        # 색상 매핑 적용
        mapped_colors = [self._map_color(color) for color in colors[:1]]
        
        return SmartExtractedContext(
            emotions=emotions[:1],
            emotions_alternatives=self._get_contextual_alternatives(emotions[0], 'emotions', story),
            situations=situations[:1],
            situations_alternatives=self._get_contextual_alternatives(situations[0], 'situations', story),
            moods=moods[:1],
            moods_alternatives=self._get_contextual_alternatives(moods[0], 'moods', story),
            colors=mapped_colors,
            colors_alternatives=[self._map_color(alt) for alt in self._get_contextual_alternatives(colors[0], 'colors', story)],
            confidence=0.4,
            extraction_method="rule_based"
        )
    
    async def _lightweight_llm_extract(self, story: str) -> SmartExtractedContext:
        """간단한 LLM 추출 (중간 정확도, 중간 속도)"""
        try:
            prompt = f"""
            다음 이야기에서 키워드를 추출하세요:
            "{story}"
            
            **중요**: 감정과 상황을 명확히 구분하세요!
            - 감정: 내적 감정 상태 (기쁨, 슬픔, 걱정, 감사, 그리움, 설렘, 따뜻함, 힘듦, 지침)
            - 상황: 외적 상황/이벤트 (생일, 이직, 합격, 이사, 결혼, 졸업, 기념일, 축하, 자기위로, 힐링, 휴식, 스트레스, 번아웃, 일상)
            
            **추출할 정보**:
            1. 감정 (1개): 기쁨, 슬픔, 걱정, 감사, 그리움, 설렘, 따뜻함, 사랑, 힘듦, 지침 중에서
            2. 상황 (1개): 생일, 이직, 합격, 이사, 결혼, 졸업, 기념일, 축하, 자기위로, 힐링, 휴식, 스트레스, 번아웃, 일상 중에서  
            3. 무드 (1개): 로맨틱한, 따뜻한, 밝은, 우아한, 활기찬, 사랑스러운, 경쾌한, 조용한, 차분한 중에서
            4. 색상 (1개): 핑크, 레드, 화이트, 옐로우, 퍼플, 블루, 라벤더, 크림 중에서
            
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
            return self._parse_llm_response(result, story, "lightweight_llm")
            
        except Exception as e:
            print(f"❌ 간단한 LLM 추출 실패: {e}")
            return self._rule_based_extract(story)
    
    async def _full_llm_extract(self, story: str) -> SmartExtractedContext:
        """전체 LLM 추출 (높은 정확도, 낮은 속도)"""
        try:
            prompt = f"""
            다음 이야기에서 키워드를 추출하세요:
            "{story}"
            
            **중요**: 
            1. 감정과 상황을 명확히 구분하세요!
               - 감정: 내적 감정 상태 (기쁨, 슬픔, 걱정, 감사, 그리움, 설렘, 따뜻함, 사랑, 힘듦, 지침)
               - 상황: 외적 상황/이벤트 (생일, 이직, 합격, 이사, 결혼, 졸업, 기념일, 축하, 자기위로, 힐링, 휴식, 스트레스, 번아웃, 일상)
            2. 각 차원의 대안 키워드는 다른 차원의 값들을 참조하여 
               연관성과 맥락을 고려해서 추출하세요.
            
            **추출할 정보**:
            1. 감정 (1개): 기쁨, 슬픔, 걱정, 감사, 그리움, 설렘, 따뜻함, 사랑, 힘듦, 지침 중에서
            2. 상황 (1개): 생일, 이직, 합격, 이사, 결혼, 졸업, 기념일, 축하, 자기위로, 힐링, 휴식, 스트레스, 번아웃, 일상 중에서  
            3. 무드 (1개): 로맨틱한, 따뜻한, 밝은, 우아한, 활기찬, 사랑스러운, 경쾌한, 조용한, 차분한 중에서
            4. 색상 (1개): 핑크, 레드, 화이트, 옐로우, 퍼플, 블루, 라벤더, 크림 중에서
            
            **맥락 기반 대안 키워드 예시**:
            - emotions: "사랑" → 대안: "따뜻함", "기쁨" (situations: "생일", moods: "로맨틱한" 참조)
            - colors: "핑크" → 대안: "라일락", "화이트" (emotions: "사랑", moods: "사랑스러운" 참조)
            
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
                    {"role": "system", "content": "꽃 추천을 위한 맥락 기반 키워드 추출 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result, story, "full_llm")
            
        except Exception as e:
            print(f"❌ 전체 LLM 추출 실패: {e}")
            return await self._lightweight_llm_extract(story)
    
    def _parse_llm_response(self, response: str, story: str, method: str) -> SmartExtractedContext:
        """LLM 응답 파싱"""
        try:
            # JSON 추출 시도
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                data = json.loads(json_str)
                
                # 메인 키워드 추출
                emotion = data.get('emotion', '')
                situation = data.get('situation', '')
                mood = data.get('mood', '')
                color = data.get('color', '')
                
                # 색상 매핑 적용
                mapped_color = self._map_color(color)
                mapped_color_alternatives = [self._map_color(alt) for alt in self._get_contextual_alternatives(color, 'colors', story)]
                
                # 맥락 기반 대안 키워드 생성
                return SmartExtractedContext(
                    emotions=[emotion] if emotion else [],
                    emotions_alternatives=self._get_contextual_alternatives(emotion, 'emotions', story),
                    situations=[situation] if situation else [],
                    situations_alternatives=self._get_contextual_alternatives(situation, 'situations', story),
                    moods=[mood] if mood else [],
                    moods_alternatives=self._get_contextual_alternatives(mood, 'moods', story),
                    colors=[mapped_color] if mapped_color else [],
                    colors_alternatives=mapped_color_alternatives,
                    confidence=0.9 if method == "full_llm" else 0.7,
                    extraction_method=method
                )
            
            return self._rule_based_extract(story)
            
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            return self._rule_based_extract(story)
    
    def _get_contextual_alternatives(self, main_keyword: str, dimension: str, story: str) -> List[str]:
        """맥락을 고려한 대안 키워드 생성"""
        if not main_keyword:
            return []
        
        # 기본 대안 키워드
        alternatives = self.contextual_alternatives.get(dimension, {}).get(main_keyword, [])
        
        # 스토리 맥락을 고려한 추가 대안 생성
        story_lower = story.lower()
        
        if dimension == 'emotions':
            # 상황과 무드를 참조하여 감정 대안 생성
            if '생일' in story_lower or '축하' in story_lower:
                alternatives.extend(['기쁨', '설렘'])
            if '고백' in story_lower or '사랑' in story_lower:
                alternatives.extend(['설렘', '따뜻함'])
            if '위로' in story_lower or '힘들' in story_lower or '스트레스' in story_lower:
                alternatives.extend(['힘듦', '지침', '위로'])
            if '자기' in story_lower and ('위로' in story_lower or '힐링' in story_lower):
                alternatives.extend(['힘듦', '지침', '따뜻함'])
        
        elif dimension == 'situations':
            # 맥락을 고려한 상황 대안 생성
            if '자기' in story_lower and ('위로' in story_lower or '힐링' in story_lower):
                alternatives.extend(['자기위로', '힐링', '휴식'])
            if '힘들' in story_lower or '스트레스' in story_lower:
                alternatives.extend(['스트레스', '힘듦', '일상'])
            if '선물' in story_lower and '자기' in story_lower:
                alternatives.extend(['자기위로', '힐링', '일상'])
        
        elif dimension == 'moods':
            # 맥락을 고려한 무드 대안 생성
            if '조용한' in story_lower or '차분한' in story_lower:
                alternatives.extend(['차분한', '부드러운', '은은한'])
            if '따뜻한' in story_lower or '위로' in story_lower:
                alternatives.extend(['따뜻한', '부드러운', '은은한'])
            if '힘들' in story_lower or '스트레스' in story_lower:
                alternatives.extend(['차분한', '부드러운', '조용한'])
            if '자기' in story_lower and ('위로' in story_lower or '힐링' in story_lower):
                alternatives.extend(['차분한', '부드러운', '조용한'])
        
        elif dimension == 'colors':
            # 감정과 무드를 참조하여 색상 대안 생성
            if '사랑' in story_lower or '로맨틱' in story_lower:
                alternatives.extend(['라일락', '화이트'])
            if '기쁨' in story_lower or '밝은' in story_lower:
                alternatives.extend(['옐로우', '화이트'])
            if '따뜻한' in story_lower or '위로' in story_lower:
                alternatives.extend(['크림', '화이트'])
            if '힘들' in story_lower or '지침' in story_lower:
                alternatives.extend(['화이트', '크림', '라벤더'])
        
        # 중복 제거하고 최대 3개 반환
        unique_alternatives = list(dict.fromkeys(alternatives))
        return unique_alternatives[:3]
    
    def _map_color(self, color: str) -> str:
        """색상을 실제 꽃 데이터 색상으로 매핑"""
        return self.color_mapping.get(color, color)
    
    def cleanup(self):
        """리소스 정리"""
        pass
