from fastapi import APIRouter
from app.api.v1.endpoints import recommend, keywords, admin, fast_context, stories, unified, sample_stories

api_v1_router = APIRouter()

# 라우터 등록 - 단순화
print("🔧 라우터 등록 시작...")

try:
    api_v1_router.include_router(recommend.router, tags=["recommendations"])
    print("✅ Recommend 라우터 등록 완료")
except Exception as e:
    print(f"❌ Recommend 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(keywords.router, tags=["keywords"])
    print("✅ Keywords 라우터 등록 완료")
except Exception as e:
    print(f"❌ Keywords 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
    print("✅ Admin 라우터 등록 완료")
except Exception as e:
    print(f"❌ Admin 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(fast_context.router, tags=["fast-context"])
    print("✅ Fast Context 라우터 등록 완료")
except Exception as e:
    print(f"❌ Fast Context 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"])
    print("✅ Stories 라우터 등록 완료")
except Exception as e:
    print(f"❌ Stories 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(unified.router, tags=["unified"])
    print("✅ Unified 라우터 등록 완료")
except Exception as e:
    print(f"❌ Unified 라우터 등록 실패: {e}")

try:
    api_v1_router.include_router(sample_stories.router, tags=["sample-stories"])
    print("✅ Sample Stories 라우터 등록 완료")
except Exception as e:
    print(f"❌ Sample Stories 라우터 등록 실패: {e}")

print("🔧 라우터 등록 완료")
