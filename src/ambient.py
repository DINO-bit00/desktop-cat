import sys
import os
import math
import struct
import io
import wave
import random
import threading
from typing import Optional

AMBIENT_TRACKS = {
    "rain": {"name": "🌧️ Suara Hujan Lembut (Gentle Rain)", "file": "ambient_rain.wav"},
    "fire": {"name": "🪵 Gemeretak Api Unggun (Cozy Fire)", "file": "ambient_fire.wav"},
    "waves": {"name": "🌊 Deburan Ombak Santai (Ocean Waves)", "file": "ambient_waves.wav"},
}


def _ensure_ambient_file(ambient_type: str, file_path: str, duration_sec: float = 6.0, sample_rate: int = 22050):
    """Generates procedural ambient audio file if not present on disk."""
    if os.path.exists(file_path):
        return

    total_samples = int(sample_rate * duration_sec)
    samples = [0.0] * total_samples

    if ambient_type == "rain":
        b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
        for i in range(total_samples):
            white = random.uniform(-1.0, 1.0)
            b0 = 0.99886 * b0 + white * 0.0555179
            b1 = 0.99332 * b1 + white * 0.0750759
            b2 = 0.96900 * b2 + white * 0.1538520
            b3 = 0.86650 * b3 + white * 0.3104856
            b4 = 0.55000 * b4 + white * 0.5329522
            b5 = -0.7616 * b5 - white * 0.0168980
            pink = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362
            b6 = white * 0.115926
            samples[i] = pink * 0.18

        drop_count = int(duration_sec * 8)
        for _ in range(drop_count):
            drop_idx = random.randint(0, total_samples - 600)
            f_drop = random.uniform(800.0, 1800.0)
            for j in range(400):
                t = j / sample_rate
                vol = math.exp(-25.0 * (j / 400.0))
                samples[drop_idx + j] += math.sin(2.0 * math.pi * f_drop * t) * vol * 0.12

    elif ambient_type == "fire":
        b0 = 0.0
        for i in range(total_samples):
            white = random.uniform(-1.0, 1.0)
            b0 = 0.99 * b0 + white * 0.06
            samples[i] = b0 * 0.22

        pop_count = int(duration_sec * 12)
        for _ in range(pop_count):
            idx = random.randint(0, total_samples - 300)
            f_pop = random.uniform(350.0, 950.0)
            for j in range(200):
                vol = math.exp(-35.0 * (j / 200.0))
                samples[idx + j] += (random.uniform(-1.0, 1.0) * 0.5 + math.sin(2.0 * math.pi * f_pop * (j / sample_rate)) * 0.5) * vol * 0.35

    else:  # waves
        b0 = 0.0
        for i in range(total_samples):
            t = i / sample_rate
            white = random.uniform(-1.0, 1.0)
            b0 = 0.992 * b0 + white * 0.08
            swell = (math.sin(2.0 * math.pi * (t / 3.8)) + 1.0) * 0.5
            samples[i] = b0 * swell * 0.30

    # Crossfade loop edges
    fade_len = int(sample_rate * 0.3)
    for i in range(fade_len):
        fade_in = i / fade_len
        fade_out = 1.0 - fade_in
        samples[i] = samples[i] * fade_in + samples[total_samples - fade_len + i] * fade_out

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            clamped = [max(-32767, min(32767, int(s * 32767))) for s in samples]
            raw = struct.pack(f"<{len(clamped)}h", *clamped)
            wf.writeframes(raw)
    except Exception:
        pass


class AmbientPlayer:
    """
    Background Ambient Lo-fi Sound Player:
    Plays calming environmental loops asynchronously for focused coding and work sessions.
    """
    def __init__(self):
        self.active_track: Optional[str] = None
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._sound_dir = os.path.join(base_dir, "assets", "sounds")
        # Pre-ensure files exist
        for key, info in AMBIENT_TRACKS.items():
            p = os.path.join(self._sound_dir, info["file"])
            _ensure_ambient_file(key, p)

    def is_playing(self) -> bool:
        return self.active_track is not None

    def play(self, track_name: str):
        """Starts looping the chosen ambient sound."""
        if track_name not in AMBIENT_TRACKS:
            return

        file_name = AMBIENT_TRACKS[track_name]["file"]
        file_path = os.path.join(self._sound_dir, file_name)
        _ensure_ambient_file(track_name, file_path)

        self.active_track = track_name
        if sys.platform == "win32" and os.path.exists(file_path):
            try:
                import winsound
                winsound.PlaySound(
                    file_path,
                    winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC
                )
            except Exception:
                pass

    def stop(self):
        """Stops ambient sound playback."""
        self.active_track = None
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
