"""
실시간 WebSocket 핸들러
스마트 키워드 추출기와 연동하여 실시간 키워드 추출 처리
"""

import asyncio
import json
import time
from typing import Set, Dict, Any
from websockets import WebSocketServerProtocol
from app.services.smart_websocket_extractor import SmartWebSocketExtractor

class RealtimeWebSocketHandler:
    """실시간 WebSocket 핸들러"""
    
    def __init__(self):
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.debounce_timers: Dict[WebSocketServerProtocol, asyncio.Task] = {}
        self.debounce_delay = 2.0  # 2초 디바운싱
        self.extractor = SmartWebSocketExtractor()
    
    async def connect(self, websocket: WebSocketServerProtocol):
        """WebSocket 연결 처리"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # 연결 확인 메시지 전송
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "WebSocket 연결됨",
            "timestamp": time.time()
        }))
        
        print(f"✅ WebSocket 연결됨: {websocket.remote_address}")
    
    def disconnect(self, websocket: WebSocketServerProtocol):
        """WebSocket 연결 해제 처리"""
        self.active_connections.discard(websocket)
        
        # 디바운스 타이머 정리
        if websocket in self.debounce_timers:
            self.debounce_timers[websocket].cancel()
            del self.debounce_timers[websocket]
        
        print(f"❌ WebSocket 연결 해제됨: {websocket.remote_address}")
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """메시지 처리"""
        try:
            data = json.loads(message)
            story = data.get("story", "").strip()
            
            # 최소 길이 체크 (10자 이상)
            if len(story) < 10:
                await websocket.send_text(json.dumps({
                    "type": "processing",
                    "message": "더 많은 내용을 입력해주세요 (최소 10자)",
                    "timestamp": time.time()
                }))
                return
            
            # 디바운싱 처리
            await self._handle_debounced_extraction(websocket, story)
            
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "잘못된 JSON 형식입니다",
                "timestamp": time.time()
            }))
        except Exception as e:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"메시지 처리 오류: {str(e)}",
                "timestamp": time.time()
            }))
    
    async def _handle_debounced_extraction(self, websocket: WebSocketServerProtocol, story: str):
        """디바운싱된 키워드 추출 처리"""
        # 기존 타이머 취소
        if websocket in self.debounce_timers:
            self.debounce_timers[websocket].cancel()
        
        # 처리 중 메시지 전송
        await websocket.send_text(json.dumps({
            "type": "processing",
            "message": "키워드 추출 중...",
            "timestamp": time.time()
        }))
        
        # 새로운 디바운스 타이머 생성
        task = asyncio.create_task(self._debounced_extraction(websocket, story))
        self.debounce_timers[websocket] = task
    
    async def _debounced_extraction(self, websocket: WebSocketServerProtocol, story: str):
        """디바운싱 후 키워드 추출 실행"""
        try:
            # 디바운스 대기
            await asyncio.sleep(self.debounce_delay)
            
            # 스마트 키워드 추출
            context = await self.extractor.extract_with_confidence(story)
            
            if context and context.is_valid():
                # 성공 응답 전송
                await websocket.send_text(json.dumps({
                    "type": "keywords",
                    "data": {
                        "emotions": {
                            "main": context.emotions[0] if context.emotions else "",
                            "alternatives": context.emotions_alternatives
                        },
                        "situations": {
                            "main": context.situations[0] if context.situations else "",
                            "alternatives": context.situations_alternatives
                        },
                        "moods": {
                            "main": context.moods[0] if context.moods else "",
                            "alternatives": context.moods_alternatives
                        },
                        "colors": {
                            "main": context.colors[0] if context.colors else "",
                            "alternatives": context.colors_alternatives
                        },
                        "confidence": context.confidence,
                        "extraction_method": context.extraction_method
                    },
                    "timestamp": time.time()
                }))
                
                print(f"✅ 키워드 추출 완료: {context.extraction_method} (신뢰도: {context.confidence})")
                
            else:
                # 추출 실패 응답
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "키워드 추출에 실패했습니다",
                    "timestamp": time.time()
                }))
        
        except asyncio.CancelledError:
            # 타이머가 취소됨 (새로운 입력이 들어옴)
            pass
        except Exception as e:
            # 오류 응답
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"키워드 추출 오류: {str(e)}",
                "timestamp": time.time()
            }))
            print(f"❌ 키워드 추출 오류: {e}")
    
    def get_connection_count(self) -> int:
        """활성 연결 수 반환"""
        return len(self.active_connections)
    
    async def cleanup(self):
        """리소스 정리"""
        # 모든 연결 해제
        for websocket in list(self.active_connections):
            await websocket.close()
        
        # 모든 타이머 취소
        for task in self.debounce_timers.values():
            task.cancel()
        
        # 추출기 정리
        self.extractor.cleanup()
        
        # 컬렉션 정리
        self.active_connections.clear()
        self.debounce_timers.clear()
        
        print("🧹 WebSocket 리소스 정리 완료")
