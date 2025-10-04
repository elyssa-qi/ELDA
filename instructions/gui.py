# gui.py
import tkinter as tk
from tkinter import scrolledtext, Canvas
import threading
from gemini_client import ask_gemini
from voice_output import speak
import speech_recognition as sr

class ModernButton(tk.Canvas):
    """Custom button with hover effects"""
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text

        # Colors
        self.bg_normal = kwargs.get('bg', '#667eea')
        self.bg_hover = '#5568d3'
        self.fg_color = kwargs.get('fg', 'white')

        # Draw button
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

        self.draw()

    def draw(self, bg=None):
        self.delete('all')
        color = bg or self.bg_normal
        self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(),
                            fill=color, outline='', tags='bg')
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2,
                        text=self.text, fill=self.fg_color, font=('Segoe UI', 11, 'bold'))

    def on_enter(self, e):
        self.draw(self.bg_hover)

    def on_leave(self, e):
        self.draw(self.bg_normal)

class EldaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Elda - AI Assistant")
        self.root.geometry("900x700")

        # Light color scheme with better visibility
        self.bg_main = '#f5f7fa'
        self.bg_secondary = '#667eea'
        self.bg_chat = '#ffffff'
        self.accent = '#e94560'
        self.accent2 = '#667eea'
        self.text_primary = '#2d3748'
        self.text_secondary = '#4a5568'

        self.root.configure(bg=self.bg_main)

        # Header with gradient effect
        header = tk.Frame(root, bg=self.bg_secondary, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Title with icon
        title_frame = tk.Frame(header, bg=self.bg_secondary)
        title_frame.pack(expand=True)

        icon = tk.Label(title_frame, text="🤖", font=('Segoe UI', 32), bg=self.bg_secondary)
        icon.pack(side=tk.LEFT, padx=(0, 15))

        title_text = tk.Frame(title_frame, bg=self.bg_secondary)
        title_text.pack(side=tk.LEFT)

        title = tk.Label(title_text, text="Elda",
                        font=('Segoe UI', 24, 'bold'),
                        bg=self.bg_secondary, fg=self.text_primary)
        title.pack(anchor='w')

        subtitle = tk.Label(title_text, text="Your AI Assistant",
                           font=('Segoe UI', 11),
                           bg=self.bg_secondary, fg=self.text_secondary)
        subtitle.pack(anchor='w')

        # Chat container with rounded effect
        chat_container = tk.Frame(root, bg=self.bg_main)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chat display with custom styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg=self.bg_chat,
            fg='#2d3748',
            state=tk.DISABLED,
            padx=15,
            pady=15,
            relief=tk.SOLID,
            bd=1,
            insertbackground='#2d3748',
            selectbackground=self.accent2,
            selectforeground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for message bubbles
        self.chat_display.tag_config('user_label',
                                     foreground=self.accent,
                                     font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('user_msg',
                                     foreground='#2d3748',
                                     font=('Segoe UI', 11),
                                     lmargin1=20, lmargin2=20,
                                     rmargin=50)
        self.chat_display.tag_config('assistant_label',
                                     foreground=self.accent2,
                                     font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('assistant_msg',
                                     foreground='#2d3748',
                                     font=('Segoe UI', 11),
                                     lmargin1=20, lmargin2=20,
                                     rmargin=50)
        self.chat_display.tag_config('system',
                                     foreground='#888',
                                     font=('Segoe UI', 10, 'italic'),
                                     justify='center')
        self.chat_display.tag_config('spacing',
                                     font=('Segoe UI', 4))

        # Input area with modern styling
        input_container = tk.Frame(root, bg=self.bg_secondary)
        input_container.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Label to help identify the input area
        tk.Label(input_container,
                text="Type your message:",
                font=('Segoe UI', 10),
                bg=self.bg_secondary,
                fg='white').pack(anchor='w', padx=15, pady=(10, 5))

        input_frame = tk.Frame(input_container, bg=self.bg_secondary)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Text input with better visibility
        self.user_input = tk.Entry(
            input_frame,
            font=('Segoe UI', 13),
            bg='white',
            fg='#333',
            relief=tk.SOLID,
            insertbackground='#333',
            bd=1
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.user_input.bind('<Return>', lambda e: self.send_message())

        # Controls frame
        controls_frame = tk.Frame(input_frame, bg=self.bg_secondary)
        controls_frame.pack(side=tk.LEFT)

        # Microphone button for voice input
        self.mic_button = tk.Button(
            controls_frame,
            text="🎤",
            command=self.start_voice_input,
            font=('Segoe UI', 16),
            bg=self.bg_secondary,
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2',
            activebackground=self.bg_secondary,
            activeforeground=self.accent,
            bd=0
        )
        self.mic_button.pack(side=tk.LEFT, padx=(0, 10))

        # Speak toggle button
        self.speak_var = tk.BooleanVar(value=False)
        self.speak_button = tk.Checkbutton(
            controls_frame,
            text="🔊",
            variable=self.speak_var,
            font=('Segoe UI', 16),
            bg=self.bg_secondary,
            fg='white',
            selectcolor=self.bg_secondary,
            activebackground=self.bg_secondary,
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.speak_button.pack(side=tk.LEFT, padx=(0, 10))

        # Send button with modern design
        self.send_button = tk.Button(
            controls_frame,
            text="Send ➤",
            command=self.send_message,
            font=('Segoe UI', 12, 'bold'),
            bg=self.accent,
            fg='white',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor='hand2',
            activebackground='#d63851',
            activeforeground='white',
            bd=0
        )
        self.send_button.pack(side=tk.LEFT)

        # Welcome message
        self.add_message("Hello! I'm Elda, your AI assistant. How can I help you today?", 'assistant')

        # Focus on input
        self.user_input.focus()

    def add_message(self, text, sender='user'):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)

        if sender == 'user':
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, "● You\n", 'user_label')
            self.chat_display.insert(tk.END, f"{text}\n", 'user_msg')
            self.chat_display.insert(tk.END, "\n", 'spacing')
        elif sender == 'assistant':
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, "● Elda\n", 'assistant_label')
            self.chat_display.insert(tk.END, f"{text}\n", 'assistant_msg')
            self.chat_display.insert(tk.END, "\n", 'spacing')
        else:
            self.chat_display.insert(tk.END, f"\n{text}\n\n", 'system')

        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def send_message(self):
        """Handle sending a message"""
        question = self.user_input.get().strip()
        if not question:
            return

        # Add user message
        self.add_message(question, 'user')
        self.user_input.delete(0, tk.END)

        # Disable input while processing
        self.send_button.config(state=tk.DISABLED)
        self.user_input.config(state=tk.DISABLED)

        # Show thinking message
        self.add_message("● Thinking...", 'system')

        # Process in background thread
        threading.Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        ).start()

    def process_question(self, question):
        """Process question with Gemini (runs in background thread)"""
        try:
            # Get response
            answer = ask_gemini(question)

            # Remove "Thinking..." message
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("end-4l", "end-1l")
            self.chat_display.config(state=tk.DISABLED)

            # Add assistant response
            self.add_message(answer, 'assistant')

            # Speak if enabled
            if self.speak_var.get():
                threading.Thread(target=speak, args=(answer,), daemon=True).start()

        except Exception as e:
            self.add_message(f"Error: {str(e)}", 'system')

        finally:
            # Re-enable input
            self.send_button.config(state=tk.NORMAL)
            self.user_input.config(state=tk.NORMAL)
            self.user_input.focus()

    def start_voice_input(self):
        """Start listening for voice input"""
        # Disable buttons during recording
        self.mic_button.config(state=tk.DISABLED, text="🎤 Listening...")

        # Run voice recognition in background
        threading.Thread(target=self.record_voice, daemon=True).start()

    def record_voice(self):
        """Record and transcribe voice input"""
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen for audio
                audio = recognizer.listen(source, timeout=5)

            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio)

            # Update input field with recognized text
            self.user_input.delete(0, tk.END)
            self.user_input.insert(0, text)

        except sr.WaitTimeoutError:
            self.add_message("No speech detected. Please try again.", 'system')
        except sr.UnknownValueError:
            self.add_message("Could not understand audio. Please try again.", 'system')
        except sr.RequestError as e:
            self.add_message(f"Speech recognition error: {e}", 'system')
        except Exception as e:
            self.add_message(f"Error: {e}", 'system')
        finally:
            # Re-enable microphone button
            self.mic_button.config(state=tk.NORMAL, text="🎤")

def main():
    root = tk.Tk()
    app = EldaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
