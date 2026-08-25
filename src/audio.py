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


def _generate_sound(sound_type: str, sample_rate: int = 22050) -> bytes:
    """Procedurally synthesizes 8-bit retro sound waveforms."""
    samples = []

    if sound_type == "meow_cute":
        # Classic 8-bit Game Boy / NES kitten meow (pitch sweep with gentle vibrato)
        dur = 0.28
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            if prog < 0.4:
                freq = 650.0 + (1150.0 - 650.0) * (prog / 0.4)
            else:
                freq = 1150.0 - (1150.0 - 750.0) * ((prog - 0.4) / 0.6)
            freq += 35.0 * math.sin(2 * math.pi * 18.0 * t)
            vol = (prog / 0.15) if prog < 0.15 else ((1.0 - prog) / 0.3 if prog > 0.7 else 1.0)
            phase = (t * freq) % 1.0
            val = 0.75 if phase < 0.25 else -0.75  # 25% duty cycle pulse wave
            samples.append(val * vol * 0.55 * 32767)

    elif sound_type == "meow_happy":
        # Cheerful 3-note ascending arpeggio chirp (B5 -> E6 -> A6)
        notes = [(987.77, 0.075), (1318.51, 0.085), (1760.00, 0.14)]
        for freq, dur in notes:
            n_samples = int(sample_rate * dur)
            for i in range(n_samples):
                t = i / sample_rate
                prog = i / n_samples
                vol = (1.0 - prog * 0.7) * min(1.0, prog * 8.0)
                phase = (t * freq) % 1.0
                val = 0.8 if phase < 0.5 else -0.8
                samples.append(val * vol * 0.5 * 32767)

    elif sound_type == "meow_boss":
        # Deep, cool 8-bit chirp tailored for Boss Oyen (triangle/square blend)
        dur = 0.26
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            freq = 430.0 + 310.0 * math.sin(math.pi * prog)
            vol = 1.0 - prog * 0.75
            phase = (t * freq) % 1.0
            val = (2.0 * phase - 1.0) if phase < 0.5 else (1.0 - 2.0 * (phase - 0.5))
            samples.append(val * vol * 0.6 * 32767)

    elif sound_type == "meow_chibi":
        # High squeaky tiny kitten chirp for Mochi / Snowball
        dur = 0.18
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            freq = 1350.0 + 900.0 * prog - 400.0 * (prog ** 2)
            vol = (1.0 - prog) * min(1.0, prog * 10.0)
            phase = (t * freq) % 1.0
            val = 0.7 if phase < 0.3 else -0.7
            samples.append(val * vol * 0.5 * 32767)

    elif sound_type == "purr":
        # Soothing low-frequency purr rumble for petting
        dur = 0.42
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            base = math.sin(2 * math.pi * 92.0 * t)
            mod = 0.5 + 0.5 * math.sin(2 * math.pi * 22.0 * t)
            samples.append(base * mod * 0.45 * 32767)

    elif sound_type == "celebrate":
        # Ascending 4-note victory sparkle chime (C6, E6, G6, C7)
        chime_notes = [(1046.50, 0.07), (1318.51, 0.07), (1567.98, 0.08), (2093.00, 0.24)]
        for freq, dur in chime_notes:
            n_samples = int(sample_rate * dur)
            for i in range(n_samples):
                t = i / sample_rate
                prog = i / n_samples
                vol = (1.0 - prog * 0.6) * min(1.0, prog * 12.0)
                phase = (t * freq) % 1.0
                val = 0.75 if phase < 0.5 else -0.75
                val += 0.35 * math.sin(2 * math.pi * (freq * 2.0) * t)
                samples.append(val * vol * 0.45 * 32767)

    elif sound_type == "pop":
        # Short bubbly pop for bubble dialogues & peek mode
        dur = 0.06
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            freq = 400.0 + 1600.0 * (1.0 - prog)
            vol = (1.0 - prog) ** 2
            val = math.sin(2 * math.pi * freq * t)
            samples.append(val * vol * 0.65 * 32767)

    elif sound_type == "water":
        # Upward bubbly splash for hydration reminder
        dur = 0.32
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            freq = 500.0 + 900.0 * prog + 80.0 * math.sin(2 * math.pi * 30.0 * t)
            vol = math.sin(math.pi * prog)
            val = math.sin(2 * math.pi * freq * t)
            samples.append(val * vol * 0.5 * 32767)

    elif sound_type == "stretch":
        # Cute sleepy stretch yawn sweep (descending then rising)
        dur = 0.38
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            prog = i / total
            if prog < 0.5:
                freq = 780.0 - 280.0 * (prog / 0.5)
            else:
                freq = 500.0 + 450.0 * ((prog - 0.5) / 0.5)
            vol = math.sin(math.pi * prog)
            phase = (t * freq) % 1.0
            val = (2.0 * phase - 1.0) if phase < 0.5 else (1.0 - 2.0 * (phase - 0.5))
            samples.append(val * vol * 0.5 * 32767)

    else:
        # Default simple blip
        dur = 0.05
        total = int(sample_rate * dur)
        for i in range(total):
            t = i / sample_rate
            samples.append(math.sin(2 * math.pi * 1200.0 * t) * 0.4 * 32767)

    return _synthesize_wav(samples, sample_rate)


def init_audio():
    """Pre-caches all standard sound effects in memory for zero-latency playback."""
    global _INITIALIZED
    if _INITIALIZED:
        return
    presets = [
        "meow_cute", "meow_happy", "meow_boss", "meow_chibi",
        "purr", "celebrate", "pop", "water", "stretch", "blip"
    ]
    for p in presets:
        _AUDIO_CACHE[p] = _generate_sound(p)
    _INITIALIZED = True


def play_sound(sound_type: str, settings: Optional[dict] = None):
    """
    Plays an 8-bit sound effect asynchronously without blocking the UI thread.
    Respects user's 'sound_enabled' preference.
    """
    if settings is not None and not settings.get("sound_enabled", True):
        return

    if not _INITIALIZED:
        init_audio()

    wav_data = _AUDIO_CACHE.get(sound_type)
    if not wav_data:
        wav_data = _generate_sound(sound_type)
        _AUDIO_CACHE[sound_type] = wav_data

    if sys.platform == "win32":
        try:
            import winsound
            winsound.PlaySound(wav_data, winsound.SND_MEMORY | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception:
            pass


def play_meow_for_skin(skin_name: str, settings: Optional[dict] = None):
    """Selects and plays the distinct 8-bit meow personality matching the active skin."""
    if skin_name == "boss_oyen":
        play_sound("meow_boss", settings)
    elif skin_name in ("mochi", "snowball"):
        play_sound("meow_chibi", settings)
    elif skin_name in ("tuxedo", "calico"):
        play_sound("meow_happy", settings)
    else:
        play_sound("meow_cute", settings)


def play_purr(settings: Optional[dict] = None):
    play_sound("purr", settings)


def play_celebrate(settings: Optional[dict] = None):
    play_sound("celebrate", settings)


def play_pop(settings: Optional[dict] = None):
    play_sound("pop", settings)


def play_water(settings: Optional[dict] = None):
    play_sound("water", settings)


def play_stretch(settings: Optional[dict] = None):
    play_sound("stretch", settings)


init_audio()
