#!/usr/bin/env python3
"""
자동 동기화를 위한 Cron Job 설정 스크립트
"""

import os
import sys
from datetime import datetime

def setup_cron_job():
    """Cron Job 설정"""
    
    # 현재 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 스크립트 경로
    sync_script = os.path.join(project_root, "scripts", "sync_flower_database.py")
    
    # Cron Job 명령어 생성
    cron_command = f"0 */6 * * * cd {project_root} && python {sync_script} >> logs/sync.log 2>&1"
    
    print("🔄 Cron Job 설정 중...")
    print(f"📁 프로젝트 경로: {project_root}")
    print(f"📝 스크립트 경로: {sync_script}")
    print(f"⏰ 실행 주기: 6시간마다 (매시 0분)")
    print(f"📋 Cron 명령어: {cron_command}")
    
    # 로그 디렉토리 생성
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Cron Job 추가
    try:
        import subprocess
        
        # 현재 cron 작업 확인
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        # 이미 설정되어 있는지 확인
        if "sync_flower_database.py" in current_cron:
            print("⚠️ 이미 동기화 Cron Job이 설정되어 있습니다.")
            return False
        
        # 새로운 cron 작업 추가
        new_cron = current_cron + f"\n{cron_command}\n"
        
        # 임시 파일에 저장
        temp_file = "/tmp/flower_sync_cron"
        with open(temp_file, 'w') as f:
            f.write(new_cron)
        
        # cron 작업 설치
        subprocess.run(['crontab', temp_file], check=True)
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        print("✅ Cron Job 설정 완료!")
        print("📅 다음 실행 시간: 6시간 후")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Cron Job 설정 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def remove_cron_job():
    """Cron Job 제거"""
    try:
        import subprocess
        
        # 현재 cron 작업 확인
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        # 동기화 관련 cron 작업 제거
        lines = current_cron.split('\n')
        filtered_lines = [line for line in lines if "sync_flower_database.py" not in line]
        
        new_cron = '\n'.join(filtered_lines)
        
        # 임시 파일에 저장
        temp_file = "/tmp/flower_sync_cron"
        with open(temp_file, 'w') as f:
            f.write(new_cron)
        
        # cron 작업 설치
        subprocess.run(['crontab', temp_file], check=True)
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        print("✅ Cron Job 제거 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Cron Job 제거 실패: {e}")
        return False

def show_cron_status():
    """현재 Cron Job 상태 확인"""
    try:
        import subprocess
        
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        if "sync_flower_database.py" in current_cron:
            print("✅ 동기화 Cron Job이 설정되어 있습니다.")
            for line in current_cron.split('\n'):
                if "sync_flower_database.py" in line:
                    print(f"📋 설정된 작업: {line}")
        else:
            print("❌ 동기화 Cron Job이 설정되어 있지 않습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ Cron Job 상태 확인 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python setup_cron.py setup    # Cron Job 설정")
        print("  python setup_cron.py remove   # Cron Job 제거")
        print("  python setup_cron.py status   # Cron Job 상태 확인")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_cron_job()
    elif command == "remove":
        remove_cron_job()
    elif command == "status":
        show_cron_status()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()


