import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from app.models.schemas import StoryData, StoryCreateRequest

# 로거 설정
logger = logging.getLogger(__name__)


class StoryManager:
    """스토리 데이터 관리 서비스"""
    
    def __init__(self):
        self.stories_file = Path("data/stories.json")
        self.stories_file.parent.mkdir(exist_ok=True)
        self._load_stories()
    
    def _load_stories(self):
        """스토리 데이터 로드"""
        if self.stories_file.exists():
            with open(self.stories_file, 'r', encoding='utf-8') as f:
                self.stories = json.load(f)
        else:
            self.stories = {}
            self._save_stories()
    
    def _save_stories(self):
        """스토리 데이터 저장"""
        with open(self.stories_file, 'w', encoding='utf-8') as f:
            json.dump(self.stories, f, ensure_ascii=False, indent=2, default=str)
    
    def _generate_story_id(self, flower_name: str) -> str:
        """스토리 ID 생성 - 새로운 정책: S{YYMMDD}-{FLC}-{NNNNNN}"""
        # 오늘 날짜 (YYMMDD 형식)
        today = datetime.now().strftime("%y%m%d")  # 2자리 연도
        
        # 꽃 영문명에서 3자리 코드 생성
        flower_code = self._get_flower_code(flower_name)
        
        # 오늘 날짜에 해당하는 스토리들 필터링
        today_stories = [
            story_id for story_id in self.stories.keys()
            if story_id.startswith(f"S{today}-{flower_code}-")
        ]
        
        # 다음 순번 계산
        next_number = len(today_stories) + 1
        
        # 6자리 순번으로 포맷팅
        sequence = f"{next_number:06d}"
        
        return f"S{today}-{flower_code}-{sequence}"
    
    def _get_flower_code(self, flower_name: str) -> str:
        """꽃 영문명에서 3자리 코드 생성"""
        # 꽃 영문명 매핑 테이블
        flower_code_mapping = {
            # 주요 꽃들
            'Sweet Pea': 'SWP',
            'Rose': 'ROS',
            'Tulip': 'TUL',
            'Gerbera': 'GER',
            'Alstroemeria': 'ALS',
            'Lily': 'LIL',
            'Carnation': 'CAR',
            'Dahlia': 'DAH',
            'Peony': 'PEO',
            'Iris': 'IRI',
            'Anemone': 'ANE',
            'Ranunculus': 'RAN',
            'Gladiolus': 'GLA',
            'Freesia': 'FRE',
            'Lisianthus': 'LIS',
            'Stock': 'STO',
            'Scabiosa': 'SCA',
            'Bouvardia': 'BOU',
            'Marguerite': 'MAR',
            'Cockscomb': 'COC',
            'Cotton': 'COT',
            'Drumstick': 'DRU',
            'Gentiana': 'GEN',
            'Zinnia': 'ZIN',
            'Tagetes': 'TAG',
            'Veronica': 'VER',
            'Hydrangea': 'HYD',
            'Astilbe': 'AST',
            'Anthurium': 'ANT',
            'Cymbidium': 'CYM',
            'Baby\'s Breath': 'BAB',
            'Oxypetalum': 'OXY',
            'Spiraea': 'SPI',
            'Iberis': 'IBE',
            'Ammi': 'AMM',
            'Lathyrus': 'LAT',
            'Zantedeschia': 'ZAN',
            'Dianthus': 'DIA',
            'Garden': 'GAR',
            'Globe': 'GLO',
            'Lathyrus Odoratus': 'SWP',  # Sweet Pea의 학명
            'Rosa': 'ROS',  # Rose의 학명
            'Tulipa': 'TUL',  # Tulip의 학명
            'Gerbera Daisy': 'GER',
            'Alstroemeria spp': 'ALS',
            'Lilium': 'LIL',  # Lily의 학명
            'Dianthus caryophyllus': 'CAR',  # Carnation의 학명
            'Dahlia pinnata': 'DAH',  # Dahlia의 학명
            'Paeonia': 'PEO',  # Peony의 학명
            'Iris sanguinea': 'IRI',
            'Anemone coronaria': 'ANE',
            'Ranunculus asiaticus': 'RAN',
            'Gladiolus': 'GLA',
            'Freesia refracta': 'FRE',
            'Eustoma': 'LIS',  # Lisianthus의 학명
            'Matthiola': 'STO',  # Stock의 학명
            'Scabiosa': 'SCA',
            'Bouvardia': 'BOU',
            'Argyranthemum': 'MAR',  # Marguerite의 학명
            'Celosia': 'COC',  # Cockscomb의 학명
            'Gossypium': 'COT',  # Cotton의 학명
            'Craspedia': 'DRU',  # Drumstick의 학명
            'Gentiana andrewsii': 'GEN',
            'Zinnia elegans': 'ZIN',
            'Tagetes erecta': 'TAG',
            'Veronica spicata': 'VER',
            'Hydrangea': 'HYD',
            'Astilbe japonica': 'AST',
            'Anthurium andraeanum': 'ANT',
            'Cymbidium spp': 'CYM',
            'Gypsophila': 'BAB',  # Baby's Breath의 학명
            'Oxypetalum coeruleum': 'OXY',
            'Spiraea prunifolia': 'SPI',
            'Iberis sempervirens': 'IBE',
            'Ammi majus': 'AMM',
            'Zantedeschia aethiopica': 'ZAN',
            'Dianthus': 'DIA',
        }
        
        # 정확한 매칭 시도
        if flower_name in flower_code_mapping:
            return flower_code_mapping[flower_name]
        
        # 부분 매칭 시도 (영문명에 포함된 경우)
        for key, code in flower_code_mapping.items():
            if flower_name.lower() in key.lower() or key.lower() in flower_name.lower():
                return code
        
        # 매칭되지 않은 경우 영문명에서 3자리 추출
        # 한글명인 경우 영문명으로 변환 시도
        korean_to_english = {
            '스위트피': 'SWP',
            '장미': 'ROS',
            '튤립': 'TUL',
            '거베라': 'GER',
            '알스트로메리아': 'ALS',
            '백합': 'LIL',
            '카네이션': 'CAR',
            '달리아': 'DAH',
            '피오니': 'PEO',
            '아이리스': 'IRI',
            '아네모네': 'ANE',
            '라넌큘러스': 'RAN',
            '글라디올러스': 'GLA',
            '프리지아': 'FRE',
            '리시안서스': 'LIS',
            '스톡': 'STO',
            '스카비오사': 'SCA',
            '부바르디아': 'BOU',
            '마거리트': 'MAR',
            '맨드라미': 'COC',
            '목화': 'COT',
            '드럼스틱': 'DRU',
            '젠티아나': 'GEN',
            '천일홍': 'ZIN',
            '태게테스': 'TAG',
            '베로니카': 'VER',
            '수국': 'HYD',
            '아스틸베': 'AST',
            '안스리움': 'ANT',
            '심비디움': 'CYM',
            '베이비브레스': 'BAB',
            '옥시페탈럼': 'OXY',
            '스피라에아': 'SPI',
            '이베리스': 'IBE',
            '아미': 'AMM',
            '잔테데스키아': 'ZAN',
            '다이안서스': 'DIA',
        }
        
        if flower_name in korean_to_english:
            return korean_to_english[flower_name]
        
        # 마지막 fallback: 영문명에서 3자리 추출
        english_name = flower_name.upper()
        # 공백과 특수문자 제거
        english_name = ''.join(c for c in english_name if c.isalpha())
        
        if len(english_name) >= 3:
            return english_name[:3]
        else:
            # 3자리 미만인 경우 X로 패딩
            return english_name.ljust(3, 'X')
    
    def create_story(self, request: StoryCreateRequest) -> StoryData:
        """새로운 스토리 생성"""
        # 스토리 ID 생성
        story_id = self._generate_story_id(request.matched_flower.flower_name)
        
        # 현재 시간
        now = datetime.now()
        
        # StoryData 객체 생성
        story_data = StoryData(
            story_id=story_id,
            original_story=request.story,
            created_at=now,
            updated_at=None,
            emotions=request.emotions,
            flower_name=request.matched_flower.flower_name,
            flower_name_en=request.matched_flower.korean_name,  # 영문 이름은 별도 필드 필요할 수 있음
            scientific_name=request.matched_flower.scientific_name,
            flower_card_message=request.flower_card_message or "",
            flower_blend=request.composition,
            season_info=request.season_info or "",
            recommendation_reason=request.recommendation_reason,
            flower_image_url=request.matched_flower.image_url,
            keywords=request.keywords,
            hashtags=request.hashtags,
            color_keywords=request.color_keywords,
            excluded_keywords=request.excluded_keywords
        )
        
        # 데이터베이스에 저장
        self.stories[story_id] = story_data.dict()
        self._save_stories()
        
        return story_data
    
    def get_story(self, story_id: str) -> Optional[StoryData]:
        """스토리 ID로 스토리 조회"""
        if story_id not in self.stories:
            return None
        
        story_dict = self.stories[story_id]
        
        # datetime 문자열을 datetime 객체로 변환
        if isinstance(story_dict.get('created_at'), str):
            story_dict['created_at'] = datetime.fromisoformat(story_dict['created_at'].replace('Z', '+00:00'))
        if story_dict.get('updated_at') and isinstance(story_dict['updated_at'], str):
            story_dict['updated_at'] = datetime.fromisoformat(story_dict['updated_at'].replace('Z', '+00:00'))
        
        return StoryData(**story_dict)
    
    def update_story(self, story_id: str, update_data: Dict[str, Any]) -> Optional[StoryData]:
        """스토리 업데이트"""
        if story_id not in self.stories:
            return None
        
        # 기존 데이터 가져오기
        story_dict = self.stories[story_id]
        
        # 업데이트할 데이터 적용
        story_dict.update(update_data)
        story_dict['updated_at'] = datetime.now()
        
        # StoryData 객체로 변환하여 검증
        story_data = StoryData(**story_dict)
        
        # 저장
        self.stories[story_id] = story_data.dict()
        self._save_stories()
        
        return story_data
    
    def delete_story(self, story_id: str) -> bool:
        """스토리 삭제"""
        if story_id not in self.stories:
            return False
        
        del self.stories[story_id]
        self._save_stories()
        return True
    
    def get_all_stories(self) -> Dict[str, StoryData]:
        """모든 스토리 조회"""
        return {
            story_id: self.get_story(story_id)
            for story_id in self.stories.keys()
        }
    
    def get_stories_by_date(self, date_str: str) -> Dict[str, StoryData]:
        """특정 날짜의 스토리들 조회"""
        return {
            story_id: self.get_story(story_id)
            for story_id in self.stories.keys()
            if story_id.startswith(f"S{date_str}")
        }
    
    def get_stories_by_flower(self, flower_name: str) -> Dict[str, StoryData]:
        """특정 꽃에 대한 스토리들 조회"""
        flower_prefix = flower_name[:3] if len(flower_name) >= 3 else flower_name.ljust(3, 'X')
        
        return {
            story_id: self.get_story(story_id)
            for story_id in self.stories.keys()
            if flower_prefix in story_id
        }
    
    def get_story_count(self) -> int:
        """전체 스토리 개수"""
        return len(self.stories)
    
    def get_daily_story_count(self, date_str: str) -> int:
        """특정 날짜의 스토리 개수"""
        return len([
            story_id for story_id in self.stories.keys()
            if story_id.startswith(f"S{date_str}")
        ])


# 전역 인스턴스
story_manager = StoryManager()
