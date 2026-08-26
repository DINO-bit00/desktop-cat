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
    "pomodoro_cycles": 4,           # Number of auto focus-break cycles
    "hydration_reminder_min": 45,   # Drink water reminder every 45 min
    "hydration_reminder_enabled": True, # Hydration reminder toggle
    "stretch_reminder_min": 60,     # Posture & stretch reminder every 60 min
    "stretch_reminder_enabled": True, # Posture reminder toggle
    "sound_enabled": True,          # Cute synthesized retro blip
    "sticky_note": "",              # Pinned focus goal / note
    "user_name": "",                # Panggilan nama user
    "scale": 1.0,                   # Size scale
    "run_on_startup": False,        # Windows Registry Run on startup
    "ai_watcher_enabled": True,     # Auto-detect AI Agent thinking & celebration
    "auto_peek_fullscreen": True    # Auto-peek at screen edge during fullscreen/gaming
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
