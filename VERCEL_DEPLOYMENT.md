# Vercel 배포 가이드

## 🚀 빠른 배포 방법

### 1. Vercel CLI 설치
```bash
npm i -g vercel
```

### 2. 프로젝트 디렉토리에서 로그인
```bash
vercel login
```

### 3. 배포 실행
```bash
vercel
```

### 4. 환경 변수 설정
Vercel 대시보드에서 다음 환경 변수 설정:

```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
DATABASE_URL=your_database_url_here
ENVIRONMENT=production
LOG_LEVEL=info
```

## 📁 프로젝트 구조

```
floiy-reco/
├── app/                    # FastAPI 백엔드
├── frontend/              # 프론트엔드 파일
├── data/                  # 이미지 및 데이터
├── vercel.json           # Vercel 설정
├── requirements-vercel.txt # Vercel용 의존성
└── VERCEL_DEPLOYMENT.md  # 이 가이드
```

## ⚠️ 주의사항

1. **이미지 파일**: `data/images_webp/` 폴더의 이미지들이 Vercel에 업로드됨
2. **API 엔드포인트**: `/api/v1/*` 경로로 접근
3. **정적 파일**: `/images/*`, `/frontend/*` 경로로 접근

## 🔧 커스텀 도메인 설정

Vercel 대시보드에서 `plainflower.club` 도메인 연결 가능

## 📊 배포 후 확인

1. **API 엔드포인트**: `https://your-project.vercel.app/api/v1/health`
2. **프론트엔드**: `https://your-project.vercel.app/frontend/pages/simple_test.html`
3. **이미지**: `https://your-project.vercel.app/images/marguerite-daisy-wh.webp`
