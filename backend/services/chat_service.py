from groq import Groq
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# PROMPT ENGINEERING: Agronomist Persona for Chat
AGRONOMIST_SYSTEM_PROMPT = """
You are 'nanoBot', a world-class AI Agronomist and Soil Scientist at nanoFarms. 
Your goal is to provide precise, scientific, and actionable agricultural advice to farmers.

Core Guidelines:
1. **Persona**: Professional, empathetic, and data-driven.
2. **Knowledge Base**: Expert in plant diseases, soil NPK, and organic pest control.
3. **Response Structure**: Use clear headings and bullet points. Focus on 3-step action plans when possible.
4. **Safety**: Prioritize organic/safe methods over toxic chemicals.
"""

class GroqAIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or self.api_key == "your_groq_key_here":
            print("⚠️  WARNING: GROQ_API_KEY not set correctly in backend/.env")
            self.client = None
            return

        self.client = Groq(api_key=self.api_key)
        # Models
        self.chat_model = "llama-3.3-70b-versatile"
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct" 
        print(f"✅ Groq AI Service initialised (Chat: {self.chat_model}, Vision: {self.vision_model}).")

    async def get_chat_response(self, user_message: str, history: list = None) -> str:
        if not self.client:
            return "Groq AI is not configured. Please add a valid GROQ_API_KEY to your .env file."

        try:
            messages = [{"role": "system", "content": AGRONOMIST_SYSTEM_PROMPT}]
            if history:
                for h in history:
                    role = h["role"] if h["role"] != "model" else "assistant"
                    messages.append({"role": role, "content": h["parts"][0]})
            messages.append({"role": "user", "content": user_message})

            completion = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq Chat Error: {e}")
            return f"Chat Error: {str(e)}"

    async def identify_disease_vision(self, image_bytes: bytes, content_type: str) -> str:
        if not self.client:
            return "Groq AI (Vision) not configured."

        try:
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            prompt = (
                "You are an expert agronomist. Identify the crop and any visible disease "
                "in this leaf photo. Return ONLY the identification as 'CROP: <name>, DISEASE: <name>'."
            )

            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=100,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Groq Vision Error: {e}")
            return f"Error identifying via Groq Vision: {str(e)}"

# Singleton — stays in memory
groq_service = GroqAIService()
# Aliases for easier refactor
chat_service = groq_service 
