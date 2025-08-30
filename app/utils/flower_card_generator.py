import openai
import os
from app.models.schemas import EmotionAnalysis, FlowerMatch
from typing import List

def generate_flower_card_message(flower_match: FlowerMatch, emotion_analysis: List[EmotionAnalysis], story: str) -> str:
    """
    꽃 카드 메시지 생성 (영어 인용구 + 출처)
    """
    try:
        # 주요 감정 추출
        primary_emotion = emotion_analysis[0].emotion if emotion_analysis else "warmth"
        
        # 꽃 정보
        flower_name = flower_match.flower_name
        flower_keywords = ", ".join(flower_match.keywords) if flower_match.keywords else "beauty, grace"
        
        # 프롬프트 생성
        prompt = f"""
        Create a beautiful English flower card message for a Korean customer.
        
        Flower: {flower_name}
        Flower meaning: {flower_keywords}
        Primary emotion: {primary_emotion}
        Customer story: {story}
        
        Requirements:
        1. Use a meaningful quote from literature, poetry, or famous authors
        2. Include the source/author in parentheses
        3. Make it warm, personal, and suitable for a flower card
        4. Keep it concise (1-2 sentences)
        5. Focus on the flower's meaning and the emotion
        
        Format: "Quote here" - (Author/Source)
        
        Example style:
        "Every flower is a soul blossoming in nature" - (Gerard de Nerval)
        "Happiness held is the seed; happiness shared is the flower" - (John Harrigan)
        """
        
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a poetic flower card message writer who creates beautiful, meaningful quotes for flower gifts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        message = response.choices[0].message.content.strip()
        
        # 기본 메시지가 없으면 fallback
        if not message or len(message) < 10:
            return f"\"{flower_name} brings beauty and {primary_emotion} to your special day\" - (Flower Wisdom)"
        
        return message
        
    except Exception as e:
        print(f"❌ 꽃 카드 메시지 생성 오류: {e}")
        # Fallback 메시지
        return f"\"{flower_match.flower_name} represents beauty and grace\" - (Flower Wisdom)"
