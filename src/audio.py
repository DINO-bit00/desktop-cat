"""
8-Bit Chiptune Procedural Audio Synthesizer & Sound FX Engine
Zero external binary dependencies — generates pure mathematical retro WAV audio in memory.
Non-blocking asynchronous playback on Windows via winsound.
"""

import math
import struct
import io
import wave
import sys
from typing import Dict, Optional

# Pre-cached in-memory WAV byte buffers for instant 0ms latency playback
_AUDIO_CACHE: Dict[str, bytes] = {}
_INITIALIZED = False


def _synthesize_wav(samples: list, sample_rate: int = 22050) -> bytes:
    """Encodes 16-bit Mono PCM audio samples into in-memory WAV byte buffer."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        clamped = [max(-32767, min(32767, int(s))) for s in samples]
        raw = struct.pack(f"<{len(clamped)}h", *clamped)
        wf.writeframes(raw)
    return buf.getvalue()


def _generate_sound(sound_type: str, sample_rate: int = 44100) -> bytes:
    """Procedurally synthesizes soft, sweet, kawaii feline vocalizations and pleasant UI chimes."""
    samples = []

    if sound_type == "meow_cute":
        # Sweet, high-pitch tiny kitten "Mew~!" (0.35s)
        dur = 0.35
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            if prog < 0.35:
                f0 = 680.0 + (890.0 - 680.0) * math.sin((prog / 0.35) * (math.pi / 2.0))
            else:
                f0 = 890.0 - (890.0 - 720.0) * ((prog - 0.35) / 0.65) ** 1.3
            f0 += 12.0 * math.sin(2.0 * math.pi * 7.5 * t)
            vol = (prog / 0.12) ** 2.0 if prog < 0.12 else (((1.0 - prog) / 0.35) ** 1.8 if prog > 0.65 else 1.0)
            
            s = 0.65 * math.sin(2.0 * math.pi * f0 * t)
            s += 0.28 * math.sin(2.0 * math.pi * (f0 * 2.0) * t + 0.3)
            s += 0.12 * math.sin(2.0 * math.pi * (f0 * 3.0) * t + 0.6)
            s += 0.05 * math.sin(2.0 * math.pi * (f0 * 4.0) * t + 0.9)
            s *= (1.0 + 0.08 * math.sin(2.0 * math.pi * 32.0 * t))
            samples.append(s * vol * 0.42 * 32767)

    elif sound_type == "meow_happy":
        # Cheerful, melodic "Nyaa~!" (0.42s)
        dur = 0.42
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            if prog < 0.25:
                f0 = 560.0 + 260.0 * (prog / 0.25)
            elif prog < 0.6:
                f0 = 820.0 - 60.0 * ((prog - 0.25) / 0.35)
            else:
                f0 = 760.0 - 120.0 * ((prog - 0.6) / 0.4) ** 1.2
            f0 += 15.0 * math.sin(2.0 * math.pi * 6.8 * t)
            vol = (prog / 0.08) if prog < 0.08 else (((1.0 - prog) / 0.3) ** 1.5 if prog > 0.7 else 1.0)
            
            s = 0.60 * math.sin(2.0 * math.pi * f0 * t)
            s += 0.25 * math.sin(2.0 * math.pi * (f0 * 2.0) * t)
            s += 0.14 * math.sin(2.0 * math.pi * (f0 * 3.0) * t)
            s += 0.06 * math.sin(2.0 * math.pi * (f0 * 4.0) * t)
            samples.append(s * vol * 0.40 * 32767)

    elif sound_type == "meow_boss":
        # Cool, mellow, low gentle purr-meow for Boss Oyen (0.32s)
        dur = 0.32
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            f0 = 360.0 + 140.0 * math.sin(math.pi * prog)
            f0 += 8.0 * math.sin(2.0 * math.pi * 5.0 * t)
            vol = math.sin(math.pi * prog) ** 1.2
            
            s = 0.70 * math.sin(2.0 * math.pi * f0 * t)
            s += 0.22 * math.sin(2.0 * math.pi * (f0 * 2.0) * t)
            s += 0.08 * math.sin(2.0 * math.pi * (f0 * 3.0) * t)
            samples.append(s * vol * 0.45 * 32767)

    elif sound_type == "meow_chibi":
        # Ultra tiny soft high squeak kitten mew for Mochi / Snowball (0.22s)
        dur = 0.22
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            f0 = 850.0 + 350.0 * math.sin(math.pi * prog) - 50.0 * prog
            vol = math.sin(math.pi * prog) ** 1.4
            
            s = 0.75 * math.sin(2.0 * math.pi * f0 * t)
            s += 0.20 * math.sin(2.0 * math.pi * (f0 * 2.0) * t)
            s += 0.05 * math.sin(2.0 * math.pi * (f0 * 3.0) * t)
            samples.append(s * vol * 0.38 * 32767)

    elif sound_type == "purr":
        # Real soothing low-frequency purr vibration (0.55s)
        dur = 0.55
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            f0 = 75.0 + 10.0 * math.sin(2.0 * math.pi * 3.0 * t)
            vol = math.sin(math.pi * (i / total)) ** 0.8
            flutter = 0.5 + 0.5 * math.sin(2.0 * math.pi * 25.0 * t)
            s = math.sin(2.0 * math.pi * f0 * t) * flutter + 0.3 * math.sin(2.0 * math.pi * (f0 * 2.0) * t) * flutter
            samples.append(s * vol * 0.35 * 32767)

    elif sound_type == "celebrate":
        # Gentle celesta chime arpeggio for victory/celebration
        notes = [(1046.50, 0.08), (1318.51, 0.08), (1567.98, 0.09), (2093.00, 0.28)]
        for freq, d in notes:
            n_samples = int(sample_rate * d)
            for j in range(n_samples):
                t = j / sample_rate
                prog = j / n_samples
                vol = math.exp(-4.5 * prog)
                s = math.sin(2.0 * math.pi * freq * t) + 0.25 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                samples.append(s * vol * 0.35 * 32767)

    elif sound_type == "pop":
        # Ultra soft wooden drop / bubble pop
        dur = 0.05
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            f0 = 800.0 * (1.0 - 0.6 * prog)
            vol = math.exp(-12.0 * prog)
            s = math.sin(2.0 * math.pi * f0 * t)
            samples.append(s * vol * 0.38 * 32767)

    elif sound_type == "water":
        # Gentle bubbling splash for hydration reminder
        dur = 0.32
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            f0 = 450.0 + 350.0 * prog + 40.0 * math.sin(2.0 * math.pi * 18.0 * t)
            vol = math.sin(math.pi * prog)
            s = math.sin(2.0 * math.pi * f0 * t)
            samples.append(s * vol * 0.35 * 32767)

    elif sound_type == "stretch":
        # Cute sleepy stretch yawn vocalization
        dur = 0.38
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            if prog < 0.5:
                f0 = 620.0 - 180.0 * (prog / 0.5)
            else:
                f0 = 440.0 + 260.0 * ((prog - 0.5) / 0.5)
            vol = math.sin(math.pi * prog) ** 1.2
            s = 0.70 * math.sin(2.0 * math.pi * f0 * t) + 0.25 * math.sin(2.0 * math.pi * (f0 * 2.0) * t)
            samples.append(s * vol * 0.38 * 32767)

    else:
        # Default simple soft blip
        dur = 0.04
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            vol = math.exp(-15.0 * prog)
            samples.append(math.sin(2.0 * math.pi * 950.0 * t) * vol * 0.35 * 32767)

    return _synthesize_wav(samples, sample_rate)


import os
import threading

_SOUND_FILES: Dict[str, str] = {}


def init_audio():
    """Pre-caches all standard sound effects in memory and generates local WAV files for instant async playback."""
    global _INITIALIZED
    if _INITIALIZED:
        return
    
    sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")
    try:
        os.makedirs(sound_dir, exist_ok=True)
    except Exception:
        pass

    presets = [
        "meow_cute", "meow_happy", "meow_boss", "meow_chibi",
        "purr", "celebrate", "pop", "water", "stretch", "blip"
    ]
    for p in presets:
        wav_data = _generate_sound(p)
        _AUDIO_CACHE[p] = wav_data
        
        file_path = os.path.join(sound_dir, f"{p}.wav")
        try:
            with open(file_path, "wb") as f:
                f.write(wav_data)
            _SOUND_FILES[p] = file_path
        except Exception:
            pass

    _INITIALIZED = True


def play_sound(sound_type: str, settings: Optional[dict] = None, force: bool = False):
    """
    Plays an 8-bit sound effect asynchronously without blocking the UI thread.
    Respects user's 'sound_enabled' preference unless force=True (e.g. previewing).
    """
    if not force and settings is not None and not settings.get("sound_enabled", True):
        return

    if not _INITIALIZED:
        init_audio()

    file_path = _SOUND_FILES.get(sound_type)
    if file_path and os.path.exists(file_path) and sys.platform == "win32":
        try:
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass

    wav_data = _AUDIO_CACHE.get(sound_type)
    if not wav_data:
        wav_data = _generate_sound(sound_type)
        _AUDIO_CACHE[sound_type] = wav_data

    if sys.platform == "win32":
        try:
            import winsound
            threading.Thread(
                target=lambda: winsound.PlaySound(wav_data, winsound.SND_MEMORY),
                daemon=True
            ).start()
        except Exception:
            pass


def play_meow_for_skin(skin_name: str, settings: Optional[dict] = None, force: bool = False):
    """Selects and plays the distinct 8-bit meow personality matching the active skin."""
    if skin_name == "boss_oyen":
        play_sound("meow_boss", settings, force=force)
    elif skin_name in ("mochi", "snowball"):
        play_sound("meow_chibi", settings, force=force)
    elif skin_name in ("tuxedo", "calico"):
        play_sound("meow_happy", settings, force=force)
    else:
        play_sound("meow_cute", settings, force=force)


def play_purr(settings: Optional[dict] = None, force: bool = False):
    play_sound("purr", settings, force=force)


def play_celebrate(settings: Optional[dict] = None, force: bool = False):
    play_sound("celebrate", settings, force=force)


def play_pop(settings: Optional[dict] = None, force: bool = False):
    play_sound("pop", settings, force=force)


def play_water(settings: Optional[dict] = None, force: bool = False):
    play_sound("water", settings, force=force)


def play_stretch(settings: Optional[dict] = None, force: bool = False):
    play_sound("stretch", settings, force=force)


init_audio()
