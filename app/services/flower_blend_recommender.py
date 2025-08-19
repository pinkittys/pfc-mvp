"""
꽃 구성 추천 서비스 (MVP 버전 - 예산 제외)
"""
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path
from app.models.schemas import FlowerMatch

@dataclass
class FlowerBlend:
    """꽃 구성"""
    main_flowers: List[str]
    sub_flowers: List[str]
    filler_flowers: List[str]
    line_flowers: List[str]
    foliage: List[str]
    total_flowers: int
    color_harmony: str
    style_description: str
    color_theme: List[str] = None

@dataclass
class BlendRecommendation:
    """구성 추천 결과"""
    blend: FlowerBlend
    emotion_fit: float
    color_fit: float
    total_score: float
    reasoning: str

class FlowerBlendRecommender:
    def __init__(self):
        self.blend_guide = self._load_blend_guide()
        self.flower_roles = self._load_flower_roles()
    
    def _load_blend_guide(self) -> Dict[str, Any]:
        """꽃 구성 가이드 로드"""
        guide_path = Path("data/flower_blend_guide.json")
        if guide_path.exists():
            with open(guide_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_flower_roles(self) -> Dict[str, str]:
        """꽃별 역할 매핑"""
        return {
            # 메인 꽃들 (focal=1)
            "장미": "main",
            "작약": "main", 
            "거베라": "main",
            "튤립": "main",
            
            # 서브 꽃들 (중간 크기)
            "리시안셔스": "sub",
            "다알리아": "sub",
            "백합": "sub",
            "수국": "sub",
            
            # 필러 꽃들 (작은 꽃)
            "마가렛": "filler",
            "스카비오사": "filler",
            "부바르디아": "filler",
            "천일홍": "filler",
            
            # 라인 꽃들 (높이감)
            "골든볼": "line",
            "스토크": "line",
            "맨드라미": "line",
            
            # 그린 소재
            "목화": "foliage"
        }
    
    def create_flower_blend(self, flower_matches: List[FlowerMatch], 
                           color_preference: List[str] = None) -> List[BlendRecommendation]:
        """꽃 구성 추천 생성 (MVP - 예산 제외)"""
        recommendations = []
        
        # 표준 구성 크기 (예산 무관)
        size_config = {
            "main_count": 1,
            "sub_count": 2,
            "filler_count": 2,
            "line_count": 1,
            "foliage_count": 1
        }
        
        blend = self._create_blend_from_matches(flower_matches, size_config, color_preference)
        if blend:
            recommendation = self._evaluate_blend(blend, flower_matches, color_preference)
            recommendations.append(recommendation)
        
        # 최고 점수 구성만 반환
        return recommendations[:1] if recommendations else []
    
    def _create_blend_from_matches(self, flower_matches: List[FlowerMatch], 
                                  size_config: Dict[str, int], 
                                  color_preference: List[str] = None) -> FlowerBlend:
        """매칭된 꽃들로 구성 생성"""
        if not flower_matches:
            return None
        
        # 역할별로 꽃 분류
        role_flowers = {
            "main": [],
            "sub": [],
            "filler": [],
            "line": [],
            "foliage": []
        }
        
        for match in flower_matches:
            role = self.flower_roles.get(match.flower_name, "filler")
            role_flowers[role].append(match)
        
        # 메인 꽃 선택 (전체 점수가 가장 높은 꽃을 메인으로 선택)
        all_flowers = []
        for role, flowers in role_flowers.items():
            all_flowers.extend(flowers)
        
        if all_flowers:
            # 전체 점수가 가장 높은 꽃을 메인으로 선택
            best_flower = max(all_flowers, key=lambda x: x.match_score)
            main_flowers = [best_flower.flower_name]
            
            # 선택된 꽃을 해당 역할에서 제거
            for role, flowers in role_flowers.items():
                role_flowers[role] = [f for f in flowers if f.flower_name != best_flower.flower_name]
        else:
            main_flowers = []
        
        # 서브 꽃 선택
        sub_flowers = []
        if role_flowers["sub"]:
            sub_flowers = [f.flower_name for f in role_flowers["sub"][:size_config["sub_count"]]]
        
        # 필러 꽃 선택
        filler_flowers = []
        if role_flowers["filler"]:
            filler_flowers = [f.flower_name for f in role_flowers["filler"][:size_config["filler_count"]]]
        
        # 라인 꽃 선택
        line_flowers = []
        if role_flowers["line"]:
            line_flowers = [f.flower_name for f in role_flowers["line"][:size_config["line_count"]]]
        
        # 그린 소재 선택
        foliage = []
        if role_flowers["foliage"]:
            foliage = [f.flower_name for f in role_flowers["foliage"][:size_config["foliage_count"]]]
        
        # 컬러 테마 결정
        color_theme = self._determine_color_theme(main_flowers + sub_flowers + filler_flowers, color_preference)
        
        # 스타일 설명 생성
        style_description = self._generate_style_description(main_flowers, color_theme)
        
        # 컬러 하모니 평가
        color_harmony = self._evaluate_color_harmony(color_theme)
        
        total_flowers = len(main_flowers) + len(sub_flowers) + len(filler_flowers) + len(line_flowers) + len(foliage)
        
        return FlowerBlend(
            main_flowers=main_flowers,
            sub_flowers=sub_flowers,
            filler_flowers=filler_flowers,
            line_flowers=line_flowers,
            foliage=foliage,
            total_flowers=total_flowers,
            color_harmony=color_harmony,
            style_description=style_description,
            color_theme=color_theme
        )
    
    def _evaluate_blend(self, blend: FlowerBlend, flower_matches: List[FlowerMatch], 
                       color_preference: List[str] = None) -> BlendRecommendation:
        """구성 평가"""
        # 감정 적합도 (매칭 점수 기반)
        emotion_fit = 0.0
        if blend.main_flowers:
            main_match = next((m for m in flower_matches if m.flower_name == blend.main_flowers[0]), None)
            if main_match:
                emotion_fit = main_match.match_score
        
        # 컬러 적합도
        color_fit = self._calculate_color_fit(blend.color_theme, color_preference)
        
        # 총점 계산
        total_score = (emotion_fit * 0.7) + (color_fit * 0.3)
        
        # 추론 설명
        reasoning = f"메인 꽃 {blend.main_flowers[0] if blend.main_flowers else 'Unknown'}을 중심으로 한 {blend.total_flowers}개 꽃 구성"
        
        return BlendRecommendation(
            blend=blend,
            emotion_fit=emotion_fit,
            color_fit=color_fit,
            total_score=total_score,
            reasoning=reasoning
        )
    
    def _determine_color_theme(self, flowers: List[str], color_preference: List[str] = None) -> List[str]:
        """컬러 테마 결정"""
        # 기본 컬러 매핑
        flower_colors = {
            "장미": ["레드", "핑크", "화이트"],
            "수국": ["블루", "핑크", "화이트"],
            "거베라": ["레드", "핑크", "옐로우"],
            "튤립": ["레드", "핑크", "옐로우"],
            "작약": ["핑크", "화이트"],
            "리시안셔스": ["화이트", "핑크"],
            "마가렛": ["화이트", "핑크"],
            "부바르디아": ["화이트", "핑크"],
            "스카비오사": ["블루", "화이트"],
            "골든볼": ["옐로우"],
            "스토크": ["퍼플", "화이트"],
            "맨드라미": ["레드", "핑크"],
            "천일홍": ["퍼플", "핑크"],
            "목화": ["화이트"]
        }
        
        theme_colors = []
        for flower in flowers:
            if flower in flower_colors:
                theme_colors.extend(flower_colors[flower])
        
        # 중복 제거
        theme_colors = list(set(theme_colors))
        
        # 선호 컬러가 있으면 우선 적용
        if color_preference:
            theme_colors = color_preference[:3] + [c for c in theme_colors if c not in color_preference]
        
        return theme_colors[:3]  # 최대 3개 컬러
    
    def _calculate_color_fit(self, theme_colors: List[str], preferred_colors: List[str] = None) -> float:
        """컬러 적합도 계산"""
        if not preferred_colors:
            return 0.8  # 기본 점수
        
        if not theme_colors:
            return 0.5
        
        # 선호 컬러와 테마 컬러 매칭
        matches = 0
        for pref_color in preferred_colors:
            if any(pref_color in theme_color or theme_color in pref_color for theme_color in theme_colors):
                matches += 1
        
        return min(1.0, matches / len(preferred_colors))
    
    def _evaluate_color_harmony(self, colors: List[str]) -> str:
        """컬러 하모니 평가"""
        if not colors:
            return "중성"
        
        warm_colors = ["레드", "핑크", "오렌지", "옐로우"]
        cool_colors = ["블루", "퍼플", "그린"]
        
        warm_count = sum(1 for c in colors if any(w in c for w in warm_colors))
        cool_count = sum(1 for c in colors if any(cool in c for cool in cool_colors))
        
        if warm_count > cool_count:
            return "따뜻한"
        elif cool_count > warm_count:
            return "시원한"
        else:
            return "균형잡힌"
    
    def _generate_style_description(self, main_flowers: List[str], color_theme: List[str]) -> str:
        """스타일 설명 생성"""
        if not main_flowers:
            return "클래식한 꽃다발"
        
        main_flower = main_flowers[0]
        style_map = {
            "장미": "로맨틱한",
            "수국": "우아한",
            "거베라": "활기찬",
            "튤립": "신선한",
            "작약": "고급스러운",
            "리시안셔스": "세련된"
        }
        
        style = style_map.get(main_flower, "아름다운")
        return f"{style} {main_flower} 꽃다발"
