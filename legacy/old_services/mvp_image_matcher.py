"""
MVP 이미지 매처
메인 꽃만 매칭하고 텍스트로 꽃다발 구성 설명
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MVPImageMatchResult:
    """MVP 이미지 매칭 결과"""
    image_url: str
    confidence: float
    main_flower: str
    main_flower_color: str
    bouquet_composition_text: str
    match_reason: str

class MVPImageMatcher:
    """MVP 이미지 매처 - 메인 꽃 우선 매칭"""
    
    def __init__(self):
        self.images_index_path = Path("data/images_index_enhanced.csv")
        self.images_data = self._load_images_index()
        
        # 색상 매핑
        self.color_mapping = {
            "화이트": "white", "흰색": "white",
            "핑크": "pink", "분홍": "pink",
            "레드": "red", "빨강": "red",
            "옐로우": "yellow", "노랑": "yellow",
            "퍼플": "purple", "보라": "purple",
            "블루": "blue", "파랑": "blue",
            "오렌지": "orange", "주황": "orange",
            "라벤더": "lavender"
        }
    
    def _load_images_index(self) -> pd.DataFrame:
        """이미지 인덱스 로드"""
        if self.images_index_path.exists():
            return pd.read_csv(self.images_index_path)
        else:
            print("⚠️ 향상된 이미지 인덱스를 찾을 수 없습니다.")
            return pd.DataFrame()
    
    def match_main_flower(self, main_flower: str, color_preference: List[str] = None) -> MVPImageMatchResult:
        """메인 꽃 매칭"""
        print(f"🎯 메인 꽃 매칭: {main_flower}")
        
        if self.images_data.empty:
            return self._fallback_result(main_flower)
        
        # 1단계: 메인 꽃 이름 정확 매칭
        exact_matches = self.images_data[
            (self.images_data['korean_flower_name'] == main_flower) & 
            (self.images_data['is_single_flower'] == True)
        ]
        
        if not exact_matches.empty:
            print(f"   ✅ 메인 꽃 정확 매칭: {len(exact_matches)}개")
            
            # 색상 선호도가 있으면 색상 매칭
            if color_preference:
                color_match = self._find_color_match(exact_matches, color_preference)
                if color_match is not None:
                    return self._create_result(color_match, 3.0, "메인 꽃 + 색상 정확 매칭")
            
            # 첫 번째 매칭 결과 반환
            best_match = exact_matches.iloc[0]
            return self._create_result(best_match, 2.5, "메인 꽃 정확 매칭")
        
        # 2단계: 유사 꽃 이름 매칭
        similar_matches = self._find_similar_flower(main_flower)
        if similar_matches is not None:
            return self._create_result(similar_matches, 2.0, "유사 꽃 매칭")
        
        # 3단계: 색상 기반 매칭
        if color_preference:
            color_match = self._find_color_only_match(color_preference)
            if color_match is not None:
                return self._create_result(color_match, 1.5, "색상 기반 매칭")
        
        # 4단계: 기본 이미지
        return self._fallback_result(main_flower)
    
    def _find_color_match(self, matches: pd.DataFrame, color_preference: List[str]) -> Optional[pd.Series]:
        """색상 매칭"""
        for color in color_preference:
            english_color = self.color_mapping.get(color, color.lower())
            
            color_matches = matches[matches['dominant_colors'] == english_color]
            if not color_matches.empty:
                print(f"   🎨 색상 매칭: {color} → {english_color}")
                return color_matches.iloc[0]
        
        return None
    
    def _find_similar_flower(self, main_flower: str) -> Optional[pd.Series]:
        """유사 꽃 찾기"""
        # 유사 꽃 매핑
        similar_flowers = {
            "작약": "garden-peony",
            "부바르디아": "bouvardia",
            "스토크": "stock-flower",
            "스카비오사": "scabiosa",
            "골든볼": "drumstick-flower",
            "다알리아": "dahlia",
            "장미": "rose",
            "백합": "lily",
            "마가렛": "marguerite-daisy",
            "튤립": "tulip",
            "거베라": "gerbera-daisy",
            "맨드라미": "cockscomb",
            "목화": "cotton-plant",
            "리시안셔스": "lisianthus",
            "베이비스브레스": "babys-breath",
            "천일홍": "globe-amaranth",
            "수국": "hydrangea"
        }
        
        english_name = similar_flowers.get(main_flower)
        if english_name:
            similar_matches = self.images_data[
                (self.images_data['flower_keywords'] == english_name) & 
                (self.images_data['is_single_flower'] == True)
            ]
            if not similar_matches.empty:
                print(f"   🔄 유사 꽃 매칭: {main_flower} → {english_name}")
                return similar_matches.iloc[0]
        
        return None
    
    def _find_color_only_match(self, color_preference: List[str]) -> Optional[pd.Series]:
        """색상만으로 매칭"""
        for color in color_preference:
            english_color = self.color_mapping.get(color, color.lower())
            
            color_matches = self.images_data[
                (self.images_data['dominant_colors'] == english_color) & 
                (self.images_data['is_single_flower'] == True)
            ]
            if not color_matches.empty:
                print(f"   🎨 색상만 매칭: {color} → {english_color}")
                return color_matches.iloc[0]
        
        return None
    
    def _create_result(self, match: pd.Series, confidence: float, reason: str) -> MVPImageMatchResult:
        """매칭 결과 생성"""
        # 꽃다발 구성 텍스트 생성
        bouquet_text = self._generate_bouquet_composition_text(match)
        
        return MVPImageMatchResult(
            image_url=match['image_url'],
            confidence=confidence,
            main_flower=match['korean_flower_name'],
            main_flower_color=match['color_korean'],
            bouquet_composition_text=bouquet_text,
            match_reason=reason
        )
    
    def _generate_bouquet_composition_text(self, match: pd.Series) -> str:
        """꽃다발 구성 텍스트 생성"""
        flower_name = match['korean_flower_name']
        color = match['color_korean']
        
        # 꽃별 구성 템플릿
        composition_templates = {
            "장미": f"{color} {flower_name}를 메인으로 한 로맨틱한 꽃다발입니다. {flower_name} 주변에 작은 필러 꽃들과 그린 소재를 조화롭게 배치하여 우아하고 고급스러운 분위기를 연출합니다.",
            "튤립": f"{color} {flower_name}를 중심으로 한 신선하고 밝은 꽃다발입니다. {flower_name}의 깔끔한 라인과 함께 다양한 색상의 작은 꽃들을 조화롭게 구성하여 봄다운 경쾌한 느낌을 줍니다.",
            "거베라": f"{color} {flower_name}를 메인으로 한 활기찬 꽃다발입니다. {flower_name}의 둥근 형태와 밝은 색상이 돋보이며, 주변에 필러 꽃들과 그린 소재를 균형있게 배치하여 모던하고 경쾌한 분위기를 만듭니다.",
            "작약": f"{color} {flower_name}를 중심으로 한 우아한 꽃다발입니다. {flower_name}의 풍성한 꽃잎과 고급스러운 색상이 주목을 끌며, 세련된 필러 꽃들과 함께 로맨틱하고 고급스러운 분위기를 연출합니다.",
            "백합": f"{color} {flower_name}를 메인으로 한 고급스러운 꽃다발입니다. {flower_name}의 우아한 형태와 깊이 있는 색상이 돋보이며, 정교한 필러 꽃들과 그린 소재를 조화롭게 구성하여 세련되고 고급스러운 분위기를 만듭니다.",
            "리시안셔스": f"{color} {flower_name}를 중심으로 한 세련된 꽃다발입니다. {flower_name}의 우아한 꽃잎과 부드러운 색상이 돋보이며, 정교한 필러 꽃들과 그린 소재를 균형있게 배치하여 고급스럽고 세련된 분위기를 연출합니다."
        }
        
        return composition_templates.get(flower_name, f"{color} {flower_name}를 메인으로 한 아름다운 꽃다발입니다.")
    
    def _fallback_result(self, main_flower: str) -> MVPImageMatchResult:
        """기본 결과 반환"""
        print(f"   ⚠️ 기본 이미지 사용")
        
        return MVPImageMatchResult(
            image_url="/static/images/default_flower.webp",
            confidence=0.5,
            main_flower=main_flower,
            main_flower_color="기본",
            bouquet_composition_text=f"{main_flower}를 메인으로 한 아름다운 꽃다발입니다. 다양한 꽃들과 그린 소재를 조화롭게 구성하여 완성도 높은 어레인지를 제공합니다.",
            match_reason="기본 이미지"
        )

# 사용 예시
if __name__ == "__main__":
    matcher = MVPImageMatcher()
    
    # 테스트
    result = matcher.match_main_flower("장미", ["핑크", "화이트"])
    print(f"매칭 결과: {result.image_url}")
    print(f"신뢰도: {result.confidence}")
    print(f"구성 설명: {result.bouquet_composition_text}")
