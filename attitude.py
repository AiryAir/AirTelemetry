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

        self.pitch_text = self.create_text(350, 15, anchor="n", font=("Chakra Petch", 16), fill="white", text="Pitch: 0°")
        self.roll_text = self.create_text(350, 45, anchor="n", font=("Chakra Petch", 16), fill="white", text="Roll: 0°")

        self.pack(fill="both", expand=True)

    def pitch_to_pixels(self, pitch):
        # Linear mapping: -90..90 pitch to -262..262 pixels
        max_pitch = 90
        max_pixels = 262
        return (pitch / max_pitch) * max_pixels

    def update_attitude(self, pitch, roll):
        self.itemconfig(self.pitch_text, text=f"Pitch: {pitch}°")
        self.itemconfig(self.roll_text, text=f"Roll: {roll}°")

        flip = False
        if pitch > 90:
            pitch = 180 - pitch
            flip = True
        elif pitch < -90:
            pitch = -180 - pitch
            flip = True

        pitch_offset = self.pitch_to_pixels(pitch)

        # Calculate offset direction based on roll
        roll_radians = math.radians(roll)
        dx = -pitch_offset * math.sin(roll_radians)
        dy = pitch_offset * math.cos(roll_radians)

        # Always rotate from the original image to avoid quality loss
        if not hasattr(self, 'bg_image_orig'):
            self.bg_image_orig = Image.open(self.bg_image_path)
        bg_image = self.bg_image_orig.transpose(Image.ROTATE_180) if flip else self.bg_image_orig
        bg_image = bg_image.rotate(-roll, resample=Image.BICUBIC, expand=False)
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        self.itemconfig(self.bg_item, image=self.bg_image_tk)
        self.coords(self.bg_item, 350 + dx, 350 + dy)

    def demo(self):
        def animate_pitch(pitch_sequence, roll=0, next_animation=None):
            pitches = iter(pitch_sequence)
            def animate():
                try:
                    pitch = next(pitches)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            animate()

        def animate_roll(roll_sequence, pitch=0, next_animation=None):
            rolls = iter(roll_sequence)
            def animate():
                try:
                    roll = next(rolls)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            animate()

        def animate_pitch_and_roll(pitch_sequence, roll_sequence, next_animation=None):
            pitches = iter(pitch_sequence)
            rolls = iter(roll_sequence)
            def animate():
                try:
                    pitch = next(pitches)
                    roll = next(rolls)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            animate()

        # Create pitch sequences that stay within safe range
        pitch_sequence_full_up = list(range(-45, 46, 3))
        pitch_sequence_full_down = list(range(45, -46, -3))
        pitch_sequence_level = [0] * 20
        
        # Create roll sequences with better range
        roll_sequence_full_right = list(range(0, 46, 3))
        roll_sequence_full_left = list(range(45, -46, -3))
        roll_sequence_level = [0] * 20

        animate_pitch(
            pitch_sequence_full_up,
            next_animation=lambda: animate_pitch(
                pitch_sequence_full_down,
                next_animation=lambda: animate_pitch(
                    pitch_sequence_level,
                    next_animation=lambda: animate_roll(
                        roll_sequence_full_right,
                        next_animation=lambda: animate_roll(
                            roll_sequence_full_left,
                            next_animation=lambda: animate_roll(
                                roll_sequence_level,
                                next_animation=lambda: animate_pitch_and_roll(
                                    pitch_sequence_full_up + pitch_sequence_full_down + pitch_sequence_level,
                                    roll_sequence_full_right + roll_sequence_full_left + roll_sequence_level
                                )
                            )
                        )
                    )
                )
            )
        )

    def quick_flip(self, pitch, roll, next_animation=None):
        def animate():
            if pitch > 90 or pitch < -90:
                self.bg_image = Image.open(self.bg_image_path).rotate(180 if pitch > 90 else -180)
                self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
                self.itemconfig(self.bg_item, image=self.bg_image_tk)
                self.update()
                # Do not call update_attitude with a problematic pitch, just continue
                if next_animation:
                    next_animation()
        self.after(10, animate)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Attitude Indicator")
    root.geometry("700x700")

    bg_image_path = "assets/attitudebg1.png"
    fg_image_path = "assets/attitudefg.png"

    ai = AttitudeIndicator(root, bg_image_path, fg_image_path, width=700, height=700)
    ai.pack(fill="both", expand=True)

    # Start the demo
    root.after(1000, ai.demo)
    
    root.mainloop()
