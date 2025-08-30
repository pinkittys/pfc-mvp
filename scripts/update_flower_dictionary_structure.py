#!/usr/bin/env python3
"""
flower_dictionary.json의 flower_meanings 구조를 명확한 이름으로 변경하는 스크립트
primary → meanings (꽃말)
secondary → moods (무드)  
other → emotions (감정)
"""

import json
import os
from datetime import datetime

def update_flower_dictionary_structure():
    """flower_dictionary.json의 구조를 명확한 이름으로 변경"""
    
    input_file = "data/flower_dictionary.json"
    backup_file = f"data/flower_dictionary.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("🔄 flower_dictionary.json 구조 업데이트 시작...")
    
    try:
        # 1. 백업 생성
        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 백업 저장
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 백업 생성: {backup_file}")
        
        # 2. 구조 변경
        if "flowers" in data:
            updated_count = 0
            for flower_id, flower_data in data["flowers"].items():
                if "flower_meanings" in flower_data:
                    flower_meanings = flower_data["flower_meanings"]
                    
                    # 기존 필드 백업
                    primary = flower_meanings.get("primary", [])
                    secondary = flower_meanings.get("secondary", [])
                    other = flower_meanings.get("other", [])
                    phrases = flower_meanings.get("phrases", [])
                    
                    # 새로운 구조로 변경
                    flower_data["flower_meanings"] = {
                        "meanings": primary,      # primary → meanings (꽃말)
                        "moods": secondary,       # secondary → moods (무드)
                        "emotions": other,        # other → emotions (감정)
                        "phrases": phrases        # phrases (문장형 꽃말)
                    }
                    
                    updated_count += 1
                    print(f"🔄 {flower_id}: 구조 업데이트 완료")
        
        # 3. 업데이트된 파일 저장
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {updated_count}개 꽃 데이터 구조 업데이트 완료!")
        print(f"📁 업데이트된 파일: {input_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 구조 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = update_flower_dictionary_structure()
    
    if success:
        print("🎉 flower_dictionary.json 구조 업데이트 성공!")
        print("\n📋 변경 사항:")
        print("- primary → meanings (꽃말)")
        print("- secondary → moods (무드)")
        print("- other → emotions (감정)")
        print("- phrases (문장형 꽃말) - 유지")
    else:
        print("❌ 구조 업데이트 실패!")

if __name__ == "__main__":
    main()
