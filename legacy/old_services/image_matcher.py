from typing import Dict, Any, List
from .data_loader import load_images_index
import logging

logger = logging.getLogger(__name__)

class ImageMatchResult:
    def __init__(self, url: str, image_id: str = None, confidence: float = 0.0):
        self.url = url
        self.image_id = image_id
        self.confidence = confidence

def _score_image(img: Dict[str, Any], bundle) -> float:
    """이미지와 번들 간의 매칭 점수 계산"""
    score = 0.0
    
    # 색상 매핑 (한글 -> 영문) - 실제 발견된 색상들
    color_mapping = {
        'white': 'white', '화이트': 'white', '하양': 'white', '흰색': 'white',
        'yellow': 'yellow', '옐로우': 'yellow', '노랑': 'yellow', '노란색': 'yellow',
        'pink': 'pink', '핑크': 'pink', '분홍': 'pink',
        'red': 'red', '레드': 'red', '빨강': 'red',
        'purple': 'purple', '퍼플': 'purple', '보라': 'purple',
        'blue': 'blue', '블루': 'blue', '파랑': 'blue',
        'lavender': 'lavender', '라벤더': 'lavender'
    }
    
    # 색상 매칭 (가장 중요)
    theme_colors = set([color_mapping.get(c.lower().strip(), c.lower().strip()) for c in bundle.color_theme if c])
    img_colors = set([color_mapping.get(c.lower().strip(), c.lower().strip()) for c in (img.get("dominant_colors") or "").split("|") if c])
    
    print(f"   🔍 색상 매칭 디버그:")
    print(f"      번들 색상: {bundle.color_theme} -> {theme_colors}")
    print(f"      이미지 색상: {img.get('dominant_colors')} -> {img_colors}")
    
    if theme_colors and img_colors:
        color_match = theme_colors & img_colors
        if color_match:
            score += 2.0  # 색상 매칭에 높은 가중치
            print(f"      ✅ 색상 매칭: {color_match}")
        else:
            print(f"      ❌ 색상 매칭 실패")
    else:
        print(f"      ⚠️  색상 정보 부족")
    
    # 꽃 이름 매핑 (한글 <-> 영문)
    flower_mapping = {
        # 한글 -> 영문
        '장미': 'rose', 'rose': 'rose',
        '튤립': 'tulip', 'tulip': 'tulip',
        '백합': 'lily', 'lily': 'lily',
        '작약': 'garden-peony', 'garden-peony': 'garden-peony',
        '거베라': 'gerbera-daisy', 'gerbera-daisy': 'gerbera-daisy',
        '수국': 'hydrangea', 'hydrangea': 'hydrangea',
        '리시안셔스': 'lisianthus', 'lisianthus': 'lisianthus',
        '스토크': 'stock-flower', 'stock-flower': 'stock-flower',
        '목화': 'cotton-plant', 'cotton-plant': 'cotton-plant',
        '스카비오사': 'scabiosa', 'scabiosa': 'scabiosa',
        '드럼스틱': 'drumstick-flower', 'drumstick-flower': 'drumstick-flower',
        '달리아': 'dahlia', 'dahlia': 'dahlia',
        '부바르디아': 'bouvardia', 'bouvardia': 'bouvardia',
        '코크스콤': 'cockscomb', 'cockscomb': 'cockscomb',
        '베이비스브레스': 'babys-breath', 'babys-breath': 'babys-breath',
        '글로브아마란스': 'globe-amaranth', 'globe-amaranth': 'globe-amaranth',
        '마거리트데이지': 'marguerite-daisy', 'marguerite-daisy': 'marguerite-daisy',
        '라넌큘러스': 'ranunculus', 'ranunculus': 'ranunculus',
        '알스트로메리아': 'alstroemeria', 'alstroemeria': 'alstroemeria',
        '태게테스': 'tagetes', 'tagetes': 'tagetes',
        '해바라기': 'sunflower', 'sunflower': 'sunflower'
    }
    
    # 꽃 키워드 매칭 (강화)
    bundle_flowers = set()
    for f in bundle.main_flowers + bundle.sub_flowers:
        if f:
            flower_name = f.lower().strip()
            # 매핑된 이름과 원본 이름 모두 추가
            mapped_name = flower_mapping.get(flower_name, flower_name)
            bundle_flowers.add(flower_name)
            bundle_flowers.add(mapped_name)
    
    img_flowers = set()
    img_flower_keywords = (img.get("flower_keywords") or "").lower().replace(" ", "").split("|")
    for f in img_flower_keywords:
        if f:
            flower_name = f.lower().strip()
            # 매핑된 이름과 원본 이름 모두 추가
            mapped_name = flower_mapping.get(flower_name, flower_name)
            img_flowers.add(flower_name)
            img_flowers.add(mapped_name)
    
    print(f"   🔍 꽃 매칭 디버그:")
    print(f"      번들 꽃: {bundle_flowers}")
    print(f"      이미지 꽃: {img_flowers}")
    
    if bundle_flowers and img_flowers:
        flower_match = bundle_flowers & img_flowers
        if flower_match:
            score += 2.0  # 꽃 매칭에 높은 가중치 (색상과 동일)
            print(f"      ✅ 꽃 매칭: {flower_match}")
        else:
            print(f"      ❌ 꽃 매칭 실패")
    else:
        print(f"      ⚠️  꽃 정보 부족")
    
    # 스타일 태그 매칭
    bundle_style = set([s.lower().strip() for s in getattr(bundle, 'style_tags', []) if s])
    img_style = set((img.get("style_tags") or "").lower().replace(" ", "").split("|"))
    
    if bundle_style and img_style:
        style_match = bundle_style & img_style
        if style_match:
            score += 0.5  # 스타일 매칭에 낮은 가중치
            logger.debug(f"스타일 매칭: {style_match}")
    
    return score

class ImageMatcher:
    def __init__(self):
        self._images_cache = None
        self._cache_loaded = False
    
    def _load_images(self) -> List[Dict[str, Any]]:
        """이미지 인덱스 로드 (캐싱)"""
        if not self._cache_loaded:
            self._images_cache = load_images_index()
            self._cache_loaded = True
            logger.info(f"이미지 인덱스 로드: {len(self._images_cache or [])}개")
        return self._images_cache or []
    
    def match(self, bundle) -> ImageMatchResult:
        """번들에 가장 적합한 이미지 매칭"""
        images = self._load_images()
        
        if not images:
            logger.warning("이미지 인덱스가 비어있어 placeholder 반환")
            return ImageMatchResult(
                url="https://placehold.co/600x800?text=Floiy",
                image_id="placeholder",
                confidence=0.0
            )
        
        # 각 이미지에 대해 점수 계산
        scored_images = []
        for img in images:
            score = _score_image(img, bundle)
            scored_images.append((img, score))
            logger.debug(f"이미지 {img.get('image_id', 'unknown')} 점수: {score}")
        
        # 최고 점수 이미지 선택
        if scored_images:
            best_img, best_score = max(scored_images, key=lambda x: x[1])
            
            # 신뢰도 계산 (0-1 범위)
            max_possible_score = 4.0  # 색상(2.0) + 꽃(1.5) + 스타일(0.5)
            confidence = min(best_score / max_possible_score, 1.0)
            
            logger.info(f"최적 이미지 선택: {best_img.get('image_id')} (점수: {best_score:.2f}, 신뢰도: {confidence:.2f})")
            
            return ImageMatchResult(
                url=best_img.get("image_url") or "https://placehold.co/600x800?text=Floiy",
                image_id=best_img.get("image_id"),
                confidence=confidence
            )
        
        # 매칭 실패 시 기본 이미지
        logger.warning("적합한 이미지를 찾을 수 없어 기본 이미지 반환")
        return ImageMatchResult(
            url="https://placehold.co/600x800?text=Floiy",
            image_id="default",
            confidence=0.0
        )
