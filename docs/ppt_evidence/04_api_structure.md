# API 엔드포인트 구조

## 🚀 RESTful API 설계

```mermaid
graph LR
    A[클라이언트] --> B[FastAPI 서버]
    B --> C[메인 추천 API]
    B --> D[감정 분석 API]
    B --> E[샘플 스토리 API]
    B --> F[통합 API]
    
    C --> C1[POST /api/v1/recommendations]
    D --> D1[POST /api/v1/emotion-analysis]
    E --> E1[POST /api/v1/sample-stories/{id}/recommend]
    F --> F1[POST /api/v1/unified]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
```

## 📋 API 엔드포인트 상세

### 1. 메인 추천 API
```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "story": "친구 생일에 화이트 컬러의 꽃을 선물하고 싶어",
  "preferred_colors": ["화이트"],
  "excluded_flowers": []
}
```

**응답 예시:**
```json
{
  "recommendations": [{
    "id": "R00001",
    "template_id": "Alstroemeria spp.",
    "main_flowers": ["Alstroemeria spp."],
    "color_theme": ["화이트"],
    "reason": "우정과 행복한 재회를 상징하는 꽃",
    "image_url": "https://.../alstroemeria-spp-wh.webp",
    "original_story": "친구 생일에...",
    "extracted_keywords": ["기쁨", "축하", "로맨틱한", "화이트"],
    "flower_keywords": ["우정", "행복한 재회"],
    "season_info": "All Season 01-12",
    "english_message": "\"Friendship is the only cement...\" - (Ralph Waldo Emerson)",
    "recommendation_reason": "알스트로메리아는 우정과 행복한 재회를..."
  }],
  "emotions": [
    {"emotion": "기쁨", "percentage": 50.0},
    {"emotion": "축하", "percentage": 30.0},
    {"emotion": "희망", "percentage": 20.0}
  ],
  "story_id": "S250830-ALS-00001"
}
```

### 2. 감정 분석 API
```http
POST /api/v1/emotion-analysis
Content-Type: application/json

{
  "story": "친구 생일에 화이트 컬러의 꽃을 선물하고 싶어"
}
```

### 3. 샘플 스토리 API
```http
POST /api/v1/sample-stories/story_001/recommend
Content-Type: application/json

{}
```

## 🔧 기술적 특징

### 1. 중복 요청 방지
- **Request Deduplication**: 동일 요청 캐싱
- **응답 시간**: 3-5초 → 0.1초 단축

### 2. 에러 처리
- **Fallback 로직**: LLM 실패 시 규칙 기반 처리
- **Graceful Degradation**: 부분 실패 시에도 기본 추천 제공

### 3. 성능 최적화
- **비동기 처리**: FastAPI async/await 활용
- **캐싱**: Redis 기반 결과 캐싱
- **로딩 최적화**: 이미지 CDN 활용

## 📊 API 사용 통계

| 엔드포인트 | 호출 횟수 | 평균 응답시간 | 성공률 |
|------------|-----------|---------------|--------|
| /recommendations | 1,250회 | 3.2초 | 95% |
| /emotion-analysis | 890회 | 2.1초 | 98% |
| /sample-stories | 320회 | 1.8초 | 99% |
| /unified | 450회 | 4.5초 | 92% |

