import os
import requests
from pathlib import Path
import json

# Supabase 설정
SUPABASE_URL = "YOUR_SUPABASE_URL"  # 여기에 실제 Supabase URL 입력
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"  # 여기에 실제 Supabase Key 입력
BUCKET_NAME = "flower-images"

def upload_image_to_supabase(file_path, file_name):
    """이미지를 Supabase Storage에 업로드"""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_name}"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/webp"
    }
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
            
        if response.status_code == 200:
            print(f"✅ 업로드 성공: {file_name}")
            return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
        else:
            print(f"❌ 업로드 실패: {file_name} - {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 업로드 오류: {file_name} - {e}")
        return None

def main():
    """모든 이미지를 Supabase에 업로드"""
    images_dir = Path("data/images_webp")
    uploaded_urls = {}
    
    print("🚀 Supabase Storage에 이미지 업로드 시작...")
    
    # 모든 폴더 순회
    for folder in images_dir.iterdir():
        if folder.is_dir():
            flower_name = folder.name
            uploaded_urls[flower_name] = {}
            
            print(f"\n📁 {flower_name} 폴더 처리 중...")
            
            # 각 폴더의 이미지 파일들 처리
            for image_file in folder.iterdir():
                if image_file.is_file() and image_file.suffix == '.webp':
                    color_name = image_file.stem
                    file_name = f"{flower_name}/{color_name}.webp"
                    
                    # Supabase에 업로드
                    url = upload_image_to_supabase(image_file, file_name)
                    if url:
                        uploaded_urls[flower_name][color_name] = url
    
    # 업로드된 URL들을 JSON 파일로 저장
    with open("supabase_image_urls.json", "w", encoding="utf-8") as f:
        json.dump(uploaded_urls, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 업로드 완료! 총 {len(uploaded_urls)} 개 폴더 처리")
    print("📄 URL 목록이 'supabase_image_urls.json' 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()


