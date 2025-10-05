import subprocess
import re

def get_current_brightness():
    """Get the current screen brightness (0-100)"""
    try:
        result = subprocess.run(["brightness", "-l"], capture_output=True, text=True, check=True)
        # Example output line: "display 0: brightness 0.500000"
        for line in result.stdout.splitlines():
            if "brightness" in line:
                value = float(line.split()[-1])
                return int(value * 100)
        print("Error: Could not parse brightness")
        return 50  # fallback
    except FileNotFoundError:
        print("Error: 'brightness' command not found. Install with 'brew install brightness'")
        return 50
    except Exception as e:
        print(f"Error getting brightness: {e}")
        return 50

def set_brightness(level):
    level = max(0, min(100, level))
    value = level / 100
    try:
        subprocess.run(["brightness", str(value)], check=True)
        print(f"Brightness set to {level}%")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set brightness: {e}")
    except FileNotFoundError:
        print("Error: 'brightness' command not found. Install with 'brew install brightness'")


def adjust_brightness(change):
    """Adjust brightness by a relative amount (+/- percentage)"""
    current = get_current_brightness()
    new_brightness = max(0, min(100, current + change))
    set_brightness(new_brightness)
    print(f"Brightness adjusted from {current}% to {new_brightness}%")

def parse_command(command):
    """Parse text command and adjust brightness accordingly"""
    command = command.lower().strip()

    # Increase
    if any(word in command for word in ["increase", "raise", "up", "brighter", "higher"]):
        numbers = re.findall(r'\d+', command)
        amount = int(numbers[0]) if numbers else 10
        adjust_brightness(amount)

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

    # Dim/off
    elif any(word in command for word in ["dim", "dark", "off", "minimum"]):
        set_brightness(0)

    # Max/full
    elif any(word in command for word in ["max", "maximum", "full", "brightest"]):
        set_brightness(100)

    # Current status
    elif any(word in command for word in ["current", "status", "what", "level"]):
        current = get_current_brightness()
        print(f"Current brightness: {current}%")

    else:
        print("Command not recognized. Try:")
        print("  - 'increase brightness' or 'increase brightness by 20'")
        print("  - 'decrease brightness' or 'decrease brightness by 15'")
        print("  - 'set brightness to 50'")
        print("  - 'dim' or 'max brightness'")
        print("  - 'current brightness'")

if __name__ == "__main__":
    print("AI Brightness Control Agent")
    print("Commands: increase/decrease/set/dim/max/current")
    print("Type 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if command:
            parse_command(command)
