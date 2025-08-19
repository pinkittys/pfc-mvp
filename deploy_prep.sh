#!/bin/bash

echo "🚀 배포 전 프로젝트 정리 시작"

# 1. 아카이브 디렉토리 생성
echo "📦 아카이브 디렉토리 생성..."
mkdir -p archive/development_scripts
mkdir -p archive/test_files
mkdir -p archive/logs
mkdir -p archive/docs

# 2. 개발 스크립트 아카이빙
echo "🔧 개발 스크립트 아카이빙..."
mv scripts/ archive/development_scripts/

# 3. 테스트 파일들 아카이빙
echo "🧪 테스트 파일들 아카이빙..."
mv test_*.html archive/test_files/ 2>/dev/null || true
mv test_*.py archive/test_files/ 2>/dev/null || true
mv interactive_test.html archive/test_files/ 2>/dev/null || true
mv api_test.html archive/test_files/ 2>/dev/null || true

# 4. 로그 파일들 아카이빙
echo "📝 로그 파일들 아카이빙..."
mv logs/ archive/ 2>/dev/null || true
mv *.log archive/logs/ 2>/dev/null || true

# 5. 백업 파일들 아카이빙
echo "💾 백업 파일들 아카이빙..."
mv *.backup archive/ 2>/dev/null || true

# 6. 개발 문서들 아카이빙
echo "📚 개발 문서들 아카이빙..."
mv docs/ archive/ 2>/dev/null || true

# 7. 불필요한 파일들 정리
echo "🧹 불필요한 파일들 정리..."
rm -f .DS_Store
rm -f token.json
rm -f service-account-key.json.backup

# 8. 프로덕션용 .gitignore 업데이트
echo "🔒 .gitignore 업데이트..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp

# Archive (개발용 파일들)
archive/

# Test files
test_*.html
test_*.py

# Backup files
*.backup

# Credentials
token.json
service-account-key.json
credentials.json
EOF

echo "✅ 프로젝트 정리 완료!"
echo "📁 아카이브된 파일들:"
echo "  - archive/development_scripts/ (개발 스크립트들)"
echo "  - archive/test_files/ (테스트 파일들)"
echo "  - archive/logs/ (로그 파일들)"
echo "  - archive/docs/ (개발 문서들)"
echo ""
echo "🚀 이제 GitHub에 push할 준비가 되었습니다!"
