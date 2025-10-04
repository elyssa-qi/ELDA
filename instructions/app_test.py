# app_test.py - Test version without API dependencies
from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Handle user questions and return AI responses"""
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # Mock response for testing
    answer = f"Test response: I received your question '{question}'. This is a mock response for testing the UI."

    return jsonify({
        'question': question,
        'answer': answer
    })

@app.route('/generate-steps', methods=['POST'])
def generate_steps_endpoint():
    """Generate step-by-step instructions for a task"""
    data = request.get_json()
    task = data.get('task', '').strip()

    if not task:
        return jsonify({'error': 'No task provided'}), 400

    # Mock steps for testing
    mock_steps = [
        "Open your web browser",
        "Navigate to the appropriate website",
        "Locate the search function",
        "Enter your search query",
        "Review the results",
        "Take action based on findings"
    ]
    
    steps_data = {
        "task": task.replace("how to", "").replace("how do i", "").strip(),
        "steps": mock_steps
    }

    return jsonify(steps_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

