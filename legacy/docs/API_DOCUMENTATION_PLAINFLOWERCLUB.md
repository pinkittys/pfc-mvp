# 🌸 Plain Flower Club API 문서

## 📋 개요
Plain Flower Club는 사용자의 감정과 상황에 맞는 꽃을 추천해주는 서비스입니다.

**Base URL**: `https://plainflowerclub.com/api/v1`

## 🔑 인증
현재 API는 인증이 필요하지 않습니다. (개발 단계)

## 📡 API 엔드포인트

### 1. 감정 분석 및 꽃 추천

#### POST `/emotion-analysis`
사용자의 이야기를 분석하여 감정을 추출하고 꽃을 추천합니다.

**Request Body:**
```json
{
  "story": "친구의 생일을 축하하고 싶어요. 밝고 활기찬 분위기의 꽃다발을 원해요.",
  "recipient_emotion": "기쁨",
  "relationship": "친구",
  "occasion": "생일"
}
```

**Response:**
```json
{
  "success": true,
  "recommendation": {
    "primary_flower": {
      "name": "Gerbera Daisy",
      "korean_name": "거베라",
      "color": "옐로우",
      "image_url": "https://plainflowerclub.com/images/gerbera-daisy/옐로우.webp",
      "meaning": "기쁨과 희망을 상징하는 밝은 꽃입니다."
    },
    "secondary_flowers": [
      {
        "name": "Dahlia",
        "korean_name": "달리아",
        "color": "핑크",
        "image_url": "https://plainflowerclub.com/images/dahlia/핑크.webp"
      }
    ],
    "reason": "친구의 생일을 축하하는 밝고 활기찬 분위기에 완벽한 조합입니다. 거베라는 기쁨과 희망을, 달리아는 우아함과 감사를 표현합니다.",
    "keywords": {
      "emotions": ["기쁨", "감사"],
      "situations": ["생일", "축하"],
      "moods": ["밝은", "활기찬"],
      "colors": ["옐로우", "핑크"]
    }
  }
}
```

### 2. 실시간 컨텍스트 추출

#### POST `/extract-context`
사용자의 이야기에서 실시간으로 키워드를 추출합니다.

**Request Body:**
```json
{
  "story": "새해 첫날, 가족과 함께 시작을 기념할 수 있는 희망적인 꽃이 필요해요."
}
```

**Response:**
```json
{
  "success": true,
  "context": {
    "intent": "기념",
    "situation": "새해",
    "sender_emotion": "희망",
    "receiver_emotion": "기대",
    "relationship": "가족",
    "mood": "희망적인",
    "colors": ["화이트", "옐로우"]
  }
}
```

### 3. 꽃 정보 조회

#### GET `/flower-info/{flower_name}`
특정 꽃의 상세 정보를 조회합니다.

**Response:**
```json
{
  "success": true,
  "flower": {
    "name": "Rose",
    "korean_name": "장미",
    "scientific_name": "Rosa",
    "colors": ["레드", "핑크", "화이트", "옐로우"],
    "meanings": {
      "레드": ["사랑", "열정"],
      "핑크": ["우아함", "감사"],
      "화이트": ["순수", "신뢰"],
      "옐로우": ["우정", "기쁨"]
    },
    "season": "봄-가을",
    "care_tips": "시원한 곳에 보관하고 정기적으로 물을 갈아주세요."
  }
}
```

### 4. 꽃 시즌 정보

#### GET `/flower-season/{flower_name}`
특정 꽃의 시즌 정보를 조회합니다.

**Response:**
```json
{
  "success": true,
  "season": {
    "flower_name": "Tulip",
    "peak_season": "봄",
    "available_months": [3, 4, 5],
    "seasonal_meaning": "새로운 시작과 희망을 상징합니다."
  }
}
```

### 5. 이미지 URL 조회

#### GET `/flower-images/{flower_name}`
특정 꽃의 모든 색상 이미지를 조회합니다.

**Response:**
```json
{
  "success": true,
  "images": [
    {
      "color": "레드",
      "url": "https://plainflowerclub.com/images/rose/레드.webp",
      "base64": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4..."
    },
    {
      "color": "핑크",
      "url": "https://plainflowerclub.com/images/rose/핑크.webp",
      "base64": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4..."
    }
  ]
}
```

## 🎨 이미지 URL 패턴

### 기본 패턴
```
https://plainflowerclub.com/images/{flower-folder}/{color}.webp
```

### 예시
- `https://plainflowerclub.com/images/rose/레드.webp`
- `https://plainflowerclub.com/images/gerbera-daisy/옐로우.webp`
- `https://plainflowerclub.com/images/tulip/화이트.webp`

## 📊 데이터 모델

### Flower Object
```typescript
interface Flower {
  name: string;           // 영문 이름
  korean_name: string;    // 한글 이름
  scientific_name: string; // 학명
  color: string;          // 색상
  image_url: string;      // 이미지 URL
  meaning: string;        // 꽃말
  season?: string;        // 시즌
  care_tips?: string;     // 관리 팁
}
```

### Recommendation Object
```typescript
interface Recommendation {
  primary_flower: Flower;
  secondary_flowers: Flower[];
  reason: string;
  keywords: {
    emotions: string[];
    situations: string[];
    moods: string[];
    colors: string[];
  };
}
```

### Context Object
```typescript
interface Context {
  intent: string;
  situation: string;
  sender_emotion: string;
  receiver_emotion: string;
  relationship: string;
  mood: string;
  colors: string[];
}
```

## 🔄 실시간 키워드 추출 사용법

### JavaScript 예시
```javascript
// 실시간 키워드 추출
async function extractKeywords(story) {
  const response = await fetch('https://plainflowerclub.com/api/v1/extract-context', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ story })
  });
  
  const data = await response.json();
  return data.context;
}

// 디바운싱을 사용한 실시간 추출
let debounceTimer;
function startRealtimeExtraction(story) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    const keywords = await extractKeywords(story);
    displayKeywords(keywords);
  }, 1000); // 1초 딜레이
}
```

## 🎯 추천 로직

### 우선순위
1. **감정 기반**: 사용자의 감정과 가장 잘 맞는 꽃
2. **상황 기반**: 특별한 상황(생일, 고백 등)에 적합한 꽃
3. **색상 기반**: 요청된 색상이 있는 꽃
4. **계절 기반**: 현재 계절에 맞는 꽃

### 특별한 상황 처리
- **반려동물 상실**: 위로와 슬픔을 표현하는 화이트/블루 계열
- **고백**: 로맨틱한 레드/핑크 계열
- **축하**: 밝고 활기찬 옐로우/오렌지 계열

## 🚨 에러 처리

### 에러 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "입력값이 올바르지 않습니다.",
    "details": "story 필드는 필수입니다."
  }
}
```

### 주요 에러 코드
- `INVALID_INPUT`: 입력값 오류
- `FLOWER_NOT_FOUND`: 꽃을 찾을 수 없음
- `ANALYSIS_FAILED`: 감정 분석 실패
- `SERVER_ERROR`: 서버 내부 오류

## 📱 프론트엔드 통합 예시

### React 예시
```jsx
import React, { useState, useEffect } from 'react';

function FlowerRecommendation() {
  const [story, setStory] = useState('');
  const [keywords, setKeywords] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  // 실시간 키워드 추출
  useEffect(() => {
    if (story.length > 10) {
      const timer = setTimeout(async () => {
        try {
          const response = await fetch('https://plainflowerclub.com/api/v1/extract-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ story })
          });
          const data = await response.json();
          setKeywords(data.context);
        } catch (error) {
          console.error('키워드 추출 실패:', error);
        }
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [story]);

  // 꽃 추천 요청
  const getRecommendation = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://plainflowerclub.com/api/v1/emotion-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story })
      });
      const data = await response.json();
      setRecommendation(data.recommendation);
    } catch (error) {
      console.error('추천 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        value={story}
        onChange={(e) => setStory(e.target.value)}
        placeholder="꽃을 받을 사람에 대해 이야기해주세요..."
      />
      
      {keywords && (
        <div className="keywords">
          <h3>추출된 키워드</h3>
          <div>감정: {keywords.emotions.join(', ')}</div>
          <div>상황: {keywords.situations.join(', ')}</div>
          <div>분위기: {keywords.moods.join(', ')}</div>
          <div>색상: {keywords.colors.join(', ')}</div>
        </div>
      )}
      
      <button onClick={getRecommendation} disabled={loading}>
        {loading ? '추천 중...' : '꽃 추천받기'}
      </button>
      
      {recommendation && (
        <div className="recommendation">
          <h3>추천 꽃</h3>
          <img src={recommendation.primary_flower.image_url} alt={recommendation.primary_flower.korean_name} />
          <h4>{recommendation.primary_flower.korean_name}</h4>
          <p>{recommendation.reason}</p>
        </div>
      )}
    </div>
  );
}
```

## 🔧 개발 환경 설정

### 로컬 개발
```bash
# 1. 저장소 클론
git clone <repository-url>
cd floiy-reco

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
export OPENAI_API_KEY="your-openai-api-key"

# 4. 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker 배포
```bash
# 1. 배포 스크립트 실행
./deploy_plainflowerclub.sh

# 2. 로그 확인
docker-compose logs -f

# 3. 서비스 중지
docker-compose down
```

## 📞 지원 및 문의

- **API 문서**: `https://plainflowerclub.com/docs`
- **관리자 퍼널**: `https://plainflowerclub.com/admin/`
- **메인 사이트**: `https://plainflowerclub.com`
- **이슈 리포트**: GitHub Issues

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 12월  
**문서 작성자**: Plain Flower Club Development Team

