# IN BETA, INACCURATE PITCH INDICATION ON ROLL

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
        if pitch == 0:
            return 0
        elif pitch == 15:
            return 43.67
        elif pitch == 30:
            return 87.33
        elif pitch == 45:
            return 131
        elif pitch == 60:
            return 174.67
        elif pitch == 75:
            return 218.33
        elif pitch == 90:
            return 262
        else:
            abs_pitch = abs(pitch)
            if abs_pitch < 15:
                return abs_pitch * 43.67 / 15
            elif abs_pitch < 30:
                return 43.67 + (abs_pitch - 15) * (87.33 - 43.67) / 15
            elif abs_pitch < 45:
                return 87.33 + (abs_pitch - 30) * (131 - 87.33) / 15
            elif abs_pitch < 60:
                return 131 + (abs_pitch - 45) * (174.67 - 131) / 15
            elif abs_pitch < 75:
                return 174.67 + (abs_pitch - 60) * (218.33 - 174.67) / 15
            elif abs_pitch < 90:
                return 218.33 + (abs_pitch - 75) * (262 - 218.33) / 15
            else:
                return 262

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
        if pitch < 0:
            pitch_offset = -pitch_offset

        roll_radians = math.radians(roll)
        roll_compensation = pitch_offset * math.cos(roll_radians)

        total_offset = pitch_offset

        if flip:
            self.bg_image = Image.open(self.bg_image_path).rotate(180)
        else:
            self.bg_image = Image.open(self.bg_image_path)

        self.bg_image = self.bg_image.rotate(-roll)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.itemconfig(self.bg_item, image=self.bg_image_tk)
        self.coords(self.bg_item, 350, 350 + total_offset)

    def demo(self):
        def animate_pitch(pitch_sequence, roll=0, next_animation=None):
            def animate():
                try:
                    pitch = next(pitches)
                    if abs(pitch) > 88:
                        self.quick_flip(pitch, roll, next_animation)
                        return
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            pitches = iter(pitch_sequence)
            animate()

        def animate_roll(roll_sequence, pitch=0, next_animation=None):
            def animate():
                try:
                    roll = next(rolls)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            rolls = iter(roll_sequence)
            animate()

        def animate_pitch_and_roll(pitch_sequence, roll_sequence, next_animation=None):
            def animate():
                try:
                    pitch = next(pitches)
                    roll = next(rolls)
                    if abs(pitch) > 88:
                        self.quick_flip(pitch, roll, next_animation)
                        return
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            pitches = iter(pitch_sequence)
            rolls = iter(roll_sequence)
            animate()

        pitch_sequence_full_up = list(range(-6, 6, 2))
        pitch_sequence_full_down = list(range(6, -6, -2))
        pitch_sequence_flip_over = list(range(0, 120, 2)) + list(range(120, 0, -2))
        pitch_sequence_level = [0] * 36
        roll_sequence_full_right = list(range(0, 6, 2))
        roll_sequence_full_left = list(range(6, -6, -2))
        roll_sequence_level = [0] * 36

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
                                    roll_sequence_full_right + roll_sequence_full_left + roll_sequence_level,
                                    next_animation=lambda: self.quick_flip(
                                        pitch_sequence_flip_over[0], 0, animate_pitch_and_roll(
                                            pitch_sequence_flip_over, [0]*len(pitch_sequence_flip_over)
                                        )
                                    )
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
                new_pitch = 180 - pitch if pitch > 90 else -180 - pitch
                self.update_attitude(new_pitch, roll)
                self.update()
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
