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
  "english_description": "A radiant sunflower that symbolizes new beginnings and unwavering support for your friend's journey ahead.",
  "emotions": [
    {"emotion": "응원/격려", "percentage": 60.0},
    {"emotion": "감사/존경", "percentage": 40.0}
  ],
  "seasonality": ["여름", "가을"],
  "composition": {
    "main_flower": "해바라기",
    "accent_flowers": ["베이비브레스", "거베라"],
    "greenery": ["아스파라거스", "몬스테라"]
  },
  "your_story": "친구가 이직하게 되었어요. 새로운 시작을 응원하는 마음을 담아 꽃을 선물하고 싶어요.",
  "comment": "친구의 새로운 시작을 응원하는 마음에 밝은 해바라기가 완벽하게 어울려요. 이 꽃은 '성공'과 '희망'의 의미를 담고 있어, 새로운 도전을 시작하는 친구에게 큰 힘이 될 거예요.",
  "story_id": "S250822-SUN-00001"
}
```

---

## 📊 응답 필드 설명

### 추천 결과 응답 필드

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `flower_name` | string | 꽃 영문명 |
| `korean_name` | string | 꽃 한글명 |
| `scientific_name` | string | 꽃 학명 |
| `image_url` | string | 꽃 이미지 URL |
| `hashtags` | array | 관련 해시태그 목록 |
| `english_description` | string | 영문 추천 문구 |
| `emotions` | array | 감정 분석 결과 (감정명, 비율) |
| `seasonality` | array | 꽃의 계절 정보 |
| `composition` | object | 꽃 구성 정보 |
| `your_story` | string | 사용자가 입력한 사연 |
| `comment` | string | 추천 이유 (한글) |
| `story_id` | string | 스토리 고유 ID |

### 구성 정보 필드

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `main_flower` | string | 메인 꽃 |
| `accent_flowers` | array | 액센트 꽃들 |
| `greenery` | array | 그린리 (잎) |

---

## 🔧 사용 예시

### JavaScript (Fetch API)
```javascript
// 1. 샘플 사연 가져오기
const getSampleStories = async () => {
  const response = await fetch('https://api.plainflowerclub.com/api/v1/sample-stories', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  });
  return await response.json();
};

// 2. 키워드 추출
const extractKeywords = async (story) => {
  const response = await fetch('https://api.plainflowerclub.com/api/v1/extract-keywords', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: story,
      preferred_colors: [],
      excluded_flowers: []
    })
  });
  return await response.json();
};

// 3. 추천 결과 받기
const getRecommendation = async (story, colors) => {
  const response = await fetch('https://api.plainflowerclub.com/api/v1/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: story,
      preferred_colors: colors,
      excluded_flowers: [],
      updated_context: {
        colors: colors
      }
    })
  });
  return await response.json();
};
```

### React Hook 예시
```javascript
import { useState, useEffect } from 'react';

const useFlowerRecommendation = () => {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendation = async (story, colors = []) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('https://api.plainflowerclub.com/api/v1/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story,
          preferred_colors: colors,
          excluded_flowers: [],
          updated_context: { colors }
        })
      });
      
      if (!response.ok) {
        throw new Error('추천 요청 실패');
      }
      
      const data = await response.json();
      setRecommendation(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { recommendation, loading, error, getRecommendation };
};
```

---

## 🚨 에러 처리

### HTTP 상태 코드
- `200`: 성공
- `400`: 잘못된 요청
- `429`: 요청이 너무 빠름 (디바운싱)
- `500`: 서버 오류

### 에러 응답 예시
```json
{
  "detail": "요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요."
}
```

---

## 📝 개발 가이드

### 1. 개발 환경 설정
```javascript
// 개발 환경에서는 로컬 API 사용
const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000' 
  : 'https://api.plainflowerclub.com';
```

### 2. 요청 최적화
- 키워드 추출은 실시간으로 호출
- 추천 결과는 사용자가 최종 결정할 때만 호출
- 중복 요청 방지를 위해 디바운싱 적용

### 3. 이미지 처리
- 이미지 URL은 Supabase Storage에서 제공
- 이미지 로딩 실패 시 기본 이미지 표시
- 이미지 최적화를 위해 WebP 형식 사용

---

## 🔄 마이그레이션 가이드

### 기존 엔드포인트 → 새로운 엔드포인트

| 기존 | 새로운 |
|------|--------|
| `/api/v1/emotion-analysis` | `/api/v1/recommend` |
| `/api/v1/extract-context` | `/api/v1/extract-keywords` |
| `/api/v1/fast-context` | `/api/v1/extract-keywords` |
| `/api/v1/flower-season/{name}` | `/api/v1/recommend` (seasonality 포함) |

### 주요 변경사항
1. **단순화**: 8개 → 3개 엔드포인트
2. **통합**: 모든 추천 정보를 한 번에 제공
3. **표준화**: 일관된 응답 형식
4. **최적화**: 중복 요청 방지 및 캐싱

---

**문의사항**: 개발팀에 문의하세요! 🌸
