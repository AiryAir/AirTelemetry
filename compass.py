import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import threading
import sv_ttk

class RotatingCompass(Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.configure(bg="#1c1c1c", highlightthickness=0)

        self.center_image = Image.open("assets\compass.png")
        self.rotating_image = Image.open("assets\\needle.png")

        self.center_image_tk = ImageTk.PhotoImage(self.center_image)
        self.rotating_image_tk = ImageTk.PhotoImage(self.rotating_image)

        # Calculate the center position of the window
        self.update_idletasks()  # Ensure window dimensions are updated
        self.center_x = self.parent.winfo_width() // 2
        self.center_y = self.parent.winfo_height() // 2

        # Calculate offsets for centering images
        self.center_image_offset_x = self.center_image_tk.width() // 2
        self.center_image_offset_y = self.center_image_tk.height() // 2
        self.rotating_image_offset_x = self.rotating_image_tk.width() // 2
        self.rotating_image_offset_y = self.rotating_image_tk.height() // 2

        # Place the center image in the middle of the window
        self.center_image_label = self.create_image(self.center_x, self.center_y, image=self.center_image_tk)

        # Place the rotating image in the same position as the center image
        self.rotating_image_label = self.create_image(self.center_x, self.center_y, image=self.rotating_image_tk)

        # Add text to display the angle
        self.angle_text = self.create_text(self.center_x, self.center_y, text="0°", fill="white", font=("Segoe UI Bold", 46))

        # Start the rotation loop in a separate thread
        self.rotate_thread = threading.Thread(target=self.rotate_loop, daemon=True)
        self.rotate_thread.start()

    def rotate_needle(self, angle):
        rotated_image = self.rotating_image.rotate(angle, expand=True)
        self.rotating_image_tk = ImageTk.PhotoImage(rotated_image)
        self.itemconfig(self.rotating_image_label, image=self.rotating_image_tk)
        self.coords(self.rotating_image_label, self.center_x, self.center_y)
        self.itemconfig(self.angle_text, text=f"{360 - angle}°")

    def rotate_loop(self):
        # while True:
        for angle in range(0, 360):
            self.rotate_needle(360 - angle)
            self.update()
            self.parent.after(10)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x700")
    compass = RotatingCompass(root)
    compass.pack(fill="both", expand=True)
    sv_ttk.set_theme("dark")
    root.mainloop()
