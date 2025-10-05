import subprocess
import re

def get_current_brightness():
    """Get the current display brightness (0-100)"""
    try:
        result = subprocess.run(
            ["osascript", "-e", "tell application \"System Events\" to get value of slider 1 of group 1 of tab group 1 of window 1 of application process \"System Settings\""],
            capture_output=True,
            text=True
        )
        # Alternative method using brightnessctl if available
        if result.returncode != 0:
            result = subprocess.run(
                ["brightnessctl", "get"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # brightnessctl returns values like 255, convert to percentage
                brightness = int(result.stdout.strip())
                return int((brightness / 255) * 100)
        
        # Fallback: try to get from system
        return 50  # Default fallback
    except Exception as e:
        print(f"Error getting brightness: {e}")
        return 50

def set_brightness(level):
    """Set the display brightness to a specific level (0-100)"""
    level = max(0, min(100, level))  # Clamp between 0-100
    try:
        # Try brightnessctl first (if available)
        result = subprocess.run(
            ["brightnessctl", "set", f"{level}%"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Brightness set to {level}%")
            return
        
        # Fallback to AppleScript
        subprocess.run(
            ["osascript", "-e", f"tell application \"System Events\" to set value of slider 1 of group 1 of tab group 1 of window 1 of application process \"System Settings\" to {level}"],
            check=True
        )
        print(f"Brightness set to {level}%")
    except Exception as e:
        print(f"Error setting brightness: {e}")

def adjust_brightness(change):
    """Adjust brightness by a relative amount (+/- percentage)"""
    current = get_current_brightness()
    new_brightness = current + change
    new_brightness = max(0, min(100, new_brightness))
    set_brightness(new_brightness)
    print(f"Brightness adjusted from {current}% to {new_brightness}%")

def parse_command(command):
    """Parse text command and adjust brightness accordingly"""
    command = command.lower().strip()

    # Check for "increase/raise/up" commands
    if any(word in command for word in ["increase", "raise", "up", "brighter", "higher"]):
        # Check for specific amount
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_brightness(amount)

    # Check for "decrease/lower/down" commands
    elif any(word in command for word in ["decrease", "lower", "down", "dimmer", "dim", "softer"]):
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_brightness(-amount)

    # Check for "set to" or specific number
    elif "set" in command or "to" in command:
        numbers = re.findall(r'\d+', command)
        if numbers:
            set_brightness(int(numbers[0]))
        else:
            print("Please specify a brightness level (0-100)")

    # Check for minimum/maximum
    elif any(word in command for word in ["min", "minimum", "darkest"]):
        set_brightness(0)

    elif any(word in command for word in ["max", "maximum", "brightest", "full"]):
        set_brightness(100)

    # Check for current/status
    elif any(word in command for word in ["current", "status", "what", "level"]):
        current = get_current_brightness()
        print(f"Current brightness: {current}%")

    else:
        print("Command not recognized. Try:")
        print("  - 'increase brightness' or 'increase brightness by 20'")
        print("  - 'decrease brightness' or 'decrease brightness by 15'")
        print("  - 'set brightness to 50'")
        print("  - 'minimum brightness' or 'maximum brightness'")
        print("  - 'current brightness'")

if __name__ == "__main__":
    print("AI Brightness Control Agent")
    print("Commands: increase/decrease/set/min/max/current")
    print("Type 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if command:
            parse_command(command)
