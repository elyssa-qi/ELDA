import subprocess
import re
import os
import time

def get_volume_symbol(volume_level, muted=False):
    """Get the appropriate volume symbol based on volume level"""
    if muted or volume_level == 0:
        return "🔇"  # Muted speaker
    elif volume_level <= 33:
        return "🔈"  # Low volume speaker
    elif volume_level <= 66:
        return "🔉"  # Medium volume speaker
    else:
        return "🔊"  # High volume speaker

def get_volume_bars(volume_level, max_bars=10):
    """Create a visual volume bar representation"""
    filled_bars = int((volume_level / 100) * max_bars)
    empty_bars = max_bars - filled_bars
    return "█" * filled_bars + "░" * empty_bars

def get_volume_waves(volume_level):
    """Get sound wave representation based on volume level"""
    if volume_level == 0:
        return ""
    elif volume_level <= 25:
        return "▫"  # Small wave
    elif volume_level <= 50:
        return "▫▫"  # Two small waves
    elif volume_level <= 75:
        return "▫▫▫"  # Three small waves
    else:
        return "▫▫▫▫"  # Four waves (max)

def display_volume_status(volume_level=None):
    """Display current volume with visual indicators"""
    if volume_level is None:
        volume_level = get_current_volume()
    
    symbol = get_volume_symbol(volume_level)
    bars = get_volume_bars(volume_level)
    waves = get_volume_waves(volume_level)
    
    print(f"\n{symbol} Volume: {volume_level}%")
    print(f"Level: [{bars}] {volume_level}%")
    if waves:
        print(f"Waves: {waves}")

def show_native_volume_overlay():
    """Trigger the native macOS volume overlay to appear"""
    # Simulate pressing the volume up key briefly to trigger the native overlay
    subprocess.run([
        "osascript", "-e", 
        """
        tell application "System Events"
            key code 72 -- Volume Up key
            delay 0.1
            key code 74 -- Volume Down key  
        end tell
        """
    ], check=False)

def show_volume_notification(volume_level, action="Volume Changed"):
    """Show a native macOS notification for volume changes"""
    symbol = get_volume_symbol(volume_level)
    bars = get_volume_bars(volume_level, max_bars=8)  # Shorter bars for notification
    
    # Create notification message
    if volume_level == 0:
        message = "Volume Muted"
    elif volume_level == 100:
        message = "Volume at Maximum"
    else:
        message = f"Volume: {volume_level}% [{bars}]"
    
    # Send macOS notification with proper escaping
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{action}" subtitle "Volume Control"'
        ], check=True)
    except subprocess.CalledProcessError:
        # Fallback notification method
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{action}"'
        ], check=False)

def get_current_volume():
    """Get the current system volume (0-100)"""
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True,
        text=True
    )
    return int(result.stdout.strip())

def set_volume(level):
    """Set the system volume to a specific level (0-100)"""
    level = max(0, min(100, level))  # Clamp between 0-100
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {level}"],
        check=True
    )
    show_native_volume_overlay()
    show_volume_notification(level, "Volume Set")
    display_volume_status(level)

def adjust_volume(change):
    """Adjust volume by a relative amount (+/- percentage)"""
    current = get_current_volume()
    new_volume = current + change
    new_volume = max(0, min(100, new_volume))
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {new_volume}"],
        check=True
    )
    print(f"Volume adjusted from {current}% to {new_volume}%")
    show_native_volume_overlay()
    
    # Show appropriate notification based on change direction
    if change > 0:
        show_volume_notification(new_volume, "Volume Increased")
    else:
        show_volume_notification(new_volume, "Volume Decreased")
    
    display_volume_status(new_volume)

def parse_command(command):
    """Parse text command and adjust volume accordingly"""
    command = command.lower().strip()

    # Check for "increase/raise/up" commands
    if any(word in command for word in ["increase", "raise", "up", "louder", "higher"]):
        # Check for specific amount
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_volume(amount)

    # Check for "decrease/lower/down" commands
    elif any(word in command for word in ["decrease", "lower", "down", "quieter", "softer"]):
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_volume(-amount)

    # Check for "set to" or specific number
    elif "set" in command or "to" in command:
        numbers = re.findall(r'\d+', command)
        if numbers:
            set_volume(int(numbers[0]))
        else:
            print("Please specify a volume level (0-100)")

    # Check for mute
    elif "mute" in command:
        set_volume(0)

    # Check for max/full
    elif any(word in command for word in ["max", "maximum", "full"]):
        set_volume(100)

    # Check for current/status
    elif any(word in command for word in ["current", "status", "what", "level"]):
        current = get_current_volume()
        show_native_volume_overlay()
        display_volume_status(current)
    
    # Check for notification test
    elif "notify" in command:
        current = get_current_volume()
        show_volume_notification(current, "Current Volume")

    else:
        print("Command not recognized. Try:")
        print("  - 'increase volume' or 'increase volume by 20'")
        print("  - 'decrease volume' or 'decrease volume by 15'")
        print("  - 'set volume to 50'")
        print("  - 'mute' or 'max volume'")
        print("  - 'current volume' or 'notify'")

def test_overlay():
    """Test function to show native volume overlay"""
    print("Testing native volume overlay...")
    print("This will trigger the actual macOS volume indicator")
    show_native_volume_overlay()

def test_notification():
    """Test function to show volume notifications"""
    print("Testing volume notifications...")
    
    # Test basic notification first
    print("Testing basic notification...")
    try:
        subprocess.run([
            "osascript", "-e",
            'display notification "Test notification from volume control" with title "Test"'
        ], check=True)
        print("✓ Basic notification sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Basic notification failed: {e}")
        return
    
    # Test volume notifications
    print("Testing volume notifications...")
    test_levels = [25, 50, 75]
    
    for level in test_levels:
        print(f"Showing notification for {level}% volume")
        show_volume_notification(level, f"Test {level}%")
        time.sleep(1.5)  # Longer pause between notifications

if __name__ == "__main__":
    print("AI Volume Control Agent")
    print("Commands: increase/decrease/set/mute/max/current")
    print("Special: 'test overlay' or 'test notification' for demos")
    print("Type 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        elif command.lower() == "test overlay":
            test_overlay()
        elif command.lower() == "test notification":
            test_notification()
        elif command:
            parse_command(command)
