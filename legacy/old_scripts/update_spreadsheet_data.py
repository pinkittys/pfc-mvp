#!/usr/bin/env python3
"""
구글 스프레드시트 데이터를 완전히 업데이트하는 스크립트
"""
import json

def create_complete_spreadsheet_data():
    """구글 스프레드시트에서 확인된 모든 꽃 데이터 생성"""
    
    # 구글 스프레드시트에서 확인된 모든 꽃 데이터
    all_flowers = [
        # 화이트 색상
        {
            'uid': '1034ab74',
            'flower_id': 'marguerite-daisy-wh',
            'flower_slug': 'marguerite-daisy',
            'color_code': 'wh',
            'name_ko': '마가렛',
            'name_en': 'Marguerite Daisy',
            'scientific_name': 'Argyranthemum frutescens',
            'is_main': True,
            'base_color': 'wh',
            'alt_colors': '로맨틱,내추럴,우아함',
            'moods': '감사,평온,애틋함',
            'emotions': '감사전달,고백,인테리어',
            'contexts': 'Spring/Summer 03-08',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium',
            'features': 'pure,sincere,gentle,clean',
            'flower_language_short': '진심, 순결한 사랑',
            'flower_language_long': '진심을 담아, 고요히 전해요.',
            'image_key': 'marguerite-daisy-wh',
            'image_url': 'https://cdn.plainflower.club/flowers/marguerite-daisy-wh.png'
        },
        {
            'uid': 'a18c8a4a',
            'flower_id': 'bouvardia-wh',
            'flower_slug': 'bouvardia',
            'color_code': 'wh',
            'name_ko': '부바르디아',
            'name_en': 'Bouvardia',
            'scientific_name': 'Bouvardia spp.',
            'is_main': True,
            'base_color': 'wh',
            'alt_colors': '로맨틱,우아함,내추럴',
            'moods': '감사,애틋함,평온',
            'emotions': '감사전달,생일,위로·쾌유',
            'contexts': 'Spring/Summer 03-08',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium',
            'features': 'pure,gentle,graceful,serene',
            'flower_language_short': '순수한 사랑, 감사',
            'flower_language_long': '순수한 사랑, 감사',
            'image_key': 'bouvardia-wh',
            'image_url': 'https://cdn.plainflower.club/flowers/bouvardia-wh.png'
        },
        {
            'uid': 'iberis-wh',
            'flower_id': 'iberis-wh',
            'flower_slug': 'iberis',
            'color_code': 'wh',
            'name_ko': '이베리스',
            'name_en': 'Iberis',
            'scientific_name': 'Iberis sempervirens',
            'is_main': True,
            'base_color': 'wh',
            'alt_colors': '미니멀,내추럴,우아함',
            'moods': '순수,감사,평온',
            'emotions': '감사전달,인테리어,위로·쾌유',
            'contexts': 'Spring 03-05',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium',
            'features': 'tiny white clusters,low growth habit,soft dome shape,gentle layering,clean aura',
            'flower_language_short': '순결, 겸손, 고요함',
            'flower_language_long': '조용한 마음을 전해요',
            'image_key': 'iberis-wh',
            'image_url': 'https://cdn.plainflower.club/flowers/iberis-wh.png'
        },
        {
            'uid': 'spiraea-wh',
            'flower_id': 'spiraea-wh',
            'flower_slug': 'spiraea',
            'color_code': 'wh',
            'name_ko': '조팝나무',
            'name_en': 'Spiraea',
            'scientific_name': 'Spiraea prunifolia',
            'is_main': True,
            'base_color': 'wh',
            'alt_colors': '내추럴,우아함,미니멀',
            'moods': '순수,애틋함,평온',
            'emotions': '인테리어,위로·쾌유,자기선물',
            'contexts': 'Spring 03-05',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium',
            'features': 'cascading white clusters,curved lines,delicate petals,airy flow,gentle rhythm',
            'flower_language_short': '순결, 고결, 첫사랑',
            'flower_language_long': '순수한 마음을 전해요',
            'image_key': 'spiraea-wh',
            'image_url': 'https://cdn.plainflower.club/flowers/spiraea-wh.png'
        },
        {
            'uid': 'calla-lily-wh',
            'flower_id': 'calla-lily-wh',
            'flower_slug': 'calla-lily',
            'color_code': 'wh',
            'name_ko': '카라',
            'name_en': 'Calla Lily',
            'scientific_name': 'Zantedeschia aethiopica',
            'is_main': True,
            'base_color': 'wh',
            'alt_colors': '미니멀,우아함,모던',
            'moods': '평온,존엄,위로',
            'emotions': '인테리어,위로·쾌유,자기선물',
            'contexts': 'Spring/Summer 03-08',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium',
            'features': 'elegant white trumpet,clean curve,sculptural shape,serene finish,modern presence',
            'flower_language_short': '순결, 존엄, 위로',
            'flower_language_long': '고요한 위로를 담았어요',
            'image_key': 'calla-lily-wh',
            'image_url': 'https://cdn.plainflower.club/flowers/calla-lily-wh.png'
        },
        
        # 오렌지 색상
        {
            'uid': '975d0276',
            'flower_id': 'cockscomb-or',
            'flower_slug': 'cockscomb',
            'color_code': 'or',
            'name_ko': '맨드라미',
            'name_en': 'Cockscomb',
            'scientific_name': 'Celosia cristata',
            'is_main': True,
            'base_color': 'or',
            'alt_colors': '비비드,시크,모던',
            'moods': '축하,격려,기쁨',
            'emotions': '기념일,응원·격려,자기선물',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'vivid,energetic,lively,warm',
            'flower_language_short': '열정, 생동감',
            'flower_language_long': '열정의 마음을 담았어요',
            'image_key': 'cockscomb-or',
            'image_url': 'https://cdn.plainflower.club/flowers/cockscomb-or.png'
        },
        {
            'uid': 'alstroemeria-or',
            'flower_id': 'alstroemeria-or',
            'flower_slug': 'alstroemeria',
            'color_code': 'or',
            'name_ko': '알스트로메리아',
            'name_en': 'Alstroemeria',
            'scientific_name': 'Alstroemeria spp.',
            'is_main': True,
            'base_color': 'or',
            'alt_colors': '비비드,러블리,내추럴',
            'moods': '기쁨,응원,축하',
            'emotions': '응원·격려,생일,기념일',
            'contexts': 'All Season 01-12',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'bright,cheerful,warm,energetic',
            'flower_language_short': '밝은 에너지로 응원해요',
            'flower_language_long': '밝은 에너지로 응원해요',
            'image_key': 'alstroemeria-or',
            'image_url': 'https://cdn.plainflower.club/flowers/alstroemeria-or.png'
        },
        
        # 레드 색상
        {
            'uid': 'eec78466',
            'flower_id': 'cockscomb-rd',
            'flower_slug': 'cockscomb',
            'color_code': 'rd',
            'name_ko': '맨드라미',
            'name_en': 'Cockscomb',
            'scientific_name': 'Celosia cristata',
            'is_main': True,
            'base_color': 'rd',
            'alt_colors': '비비드,시크,로맨틱',
            'moods': '설렘,용기,축하',
            'emotions': '고백,기념일,승진·합격',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'passionate,bold,intense,vibrant',
            'flower_language_short': '불타는 사랑, 열정',
            'flower_language_long': '불타는 사랑, 열정',
            'image_key': 'cockscomb-rd',
            'image_url': 'https://cdn.plainflower.club/flowers/cockscomb-rd.png'
        },
        {
            'uid': 'carnation-rd',
            'flower_id': 'carnation-rd',
            'flower_slug': 'carnation',
            'color_code': 'rd',
            'name_ko': '카네이션',
            'name_en': 'Carnation',
            'scientific_name': 'Dianthus caryophyllus',
            'is_main': True,
            'base_color': 'rd',
            'alt_colors': '클래식,로맨틱,우아함',
            'moods': '사랑,자부심,감사',
            'emotions': '감사전달,기념일,승진·합격',
            'contexts': 'All Season 01-12',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'ruffled red petals,bold fullness,classic elegance,rich tone,heartfelt bloom',
            'flower_language_short': '사랑, 존경, 감사',
            'flower_language_long': '깊은 사랑을 전해요',
            'image_key': 'carnation-rd',
            'image_url': 'https://cdn.plainflower.club/flowers/carnation-rd.png'
        },
        
        # 옐로우 색상
        {
            'uid': '21c1aef6',
            'flower_id': 'drumstick-flower-yl',
            'flower_slug': 'drumstick-flower',
            'color_code': 'yl',
            'name_ko': '골든볼',
            'name_en': 'Drumstick Flower',
            'scientific_name': 'Craspedia globosa',
            'is_main': True,
            'base_color': 'yl',
            'alt_colors': '비비드,러블리,미니멀',
            'moods': '기쁨,희망,감사',
            'emotions': '생일,응원·격려,인테리어',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'bright,cheerful,joyful,sunny',
            'flower_language_short': '영원한 행복, 감사',
            'flower_language_long': '영원한 행복, 감사',
            'image_key': 'drumstick-flower-yl',
            'image_url': 'https://cdn.plainflower.club/flowers/drumstick-flower-yl.png'
        },
        {
            'uid': 'dahlia-yl',
            'flower_id': 'dahlia-yl',
            'flower_slug': 'dahlia',
            'color_code': 'yl',
            'name_ko': '다알리아',
            'name_en': 'Dahlia',
            'scientific_name': 'Dahlia pinnata',
            'is_main': True,
            'base_color': 'yl',
            'alt_colors': '비비드,러블리,미니멀',
            'moods': '기쁨,축하,희망',
            'emotions': '생일,승진·합격,응원·격려',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'cheerful,sunny,joyful,bright',
            'flower_language_short': '우정, 행복',
            'flower_language_long': '우정, 행복',
            'image_key': 'dahlia-yl',
            'image_url': 'https://cdn.plainflower.club/flowers/dahlia-yl.png'
        },
        {
            'uid': 'freesia-yl',
            'flower_id': 'freesia-yl',
            'flower_slug': 'freesia',
            'color_code': 'yl',
            'name_ko': '프리지아',
            'name_en': 'Freesia',
            'scientific_name': 'Freesia refracta',
            'is_main': True,
            'base_color': 'yl',
            'alt_colors': '러블리,비비드,내추럴',
            'moods': '기쁨,감사,희망',
            'emotions': '감사전달,생일,응원·격려',
            'contexts': 'Spring 03-05',
            'season_months': 'Spring 03-05',
            'price_tier': 'medium',
            'features': 'sunny yellow trumpet,sweet scent,gentle arch,vibrant fullness,cheerful glow',
            'flower_language_short': '감사, 기쁨, 희망',
            'flower_language_long': '밝은 감사를 전해요',
            'image_key': 'freesia-yl',
            'image_url': 'https://cdn.plainflower.club/flowers/freesia-yl.png'
        },
        {
            'uid': 'sunflower-yl',
            'flower_id': 'sunflower-yl',
            'flower_slug': 'sunflower',
            'color_code': 'yl',
            'name_ko': '해바라기',
            'name_en': 'Sunflower',
            'scientific_name': 'Helianthus annuus',
            'is_main': True,
            'base_color': 'yl',
            'alt_colors': '비비드,내추럴,러블리',
            'moods': '희망,격려,자부심',
            'emotions': '응원·격려,생일,승진·합격',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'golden yellow rays,bold round center,upright posture,radiant energy,cheerful structure',
            'flower_language_short': '희망, 존경, 격려',
            'flower_language_long': '밝은 응원을 담았어요',
            'image_key': 'sunflower-yl',
            'image_url': 'https://cdn.plainflower.club/flowers/sunflower-yl.png'
        },
        
        # 핑크 색상
        {
            'uid': 'dahlia-pk',
            'flower_id': 'dahlia-pk',
            'flower_slug': 'dahlia',
            'color_code': 'pk',
            'name_ko': '다알리아',
            'name_en': 'Dahlia',
            'scientific_name': 'Dahlia pinnata',
            'is_main': True,
            'base_color': 'pk',
            'alt_colors': '로맨틱,러블리,파스텔',
            'moods': '감사,애틋함,기쁨',
            'emotions': '감사전달,생일,자기선물',
            'contexts': 'Summer/Fall 06-11',
            'season_months': 'Summer/Fall 06-11',
            'price_tier': 'medium',
            'features': 'romantic,tender,warm,soft',
            'flower_language_short': '감사의 마음, 애정',
            'flower_language_long': '감사의 마음, 애정',
            'image_key': 'dahlia-pk',
            'image_url': 'https://cdn.plainflower.club/flowers/dahlia-pk.png'
        },
        {
            'uid': 'carnation-pk',
            'flower_id': 'carnation-pk',
            'flower_slug': 'carnation',
            'color_code': 'pk',
            'name_ko': '카네이션',
            'name_en': 'Carnation',
            'scientific_name': 'Dianthus caryophyllus',
            'is_main': True,
            'base_color': 'pk',
            'alt_colors': '로맨틱,러블리,파스텔',
            'moods': '감사,기쁨,설렘',
            'emotions': '감사전달,생일,기념일',
            'contexts': 'All Season 01-12',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'soft pink frills,gentle charm,cheerful tone,warm fullness,sweet texture',
            'flower_language_short': '감사, 애정, 행복',
            'flower_language_long': '고마운 마음을 전해요',
            'image_key': 'carnation-pk',
            'image_url': 'https://cdn.plainflower.club/flowers/carnation-pk.png'
        },
        
        # 블루 색상
        {
            'uid': 'oxypetalum-bl',
            'flower_id': 'oxypetalum-bl',
            'flower_slug': 'oxypetalum',
            'color_code': 'bl',
            'name_ko': '옥시페탈럼',
            'name_en': 'Oxypetalum',
            'scientific_name': 'Oxypetalum coeruleum',
            'is_main': True,
            'base_color': 'bl',
            'alt_colors': '내추럴,파스텔,러블리',
            'moods': '희망,설렘,격려',
            'emotions': '응원·격려,자기선물,고백',
            'contexts': 'Spring/Summer 03-08',
            'season_months': 'Spring/Summer 03-08',
            'price_tier': 'medium',
            'features': 'soft sky blue petals,velvet texture,five-pointed star,gentle curves,airy bloom',
            'flower_language_short': '희망, 순수, 격려',
            'flower_language_long': '희망의 마음을 담았어요',
            'image_key': 'oxypetalum-bl',
            'image_url': 'https://cdn.plainflower.club/flowers/oxypetalum-bl.png'
        },
        {
            'uid': 'gentian-bl',
            'flower_id': 'gentian-bl',
            'flower_slug': 'gentian',
            'color_code': 'bl',
            'name_ko': '용담',
            'name_en': 'Gentian',
            'scientific_name': 'Gentiana andrewsii',
            'is_main': True,
            'base_color': 'bl',
            'alt_colors': '미니멀,우아함,시크',
            'moods': '위로,성숙함,진심',
            'emotions': '위로·쾌유,자기선물,인테리어',
            'contexts': 'Fall 09-11',
            'season_months': 'Fall 09-11',
            'price_tier': 'medium',
            'features': 'closed blue bloom,upright tube shape,subtle glow,thick texture,meditative form',
            'flower_language_short': '위로, 고결함, 성숙함',
            'flower_language_long': '고요한 위로를 담았어요',
            'image_key': 'gentian-bl',
            'image_url': 'https://cdn.plainflower.club/flowers/gentian-bl.png'
        },
        
        # 연보라 색상
        {
            'uid': 'd4b5a8a8',
            'flower_id': 'lisianthus_ll',
            'flower_slug': 'lisianthus',
            'color_code': 'll',
            'name_ko': '리시안셔스',
            'name_en': 'Lisianthus',
            'scientific_name': 'Eustoma grandiflorum',
            'is_main': True,
            'base_color': 'll',
            'alt_colors': '우아함,클래식,로맨틱',
            'moods': '애틋함,평온,그리움',
            'emotions': '기념일,위로·쾌유,인테리어',
            'contexts': 'All Season 01-12',
            'season_months': 'All Season 01-12',
            'price_tier': 'medium',
            'features': 'elegant,calm,graceful,dreamy',
            'flower_language_short': '우아함, 클래식, 로맨틱',
            'flower_language_long': '우아함, 클래식, 로맨틱',
            'image_key': 'lisianthus_ll',
            'image_url': 'https://cdn.plainflower.club/flowers/lisianthus_ll.png'
        }
    ]
    
    return all_flowers

def main():
    """메인 함수"""
    print("🔄 구글 스프레드시트 데이터 업데이트 시작...")
    
    # 완전한 꽃 데이터 생성
    all_flowers = create_complete_spreadsheet_data()
    
    # 기존 파일에 저장
    with open('data/spreadsheet_flowers.json', 'w', encoding='utf-8') as f:
        json.dump(all_flowers, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 구글 스프레드시트 데이터 업데이트 완료!")
    print(f"   📋 총 꽃 데이터: {len(all_flowers)}개")
    
    # 색상별 통계
    color_stats = {}
    for flower in all_flowers:
        color = flower['base_color']
        color_stats[color] = color_stats.get(color, 0) + 1
    
    print(f"   🎨 색상별 통계:")
    for color, count in color_stats.items():
        print(f"      - {color}: {count}개")

if __name__ == "__main__":
    main()
