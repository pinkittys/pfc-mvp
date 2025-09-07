from fastapi import APIRouter
from app.api.v1.endpoints import recommend, admin, stories, unified, sample_stories, realtime_context

api_v1_router = APIRouter()

# 라우터 등록 - 핵심 API 우선
print("🔧 라우터 등록 시작...")

# 1. 핵심 API들 (먼저 등록)
try:
    api_v1_router.include_router(sample_stories.router, tags=["sample-stories"])
    print("✅ Sample Stories 라우터 등록 완료")
except Exception as e:
    print(f"❌ Sample Stories 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(unified.router, tags=["unified"])
    print("✅ Unified 라우터 등록 완료")
except Exception as e:
    print(f"❌ Unified 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(recommend.router, tags=["recommendations"])
    print("✅ Recommend 라우터 등록 완료")
except Exception as e:
    print(f"❌ Recommend 라우터 등록 실패: {e}")

# 2. 기타 API들 (필요시에만)
try:
    api_v1_router.include_router(realtime_context.router, tags=["realtime-context"])
    print("✅ Realtime Context 라우터 등록 완료")
except Exception as e:
    print(f"❌ Realtime Context 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"])
    print("✅ Stories 라우터 등록 완료")
except Exception as e:
    print(f"❌ Stories 라우터 등록 실패: {e}")

# 3. 관리자 API들 (마지막에 등록)
try:
    api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
    print("✅ Admin 라우터 등록 완료")
except Exception as e:
    print(f"❌ Admin 라우터 등록 실패: {e}")

print("🔧 라우터 등록 완료")
