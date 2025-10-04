"""
Complete Task Helper App with AI Integration
This version includes task input and AI-powered step generation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Design System (same as before)
class DesignSystem:
    BACKGROUND = "#ffffff"
    FOREGROUND = "#25262b"
    PRIMARY = "#030213"
    PRIMARY_FOREGROUND = "#ffffff"
    SECONDARY = "#f3f3f5"
    MUTED = "#ececf0"
    MUTED_FOREGROUND = "#717182"
    ACCENT = "#e9ebef"
    TEXT_SM = 14
    TEXT_BASE = 16
    TEXT_LG = 18
    TEXT_XL = 20


class StepGuidePopup:
    """Step-by-step guide popup with your exact design"""
    
    def __init__(self, parent, title: str, steps: list, on_close=None):
        self.parent = parent
        self.title = title
        self.steps = steps
        self.current_step = 0
        self.on_close = on_close
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Step Guide")
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        width = 400
        height = 500
        screen_width = self.window.winfo_screenwidth()
        x = screen_width - width - 24
        y = 24
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        self.window.attributes('-topmost', True)
        self.window.configure(bg=DesignSystem.BACKGROUND)
        
    def create_widgets(self):
        main_frame = tk.Frame(
            self.window,
            bg=DesignSystem.BACKGROUND,
            highlightbackground="#e5e5e5",
            highlightthickness=1
        )
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=DesignSystem.BACKGROUND)
        header_frame.pack(fill='x', padx=20, pady=(20, 16))
        
        title_label = tk.Label(
            header_frame,
            text=self.title,
            font=(None, DesignSystem.TEXT_XL, 'bold'),
            bg=DesignSystem.BACKGROUND,
            fg=DesignSystem.FOREGROUND
        )
        title_label.pack(anchor='w')
        
        # Progress
        progress_frame = tk.Frame(main_frame, bg=DesignSystem.BACKGROUND)
        progress_frame.pack(fill='x', padx=20, pady=(0, 16))
        
        self.progress_label = tk.Label(
            progress_frame,
            text=f"Step {self.current_step + 1} of {len(self.steps)}",
            font=(None, DesignSystem.TEXT_SM),
            bg=DesignSystem.BACKGROUND,
            fg=DesignSystem.MUTED_FOREGROUND
        )
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = tk.Canvas(
            progress_frame,
            height=8,
            bg=DesignSystem.MUTED,
            highlightthickness=0
        )
        self.progress_bar.pack(fill='x', pady=(8, 0))
        
        # Step card
        self.step_card = tk.Frame(
            main_frame,
            bg=DesignSystem.ACCENT,
            highlightbackground="#e5e5e5",
            highlightthickness=1
        )
        self.step_card.pack(fill='x', padx=20, pady=(0, 16))
        
        step_num_frame = tk.Frame(self.step_card, bg=DesignSystem.ACCENT)
        step_num_frame.pack(anchor='w', padx=20, pady=(20, 12))
        
        self.step_number = tk.Label(
            step_num_frame,
            text="1",
            font=(None, DesignSystem.TEXT_SM, 'bold'),
            bg=DesignSystem.PRIMARY,
            fg=DesignSystem.PRIMARY_FOREGROUND,
            padx=12,
            pady=4
        )
        self.step_number.pack()
        
        self.step_text = tk.Label(
            self.step_card,
            text="",
            font=(None, DesignSystem.TEXT_BASE, 'bold'),
            bg=DesignSystem.ACCENT,
            fg=DesignSystem.FOREGROUND,
            wraplength=340,
            justify='left'
        )
        self.step_text.pack(anchor='w', padx=20, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=DesignSystem.BACKGROUND)
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.prev_btn = tk.Button(
            btn_frame,
            text="← Previous",
            font=(None, DesignSystem.TEXT_BASE, 'bold'),
            bg=DesignSystem.SECONDARY,
            fg=DesignSystem.FOREGROUND,
            command=self.previous_step,
            cursor='hand2',
            relief='flat',
            padx=16,
            pady=8
        )
        self.prev_btn.pack(side='left', expand=True, fill='x', padx=(0, 8))
        
        self.next_btn = tk.Button(
            btn_frame,
            text="Next →",
            font=(None, DesignSystem.TEXT_BASE, 'bold'),
            bg=DesignSystem.PRIMARY,
            fg=DesignSystem.PRIMARY_FOREGROUND,
            command=self.next_step,
            cursor='hand2',
            relief='flat',
            padx=16,
            pady=8
        )
        self.next_btn.pack(side='left', expand=True, fill='x')
        
        # Steps list
        list_frame = tk.Frame(main_frame, bg=DesignSystem.BACKGROUND)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            list_frame,
            text="All Steps",
            font=(None, DesignSystem.TEXT_SM, 'bold'),
            bg=DesignSystem.BACKGROUND,
            fg=DesignSystem.MUTED_FOREGROUND
        ).pack(anchor='w', pady=(0, 8))
        
        self.steps_container = tk.Frame(list_frame, bg=DesignSystem.BACKGROUND)
        self.steps_container.pack(fill='both', expand=True)
        
        self.update_display()
        
    def update_display(self):
        progress = (self.current_step + 1) / len(self.steps)
        self.progress_label.config(text=f"Step {self.current_step + 1} of {len(self.steps)}")
        
        self.progress_bar.delete('all')
        bar_width = self.progress_bar.winfo_width() or 360
        self.progress_bar.create_rectangle(
            0, 0, bar_width * progress, 8,
            fill=DesignSystem.PRIMARY,
            outline=''
        )
        
        step = self.steps[self.current_step]
        self.step_number.config(text=str(step['id']))
        self.step_text.config(text=step['instruction'])
        
        self.prev_btn.config(state='normal' if self.current_step > 0 else 'disabled')
        self.next_btn.config(text="Finish ✓" if self.current_step >= len(self.steps) - 1 else "Next →")
        
        self.update_steps_list()
        
    def update_steps_list(self):
        for widget in self.steps_container.winfo_children():
            widget.destroy()
        
        for idx, step in enumerate(self.steps):
            is_current = (idx == self.current_step)
            is_done = (idx < self.current_step)
            
            bg = DesignSystem.ACCENT if is_current else DesignSystem.MUTED if is_done else DesignSystem.BACKGROUND
            
            btn = tk.Button(
                self.steps_container,
                text=f"{'✓' if is_done else step['id']}. {step['instruction']}",
                font=(None, DesignSystem.TEXT_SM, 'bold' if is_current else 'normal'),
                bg=bg,
                fg=DesignSystem.FOREGROUND,
                anchor='w',
                padx=12,
                pady=8,
                relief='flat',
                command=lambda i=idx: self.jump_to_step(i),
                cursor='hand2'
            )
            btn.pack(fill='x', pady=2)
    
    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_display()
        else:
            messagebox.showinfo("Complete!", "You've finished all steps! 🎉")
            self.close_window()
    
    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()
    
    def jump_to_step(self, idx):
        self.current_step = idx
        self.update_display()
    
    def close_window(self):
        if self.on_close:
            self.on_close()
        self.window.destroy()


class TaskInputDialog:
    """Dialog to get task from user"""
    
    def __init__(self, parent, on_submit):
        self.parent = parent
        self.on_submit = on_submit
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("What do you need help with?")
        
        width = 500
        height = 300
        x = (parent.winfo_screenwidth() - width) // 2
        y = (parent.winfo_screenheight() - height) // 2
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        self.dialog.configure(bg=DesignSystem.BACKGROUND)
        
        # Title
        tk.Label(
            self.dialog,
            text="What task do you need help with?",
            font=(None, DesignSystem.TEXT_XL, 'bold'),
            bg=DesignSystem.BACKGROUND,
            fg=DesignSystem.FOREGROUND
        ).pack(pady=(30, 20))
        
        # Input
        self.task_input = tk.Text(
            self.dialog,
            height=5,
            font=(None, DesignSystem.TEXT_BASE),
            bg=DesignSystem.SECONDARY,
            fg=DesignSystem.FOREGROUND,
            relief='flat',
            padx=15,
            pady=10
        )
        self.task_input.pack(fill='x', padx=30, pady=(0, 20))
        self.task_input.focus()

        # Bind Enter key (Ctrl+Enter or Cmd+Enter to submit)
        self.dialog.bind('<Command-Return>', lambda e: self.submit())
        self.dialog.bind('<Control-Return>', lambda e: self.submit())

        # Submit button
        tk.Button(
            self.dialog,
            text="✨ Get Step-by-Step Help",
            font=(None, DesignSystem.TEXT_BASE, 'bold'),
            bg=DesignSystem.PRIMARY,
            fg=DesignSystem.PRIMARY_FOREGROUND,
            command=self.submit,
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=12
        ).pack(fill='x', padx=30)
        
        self.task_input.focus()
        
    def submit(self):
        task = self.task_input.get('1.0', 'end-1c').strip()
        if task:
            self.dialog.destroy()
            self.on_submit(task)
        else:
            messagebox.showwarning("Empty", "Please describe what you need help with!")


class MainApp:
    """Main application with AI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Task Helper")
        self.root.geometry("1200x800")
        self.root.configure(bg="#e0f2fe")
        
        # AI client
        api_key = os.environ.get("GEMINI_API_KEY")
        print(f"API Key found: {bool(api_key)}")
        if api_key:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-2.5-flash')
            print("Gemini client initialized successfully")
        else:
            self.client = None
            print("No API key found")
        
        self.current_popup = None
        
        # Background
        bg = tk.Frame(self.root, bg="#e0f2fe")
        bg.pack(fill='both', expand=True)
        
        tk.Label(
            bg,
            text="Desktop background",
            font=(None, DesignSystem.TEXT_BASE),
            bg="#e0f2fe",
            fg=DesignSystem.MUTED_FOREGROUND,
            padx=32,
            pady=32
        ).pack(anchor='nw')
        
        # Start button
        tk.Button(
            bg,
            text="🪄 Get Help with a Task",
            font=(None, DesignSystem.TEXT_LG, 'bold'),
            bg=DesignSystem.PRIMARY,
            fg=DesignSystem.PRIMARY_FOREGROUND,
            command=self.show_task_input,
            cursor='hand2',
            relief='flat',
            padx=30,
            pady=15
        ).pack(pady=50)

        # Auto-show task input dialog on startup
        self.root.after(100, self.show_task_input)

    def show_task_input(self):
        """Show dialog to get task from user"""
        TaskInputDialog(self.root, self.process_task)
    
    def process_task(self, task_description):
        """Send task to AI and create popup with steps"""
        print(f"Processing task: {task_description}")
        print(f"Client status: {self.client}")
        if not self.client:
            print("No client - showing error")
            messagebox.showerror(
                "API Key Missing",
                "Please set GEMINI_API_KEY environment variable"
            )
            return
        
        # Show loading message
        loading = tk.Toplevel(self.root)
        loading.title("Thinking...")
        loading.geometry("300x100")
        loading.configure(bg=DesignSystem.BACKGROUND)
        
        tk.Label(
            loading,
            text="🤔 AI is breaking down your task...",
            font=(None, DesignSystem.TEXT_BASE, 'bold'),
            bg=DesignSystem.BACKGROUND,
            fg=DesignSystem.FOREGROUND
        ).pack(expand=True)
        
        loading.update()
        
        try:
            # Call Gemini API
            prompt = f"""You are helping elderly users complete computer tasks.

Break the task into VERY simple steps:
- Maximum 6 steps
- Each step is ONE action
- Use simple language (5th grade level)
- Include WHERE to look (top, bottom, left, right)
- Be encouraging and patient

Return ONLY valid JSON in this format:
{{
    "task_title": "Friendly task name",
    "steps": [
        {{
            "id": 1,
            "instruction": "Clear, simple action (under 12 words)"
        }}
    ]
}}

Break down this task for an elderly user: {task_description}"""

            message = self.client.generate_content(prompt)
            
            # Parse response
            response_text = message.text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            breakdown = json.loads(response_text)
            
            # Close loading
            loading.destroy()
            
            # Create popup with steps
            title = breakdown.get('task_title', task_description)
            steps = breakdown.get('steps', [])
            
            if steps:
                self.current_popup = StepGuidePopup(
                    self.root,
                    title=title,
                    steps=steps,
                    on_close=self.on_popup_close
                )
            else:
                messagebox.showerror("Error", "Could not break down the task")
                
        except Exception as e:
            loading.destroy()
            messagebox.showerror("Error", f"Failed to process task:\n{str(e)}")
    
    def on_popup_close(self):
        """Called when popup is closed"""
        self.current_popup = None
    
    def run(self):
        """Start the app"""
        self.root.mainloop()


# ==============================================
# RUN THE APPLICATION
# ==============================================

if __name__ == "__main__":
    app = MainApp()
    app.run()