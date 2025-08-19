"""
추천 과정 로깅 서비스
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from .realtime_context_extractor import ExtractedContext
from app.models.schemas import EmotionAnalysis, FlowerMatch
from .flower_blend_recommender import FlowerBlend, BlendRecommendation
from .image_matcher import ImageMatchResult

@dataclass
class RecommendationLog:
    """추천 로그 데이터"""
    timestamp: str
    customer_story: str
    budget: int
    
    # 1단계: 맥락 추출
    extracted_context: Dict[str, Any]
    
    # 2단계: 감정 분석
    emotion_analysis: Dict[str, Any]
    
    # 3단계: 꽃 매칭
    flower_matches: List[Dict[str, Any]]
    
    # 4단계: 꽃 구성
    blend_recommendations: List[Dict[str, Any]]
    
    # 5단계: 최종 추천
    final_recommendation: Dict[str, Any]
    
    # 메타데이터
    processing_time_ms: int
    confidence_score: float
    tags: List[str]

class RecommendationLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 로그 파일 설정
        self.setup_logging()
        
        # 로그 데이터 저장소
        self.logs: List[RecommendationLog] = []
    
    def setup_logging(self):
        """로깅 설정"""
        # 파일 핸들러
        log_file = self.log_dir / f"recommendation_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # 로거 설정
        self.logger = logging.getLogger('recommendation')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
    
    def log_recommendation_process(self, customer_story: str, budget: int, 
                                 extracted_context, emotion_analysis, 
                                 flower_matches, blend_recommendations, 
                                 final_recommendation, processing_time_ms: int, 
                                 tags: List[str]):
        """추천 프로세스 전체를 로깅"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "customer_story": customer_story,
            "budget": budget,  # MVP에서는 None
            "extracted_context": self._context_to_dict(extracted_context),
            "emotion_analysis": self._emotion_analysis_to_dict(emotion_analysis),
            "flower_matches": [self._flower_match_to_dict(match) for match in flower_matches],
            "blend_recommendations": [self._blend_recommendation_to_dict(rec) for rec in blend_recommendations],
            "final_recommendation": final_recommendation,
            "tags": tags
        }
    
    def _context_to_dict(self, context: ExtractedContext) -> Dict[str, Any]:
        """맥락 추출 결과를 딕셔너리로 변환"""
        return {
            "emotions": context.emotions,
            "situations": context.situations,
            "moods": context.moods,
            "colors": context.colors,
            "confidence": context.confidence
        }
    
    def _emotion_analysis_to_dict(self, emotion_analysis) -> Dict[str, Any]:
        """감정 분석을 딕셔너리로 변환"""
        return {
            "primary_emotion": emotion_analysis.primary_emotion,
            "secondary_emotion": emotion_analysis.secondary_emotion,
            "tertiary_emotion": emotion_analysis.tertiary_emotion,
            "emotion_scores": emotion_analysis.emotion_scores,
            "total_emotions": emotion_analysis.total_emotions
        }
    
    def _flower_match_to_dict(self, match: FlowerMatch) -> Dict[str, Any]:
        """꽃 매칭 결과를 딕셔너리로 변환"""
        return {
            "flower_name": match.flower_name,
            "match_score": match.match_score,
            "emotion_fit": match.emotion_fit,
            "situation_fit": match.situation_fit,
            "reason": match.reason
        }
    
    def _blend_recommendation_to_dict(self, blend_rec) -> Dict[str, Any]:
        """꽃 구성 추천을 딕셔너리로 변환"""
        return {
            "main_flowers": blend_rec.blend.main_flowers,
            "sub_flowers": blend_rec.blend.sub_flowers,
            "filler_flowers": blend_rec.blend.filler_flowers,
            "line_flowers": blend_rec.blend.line_flowers,
            "foliage": blend_rec.blend.foliage,
            "total_flowers": blend_rec.blend.total_flowers,
            "color_harmony": blend_rec.blend.color_harmony,
            "style_description": blend_rec.blend.style_description,
            "color_theme": blend_rec.blend.color_theme,
            "emotion_fit": blend_rec.emotion_fit,
            "color_fit": blend_rec.color_fit,
            "total_score": blend_rec.total_score,
            "reasoning": blend_rec.reasoning
        }
    
    def _save_log(self, log_data: RecommendationLog):
        """로그 데이터 저장"""
        # JSON 파일로 저장
        json_file = self.log_dir / f"recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(log_data), f, ensure_ascii=False, indent=2)
        
        # 로그 목록에 추가
        self.logs.append(log_data)
        
        # 일별 통합 로그 파일
        daily_file = self.log_dir / f"daily_recommendations_{datetime.now().strftime('%Y%m%d')}.json"
        self._append_to_daily_log(log_data, daily_file)
    
    def _append_to_daily_log(self, log_data: RecommendationLog, daily_file: Path):
        """일별 통합 로그에 추가"""
        try:
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_logs = json.load(f)
            else:
                daily_logs = []
            
            daily_logs.append(asdict(log_data))
            
            with open(daily_file, 'w', encoding='utf-8') as f:
                json.dump(daily_logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"일별 로그 저장 실패: {e}")
    
    def _log_to_console(self, log_data: RecommendationLog):
        """콘솔에 로그 출력"""
        self.logger.info(f"=== 추천 로그 ===")
        self.logger.info(f"고객 이야기: {log_data.customer_story[:100]}...")
        self.logger.info(f"예산: {log_data.budget:,}원")
        self.logger.info(f"처리 시간: {log_data.processing_time_ms}ms")
        self.logger.info(f"신뢰도: {log_data.confidence_score:.2f}")
        
        # 맥락 추출 결과
        context = log_data.extracted_context
        self.logger.info(f"추출된 맥락:")
        self.logger.info(f"  감정: {context['emotions']}")
        self.logger.info(f"  상황: {context['situations']}")
        self.logger.info(f"  무드: {context['moods']}")
        self.logger.info(f"  컬러: {context['colors']}")
        
        # 감정 분석 결과
        emotion = log_data.emotion_analysis
        self.logger.info(f"감정 분석:")
        self.logger.info(f"  주요 감정: {emotion['primary_emotion']}")
        self.logger.info(f"  감정 점수: {emotion['emotion_scores']}")
        
        # 꽃 매칭 결과
        self.logger.info(f"꽃 매칭 ({len(log_data.flower_matches)}개):")
        for i, match in enumerate(log_data.flower_matches[:3], 1):
            self.logger.info(f"  {i}. {match['flower_name']} (점수: {match['match_score']:.2f})")
        
        # 최종 추천
        final = log_data.final_recommendation
        self.logger.info(f"최종 추천:")
        self.logger.info(f"  메인 꽃: {final.get('main_flower', 'N/A')}")
        self.logger.info(f"  이미지: {final.get('image_url', 'N/A')}")
        self.logger.info(f"  추천 이유: {final.get('reason', 'N/A')[:100]}...")
        
        self.logger.info(f"태그: {log_data.tags}")
        self.logger.info(f"================\n")
    
    def get_recommendation_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """추천 통계 조회"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        daily_file = self.log_dir / f"daily_recommendations_{date}.json"
        
        if not daily_file.exists():
            return {"error": "해당 날짜의 로그가 없습니다."}
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 통계 계산
        total_recommendations = len(logs)
        avg_confidence = sum(log['confidence_score'] for log in logs) / total_recommendations
        avg_processing_time = sum(log['processing_time_ms'] for log in logs) / total_recommendations
        
        # 주요 감정 분석
        primary_emotions = {}
        for log in logs:
            emotion = log['emotion_analysis']['primary_emotion']
            primary_emotions[emotion] = primary_emotions.get(emotion, 0) + 1
        
        # 주요 꽃 분석
        main_flowers = {}
        for log in logs:
            flower = log['final_recommendation'].get('main_flower', 'Unknown')
            main_flowers[flower] = main_flowers.get(flower, 0) + 1
        
        return {
            "date": date,
            "total_recommendations": total_recommendations,
            "avg_confidence": round(avg_confidence, 2),
            "avg_processing_time_ms": round(avg_processing_time, 0),
            "primary_emotions": primary_emotions,
            "main_flowers": main_flowers
        }
    
    def search_recommendations(
        self, 
        keyword: str = None, 
        emotion: str = None, 
        flower: str = None,
        date: str = None
    ) -> List[RecommendationLog]:
        """추천 로그 검색"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        daily_file = self.log_dir / f"daily_recommendations_{date}.json"
        
        if not daily_file.exists():
            return []
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        filtered_logs = []
        
        for log in logs:
            # 키워드 검색
            if keyword and keyword.lower() not in log['customer_story'].lower():
                continue
            
            # 감정 검색
            if emotion and emotion not in log['emotion_analysis']['primary_emotion']:
                continue
            
            # 꽃 검색
            if flower and flower not in log['final_recommendation'].get('main_flower', ''):
                continue
            
            filtered_logs.append(log)
        
        return filtered_logs
