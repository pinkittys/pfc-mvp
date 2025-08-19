import base64
import json
from pathlib import Path

def image_to_base64(image_path):
    """이미지를 Base64로 인코딩"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/webp;base64,{encoded_string}"
    except Exception as e:
        print(f"❌ Base64 변환 실패: {image_path} - {e}")
        return None

def main():
    """모든 이미지를 Base64로 변환"""
    images_dir = Path("data/images_webp")
    base64_images = {}
    
    print("🔄 이미지를 Base64로 변환 중...")
    
    # 모든 폴더 순회
    for folder in images_dir.iterdir():
        if folder.is_dir():
            flower_name = folder.name
            base64_images[flower_name] = {}
            
            print(f"📁 {flower_name} 폴더 처리 중...")
            
            # 각 폴더의 이미지 파일들 처리
            for image_file in folder.iterdir():
                if image_file.is_file() and image_file.suffix == '.webp':
                    color_name = image_file.stem
                    base64_data = image_to_base64(image_file)
                    if base64_data:
                        base64_images[flower_name][color_name] = base64_data
                        print(f"  ✅ {color_name}.webp 변환 완료")
    
    # Base64 데이터를 JSON 파일로 저장
    with open("base64_images.json", "w", encoding="utf-8") as f:
        json.dump(base64_images, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 변환 완료! 총 {len(base64_images)} 개 폴더 처리")
    print("📄 Base64 데이터가 'base64_images.json' 파일에 저장되었습니다.")
    print("💡 이제 이 데이터를 사용하여 이미지를 직접 HTML에 임베드할 수 있습니다.")

if __name__ == "__main__":
    main()


