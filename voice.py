import pvporcupine
import os
import sounddevice as sd
import struct
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
elda = pvporcupine.create(
    access_key=ACCESS_KEY, keyword_paths=["hey_elda.ppn"]
)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    pcm = struct.unpack_from("h" * elda.frame_length, indata)
    result = elda.process(pcm)

    if result >= 0:
        print("Wake word 'Hey Elda' detected!")

with sd.RawInputStream(
    samplerate=elda.sample_rate,
    blocksize=elda.frame_length,
    dtype="int16",
    channels=1,
    callback=audio_callback,
):
    print("Listening for 'Hey Elda'... Press Ctrl+C to stop.")
    while True:
        sd.sleep(1000)