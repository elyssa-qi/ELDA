import sys
import os

# Add root folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from speech2text.stt_capture import listen_and_process  # your voice agent pipeline

def main():
    print("💬 Say something to the assistant...")
    listen_and_process()

if __name__ == "__main__":
    main()
