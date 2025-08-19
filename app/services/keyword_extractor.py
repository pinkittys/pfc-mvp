from app.models.schemas import KeywordResponse

BASIC_MOOD_DICT = {
    "bright": ["밝", "화사", "환한", "경쾌"],
    "soft": ["잔잔", "은은", "포근", "따뜻", "마음", "괜찮을"],
    "romantic": ["로맨틱", "사랑", "달콤"],
    "calm": ["차분", "고요", "편안"],
    "strong": ["강렬", "강한", "선명", "뚜렷"],  # 강렬한 추가
    "minimal": ["미니멀", "심플", "깔끔"],  # 미니멀 추가
}

OCCASION_DICT = {
    "birthday": ["생일"],
    "cheer_up": ["응원", "위로", "회복", "힘내", "수술", "괜찮을"],
    "congrats": ["축하", "합격", "승진", "오픈", "결혼식", "축사"],
    "apology": ["사과", "미안"],
    "interior": ["인테리어", "집", "방", "공간"],  # 인테리어 추가
}

COLOR_DICT = {
    "white": ["화이트", "하양", "흰색"],
    "yellow": ["노랑", "옐로우", "노란색"],
    "pink": ["핑크", "분홍", "핑크색"],
    "red": ["빨강", "레드", "빨간색"],
    "purple": ["보라", "퍼플", "보라색"],
    "blue": ["파랑", "블루", "파란색"],
    "orange": ["오렌지", "주황", "주황색"],
}

DESIGN_DICT = {
    "point": ["포인트", "포인트컬러", "강조"],
    "modern": ["모던", "현대적", "트렌디"],
    "classic": ["클래식", "전통적", "고전적"],
}

class KeywordExtractor:
    def run(self, story: str) -> KeywordResponse:
        s = story.lower()
        
        # 무드 태그 추출 (색상 제외)
        mood_tags = []
        for tag, kws in BASIC_MOOD_DICT.items():
            if any(kw in story for kw in kws):
                mood_tags.append(tag)

        # 상황 추출
        occasion = None
        for oc, kws in OCCASION_DICT.items():
            if any(kw in story for kw in kws):
                occasion = oc
                break

        # 색상 추출 (별도로 관리)
        colors = []
        for color, kws in COLOR_DICT.items():
            if any(kw in story for kw in kws):
                colors.append(color)

        # 디자인 키워드 추출
        design_keywords = []
        for design, kws in DESIGN_DICT.items():
            if any(kw in story for kw in kws):
                design_keywords.append(design)

        # 기본 키워드 추출 (색상 제외)
        seed_kws = ["엄마","아빠","친구","연인","생일","위로","축하","밝은","은은한","동생","결혼식","축사","마음","직장","선배","수술","괜찮을"]
        keywords = [kw for kw in seed_kws if kw in story]
        
        # 모든 키워드 합치기 (색상은 별도로 관리하여 중복 방지)
        all_keywords = keywords + design_keywords
        all_keywords = list(set(all_keywords))  # 중복 제거
        
        mood_tags = list(set(mood_tags))  # 중복 제거
        colors = list(set(colors))  # 중복 제거

        return KeywordResponse(keywords=all_keywords, mood_tags=mood_tags, occasion=occasion)
