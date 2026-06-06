"""AUDIO -- tiny built-in beeps, no sound files needed."""

import math
import array

import pygame


def make_tone(freq, ms, volume=0.35, fade=True):
    """Build a short beep from scratch so we need no external files."""
    sample_rate = 44100
    n = int(sample_rate * ms / 1000)
    buf = array.array("h")  # signed 16-bit samples
    for i in range(n):
        t = i / sample_rate
        env = (1.0 - i / n) if fade else 1.0          # fade out
        # square-ish wave sounds nice and retro
        wave = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        buf.append(int(32767 * volume * env * wave))
    return pygame.mixer.Sound(buffer=buf.tobytes())


def play(sound):
    """Play a sound, or do nothing if audio failed to initialize."""
    if sound is not None:
        sound.play()


class SoundBank:
    """The three game sounds. Stays silent if the mixer is unavailable."""

    def __init__(self):
        self.jump = self.death = self.win = None
        try:
            self.jump = make_tone(660, 70, 0.30)
            self.death = make_tone(150, 320, 0.40)
            self.win = make_tone(880, 400, 0.35, fade=False)
        except Exception:
            pass  # game runs fine without sound
