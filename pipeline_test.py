"""
이미지 생성 실험 파이프라인
Gemini + NanoBana API를 이용한 꽃 이미지 생성 실험
"""
import os
import json
import time
from datetime import datetime
from config.settings import GEMINI_API_KEY, NANOBANA_API_KEY, EXPERIMENT_CONFIG

class ImageGenerationPipeline:
    def __init__(self):
        self.gemini_client = None
        self.nanobana_client = None
        self.setup_clients()
    
    def setup_clients(self):
        """API 클라이언트 초기화"""
        try:
            # Gemini 설정
            if GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini 클라이언트 초기화 완료")
            else:
                print("⚠️ Gemini API 키가 설정되지 않음")
            
            # NanoBana 설정
            if NANOBANA_API_KEY:
                import requests
                self.nanobana_client = requests
                print("✅ NanoBana 클라이언트 초기화 완료")
            else:
                print("⚠️ NanoBana API 키가 설정되지 않음")
                
        except Exception as e:
            print(f"❌ 클라이언트 초기화 실패: {e}")
    
    def generate_prompt_with_gemini(self, flower_name, emotion, color, situation):
        """Gemini로 이미지 생성 프롬프트 생성"""
        if not self.gemini_client:
            return None
            
        prompt_template = f"""
        꽃 이미지 생성 프롬프트를 만들어주세요.
        
        꽃: {flower_name}
        감정: {emotion}
        색상: {color}
        상황: {situation}
        
        다음 스타일로 프롬프트를 생성해주세요:
        - 사진처럼 사실적인 스타일
        - 부드러운 조명
        - 깔끔한 배경
        - 꽃의 아름다움이 돋보이도록
        
        영어로 프롬프트를 작성해주세요.
        """
        
        try:
            response = self.gemini_client.generate_content(prompt_template)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini 프롬프트 생성 실패: {e}")
            return None
    
    def generate_image_with_nanobana(self, prompt, style="photorealistic"):
        """NanoBana로 이미지 생성"""
        if not self.nanobana_client:
            return None
            
        # NanoBana API 호출 (실제 API 문서에 따라 수정 필요)
        headers = {
            "Authorization": f"Bearer {NANOBANA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "style": style,
            "width": 1024,
            "height": 1024,
            "quality": "high"
        }
        
        try:
            response = self.nanobana_client.post(
                "https://api.nanobana.com/v1/generate",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ NanoBana API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ NanoBana 이미지 생성 실패: {e}")
            return None
    
    def run_experiment(self):
        """전체 실험 실행"""
        print("🚀 이미지 생성 실험 시작")
        print("=" * 50)
        
        results = []
        
        for i, test_case in enumerate(EXPERIMENT_CONFIG["test_flowers"]):
            print(f"\n📸 실험 {i+1}: {test_case['name']}")
            
            # 1. Gemini로 프롬프트 생성
            prompt = self.generate_prompt_with_gemini(
                test_case["name"],
                test_case["emotion"], 
                test_case["color"],
                "꽃다발"
            )
            
            if not prompt:
                print("❌ 프롬프트 생성 실패")
                continue
                
            print(f"✅ 프롬프트: {prompt[:100]}...")
            
            # 2. NanoBana로 이미지 생성
            for style in EXPERIMENT_CONFIG["image_styles"]:
                print(f"🎨 스타일: {style}")
                
                image_result = self.generate_image_with_nanobana(prompt, style)
                
                if image_result:
                    # 결과 저장
                    result = {
                        "flower": test_case["name"],
                        "emotion": test_case["emotion"],
                        "color": test_case["color"],
                        "style": style,
                        "prompt": prompt,
                        "image_url": image_result.get("image_url"),
                        "created_at": datetime.now().isoformat()
                    }
                    results.append(result)
                    print(f"✅ 이미지 생성 완료: {style}")
                else:
                    print(f"❌ 이미지 생성 실패: {style}")
            
            # API 호출 간격 조절
            time.sleep(2)
        
        # 결과 저장
        self.save_results(results)
        print(f"\n🎉 실험 완료! 총 {len(results)}개 이미지 생성")
    
    def save_results(self, results):
        """실험 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 저장
        with open(f"test_results/experiment_results_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 로그 저장
        with open(f"logs/experiment_log_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(f"이미지 생성 실험 결과\n")
            f.write(f"실험 시간: {datetime.now()}\n")
            f.write(f"총 결과: {len(results)}개\n\n")
            
            for result in results:
                f.write(f"꽃: {result['flower']}\n")
                f.write(f"스타일: {result['style']}\n")
                f.write(f"이미지 URL: {result['image_url']}\n")
                f.write("-" * 30 + "\n")

if __name__ == "__main__":
    pipeline = ImageGenerationPipeline()
    pipeline.run_experiment()
