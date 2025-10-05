import subprocess
import requests
import os
from dotenv import load_dotenv

load_dotenv()
ELEVEN_KEY = os.getenv("ELEVEN_KEY")  # Your ElevenLabs API key
VOICE_ID = os.getenv("ELEVEN_VOICE_ID")  # Optional: choose a voice

def get_clipboard_text():
    """Grabs the currently highlighted/copied text on macOS."""
    # Simulate Cmd+C to copy selection
    subprocess.run([
        "osascript",
        "-e",
        'tell application "System Events" to keystroke "c" using command down'
    ])
    
    # Read from clipboard
    result = subprocess.run(["pbpaste"], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")

def read_text_elevenlabs(text):
    """Convert text to speech using ElevenLabs API and play it."""
    if not text.strip():
        print("No text to read.")
        return
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        with open("output.wav", "wb") as f:
            f.write(response.content)
        # Play audio
        subprocess.run(["afplay", "output.wav"])
    else:
        print("ElevenLabs TTS error:", response.status_code, response.text)
