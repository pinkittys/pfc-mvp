from typing import List, Dict, Any

class RulesEngine:
    def apply(self,
              keywords: List[str],
              mood_tags: List[str],
              occasion: str | None,
              budget: int | None,
              preferred_colors: List[str],
              excluded_flowers: List[str]) -> Dict[str, Any]:
        return {
            "keywords": keywords,
            "mood_tags": mood_tags,
            "occasion": occasion,
            "budget": budget or 0,
            "preferred_colors": [c.lower() for c in preferred_colors],
            "excluded_flowers": set(excluded_flowers),
        }
