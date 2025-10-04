"""
AI Task Helper - Floating Popup
Creates a floating window that appears on top of everything
"""

import tkinter as tk
from tkinter import messagebox
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

class TaskPopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🪄 AI Task Helper")

        # Make it float on top
        self.root.attributes('-topmost', True)

        # Position in center of screen
        width = 600
        height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Style
        self.root.configure(bg='#ffffff')

        # Title
        title = tk.Label(
            self.root,
            text="What do you need help with?",
            font=('Arial', 24, 'bold'),
            bg='#ffffff',
            fg='#030213'
        )
        title.pack(pady=(40, 20))

        # Input
        self.task_input = tk.Text(
            self.root,
            height=6,
            font=('Arial', 16),
            bg='#f3f3f5',
            fg='#25262b',
            relief='flat',
            padx=15,
            pady=15,
            wrap='word'
        )
        self.task_input.pack(fill='x', padx=40, pady=(0, 20))
        self.task_input.focus_set()

        # Hint text
        hint = tk.Label(
            self.root,
            text="Example: Send an email to my grandson",
            font=('Arial', 12),
            bg='#ffffff',
            fg='#717182'
        )
        hint.pack(pady=(0, 10))

        # Submit button
        submit_btn = tk.Button(
            self.root,
            text="✨ Get Step-by-Step Help",
            font=('Arial', 16, 'bold'),
            bg='#030213',
            fg='#ffffff',
            command=self.process_task,
            cursor='hand2',
            relief='flat',
            padx=30,
            pady=15,
            activebackground='#25262b',
            activeforeground='#ffffff'
        )
        submit_btn.pack(pady=10)

        # Keyboard shortcuts
        self.root.bind('<Command-Return>', lambda e: self.process_task())
        self.root.bind('<Control-Return>', lambda e: self.process_task())
        self.root.bind('<Escape>', lambda e: self.root.quit())

    def process_task(self):
        task = self.task_input.get('1.0', 'end-1c').strip()

        if not task:
            messagebox.showwarning("Empty", "Please describe what you need help with!")
            return

        # Show loading
        loading = tk.Toplevel(self.root)
        loading.title("Processing...")
        loading.geometry("300x100")
        loading.attributes('-topmost', True)
        loading.configure(bg='#ffffff')

        tk.Label(
            loading,
            text="🤔 AI is thinking...",
            font=('Arial', 14, 'bold'),
            bg='#ffffff',
            fg='#030213'
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

Break down this task for an elderly user: {task}"""

            response = model.generate_content(prompt)
            response_text = response.text

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

            loading.destroy()

            # Show steps in a popup
            self.show_steps(breakdown)

        except Exception as e:
            loading.destroy()
            messagebox.showerror("Error", f"Failed to process task:\n{str(e)}")

    def show_steps(self, breakdown):
        """Show steps in a floating window on the right side"""
        steps_window = tk.Toplevel(self.root)
        steps_window.title("Your Steps")

        # Position on right side of screen
        width = 400
        height = 600
        screen_width = steps_window.winfo_screenwidth()
        x = screen_width - width - 24
        y = 24
        steps_window.geometry(f'{width}x{height}+{x}+{y}')
        steps_window.attributes('-topmost', True)
        steps_window.configure(bg='#ffffff')

        # Main frame
        main_frame = tk.Frame(steps_window, bg='#ffffff')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title = breakdown.get('task_title', 'Your Task')
        tk.Label(
            main_frame,
            text=title,
            font=('Arial', 20, 'bold'),
            bg='#ffffff',
            fg='#030213',
            wraplength=360,
            justify='left'
        ).pack(anchor='w', pady=(0, 20))

        # Steps
        steps = breakdown.get('steps', [])
        for step in steps:
            # Step frame
            step_frame = tk.Frame(
                main_frame,
                bg='#e9ebef',
                highlightbackground='#e5e5e5',
                highlightthickness=1
            )
            step_frame.pack(fill='x', pady=8)

            # Step number
            tk.Label(
                step_frame,
                text=str(step['id']),
                font=('Arial', 14, 'bold'),
                bg='#030213',
                fg='#ffffff',
                padx=12,
                pady=6
            ).pack(anchor='w', padx=15, pady=(15, 8))

            # Step text
            tk.Label(
                step_frame,
                text=step['instruction'],
                font=('Arial', 16),
                bg='#e9ebef',
                fg='#030213',
                wraplength=340,
                justify='left'
            ).pack(anchor='w', padx=15, pady=(0, 15))

        # Close button
        tk.Button(
            main_frame,
            text="✓ Done",
            font=('Arial', 14, 'bold'),
            bg='#030213',
            fg='#ffffff',
            command=lambda: [steps_window.destroy(), self.root.quit()],
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=10
        ).pack(pady=(20, 0))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskPopup()
    app.run()
