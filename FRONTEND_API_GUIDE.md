# PlainFlowerClub API 가이드 (프론트엔드 개발자용)

## 🚀 API 서버 정보

### 🎉 현재 사용 가능한 API URL (SSL 인증서 완료!):
```
https://api.plainflowerclub.com/api/v1
```

### 📚 API 문서:
```
https://api.plainflowerclub.com/docs
```

### 🧪 테스트 페이지:
```
https://api.plainflowerclub.com/FRONTEND_TEST.html
```

---

## 📋 API 엔드포인트 목록

### 1. Health Check
```javascript
GET /health
```
**참고**: Health Check는 `/api/v1/health`가 아니라 루트 경로 `/health`에 있습니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-22T11:52:50.543588",
  "version": "1.0.0",
  "services": {
    "api": "running",
    "database": "connected",
    "openai": "available"
  }
}
```

### 2. 빠른 키워드 추출
```javascript
POST /fast-context
```

**요청 본문:**
```json
{
  "story": "오늘 친구와 함께 카페에 갔어요. 분위기가 정말 좋았고 커피도 맛있었어요."
}
```

**응답 예시:**
```json
{
  "emotions": ["우정"],
  "situations": ["친구"],
  "moods": ["따뜻한"],
  "colors": ["옐로우"]
}
```

### 3. 상세 키워드 추출
```javascript
POST /extract-context
```

**요청 본문:**
```json
{
  "story": "오늘 친구와 함께 카페에 갔어요. 분위기가 정말 좋았고 커피도 맛있었어요."
}
```

**응답 예시:**
```json
{
  "emotions": ["사랑"],
  "situations": ["휴식공간"],
  "moods": ["편안한"],
  "colors": ["파스텔톤"],
  "confidence": 0.85,
  "user_intent": "meaning_based",
  "mentioned_flower": null
}
```

### 4. 감정 분석
```javascript
POST /emotion-analysis
```

**요청 본문:**
```json
{
  "story": "오늘 친구와 함께 카페에 갔어요. 분위기가 정말 좋았고 커피도 맛있었어요."
}
```

**응답 예시:**
```json
{
  "emotion": "기쁨",
  "intensity": 0.8,
  "keywords": ["친구", "카페", "분위기", "커피"]
}
```

### 5. 꽃 추천
```javascript
POST /recommendations
```

**요청 본문:**
```json
{
  "story": "오늘 친구와 함께 카페에 갔어요. 분위기가 정말 좋았고 커피도 맛있었어요.",
  "preferred_colors": ["핑크", "화이트"],
  "excluded_flowers": [],
  "top_k": 3
}
```

**응답 예시:**
```json
{
  "recommendations": [
    {
      "flower_id": "rose-red",
      "flower_name": "레드 로즈",
      "scientific_name": "Rosa spp.",
      "color": "레드",
      "meaning": "사랑과 열정",
      "image_url": "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/rose-red.webp",
      "reason": "기쁜 감정과 친구와의 만남에 어울리는 꽃입니다."
    }
  ]
}
```

### 6. 꽃 계절 정보
```javascript
GET /flower-season/{flowerName}
```

**응답 예시:**
```json
{
  "flower_name": "레드 로즈",
  "season": "봄, 여름, 가을",
  "availability": "연중"
}
```

### 7. 스토리 공유 URL 생성
```javascript
POST /api/v1/stories/share
```

**요청 본문:**
```json
{
  "story_id": "S250822-FLC-00001"
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "공유 URL이 생성되었습니다.",
  "data": {
    "story_id": "S250822-FLC-00001",
    "story": "오늘 친구와 함께 카페에 갔어요...",
    "recommendations": [...],
    "created_at": "2025-08-22T11:52:50.543588"
  },
  "share_url": "/share/UzI1MDgyMi1GTEMtMDAwMDE="
}
```

### 8. 공유된 스토리 조회
```javascript
GET /api/v1/stories/share/{encoded_id}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "공유된 스토리를 성공적으로 조회했습니다.",
  "data": {
    "story_id": "S250822-FLC-00001",
    "story": "오늘 친구와 함께 카페에 갔어요...",
    "recommendations": [...],
    "created_at": "2025-08-22T11:52:50.543588"
  }
}
```

---

## 🔧 JavaScript 사용 예시

### 기본 설정:
```javascript
const API_BASE = 'https://port-0-plainflowerclub-mej0wlho47c6df8c.sel5.cloudtype.app/api/v1';

// 향후 변경 시:
// const API_BASE = 'https://api.plainflowerclub.com/api/v1';
```

### Health Check:
```javascript
async function checkHealth() {
  try {
    const response = await fetch('https://port-0-plainflowerclub-mej0wlho47c6df8c.sel5.cloudtype.app/health');
    const data = await response.json();
    console.log('API 상태:', data);
    return data;
  } catch (error) {
    console.error('API 연결 실패:', error);
  }
}
```

### 키워드 추출:
```javascript
async function extractKeywords(story) {
  try {
    const response = await fetch(`${API_BASE}/fast-context`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ story })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('키워드 추출 실패:', error);
  }
}
```

### 꽃 추천:
```javascript
async function recommendFlowers(story, preferred_colors = [], excluded_flowers = [], top_k = 3) {
  try {
    const response = await fetch(`${API_BASE}/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        story, 
        preferred_colors, 
        excluded_flowers, 
        top_k 
      })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('꽃 추천 실패:', error);
  }
}
```

### 스토리 공유:
```javascript
async function shareStory(storyId) {
  try {
    const response = await fetch(`${API_BASE}/stories/share`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ story_id: storyId })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('스토리 공유 실패:', error);
  }
}

async function getSharedStory(encodedId) {
  try {
    const response = await fetch(`${API_BASE}/stories/share/${encodedId}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('공유 스토리 조회 실패:', error);
  }
}
```

---

## 🎨 React/Vue.js 예시

### React Hook 예시:
```javascript
import { useState, useEffect } from 'react';

const API_BASE = 'https://port-0-plainflowerclub-mej0wlho47c6df8c.sel5.cloudtype.app/api/v1';

export function useFlowerRecommendation() {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);

  const getRecommendations = async (story) => {
    setLoading(true);
    setError(null);
    
    try {
      // 1. 키워드 추출
      const contextResponse = await fetch(`${API_BASE}/fast-context`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story })
      });
      const contextData = await contextResponse.json();
      
      // 2. 꽃 추천
      const recommendResponse = await fetch(`${API_BASE}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          story: story,
          preferred_colors: contextData.colors || [],
          excluded_flowers: [],
          top_k: 3
        })
      });
      const recommendData = await recommendResponse.json();
      
      setRecommendations(recommendData.recommendations);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { loading, recommendations, error, getRecommendations };
}
```

---

## ⚠️ 주의사항

### 1. CORS 설정
- API 서버에서 CORS가 설정되어 있어 브라우저에서 직접 호출 가능
- 프론트엔드 도메인에서 API 호출 시 문제없음

### 2. 에러 처리
- 모든 API 호출에 try-catch 블록 사용 권장
- 네트워크 오류 및 서버 오류 처리 필요

### 3. 로딩 상태
- API 호출 시 로딩 상태 표시 권장
- 사용자 경험 향상을 위한 스켈레톤 UI 고려

---

## 📞 문의사항

API 관련 문의사항이 있으시면 백엔드 개발팀에 연락해주세요!

---

## 🔄 업데이트 내역

- **2025-08-22**: API 가이드 최초 작성
- **현재 URL**: Cloudtype 임시 URL 사용 중
- **향후 업데이트**: SSL 인증서 해결 후 도메인 변경 예정
