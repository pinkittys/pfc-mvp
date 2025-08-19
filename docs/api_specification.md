# API 명세서 (디자이너 & 프론트엔드 개발자용)

## 🎯 개요
Floiy-Reco 꽃다발 추천 시스템의 API 명세서입니다.

## 📡 API 엔드포인트

### 1. 꽃다발 추천 API
**POST** `/api/v1/recommendations`

#### 요청 (Request)
```json
{
  "story": "첫사랑에게 고백하려고 해요. 수줍고 설레는 마음을 담아서 핑크나 화이트 톤이 좋겠어요.",
  "preferred_colors": ["핑크", "화이트"],
  "excluded_flowers": [],
  "top_k": 1
}
```

#### 응답 (Response)
```json
{
  "recommendations": [
    {
      "id": "R001",
      "template_id": "장미",
      "name": "추천 꽃다발",
      "main_flowers": ["장미"],
      "sub_flowers": ["리시안셔스"],
      "color_theme": ["핑크", "화이트"],
      "reason": "첫사랑에게 고백하는 특별한 순간을 위해 장미를 선택했습니다. 장미는 사랑과 진심을 상징하며, 핑크와 화이트의 조화는 수줍고 설레는 마음을 아름답게 표현합니다. 이 꽃다발이 고객님의 진심어린 마음을 전달하는 완벽한 메신저가 될 것입니다.",
      "image_url": "/static/images/rose/pink.webp"
    }
  ]
}
```

### 2. 맥락 추출 API (선택사항)
**POST** `/api/v1/context-extraction`

#### 요청 (Request)
```json
{
  "story": "친구가 갑작스럽게 반려견을 떠나보냈어요. 차분하고 위로가 되는 색감이면 좋겠어요."
}
```

#### 응답 (Response)
```json
{
  "emotions": ["슬픔", "그리움"],
  "situations": ["애도", "위로"],
  "moods": ["차분한", "따뜻한"],
  "colors": ["따뜻한 톤"],
  "confidence": 0.90
}
```

### 3. 사연 샘플 API
**GET** `/api/v1/samples`

#### 요청 (Request)
```
GET /api/v1/samples?count=50
```

#### 응답 (Response)
```json
[
  {
    "id": "sample_1",
    "text": "예전에 이 친구랑 파리 여행 갔던 게 기억나. 그때 분위기를 담고 싶어.",
    "category": "추억",
    "tags": ["여행", "추억", "로맨틱", "파리"]
  },
  {
    "id": "sample_2",
    "text": "조용하고 차분한 성격에 책 읽는 걸 좋아하는 친구에게 선물하고 싶어.",
    "category": "친구",
    "tags": ["차분한", "책", "친구", "은은한"]
  }
]
```

### 4. 실시간 맥락 추출 API (WebSocket)
**WebSocket** `/api/v1/realtime/ws/context-extraction`

#### 연결
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws/context-extraction');
```

#### 텍스트 입력 전송
```json
{
  "type": "text_input",
  "text": "사용자가 입력한 텍스트"
}
```

#### 실시간 응답
```json
{
  "type": "context_update",
  "context": {
    "emotions": ["사랑", "설렘"],
    "situations": ["고백", "첫사랑"],
    "moods": ["수줍은", "따뜻한"],
    "colors": ["핑크", "화이트"],
    "confidence": 0.95
  },
  "keywords": ["사랑", "설렘", "고백", "첫사랑", "수줍은", "따뜻한", "핑크", "화이트"]
}
```

## 🎨 UI/UX 가이드라인

### 1. 메인 화면 구성
```
┌─────────────────────────────────────┐
│           Floiy-Reco               │
├─────────────────────────────────────┤
│                                     │
│  💬 고객님의 이야기를 들려주세요    │
│  ┌─────────────────────────────────┐ │
│  │                                 │ │
│  │ [스토리 입력 텍스트 영역]        │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  🎨 선호하는 색상 (선택사항)        │
│  [핑크] [레드] [화이트] [블루] ...  │
│                                     │
│  [꽃다발 추천받기] 버튼             │
│                                     │
└─────────────────────────────────────┘
```

### 2. 추천 결과 화면
```
┌─────────────────────────────────────┐
│           추천 결과                 │
├─────────────────────────────────────┤
│                                     │
│  🌸 추천 꽃다발                     │
│  ┌─────────────────────────────────┐ │
│  │                                 │ │
│  │        [꽃다발 이미지]          │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  📝 구성 정보                       │
│  • 메인 꽃: 장미                    │
│  • 서브 꽃: 리시안셔스              │
│  • 컬러 테마: 핑크, 화이트          │
│                                     │
│  💌 추천 이유                       │
│  [전문적이고 따뜻한 메시지]         │
│                                     │
│  [다시 추천받기] [공유하기]         │
│                                     │
└─────────────────────────────────────┘
```

### 3. 색상 팔레트
- **핑크 계열**: #FFB6C1, #FFC0CB, #FF69B4
- **레드 계열**: #DC143C, #B22222, #8B0000
- **화이트 계열**: #FFFFFF, #F5F5F5, #F8F8FF
- **블루 계열**: #4169E1, #1E90FF, #00BFFF
- **옐로우 계열**: #FFD700, #FFA500, #FF8C00
- **퍼플 계열**: #9370DB, #8A2BE2, #9932CC

### 4. 폰트 가이드라인
- **제목**: Pretendard Bold, 24px
- **부제목**: Pretendard SemiBold, 18px
- **본문**: Pretendard Regular, 16px
- **설명**: Pretendard Light, 14px

### 5. 반응형 디자인
- **모바일**: 320px ~ 768px
- **태블릿**: 768px ~ 1024px
- **데스크톱**: 1024px 이상

## 🔧 개발 가이드라인

### 1. 에러 처리
```javascript
// API 호출 예시
try {
  const response = await fetch('/api/v1/recommendations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      story: userStory,
      preferred_colors: selectedColors,
      excluded_flowers: excludedFlowers,
      top_k: 1
    })
  });
  
  if (!response.ok) {
    throw new Error('추천 요청에 실패했습니다.');
  }
  
  const data = await response.json();
  // 추천 결과 처리
  
} catch (error) {
  // 에러 처리
  console.error('Error:', error);
  showErrorMessage('추천 시스템에 일시적인 문제가 발생했습니다.');
}
```

### 2. 로딩 상태
- API 호출 시 로딩 스피너 표시
- 추천 생성 시간: 평균 3-5초
- 타임아웃: 30초

### 3. 이미지 처리
- 이미지 형식: WebP (권장), JPG, PNG
- 이미지 크기: 4:5 비율 (800x1000px 권장)
- 이미지 최적화: 압축 및 lazy loading 적용

## 📱 모바일 최적화

### 1. 터치 인터페이스
- 버튼 최소 크기: 44x44px
- 터치 간격: 8px 이상
- 스와이프 제스처 지원

### 2. 성능 최적화
- 이미지 lazy loading
- API 응답 캐싱
- 번들 크기 최적화

## 🎨 브랜딩 가이드라인

### 1. 로고
- 메인 로고: Floiy-Reco
- 서브 로고: 꽃 아이콘 + 텍스트

### 2. 브랜드 컬러
- **Primary**: #FF6B9D (핑크)
- **Secondary**: #4ECDC4 (민트)
- **Accent**: #FFE66D (옐로우)
- **Neutral**: #2C3E50 (다크 그레이)

### 3. 일러스트레이션 스타일
- 부드럽고 따뜻한 톤
- 미니멀한 꽃 일러스트
- 파스텔 컬러 팔레트
