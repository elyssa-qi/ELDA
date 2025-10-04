# list_models.py
from google import genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY missing in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

print("✅ Listing available Gemini models:")
for model in client.models.list():
    print("-", model.name)
