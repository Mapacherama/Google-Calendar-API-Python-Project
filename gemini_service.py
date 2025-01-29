import os
import google.generativeai as genai

# Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def chat_with_gemini(prompt: str, model="gemini-pro"):
    """
    Calls Google's Gemini AI API and returns a response.
    
    :param prompt: User input message
    :param model: Gemini model to use (default: gemini-pro)
    :return: AI-generated response
    """
    try:
        response = genai.GenerativeModel(model).generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"