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
    
def parse_natural_language_request(user_input):
    """Use AI to interpret scheduling requests in natural language."""
    prompt = f"""
    Analyze this scheduling request: "{user_input}"
    Extract:
    - Event title
    - Date and time
    - Duration (if mentioned)
    - Any additional context
    Respond with structured JSON format.
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text 