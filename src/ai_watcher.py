"""
AI Agent Auto-Watcher Module (Deterministic Step-Level State Engine)
Directly parses Antigravity / Gemini Agent transcript steps in real-time
with 0-latency synchronization and zero guesswork.

State Flow:
- User submits prompt (USER_INPUT) -> Thinking state [O O] + [...]
- AI runs tools / bash / search (PLANNER_RESPONSE with tool_calls / GENERIC) -> Stays in Thinking state
- AI finishes final response (PLANNER_RESPONSE with 0 tool_calls) -> Celebrate Jump + Victory Meow!
"""

import os
import sys
import time
import json
import glob
import ctypes
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class AIAgentWatcher(QObject):
    # Signals
    ai_thinking_started = pyqtSignal(str)   # tool_name
    ai_task_completed = pyqtSignal(str)     # tool_name

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self.celebrated_steps = set()
        self.last_seen_step_index = None

        self._init_current_state()

        # High-frequency low-overhead scan timer (200ms interval, <0.01% CPU)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scan_ai_activity)
        if self.is_enabled():
            self.timer.start(200)

    def is_enabled(self) -> bool:
        return self.settings.get("ai_watcher_enabled", True)

    def set_enabled(self, enabled: bool):
        self.settings["ai_watcher_enabled"] = enabled
        if enabled:
            self._init_current_state()
            self.timer.start(200)
        else:
            self.timer.stop()
            self.is_active_ai_session = False

    def _get_latest_antigravity_transcript(self):
        gemini_dir = os.path.expanduser(r"~\.gemini\antigravity\brain")
        if not os.path.exists(gemini_dir):
            return None
        transcripts = glob.glob(os.path.join(gemini_dir, "*", ".system_generated", "logs", "transcript.jsonl"))
        if not transcripts:
            return None
        transcripts.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return transcripts[0]

    def _read_last_step(self, path: str):
        try:
            with open(path, "rb") as f:
                try:
                    f.seek(-8192, os.SEEK_END)
                except OSError:
                    pass
                raw = f.read().decode("utf-8", errors="ignore").strip()
                if not raw:
                    return None
                lines = raw.splitlines()
                if not lines:
                    return None
                return json.loads(lines[-1])
        except Exception:
            return None

    def _init_current_state(self):
        latest = self._get_latest_antigravity_transcript()
        if not latest:
            return
        last_step = self._read_last_step(latest)
        if last_step:
            step_idx = last_step.get("step_index")
            if step_idx is not None:
                self.celebrated_steps.add(step_idx)
                self.last_seen_step_index = step_idx

    def _scan_ai_activity(self):
        if not self.is_enabled():
            return

        latest = self._get_latest_antigravity_transcript()
        if not latest:
            return

        try:
            mtime = os.path.getmtime(latest)
        except Exception:
            return

        now = time.time()
        time_since_mod = now - mtime

        step = self._read_last_step(latest)
        if not step:
            return

        step_idx = step.get("step_index")
        step_type = step.get("type")
        tool_calls = step.get("tool_calls", [])
        tc_count = len(tool_calls) if tool_calls else 0
        source = step.get("source")

        # Active session within recent 30 seconds
        if time_since_mod < 30.0:
            if step_type == "USER_INPUT" or tc_count > 0 or step_type == "GENERIC":
                if not self.is_active_ai_session:
                    self.is_active_ai_session = True
                    self.active_tool_name = "Antigravity"
                    self.ai_thinking_started.emit("Antigravity")
            elif step_type == "PLANNER_RESPONSE" and tc_count == 0 and source == "MODEL":
                if step_idx is not None and step_idx not in self.celebrated_steps:
                    self.celebrated_steps.add(step_idx)
                    self.is_active_ai_session = False
                    self.active_tool_name = ""
                    self.ai_task_completed.emit("Antigravity")
        else:
            # Idle timeout
            if self.is_active_ai_session:
                self.is_active_ai_session = False
                self.active_tool_name = ""

    def trigger_thinking_start(self, tool_name="AI Agent"):
        """Programmatic trigger for starting AI thinking."""
        self.is_active_ai_session = True
        self.active_tool_name = tool_name
        self.ai_thinking_started.emit(tool_name)

    def trigger_task_done(self, tool_name="AI Agent"):
        """Programmatic trigger for completing AI task -> jump celebrate."""
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self.ai_task_completed.emit(tool_name)
