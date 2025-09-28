# 추천 API 구조 설계

## 📋 API 엔드포인트

### 1️⃣ 키워드 추출 (기존)
```
POST /api/v1/extract-keywords
Request: {"story": "텍스트"}
Response: {
  "success": true,
  "keywords": [
    {"type": "emotions", "main": "기쁨", "alternatives": ["행복", "즐거움", "설렘"]},
    {"type": "situations", "main": "축하", "alternatives": ["성취", "기념일", "일상"]},
    {"type": "moods", "main": "화려한", "alternatives": ["따뜻한", "부드러운", "차분한"]},
    {"type": "colors", "main": "레드", "alternatives": ["핑크", "화이트", "오렌지"]}
  ],
  "confidence": 0.85,
  "extraction_method": "smart"
}
```

### 2️⃣ 추천 요청 (새로운 구조)
```
POST /api/v1/unified/recommend
Request: {
  "story": "친구 생일 축하하고 싶어요",
  "selected_keywords": {
    "emotions": "기쁨",
    "situations": "축하", 
    "moods": "화려한",
    "colors": "레드"
  },
  "excluded_keywords": ["장미", "튤립"]
}
Response: {
  "success": true,
  "created_at": "2025.09.17.",
  "story_id": "S250917-ZIN-S2901",
  "your_story": "친구 생일 축하하고 싶어요",
  
  "flower_info": {
    "korean_name": "지니아",
    "english_name": "zinnia", 
    "scientific_name": "Zinnia elegans"
  },
  
  "flower_blend": {
    "main_flower": "지니아",
    "sub_flowers": ["서브꽃1", "서브꽃2"],
    "composition_name": "구성명"
  },
  
  "flower_image_url": "꽃 이미지 URL",
  "calligraphy_image_url": "캘리그래피 이미지 URL",
  
  "flower_card_message": {
    "quote": "인용구",
    "source": "출처"
  },
  
  "emotions": [
    {"emotion": "기쁨", "percentage": 40.0},
    {"emotion": "감사", "percentage": 35.0},
    {"emotion": "희망", "percentage": 25.0}
  ],
  
  "season_detail": {
    "availability": "Spring/Summer",
    "best_season": "03-08"
  },
  
  "comment": "추천 이유",
  "hashtags": ["#기쁨", "#감사", "#특별한"]
}
```

### 3️⃣ 스냅샷 조회 (새로운 기능)
```
GET /api/v1/recommend/{story_id}
Response: {
  "success": true,
  "created_at": "2025.09.17.",
  "story_id": "S250917-ZIN-S2901",
  "your_story": "사연 내용",
  
  "flower_info": {
    "korean_name": "지니아",
    "english_name": "zinnia", 
    "scientific_name": "Zinnia elegans"
  },
  
  "flower_blend": {
    "main_flower": "지니아",
    "sub_flowers": ["서브꽃1", "서브꽃2"],
    "composition_name": "구성명"
  },
  
  "flower_image_url": "꽃 이미지 URL",
  "calligraphy_image_url": "캘리그래피 이미지 URL",
  
  "flower_card_message": {
    "quote": "인용구",
    "source": "출처"
  },
  
  "emotions": [
    {"emotion": "기쁨", "percentage": 40.0},
    {"emotion": "감사", "percentage": 35.0},
    {"emotion": "희망", "percentage": 25.0}
  ],
  
  "season_detail": {
    "availability": "Spring/Summer",
    "best_season": "03-08"
  },
  
  "comment": "추천 이유",
  "hashtags": ["#기쁨", "#감사", "#특별한"]
}
```

## 🔄 워크플로우

### 프론트엔드 플로우
1. **스토리 입력** → `POST /extract-keywords` → 키워드 추출
2. **키워드 선택/수정** → 프론트엔드에서 처리
3. **"추천받기" 클릭** → `POST /unified/recommend` → 추천 결과 + 스냅샷 저장
4. **결과 공유** → `GET /recommend/{story_id}` → 스냅샷 조회

### 백엔드 플로우
1. **요청 검증** → 스토리, 키워드 유효성 확인
2. **꽃 매칭** → 스프레드시트 기반 추천 로직
3. **결과 생성** → 꽃 정보, 이미지, 설명 등 생성
4. **스냅샷 저장** → Supabase에 전체 결과 저장
5. **응답 반환** → 최종 결과 반환

## 📊 데이터 흐름

```
사용자 입력 → 키워드 추출 → 키워드 선택 → 추천 요청 → 꽃 매칭 → 스냅샷 저장 → 결과 반환
     ↓              ↓           ↓          ↓         ↓         ↓         ↓
  스토리 텍스트 → 4개 디멘션 → 사용자 선택 → 최종 요청 → 추천 로직 → DB 저장 → UI 표시
```

## 🎯 핵심 특징

1. **스냅샷 저장**: 모든 추천 결과를 DB에 저장
2. **재조회 가능**: story_id로 언제든 결과 조회
3. **공유 가능**: URL로 결과 공유
4. **분석 가능**: 추천 패턴 분석
5. **캐싱 효과**: 같은 요청 시 빠른 응답
