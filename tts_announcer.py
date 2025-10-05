"""
Elda Text-to-Speech Announcer
Uses ElevenLabs API to announce task completion and status updates
"""

import os
import requests
import io
import pygame
from dotenv import load_dotenv
import time

load_dotenv()

class EldaTTSAnnouncer:
    """Text-to-Speech announcer for Elda using ElevenLabs"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Default voice ID
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            print("✓ Audio system initialized")
        except Exception as e:
            print(f"⚠️ Audio system initialization failed: {e}")
    
    def _generate_speech(self, text, voice_id=None):
        """Generate speech audio from text using ElevenLabs API"""
        if not self.api_key:
            print("⚠️ ElevenLabs API key not found. Set ELEVENLABS_API_KEY in .env")
            return None
        
        voice_id = voice_id or self.voice_id
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"✗ ElevenLabs API error: {e}")
            return None
    
    def _play_audio(self, audio_data):
        """Play audio data using pygame"""
        try:
            # Create audio stream from bytes
            audio_stream = io.BytesIO(audio_data)
            
            # Load and play audio
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.01)
                
        except Exception as e:
            print(f"✗ Audio playback error: {e}")
    
    def announce_task_completion(self, task_description):
        """Announce that a task has been completed"""
        message = f"I've successfully completed the task: {task_description}"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
        else:
            print("⚠️ Could not generate speech, falling back to text only")
    
    def introduce_myself(self):
        message = "Hi I'm Elda, your personal digital assistant. How can I help you?"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_brightness_change(self, action):
        """Announce brightness adjustment"""
        message = f"I've {action} your screen brightness"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_volume_change(self, action):
        """Announce volume adjustment"""
        message = f"I've {action} your volume"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_zoom_change(self, action):
        """Announce zoom adjustment"""
        message = f"I've {action} the zoom level"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_how_to_triggered(self):
        """Announce that a how-to guide is being displayed"""
        message = "I'm showing you a helpful guide for that task"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_error(self, error_description):
        """Announce when an error occurs"""
        message = f"I encountered an issue: {error_description}"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def announce_listening(self):
        """Announce that Elda is ready to listen"""
        message = "I'm listening, how can I help you?"
        print(f"🔊 Elda announcing: {message}")
        
        audio_data = self._generate_speech(message)
        if audio_data:
            self._play_audio(audio_data)
    
    def test_tts(self):
        """Test the TTS system"""
        print("Testing TTS system...")
        test_message = "Hello! I'm Elda, your AI assistant. This is a test of my text-to-speech capabilities."
        
        audio_data = self._generate_speech(test_message)
        if audio_data:
            print("✓ TTS generation successful, playing audio...")
            self._play_audio(audio_data)
            print("✓ TTS test completed")
        else:
            print("✗ TTS test failed")
    
    def get_available_voices(self):
        """Get list of available voices from ElevenLabs"""
        if not self.api_key:
            print("⚠️ ElevenLabs API key not found")
            return []
        
        url = f"{self.base_url}/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            voices = response.json().get("voices", [])
            
            print("Available voices:")
            for voice in voices:
                print(f"  - {voice['name']} (ID: {voice['voice_id']})")
            
            return voices
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching voices: {e}")
            return []


# Convenience functions for easy integration
def announce_task_completion(task_description):
    """Convenience function to announce task completion"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_task_completion(task_description)

def announce_brightness_change(action):
    """Convenience function to announce brightness change"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_brightness_change(action)

def announce_volume_change(action):
    """Convenience function to announce volume change"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_volume_change(action)

def announce_zoom_change(action):
    """Convenience function to announce zoom change"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_zoom_change(action)

def announce_how_to_triggered():
    """Convenience function to announce how-to guide"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_how_to_triggered()

def announce_error(error_description):
    """Convenience function to announce errors"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_error(error_description)

def announce_listening():
    """Convenience function to announce listening status"""
    announcer = EldaTTSAnnouncer()
    announcer.announce_listening()

def introduce_myself():
    """Introduce Elda"""
    announcer = EldaTTSAnnouncer()
    announcer.introduce_myself()


if __name__ == "__main__":
    # Test the TTS system
    announcer = EldaTTSAnnouncer()
    
    print("=" * 60)
    print("ELDA TTS ANNOUNCER TEST")
    print("=" * 60)
    
    # Test basic functionality
    announcer.test_tts()
    
    print("\n" + "=" * 60)
    print("Testing task completion announcements...")
    print("=" * 60)
    
    # Test various announcements
    announcer.announce_task_completion("adjusting your screen brightness")
    time.sleep(2)
    
    announcer.announce_brightness_change("increased")
    time.sleep(2)
    
    announcer.announce_zoom_change("zoomed in")
    time.sleep(2)
    
    announcer.announce_how_to_triggered()
    time.sleep(2)
    
    print("\n✓ All TTS tests completed!")