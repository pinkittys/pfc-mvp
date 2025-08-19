# 🌸 Plain Flower Club 배포 가이드

## 🚀 간단 배포 방법

### 1단계: 서버 준비
- **VPS/클라우드 서버** (AWS, GCP, Vultr, DigitalOcean 등)
- **도메인**: plainflowerclub.com (이미 구매 완료)
- **Docker & Docker Compose** 설치 필요

### 2단계: 코드 업로드
```bash
# 서버에 접속 후
git clone <your-repository-url>
cd floiy-reco
```

### 3단계: 배포 실행
```bash
# 배포 스크립트 실행
./deploy_plainflowerclub.sh
```

스크립트가 실행되면:
1. OpenAI API 키 입력 요청
2. Google 인증서 파일 경로 입력 (선택사항)
3. 자동으로 SSL 인증서 생성
4. Docker 이미지 빌드 및 배포
5. 헬스체크 및 완료 알림

### 4단계: 도메인 연결
가비아에서 도메인 DNS 설정:
- **A 레코드**: `@` → 서버 IP 주소
- **A 레코드**: `www` → 서버 IP 주소

## 🌐 배포 완료 후 접속 URL

- **메인 사이트**: https://plainflowerclub.com
- **API 문서**: https://plainflowerclub.com/docs
- **관리자 퍼널**: https://plainflowerclub.com/admin/
- **이미지 서버**: https://plainflowerclub.com/images/

## 🔧 관리 명령어

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart

# 서비스 중지
docker-compose down
```

## 📞 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs -f

# 컨테이너 상태 확인
docker-compose ps

# 헬스체크
curl https://plainflowerclub.com/health
```

### 도메인 연결이 안 되는 경우
1. 가비아 DNS 설정 확인
2. 서버 방화벽 설정 확인 (포트 80, 443, 8002)
3. DNS 전파 대기 (최대 24시간)

## 💰 예상 비용

- **VPS 서버**: 월 $5-20 (사용량에 따라)
- **도메인**: 연 $10-15 (이미 구매 완료)
- **OpenAI API**: 사용량에 따라 (월 $1-50)

## 🎯 프론트엔드 개발자에게 전달할 것

1. **API Base URL**: `https://plainflowerclub.com/api/v1`
2. **API 문서**: `API_DOCUMENTATION_PLAINFLOWERCLUB.md`
3. **이미지 URL 패턴**: `https://plainflowerclub.com/images/{flower-folder}/{color}.webp`

## 📋 체크리스트

- [ ] 서버 준비 (VPS/클라우드)
- [ ] Docker & Docker Compose 설치
- [ ] 코드 업로드
- [ ] OpenAI API 키 준비
- [ ] 배포 스크립트 실행
- [ ] 도메인 DNS 설정
- [ ] SSL 인증서 확인
- [ ] API 테스트
- [ ] 프론트엔드 개발자에게 API 문서 전달

---

**도메인**: plainflowerclub.com  
**배포 스크립트**: `deploy_plainflowerclub.sh`  
**API 문서**: `API_DOCUMENTATION_PLAINFLOWERCLUB.md`

