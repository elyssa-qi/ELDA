# websocket_client.py
import asyncio
import websockets
import json

class ElectronClient:
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
    
    async def connect(self):
        """Connect to Electron WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print("✅ Connected to Electron")
        except Exception as e:
            print(f"⚠️ Failed to connect to Electron: {e}")
    
    async def send_command(self, command, **kwargs):
        """Send a command to Electron"""
        if not self.websocket:
            await self.connect()
        
        if self.websocket:
            message = {"command": command, **kwargs}
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent to Electron: {command}")
    
    async def show_listening(self):
        """Show listening state in Electron"""
        await self.send_command("showListening")
    
    async def show_how_to(self, transcription):
        """Show how-to tutorial in Electron"""
        await self.send_command("showHowTo", transcription=transcription)
    
    async def close(self):
        """Close the connection"""
        if self.websocket:
            await self.websocket.close()

# Synchronous wrappers for easy use
def trigger_electron_listening():
    """Synchronous function to show listening state"""
    async def _trigger():
        client = ElectronClient()
        await client.connect()
        await client.show_listening()
        await client.close()
    
    try:
        asyncio.run(_trigger())
    except Exception as e:
        print(f"⚠️ Error showing listening state: {e}")

def trigger_electron_howto(transcription):
    """Synchronous function to trigger Electron from anywhere"""
    async def _trigger():
        client = ElectronClient()
        await client.connect()
        await client.show_how_to(transcription)
        await client.close()
    
    try:
        asyncio.run(_trigger())
    except Exception as e:
        print(f"⚠️ Error triggering Electron: {e}")