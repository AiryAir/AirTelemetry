import tkinter as tk
from PIL import Image, ImageTk

class AttitudeIndicator(tk.Canvas):
    def __init__(self, parent, bg_image_path, fg_image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bg_image_path = bg_image_path
        self.fg_image_path = fg_image_path

        # Load images
        self.bg_image = Image.open(bg_image_path)
        self.fg_image = Image.open(fg_image_path)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.fg_image_tk = ImageTk.PhotoImage(self.fg_image)

        # Create image items on the canvas
        self.bg_item = self.create_image(350, 350, anchor="center", image=self.bg_image_tk)
        self.fg_item = self.create_image(350, 350, anchor="center", image=self.fg_image_tk)

        # Create text items for pitch and roll
        self.pitch_text = self.create_text(10, 10, anchor="nw", font=("Segoe UI", 24, "bold"), fill="white", text="Pitch: 0°")
        self.roll_text = self.create_text(10, 50, anchor="nw", font=("Segoe UI", 24, "bold"), fill="white", text="Roll: 0°")

        self.pack(fill="both", expand=True)

    def update_attitude(self, pitch, roll):
        self.itemconfig(self.pitch_text, text=f"Pitch: {pitch}°")
        self.itemconfig(self.roll_text, text=f"Roll: {roll}°")

        # Calculate the new position of the background image based on pitch
        offset = int(pitch * 179 / 90)

        # Rotate the background image based on roll
        if abs(pitch) > 90:
            self.bg_image = Image.open(self.bg_image_path).rotate(180)
        else:
            self.bg_image = Image.open(self.bg_image_path)

        self.bg_image = self.bg_image.rotate(-roll)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.itemconfig(self.bg_item, image=self.bg_image_tk)
        self.coords(self.bg_item, 350, 350 + offset)

    def demo(self):
        import itertools
        import math

        pitches = itertools.chain(range(-90, 91, 2), range(90, -91, -2))
        rolls = itertools.cycle(itertools.chain(range(-90, 91, 2), range(90, -91, -2)))

        def animate():
            try:
                pitch = next(pitches)
                roll = next(rolls)

                if abs(pitch) > 90:
                    # Smooth flip transition
                    for step in range(1, 181, 10):
                        angle = step if pitch > 90 else -step
                        bg_image_rotated = Image.open(self.bg_image_path).rotate(180 + angle)
                        self.bg_image_tk = ImageTk.PhotoImage(bg_image_rotated)
                        self.itemconfig(self.bg_item, image=self.bg_image_tk)
                        self.update()
                        self.after(10)
                
                self.update_attitude(pitch, roll)
                self.update()
                self.after(50, animate)
            except StopIteration:
                pass

        animate()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Attitude Indicator")
    root.geometry("700x700")

    # Provide the paths to your background and foreground images
    bg_image_path = "assets/attitudebg.png"
    fg_image_path = "assets/attitudefg.png"

    ai = AttitudeIndicator(root, bg_image_path, fg_image_path, width=700, height=700)
    ai.pack(fill="both", expand=True)

    # Start the demo
    root.after(1000, ai.demo)
    
    root.mainloop()
