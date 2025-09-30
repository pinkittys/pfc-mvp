from fastapi import APIRouter
from app.api.v1.endpoints import recommend, admin, stories, unified, sample_stories, realtime_context, advanced
import os

api_v1_router = APIRouter()

# 라우터 등록 - 핵심 API 우선
print("🔧 라우터 등록 시작...")

# 1. 핵심 API들 (항상 문서에 표시)
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

# 고급 옵션 API들 (문서에 표시)
try:
    api_v1_router.include_router(advanced.router, prefix="/advanced", tags=["advanced"])
    print("✅ Advanced 라우터 등록 완료")
except Exception as e:
    print(f"❌ Advanced 라우터 등록 실패: {e}")

# 2. 기타 API들 (문서에서 숨김 - 코드는 유지)
try:
    api_v1_router.include_router(recommend.router, tags=["recommendations"], include_in_schema=False)
    print("✅ Recommend 라우터 등록 완료 (문서에서 숨김)")
except Exception as e:
    print(f"❌ Recommend 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(realtime_context.router, tags=["realtime-context"], include_in_schema=False)
    print("✅ Realtime Context 라우터 등록 완료 (문서에서 숨김)")
except Exception as e:
    print(f"❌ Realtime Context 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"], include_in_schema=False)
    print("✅ Stories 라우터 등록 완료 (문서에서 숨김)")
except Exception as e:
    print(f"❌ Stories 라우터 등록 실패: {e}")

# 3. 관리자 API들 (문서에서 숨김 - 코드는 유지)
try:
    api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"], include_in_schema=False)
    print("✅ Admin 라우터 등록 완료 (문서에서 숨김)")
except Exception as e:
    print(f"❌ Admin 라우터 등록 실패: {e}")

print("🔧 라우터 등록 완료")
