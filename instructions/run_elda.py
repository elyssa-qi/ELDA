#!/usr/bin/env python3
"""
Elda AI Assistant Launcher
Run this script to start the Elda desktop application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['tkinter', 'threading', 're', 'json']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("⚠️  .env file not found!")
        print("Please create a .env file with your API keys:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("ELEVEN_KEY=your_elevenlabs_api_key_here")
        print("ELEVEN_VOICE_ID=your_voice_id_here")
        print("\nRunning in test mode instead...")
        return False
    
    # Check if API keys are set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content or 'your_elevenlabs_api_key_here' in content:
            print("⚠️  API keys not configured in .env file!")
            print("Please update your .env file with actual API keys.")
            print("Running in test mode instead...")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 Elda AI Assistant Launcher")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed!")
        sys.exit(1)
    
    # Check environment
    has_api_keys = check_env_file()
    
    # Determine which version to run
    if has_api_keys:
        print("✅ API keys found. Starting full version...")
        script_name = "elda_desktop.py"
    else:
        print("🧪 Starting test version...")
        script_name = "elda_desktop_test.py"
    
    # Get script path
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
    
    print(f"🚀 Launching {script_name}...")
    print("Press Ctrl+C to stop the application")
    print("=" * 40)
    
    try:
        # Run the application
        subprocess.run([sys.executable, str(script_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Elda stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Elda: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

