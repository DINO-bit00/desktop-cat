"""
Ultra-lightweight Silent Sound Module for NyangBuddy.
Zero external files, zero disk writes, instant execution.
Supports 100% Silent Mode (Mode Senyap) by default.
"""

import sys
from typing import Optional


def play_sound(sound_type: str = "blip", settings: Optional[dict] = None, force: bool = False):
    """
    Plays an optional lightweight retro Windows system beep if sound is explicitly enabled.
    In Silent Mode (default), does absolutely nothing (0 CPU, 0 RAM, 0 disk write).
    """
    if settings is not None:
        if not settings.get("sound_enabled", False) and not force:
            return

    # Lightweight non-blocking system beep only if sound_enabled is True
    if sys.platform == "win32":
        try:
            import winsound
            if sound_type in ("meow", "meow_cute", "meow_happy", "meow_boss", "meow_chibi"):
                winsound.Beep(1450, 40)
            elif sound_type in ("pop", "water"):
                winsound.Beep(1800, 25)
            elif sound_type in ("celebrate", "done"):
                winsound.Beep(1650, 50)
            elif sound_type in ("stretch", "yawn"):
                winsound.Beep(980, 40)
            elif sound_type in ("munch", "feed"):
                winsound.Beep(1200, 30)
            else:
                winsound.Beep(1350, 25)
        except Exception:
            pass


def play_meow(skin_name: str = "boss_oyen", settings: Optional[dict] = None, force: bool = False):
    play_sound("meow", settings, force=force)


def play_meow_for_skin(skin_name: str, settings: Optional[dict] = None, force: bool = False):
    """Selects and plays the distinct 8-bit meow personality matching the active skin."""
    play_sound("meow", settings, force=force)


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


def play_munch(settings: Optional[dict] = None, force: bool = False):
    play_sound("munch", settings, force=force)


def init_audio():
    """No-op init for compatibility."""
    pass
