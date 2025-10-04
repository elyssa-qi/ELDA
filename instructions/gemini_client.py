# gemini_client.py
from google import genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Pick a valid model: "gemini-1.5-flash" (fast) or "gemini-1.5-pro" (more reasoning)
GEMINI_MODEL = "models/gemini-2.5-flash"

if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY missing in .env")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(question: str) -> str:
    """Send a question to Gemini and return the response text"""
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=question
        )

        # Try to extract the response text
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "⚠️ Gemini returned an unexpected response format."

    except Exception as e:
        return f"⚠️ Gemini API error: {e}"
