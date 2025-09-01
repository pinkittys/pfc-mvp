from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# API 라우터 등록
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Floiy-Reco API is running!"}

@app.get("/ping")
async def ping():
    """간단한 헬스체크 엔드포인트 (빠른 응답)"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    """빠른 헬스체크 엔드포인트 (Pod 시작용)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

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

@app.get("/admin")
async def admin_panel():
    return FileResponse("admin_panel.html")

@app.get("/admin_panel.html")
async def admin_panel_html():
    return FileResponse("admin_panel.html")

@app.get("/simple_test.html")
async def simple_test():
    return FileResponse("simple_test.html")

@app.get("/sample_stories_demo.html")
async def sample_stories_demo():
    """사연 샘플 데모 페이지"""
    return FileResponse("sample_stories_demo.html")

@app.get("/demo")
async def demo():
    """사연 샘플 데모 페이지 (단축 URL)"""
    return FileResponse("sample_stories_demo.html")
