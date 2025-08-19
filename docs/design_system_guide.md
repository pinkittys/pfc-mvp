# 디자인 시스템 가이드 (디자이너용)

## 🎨 브랜드 아이덴티티

### 1. 브랜드 컨셉
- **브랜드명**: PlainFlowerClub
- **핵심 가치**: 따뜻함, 진심, 아름다움
- **톤앤매너**: 부드럽고 감성적, 전문적이면서 친근한
- **타겟**: 감정을 중요시하는 20-40대 여성
- **버전**: 0.82ver beta (현재 개발 버전)

### 2. 브랜드 컬러
```css
/* Primary Colors */
--primary-pink: #FF6B9D;      /* 메인 핑크 */
--primary-mint: #4ECDC4;      /* 서브 민트 */
--accent-yellow: #FFE66D;     /* 액센트 옐로우 */

/* Neutral Colors */
--neutral-dark: #2C3E50;      /* 다크 그레이 */
--neutral-light: #F8F9FA;     /* 라이트 그레이 */
--neutral-white: #FFFFFF;     /* 화이트 */

/* Semantic Colors */
--success: #28A745;           /* 성공 */
--warning: #FFC107;           /* 경고 */
--error: #DC3545;             /* 에러 */
--info: #17A2B8;              /* 정보 */
```

### 3. 타이포그래피
```css
/* Font Family */
--font-primary: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
--font-serif: 'Times New Roman', serif;  /* 메인 헤드라인용 */

/* Font Weights */
--font-light: 300;
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Font Sizes */
--text-xs: 12px;      /* 캡션, 버전 정보 */
--text-sm: 14px;      /* 설명, 서브타이틀 */
--text-base: 16px;    /* 본문, 입력 텍스트 */
--text-lg: 18px;      /* 부제목 */
--text-xl: 20px;      /* 제목 */
--text-2xl: 24px;     /* 대제목 */
--text-3xl: 32px;     /* 헤드라인 */
```

## 🎯 컴포넌트 시스템

### 1. 버튼 (Button)
```css
/* Primary Button */
.btn-primary {
  background: var(--primary-pink);
  color: white;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: var(--font-semibold);
  transition: all 0.2s ease;
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: var(--primary-pink);
  border: 2px solid var(--primary-pink);
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: var(--font-semibold);
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: var(--neutral-dark);
  border: none;
  padding: 8px 16px;
  font-weight: var(--font-medium);
}
```

### 2. 입력 필드 (Input)
```css
/* Text Input */
.input-field {
  border: 2px solid #E9ECEF;
  border-radius: 12px;
  padding: 16px;
  font-size: var(--text-base);
  transition: border-color 0.2s ease;
}

.input-field:focus {
  border-color: var(--primary-pink);
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
}

/* Textarea */
.textarea-field {
  border: 2px solid #E9ECEF;
  border-radius: 12px;
  padding: 16px;
  font-size: var(--text-base);
  min-height: 120px;
  resize: vertical;
}
```

### 3. 카드 (Card)
```css
/* Recommendation Card */
.card-recommendation {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #F1F3F4;
}

/* Image Card */
.card-image {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}
```

### 4. 색상 선택기 (Color Picker)
```css
/* Color Option */
.color-option {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-option.selected {
  border-color: var(--primary-pink);
  transform: scale(1.1);
}

.color-option:hover {
  transform: scale(1.05);
}
```

### 5. 키워드 태그 (Keyword Tags)
```css
/* Keyword Tag */
.keyword-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: #F8F9FA;
  border: 1px solid #E9ECEF;
  border-radius: 20px;
  font-size: var(--text-sm);
  color: var(--neutral-dark);
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 4px;
}

.keyword-tag:hover {
  background: #E9ECEF;
  transform: translateY(-1px);
}

.keyword-tag .remove-icon {
  margin-left: 8px;
  width: 16px;
  height: 16px;
  opacity: 0.6;
  cursor: pointer;
}

.keyword-tag .remove-icon:hover {
  opacity: 1;
}
```

## 📱 레이아웃 시스템

### 1. 그리드 시스템
```css
/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

/* Grid */
.grid {
  display: grid;
  gap: 24px;
}

.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive */
@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}
```

### 2. 스페이싱
```css
/* Spacing Scale */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;
--space-3xl: 64px;
```

### 3. 브레이크포인트
```css
/* Mobile First */
--breakpoint-sm: 576px;
--breakpoint-md: 768px;
--breakpoint-lg: 992px;
--breakpoint-xl: 1200px;
```

## 🎨 일러스트레이션 가이드라인

### 1. 꽃 일러스트 스타일
- **스타일**: 미니멀, 부드러운 라인
- **색상**: 파스텔 톤, 자연스러운 그라데이션
- **디테일**: 과도하지 않은 세밀함, 감성적 표현

### 2. 아이콘 시스템
```css
/* Icon Sizes */
--icon-xs: 16px;
--icon-sm: 20px;
--icon-md: 24px;
--icon-lg: 32px;
--icon-xl: 48px;

/* Icon Colors */
--icon-primary: var(--primary-pink);
--icon-secondary: var(--primary-mint);
--icon-neutral: var(--neutral-dark);
```

### 3. 일러스트레이션 컬러 팔레트
```css
/* Flower Colors */
--flower-pink: #FFB6C1;
--flower-red: #DC143C;
--flower-white: #FFFFFF;
--flower-yellow: #FFD700;
--flower-blue: #4169E1;
--flower-purple: #9370DB;
--flower-orange: #FFA500;
```

## 🎭 애니메이션 가이드라인

### 1. 트랜지션
```css
/* Standard Transitions */
--transition-fast: 0.15s ease;
--transition-normal: 0.3s ease;
--transition-slow: 0.5s ease;

/* Hover Effects */
.hover-lift {
  transition: transform var(--transition-normal);
}

.hover-lift:hover {
  transform: translateY(-4px);
}

/* Loading Animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
```

### 2. 마이크로 인터랙션
- **버튼 클릭**: 스케일 다운 효과
- **색상 선택**: 부드러운 확대 및 테두리 변화
- **로딩**: 펄스 애니메이션
- **결과 표시**: 페이드인 + 슬라이드업

## 📐 디자인 토큰

### 1. Border Radius
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 50%;
```

### 2. Shadows
```css
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

### 3. Z-Index
```css
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-tooltip: 1070;
```

## 🎨 무드보드

### 1. 감정별 컬러 매핑
- **사랑/로맨틱**: 핑크, 레드, 화이트
- **감사/진심**: 화이트, 핑크, 민트
- **기쁨/축하**: 옐로우, 오렌지, 핑크
- **위로/평화**: 블루, 화이트, 라벤더
- **그리움/추억**: 퍼플, 블루, 화이트

### 2. 계절별 컬러
- **봄**: 핑크, 옐로우, 민트
- **여름**: 블루, 화이트, 옐로우
- **가을**: 오렌지, 레드, 브라운
- **겨울**: 화이트, 블루, 실버

## 📱 모바일 최적화

### 1. 터치 타겟
- **최소 크기**: 44x44px
- **권장 크기**: 48x48px
- **간격**: 8px 이상

### 2. 제스처
- **스와이프**: 결과 카드 넘기기
- **탭**: 색상 선택, 버튼 클릭
- **롱프레스**: 색상 상세 정보

### 3. 접근성
- **색상 대비**: WCAG AA 기준 준수
- **폰트 크기**: 최소 16px
- **포커스 표시**: 명확한 포커스 인디케이터
