"""
꽃 매칭 서비스
"""
import os
import json
import random
from typing import List, Dict, Optional
from app.models.schemas import EmotionAnalysis, FlowerMatch
from app.services.realtime_context_extractor import RealtimeContextExtractor
from app.services.comfort_flower_matcher import ComfortFlowerMatcher

class FlowerMatcher:
    def __init__(self):
        """꽃 매칭 서비스 초기화"""
        # 실시간 맥락 추출기
        self.context_extractor = RealtimeContextExtractor()
        
        # 위로/슬픔 상황 특화 매칭기
        self.comfort_matcher = ComfortFlowerMatcher()
        
        # LLM 클라이언트 초기화
        try:
            from openai import OpenAI
            self.llm_client = OpenAI()
        except ImportError:
            print("⚠️ OpenAI 클라이언트 초기화 실패")
            self.llm_client = None
        
        # Base64 이미지 데이터 로드 (35개 꽃 이미지)
        self.base64_images = self._load_base64_images()
        
        # 꽃 데이터베이스 로드 (flower_dictionary.json에서)
        self.flower_database = self._load_flower_database()
        
        print(f"🌸 꽃 매칭 시스템 초기화 완료")
        print(f"📚 꽃 데이터베이스: {len(self.flower_database)}개 꽃")
        print(f"🖼️ Base64 이미지: {len(self.base64_images)}개 폴더")
    
    def _load_flower_database(self) -> Dict[str, Dict]:
        """꽃 데이터베이스 로드 (flower_dictionary.json에서)"""
        try:
            with open("data/flower_dictionary.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                # flowers 키가 있는 경우 해당 데이터 사용
                if "flowers" in data:
                    return data["flowers"]
                # 직접 꽃 데이터인 경우
                return data
        except Exception as e:
            print(f"❌ 꽃 데이터베이스 로드 실패: {e}")
            # 폴백: 하드코딩된 데이터 사용
            return self._create_flower_database_fallback()
    
    def _create_flower_database_fallback(self) -> Dict[str, Dict]:
        """하드코딩된 꽃 데이터베이스 (폴백용)"""
        return {
            "Rosa-레드": {
                "id": "Rosa-레드",
                "korean_name": "장미",
                "scientific_name": "Rosa",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["사랑", "열정"],
                    "secondary": ["아름다움", "존경"],
                    "other": ["용기", "명예"]
                },
                "moods": {
                    "primary": ["로맨틱한", "강렬한"],
                    "secondary": ["우아한", "격식있는"],
                    "other": ["열정적인", "매혹적인"]
                },
                "relationship_suitability": {
                    "romantic": ["연인", "고백", "사랑"],
                    "respect": ["부모님", "선생님", "존경"]
                },
                "usage_contexts": ["고백", "기념일", "로맨틱"],
                "seasonal_events": ["발렌타인데이", "결혼기념일"]
            },
            "Gerbera jamesonii-옐로우": {
                "id": "Gerbera jamesonii-옐로우",
                "korean_name": "거베라",
                "scientific_name": "Gerbera jamesonii",
                "color": "옐로우",
                "flower_meanings": {
                    "primary": ["기쁨", "희망"],
                    "secondary": ["활기", "긍정"],
                    "other": ["행복", "웃음"]
                },
                "moods": {
                    "primary": ["밝은", "활기찬"],
                    "secondary": ["경쾌한", "긍정적인"],
                    "other": ["즐거운", "행복한"]
                },
                "relationship_suitability": {
                    "celebration": ["생일", "축하", "합격"],
                    "encouragement": ["응원", "격려", "힘내"]
                },
                "usage_contexts": ["생일", "축하", "응원"],
                "seasonal_events": ["생일", "졸업", "합격"]
            },
            "Tulipa-화이트": {
                "id": "Tulipa-화이트",
                "korean_name": "튤립",
                "scientific_name": "Tulipa",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순수", "신뢰"],
                    "secondary": ["희망", "새로운 시작"],
                    "other": ["완벽한 사랑", "고백"]
                },
                "moods": {
                    "primary": ["순수한", "깨끗한"],
                    "secondary": ["희망적인", "신뢰할 수 있는"],
                    "other": ["완벽한", "이상적인"]
                },
                "relationship_suitability": {
                    "pure_love": ["첫사랑", "고백", "순수한 사랑"],
                    "trust": ["신뢰", "믿음", "우정"]
                },
                "usage_contexts": ["고백", "첫사랑", "신뢰"],
                "seasonal_events": ["봄", "새로운 시작"]
            },
            "Alstroemeria Spp-화이트": {
                "id": "Alstroemeria Spp-화이트",
                "korean_name": "알스트로메리아",
                "scientific_name": "Alstroemeria Spp",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["우정", "지지"],
                    "secondary": ["감사", "존경"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["따뜻한", "우정적인"],
                    "secondary": ["감사한", "존경하는"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "friendship": ["친구", "우정", "지지"],
                    "gratitude": ["감사", "존경", "은인"]
                },
                "usage_contexts": ["우정", "감사", "지지"],
                "seasonal_events": ["우정의 날", "감사의 날"]
            },
            "Lisianthus-화이트": {
                "id": "Lisianthus-화이트",
                "korean_name": "리시안서스",
                "scientific_name": "Lisianthus",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["우아함", "세련됨"],
                    "secondary": ["수줍은 사랑", "고귀함"],
                    "other": ["완벽한 아름다움", "순결"]
                },
                "moods": {
                    "primary": ["우아한", "세련된"],
                    "secondary": ["수줍은", "고귀한"],
                    "other": ["완벽한", "순결한"]
                },
                "relationship_suitability": {
                    "elegant": ["우아한", "세련된", "고급스러운"],
                    "pure_love": ["수줍은 사랑", "순결한 마음"]
                },
                "usage_contexts": ["우아한", "세련된", "고급스러운"],
                "seasonal_events": ["웨딩", "특별한 날"]
            },
            "Lathyrus Odoratus-핑크": {
                "id": "Lathyrus Odoratus-핑크",
                "korean_name": "스위트피",
                "scientific_name": "Lathyrus Odoratus",
                "color": "핑크",
                "flower_meanings": {
                    "primary": ["아름다움", "자연스러움"],
                    "secondary": ["사랑", "기쁨"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["아름다운", "자연스러운"],
                    "secondary": ["사랑스러운", "기쁜"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "natural": ["자연스러운", "아름다운", "순수한"],
                    "romantic": ["사랑", "기쁨", "희망"]
                },
                "usage_contexts": ["자연스러운", "아름다운", "사랑"],
                "seasonal_events": ["봄", "자연"]
            },
            "Gladiolus-레드": {
                "id": "Gladiolus-레드",
                "korean_name": "글라디올러스",
                "scientific_name": "Gladiolus",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["용기", "성공"],
                    "secondary": ["희망", "기억"],
                    "other": ["정직", "성실"]
                },
                "moods": {
                    "primary": ["용기있는", "성공적인"],
                    "secondary": ["희망적인", "기억하는"],
                    "other": ["정직한", "성실한"]
                },
                "relationship_suitability": {
                    "courage": ["용기", "성공", "희망"],
                    "memory": ["기억", "추억", "정직"]
                },
                "usage_contexts": ["용기", "성공", "기억"],
                "seasonal_events": ["졸업", "성공", "기념"]
            },
            "Ranunculus Asiaticus-오렌지": {
                "id": "Ranunculus Asiaticus-오렌지",
                "korean_name": "라넌큘러스",
                "scientific_name": "Ranunculus Asiaticus",
                "color": "오렌지",
                "flower_meanings": {
                    "primary": ["매력", "아름다움"],
                    "secondary": ["사랑", "기쁨"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["매력적인", "아름다운"],
                    "secondary": ["사랑스러운", "기쁜"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "attraction": ["매력", "아름다움", "사랑"],
                    "joy": ["기쁨", "희망", "행복"]
                },
                "usage_contexts": ["매력", "아름다움", "기쁨"],
                "seasonal_events": ["봄", "사랑"]
            },
            "Zinnia Elegans-레드": {
                "id": "Zinnia Elegans-레드",
                "korean_name": "백일홍",
                "scientific_name": "Zinnia Elegans",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["인연", "행복"],
                    "secondary": ["떠나간 사랑을 그리워하다", "추억"],
                    "other": ["희망", "사랑"]
                },
                "moods": {
                    "primary": ["인연스러운", "행복한"],
                    "secondary": ["그리워하는", "추억하는"],
                    "other": ["희망적인", "사랑스러운"]
                },
                "relationship_suitability": {
                    "fate": ["인연", "행복", "사랑"],
                    "memory": ["떠나간 사랑", "추억", "그리움"]
                },
                "usage_contexts": ["인연", "행복", "추억"],
                "seasonal_events": ["인연", "추억"]
            },
            "Marguerite Daisy-화이트": {
                "id": "Marguerite Daisy-화이트",
                "korean_name": "마거리트 데이지",
                "scientific_name": "Marguerite Daisy",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순수", "희망"],
                    "secondary": ["사랑", "기쁨"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["순수한", "희망적인"],
                    "secondary": ["사랑스러운", "기쁜"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "purity": ["순수", "희망", "사랑"],
                    "joy": ["기쁨", "행복", "평화"]
                },
                "usage_contexts": ["순수", "희망", "기쁨"],
                "seasonal_events": ["봄", "희망"]
            },
            "Dianthus Caryophyllus-레드": {
                "id": "Dianthus Caryophyllus-레드",
                "korean_name": "카네이션",
                "scientific_name": "Dianthus Caryophyllus",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["사랑", "감사"],
                    "secondary": ["존경", "아름다움"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["사랑스러운", "감사한"],
                    "secondary": ["존경하는", "아름다운"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "love": ["사랑", "감사", "존경"],
                    "beauty": ["아름다움", "희망", "행복"]
                },
                "usage_contexts": ["사랑", "감사", "존경"],
                "seasonal_events": ["어머니날", "부모님날"]
            },
            "Hydrangea-블루": {
                "id": "Hydrangea-블루",
                "korean_name": "수국",
                "scientific_name": "Hydrangea",
                "color": "블루",
                "flower_meanings": {
                    "primary": ["진심", "이해"],
                    "secondary": ["차가운 마음", "거절"],
                    "other": ["변덕", "무정"]
                },
                "moods": {
                    "primary": ["차가운", "무정한"],
                    "secondary": ["이해하는", "진심 어린"],
                    "other": ["변덕스러운", "복잡한"]
                },
                "relationship_suitability": {
                    "understanding": ["이해", "진심", "공감"],
                    "apology": ["사과", "화해", "용서"]
                },
                "usage_contexts": ["이해", "사과", "화해"],
                "seasonal_events": ["여름", "비오는 날"]
            },
            "Anemone Coronaria-레드": {
                "id": "Anemone Coronaria-레드",
                "korean_name": "아네모네",
                "scientific_name": "Anemone Coronaria",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["희망", "기대"],
                    "secondary": ["사랑", "기쁨"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["희망적인", "기대하는"],
                    "secondary": ["사랑스러운", "기쁜"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "hope": ["희망", "기대", "사랑"],
                    "joy": ["기쁨", "행복", "평화"]
                },
                "usage_contexts": ["희망", "기대", "기쁨"],
                "seasonal_events": ["봄", "희망"]
            },
            "Gerbera Daisy-옐로우": {
                "id": "Gerbera Daisy-옐로우",
                "korean_name": "거베라 데이지",
                "scientific_name": "Gerbera Daisy",
                "color": "옐로우",
                "flower_meanings": {
                    "primary": ["기쁨", "희망"],
                    "secondary": ["활기", "긍정"],
                    "other": ["행복", "웃음"]
                },
                "moods": {
                    "primary": ["밝은", "활기찬"],
                    "secondary": ["경쾌한", "긍정적인"],
                    "other": ["즐거운", "행복한"]
                },
                "relationship_suitability": {
                    "celebration": ["생일", "축하", "합격"],
                    "encouragement": ["응원", "격려", "힘내"]
                },
                "usage_contexts": ["생일", "축하", "응원"],
                "seasonal_events": ["생일", "졸업", "합격"]
            },
            "Lily-화이트": {
                "id": "Lily-화이트",
                "korean_name": "릴리",
                "scientific_name": "Lily",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순결", "순수"],
                    "secondary": ["고귀함", "아름다움"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["순결한", "순수한"],
                    "secondary": ["고귀한", "아름다운"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "purity": ["순결", "순수", "고귀함"],
                    "beauty": ["아름다움", "희망", "행복"]
                },
                "usage_contexts": ["순결", "순수", "고귀함"],
                "seasonal_events": ["웨딩", "순결"]
            },
            "Dahlia-핑크": {
                "id": "Dahlia-핑크",
                "korean_name": "달리아",
                "scientific_name": "Dahlia",
                "color": "핑크",
                "flower_meanings": {
                    "primary": ["우아함", "아름다움"],
                    "secondary": ["사랑", "기쁨"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["우아한", "아름다운"],
                    "secondary": ["사랑스러운", "기쁜"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "elegance": ["우아함", "아름다움", "사랑"],
                    "joy": ["기쁨", "희망", "행복"]
                },
                "usage_contexts": ["우아함", "아름다움", "기쁨"],
                "seasonal_events": ["가을", "우아함"]
            },
            "Garden Peony-핑크": {
                "id": "Garden Peony-핑크",
                "korean_name": "가든 피오니",
                "scientific_name": "Garden Peony",
                "color": "핑크",
                "flower_meanings": {
                    "primary": ["부끄러움", "수줍음"],
                    "secondary": ["아름다움", "사랑"],
                    "other": ["희망", "행복"]
                },
                "moods": {
                    "primary": ["부끄러운", "수줍은"],
                    "secondary": ["아름다운", "사랑스러운"],
                    "other": ["희망적인", "행복한"]
                },
                "relationship_suitability": {
                    "shyness": ["부끄러움", "수줍음", "사랑"],
                    "beauty": ["아름다움", "희망", "행복"]
                },
                "usage_contexts": ["부끄러움", "수줍음", "아름다움"],
                "seasonal_events": ["봄", "사랑"]
            },
            "Iris Sanguinea-퍼플": {
                "id": "Iris Sanguinea-퍼플",
                "korean_name": "아이리",
                "scientific_name": "Iris Sanguinea",
                "color": "퍼플",
                "flower_meanings": {
                    "primary": ["희망", "신뢰"],
                    "secondary": ["지혜", "용기"],
                    "other": ["사랑", "행복"]
                },
                "moods": {
                    "primary": ["희망적인", "신뢰할 수 있는"],
                    "secondary": ["지혜로운", "용기있는"],
                    "other": ["사랑스러운", "행복한"]
                },
                "relationship_suitability": {
                    "hope": ["희망", "신뢰", "지혜"],
                    "courage": ["용기", "사랑", "행복"]
                },
                "usage_contexts": ["희망", "신뢰", "지혜"],
                "seasonal_events": ["봄", "희망"]
            },
            "Babys Breath-화이트": {
                "id": "Babys Breath-화이트",
                "korean_name": "베이비 브레스",
                "scientific_name": "Babys Breath",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순수", "순결"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["순수한", "순결한"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "purity": ["순수", "순결", "희망"],
                    "love": ["사랑", "행복", "평화"]
                },
                "usage_contexts": ["순수", "순결", "희망"],
                "seasonal_events": ["웨딩", "순결"]
            },
            "Stock Flower-화이트": {
                "id": "Stock Flower-화이트",
                "korean_name": "스톡 플라워",
                "scientific_name": "Stock Flower",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["영원한 사랑", "아름다움"],
                    "secondary": ["희망", "행복"],
                    "other": ["평화", "기쁨"]
                },
                "moods": {
                    "primary": ["영원한", "아름다운"],
                    "secondary": ["희망적인", "행복한"],
                    "other": ["평화로운", "기쁜"]
                },
                "relationship_suitability": {
                    "eternal": ["영원한 사랑", "아름다움", "희망"],
                    "happiness": ["행복", "평화", "기쁨"]
                },
                "usage_contexts": ["영원한 사랑", "아름다움", "행복"],
                "seasonal_events": ["영원한 사랑", "기념"]
            },
            "Scabiosa-블루": {
                "id": "Scabiosa-블루",
                "korean_name": "스카비오사",
                "scientific_name": "Scabiosa",
                "color": "블루",
                "flower_meanings": {
                    "primary": ["불운", "슬픔"],
                    "secondary": ["희망", "위로"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["불운한", "슬픈"],
                    "secondary": ["희망적인", "위로하는"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "comfort": ["위로", "희망", "평화"],
                    "stability": ["안정", "평화", "위로"]
                },
                "usage_contexts": ["위로", "희망", "평화"],
                "seasonal_events": ["위로", "안정"]
            },
            "Ammi Majus-화이트": {
                "id": "Ammi Majus-화이트",
                "korean_name": "아미 마주스",
                "scientific_name": "Ammi Majus",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["희망", "기쁨"],
                    "secondary": ["사랑", "행복"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["희망적인", "기쁜"],
                    "secondary": ["사랑스러운", "행복한"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "hope": ["희망", "기쁨", "사랑"],
                    "happiness": ["행복", "평화", "안정"]
                },
                "usage_contexts": ["희망", "기쁨", "행복"],
                "seasonal_events": ["봄", "희망"]
            },
            "Anthurium Andraeanum-레드": {
                "id": "Anthurium Andraeanum-레드",
                "korean_name": "안스리움",
                "scientific_name": "Anthurium Andraeanum",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["열정", "사랑"],
                    "secondary": ["아름다움", "희망"],
                    "other": ["행복", "기쁨"]
                },
                "moods": {
                    "primary": ["열정적인", "사랑스러운"],
                    "secondary": ["아름다운", "희망적인"],
                    "other": ["행복한", "기쁜"]
                },
                "relationship_suitability": {
                    "passion": ["열정", "사랑", "아름다움"],
                    "beauty": ["희망", "행복", "기쁨"]
                },
                "usage_contexts": ["열정", "사랑", "희망"],
                "seasonal_events": ["열정", "사랑"]
            },
            "Astilbe Japonica-핑크": {
                "id": "Astilbe Japonica-핑크",
                "korean_name": "아스틸베",
                "scientific_name": "Astilbe Japonica",
                "color": "핑크",
                "flower_meanings": {
                    "primary": ["희망", "기쁨"],
                    "secondary": ["사랑", "행복"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["희망적인", "기쁜"],
                    "secondary": ["사랑스러운", "행복한"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "hope": ["희망", "기쁨", "사랑"],
                    "happiness": ["행복", "평화", "안정"]
                },
                "usage_contexts": ["희망", "기쁨", "행복"],
                "seasonal_events": ["여름", "희망"]
            },
            "Bouvardia-화이트": {
                "id": "Bouvardia-화이트",
                "korean_name": "부바르디아",
                "scientific_name": "Bouvardia",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["우아함", "아름다움"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["우아한", "아름다운"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "elegance": ["우아함", "아름다움", "희망"],
                    "love": ["사랑", "행복", "평화"]
                },
                "usage_contexts": ["우아함", "아름다움", "사랑"],
                "seasonal_events": ["우아함", "아름다움"]
            },
            "Cockscomb-레드": {
                "id": "Cockscomb-레드",
                "korean_name": "맨드라미",
                "scientific_name": "Cockscomb",
                "color": "레드",
                "flower_meanings": {
                    "primary": ["용기", "열정"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "기쁨"]
                },
                "moods": {
                    "primary": ["용기있는", "열정적인"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "기쁜"]
                },
                "relationship_suitability": {
                    "courage": ["용기", "열정", "희망"],
                    "passion": ["사랑", "행복", "기쁨"]
                },
                "usage_contexts": ["용기", "열정", "희망"],
                "seasonal_events": ["용기", "열정"]
            },
            "Cotton Plant-화이트": {
                "id": "Cotton Plant-화이트",
                "korean_name": "면화",
                "scientific_name": "Cotton Plant",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순수", "자연"],
                    "secondary": ["희망", "평화"],
                    "other": ["안정", "편안함"]
                },
                "moods": {
                    "primary": ["순수한", "자연스러운"],
                    "secondary": ["희망적인", "평화로운"],
                    "other": ["안정적인", "편안한"]
                },
                "relationship_suitability": {
                    "purity": ["순수", "자연", "희망"],
                    "peace": ["평화", "안정", "편안함"]
                },
                "usage_contexts": ["순수", "자연", "평화"],
                "seasonal_events": ["자연", "평화"]
            },
            "Cymbidium Spp-화이트": {
                "id": "Cymbidium Spp-화이트",
                "korean_name": "심비디움",
                "scientific_name": "Cymbidium Spp",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["고귀함", "아름다움"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["고귀한", "아름다운"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "nobility": ["고귀함", "아름다움", "희망"],
                    "beauty": ["사랑", "행복", "평화"]
                },
                "usage_contexts": ["고귀함", "아름다움", "사랑"],
                "seasonal_events": ["고귀함", "아름다움"]
            },
            "Drumstick Flower-옐로우": {
                "id": "Drumstick Flower-옐로우",
                "korean_name": "드럼스틱 플라워",
                "scientific_name": "Drumstick Flower",
                "color": "옐로우",
                "flower_meanings": {
                    "primary": ["기쁨", "희망"],
                    "secondary": ["활기", "긍정"],
                    "other": ["행복", "웃음"]
                },
                "moods": {
                    "primary": ["기쁜", "희망적인"],
                    "secondary": ["활기찬", "긍정적인"],
                    "other": ["행복한", "웃음"]
                },
                "relationship_suitability": {
                    "joy": ["기쁨", "희망", "활기"],
                    "positivity": ["긍정", "행복", "웃음"]
                },
                "usage_contexts": ["기쁨", "희망", "행복"],
                "seasonal_events": ["기쁨", "희망"]
            },
            "Gentiana Andrewsii-블루": {
                "id": "Gentiana Andrewsii-블루",
                "korean_name": "용담",
                "scientific_name": "Gentiana Andrewsii",
                "color": "블루",
                "flower_meanings": {
                    "primary": ["진심", "이해"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["진심 어린", "이해하는"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "sincerity": ["진심", "이해", "희망"],
                    "love": ["사랑", "행복", "평화"]
                },
                "usage_contexts": ["진심", "이해", "사랑"],
                "seasonal_events": ["진심", "이해"]
            },
            "Globe Amaranth-퍼플": {
                "id": "Globe Amaranth-퍼플",
                "korean_name": "천일홍",
                "scientific_name": "Globe Amaranth",
                "color": "퍼플",
                "flower_meanings": {
                    "primary": ["영원한 사랑", "불변"],
                    "secondary": ["희망", "사랑"],
                    "other": ["행복", "평화"]
                },
                "moods": {
                    "primary": ["영원한", "불변하는"],
                    "secondary": ["희망적인", "사랑스러운"],
                    "other": ["행복한", "평화로운"]
                },
                "relationship_suitability": {
                    "eternal": ["영원한 사랑", "불변", "희망"],
                    "love": ["사랑", "행복", "평화"]
                },
                "usage_contexts": ["영원한 사랑", "불변", "희망"],
                "seasonal_events": ["영원한 사랑", "불변"]
            },
            "Iberis Sempervirens-화이트": {
                "id": "Iberis Sempervirens-화이트",
                "korean_name": "이베리스",
                "scientific_name": "Iberis Sempervirens",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["순수", "희망"],
                    "secondary": ["사랑", "행복"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["순수한", "희망적인"],
                    "secondary": ["사랑스러운", "행복한"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "purity": ["순수", "희망", "사랑"],
                    "happiness": ["행복", "평화", "안정"]
                },
                "usage_contexts": ["순수", "희망", "행복"],
                "seasonal_events": ["순수", "희망"]
            },
            "Veronica Spicata-화이트": {
                "id": "Veronica Spicata-화이트",
                "korean_name": "베로니카",
                "scientific_name": "Veronica Spicata",
                "color": "화이트",
                "flower_meanings": {
                    "primary": ["희망", "기쁨"],
                    "secondary": ["사랑", "행복"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["희망적인", "기쁜"],
                    "secondary": ["사랑스러운", "행복한"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "hope": ["희망", "기쁨", "사랑"],
                    "happiness": ["행복", "평화", "안정"]
                },
                "usage_contexts": ["희망", "기쁨", "행복"],
                "seasonal_events": ["희망", "기쁨"]
            },
            "Tagetes Erecta-옐로우": {
                "id": "Tagetes Erecta-옐로우",
                "korean_name": "태게테스",
                "scientific_name": "Tagetes Erecta",
                "color": "옐로우",
                "flower_meanings": {
                    "primary": ["기쁨", "희망"],
                    "secondary": ["활기", "긍정"],
                    "other": ["행복", "웃음"]
                },
                "moods": {
                    "primary": ["기쁜", "희망적인"],
                    "secondary": ["활기찬", "긍정적인"],
                    "other": ["행복한", "웃음"]
                },
                "relationship_suitability": {
                    "joy": ["기쁨", "희망", "활기"],
                    "positivity": ["긍정", "행복", "웃음"]
                },
                "usage_contexts": ["기쁨", "희망", "행복"],
                "seasonal_events": ["기쁨", "희망"]
            },
            "Freesia Refracta-옐로우": {
                "id": "Freesia Refracta-옐로우",
                "korean_name": "프리지아",
                "scientific_name": "Freesia Refracta",
                "color": "옐로우",
                "flower_meanings": {
                    "primary": ["순수", "희망"],
                    "secondary": ["사랑", "행복"],
                    "other": ["평화", "안정"]
                },
                "moods": {
                    "primary": ["순수한", "희망적인"],
                    "secondary": ["사랑스러운", "행복한"],
                    "other": ["평화로운", "안정적인"]
                },
                "relationship_suitability": {
                    "purity": ["순수", "희망", "사랑"],
                    "happiness": ["행복", "평화", "안정"]
                },
                "usage_contexts": ["순수", "희망", "행복"],
                "seasonal_events": ["순수", "희망"]
            }
        }
    
    def match(self, emotions: List[EmotionAnalysis], story: str, user_intent: str = "meaning_based", excluded_keywords: List[Dict[str, str]] = None, mentioned_flower: str = None, context: object = None) -> FlowerMatch:
        """꽃 매칭 - 사용자 의도에 따라 다른 전략 적용"""
        print(f"🎯 매칭 전략: {user_intent}")
        print(f"🚫 제외된 키워드: {excluded_keywords}")
        print(f"🌸 언급된 꽃: {mentioned_flower}")
        
        # 시즌 정보 추출
        current_season = self._extract_season_from_story(story)
        print(f"🌱 추출된 시즌: {current_season}")
        
        if user_intent == "design_based":
            return self._design_based_match(emotions, story, current_season, excluded_keywords)
        else:
            return self._meaning_based_match(emotions, story, current_season, excluded_keywords, mentioned_flower, context)
    
    def _extract_season_from_story(self, story: str) -> str:
        """스토리에서 시즌 정보 추출"""
        story_lower = story.lower()
        
        # 명시적 시즌 키워드
        if any(keyword in story_lower for keyword in ["새해", "1월", "정월", "설날", "겨울", "추운"]):
            return "겨울"
        elif any(keyword in story_lower for keyword in ["봄", "3월", "4월", "5월", "따뜻한", "개화"]):
            return "봄"
        elif any(keyword in story_lower for keyword in ["여름", "6월", "7월", "8월", "더운", "휴가"]):
            return "여름"
        elif any(keyword in story_lower for keyword in ["가을", "9월", "10월", "11월", "선선한", "단풍"]):
            return "가을"
        
        # 현재 날짜 기준 (기본값)
        from datetime import datetime
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            return "겨울"
        elif current_month in [3, 4, 5]:
            return "봄"
        elif current_month in [6, 7, 8]:
            return "여름"
        else:
            return "가을"
    
    def _is_flower_available_in_season(self, flower_data: dict, season: str) -> bool:
        """꽃이 해당 시즌에 구할 수 있는지 확인"""
        seasonality = flower_data.get('seasonality', [])
        return season in seasonality
    
    def _design_based_match(self, emotions: List[EmotionAnalysis], story: str, current_season: str = None, excluded_keywords: List[Dict[str, str]] = None) -> FlowerMatch:
        """디자인 기반 매칭: 컬러, 무드 우선, 감정/키워드 다음"""
        print("🎨 디자인 기반 매칭 시작")
        
        # 1. 컬러 추출
        color_keywords = self._extract_contextual_colors(story)
        print(f"🎨 추출된 컬러: {color_keywords}")
        
        # 2. 무드 추출
        mood_keywords = self._extract_mood_keywords(story)
        print(f"🎭 추출된 무드: {mood_keywords}")
        
        # 3. 컬러 + 무드 + 시즌 기반 점수 계산 (제외 조건 반영)
        flower_scores = {}
        excluded_texts = [kw.get('text', '') for kw in (excluded_keywords or [])]
        print(f"🚫 제외할 키워드들: {excluded_texts}")
        
        for flower_id, flower_data in self.flower_database.items():
            score = 0.0
            
            # 제외 조건 체크 - 제외된 키워드와 매칭되면 강한 페널티
            flower_color = flower_data.get('color', '')
            if excluded_keywords:
                for excluded_kw in excluded_keywords:
                    excluded_text = excluded_kw.get('text', '')
                    excluded_type = excluded_kw.get('type', '')
                    
                    # 색상 제외 조건
                    if excluded_type == 'color' and excluded_text in flower_color:
                        score -= 200.0  # 제외된 색상이면 강한 페널티
                        print(f"🚫 색상 제외 조건: {flower_data['korean_name']} - {excluded_text} 색상 제외됨")
                        break
                    
                    # 무드 제외 조건
                    elif excluded_type == 'mood':
                        flower_moods = flower_data.get('moods', {})
                        all_moods = []
                        all_moods.extend(flower_moods.get('primary', []))
                        all_moods.extend(flower_moods.get('secondary', []))
                        
                        if any(excluded_text in mood for mood in all_moods):
                            score -= 150.0  # 제외된 무드면 강한 페널티
                            print(f"🚫 무드 제외 조건: {flower_data['korean_name']} - {excluded_text} 무드 제외됨")
                            break
            
            # 시즌 매칭 (최우선 - 시즌에 맞지 않으면 강한 페널티)
            if current_season and not self._is_flower_available_in_season(flower_data, current_season):
                score -= 100.0  # 시즌에 맞지 않으면 강한 페널티
                print(f"❌ 시즌 불일치: {flower_data['korean_name']} - {current_season} 시즌에 구할 수 없음")
            elif current_season and self._is_flower_available_in_season(flower_data, current_season):
                score += 20.0  # 시즌에 맞으면 보너스
                print(f"✅ 시즌 매칭: {flower_data['korean_name']} - {current_season} 시즌에 구할 수 있음")
            
            # 컬러 매칭 (높은 가중치) - 제외되지 않은 색상만
            if color_keywords and flower_data.get('color', '') in color_keywords:
                if flower_color not in excluded_texts:  # 제외된 색상이 아니면
                    score += 50.0
                    print(f"🎨 컬러 매칭: {flower_data['korean_name']} - {flower_data.get('color', '')}")
            
            # 무드 매칭 (중간 가중치) - 제외되지 않은 무드만
            flower_moods = flower_data.get('moods', {})
            all_moods = []
            all_moods.extend(flower_moods.get('primary', []))
            all_moods.extend(flower_moods.get('secondary', []))
            
            for mood in mood_keywords:
                if mood not in excluded_texts and any(mood in flower_mood for flower_mood in all_moods):
                    score += 30.0
                    print(f"🎭 무드 매칭: {flower_data['korean_name']} - {mood}")
            
            # 감정/키워드 매칭 (낮은 가중치) - 제외되지 않은 감정만
            emotion_names = [e.emotion for e in emotions]
            flower_meanings = flower_data.get('flower_meanings', {})
            all_meanings = []
            all_meanings.extend(flower_meanings.get('primary', []))
            all_meanings.extend(flower_meanings.get('secondary', []))
            
            for emotion in emotion_names:
                if emotion not in excluded_texts and any(emotion in meaning for meaning in all_meanings):
                    score += 10.0
                    print(f"💭 감정 매칭: {flower_data['korean_name']} - {emotion}")
            
            flower_scores[flower_id] = score
        
        # 최고 점수 꽃 선택
        if not flower_scores:
            return self._fallback_match(emotions, story)
        
        best_flower_id = max(flower_scores, key=flower_scores.get)
        best_flower = self.flower_database[best_flower_id]
        
        print(f"🏆 디자인 기반 최종 선택: {best_flower['korean_name']} (점수: {flower_scores[best_flower_id]:.2f})")
        
        # 결과 생성
        image_url = self._get_flower_image_url(best_flower, color_keywords)
        emotion_names = [e.emotion if hasattr(e, 'emotion') else str(e) for e in emotions]
        hashtags = self._generate_hashtags(best_flower, emotion_names, excluded_keywords)
        
        return FlowerMatch(
            flower_name=best_flower['scientific_name'],
            korean_name=best_flower['korean_name'],
            scientific_name=best_flower['scientific_name'],
            image_url=image_url,
            keywords=best_flower.get('flower_meanings', {}).get('primary', [])[:2],
            hashtags=hashtags,
            color_keywords=color_keywords
        )
    
    def _meaning_based_match(self, emotions: List[EmotionAnalysis], story: str, current_season: str = None, excluded_keywords: List[Dict[str, str]] = None, mentioned_flower: str = None, context: object = None) -> FlowerMatch:
        """의미 기반 매칭: 꽃말과 꽃 특징 우선"""
        print("💭 의미 기반 매칭 시작")
        
        # 컬러 키워드 추출 (context에서 우선, 없으면 스토리에서 추출)
        if context and hasattr(context, 'colors') and context.colors:
            color_keywords = context.colors
            print(f"🎨 Context에서 색상 추출: {color_keywords}")
        else:
            color_keywords = self._extract_contextual_colors(story)
            print(f"🎨 스토리에서 색상 추출: {color_keywords}")
        
        # 언급된 꽃이 있으면 우선 선택
        if mentioned_flower and mentioned_flower in self.flower_database:
            best_flower = self.flower_database[mentioned_flower]
            print(f"🌸 언급된 꽃 우선 선택: {best_flower['korean_name']} ({mentioned_flower})")
            
            # 결과 생성
            image_url = self._get_flower_image_url(best_flower, color_keywords)
            emotion_names = [e.emotion if hasattr(e, 'emotion') else str(e) for e in emotions]
            hashtags = self._generate_hashtags(best_flower, emotion_names, excluded_keywords)
            
            return FlowerMatch(
                flower_name=best_flower['scientific_name'],
                korean_name=best_flower['korean_name'],
                scientific_name=best_flower['scientific_name'],
                image_url=image_url,
                keywords=best_flower.get('flower_meanings', {}).get('primary', [])[:2],
                hashtags=hashtags,
                color_keywords=color_keywords
            )
        
        # 기존 매칭 로직 사용
        flower_scores = self._calculate_flower_scores(emotions, story, color_keywords, current_season)
        
        if not flower_scores:
            return self._fallback_match(emotions, story)
        
        # 최고 점수 꽃 선택
        best_flower_id = max(flower_scores, key=flower_scores.get)
        best_flower = self.flower_database[best_flower_id]
        
        print(f"🏆 의미 기반 최종 선택: {best_flower['korean_name']} (점수: {flower_scores[best_flower_id]:.2f})")
        
        # 결과 생성
        image_url = self._get_flower_image_url(best_flower, color_keywords)
        emotion_names = [e.emotion if hasattr(e, 'emotion') else str(e) for e in emotions]
        hashtags = self._generate_hashtags(best_flower, emotion_names, excluded_keywords)
        
        return FlowerMatch(
            flower_name=best_flower['scientific_name'],
            korean_name=best_flower['korean_name'],
            scientific_name=best_flower['scientific_name'],
            image_url=image_url,
            keywords=best_flower.get('flower_meanings', {}).get('primary', [])[:2],
            hashtags=hashtags,
            color_keywords=color_keywords
        )
    
    def _calculate_flower_scores_with_dictionary(self, emotions: List[EmotionAnalysis], story: str, all_flowers: List, color_keywords: List[str]) -> Dict[str, float]:
        """꽃 사전 데이터를 사용한 점수 계산 (컬러 우선 필터링 → 꽃말/상징/감정 유사도)"""
        scores = {}
        
        # 1단계: 컬러 필터링 (컬러가 지정된 경우)
        filtered_flowers = all_flowers
        if color_keywords:
            filtered_flowers = []
            for flower in all_flowers:
                if hasattr(flower, 'dict'):
                    flower_dict = flower.dict()
                else:
                    flower_dict = flower
                
                flower_colors = flower_dict.get('color', [])
                if isinstance(flower_colors, str):
                    flower_colors = [flower_colors]
                
                # 컬러 매칭 확인
                color_matched = any(color in flower_colors for color in color_keywords)
                if color_matched:
                    filtered_flowers.append(flower)
                    print(f"🎨 컬러 필터링 통과: {flower_dict['korean_name']} - {flower_colors}")
                else:
                    print(f"❌ 컬러 필터링 제외: {flower_dict['korean_name']} - 요청: {color_keywords}, 실제: {flower_colors}")
        
        print(f"🔍 컬러 필터링 후 꽃 개수: {len(filtered_flowers)}개")
        
        # 2단계: 꽃말/상징/감정 유사도 점수 계산
        for flower in filtered_flowers:
            if hasattr(flower, 'dict'):
                flower_dict = flower.dict()
            else:
                flower_dict = flower
            
            flower_id = flower_dict['id']
            score = 0.0
            
            # 제외된 키워드 확인
            excluded_texts = [kw.get('text', '') for kw in excluded_keywords] if excluded_keywords else []
            print(f"🚫 제외된 키워드: {excluded_texts}")
            
            # 1. 꽃말 매칭 점수 (최우선) - 제외된 키워드 제외
            flower_meanings = flower_dict.get('flower_meanings', {})
            all_meanings = []
            all_meanings.extend(flower_meanings.get('primary', []))
            all_meanings.extend(flower_meanings.get('secondary', []))
            all_meanings.extend(flower_meanings.get('other', []))
            
            story_lower = story.lower()
            for meaning in all_meanings:
                # 제외된 키워드가 꽃말에 포함되어 있으면 점수 감점
                if any(excluded in meaning for excluded in excluded_texts):
                    score -= 3.0  # 제외된 키워드로 인한 큰 감점
                    print(f"❌ 제외된 키워드 꽃말: {flower_dict['korean_name']} - {meaning} (-3.0)")
                elif meaning.lower() in story_lower:
                    score += 2.0  # 꽃말 매칭은 높은 점수
                    print(f"💐 꽃말 매칭: {flower_dict['korean_name']} - {meaning} (+2.0)")
            
            # 2. 감정 매칭 점수 - 제외된 감정 제외
            flower_moods = flower_dict.get('moods', {})
            all_moods = []
            for mood_list in flower_moods.values():
                if isinstance(mood_list, list):
                    all_moods.extend(mood_list)
            
            for emotion in emotions:
                # 제외된 감정이면 매칭하지 않음
                if emotion.emotion in excluded_texts:
                    print(f"🚫 제외된 감정 매칭 건너뜀: {flower_dict['korean_name']} - {emotion.emotion}")
                    continue
                elif emotion.emotion in all_moods:
                    score += emotion.percentage * 0.02  # 감정 매칭 점수 증가
                    print(f"💭 감정 매칭: {flower_dict['korean_name']} - {emotion.emotion} (+{emotion.percentage * 0.02:.2f})")
            
            # 3. 사용 맥락 점수
            usage_contexts = flower_dict.get('usage_contexts', [])
            for context in usage_contexts:
                if context.lower() in story_lower:
                    score += 0.5
                    print(f"📝 맥락 매칭: {flower_dict['korean_name']} - {context} (+0.5)")
            
            # 4. 관계 적합성 점수
            relationship_suitability = flower_dict.get('relationship_suitability', {})
            for relationship, keywords in relationship_suitability.items():
                if isinstance(keywords, list) and any(keyword in story_lower for keyword in keywords):
                    score += 0.4
                    print(f"💕 관계 매칭: {flower_dict['korean_name']} - {relationship} (+0.4)")
            
            # 5. 계절 이벤트 점수
            seasonal_events = flower_dict.get('seasonal_events', [])
            for event in seasonal_events:
                if event.lower() in story_lower:
                    score += 0.3
                    print(f"🌱 계절 매칭: {flower_dict['korean_name']} - {event} (+0.3)")
            
            # 6. 특별 보너스 점수
            # 부정적 감정 해결 꽃 우선순위
            negative_emotions = ["우울", "스트레스", "외로움", "불안", "슬픔", "걱정"]
            if any(emotion in str(emotions) for emotion in negative_emotions):
                healing_keywords = ["희망", "기쁨", "행복", "활기", "위로", "따뜻함", "사랑", "기운"]
                if any(keyword in str(all_meanings) for keyword in healing_keywords):
                    score *= 1.3
                    print(f"💚 부정적 감정 해결 꽃: {flower_dict['korean_name']} (점수: {score:.2f})")
            
            scores[flower_id] = score
        
        print(f"📊 꽃 점수 요약: {len(scores)}개 꽃 중 상위 5개")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for flower_id, score in sorted_scores:
            flower = self.flower_database.get(flower_id)
            if flower:
                print(f"  {flower['korean_name']}: {score:.2f}")
        
        return scores
    
    def _load_base64_images(self):
        """Base64 이미지 데이터 로드"""
        try:
            # 현재 작업 디렉토리에서 직접 찾기
            import os
            base64_path = os.path.join(os.getcwd(), "base64_images.json")
            
            print(f"🔍 Base64 이미지 경로: {base64_path}")
            print(f"🔍 현재 작업 디렉토리: {os.getcwd()}")
            
            if not os.path.exists(base64_path):
                print(f"❌ 파일이 존재하지 않음: {base64_path}")
                return {}
            
            with open(base64_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ Base64 이미지 로드 성공: {len(data)} 개 폴더")
                print(f"📁 사용 가능한 폴더: {list(data.keys())}")
                return data
        except Exception as e:
            print(f"❌ Base64 이미지 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_flower_image_url(self, flower, color_keywords: List[str]) -> str:
        """꽃별 색상에 맞는 Supabase Storage 이미지 URL 반환"""
        flower_name = flower['korean_name']
        scientific_name = flower['scientific_name']
        
        print(f"🔍 Storage 이미지 매칭 디버깅:")
        print(f"  꽃 이름: {flower_name}")
        print(f"  학명: {scientific_name}")
        print(f"  색상 키워드: {color_keywords}")
        
        # flower_id 생성 (스프레드시트 형식)
        flower_id = self._generate_flower_id(scientific_name, color_keywords)
        
        if flower_id:
            # Supabase Storage URL 생성
            supabase_url = os.getenv("SUPABASE_URL")
            if supabase_url:
                storage_url = f"{supabase_url}/storage/v1/object/public/flowers/{flower_id}.webp"
                print(f"✅ Storage URL 생성: {storage_url}")
                return storage_url
        
        # 폴백: 기존 로컬 이미지 URL 사용
        print(f"⚠️ Storage URL 생성 실패, 로컬 이미지 사용: {flower_name}")
        return self._get_local_flower_image_url(flower, color_keywords)
    
    def _generate_flower_id(self, scientific_name: str, color_keywords: List[str]) -> str:
        """스프레드시트 형식의 flower_id 생성"""
        try:
            # 학명을 소문자로 변환하고 공백을 하이픈으로 변경
            base_flower = scientific_name.lower().replace(' ', '-').replace('.', '')
            
            # 색상 코드 매핑
            color_mapping = {
                '화이트': 'wh', '핑크': 'pk', '레드': 'rd', '옐로우': 'yl',
                '퍼플': 'pu', '블루': 'bl', '오렌지': 'or', '그린': 'gr',
                '크림색': 'cr', '베이지': 'be', '라일락': 'll', '네이비': 'nv',
                'white': 'wh', 'pink': 'pk', 'red': 'rd', 'yellow': 'yl',
                'purple': 'pu', 'blue': 'bl', 'orange': 'or', 'green': 'gr',
                'cream': 'cr', 'beige': 'be', 'lilac': 'll', 'navy': 'nv'
            }
            
            # 색상 키워드에서 색상 코드 찾기
            color_code = None
            for color in color_keywords:
                clean_color = color.strip("'\"")
                if clean_color in color_mapping:
                    color_code = color_mapping[clean_color]
                    break
            
            if color_code:
                flower_id = f"{base_flower}-{color_code}"
                print(f"  생성된 flower_id: {flower_id}")
                return flower_id
            
            return None
            
        except Exception as e:
            print(f"❌ flower_id 생성 실패: {e}")
            return None
    
    def _get_local_flower_image_url(self, flower, color_keywords: List[str]) -> str:
        """기존 로컬 이미지 URL 반환 (폴백용)"""
        flower_name = flower['korean_name']
        scientific_name = flower['scientific_name']
        flower_folder = self._get_flower_folder(scientific_name)
        
        # Base64 이미지가 없는 경우 기본 이미지 사용
        if not flower_folder or flower_folder not in self.base64_images:
            return f"/images/default/{flower_name.lower().replace(' ', '-')}.webp"
        
        # 꽃별 색상 매핑 (요청 색상 → 실제 파일명)
        color_mapping = self._get_flower_color_mapping(flower_name)
        
        # 색상 키워드 정리 (따옴표 제거)
        clean_color_keywords = []
        for color in color_keywords:
            clean_color = color.strip("'\"")
            clean_color_keywords.append(clean_color)
        
        # 1차: 정확한 색상 매칭 시도
        for clean_keyword in clean_color_keywords:
            actual_color = color_mapping.get(clean_keyword, clean_keyword)
            image_url = f"/images/{flower_folder}/{actual_color}.webp"
            
            # 실제 파일 존재 여부 확인
            if self._is_image_file_exists(flower_folder, actual_color):
                return image_url
        
        # 2차: 사용 가능한 색상 중에서 선택
        available_colors = self._get_available_colors(flower_folder)
        if available_colors:
            best_color = self._find_best_matching_color(clean_color_keywords, available_colors)
            image_url = f"/images/{flower_folder}/{best_color}.webp"
            return image_url
        
        # 3차: 기본 색상 사용
        default_color = self._get_default_color(flower_name)
        image_url = f"/images/{flower_folder}/{default_color}.webp"
        return image_url
    
    def _is_image_file_exists(self, flower_folder: str, color: str) -> bool:
        """실제 이미지 파일이 존재하는지 확인"""
        import os
        image_path = f"data/images_webp/{flower_folder}/{color}.webp"
        return os.path.exists(image_path)
    
    def _get_available_colors(self, flower_folder: str) -> List[str]:
        """꽃 폴더에서 사용 가능한 색상 목록 반환"""
        import os
        folder_path = f"data/images_webp/{flower_folder}"
        if not os.path.exists(folder_path):
            return []
        
        colors = []
        for file in os.listdir(folder_path):
            if file.endswith('.webp'):
                color = file.replace('.webp', '')
                colors.append(color)
        
        return colors
    
    def _find_best_matching_color(self, requested_colors: List[str], available_colors: List[str]) -> str:
        """요청된 색상과 가장 유사한 사용 가능한 색상 찾기"""
        if not available_colors:
            return "화이트"  # 기본값
        
        # 색상 유사도 매핑
        color_similarity = {
            "핑크": ["핑크", "라일락", "레드"],
            "레드": ["레드", "핑크", "오렌지"],
            "옐로우": ["옐로우", "오렌지"],
            "오렌지": ["오렌지", "옐로우", "레드"],
            "블루": ["블루", "퍼플"],
            "퍼플": ["퍼플", "블루", "라일락"],
            "라일락": ["라일락", "퍼플", "핑크"],
            "그린": ["그린"],
            "화이트": ["화이트", "아이보리", "크림"],
            "아이보리": ["아이보리", "화이트", "크림"],
            "파스텔톤": ["핑크", "라일락", "화이트"]
        }
        
        # 요청된 색상과 가장 유사한 색상 찾기
        for requested_color in requested_colors:
            if requested_color in color_similarity:
                for similar_color in color_similarity[requested_color]:
                    if similar_color in available_colors:
                        return similar_color
        
        # 유사한 색상이 없으면 첫 번째 사용 가능한 색상 반환
        return available_colors[0]
    
    def _get_flower_color_mapping(self, flower_name: str) -> Dict[str, str]:
        """꽃별 색상 매핑 반환"""
        # 색상 매핑 (새로운 색상 코드 시스템)
        base_mapping = {
            # 강렬한/비비드 색상 요청
            "알록달록": "레드",
            "화려한": "레드",
            "형형색색": "레드",
            "비비드": "레드",
            "선명한": "레드",
            "강렬한": "레드",
            "포인트": "레드",
            "포인트 컬러": "레드",
            
            # 기본 색상들 (통일된 색상명 사용)
            "화이트": "화이트", "white": "화이트", "흰색": "화이트", "wh": "화이트",
            "아이보리": "아이보리", "ivory": "아이보리", "iv": "아이보리",
            "베이지": "베이지", "beige": "베이지", "be": "베이지",
            "옐로우": "옐로우", "yellow": "옐로우", "yl": "옐로우", "노랑": "옐로우",
            "오렌지": "오렌지", "orange": "오렌지", "or": "오렌지", "오렌지톤": "오렌지",
            "코랄": "코랄", "coral": "코랄", "cr": "코랄",
            "핑크": "핑크", "pink": "핑크", "pk": "핑크",
            "레드": "레드", "red": "레드", "rd": "레드", "빨강": "레드",
            "라일락": "라일락", "lilac": "라일락", "ll": "라일락", "라벤더": "라일락",
            "퍼플": "퍼플", "purple": "퍼플", "pu": "퍼플", "보라": "퍼플",
            "블루": "블루", "blue": "블루", "bl": "블루", "파랑": "블루", "옅은 블루": "블루",
            "그린": "그린", "green": "그린", "gn": "그린", "초록": "그린",
            
            # 기존 호환성 유지
            "크림": "화이트", "cream": "화이트", "크림색": "화이트",
            "연핑크": "핑크", "light-pink": "핑크",
            "연보라": "라일락",
            "네이비": "블루", "네이비블루": "블루", "네이비 블루": "블루",
            "파스텔톤": "핑크", "파스텔": "핑크", "부드러운 색": "핑크", "연한 색": "핑크", "옅은": "핑크"
        }
        
        # 꽃별 특별 매핑 (기존 호환성 유지)
        flower_specific_mapping = {
            "Alstroemeria Spp": {
                "옐로우": "오렌지",
                "yellow": "오렌지",
                "노랑": "오렌지",
                "블루": "화이트",
                "blue": "화이트",
                "파랑": "화이트"
            },
            "Gerbera Daisy": {
                "옐로우": "옐로우",
                "yellow": "옐로우",
                "노랑": "옐로우",
                "오렌지": "오렌지",
                "orange": "오렌지"
            },
            "Dahlia": {
                "옐로우": "옐로우",
                "yellow": "옐로우",
                "노랑": "옐로우",
                "오렌지": "오렌지",
                "orange": "오렌지"
            },
            "Tulip": {
                "옐로우": "옐로우",
                "yellow": "옐로우",
                "노랑": "옐로우",
                "그린": "그린",
                "green": "그린"
            },
            "Lily": {
                "크림": "아이보리",
                "cream": "아이보리",
                "아이보리": "아이보리",
                "ivory": "아이보리",
                "연핑크": "핑크",
                "light-pink": "핑크",
                "연보라": "라일락"
            }
        }
        
        # 기본 매핑에 꽃별 특별 매핑 추가
        if flower_name in flower_specific_mapping:
            base_mapping.update(flower_specific_mapping[flower_name])
        
        return base_mapping
    
    def _is_color_available(self, flower_name: str, color: str) -> bool:
        """해당 꽃의 색상이 실제로 사용 가능한지 확인"""
        # 실제 파일 존재 여부를 확인하는 로직
        # 현재는 간단한 매핑으로 처리
        available_colors = {
            "gerbera-daisy": ["옐로우", "오렌지", "레드", "핑크"],
            "tulip": ["레드", "화이트", "옐로우", "핑크", "퍼플"],
            "lily": ["화이트", "아이보리", "핑크", "라일락"],
            "hydrangea": ["핑크", "블루", "퍼플", "라일락"],
            "scabiosa": ["화이트", "블루", "퍼플", "라일락"],
            "stock-flower": ["퍼플", "화이트", "핑크", "라일락"],
            "rose": ["레드", "핑크", "화이트", "퍼플", "라일락"],
            "garden-peony": ["화이트", "핑크", "아이보리", "라일락"],
            "lisianthus": ["화이트", "아이보리", "핑크", "라일락"],
            "bouvardia": ["화이트", "아이보리", "핑크"],
            "drumstick-flower": ["옐로우", "오렌지"],
            "cotton-plant": ["화이트", "아이보리", "베이지"],
            "cockscomb": ["레드", "오렌지", "옐로우"],
            "globe-amaranth": ["퍼플", "핑크", "화이트", "라일락"],
            "marguerite-daisy": ["화이트", "아이보리"],
            "babys-breath": ["화이트", "아이보리"],
            "dahlia": ["옐로우", "핑크", "오렌지", "레드"],
            
            "gladiolus": ["레드", "핑크", "화이트", "옐로우"],
            "astilbe-japonica": ["핑크"],
            "ranunculus": ["핑크", "화이트", "옐로우", "오렌지"],
            "alstroemeria-spp": ["핑크", "오렌지", "옐로우"],
            "ammi-majus": ["화이트"],
            "anemone-coronaria": ["레드", "퍼플"],
            "anthurium-andraeanum": ["레드", "그린", "화이트"],
            "cymbidium-spp": ["화이트", "핑크", "그린"],
            "veronica-spicata": ["퍼플"],
            "zinnia-elegans": ["핑크"]
        }
        
        flower_folder = self._get_flower_folder(flower_name)
        return color in available_colors.get(flower_folder, [])
    
    def _get_fallback_color(self, flower_name: str, color_keywords: List[str]) -> str:
        """폴백 색상 반환"""
        # 기본 색상 우선
        default_color = self._get_default_color(flower_name)
        if default_color:
            return default_color
        
        # 색상 키워드가 있으면 첫 번째 사용
        if color_keywords:
            return color_keywords[0]
        
        return '화이트'
    
    def _get_flower_folder(self, flower_name: str) -> str:
        """꽃 이름을 폴더명으로 변환"""
        folder_mapping = {
            "Gerbera Daisy": "gerbera-daisy",
            "Gerbera jamesonii": "gerbera-daisy",
            "Dahlia": "dahlia",
            "Rose": "rose",
            "Lily": "lily",
            "Tulip": "tulip",
            "Tulipa": "tulip",
            "Garden Peony": "garden-peony",
            "Lisianthus": "lisianthus",
            "Hydrangea": "hydrangea",
            "Scabiosa": "scabiosa",
            "Bouvardia": "bouvardia",
            "Stock Flower": "stock-flower",
            "Drumstick Flower": "drumstick-flower",
            "Cotton Plant": "cotton-plant",
            "Cockscomb": "cockscomb",
            "Globe Amaranth": "globe-amaranth",
            "Marguerite Daisy": "marguerite-daisy",
            "Babys Breath": "babys-breath",

            "Gladiolus": "gladiolus",
            "Astilbe Japonica": "astilbe-japonica",
            "Cymbidium Spp": "cymbidium-spp",
            "Anemone Coronaria": "anemone-coronaria",
            "Anthurium Andraeanum": "anthurium-andraeanum",
            "Ammi Majus": "ammi-majus",
            "Veronica Spicata": "veronica-spicata",
            "Alstroemeria Spp": "alstroemeria-spp",
            "Zinnia Elegans": "zinnia-elegans",
            "Tagetes Erecta": "tagetes-erecta",
            "Iberis Sempervirens": "iberis-sempervirens",
            "Iris Sanguinea": "iris-sanguinea",
            "Lathyrus Odoratus": "lathyrus-odoratus",
            "Ranunculus Asiaticus": "ranunculus-asiaticus",
            "Gentiana Andrewsii": "gentiana-andrewsii",
            "Dianthus Caryophyllus": "dianthus-caryophyllus",
            "Freesia Refracta": "freesia-refracta",
            "Ranunculus": "ranunculus"
        }
        return folder_mapping.get(flower_name, "")
    
    def _check_image_exists(self, folder_name: str, color: str) -> bool:
        """이미지 파일이 실제로 존재하는지 확인"""
        import os
        image_path = f"data/images_webp/{folder_name}/{color}.webp"
        return os.path.exists(image_path)
    
    def _fallback_match(self, emotions: List[EmotionAnalysis], story: str) -> FlowerMatch:
        """폴백 매칭 로직"""
        # 실시간 컨텍스트 추출기에서 색상 가져오기
        try:
            from app.services.realtime_context_extractor import RealtimeContextExtractor
            context_extractor = RealtimeContextExtractor()
            context = context_extractor.extract_context_realtime(story)
            color_keywords = context.colors if context.colors else self._extract_contextual_colors(story)
        except:
            color_keywords = self._extract_contextual_colors(story)
        
        print(f"🎨 폴백 - 실시간 추출된 색상 키워드: {color_keywords}")
        
        # 색상 우선 매칭 - 절대 우선순위
        if color_keywords:
            color_flower_map = {
                # 블루 계열
                "블루": ["Rose", "Hydrangea", "Scabiosa", "Veronica Spicata"],
                "옅은 블루": ["Rose", "Hydrangea", "Scabiosa", "Veronica Spicata"],
                "파랑": ["Rose", "Hydrangea", "Scabiosa", "Veronica Spicata"],
                "네이비 블루": ["Rose", "Dahlia"],
                
                # 핑크 계열
                "핑크": ["Rose", "Alstroemeria Spp", "Dahlia", "Zinnia Elegans", "Ranunculus"],
                "연핑크": ["Rose", "Alstroemeria Spp", "Dahlia", "Zinnia Elegans"],
                "옅은 핑크": ["Rose", "Alstroemeria Spp", "Dahlia", "Zinnia Elegans"],
                
                # 레드 계열
                "레드": ["Rose", "Cockscomb", "Zinnia Elegans", "Tulip"],
                "빨강": ["Rose", "Cockscomb", "Zinnia Elegans", "Tulip"],
                
                # 옐로우 계열
                "옐로우": ["Gerbera Daisy", "Dahlia", "Tagetes Erecta", "Tulip"],
                "노랑": ["Gerbera Daisy", "Dahlia", "Tagetes Erecta", "Tulip"],
                
                # 오렌지 계열
                "오렌지": ["Gerbera Daisy", "Cockscomb", "Tagetes Erecta", "Alstroemeria Spp", "Rose"],
                "주황": ["Gerbera Daisy", "Cockscomb", "Tagetes Erecta", "Alstroemeria Spp", "Rose"],
                
                # 퍼플 계열
                "퍼플": ["Veronica Spicata", "Globe Amaranth"],
                "보라": ["Veronica Spicata", "Globe Amaranth"],
                "라일락": ["Veronica Spicata", "Globe Amaranth"],
                
                # 화이트 계열
                "화이트": ["Alstroemeria Spp", "Ranunculus", "Tulip", "Cockscomb", "Drumstick Flower", "Dahlia", "Rose", "Scabiosa", "Globe Amaranth", "Hydrangea"],
                "흰색": ["Alstroemeria Spp", "Ranunculus", "Tulip", "Cockscomb", "Drumstick Flower", "Dahlia", "Rose", "Scabiosa", "Globe Amaranth", "Hydrangea"],
                
                # 베이지 계열
                "베이지": ["Gerbera Daisy"],
                "크림색": ["Alstroemeria Spp"]
            }
            
            # 색상에 맞는 꽃들 찾기 (실제 이미지가 있는 컬러만)
            available_flowers = []
            for color in color_keywords:
                if color in color_flower_map:
                    for flower_name in color_flower_map[color]:
                        if flower_name in self.flower_database:
                            # 실제 이미지 파일이 있는지 확인
                            folder_name = self._get_flower_folder(flower_name)
                            if self._check_image_exists(folder_name, color):
                                available_flowers.append(flower_name)
                                print(f"✅ 이미지 확인: {flower_name} - {color} (폴더: {folder_name})")
                            else:
                                print(f"❌ 이미지 없음: {flower_name} - {color} (폴더: {folder_name})")
            
            if available_flowers:
                import random
                # 가중치를 적용하여 다양한 꽃이 선택되도록 함
                weights = []
                for flower in available_flowers:
                    # 최근에 많이 선택된 꽃들은 가중치를 낮춤
                    if flower in ["Rose", "Lisianthus", "Gerbera Daisy"]:
                        weights.append(0.5)  # 가중치 낮춤
                    else:
                        weights.append(1.0)  # 일반 가중치
                
                # 가중치가 적용된 랜덤 선택
                if weights and sum(weights) > 0:
                    flower_name = random.choices(available_flowers, weights=weights)[0]
                else:
                    flower_name = random.choice(available_flowers)
                
                print(f"🎨 색상 우선 매칭: {color_keywords} → {flower_name}")
                # 색상이 있으면 무조건 색상 우선 매칭 사용
            else:
                # 색상에 맞는 꽃이 없으면 다른 색상으로 fallback
                print(f"⚠️ 요청된 색상 {color_keywords}에 맞는 꽃이 없어 다른 색상으로 fallback")
                flower_name = self._get_fallback_flower_by_context(story)
        else:
            # 색상 요청이 없으면 일반 로직 사용
            flower_name = self._get_fallback_flower_by_context(story)
        
        flower_data = self.flower_database.get(flower_name)
        image_url = self._get_flower_image_url(flower_data, color_keywords)
        emotion_names = [e.emotion if hasattr(e, 'emotion') else str(e) for e in emotions]
        hashtags = self._generate_hashtags(flower_data, emotion_names)
        
        return FlowerMatch(
            flower_name=flower_name,
            korean_name=flower_data["korean_name"],
            scientific_name=flower_data["scientific_name"],
            image_url=image_url,
            keywords=flower_data["flower_meanings"]["primary"],
            hashtags=hashtags,
            color_keywords=color_keywords
        )
    
    def _get_fallback_flower_by_context(self, story: str) -> str:
        """컨텍스트 기반 폴백 꽃 선택"""
        # 우선순위 규칙
        if any(keyword in story.lower() for keyword in ["알록달록", "화려한", "형형색색", "비비드", "선명한"]):
            # 알록달록/비비드 색상 요청 - 가장 밝고 선명한 꽃들 우선
            vivid_flowers = ["Gerbera Daisy", "Dahlia", "Cockscomb", "Drumstick Flower", "Zinnia Elegans"]
            import random
            return random.choice(vivid_flowers)
        elif any(keyword in story.lower() for keyword in ["해외 유학", "유학 완료", "돌아왔어", "여행지"]):
            # 해외 유학 완료 환영 - 밝고 경쾌한 꽃 우선
            celebration_flowers = ["Gerbera Daisy", "Dahlia", "Tulip", "Cockscomb", "Drumstick Flower", "Tagetes Erecta"]
            import random
            return random.choice(celebration_flowers)
        elif any(keyword in story.lower() for keyword in ["형형색색", "화려한", "축하", "합격", "성취"]):
            celebration_flowers = ["Dahlia", "Gerbera Daisy", "Cockscomb", "Zinnia Elegans"]
            import random
            return random.choice(celebration_flowers)
        elif any(keyword in story.lower() for keyword in ["우드톤", "내추럴", "인테리어"]):
            # 내추럴한 꽃들 중에서 선택 (Lisianthus 우선순위 낮춤)
            natural_flowers = ["Lily", "Garden Peony", "Cotton Plant", "Babys Breath", "Marguerite Daisy", "Ammi Majus"]
            import random
            return random.choice(natural_flowers)
        elif any(keyword in story.lower() for keyword in ["독특한", "모던한", "포인트"]):
            # 독특한 꽃들 중에서 선택
            unique_flowers = ["Scabiosa", "Drumstick Flower", "Cockscomb", "Globe Amaranth", "Astilbe Japonica"]
            import random
            return random.choice(unique_flowers)
        elif any(keyword in story.lower() for keyword in ["부드러운", "자연스러운", "순수한"]):
            # 부드러운 꽃들 중에서 선택
            soft_flowers = ["Babys Breath", "Marguerite Daisy", "Cotton Plant", "Lily", "Ammi Majus"]
            import random
            return random.choice(soft_flowers)
        elif any(keyword in story.lower() for keyword in ["그리움", "추억", "이사", "떠남", "20년지기", "만남", "기념"]):
            # 그리움/추억 관련 꽃들 중에서 선택 (Lisianthus 우선순위 낮춤)
            memory_flowers = ["Scabiosa", "Stock Flower", "Hydrangea", "Lathyrus Odoratus", "Garden Peony", "Veronica Spicata"]
            import random
            return random.choice(memory_flowers)
        elif any(keyword in story.lower() for keyword in ["위로", "응원", "힘들어", "격려", "후배", "발표", "긴장"]):
            # 격려/응원 관련 꽃들 중에서 선택
            encouragement_flowers = ["Freesia Refracta", "Gerbera Daisy", "Tulip", "Dahlia", "Gentiana Andrewsii"]
            import random
            return random.choice(encouragement_flowers)
        else:
            # 점수 기반 선택
            scores = self._calculate_flower_scores(emotions, story)
            return max(scores, key=scores.get)
    
    def _calculate_flower_scores(self, emotions: List[EmotionAnalysis], story: str, color_keywords: List[str], current_season: str = None) -> Dict[str, float]:
        """꽃 점수 계산 (유사도 기반)"""
        scores = {}
        
        for flower_id, flower_data in self.flower_database.items():
            score = 0.0
            
            # 1. 감정 유사도 매칭 점수
            flower_moods = flower_data.get('moods', {})
            # moods는 딕셔너리 형태이므로 모든 값들을 평면화
            all_moods = []
            for mood_list in flower_moods.values():
                if isinstance(mood_list, list):
                    all_moods.extend(mood_list)
            
            for emotion in emotions:
                # 감정 유사도 계산
                emotion_similarity = self._calculate_emotion_similarity(emotion.emotion, all_moods)
                score += emotion_similarity * emotion.percentage * 0.01
                if emotion_similarity > 0.5:
                    print(f"💭 감정 유사도 매칭: {flower_data['korean_name']} - {emotion.emotion} (유사도: {emotion_similarity:.2f}, +{emotion_similarity * emotion.percentage * 0.01:.2f})")
            
            # 2. 색상 유사도 매칭 점수
            flower_colors = flower_data.get('color', [])
            if isinstance(flower_colors, str):
                flower_colors = [flower_colors]
            
            for color in color_keywords:
                # 색상 유사도 계산
                color_similarity = self._calculate_color_similarity(color, flower_colors)
                score += color_similarity * 0.3
                if color_similarity > 0.5:
                    print(f"🎨 색상 유사도 매칭: {flower_data['korean_name']} - {color} (유사도: {color_similarity:.2f}, +{color_similarity * 0.3:.2f})")
            
            # 3. 관계 적합성 유사도 점수
            relationship_suitability = flower_data.get('relationship_suitability', {})
            story_lower = story.lower()
            for relationship, keywords in relationship_suitability.items():
                if isinstance(keywords, list):
                    # 키워드 유사도 계산
                    keyword_similarity = self._calculate_keyword_similarity(story_lower, keywords)
                    score += keyword_similarity * 0.4
                    if keyword_similarity > 0.3:
                        print(f"💕 관계 유사도 매칭: {flower_data['korean_name']} - {relationship} (유사도: {keyword_similarity:.2f}, +{keyword_similarity * 0.4:.2f})")
            
            # 4. 사용 맥락 유사도 점수
            usage_contexts = flower_data.get('usage_contexts', [])
            context_similarity = self._calculate_keyword_similarity(story_lower, usage_contexts)
            score += context_similarity * 0.3
            if context_similarity > 0.3:
                print(f"📝 맥락 유사도 매칭: {flower_data['korean_name']} (유사도: {context_similarity:.2f}, +{context_similarity * 0.3:.2f})")
            
            # 5. 계절 이벤트 유사도 점수
            seasonal_events = flower_data.get('seasonal_events', [])
            event_similarity = self._calculate_keyword_similarity(story_lower, seasonal_events)
            score += event_similarity * 0.2
            if event_similarity > 0.3:
                print(f"🌱 계절 유사도 매칭: {flower_data['korean_name']} (유사도: {event_similarity:.2f}, +{event_similarity * 0.2:.2f})")
            
            # 6. 꽃말 유사도 점수
            flower_meanings = flower_data.get('flower_meanings', {})
            primary_meanings = flower_meanings.get('primary', [])
            meaning_similarity = self._calculate_keyword_similarity(story_lower, primary_meanings)
            score += meaning_similarity * 0.2
            if meaning_similarity > 0.3:
                print(f"💐 꽃말 유사도 매칭: {flower_data['korean_name']} (유사도: {meaning_similarity:.2f}, +{meaning_similarity * 0.2:.2f})")
            
            # 7. 리시안셔스 점수 조정 (다양성 확보)
            if flower_data['korean_name'] == '리시안서스':
                score *= 0.7
                print(f"🔽 리시안서스 점수 조정: {score:.2f}")
            
            # 8. 옐로우 톤 꽃 우선순위 (밝은 기분을 위한)
            if any(keyword in story.lower() for keyword in ["흐린 날씨", "흐려서", "기분이 처져요", "처져", "우울", "침침한", "밝아질", "밝게", "활기", "기운"]):
                if flower_data.get('color') in ['옐로우', '노랑', '골드']:
                    score *= 1.5
                    print(f"☀️ 옐로우 톤 우선순위: {flower_data['korean_name']} (점수: {score:.2f})")
            
            # 9. 부정적 감정 해결 꽃 우선순위
            negative_emotions = ["우울", "스트레스", "외로움", "불안", "슬픔", "걱정"]
            if any(emotion in str(emotions) for emotion in negative_emotions):
                # 부정적 감정을 해결하는 꽃말을 가진 꽃들 우선순위
                flower_meanings = flower_data.get('flower_meanings', {})
                all_meanings = []
                all_meanings.extend(flower_meanings.get('primary', []))
                all_meanings.extend(flower_meanings.get('secondary', []))
                all_meanings.extend(flower_meanings.get('other', []))
                
                healing_keywords = ["희망", "기쁨", "행복", "활기", "위로", "따뜻함", "사랑", "기운"]
                if any(keyword in str(all_meanings) for keyword in healing_keywords):
                    score *= 1.3
                    print(f"💚 부정적 감정 해결 꽃: {flower_data['korean_name']} (점수: {score:.2f})")
            
            # 3. 색상 유사도 점수
            if color_keywords:
                flower_color = flower_data.get('color', '')
                color_similarity = self._calculate_color_similarity(color_keywords[0], [flower_color])
                score += color_similarity * 0.3
                if color_similarity > 0.3:
                    print(f"🎨 색상 유사도 매칭: {flower_data['korean_name']} - {color_keywords[0]} (유사도: {color_similarity:.2f}, +{color_similarity * 0.3:.2f})")
            
            # 색상 우선순위 조정 (요청된 색상과 정확히 일치하는 경우 높은 점수)
            if color_keywords and flower_data.get('color', '') in color_keywords:
                score *= 2.0  # 색상 일치 시 점수 2배
                print(f"🎯 색상 정확 매칭: {flower_data['korean_name']} - {flower_data.get('color', '')} (점수: {score:.2f})")
            elif color_keywords and flower_data.get('color', '') not in color_keywords:
                score *= 0.3  # 색상 불일치 시 점수 대폭 감소
                print(f"❌ 색상 불일치: {flower_data['korean_name']} - 요청: {color_keywords[0]}, 실제: {flower_data.get('color', '')} (점수: {score:.2f})")
            
            scores[flower_id] = score
        
        print(f"📊 꽃 점수 요약: {len(scores)}개 꽃 중 상위 5개")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for flower_id, score in sorted_scores:
            flower_data = self.flower_database[flower_id]
            print(f"  {flower_data['korean_name']}: {score:.2f}")
        
        return scores
    
    def _calculate_emotion_similarity(self, emotion: str, mood_list: List[str]) -> float:
        """감정 유사도 계산"""
        emotion_lower = emotion.lower()
        
        # 감정 유사도 매핑
        emotion_similarities = {
            "사랑/로맨스": ["사랑", "로맨틱한", "열정적인", "매혹적인", "사랑스러운"],
            "기쁨": ["기쁜", "행복한", "즐거운", "밝은", "활기찬"],
            "위로": ["위로하는", "따뜻한", "안정적인", "편안한", "포근한"],
            "응원/격려": ["응원하는", "격려하는", "지지하는", "용기있는", "희망적인"],
            "감사/존경": ["감사한", "존경하는", "고귀한", "아름다운", "우아한"],
            "그리움/추억": ["그리운", "추억하는", "아련한", "회상하는", "기억하는"],
            "희망": ["희망적인", "미래의", "새로운", "신뢰할 수 있는", "완벽한"],
            "순수": ["순수한", "순결한", "깨끗한", "자연스러운", "이상적인"]
        }
        
        # 감정 그룹 찾기
        for group, similar_emotions in emotion_similarities.items():
            if emotion_lower in group.lower() or any(similar in emotion_lower for similar in similar_emotions):
                # 해당 그룹의 감정들과 매칭
                for mood in mood_list:
                    mood_lower = mood.lower()
                    if any(similar in mood_lower for similar in similar_emotions):
                        return 0.8  # 높은 유사도
                    elif any(word in mood_lower for word in emotion_lower.split()):
                        return 0.6  # 중간 유사도
        
        # 직접 매칭
        for mood in mood_list:
            mood_lower = mood.lower()
            if emotion_lower in mood_lower or mood_lower in emotion_lower:
                return 1.0  # 완전 일치
            elif any(word in mood_lower for word in emotion_lower.split()):
                return 0.7  # 부분 일치
        
        return 0.0  # 유사도 없음
    
    def _calculate_color_similarity(self, requested_color: str, available_colors: List[str]) -> float:
        """색상 유사도 계산"""
        requested_lower = requested_color.lower()
        
        # 색상 유사도 매핑
        color_similarities = {
            "핑크": ["핑크", "연핑크", "라이트핑크", "로즈", "살구색"],
            "레드": ["레드", "빨강", "크림슨", "버건디", "마론"],
            "화이트": ["화이트", "흰색", "아이보리", "크림", "오프화이트"],
            "옐로우": ["옐로우", "노랑", "골드", "크림", "베이지"],
            "블루": ["블루", "파랑", "네이비", "스카이블루", "옅은 블루"],
            "퍼플": ["퍼플", "보라", "라일락", "라벤더", "바이올렛"],
            "오렌지": ["오렌지", "코랄", "살구색", "피치", "어프리콧"],
            "그린": ["그린", "초록", "민트", "세이지", "올리브"]
        }
        
        # 색상 그룹 찾기
        for group, similar_colors in color_similarities.items():
            if requested_lower in group.lower() or any(similar in requested_lower for similar in similar_colors):
                # 해당 그룹의 색상들과 매칭
                for color in available_colors:
                    color_lower = color.lower()
                    if any(similar in color_lower for similar in similar_colors):
                        return 0.9  # 높은 유사도
                    elif any(word in color_lower for word in requested_lower.split()):
                        return 0.7  # 중간 유사도
        
        # 직접 매칭
        for color in available_colors:
            color_lower = color.lower()
            if requested_lower in color_lower or color_lower in requested_lower:
                return 1.0  # 완전 일치
            elif any(word in color_lower for word in requested_lower.split()):
                return 0.8  # 부분 일치
        
        return 0.0  # 유사도 없음
    
    def _calculate_keyword_similarity(self, story: str, keywords: List[str]) -> float:
        """키워드 유사도 계산"""
        if not keywords:
            return 0.0
        
        max_similarity = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 완전 일치
            if keyword_lower in story:
                max_similarity = max(max_similarity, 1.0)
            # 부분 일치
            elif any(word in story for word in keyword_lower.split()):
                max_similarity = max(max_similarity, 0.7)
            # 유사 키워드 매칭
            else:
                # 유사 키워드 매핑
                similar_keywords = {
                    "사랑": ["연인", "고백", "첫사랑", "로맨스", "애정"],
                    "기쁨": ["행복", "즐거움", "웃음", "밝음", "활기"],
                    "위로": ["안정", "편안함", "포근함", "따뜻함", "힐링"],
                    "응원": ["격려", "지지", "힘내", "화이팅", "후원"],
                    "감사": ["고마움", "은인", "축복", "보답", "존경"],
                    "희망": ["미래", "꿈", "새로운", "신뢰", "완벽"],
                    "순수": ["순결", "깨끗함", "자연", "이상", "완벽"],
                    "우정": ["친구", "지지", "동료", "함께", "우정"],
                    "축하": ["생일", "성취", "합격", "기념", "경쾌"],
                    "그리움": ["추억", "과거", "회상", "아련함", "이사"]
                }
                
                for base_keyword, similar_list in similar_keywords.items():
                    if keyword_lower in base_keyword or any(similar in keyword_lower for similar in similar_list):
                        for similar in similar_list:
                            if similar in story:
                                max_similarity = max(max_similarity, 0.6)
                                break
        
        return max_similarity
    
    def _is_wedding_bouquet(self, story: str) -> bool:
        """웨딩 부케 관련 사연인지 확인"""
        wedding_keywords = ["결혼식", "부케", "웨딩", "신부", "드레스", "미니멀", "심플", "포인트 컬러"]
        story_lower = story.lower()
        return any(keyword in story_lower for keyword in wedding_keywords)
    
    def _match_wedding_bouquet(self, emotions: List[EmotionAnalysis], story: str, color_keywords: List[str]) -> FlowerMatch:
        """웨딩 부케 특별 매칭"""
        # 웨딩 부케용 고급 꽃들 (우선순위 순서)
        wedding_flowers = [
            "Garden Peony",  # 작약 - 가장 고급스럽고 우아함
            "Lisianthus",    # 리시안셔스 - 세련되고 고급스러움
            "Rose",          # 장미 - 클래식하고 우아함
            "Lily",          # 백합 - 순수하고 고귀함
            "Hydrangea",     # 수국 - 풍성하고 우아함
            "Scabiosa",      # 스카비오사 - 모던하고 세련됨
            "Bouvardia",     # 부바르디아 - 우아하고 세련됨
            "Tulip",         # 튤립 - 신선하고 우아함
            "Dahlia",        # 다알리아 - 화려하고 현대적
            "Gerbera Daisy"  # 거베라 - 밝고 활기참
        ]
        
        # 포인트 컬러가 있는 경우 비비드한 색상으로 매핑
        if color_keywords:
            for color in color_keywords:
                if "포인트" in color or "컬러" in color:
                    # 포인트 컬러는 비비드한 색상으로 매핑 (화이트 제외)
                    vivid_colors = ["핑크", "레드", "오렌지", "옐로우", "퍼플", "블루"]
                    for vivid_color in vivid_colors:
                        for flower_name in wedding_flowers:
                            flower_data = self.flower_database.get(flower_name)
                            available_colors = flower_data.get("color", [])
                            if vivid_color in available_colors:
                                # 실제 이미지 파일이 있는지 확인
                                image_folder = self._get_flower_folder(flower_name)
                                if self._check_image_exists(image_folder, vivid_color):
                                    print(f"🎨 웨딩 부케 포인트 컬러 매칭: {flower_name} - {vivid_color}")
                                    return self._create_flower_match(flower_name, [vivid_color], story)
        
        # 기본적으로 가장 고급스러운 꽃 선택 (실제 이미지가 있는 색상으로)
        return self._fallback_match(emotions, story)
    
    def _generate_hashtags(self, flower: dict, emotions: List[str] = None, excluded_keywords: List[Dict[str, str]] = None) -> List[str]:
        """해시태그 생성 - 감정 분석 결과를 그대로 사용"""
        hashtags = []
        
        # 1. 꽃 이름
        hashtags.append(f"#{flower['korean_name']}")
        
        # 2. 감정 분석 결과를 그대로 사용 (순서대로 3개)
        if emotions:
            # 제외된 키워드 확인
            excluded_texts = [kw.get('text', '') for kw in excluded_keywords] if excluded_keywords else []
            
            # 감정 분석 결과에서 제외된 키워드 제외하고 순서대로 3개 사용
            for emotion in emotions[:3]:
                if emotion not in excluded_texts:
                    hashtags.append(f"#{emotion}")
        
        # 3. 감정이 부족하면 꽃말로 보충 (최대 1개)
        if len(hashtags) < 4 and emotions:
            flower_meanings = flower.get('flower_meanings', {})
            primary_meanings = flower_meanings.get('primary', [])
            
            if primary_meanings:
                # 첫 번째 꽃말 사용
                hashtag = f"#{primary_meanings[0]}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        return hashtags

    def _extract_contextual_colors(self, story: str) -> List[str]:
        """맥락 기반 색상 추출"""
        context = self._extract_contextual_keywords(story)
        colors = context.get("colors", [])
        
        # 위로/슬픔 상황에서 부적절한 색상 필터링
        filtered_colors = self.comfort_matcher.filter_inappropriate_colors(story, colors)
        
        return filtered_colors
    
    def _fallback_color_extraction(self, story: str) -> List[str]:
        """폴백 색상 추출 로직"""
        story_lower = story.lower()
        
        # 명시적 색상 요청 우선 처리
        explicit_colors = self._extract_explicit_colors(story)
        if explicit_colors:
            return explicit_colors
        
        # 맥락 기반 색상 추천
        contextual_colors = []
        
        # 위로/힐링/편안함 관련 색상
        if any(word in story_lower for word in ["위로", "힐링", "편안", "차분", "가벼운", "한결", "편안하게", "쉬고", "휴식", "편안히", "쉬고 싶어", "편안한", "차분한", "조용한", "평온한"]):
            contextual_colors = ["그린", "화이트", "블루"]
        
        # 희망/기쁨/축하 관련 색상
        elif any(word in story_lower for word in ["희망", "기쁨", "밝", "활기", "경쾌", "축하", "합격", "성취"]):
            contextual_colors = ["노랑", "오렌지", "핑크", "레드"]
        
        # 형형색색/화려한 색상
        elif any(word in story_lower for word in ["형형색색", "화려", "다양한", "컬러풀"]):
            contextual_colors = ["노랑", "오렌지", "핑크", "레드", "퍼플"]
        
        # 사랑/로맨스 관련 색상
        elif any(word in story_lower for word in ["사랑", "로맨스", "고백", "연인"]):
            contextual_colors = ["핑크", "레드", "화이트"]
        
        # 그린톤 소파와 어울리는 색상
        elif "그린" in story_lower or "green" in story_lower:
            contextual_colors = ["그린", "화이트", "크림"]
        
        # 우드톤/내추럴 관련 색상
        elif "우드톤" in story_lower or "내추럴" in story_lower:
            contextual_colors = ["그린", "화이트", "크림", "베이지"]
        
        # 강렬한 포인트 색상
        elif any(word in story_lower for word in ["강렬", "포인트", "대비"]):
            contextual_colors = ["노랑", "오렌지", "빨강"]
        
        # 기본 위로 색상 (아무 조건도 만족하지 않을 때)
        if not contextual_colors:
            contextual_colors = ["크림", "화이트", "연핑크"]
        
        return contextual_colors[:2]  # 최대 2개 색상 추출
    
    def _extract_explicit_colors(self, story: str) -> List[str]:
        """명시적 색상 요청 추출"""
        import re
        color_mapping = {
            "그린": "그린", "green": "그린",
            "옐로우": "옐로우", "yellow": "옐로우", "노랑": "옐로우",
            "핑크": "핑크", "pink": "핑크",
            "화이트": "화이트", "white": "화이트", "흰색": "화이트",
            "블루": "블루", "blue": "블루", "파랑": "블루", "하늘색": "블루",
            "레드": "레드", "red": "레드", "빨강": "레드",
            "퍼플": "퍼플", "purple": "퍼플", "보라": "퍼플",
            "오렌지": "오렌지", "orange": "오렌지",
            # 파스텔톤 컬러들을 DB 컬러로 매핑 (파스텔톤 제외)
            "연핑크": "핑크",
            "연노랑": "옐로우",
            "연초록": "그린",
            "연보라": "퍼플",
            "연빨강": "레드",
            "연주황": "오렌지"
        }

        extracted_colors = []

        # "그린·옐로우" 같은 조합 패턴 찾기
        patterns = [
            r'그린[·\s]*옐로우',
            r'옐로우[·\s]*그린',
            r'green[·\s]*yellow',
            r'yellow[·\s]*green',
            r'그린[·\s]*노랑',
            r'노랑[·\s]*그린'
        ]

        for pattern in patterns:
            if re.search(pattern, story, re.IGNORECASE):
                if "그린" in pattern or "green" in pattern:
                    extracted_colors.append("그린")
                if "옐로우" in pattern or "yellow" in pattern or "노랑" in pattern:
                    extracted_colors.append("옐로우")
                return extracted_colors

        # 개별 색상 키워드 찾기
        for keyword, color in color_mapping.items():
            if keyword in story.lower():
                if color not in extracted_colors:
                    extracted_colors.append(color)

        return extracted_colors[:3]  # 최대 3개
    
    def _generate_emotion_hashtags(self, emotions: List[EmotionAnalysis], excluded_keywords: List[Dict[str, str]] = None) -> List[str]:
        """감정 기반 해시태그 생성 (제외된 키워드 제외)"""
        hashtags = []
        excluded_texts = [kw.get('text', '') for kw in excluded_keywords] if excluded_keywords else []
        
        for emotion in emotions[:3]:  # 상위 3개 감정
            # 제외된 감정이면 해시태그에 포함하지 않음
            if emotion.emotion not in excluded_texts:
                hashtags.append(f"#{emotion.emotion}")
        
        return hashtags

    def _get_flowers_from_api(self) -> List[Dict]:
        """API에서 꽃 사전 데이터 가져오기"""
        try:
            response = requests.get("http://localhost:8002/api/v1/admin/dictionary/flowers", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API 응답 오류: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
            return []
    
    def _get_flower_by_id(self, flowers: List[Dict], flower_id: str) -> Optional[Dict]:
        """ID로 꽃 찾기"""
        return self.flower_database.get(flower_id)
    
    def _get_flower_info(self, flower_name: str) -> Optional[Dict]:
        """꽃 이름으로 정보 찾기"""
        for flower_data in self.flower_database.values():
            if flower_data['korean_name'] == flower_name:
                return flower_data
        return None
    
    def _is_flower_in_database(self, flower_name: str) -> bool:
        """꽃이 데이터베이스에 있는지 확인"""
        return self._get_flower_info(flower_name) is not None
    
    def _calculate_flower_scores_with_api_data(self, emotions: List[EmotionAnalysis], story: str, all_flowers: List[Dict], color_keywords: List[str]) -> Dict[str, float]:
        """API 데이터를 사용한 점수 계산"""
        scores = {}
        
        for flower in all_flowers:
            flower_id = flower.get('id', '')
            if not flower_id:
                continue
                
            score = 0.0
            
            # 1. 감정 매칭 점수
            flower_moods = flower.get('moods', {})
            # moods는 딕셔너리 형태이므로 모든 값들을 평면화
            all_moods = []
            for mood_list in flower_moods.values():
                if isinstance(mood_list, list):
                    all_moods.extend(mood_list)
            
            for emotion in emotions:
                if emotion.emotion in all_moods:
                    score += emotion.percentage * 0.01
                    print(f"💭 감정 매칭: {flower['korean_name']} - {emotion.emotion} (+{emotion.percentage * 0.01:.2f})")
            
            # 2. 색상 매칭 점수 (우선순위 높임)
            flower_colors = flower.get('color', [])
            if isinstance(flower_colors, str):
                flower_colors = [flower_colors]
            
            for color in color_keywords:
                if color in flower_colors:
                    score += 3.0  # 색상 매칭 점수를 1.0에서 3.0으로 더욱 높임
                    print(f"🎨 색상 매칭: {flower['korean_name']} - {color} (+3.0)")
                else:
                    score -= 1.0  # 색상 불일치 시 페널티
                    print(f"❌ 색상 불일치: {flower['korean_name']} - 요청: {color}, 실제: {flower_colors} (-1.0)")
            
            # 3. 관계 적합성 점수
            relationship_suitability = flower.get('relationship_suitability', {})
            story_lower = story.lower()
            for relationship, keywords in relationship_suitability.items():
                if isinstance(keywords, list) and any(keyword in story_lower for keyword in keywords):
                    score += 0.4
                    print(f"💕 관계 매칭: {flower['korean_name']} - {relationship} (+0.4)")
            
            # 4. 사용 맥락 점수
            usage_contexts = flower.get('usage_contexts', [])
            for context in usage_contexts:
                if context.lower() in story_lower:
                    score += 0.3
                    print(f"📝 맥락 매칭: {flower['korean_name']} - {context} (+0.3)")
            
            # 5. 계절 이벤트 점수
            seasonal_events = flower.get('seasonal_events', [])
            for event in seasonal_events:
                if event.lower() in story_lower:
                    score += 0.2
                    print(f"🌱 계절 매칭: {flower['korean_name']} - {event} (+0.2)")
            
            # 6. 특별 키워드 매칭
            flower_meanings = flower.get('flower_meanings', {})
            primary_meanings = flower_meanings.get('primary', [])
            for meaning in primary_meanings:
                if meaning.lower() in story_lower:
                    score += 0.2
                    print(f"💐 꽃말 매칭: {flower['korean_name']} - {meaning} (+0.2)")
            
            # 7. 리시안셔스 점수 조정 (다양성 확보)
            if flower['korean_name'] == '리시안서스':
                score *= 0.7
                print(f"🔽 리시안서스 점수 조정: {score:.2f}")
            
            # 8. 옐로우 톤 꽃 우선순위 (밝은 기분을 위한)
            if any(keyword in story.lower() for keyword in ["흐린 날씨", "흐려서", "기분이 처져요", "처져", "우울", "침침한", "밝아질", "밝게", "활기", "기운"]):
                if flower_data.get('color') in ['옐로우', '노랑', '골드']:
                    score *= 1.5
                    print(f"☀️ 옐로우 톤 우선순위: {flower_data['korean_name']} (점수: {score:.2f})")
            
            # 9. 부정적 감정 해결 꽃 우선순위
            negative_emotions = ["우울", "스트레스", "외로움", "불안", "슬픔", "걱정"]
            if any(emotion in str(emotions) for emotion in negative_emotions):
                # 부정적 감정을 해결하는 꽃말을 가진 꽃들 우선순위
                flower_meanings = flower_data.get('flower_meanings', {})
                all_meanings = []
                all_meanings.extend(flower_meanings.get('primary', []))
                all_meanings.extend(flower_meanings.get('secondary', []))
                all_meanings.extend(flower_meanings.get('other', []))
                
                healing_keywords = ["희망", "기쁨", "행복", "활기", "위로", "따뜻함", "사랑", "기운"]
                if any(keyword in str(all_meanings) for keyword in healing_keywords):
                    score *= 1.3
                    print(f"💚 부정적 감정 해결 꽃: {flower_data['korean_name']} (점수: {score:.2f})")
            
            # 3. 색상 유사도 점수
            if color_keywords:
                flower_color = flower_data.get('color', '')
                color_similarity = self._calculate_color_similarity(color_keywords[0], [flower_color])
                score += color_similarity * 0.3
                if color_similarity > 0.3:
                    print(f"🎨 색상 유사도 매칭: {flower_data['korean_name']} - {color_keywords[0]} (유사도: {color_similarity:.2f}, +{color_similarity * 0.3:.2f})")
            
            # 색상 우선순위 조정 (요청된 색상과 정확히 일치하는 경우 높은 점수)
            if color_keywords and flower_data.get('color', '') in color_keywords:
                score *= 2.0  # 색상 일치 시 점수 2배
                print(f"🎯 색상 정확 매칭: {flower_data['korean_name']} - {flower_data.get('color', '')} (점수: {score:.2f})")
            elif color_keywords and flower_data.get('color', '') not in color_keywords:
                score *= 0.3  # 색상 불일치 시 점수 대폭 감소
                print(f"❌ 색상 불일치: {flower_data['korean_name']} - 요청: {color_keywords[0]}, 실제: {flower_data.get('color', '')} (점수: {score:.2f})")
            
            scores[flower_id] = score
        
        print(f"📊 꽃 점수 요약: {len(scores)}개 꽃 중 상위 5개")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for flower_id, score in sorted_scores:
            flower = self._get_flower_by_id(all_flowers, flower_id)
            if flower:
                print(f"  {flower['korean_name']}: {score:.2f}")
        
        return scores
    
    def _get_default_color(self, flower_name: str) -> str:
        """꽃의 기본 색상 반환"""
        flower_data = self._get_flower_info(flower_name)
        if flower_data:
            return flower_data.get('color', '화이트')
        return '화이트'

    def _extract_contextual_keywords(self, story: str) -> Dict[str, List[str]]:
        """맥락 기반 키워드 추출 (의도, 상황, 감정, 관계, 분위기, 색상)"""
        try:
            # LLM을 통한 맥락 분석
            context = self._analyze_story_context_with_llm(story)
            return context
        except Exception as e:
            print(f"❌ LLM 맥락 분석 실패: {e}")
            # 폴백: 규칙 기반 맥락 분석
            return self._fallback_contextual_analysis(story)
    
    def _analyze_story_context_with_llm(self, story: str) -> Dict[str, List[str]]:
        """LLM을 통한 맥락 분석"""
        prompt = f"""
다음 이야기를 분석하여 맥락적 키워드를 추출해주세요.

**이야기**: {story}

**분석 요구사항**:
1. **의도**: 꽃을 주는 목적 (축하, 위로, 사랑 표현, 감사 등)
2. **상황**: 어떤 상황에서 꽃을 주는지 (생일, 졸업, 병문안, 고백 등)
3. **보내는 사람 감정**: 꽃을 주는 사람의 감정 상태
4. **받는 사람 감정**: 꽃을 받는 사람의 예상 감정
5. **관계**: 두 사람의 관계 (연인, 부모자식, 친구, 동료 등)
6. **선호 분위기**: 원하는 분위기 (로맨틱, 우아, 활기찬, 차분한 등)
7. **색상**: 적합한 색상 (명시적 요청이 있으면 우선, 없으면 맥락 기반 추천)

**특별 주의사항**:
- **슬픔/위로 맥락**: 반려동물이나 사람의 죽음, 이별 등 슬픈 상황에서는 차분하고 위로가 되는 색상 추천
  - 블루톤: 차분함, 평온함, 위로
  - 화이트톤: 순수함, 평화, 새로운 시작
  - 라벤더톤: 평온함, 치유, 인연
- **색상 추출 규칙**:
  - "무지개"라는 단어가 있어도 무지개색상 추출 금지
  - 슬픈 상황에서는 블루, 화이트, 라벤더, 퍼플 등 차분한 색상만 추출
  - 화려한 색상(레드, 오렌지, 핑크, 옐로우)은 축하/기쁨 상황에서만 추출
- **상황 요약 규칙**:
  - 긴 문장 그대로 사용 금지
  - 핵심 상황만 단어로 요약 (예: "반려견이 무지개다리를 건넌" → "반려동물 상실")
  - 대상도 간결하게 요약 (예: "지인에게" → "지인")
- **부적절한 표현 변환**: "무지개다리를 건넌" → "별이 된", "돌아가신" → "떠나신"
- 맥락을 고려하여 의미있는 키워드 추출
- 각 카테고리별로 1-3개 키워드 추출

JSON 형식으로 응답:
{{
    "intent": ["의도1", "의도2"],
    "situation": ["상황1", "상황2"],
    "sender_emotion": ["감정1", "감정2"],
    "receiver_emotion": ["감정1", "감정2"],
    "relationship": ["관계1", "관계2"],
    "mood": ["분위기1", "분위기2"],
    "colors": ["색상1", "색상2"]
}}
"""

        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # JSON 파싱
            import json
            import re
            
            # JSON 부분만 추출
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                context_data = json.loads(json_match.group())
                return context_data
            else:
                raise Exception("JSON 파싱 실패")
                
        except Exception as e:
            print(f"❌ LLM 응답 파싱 실패: {e}")
            raise e
    
    def _fallback_contextual_analysis(self, story: str) -> Dict[str, List[str]]:
        """폴백: 규칙 기반 맥락 분석"""
        story_lower = story.lower()
        
        context = {
            "intent": [],
            "situation": [],
            "sender_emotion": [],
            "receiver_emotion": [],
            "relationship": [],
            "mood": [],
            "colors": []
        }
        
        # 의도 분석
        if any(word in story_lower for word in ["축하", "합격", "성취", "기념"]):
            context["intent"].append("축하")
        elif any(word in story_lower for word in ["위로", "힐링", "편안", "차분"]):
            context["intent"].append("위로")
        elif any(word in story_lower for word in ["사랑", "고백", "로맨스"]):
            context["intent"].append("사랑표현")
        elif any(word in story_lower for word in ["감사", "고마움", "존경"]):
            context["intent"].append("감사")
        
        # 상황 분석
        if any(word in story_lower for word in ["생일", "기념일"]):
            context["situation"].append("생일")
        elif any(word in story_lower for word in ["졸업", "합격", "취업"]):
            context["situation"].append("성취")
        elif any(word in story_lower for word in ["병문안", "회복", "건강"]):
            context["situation"].append("건강")
        elif any(word in story_lower for word in ["고백", "프로포즈"]):
            context["situation"].append("로맨스")
        
        # 관계 분석
        if any(word in story_lower for word in ["연인", "남자친구", "여자친구", "애인"]):
            context["relationship"].append("연인")
        elif any(word in story_lower for word in ["부모님", "어머니", "아버지"]):
            context["relationship"].append("부모자식")
        elif any(word in story_lower for word in ["친구", "동료", "지인"]):
            context["relationship"].append("친구")
        
        # 분위기 분석
        if any(word in story_lower for word in ["로맨틱", "사랑스러운"]):
            context["mood"].append("로맨틱")
        elif any(word in story_lower for word in ["우아", "고급스러운"]):
            context["mood"].append("우아")
        elif any(word in story_lower for word in ["활기", "밝은"]):
            context["mood"].append("활기찬")
        elif any(word in story_lower for word in ["차분", "편안한"]):
            context["mood"].append("차분한")
        
        # 색상 분석 (기존 로직 활용)
        context["colors"] = self._fallback_color_extraction(story)
        
        return context
    
    def _extract_mood_keywords(self, story: str) -> List[str]:
        """스토리에서 무드 키워드 추출 (맥락 기반)"""
        context = self._extract_contextual_keywords(story)
        return context.get("mood", [])
    
    def _apply_comfort_situation_bonus(self, flower_data: Dict, story: str, score: float) -> float:
        """위로/슬픔 상황 특별 보너스 적용"""
        comfort_keywords = ["무지개다리를 건넌", "돌아가신", "별이 된", "위로", "슬픔", "이별", "반려견", "반려동물"]
        
        if any(keyword in story.lower() for keyword in comfort_keywords):
            # 위로 관련 꽃말을 가진 꽃들에 높은 가중치
            flower_meanings = flower_data.get('flower_meanings', {})
            all_meanings = []
            all_meanings.extend(flower_meanings.get('primary', []))
            all_meanings.extend(flower_meanings.get('secondary', []))
            all_meanings.extend(flower_meanings.get('other', []))
            
            comfort_flower_keywords = ["희망", "위로", "치유", "평화", "인연", "새로운 시작", "평온", "차분"]
            if any(keyword in str(all_meanings) for keyword in comfort_flower_keywords):
                score *= 2.0
                print(f"🕊️ 위로 꽃 우선순위: {flower_data['korean_name']} (점수: {score:.2f})")
            
            # 블루톤, 화이트톤 꽃에 가중치
            flower_color = flower_data.get('color', '')
            comfort_colors = ["블루", "화이트", "라벤더", "퍼플", "아이보리"]
            if flower_color in comfort_colors:
                score *= 1.8
                print(f"💙 위로 색상 우선순위: {flower_data['korean_name']} - {flower_color} (점수: {score:.2f})")
            
            # 화려한 색상 꽃에 페널티 (무지개색상 등)
            bright_colors = ["레드", "오렌지", "핑크", "옐로우"]
            if flower_color in bright_colors:
                score *= 0.3
                print(f"❌ 화려한 색상 페널티: {flower_data['korean_name']} - {flower_color} (점수: {score:.2f})")
        
        return score
