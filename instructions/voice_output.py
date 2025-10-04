# voice_output.py
import requests
import tempfile
import platform
import subprocess
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env explicitly
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

ELEVEN_API_KEY = os.getenv("ELEVEN_KEY")
VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

if not ELEVEN_API_KEY or not VOICE_ID:
    raise ValueError("⚠️ ELEVEN_KEY or ELEVEN_VOICE_ID is missing in .env")

ELEVEN_API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

def speak(text: str):
    """Send text to ElevenLabs API and play the audio"""
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    json_data = {
        "text": text,
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }

    response = requests.post(ELEVEN_API_URL, headers=headers, json=json_data)
    if response.status_code != 200:
        print("⚠️ TTS API error:", response.status_code, response.text)
        return

    # Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(response.content)
        temp_file = f.name

    # Play the audio
    if platform.system() == "Darwin":  # Mac
        subprocess.run(["afplay", temp_file])
    elif platform.system() == "Linux":
        subprocess.run(["mpg123", temp_file])
    elif platform.system() == "Windows":
        subprocess.run(["powershell", "-c", f'(New-Object Media.SoundPlayer "{temp_file}").PlaySync()'])
