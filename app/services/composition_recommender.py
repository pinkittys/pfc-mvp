from typing import List
from app.models.schemas import EmotionAnalysis, FlowerMatch, FlowerComposition
import random

class CompositionRecommender:
    def __init__(self):
        self.compositions = {
            "Shine Your Light": {
                "sub_flowers": ["라벤더", "실버리프"],
                "description": "희망과 따뜻함을 담은 구성"
            },
            "Pure Love": {
                "sub_flowers": ["베이비 브레스", "핑크 로즈"],
                "description": "순수한 사랑을 담은 구성"
            },
            "Spring Joy": {
                "sub_flowers": ["튤립", "데이지"],
                "description": "봄의 기쁨을 담은 구성"
            },
            "Elegant Grace": {
                "sub_flowers": ["백합", "오키드"],
                "description": "고귀한 우아함을 담은 구성"
            },
            "Celebration": {
                "sub_flowers": ["스톡", "베이비 브레스"],
                "description": "축하와 기쁨을 담은 구성"
            },
            "Fresh Welcome": {
                "sub_flowers": ["화이트 베이비 브레스", "그린 유칼립투스"],
                "description": "싱그러운 환영을 담은 구성"
            },
            "Green Yellow Harmony": {
                "sub_flowers": ["그린 유칼립투스", "옐로우 데이지"],
                "description": "그린·옐로우 조화를 담은 구성"
            },
            "Gentle Comfort": {
                "sub_flowers": ["화이트 베이비 브레스", "크림 로즈"],
                "description": "차분하고 위로가 되는 구성"
            },
            "Colorful Celebration": {
                "sub_flowers": ["오렌지 거베라", "핑크 데이지"],
                "description": "화려하고 축하 분위기의 구성"
            },
            "Elegant Simplicity": {
                "sub_flowers": ["화이트 베이비 브레스", "그린 유칼립투스"],
                "description": "우아하고 심플한 구성"
            },
            "Wedding Elegance": {
                "sub_flowers": ["화이트 베이비 브레스", "크림 로즈"],
                "description": "웨딩에 어울리는 우아한 구성"
            },
            "Minimal Elegance": {
                "sub_flowers": ["화이트 베이비 브레스"],
                "description": "미니멀하고 우아한 구성"
            },
            "Vivid Simplicity": {
                "sub_flowers": ["화이트 베이비 브레스", "그린 유칼립투스"],
                "description": "강렬한 꽃과 소재의 심플한 조화"
            }
        }
    
    def recommend(self, matched_flower: FlowerMatch, emotions: List[EmotionAnalysis]) -> FlowerComposition:
        """매칭된 꽃과 감정을 기반으로 구성 추천"""
        # 감정에 따른 구성 선택
        primary_emotion = emotions[0].emotion if emotions else "따뜻함"
        
        # 웨딩 부케 특별 처리
        if self._is_wedding_bouquet_request(matched_flower):
            return self._recommend_wedding_bouquet_composition(matched_flower, emotions)
        
        # 심플한 무드 요청 체크
        if self._is_simple_mood_request(emotions):
            return self._recommend_simple_composition(matched_flower, emotions)
        
        # 디자인 중심 사연인 경우
        if primary_emotion == "디자인":
            return self._recommend_design_composition(matched_flower, emotions)
        
        # 색상 기반 구성 선택 (그린·옐로우 요청이 있는 경우)
        if self._has_green_yellow_request(matched_flower):
            return FlowerComposition(
                main_flower=matched_flower.flower_name,
                sub_flowers=["그린 유칼립투스", "옐로우 데이지"],
                composition_name="Green Yellow Harmony"
            )
        
        # 강렬한 꽃들은 소재와만 블렌딩 (Cockscomb, Dahlia, Gerbera Daisy)
        if matched_flower.flower_name in ["Cockscomb", "Dahlia", "Gerbera Daisy"]:
            return FlowerComposition(
                main_flower=matched_flower.flower_name,
                sub_flowers=["화이트 베이비 브레스", "그린 유칼립투스"],
                composition_name="Vivid Simplicity"
            )
        
        # 위로/애도 관련 사연 체크
        if self._is_comfort_needed(matched_flower):
            return FlowerComposition(
                main_flower=matched_flower.flower_name,
                sub_flowers=["화이트 베이비 브레스", "크림 로즈"],
                composition_name="Gentle Comfort"
            )
        
        composition_mapping = {
            "그리움": "Shine Your Light",
            "따뜻함": "Shine Your Light", 
            "애뜻함": "Pure Love",
            "기쁨": "Celebration",
            "기쁨/축하": "Celebration",
            "축하": "Colorful Celebration",  # 수정
            "환영": "Fresh Welcome",
            "감사": "Elegant Grace",
            "감사/존경": "Elegant Grace",
            "응원": "Spring Joy",
            "위로": "Gentle Comfort",  # 추가
            "슬픔": "Gentle Comfort",  # 추가
            "애도": "Gentle Comfort"   # 추가
        }
        
        composition_name = composition_mapping.get(primary_emotion, "Shine Your Light")
        composition_data = self.compositions[composition_name]
        
        return FlowerComposition(
            main_flower=matched_flower.flower_name,
            sub_flowers=composition_data["sub_flowers"],
            composition_name=composition_name
        )
    
    def _recommend_design_composition(self, matched_flower: FlowerMatch, emotions: List[EmotionAnalysis]) -> FlowerComposition:
        """디자인 중심 사연에 대한 구성 추천"""
        flower_name = matched_flower.flower_name
        
        # 꽃별 맞춤 구성
        design_compositions = {
            "Garden Peony": {
                "name": "Green Harmony",
                "sub_flowers": ["화이트 데이지", "그린 유칼립투스"],
                "description": "그린톤과 조화로운 구성"
            },
            "Gerbera Daisy": {
                "name": "Modern Contrast",
                "sub_flowers": ["블루 델피니움", "실버리프"],
                "description": "현대적인 대비 구성"
            },
            "Rose": {
                "name": "Classic Elegance",
                "sub_flowers": ["화이트 백합", "그린 몬스테라"],
                "description": "클래식한 우아함 구성"
            },
            "Lily": {
                "name": "Minimal Grace",
                "sub_flowers": ["화이트 베이비 브레스", "그린 아스파라거스"],
                "description": "미니멀한 우아함 구성"
            },
            "Lisianthus": {
                "name": "Fresh Welcome",
                "sub_flowers": ["화이트 베이비 브레스", "그린 유칼립투스"],
                "description": "싱그러운 환영 구성"
            },
            "Dahlia": {
                "name": "Bold Statement",
                "sub_flowers": ["오렌지 거베라", "그린 유칼립투스"],
                "description": "강렬한 포인트 구성"
            },
            "Tulip": {
                "name": "Fresh Spring",
                "sub_flowers": ["핑크 데이지", "그린 몬스테라"],
                "description": "신선한 봄 구성"
            }
        }
        
        composition = design_compositions.get(flower_name, design_compositions["Garden Peony"])
        
        return FlowerComposition(
            main_flower=matched_flower.flower_name,
            sub_flowers=composition["sub_flowers"],
            composition_name=composition["name"]
        )

    def _has_green_yellow_request(self, matched_flower: FlowerMatch) -> bool:
        """그린·옐로우 요청이 있는지 확인"""
        # 꽃 매칭에서 그린·옐로우 계열이 선택되었는지 확인
        green_yellow_flowers = ["Gerbera Daisy", "Tulip", "Dahlia"]
        return matched_flower.flower_name in green_yellow_flowers
    
    def _is_colorful_request(self, matched_flower: FlowerMatch) -> bool:
        """형형색색/화려한 요청이 있는지 확인"""
        # 화려한 꽃들이 선택되었는지 확인
        colorful_flowers = ["Dahlia", "Gerbera Daisy"]
        return matched_flower.flower_name in colorful_flowers
    
    def _is_wedding_bouquet_request(self, matched_flower: FlowerMatch) -> bool:
        """웨딩 부케 요청인지 확인"""
        # 웨딩 부케에 적합한 고급 꽃들
        wedding_flowers = ["Garden Peony", "Lisianthus", "Rose", "Lily", "Hydrangea", "Scabiosa", "Bouvardia"]
        return matched_flower.flower_name in wedding_flowers
    
    def _is_simple_mood_request(self, emotions: List[EmotionAnalysis]) -> bool:
        """심플한 무드 요청인지 확인"""
        simple_keywords = ["심플", "미니멀", "간단", "차분", "조용"]
        for emotion in emotions:
            if any(keyword in emotion.emotion for keyword in simple_keywords):
                return True
        return False
    
    def _recommend_wedding_bouquet_composition(self, matched_flower: FlowerMatch, emotions: List[EmotionAnalysis]) -> FlowerComposition:
        """웨딩 부케 특별 구성 추천"""
        # 포인트 컬러의 큰 꽃이 메인일 때는 작은 소재들로 심플하게
        large_flowers = ["Garden Peony", "Hydrangea", "Dahlia"]
        
        if matched_flower.flower_name in large_flowers:
            # 큰 꽃은 작은 소재들로 심플하게
            return FlowerComposition(
                main_flower=matched_flower.flower_name,
                sub_flowers=["화이트 베이비 브레스", "그린 유칼립투스"],
                composition_name="Elegant Simplicity"
            )
        else:
            # 중간 크기 꽃은 적당한 소재와 조화
            return FlowerComposition(
                main_flower=matched_flower.flower_name,
                sub_flowers=["화이트 베이비 브레스", "크림 로즈"],
                composition_name="Wedding Elegance"
            )
    
    def _recommend_simple_composition(self, matched_flower: FlowerMatch, emotions: List[EmotionAnalysis]) -> FlowerComposition:
        """심플한 무드 구성 추천"""
        # 심플한 무드는 최소한의 소재로 구성
        return FlowerComposition(
            main_flower=matched_flower.flower_name,
            sub_flowers=["화이트 베이비 브레스"],
            composition_name="Minimal Elegance"
        )
    
    def _is_comfort_needed(self, matched_flower: FlowerMatch) -> bool:
        """위로가 필요한 상황인지 확인"""
        # 백합은 위로와 차분함에 적합한 꽃
        comfort_flowers = ["Lily", "백합"]
        return matched_flower.flower_name in comfort_flowers or matched_flower.korean_name in comfort_flowers
