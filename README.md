# Elda - AI Voice Assistant

Elda is an intelligent voice assistant specifically designed to help elderly users navigate technology with confidence. Using advanced AI and natural language processing, Elda provides step-by-step visual tutorials triggered by simple voice commands, making technology more accessible for seniors.

## 🌟 Features

### 🎤 **Voice Interaction**
- **Wake Word Detection**: Uses Porcupine wake word engine with custom "Hey Elda" trigger
- **Speech-to-Text**: Powered by OpenAI Whisper for accurate voice transcription
- **Intent Recognition**: AI-powered command understanding using Google Gemini
- **Text-to-Speech**: ElevenLabs integration for natural voice responses

### 🎛️ **System Control**
- **Volume Control**: Increase/decrease system volume by 50% or custom amounts
- **Brightness Control**: Adjust screen brightness with voice commands
- **Screen Zoom**: Control macOS accessibility zoom features
- **Smart Defaults**: All commands default to 50% adjustments for better user experience

### 📚 **Interactive Tutorials**
- **AI-Generated Guides**: Creates step-by-step tutorials for any topic
- **Visual Interface**: Beautiful Electron-based tutorial cards
- **Progress Tracking**: Save and resume tutorial progress
- **Detailed Help**: Expandable help sections for each step

### 🎨 **Modern Interface**
- **React Frontend**: Responsive tutorial interface with smooth animations
- **Always-on-Top Window**: Non-intrusive popup that stays accessible
- **Visual States**: Different Elda avatars for listening, thinking, and tutorial modes
- **Real-time Updates**: Live WebSocket communication between components

## 🏗️ Architecture

```
Elda/
├── voice.py                 # Main wake word detection and orchestration
├── speech2text/
│   ├── stt_capture.py      # Speech processing and intent handling
│   └── howto_generator.py  # Flask API for tutorial generation
├── tts_announcer.py        # Text-to-speech with ElevenLabs
├── volume.py               # System volume control
├── brightness.py           # Screen brightness control
├── zoom_controller/        # macOS zoom accessibility features
├── websocket_client.py     # Electron communication
└── elda-app/              # Electron frontend
    ├── main.js            # Electron main process
    ├── renderer/          # React frontend
    │   ├── App.jsx        # Main tutorial interface
    │   ├── components/    # React components
    │   └── styles.css     # Styling
    └── package.json       # Node.js dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **macOS** (for system controls)
- **Microphone access**

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Elda
```

### 2. Python Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Node.js Dependencies

```bash
cd elda-app
npm install
cd ..
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Wake Word Detection
ACCESS_KEY=your_porcupine_access_key

# AI Services
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
```

### 5. Start the Services

**Terminal 1 - Main Voice Assistant:**
```bash
source .venv/bin/activate
python voice.py
```

**Terminal 2 - Tutorial Generator API:**
```bash
source .venv/bin/activate
python speech2text/howto_generator.py
```

**Terminal 3 - Electron Frontend:**
```bash
cd elda-app
npm start
```

## 🎯 Voice Commands

### System Control
- **"Hey Elda, increase volume"** - Increase volume by 50%
- **"Hey Elda, decrease volume"** - Decrease volume by 50%
- **"Hey Elda, turn up volume by 25"** - Custom volume adjustment
- **"Hey Elda, make it brighter"** - Increase screen brightness
- **"Hey Elda, zoom in"** - Zoom into screen
- **"Hey Elda, zoom out"** - Zoom out of screen

### Information & Help
- **"Hey Elda, introduce yourself"** - Get Elda's introduction
- **"Hey Elda, show me how to [topic]"** - Generate interactive tutorial
- **"Hey Elda, how do I [action]"** - Get step-by-step guidance

### Examples
- "Hey Elda, how do I send an email?"
- "Hey Elda, can you make this video louder?"
- "Hey Elda, zoom in on the screen please?"

## 🔧 Configuration

### Custom Wake Word
Replace `hello_elda.ppn` with your custom Porcupine wake word model.

### Voice Settings
Modify voice settings in `tts_announcer.py`:
```python
self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "your_default_voice")
```

### Tutorial Customization
Adjust tutorial generation in `howto_generator.py`:
```python
HOWTO_SYSTEM_PROMPT = """Your custom prompt here..."""
```

## 🛠️ Development

### Adding New Commands

1. **Add Intent Detection** in `speech2text/stt_capture.py`:
```python
# In detect_intent_keywords()
if any(word in text for word in ["your", "keywords"]):
    return "your_new_intent"
```

2. **Handle the Command**:
```python
elif intent == "your_new_intent":
    print("🆕 New command detected!")
    # Your implementation here
```

3. **Update Gemini Prompt** to recognize the new intent.

### Adding New System Controls

Create a new module (e.g., `new_feature.py`) and integrate it:
```python
from new_feature import your_function
# Add to handle_command()
```

## 📱 Interface Components

### EldaState Component
- **Listening State**: Shows Elda avatar when ready to listen
- **Thinking State**: Animated thinking gif during processing
- **Tutorial State**: Interactive tutorial cards

### TutorialCard Component
- **Step Navigation**: Next/Previous buttons
- **Progress Tracking**: Visual progress indicators
- **Detailed Help**: Expandable help sections
- **Completion Tracking**: Mark steps as completed

## 🔐 Permissions

### macOS Accessibility
For zoom and brightness controls, grant Terminal accessibility permissions:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Add Terminal (or your terminal app)
3. Enable the checkbox

### Microphone Access
Grant microphone permissions for wake word detection and speech recognition.

## 🐛 Troubleshooting

### Common Issues

**"Wake word not detected"**
- Check microphone permissions
- Verify Porcupine access key
- Ensure quiet environment

**"Intent detection fails"**
- Check Gemini API quota (50 requests/day free tier)
- System falls back to keyword matching automatically
- Verify API keys in `.env`

**"Tutorial not showing"**
- Ensure Flask server is running (`python speech2text/howto_generator.py`)
- Check port 3000 is available
- Verify Electron frontend is running

**"Volume/Brightness not working"**
- Grant accessibility permissions
- Try running from terminal with elevated permissions
- Check macOS version compatibility

### Logs and Debugging

Enable debug mode by setting environment variables:
```bash
export DEBUG=1
python voice.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
