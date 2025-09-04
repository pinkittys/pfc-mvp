# 🏗️ 시스템 아키텍처 및 플로우차트

## **1. 전체 시스템 아키텍처**

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[사용자 인터페이스<br/>HTML/JavaScript]
        WS[WebSocket 클라이언트]
    end
    
    subgraph "API Gateway Layer"
        FastAPI[FastAPI 서버<br/>uvicorn]
        Router[API 라우터]
    end
    
    subgraph "Core Services Layer"
        SmartExtractor[SmartWebSocketExtractor<br/>스마트 키워드 추출]
        FlowerMatcher[FlowerMatcher<br/>꽃 매칭 엔진]
        EmotionAnalyzer[EmotionAnalyzer<br/>감정 분석]
        StoryManager[StoryManager<br/>스토리 관리]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-4o-mini]
        GoogleDrive[Google Drive API<br/>이미지 동기화]
        GoogleSheet[Google Spreadsheet<br/>꽃 메타데이터]
    end
    
    subgraph "Data Layer"
        Supabase[(Supabase<br/>데이터베이스)]
        LocalFS[로컬 파일시스템<br/>이미지/데이터]
    end
    
    UI --> WS
    WS --> FastAPI
    FastAPI --> Router
    Router --> SmartExtractor
    SmartExtractor --> OpenAI
    SmartExtractor --> FlowerMatcher
    FlowerMatcher --> GoogleSheet
    FlowerMatcher --> EmotionAnalyzer
    EmotionAnalyzer --> OpenAI
    StoryManager --> Supabase
    GoogleDrive --> LocalFS
    GoogleSheet --> LocalFS
```

## **2. 실시간 키워드 추출 플로우**

```mermaid
flowchart TD
    A[사용자 타이핑] --> B{텍스트 길이 체크}
    
    B -->|10자 미만| C[규칙 기반 추출<br/>빠름, 낮은 정확도]
    B -->|10-30자| D[간단한 LLM 추출<br/>중간 속도, 중간 정확도]
    B -->|30자 이상| E[전체 LLM 추출<br/>느림, 높은 정확도]
    
    C --> F[키워드 결과 생성]
    D --> F
    E --> F
    
    F --> G[맥락 기반 대안 키워드 생성]
    G --> H[WebSocket으로 실시간 전송]
    
    H --> I[사용자 UI 업데이트]
    I --> J{사용자 선택 완료?}
    
    J -->|No| A
    J -->|Yes| K[최종 키워드 확정]
    
    K --> L[꽃 추천 요청]
```

## **3. 꽃 매칭 엔진 플로우**

```mermaid
flowchart TD
    A[사용자 선택 키워드] --> B[1차 필터링<br/>감정/상황/무드 기반]
    
    B --> C[꽃 풀 생성<br/>기본 매칭 결과]
    
    C --> D[2차 필터링<br/>색상/계절/꽃의 의미]
    
    D --> E[정밀 매칭 결과<br/>상위 후보 선별]
    
    E --> F[3차 필터링<br/>사용자 제외 키워드 반영]
    
    F --> G[최종 추천 꽃 선정]
    
    G --> H[추천 이유 생성<br/>LLM 기반]
    
    H --> I[영어 꽃 카드 메시지 생성]
    
    I --> J[결과 반환 + 스토리 저장]
```

## **4. 데이터 흐름 파이프라인**

```mermaid
sequenceDiagram
    participant User as 사용자
    participant WS as WebSocket
    participant API as FastAPI
    participant AI as OpenAI
    participant DB as Supabase
    
    User->>WS: 이야기 입력 시작
    WS->>API: 실시간 키워드 추출 요청
    API->>AI: LLM 기반 키워드 추출
    AI-->>API: 키워드 결과
    API-->>WS: 실시간 키워드 전송
    WS-->>User: 키워드 UI 업데이트
    
    User->>WS: 이야기 완성
    WS->>API: 최종 키워드 확정
    API->>API: 꽃 매칭 엔진 실행
    API->>AI: 추천 이유 생성
    AI-->>API: 추천 이유 + 영어 메시지
    API->>DB: 스토리 데이터 저장
    API-->>WS: 최종 추천 결과
    WS-->>User: 꽃 추천 결과 표시
```

## **5. 스마트 추출 전략 매트릭스**

```mermaid
graph LR
    subgraph "텍스트 길이별 추출 전략"
        A[10자 미만<br/>규칙 기반<br/>빠름<br/>정확도 60-70%]
        B[10-30자<br/>간단한 LLM<br/>중간 속도<br/>정확도 70-80%]
        C[30자 이상<br/>전체 LLM<br/>느림<br/>정확도 85-95%]
    end
    
    A --> D[즉시 응답]
    B --> E[1-2초 응답]
    C --> F[2-3초 응답]
    
    D --> G[사용자 경험: 빠른 피드백]
    E --> H[사용자 경험: 균형잡힌 응답]
    F --> I[사용자 경험: 정확한 결과]
```

## **6. 맥락 기반 키워드 생성 예시**

```mermaid
graph TD
    A[사용자 입력: "친구 생일 축하하고 싶어요"] --> B[감정 추출: "기쁨"]
    
    B --> C[상황 참조: "생일"]
    C --> D[감정 대안 생성: "사랑", "설렘"]
    
    A --> E[색상 추출: "핑크"]
    E --> F[감정 참조: "기쁨"]
    F --> G[색상 대안 생성: "라일락", "화이트"]
    
    A --> H[무드 추출: "따뜻한"]
    H --> I[감정 참조: "기쁨"]
    I --> J[무드 대안 생성: "경쾌한", "밝은"]
    
    D --> K[최종 감정: 기쁨 + 사랑, 설렘]
    G --> L[최종 색상: 핑크 + 라일락, 화이트]
    J --> M[최종 무드: 따뜻한 + 경쾌한, 밝은]
```

## **7. 시스템 성능 지표**

```mermaid
pie title 시스템 응답 속도 분포
    "규칙 기반 (10자 미만)" : 15
    "간단한 LLM (10-30자)" : 35
    "전체 LLM (30자 이상)" : 50
```

```mermaid
pie title 시스템 정확도 분포
    "규칙 기반" : 25
    "간단한 LLM" : 30
    "전체 LLM" : 45
```

## **8. 개발 완성도 현황**

```mermaid
gantt
    title 개발 완성도 현황
    dateFormat  YYYY-MM-DD
    section 데이터 구축
    꽃 메타데이터 구축    :done, data1, 2024-12-01, 2024-12-05
    꽃 이미지 데이터 구축  :done, data2, 2024-12-01, 2024-12-10
    샘플 스토리 생성      :done, data3, 2024-12-05, 2024-12-15
    
    section 백엔드 개발
    FastAPI 서버 구축     :done, backend1, 2024-12-01, 2024-12-10
    AI 추천 로직 구현     :done, backend2, 2024-12-10, 2024-12-20
    WebSocket 실시간 처리  :done, backend3, 2024-12-15, 2024-12-25
    
    section 시스템 통합
    API 엔드포인트 통합    :done, integration1, 2024-12-20, 2024-12-28
    성능 최적화          :done, integration2, 2024-12-25, 2024-12-30
    테스트 및 배포        :done, integration3, 2024-12-28, 2024-12-31
```

---

**이 다이어그램들은 Floiy-Reco 시스템의 전체적인 구조와 데이터 흐름을 시각적으로 보여줍니다.** 🎯✨
