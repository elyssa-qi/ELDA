# gemini_client.py
from google import genai
from dotenv import load_dotenv
import os
import re
import json

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Pick a valid model: "gemini-1.5-flash" (fast) or "gemini-1.5-pro" (more reasoning)
GEMINI_MODEL = "models/gemini-2.5-flash"

if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY missing in .env")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(question: str) -> str:
    """Send a question to Gemini and return the response text"""
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=question
        )

        # Try to extract the response text
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "⚠️ Gemini returned an unexpected response format."

    except Exception as e:
        return f"⚠️ Gemini API error: {e}"

def generate_steps(task: str) -> dict:
    """Generate step-by-step instructions for a task"""
    try:
        # Create a prompt for generating structured steps
        prompt = f"""
        Create a step-by-step guide for the following task: "{task}"
        
        Please provide:
        1. A clear, concise task title (extract the main action from the request)
        2. 3-6 simple, actionable steps that can be completed one at a time
        3. Each step should be short and digestible (1-2 sentences max)
        4. Steps should be in logical order
        5. Make steps specific and actionable
        
        Format your response as JSON with this structure:
        {{
            "task": "Clear task title",
            "steps": [
                "Step 1 description",
                "Step 2 description",
                "Step 3 description"
            ]
        }}
        
        Example for "how to search for something on Google":
        {{
            "task": "search on Google",
            "steps": [
                "Open your web browser",
                "Go to google.com",
                "Type your search query in the search box",
                "Press Enter or click the Search button",
                "Review the search results"
            ]
        }}
        """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        # Extract response text
        if hasattr(response, "text") and response.text:
            response_text = response.text.strip()
        elif hasattr(response, "candidates"):
            response_text = response.candidates[0].content.parts[0].text.strip()
        else:
            raise ValueError("Unexpected response format from Gemini")

        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                steps_data = json.loads(json_str)
                
                # Validate the structure
                if 'task' in steps_data and 'steps' in steps_data:
                    return steps_data
                else:
                    raise ValueError("Invalid JSON structure")
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: try to extract steps manually
            return extract_steps_fallback(response_text, task)

    except Exception as e:
        # Ultimate fallback
        return {
            "task": task,
            "steps": [
                "I apologize, but I encountered an error generating steps for this task.",
                "Please try rephrasing your request or ask for help with a specific step.",
                "You can also ask me to explain any part of the task in more detail."
            ]
        }

def extract_steps_fallback(response_text: str, task: str) -> dict:
    """Fallback method to extract steps from unstructured response"""
    # Try to find numbered steps
    step_pattern = r'(?:step\s*\d+|^\d+\.)\s*[:\-]?\s*(.+?)(?=\n|$)'
    steps = re.findall(step_pattern, response_text, re.IGNORECASE | re.MULTILINE)
    
    if not steps:
        # Try to find bullet points or dashes
        bullet_pattern = r'^[\-\*]\s*(.+?)(?=\n|$)'
        steps = re.findall(bullet_pattern, response_text, re.MULTILINE)
    
    if not steps:
        # Split by lines and filter
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        steps = [line for line in lines if len(line) > 10 and not line.startswith(('Task:', 'Steps:', 'Here'))]
    
    # Clean up steps
    cleaned_steps = []
    for step in steps[:6]:  # Limit to 6 steps
        step = re.sub(r'^(step\s*\d+|^\d+\.)\s*[:\-]?\s*', '', step, flags=re.IGNORECASE)
        step = step.strip()
        if step and len(step) > 5:
            cleaned_steps.append(step)
    
    if not cleaned_steps:
        cleaned_steps = [
            "I need more information to provide specific steps.",
            "Could you please clarify what exactly you want to accomplish?",
            "Feel free to ask me about any specific part of this task."
        ]
    
    return {
        "task": task,
        "steps": cleaned_steps
    }
