import os
import sounddevice as sd
import wavio
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
import requests
from websocket_client import trigger_electron_howto

load_dotenv()

# ---------------- Keys ---------------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = genai.Client(api_key=GEMINI_KEY)

# ---------------- Audio Recording ---------------- #
def record_audio(filename="command.wav", duration=10, fs=16000):
    """
    Records audio from the microphone and saves to a WAV file.
    """
    print(f"🔴 Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, fs, sampwidth=2)
    print(f"✅ Saved audio to {filename}")
    return filename

# ---------------- Speech-to-Text (OpenAI Whisper) ---------------- #
def transcribe_whisper(audio_file_path: str) -> str:
    """
    Transcribe audio using OpenAI Whisper.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client_openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        text = transcription.text
        print("📝 Transcribed text:", text)
        return text
    except Exception as e:
        print(f"⚠️ Whisper STT error: {e}")
        return None

# ---------------- Intent Detection (Gemini) ---------------- #
def detect_intent(transcribed_text: str) -> str:
    """
    Use Gemini to determine the user's intent.
    """
    prompt = f"""You are an intent classifier for a voice assistant. 
    
A user said: "{transcribed_text}"

Analyze the request and return ONLY one of these exact intents:
- zoom_in
- increase_volume
- how_to_do_something
- read_text
- other

Return only the intent name, nothing else."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        intent = response.text.strip().lower()
        print(f"🎯 Detected intent: {intent}")
        return intent
    except Exception as e:
        print(f"⚠️ Error detecting intent: {e}")
        return "other"

# ---------------- Command Handling ---------------- #
def handle_command(transcribed_text: str, intent: str):
    """
    Handle different intents based on what Gemini determined.
    """
    if not transcribed_text:
        print("No transcription available")
        return
    
    if intent == "zoom_in":
        print("🔍 Zoom in command detected!")
        # TODO: Implement zoom functionality
        
    elif intent == "read_text":
        print("📖 Read text command detected!")
        # TODO: Implement TTS functionality
        # Example: speak(transcribed_text)
        
    elif intent == "increase_volume":
        print("🔊 Increase volume command detected!")

        
    elif intent == "how_to_do_something":
        print("📚 How-to command detected!")
        
        # Trigger Electron window via WebSocket
        trigger_electron_howto(transcribed_text)
        
        # The Electron frontend will fetch from Flask when it loads
        print("✅ Electron window triggered!")
# ---------------- Full Pipeline ---------------- #
def listen_and_process():
    """
    Full pipeline: record -> transcribe -> detect intent -> handle command
    """
    # Step 1: Record audio
    audio_file = record_audio(duration=10)
    
    # Step 2: Transcribe with Whisper
    command_text = transcribe_whisper(audio_file)
    
    if not command_text:
        print("⚠️ No transcription available")
        return
    
    # Step 3: Detect intent with Gemini
    intent = detect_intent(command_text)
    
    # Step 4: Handle the command based on intent
    handle_command(command_text, intent)
    
    # Optional: Clean up audio file
    try:
        os.remove(audio_file)
    except:
        pass

# For testing standalone
if __name__ == "__main__":
    print("Testing STT capture...")
    listen_and_process()