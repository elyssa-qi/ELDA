# elda_desktop.py - Desktop AI Assistant with Step-by-Step Modal
import tkinter as tk
from tkinter import scrolledtext, Canvas, messagebox, ttk
import threading
import re
import json
from gemini_client import ask_gemini, generate_steps
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

class StepModal:
    """Step-by-step modal window"""
    def __init__(self, parent, task, steps):
        self.parent = parent
        self.task = task
        self.steps = steps
        self.completed_steps = 0
        self.step_vars = []
        
        self.create_modal()
        
    def create_modal(self):
        """Create the modal window"""
        self.modal = tk.Toplevel(self.parent)
        self.modal.title(f"How to {self.task}")
        self.modal.geometry("500x600")
        self.modal.configure(bg='white')
        self.modal.resizable(False, False)
        
        # Make modal stay on top
        self.modal.transient(self.parent)
        self.modal.grab_set()
        
        # Center the modal
        self.center_modal()
        
        # Header
        header_frame = tk.Frame(self.modal, bg='white', height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text=f"How to {self.task}",
                              font=('Segoe UI', 18, 'bold'),
                              bg='white', fg='#333')
        title_label.pack(side=tk.LEFT)
        
        close_button = tk.Button(header_frame, text="×", 
                                font=('Segoe UI', 20),
                                bg='white', fg='#666',
                                relief=tk.FLAT, bd=0,
                                command=self.close_modal)
        close_button.pack(side=tk.RIGHT)
        
        # Progress section
        progress_frame = tk.Frame(self.modal, bg='white')
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        progress_label = tk.Label(progress_frame, text="Progress",
                                 font=('Segoe UI', 12),
                                 bg='white', fg='#666')
        progress_label.pack(anchor='w')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=400,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 5))
        
        self.progress_text = tk.Label(progress_frame, text="0/0",
                                     font=('Segoe UI', 10),
                                     bg='white', fg='#666')
        self.progress_text.pack(anchor='w')
        
        # Steps container
        steps_frame = tk.Frame(self.modal, bg='white')
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create scrollable frame for steps
        canvas = tk.Canvas(steps_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create step items
        for i, step in enumerate(self.steps):
            self.create_step_item(i, step)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Help section
        help_frame = tk.Frame(self.modal, bg='white')
        help_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        help_button = tk.Button(help_frame, 
                               text="Need General Help? Call AI Agent",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#007bff', fg='white',
                               relief=tk.FLAT, bd=0,
                               padx=20, pady=10,
                               command=self.request_help)
        help_button.pack(fill=tk.X)
        
        # Update progress
        self.update_progress()
        
    def create_step_item(self, index, step_text):
        """Create a step item with checkbox and actions"""
        step_frame = tk.Frame(self.scrollable_frame, 
                             bg='#f8f9ff',
                             relief=tk.SOLID,
                             bd=1)
        step_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Step content frame
        content_frame = tk.Frame(step_frame, bg='#f8f9ff')
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Checkbox and step info
        checkbox_frame = tk.Frame(content_frame, bg='#f8f9ff')
        checkbox_frame.pack(fill=tk.X)
        
        var = tk.BooleanVar()
        self.step_vars.append(var)
        var.trace('w', lambda *args, idx=index: self.toggle_step(idx))
        
        checkbox = tk.Checkbutton(checkbox_frame, 
                                 variable=var,
                                 bg='#f8f9ff',
                                 activebackground='#f8f9ff',
                                 selectcolor='#f8f9ff',
                                 relief=tk.FLAT, bd=0)
        checkbox.pack(side=tk.LEFT)
        
        step_title = tk.Label(checkbox_frame, 
                             text=f"Step {index + 1}:",
                             font=('Segoe UI', 12, 'bold'),
                             bg='#f8f9ff', fg='#333')
        step_title.pack(side=tk.LEFT, padx=(10, 0))
        
        # Step description
        step_desc = tk.Label(content_frame, 
                            text=step_text,
                            font=('Segoe UI', 11),
                            bg='#f8f9ff', fg='#666',
                            wraplength=400,
                            justify=tk.LEFT)
        step_desc.pack(anchor='w', pady=(5, 10))
        
        # Can't complete button
        cant_complete_btn = tk.Button(content_frame,
                                     text="Can't Complete This Step",
                                     font=('Segoe UI', 10),
                                     bg='#ffe6e6', fg='#d63384',
                                     relief=tk.FLAT, bd=1,
                                     command=lambda: self.cant_complete_step(index))
        cant_complete_btn.pack(anchor='center')
        
    def toggle_step(self, index):
        """Handle step completion toggle"""
        if self.step_vars[index].get():
            self.completed_steps += 1
        else:
            self.completed_steps -= 1
        
        self.update_progress()
        
        # Check if all steps completed
        if self.completed_steps == len(self.steps):
            self.all_steps_completed()
            
    def cant_complete_step(self, index):
        """Handle can't complete step action"""
        self.step_vars[index].set(True)
        # Show message that they can ask for help
        messagebox.showinfo("Help Available", 
                           f"Step {index + 1} marked as completed. You can ask for help with this step anytime!")
        
    def update_progress(self):
        """Update progress bar and text"""
        total = len(self.steps)
        if total > 0:
            progress = (self.completed_steps / total) * 100
            self.progress_var.set(progress)
            self.progress_text.config(text=f"{self.completed_steps}/{total}")
        
    def all_steps_completed(self):
        """Handle when all steps are completed"""
        messagebox.showinfo("Congratulations!", "🎉 You've completed all steps!")
        self.close_modal()
        
    def request_help(self):
        """Handle help request"""
        self.close_modal()
        # Focus back to main window input
        self.parent.focus_set()
        self.parent.user_input.focus()
        
    def close_modal(self):
        """Close the modal"""
        self.modal.destroy()
        
    def center_modal(self):
        """Center the modal on screen"""
        self.modal.update_idletasks()
        width = self.modal.winfo_width()
        height = self.modal.winfo_height()
        x = (self.modal.winfo_screenwidth() // 2) - (width // 2)
        y = (self.modal.winfo_screenheight() // 2) - (height // 2)
        self.modal.geometry(f'{width}x{height}+{x}+{y}')

class EldaDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Elda - AI Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#667eea')  # Match browser gradient background
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('elda_icon.ico')
        except:
            pass

        # Modern color scheme matching browser version
        self.bg_main = '#667eea'  # Gradient background
        self.bg_secondary = '#ffffff'  # White container
        self.bg_chat = '#f8f9fa'  # Light gray chat background
        self.accent = '#667eea'  # Blue accent
        self.accent2 = '#764ba2'  # Purple accent
        self.text_primary = '#333333'
        self.text_secondary = '#666666'
        self.user_bubble = '#667eea'
        self.assistant_bubble = '#ffffff'

        # Main container with rounded corners effect
        main_container = tk.Frame(root, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with gradient effect
        header = tk.Frame(main_container, bg=self.bg_secondary, height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 0))
        header.pack_propagate(False)

        # Title with icon
        title_frame = tk.Frame(header, bg=self.bg_secondary)
        title_frame.pack(expand=True)

        title = tk.Label(title_frame, text="🤖 Elda - AI Assistant",
                        font=('Segoe UI', 24, 'bold'),
                        bg=self.bg_secondary, fg=self.text_primary)
        title.pack()

        subtitle = tk.Label(title_frame, text="Your AI Assistant",
                           font=('Segoe UI', 12),
                           bg=self.bg_secondary, fg=self.text_secondary)
        subtitle.pack()

        # Chat container
        chat_container = tk.Frame(main_container, bg=self.bg_chat)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chat display with modern styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Segoe UI', 14),
            bg=self.bg_chat,
            fg=self.text_primary,
            state=tk.DISABLED,
            padx=20,
            pady=20,
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.text_primary,
            selectbackground=self.accent,
            selectforeground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for modern message bubbles
        self.chat_display.tag_config('user_msg',
                                     foreground='white',
                                     font=('Segoe UI', 14),
                                     background=self.user_bubble,
                                     relief=tk.FLAT,
                                     borderwidth=0)
        self.chat_display.tag_config('assistant_msg',
                                     foreground=self.text_primary,
                                     font=('Segoe UI', 14),
                                     background=self.assistant_bubble,
                                     relief=tk.SOLID,
                                     borderwidth=1)
        self.chat_display.tag_config('system',
                                     foreground=self.text_secondary,
                                     font=('Segoe UI', 12, 'italic'),
                                     justify='center')
        self.chat_display.tag_config('spacing',
                                     font=('Segoe UI', 8))

        # Input area with modern styling
        input_container = tk.Frame(main_container, bg=self.bg_secondary)
        input_container.pack(fill=tk.X, padx=20, pady=(0, 20))

        input_frame = tk.Frame(input_container, bg=self.bg_secondary)
        input_frame.pack(fill=tk.X, padx=20, pady=20)

        # Text input with modern styling
        self.user_input = tk.Entry(
            input_frame,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.text_primary,
            relief=tk.SOLID,
            insertbackground=self.text_primary,
            bd=2,
            highlightthickness=0
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0, 10))
        self.user_input.bind('<Return>', lambda e: self.send_message())

        # Controls frame
        controls_frame = tk.Frame(input_frame, bg=self.bg_secondary)
        controls_frame.pack(side=tk.LEFT)

        # Checkbox for speak toggle
        self.speak_var = tk.BooleanVar(value=False)
        self.speak_button = tk.Checkbutton(
            controls_frame,
            text="🔊 Speak",
            variable=self.speak_var,
            font=('Segoe UI', 12),
            bg=self.bg_secondary,
            fg=self.text_secondary,
            selectcolor=self.bg_secondary,
            activebackground=self.bg_secondary,
            activeforeground=self.text_secondary,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.speak_button.pack(side=tk.LEFT, padx=(0, 10))

        # Send button with modern design
        self.send_button = tk.Button(
            controls_frame,
            text="Send",
            command=self.send_message,
            font=('Segoe UI', 14, 'bold'),
            bg=self.accent,
            fg='white',
            relief=tk.FLAT,
            padx=24,
            pady=12,
            cursor='hand2',
            activebackground=self.accent2,
            activeforeground='white',
            bd=0
        )
        self.send_button.pack(side=tk.LEFT)

        # Welcome message
        self.add_message("Hello! I'm Elda, your AI assistant. How can I help you today?", 'assistant')

        # Focus on input
        self.user_input.focus()

    def add_message(self, text, sender='user'):
        """Add a message to the chat display with modern bubble styling"""
        self.chat_display.config(state=tk.NORMAL)

        if sender == 'user':
            # User message bubble (blue, right-aligned)
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"  {text}  \n", 'user_msg')
            self.chat_display.insert(tk.END, "\n", 'spacing')
        elif sender == 'assistant':
            # Assistant message bubble (white, left-aligned)
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"  {text}  \n", 'assistant_msg')
            self.chat_display.insert(tk.END, "\n", 'spacing')
        else:
            # System message (centered, italic)
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
            # Check if this is a step-by-step request
            if self.is_step_by_step_request(question):
                # Generate steps
                steps_data = generate_steps(question)
                
                # Remove "Thinking..." message
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-4l", "end-1l")
                self.chat_display.config(state=tk.DISABLED)
                
                # Show step-by-step modal
                self.show_step_modal(steps_data['task'], steps_data['steps'])
                self.add_message(f"I've created a step-by-step guide for \"{steps_data['task']}\". Check out the modal!", 'assistant')
                
            else:
                # Regular chat response
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
            # Remove "Thinking..." message
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("end-4l", "end-1l")
            self.chat_display.config(state=tk.DISABLED)
            self.add_message(f"Error: {str(e)}", 'system')

        finally:
            # Re-enable input
            self.send_button.config(state=tk.NORMAL)
            self.user_input.config(state=tk.NORMAL)
            self.user_input.focus()

    def is_step_by_step_request(self, message):
        """Detect if user is asking for step-by-step instructions"""
        step_keywords = [
            'how to', 'how do i', 'steps to', 'step by step', 'guide me', 
            'walk me through', 'show me how', 'tutorial', 'instructions'
        ]
        return any(keyword in message.lower() for keyword in step_keywords)

    def show_step_modal(self, task, steps):
        """Show the step-by-step modal"""
        StepModal(self.root, task, steps)

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
            self.add_message(f"Voice input: \"{text}\"", 'system')

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
    app = EldaDesktop(root)
    
    # Handle window close
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit Elda?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

