#!/usr/bin/env python3
"""
샘플 스토리 자동 체크 스크립트
- 이미지 URL 접근 가능 여부
- 색상 키워드와 이미지 색상 일치 여부
- 댓글 내용과 추천 꽃 일치 여부
"""

import requests
import json
import re
from typing import Dict, List, Tuple

def check_image_accessibility(url: str) -> bool:
    """이미지 URL 접근 가능 여부 확인"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def extract_color_from_filename(filename: str) -> str:
    """파일명에서 색상 추출"""
    color_mapping = {
        'pk': '핑크', 'pink': '핑크',
        'rd': '빨강', 'red': '빨강',
        'wh': '화이트', 'white': '화이트',
        'yl': '옐로우', 'yellow': '옐로우',
        'pu': '퍼플', 'purple': '퍼플',
        'bl': '블루', 'blue': '블루',
        'gr': '그린', 'green': '그린',
        'or': '오렌지', 'orange': '오렌지',
        'll': '라벤더', 'lavender': '라벤더'
    }
    
    # 파일명에서 색상 코드 추출
    for color_code, color_name in color_mapping.items():
        if f"-{color_code}." in filename:
            return color_name
    
    return "알 수 없음"

def check_sample_stories():
    """샘플 스토리 전체 체크"""
    print("🔍 샘플 스토리 자동 체크 시작...\n")
    
    issues = []
    
    # S01~S30 체크
    for i in range(1, 31):
        story_id = f"S{i:02d}"
        
        try:
            # API 호출
            response = requests.post(
                f"http://localhost:8000/api/v1/sample-stories/{story_id}/recommend",
                timeout=10
            )
            
            if response.status_code != 200:
                issues.append(f"❌ {story_id}: API 호출 실패 ({response.status_code})")
                continue
                
            data = response.json()
            
            # 1. 이미지 URL 접근 가능 여부 체크
            flower_image_url = data.get('flower_image_url', '')
            calligraphy_image_url = data.get('calligraphy_image_url', '')
            
            if not check_image_accessibility(flower_image_url):
                issues.append(f"❌ {story_id}: 꽃 이미지 접근 불가 - {flower_image_url}")
            
            if not check_image_accessibility(calligraphy_image_url):
                issues.append(f"❌ {story_id}: 캘리그래피 이미지 접근 불가 - {calligraphy_image_url}")
            
            # 2. 색상 일치 여부 체크
            flower_name = data.get('flower_name', '')
            comment = data.get('comment', '')
            
            # 파일명에서 색상 추출
            flower_filename = flower_image_url.split('/')[-1] if flower_image_url else ''
            image_color = extract_color_from_filename(flower_filename)
            
            # 댓글에서 색상 언급 확인
            comment_colors = []
            color_keywords = ['핑크', '빨강', '레드', '화이트', '옐로우', '퍼플', '블루', '그린', '오렌지', '라벤더', '연보라']
            for color in color_keywords:
                if color in comment:
                    comment_colors.append(color)
            
            # 색상 일치 여부 체크
            if comment_colors and image_color not in comment_colors:
                issues.append(f"⚠️ {story_id}: 색상 불일치 - 이미지:{image_color}, 댓글:{comment_colors}")
            
            # 3. 꽃 이름 일치 여부 체크
            if flower_name and flower_name not in comment:
                issues.append(f"⚠️ {story_id}: 꽃 이름 불일치 - 추천:{flower_name}, 댓글에 언급 없음")
            
            print(f"✅ {story_id}: {flower_name} ({image_color}) - 정상")
            
        except Exception as e:
            issues.append(f"❌ {story_id}: 오류 발생 - {str(e)}")
    
    # 결과 출력
    print(f"\n📊 체크 완료!")
    print(f"✅ 정상: {30 - len(issues)}개")
    print(f"❌ 문제: {len(issues)}개")
    
    if issues:
        print(f"\n🚨 발견된 문제들:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n🎉 모든 샘플 스토리가 정상입니다!")

if __name__ == "__main__":
    check_sample_stories()
