# 꽃 추천 시스템 개발자 가이드

## 📋 개요

이 문서는 꽃 추천 시스템의 디자이너와 프론트엔드 개발자를 위한 가이드입니다. 시스템의 구조, API, 데이터 형식, 그리고 로깅 시스템에 대한 정보를 제공합니다.

## 🏗️ 시스템 아키텍처

### 전체 구조
```
floiy-reco/
├── app/
│   ├── api/v1/           # REST API 엔드포인트
│   ├── core/             # 설정 및 핵심 기능
│   ├── models/           # 데이터 모델 및 스키마
│   ├── pipelines/        # 추천 파이프라인
│   ├── services/         # 비즈니스 로직 서비스
│   └── utils/            # 유틸리티 함수
├── data/                 # 데이터 파일들
├── logs/                 # 로그 파일들
└── scripts/              # 유틸리티 스크립트
```

### 추천 파이프라인
1. **맥락 추출** (LLM 기반)
2. **감정 분석**
3. **꽃 매칭**
4. **꽃 구성 추천**
5. **이미지 매칭**
6. **추천 이유 생성**

## 🔌 API 엔드포인트

### 1. 꽃 추천 API
```
POST /api/v1/recommend
```

**요청 예시:**
```json
{
  "story": "친구가 갑작스럽게 반려견을 떠나보냈어요. 차분하고 위로가 되는 색감이면 좋겠어요.",
  "budget": 50000
}
```

**응답 예시:**
```json
{
  "recommendations": [
    {
      "id": "R001",
      "template_id": "장미",
      "name": "추천 꽃다발",
      "main_flowers": ["장미"],
      "sub_flowers": ["튤립", "작약"],
      "color_theme": ["화이트", "연한 핑크"],
      "estimated_price": 27000,
      "reason": "친구의 반려견을 떠나보내는 마음은 진정한 그리움과 애틋함이 담겨 있습니다...",
      "image_url": "/static/images/garden-peony/화이트.webp"
    }
  ]
}
```

### 2. 맥락 추출 API
```
POST /api/v1/context-extraction
```

**요청 예시:**
```json
{
  "story": "첫사랑에게 고백하려고 해요. 진심어린 사랑을 전하고 싶어요."
}
```

**응답 예시:**
```json
{
  "emotions": ["사랑", "로맨틱함"],
  "situations": ["연인", "고백"],
  "moods": ["로맨틱한", "달콤한"],
  "colors": ["핑크", "화이트"],
  "confidence": 0.90
}
```

### 3. 키워드 추출 API
```
POST /api/v1/keywords
```

**요청 예시:**
```json
{
  "text": "회사 동료가 승진했어요. 축하하고 싶어요."
}
```

**응답 예시:**
```json
{
  "keywords": ["승진", "축하", "동료", "회사"]
}
```

## 📊 데이터 구조

### 꽃 데이터베이스 (`data/flowers_enhanced.csv`)
- **flower_id**: 고유 ID
- **flower_name**: 꽃 이름 (한국어)
- **english_name**: 영어 이름
- **scientific_name**: 학명
- **symbolism**: 꽃말
- **mood**: 무드
- **occasion**: 적합한 상황
- **price**: 가격대
- **season**: 계절
- **roles**: 역할 (main, sub, filler, line, foliage)

### 이미지 인덱스 (`data/images_index_enhanced.csv`)
- **image_id**: 이미지 ID
- **flower_name**: 꽃 이름
- **color**: 색상
- **file_path**: 파일 경로
- **flower_keywords**: 꽃 키워드
- **style_tags**: 스타일 태그

### 꽃 의미 데이터 (`data/korean_flower_meanings.json`)
```json
{
  "장미": {
    "symbolism": "사랑, 열정, 아름다움",
    "color_meanings": {
      "레드": "진정한 사랑",
      "핑크": "로맨틱한 사랑",
      "화이트": "순수한 사랑"
    },
    "situations": ["연인", "고백", "기념일"],
    "emotion_scores": {
      "사랑": 0.9,
      "열정": 0.8,
      "아름다움": 0.7
    }
  }
}
```

## 📝 로깅 시스템

### 로그 파일 위치
- **일별 통합 로그**: `logs/daily_recommendations_YYYYMMDD.json`
- **개별 추천 로그**: `logs/recommendation_YYYYMMDD_HHMMSS.json`
- **텍스트 로그**: `logs/recommendation_YYYYMMDD.log`

### 로그 데이터 구조
```json
{
  "timestamp": "2025-08-15T04:14:36.123456",
  "customer_story": "고객 이야기",
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
    "emotion_scores": {"감정1": 0.5, "감정2": 0.3},
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

### 로그 통계 API
```python
# 통계 조회
stats = logger.get_recommendation_stats("20250815")

# 로그 검색
results = logger.search_recommendations(
    keyword="반려견",
    emotion="위로",
    flower="장미",
    date="20250815"
)
```

## 🎨 디자인 가이드라인

### 색상 팔레트
- **화이트**: 순수, 깔끔함
- **핑크**: 로맨틱, 부드러움
- **레드**: 열정, 사랑
- **옐로우**: 기쁨, 활력
- **퍼플**: 신비, 고귀함
- **블루**: 평화, 신뢰
- **라벤더**: 우아함, 평온함

### 꽃 역할별 특징
- **메인 꽃**: 가장 큰 꽃, 중앙 배치
- **서브 꽃**: 메인 꽃 보조, 볼륨감
- **필러 꽃**: 작은 꽃, 공간 채움
- **라인 꽃**: 긴 줄기, 높이감
- **그린**: 잎사귀, 자연스러움

### 스타일 가이드
- **로맨틱**: 부드러운 곡선, 핑크/화이트 톤
- **모던**: 깔끔한 직선, 단색 조합
- **자연스러운**: 비대칭, 다양한 높이
- **고전적**: 대칭, 정형화된 형태
- **캐주얼**: 자유로운 배치, 밝은 색상

## 🔧 개발 환경 설정

### 필수 의존성
```bash
pip install -r requirements.txt
```

### 환경 변수
```bash
# .env 파일
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📈 성능 지표

### 추천 품질 지표
- **신뢰도**: 0.0-1.0 (LLM 추출 정확도)
- **처리 시간**: 평균 4-5초
- **매칭 점수**: 0.0-1.0 (꽃 매칭 정확도)

### 모니터링 지표
- 일일 추천 수
- 평균 신뢰도
- 평균 처리 시간
- 주요 감정 분포
- 주요 꽃 분포

## 🚀 향후 개발 계획

### 단기 계획
- [ ] 이미지 매칭 알고리즘 개선
- [ ] 더 많은 꽃 데이터 추가
- [ ] 사용자 피드백 시스템

### 중기 계획
- [ ] 개인화 추천 시스템
- [ ] 계절별 추천 로직
- [ ] 가격대별 최적화

### 장기 계획
- [ ] AI 이미지 생성 통합
- [ ] 실시간 재고 연동
- [ ] 소셜 기능 추가

## 📞 문의 및 지원

### 개발팀 연락처
- **백엔드 개발**: [이메일]
- **프론트엔드 개발**: [이메일]
- **디자인**: [이메일]

### 문서 및 리소스
- **API 문서**: `/docs` (Swagger UI)
- **코드 저장소**: [GitHub 링크]
- **이슈 트래커**: [GitHub Issues]

---

*마지막 업데이트: 2025-08-15*



