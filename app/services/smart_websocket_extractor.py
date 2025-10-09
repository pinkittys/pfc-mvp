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
        
        # 꽃 색상 풀 데이터 로드
        self.flower_color_pools = self._load_flower_color_pools()
        
        # 규칙 기반 키워드 매핑
        self.rule_keywords = {
            'emotions': ['사랑', '기쁨', '감사', '그리움', '위로', '축하', '희망', '설렘', '따뜻함'],
            'situations': ['생일', '축하', '고백', '위로', '이사', '합격', '결혼', '졸업', '기념일'],
            'moods': ['로맨틱한', '따뜻한', '밝은', '우아한', '활기찬', '사랑스러운', '경쾌한'],
            'colors': ['핑크', '레드', '화이트', '옐로우', '퍼플', '블루', '라일락', '크림', '오렌지', '코랄']
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
            
            # 오렌지 계열 → 오렌지
            "오렌지": "오렌지",
            "주황": "오렌지",
            "주황색": "오렌지",
            
            # 코랄 계열 → 코랄
            "코랄": "코랄",
            "코랄색": "코랄",
            "산호": "코랄",
            "인디고": "퍼플",
            
            # 기타 매핑
            "로즈": "핑크",
            "크림슨": "레드",
            "버건디": "레드",
            "골드": "옐로우",
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
            4. 색상 (1개): 핑크, 레드, 화이트, 옐로우, 퍼플, 블루, 라벤더, 크림, 오렌지, 코랄 중에서
            
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
            4. 색상 (1개): 핑크, 레드, 화이트, 옐로우, 퍼플, 블루, 라벤더, 크림, 오렌지, 코랄 중에서
            
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
    
    def _load_flower_color_pools(self) -> Dict[str, List[str]]:
        """꽃별 색상 풀 데이터 로드"""
        try:
            with open('data/spreadsheet_flowers.json', 'r', encoding='utf-8') as f:
                flowers_data = json.load(f)
            
            flower_color_pools = {}
            for flower_data in flowers_data:
                flower_name = flower_data.get('name_ko', '')
                flower_slug = flower_data.get('flower_slug', '')
                color_code = flower_data.get('color_code', '')
                
                if (flower_name or flower_slug) and color_code:
                    # 색상 코드를 한글 색상명으로 변환
                    color_mapping = {
                        'wh': '화이트', 'pk': '핑크', 'rd': '레드', 'yl': '옐로우',
                        'or': '오렌지', 'bl': '블루', 'pu': '퍼플', 'll': '라벤더',
                        'gr': '그린', 'cr': '크림'
                    }
                    
                    color_name = color_mapping.get(color_code, color_code)
                    
                    # 꽃 이름 매핑 (영문 -> 한글)
                    flower_mapping = {
                        'gerbera': '거베라',
                        'gerbera-daisy': '거베라',  # 거베라 데이지 매핑 추가
                        'sunflower': '해바라기', 
                        'rose': '장미',
                        'lily': '백합',
                        'tulip': '튤립',
                        'hydrangea': '수국',
                        'freesia': '프리지아',
                        'marigold': '마리골드',
                        'tagetes': '태게테스',
                        'alstroemeria': '알스트로메리아',
                        'lisianthus': '리시안셔스'
                    }
                    
                    # 한글 이름이 있으면 사용, 없으면 영문 slug를 한글로 변환
                    if flower_name and flower_name.strip():
                        final_flower_name = flower_name
                    else:
                        final_flower_name = flower_mapping.get(flower_slug, flower_slug)
                    
                    if final_flower_name not in flower_color_pools:
                        flower_color_pools[final_flower_name] = []
                    
                    if color_name not in flower_color_pools[final_flower_name]:
                        flower_color_pools[final_flower_name].append(color_name)
            
            print(f"🌸 꽃 색상 풀 로드 완료: {len(flower_color_pools)}개 꽃")
            # 디버깅: 거베라 색상 풀 확인
            if '거베라' in flower_color_pools:
                print(f"🌸 거베라 색상 풀: {flower_color_pools['거베라']}")
            else:
                print(f"❌ 거베라가 색상 풀에 없음")
                print(f"🔍 로드된 꽃들: {list(flower_color_pools.keys())}")
            return flower_color_pools
            
        except Exception as e:
            print(f"❌ 꽃 색상 풀 로드 실패: {e}")
            return {}
    
    def _get_flower_color_pool(self, flower_name: str) -> List[str]:
        """특정 꽃의 색상 풀 반환"""
        return self.flower_color_pools.get(flower_name, [])
    
    def _get_mentioned_flower_colors(self, story: str) -> List[str]:
        """스토리에서 언급된 꽃의 색상 풀 반환"""
        story_lower = story.lower()
        print(f"🔍 스토리에서 꽃 이름 검색: '{story_lower}'")
        
        # 꽃 이름 매핑 (한글 -> 한글, 한글 -> 영문)
        flower_mapping = {
            '거베라': ['거베라', 'gerbera'],
            '해바라기': ['해바라기', 'sunflower'], 
            '장미': ['장미', 'rose'],
            '백합': ['백합', 'lily'],
            '튤립': ['튤립', 'tulip'],
            '수국': ['수국', 'hydrangea'],
            '프리지아': ['프리지아', 'freesia'],
            '마리골드': ['마리골드', 'marigold'],
            '태게테스': ['태게테스', 'tagetes'],
            '알스트로메리아': ['알스트로메리아', 'alstroemeria'],
            '리시안셔스': ['리시안셔스', 'lisianthus'],
            '라벤더': ['라벤더', 'lavender'],
            '라벤다': ['라벤다', 'lavender']
        }
        
        # 언급된 꽃 찾기
        for flower_name, possible_names in flower_mapping.items():
            if flower_name in story_lower:
                print(f"✅ 언급된 꽃 발견: '{flower_name}'")
                
                # 가능한 모든 이름으로 색상 풀 찾기
                for possible_name in possible_names:
                    color_pool = self._get_flower_color_pool(possible_name)
                    print(f"🔍 '{possible_name}'의 색상 풀: {color_pool}")
                    if color_pool:
                        print(f"🌸 언급된 꽃 '{flower_name}'의 색상 풀: {color_pool}")
                        return color_pool
                
                print(f"❌ '{flower_name}'의 모든 가능한 이름에서 색상 풀을 찾을 수 없음")
        
        print(f"❌ 언급된 꽃을 찾을 수 없음")
        return []
    
    def _get_contextual_alternatives(self, main_keyword: str, dimension: str, story: str) -> List[str]:
        """맥락을 고려한 대안 키워드 생성"""
        if not main_keyword:
            return []
        
        # 기본 대안 키워드
        alternatives = self.contextual_alternatives.get(dimension, {}).get(main_keyword, [])
        
        # 기본 대안이 없으면 전체 키워드 목록에서 랜덤하게 선택
        if not alternatives:
            if dimension == 'emotions':
                alternatives = ['따뜻함', '기쁨', '감사']
            elif dimension == 'situations':
                alternatives = ['일상', '축하', '위로']
            elif dimension == 'moods':
                alternatives = ['따뜻한', '부드러운', '차분한']
            elif dimension == 'colors':
                alternatives = ['화이트', '핑크', '라벤더']
        
        # 대안키워드가 여전히 비어있으면 강제로 기본값 설정
        if not alternatives:
            alternatives = ['기본값1', '기본값2', '기본값3']
        
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
            # 기본 대안이 없으면 추가
            if not alternatives:
                alternatives.extend(['따뜻함', '기쁨', '감사'])
        
        elif dimension == 'situations':
            # 맥락을 고려한 상황 대안 생성
            if '자기' in story_lower and ('위로' in story_lower or '힐링' in story_lower):
                alternatives.extend(['자기위로', '힐링', '휴식'])
            if '힘들' in story_lower or '스트레스' in story_lower:
                alternatives.extend(['스트레스', '힘듦', '일상'])
            if '선물' in story_lower and '자기' in story_lower:
                alternatives.extend(['자기위로', '힐링', '일상'])
            # 기본 대안이 없으면 추가
            if not alternatives:
                alternatives.extend(['일상', '축하', '위로'])
        
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
            # 기본 대안이 없으면 추가
            if not alternatives:
                alternatives.extend(['따뜻한', '부드러운', '차분한'])
        
        elif dimension == 'colors':
            # 맥락을 고려한 색상 대안 생성 (유사한 느낌의 색상들)
            story_lower = story.lower()
            
            # 언급된 꽃의 색상 풀 확인
            mentioned_flower_colors = self._get_mentioned_flower_colors(story)
            if mentioned_flower_colors:
                alternatives = mentioned_flower_colors[:3]  # 언급된 꽃의 색상 풀 사용
                print(f"🌸 언급된 꽃 색상 풀 사용: {alternatives}")
            else:
                # 위로/힐링/병문안 맥락
                if any(word in story_lower for word in ['위로', '힐링', '병원', '입원', '편찮', '아프', '안부', '병문안', '치유', '회복', '안정', '평온', '차분', '조용', '편안']):
                    alternatives = ['크림', '라벤더', '블루']  # 차분하고 위로가 되는 색상들
                
                # 축하/기쁨/생일 맥락
                elif any(word in story_lower for word in ['축하', '기쁨', '생일', '합격', '성공', '졸업', '승진', '취업', '파티', '잔치']):
                    alternatives = ['핑크', '옐로우', '오렌지']  # 밝고 축하하는 색상들
                
                # 로맨틱/사랑 맥락
                elif any(word in story_lower for word in ['사랑', '로맨틱', '연인', '아내', '남편', '여자친구', '남자친구', '고백', '프로포즈', '결혼', '기념일']):
                    alternatives = ['핑크', '레드', '크림']  # 로맨틱한 색상들
                
                # 감사/고마움 맥락
                elif any(word in story_lower for word in ['감사', '고마워', '고생', '애써', '도움', '배려']):
                    alternatives = ['크림', '화이트', '핑크']  # 따뜻하고 감사한 색상들
                
                # 우아함/고급스러움 맥락
                elif any(word in story_lower for word in ['우아한', '고급스러운', '세련된', '품격', '신비로운', '아름다운']):
                    alternatives = ['퍼플', '화이트', '크림']  # 우아하고 고급스러운 색상들
                
                # 기본값 (일반적인 상황)
                else:
                    alternatives = ['화이트', '핑크', '크림']  # 중성적이고 안전한 색상들
        
        # 중복 제거하고 최대 3개 반환
        unique_alternatives = list(dict.fromkeys(alternatives))
        return unique_alternatives[:3]
    
    def _map_color(self, color: str) -> str:
        """색상을 실제 꽃 데이터 색상으로 매핑"""
        return self.color_mapping.get(color, color)
    
    def cleanup(self):
        """리소스 정리"""
        pass
