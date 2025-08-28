from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from app.models.schemas import FlowerMatch, EmotionAnalysis, FlowerComposition
from app.services.flower_matcher import FlowerMatcher
from app.services.composition_recommender import CompositionRecommender
from app.api.v1.endpoints.recommend import _generate_unified_recommendation_reason, _generate_flower_card_message

router = APIRouter()

# 샘플 사연 데이터 로드
def load_sample_stories():
    """샘플 사연 데이터를 로드합니다."""
    try:
        with open("data/sample_stories.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("sample_stories", [])
    except Exception as e:
        print(f"❌ 샘플 사연 데이터 로드 실패: {e}")
        return []

@router.get("/sample-stories")
async def get_sample_stories():
    """샘플 사연 목록을 반환합니다."""
    stories = load_sample_stories()
    return {
        "stories": stories,
        "total_count": len(stories)
    }

@router.get("/sample-stories/{story_id}")
async def get_sample_story(story_id: str):
    """특정 샘플 사연을 반환합니다."""
    stories = load_sample_stories()
    story = next((s for s in stories if s["id"] == story_id), None)
    
    if not story:
        raise HTTPException(status_code=404, detail="사연을 찾을 수 없습니다.")
    
    return story

@router.post("/sample-stories/{story_id}/recommend")
async def recommend_from_sample_story(story_id: str):
    """샘플 사연의 미리 설정된 키워드로 꽃을 추천합니다."""
    try:
        # 샘플 사연 로드
        stories = load_sample_stories()
        story = next((s for s in stories if s["id"] == story_id), None)
        
        if not story:
            raise HTTPException(status_code=404, detail="사연을 찾을 수 없습니다.")
        
        # 미리 설정된 키워드 추출
        predefined_keywords = story["predefined_keywords"]
        
        # EmotionAnalysis 객체 생성
        emotions = []
        if predefined_keywords.get("emotions"):
            for emotion in predefined_keywords["emotions"]:
                emotions.append(EmotionAnalysis(
                    emotion=emotion,
                    percentage=50.0,  # 기본값
                    description=f"{emotion}한 마음"
                ))
        else:
            # 기본 감정 설정
            emotions.append(EmotionAnalysis(
                emotion="기쁨",
                percentage=50.0,
                description="기쁜 마음"
            ))
        
        # 샘플 스토리별 미리 정의된 꽃 매칭 (40가지 다양한 꽃으로 분산)
        predefined_flower_mapping = {
            # 기념일·축하 (10개) - 다양한 꽃들
            "story_001": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "레드", "keywords": ["존경", "충성"]},
            "story_002": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "핑크", "keywords": ["기쁨", "사랑"]},
            "story_003": {"korean_name": "거베라", "scientific_name": "Gerbera Daisy", "color": "레드", "keywords": ["기쁨", "축하"]},
            "story_004": {"korean_name": "해바라기", "scientific_name": "Sunflower", "color": "옐로우", "keywords": ["감사", "존경"]},
            "story_005": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "핑크", "keywords": ["기쁨", "사랑"]},
            "story_006": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "핑크", "keywords": ["축하", "응원"]},
            "story_007": {"korean_name": "장미", "scientific_name": "Rose", "color": "레드", "keywords": ["축하", "성취"]},
            "story_008": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "핑크", "keywords": ["기쁨", "축하"]},
            "story_009": {"korean_name": "튤립", "scientific_name": "Tulip", "color": "레드", "keywords": ["축하", "성취"]},
            "story_010": {"korean_name": "카네이션", "scientific_name": "Carnation", "color": "레드", "keywords": ["축하", "응원"]},
            
            # 사랑·고백·감사 (10개) - 로맨틱한 꽃들
            "story_011": {"korean_name": "장미", "scientific_name": "Rose", "color": "핑크", "keywords": ["사랑", "감사"]},
            "story_012": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "레드", "keywords": ["사랑", "고백"]},
            "story_013": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "핑크", "keywords": ["사랑", "감사"]},
            "story_014": {"korean_name": "스위트피", "scientific_name": "Sweet Pea", "color": "핑크", "keywords": ["사랑", "고백"]},
            "story_015": {"korean_name": "리시안서스", "scientific_name": "Lisianthus", "color": "핑크", "keywords": ["사랑", "감사"]},
            "story_016": {"korean_name": "장미", "scientific_name": "Rose", "color": "레드", "keywords": ["사랑", "고백"]},
            "story_017": {"korean_name": "카네이션", "scientific_name": "Carnation", "color": "핑크", "keywords": ["사랑", "감사"]},
            "story_018": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "레드", "keywords": ["사랑", "고백"]},
            "story_019": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "핑크", "keywords": ["사랑", "감사"]},
            "story_020": {"korean_name": "스위트피", "scientific_name": "Sweet Pea", "color": "핑크", "keywords": ["사랑", "고백"]},
            
            # 위로·응원·격려 (10개) - 따뜻한 꽃들
            "story_021": {"korean_name": "부바르디아", "scientific_name": "Bouvardia", "color": "화이트", "keywords": ["위로", "응원"]},
            "story_022": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "핑크", "keywords": ["위로", "희망"]},
            "story_023": {"korean_name": "아스틸베", "scientific_name": "Astilbe Japonica", "color": "핑크", "keywords": ["위로", "응원"]},
            "story_024": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "레드", "keywords": ["위로", "격려"]},
            "story_025": {"korean_name": "리시안서스", "scientific_name": "Lisianthus", "color": "핑크", "keywords": ["위로", "응원"]},
            "story_026": {"korean_name": "부바르디아", "scientific_name": "Bouvardia", "color": "화이트", "keywords": ["위로", "희망"]},
            "story_027": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "핑크", "keywords": ["위로", "응원"]},
            "story_028": {"korean_name": "히드란지아", "scientific_name": "Hydrangea", "color": "핑크", "keywords": ["위로", "격려"]},
            "story_029": {"korean_name": "아스틸베", "scientific_name": "Astilbe Japonica", "color": "핑크", "keywords": ["위로", "응원"]},
            "story_030": {"korean_name": "리시안서스", "scientific_name": "Lisianthus", "color": "핑크", "keywords": ["위로", "희망"]},
            
            # 비즈니스·격식 (6개) - 격식있는 꽃들
            "story_031": {"korean_name": "부바르디아", "scientific_name": "Bouvardia", "color": "화이트", "keywords": ["비즈니스", "격식"]},
            "story_032": {"korean_name": "리시안서스", "scientific_name": "Lisianthus", "color": "화이트", "keywords": ["비즈니스", "격식"]},
            "story_033": {"korean_name": "알스트로메리아", "scientific_name": "Alstroemeria Spp", "color": "화이트", "keywords": ["비즈니스", "격식"]},
            "story_034": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "핑크", "keywords": ["비즈니스", "격식"]},
            "story_035": {"korean_name": "카네이션", "scientific_name": "Carnation", "color": "핑크", "keywords": ["비즈니스", "격식"]},
            "story_036": {"korean_name": "부바르디아", "scientific_name": "Bouvardia", "color": "화이트", "keywords": ["비즈니스", "격식"]},
            
            # 일상·자기보상 (4개) - 밝은 꽃들
            "story_037": {"korean_name": "프리지아", "scientific_name": "Freesia Refracta", "color": "옐로우", "keywords": ["일상", "자기보상"]},
            "story_038": {"korean_name": "거베라", "scientific_name": "Gerbera Daisy", "color": "옐로우", "keywords": ["일상", "자기보상"]},
            "story_039": {"korean_name": "튤립", "scientific_name": "Tulip", "color": "핑크", "keywords": ["일상", "자기보상"]},
            "story_040": {"korean_name": "백일홍", "scientific_name": "Zinnia Elegans", "color": "레드", "keywords": ["일상", "자기보상"]}
        }
        
        # 미리 정의된 꽃 정보 가져오기
        predefined_flower = predefined_flower_mapping.get(story_id)
        if not predefined_flower:
            raise HTTPException(status_code=404, detail="샘플 스토리를 찾을 수 없습니다.")
        
        # FlowerMatch 객체 생성 (이미지 URL 포함)
        from app.models.schemas import FlowerMatch
        
        # 이미지 URL 생성
        flower_matcher = FlowerMatcher()
        image_url = flower_matcher._get_flower_image_url(
            {
                'korean_name': predefined_flower['korean_name'],
                'scientific_name': predefined_flower['scientific_name']
            },
            [predefined_flower['color']]
        )
        
        matched_flower = FlowerMatch(
            flower_name=predefined_flower['scientific_name'],
            korean_name=predefined_flower['korean_name'],
            scientific_name=predefined_flower['scientific_name'],
            image_url=image_url,
            keywords=predefined_flower['keywords'],
            hashtags=[f"#{predefined_flower['korean_name']}", f"#{predefined_flower['keywords'][0]}", f"#{predefined_flower['keywords'][1]}"],
            color_keywords=[predefined_flower['color']],
            excluded_keywords=[]
        )
        
        # 꽃 조합 추천
        composition_recommender = CompositionRecommender()
        composition = composition_recommender.recommend(
            matched_flower=matched_flower,
            emotions=emotions
        )
        
        # 미리 정의된 추천 이유와 꽃 카드 메시지 (GPT 호출 없이 빠른 응답)
        predefined_reasons = {
            # 1-10번 스토리 (GPT로 생성된 고품질 콘텐츠)
            "story_001": "백일홍의 존경, 충성의 의미를 담아 아빠가 정년퇴직을 하셨어에 어울리는 꽃을 선택했습니다.",
            "story_002": "알스트로메리아의 기쁨, 사랑의 의미를 담아 언니가 드디어 박사 학위를 받았어에 어울리는 꽃을 선택했습니다.",
            "story_003": "거베라의 기쁨, 축하의 의미를 담아 오랜만에 만난 동호회 친구의 생일 파티에 초대받았어에 어울리는 꽃을 선택했습니다.",
            "story_004": "해바라기의 감사, 존경의 의미를 담아 고등학교 담임 선생님 환갑을 맞으셨어에 어울리는 꽃을 선택했습니다.",
            "story_005": "백일홍의 기쁨, 사랑의 의미를 담아 첫 조카의 돌잔치라, 아기와 잘 어울리는 파스텔톤의 귀여운 꽃을 원해에 어울리는 꽃을 선택했습니다.",
            "story_006": "알스트로메리아의 축하, 응원의 의미를 담아 사무실 후배가 드디어 대리로 승진했어에 어울리는 꽃을 선택했습니다.",
            "story_007": "장미의 축하, 성취의 의미를 담아 아내가 마라톤 완주 메달을 땄어에 어울리는 꽃을 선택했습니다.",
            "story_008": "백일홍의 기쁨, 축하의 의미를 담아 친구 부부가 쌍둥이를 출산했어에 어울리는 꽃을 선택했습니다.",
            "story_009": "튤립의 축하, 성취의 의미를 담아 엄마의 요리 교실이 1주년을 맞았어에 어울리는 꽃을 선택했습니다.",
            "story_010": "카네이션의 축하, 응원의 의미를 담아 직장 상사가 해외 지사로 발령 났어에 어울리는 꽃을 선택했습니다.",
            # 11-20번 스토리 (자연스러운 고품질 콘텐츠)
            "story_011": "옛 연인에게 따뜻한 마음을 전하며, 그리웠던 시간을 아름답게 기념해요.",
            "story_012": "아내의 고생을 위로하며, 사랑과 감사의 마음을 담아 드려요.",
            "story_013": "오래된 친구에게 감사의 마음을 전하며, 소중한 우정을 기념해요.",
            "story_014": "여자친구에게 순수한 고백을 하며, 설레는 마음을 담아 드려요.",
            "story_015": "딸의 졸업을 축하하며, 자랑스럽고 감사한 마음을 전해요.",
            "story_016": "아내와의 첫 만남 20주년을 기념하며, 오랜 사랑을 아름답게 표현해요.",
            "story_017": "아이의 마음을 담아 가족에게 사랑을 전하며, 소박하지만 진심 어린 선물을 준비해요.",
            "story_018": "동생 부부의 신혼여행 환영을 위해 따뜻한 마음을 담아 드려요.",
            "story_019": "할머니께 감사의 마음을 전하며, 오랜 세월 보살펴주신 은혜에 감사해요.",
            "story_020": "남편에게 든든함에 대한 감사를 전하며, 평소 표현하지 못한 마음을 담아요.",
            # 21-30번 스토리 (자연스러운 고품질 콘텐츠)
            "story_021": "친구의 시험 실패를 위로하며, 다시 도전할 수 있는 힘을 전해요.",
            "story_022": "동생의 취업 실패를 위로하며, 새로운 기회를 응원해요.",
            "story_023": "친구의 이별을 위로하며, 시간이 치유해줄 거라고 믿어요.",
            "story_024": "동료의 프로젝트 실패를 위로하며, 함께 극복해나갈 거예요.",
            "story_025": "친구의 건강 문제를 걱정하며, 빠른 회복을 기원해요.",
            "story_026": "가족의 어려움을 함께하며, 서로 의지할 수 있는 힘을 전해요.",
            "story_027": "친구의 슬픔을 나누며, 함께 울어줄 수 있는 마음을 담아요.",
            "story_028": "동료의 스트레스를 이해하며, 잠시 쉬어갈 수 있는 시간을 만들어요.",
            "story_029": "친구의 고민을 들어주며, 해결책을 함께 찾아나갈 거예요.",
            "story_030": "가족의 외로움을 달래며, 항상 곁에 있다는 마음을 전해요.",
            "story_031": "비즈니스 파트너에게 격식 있는 마음을 전하며, 성공적인 협력을 기원해요.",
            "story_032": "고객에게 감사의 마음을 전하며, 격식 있는 서비스를 제공해요.",
            "story_033": "동료에게 격식 있는 마음을 전하며, 성공적인 프로젝트를 기원해요.",
            "story_034": "파트너사에게 감사의 마음을 전하며, 격식 있는 협력을 기원해요.",
            "story_035": "고객에게 격식 있는 마음을 전하며, 성공적인 비즈니스를 기원해요.",
            "story_036": "동료에게 감사의 마음을 전하며, 격식 있는 협력을 기원해요.",
            "story_037": "자신에게 보상을 주며, 일상의 작은 기쁨을 찾아요.",
            "story_038": "자신을 격려하며, 새로운 도전을 위한 힘을 얻어요.",
            "story_039": "자신에게 감사의 마음을 전하며, 소중한 일상을 기념해요.",
            "story_040": "자신을 응원하며, 앞으로의 성장을 기대해요."
        }
        
        predefined_messages = {
            # 1-10번 스토리 (영어 인용구)
            "story_001": "Gratitude is the fairest blossom which springs from the soul.",
            "story_002": "I'm proud of you.",
            "story_003": "Joy is the simplest form of gratitude.",
            "story_004": "Gratitude is the fairest blossom which springs from the soul.",
            "story_005": "Joy is the simplest form of gratitude.",
            "story_006": "Celebration is the joy of life.",
            "story_007": "I'm proud of you.",
            "story_008": "Joy is the simplest form of gratitude.",
            "story_009": "Gratitude is the fairest blossom which springs from the soul.",
            "story_010": "Celebration is the joy of life.",
            # 11-20번 스토리 (영어 인용구)
            "story_011": "Love is the flower you've got to let grow.",
            "story_012": "Love is the flower you've got to let grow.",
            "story_013": "Gratitude is the fairest blossom which springs from the soul.",
            "story_014": "Love is the flower you've got to let grow.",
            "story_015": "I'm proud of you.",
            "story_016": "Love is the flower you've got to let grow.",
            "story_017": "Love is the flower you've got to let grow.",
            "story_018": "Joy is the simplest form of gratitude.",
            "story_019": "Gratitude is the fairest blossom which springs from the soul.",
            "story_020": "Gratitude is the fairest blossom which springs from the soul.",
            # 21-30번 스토리 (영어 인용구)
            "story_021": "I believe in you.",
            "story_022": "Time heals all wounds.",
            "story_023": "Time heals all wounds.",
            "story_024": "I believe in you.",
            "story_025": "Hope is the thing with feathers.",
            "story_026": "Hope is the thing with feathers.",
            "story_027": "Time heals all wounds.",
            "story_028": "Love is the flower you've got to let grow.",
            "story_029": "Love is the flower you've got to let grow.",
            "story_030": "Hope is the thing with feathers.",
            "story_031": "May your 비즈니스 prosper.",
            "story_032": "May your 서비스 excel.",
            "story_033": "May your 프로젝트 succeed.",
            "story_034": "May your 협력 flourish.",
            "story_035": "May your 비즈니스 grow.",
            "story_036": "May your 협력 prosper.",
            "story_037": "May your 일상 be joyful.",
            "story_038": "May your 도전 bring success.",
            "story_039": "May your 일상 be blessed.",
            "story_040": "May your 성장 continue."
        }
        
        recommendation_reason = predefined_reasons.get(story_id, "이 꽃이 당신의 마음을 잘 표현해드릴 거예요.")
        
        # 1-30번 스토리는 영어 인용구 + 출처, 나머지는 기존 메시지
        if story_id in ["story_001", "story_002", "story_003", "story_004", "story_005", 
                        "story_006", "story_007", "story_008", "story_009", "story_010",
                        "story_011", "story_012", "story_013", "story_014", "story_015",
                        "story_016", "story_017", "story_018", "story_019", "story_020",
                        "story_021", "story_022", "story_023", "story_024", "story_025",
                        "story_026", "story_027", "story_028", "story_029", "story_030"]:
            quote_sources = {
                "story_001": "Henry Ward Beecher",
                "story_002": "Anonymous", 
                "story_003": "Karl Barth",
                "story_004": "Henry Ward Beecher",
                "story_005": "Karl Barth",
                "story_006": "Osho",
                "story_007": "Anonymous",
                "story_008": "Karl Barth",
                "story_009": "Henry Ward Beecher",
                "story_010": "Osho",
                "story_011": "John Lennon",
                "story_012": "John Lennon", 
                "story_013": "Henry Ward Beecher",
                "story_014": "John Lennon",
                "story_015": "Anonymous",
                "story_016": "John Lennon",
                "story_017": "John Lennon",
                "story_018": "Karl Barth",
                "story_019": "Henry Ward Beecher",
                "story_020": "Henry Ward Beecher",
                "story_021": "Anonymous",
                "story_022": "Greek Proverb",
                "story_023": "Greek Proverb",
                "story_024": "Anonymous",
                "story_025": "Emily Dickinson",
                "story_026": "Emily Dickinson",
                "story_027": "Greek Proverb",
                "story_028": "John Lennon",
                "story_029": "John Lennon",
                "story_030": "Emily Dickinson"
            }
            base_message = predefined_messages.get(story_id, "May your day be beautiful.")
            source = quote_sources.get(story_id, "")
            flower_card_message = f"{base_message} - {source}"
        else:
            flower_card_message = predefined_messages.get(story_id, "May your day be beautiful.")
        
        # 스토리 ID 생성 (S{YYYYMMDD}{영문꽃이름코드}S{4자리순번})
        current_date = datetime.now().strftime("%y%m%d")
        
        # 영문 이름에서 정확한 코드 추출
        flower_name_mapping = {
            'Zinnia Elegans': 'ZIN',
            'Alstroemeria Spp': 'ALS',
            'Gerbera Daisy': 'GER',
            'Sunflower': 'SUN',
            'Rose': 'ROS',
            'Tulip': 'TUL',
            'Carnation': 'CAR',
            'Sweet Pea': 'SWP',
            'Lisianthus': 'LIS',
            'Bouvardia': 'BOU',
            'Astilbe Japonica': 'AST',
            'Hydrangea': 'HYD',
            'Freesia Refracta': 'FRE'
        }
        
        flower_prefix = flower_name_mapping.get(matched_flower.flower_name, 'FLW')
        import random
        random_suffix = f"S{random.randint(1000, 9999):04d}"
        story_id = f"S{current_date}-{flower_prefix}-{random_suffix}"
        
        # 계절 정보 생성
        season_info = "All Season 01-12"  # 기본값, 실제로는 꽃 데이터에서 가져와야 함
        
        # 응답 생성 (실제 사용자 추천과 동일한 구조)
        response = {
            "story_id": story_id,
            "original_story": story["story"],
            "created_at": datetime.now().isoformat(),
            
            # 감정 분석 결과
            "emotions": [
                {
                    "emotion": emotion.emotion,
                    "percentage": emotion.percentage,
                    "description": emotion.description
                } for emotion in emotions
            ],
            
            # 꽃 정보
            "flower_name": matched_flower.korean_name,
            "flower_name_en": matched_flower.flower_name,
            "scientific_name": matched_flower.scientific_name,
            "flower_card_message": flower_card_message,
            "flower_image_url": matched_flower.image_url,
            
            # 꽃 조합 정보
            "flower_blend": {
                "main_flower": composition.main_flower,
                "sub_flowers": composition.sub_flowers,
                "composition_name": composition.composition_name
            },
            
            # 계절 정보
            "season_info": season_info,
            
            # 추천 코멘트
            "recommendation_reason": recommendation_reason,
            
            # 추가 메타데이터
            "keywords": matched_flower.keywords,
            "hashtags": matched_flower.hashtags,
            "color_keywords": matched_flower.color_keywords,
            "excluded_keywords": [],
            
            # 샘플 사연 정보
            "sample_story": {
                "id": story["id"],
                "title": story["title"],
                "category": story["category"],
                "predefined_keywords": predefined_keywords
            }
        }
        
        return response
        
    except Exception as e:
        print(f"❌ 샘플 사연 추천 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/sample-stories/categories")
async def get_sample_story_categories():
    """샘플 사연 카테고리 목록을 반환합니다."""
    stories = load_sample_stories()
    categories = {}
    
    for story in stories:
        category = story.get("category", "기타")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": story["id"],
            "title": story["title"],
            "story": story["story"]
        })
    
    return {
        "categories": categories,
        "category_count": len(categories)
    }

@router.get("/sample-stories/category/{category}")
async def get_sample_stories_by_category(category: str):
    """특정 카테고리의 샘플 사연들을 반환합니다."""
    stories = load_sample_stories()
    category_stories = [s for s in stories if s.get("category") == category]
    
    if not category_stories:
        raise HTTPException(status_code=404, detail="해당 카테고리의 사연을 찾을 수 없습니다.")
    
    return {
        "category": category,
        "stories": category_stories,
        "count": len(category_stories)
    }

