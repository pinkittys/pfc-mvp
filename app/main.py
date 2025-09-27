from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import WebSocket
import os
from datetime import datetime

from app.api.v1.router import api_v1_router

app = FastAPI(
    title="Floiy-Reco API",
    description="꽃 추천 시스템 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
app.mount("/images", StaticFiles(directory="data/images_webp"), name="images")
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/static", StaticFiles(directory="."), name="static")

# API 라우터 등록
app.include_router(api_v1_router, prefix="/api/v1")

# WebSocket 테스트 엔드포인트 (직접 추가)
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket 연결 테스트 성공!")

@app.get("/")
async def root():
    return {"message": "Floiy-Reco API is running!"}

@app.get("/ping")
async def ping():
    """간단한 헬스체크 엔드포인트 (빠른 응답)"""
    try:
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Ping endpoint error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """빠른 헬스체크 엔드포인트 (Pod 시작용)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ready")
async def ready_check():
    """Pod readiness probe용 간단한 엔드포인트"""
    return {"ready": True}

@app.get("/health/detailed")
async def detailed_health_check():
    """상세 헬스체크 엔드포인트 (모니터링용)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "openai": "available"
        }
    }

@app.get("/admin", include_in_schema=False)
async def admin_panel():
    return FileResponse("admin_panel.html")

@app.get("/admin_panel.html", include_in_schema=False)
async def admin_panel_html():
    return FileResponse("admin_panel.html")

@app.get("/simple_test.html", include_in_schema=False)
async def simple_test():
    return FileResponse("simple_api_test.html")

@app.get("/sample_stories_demo.html", include_in_schema=False)
async def sample_stories_demo():
    """사연 샘플 데모 페이지"""
    return FileResponse("sample_stories_demo.html")

@app.get("/demo", include_in_schema=False)
async def demo():
    """사연 샘플 데모 페이지 (단축 URL)"""
    return FileResponse("sample_stories_demo.html")

@app.get("/realtime_keyword_test.html", include_in_schema=False)
async def realtime_keyword_test():
    """실시간 키워드 추출 테스트 페이지"""
    return FileResponse("frontend/pages/realtime_keyword_test.html")

@app.get("/keyword_test", include_in_schema=False)
async def keyword_test():
    """실시간 키워드 추출 테스트 페이지 (단축 URL)"""
    return FileResponse("frontend/pages/realtime_keyword_test.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
