from fastapi import APIRouter
from app.api.v1.endpoints import recommend, keywords, admin, fast_context, stories

api_v1_router = APIRouter()

api_v1_router.include_router(recommend.router, tags=["recommendations"])
api_v1_router.include_router(keywords.router, tags=["keywords"])
api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_v1_router.include_router(fast_context.router, tags=["fast-context"])
api_v1_router.include_router(stories.router, prefix="/stories", tags=["stories"])
