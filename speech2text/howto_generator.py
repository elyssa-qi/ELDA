import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini with newer library
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

HOWTO_SYSTEM_PROMPT = """You are a helpful assistant that creates clear, concise how-to guides for users who may not be tech-savvy.

When given a user request, you must respond with ONLY valid JSON in the following exact format:

{
    "title": "How to [task]",
    "steps": [
        {
            "title": "1. Brief action title",
            "description": "One sentence describing what to do in this step.",
            "detailedHelp": "A detailed explanation (2-4 sentences) with specific, step-by-step instructions. Include helpful tips, what to look for, and guidance on exactly how to perform the action. Write as if explaining to someone unfamiliar with the process.",
            "step": 1,
            "totalSteps": 5
        },
        // ... exactly 5 steps total
    ]
}

Requirements:
- Always create exactly 5 steps
- Each step's "title" should start with the step number (e.g., "1. ", "2. "), followed by a brief action-oriented phrase (3-7 words)
- Each "description" must be exactly ONE clear sentence stating what to do
- Each "detailedHelp" should be 2-4 sentences providing specific, detailed guidance on HOW to complete the step, including what to look for, where to click, or what to expect
- Use simple, accessible language suitable for beginners
- Include the "step" number (1-5) and "totalSteps" (always 5) in each step object
- Do not include any text outside the JSON structure
- Do not use markdown code blocks in your response

Example for "how to search for recipes on Google":
{
    "title": "How to Search for Recipes on Google",
    "steps": [
        {
            "title": "1. Open Google",
            "description": "Go to the Internet and type www.google.com",
            "detailedHelp": "Open your web browser (like Chrome, Firefox, or Safari). In the address bar at the top of the window, type 'www.google.com' and press the Enter key on your keyboard. This will take you to Google's homepage where you can search for anything.",
            "step": 1,
            "totalSteps": 5
        },
        {
            "title": "2. Search for recipes",
            "description": "Type 'easy dinner recipes' in the search box and press Enter",
            "detailedHelp": "Look for the large search box in the middle of the Google page. Click inside it with your mouse. Using your keyboard, type the words 'easy dinner recipes' (without the quotes). When you're done typing, press the Enter key or click the 'Google Search' button below the search box.",
            "step": 2,
            "totalSteps": 5
        },
        {
            "title": "3. Browse results",
            "description": "Look through the search results and click on a recipe that looks good",
            "detailedHelp": "Google will show you a list of websites with recipes. Each result has a title (in blue) and a short description below it. Scroll down the page to see more results. When you find a recipe that sounds interesting, click on the blue title to open that website.",
            "step": 3,
            "totalSteps": 5
        },
        {
            "title": "4. Read the recipe",
            "description": "Scroll down to see the ingredients and cooking instructions",
            "detailedHelp": "Once the recipe website opens, you'll need to scroll down to find the full recipe. Use your mouse wheel or the scroll bar on the right side of the window to move down the page. Look for sections labeled 'Ingredients' (what you need) and 'Instructions' or 'Directions' (how to make it).",
            "step": 4,
            "totalSteps": 5
        },
        {
            "title": "5. Save or print",
            "description": "Click the print button or bookmark the page to save it for later",
            "detailedHelp": "To save this recipe, you have two options: 1) To print it, look for a 'Print' button on the recipe page, or press Ctrl+P (Windows) or Command+P (Mac) on your keyboard. 2) To bookmark it, click the star icon in your browser's address bar, or press Ctrl+D (Windows) or Command+D (Mac). This saves the page so you can find it again later.",
            "step": 5,
            "totalSteps": 5
        }
    ]
}

Now process the following request and respond with only the JSON:"""

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron frontend

def generate_howto_guide(transcribed_text):
    """
    Generate a structured how-to guide from transcribed text
    
    Args:
        transcribed_text: The user's transcribed request
        
    Returns:
        dict: Structured how-to guide with title and 5 steps
    """
    try:
        # Combine system prompt with user request
        full_prompt = f"{HOWTO_SYSTEM_PROMPT}\n\nUser request: {transcribed_text}"
        
        # Generate response from Gemini using newer library
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt
        )
        
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON response
        howto_data = json.loads(response_text)
        
        # Validate structure
        if not validate_howto_structure(howto_data):
            raise ValueError("Invalid how-to structure from LLM")
        
        return {
            "success": True,
            "data": howto_data
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        return {
            "success": False,
            "error": "Failed to parse LLM response",
            "details": str(e)
        }
    except Exception as e:
        print(f"Error generating how-to: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def validate_howto_structure(data):
    """Validate the how-to guide structure"""
    if not isinstance(data, dict):
        return False
    if 'title' not in data or 'steps' not in data:
        return False
    if not isinstance(data['steps'], list) or len(data['steps']) != 5:
        return False
    
    for step in data['steps']:
        # Updated to match new format
        required_fields = ['title', 'description', 'detailedHelp', 'step', 'totalSteps']
        if not all(field in step for field in required_fields):
            return False
    
    return True

@app.route('/generate-howto', methods=['POST'])
def generate_howto_endpoint():
    """
    REST endpoint to generate how-to guide
    
    Expected JSON payload:
    {
        "transcription": "how to make coffee"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'transcription' not in data:
            return jsonify({
                "success": False,
                "error": "Missing transcription in request"
            }), 400
        
        transcription = data['transcription']
        result = generate_howto_guide(transcription)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Run on port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=True)