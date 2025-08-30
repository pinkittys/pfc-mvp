# 🌸 PlainFlowerClub API 가이드 (프론트엔드 개발자용)

## 🚀 API 서버 정보

### 🎉 현재 사용 가능한 API URL:
```
https://api.plainflowerclub.com/api/v1
```

### 📚 API 문서:
```
https://api.plainflowerclub.com/docs
```

### 🧪 데모 페이지:
```
https://api.plainflowerclub.com/demo
```

---

## 📋 핵심 API 엔드포인트

### 1. 사연 샘플 목록 조회
```javascript
GET /sample-stories
```

**응답 예시:**
```json
{
  "stories": [
    {
      "id": "story_001",
      "title": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "story": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
      "predefined_keywords": {
        "emotions": ["희망", "응원"],
        "situations": ["새로운 시작", "격려"],
        "moods": ["활기찬", "따뜻한"],
        "colors": ["옐로우"]
      },
      "category": "응원/격려"
    }
  ],
  "total_count": 30
}
```

### 2. 사연별 꽃 추천
```javascript
POST /sample-stories/{story_id}/recommend
```

**응답 예시:**
```json
{
  "story_id": "S250828-SUN-00001",
  "original_story": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
  "created_at": "2025-08-28T10:30:00.000Z",
  
  "emotions": [
    {
      "emotion": "희망",
      "percentage": 50.0,
      "description": "희망한 마음"
    },
    {
      "emotion": "응원",
      "percentage": 50.0,
      "description": "응원한 마음"
    }
  ],
  
  "flower_name": "해바라기",
  "flower_name_en": "Sunflower",
  "scientific_name": "Helianthus annuus",
  "flower_card_message": "May your dreams take flight and soar high.",
  "flower_image_url": "https://api.plainflowerclub.com/images/sunflower/옐로우.webp",
  
  "flower_blend": {
    "main_flower": "해바라기",
    "sub_flowers": ["베이비브레스", "거베라"],
    "composition_name": "희망의 꽃다발"
  },
  
  "season_info": "Summer 06-08",
  "recommendation_reason": "새로운 시작을 하는 동생에게 해바라기는 희망과 응원의 의미를 담아줄 거예요. 밝은 노란색이 새로운 도전에 대한 긍정적인 에너지를 전달하고, 해바라기의 상징적인 의미가 동생의 미래를 밝게 비춰줄 것입니다.",
  
  "keywords": ["응원", "희망"],
  "hashtags": ["#해바라기", "#옐로우", "#응원", "#새로운시작"],
  "color_keywords": ["옐로우"],
  "excluded_keywords": [],
  
  "sample_story": {
    "id": "story_001",
    "title": "새로운 시작을 하게된 회사 동생에게 응원과 격려의 의미로 꽃을 주고 싶어",
    "category": "응원/격려",
    "predefined_keywords": {
      "emotions": ["희망", "응원"],
      "situations": ["새로운 시작", "격려"],
      "moods": ["활기찬", "따뜻한"],
      "colors": ["옐로우"]
    }
  }
}
```

### 3. 카테고리별 사연 조회
```javascript
GET /sample-stories/categories
GET /sample-stories/category/{category}
```

**카테고리 목록:**
- 응원/격려
- 위로/슬픔
- 사랑/로맨스
- 축하/감사
- 축하/성취
- 병문안/위로
- 축하/새로운 시작
- 사랑/기념일
- 축하/생일
- 감사/사랑
- 축하/결혼
- 이별/추억
- 우정/일상

---

## 🎨 구현 가이드

### 1. 사연 샘플 기능 구현

**A. 사연 목록 로드**
```javascript
const loadStories = async () => {
  try {
    const response = await fetch('https://api.plainflowerclub.com/api/v1/sample-stories');
    const data = await response.json();
    return data.stories; // 30개 사연 배열
  } catch (error) {
    console.error('사연 로드 실패:', error);
    throw error;
  }
};
```

**B. 사연 선택 시 추천 요청**
```javascript
const getRecommendation = async (storyId) => {
  try {
    const response = await fetch(`https://api.plainflowerclub.com/api/v1/sample-stories/${storyId}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('추천 요청 실패:', error);
    throw error;
  }
};
```

**C. 추천 결과 표시**
```javascript
const displayRecommendation = (data) => {
  // 꽃 정보 표시
  const flowerInfo = {
    name: data.flower_name,
    nameEn: data.flower_name_en,
    scientificName: data.scientific_name,
    imageUrl: data.flower_image_url,
    cardMessage: data.flower_card_message,
    keywords: data.keywords,
    hashtags: data.hashtags
  };
  
  // 감정 정보 표시
  const emotionInfo = {
    emotions: data.emotions,
    totalEmotions: data.emotions.length
  };
  
  // 꽃 조합 정보 표시
  const compositionInfo = {
    mainFlower: data.flower_blend.main_flower,
    subFlowers: data.flower_blend.sub_flowers,
    compositionName: data.flower_blend.composition_name
  };
  
  // 사연 정보 표시
  const storyInfo = {
    storyId: data.story_id,
    originalStory: data.original_story,
    createdAt: data.created_at,
    seasonInfo: data.season_info,
    recommendationReason: data.recommendation_reason,
    colorKeywords: data.color_keywords
  };
  
  // 샘플 사연 정보 (샘플 추천인 경우)
  const sampleStoryInfo = data.sample_story ? {
    id: data.sample_story.id,
    title: data.sample_story.title,
    category: data.sample_story.category,
    predefinedKeywords: data.sample_story.predefined_keywords
  } : null;
  
  return { 
    flowerInfo, 
    emotionInfo, 
    compositionInfo, 
    storyInfo, 
    sampleStoryInfo 
  };
};
```

### 2. UI 컴포넌트 예시

**A. 사연 카드 컴포넌트**
```javascript
const StoryCard = ({ story, onSelect }) => {
  return (
    <div className="story-card" onClick={() => onSelect(story.id)}>
      <h3 className="story-title">{story.title}</h3>
      <p className="story-text">{story.story}</p>
      <span className="story-category">{story.category}</span>
      <div className="keywords">
        {story.predefined_keywords.emotions.map(emotion => (
          <span key={emotion} className="keyword-tag">{emotion}</span>
        ))}
        {story.predefined_keywords.colors.map(color => (
          <span key={color} className="keyword-tag">{color}</span>
        ))}
      </div>
    </div>
  );
};
```

**B. 추천 결과 컴포넌트**
```javascript
const RecommendationResult = ({ data }) => {
  const { flowerInfo, emotionInfo, compositionInfo, storyInfo, sampleStoryInfo } = displayRecommendation(data);
  
  return (
    <div className="recommendation-result">
      {/* 꽃 정보 섹션 */}
      <div className="flower-section">
        <img src={flowerInfo.imageUrl} alt={flowerInfo.name} />
        <h2>{flowerInfo.name}</h2>
        <p className="scientific-name">{flowerInfo.scientificName}</p>
        <p className="card-message">{flowerInfo.cardMessage}</p>
        <div className="keywords">
          {flowerInfo.keywords.map(keyword => (
            <span key={keyword} className="keyword">{keyword}</span>
          ))}
        </div>
        <div className="hashtags">
          {flowerInfo.hashtags.map(hashtag => (
            <span key={hashtag} className="hashtag">{hashtag}</span>
          ))}
        </div>
      </div>
      
      {/* 감정 분석 섹션 */}
      <div className="emotion-section">
        <h3>감정 분석</h3>
        <div className="emotions">
          {emotionInfo.emotions.map(emotion => (
            <div key={emotion.emotion} className="emotion-item">
              <span className="emotion-name">{emotion.emotion}</span>
              <span className="emotion-percentage">{emotion.percentage}%</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* 꽃 조합 섹션 */}
      <div className="composition-section">
        <h3>꽃 조합</h3>
        <div className="composition">
          <p><strong>메인 꽃:</strong> {compositionInfo.mainFlower}</p>
          <p><strong>서브 꽃:</strong> {compositionInfo.subFlowers.join(', ')}</p>
          <p><strong>조합명:</strong> {compositionInfo.compositionName}</p>
        </div>
      </div>
      
      {/* 사연 정보 섹션 */}
      <div className="story-section">
        <h3>선택한 사연</h3>
        <p>{storyInfo.originalStory}</p>
        <div className="story-details">
          <p><strong>스토리 ID:</strong> {storyInfo.storyId}</p>
          <p><strong>계절:</strong> {storyInfo.seasonInfo}</p>
          <p><strong>추천 이유:</strong> {storyInfo.recommendationReason}</p>
          <p><strong>선호 색상:</strong> {storyInfo.colorKeywords.join(', ')}</p>
        </div>
      </div>
      
      {/* 샘플 사연 정보 (샘플 추천인 경우) */}
      {sampleStoryInfo && (
        <div className="sample-story-section">
          <h3>샘플 사연 정보</h3>
          <p><strong>제목:</strong> {sampleStoryInfo.title}</p>
          <p><strong>카테고리:</strong> {sampleStoryInfo.category}</p>
          <div className="predefined-keywords">
            <p><strong>감정:</strong> {sampleStoryInfo.predefinedKeywords.emotions.join(', ')}</p>
            <p><strong>상황:</strong> {sampleStoryInfo.predefinedKeywords.situations.join(', ')}</p>
            <p><strong>분위기:</strong> {sampleStoryInfo.predefinedKeywords.moods.join(', ')}</p>
            <p><strong>색상:</strong> {sampleStoryInfo.predefinedKeywords.colors.join(', ')}</p>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🎯 사용자 플로우

### 1. 사연 선택 플로우
```
사용자 → 사연 목록 조회 → 사연 카드 선택 → 추천 요청 → 결과 표시
```

### 2. 구현 순서
1. **사연 목록 표시**: 30개 사연을 카드 형태로 표시
2. **사연 선택**: 사용자가 카드 클릭
3. **로딩 표시**: 추천 요청 중 로딩 애니메이션
4. **결과 표시**: 꽃 추천 결과 화면으로 전환
5. **뒤로가기**: 다른 사연 선택 가능

---

## 🎨 디자인 가이드

### 1. 색상 팔레트
- **Primary**: #667eea (보라색)
- **Secondary**: #764ba2 (진보라색)
- **Background**: #f5f7fa (연한 회색)
- **Text**: #333333 (진한 회색)
- **Light Text**: #666666 (중간 회색)

### 2. 카드 디자인
- **Border Radius**: 15px
- **Shadow**: 0 10px 25px rgba(0,0,0,0.1)
- **Hover Effect**: translateY(-5px)
- **Selected State**: 보라색 테두리

### 3. 키워드 태그
- **Background**: #e9ecef
- **Text Color**: #495057
- **Border Radius**: 12px
- **Padding**: 3px 8px

---

## 🔧 에러 처리

### 1. 공통 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

### 2. 주요 HTTP 상태 코드
- `200`: 성공
- `404`: 사연을 찾을 수 없음
- `500`: 서버 내부 오류

### 3. 에러 처리 예시
```javascript
const handleError = (error) => {
  if (error.status === 404) {
    return '사연을 찾을 수 없습니다.';
  } else if (error.status === 500) {
    return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
  } else {
    return '알 수 없는 오류가 발생했습니다.';
  }
};
```

---

## 📱 반응형 디자인

### 1. 브레이크포인트
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### 2. 그리드 시스템
```css
.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}
```

---

## 🚀 성능 최적화

### 1. 이미지 최적화
- **WebP 포맷** 사용
- **Lazy Loading** 적용
- **Fallback 이미지** 제공

### 2. API 호출 최적화
- **캐싱** 적용
- **디바운싱** 구현
- **에러 재시도** 로직

---

## 📞 지원 및 문의

### 1. 개발 환경
- **로컬 테스트**: `http://localhost:8000/api/v1`
- **프로덕션**: `https://api.plainflowerclub.com/api/v1`

### 2. 문의사항
- **API 문서**: `https://api.plainflowerclub.com/docs`
- **데모 페이지**: `https://api.plainflowerclub.com/demo`
- **헬스체크**: `https://api.plainflowerclub.com/health`

---

## 🎉 완성된 기능

✅ **30개 사연 샘플** 제공  
✅ **미리 설정된 키워드** 활용  
✅ **즉시 추천** 기능  
✅ **159개 꽃 이미지** 지원  
✅ **27개 꽃 종류** 데이터베이스  
✅ **색상별 매칭** 시스템  
✅ **카테고리별 분류**  
✅ **반응형 디자인** 지원  

이제 **사연 선택 → 즉시 추천** 기능이 완성되었습니다! 🌸✨
