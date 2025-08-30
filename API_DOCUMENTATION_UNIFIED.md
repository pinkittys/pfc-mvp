# 🌸 Plain Flower Club - 통합 API 문서

## 📋 개요

프론트엔드 개발자를 위한 단순화된 API 엔드포인트입니다. 기존의 8개 엔드포인트를 3개로 통합하여 개발 편의성을 높였습니다.

**Base URL**: `https://api.plainflowerclub.com`

---

## 🚀 새로운 통합 엔드포인트

### 1. 샘플 사연 시연
```http
POST /api/v1/sample-stories
```

**응답 예시:**
```json
{
  "success": true,
  "stories": [
    {
      "id": "sample_1",
      "title": "첫 손자 태어남",
      "story": "첫 손자가 태어난 날이에요. 병실 분위기가 환해지는 꽃바구니를 준비하고 싶어요.",
      "emotions": ["기쁨", "감사"],
      "situations": ["축하"],
      "colors": ["핑크", "화이트"]
    }
  ]
}
```

---

### 2. 실시간 키워드 추출
```http
POST /api/v1/extract-keywords
```

**요청 본문:**
```json
{
  "story": "친구가 이직하게 되었어요. 새로운 시작을 응원하는 마음을 담아 꽃을 선물하고 싶어요.",
  "preferred_colors": ["옐로우", "화이트"],
  "excluded_flowers": [],
  "updated_context": {
    "colors": ["옐로우"],
    "emotions": ["응원"],
    "situations": ["이직"],
    "moods": ["따뜻한"]
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "keywords": {
    "emotions": ["응원", "감사"],
    "situations": ["이직"],
    "moods": ["따뜻한"],
    "colors": ["옐로우"]
  },
  "confidence": 0.85
}
```

---

### 3. 통합 추천 결과
```http
POST /api/v1/recommend
```

**요청 본문:**
```json
{
  "story": "친구가 이직하게 되었어요. 새로운 시작을 응원하는 마음을 담아 꽃을 선물하고 싶어요.",
  "preferred_colors": ["옐로우", "화이트"],
  "excluded_flowers": [],
  "updated_context": {
    "colors": ["옐로우"],
    "emotions": ["응원"],
    "situations": ["이직"],
    "moods": ["따뜻한"]
  }
}
```

**응답 예시:**
```json
{
  "flower_name": "Sunflower",
  "korean_name": "해바라기",
  "scientific_name": "Helianthus annuus",
  "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/sunflower-yl.webp",
  "hashtags": ["#해바라기", "#옐로우", "#응원", "#이직", "#여름"],
  "keywords": ["응원", "희망"],
  "color_keywords": ["옐로우"]
}
```

---

## 🌸 사연 샘플 관련 엔드포인트

### 1. 사연 샘플 목록 조회
```http
GET /api/v1/sample-stories
```

**응답 예시:**
```json
{
  "stories": [
    {
      "id": "story_001",
      "title": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "story": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "predefined_keywords": {
        "emotions": ["희망", "응원"],
        "situations": ["새로운 시작", "격려"],
        "moods": ["활기찬", "따뜻한"],
        "colors": ["옐로우"]
      },
      "category": "응원/격려"
    }
  ],
  "total_count": 30
}
```

### 2. 특정 사연 조회
```http
GET /api/v1/sample-stories/{story_id}
```

### 3. 사연별 꽃 추천
```http
POST /api/v1/sample-stories/{story_id}/recommend
```

**응답 예시:**
```json
{
  "story": {
    "id": "story_001",
    "title": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
    "story": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
    "predefined_keywords": {
      "emotions": ["희망", "응원"],
      "situations": ["새로운 시작", "격려"],
      "moods": ["활기찬", "따뜻한"],
      "colors": ["옐로우"]
    },
    "category": "응원/격려"
  },
  "predefined_keywords": {
    "emotions": ["희망", "응원"],
    "situations": ["새로운 시작", "격려"],
    "moods": ["활기찬", "따뜻한"],
    "colors": ["옐로우"]
  },
  "recommendation": {
    "flower_name": "Sunflower",
    "korean_name": "해바라기",
    "scientific_name": "Helianthus annuus",
    "image_url": "https://api.plainflowerclub.com/images/sunflower/옐로우.webp",
    "keywords": ["응원", "희망"],
    "hashtags": ["#해바라기", "#옐로우", "#응원", "#새로운시작"],
    "color_keywords": ["옐로우"]
  }
}
```

### 4. 카테고리별 사연 조회
```http
GET /api/v1/sample-stories/categories
GET /api/v1/sample-stories/category/{category}
```

---

## 🎨 데모 페이지

### 사연 샘플 데모
- **URL**: `https://api.plainflowerclub.com/demo`
- **기능**: 30개 사연 샘플을 카드 형태로 표시하고, 선택 시 바로 꽃 추천 결과 제공

---

## 📱 프론트엔드 연동 가이드

### 사연 샘플 기능 구현 순서

1. **사연 목록 로드**
```javascript
const response = await fetch('https://api.plainflowerclub.com/api/v1/sample-stories');
const data = await response.json();
const stories = data.stories;
```

2. **사연 선택 시 추천 요청**
```javascript
const response = await fetch(`https://api.plainflowerclub.com/api/v1/sample-stories/${storyId}/recommend`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
});
const result = await response.json();
```

3. **추천 결과 표시**
```javascript
const { story, predefined_keywords, recommendation } = result;
// 꽃 이미지, 이름, 해시태그 등 표시
```

---

## 🔧 에러 처리

### 공통 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

### 주요 HTTP 상태 코드
- `200`: 성공
- `404`: 사연을 찾을 수 없음
- `500`: 서버 내부 오류

---

## 📞 지원

API 사용 중 문제가 발생하면 다음을 확인해주세요:
1. **헬스체크**: `GET /health`
2. **API 문서**: `https://api.plainflowerclub.com/docs`
3. **데모 페이지**: `https://api.plainflowerclub.com/demo`
