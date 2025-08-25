# 🌸 구글 드라이브 꽃 이미지 자동 동기화 시스템

구글 드라이브에 업로드되는 꽃 이미지를 자동으로 다운로드하고 시스템에 등록하는 기능입니다.

## 🚀 주요 기능

- **자동 파일 감지**: 구글 드라이브 폴더의 새 이미지 파일 자동 감지
- **파일명 파싱**: `꽃이름-색상코드.확장자` 형식의 파일명에서 정보 추출
- **WebP 변환**: 다운로드한 이미지를 WebP 형식으로 자동 변환
- **Base64 인코딩**: 변환된 이미지를 base64로 인코딩하여 시스템에 저장
- **실시간 모니터링**: 5분마다 구글 드라이브 폴더를 확인하여 새 파일 동기화

## 📋 파일명 규칙

구글 드라이브에 업로드하는 이미지 파일은 다음 형식을 따라야 합니다:

```
꽃이름-색상코드.확장자
```

### 예시:
- `alstroemeria-spp-wh.png` → 알스트로메리아 화이트
- `rose-pk.jpg` → 장미 핑크
- `lily-wh.png` → 백합 화이트

### 지원하는 색상 코드:
- `wh` / `white` → 화이트
- `iv` / `ivory` → 아이보리
- `be` / `beige` → 베이지
- `yl` / `yellow` → 옐로우
- `or` / `orange` → 오렌지
- `cr` / `coral` → 코랄
- `pk` / `pink` → 핑크
- `rd` / `red` → 레드
- `ll` / `lilac` → 라일락
- `pu` / `purple` → 퍼플
- `bl` / `blue` → 블루
- `gr` / `green` → 그린

## 🔧 설치 및 설정

### 1. 필요한 패키지 설치

```bash
pip install -r requirements_google_drive.txt
```

### 2. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Drive API 활성화
4. 사용자 인증 정보 생성
5. OAuth 2.0 클라이언트 ID 생성
6. JSON 키 다운로드 후 `credentials.json`으로 이름 변경

### 3. API 설정 스크립트 실행

```bash
python scripts/setup_google_drive.py --setup
```

또는 설정 상태 확인:

```bash
python scripts/setup_google_drive.py --check
```

## 🎯 사용법

### 1. 관리자 페이지에서 사용

1. 관리자 페이지 접속: `http://localhost:8002/admin`
2. "데이터 동기화" 섹션에서 다음 버튼 사용:
   - **☁️ 구글 드라이브 동기화**: 수동으로 한 번 동기화
   - **👀 드라이브 모니터링 시작**: 자동 모니터링 시작 (5분마다)
   - **⏹️ 드라이브 모니터링 중단**: 자동 모니터링 중단

### 2. 명령줄에서 사용

#### 수동 동기화
```bash
python scripts/google_drive_api_sync.py
```

#### 강제 동기화 (모든 파일 다시 처리)
```bash
python scripts/google_drive_api_sync.py --force
```

#### 자동 모니터링 시작
```bash
python scripts/google_drive_api_sync.py --watch
```

#### 모니터링 간격 설정 (기본: 5분)
```bash
python scripts/google_drive_api_sync.py --watch --interval 600  # 10분
```

## 📁 파일 구조

```
floiy-reco/
├── scripts/
│   ├── google_drive_api_sync.py      # 메인 동기화 스크립트
│   ├── setup_google_drive.py         # API 설정 도우미
│   └── google_drive_sync.py          # 기본 동기화 스크립트
├── data/
│   ├── raw_images/                   # 다운로드한 원본 이미지
│   │   ├── alstroemeria-spp/
│   │   │   ├── alstroemeria-spp-wh.png
│   │   │   └── alstroemeria-spp-pk.png
│   │   └── rose/
│   │       └── rose-pk.jpg
│   └── images_webp/                  # 변환된 WebP 이미지
│       ├── alstroemeria-spp/
│       │   ├── 화이트.webp
│       │   └── 핑크.webp
│       └── rose/
│           └── 핑크.webp
├── credentials.json                  # Google API 인증 정보
├── token.json                       # OAuth 토큰
├── last_sync.json                   # 마지막 동기화 정보
├── base64_images.json               # Base64 인코딩된 이미지
└── logs/
    └── google_drive_api_sync.log    # 동기화 로그
```

## 🔄 동기화 프로세스

1. **파일 감지**: 구글 드라이브 폴더에서 새 이미지 파일 확인
2. **파일명 파싱**: 파일명에서 꽃 이름과 색상 정보 추출
3. **다운로드**: 원본 이미지를 `data/raw_images/` 폴더에 저장
4. **WebP 변환**: 이미지를 WebP 형식으로 변환 (품질 85%)
5. **이동**: 변환된 파일을 `data/images_webp/` 폴더로 이동
6. **Base64 인코딩**: WebP 이미지를 base64로 인코딩
7. **시스템 업데이트**: `base64_images.json` 및 `flower_matcher.py` 업데이트

## 📊 로그 및 모니터링

### 로그 파일 위치
- `logs/google_drive_api_sync.log`: 상세한 동기화 로그
- `last_sync.json`: 마지막 동기화 통계 정보

### 로그 예시
```
2024-08-16 22:45:30 - INFO - 🔄 구글 드라이브 API 동기화 시작...
2024-08-16 22:45:31 - INFO - 구글 드라이브에서 15개 이미지 파일 발견
2024-08-16 22:45:32 - INFO - 파일 다운로드 완료: alstroemeria-spp-wh.png
2024-08-16 22:45:33 - INFO - WebP 변환 완료: alstroemeria-spp-wh.webp
2024-08-16 22:45:34 - INFO - 이미지 처리 완료: alstroemeria-spp - 화이트
2024-08-16 22:45:35 - INFO - 🎉 구글 드라이브 API 동기화 완료!
2024-08-16 22:45:35 - INFO - 📊 처리된 파일: 15개
2024-08-16 22:45:35 - INFO - 📥 다운로드: 15개
2024-08-16 22:45:35 - INFO - 🔄 변환: 15개
2024-08-16 22:45:35 - INFO - ❌ 오류: 0개
```

## ⚠️ 주의사항

1. **파일명 규칙**: 반드시 `꽃이름-색상코드.확장자` 형식을 따라야 합니다.
2. **API 할당량**: Google Drive API는 일일 사용량 제한이 있습니다.
3. **토큰 만료**: OAuth 토큰은 만료될 수 있으므로 주기적으로 갱신이 필요합니다.
4. **네트워크**: 안정적인 인터넷 연결이 필요합니다.

## 🛠️ 문제 해결

### 자주 발생하는 문제

1. **"credentials.json 파일이 없습니다"**
   - Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 JSON 키를 다운로드하세요.

2. **"토큰이 만료되었습니다"**
   - `python scripts/setup_google_drive.py --check`를 실행하여 토큰을 갱신하세요.

3. **"폴더 접근 실패"**
   - 구글 드라이브 폴더 ID가 올바른지 확인하세요.
   - 폴더에 대한 읽기 권한이 있는지 확인하세요.

4. **"WebP 변환 실패"**
   - Pillow 라이브러리가 설치되어 있는지 확인하세요.
   - 이미지 파일이 손상되지 않았는지 확인하세요.

### 디버깅

상세한 로그를 보려면:

```bash
tail -f logs/google_drive_api_sync.log
```

## 🔗 관련 링크

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Drive API 문서](https://developers.google.com/drive/api)
- [OAuth 2.0 설정 가이드](https://developers.google.com/identity/protocols/oauth2)

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.


