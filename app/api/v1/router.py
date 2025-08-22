from fastapi import APIRouter
from app.api.v1.endpoints import recommend, keywords, admin, fast_context, stories

api_v1_router = APIRouter()

# 라우터 등록
api_v1_router.include_router(recommend.router, tags=["recommendations"])
api_v1_router.include_router(keywords.router, tags=["keywords"])
api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_v1_router.include_router(fast_context.router, tags=["fast-context"])

# Stories 라우터 등록 - 명시적으로 확인
print("🔧 Stories 라우터 등록 중...")
api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"])
print("✅ Stories 라우터 등록 완료")

# 등록된 라우터 확인
print("📋 등록된 라우터:")
for route in api_v1_router.routes:
    print(f"  - {route.path} [{', '.join(route.methods)}]")
