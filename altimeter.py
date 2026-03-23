import tkinter as tk
from PIL import Image, ImageTk
import math


class Altimeter(tk.Canvas):

    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("width", 700)
        kwargs.setdefault("height", 700)
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1c1c1c", highlightthickness=0)

        # Load images
        self.bg_orig = Image.open("assets/altimeter-bg.png")
        self.ptr_10k_orig = Image.open("assets/10k_pointer.png")
        self.ptr_1k_orig = Image.open("assets/1k_pointer.png")
        self.ptr_100_orig = Image.open("assets/pointy.png")

        self.bg_tk = ImageTk.PhotoImage(self.bg_orig)

        # Initial pointer images
        self.ptr_10k_tk = ImageTk.PhotoImage(self.ptr_10k_orig)
        self.ptr_1k_tk = ImageTk.PhotoImage(self.ptr_1k_orig)
        self.ptr_100_tk = ImageTk.PhotoImage(self.ptr_100_orig)

        # Rotation cache: keyed by (pointer_id, rounded_angle) -> PhotoImage
        self._rotation_cache = {}

        # Canvas center
        self.cx = 350
        self.cy = 350

        # Place background
        self.bg_item = self.create_image(self.cx, self.cy, anchor="center", image=self.bg_tk)

        # On-gauge text (drawn before pointers so needles render on top)
        # Positioned to align with the labeled areas on the background image
        self.alt_text = self.create_text(self.cx, 348, anchor="center",
                                         font=("Segoe UI", 28, "bold"), fill="white", text="0")
        self.fl_text = self.create_text(175, 415, anchor="center",
                                        font=("Segoe UI", 22, "bold"), fill="white", text="0")
        self.pressure_text = self.create_text(self.cx, 448, anchor="center",
                                              font=("Segoe UI", 22, "bold"), fill="white", text="29.92")

        # Place pointers (order: 10k behind, then 1k, then 100ft on top)
        self.ptr_10k_item = self.create_image(self.cx, self.cy, anchor="center", image=self.ptr_10k_tk)
        self.ptr_1k_item = self.create_image(self.cx, self.cy, anchor="center", image=self.ptr_1k_tk)
        self.ptr_100_item = self.create_image(self.cx, self.cy, anchor="center", image=self.ptr_100_tk)

        self.pack(fill="both", expand=True)

    def _rotate_pointer(self, pointer_id, orig_image, angle):
        """Rotate a pointer image by angle degrees with caching. Images point down, so offset 180°."""
        # Round to 1° to limit cache size while keeping smooth visuals
        rounded = round(angle)
        key = (pointer_id, rounded)
        if key not in self._rotation_cache:
            rotated = orig_image.rotate(180 - rounded, resample=Image.BICUBIC, expand=True)
            self._rotation_cache[key] = ImageTk.PhotoImage(rotated)
        return self._rotation_cache[key]

    def update_altitude(self, altitude, pressure_hpa=1013.25):
        """Update the altimeter display for a given altitude in feet."""
        self.itemconfig(self.alt_text, text=f"{int(altitude)}")

        # Flight level = altitude / 100
        fl = int(altitude / 100)
        self.itemconfig(self.fl_text, text=f"{fl}")

        # Barometric formula: pressure drops ~1 hPa per 27ft near sea level
        pressure = pressure_hpa * (1 - altitude / 145442) ** 5.255
        pressure = max(pressure, 0.0)
        self.itemconfig(self.pressure_text, text=f"{pressure:.1f}")

        # 100ft hand: full rotation per 1,000ft
        angle_100 = (altitude % 1000) / 1000 * 360

        # 1,000ft hand: full rotation per 10,000ft
        angle_1k = (altitude % 10000) / 10000 * 360

        # 10,000ft hand: full rotation per 100,000ft
        angle_10k = (altitude % 100000) / 100000 * 360

        # Rotate and update each pointer (cached)
        self.ptr_100_tk = self._rotate_pointer("100", self.ptr_100_orig, angle_100)
        self.itemconfig(self.ptr_100_item, image=self.ptr_100_tk)

        self.ptr_1k_tk = self._rotate_pointer("1k", self.ptr_1k_orig, angle_1k)
        self.itemconfig(self.ptr_1k_item, image=self.ptr_1k_tk)

        self.ptr_10k_tk = self._rotate_pointer("10k", self.ptr_10k_orig, angle_10k)
        self.itemconfig(self.ptr_10k_item, image=self.ptr_10k_tk)

    def demo(self):
        """Demo: climb from 0 to 12,500ft, hold, descend back to 0, then loop."""
        # Climb phase: 0 -> 12500ft
        climb = [alt / 10 for alt in range(0, 125000, 60)]
        # Hold at 12500ft
        hold = [12500.0] * 20
        # Descend phase: 12500 -> 0ft
        descend = [alt / 10 for alt in range(125000, 0, -80)]
        # Hold at 0
        hold_ground = [0.0] * 15

        sequence = climb + hold + descend + hold_ground

        def animate(idx=0):
            if idx < len(sequence):
                self.update_altitude(sequence[idx])
                self.after(40, animate, idx + 1)
            else:
                self.demo()  # Loop

        animate()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Altimeter")
    root.geometry("700x700")
    root.configure(bg="#1c1c1c")

    alt = Altimeter(root)

    root.after(1000, alt.demo)
    root.mainloop()
