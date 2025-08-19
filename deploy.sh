#!/bin/bash

# Floiy Recommendation API 배포 스크립트
# 사용법: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-staging}
DOMAIN=${2:-"your-domain.com"}

echo "🚀 Floiy Recommendation API 배포 시작..."
echo "📍 환경: $ENVIRONMENT"
echo "🌐 도메인: $DOMAIN"

# 1. 환경 변수 파일 생성
echo "📝 환경 변수 설정..."
cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_APPLICATION_CREDENTIALS=/app/google_credentials.json
ENVIRONMENT=$ENVIRONMENT
DOMAIN=$DOMAIN
EOF

# 2. SSL 인증서 생성 (개발용)
echo "🔐 SSL 인증서 생성..."
mkdir -p ssl
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=Floiy/CN=$DOMAIN"
    echo "✅ SSL 인증서 생성 완료"
else
    echo "✅ 기존 SSL 인증서 사용"
fi

# 3. 관리자 퍼널 복사
echo "📁 관리자 퍼널 설정..."
mkdir -p admin
cp admin_panel.html admin/index.html

# 4. Docker 이미지 빌드
echo "🐳 Docker 이미지 빌드..."
docker-compose build --no-cache

# 5. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리..."
docker-compose down --remove-orphans

# 6. 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작..."
docker-compose up -d

# 7. 헬스체크
echo "🏥 헬스체크 중..."
sleep 10

for i in {1..30}; do
    if curl -f http://localhost:8002/health > /dev/null 2>&1; then
        echo "✅ 서비스가 정상적으로 시작되었습니다!"
        break
    fi
    echo "⏳ 서비스 시작 대기 중... ($i/30)"
    sleep 2
done

if [ $i -eq 30 ]; then
    echo "❌ 서비스 시작 실패"
    docker-compose logs
    exit 1
fi

# 8. 배포 완료 정보
echo ""
echo "🎉 배포 완료!"
echo "📊 서비스 정보:"
echo "   - API 서버: https://$DOMAIN/api/"
echo "   - API 문서: https://$DOMAIN/docs"
echo "   - 관리자 퍼널: https://$DOMAIN/admin/"
echo "   - 이미지 서버: https://$DOMAIN/images/"
echo ""
echo "🔧 유용한 명령어:"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - 서비스 중지: docker-compose down"
echo "   - 서비스 재시작: docker-compose restart"
echo ""

# 9. 초기 데이터 동기화 (선택사항)
read -p "초기 데이터 동기화를 실행하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 초기 데이터 동기화 시작..."
    docker-compose exec floiy-reco-api python scripts/sync_flower_database.py
    docker-compose exec floiy-reco-api python scripts/auto_sync_from_spreadsheet.py
    echo "✅ 초기 데이터 동기화 완료"
fi

