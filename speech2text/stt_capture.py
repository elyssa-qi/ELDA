import os
import sounddevice as sd
import wavio
from zoom_controller.zoom_controller import ZoomController
from brightness import increase_brightness, decrease_brightness
from volume import parse_command as volume_parse_command
from tts_announcer import (
    announce_brightness_change, 
    announce_volume_change, 
    announce_zoom_change, 
    announce_how_to_triggered,
    announce_error,
    introduce_myself 
)
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
import requests
from websocket_client import trigger_electron_howto

load_dotenv()
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# ---------------- Keys ---------------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = genai.Client(api_key=GEMINI_KEY)

# ---------------- Audio Recording ---------------- #
def record_audio(filename="command.wav", duration=3, fs=16000):
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

# ---------------- Keyword-based Intent Detection (Fallback) ---------------- #
def detect_intent_keywords(transcribed_text: str) -> str:
    """
    Simple keyword-based intent detection as fallback when Gemini fails.
    """
    text = transcribed_text.lower()
    
    # Introduce myself keywords
    if any(word in text for word in ["introduce", "who are you", "what are you", "tell me about yourself", "yourself"]):
        return "introduce_myself"
    
    # Zoom keywords
    if any(word in text for word in ["zoom in", "zoom closer", "closer", "bigger"]):
        return "zoom_in"
    elif any(word in text for word in ["zoom out", "zoom away", "smaller", "farther"]):
        return "zoom_out"
    
    # Volume keywords
    if any(word in text for word in ["volume up 50", "increase volume 50", "volume up by 50"]):
        return "volume_up_50"
    elif any(word in text for word in ["volume down 50", "decrease volume 50", "volume down by 50"]):
        return "volume_down_50"
    elif any(word in text for word in ["increase volume", "turn up", "louder", "volume up"]):
        return "increase_volume"
    elif any(word in text for word in ["decrease volume", "turn down", "quieter", "volume down", "lower volume"]):
        return "adjust_volume"
    
    # Brightness keywords
    if any(word in text for word in ["brighter", "increase brightness", "brightness up"]):
        return "adjust_brightness"
    elif any(word in text for word in ["dimmer", "decrease brightness", "brightness down"]):
        return "adjust_brightness"
    
    # How-to keywords
    if any(word in text for word in ["how to", "how do i", "help me", "teach me", "show me how"]):
        return "how_to_do_something"
    
    # Read text keywords
    if any(word in text for word in ["read", "read text", "read clipboard", "what does this say"]):
        return "read_text"
    
    return "other"

# ---------------- Intent Detection (Gemini with Fallback) ---------------- #
def detect_intent(transcribed_text: str) -> str:
    """
    Use Gemini to determine the user's intent, with keyword fallback.
    """
    prompt = f"""You are an intent classifier for a voice assistant. 
    
A user said: "{transcribed_text}"

Analyze the request and return ONLY one of these exact intents:
- introduce_myself
- zoom_in
- zoom_out
- increase_volume
- adjust_volume
- volume_up_50
- volume_down_50
- adjust_brightness
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
        print(f"🎯 Detected intent (Gemini): {intent}")
        return intent
    except Exception as e:
        print(f"⚠️ Gemini failed ({e}), using keyword fallback...")
        intent = detect_intent_keywords(transcribed_text)
        print(f"🎯 Detected intent (keywords): {intent}")
        return intent

# ---------------- Command Handling ---------------- #
def handle_command(transcribed_text: str, intent: str):
    """
    Handle different intents based on what Gemini determined.
    """
    if not transcribed_text:
        print("No transcription available")
        return
    
    if intent == "introduce_myself":
        print("👋 Introduce myself command detected!")
        introduce_myself()
    
    elif intent == "zoom_in":
        print("🔍 Zoom in command detected!")
        try:
            zoom_controller = ZoomController()
            zoom_controller.zoom_in()
            announce_zoom_change("zoomed in")
        except Exception as e:
            print(f"Error with zoom: {e}")
            announce_error("zooming in")
    
    elif intent == "zoom_out":
        print("🔍 Zoom out command detected!")
        try:
            zoom_controller = ZoomController()
            zoom_controller.zoom_out()
            announce_zoom_change("zoomed out")
        except Exception as e:
            print(f"Error with zoom: {e}")
            announce_error("zooming out")
        
    elif intent == "read_text":
        print("📖 Read text command detected!")
        # TODO: Implement TTS functionality
        # Example: speak(transcribed_text)
        
    elif intent == "increase_volume":
        print("🔊 Increase volume command detected!")
        try:
            volume_parse_command(transcribed_text)
            announce_volume_change("increased")
        except Exception as e:
            print(f"Error with volume: {e}")
            announce_error("adjusting volume")
        
    elif intent == "adjust_volume":
        print("🔊 Volume command detected!")
        try:
            volume_parse_command(transcribed_text)
            announce_volume_change("adjusted")
        except Exception as e:
            print(f"Error with volume: {e}")
            announce_error("adjusting volume")
    
    elif intent == "volume_up_50":
        print("🔊 Volume up 50% command detected!")
        try:
            from volume import increase_volume
            increase_volume()
            announce_volume_change("increased by 50%")
        except Exception as e:
            print(f"Error with volume: {e}")
            announce_error("increasing volume")
    
    elif intent == "volume_down_50":
        print("🔊 Volume down 50% command detected!")
        try:
            from volume import decrease_volume
            decrease_volume()
            announce_volume_change("decreased by 50%")
        except Exception as e:
            print(f"Error with volume: {e}")
            announce_error("decreasing volume")

    elif intent == "adjust_brightness":
        print("💡 Brightness command detected!")
        try:
            # Determine if it's increase or decrease based on keywords
            if any(word in transcribed_text.lower() for word in ["increase", "raise", "up", "brighter", "higher"]):
                increase_brightness()
                announce_brightness_change("increased")
            elif any(word in transcribed_text.lower() for word in ["decrease", "lower", "down", "dimmer", "darker"]):
                decrease_brightness()
                announce_brightness_change("decreased")
            else:
                # Default to increase if unclear
                increase_brightness()
                announce_brightness_change("increased")
        except Exception as e:
            print(f"Error with brightness: {e}")
            announce_error("adjusting brightness")
        
    elif intent == "how_to_do_something":
        print("📚 How-to command detected!")
        
        try:
            # Trigger Electron window via WebSocket
            trigger_electron_howto(transcribed_text)
            
            # The Electron frontend will fetch from Flask when it loads
            print("✅ Electron window triggered!")
            announce_how_to_triggered()
        except Exception as e:
            print(f"Error with how-to: {e}")
            announce_error("showing the guide")
        
    # Additional keyword-based detection for better coverage
    elif any(word in transcribed_text.lower() for word in ["brightness", "dim", "bright", "increase brightness", "decrease brightness"]):
        print("💡 Brightness command detected!")
        try:
            # Determine if it's increase or decrease based on keywords
            if any(word in transcribed_text.lower() for word in ["increase", "raise", "up", "brighter", "higher"]):
                increase_brightness()
                announce_brightness_change("increased")
            elif any(word in transcribed_text.lower() for word in ["decrease", "lower", "down", "dimmer", "darker"]):
                decrease_brightness()
                announce_brightness_change("decreased")
            else:
                # Default to increase if unclear
                increase_brightness()
                announce_brightness_change("increased")
        except Exception as e:
            print(f"Error with brightness: {e}")
            announce_error("adjusting brightness")

    elif any(word in transcribed_text.lower() for word in ["volume", "louder", "quieter", "mute"]):
        print("🔊 Volume command detected!")
        try:
            volume_parse_command(transcribed_text)
            announce_volume_change("adjusted")
        except Exception as e:
            print(f"Error with volume: {e}")
            announce_error("adjusting volume")
# ---------------- Full Pipeline ---------------- #
def listen_and_process():
    """
    Full pipeline: record -> transcribe -> detect intent -> handle command
    """
    # Step 1: Record audio
    audio_file = record_audio(duration=3)
    
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