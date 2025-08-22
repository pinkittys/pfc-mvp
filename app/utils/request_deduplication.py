import time
import hashlib
from typing import Dict, Optional
from threading import Lock

class RequestDeduplicator:
    """요청 중복 방지 및 디바운싱 유틸리티"""
    
    def __init__(self, debounce_time: float = 0.5):
        self.debounce_time = debounce_time
        self.pending_requests: Dict[str, float] = {}
        self.completed_requests: Dict[str, Dict] = {}
        self.lock = Lock()
    
    def generate_request_id(self, story: str, preferred_colors: list, excluded_flowers: list) -> str:
        """요청 내용을 기반으로 고유 ID 생성"""
        content = f"{story}:{','.join(preferred_colors)}:{','.join(excluded_flowers)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def should_process_request(self, request_id: str) -> bool:
        """요청을 처리해야 하는지 확인 (디바운싱 + 중복 방지)"""
        current_time = time.time()
        
        with self.lock:
            # 이미 완료된 동일한 요청이 있는지 확인
            if request_id in self.completed_requests:
                completed_time = self.completed_requests[request_id].get('timestamp', 0)
                if current_time - completed_time < self.debounce_time:
                    print(f"🔄 중복 요청 감지 및 스킵: {request_id}")
                    return False
            
            # 진행 중인 요청이 있는지 확인
            if request_id in self.pending_requests:
                pending_time = self.pending_requests[request_id]
                if current_time - pending_time < self.debounce_time:
                    print(f"⏳ 디바운싱: 진행 중인 요청 대기 중 - {request_id}")
                    return False
            
            # 새로운 요청 등록
            self.pending_requests[request_id] = current_time
            print(f"✅ 새로운 요청 등록: {request_id}")
            return True
    
    def mark_request_completed(self, request_id: str, result: Dict):
        """요청 완료 표시"""
        current_time = time.time()
        
        with self.lock:
            # 진행 중인 요청에서 제거
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
            
            # 완료된 요청으로 등록
            self.completed_requests[request_id] = {
                'timestamp': current_time,
                'result': result
            }
            
            # 오래된 완료 요청 정리 (메모리 누수 방지)
            self._cleanup_old_requests(current_time)
            
            print(f"✅ 요청 완료 등록: {request_id}")
    
    def get_cached_result(self, request_id: str) -> Optional[Dict]:
        """캐시된 결과 반환"""
        current_time = time.time()
        
        with self.lock:
            if request_id in self.completed_requests:
                completed_data = self.completed_requests[request_id]
                completed_time = completed_data['timestamp']
                
                # 캐시 유효 시간 내라면 결과 반환
                if current_time - completed_time < self.debounce_time:
                    print(f"📋 캐시된 결과 반환: {request_id}")
                    return completed_data['result']
        
        return None
    
    def _cleanup_old_requests(self, current_time: float):
        """오래된 완료 요청 정리"""
        cleanup_threshold = current_time - (self.debounce_time * 10)  # 10배 더 오래 보관
        
        keys_to_remove = [
            req_id for req_id, data in self.completed_requests.items()
            if data['timestamp'] < cleanup_threshold
        ]
        
        for req_id in keys_to_remove:
            del self.completed_requests[req_id]
        
        if keys_to_remove:
            print(f"🧹 오래된 요청 정리: {len(keys_to_remove)}개")

# 전역 인스턴스
request_deduplicator = RequestDeduplicator(debounce_time=0.5)
