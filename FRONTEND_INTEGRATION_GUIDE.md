# 실시간 키워드 추출 기능 프론트엔드 연동 가이드

## 📋 개요
사용자가 사연을 입력하는 동안 실시간으로 키워드를 추출하고, 사용자가 대안 키워드를 선택할 수 있는 기능을 프론트엔드에 연동하는 가이드입니다.

## 🔗 API 엔드포인트

### 1. 실시간 키워드 추출
```javascript
POST /api/v1/extract-keywords?mode=realtime
```

**요청:**
```json
{
  "story": "사용자가 입력한 사연 텍스트"
}
```

**응답:**
```json
{
  "success": true,
  "mode": "realtime",
  "extraction_stage": {
    "stage": "partial",
    "progress": 0.6
  },
  "keywords": [
    {
      "type": "emotions",
      "main": "기쁨",
      "alternatives": ["감사", "희망", "사랑"]
    },
    {
      "type": "situations", 
      "main": "생일",
      "alternatives": ["축하", "기념일", "특별한날"]
    },
    {
      "type": "moods",
      "main": "따뜻한",
      "alternatives": ["화려한", "우아한", "자연스러운"]
    },
    {
      "type": "colors",
      "main": "핑크",
      "alternatives": ["레드", "화이트", "옐로우"]
    }
  ],
  "confidence": 0.85,
  "extraction_method": "lightweight_llm"
}
```

### 2. 최종 키워드 추출 (사용자 수정 포함)
```javascript
POST /api/v1/extract-keywords?mode=final
```

**요청:**
```json
{
  "story": "사용자가 입력한 사연 텍스트",
  "updated_context": {
    "emotions": ["감사"],
    "situations": ["생일"],
    "moods": ["따뜻한"],
    "colors": ["핑크"]
  }
}
```

### 3. 최종 꽃 추천
```javascript
POST /api/v1/recommend
```

**요청:**
```json
{
  "story": "사용자가 입력한 사연 텍스트",
  "preferred_colors": [],
  "excluded_flowers": [],
  "updated_context": {
    "emotions": ["감사"],
    "situations": ["생일"],
    "moods": ["따뜻한"],
    "colors": ["핑크"]
  }
}
```

## 🎨 UI 컴포넌트 구조

### 1. 키워드 표시 컴포넌트
```html
<div class="keyword-section">
  <div class="keyword-dropdown">
    <select id="emotions_select" onchange="updateKeyword('emotions', this.value)">
      <option value="기쁨" selected>기쁨</option>
      <option value="감사">감사</option>
      <option value="희망">희망</option>
    </select>
  </div>
  <div class="alternatives-section">
    <span class="alternatives-label">대안:</span>
    <div class="alternatives-tags">
      <span class="alternative-tag" onclick="selectAlternative('emotions', '감사')">감사</span>
      <span class="alternative-tag" onclick="selectAlternative('emotions', '희망')">희망</span>
    </div>
  </div>
</div>
```

### 2. CSS 스타일
```css
.keyword-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.keyword-dropdown {
  position: relative;
  margin-bottom: 10px;
}

.keyword-dropdown select {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  background: white;
}

.alternatives-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.alternatives-label {
  font-weight: bold;
  color: #666;
  font-size: 14px;
}

.alternatives-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.alternative-tag {
  padding: 5px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.alternative-tag:hover {
  background: #1976d2;
  color: white;
}

.selected-keyword {
  background: #27ae60 !important;
  color: white !important;
}
```

## ⚡ JavaScript 구현

### 1. 전역 변수
```javascript
let currentMode = 'realtime';
let currentKeywords = {};
let updatedContext = {};
let debounceTimer = null;
```

### 2. 실시간 키워드 추출 함수
```javascript
async function extractKeywordsRealtime(story) {
  if (!story.trim()) return;
  
  try {
    const response = await fetch(`/api/v1/extract-keywords?mode=realtime`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ story })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    if (data.success) {
      displayKeywords(data);
      currentKeywords = data.keywords;
    }
  } catch (error) {
    console.error('키워드 추출 실패:', error);
  }
}
```

### 3. 디바운싱 처리
```javascript
function onStoryInput(event) {
  const story = event.target.value;
  
  // 디바운싱: 500ms 후에 키워드 추출
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    extractKeywordsRealtime(story);
  }, 500);
}
```

### 4. 키워드 표시 함수
```javascript
function displayKeywords(data) {
  const keywords = data.keywords;
  
  // 각 키워드 타입별로 표시
  keywords.forEach(keyword => {
    const elementId = keyword.type + 'Result';
    displayKeywordSection(elementId, keyword);
  });
  
  // 신뢰도 표시
  if (data.confidence) {
    const confidencePercent = Math.round(data.confidence * 100);
    document.getElementById('confidenceValue').textContent = `${confidencePercent}%`;
  }
}

function displayKeywordSection(elementId, keywordData) {
  const element = document.getElementById(elementId);
  const mainKeyword = keywordData.main;
  const alternatives = keywordData.alternatives || [];
  
  // 드롭다운 옵션 생성
  let optionsHtml = '';
  [mainKeyword, ...alternatives].forEach((option, index) => {
    const selected = index === 0 ? 'selected' : '';
    optionsHtml += `<option value="${option}" ${selected}>${option}</option>`;
  });
  
  // 대안 태그 생성
  let alternativesHtml = '';
  alternatives.forEach(alt => {
    alternativesHtml += `<span class="alternative-tag" onclick="selectAlternative('${keywordData.type}', '${alt}')">${alt}</span>`;
  });
  
  element.innerHTML = `
    <div class="keyword-section">
      <div class="keyword-dropdown">
        <select onchange="updateKeyword('${keywordData.type}', this.value)">
          ${optionsHtml}
        </select>
      </div>
      <div class="alternatives-section">
        <span class="alternatives-label">대안:</span>
        <div class="alternatives-tags">
          ${alternativesHtml}
        </div>
      </div>
    </div>
  `;
}
```

### 5. 키워드 업데이트 함수
```javascript
function updateKeyword(dimension, newValue) {
  console.log(`키워드 업데이트: ${dimension} = ${newValue}`);
  
  // updated_context에 변경사항 저장
  if (!updatedContext[dimension]) {
    updatedContext[dimension] = [];
  }
  updatedContext[dimension] = [newValue];
  
  // UI에 선택된 키워드 강조 표시
  highlightSelectedKeyword(dimension, newValue);
  
  // 추천 버튼 활성화
  updateRecommendButton();
}

function selectAlternative(dimension, value) {
  // 대안 클릭 시 드롭다운 값 변경
  const selectElement = document.querySelector(`select[onchange*="${dimension}"]`);
  if (selectElement) {
    selectElement.value = value;
    updateKeyword(dimension, value);
  }
}

function highlightSelectedKeyword(dimension, value) {
  // 선택된 키워드 강조 표시
  const tags = document.querySelectorAll(`.alternative-tag[onclick*="${dimension}"]`);
  tags.forEach(tag => {
    if (tag.textContent === value) {
      tag.classList.add('selected-keyword');
    } else {
      tag.classList.remove('selected-keyword');
    }
  });
}
```

### 6. 최종 추천 함수
```javascript
async function getRecommendation() {
  const story = document.getElementById('storyInput').value;
  if (!story.trim()) {
    alert('사연을 입력해주세요.');
    return;
  }
  
  try {
    const response = await fetch('/api/v1/recommend', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        story: story,
        preferred_colors: [],
        excluded_flowers: [],
        updated_context: updatedContext
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    displayRecommendationResult(result);
    
  } catch (error) {
    console.error('추천 요청 실패:', error);
    alert('추천 요청에 실패했습니다: ' + error.message);
  }
}
```

## 🔄 사용자 플로우

1. **사연 입력**: 사용자가 텍스트를 입력하면 500ms 디바운싱 후 실시간 키워드 추출
2. **키워드 표시**: 추출된 키워드가 드롭다운과 대안 태그로 표시
3. **키워드 선택**: 사용자가 드롭다운이나 대안 태그를 클릭하여 키워드 변경
4. **최종 추천**: 변경된 키워드가 `updated_context`에 저장되어 최종 추천 시 전달

## 🎯 핵심 포인트

- **실시간 피드백**: 사용자 입력 중 즉시 키워드 표시
- **사용자 수정**: 대안 키워드 선택으로 개인화
- **자동 전달**: 수정된 키워드가 자동으로 최종 추천에 반영
- **디바운싱**: API 호출 최적화를 위한 500ms 지연
- **에러 처리**: 네트워크 오류 및 API 오류 처리

## 📱 반응형 고려사항

- 모바일에서는 대안 태그를 세로로 배치
- 드롭다운은 터치 친화적으로 크기 조정
- 키워드 섹션은 카드 형태로 구분하여 가독성 향상

이 가이드를 참고하여 프론트엔드에 실시간 키워드 추출 기능을 연동해주세요! 🚀
