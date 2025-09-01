"""
실시간 WebSocket 처리를 위한 최적화된 핸들러
빠르고 안정적인 실시간 키워드 추출
"""

import asyncio
import json
import time
from typing import Dict, Set, Optional
from fastapi import WebSocket
from .realtime_context_extractor_simple import SimpleRealtimeContextExtractor, ExtractedContext

class RealtimeWebSocketHandler:
    """실시간 WebSocket 처리 핸들러"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.extractor = SimpleRealtimeContextExtractor()
        self.debounce_timers: Dict[WebSocket, asyncio.Task] = {}
        self.debounce_delay = 2.0  # 2초 디바운싱
        
    async def connect(self, websocket: WebSocket):
        """WebSocket 연결 처리"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ WebSocket 연결됨 (총 {len(self.active_connections)}개)")
        
        # 연결 메시지 전송
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "실시간 키워드 추출 연결됨",
            "timestamp": time.time()
        }))
    
    def disconnect(self, websocket: WebSocket):
        """WebSocket 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # 디바운스 타이머 정리
        if websocket in self.debounce_timers:
            self.debounce_timers[websocket].cancel()
            del self.debounce_timers[websocket]
            
        print(f"❌ WebSocket 연결 해제됨 (총 {len(self.active_connections)}개)")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """메시지 처리 (디바운싱 적용)"""
        try:
            data = json.loads(message)
            story = data.get('story', '').strip()
            
            if not story:
                return
            
            # 10글자 미만이면 처리하지 않음
            if len(story) < 10:
                await websocket.send_text(json.dumps({
                    "type": "info",
                    "message": "10글자 이상 입력해주세요",
                    "timestamp": time.time()
                }))
                return
            
            # 기존 디바운스 타이머 취소
            if websocket in self.debounce_timers:
                self.debounce_timers[websocket].cancel()
            
            # 새로운 디바운스 타이머 시작
            timer_task = asyncio.create_task(self._debounced_extraction(websocket, story))
            self.debounce_timers[websocket] = timer_task
            
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "잘못된 JSON 형식",
                "timestamp": time.time()
            }))
        except Exception as e:
            print(f"❌ 메시지 처리 오류: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"처리 오류: {str(e)}",
                "timestamp": time.time()
            }))
    
    async def _debounced_extraction(self, websocket: WebSocket, story: str):
        """디바운싱된 키워드 추출"""
        try:
            # 2초 대기
            await asyncio.sleep(self.debounce_delay)
            
            # 타이머가 여전히 유효한지 확인
            if websocket not in self.active_connections:
                return
            
            # 키워드 추출 시작
            await websocket.send_text(json.dumps({
                "type": "processing",
                "message": "키워드 추출 중...",
                "timestamp": time.time()
            }))
            
            # 비동기 키워드 추출
            context = await self.extractor.extract_context_realtime_async(story)
            
            if context and context.is_valid():
                # 성공 응답
                response = {
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
                        "confidence": context.confidence
                    },
                    "timestamp": time.time()
                }
                
                await websocket.send_text(json.dumps(response))
                
                # 성공 로그
                print(f"✅ 키워드 추출 성공: {story[:30]}...")
                
            else:
                # 실패 응답
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "키워드 추출 실패",
                    "timestamp": time.time()
                }))
                
        except asyncio.CancelledError:
            # 타이머가 취소됨 (사용자가 계속 타이핑 중)
            pass
        except Exception as e:
            print(f"❌ 키워드 추출 오류: {e}")
            if websocket in self.active_connections:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"키워드 추출 오류: {str(e)}",
                    "timestamp": time.time()
                }))
    
    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"❌ 브로드캐스트 실패: {e}")
                disconnected.add(connection)
        
        # 연결이 끊어진 클라이언트 정리
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """활성 연결 수 반환"""
        return len(self.active_connections)
    
    async def cleanup(self):
        """리소스 정리"""
        # 모든 연결 해제
        for connection in list(self.active_connections):
            self.disconnect(connection)
        
        # 추출기 정리
        self.extractor.cleanup()
        
        print("🧹 WebSocket 핸들러 정리 완료")
