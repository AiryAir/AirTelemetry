import tkinter as tk
from PIL import Image, ImageTk
import math

class AttitudeIndicator(tk.Canvas):
    def __init__(self, parent, bg_image_path, fg_image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bg_image_path = bg_image_path
        self.fg_image_path = fg_image_path

        self.bg_image = Image.open(bg_image_path)
        self.fg_image = Image.open(fg_image_path)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.fg_image_tk = ImageTk.PhotoImage(self.fg_image)

        self.bg_item = self.create_image(350, 350, anchor="center", image=self.bg_image_tk)
        self.fg_item = self.create_image(350, 350, anchor="center", image=self.fg_image_tk)

        self.pitch_text = self.create_text(350, 20, anchor="n", font=("Segoe UI", 12), fill="white", text="Pitch: 0°")
        self.roll_text = self.create_text(350, 40, anchor="n", font=("Segoe UI", 12), fill="white", text="Roll: 0°")

        self.pack(fill="both", expand=True)

    def update_attitude(self, pitch, roll):
        self.itemconfig(self.pitch_text, text=f"Pitch: {pitch}°")
        self.itemconfig(self.roll_text, text=f"Roll: {roll}°")

        pitch_offset = int(pitch * 179 / 90)
        
        roll_radians = math.radians(roll)
        roll_compensation = pitch_offset * math.cos(roll_radians)
        
        # Total offset
        total_offset = pitch_offset + roll_compensation

        if abs(pitch) > 90:
            self.bg_image = Image.open(self.bg_image_path).rotate(180)
        else:
            self.bg_image = Image.open(self.bg_image_path)

        self.bg_image = self.bg_image.rotate(-roll)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.itemconfig(self.bg_item, image=self.bg_image_tk)
        self.coords(self.bg_item, 350, 350 + total_offset)

    def demo(self):
        import itertools

        pitches = itertools.chain(range(-90, 91, 2), range(90, -91, -2))
        rolls = itertools.cycle(itertools.chain(range(-90, 91, 2), range(90, -91, -2)))

        def animate():
            try:
                pitch = next(pitches)
                roll = next(rolls)

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

    bg_image_path = "assets/attitudebg.png"
    fg_image_path = "assets/attitudefg.png"

    ai = AttitudeIndicator(root, bg_image_path, fg_image_path, width=700, height=700)
    ai.pack(fill="both", expand=True)

    # Start the demo
    root.after(1000, ai.demo)
    
    root.mainloop()
