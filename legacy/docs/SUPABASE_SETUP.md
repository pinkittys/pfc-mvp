# Supabase 데이터 동기화 가이드

## 📋 개요
이 가이드는 꽃 추천 시스템의 데이터를 Supabase에 동기화하는 방법을 설명합니다.

## 🗄️ 전송되는 데이터

### 1. 꽃 카탈로그 (flower_catalog)
- **소스**: 구글 스프레드시트
- **내용**: 꽃 ID, 이름(한글/영문), 학명, 색상, 계절 정보, 감정/무드 등
- **레코드 수**: ~155개

### 2. 스토리 추천 로그 (stories)
- **소스**: `data/stories.json`
- **내용**: 사용자 스토리, 추천된 꽃, 감정 분석, 추천 이유, 꽃카드 메시지 등
- **레코드 수**: 생성된 추천 수만큼

### 3. 꽃 이미지 (flower_images)
- **소스**: `data/images_webp/`, `base64_images.json`
- **내용**: 꽃별 색상별 이미지 (Base64 인코딩)
- **레코드 수**: ~500개 (꽃 × 색상 조합)

## 🚀 설정 방법

### 1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com) 접속
2. 새 프로젝트 생성
3. 프로젝트 URL과 API 키 확인

### 2. 환경변수 설정
```bash
# .env 파일에 추가
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. 데이터베이스 스키마 생성
1. Supabase Dashboard → SQL Editor
2. `supabase_schema.sql` 내용 복사하여 실행
3. 테이블 생성 확인

### 4. 데이터 동기화 실행
```bash
python scripts/supabase_data_sync.py
```

## 📊 테이블 구조

### flower_catalog
```sql
- id: BIGSERIAL PRIMARY KEY
- flower_id: VARCHAR(100) UNIQUE
- name_ko: VARCHAR(100) (한글명)
- name_en: VARCHAR(100) (영문명)
- scientific_name: VARCHAR(100) (학명)
- color_code: VARCHAR(10) (색상 코드)
- season_months: VARCHAR(50) (계절 정보)
- moods, emotions, contexts: TEXT
- created_at, updated_at: TIMESTAMP
```

### stories
```sql
- id: BIGSERIAL PRIMARY KEY
- story_id: VARCHAR(50) UNIQUE (S250819-SWP-000001 형식)
- story: TEXT (사용자 입력 스토리)
- emotions: JSONB (감정 분석 결과)
- matched_flower: JSONB (매칭된 꽃 정보)
- recommendation_reason: TEXT (추천 이유)
- flower_card_message: TEXT (꽃카드 메시지)
- season_info: VARCHAR(100) (계절 정보)
- keywords, hashtags: JSONB
- created_at: TIMESTAMP
```

### flower_images
```sql
- id: BIGSERIAL PRIMARY KEY
- flower_id: VARCHAR(100) (꽃 ID)
- color: VARCHAR(50) (색상)
- image_data: TEXT (Base64 인코딩)
- image_url: VARCHAR(255) (이미지 URL)
- created_at: TIMESTAMP
```

## 🔍 유용한 쿼리

### 추천 통계 조회
```sql
SELECT * FROM flower_recommendation_stats;
```

### 꽃별 이미지 조회
```sql
SELECT * FROM flower_catalog_with_images 
WHERE flower_id = 'rose-wh';
```

### 최근 추천 조회
```sql
SELECT story_id, story, matched_flower->>'flower_name' as flower_name
FROM stories 
ORDER BY created_at DESC 
LIMIT 10;
```

## ⚠️ 주의사항

1. **이미지 크기**: Base64 인코딩된 이미지는 크기가 클 수 있음
2. **API 제한**: Supabase 무료 플랜의 API 호출 제한 확인
3. **데이터 백업**: 동기화 전 기존 데이터 백업 권장
4. **권한 설정**: RLS 정책에 따라 읽기/쓰기 권한 확인

## 🔄 자동 동기화

### Cron Job 설정 (선택사항)
```bash
# 매일 자정에 동기화
0 0 * * * cd /path/to/floiy-reco && python scripts/supabase_data_sync.py
```

### GitHub Actions 설정 (선택사항)
```yaml
name: Supabase Sync
on:
  schedule:
    - cron: '0 0 * * *'  # 매일 자정
  workflow_dispatch:     # 수동 실행 가능

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests
      - name: Sync to Supabase
        run: python scripts/supabase_data_sync.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

## 📈 모니터링

### 동기화 상태 확인
```bash
# 로그 확인
tail -f logs/supabase_sync.log

# 데이터베이스 연결 테스트
python -c "
import os
import requests
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
response = requests.get(f'{url}/rest/v1/flower_catalog?select=count', 
                       headers={'apikey': key})
print(f'연결 상태: {response.status_code}')
print(f'꽃 카탈로그 수: {response.json()}')
"
```

## 🆘 문제 해결

### 일반적인 오류
1. **인증 오류**: API 키 확인
2. **권한 오류**: RLS 정책 확인
3. **데이터 크기 오류**: 이미지 크기 확인
4. **네트워크 오류**: 인터넷 연결 확인

### 로그 확인
```bash
python scripts/supabase_data_sync.py 2>&1 | tee sync.log
```
