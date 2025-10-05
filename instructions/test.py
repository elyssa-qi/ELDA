import openai
import os
from dotenv import load_dotenv


openai.api_key = os.getenv("OPENAI_API_KEY")

audio_file_path = "command.wav"

with open(audio_file_path, "rb") as audio_file:
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

print("Transcribed text:", transcription.text)
