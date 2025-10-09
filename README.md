# 🌸 Floiy 이미지 생성 실험

Gemini + NanoBana API를 이용한 꽃 이미지 생성 실험 프로젝트

## 🎯 실험 목표

- **Gemini API**: 꽃 이미지 생성 프롬프트 최적화
- **NanoBana API**: 실제 이미지 생성 및 품질 테스트
- **파이프라인**: 자동화된 이미지 생성 워크플로우 구축

## 🚀 시작하기

### 1. 환경 설정
```bash
# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp config/env_example.txt .env
# .env 파일에 API 키 입력
```

### 2. API 키 설정
```bash
# .env 파일에 추가
GEMINI_API_KEY=your_gemini_api_key_here
NANOBANA_API_KEY=your_nanobana_api_key_here
```

### 3. 실험 실행
```bash
python pipeline_test.py
```

## 📁 프로젝트 구조

```
floiy-image-experiment/
├── config/
│   ├── settings.py          # 설정 파일
│   └── env_example.txt      # 환경 변수 예시
├── gemini_prompts/          # Gemini 생성 프롬프트들
├── nanobana_generation/     # NanoBana 생성 이미지들
├── test_results/            # 실험 결과 JSON
├── logs/                    # 실험 로그
├── pipeline_test.py         # 메인 실험 파이프라인
└── requirements.txt         # 패키지 목록
```

## 🧪 실험 시나리오

### 테스트 케이스
1. **장미** (사랑, 핑크) - 로맨틱한 상황
2. **해바라기** (기쁨, 옐로우) - 축하 상황  
3. **라벤더** (평온, 퍼플) - 위로 상황

### 이미지 스타일
- `photorealistic`: 사진처럼 사실적
- `artistic`: 예술적 스타일
- `minimalist`: 미니멀 스타일
- `vintage`: 빈티지 스타일

## 📊 결과 분석

실험 결과는 다음 위치에 저장됩니다:
- `test_results/`: JSON 형태의 상세 결과
- `logs/`: 실험 과정 로그
- `nanobana_generation/`: 생성된 이미지 파일들

## 🔧 커스터마이징

`config/settings.py`에서 실험 설정을 수정할 수 있습니다:
- 테스트할 꽃 종류
- 이미지 스타일
- API 설정

## ⚠️ 주의사항

- 이 프로젝트는 **실험용**입니다
- 프로덕션 환경과 완전히 분리되어 있습니다
- API 사용량에 주의하세요