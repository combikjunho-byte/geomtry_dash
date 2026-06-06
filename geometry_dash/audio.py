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


def _square(freq, t):
    """One sample of a square wave (retro chiptune timbre)."""
    if freq <= 0:
        return 0.0
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0


def make_music(volume=0.16):
    """Build a short, upbeat chiptune loop from scratch (no sound files).

    A square-wave melody rides over a steady bass line; the result is one
    bar that we loop forever underneath the whole game.
    """
    sample_rate = 44100
    bpm = 132
    beat = 60.0 / bpm

    # One note per beat. 0 = a rest. Melody on top, bass an octave+ below.
    melody = [523, 659, 784, 659, 587, 698, 880, 698,
              523, 659, 784, 1047, 988, 784, 659, 587]
    bass = [131, 131, 165, 165, 147, 147, 196, 196,
            131, 131, 165, 165, 196, 196, 147, 147]

    total_beats = len(melody)
    total_samples = int(sample_rate * total_beats * beat)
    buf = array.array("h")  # signed 16-bit samples
    for i in range(total_samples):
        t = i / sample_rate
        beat_pos = t / beat
        idx = int(beat_pos) % total_beats
        frac = beat_pos - int(beat_pos)
        env = 0.35 + 0.65 * max(0.0, 1.0 - frac)        # soft pluck per beat
        sample = 0.6 * _square(melody[idx], t) + 0.4 * _square(bass[idx], t)
        buf.append(int(32767 * volume * env * sample * 0.5))
    return pygame.mixer.Sound(buffer=buf.tobytes())


def play(sound):
    """Play a sound, or do nothing if audio failed to initialize."""
    if sound is not None:
        sound.play()


# A channel reserved for the looping background track, so sound effects
# (jump / death / win) never interrupt the music.
MUSIC_CHANNEL = 7


class SoundBank:
    """The game sounds plus looping music. Stays silent if the mixer fails."""

    def __init__(self):
        self.jump = self.death = self.win = self.music = None
        try:
            self.jump = make_tone(660, 70, 0.30)
            self.death = make_tone(150, 320, 0.40)
            self.win = make_tone(880, 400, 0.35, fade=False)
            self.music = make_music()
        except Exception:
            pass  # game runs fine without sound

    def start_music(self):
        """Loop the background track forever (called once, from the menu)."""
        if self.music is None:
            return
        try:
            pygame.mixer.Channel(MUSIC_CHANNEL).play(self.music, loops=-1)
        except Exception:
            pass  # never let an audio hiccup crash the game
