#!/usr/bin/env python3
"""
구글 스프레드시트의 is_main 값을 현재 시스템에 동기화
"""
import pandas as pd
import json
from pathlib import Path

def analyze_is_main_criteria():
    """is_main 기준 분석"""
    print("🔍 is_main 기준 분석")
    print("=" * 50)
    
    # 현재 flowers_enhanced.csv 분석
    flowers_df = pd.read_csv("data/flowers_enhanced.csv")
    
    print("📊 현재 데이터 분석:")
    print(f"   총 꽃 종류: {len(flowers_df)}개")
    print(f"   focal=1인 꽃: {len(flowers_df[flowers_df['focal'] == 1])}개")
    print(f"   filler=1인 꽃: {len(flowers_df[flowers_df['filler'] == 1])}개")
    print(f"   line=1인 꽃: {len(flowers_df[flowers_df['line'] == 1])}개")
    print(f"   foliage=1인 꽃: {len(flowers_df[flowers_df['foliage'] == 1])}개")
    
    print("\n🌺 focal=1인 꽃들 (메인 후보):")
    focal_flowers = flowers_df[flowers_df['focal'] == 1]
    for _, row in focal_flowers.iterrows():
        print(f"   - {row['name_ko']} ({row['color_palette_primary']}) - {row['price_tier']}")
    
    print("\n🌸 filler=1인 꽃들 (필러 후보):")
    filler_flowers = flowers_df[flowers_df['filler'] == 1]
    for _, row in filler_flowers.iterrows():
        print(f"   - {row['name_ko']} ({row['color_palette_primary']}) - {row['price_tier']}")

def propose_is_main_criteria():
    """is_main 기준 제안"""
    print("\n💡 is_main 기준 제안")
    print("=" * 50)
    
    print("1️⃣ 꽃 크기 기준:")
    print("   - 대형 꽃 (5cm 이상): 메인")
    print("   - 중형 꽃 (3-5cm): 서브")
    print("   - 소형 꽃 (3cm 미만): 필러")
    
    print("\n2️⃣ 시각적 임팩트 기준:")
    print("   - 눈에 잘 띄는 꽃: 메인")
    print("   - 보조적인 꽃: 서브/필러")
    
    print("\n3️⃣ 가격대 기준:")
    print("   - 고급 꽃 (8,000원 이상): 메인")
    print("   - 중급 꽃 (4,000-8,000원): 서브")
    print("   - 보급형 꽃 (4,000원 미만): 필러")
    
    print("\n4️⃣ 역할 기준 (현재 focal 칼럼):")
    print("   - focal=1: 메인 꽃")
    print("   - filler=1: 필러 꽃")
    print("   - line=1: 라인 꽃")
    print("   - foliage=1: 그린 소재")

def update_flower_roles():
    """꽃 역할 업데이트"""
    print("\n🔄 꽃 역할 업데이트")
    print("=" * 50)
    
    flowers_df = pd.read_csv("data/flowers_enhanced.csv")
    
    # focal=1인 꽃들을 메인으로 설정
    flowers_df['is_main'] = (flowers_df['focal'] == 1).astype(int)
    
    # 결과 확인
    main_flowers = flowers_df[flowers_df['is_main'] == 1]
    sub_flowers = flowers_df[flowers_df['is_main'] == 0]
    
    print(f"✅ 메인 꽃: {len(main_flowers)}개")
    for _, row in main_flowers.iterrows():
        print(f"   - {row['name_ko']} ({row['color_palette_primary']})")
    
    print(f"\n✅ 서브/필러 꽃: {len(sub_flowers)}개")
    for _, row in sub_flowers.iterrows():
        print(f"   - {row['name_ko']} ({row['color_palette_primary']})")
    
    # 파일 저장
    flowers_df.to_csv("data/flowers_enhanced_updated.csv", index=False)
    print(f"\n💾 업데이트된 파일 저장: data/flowers_enhanced_updated.csv")

def create_flower_roles_mapping():
    """꽃 역할 매핑 생성"""
    print("\n🗺️ 꽃 역할 매핑 생성")
    print("=" * 50)
    
    flowers_df = pd.read_csv("data/flowers_enhanced.csv")
    
    # 역할별 매핑 생성
    flower_roles = {}
    
    for _, row in flowers_df.iterrows():
        flower_name = row['name_ko']
        color = row['color_palette_primary']
        key = f"{flower_name}_{color}"
        
        if row['focal'] == 1:
            role = "main"
        elif row['filler'] == 1:
            role = "filler"
        elif row['line'] == 1:
            role = "line"
        elif row['foliage'] == 1:
            role = "foliage"
        else:
            role = "sub"
        
        flower_roles[key] = role
    
    # JSON 파일로 저장
    with open("data/flower_roles_mapping.json", "w", encoding="utf-8") as f:
        json.dump(flower_roles, f, ensure_ascii=False, indent=2)
    
    print(f"💾 꽃 역할 매핑 저장: data/flower_roles_mapping.json")
    
    # 역할별 통계
    role_counts = {}
    for role in flower_roles.values():
        role_counts[role] = role_counts.get(role, 0) + 1
    
    print("\n📊 역할별 통계:")
    for role, count in role_counts.items():
        print(f"   {role}: {count}개")

def main():
    """메인 함수"""
    print("🎯 구글 스프레드시트 is_main 동기화")
    print("=" * 70)
    
    # 1. 현재 기준 분석
    analyze_is_main_criteria()
    
    # 2. 기준 제안
    propose_is_main_criteria()
    
    # 3. 꽃 역할 업데이트
    update_flower_roles()
    
    # 4. 꽃 역할 매핑 생성
    create_flower_roles_mapping()
    
    print("\n✅ 동기화 완료!")

if __name__ == "__main__":
    main()


