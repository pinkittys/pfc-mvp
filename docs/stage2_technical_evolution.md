# 🏗️ 2차 개발 기술 아키텍처 진화

## **🔄 시스템 진화 과정**

### **1차 개발 (현재) → 2차 개발 (목표)**

```mermaid
graph TB
    subgraph "1차 개발 (현재)"
        A1[규칙 기반 키워드 추출]
        A2[GPT-4o-mini 기반 추출]
        A3[기본 꽃 매칭]
        A4[HTTP API + WebSocket]
        A5[Supabase 데이터베이스]
    end
    
    subgraph "2차 개발 (목표)"
        B1[임베딩 기반 의미 매칭]
        B2[멀티 모달 AI (텍스트 + 이미지)]
        B3[고도화된 꽃 매칭 + 가격 반영]
        B4[실시간 스트리밍 + 개인화]
        B5[벡터 DB + 관계형 DB 하이브리드]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A5 --> B5
    
    style A1 fill:#ffcccc
    style A2 fill:#ffcccc
    style A3 fill:#ffcccc
    style A4 fill:#ffcccc
    style A5 fill:#ffcccc
    
    style B1 fill:#ccffcc
    style B2 fill:#ccffcc
    style B3 fill:#ccffcc
    style B4 fill:#ccffcc
    style B5 fill:#ccffcc
```

---

## **🎯 핵심 기술 진화**

### **AI 모델 진화**

```mermaid
graph LR
    subgraph "1차: LLM 기반"
        A[GPT-4o-mini]
        B[규칙 기반 fallback]
        C[기본 키워드 추출]
    end
    
    subgraph "2차: 멀티 모달 AI"
        D[Sentence Transformers]
        E[Stable Diffusion]
        F[임베딩 기반 매칭]
        G[이미지 생성]
    end
    
    A --> D
    B --> F
    C --> F
    D --> E
    F --> G
    
    style A fill:#ff9999
    style D fill:#99ff99
    style E fill:#9999ff
```

### **데이터 처리 진화**

```mermaid
graph TB
    subgraph "1차: 기본 데이터 처리"
        A1[Google Spreadsheet]
        A2[로컬 이미지 저장]
        A3[Supabase 관계형 DB]
        A4[기본 검색]
    end
    
    subgraph "2차: 고도화된 데이터 처리"
        B1[경매 데이터 API 연동]
        B2[벡터 데이터베이스]
        B3[실시간 가격 정보]
        B4[의미 기반 검색]
        B5[개인화 추천]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A3 --> B5
    
    style A1 fill:#ffcccc
    style A2 fill:#ffcccc
    style A3 fill:#ffcccc
    style A4 fill:#ffcccc
    
    style B1 fill:#ccffcc
    style B2 fill:#ccffcc
    style B3 fill:#ccffcc
    style B4 fill:#ccffcc
    style B5 fill:#ccffcc
```

---

## **🏗️ 2차 개발 시스템 아키텍처**

### **전체 시스템 구조**

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[사용자 인터페이스<br/>React/Next.js]
        WS[WebSocket 클라이언트<br/>실시간 통신]
        AR[AR 기능<br/>모바일 앱]
    end
    
    subgraph "API Gateway Layer"
        FastAPI[FastAPI 서버<br/>uvicorn]
        Router[API 라우터<br/>버전 관리]
        Auth[JWT 인증<br/>OAuth 연동]
    end
    
    subgraph "AI Services Layer"
        EmbeddingService[Sentence Transformers<br/>임베딩 서비스]
        ImageGenService[Stable Diffusion<br/>이미지 생성]
        RecommendationService[고도화된 추천 엔진<br/>개인화 학습]
        ContextService[맥락 이해 서비스<br/>실시간 분석]
    end
    
    subgraph "Data Processing Layer"
        VectorDB[Pinecone/Weaviate<br/>벡터 데이터베이스]
        RelationalDB[Supabase<br/>관계형 데이터베이스]
        Cache[Redis<br/>캐싱 및 세션]
        Queue[Celery<br/>비동기 작업]
    end
    
    subgraph "External Services"
        AuctionAPI[경매 데이터 API<br/>실시간 가격]
        PaymentAPI[결제 시스템<br/>PG 연동]
        Monitoring[Prometheus + Grafana<br/>시스템 모니터링]
    end
    
    UI --> FastAPI
    WS --> FastAPI
    AR --> FastAPI
    
    FastAPI --> Router
    Router --> Auth
    
    Auth --> EmbeddingService
    Auth --> ImageGenService
    Auth --> RecommendationService
    Auth --> ContextService
    
    EmbeddingService --> VectorDB
    RecommendationService --> RelationalDB
    ContextService --> Cache
    ImageGenService --> Queue
    
    RecommendationService --> AuctionAPI
    Auth --> PaymentAPI
    FastAPI --> Monitoring
```

---

## **🚀 성능 향상 지표**

### **처리 속도 개선**

```mermaid
graph LR
    subgraph "1차 개발 성능"
        A1[키워드 추출: 1-3초]
        A2[꽃 매칭: 2-5초]
        A3[전체 추천: 3-8초]
    end
    
    subgraph "2차 개발 목표 성능"
        B1[키워드 추출: 0.5-1초]
        B2[꽃 매칭: 1-2초]
        B3[전체 추천: 2-4초]
        B4[이미지 생성: 3-5초]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    
    style A1 fill:#ffcccc
    style A2 fill:#ffcccc
    style A3 fill:#ffcccc
    
    style B1 fill:#ccffcc
    style B2 fill:#ccffcc
    style B3 fill:#ccffcc
    style B4 fill:#ccffcc
```

### **정확도 향상**

```mermaid
pie title 1차 vs 2차 개발 정확도 비교
    "1차: 색상 매칭 85%" : 85
    "1차: 감정 분석 70%" : 70
    "1차: 꽃말 매칭 75%" : 75
    "1차: 전체 추천 75%" : 75
```

```mermaid
pie title 2차 개발 목표 정확도
    "2차: 색상 매칭 90%" : 90
    "2차: 감정 분석 85%" : 85
    "2차: 꽃말 매칭 88%" : 88
    "2차: 전체 추천 85%" : 85
```

---

## **🔧 기술 구현 세부사항**

### **임베딩 기반 의미 매칭**

```mermaid
flowchart TD
    A[사용자 입력] --> B[Sentence Transformers]
    B --> C[텍스트 임베딩 벡터]
    C --> D[벡터 데이터베이스 검색]
    D --> E[Cosine Similarity 계산]
    E --> F[상위 매칭 결과]
    F --> G[가격/수요 데이터 반영]
    G --> H[최종 추천 결과]
    
    style B fill:#99ff99
    style D fill:#99ff99
    style E fill:#99ff99
```

### **이미지 생성 파이프라인**

```mermaid
flowchart TD
    A[꽃 추천 결과] --> B[템플릿 선택]
    B --> C[Stable Diffusion API]
    C --> D[이미지 생성]
    D --> E[품질 검증]
    E --> F[사용자 피드백]
    F --> G[모델 파라미터 튜닝]
    G --> C
    
    style C fill:#9999ff
    style D fill:#9999ff
    style G fill:#9999ff
```

---

## **📊 리소스 요구사항**

### **인프라 요구사항**

```mermaid
graph TB
    subgraph "현재 인프라"
        A1[CPU 서버: 2코어]
        A2[메모리: 4GB]
        A3[저장공간: 100GB]
        A4[네트워크: 기본]
    end
    
    subgraph "2차 개발 필요 인프라"
        B1[GPU 서버: 8코어 + GPU]
        B2[메모리: 16GB+]
        B3[저장공간: 500GB+]
        B4[네트워크: 고속 + CDN]
        B5[벡터 DB: Pinecone/Weaviate]
        B6[캐싱: Redis 클러스터]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A1 --> B5
    A1 --> B6
    
    style A1 fill:#ffcccc
    style A2 fill:#ffcccc
    style A3 fill:#ffcccc
    style A4 fill:#ffcccc
    
    style B1 fill:#ccffcc
    style B2 fill:#ccffcc
    style B3 fill:#ccffcc
    style B4 fill:#ccffcc
    style B5 fill:#ccffcc
    style B6 fill:#ccffcc
```

---

## **🎯 구현 우선순위**

### **Phase별 구현 순서**

```mermaid
gantt
    title 2차 개발 구현 우선순위
    dateFormat  YYYY-MM-DD
    section Phase 1 (25.09-25.10)
    데이터 확장          :priority1, 2025-09-01, 2025-10-31
    경매 API 연동        :priority1, 2025-09-15, 2025-10-15
    
    section Phase 2 (25.10-25.11)
    임베딩 모델 구축     :priority2, 2025-10-01, 2025-11-15
    벡터 DB 연동        :priority2, 2025-10-15, 2025-11-30
    
    section Phase 3 (25.11-25.12)
    이미지 생성 모델     :priority3, 2025-11-01, 2025-12-31
    템플릿 자동화        :priority3, 2025-11-15, 2025-12-15
    
    section Phase 4 (25.12)
    통합 테스트          :priority4, 2025-12-01, 2025-12-31
    
    section Phase 5 (26.01)
    베타 출시            :priority5, 2026-01-01, 2026-01-31
```

---

**이 문서는 Floiy-Reco의 2차 개발에서 기술적 진화 과정과 새로운 아키텍처를 상세히 보여줍니다.** 🚀✨
