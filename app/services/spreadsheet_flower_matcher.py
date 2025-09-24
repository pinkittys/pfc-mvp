"""
구글 스프레드시트 데이터를 완전히 활용한 꽃 매칭 시스템
- 무드, 이모션, 컨텍스트, 꽃말(flower_language) 모두 고려
- Supabase 이미지 우선 매칭
"""
import json
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from app.services.supabase_image_fetcher import SupabaseImageFetcher

@dataclass
class SpreadsheetFlowerData:
    """스프레드시트 꽃 데이터"""
    uid: str
    flower_id: str
    flower_slug: str
    color_code: str
    name_ko: str
    name_en: str
    scientific_name: str
    is_main: bool
    base_color: str
    alt_colors: List[str]
    moods: List[str]
    emotions: List[str]
    contexts: List[str]
    season_months: str
    price_tier: str
    features: List[str]
    flower_language_short: str
    flower_language_long: str
    image_key: str
    image_url: str

@dataclass
class SpreadsheetMatchResult:
    """스프레드시트 매칭 결과"""
    flower_data: SpreadsheetFlowerData
    image_url: str
    confidence: float
    match_reason: str
    color_matched: bool
    mood_matched: bool
    emotion_matched: bool
    context_matched: bool
    flower_language_matched: bool

class SpreadsheetFlowerMatcher:
    """구글 스프레드시트 데이터 기반 꽃 매칭 시스템"""
    
    def __init__(self):
        self.flower_data = self._load_spreadsheet_data()
        self.image_fetcher = SupabaseImageFetcher()
        
        print(f"📊 스프레드시트 매칭 시스템 초기화 완료")
        print(f"   📋 꽃 데이터: {len(self.flower_data)}개")
    
    def _load_spreadsheet_data(self) -> List[SpreadsheetFlowerData]:
        """구글 스프레드시트 데이터 로드"""
        try:
            # 스프레드시트 데이터 로드 (오렌지 색상 꽃 포함)
            with open("data/spreadsheet_flowers.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            flowers = []
            for item in data:
                flower = SpreadsheetFlowerData(
                    uid=item.get('uid', ''),
                    flower_id=item.get('flower_id', ''),
                    flower_slug=item.get('flower_slug', ''),
                    color_code=item.get('color_code', ''),
                    name_ko=item.get('name_ko', ''),
                    name_en=item.get('name_en', ''),
                    scientific_name=item.get('scientific_name', ''),
                    is_main=item.get('is_main', True),
                    base_color=item.get('base_color', ''),
                    alt_colors=self._parse_list(item.get('alt_colors', '')),
                    moods=self._parse_list(item.get('moods', '')),
                    emotions=self._parse_list(item.get('emotions', '')),
                    contexts=self._parse_list(item.get('contexts', '')),
                    season_months=item.get('season_months', ''),
                    price_tier=item.get('price_tier', 'medium'),
                    features=self._parse_list(item.get('features', '')),
                    flower_language_short=item.get('flower_language_short', ''),
                    flower_language_long=item.get('flower_language_long', ''),
                    image_key=item.get('image_key', ''),
                    image_url=item.get('image_url', '')
                )
                flowers.append(flower)
            
            return flowers
            
        except Exception as e:
            print(f"❌ 스프레드시트 데이터 로드 실패: {e}")
            return []
    
    def _parse_list(self, data: str) -> List[str]:
        """문자열을 리스트로 파싱"""
        if not data:
            return []
        
        if isinstance(data, list):
            return data
        
        # 쉼표로 구분된 문자열을 리스트로 변환
        return [item.strip() for item in str(data).split(',') if item.strip()]
    
    def match_flower_with_explicit(self, story: str, emotions: List[str], situations: List[str], 
                                  moods: List[str], preferred_colors: List[str], 
                                  explicit_flowers: List[str]) -> Optional[SpreadsheetMatchResult]:
        """명시적 꽃 지정이 있을 때의 매칭 로직"""
        print(f"🎯 명시적 꽃 매칭 시작: {explicit_flowers}")
        
        # 1. 명시적 꽃 지정으로 필터링
        filtered_flowers = []
        for flower in self.flowers:
            if any(explicit_flower.lower() in flower.name_en.lower() for explicit_flower in explicit_flowers):
                filtered_flowers.append(flower)
        
        if not filtered_flowers:
            print(f"❌ 명시적 꽃 지정에 해당하는 꽃이 없음: {explicit_flowers}")
            return None
        
        print(f"✅ 명시적 꽃 필터링 결과: {len(filtered_flowers)}개")
        
        # 2. 4개 디멘션 기반 매칭 (감정, 상황, 무드, 컬러)
        best_match = None
        best_score = 0
        
        for flower in filtered_flowers:
            score = 0
            match_details = []
            
            # 감정 매칭
            emotion_matches = set(emotions) & set(flower.emotions)
            if emotion_matches:
                score += len(emotion_matches) * 3
                match_details.append(f"감정({', '.join(emotion_matches)})")
            
            # 상황 매칭
            situation_matches = set(situations) & set(flower.contexts)
            if situation_matches:
                score += len(situation_matches) * 3
                match_details.append(f"상황({', '.join(situation_matches)})")
            
            # 무드 매칭
            mood_matches = set(moods) & set(flower.moods)
            if mood_matches:
                score += len(mood_matches) * 2
                match_details.append(f"무드({', '.join(mood_matches)})")
            
            # 컬러 매칭
            color_matches = set(preferred_colors) & set([flower.base_color] + flower.alt_colors)
            if color_matches:
                score += len(color_matches) * 2
                match_details.append(f"컬러({', '.join(color_matches)})")
            
            # 꽃말 매칭 (보너스)
            if flower.flower_language_short and any(keyword in flower.flower_language_short for keyword in emotions + situations):
                score += 1
                match_details.append("꽃말")
            
            print(f"  {flower.name_ko}: {score}점 ({', '.join(match_details)})")
            
            if score > best_score:
                best_score = score
                best_match = flower
                best_match_details = match_details
        
        if best_match and best_score > 0:
            # 이미지 URL 가져오기
            image_url = self._get_flower_image_url(best_match)
            
            return SpreadsheetMatchResult(
                flower_data=best_match,
                image_url=image_url,
                confidence=min(best_score / 10.0, 1.0),  # 최대 1.0
                match_reason=f"명시적 꽃 지정 + 4개 디멘션 매칭: {', '.join(best_match_details)}",
                color_matched=bool(set(preferred_colors) & set([best_match.base_color] + best_match.alt_colors)),
                mood_matched=bool(set(moods) & set(best_match.moods)),
                emotion_matched=bool(set(emotions) & set(best_match.emotions)),
                context_matched=bool(set(situations) & set(best_match.contexts)),
                flower_language_matched=bool(best_match.flower_language_short)
            )
        
        print(f"❌ 명시적 꽃 매칭 실패: 점수 {best_score}")
        return None

    def match_flower(self, 
                    story: str,
                    emotions: List[str] = None,
                    situations: List[str] = None,
                    moods: List[str] = None,
                    preferred_colors: List[str] = None,
                    mentioned_flower: str = None) -> SpreadsheetMatchResult:
        """스프레드시트 데이터 기반 꽃 매칭"""
        
        print(f"📊 스프레드시트 매칭 시작")
        print(f"   📝 스토리: {story[:50]}...")
        print(f"   🎨 선호 색상: {preferred_colors}")
        print(f"   😊 감정: {emotions}")
        print(f"   📍 상황: {situations}")
        print(f"   🌟 무드: {moods}")
        print(f"   🌸 언급된 꽃: {mentioned_flower}")
        
        # 0단계: 언급된 꽃 우선 매칭 (최우선순위)
        if mentioned_flower:
            mentioned_matches = self._match_by_mentioned_flower(mentioned_flower, preferred_colors)
            if mentioned_matches:
                best_match = self._select_best_match(mentioned_matches, emotions, situations, moods, story)
                if best_match:
                    print(f"✅ 언급된 꽃 매칭 성공: {mentioned_flower}")
                    return best_match
        
        # 1단계: 색상 우선 매칭
        if preferred_colors:
            color_matches = self._match_by_color(preferred_colors)
            if color_matches:
                best_match = self._select_best_match(color_matches, emotions, situations, moods, story)
                if best_match:
                    return best_match
        
        # 2단계: 상황/컨텍스트 매칭
        if situations:
            context_matches = self._match_by_context(situations)
            if context_matches:
                best_match = self._select_best_match(context_matches, emotions, situations, moods, story)
                if best_match:
                    return best_match
        
        # 3단계: 감정 매칭
        if emotions:
            emotion_matches = self._match_by_emotion(emotions)
            if emotion_matches:
                best_match = self._select_best_match(emotion_matches, emotions, situations, moods, story)
                if best_match:
                    return best_match
        
        # 4단계: 무드 매칭
        if moods:
            mood_matches = self._match_by_mood(moods)
            if mood_matches:
                best_match = self._select_best_match(mood_matches, emotions, situations, moods, story)
                if best_match:
                    return best_match
        
        # 5단계: 꽃말 매칭
        flower_language_matches = self._match_by_flower_language(story)
        if flower_language_matches:
            best_match = self._select_best_match(flower_language_matches, emotions, situations, moods, story)
            if best_match:
                return best_match
        
        # 6단계: 기본 매칭
        return self._fallback_match()
    
    def _match_by_color(self, preferred_colors: List[str]) -> List[SpreadsheetFlowerData]:
        """색상 기반 매칭"""
        matches = []
        
        # 한글 색상명을 영문 코드로 매핑
        color_mapping = {
            '화이트': 'wh', '흰색': 'wh', 'white': 'wh',
            '핑크': 'pk', '분홍': 'pk', 'pink': 'pk',
            '레드': 'rd', '빨강': 'rd', 'red': 'rd',
            '옐로우': 'yl', '노랑': 'yl', 'yellow': 'yl',
            '오렌지': 'or', '주황': 'or', 'orange': 'or',
            '블루': 'bl', '파랑': 'bl', 'blue': 'bl',
            '퍼플': 'pu', '보라': 'pu', 'purple': 'pu',
            '라벤더': 'll', '연보라': 'll', 'lavender': 'll',
            '그린': 'gr', '초록': 'gr', 'green': 'gr'
        }
        
        # 한글 색상명을 영문 코드로 변환
        mapped_colors = []
        for color in preferred_colors:
            mapped_color = color_mapping.get(color, color)
            mapped_colors.append(mapped_color)
        
        print(f"   🎨 색상 매핑: {preferred_colors} → {mapped_colors}")
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 기본 색상 매칭 (영문 코드)
            if flower.base_color in mapped_colors:
                matches.append(flower)
                continue
            
            # 대체 색상 매칭 (영문 코드)
            if any(color in mapped_colors for color in flower.alt_colors):
                matches.append(flower)
                continue
        
        print(f"   🎨 색상 매칭: {len(matches)}개")
        return matches
    
    def _match_by_mentioned_flower(self, mentioned_flower: str, preferred_colors: List[str] = None) -> List[SpreadsheetFlowerData]:
        """언급된 꽃 기반 매칭 (최우선순위)"""
        matches = []
        
        # 꽃 이름 매핑 (한글 -> 영문)
        flower_mapping = {
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
        
        # 언급된 꽃 이름을 영문으로 변환
        mapped_flower = flower_mapping.get(mentioned_flower, mentioned_flower.lower())
        
        print(f"   🌸 언급된 꽃 매핑: {mentioned_flower} -> {mapped_flower}")
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 꽃 이름 매칭 (영문 slug 기준)
            if flower.flower_slug == mapped_flower:
                # 색상이 지정된 경우 해당 색상만 매칭
                if preferred_colors:
                    # 한글 색상명을 영문 코드로 매핑
                    color_mapping = {
                        '화이트': 'wh', '흰색': 'wh', 'white': 'wh',
                        '핑크': 'pk', '분홍': 'pk', 'pink': 'pk',
                        '레드': 'rd', '빨강': 'rd', 'red': 'rd',
                        '옐로우': 'yl', '노랑': 'yl', 'yellow': 'yl',
                        '오렌지': 'or', '주황': 'or', 'orange': 'or',
                        '블루': 'bl', '파랑': 'bl', 'blue': 'bl',
                        '퍼플': 'pu', '보라': 'pu', 'purple': 'pu',
                        '라벤더': 'll', '연보라': 'll', 'lavender': 'll',
                        '그린': 'gr', '초록': 'gr', 'green': 'gr'
                    }
                    
                    mapped_colors = [color_mapping.get(color, color) for color in preferred_colors]
                    
                    # 지정된 색상과 일치하는 경우만 매칭
                    if flower.base_color in mapped_colors:
                        matches.append(flower)
                        print(f"   ✅ 언급된 꽃+색상 매칭: {flower.name_ko} ({flower.base_color})")
                    else:
                        # 지정된 색상이 없으면 사용 가능한 색상으로 매칭
                        matches.append(flower)
                        print(f"   ⚠️ 언급된 꽃 매칭 (색상 불일치): {flower.name_ko} ({flower.base_color}) - 요청: {preferred_colors}")
                else:
                    # 색상이 지정되지 않은 경우 모든 색상 매칭
                    matches.append(flower)
                    print(f"   ✅ 언급된 꽃 매칭: {flower.name_ko} ({flower.base_color})")
        
        print(f"   🌸 언급된 꽃 매칭: {len(matches)}개")
        return matches
    
    def _match_by_context(self, situations: List[str]) -> List[SpreadsheetFlowerData]:
        """상황/컨텍스트 기반 매칭 - 강화된 매칭 로직"""
        matches = []
        
        # 특별한 상황 매칭 규칙 (우선순위 높음)
        special_situation_rules = {
            "새로운 시작": ["프리지아", "해바라기"],
            "축하": ["프리지아", "해바라기", "장미"],
            "성공": ["프리지아", "해바라기"],
            "취업": ["프리지아", "해바라기"],
            "합격": ["프리지아", "해바라기"],
            "졸업": ["프리지아", "해바라기"],
            "승진": ["프리지아", "해바라기"]
        }
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 특별한 상황 매칭 (우선순위 높음)
            for situation in situations:
                for special_keyword, preferred_flowers in special_situation_rules.items():
                    if special_keyword in situation:
                        if flower.name_ko in preferred_flowers:
                            matches.append(flower)
                            print(f"   🎯 특별 상황 매칭: {situation} → {flower.name_ko}")
                            break
                
                # 일반 컨텍스트 매칭
                if any(context in situation for context in flower.contexts):
                    matches.append(flower)
                    break
        
        print(f"   📍 상황 매칭: {len(matches)}개")
        return matches
    
    def _match_by_emotion(self, emotions: List[str]) -> List[SpreadsheetFlowerData]:
        """감정 기반 매칭"""
        matches = []
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 감정 매칭
            for emotion in emotions:
                if any(flower_emotion in emotion for flower_emotion in flower.emotions):
                    matches.append(flower)
                    break
        
        print(f"   😊 감정 매칭: {len(matches)}개")
        return matches
    
    def _match_by_mood(self, moods: List[str]) -> List[SpreadsheetFlowerData]:
        """무드 기반 매칭"""
        matches = []
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 무드 매칭
            for mood in moods:
                if any(flower_mood in mood for flower_mood in flower.moods):
                    matches.append(flower)
                    break
        
        print(f"   🌟 무드 매칭: {len(matches)}개")
        return matches
    
    def _match_by_flower_language(self, story: str) -> List[SpreadsheetFlowerData]:
        """꽃말 기반 매칭 - 강화된 매칭 로직"""
        matches = []
        
        # 스토리에서 키워드 추출
        story_keywords = self._extract_story_keywords(story)
        
        # 특별한 꽃말 매칭 규칙 (우선순위 높음)
        special_flower_language_rules = {
            "새로운 시작": ["프리지아"],
            "축하": ["프리지아", "해바라기"],
            "성공": ["프리지아", "해바라기"],
            "취업": ["프리지아"],
            "합격": ["프리지아"],
            "졸업": ["프리지아"],
            "승진": ["프리지아"]
        }
        
        for flower in self.flower_data:
            if not flower.is_main:
                continue
            
            # 특별한 꽃말 매칭 (우선순위 높음)
            for keyword in story_keywords:
                for special_keyword, preferred_flowers in special_flower_language_rules.items():
                    if special_keyword in keyword:
                        if flower.name_ko in preferred_flowers:
                            matches.append(flower)
                            print(f"   🎯 특별 꽃말 매칭: {keyword} → {flower.name_ko}")
                            break
            
            # 일반 꽃말 매칭
            flower_language = f"{flower.flower_language_short} {flower.flower_language_long}"
            
            for keyword in story_keywords:
                if keyword in flower_language:
                    matches.append(flower)
                    break
        
        print(f"   💬 꽃말 매칭: {len(matches)}개")
        return matches
    
    def _extract_story_keywords(self, story: str) -> List[str]:
        """스토리에서 키워드 추출 - 강화된 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용 가능)
        keywords = []
        
        # 감정 키워드
        emotion_keywords = ["사랑", "감사", "기쁨", "위로", "격려", "희망", "축하", "슬픔", "그리움"]
        for keyword in emotion_keywords:
            if keyword in story:
                keywords.append(keyword)
        
        # 상황 키워드 (강화)
        situation_keywords = [
            "생일", "기념일", "졸업", "승진", "합격", "고백", "결혼", "출산", "병문안",
            "새로운 시작", "취업", "성공", "파티", "잔치", "기념", "특별한날"
        ]
        for keyword in situation_keywords:
            if keyword in story:
                keywords.append(keyword)
        
        # 특별한 키워드 조합 (우선순위 높음)
        special_combinations = [
            "새로운 시작을 축하", "취업 성공", "합격 축하", "졸업 축하", "승진 축하"
        ]
        for combination in special_combinations:
            if combination in story:
                keywords.append(combination)
        
        return keywords
    
    def _select_best_match(self, 
                          candidates: List[SpreadsheetFlowerData],
                          emotions: List[str],
                          situations: List[str],
                          moods: List[str],
                          story: str) -> Optional[SpreadsheetMatchResult]:
        """최적 매칭 선택 (명확한 우선순위 시스템)"""
        if not candidates:
            return None
        
        print(f"🔍 후보 꽃들: {[f.flower_data.name_ko for f in candidates] if hasattr(candidates[0], 'flower_data') else [f.name_ko for f in candidates]}")
        
        best_flower = None
        best_score = 0
        best_reason = ""
        
        for flower in candidates:
            score = 0
            reasons = []
            
            # 1. 색상 매칭 점수 (최우선)
            if emotions and any(color in [flower.base_color] + flower.alt_colors for color in emotions):
                score += 10  # 색상 매칭 최우선
                reasons.append("색상 정확 매칭")
            
            # 2. 상황 매칭 점수 (두 번째 우선순위) - 강화
            if situations:
                # 특별한 상황 매칭 (우선순위 높음)
                special_situation_rules = {
                    "새로운 시작": ["프리지아", "해바라기"],
                    "축하": ["프리지아", "해바라기", "장미"],
                    "성공": ["프리지아", "해바라기"],
                    "취업": ["프리지아", "해바라기"],
                    "합격": ["프리지아", "해바라기"],
                    "졸업": ["프리지아", "해바라기"],
                    "승진": ["프리지아", "해바라기"]
                }
                
                for situation in situations:
                    for special_keyword, preferred_flowers in special_situation_rules.items():
                        if special_keyword in situation and flower.name_ko in preferred_flowers:
                            score += 12  # 특별 상황 매칭 최우선
                            reasons.append(f"특별 상황 매칭({special_keyword})")
                            break
                
                # 일반 상황 매칭
                if any(situation in flower.contexts for situation in situations):
                    score += 8
                    reasons.append("상황 매칭")
            
            # 3. 감정 매칭 점수 (세 번째 우선순위)
            if emotions and any(emotion in flower.emotions for emotion in emotions):
                score += 6
                reasons.append("감정 매칭")
            
            # 4. 꽃말 매칭 점수 (네 번째 우선순위) - 강화
            story_keywords = self._extract_story_keywords(story)
            flower_language = f"{flower.flower_language_short} {flower.flower_language_long}"
            
            # 특별한 꽃말 매칭 (우선순위 높음)
            special_flower_language_rules = {
                "새로운 시작": ["프리지아"],
                "축하": ["프리지아", "해바라기"],
                "성공": ["프리지아", "해바라기"],
                "취업": ["프리지아"],
                "합격": ["프리지아"],
                "졸업": ["프리지아"],
                "승진": ["프리지아"]
            }
            
            for keyword in story_keywords:
                for special_keyword, preferred_flowers in special_flower_language_rules.items():
                    if special_keyword in keyword and flower.name_ko in preferred_flowers:
                        score += 6  # 특별 꽃말 매칭 우선순위 높음
                        reasons.append(f"특별 꽃말 매칭({special_keyword})")
                        break
            
            # 일반 꽃말 매칭
            if any(keyword in flower_language for keyword in story_keywords):
                score += 4
                reasons.append("꽃말 매칭")
            
            # 5. 무드 매칭 점수 (다섯 번째 우선순위)
            if moods and any(mood in flower.moods for mood in moods):
                score += 2
                reasons.append("무드 매칭")
            
            # 6. 계절 적합성 점수 (여섯 번째 우선순위)
            season_score = self._calculate_season_score(flower)
            score += season_score
            if season_score > 0:
                reasons.append("계절 적합성")
            
            # 7. 꽃의 인기도 점수 (일곱 번째 우선순위)
            popularity_score = self._calculate_popularity_score(flower)
            score += popularity_score
            if popularity_score > 0:
                reasons.append("인기도")
            
            print(f"   📊 {flower.name_ko}: {score:.1f}점 ({', '.join(reasons)})")
            
            if score > best_score:
                best_score = score
                best_flower = flower
                best_reason = ", ".join(reasons)
        
        if best_flower:
            # 꽃 이름과 색상이 정확히 일치하는 이미지 찾기
            image_match = self.image_fetcher.find_image(best_flower.name_ko, best_flower.base_color)
            if image_match:
                image_url = image_match.url
                print(f"✅ 정확한 꽃+색상 매칭: {best_flower.name_ko} ({best_flower.base_color}) → {image_match.filename}")
            else:
                # 폴백: 스프레드시트 URL 사용
                image_url = best_flower.image_url
                print(f"⚠️ 정확한 매칭 실패, 스프레드시트 URL 사용: {best_flower.name_ko} ({best_flower.base_color})")
            
            return SpreadsheetMatchResult(
                flower_data=best_flower,
                image_url=image_url,
                confidence=best_score / 10.0,
                match_reason=best_reason,
                color_matched=True,
                mood_matched=True,
                emotion_matched=True,
                context_matched=True,
                flower_language_matched=True
            )
        
        return None
    
    def _fallback_match(self) -> SpreadsheetMatchResult:
        """기본 매칭"""
        # 기본적으로 첫 번째 꽃 반환
        if self.flower_data:
            flower = self.flower_data[0]
            
            # Supabase 이미지 매칭 (실제 Storage URL 사용)
            image_match = self.image_fetcher.find_image(flower.name_ko, flower.base_color)
            if image_match:
                image_url = image_match.url
                print(f"✅ 기본 매칭 - Supabase Storage: {image_match.filename}")
            else:
                # 폴백: 스프레드시트 URL 사용
                image_url = flower.image_url
                print(f"⚠️ 기본 매칭 - 스프레드시트 URL: {flower.name_ko}")
            
            return SpreadsheetMatchResult(
                flower_data=flower,
                image_url=image_url,
                confidence=0.5,
                match_reason="기본 매칭",
                color_matched=False,
                mood_matched=False,
                emotion_matched=False,
                context_matched=False,
                flower_language_matched=False
            )
        
        # 빈 결과 반환
        return None
    
    def _calculate_season_score(self, flower: SpreadsheetFlowerData) -> float:
        """계절 적합성 점수 계산"""
        from datetime import datetime
        
        current_month = datetime.now().month
        
        # 계절 매핑
        season_mapping = {
            "Spring": [3, 4, 5],
            "Summer": [6, 7, 8], 
            "Fall": [9, 10, 11],
            "Winter": [12, 1, 2]
        }
        
        # 꽃의 계절 정보 파싱
        season_info = flower.season_months
        if not season_info:
            return 0
        
        # "Spring/Summer 03-08" 형식 파싱
        if "/" in season_info:
            seasons = season_info.split("/")[0].split(" ")
            if len(seasons) > 0:
                season = seasons[0]
                if season in season_mapping and current_month in season_mapping[season]:
                    return 1.0
        
        # "All Season 01-12" 형식
        if "All Season" in season_info:
            return 0.5
        
        return 0
    
    def _calculate_popularity_score(self, flower: SpreadsheetFlowerData) -> float:
        """꽃의 인기도 점수 계산"""
        # 인기 꽃들 (실제 데이터 기반)
        popular_flowers = {
            "장미": 3.0,
            "카네이션": 2.5,
            "해바라기": 2.0,
            "수국": 1.5,
            "용담": 1.0,
            "라넌큘러스": 1.5,
            "알스트로메리아": 1.0,
            "리시안셔스": 1.0,
            "프리지아": 1.0,
            "다알리아": 1.0
        }
        
        return popular_flowers.get(flower.name_ko, 0.5)

# 사용 예시
if __name__ == "__main__":
    matcher = SpreadsheetFlowerMatcher()
    
    # 테스트
    result = matcher.match_flower(
        story="친구가 번아웃으로 힘들어해요. 친구에게 힘이되는 선물을 하고 싶어요.",
        emotions=["위로"],
        situations=["번아웃"],
        moods=["차분한"],
        preferred_colors=["블루"]
    )
    
    if result:
        print(f"매칭 결과: {result.flower_data.name_ko}")
        print(f"이미지 URL: {result.image_url}")
        print(f"신뢰도: {result.confidence}")
        print(f"매칭 이유: {result.match_reason}")
    else:
        print("매칭 실패")
