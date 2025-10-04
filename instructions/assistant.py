# assistant.py
from gemini_client import ask_gemini
from voice_output import speak

def main():
    print("💬 Voice Assistant (type 'quit' to exit)")
    while True:
        question = input("You: ")
        if question.lower() in ["quit", "exit"]:
            break

        # Get Gemini response
        answer = ask_gemini(question)
        print(f"Assistant: {answer}")

        # Speak the response
        speak(answer)

if __name__ == "__main__":
    main()
