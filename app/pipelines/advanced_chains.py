"""
고급 추천 체인 (LLM 기반 + 동적 가중치)
"""
from typing import List, Dict, Any
from app.services.llm_keyword_extractor import LLMKeywordExtractor, ExtractedInfo
from app.services.advanced_recommender import AdvancedRecommender, AdvancedBundle
from app.services.image_matcher import ImageMatcher
from app.models.schemas import RecommendRequest, RecommendResponse, RecommendationItem

class AdvancedRecommendChain:
    def __init__(self):
        self.extractor = LLMKeywordExtractor()
        self.recommender = AdvancedRecommender()
        self.matcher = ImageMatcher()
    
    def run(self, request: RecommendRequest) -> RecommendResponse:
        """고급 추천 체인 실행"""
        print(f"🚀 고급 추천 체인 시작")
        print(f"   고객 스토리: {request.story[:50]}...")
        
        # 1. LLM 기반 키워드 추출
        print(f"🔍 1단계: LLM 키워드 추출")
        extracted_info = self.extractor.extract_with_llm(request.story)
        
        print(f"   추출된 정보:")
        print(f"     감정: {extracted_info.emotion}")
        print(f"     상황: {extracted_info.situation}")
        print(f"     무드: {extracted_info.mood}")
        print(f"     색상방향: {extracted_info.color_direction}")
        print(f"     선호도 강도: 색상({extracted_info.color_intensity:.2f}), 감정({extracted_info.emotion_intensity:.2f})")
        
        # 2. 동적 가중치 기반 추천
        print(f"🎯 2단계: 동적 가중치 추천")
        bundles = self.recommender.compose_advanced(
            extracted_info=extracted_info,
            budget=request.budget or 50000,
            top_k=3
        )
        
        print(f"   추천 번들 {len(bundles)}개 생성")
        
        # 3. 이미지 매칭
        print(f"🖼️  3단계: 이미지 매칭")
        items = []
        
        for bundle in bundles:
            img = self.matcher.match(bundle)
            items.append(RecommendationItem(
                id=bundle.id,
                template_id=bundle.template_id,
                name=bundle.name,
                main_flowers=bundle.main_flowers,
                sub_flowers=bundle.sub_flowers,
                color_theme=bundle.color_theme,
                estimated_price=bundle.estimated_price,
                reason=bundle.reason,
                image_url=img.url
            ))
            print(f"     📸 {bundle.name} → {img.url} (신뢰도: {img.confidence:.2f})")
        
        return RecommendResponse(recommendations=items)
    
    def run_with_details(self, request: RecommendRequest) -> Dict[str, Any]:
        """상세 정보와 함께 추천 체인 실행 (디버깅용)"""
        print(f"🔍 고급 추천 체인 상세 실행")
        
        # 1. 키워드 추출
        extracted_info = self.extractor.extract_with_llm(request.story)
        
        # 2. 추천
        bundles = self.recommender.compose_advanced(
            extracted_info=extracted_info,
            budget=request.budget or 50000,
            top_k=3
        )
        
        # 3. 이미지 매칭
        detailed_items = []
        for bundle in bundles:
            img = self.matcher.match(bundle)
            detailed_items.append({
                "bundle": bundle,
                "image": {
                    "url": img.url,
                    "confidence": img.confidence,
                    "image_id": img.image_id
                }
            })
        
        return {
            "extracted_info": extracted_info,
            "bundles": bundles,
            "detailed_items": detailed_items,
            "request": request
        }
