# # wake_word_listener.py
# import speech_recognition as sr

# def listen_for_wake_word(wake_word="hey elda"):
#     recognizer = sr.Recognizer()
#     mic = sr.Microphone()

#     print("🎙️ Listening for wake word...")

#     while True:
#         with mic as source:
#             recognizer.adjust_for_ambient_noise(source)
#             audio = recognizer.listen(source)

#         try:
#             text = recognizer.recognize_google(audio).lower()
#             print("Heard:", text)

#             if wake_word in text:
#                 print("✅ Wake word detected!")
#                 return True
#         except sr.UnknownValueError:
#             pass
#         except sr.RequestError as e:
#             print(f"⚠️ Speech recognition error: {e}")
