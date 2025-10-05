import os 
def increase_volume(amount=10):
    current_vol = int(os.popen("osascript -e 'output volume of (get volume settings)'").read().strip())
    new_vol = min(current_vol + amount, 100)
    os.system(f"osascript -e 'set volume output volume {new_vol}'")
    print(f"Volume increased to {new_vol}%")