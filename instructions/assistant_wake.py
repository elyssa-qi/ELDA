# # assistant_wake.py
# from gemini_client import ask_gemini
# from voice_output import speak
# from wake_word_listener import wait_for_wake_word, record_user_input  # hypothetical module

# def run_assistant():
#     print("🤖 Voice assistant ready. Say 'Hey Elda' to activate.")
#     while True:
#         # Wait until wake word is detected
#         wait_for_wake_word("Hey Elda")

#         # Once wake word detected, record user's question
#         print("🎤 Listening...")
#         question = record_user_input()  # returns string of what user said

#         if not question:
#             speak("I didn't catch that. Please try again.")
#             continue

#         print(f"You said: {question}")

#         # Get Gemini response
#         answer = ask_gemini(question)
#         print(f"Assistant: {answer}")

#         # Speak the response
#         speak(answer)
