"""
위로와 슬픔 상황에 특화된 꽃 매칭 로직
"""

from typing import Dict, List, Tuple
import re


class ComfortFlowerMatcher:
    """위로/슬픔 상황 특화 꽃 매칭"""
    
    def __init__(self):
        # 위로/슬픔 상황 키워드
        self.comfort_keywords = [
            "무지개다리를 건넌", "돌아가신", "별이 된", "위로", "슬픔", "이별", 
            "반려견", "반려동물", "애도", "추모", "고인", "상주", "장례", "별세",
            "번아웃", "지쳐", "힘들", "스트레스", "피곤", "우울", "불안", "걱정"
        ]
        
        # 위로 관련 꽃말 키워드
        self.comfort_flower_keywords = [
            "희망", "위로", "치유", "평화", "인연", "새로운 시작", 
            "평온", "차분", "안정", "편안", "포근", "따뜻함"
        ]
        
        # 위로에 적합한 색상
        self.comfort_colors = ["블루", "화이트", "라벤더", "퍼플", "아이보리", "크림"]
        
        # 위로에 부적합한 화려한 색상
        self.bright_colors = ["레드", "오렌지", "핑크", "옐로우", "골드"]
        
        # 위로에 특화된 꽃들
        self.comfort_flowers = {
            "마거리트 데이지": {
                "meanings": ["희망", "치유", "기쁨"],
                "colors": ["화이트", "아이보리"],
                "mood": "따뜻한",
                "bonus": 2.5
            },
            "젠티아나": {
                "meanings": ["위로받는", "희망찬"],
                "colors": ["블루"],
                "mood": "차분한",
                "bonus": 2.3
            },
            "베로니카": {
                "meanings": ["희망", "평화"],
                "colors": ["퍼플"],
                "mood": "평온한",
                "bonus": 2.2
            },
            "스카비오사": {
                "meanings": ["희망", "평화"],
                "colors": ["블루", "퍼플"],
                "mood": "차분한",
                "bonus": 2.1
            },
            "리시안셔스": {
                "meanings": ["희망", "새로운 시작"],
                "colors": ["화이트", "아이보리"],
                "mood": "순수한",
                "bonus": 2.0
            },
            "튤립": {
                "meanings": ["희망", "새로운 시작"],
                "colors": ["화이트", "아이보리"],
                "mood": "순수한",
                "bonus": 1.8
            },
            "알스트로메리아": {
                "meanings": ["희망", "우정"],
                "colors": ["화이트", "아이보리"],
                "mood": "따뜻한",
                "bonus": 1.7
            }
        }
    
    def is_comfort_situation(self, story: str) -> bool:
        """위로/슬픔 상황인지 판단"""
        story_lower = story.lower()
        return any(keyword in story_lower for keyword in self.comfort_keywords)
    
    def apply_comfort_bonus(self, flower_data: Dict, story: str, base_score: float) -> Tuple[float, List[str]]:
        """위로/슬픔 상황 보너스 적용"""
        if not self.is_comfort_situation(story):
            return base_score, []
        
        score = base_score
        applied_bonuses = []
        
        flower_name = flower_data.get('korean_name', '')
        flower_color = flower_data.get('color', '')
        
        # 1. 위로 특화 꽃 보너스
        if flower_name in self.comfort_flowers:
            flower_info = self.comfort_flowers[flower_name]
            score *= flower_info['bonus']
            applied_bonuses.append(f"🕊️ 위로 특화 꽃: {flower_name} (x{flower_info['bonus']})")
        
        # 2. 위로 관련 꽃말 보너스
        flower_meanings = flower_data.get('flower_meanings', {})
        all_meanings = []
        all_meanings.extend(flower_meanings.get('meanings', flower_meanings.get('primary', [])))
        all_meanings.extend(flower_meanings.get('moods', flower_meanings.get('secondary', [])))
        all_meanings.extend(flower_meanings.get('emotions', flower_meanings.get('other', [])))
        
        comfort_meaning_count = sum(1 for meaning in all_meanings 
                                  if any(keyword in str(meaning) for keyword in self.comfort_flower_keywords))
        
        if comfort_meaning_count > 0:
            bonus_multiplier = 1.0 + (comfort_meaning_count * 0.3)
            score *= bonus_multiplier
            applied_bonuses.append(f"💙 위로 꽃말 보너스: {comfort_meaning_count}개 (x{bonus_multiplier:.1f})")
        
        # 3. 위로에 적합한 색상 보너스
        if flower_color in self.comfort_colors:
            score *= 1.8
            applied_bonuses.append(f"💙 위로 색상 보너스: {flower_color} (x1.8)")
        
        # 4. 화려한 색상 페널티
        if flower_color in self.bright_colors:
            score *= 0.3
            applied_bonuses.append(f"❌ 화려한 색상 페널티: {flower_color} (x0.3)")
        
        # 5. 무지개 관련 키워드가 있을 때 특별 처리
        if "무지개" in story.lower():
            # 무지개색상 꽃에 강한 페널티
            rainbow_colors = ["레드", "오렌지", "옐로우", "그린", "블루", "퍼플"]
            if flower_color in rainbow_colors:
                score *= 0.1
                applied_bonuses.append(f"🌈 무지개색상 강한 페널티: {flower_color} (x0.1)")
        
        return score, applied_bonuses
    
    def get_comfort_recommendations(self, story: str, available_flowers: List[Dict]) -> List[Dict]:
        """위로/슬픔 상황에 적합한 꽃 추천"""
        if not self.is_comfort_situation(story):
            return []
        
        recommendations = []
        
        for flower in available_flowers:
            flower_name = flower.get('korean_name', '')
            
            if flower_name in self.comfort_flowers:
                flower_info = self.comfort_flowers[flower_name]
                recommendations.append({
                    'flower': flower,
                    'reason': f"{flower_name}은 {', '.join(flower_info['meanings'])}의 의미를 가지고 있어 위로에 적합합니다.",
                    'color_recommendation': flower_info['colors'],
                    'mood': flower_info['mood'],
                    'priority': 'high'
                })
        
        return recommendations
    
    def filter_inappropriate_colors(self, story: str, color_keywords: List[str]) -> List[str]:
        """위로/슬픔 상황에서 부적절한 색상 필터링"""
        if not self.is_comfort_situation(story):
            return color_keywords
        
        filtered_colors = []
        story_lower = story.lower()
        
        # 무지개 관련 키워드가 있을 때 강력한 필터링
        if "무지개" in story_lower:
            # 무지개색상 완전 제거, 위로에 적합한 색상만 사용
            for color in self.comfort_colors:
                if color not in filtered_colors:
                    filtered_colors.append(color)
            return filtered_colors[:2]  # 최대 2개만
        
        # 일반적인 위로 상황에서는 위로에 적합한 색상 우선
        for color in color_keywords:
            if color in self.comfort_colors:
                if color not in filtered_colors:
                    filtered_colors.insert(0, color)  # 앞에 추가
            elif color not in self.bright_colors:
                # 화려하지 않은 색상은 허용
                if color not in filtered_colors:
                    filtered_colors.append(color)
        
        # 위로에 적합한 색상이 없으면 기본 색상 추가
        if not filtered_colors:
            filtered_colors = ["블루", "화이트"]
        
        return filtered_colors[:3]  # 최대 3개 색상만 반환
