import google.generativeai as genai
import os

def get_ai_response(user_message):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "AI service is not configured."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction="You are a helpful tutor for a gamified learning platform focused on Environmental Awareness & Sustainability. Answer student questions clearly and concisely. Keep responses short and educational."
        )
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
