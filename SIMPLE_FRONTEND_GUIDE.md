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
    "main": "설렘",
    "alternatives": ["따뜻함", "기쁨", "감사"]
  },
  "situations": {
    "main": "축하", 
    "alternatives": ["일상", "축하", "위로"]
  },
  "moods": {
    "main": "로맨틱한",
    "alternatives": ["사랑스러운", "따뜻한", "우아한"]
  },
  "colors": {
    "main": "핑크",
    "alternatives": ["핑크", "레드", "화이트"]
  },
  "confidence": 0.9,
  "extraction_method": "full_llm"
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
  "flower_name": "장미",
  "korean_name": "장미",
  "scientific_name": "Rosa spp.",
  "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-pk.webp",
  "calligraphy_image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/calligraphy-images/rose-pk.webp",
  "hashtags": ["#사랑", "#기쁨", "#축하"],
  "english_description": "Beautiful Rose flower",
  "emotions": [
    {"emotion": "사랑", "percentage": 40.0},
    {"emotion": "기쁨", "percentage": 30.0},
    {"emotion": "축하", "percentage": 30.0}
  ],
  "season_detail": {
    "availability": "Spring/Summer",
    "best_season": "03-08"
  },
  "composition": {
    "main_flower": "장미",
    "sub_flowers": ["리시안셔스", "안개꽃"],
    "composition_name": "로맨틱 부케"
  },
  "created_at": "2025.09.30.",
  "your_story": "첫사랑에게 고백하려고 해요. 수줍고 설레는 마음을 담아서 핑크나 화이트 톤이 좋겠어요.",
  "comment": "첫사랑에게 고백하는 특별한 순간을 위해 장미를 선택했습니다. 장미는 사랑과 진심을 상징하며, 핑크 색상은 수줍고 설레는 마음을 아름답게 표현합니다."
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

### 추천 결과 조회 (공유용)
```javascript
GET /api/v1/recommend/{story_id}
```

**사용 시나리오:**
- 추천 생성 후 `story_id`를 받아서 저장
- 공유할 때 `story_id`로 추천 결과 조회
- 저장된 스냅샷 데이터 반환

### 고급 조회 (분석용)
```javascript
GET /api/v1/advanced/recommend/{story_id}
```

**고급 기능:**
- 기본 조회 + 추가 메타데이터
- `retrieved_at`, `status` 등 분석 정보
- 추천 품질 평가 데이터

### 고급 통계 조회
```javascript
GET /api/v1/advanced/stats
```
