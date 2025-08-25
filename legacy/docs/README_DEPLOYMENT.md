# 🚀 Floiy Recommendation API 배포 가이드

## 📋 배포 방법

### 1. Docker를 사용한 배포 (권장)

#### 사전 준비사항
- Docker & Docker Compose 설치
- 도메인 설정 (선택사항)
- SSL 인증서 (프로덕션용)

#### 배포 단계

```bash
# 1. 저장소 클론
git clone <repository-url>
cd floiy-reco

# 2. 환경 변수 설정
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/google-credentials.json"

# 3. 배포 스크립트 실행
./deploy.sh production your-domain.com
```

#### 배포 스크립트 기능
- ✅ SSL 인증서 자동 생성
- ✅ Docker 이미지 빌드
- ✅ 컨테이너 배포
- ✅ 헬스체크
- ✅ 초기 데이터 동기화

### 2. 수동 배포

#### Docker Compose 사용
```bash
# 1. 환경 변수 파일 생성
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=/app/google_credentials.json
ENVIRONMENT=production
DOMAIN=your-domain.com
EOF

# 2. SSL 인증서 생성
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Floiy/CN=your-domain.com"

# 3. 관리자 퍼널 설정
mkdir -p admin
cp admin_panel.html admin/index.html

# 4. 서비스 시작
docker-compose up -d

# 5. 로그 확인
docker-compose logs -f
```

#### 직접 Python 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
export OPENAI_API_KEY="your-openai-api-key"

# 3. 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## 🌐 서비스 URL

배포 완료 후 다음 URL로 접근 가능:

- **API 서버**: `https://your-domain.com/api/v1/`
- **API 문서**: `https://your-domain.com/docs`
- **관리자 퍼널**: `https://your-domain.com/admin/`
- **이미지 서버**: `https://your-domain.com/images/`
- **헬스체크**: `https://your-domain.com/health`

## 🔧 관리 명령어

### Docker Compose 명령어
```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart

# 서비스 중지
docker-compose down

# 특정 서비스만 재시작
docker-compose restart floiy-reco-api
```

### 데이터 동기화
```bash
# 꽃 데이터베이스 동기화
docker-compose exec floiy-reco-api python scripts/sync_flower_database.py

# 이미지 동기화
docker-compose exec floiy-reco-api python scripts/auto_sync_from_spreadsheet.py

# 전체 동기화
docker-compose exec floiy-reco-api python scripts/full_sync.py
```

## 📊 모니터링

### 헬스체크
```bash
# 헬스체크 확인
curl -f https://your-domain.com/health

# 응답 예시
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00",
  "version": "1.0.0",
  "services": {
    "api": "running",
    "database": "connected",
    "openai": "available"
  }
}
```

### 로그 모니터링
```bash
# 실시간 로그 확인
docker-compose logs -f floiy-reco-api

# 에러 로그만 확인
docker-compose logs -f floiy-reco-api | grep ERROR

# 특정 시간대 로그
docker-compose logs --since="2024-12-19T10:00:00" floiy-reco-api
```

## 🔒 보안 설정

### 환경 변수
```bash
# 필수 환경 변수
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=/app/google_credentials.json

# 선택적 환경 변수
ENVIRONMENT=production
DOMAIN=your-domain.com
DEBUG=false
LOG_LEVEL=INFO
```

### SSL 인증서 (프로덕션)
```bash
# Let's Encrypt 사용 (권장)
certbot certonly --standalone -d your-domain.com

# 인증서 파일 복사
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem

# 서비스 재시작
docker-compose restart nginx
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8002

# 다른 포트 사용
docker-compose up -d -p 8003:8002
```

#### 2. 메모리 부족
```bash
# Docker 메모리 제한 확인
docker stats

# 컨테이너 리소스 제한
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 3. 이미지 로드 실패
```bash
# 이미지 권한 확인
ls -la data/images_webp/

# 권한 수정
chmod -R 755 data/images_webp/
```

#### 4. API 응답 지연
```bash
# 로그 확인
docker-compose logs floiy-reco-api | grep "timeout"

# OpenAI API 상태 확인
curl -I https://api.openai.com/v1/models
```

### 디버깅 모드
```bash
# 디버그 모드로 실행
docker-compose down
DEBUG=true docker-compose up -d

# 상세 로그 확인
docker-compose logs -f floiy-reco-api
```

## 📈 성능 최적화

### Nginx 설정 최적화
```nginx
# nginx.conf에 추가
worker_processes auto;
worker_connections 1024;

# Gzip 압축
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;
```

### Docker 최적화
```yaml
# docker-compose.yml에 추가
services:
  floiy-reco-api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🔄 백업 및 복구

### 데이터 백업
```bash
# 꽃 데이터베이스 백업
cp data/flower_dictionary.json backup/flower_dictionary_$(date +%Y%m%d).json

# 이미지 백업
tar -czf backup/images_$(date +%Y%m%d).tar.gz data/images_webp/

# 전체 백업
docker-compose exec floiy-reco-api tar -czf /app/backup_$(date +%Y%m%d).tar.gz /app/data/
```

### 복구
```bash
# 데이터 복구
cp backup/flower_dictionary_20241219.json data/flower_dictionary.json

# 이미지 복구
tar -xzf backup/images_20241219.tar.gz -C data/

# 서비스 재시작
docker-compose restart floiy-reco-api
```

## 📞 지원

### 로그 수집
```bash
# 문제 발생 시 로그 수집
docker-compose logs --since="1h" > logs_$(date +%Y%m%d_%H%M%S).txt

# 시스템 정보 수집
docker system info > system_info.txt
docker-compose ps > service_status.txt
```

### 연락처
- **개발팀**: dev@floiy.com
- **운영팀**: ops@floiy.com
- **긴급연락**: +82-10-1234-5678

---

**배포 가이드 버전**: 1.0.0  
**최종 업데이트**: 2024년 12월  
**작성자**: Floiy Development Team

