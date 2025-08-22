from fastapi import APIRouter
from app.api.v1.endpoints import recommend, keywords, admin, fast_context, stories

api_v1_router = APIRouter()

# 라우터 등록 - 명시적으로 확인
try:
    print("🔧 Recommend 라우터 등록 중...")
    print(f"Recommend router: {recommend.router}")
    print(f"Recommend router routes: {recommend.router.routes}")
    
    api_v1_router.include_router(recommend.router, tags=["recommendations"])
    print("✅ Recommend 라우터 등록 완료")
    
except Exception as e:
    print(f"❌ Recommend 라우터 등록 실패: {e}")
    raise e

try:
    print("🔧 Keywords 라우터 등록 중...")
    api_v1_router.include_router(keywords.router, tags=["keywords"])
    print("✅ Keywords 라우터 등록 완료")
except Exception as e:
    print(f"❌ Keywords 라우터 등록 실패: {e}")
    raise e

try:
    print("🔧 Admin 라우터 등록 중...")
    api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
    print("✅ Admin 라우터 등록 완료")
except Exception as e:
    print(f"❌ Admin 라우터 등록 실패: {e}")
    raise e

try:
    print("🔧 Fast Context 라우터 등록 중...")
    api_v1_router.include_router(fast_context.router, tags=["fast-context"])
    print("✅ Fast Context 라우터 등록 완료")
except Exception as e:
    print(f"❌ Fast Context 라우터 등록 실패: {e}")
    raise e

# Stories 라우터 등록 - 명시적으로 확인
try:
    print("🔧 Stories 라우터 등록 중...")
    print(f"Stories router: {stories.router}")
    print(f"Stories router routes: {stories.router.routes}")
    
    api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"])
    print("✅ Stories 라우터 등록 완료")
    
    # 등록된 라우터 확인
    print("📋 등록된 라우터:")
    for route in api_v1_router.routes:
        print(f"  - {route.path} [{', '.join(route.methods)}]")
        
except Exception as e:
    print(f"❌ Stories 라우터 등록 실패: {e}")
    raise e
