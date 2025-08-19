# API 참조 문서

## 📋 개요

이 문서는 꽃 추천 시스템의 모든 API 엔드포인트에 대한 상세한 참조 정보를 제공합니다.

## 🔗 기본 URL

```
http://localhost:8000
```

## 🔐 인증

현재 모든 API는 인증이 필요하지 않습니다.

## 📊 응답 형식

모든 API 응답은 JSON 형식으로 반환됩니다.

### 성공 응답
```json
{
  "recommendations": [...],
  "status": "success"
}
```

### 오류 응답
```json
{
  "error": "오류 메시지",
  "status": "error",
  "code": 400
}
```

## 🚀 API 엔드포인트

### 1. 꽃 추천 API

고객의 이야기와 예산을 바탕으로 꽃다발을 추천합니다.

**엔드포인트:** `POST /api/v1/recommend`

**요청 본문:**
```json
{
  "story": "string",     // 고객의 이야기 (필수)
  "budget": "integer"    // 예산 (선택, 기본값: 50000)
}
```

**응답:**
```json
{
  "recommendations": [
    {
      "id": "string",                    // 추천 ID
      "template_id": "string",           // 템플릿 ID
      "name": "string",                  // 추천 이름
      "main_flowers": ["string"],        // 메인 꽃 목록
      "sub_flowers": ["string"],         // 서브 꽃 목록
      "color_theme": ["string"],         // 컬러 테마
      "estimated_price": "integer",      // 예상 가격
      "reason": "string",                // 추천 이유
      "image_url": "string"              // 이미지 URL
    }
  ]
}
```

**예시:**
```bash
curl -X POST "http://localhost:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "story": "친구가 갑작스럽게 반려견을 떠나보냈어요. 차분하고 위로가 되는 색감이면 좋겠어요.",
    "budget": 50000
  }'
```

### 2. 맥락 추출 API

고객의 이야기에서 감정, 상황, 무드, 색상을 추출합니다.

**엔드포인트:** `POST /api/v1/context-extraction`

**요청 본문:**
```json
{
  "story": "string"    // 고객의 이야기 (필수)
}
```

**응답:**
```json
{
  "emotions": ["string"],      // 추출된 감정 목록
  "situations": ["string"],    // 추출된 상황 목록
  "moods": ["string"],         // 추출된 무드 목록
  "colors": ["string"],        // 추출된 색상 목록
  "confidence": "float"        // 신뢰도 (0.0-1.0)
}
```

**예시:**
```bash
curl -X POST "http://localhost:8000/api/v1/context-extraction" \
  -H "Content-Type: application/json" \
  -d '{
    "story": "첫사랑에게 고백하려고 해요. 진심어린 사랑을 전하고 싶어요."
  }'
```

### 3. 키워드 추출 API

텍스트에서 관련 키워드를 추출합니다.

**엔드포인트:** `POST /api/v1/keywords`

**요청 본문:**
```json
{
  "text": "string"    // 분석할 텍스트 (필수)
}
```

**응답:**
```json
{
  "keywords": ["string"]    // 추출된 키워드 목록
}
```

**예시:**
```bash
curl -X POST "http://localhost:8000/api/v1/keywords" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "회사 동료가 승진했어요. 축하하고 싶어요."
  }'
```

## 📊 데이터 모델

### RecommendRequest
```json
{
  "story": "string",     // 고객의 이야기
  "budget": "integer"    // 예산 (기본값: 50000)
}
```

### RecommendResponse
```json
{
  "recommendations": [
    {
      "id": "string",
      "template_id": "string",
      "name": "string",
      "main_flowers": ["string"],
      "sub_flowers": ["string"],
      "color_theme": ["string"],
      "estimated_price": "integer",
      "reason": "string",
      "image_url": "string"
    }
  ]
}
```

### ContextExtractionRequest
```json
{
  "story": "string"    // 고객의 이야기
}
```

### ContextExtractionResponse
```json
{
  "emotions": ["string"],
  "situations": ["string"],
  "moods": ["string"],
  "colors": ["string"],
  "confidence": "float"
}
```

### KeywordRequest
```json
{
  "text": "string"    // 분석할 텍스트
}
```

### KeywordResponse
```json
{
  "keywords": ["string"]
}
```

## 🔍 오류 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 422 | 유효성 검사 실패 |
| 500 | 서버 내부 오류 |

## 📝 사용 예시

### JavaScript (Fetch API)
```javascript
// 꽃 추천 요청
async function getRecommendation(story, budget) {
  const response = await fetch('/api/v1/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: story,
      budget: budget
    })
  });
  
  return await response.json();
}

// 맥락 추출 요청
async function extractContext(story) {
  const response = await fetch('/api/v1/context-extraction', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: story
    })
  });
  
  return await response.json();
}
```

### Python (requests)
```python
import requests

# 꽃 추천 요청
def get_recommendation(story, budget):
    response = requests.post(
        'http://localhost:8000/api/v1/recommend',
        json={
            'story': story,
            'budget': budget
        }
    )
    return response.json()

# 맥락 추출 요청
def extract_context(story):
    response = requests.post(
        'http://localhost:8000/api/v1/context-extraction',
        json={
            'story': story
        }
    )
    return response.json()
```

### cURL
```bash
# 꽃 추천
curl -X POST "http://localhost:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "story": "친구가 갑작스럽게 반려견을 떠나보냈어요.",
    "budget": 50000
  }'

# 맥락 추출
curl -X POST "http://localhost:8000/api/v1/context-extraction" \
  -H "Content-Type: application/json" \
  -d '{
    "story": "첫사랑에게 고백하려고 해요."
  }'

# 키워드 추출
curl -X POST "http://localhost:8000/api/v1/keywords" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "회사 동료가 승진했어요."
  }'
```

## 🔧 개발 도구

### Swagger UI
API 문서를 시각적으로 확인할 수 있습니다:
```
http://localhost:8000/docs
```

### ReDoc
대안 API 문서:
```
http://localhost:8000/redoc
```

## 📊 성능 정보

### 응답 시간
- **꽃 추천 API**: 평균 4-5초
- **맥락 추출 API**: 평균 2-3초
- **키워드 추출 API**: 평균 1초 이내

### 처리량
- **동시 요청**: 최대 10개
- **일일 요청**: 제한 없음

### 제한사항
- **요청 본문 크기**: 최대 1MB
- **텍스트 길이**: 최대 1000자

## 🔄 버전 관리

현재 API 버전: `v1`

버전 변경 시 하위 호환성을 유지합니다.

---

*마지막 업데이트: 2025-08-15*



