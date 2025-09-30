# 🌸 PlainFlowerClub API 가이드 (프론트엔드 개발자용) - 2025년 최신판

## 🚀 API 서버 정보

### 🎉 현재 사용 가능한 API URL:
```
https://api.plainflowerclub.com/api/v1
```

### 📚 API 문서 (Swagger UI):
```
https://api.plainflowerclub.com/docs
```

### 🧪 데모 페이지:
```
https://api.plainflowerclub.com/demo
```

---

## 📋 핵심 API 엔드포인트 (2025년 최신)

### 1. 키워드 추출 API
**사용자 스토리에서 감정, 상황, 무드, 색상을 자동으로 추출합니다.**

```javascript
POST /api/v1/extract-keywords
```

**요청 (Request):**
```json
{
  "story": "첫사랑에게 고백하려고 해요. 수줍고 설레는 마음을 담아서 핑크나 화이트 톤이 좋겠어요."
}
```

**응답 (Response):**
```json
{
  "emotions": {
    "main": "기쁨",
    "alternatives": ["행복", "즐거움", "설렘"]
  },
  "situations": {
    "main": "축하",
    "alternatives": ["경사", "축하파티", "기념"]
  },
  "moods": {
    "main": "밝은",
    "alternatives": ["밝게", "활기찬", "경쾌한"]
  },
  "colors": {
    "main": "핑크",
    "alternatives": ["라일락", "화이트"]
  },
  "confidence": 0.85,
  "extraction_method": "lightweight_llm"
}
```

### 2. 꽃 추천 API (메인)
**선택된 키워드로 꽃을 추천합니다.**

```javascript
POST /api/v1/recommend
```

**요청 (Request):**
```json
{
  "story": "첫사랑에게 고백하려고 해요. 수줍고 설레는 마음을 담아서 핑크나 화이트 톤이 좋겠어요.",
  "selected_keywords": {
    "emotions": "기쁨",
    "situations": "축하",
    "moods": "밝은",
    "colors": "핑크"
  },
  "excluded_keywords": []
}
```

**응답 (Response):**
```json
{
  "recommendation_id": "rec_20250930_001",
  "matched_flower": {
    "flower_id": "rose-pk",
    "name_ko": "장미",
    "name_en": "Rose",
    "scientific_name": "Rosa spp.",
    "color": "핑크",
    "season": "Spring 03-05",
    "price_tier": "high",
    "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-pk.webp",
    "flower_language": "사랑, 진심, 아름다움",
    "keywords": {
      "emotions": ["사랑", "기쁨", "행복"],
      "situations": ["축하", "고백", "사랑"],
      "moods": ["밝은", "활기찬", "로맨틱"],
      "colors": ["핑크", "화이트"]
    }
  },
  "recommendation_reason": "첫사랑에게 고백하는 특별한 순간을 위해 장미를 선택했습니다. 장미는 사랑과 진심을 상징하며, 핑크 색상은 수줍고 설레는 마음을 아름답게 표현합니다. 이 꽃이 고객님의 진심어린 마음을 전달하는 완벽한 메신저가 될 것입니다.",
  "confidence": 0.92,
  "matching_score": 0.88,
  "created_at": "2025-09-30T22:45:00Z"
}
```

### 3. 샘플 스토리 조회 API
**미리 준비된 샘플 스토리들을 조회합니다.**

```javascript
GET /api/v1/sample-stories
```

**응답 (Response):**
```json
{
  "stories": [
    {
      "id": "S01",
      "title": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "story": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "category": "응원/격려",
      "predefined_keywords": {
        "emotions": ["희망", "응원"],
        "situations": ["새로운 시작", "격려"],
        "moods": ["활기찬", "따뜻한"],
        "colors": ["옐로우"]
      }
    }
  ],
  "total_count": 30
}
```

### 4. 샘플 스토리 추천 API
**특정 샘플 스토리로 꽃을 추천합니다.**

```javascript
POST /api/v1/sample-stories/{story_id}/recommend
```

**요청 (Request):**
```json
{
  "story_id": "S01"
}
```

**응답 (Response):**
```json
{
  "recommendation_id": "rec_sample_S01_001",
  "matched_flower": {
    "flower_id": "sunflower-yl",
    "name_ko": "해바라기",
    "name_en": "Sunflower",
    "scientific_name": "Helianthus annuus",
    "color": "옐로우",
    "season": "Summer 06-08",
    "price_tier": "medium",
    "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/sunflower-yl.webp",
    "flower_language": "희망, 응원, 긍정적 에너지",
    "keywords": {
      "emotions": ["희망", "응원", "긍정"],
      "situations": ["새로운 시작", "격려", "응원"],
      "moods": ["활기찬", "따뜻한", "밝은"],
      "colors": ["옐로우", "골드"]
    }
  },
  "recommendation_reason": "새로운 시작을 하는 회사 동생에게 해바라기를 추천합니다. 해바라기는 희망과 응원을 상징하며, 밝은 옐로우 색상은 긍정적인 에너지를 전달합니다. 이 꽃이 동생에게 새로운 시작에 대한 용기와 희망을 전달하는 완벽한 메신저가 될 것입니다.",
  "confidence": 0.95,
  "matching_score": 0.92,
  "created_at": "2025-09-30T22:45:00Z"
}
```

---

## 🔧 프론트엔드 구현 가이드

### 1. 기본 플로우
```javascript
// 1단계: 사용자 스토리 입력
const userStory = "첫사랑에게 고백하려고 해요...";

// 2단계: 키워드 추출
const keywordsResponse = await fetch('/api/v1/extract-keywords', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ story: userStory })
});
const keywords = await keywordsResponse.json();

// 3단계: 사용자가 키워드 선택 (UI에서)
const selectedKeywords = {
  emotions: "기쁨",
  situations: "축하", 
  moods: "밝은",
  colors: "핑크"
};

// 4단계: 꽃 추천
const recommendationResponse = await fetch('/api/v1/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    story: userStory,
    selected_keywords: selectedKeywords,
    excluded_keywords: []
  })
});
const recommendation = await recommendationResponse.json();
```

### 2. 에러 처리
```javascript
try {
  const response = await fetch('/api/v1/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('API 오류:', error.detail);
    // 사용자에게 오류 메시지 표시
  }
  
  const result = await response.json();
  // 추천 결과 처리
  
} catch (error) {
  console.error('네트워크 오류:', error);
  // 네트워크 오류 처리
}
```

### 3. 로딩 상태 관리
```javascript
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);

const handleRecommendation = async () => {
  setIsLoading(true);
  setError(null);
  
  try {
    const response = await fetch('/api/v1/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error('추천 생성 실패');
    }
    
    const result = await response.json();
    // 추천 결과 처리
    
  } catch (err) {
    setError(err.message);
  } finally {
    setIsLoading(false);
  }
};
```

---

## 📱 샘플 구현 코드

### React 컴포넌트 예시
```jsx
import React, { useState } from 'react';

const FlowerRecommendation = () => {
  const [story, setStory] = useState('');
  const [keywords, setKeywords] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const extractKeywords = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/extract-keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story })
      });
      const data = await response.json();
      setKeywords(data);
    } catch (error) {
      console.error('키워드 추출 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRecommendation = async (selectedKeywords) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          story,
          selected_keywords: selectedKeywords,
          excluded_keywords: []
        })
      });
      const data = await response.json();
      setRecommendation(data);
    } catch (error) {
      console.error('추천 생성 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <textarea 
        value={story}
        onChange={(e) => setStory(e.target.value)}
        placeholder="사연을 입력해주세요..."
      />
      <button onClick={extractKeywords} disabled={isLoading}>
        키워드 추출
      </button>
      
      {keywords && (
        <div>
          <h3>추출된 키워드</h3>
          <p>감정: {keywords.emotions.main}</p>
          <p>상황: {keywords.situations.main}</p>
          <p>무드: {keywords.moods.main}</p>
          <p>색상: {keywords.colors.main}</p>
          <button onClick={() => getRecommendation({
            emotions: keywords.emotions.main,
            situations: keywords.situations.main,
            moods: keywords.moods.main,
            colors: keywords.colors.main
          })}>
            꽃 추천받기
          </button>
        </div>
      )}
      
      {recommendation && (
        <div>
          <h3>추천 꽃</h3>
          <img src={recommendation.matched_flower.image_url} alt={recommendation.matched_flower.name_ko} />
          <h4>{recommendation.matched_flower.name_ko}</h4>
          <p>{recommendation.recommendation_reason}</p>
        </div>
      )}
    </div>
  );
};

export default FlowerRecommendation;
```

---

## 🚨 주의사항

1. **API 키**: 현재는 API 키가 필요하지 않습니다.
2. **Rate Limiting**: 과도한 요청 시 제한될 수 있습니다.
3. **응답 시간**: 키워드 추출과 추천 생성에 시간이 걸릴 수 있습니다 (3-10초).
4. **에러 처리**: 항상 try-catch로 에러를 처리하세요.
5. **로딩 상태**: 사용자 경험을 위해 로딩 상태를 표시하세요.

---

## 📞 지원

문제가 있거나 추가 정보가 필요한 경우:
- API 문서: https://api.plainflowerclub.com/docs
- 데모 페이지: https://api.plainflowerclub.com/demo
