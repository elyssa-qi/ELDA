import subprocess
import re

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
    print(f"Volume set to {level}%")

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
        print(f"Current volume: {current}%")

    else:
        print("Command not recognized. Try:")
        print("  - 'increase volume' or 'increase volume by 20'")
        print("  - 'decrease volume' or 'decrease volume by 15'")
        print("  - 'set volume to 50'")
        print("  - 'mute' or 'max volume'")
        print("  - 'current volume'")

if __name__ == "__main__":
    print("AI Volume Control Agent")
    print("Commands: increase/decrease/set/mute/max/current")
    print("Type 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if command:
            parse_command(command)
