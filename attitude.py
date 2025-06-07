import tkinter as tk
from PIL import Image, ImageTk
import math

class AttitudeIndicator(tk.Canvas):    def __init__(self, parent, bg_image_path, fg_image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bg_image_path = bg_image_path
        self.fg_image_path = fg_image_path

        # Load and cache original images
        self.bg_image_orig = Image.open(bg_image_path)
        self.fg_image = Image.open(fg_image_path)
        
        # Pre-create rotated images cache for better performance
        self.bg_image_cache = {}
        self.bg_image_flipped_cache = {}
        
        # Initial images
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image_orig)
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
        effective_roll = roll
        
        # Handle edge case when crossing 90° pitch
        if pitch > 90:
            pitch = 180 - pitch
            flip = True
            # When inverted, roll direction is reversed
            effective_roll = -roll + 180
        elif pitch < -90:
            pitch = -180 - pitch
            flip = True
            # When inverted, roll direction is reversed
            effective_roll = -roll - 180

        # Normalize roll to -180 to 180 range
        while effective_roll > 180:
            effective_roll -= 360
        while effective_roll < -180:
            effective_roll += 360

        pitch_offset = self.pitch_to_pixels(pitch)

        # Calculate offset direction based on effective roll
        roll_radians = math.radians(effective_roll)
        dx = -pitch_offset * math.sin(roll_radians)
        dy = pitch_offset * math.cos(roll_radians)

        # Always rotate from the original image to avoid quality loss
        if not hasattr(self, 'bg_image_orig'):
            self.bg_image_orig = Image.open(self.bg_image_path)
        bg_image = self.bg_image_orig.transpose(Image.ROTATE_180) if flip else self.bg_image_orig
        bg_image = bg_image.rotate(-effective_roll, resample=Image.BICUBIC, expand=False)
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        self.itemconfig(self.bg_item, image=self.bg_image_tk)
        self.coords(self.bg_item, 350 + dx, 350 + dy)

    def demo(self):
        def animate_pitch_and_roll(pitch_sequence, roll_sequence, next_animation=None):
            pitches = iter(pitch_sequence)
            rolls = iter(roll_sequence)
            def animate():
                try:
                    pitch = next(pitches)
                    roll = next(rolls)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(25, animate)  # Much faster frame rate for smoothness
                except StopIteration:
                    if next_animation:
                        next_animation()
            animate()

        # Create sequences with very small increments for ultra-smooth motion
        
        # Phase 1: Normal flight maneuvers (very smooth curves)
        normal_pitch = (
            list(range(0, 450, 5)) +     # Climb (0° to 45° in 0.5° steps)
            list(range(450, -450, -5)) + # Dive through level (45° to -45° in 0.5° steps)
            list(range(-450, 0, 5))      # Return to level (-45° to 0° in 0.5° steps)
        )
        normal_pitch = [p/10 for p in normal_pitch]  # Convert back to actual degrees
        
        normal_roll = (
            list(range(0, 600, 5)) +     # Roll right (0° to 60° in 0.5° steps)
            list(range(600, -600, -5)) + # Roll left through level (60° to -60° in 0.5° steps)
            list(range(-600, 0, 5))      # Return to level (-60° to 0° in 0.5° steps)
        )
        normal_roll = [r/10 for r in normal_roll]  # Convert back to actual degrees
        
        # Phase 2: Edge case demonstration (crossing 90° pitch) - very smooth
        edge_pitch = (
            list(range(0, 950, 8)) +     # Approach and cross 90° (0° to 95° in 0.8° steps)
            list(range(950, 1300, 5)) +  # Continue in inverted territory (95° to 130° in 0.5° steps)
            list(range(1300, 1800, 8)) + # Full inverted (130° to 180° in 0.8° steps)
            list(range(1800, 1300, -8)) +# Return from full inverted (180° to 130° in 0.8° steps)
            list(range(1300, 950, -5)) + # Back towards edge (130° to 95° in 0.5° steps)
            list(range(950, 0, -8))      # Cross back to normal (95° to 0° in 0.8° steps)
        )
        edge_pitch = [p/10 for p in edge_pitch]  # Convert back to actual degrees
        
        edge_roll = (
            [30] * 120 +                 # Constant roll while crossing edge
            list(range(300, -300, -3)) + # Roll motion in inverted flight (30° to -30° in 0.3° steps)
            [0] * 63 +                   # Level roll at full inverted
            list(range(0, 300, 3)) +     # Roll back (0° to 30° in 0.3° steps)
            [30] * 120 +                 # Constant roll while crossing back
            list(range(300, 0, -8))      # Return to level (30° to 0° in 0.8° steps)
        )
        edge_roll = [r/10 for r in edge_roll]  # Convert back to actual degrees
        
        # Phase 3: Complex aerobatic maneuver - ultra smooth
        aerobatic_pitch = (
            list(range(0, 1200, 8)) +    # Aggressive climb to inverted (0° to 120° in 0.8° steps)
            [120] * 25 +                 # Hold inverted
            list(range(1200, 2400, 8)) + # Continue past inverted (120° to 240° in 0.8° steps)
            list(range(2400, 3600, 8)) + # Complete loop (240° to 360° in 0.8° steps)
            list(range(3600, 0, -12))    # Return to level (360° to 0° in 1.2° steps)
        )
        aerobatic_pitch = [p/10 for p in aerobatic_pitch]  # Convert back to actual degrees
        
        aerobatic_roll = (
            list(range(0, 450, 3)) +     # Roll during climb (0° to 45° in 0.3° steps)
            list(range(450, -450, -6)) + # Roll variation in inverted (45° to -45° in 0.6° steps)
            list(range(-450, 0, 3)) +    # Level out (-45° to 0° in 0.3° steps)
            [0] * 150 +                  # Hold level during descent
            [0] * 100                    # Final level
        )
        aerobatic_roll = [r/10 for r in aerobatic_roll]  # Convert back to actual degrees

        # Start the demo sequence
        animate_pitch_and_roll(
            normal_pitch, normal_roll,
            next_animation=lambda: animate_pitch_and_roll(
                edge_pitch, edge_roll,
                next_animation=lambda: animate_pitch_and_roll(
                    aerobatic_pitch, aerobatic_roll,
                    next_animation=lambda: self.demo()  # Loop the demo
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
