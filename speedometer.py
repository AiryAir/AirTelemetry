import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

class AnalogSpeedometer(Canvas):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("width", 700)
        kwargs.setdefault("height", 700)
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.configure(bg="#1c1c1c", highlightthickness=0)

        self.center_image = Image.open("assets/speedobg.png")
        self.rotating_image = Image.open("assets/pointy.png")

        self.center_image_tk = ImageTk.PhotoImage(self.center_image)
        self.rotating_image_tk = ImageTk.PhotoImage(self.rotating_image)

        # Rotation cache: angle -> PhotoImage
        self._rotation_cache = {}

        self.update_idletasks()
        self.center_x = self.parent.winfo_width() // 2
        self.center_y = self.parent.winfo_height() // 2

        self.center_image_label = self.create_image(self.center_x, self.center_y, image=self.center_image_tk)

        self.rotating_image_label = self.create_image(self.center_x, self.center_y, image=self.rotating_image_tk)

        self.angle_text = self.create_text(self.center_x, self.center_y, text="0", fill="white", font=("Segoe UI Bold", 46))

    def set_speed(self, speed):
        """Set the displayed speed value."""
        angle = speed % 360
        if angle < 90:
            self.rotate_needle(75)
            self.itemconfig(self.angle_text, text=f"{speed}")
        else:
            self.rotate_needle(angle)
            self.itemconfig(self.angle_text, text=f"{speed}")

    def rotate_needle(self, angle):
        rounded = round(angle) % 360
        if rounded not in self._rotation_cache:
            rotated_image = self.rotating_image.rotate(rounded, resample=Image.BICUBIC, expand=True)
            self._rotation_cache[rounded] = ImageTk.PhotoImage(rotated_image)
        self.rotating_image_tk = self._rotation_cache[rounded]
        self.itemconfig(self.rotating_image_label, image=self.rotating_image_tk)
        self.coords(self.rotating_image_label, self.center_x, self.center_y)
        self.itemconfig(self.angle_text, text=f"{360 - rounded}")

    def demo(self):
        angles = list(range(50, 361))
        def animate(idx=0):
            if idx < len(angles):
                angle = angles[idx]
                if angle < 90:
                    self.rotate_needle(75)
                    self.itemconfig(self.angle_text, text=f"{360 - angle}")
                else:
                    self.rotate_needle(angle)
                self.after(40, animate, idx + 1)
            else:
                self.demo()
        animate()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x700")
    compass = AnalogSpeedometer(root)
    compass.pack(fill="both", expand=True)
    root.after(1000, compass.demo)
    root.mainloop()
