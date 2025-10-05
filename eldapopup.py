import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time

def show_popup(png_path, process_function, loading_gif_path=None):
    popup = tk.Tk()
    popup.overrideredirect(True)

# Make the window transparent
    popup.attributes('-transparentcolor', 'black')  # Makes black pixels transparent
    popup.attributes('-topmost', True) 
    popup.geometry("400x400+500+200")  # adjust size/position

    # Display static PNG first
    img = Image.open(png_path)
    img = img.resize((300, 300))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(popup, image=photo)
    label_img.photo = photo  # keep reference
    label_img.pack(pady=10)

    # Placeholder for loading GIF
    loading_label = None
    frames = []

    if loading_gif_path:
        loading_label = tk.Label(popup)
        loading_label.pack(pady=10)

        # Load all frames from GIF
        gif = Image.open(loading_gif_path)
        for frame in ImageSequence.Iterator(gif):
            frame = frame.resize((100, 100))  # optional resize
            frames.append(ImageTk.PhotoImage(frame))

        def animate(frame_index=0):
            if frames:
                loading_label.config(image=frames[frame_index])
                loading_label.photo = frames[frame_index]  # keep reference
                popup.after(100, animate, (frame_index + 1) % len(frames))

    # Run your process in a thread
    def run_process():
        # Start GIF animation if available
        if frames:
            animate()
        process_function()  # your AI step generator or API call
        popup.destroy()      # close popup when done

    threading.Thread(target=run_process, daemon=True).start()
    popup.mainloop()
