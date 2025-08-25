#!/usr/bin/env python3
"""
Supabase Storage의 잘못된 파일명들 수정
"""
import os
import requests
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_storage_file_names():
    """Storage 파일명 수정"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ SUPABASE_URL과 SUPABASE_ANON_KEY 환경변수가 필요합니다")
            return False
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        logger.info("🔧 Storage 파일명 수정 시작...")
        
        # 수정할 파일명 매핑 (잘못된 이름 -> 올바른 이름)
        file_fixes = [
            {
                'wrong': 'tulip-.webp',
                'correct': 'tulip-wh.webp',
                'description': 'tulip 화이트'
            },
            {
                'wrong': 'stock-flower-.webp', 
                'correct': 'stock-flower-pu.webp',
                'description': 'stock-flower 퍼플'
            },
            {
                'wrong': 'scabiosa-.webp',
                'correct': 'scabiosa-wh.webp', 
                'description': 'scabiosa 화이트'
            },
            {
                'wrong': 'lily-.webp',
                'correct': 'lily-wh.webp',
                'description': 'lily 화이트'
            },
            {
                'wrong': 'babys-breath-.webp',
                'correct': 'babys-breath-wh.webp',
                'description': 'babys-breath 화이트'
            }
        ]
        
        fixed_count = 0
        
        for fix in file_fixes:
            wrong_name = fix['wrong']
            correct_name = fix['correct']
            description = fix['description']
            
            try:
                logger.info(f"🔧 수정 시도: {wrong_name} → {correct_name} ({description})")
                
                # 1. 잘못된 파일이 존재하는지 확인
                check_response = requests.head(
                    f"{supabase_url}/storage/v1/object/public/flowers/{wrong_name}",
                    headers=headers
                )
                
                if check_response.status_code == 200:
                    logger.info(f"✅ 잘못된 파일 존재: {wrong_name}")
                    
                    # 2. 올바른 파일이 이미 존재하는지 확인
                    correct_check = requests.head(
                        f"{supabase_url}/storage/v1/object/public/flowers/{correct_name}",
                        headers=headers
                    )
                    
                    if correct_check.status_code == 200:
                        logger.info(f"⚠️ 올바른 파일 이미 존재: {correct_name}")
                        logger.info(f"🗑️ 잘못된 파일 삭제: {wrong_name}")
                        
                        # 잘못된 파일 삭제
                        delete_response = requests.delete(
                            f"{supabase_url}/storage/v1/object/flowers/{wrong_name}",
                            headers=headers
                        )
                        
                        if delete_response.status_code in [200, 204]:
                            fixed_count += 1
                            logger.info(f"✅ 잘못된 파일 삭제 성공: {wrong_name}")
                        else:
                            logger.warning(f"⚠️ 삭제 실패: {wrong_name} - {delete_response.status_code}")
                    else:
                        logger.info(f"📝 올바른 파일 없음: {correct_name}")
                        logger.info(f"🔄 파일명 변경 시도: {wrong_name} → {correct_name}")
                        
                        # 파일명 변경 (복사 후 삭제)
                        copy_response = requests.post(
                            f"{supabase_url}/storage/v1/object/copy/flowers/{wrong_name}",
                            headers=headers,
                            json={'destination': f"flowers/{correct_name}"}
                        )
                        
                        if copy_response.status_code in [200, 201]:
                            # 원본 파일 삭제
                            delete_response = requests.delete(
                                f"{supabase_url}/storage/v1/object/flowers/{wrong_name}",
                                headers=headers
                            )
                            
                            if delete_response.status_code in [200, 204]:
                                fixed_count += 1
                                logger.info(f"✅ 파일명 변경 성공: {wrong_name} → {correct_name}")
                            else:
                                logger.warning(f"⚠️ 원본 삭제 실패: {wrong_name}")
                        else:
                            logger.warning(f"⚠️ 파일 복사 실패: {wrong_name} → {correct_name}")
                else:
                    logger.info(f"ℹ️ 잘못된 파일 없음: {wrong_name}")
                    
            except Exception as e:
                logger.error(f"❌ 수정 오류: {wrong_name} - {e}")
        
        logger.info(f"✅ Storage 파일명 수정 완료: {fixed_count}개 수정됨")
        
        # 수정 후 확인
        logger.info("🔍 수정 후 확인...")
        
        for fix in file_fixes:
            wrong_name = fix['wrong']
            correct_name = fix['correct']
            
            # 잘못된 파일이 삭제되었는지 확인
            wrong_check = requests.head(
                f"{supabase_url}/storage/v1/object/public/flowers/{wrong_name}",
                headers=headers
            )
            
            if wrong_check.status_code != 200:
                logger.info(f"✅ 잘못된 파일 삭제 확인: {wrong_name}")
            else:
                logger.warning(f"⚠️ 잘못된 파일 아직 존재: {wrong_name}")
            
            # 올바른 파일이 존재하는지 확인
            correct_check = requests.head(
                f"{supabase_url}/storage/v1/object/public/flowers/{correct_name}",
                headers=headers
            )
            
            if correct_check.status_code == 200:
                logger.info(f"✅ 올바른 파일 존재 확인: {correct_name}")
            else:
                logger.warning(f"⚠️ 올바른 파일 없음: {correct_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    fix_storage_file_names()
