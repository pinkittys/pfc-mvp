#!/bin/bash

# Plain Flower Club 배포 스크립트
# 도메인: plainflowerclub.com

set -e

echo "🌸 Plain Flower Club 배포 시작..."
echo "🌐 도메인: plainflowerclub.com"

# 1. 환경 변수 설정
echo "📝 환경 변수 설정..."
read -p "OpenAI API 키를 입력하세요: " OPENAI_API_KEY
read -p "Google 서비스 계정 JSON 파일 경로를 입력하세요 (선택사항): " GOOGLE_CREDENTIALS_PATH

cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_APPLICATION_CREDENTIALS=/app/google_credentials.json
ENVIRONMENT=production
DOMAIN=plainflowerclub.com
EOF

# 2. SSL 인증서 생성 (개발용)
echo "🔐 SSL 인증서 생성..."
mkdir -p ssl
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=PlainFlowerClub/CN=plainflowerclub.com"
    echo "✅ SSL 인증서 생성 완료"
else
    echo "✅ 기존 SSL 인증서 사용"
fi

# 3. Google 인증서 복사 (있는 경우)
if [ ! -z "$GOOGLE_CREDENTIALS_PATH" ] && [ -f "$GOOGLE_CREDENTIALS_PATH" ]; then
    echo "📄 Google 인증서 복사..."
    cp "$GOOGLE_CREDENTIALS_PATH" google_credentials.json
    echo "✅ Google 인증서 복사 완료"
else
    echo "⚠️ Google 인증서가 없습니다. 스프레드시트 동기화 기능은 사용할 수 없습니다."
fi

# 4. 관리자 퍼널 설정
echo "📁 관리자 퍼널 설정..."
mkdir -p admin
cp admin_panel.html admin/index.html

# 5. Docker 이미지 빌드
echo "🐳 Docker 이미지 빌드..."
docker-compose build --no-cache

# 6. 기존 컨테이너 정리
echo "🛑 기존 컨테이너 정리..."
docker-compose down --remove-orphans

# 7. 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작..."
docker-compose up -d

# 8. 헬스체크
echo "🏥 헬스체크 중..."
sleep 15

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

# 9. 배포 완료 정보
echo ""
echo "🎉 Plain Flower Club 배포 완료!"
echo ""
echo "📊 서비스 정보:"
echo "   🌐 메인 사이트: https://plainflowerclub.com"
echo "   📚 API 문서: https://plainflowerclub.com/docs"
echo "   🛠️ 관리자 퍼널: https://plainflowerclub.com/admin/"
echo "   🖼️ 이미지 서버: https://plainflowerclub.com/images/"
echo ""
echo "🔧 유용한 명령어:"
echo "   📋 로그 확인: docker-compose logs -f"
echo "   🛑 서비스 중지: docker-compose down"
echo "   🔄 서비스 재시작: docker-compose restart"
echo ""
echo "📞 문제 발생 시:"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - 서비스 상태: docker-compose ps"
echo "   - 헬스체크: curl https://plainflowerclub.com/health"
echo ""

# 10. 초기 데이터 동기화 (선택사항)
read -p "초기 데이터 동기화를 실행하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 초기 데이터 동기화 시작..."
    docker-compose exec floiy-reco-api python scripts/sync_flower_database.py
    if [ -f "google_credentials.json" ]; then
        docker-compose exec floiy-reco-api python scripts/auto_sync_from_spreadsheet.py
    fi
    echo "✅ 초기 데이터 동기화 완료"
fi

echo ""
echo "🎊 Plain Flower Club가 성공적으로 배포되었습니다!"
echo "🌐 https://plainflowerclub.com 에서 확인하세요!"

