import pvporcupine
import os
import sounddevice as sd
import struct
from dotenv import load_dotenv
from speech2text.stt_capture import listen_and_process

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")

elda = pvporcupine.create(
    access_key=ACCESS_KEY, 
    keyword_paths=["hey_elda.ppn"]
)

# Flag to trigger processing outside the callback
wake_word_detected = False

def audio_callback(indata, frames, time, status):
    global wake_word_detected
    
    if status:
        print(status)
    
    pcm = struct.unpack_from("h" * elda.frame_length, indata)
    result = elda.process(pcm)
    
    if result >= 0:
        print("🎤 Wake word 'Hey Elda' detected!")
        wake_word_detected = True

# Main loop
print("👂 Listening for 'Hey Elda'... Press Ctrl+C to stop.")

while True:
    wake_word_detected = False
    
    # Listen for wake word
    with sd.RawInputStream(
        samplerate=elda.sample_rate,
        blocksize=elda.frame_length,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        # Wait for wake word detection
        while not wake_word_detected:
            sd.sleep(100)
    
    # Stream is now closed, safe to record
    print("Processing command...")
    try:
        listen_and_process()
    except Exception as e:
        print(f"⚠️ Error processing command: {e}")
    
    print("Ready for next wake word...\n")