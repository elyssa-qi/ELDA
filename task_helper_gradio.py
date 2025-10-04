"""
AI Task Helper - Gradio Web Interface
Break down tasks into simple, digestible steps for elderly users
"""

import gradio as gr
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

def break_down_task(task_description):
    """Break down a task into simple steps using AI"""

    if not task_description or not task_description.strip():
        return "Please enter a task description."

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

    try:
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

        # Format steps nicely
        title = breakdown.get('task_title', task_description)
        steps = breakdown.get('steps', [])

        output = f"# {title}\n\n"
        for step in steps:
            output += f"**Step {step['id']}:** {step['instruction']}\n\n"

        return output

    except Exception as e:
        return f"Error: {str(e)}\n\nPlease try again or check your API key."

# Create Gradio interface
with gr.Blocks(title="AI Task Helper") as app:
    gr.Markdown("""
    # 🪄 AI Task Helper
    ### I'll break down any task into simple, easy-to-follow steps!
    """)

    with gr.Row():
        with gr.Column():
            task_input = gr.Textbox(
                label="What do you need help with?",
                placeholder="Example: Send an email to my grandson",
                lines=3
            )
            submit_btn = gr.Button("✨ Get Step-by-Step Help", variant="primary", size="lg")

    output = gr.Markdown(label="Your Steps")

    submit_btn.click(
        fn=break_down_task,
        inputs=task_input,
        outputs=output
    )

    task_input.submit(
        fn=break_down_task,
        inputs=task_input,
        outputs=output
    )

if __name__ == "__main__":
    app.launch(share=False, server_name="127.0.0.1", server_port=7860)
