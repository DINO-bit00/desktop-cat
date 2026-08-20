"""
Settings Manager for Desktop Cat
Saves and loads user preferences locally in JSON format with zero telemetry.
"""

import json
import os

DEFAULT_SETTINGS = {
    "skin": "oyen",                 # oyen, calico, tuxedo, grey, shiro
    "wander_mode": True,            # Auto-wander or stay still
    "stay_on_top": True,            # Always on top
    "pomodoro_work_min": 25,        # Focus duration
    "pomodoro_break_min": 5,        # Break duration
    "hydration_reminder_min": 45,   # Drink water reminder every 45 min
    "stretch_reminder_min": 60,     # Posture & stretch reminder every 60 min
    "stretch_reminder_enabled": True, # Posture reminder toggle
    "sound_enabled": True,          # Cute synthesized retro blip
    "sticky_note": "",              # Pinned focus goal / note
    "scale": 1.0,                   # Size scale
    "run_on_startup": False         # Windows Registry Run on startup
}

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")


def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings = DEFAULT_SETTINGS.copy()
                settings.update(data)
                return settings
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Settings] Error saving settings: {e}")
