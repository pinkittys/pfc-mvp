# Plain Flower Club API 문서

## 🚀 서버 정보

### 프로덕션 환경
- **API 서버**: `https://plainflowerclub.com`
- **API 문서**: `https://plainflowerclub.com/docs` (Swagger UI)
- **헬스체크**: `https://plainflowerclub.com/health`

### 개발 환경
- **API 서버**: `https://dev.plainflowerclub.com`
- **API 문서**: `https://dev.plainflowerclub.com/docs` (Swagger UI)
- **헬스체크**: `https://dev.plainflowerclub.com/health`

## 📋 주요 엔드포인트

### 1. 꽃 추천 분석
```
POST /api/v1/analyze
Content-Type: application/json

Request Body:
{
  "story": "엄마 생신에 꽃을 선물하고 싶어요",
  "preferred_colors": ["pink", "white"],
  "excluded_flowers": [],
  "top_k": 1
}

Response:
{
  "recommendations": [
    {
      "id": "flower_001",
      "name": "핑크 카네이션",
      "main_flowers": ["Carnation"],
      "color_theme": ["pink"],
      "reason": "엄마를 위한 따뜻한 마음을 담은 추천",
      "image_url": "https://..."
    }
  ]
}
```

### 2. 스토리 관리
```
GET /api/v1/stories - 스토리 목록 조회
POST /api/v1/stories - 새 스토리 생성
GET /api/v1/stories/{story_id} - 특정 스토리 조회
```

### 3. 키워드 추출
```
POST /api/v1/extract_keywords
Content-Type: application/json

Request Body:
{
  "story": "친구 생일에 축하 꽃을 선물하고 싶어요"
}

Response:
{
  "keywords": ["친구", "생일", "축하"],
  "mood_tags": ["bright", "cheerful"],
  "occasion": "birthday"
}
```

## 🔧 환경 설정

### CORS 설정
- **허용된 Origin**: `*` (모든 도메인)
- **허용된 Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **허용된 Headers**: `*`

### 인증
- 현재 인증 없음 (공개 API)
- 향후 JWT 토큰 인증 예정

## 📱 프론트엔드 연동 예시

### JavaScript (Fetch API)
```javascript
// 환경별 API 서버 설정
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://plainflowerclub.com' 
  : 'https://dev.plainflowerclub.com';

// 꽃 추천 요청
async function getFlowerRecommendation(story) {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: story,
      preferred_colors: [],
      excluded_flowers: [],
      top_k: 1
    })
  });
  
  const data = await response.json();
  return data.recommendations[0];
}

// 사용 예시
const recommendation = await getFlowerRecommendation("엄마 생신에 꽃을 선물하고 싶어요");
console.log(recommendation);
```

### React Hook 예시
```javascript
import { useState, useEffect } from 'react';

// 환경별 API 서버 설정
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://plainflowerclub.com' 
  : 'https://dev.plainflowerclub.com';

function useFlowerRecommendation() {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendation = async (story) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story: story,
          preferred_colors: [],
          excluded_flowers: [],
          top_k: 1
        })
      });
      
      const data = await response.json();
      setRecommendation(data.recommendations[0]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { recommendation, loading, error, getRecommendation };
}
```

## 🎨 현재 사용 가능한 페이지들

### 프로덕션 환경
- **웹 인터페이스**: `https://plainflowerclub.com/simple_test.html`
- **관리자 패널**: `https://plainflowerclub.com/admin_panel.html`

### 개발 환경
- **웹 인터페이스**: `https://dev.plainflowerclub.com/simple_test.html`
- **관리자 패널**: `https://dev.plainflowerclub.com/admin_panel.html`

## 📞 문의사항

- **API 관련 문의**: 개발팀
- **문서 업데이트**: GitHub Issues
- **실시간 테스트**: Swagger UI (`/docs`)

## 🔄 환경별 사용 가이드

### 개발 시
- **API 서버**: `https://dev.plainflowerclub.com`
- **테스트 페이지**: `https://dev.plainflowerclub.com/simple_test.html`
- **환경변수**: `NODE_ENV=development`

### 프로덕션 배포 시
- **API 서버**: `https://plainflowerclub.com`
- **환경변수**: `NODE_ENV=production`

---

**버전**: 1.1.0  
**최종 업데이트**: 2024년 12월  
**작성자**: Floiy Development Team
