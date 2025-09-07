import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.supabase_image_fetcher import SupabaseImageFetcher

@dataclass
class FlowerData:
    """꽃 데이터 구조"""
    name_ko: str
    name_en: str
    scientific_name: str
    base_color: str
    alt_colors: List[str]
    flower_language_short: str
    flower_language_long: str
    emotions: List[str]
    contexts: List[str]
    moods: List[str]
    season_months: List[int]
    popularity: str

@dataclass
class LLMMatchResult:
    """LLM 매칭 결과"""
    flower_data: FlowerData
    image_url: str
    confidence: float
    match_reason: str
    llm_explanation: str

class LLMFlowerMatcher:
    """LLM 기반 꽃 추천 시스템"""
    
    def __init__(self):
        self.context_extractor = RealtimeContextExtractor()
        self.image_fetcher = SupabaseImageFetcher()
        self.flower_data = self._load_flower_data()
        
        # OpenAI 클라이언트 직접 초기화
        import openai
        self.client = openai.OpenAI(api_key=self.context_extractor.openai_api_key)
        
    def _load_flower_data(self) -> List[FlowerData]:
        """꽃 데이터 로드"""
        try:
            with open('data/flower_dictionary.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 실제 꽃 데이터는 'flowers' 키에 있음
            flowers_data = data.get('flowers', {})
            
            flowers = []
            for key, item in flowers_data.items():
                # 색상 매핑 (한국어 -> 영어 코드)
                color_mapping = {
                    '화이트': 'wh', '흰색': 'wh',
                    '오렌지': 'or', '주황': 'or',
                    '레드': 'rd', '빨강': 'rd',
                    '옐로우': 'yl', '노랑': 'yl',
                    '핑크': 'pk', '분홍': 'pk',
                    '라일락': 'll', '연보라': 'll',
                    '블루': 'bl', '파랑': 'bl',
                    '퍼플': 'pu', '보라': 'pu',
                    '그린': 'gr', '초록': 'gr'
                }
                
                korean_color = item.get('color', '')
                base_color = color_mapping.get(korean_color, korean_color.lower() if korean_color else 'wh')
                
                flower = FlowerData(
                    name_ko=item.get('korean_name', ''),
                    name_en=item.get('scientific_name', '').split()[0] if item.get('scientific_name') else '',
                    scientific_name=item.get('scientific_name', ''),
                    base_color=base_color,
                    alt_colors=[],
                    flower_language_short=item.get('flower_meanings', {}).get('meanings', [''])[0] if item.get('flower_meanings', {}).get('meanings') else '',
                    flower_language_long=item.get('flower_meanings', {}).get('meanings', [''])[0] if item.get('flower_meanings', {}).get('meanings') else '',
                    emotions=item.get('flower_meanings', {}).get('emotions', []),
                    contexts=item.get('flower_meanings', {}).get('meanings', []),
                    moods=item.get('moods', {}).get('primary', []),
                    season_months=[],
                    popularity='medium'
                )
                flowers.append(flower)
            
            print(f"✅ {len(flowers)}개 꽃 데이터 로드 완료")
            return flowers
            
        except Exception as e:
            print(f"❌ 꽃 데이터 로드 실패: {e}")
            return []
    
    def match_flower(self, story: str, preferred_colors: List[str] = None) -> Optional[LLMMatchResult]:
        """LLM 기반 꽃 매칭"""
        try:
            print(f"🚀 LLM 매칭 시작: story='{story}', colors={preferred_colors}")
            
            # 1. 색상 필터링 (사용자 요청이 있는 경우)
            if preferred_colors:
                candidates = self._filter_by_color(preferred_colors)
                print(f"🎨 색상 필터링: {len(candidates)}개 후보")
                print(f"🎨 필터링된 꽃들: {[f'{f.name_ko}({f.base_color})' for f in candidates[:5]]}")
            else:
                candidates = self.flower_data
                print(f"🌺 전체 후보: {len(candidates)}개")
            
            if not candidates:
                print("❌ 후보 꽃이 없습니다")
                return None
            
            # 2. LLM이 후보군 중에서 최적 선택
            print(f"🤖 LLM 선택 시작...")
            selected_flower = self._llm_select_flower(story, candidates, preferred_colors)
            if not selected_flower:
                print("❌ LLM 선택 실패")
                return None
            
            # 3. 이미지 URL 가져오기
            image_url = self._get_flower_image_url(selected_flower)
            
            # 4. 매칭 이유 생성
            match_reason = self._generate_match_reason(story, selected_flower)
            
            # 5. 결과 반환
            result = LLMMatchResult(
                flower_data=selected_flower,
                image_url=image_url,
                confidence=0.9,  # LLM 기반이므로 높은 신뢰도
                match_reason=match_reason,
                llm_explanation=f"LLM이 '{story}' 상황에 가장 적합한 꽃으로 {selected_flower.name_ko}를 선택했습니다."
            )
            
            print(f"✅ LLM 매칭 성공: {selected_flower.name_ko}")
            return result
            
        except Exception as e:
            print(f"❌ LLM 매칭 실패: {e}")
            return None
    
    def _filter_by_color(self, preferred_colors: List[str]) -> List[FlowerData]:
        """색상별 꽃 필터링"""
        filtered = []
        for flower in self.flower_data:
            if flower.base_color in preferred_colors or any(color in flower.alt_colors for color in preferred_colors):
                filtered.append(flower)
        
        # 해당 색상의 꽃이 없으면 빈 리스트 반환
        if not filtered and preferred_colors:
            print(f"⚠️ {preferred_colors} 색상의 꽃이 없습니다. 전체 꽃에서 선택합니다.")
            return self.flower_data  # 전체 꽃에서 선택하도록 변경
        
        return filtered
    
    def _llm_select_flower(self, story: str, candidates: List[FlowerData], preferred_colors: List[str] = None) -> Optional[FlowerData]:
        """LLM이 후보군 중에서 최적의 꽃 선택"""
        try:
            # 후보 꽃들을 텍스트로 포맷팅
            candidates_text = self._format_flower_candidates(candidates)
            
            # LLM 프롬프트 생성
            prompt = f"""
다음 상황에 가장 적합한 꽃을 선택해주세요:

상황: {story}
선호 색상: {preferred_colors if preferred_colors else "제한 없음"}

**중요**: 
- 선호 색상이 지정된 경우, 해당 색상의 꽃을 우선 선택하세요.
- 만약 선호 색상의 꽃이 없다면, 상황과 꽃말에 가장 적합한 꽃을 선택하세요.
- 색상이 일치하는 꽃이 여러 개 있다면, 상황과 꽃말에 가장 적합한 것을 선택하세요.

후보 꽃들:
{candidates_text}

각 꽃의 꽃말, 감정, 상황, 무드를 고려하여 가장 적합한 꽃의 한국어 이름을 정확히 알려주세요.
답변은 꽃의 한국어 이름만 정확히 써주세요. (예: 용담, 수국, 카네이션)
"""
            
            # LLM 호출
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            selected_name = response.choices[0].message.content.strip()
            print(f"🤖 LLM 선택: {selected_name}")
            
            # 선택된 꽃 찾기
            for flower in candidates:
                if flower.name_ko == selected_name:
                    return flower
            
            print(f"⚠️ LLM이 선택한 '{selected_name}'이 후보에 없습니다")
            return None
            
        except Exception as e:
            print(f"❌ LLM 선택 실패: {e}")
            return None
    
    def _format_flower_candidates(self, candidates: List[FlowerData]) -> str:
        """후보 꽃들을 텍스트로 포맷팅"""
        formatted = []
        for i, flower in enumerate(candidates[:10], 1):  # 상위 10개만 표시
            flower_info = f"""
{i}. {flower.name_ko} ({flower.name_en})
   - 꽃말: {flower.flower_language_short} - {flower.flower_language_long}
   - 감정: {', '.join(flower.emotions)}
   - 상황: {', '.join(flower.contexts)}
   - 무드: {', '.join(flower.moods)}
   - 색상: {flower.base_color} (대체: {', '.join(flower.alt_colors)})
"""
            formatted.append(flower_info)
        
        return '\n'.join(formatted)
    
    def _get_flower_image_url(self, flower: FlowerData) -> str:
        """꽃 이미지 URL 가져오기"""
        try:
            image = self.image_fetcher.find_image(flower.name_ko, flower.base_color)
            if image:
                return image.url
            else:
                # 폴백: 기본 이미지 URL
                return f"https://cdn.plainflower.club/images/{flower.name_en.lower().replace(' ', '-')}-{flower.base_color}.webp"
        except Exception as e:
            print(f"❌ 이미지 URL 가져오기 실패: {e}")
            return f"https://cdn.plainflower.club/images/{flower.name_en.lower().replace(' ', '-')}-{flower.base_color}.webp"
    
    def _generate_match_reason(self, story: str, flower: FlowerData) -> str:
        """매칭 이유 생성"""
        reasons = []
        
        # 꽃말 매칭
        if flower.flower_language_short:
            reasons.append(f"{flower.flower_language_short}의 꽃말")
        
        # 감정 매칭
        if flower.emotions:
            reasons.append(f"{', '.join(flower.emotions[:2])} 감정에 적합")
        
        # 상황 매칭
        if flower.contexts:
            reasons.append(f"{', '.join(flower.contexts[:2])} 상황에 적합")
        
        # 색상 매칭
        reasons.append(f"{flower.base_color} 색상의 아름다움")
        
        return f"{flower.name_ko}는 {', '.join(reasons)}으로 이 상황에 가장 적합합니다."
