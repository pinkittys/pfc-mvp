"""
실시간 컨텍스트 추출을 위한 WebSocket 엔드포인트
최적화된 실시간 키워드 추출
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.services.realtime_websocket_handler import RealtimeWebSocketHandler
import json
import logging
import time

router = APIRouter()
handler = RealtimeWebSocketHandler()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.websocket("/ws/context-extraction")
async def websocket_context_extraction(websocket: WebSocket):
    """
    실시간 맥락 추출을 위한 WebSocket 엔드포인트
    
    클라이언트는 다음과 같은 형식으로 메시지를 보내야 합니다:
    {
        "story": "사용자의 이야기 내용"
    }
    
    서버는 다음과 같은 형식으로 응답합니다:
    {
        "type": "keywords",
        "data": {
            "emotions": {"main": "감정", "alternatives": ["대안1", "대안2", "대안3"]},
            "situations": {"main": "상황", "alternatives": ["대안1", "대안2", "대안3"]},
            "moods": {"main": "무드", "alternatives": ["대안1", "대안2", "대안3"]},
            "colors": {"main": "색상", "alternatives": ["대안1", "대안2", "대안3"]},
            "confidence": 0.9
        },
        "timestamp": 1234567890.123
    }
    """
    try:
        # WebSocket 연결
        await handler.connect(websocket)
        logger.info(f"WebSocket 연결됨: {websocket.client}")
        
        # 메시지 수신 루프
        while True:
            try:
                # 메시지 수신
                message = await websocket.receive_text()
                logger.debug(f"메시지 수신: {message[:100]}...")
                
                # 메시지 처리
                await handler.handle_message(websocket, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket 연결 해제됨: {websocket.client}")
                break
            except Exception as e:
                logger.error(f"메시지 처리 오류: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"메시지 처리 오류: {str(e)}",
                    "timestamp": time.time()
                }))
                
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
    finally:
        # 연결 해제 처리
        handler.disconnect(websocket)

@router.get("/status")
async def get_websocket_status():
    """WebSocket 연결 상태 확인"""
    return {
        "active_connections": handler.get_connection_count(),
        "status": "running"
    }

@router.post("/cleanup")
async def cleanup_websocket():
    """WebSocket 리소스 정리 (관리자용)"""
    await handler.cleanup()
    return {"message": "WebSocket 리소스 정리 완료"}
