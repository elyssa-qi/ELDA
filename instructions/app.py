# app.py
from flask import Flask, render_template, request, jsonify
from gemini_client import ask_gemini
from voice_output import speak
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

    # Get response from Gemini
    answer = ask_gemini(question)

    # Optionally speak the response (in background to not block)
    if data.get('speak', False):
        threading.Thread(target=speak, args=(answer,), daemon=True).start()

    return jsonify({
        'question': question,
        'answer': answer
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
