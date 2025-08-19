# Floiy-Reco 🌸

꽃 추천 시스템 - 실시간 키워드 추출 및 꽃 매칭 API

## 🚀 배포 정보

### 백엔드 (FastAPI)
- **프레임워크**: FastAPI + Python 3.11
- **데이터베이스**: Supabase (PostgreSQL)
- **이미지 스토리지**: Supabase Storage
- **배포**: Cloudtype

### 프론트엔드
- **기술**: HTML/CSS/JavaScript
- **배포**: Vercel

## 📁 프로젝트 구조

```
floiy-reco/
├── app/                    # 메인 애플리케이션
│   ├── api/               # API 엔드포인트
│   ├── core/              # 핵심 설정
│   ├── models/            # 데이터 모델
│   ├── pipelines/         # 데이터 파이프라인
│   ├── services/          # 비즈니스 로직
│   └── utils/             # 유틸리티
├── data/                  # 꽃 데이터
│   ├── flower_dictionary.json
│   ├── images_webp/       # 꽃 이미지들
│   └── stories.json       # 스토리 데이터
├── simple_test.html       # 프론트엔드 인터페이스
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 설정
└── .env.example          # 환경변수 예시
```

## 🔧 설치 및 실행

### 로컬 개발

1. **의존성 설치**
```bash
pip install -r requirements.txt
```

2. **환경변수 설정**
```bash
cp .env.example .env
# .env 파일에 실제 값들 입력
```

3. **서버 실행**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 실행

```bash
docker build -t floiy-reco .
docker run -p 8000:8000 floiy-reco
```

## 🌐 API 엔드포인트

### 주요 엔드포인트
- `GET /` - API 상태 확인
- `GET /health` - 헬스체크
- `POST /api/v1/analyze` - 꽃 추천 분석
- `GET /simple_test.html` - 웹 인터페이스

### Swagger 문서
- `GET /docs` - API 문서 (Swagger UI)

## 🔑 환경변수

```env
# Supabase 설정
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI 설정 (선택사항)
OPENAI_API_KEY=your_openai_api_key

# Google Drive 설정 (선택사항)
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials.json
```

## 📊 주요 기능

### 1. 실시간 키워드 추출
- 감정 분석
- 상황 인식
- 색상 선호도 추출
- 무드 분석

### 2. 꽃 매칭 알고리즘
- 의미 기반 매칭
- 색상 기반 매칭
- 계절 기반 매칭
- 감정 기반 매칭

### 3. 이미지 관리
- Supabase Storage 연동
- 자동 이미지 URL 생성
- 표준화된 파일명 체계

### 4. 스토리 관리
- 사용자 스토리 저장
- 추천 이력 관리
- 스토리 ID 체계

## 🚀 배포

### Cloudtype 배포

1. **GitHub 저장소 연결**
2. **환경변수 설정**
3. **자동 배포**

### 환경변수 설정 (Cloudtype)
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OPENAI_API_KEY` (선택사항)

## 📈 모니터링

### 헬스체크
```bash
curl https://your-domain.com/health
```

### 로그 확인
- Cloudtype 대시보드에서 실시간 로그 확인

## 🔄 업데이트

### 데이터 업데이트
- `flower_dictionary.json` 수동 업데이트
- Supabase 데이터베이스 직접 수정
- 이미지 추가 시 Supabase Storage에 업로드

### 코드 업데이트
- GitHub에 push하면 자동 배포
- 환경변수 변경 시 수동 재배포 필요

## 📞 지원

- **기술 지원**: 개발팀
- **문서**: `/docs` 엔드포인트
- **이슈**: GitHub Issues

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 8월
