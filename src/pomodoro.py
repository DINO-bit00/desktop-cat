"""
Pomodoro & Health Reminders System
Manages focus timers, short breaks, and ergonomic/hydration reminders.
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class PomodoroManager(QObject):
    # Signals
    tick = pyqtSignal(int, str)             # remaining_seconds, mode ("work" / "break")
    session_started = pyqtSignal(str)       # mode ("work" / "break")
    session_finished = pyqtSignal(str)      # mode ("work" / "break")
    reminder_triggered = pyqtSignal(str)    # reminder text

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_active = False
        self.mode = "idle"  # "work", "break", "idle"
        self.remaining_seconds = 0

        # Main 1-second interval timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        # Hydration / Stretch reminder timer
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self._on_hydration_check)
        self._start_reminder_timer()

    def _start_reminder_timer(self):
        interval_min = self.settings.get("hydration_reminder_min", 45)
        if interval_min > 0:
            self.reminder_timer.start(interval_min * 60 * 1000)
        else:
            self.reminder_timer.stop()

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
            "Jangan lupa regangkan leher dan punggungmu nya~ 🧘",
            "Kedipkan mata dan istirahatkan pandangan sejenak nya! 👀",
            "Postur tubuh tegak ya! Semangat terus kerjanya~ ✨"
        ]
        import random
        self.reminder_triggered.emit(random.choice(messages))

    def format_time(self):
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        return f"{mins:02d}:{secs:02d}"
