# 데이터 스키마 문서

## 📋 개요

이 문서는 꽃 추천 시스템에서 사용되는 모든 데이터 구조와 스키마를 정의합니다.

## 🌺 꽃 데이터베이스

### flowers_enhanced.csv

꽃의 상세 정보를 포함하는 메인 데이터베이스입니다.

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| flower_id | integer | 고유 ID | 1 |
| flower_name | string | 꽃 이름 (한국어) | "장미" |
| english_name | string | 영어 이름 | "rose" |
| scientific_name | string | 학명 | "Rosa" |
| symbolism | string | 꽃말 | "사랑, 열정, 아름다움" |
| mood | string | 무드 | "로맨틱한" |
| occasion | string | 적합한 상황 | "연인, 고백, 기념일" |
| price | string | 가격대 | "중간" |
| season | string | 계절 | "봄, 여름" |
| roles | string | 역할 | "main, sub" |

**예시 데이터:**
```csv
flower_id,flower_name,english_name,scientific_name,symbolism,mood,occasion,price,season,roles
1,장미,rose,Rosa,사랑, 열정, 아름다움,로맨틱한,연인, 고백, 기념일,중간,봄, 여름,main, sub
2,튤립,tulip,Tulipa,완벽한 사랑, 봄, 새로운 시작,희망찬,연인, 봄, 새로운 시작,중간,봄,main, sub
```

## 🖼️ 이미지 인덱스

### images_index_enhanced.csv

꽃 이미지의 메타데이터를 포함하는 인덱스입니다.

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| image_id | string | 이미지 고유 ID | "rose_red_001" |
| flower_name | string | 꽃 이름 | "rose" |
| color | string | 색상 | "red" |
| file_path | string | 파일 경로 | "/static/images/rose/레드.webp" |
| flower_keywords | string | 꽃 키워드 | "rose, 장미, 로즈" |
| style_tags | string | 스타일 태그 | "romantic, classic, elegant" |

**예시 데이터:**
```csv
image_id,flower_name,color,file_path,flower_keywords,style_tags
rose_red_001,rose,red,/static/images/rose/레드.webp,"rose, 장미, 로즈","romantic, classic, elegant"
tulip_white_001,tulip,white,/static/images/tulip/화이트.webp,"tulip, 튤립","pure, spring, fresh"
```

## 🎨 꽃 의미 데이터

### korean_flower_meanings.json

꽃의 상세한 의미와 감정 매칭 정보를 포함합니다.

```json
{
  "장미": {
    "symbolism": "사랑, 열정, 아름다움",
    "color_meanings": {
      "레드": "진정한 사랑",
      "핑크": "로맨틱한 사랑",
      "화이트": "순수한 사랑",
      "옐로우": "우정, 기쁨"
    },
    "situations": ["연인", "고백", "기념일", "축하"],
    "emotion_scores": {
      "사랑": 0.9,
      "열정": 0.8,
      "아름다움": 0.7,
      "기쁨": 0.6,
      "우정": 0.5
    }
  },
  "튤립": {
    "symbolism": "완벽한 사랑, 봄, 새로운 시작",
    "color_meanings": {
      "레드": "진정한 사랑",
      "핑크": "로맨틱한 사랑",
      "화이트": "순수함",
      "옐로우": "희망, 기쁨"
    },
    "situations": ["연인", "봄", "새로운 시작", "축하"],
    "emotion_scores": {
      "희망": 0.9,
      "사랑": 0.8,
      "기쁨": 0.7,
      "새로운 시작": 0.8
    }
  }
}
```

## 📊 로그 데이터 구조

### RecommendationLog

추천 과정의 모든 단계를 기록하는 로그 구조입니다.

```json
{
  "timestamp": "2025-08-15T04:14:36.123456",
  "customer_story": "고객의 이야기",
  "budget": 50000,
  "extracted_context": {
    "emotions": ["감정1", "감정2"],
    "situations": ["상황1", "상황2"],
    "moods": ["무드1", "무드2"],
    "colors": ["색상1", "색상2"],
    "confidence": 0.90
  },
  "emotion_analysis": {
    "primary_emotion": "주요 감정",
    "emotion_scores": {
      "감정1": 0.5,
      "감정2": 0.3
    },
    "total_emotions": 2
  },
  "flower_matches": [
    {
      "flower_name": "꽃 이름",
      "match_score": 0.75,
      "emotion_fit": 0.8,
      "situation_fit": 0.7,
      "reason": "매칭 이유"
    }
  ],
  "blend_recommendations": [
    {
      "blend": {
        "main_flowers": ["메인 꽃"],
        "sub_flowers": ["서브 꽃"],
        "filler_flowers": ["필러 꽃"],
        "line_flowers": ["라인 꽃"],
        "foliage": ["그린"],
        "total_flowers": 15,
        "estimated_price": 27000,
        "color_harmony": "색상 조화",
        "style_description": "스타일 설명",
        "color_theme": ["색상1", "색상2"]
      },
      "color_fit": 0.8,
      "total_score": 0.75,
      "reasoning": "구성 이유"
    }
  ],
  "final_recommendation": {
    "main_flower": "메인 꽃",
    "image_url": "/static/images/...",
    "reason": "추천 이유",
    "confidence": 0.8,
    "style_description": "스타일 설명",
    "color_theme": ["색상1", "색상2"]
  },
  "processing_time_ms": 4905,
  "confidence_score": 0.90,
  "tags": ["태그1", "태그2", "태그3"]
}
```

## 🔧 설정 파일

### config.py

시스템 설정을 관리하는 설정 파일입니다.

```python
class Settings:
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "꽃 추천 시스템"
    
    # 데이터베이스 설정
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"
    
    # 이미지 설정
    IMAGES_DIR: str = "data/images_webp"
    STATIC_URL: str = "/static"
    
    # LLM 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 추천 설정
    MAX_RECOMMENDATIONS: int = 1
    MIN_CONFIDENCE: float = 0.5
    MAX_PROCESSING_TIME: int = 10000
```

## 📁 파일 구조

```
data/
├── flowers.csv                    # 기본 꽃 데이터
├── flowers_enhanced.csv           # 향상된 꽃 데이터
├── images_index.csv               # 기본 이미지 인덱스
├── images_index_enhanced.csv      # 향상된 이미지 인덱스
├── korean_flower_meanings.json    # 꽃 의미 데이터
├── rules.json                     # 추천 규칙
├── templates.csv                  # 템플릿 데이터
├── images_raw/                    # 원본 이미지
└── images_webp/                   # 최적화된 이미지

logs/
├── daily_recommendations_YYYYMMDD.json    # 일별 통합 로그
├── recommendation_YYYYMMDD.log            # 텍스트 로그
└── recommendation_YYYYMMDD_HHMMSS.json   # 개별 추천 로그
```

## 🔍 데이터 검증

### 꽃 데이터 검증 규칙

1. **flower_id**: 고유해야 함
2. **flower_name**: 비어있지 않아야 함
3. **symbolism**: 최소 1개 이상의 의미 포함
4. **price**: "저", "중간", "고" 중 하나
5. **season**: 유효한 계절명
6. **roles**: 유효한 역할명

### 이미지 데이터 검증 규칙

1. **image_id**: 고유해야 함
2. **file_path**: 실제 파일이 존재해야 함
3. **flower_name**: flowers.csv에 존재하는 꽃명
4. **color**: 유효한 색상명

### 로그 데이터 검증 규칙

1. **timestamp**: ISO 8601 형식
2. **confidence_score**: 0.0-1.0 범위
3. **processing_time_ms**: 양수
4. **budget**: 양수

## 🔄 데이터 업데이트

### 꽃 데이터 업데이트

```python
# 새로운 꽃 추가
def add_flower(flower_data):
    # 1. flowers.csv에 추가
    # 2. korean_flower_meanings.json에 의미 추가
    # 3. 이미지 인덱스 업데이트
    pass

# 꽃 정보 수정
def update_flower(flower_id, updates):
    # 1. flowers.csv 수정
    # 2. 관련 이미지 인덱스 업데이트
    pass
```

### 이미지 데이터 업데이트

```python
# 새 이미지 추가
def add_image(image_data):
    # 1. 이미지 파일 복사
    # 2. images_index_enhanced.csv에 추가
    # 3. 이미지 최적화 (WebP 변환)
    pass

# 이미지 메타데이터 수정
def update_image_metadata(image_id, updates):
    # images_index_enhanced.csv 수정
    pass
```

## 📊 데이터 통계

### 현재 데이터 현황

- **총 꽃 종류**: 77개
- **총 이미지**: 25개
- **색상 종류**: 8개 (레드, 핑크, 화이트, 옐로우, 퍼플, 블루, 라벤더, 그린)
- **역할 분류**: 5개 (main, sub, filler, line, foliage)

### 데이터 품질 지표

- **데이터 완성도**: 95%
- **이미지 매칭률**: 85%
- **색상 정확도**: 90%
- **의미 데이터 품질**: 88%

## 🚀 향후 개선 계획

### 데이터 확장
- [ ] 더 많은 꽃 종류 추가
- [ ] 계절별 꽃 데이터 강화
- [ ] 가격대별 상세 정보
- [ ] 지역별 꽃 정보

### 데이터 품질 개선
- [ ] 자동 데이터 검증 시스템
- [ ] 이미지 품질 평가
- [ ] 의미 데이터 정확도 향상
- [ ] 사용자 피드백 반영

### 데이터 관리
- [ ] 데이터베이스 마이그레이션
- [ ] 버전 관리 시스템
- [ ] 백업 및 복구 시스템
- [ ] 실시간 데이터 동기화

---

*마지막 업데이트: 2025-08-15*



