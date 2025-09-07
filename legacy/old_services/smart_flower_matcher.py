"""
스마트 꽃 매칭 시스템
- 색상 우선 → 상황 → 감정 → 무드 순으로 우선순위
- 스프레드시트 DB와 Supabase 통합
- 자동 꽃 이름 매핑
"""
import pandas as pd
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from app.models.schemas import EmotionAnalysis

@dataclass
class SmartMatchResult:
    """스마트 매칭 결과"""
    flower_name: str
    korean_name: str
    scientific_name: str
    image_url: str
    confidence: float
    match_reason: str
    color_matched: bool
    situation_matched: bool
    emotion_matched: bool
    mood_matched: bool

class SmartFlowerMatcher:
    """스마트 꽃 매칭 시스템"""
    
    def __init__(self):
        """초기화"""
        self.flower_data = self._load_unified_flower_data()
        self.color_priority = self._setup_color_priority()
        self.situation_mapping = self._setup_situation_mapping()
        self.emotion_mapping = self._setup_emotion_mapping()
        self.mood_mapping = self._setup_mood_mapping()
        
        print(f"🧠 스마트 매칭 시스템 초기화 완료")
        print(f"   📊 통합 꽃 데이터: {len(self.flower_data)}개")
    
    def _load_unified_flower_data(self) -> pd.DataFrame:
        """통합 꽃 데이터 로드 (스프레드시트 + Supabase)"""
        try:
            # 1. 스프레드시트 데이터 로드
            spreadsheet_data = self._load_spreadsheet_data()
            
            # 2. Supabase 이미지 데이터 로드
            supabase_data = self._load_supabase_data()
            
            # 3. 데이터 통합
            unified_data = self._merge_data_sources(spreadsheet_data, supabase_data)
            
            return unified_data
            
        except Exception as e:
            print(f"❌ 통합 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def _load_spreadsheet_data(self) -> pd.DataFrame:
        """스프레드시트 데이터 로드"""
        try:
            with open("data/flower_dictionary.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "flowers" in data:
                    return pd.DataFrame(data["flowers"])
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ 스프레드시트 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def _load_supabase_data(self) -> pd.DataFrame:
        """Supabase 이미지 데이터 로드"""
        try:
            # Supabase에서 이미지 메타데이터 로드
            with open("data/calli_metadata.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Supabase 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def _merge_data_sources(self, spreadsheet: pd.DataFrame, supabase: pd.DataFrame) -> pd.DataFrame:
        """데이터 소스 통합"""
        if spreadsheet.empty and supabase.empty:
            return pd.DataFrame()
        
        if spreadsheet.empty:
            return supabase
        
        if supabase.empty:
            return spreadsheet
        
        # 꽃 이름 기준으로 통합
        merged = pd.merge(
            spreadsheet, 
            supabase, 
            left_on='name_ko', 
            right_on='korean_flower_name', 
            how='outer'
        )
        
        return merged
    
    def _setup_color_priority(self) -> Dict[str, int]:
        """색상 우선순위 설정"""
        return {
            '핑크': 10, 'pink': 10,
            '빨강': 9, 'red': 9,
            '화이트': 8, 'white': 8,
            '옐로우': 7, 'yellow': 7,
            '퍼플': 6, 'purple': 6,
            '블루': 5, 'blue': 5,
            '그린': 4, 'green': 4,
            '오렌지': 3, 'orange': 3
        }
    
    def _setup_situation_mapping(self) -> Dict[str, List[str]]:
        """상황별 꽃 매핑"""
        return {
            '축하': ['라넌큘러스', '장미', '거베라', '튤립'],
            '사랑': ['장미', '라넌큘러스', '튤립', '백합'],
            '감사': ['라넌큘러스', '장미', '거베라', '수국'],
            '위로': ['수국', '라벤더', '화이트장미', '백합'],
            '기념일': ['라넌큘러스', '장미', '튤립', '거베라'],
            '출산': ['핑크장미', '라넌큘러스', '거베라', '튤립'],
            '졸업': ['해바라기', '거베라', '튤립', '장미']
        }
    
    def _setup_emotion_mapping(self) -> Dict[str, List[str]]:
        """감정별 꽃 매핑"""
        return {
            '기쁨': ['해바라기', '거베라', '튤립', '라넌큘러스'],
            '사랑': ['장미', '라넌큘러스', '튤립', '백합'],
            '감사': ['라넌큘러스', '장미', '거베라', '수국'],
            '축하': ['라넌큘러스', '장미', '거베라', '튤립'],
            '위로': ['수국', '라벤더', '화이트장미', '백합'],
            '슬픔': ['화이트장미', '백합', '수국', '라벤더']
        }
    
    def _setup_mood_mapping(self) -> Dict[str, List[str]]:
        """무드별 꽃 매핑"""
        return {
            '밝은': ['해바라기', '거베라', '튤립', '라넌큘러스'],
            '따뜻한': ['장미', '라넌큘러스', '거베라', '튤립'],
            '우아한': ['백합', '장미', '라넌큘러스', '수국'],
            '신선한': ['거베라', '튤립', '라넌큘러스', '해바라기'],
            '로맨틱': ['장미', '라넌큘러스', '튤립', '백합'],
            '차분한': ['수국', '라벤더', '화이트장미', '백합']
        }
    
    def smart_match(self, 
                   story: str, 
                   emotions: List[str] = None,
                   situations: List[str] = None,
                   moods: List[str] = None,
                   preferred_colors: List[str] = None) -> SmartMatchResult:
        """스마트 매칭 실행"""
        
        print(f"🧠 스마트 매칭 시작")
        print(f"   📝 스토리: {story[:50]}...")
        print(f"   🎨 선호 색상: {preferred_colors}")
        print(f"   😊 감정: {emotions}")
        print(f"   📍 상황: {situations}")
        print(f"   🌟 무드: {moods}")
        
        # 1단계: 색상 우선 매칭
        color_matches = self._match_by_color_priority(preferred_colors)
        if color_matches:
            print(f"   ✅ 색상 우선 매칭: {len(color_matches)}개")
            best_match = self._select_best_match(color_matches, situations, emotions, moods)
            return best_match
        
        # 2단계: 상황 기반 매칭
        situation_matches = self._match_by_situation(situations)
        if situation_matches:
            print(f"   ✅ 상황 기반 매칭: {len(situation_matches)}개")
            best_match = self._select_best_match(situation_matches, situations, emotions, moods)
            return best_match
        
        # 3단계: 감정 기반 매칭
        emotion_matches = self._match_by_emotion(emotions)
        if emotion_matches:
            print(f"   ✅ 감정 기반 매칭: {len(emotion_matches)}개")
            best_match = self._select_best_match(emotion_matches, situations, emotions, moods)
            return best_match
        
        # 4단계: 무드 기반 매칭
        mood_matches = self._match_by_mood(moods)
        if mood_matches:
            print(f"   ✅ 무드 기반 매칭: {len(mood_matches)}개")
            best_match = self._select_best_match(mood_matches, situations, emotions, moods)
            return best_match
        
        # 5단계: 기본 매칭
        return self._fallback_match()
    
    def _match_by_color_priority(self, preferred_colors: List[str]) -> List[Dict]:
        """색상 우선순위 기반 매칭"""
        if not preferred_colors:
            return []
        
        matches = []
        for color in preferred_colors:
            color_priority = self.color_priority.get(color.lower(), 0)
            if color_priority > 0:
                # 해당 색상의 꽃들 찾기
                color_flowers = self.flower_data[
                    self.flower_data['dominant_colors'].str.contains(color.lower(), na=False)
                ]
                
                for _, flower in color_flowers.iterrows():
                    matches.append({
                        'flower': flower,
                        'priority': color_priority,
                        'match_type': 'color',
                        'match_value': color
                    })
        
        return matches
    
    def _match_by_situation(self, situations: List[str]) -> List[Dict]:
        """상황 기반 매칭"""
        if not situations:
            return []
        
        matches = []
        for situation in situations:
            if situation in self.situation_mapping:
                recommended_flowers = self.situation_mapping[situation]
                for flower_name in recommended_flowers:
                    flower_data = self.flower_data[
                        self.flower_data['name_ko'].str.contains(flower_name, na=False)
                    ]
                    
                    for _, flower in flower_data.iterrows():
                        matches.append({
                            'flower': flower,
                            'priority': 8,  # 상황 매칭 우선순위
                            'match_type': 'situation',
                            'match_value': situation
                        })
        
        return matches
    
    def _match_by_emotion(self, emotions: List[str]) -> List[Dict]:
        """감정 기반 매칭"""
        if not emotions:
            return []
        
        matches = []
        for emotion in emotions:
            if emotion in self.emotion_mapping:
                recommended_flowers = self.emotion_mapping[emotion]
                for flower_name in recommended_flowers:
                    flower_data = self.flower_data[
                        self.flower_data['name_ko'].str.contains(flower_name, na=False)
                    ]
                    
                    for _, flower in flower_data.iterrows():
                        matches.append({
                            'flower': flower,
                            'priority': 6,  # 감정 매칭 우선순위
                            'match_type': 'emotion',
                            'match_value': emotion
                        })
        
        return matches
    
    def _match_by_mood(self, moods: List[str]) -> List[Dict]:
        """무드 기반 매칭"""
        if not moods:
            return []
        
        matches = []
        for mood in moods:
            if mood in self.mood_mapping:
                recommended_flowers = self.mood_mapping[mood]
                for flower_name in recommended_flowers:
                    flower_data = self.flower_data[
                        self.flower_data['name_ko'].str.contains(flower_name, na=False)
                    ]
                    
                    for _, flower in flower_data.iterrows():
                        matches.append({
                            'flower': flower,
                            'priority': 4,  # 무드 매칭 우선순위
                            'match_type': 'mood',
                            'match_value': mood
                        })
        
        return matches
    
    def _select_best_match(self, matches: List[Dict], situations: List[str], emotions: List[str], moods: List[str]) -> SmartMatchResult:
        """최적 매칭 선택"""
        if not matches:
            return self._fallback_match()
        
        # 우선순위 순으로 정렬
        matches.sort(key=lambda x: x['priority'], reverse=True)
        best_match = matches[0]
        flower = best_match['flower']
        
        # 매칭 상태 확인
        color_matched = best_match['match_type'] == 'color'
        situation_matched = best_match['match_type'] == 'situation'
        emotion_matched = best_match['match_type'] == 'emotion'
        mood_matched = best_match['match_type'] == 'mood'
        
        # 이미지 URL 생성
        image_url = self._generate_image_url(flower, best_match['match_value'])
        
        return SmartMatchResult(
            flower_name=flower.get('name_en', 'Unknown'),
            korean_name=flower.get('name_ko', 'Unknown'),
            scientific_name=flower.get('scientific_name', 'Unknown'),
            image_url=image_url,
            confidence=best_match['priority'] / 10.0,
            match_reason=f"{best_match['match_type']} 매칭: {best_match['match_value']}",
            color_matched=color_matched,
            situation_matched=situation_matched,
            emotion_matched=emotion_matched,
            mood_matched=mood_matched
        )
    
    def _generate_image_url(self, flower: pd.Series, match_value: str) -> str:
        """이미지 URL 생성"""
        try:
            # Supabase 이미지 URL 생성
            flower_name = flower.get('name_en', '').lower().replace(' ', '-')
            color = match_value.lower() if match_value else 'default'
            
            # 색상 코드 매핑
            color_mapping = {
                '핑크': 'pk', 'pink': 'pk',
                '빨강': 'rd', 'red': 'rd',
                '화이트': 'wh', 'white': 'wh',
                '옐로우': 'yl', 'yellow': 'yl',
                '퍼플': 'pu', 'purple': 'pu',
                '블루': 'bl', 'blue': 'bl'
            }
            
            color_code = color_mapping.get(color, 'wh')
            image_url = f"https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/{flower_name}-{color_code}.webp"
            
            return image_url
            
        except Exception as e:
            print(f"❌ 이미지 URL 생성 실패: {e}")
            return "/static/images/default_flower.webp"
    
    def _fallback_match(self) -> SmartMatchResult:
        """기본 매칭"""
        return SmartMatchResult(
            flower_name="Rose",
            korean_name="장미",
            scientific_name="Rosa",
            image_url="/static/images/default_flower.webp",
            confidence=0.5,
            match_reason="기본 매칭",
            color_matched=False,
            situation_matched=False,
            emotion_matched=False,
            mood_matched=False
        )

# 사용 예시
if __name__ == "__main__":
    matcher = SmartFlowerMatcher()
    
    # 테스트
    result = matcher.smart_match(
        story="친구가 이직해서 너무너무 축하해주고 싶어",
        emotions=["기쁨", "축하"],
        situations=["축하"],
        moods=["밝은"],
        preferred_colors=["핑크"]
    )
    
    print(f"매칭 결과: {result.korean_name}")
    print(f"이미지 URL: {result.image_url}")
    print(f"신뢰도: {result.confidence}")
    print(f"매칭 이유: {result.match_reason}")
