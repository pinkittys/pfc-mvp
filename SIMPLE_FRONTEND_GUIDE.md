# 🌸 PlainFlowerClub API - 간단 가이드 (프론트엔드용)

## 🚀 API 서버
```
https://api.plainflowerclub.com/api/v1
```

## 📋 실제로 필요한 API는 2개뿐!

> **참고**: 고급 기능이 필요한 경우 `/api/v1/advanced/` 엔드포인트를 사용하세요.

### 1️⃣ 키워드 추출
```javascript
POST /api/v1/extract-keywords
```

**요청:**
```json
{
  "story": "첫사랑에게 고백하려고 해요"
}
```

**응답:**
```json
{
  "emotions": {
    "main": "기쁨",
    "alternatives": ["행복", "즐거움"]
  },
  "situations": {
    "main": "축하", 
    "alternatives": ["경사", "축하파티"]
  },
  "moods": {
    "main": "밝은",
    "alternatives": ["활기찬", "경쾌한"]
  },
  "colors": {
    "main": "핑크",
    "alternatives": ["라일락", "화이트"]
  }
}
```

### 2️⃣ 꽃 추천
```javascript
POST /api/v1/recommend
```

**요청:**
```json
{
  "story": "첫사랑에게 고백하려고 해요",
  "selected_keywords": {
    "emotions": "기쁨",
    "situations": "축하",
    "moods": "밝은", 
    "colors": "핑크"
  },
  "excluded_keywords": []
}
```

**응답:**
```json
{
  "matched_flower": {
    "name_ko": "장미",
    "color": "핑크",
    "image_url": "https://...",
    "flower_language": "사랑, 진심, 아름다움"
  },
  "recommendation_reason": "첫사랑에게 고백하는 특별한 순간을 위해 장미를 선택했습니다..."
}
```

## 🔧 프론트엔드 구현

```javascript
// 1단계: 키워드 추출
const extractKeywords = async (story) => {
  const response = await fetch('/api/v1/extract-keywords', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ story })
  });
  return await response.json();
};

// 2단계: 꽃 추천
const getRecommendation = async (story, selectedKeywords) => {
  const response = await fetch('/api/v1/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      story,
      selected_keywords: selectedKeywords,
      excluded_keywords: []
    })
  });
  return await response.json();
};
```

## 🎯 사용법

1. 사용자가 스토리 입력
2. `extract-keywords`로 키워드 추출
3. 사용자가 키워드 선택 (UI에서)
4. `recommend`로 꽃 추천받기

**끝!** 🎉

---

## 🔧 고급 옵션 (필요시에만 사용)

### 고급 키워드 추출
```javascript
POST /api/v1/advanced/extract-final
```

### 최종 추천 처리
```javascript
POST /api/v1/advanced/recommend/final
```

### 추천 결과 조회
```javascript
GET /api/v1/advanced/recommend/{story_id}
```

### 고급 통계 조회
```javascript
GET /api/v1/advanced/stats
```
