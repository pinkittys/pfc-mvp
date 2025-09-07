#!/usr/bin/env python3
"""
실제 꽃들의 고유한 특성을 반영한 정확한 꽃 데이터 생성 스크립트
"""
import json
import os
from typing import List, Dict

def get_local_images():
    """로컬 images_webp 폴더에서 모든 이미지 파일 가져오기"""
    images_dir = "data/images_webp"
    if not os.path.exists(images_dir):
        print(f"❌ 이미지 디렉토리가 없습니다: {images_dir}")
        return []
    
    image_files = []
    for filename in os.listdir(images_dir):
        if filename.endswith('.webp'):
            image_files.append(filename)
    
    return sorted(image_files)

def parse_image_filename(filename: str) -> Dict[str, str]:
    """이미지 파일명에서 꽃 정보 추출"""
    if not filename.endswith('.webp'):
        return None
    
    name_without_ext = filename[:-5]  # .webp 제거
    
    # 색상 코드 매핑
    color_mapping = {
        'wh': '화이트', 'or': '오렌지', 'rd': '레드', 'yl': '옐로우',
        'pk': '핑크', 'bl': '블루', 'pu': '퍼플', 'll': '연보라', 'gr': '그린'
    }
    
    # 꽃 이름 매핑
    flower_mapping = {
        'alstroemeria': '알스트로메리아',
        'anemone': '아네모네',
        'anthurium': '안스리움',
        'astilbe': '아스틸베',
        'babys-breath': '베이비브레스',
        'bouvardia': '부바르디아',
        'calla-lily': '카라',
        'carnation': '카네이션',
        'gerbera-daisy': '거베라',
        'garden-peony': '모란',
        'gladiolus': '글라디올러스',
        'hydrangea': '수국',
        'lily': '백합',
        'lisianthus': '리시안셔스',
        'marigold': '마리골드',
        'ranunculus': '라넌큘러스',
        'rose': '장미',
        'stock-flower': '스토크',
        'sunflower': '해바라기',
        'tagetes-erecta': '태게테스',
        'tulip': '튤립',
        'zinnia': '지니아'
    }
    
    # 파일명 파싱
    parts = name_without_ext.split('-')
    if len(parts) < 2:
        return None
    
    flower_key = parts[0]
    color_key = parts[-1]
    
    flower_name_ko = flower_mapping.get(flower_key, flower_key)
    color_name_ko = color_mapping.get(color_key, color_key)
    
    return {
        'flower_key': flower_key,
        'flower_name_ko': flower_name_ko,
        'color_key': color_key,
        'color_name_ko': color_name_ko,
        'filename': filename
    }

def get_flower_characteristics():
    """각 꽃의 고유한 특성 정의"""
    return {
        'alstroemeria': {
            'flower_language_short': '우정, 지지, 지속적인 사랑',
            'flower_language_long': '우정과 지지의 마음을 의미해요',
            'moods': '우정,지지,따뜻함',
            'emotions': '우정,지지,따뜻함',
            'contexts': '우정,지지,격려',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium'
        },
        'ammi': {
            'flower_language_short': '순수, 우아함, 자연스러움',
            'flower_language_long': '순수함과 자연스러움을 의미해요',
            'moods': '순수,우아함,자연스러움',
            'emotions': '순수,우아함,자연스러움',
            'contexts': '순수,자연스러움,우아함',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'anemone': {
            'flower_language_short': '기대, 희망, 새로운 시작',
            'flower_language_long': '새로운 시작과 희망을 의미해요',
            'moods': '희망,기대,새로운시작',
            'emotions': '희망,기대,새로운시작',
            'contexts': '새로운시작,희망,기대',
            'season_months': 'Spring 03-05',
            'price_tier': 'high'
        },
        'anthurium': {
            'flower_language_short': '열정, 사랑, 환대',
            'flower_language_long': '열정과 환대를 의미해요',
            'moods': '열정,사랑,환대',
            'emotions': '열정,사랑,환대',
            'contexts': '환대,열정,사랑',
            'season_months': 'All Season 01-12',
            'price_tier': 'high'
        },
        'astilbe': {
            'flower_language_short': '인내, 지속, 헌신',
            'flower_language_long': '인내와 헌신을 의미해요',
            'moods': '인내,지속,헌신',
            'emotions': '인내,지속,헌신',
            'contexts': '인내,헌신,지속',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'babys': {
            'flower_language_short': '순수, 순진함, 영원한 사랑',
            'flower_language_long': '순수함과 영원한 사랑을 의미해요',
            'moods': '순수,순진함,영원한사랑',
            'emotions': '순수,순진함,영원한사랑',
            'contexts': '순수,영원한사랑,결혼',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'bouvardia': {
            'flower_language_short': '열정, 에너지, 활력',
            'flower_language_long': '열정과 활력을 의미해요',
            'moods': '열정,에너지,활력',
            'emotions': '열정,에너지,활력',
            'contexts': '열정,활력,에너지',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'calla': {
            'flower_language_short': '아름다움, 우아함, 신성함',
            'flower_language_long': '아름다움과 신성함을 의미해요',
            'moods': '아름다움,우아함,신성함',
            'emotions': '아름다움,우아함,신성함',
            'contexts': '결혼,신성함,우아함',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'high'
        },
        'carnation': {
            'flower_language_short': '사랑, 감사, 존경',
            'flower_language_long': '사랑과 감사를 의미해요',
            'moods': '사랑,감사,존경',
            'emotions': '사랑,감사,존경',
            'contexts': '사랑,감사,존경',
            'season_months': 'All Season 01-12',
            'price_tier': 'low'
        },
        'celosia': {
            'flower_language_short': '열정, 창의성, 독특함',
            'flower_language_long': '열정과 창의성을 의미해요',
            'moods': '열정,창의성,독특함',
            'emotions': '열정,창의성,독특함',
            'contexts': '열정,창의성,독특함',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'cornflower': {
            'flower_language_short': '순수, 우아함, 자연스러움',
            'flower_language_long': '순수함과 자연스러움을 의미해요',
            'moods': '순수,우아함,자연스러움',
            'emotions': '순수,우아함,자연스러움',
            'contexts': '순수,자연스러움,우아함',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'cotton': {
            'flower_language_short': '순수, 자연스러움, 평화',
            'flower_language_long': '순수함과 평화를 의미해요',
            'moods': '순수,자연스러움,평화',
            'emotions': '순수,자연스러움,평화',
            'contexts': '순수,평화,자연스러움',
            'season_months': 'Fall 09-11',
            'price_tier': 'low'
        },
        'cymbidium': {
            'flower_language_short': '우아함, 고귀함, 아름다움',
            'flower_language_long': '우아함과 고귀함을 의미해요',
            'moods': '우아함,고귀함,아름다움',
            'emotions': '우아함,고귀함,아름다움',
            'contexts': '우아함,고귀함,아름다움',
            'season_months': 'All Season 01-12',
            'price_tier': 'high'
        },
        'dahlia': {
            'flower_language_short': '우아함, 존경, 변화',
            'flower_language_long': '우아함과 존경을 의미해요',
            'moods': '우아함,존경,변화',
            'emotions': '우아함,존경,변화',
            'contexts': '우아함,존경,변화',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium'
        },
        'default': {
            'flower_language_short': '아름다움, 마음',
            'flower_language_long': '아름다운 마음을 의미해요',
            'moods': '아름다움,마음',
            'emotions': '아름다움,마음',
            'contexts': '아름다움,마음',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium'
        },
        'drumstick': {
            'flower_language_short': '독특함, 창의성, 개성',
            'flower_language_long': '독특함과 창의성을 의미해요',
            'moods': '독특함,창의성,개성',
            'emotions': '독특함,창의성,개성',
            'contexts': '독특함,창의성,개성',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'freesia': {
            'flower_language_short': '순수, 우아함, 신뢰',
            'flower_language_long': '순수함과 신뢰를 의미해요',
            'moods': '순수,우아함,신뢰',
            'emotions': '순수,우아함,신뢰',
            'contexts': '순수,신뢰,우아함',
            'season_months': 'Spring 03-05',
            'price_tier': 'high'
        },
        'garden': {
            'flower_language_short': '우아함, 고귀함, 아름다움',
            'flower_language_long': '우아함과 고귀함을 의미해요',
            'moods': '우아함,고귀함,아름다움',
            'emotions': '우아함,고귀함,아름다움',
            'contexts': '우아함,고귀함,아름다움',
            'season_months': 'Spring 03-05',
            'price_tier': 'high'
        },
        'gentiana': {
            'flower_language_short': '신비, 우아함, 아름다움',
            'flower_language_long': '신비와 우아함을 의미해요',
            'moods': '신비,우아함,아름다움',
            'emotions': '신비,우아함,아름다움',
            'contexts': '신비,우아함,아름다움',
            'season_months': 'Summer 06-08',
            'price_tier': 'high'
        },
        'gerbera': {
            'flower_language_short': '순수, 순진함, 기쁨',
            'flower_language_long': '순수함과 기쁨을 의미해요',
            'moods': '순수,순진함,기쁨',
            'emotions': '순수,순진함,기쁨',
            'contexts': '기쁨,순수,순진함',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium'
        },
        'gladiolus': {
            'flower_language_short': '강인함, 성공, 명예',
            'flower_language_long': '강인함과 성공을 의미해요',
            'moods': '강인함,성공,명예',
            'emotions': '강인함,성공,명예',
            'contexts': '강인함,성공,명예',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'globe': {
            'flower_language_short': '독특함, 창의성, 개성',
            'flower_language_long': '독특함과 창의성을 의미해요',
            'moods': '독특함,창의성,개성',
            'emotions': '독특함,창의성,개성',
            'contexts': '독특함,창의성,개성',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'hydrangea': {
            'flower_language_short': '감사, 이해, 진정한 감정',
            'flower_language_long': '감사와 이해를 의미해요',
            'moods': '감사,이해,진정한감정',
            'emotions': '감사,이해,진정한감정',
            'contexts': '감사,이해,진정한감정',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'iberis': {
            'flower_language_short': '순수, 우아함, 자연스러움',
            'flower_language_long': '순수함과 자연스러움을 의미해요',
            'moods': '순수,우아함,자연스러움',
            'emotions': '순수,우아함,자연스러움',
            'contexts': '순수,자연스러움,우아함',
            'season_months': 'Spring 03-05',
            'price_tier': 'low'
        },
        'iris': {
            'flower_language_short': '신뢰, 지혜, 용기',
            'flower_language_long': '신뢰와 지혜를 의미해요',
            'moods': '신뢰,지혜,용기',
            'emotions': '신뢰,지혜,용기',
            'contexts': '신뢰,지혜,용기',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium'
        },
        'lathyrus': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium'
        },
        'lily': {
            'flower_language_short': '순수, 신성함, 재생',
            'flower_language_long': '순수와 신성함을 의미해요',
            'moods': '순수,신성함,재생',
            'emotions': '순수,신성함,재생',
            'contexts': '결혼,신성함,순수',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'high'
        },
        'lisianthus': {
            'flower_language_short': '감사, 존경, 우아함',
            'flower_language_long': '감사와 우아함을 의미해요',
            'moods': '감사,존경,우아함',
            'emotions': '감사,존경,우아함',
            'contexts': '감사,존경,우아함',
            'season_months': 'Summer 06-08',
            'price_tier': 'high'
        },
        'marguerite': {
            'flower_language_short': '순수, 순진함, 자연스러움',
            'flower_language_long': '순수함과 자연스러움을 의미해요',
            'moods': '순수,순진함,자연스러움',
            'emotions': '순수,순진함,자연스러움',
            'contexts': '순수,자연스러움,순진함',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'marigold': {
            'flower_language_short': '열정, 창의성, 에너지',
            'flower_language_long': '열정과 창의성을 의미해요',
            'moods': '열정,창의성,에너지',
            'emotions': '열정,창의성,에너지',
            'contexts': '열정,창의성,에너지',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'ranunculus': {
            'flower_language_short': '매력, 매혹, 아름다움',
            'flower_language_long': '매력과 아름다움을 의미해요',
            'moods': '매력,매혹,아름다움',
            'emotions': '매력,매혹,아름다움',
            'contexts': '매력,아름다움,매혹',
            'season_months': 'Spring 03-05',
            'price_tier': 'high'
        },
        'rose': {
            'flower_language_short': '사랑, 아름다움, 열정',
            'flower_language_long': '사랑과 아름다움을 의미해요',
            'moods': '사랑,아름다움,열정',
            'emotions': '사랑,아름다움,열정',
            'contexts': '사랑,아름다움,열정',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium'
        },
        'scabiosa': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'spiraea': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Spring 03-05',
            'price_tier': 'low'
        },
        'stock': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium'
        },
        'sunflower': {
            'flower_language_short': '기쁨, 충성, 존경',
            'flower_language_long': '기쁨과 충성을 의미해요',
            'moods': '기쁨,충성,존경',
            'emotions': '기쁨,충성,존경',
            'contexts': '기쁨,충성,존경',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'sweet': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium'
        },
        'tagetes': {
            'flower_language_short': '열정, 창의성, 에너지',
            'flower_language_long': '열정과 창의성을 의미해요',
            'moods': '열정,창의성,에너지',
            'emotions': '열정,창의성,에너지',
            'contexts': '열정,창의성,에너지',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        },
        'tulip': {
            'flower_language_short': '완벽한 사랑, 명성, 부',
            'flower_language_long': '완벽한 사랑을 의미해요',
            'moods': '완벽한사랑,명성,부',
            'emotions': '완벽한사랑,명성,부',
            'contexts': '완벽한사랑,명성,부',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium'
        },
        'veronica': {
            'flower_language_short': '우아함, 자연스러움, 아름다움',
            'flower_language_long': '우아함과 자연스러움을 의미해요',
            'moods': '우아함,자연스러움,아름다움',
            'emotions': '우아함,자연스러움,아름다움',
            'contexts': '우아함,자연스러움,아름다움',
            'season_months': 'Summer 06-08',
            'price_tier': 'medium'
        },
        'zinnia': {
            'flower_language_short': '열정, 창의성, 에너지',
            'flower_language_long': '열정과 창의성을 의미해요',
            'moods': '열정,창의성,에너지',
            'emotions': '열정,창의성,에너지',
            'contexts': '열정,창의성,에너지',
            'season_months': 'Summer 06-08',
            'price_tier': 'low'
        }
    }

def get_color_specific_characteristics():
    """색상별 특별한 특성"""
    return {
        'rose-bl': {
            'flower_language_short': '기적, 불가능한 사랑',
            'flower_language_long': '기적 같은 사랑을 의미해요',
            'moods': '신비,기적,희망',
            'emotions': '기적,불가능한사랑,희망',
            'contexts': '특별한순간,기적,희망'
        },
        'rose-rd': {
            'flower_language_short': '사랑, 열정, 로맨스',
            'flower_language_long': '진정한 사랑을 의미해요',
            'moods': '사랑,열정,로맨스',
            'emotions': '사랑,열정,로맨스',
            'contexts': '사랑고백,로맨스,열정'
        },
        'rose-pk': {
            'flower_language_short': '사랑, 감사, 기쁨',
            'flower_language_long': '사랑과 감사를 의미해요',
            'moods': '사랑,감사,기쁨',
            'emotions': '사랑,감사,기쁨',
            'contexts': '사랑,감사,기념일'
        },
        'rose-wh': {
            'flower_language_short': '순수, 신성한 사랑',
            'flower_language_long': '순수한 사랑을 의미해요',
            'moods': '순수,신성,깨끗함',
            'emotions': '순수,신성,깨끗함',
            'contexts': '결혼,순수,신성'
        },
        'rose-or': {
            'flower_language_short': '열정, 에너지, 활력',
            'flower_language_long': '열정과 에너지를 의미해요',
            'moods': '열정,에너지,활력',
            'emotions': '열정,에너지,활력',
            'contexts': '새로운시작,열정,에너지'
        }
    }

def create_accurate_flower_data():
    """정확한 꽃 데이터 생성"""
    print("🔄 정확한 꽃 데이터 생성 중...")
    
    # 로컬에서 이미지 파일 목록 가져오기
    image_files = get_local_images()
    
    if not image_files:
        print("❌ 로컬 이미지 파일을 찾을 수 없습니다.")
        return []
    
    print(f"📊 로컬 이미지 파일: {len(image_files)}개")
    
    # 이미지 정보 파싱
    parsed_images = []
    for filename in image_files:
        parsed = parse_image_filename(filename)
        if parsed:
            parsed_images.append(parsed)
        else:
            print(f"⚠️ 파싱 실패: {filename}")
    
    print(f"✅ 파싱된 이미지: {len(parsed_images)}개")
    
    # 꽃 특성과 색상별 특성 가져오기
    flower_characteristics = get_flower_characteristics()
    color_specific_characteristics = get_color_specific_characteristics()
    
    # 스프레드시트 데이터 생성
    spreadsheet_data = []
    uid_counter = 1
    
    for img in parsed_images:
        # 기본 꽃 특성 가져오기
        base_characteristics = flower_characteristics.get(img['flower_key'], {
            'flower_language_short': '아름다움, 마음',
            'flower_language_long': '아름다운 마음을 의미해요',
            'moods': '아름다움,마음',
            'emotions': '아름다움,마음',
            'contexts': '아름다움,마음',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium'
        })
        
        # 색상별 특별한 특성 확인
        special_key = f"{img['flower_key']}-{img['color_key']}"
        special_characteristics = color_specific_characteristics.get(special_key, {})
        
        # 최종 특성 결정 (색상별 특성이 있으면 우선 사용)
        final_characteristics = {**base_characteristics, **special_characteristics}
        
        # 꽃 데이터 생성
        flower_data = {
            'uid': f'accurate_{uid_counter:04d}',
            'flower_id': f"{img['flower_key']}-{img['color_key']}",
            'flower_slug': img['flower_key'],
            'color_code': img['color_key'],
            'name_ko': img['flower_name_ko'],
            'name_en': img['flower_key'].title(),
            'scientific_name': f"{img['flower_key'].title()} spp.",
            'is_main': True,
            'base_color': img['color_key'],
            'alt_colors': '',
            'moods': final_characteristics['moods'],
            'emotions': final_characteristics['emotions'],
            'contexts': final_characteristics['contexts'],
            'season_months': final_characteristics['season_months'],
            'price_tier': final_characteristics['price_tier'],
            'features': 'beautiful,charming,elegant',
            'flower_language_short': final_characteristics['flower_language_short'],
            'flower_language_long': final_characteristics['flower_language_long'],
            'image_key': img['filename'][:-5],  # .webp 제거
            'image_url': f"https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/{img['filename']}"
        }
        
        spreadsheet_data.append(flower_data)
        uid_counter += 1
    
    return spreadsheet_data

def main():
    """메인 함수"""
    print("🚀 정확한 꽃 데이터 생성 시작...")
    
    # 정확한 데이터 생성
    spreadsheet_data = create_accurate_flower_data()
    
    if not spreadsheet_data:
        print("❌ 데이터 생성 실패")
        return
    
    # 파일에 저장
    with open('data/spreadsheet_flowers.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 정확한 꽃 데이터 생성 완료!")
    print(f"   📋 총 꽃 데이터: {len(spreadsheet_data)}개")
    
    # 샘플 데이터 출력
    print(f"\\n🌸 샘플 데이터:")
    for i, flower in enumerate(spreadsheet_data[:3]):
        print(f"   {i+1}. {flower['name_ko']} ({flower['flower_slug']}-{flower['base_color']})")
        print(f"      꽃말: {flower['flower_language_short']}")
        print(f"      감정: {flower['emotions']}")
        print(f"      상황: {flower['contexts']}")
        print(f"      무드: {flower['moods']}")

if __name__ == "__main__":
    main()
