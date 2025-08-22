#!/usr/bin/env python3
"""
Supabase 자동 동기화를 위한 Cron Job 설정 스크립트
"""

import subprocess
import os
from pathlib import Path

def setup_supabase_cron_job():
    """Supabase 자동 동기화 Cron Job 설정"""
    try:
        # 프로젝트 루트 디렉토리
        project_root = Path(__file__).resolve().parent.parent
        supabase_script = project_root / "scripts" / "supabase_data_sync.py"
        
        # Cron Job 명령어 생성 (6시간마다 실행)
        cron_command = f"0 */6 * * * cd {project_root} && python {supabase_script} >> logs/supabase_sync.log 2>&1"
        
        print("🔄 Supabase 자동 동기화 Cron Job 설정 중...")
        print(f"📁 프로젝트 경로: {project_root}")
        print(f"📋 Cron 명령어: {cron_command}")
        
        # 로그 디렉토리 생성
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Cron Job 추가
        print("📝 Cron Job 추가 중...")
        
        # 현재 cron 작업 확인
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        # 이미 설정되어 있는지 확인
        if "supabase_data_sync.py" in current_cron:
            print("⚠️ 이미 Supabase 자동 동기화 Cron Job이 설정되어 있습니다.")
            return
        
        # 새로운 cron 작업 추가
        new_cron = current_cron + f"\n{cron_command}\n"
        
        # 임시 파일에 저장
        temp_file = "/tmp/supabase_sync_cron"
        with open(temp_file, 'w') as f:
            f.write(new_cron)
        
        # cron 작업 설치
        subprocess.run(['crontab', temp_file], check=True)
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        print("✅ Supabase 자동 동기화 Cron Job 설정 완료!")
        print("📊 6시간마다 자동으로 Supabase에 데이터가 동기화됩니다.")
        
    except Exception as e:
        print(f"❌ Cron Job 설정 실패: {e}")

def remove_supabase_cron_job():
    """Supabase 자동 동기화 Cron Job 제거"""
    try:
        print("🔄 Supabase 자동 동기화 Cron Job 제거 중...")
        
        # 현재 cron 작업 확인
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        # Supabase 자동 동기화 관련 cron 작업 제거
        lines = current_cron.split('\n')
        filtered_lines = [line for line in lines if "supabase_data_sync.py" not in line]
        new_cron = '\n'.join(filtered_lines)
        
        # 임시 파일에 저장
        temp_file = "/tmp/supabase_sync_cron"
        with open(temp_file, 'w') as f:
            f.write(new_cron)
        
        # cron 작업 설치
        subprocess.run(['crontab', temp_file], check=True)
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        print("✅ Supabase 자동 동기화 Cron Job 제거 완료!")
        
    except Exception as e:
        print(f"❌ Cron Job 제거 실패: {e}")

def show_supabase_cron_status():
    """현재 Supabase 자동 동기화 Cron Job 상태 확인"""
    try:
        print("📊 Supabase 자동 동기화 Cron Job 상태 확인 중...")
        
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        if "supabase_data_sync.py" in current_cron:
            print("✅ Supabase 자동 동기화 Cron Job이 설정되어 있습니다.")
            for line in current_cron.split('\n'):
                if "supabase_data_sync.py" in line:
                    print(f"📋 설정된 작업: {line}")
        else:
            print("❌ Supabase 자동 동기화 Cron Job이 설정되어 있지 않습니다.")
            
    except Exception as e:
        print(f"❌ Cron Job 상태 확인 실패: {e}")

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python setup_supabase_cron.py setup    # Supabase 자동 동기화 Cron Job 설정")
        print("  python setup_supabase_cron.py remove   # Supabase 자동 동기화 Cron Job 제거")
        print("  python setup_supabase_cron.py status   # Supabase 자동 동기화 Cron Job 상태 확인")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_supabase_cron_job()
    elif command == "remove":
        remove_supabase_cron_job()
    elif command == "status":
        show_supabase_cron_status()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()
