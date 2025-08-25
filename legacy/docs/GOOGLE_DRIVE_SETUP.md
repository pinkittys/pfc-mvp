# Google Drive API 설정 가이드

꽃 캘리그래피 이미지를 Google Drive에서 자동으로 동기화하기 위한 설정 방법입니다.

## 방법 1: OAuth 2.0 클라이언트 ID (현재 사용 중)

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 1.2 Google Drive API 활성화
1. "API 및 서비스" → "라이브러리" 메뉴로 이동
2. "Google Drive API" 검색 후 활성화

### 1.3 OAuth 2.0 클라이언트 ID 생성
1. "API 및 서비스" → "사용자 인증 정보" 메뉴로 이동
2. "사용자 인증 정보 만들기" → "OAuth 2.0 클라이언트 ID" 선택
3. 애플리케이션 유형: "데스크톱 앱" 선택
4. 이름 입력 후 "만들기" 클릭

### 1.4 OAuth 동의 화면 설정 (중요!)
1. "API 및 서비스" → "OAuth 동의 화면" 메뉴로 이동
2. "테스트 사용자" 섹션에서 "테스트 사용자 추가" 클릭
3. **본인의 Google 계정 이메일** 입력 후 저장
4. 이 설정이 없으면 "access_denied" 오류 발생

### 1.5 credentials.json 다운로드
1. 생성된 OAuth 2.0 클라이언트 ID 옆의 다운로드 버튼 클릭
2. 다운로드된 파일을 프로젝트 루트 디렉토리에 `credentials.json`으로 저장

## 방법 2: 서비스 계정 (더 간단, 권장)

### 2.1 서비스 계정 생성
1. "API 및 서비스" → "사용자 인증 정보" 메뉴로 이동
2. "사용자 인증 정보 만들기" → "서비스 계정" 선택
3. 서비스 계정 이름 입력 후 "만들기" 클릭

### 2.2 서비스 계정 키 생성
1. 생성된 서비스 계정 클릭
2. "키" 탭 → "키 추가" → "새 키 만들기"
3. "JSON" 선택 후 "만들기" 클릭
4. 다운로드된 JSON 파일을 `service-account-key.json`으로 저장

### 2.3 Google Drive 폴더 공유
1. [Google Drive](https://drive.google.com/)에서 캘리그래피 폴더 열기
2. 폴더 우클릭 → "공유" → "링크 복사"
3. "링크가 있는 모든 사용자" → "편집자" 권한 설정
4. 또는 서비스 계정 이메일을 직접 추가

## 3. 프로젝트 설정

### 3.1 파일 위치
```
floiy-reco/
├── credentials.json  ← OAuth 2.0 방식
├── service-account-key.json  ← 서비스 계정 방식
├── app/
├── data/
└── ...
```

### 3.2 필요한 라이브러리 설치
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## 4. 사용 방법

### 4.1 OAuth 2.0 방식
```bash
# 서버 재시작
pkill -f "uvicorn" && sleep 2 && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 동기화 테스트
curl -X POST http://localhost:8002/api/v1/admin/calligraphy/sync
```

### 4.2 서비스 계정 방식
```bash
# 서비스 계정 키 파일이 있으면 자동으로 사용됨
curl -X POST http://localhost:8002/api/v1/admin/calligraphy/sync
```

## 5. 문제 해결

### 5.1 "access_denied" 오류
- OAuth 동의 화면에서 테스트 사용자 추가 확인
- 또는 서비스 계정 방식 사용

### 5.2 "credentials.json 파일이 필요합니다" 오류
- 파일명이 정확히 `credentials.json`인지 확인
- 프로젝트 루트 디렉토리에 있는지 확인

### 5.3 더미 데이터 사용 중
- Google Drive API 인증이 실패하면 자동으로 더미 데이터 사용
- 인증 설정 완료 후 서버 재시작 필요
