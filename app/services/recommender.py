from typing import List, Dict, Any
from dataclasses import dataclass
from .data_loader import load_templates, load_flowers

@dataclass
class Bundle:
    id: str
    template_id: str | None
    name: str
    main_flowers: List[str]
    sub_flowers: List[str]
    color_theme: List[str]
    estimated_price: int
    reason: str

def _score_template(tpl: Dict[str, Any], filt: Dict[str, Any]) -> float:
    score = 0.0
    colors = set((tpl.get("color_theme") or "").lower().replace(" ", "").split("|"))
    pref = set(filt.get("preferred_colors", []))
    if pref & colors:
        score += 1.0
    try:
        price = int(tpl.get("base_price") or 0)
        budget = int(filt.get("budget") or 0)
        if budget > 0:
            # closer to budget, better
            score += max(0, 1 - abs(price - budget)/max(budget, 1))
    except:
        pass
    return score

class Recommender:
    def compose(self, filt: Dict[str, Any], top_k: int) -> List[Bundle]:
        templates = load_templates()
        if not templates:
            # fallback demo bundle
            demo = Bundle(
                id="R001",
                template_id="TPL_YS_WHT_CLASSIC",
                name="프리지아 쏠레이 & 화이트 장미",
                main_flowers=["FRE_SOL","ROS_WHT"],
                sub_flowers=["EUC","LAG"],
                color_theme=["yellow","white"],
                estimated_price=int(filt.get("budget") or 48000),
                reason="밝은 노란색 중심으로 경쾌한 분위기 구성"
            )
            return [demo]
        # score and pick top_k
        scored = sorted(templates, key=lambda t: _score_template(t, filt), reverse=True)[:top_k]
        bundles = []
        for i, t in enumerate(scored, start=1):
            bundles.append(Bundle(
                id=f"R{i:03d}",
                template_id=t.get("template_id"),
                name=t.get("name") or f"추천 구성 {i}",
                main_flowers=(t.get("main_flowers") or "").split("|"),
                sub_flowers=(t.get("sub_flowers") or "").split("|"),
                color_theme=(t.get("color_theme") or "").split("|"),
                estimated_price=int(t.get("base_price") or 0),
                reason="선호 색상과 예산에 맞춘 구성"
            ))
        return bundles
