"""
동적 가중치를 적용한 고급 추천 엔진
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from .data_loader import load_templates, load_flowers
from .llm_keyword_extractor import ExtractedInfo

@dataclass
class AdvancedBundle:
    id: str
    template_id: str | None
    name: str
    main_flowers: List[str]
    sub_flowers: List[str]
    color_theme: List[str]
    estimated_price: int
    reason: str
    score: float = 0.0
    score_breakdown: Dict[str, float] = None

class AdvancedRecommender:
    def __init__(self):
        self.templates = load_templates()
        self.flowers = load_flowers()
    
    def _calculate_dynamic_weights(self, extracted_info: ExtractedInfo) -> Dict[str, float]:
        """선호도 강도에 따른 동적 가중치 계산"""
        base_weights = {
            "color": 1.0,
            "emotion": 2.0,
            "mood": 1.5,
            "situation": 2.0,
            "season": 0.5,
            "budget": 1.0
        }
        
        # 선호도 강도에 따른 가중치 조정
        dynamic_weights = {}
        
        # 색상 가중치: 명시적 선호도가 높을수록 가중치 증가
        color_weight = base_weights["color"] * (1 + extracted_info.color_intensity)
        dynamic_weights["color"] = color_weight
        
        # 감정 가중치: 감정 표현이 강할수록 가중치 증가
        emotion_weight = base_weights["emotion"] * (1 + extracted_info.emotion_intensity)
        dynamic_weights["emotion"] = emotion_weight
        
        # 무드 가중치: 무드 표현이 강할수록 가중치 증가
        mood_weight = base_weights["mood"] * (1 + extracted_info.mood_intensity)
        dynamic_weights["mood"] = mood_weight
        
        # 상황 가중치: 상황이 명확할수록 가중치 증가
        situation_weight = base_weights["situation"] * (1 + extracted_info.situation_intensity)
        dynamic_weights["situation"] = situation_weight
        
        # 계절 가중치: 계절 정보가 있으면 가중치 적용
        dynamic_weights["season"] = base_weights["season"] if extracted_info.season else 0.0
        
        # 예산 가중치: 기본값 유지
        dynamic_weights["budget"] = base_weights["budget"]
        
        return dynamic_weights
    
    def _score_template_advanced(self, template: Dict[str, Any], 
                                extracted_info: ExtractedInfo,
                                weights: Dict[str, float]) -> Dict[str, float]:
        """고급 템플릿 스코어링"""
        score_breakdown = {}
        total_score = 0.0
        
        # 1. 색상 매칭 (동적 가중치 적용)
        if weights["color"] > 0:
            template_colors = set((template.get("color_theme") or "").lower().split("|"))
            extracted_colors = set(extracted_info.color_direction or [])
            
            color_score = 0.0
            if extracted_colors and template_colors:
                color_match = extracted_colors & template_colors
                if color_match:
                    color_score = len(color_match) / len(extracted_colors)
            
            weighted_color_score = color_score * weights["color"]
            score_breakdown["color"] = weighted_color_score
            total_score += weighted_color_score
        
        # 2. 감정 매칭 (꽃의 상징성 기반)
        if weights["emotion"] > 0 and extracted_info.emotion:
            emotion_score = self._calculate_emotion_match(template, extracted_info.emotion)
            weighted_emotion_score = emotion_score * weights["emotion"]
            score_breakdown["emotion"] = weighted_emotion_score
            total_score += weighted_emotion_score
        
        # 3. 무드 매칭
        if weights["mood"] > 0 and extracted_info.mood:
            mood_score = self._calculate_mood_match(template, extracted_info.mood)
            weighted_mood_score = mood_score * weights["mood"]
            score_breakdown["mood"] = weighted_mood_score
            total_score += weighted_mood_score
        
        # 4. 상황 매칭
        if weights["situation"] > 0 and extracted_info.situation:
            situation_score = self._calculate_situation_match(template, extracted_info.situation)
            weighted_situation_score = situation_score * weights["situation"]
            score_breakdown["situation"] = weighted_situation_score
            total_score += weighted_situation_score
        
        # 5. 계절 매칭
        if weights["season"] > 0 and extracted_info.season:
            season_score = self._calculate_season_match(template, extracted_info.season)
            weighted_season_score = season_score * weights["season"]
            score_breakdown["season"] = weighted_season_score
            total_score += weighted_season_score
        
        # 6. 예산 매칭
        if weights["budget"] > 0:
            budget_score = self._calculate_budget_match(template, extracted_info)
            weighted_budget_score = budget_score * weights["budget"]
            score_breakdown["budget"] = weighted_budget_score
            total_score += weighted_budget_score
        
        score_breakdown["total"] = total_score
        return score_breakdown
    
    def _calculate_emotion_match(self, template: Dict[str, Any], emotions: List[str]) -> float:
        """감정 매칭 점수 계산"""
        # 현재는 기본 구현 (나중에 꽃의 상징성 데이터로 확장)
        return 0.5  # 기본값
    
    def _calculate_mood_match(self, template: Dict[str, Any], moods: List[str]) -> float:
        """무드 매칭 점수 계산"""
        # 현재는 기본 구현 (나중에 꽃의 무드 데이터로 확장)
        return 0.5  # 기본값
    
    def _calculate_situation_match(self, template: Dict[str, Any], situations: List[str]) -> float:
        """상황 매칭 점수 계산"""
        # 현재는 기본 구현 (나중에 꽃의 상황 적합성 데이터로 확장)
        return 0.5  # 기본값
    
    def _calculate_season_match(self, template: Dict[str, Any], season: str) -> float:
        """계절 매칭 점수 계산"""
        # 현재는 기본 구현 (나중에 꽃의 계절 데이터로 확장)
        return 0.5  # 기본값
    
    def _calculate_budget_match(self, template: Dict[str, Any], extracted_info: ExtractedInfo) -> float:
        """예산 매칭 점수 계산"""
        try:
            price = int(template.get("base_price") or 0)
            budget = int(extracted_info.budget_preference or 50000)
            if budget > 0:
                # 예산에 가까울수록 높은 점수
                return max(0, 1 - abs(price - budget) / max(budget, 1))
        except:
            pass
        return 0.5  # 기본값
    
    def compose_advanced(self, extracted_info: ExtractedInfo, 
                        budget: int = 50000, top_k: int = 3) -> List[AdvancedBundle]:
        """고급 추천 구성"""
        if not self.templates:
            # Fallback demo bundle
            demo = AdvancedBundle(
                id="R001",
                template_id="TPL_YS_WHT_CLASSIC",
                name="프리지아 쏠레이 & 화이트 장미",
                main_flowers=["FRE_SOL", "ROS_WHT"],
                sub_flowers=["EUC", "LAG"],
                color_theme=["yellow", "white"],
                estimated_price=budget,
                reason="밝은 노란색 중심으로 경쾌한 분위기 구성",
                score=1.0,
                score_breakdown={"total": 1.0}
            )
            return [demo]
        
        # 동적 가중치 계산
        weights = self._calculate_dynamic_weights(extracted_info)
        
        print(f"🔍 동적 가중치: {weights}")
        
        # 각 템플릿에 대해 스코어링
        scored_templates = []
        for template in self.templates:
            score_breakdown = self._score_template_advanced(template, extracted_info, weights)
            total_score = score_breakdown["total"]
            
            scored_templates.append({
                "template": template,
                "score": total_score,
                "breakdown": score_breakdown
            })
        
        # 점수순 정렬 및 상위 k개 선택
        scored_templates.sort(key=lambda x: x["score"], reverse=True)
        top_templates = scored_templates[:top_k]
        
        # AdvancedBundle로 변환
        bundles = []
        for i, scored in enumerate(top_templates, 1):
            template = scored["template"]
            score_breakdown = scored["breakdown"]
            
            bundle = AdvancedBundle(
                id=f"R{i:03d}",
                template_id=template.get("template_id"),
                name=template.get("name") or f"추천 구성 {i}",
                main_flowers=(template.get("main_flowers") or "").split("|"),
                sub_flowers=(template.get("sub_flowers") or "").split("|"),
                color_theme=(template.get("color_theme") or "").split("|"),
                estimated_price=int(template.get("base_price") or budget),
                reason="선호도 기반 맞춤 구성",
                score=scored["score"],
                score_breakdown=score_breakdown
            )
            bundles.append(bundle)
        
        return bundles
