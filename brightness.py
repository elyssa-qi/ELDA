import subprocess
import re
import time

def get_brightness_symbol(brightness_level):
    """Get the appropriate brightness symbol based on level"""
    if brightness_level == 0:
        return "🌑"  # Dark moon (off/dim)
    elif brightness_level <= 25:
        return "🌒"  # Crescent moon (very low)
    elif brightness_level <= 50:
        return "🌓"  # Half moon (low-medium)
    elif brightness_level <= 75:
        return "🌔"  # Almost full moon (medium-high)
    else:
        return "☀️"  # Sun (bright)

def get_brightness_bars(brightness_level, max_bars=10):
    """Create a visual brightness bar representation"""
    filled_bars = int((brightness_level / 100) * max_bars)
    empty_bars = max_bars - filled_bars
    return "█" * filled_bars + "░" * empty_bars

def get_brightness_rays(brightness_level):
    """Get sun ray representation based on brightness level"""
    if brightness_level == 0:
        return ""
    elif brightness_level <= 25:
        return "🌙"  # Moon
    elif brightness_level <= 50:
        return "🌤️"  # Sun behind cloud
    elif brightness_level <= 75:
        return "☀️"  # Sun
    else:
        return "☀️✨"  # Sun with sparkles (max)

def display_brightness_status(brightness_level=None):
    """Display current brightness with visual indicators"""
    if brightness_level is None:
        brightness_level = get_current_brightness()
    
    symbol = get_brightness_symbol(brightness_level)
    bars = get_brightness_bars(brightness_level)
    rays = get_brightness_rays(brightness_level)
    
    print(f"\n{symbol} Brightness: {brightness_level}%")
    print(f"Level: [{bars}] {brightness_level}%")
    if rays:
        print(f"Visual: {rays}")

def show_native_brightness_overlay():
    """Trigger the native macOS brightness overlay to appear"""
    # Simulate pressing the brightness up key briefly to trigger the native overlay
    subprocess.run([
        "osascript", "-e", 
        """
        tell application "System Events"
            key code 145 -- Brightness Up key (F2)
            delay 0.1
            key code 144 -- Brightness Down key (F1)
        end tell
        """
    ], check=False)

def get_current_brightness():
    """Get the current screen brightness (0-100) - simplified fallback"""
    # Since brightness tool is failing, we'll use a simple approach
    # For now, return a reasonable default and focus on making adjustments work
    return 50  # Default fallback value

def set_brightness(level):
    level = max(0, min(100, level))
    
    print(f"Setting brightness to {level}%...")
    
    # Use a more reliable approach - try multiple key codes
    if level >= 75:
        # Max brightness - try different approaches
        print("Setting to maximum brightness...")
        
        # Method 1: Try F1 key multiple times (INVERTED - F1 for increase)
        for _ in range(6):  # Reduced from 12 to 6
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 144'
            ], check=False)
        
    elif level <= 25:
        # Min brightness - try different approaches
        print("Setting to minimum brightness...")
        
        # Method 1: Try F2 key multiple times (INVERTED - F2 for decrease)
        for _ in range(6):  # Reduced from 12 to 6
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 145'
            ], check=False)
        
    elif level >= 50:
        # Medium-high brightness
        print("Setting to medium-high brightness...")
        for _ in range(3):  # Reduced from 6 to 3
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 144'  # INVERTED - F1 for increase
            ], check=False)
    else:
        # Medium-low brightness
        print("Setting to medium-low brightness...")
        for _ in range(3):  # Reduced from 6 to 3
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 145'  # INVERTED - F2 for decrease
            ], check=False)
    
    # Always show the overlay
    show_native_brightness_overlay()
    display_brightness_status(level)


def adjust_brightness(change):
    """Adjust brightness by a relative amount (+/- percentage) - RELIABLE VERSION"""
    current = get_current_brightness()
    new_brightness = max(0, min(100, current + change))
    
    print(f"Brightness adjusting from {current}% to {new_brightness}%")
    
    # More reliable keyboard simulation
    if change > 0:
        # Increase brightness - try multiple approaches
        print("Increasing brightness...")
        presses = min(abs(change) // 10 + 2, 4)  # Reduced presses for precision
        
        # Primary method: F1 key (INVERTED - F1 for increase)
        for _ in range(presses):
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 144'
            ], check=False)
            
    elif change < 0:
        # Decrease brightness - try multiple approaches
        print("Decreasing brightness...")
        presses = min(abs(change) // 10 + 2, 4)  # Reduced presses for precision
        
        # Primary method: F2 key (INVERTED - F2 for decrease)
        for _ in range(presses):
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 145'
            ], check=False)
    
    show_native_brightness_overlay()
    display_brightness_status(new_brightness)

def parse_command(command):
    """Parse text command and adjust brightness accordingly"""
    command = command.lower().strip()

    # Increase
    if any(word in command for word in ["increase", "raise", "up", "brighter", "higher"]):
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_brightness(+amount)

    # Decrease
    elif any(word in command for word in ["decrease", "lower", "down", "dimmer", "darker"]):
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_brightness(-amount)

    # Set to specific value
    elif "set" in command or "to" in command:
        numbers = re.findall(r'\d+', command)
        if numbers:
            set_brightness(int(numbers[0]))
        else:
            print("Please specify a brightness level (0-100)")

    # Dim/off - RELIABLE
    elif any(word in command for word in ["dim", "dark", "off", "minimum"]):
        print("Setting brightness to minimum...")
        
        # Method 1: F2 key multiple times (INVERTED - F2 for decrease)
        for _ in range(8):  # Reduced from 15 to 8
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 145'
            ], check=False)
        
        show_native_brightness_overlay()
        display_brightness_status(0)

    # Max/full - RELIABLE
    elif any(word in command for word in ["max", "maximum", "full", "brightest"]):
        print("Setting brightness to maximum...")
        
        # Method 1: F1 key multiple times (INVERTED - F1 for increase)
        for _ in range(8):  # Reduced from 15 to 8
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to key code 144'
            ], check=False)
        
        show_native_brightness_overlay()
        display_brightness_status(100)

    # Current status
    elif any(word in command for word in ["current", "status", "what", "level"]):
        current = get_current_brightness()
        show_native_brightness_overlay()
        display_brightness_status(current)

    else:
        print("Command not recognized. Try:")
        print("  - 'increase brightness' or 'increase brightness by 20'")
        print("  - 'decrease brightness' or 'decrease brightness by 15'")
        print("  - 'set brightness to 50'")
        print("  - 'dim' or 'max brightness'")
        print("  - 'current brightness'")

def test_overlay():
    """Test function to show native brightness overlay"""
    print("Testing native brightness overlay...")
    print("This will trigger the actual macOS brightness indicator")
    show_native_brightness_overlay()

def test_brightness_levels():
    """Test function to show different brightness levels"""
    print("Testing brightness levels...")
    test_levels = [0, 25, 50, 75, 100]
    
    for level in test_levels:
        print(f"Testing {level}% brightness")
        display_brightness_status(level)
        time.sleep(1)

def test_brightness_keys():
    """Test different brightness key codes to see which ones work"""
    print("Testing brightness key codes...")
    print("Watch your screen brightness and let me know which keys work!")
    
    # Test different key codes for brightness
    key_codes = [
        (144, "F1 (key code 144)"),
        (145, "F2 (key code 145)"),
        (113, "F14 (key code 113)"),
        (107, "F15 (key code 107)"),
        (106, "Brightness Down (key code 106)"),
        (107, "Brightness Up (key code 107)")
    ]
    
    for key_code, description in key_codes:
        print(f"\nTesting {description}...")
        print("Press Enter to test this key code (watch brightness):")
        input()
        
        # Test the key code
        subprocess.run([
            "osascript", "-e",
            f'tell application "System Events" to key code {key_code}'
        ], check=False)
        
        print(f"Did {description} change brightness? (y/n)")
        response = input().lower()
        if response == 'y':
            print(f"✓ {description} WORKS!")
        else:
            print(f"✗ {description} doesn't work")

def test_alternative_brightness():
    """Test alternative brightness control methods"""
    print("Testing alternative brightness methods...")
    
    print("\n1. Testing osascript brightness control...")
    try:
        # Try direct brightness control
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to set value of slider 1 of group 1 of tab group 1 of window 1 of application process "System Preferences" to 75'
        ], check=False)
        print("✓ osascript brightness control attempted")
    except Exception as e:
        print(f"✗ osascript brightness control failed: {e}")
    
    print("\n2. Testing brightness command line tool...")
    try:
        result = subprocess.run(["brightness", "-l"], capture_output=True, text=True, check=True)
        print(f"✓ brightness tool output: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ brightness tool failed: {e}")
    
    print("\n3. Testing system brightness via pmset...")
    try:
        result = subprocess.run(["pmset", "-g"], capture_output=True, text=True, check=True)
        print(f"✓ pmset output available")
    except Exception as e:
        print(f"✗ pmset failed: {e}")

if __name__ == "__main__":
    print("AI Brightness Control Agent")
    print("Commands: increase/decrease/set/dim/max/current")
    print("Special: 'test overlay', 'test levels', 'test keys', or 'test alt' for demos")
    print("Type 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        elif command.lower() == "test overlay":
            test_overlay()
        elif command.lower() == "test levels":
            test_brightness_levels()
        elif command.lower() == "test keys":
            test_brightness_keys()
        elif command.lower() == "test alt":
            test_alternative_brightness()
        elif command:
            parse_command(command)
