"""
Pomodoro & Health Reminders System
Manages focus timers, short breaks, posture stretches, and hydration reminders.
"""

import random
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class PomodoroManager(QObject):
    # Signals
    tick = pyqtSignal(int, str)                 # remaining_seconds, mode ("work" / "break")
    session_started = pyqtSignal(str)           # mode ("work" / "break")
    session_finished = pyqtSignal(str)          # mode ("work" / "break")
    reminder_triggered = pyqtSignal(str)        # general reminder text
    posture_reminder_triggered = pyqtSignal()   # stretch/posture trigger

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_active = False
        self.mode = "idle"  # "work", "break", "idle"
        self.remaining_seconds = 0

        # Main 1-second interval timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        # Hydration reminder timer
        self.hydration_timer = QTimer(self)
        self.hydration_timer.timeout.connect(self._on_hydration_check)

        # Posture & Stretch reminder timer (every 60 min)
        self.posture_timer = QTimer(self)
        self.posture_timer.timeout.connect(self._on_posture_check)

        self.start_health_timers()

    def start_health_timers(self):
        """Starts/restarts hydration and posture timers based on current settings."""
        # Hydration
        hyd_min = self.settings.get("hydration_reminder_min", 45)
        if hyd_min > 0:
            self.hydration_timer.start(hyd_min * 60 * 1000)
        else:
            self.hydration_timer.stop()

        # Posture / Stretch
        stretch_enabled = self.settings.get("stretch_reminder_enabled", True)
        stretch_min = self.settings.get("stretch_reminder_min", 60)
        if stretch_enabled and stretch_min > 0:
            self.posture_timer.start(stretch_min * 60 * 1000)
        else:
            self.posture_timer.stop()

    def start_focus(self, minutes=None):
        if minutes is None:
            minutes = self.settings.get("pomodoro_work_min", 25)
        self.mode = "work"
        self.remaining_seconds = minutes * 60
        self.is_active = True
        self.timer.start(1000)
        self.session_started.emit("work")

    def start_break(self, minutes=None):
        if minutes is None:
            minutes = self.settings.get("pomodoro_break_min", 5)
        self.mode = "break"
        self.remaining_seconds = minutes * 60
        self.is_active = True
        self.timer.start(1000)
        self.session_started.emit("break")

    def stop(self):
        self.is_active = False
        self.mode = "idle"
        self.remaining_seconds = 0
        self.timer.stop()

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.tick.emit(self.remaining_seconds, self.mode)
        else:
            finished_mode = self.mode
            self.stop()
            self.session_finished.emit(finished_mode)

    def _on_hydration_check(self):
        messages = [
            "Meow! Waktunya minum air putih dulu biar tetap segar! 💧",
            "Kedipkan mata dan istirahatkan pandangan sejenak nya! 👀",
            "Segelas air putih siap membantumu tetap fokus, yuk minum! 🥛✨"
        ]
        self.reminder_triggered.emit(random.choice(messages))

    def _on_posture_check(self):
        self.posture_reminder_triggered.emit()

    def format_time(self):
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        return f"{mins:02d}:{secs:02d}"
