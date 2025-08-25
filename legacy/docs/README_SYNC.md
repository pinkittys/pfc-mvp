# 🌺 꽃 데이터베이스 동기화 시스템

구글 스프레드시트와 꽃 추천 시스템을 자동으로 동기화하는 시스템입니다.

## 📋 시스템 구성

### 1. **자동 동기화 스크립트** (`scripts/sync_flower_database.py`)
- 구글 스프레드시트에서 데이터 가져오기
- `flower_matcher.py` 자동 업데이트
- 컬러별 available 여부 확인

### 2. **관리자 API 엔드포인트**
- `/api/v1/admin/sync-spreadsheet`: 스프레드시트 동기화
- `/api/v1/admin/full-sync`: 전체 동기화
- `/api/v1/admin/auto-sync`: 기존 자동 동기화

### 3. **Cron Job 자동 실행** (`scripts/setup_cron.py`)
- 6시간마다 자동 동기화
- 로그 파일 생성

### 4. **관리자 페이지** (`admin_panel.html`)
- 웹 인터페이스로 동기화 실행
- 실시간 상태 확인

## 🚀 사용 방법

### 방법 1: 관리자 페이지 사용 (추천)

1. **서버 시작**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

2. **관리자 페이지 접속**
```
http://localhost:8002/admin_panel.html
```

3. **동기화 버튼 클릭**
- 📊 **스프레드시트 동기화**: 구글 스프레드시트만 동기화
- 🔄 **자동 동기화**: 이미지 + flower_matcher + base64
- 🌟 **전체 동기화**: 스프레드시트 + 이미지 + flower_matcher + base64

### 방법 2: 명령어 직접 실행

```bash
# 스프레드시트 동기화만
python scripts/sync_flower_database.py

# Cron Job 설정 (6시간마다 자동 실행)
python scripts/setup_cron.py setup

# Cron Job 상태 확인
python scripts/setup_cron.py status

# Cron Job 제거
python scripts/setup_cron.py remove
```

### 방법 3: API 직접 호출

```bash
# 스프레드시트 동기화
curl -X POST http://localhost:8002/api/v1/admin/sync-spreadsheet

# 전체 동기화
curl -X POST http://localhost:8002/api/v1/admin/full-sync

# 자동 동기화
curl -X POST http://localhost:8002/api/v1/admin/auto-sync
```

## 📊 구글 스프레드시트 형식

스프레드시트는 다음 컬럼을 포함해야 합니다:

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| `flower_id` | 꽃 폴더명 | `marguerite-daisy` |
| `name_ko` | 한국어 이름 | `마가렛` |
| `name_en` | 영어 이름 | `Marguerite Daisy` |
| `scientific_name` | 학명 | `Argyranthemum frutescens` |
| `base_color` | 기본 컬러 | `화이트` |
| `moods` | 무드 (쉼표 구분) | `로맨틱,내추럴,우아함` |
| `emotions` | 감정 (쉼표 구분) | `감사,평온,애틋함` |
| `contexts` | 사용 맥락 (쉼표 구분) | `감사전달,고백,인테리어` |
| `flower_language_short` | 꽃말 | `진심, 순결한 사랑` |

## 🔄 동기화 프로세스

### 1. **스프레드시트 데이터 가져오기**
- CSV 형식으로 내보내기
- 데이터 파싱 및 검증

### 2. **컬러별 Available 확인**
- 실제 이미지 파일 존재 여부 확인
- `data/images_webp/{flower_id}/{color}.webp` 경로 확인

### 3. **flower_matcher.py 업데이트**
- 기존 파일 백업 생성
- 새로운 데이터로 업데이트
- 컬러별 의미 정보 추가

### 4. **자동 동기화 (선택사항)**
- 이미지 폴더 스캔
- base64_images.json 업데이트

## 📁 파일 구조

```
floiy-reco/
├── scripts/
│   ├── sync_flower_database.py    # 동기화 스크립트
│   └── setup_cron.py             # Cron Job 설정
├── app/
│   └── api/v1/endpoints/
│       └── admin.py              # 관리자 API
├── admin_panel.html              # 관리자 페이지
├── data/
│   └── images_webp/              # 꽃 이미지 폴더
└── logs/                         # 동기화 로그
```

## ⚙️ 설정 옵션

### 스프레드시트 URL 변경
`scripts/sync_flower_database.py`에서:
```python
self.spreadsheet_url = "YOUR_SPREADSHEET_URL"
```

### 동기화 주기 변경
`scripts/setup_cron.py`에서:
```python
cron_command = f"0 */6 * * * ..."  # 6시간마다
# 0 */2 * * * = 2시간마다
# 0 */12 * * * = 12시간마다
```

### 로그 레벨 설정
환경변수로 설정:
```bash
export FLOWER_SYNC_LOG_LEVEL=DEBUG
```

## 🔍 문제 해결

### 1. **스프레드시트 접근 오류**
- 스프레드시트 공유 설정 확인
- URL이 올바른지 확인

### 2. **이미지 파일 없음**
- `data/images_webp/` 폴더에 이미지 파일 확인
- 파일명이 컬러명과 일치하는지 확인

### 3. **동기화 실패**
- 로그 파일 확인: `logs/sync.log`
- 네트워크 연결 상태 확인

### 4. **Cron Job 실행 안됨**
```bash
# Cron Job 상태 확인
crontab -l

# 로그 확인
tail -f logs/sync.log
```

## 📈 모니터링

### 로그 확인
```bash
# 실시간 로그 모니터링
tail -f logs/sync.log

# 최근 100줄 로그
tail -n 100 logs/sync.log
```

### 동기화 상태 확인
```bash
# API로 상태 확인
curl http://localhost:8002/api/v1/admin/available-flowers
```

## 🎯 권장사항

1. **정기적 동기화**: 6시간마다 자동 동기화 권장
2. **백업 관리**: 동기화 전 자동 백업 생성
3. **테스트**: 새로운 데이터 추가 시 테스트 환경에서 먼저 확인
4. **모니터링**: 로그 파일 정기적 확인

## 🔗 관련 파일

- **스프레드시트**: https://docs.google.com/spreadsheets/d/1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY/edit?gid=2100622490#gid=2100622490
- **관리자 페이지**: http://localhost:8002/admin_panel.html
- **API 문서**: http://localhost:8002/docs


