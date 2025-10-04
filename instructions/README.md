# Elda AI Assistant

A desktop AI assistant with step-by-step task guidance capabilities, built with Python and Tkinter.

## Features

- **Desktop Application**: Runs as a standalone desktop app (no browser required)
- **Step-by-Step Guidance**: Automatically detects when users need step-by-step instructions and opens a modal with progress tracking
- **Voice Input**: Speech recognition for hands-free interaction
- **Text-to-Speech**: Optional voice responses
- **Modern UI**: Clean, intuitive interface with progress tracking
- **Background Operation**: Can run continuously in the background

## Installation

1. **Clone or download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (optional for test mode):
   Create a `.env` file in the instructions directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ELEVEN_KEY=your_elevenlabs_api_key_here
   ELEVEN_VOICE_ID=your_voice_id_here
   ```

## Usage

### Quick Start
```bash
python3 run_elda.py
```

### Manual Start
- **Full version** (requires API keys): `python3 elda_desktop.py`
- **Test version** (no API keys needed): `python3 elda_desktop_test.py`

## How It Works

### Step-by-Step Feature
When you ask questions like:
- "How to search for something"
- "Guide me through sending an email"
- "Show me step by step how to..."

Elda will:
1. Detect that you need step-by-step instructions
2. Generate a structured task breakdown
3. Open a modal with:
   - Progress tracking (X/Y steps completed)
   - Checkboxes for each step
   - "Can't Complete This Step" buttons
   - "Need General Help" option

### Voice Input
Click the microphone button to:
- Speak your question
- Get automatic transcription
- Continue with text or voice responses

### Regular Chat
For general questions, Elda responds like a normal AI assistant with text responses.

## API Keys Setup

### Google Gemini (Required for AI responses)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create an API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### ElevenLabs (Optional for text-to-speech)
1. Go to [ElevenLabs](https://elevenlabs.io/settings/api-keys)
2. Create an API key
3. Choose a voice ID from the voice library
4. Add to `.env`:
   ```
   ELEVEN_KEY=your_key_here
   ELEVEN_VOICE_ID=your_voice_id_here
   ```

## File Structure

```
instructions/
├── elda_desktop.py          # Main desktop application
├── elda_desktop_test.py     # Test version (no API keys)
├── run_elda.py             # Launcher script
├── gemini_client.py        # AI client (Gemini API)
├── voice_output.py         # Text-to-speech
├── gui.py                  # Original GUI (legacy)
├── app.py                  # Web version (legacy)
├── templates/
│   └── index.html          # Web interface
└── requirements.txt        # Dependencies
```

## Troubleshooting

### Voice Input Issues
- Ensure microphone permissions are granted
- Check that PyAudio is installed correctly
- On macOS, you may need to install PortAudio: `brew install portaudio`

### API Errors
- Verify API keys are correct in `.env`
- Check internet connection
- Ensure API quotas haven't been exceeded

### UI Issues
- Try running the test version first: `python3 elda_desktop_test.py`
- Check that tkinter is installed: `python3 -c "import tkinter"`

## Development

### Test Mode
The test version (`elda_desktop_test.py`) provides:
- Mock AI responses
- Step-by-step modal functionality
- No API key requirements
- Disabled voice features

### Adding New Features
1. Modify `elda_desktop.py` for the main application
2. Update `elda_desktop_test.py` for testing
3. Test both versions before deployment

## License

This project is part of the Elda AI Assistant system.

