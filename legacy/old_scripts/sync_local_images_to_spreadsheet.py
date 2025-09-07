#!/usr/bin/env python3
"""
로컬 이미지 파일들을 기반으로 스프레드시트 데이터를 생성하는 스크립트
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
    # 예: "alstroemeria-or.webp" -> {"flower": "alstroemeria", "color": "or"}
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

def create_spreadsheet_data_from_local():
    """로컬 이미지 파일들을 기반으로 스프레드시트 데이터 생성"""
    print("🔄 로컬 이미지 파일에서 데이터 생성 중...")
    
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
    
    # 색상별 특별한 꽃말 매핑
    special_flower_language = {
        'rose-bl': {
            'flower_language_short': '기적, 불가능한 사랑',
            'flower_language_long': '기적 같은 사랑을 의미해요',
            'moods': '신비,기적,희망',
            'emotions': '기적,불가능한사랑,희망',
            'contexts': '특별한순간,기적,희망'
        },
        'rose-rd': {
            'flower_language_short': '사랑, 열정',
            'flower_language_long': '진정한 사랑을 의미해요',
            'moods': '사랑,열정,로맨틱',
            'emotions': '사랑,열정,로맨틱',
            'contexts': '사랑고백,로맨틱,열정'
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
            'flower_language_short': '열정, 에너지',
            'flower_language_long': '열정과 에너지를 의미해요',
            'moods': '열정,에너지,활력',
            'emotions': '열정,에너지,활력',
            'contexts': '새로운시작,열정,에너지'
        }
    }
    
    # 스프레드시트 데이터 생성
    spreadsheet_data = []
    uid_counter = 1
    
    for img in parsed_images:
        # 특별한 꽃말이 있는지 확인
        special_key = f"{img['flower_key']}-{img['color_key']}"
        special_data = special_flower_language.get(special_key, {})
        
        # 기본 꽃 정보 생성
        flower_data = {
            'uid': f'local_{uid_counter:04d}',
            'flower_id': f"{img['flower_key']}-{img['color_key']}",
            'flower_slug': img['flower_key'],
            'color_code': img['color_key'],
            'name_ko': img['flower_name_ko'],
            'name_en': img['flower_key'].title(),
            'scientific_name': f"{img['flower_key'].title()} spp.",
            'is_main': True,
            'base_color': img['color_key'],
            'alt_colors': '',
            'moods': special_data.get('moods', '감사,기쁨,사랑'),
            'emotions': special_data.get('emotions', '감사전달,생일,기념일'),
            'contexts': special_data.get('contexts', 'All Season 01-12'),
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'beautiful,charming,elegant',
            'flower_language_short': special_data.get('flower_language_short', '사랑, 감사, 기쁨'),
            'flower_language_long': special_data.get('flower_language_long', '마음을 담아 전해요'),
            'image_key': img['filename'][:-5],  # .webp 제거
            'image_url': f"https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/{img['filename']}"
        }
        
        spreadsheet_data.append(flower_data)
        uid_counter += 1
    
    return spreadsheet_data

def main():
    """메인 함수"""
    print("🚀 로컬 이미지 → 스프레드시트 데이터 동기화 시작...")
    
    # 로컬 기반 데이터 생성
    spreadsheet_data = create_spreadsheet_data_from_local()
    
    if not spreadsheet_data:
        print("❌ 데이터 생성 실패")
        return
    
    # 파일에 저장
    with open('data/spreadsheet_flowers.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 로컬 기반 스프레드시트 데이터 생성 완료!")
    print(f"   📋 총 꽃 데이터: {len(spreadsheet_data)}개")
    
    # 색상별 통계
    color_stats = {}
    for flower in spreadsheet_data:
        color = flower['base_color']
        color_stats[color] = color_stats.get(color, 0) + 1
    
    print(f"   🎨 색상별 통계:")
    for color, count in sorted(color_stats.items()):
        print(f"      - {color}: {count}개")
    
    # 꽃별 통계
    flower_stats = {}
    for flower in spreadsheet_data:
        flower_name = flower['flower_slug']
        flower_stats[flower_name] = flower_stats.get(flower_name, 0) + 1
    
    print(f"   🌸 꽃별 통계:")
    for flower, count in sorted(flower_stats.items()):
        print(f"      - {flower}: {count}개")

if __name__ == "__main__":
    main()
