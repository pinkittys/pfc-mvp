#!/usr/bin/env python3
"""
Supabase Storage의 모든 이미지를 기반으로 스프레드시트 데이터를 생성하는 스크립트
"""
import json
import requests
from typing import List, Dict

def get_supabase_images():
    """Supabase Storage에서 모든 이미지 목록 가져오기"""
    try:
        # Supabase Storage API를 통해 이미지 목록 가져오기
        url = "https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/list/flowers"
        headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5bHJ5ZHlqYm5hY2JqdW10eHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NzQ4MjEsImV4cCI6MjA1MDU1MDgyMX0.8QZqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5bHJ5ZHlqYm5hY2JqdW10eHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NzQ4MjEsImV4cCI6MjA1MDU1MDgyMX0.8QZqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Supabase API 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Supabase 연결 오류: {e}")
        return []

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
        'hydrangea': '수국',
        'lily': '백합',
        'lisianthus': '리시안셔스',
        'marigold': '마리골드',
        'ranunculus': '라넌큘러스',
        'rose': '장미',
        'stock-flower': '스토크',
        'sunflower': '해바라기',
        'tagetes-erecta': '태게테스',
        'tulip': '튤립'
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

def create_spreadsheet_data_from_supabase():
    """Supabase Storage 이미지를 기반으로 스프레드시트 데이터 생성"""
    print("🔄 Supabase Storage에서 이미지 목록 가져오는 중...")
    
    # Supabase에서 이미지 목록 가져오기
    images = get_supabase_images()
    
    if not images:
        print("❌ Supabase에서 이미지를 가져올 수 없습니다.")
        return []
    
    print(f"📊 Supabase Storage 이미지: {len(images)}개")
    
    # 이미지 정보 파싱
    parsed_images = []
    for img in images:
        if 'name' in img:
            parsed = parse_image_filename(img['name'])
            if parsed:
                parsed_images.append(parsed)
    
    print(f"✅ 파싱된 이미지: {len(parsed_images)}개")
    
    # 스프레드시트 데이터 생성
    spreadsheet_data = []
    uid_counter = 1
    
    for img in parsed_images:
        # 기본 꽃 정보 생성
        flower_data = {
            'uid': f'supabase_{uid_counter:04d}',
            'flower_id': f"{img['flower_key']}-{img['color_key']}",
            'flower_slug': img['flower_key'],
            'color_code': img['color_key'],
            'name_ko': img['flower_name_ko'],
            'name_en': img['flower_key'].title(),
            'scientific_name': f"{img['flower_key'].title()} spp.",
            'is_main': True,
            'base_color': img['color_key'],
            'alt_colors': '',
            'moods': '감사,기쁨,사랑',
            'emotions': '감사전달,생일,기념일',
            'contexts': 'All Season 01-12',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'beautiful,charming,elegant',
            'flower_language_short': '사랑, 감사, 기쁨',
            'flower_language_long': '마음을 담아 전해요',
            'image_key': img['filename'][:-5],  # .webp 제거
            'image_url': f"https://uylrydyjbnacbjumtxue.supabase.co/storage/v1/object/public/flowers/{img['filename']}"
        }
        
        spreadsheet_data.append(flower_data)
        uid_counter += 1
    
    return spreadsheet_data

def main():
    """메인 함수"""
    print("🚀 Supabase Storage → 스프레드시트 데이터 동기화 시작...")
    
    # Supabase 기반 데이터 생성
    spreadsheet_data = create_spreadsheet_data_from_supabase()
    
    if not spreadsheet_data:
        print("❌ 데이터 생성 실패")
        return
    
    # 파일에 저장
    with open('data/spreadsheet_flowers.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Supabase 기반 스프레드시트 데이터 생성 완료!")
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
