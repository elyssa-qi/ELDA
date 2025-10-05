import subprocess
import time

def increase_brightness():
    """Increase brightness by 25%"""
    print("🔆 Increasing brightness by 25%...")
    
    # Try multiple approaches to increase brightness
    # Method 1: F1 key (key code 144) - most common for brightness up
    for i in range(4):  # 4 presses for ~25% increase
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to key code 144'
        ], check=False)
        time.sleep(0.1)  # Small delay between presses
    
    # Method 2: If F1 doesn't work, try F15 (key code 107)
    time.sleep(0.5)
    for i in range(2):  # Backup method
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to key code 107'
        ], check=False)
        time.sleep(0.1)
    
    # Show native brightness overlay
    subprocess.run([
        "osascript", "-e", 
        """
        tell application "System Events"
            key code 144 -- Trigger overlay
            delay 0.2
        end tell
        """
    ], check=False)

def decrease_brightness():
    """Decrease brightness by 25%"""
    print("🌙 Decreasing brightness by 25%...")
    
    # Try multiple approaches to decrease brightness
    # Method 1: F2 key (key code 145) - most common for brightness down
    for i in range(4):  # 4 presses for ~25% decrease
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to key code 145'
        ], check=False)
        time.sleep(0.1)  # Small delay between presses
    
    # Method 2: If F2 doesn't work, try F14 (key code 113)
    time.sleep(0.5)
    for i in range(2):  # Backup method
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to key code 113'
        ], check=False)
        time.sleep(0.1)
    
    # Show native brightness overlay
    subprocess.run([
        "osascript", "-e", 
        """
        tell application "System Events"
            key code 145 -- Trigger overlay
            delay 0.2
        end tell
        """
    ], check=False)