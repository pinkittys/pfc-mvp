# 데이터 스키마 (프론트엔드 개발자용)

## 📊 데이터 구조

### 1. 추천 요청 (RecommendRequest)
```typescript
interface RecommendRequest {
  story: string;                    // 고객 스토리 (필수)
  preferred_colors?: string[];      // 선호 색상 (선택)
  excluded_flowers?: string[];      // 제외할 꽃 (선택)
  top_k?: number;                   // 추천 개수 (기본값: 1)
}
```

### 2. 추천 응답 (RecommendResponse)
```typescript
interface RecommendResponse {
  recommendations: RecommendationItem[];
}

interface RecommendationItem {
  id: string;                       // 추천 ID (예: "R001")
  template_id?: string;             // 템플릿 ID (메인 꽃명)
  name: string;                     // 추천 이름
  main_flowers: string[];           // 메인 꽃 목록
  sub_flowers: string[];            // 서브 꽃 목록
  color_theme: string[];            // 컬러 테마
  reason: string;                   // 추천 이유
  image_url: string;                // 이미지 URL
}
```

### 3. 맥락 추출 응답 (ContextExtractionResponse)
```typescript
interface ContextExtractionResponse {
  emotions: string[];               // 감정 목록
  situations: string[];             // 상황 목록
  moods: string[];                  // 무드 목록
  colors: string[];                 // 색상 목록
  confidence: number;               // 신뢰도 (0.0 ~ 1.0)
}
```

## 🌸 꽃 데이터

### 1. 지원하는 꽃 종류
```typescript
const FLOWER_TYPES = {
  // 메인 꽃 (focal=1)
  MAIN_FLOWERS: [
    '장미', '수국', '거베라', '튤립', '작약', '리시안셔스', '다알리아'
  ],
  
  // 서브 꽃 (중간 크기)
  SUB_FLOWERS: [
    '백합', '스토크', '천일홍'
  ],
  
  // 필러 꽃 (작은 꽃)
  FILLER_FLOWERS: [
    '마가렛', '부바르디아', '스카비오사'
  ],
  
  // 라인 꽃 (높이감)
  LINE_FLOWERS: [
    '골든볼', '맨드라미'
  ],
  
  // 그린 소재
  FOLIAGE: [
    '목화'
  ]
};
```

### 2. 지원하는 색상
```typescript
const COLOR_PALETTE = {
  // 기본 색상
  BASIC: [
    '레드', '핑크', '화이트', '옐로우', '블루', '퍼플', '오렌지'
  ],
  
  // 세부 색상
  DETAILED: [
    '빨간색', '분홍색', '흰색', '노란색', '파란색', '보라색', '주황색',
    '크림핑크', '라벤더', '다색', '라임그린'
  ]
};
```

## 🎨 UI 컴포넌트 데이터

### 1. 색상 선택 컴포넌트
```typescript
interface ColorOption {
  id: string;
  name: string;
  hex: string;
  isSelected: boolean;
}

const colorOptions: ColorOption[] = [
  { id: 'pink', name: '핑크', hex: '#FFB6C1', isSelected: false },
  { id: 'red', name: '레드', hex: '#DC143C', isSelected: false },
  { id: 'white', name: '화이트', hex: '#FFFFFF', isSelected: false },
  { id: 'yellow', name: '옐로우', hex: '#FFD700', isSelected: false },
  { id: 'blue', name: '블루', hex: '#4169E1', isSelected: false },
  { id: 'purple', name: '퍼플', hex: '#9370DB', isSelected: false }
];
```

### 2. 꽃 구성 표시 컴포넌트
```typescript
interface FlowerComposition {
  main: string[];      // 메인 꽃
  sub: string[];       // 서브 꽃
  filler: string[];    // 필러 꽃
  line: string[];      // 라인 꽃
  foliage: string[];   // 그린 소재
}

interface FlowerDisplay {
  name: string;
  role: 'main' | 'sub' | 'filler' | 'line' | 'foliage';
  color: string;
  quantity: number;
}
```

## 📱 상태 관리

### 1. 앱 상태 (AppState)
```typescript
interface AppState {
  // 사용자 입력
  userInput: {
    story: string;
    preferredColors: string[];
    excludedFlowers: string[];
  };
  
  // 추천 결과
  recommendation: {
    isLoading: boolean;
    data: RecommendationItem | null;
    error: string | null;
  };
  
  // UI 상태
  ui: {
    currentStep: 'input' | 'loading' | 'result' | 'error';
    selectedColors: string[];
  };
}
```

### 2. 로딩 상태
```typescript
interface LoadingState {
  isActive: boolean;
  message: string;
  progress?: number;  // 0-100
  estimatedTime?: number;  // 초 단위
}
```

## 🔄 API 통신

### 1. API 응답 타입
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
}
```

### 2. 에러 코드
```typescript
enum ErrorCode {
  INVALID_INPUT = 'INVALID_INPUT',
  API_TIMEOUT = 'API_TIMEOUT',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  RATE_LIMIT = 'RATE_LIMIT'
}
```

## 📊 로깅 및 분석

### 1. 사용자 행동 추적
```typescript
interface UserAction {
  action: 'story_input' | 'color_selection' | 'recommendation_request' | 'result_view';
  timestamp: string;
  data?: any;
  sessionId: string;
}
```

### 2. 추천 결과 분석
```typescript
interface RecommendationAnalytics {
  recommendationId: string;
  processingTime: number;  // 밀리초
  userSatisfaction?: number;  // 1-5 점수
  shareCount: number;
  viewCount: number;
}
```

## 🎯 사용 예시

### 1. 추천 요청
```typescript
const requestRecommendation = async (story: string, colors: string[]) => {
  try {
    const response = await fetch('/api/v1/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        story,
        preferred_colors: colors,
        excluded_flowers: [],
        top_k: 1
      })
    });
    
    const data: RecommendResponse = await response.json();
    return data.recommendations[0];
  } catch (error) {
    console.error('추천 요청 실패:', error);
    throw error;
  }
};
```

### 2. 결과 표시
```typescript
const displayRecommendation = (recommendation: RecommendationItem) => {
  return {
    mainFlower: recommendation.main_flowers[0],
    subFlowers: recommendation.sub_flowers,
    colorTheme: recommendation.color_theme,
    reason: recommendation.reason,
    imageUrl: recommendation.image_url
  };
};
```


