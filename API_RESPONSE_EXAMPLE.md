# Floiy-Reco API 응답 형식

## 1. 감정 분석 API (`/api/v1/emotion-analysis`)

### 요청 예시
```json
{
  "story": "커피 마시며 책 읽는 제 작업실에 둘 작은 꽃다발을 원해요."
}
```

### 응답 예시
```json
{
  "emotions": [
    {
      "emotion": "평온함",
      "percentage": 40.0
    },
    {
      "emotion": "우아함", 
      "percentage": 35.0
    },
    {
      "emotion": "자연스러움",
      "percentage": 25.0
    }
  ],
  "matched_flower": {
    "flower_name": "Scabiosa",
    "korean_name": "스카비오사",
    "scientific_name": "Scabiosa atropurpurea",
    "image_url": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAADsAD+JaQAA3AAAAAA",
    "keywords": ["우아함", "세련됨", "포인트", "모던", "그리움"],
    "colors": ["블루", "화이트", "퍼플"],
    "emotions": ["우아함", "세련됨", "모던", "그리움"]
  },
  "composition": {
    "main_flower": "Scabiosa",
    "sub_flowers": ["Babys Breath", "Lisianthus"],
    "style": "Modern Elegant",
    "description": "우아하고 세련된 모던 엘레간트 스타일"
  },
  "recommendation_reason": "작업실의 차분한 분위기에 어울리는 우아한 스카비오사입니다. 블루 톤이 공간에 포인트를 주면서도 자연스러운 느낌을 연출해드릴 거예요."
}
```

## 2. 맥락 추출 API (`/api/v1/extract-context`)

### 요청 예시
```json
{
  "story": "커피 마시며 책 읽는 제 작업실에 둘 작은 꽃다발을 원해요."
}
```

### 응답 예시
```json
{
  "emotions": ["평온함"],
  "situations": ["인테리어"],
  "moods": ["차분한"],
  "colors": ["블루"],
  "confidence": 0.85
}
```

## 3. 샘플 데이터 API (`/api/v1/samples`)

### 요청 예시
```
GET /api/v1/samples?count=5
```

### 응답 예시
```json
[
  "커피 마시며 책 읽는 제 작업실에 둘 작은 꽃다발을 원해요.",
  "20년지기 친구가 이사 가요. 그리움과 추억이 담긴 꽃다발을 선물하고 싶어요.",
  "베프 생일이에요! 밝고 경쾌한 느낌으로 노랑이나 오렌지 톤의 꽃다발을 원해요.",
  "연인에게 고백할 때 줄 꽃다발을 찾고 있어요. 로맨틱하고 사랑스러운 느낌으로요.",
  "부모님께 감사한 마음을 담아 꽃다발을 선물하고 싶어요."
]
```

## 중요 사항

### 이미지 URL 형식
- **형식**: `data:image/webp;base64,{base64_data}`
- **예시**: `data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAADsAD+JaQAA3AAAAAA`

### 프론트엔드에서 이미지 표시 방법
```html
<img src="data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAADsAD+JaQAA3AAAAAA" alt="꽃 이미지" />
```

### JavaScript에서 이미지 처리
```javascript
// 이미지 로드 확인
const img = new Image();
img.onload = function() {
    console.log('이미지 로드 성공');
    document.getElementById('flowerImage').src = this.src;
};
img.onerror = function() {
    console.log('이미지 로드 실패');
};
img.src = data.matched_flower.image_url;
```

## 에러 응답 형식

### 400 Bad Request
```json
{
  "detail": "스토리가 비어있습니다."
}
```

### 500 Internal Server Error
```json
{
  "detail": "감정 분석 중 오류가 발생했습니다."
}
```

## 테스트용 샘플 스토리

1. **작업실/인테리어**: "커피 마시며 책 읽는 제 작업실에 둘 작은 꽃다발을 원해요."
2. **이사/떠남**: "20년지기 친구가 이사 가요. 그리움과 추억이 담긴 꽃다발을 선물하고 싶어요."
3. **생일/축하**: "베프 생일이에요! 밝고 경쾌한 느낌으로 노랑이나 오렌지 톤의 꽃다발을 원해요."
4. **로맨스**: "연인에게 고백할 때 줄 꽃다발을 찾고 있어요. 로맨틱하고 사랑스러운 느낌으로요."
5. **감사**: "부모님께 감사한 마음을 담아 꽃다발을 선물하고 싶어요."


