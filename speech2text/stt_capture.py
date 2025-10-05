import os
import sounddevice as sd
import wavio
from zoom_controller.zoom_controller import ZoomController
from brightness import parse_command as brightness_parse_command
from volume import parse_command as volume_parse_command
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
import requests

load_dotenv()

# ---------------- Keys ---------------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client_openai = OpenAI(api_key=OPENAI_API_KEY)
client = genai.Client(api_key=GEMINI_KEY)
zoom_controller = ZoomController()

# ---------------- Audio Recording ---------------- #
def record_audio(filename="command.wav", duration=7, fs=16000):
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
- zoom_out
- zoom_toggle
- increase_volume 
- how_to_do_something
- read_text
- adjust brightness
- increase_volume
- adjust_volume
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
        zoom_controller.zoom_in()

    elif intent == "zoom_out":
        print("🔎 Zoom out command detected!")
        zoom_controller.zoom_out()

    elif intent == "zoom_toggle":
        print("🔁 Zoom toggle command detected!")
        zoom_controller.zoom_toggle()

    elif intent == "read_text":
        print("📖 Read text command detected!")
        # TODO: Implement TTS functionality
        # Example: speak(transcribed_text)

    elif intent == "increase_volume":
        print("🔊 Increase volume command detected!")
        # TODO: Implement actual volume increase functionality

    elif any(word in transcribed_text.lower() for word in ["brightness", "dim", "bright", "increase brightness", "decrease brightness"]):
        print("💡 Brightness command detected!")
        brightness_parse_command(transcribed_text)

    elif any(word in transcribed_text.lower() for word in ["volume", "louder", "quieter", "mute"]):
        print("🔊 Volume command detected!")
        volume_parse_command(transcribed_text)

    elif intent == "how_to_do_something":
        print("📚 How-to command detected!")
        # TODO: Call your how-to generator service
        try:
            response = requests.post(
                'http://localhost:5000/generate-howto',
                json={'transcription': transcribed_text},
                timeout=30
            )

            if response.status_code == 200:
                howto_data = response.json()
                print("✅ How-to guide generated!")
                print(f"Title: {howto_data['data']['title']}")
            else:
                print(f"⚠️ Error generating how-to: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to connect to how-to service: {e}")

    else:
        print(f"❓ Intent '{intent}' not handled yet")
        print(f"User said: {transcribed_text}")

# ---------------- Full Pipeline ---------------- #
def listen_and_process():
    """
    Full pipeline: record -> transcribe -> detect intent -> handle command
    """
    audio_file = record_audio(duration=7)

    command_text = transcribe_whisper(audio_file)
    if not command_text:
        print("⚠️ No transcription available")
        return

    intent = detect_intent(command_text)
    handle_command(command_text, intent)

    # Optional: Clean up audio file
    try:
        os.remove(audio_file)
    except:
        pass

# ---------------- For Testing Standalone ---------------- #
if __name__ == "__main__":
    print("Testing STT capture...")
    listen_and_process()
