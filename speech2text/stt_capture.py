import os
import sounddevice as sd
import wavio
import requests
from dotenv import load_dotenv
from google import genai
from increasevolume import increase_volume

load_dotenv()
VAPI_KEY = os.getenv("VAPI_KEY")          
GEMINI_KEY = os.getenv("GEMINI_API_KEY")  

client = genai.Client()  

def record_audio(filename="command.wav", duration=20, fs=16000):
    print(f"Recording for up to {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, fs, sampwidth=2)
    print(f"Saved audio to {filename}")
    return filename

def transcribe_vapi(audio_file):
    url = "https://api.vapi.ai/v1/speech-to-text"
    headers = {"Authorization": f"Bearer {VAPI_KEY}"}
    files = {"file": open(audio_file, "rb")}
    
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        text = response.json().get("transcription")
        print("Transcribed text:", text)
        return text
    else:
        print("Error:", response.status_code, response.text)
        return None

def handle_command_with_gemini(transcribed_text):
    if not transcribed_text:
        return

    prompt = f"""
    You are a voice assistant. A user said: "{transcribed_text}".
    Determine the user's intent and return one of these actions:
    - "zoom_in"
    - "increase_volume"
    - "how_to_do_something"
    - "read_text"
    - "other" (if you can't determine)
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    intent = response.text.strip()
    print("Gemini-determined intent:", intent)

    if intent == "zoom_in":
        print("Zoom in command detected!")  # implement actual zoom function
    elif intent == "read_text":
        print("Read text command detected!")  # implement actual TTS function
    elif intent == "increase_volume":
        print("Increase volume command deteced!") # implement actual increase volume function 
        increase_volume(15) 
    elif intent == "how_to_do_something":
        print("How to do something command detected!") #implement actual do something command 
    else:
        print("Command not recognized:", transcribed_text)

def listen_and_process():
    audio_file = record_audio(duration=20)
    command_text = transcribe_vapi(audio_file)
    handle_command_with_gemini(command_text)
