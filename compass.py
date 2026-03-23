import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import sv_ttk

class RotatingCompass(Canvas):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("width", 700)
        kwargs.setdefault("height", 700)
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.configure(bg="#1c1c1c", highlightthickness=0)

        self.center_image = Image.open("assets/compassbg.png")
        self.rotating_image = Image.open("assets/needle.png")

        self.center_image_tk = ImageTk.PhotoImage(self.center_image)
        self.rotating_image_tk = ImageTk.PhotoImage(self.rotating_image)

        # Rotation cache: angle -> PhotoImage
        self._rotation_cache = {}

        # Calculate the center position of the window
        self.update_idletasks()
        self.center_x = self.parent.winfo_width() // 2
        self.center_y = self.parent.winfo_height() // 2

        # Place the center image in the middle of the window
        self.center_image_label = self.create_image(self.center_x, self.center_y, image=self.center_image_tk)

        # Place the rotating image in the same position as the center image
        self.rotating_image_label = self.create_image(self.center_x, self.center_y, image=self.rotating_image_tk)

        # Add text to display the angle
        self.angle_text = self.create_text(self.center_x, self.center_y, text="0°", fill="white", font=("Segoe UI Bold", 46))

    def set_heading(self, heading):
        """Set the compass heading (0-360 degrees)."""
        self.rotate_needle(360 - (heading % 360))

    def rotate_needle(self, angle):
        rounded = round(angle) % 360
        if rounded not in self._rotation_cache:
            rotated_image = self.rotating_image.rotate(rounded, resample=Image.BICUBIC, expand=True)
            self._rotation_cache[rounded] = ImageTk.PhotoImage(rotated_image)
        self.rotating_image_tk = self._rotation_cache[rounded]
        self.itemconfig(self.rotating_image_label, image=self.rotating_image_tk)
        self.coords(self.rotating_image_label, self.center_x, self.center_y)
        self.itemconfig(self.angle_text, text=f"{(360 - rounded) % 360}°")

    def demo(self):
        angles = list(range(0, 360))
        def animate(idx=0):
            if idx < len(angles):
                self.rotate_needle(360 - angles[idx])
                self.after(40, animate, idx + 1)
            else:
                self.demo()
        animate()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x700")
    compass = RotatingCompass(root)
    compass.pack(fill="both", expand=True)
    sv_ttk.set_theme("dark")
    root.after(1000, compass.demo)
    root.mainloop()
