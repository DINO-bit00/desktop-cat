"""
Pomodoro & Health Reminders System
Manages focus timers, short breaks, posture stretches, and hydration reminders.
Supports multi-cycle auto-Pomodoro with configurable focus/break/cycles.
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
    hydration_reminder_triggered = pyqtSignal() # drink water/hydration trigger

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_active = False
        self.mode = "idle"  # "work", "break", "idle"
        self.remaining_seconds = 0

        # Auto-Cycle Pomodoro State
        self.current_cycle = 0       # Current cycle index (1-based when running)
        self.total_cycles = 1        # Total cycles to run
        self.work_minutes = 25       # Focus duration for current auto session
        self.break_minutes = 5       # Break duration for current auto session
        self.is_auto_cycle = False   # True when running multi-cycle auto Pomodoro

        # Main 1-second interval timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        # Hydration reminder timer (every 45 min default)
        self.hydration_timer = QTimer(self)
        self.hydration_timer.timeout.connect(self._on_hydration_check)

        # Posture & Stretch reminder timer (every 60 min default)
        self.posture_timer = QTimer(self)
        self.posture_timer.timeout.connect(self._on_posture_check)

        self.start_health_timers()

    @property
    def state(self) -> str:
        return self.mode

    def start_health_timers(self):
        """Starts/restarts hydration and posture timers based on current settings."""
        # Hydration
        hyd_enabled = self.settings.get("hydration_reminder_enabled", True)
        hyd_min = self.settings.get("hydration_reminder_min", 45)
        if hyd_enabled and hyd_min > 0:
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
        self.work_minutes = minutes
        self.mode = "work"
        self.remaining_seconds = minutes * 60
        self.is_active = True
        self.timer.start(1000)
        self.session_started.emit("work")

    def start_break(self, minutes=None):
        if minutes is None:
            minutes = self.settings.get("pomodoro_break_min", 5)
        self.break_minutes = minutes
        self.mode = "break"
        self.remaining_seconds = minutes * 60
        self.is_active = True
        self.timer.start(1000)
        self.session_started.emit("break")

    def start_auto_cycle(self, work_min: int, break_min: int, cycles: int):
        """Start a multi-cycle auto Pomodoro session (focus → break → focus → ...)."""
        self.work_minutes = work_min
        self.break_minutes = break_min
        self.total_cycles = max(1, cycles)
        self.current_cycle = 1
        self.is_auto_cycle = True
        self.start_focus(work_min)

    def advance_cycle(self):
        """
        Called by pet_window after a center-screen reminder is dismissed.
        Returns the next action: ('work', mins), ('break', mins), or ('done', 0).
        """
        if not self.is_auto_cycle:
            return ("done", 0)

        if self.mode == "idle":
            # After a work reminder was shown → start break
            return ("break", self.break_minutes)

        return ("done", 0)

    def start_next_after_break(self):
        """After break reminder, determine if we start the next cycle or finish."""
        if not self.is_auto_cycle:
            return ("done", 0)

        if self.current_cycle < self.total_cycles:
            self.current_cycle += 1
            return ("work", self.work_minutes)
        else:
            # All cycles complete
            self.is_auto_cycle = False
            return ("done", 0)

    def stop(self):
        self.is_active = False
        self.mode = "idle"
        self.remaining_seconds = 0
        self.is_auto_cycle = False
        self.current_cycle = 0
        self.total_cycles = 1
        self.timer.stop()

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.tick.emit(self.remaining_seconds, self.mode)
        else:
            finished_mode = self.mode
            # Save auto-cycle state before stop() clears it
            was_auto = self.is_auto_cycle
            saved_cycle = self.current_cycle
            saved_total = self.total_cycles
            saved_work = self.work_minutes
            saved_break = self.break_minutes

            self.is_active = False
            self.mode = "idle"
            self.remaining_seconds = 0
            self.timer.stop()

            # Restore auto-cycle state so pet_window can read it
            self.is_auto_cycle = was_auto
            self.current_cycle = saved_cycle
            self.total_cycles = saved_total
            self.work_minutes = saved_work
            self.break_minutes = saved_break

            self.session_finished.emit(finished_mode)

    def _on_hydration_check(self):
        self.hydration_reminder_triggered.emit()

    def _on_posture_check(self):
        self.posture_reminder_triggered.emit()

    def format_time(self):
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def cycle_label(self):
        """Returns cycle info label e.g. '[2/4]' or '' if single cycle."""
        if self.total_cycles > 1:
            return f"[{self.current_cycle}/{self.total_cycles}]"
        return ""
