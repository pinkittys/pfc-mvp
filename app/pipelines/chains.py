from app.models.schemas import RecommendRequest, RecommendResponse, RecommendationItem
from app.services.keyword_extractor import KeywordExtractor
from app.services.rules_engine import RulesEngine
from app.services.recommender import Recommender
from app.services.image_matcher import ImageMatcher

class RecommendChain:
    def __init__(self):
        self.extractor = KeywordExtractor()
        self.rules = RulesEngine()
        self.recommender = Recommender()
        self.matcher = ImageMatcher()

    def run(self, req: RecommendRequest) -> RecommendResponse:
        # Extract (can be reused inside recommender as well)
        k = self.extractor.run(req.story)
        # Filter
        flt = self.rules.apply(
            keywords=k.keywords,
            mood_tags=k.mood_tags,
            occasion=k.occasion,
            budget=req.budget,
            preferred_colors=req.preferred_colors,
            excluded_flowers=req.excluded_flowers
        )
        # Compose Bundles
        bundles = self.recommender.compose(flt, top_k=req.top_k)
        # Match Images
        items = []
        for b in bundles:
            img = self.matcher.match(b)
            items.append(RecommendationItem(
                id=b.id,
                template_id=b.template_id,
                name=b.name,
                main_flowers=b.main_flowers,
                sub_flowers=b.sub_flowers,
                color_theme=b.color_theme,
                estimated_price=b.estimated_price,
                reason=b.reason,
                image_url=img.url
            ))
            # 로깅 추가
            print(f"📸 이미지 매칭: {b.name} -> {img.url} (신뢰도: {img.confidence:.2f})")
        return RecommendResponse(recommendations=items)
