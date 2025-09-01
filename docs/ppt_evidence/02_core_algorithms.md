# 핵심 알고리즘 구현

## 1. 감정 분석 알고리즘

```python
class EmotionAnalyzer:
    def analyze(self, story: str) -> List[EmotionAnalysis]:
        # GPT-4 기반 감정 분석
        # 3가지 감정을 퍼센티지로 분할
        # 특수 키워드 오버라이드 로직
        
        prompt = f"""
        다음 사연에서 3가지 감정을 추출하고 퍼센티지를 계산하세요:
        사연: {story}
        
        요구사항:
        - 3가지 감정 (총합 100%)
        - JSON 형식으로 응답
        - 감정: 기쁨, 사랑, 감사, 축하, 위로, 희망 등
        """
        
        # OpenAI API 호출 및 결과 파싱
        return [
            EmotionAnalysis(emotion="기쁨", percentage=50.0),
            EmotionAnalysis(emotion="축하", percentage=30.0),
            EmotionAnalysis(emotion="희망", percentage=20.0)
        ]
```

## 2. 꽃 매칭 알고리즘

```python
def _calculate_flower_scores(self, emotions, story, colors):
    """꽃 매칭 점수 계산"""
    
    for flower in flower_database:
        score = 0.0
        
        # 1. 색상 우선순위 (5배 가중치)
        if requested_color in flower.colors:
            score += 50.0  # 직접 언급 시 최우선
        
        # 2. 감정 매칭 (퍼센티지 기반)
        for emotion in emotions:
            if emotion.emotion in flower.emotions:
                score += emotion.percentage * 0.8
        
        # 3. 꽃말 매칭 (15점 가중치)
        if any(keyword in story for keyword in flower.meanings):
            score += 15.0
        
        # 4. 계절 고려
        if current_season in flower.seasons:
            score += 5.0
    
    return sorted_flowers_by_score
```

## 3. 실시간 키워드 추출

```python
class RealtimeContextExtractor:
    def extract_context_realtime(self, text: str) -> ExtractedContext:
        """LLM 기반 실시간 맥락 추출"""
        
        # 텍스트 길이별 최적화
        if len(text) <= 15:
            max_keywords = 4  # 최소 4개 차원 보장
        elif len(text) <= 40:
            max_keywords = 4
        else:
            max_keywords = 6
        
        prompt = f"""
        다음 텍스트에서 키워드를 추출하세요:
        텍스트: {text}
        
        추출 항목:
        - 감정: {max_keywords}개
        - 상황: {max_keywords}개  
        - 무드: {max_keywords}개
        - 컬러: {max_keywords}개
        """
        
        # GPT-4 API 호출 및 결과 파싱
        return ExtractedContext(
            emotions=["기쁨", "축하"],
            situations=["생일", "선물"],
            moods=["로맨틱한", "따뜻한"],
            colors=["화이트", "핑크"]
        )
```

