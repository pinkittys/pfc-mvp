"""
실시간 맥락 추출 API 엔드포인트
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from app.services.realtime_context_extractor import RealtimeContextExtractor

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()
context_extractor = RealtimeContextExtractor()

@router.websocket("/ws/context-extraction")
async def websocket_context_extraction(websocket: WebSocket):
    """
    실시간 맥락 추출을 위한 WebSocket 엔드포인트
    
    클라이언트에서 텍스트를 입력할 때마다 실시간으로 맥락을 추출하여 반환합니다.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 클라이언트로부터 텍스트 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "text_input":
                text = message.get("text", "")
                
                # 빈 텍스트인 경우 기본 응답
                if not text.strip():
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "context_update",
                            "context": {
                                "emotions": [],
                                "situations": [],
                                "moods": [],
                                "colors": []
                            },
                            "keywords": []
                        }),
                        websocket
                    )
                    continue
                
                try:
                    # 맥락 추출
                    extracted_context = context_extractor.extract_context_from_story(text)
                    
                    # 키워드 생성 (감정 + 상황 + 무드 + 색상)
                    keywords = []
                    keywords.extend(extracted_context.emotions)
                    keywords.extend(extracted_context.situations)
                    keywords.extend(extracted_context.moods)
                    keywords.extend(extracted_context.colors)
                    
                    # 중복 제거
                    keywords = list(set(keywords))
                    
                    # 응답 전송
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "context_update",
                            "context": {
                                "emotions": extracted_context.emotions,
                                "situations": extracted_context.situations,
                                "moods": extracted_context.moods,
                                "colors": extracted_context.colors,
                                "confidence": extracted_context.confidence
                            },
                            "keywords": keywords
                        }),
                        websocket
                    )
                    
                except Exception as e:
                    # 에러 발생 시 기본 응답
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "message": "맥락 추출 중 오류가 발생했습니다."
                        }),
                        websocket
                    )
            
            elif message.get("type") == "ping":
                # 연결 상태 확인
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.post("/context-extraction/stream")
async def stream_context_extraction(text: str):
    """
    실시간 맥락 추출 (HTTP 스트리밍)
    
    텍스트를 받아서 맥락을 추출하고 키워드를 반환합니다.
    """
    try:
        # 맥락 추출
        extracted_context = context_extractor.extract_context_from_story(text)
        
        # 키워드 생성
        keywords = []
        keywords.extend(extracted_context.emotions)
        keywords.extend(extracted_context.situations)
        keywords.extend(extracted_context.moods)
        keywords.extend(extracted_context.colors)
        
        # 중복 제거
        keywords = list(set(keywords))
        
        return {
            "success": True,
            "context": {
                "emotions": extracted_context.emotions,
                "situations": extracted_context.situations,
                "moods": extracted_context.moods,
                "colors": extracted_context.colors,
                "confidence": extracted_context.confidence
            },
            "keywords": keywords
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "context": {
                "emotions": [],
                "situations": [],
                "moods": [],
                "colors": [],
                "confidence": 0.0
            },
            "keywords": []
        }
