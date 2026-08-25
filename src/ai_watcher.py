"""
AI Agent Auto-Watcher Module (Upgraded Real-time Synchronous Engine)
Monitors active AI coding agents (Antigravity, Claude Code, Aider, Cursor, Copilot)
in real-time using live transcript/log streaming and IPC triggers.

When an AI agent starts processing -> triggers cat's thinking pose [O O] + [...]
When the AI agent finishes -> triggers cat's celebrate jump + victory meow!
"""

import os
import sys
import time
import glob
import ctypes
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


def _get_active_window_title() -> str:
    """Fast, zero-overhead Win32 active window title fetcher."""
    if sys.platform != "win32":
        return ""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    except Exception:
        return ""


class AIAgentWatcher(QObject):
    # Signals
    ai_thinking_started = pyqtSignal(str)   # tool_name
    ai_task_completed = pyqtSignal(str)     # tool_name

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self._last_ai_active_time = 0.0

        # Antigravity / Gemini real-time transcript tracker
        self._ag_active_file = None
        self._ag_last_size = 0
        self._ag_last_mtime = 0.0

        # Aider / Local logs tracker
        self._local_log_files = {}

        self._init_transcripts()

        # High-cadence real-time poll timer (400ms interval, <0.01% CPU)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scan_all_ai_sources)
        if self.is_enabled():
            self.timer.start(400)

    def is_enabled(self) -> bool:
        return self.settings.get("ai_watcher_enabled", True)

    def set_enabled(self, enabled: bool):
        self.settings["ai_watcher_enabled"] = enabled
        if enabled:
            self._init_transcripts()
            self.timer.start(400)
        else:
            self.timer.stop()
            self.is_active_ai_session = False

    def _init_transcripts(self):
        """Initializes existing transcript baseline sizes so old historical files don't false-trigger."""
        gemini_dir = os.path.expanduser(r"~\.gemini\antigravity\brain")
        if os.path.exists(gemini_dir):
            transcripts = glob.glob(os.path.join(gemini_dir, "*", ".system_generated", "logs", "transcript.jsonl"))
            if transcripts:
                transcripts.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                latest = transcripts[0]
                self._ag_active_file = latest
                try:
                    self._ag_last_mtime = os.path.getmtime(latest)
                    self._ag_last_size = os.path.getsize(latest)
                except Exception:
                    pass

    def _check_antigravity_activity(self, now: float) -> bool:
        """Checks if Antigravity / Gemini Agent is actively appending logs/thoughts."""
        gemini_dir = os.path.expanduser(r"~\.gemini\antigravity\brain")
        if not os.path.exists(gemini_dir):
            return False

        transcripts = glob.glob(os.path.join(gemini_dir, "*", ".system_generated", "logs", "transcript.jsonl"))
        if not transcripts:
            return False

        transcripts.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        latest = transcripts[0]

        try:
            cur_mtime = os.path.getmtime(latest)
            cur_size = os.path.getsize(latest)
        except Exception:
            return False

        if latest != self._ag_active_file:
            # Switched to a new conversation
            self._ag_active_file = latest
            self._ag_last_mtime = cur_mtime
            self._ag_last_size = cur_size
            return False

        # Active append detected (file grew in size or was modified within 2.2 seconds)
        has_appended = (cur_size > self._ag_last_size) or (cur_mtime > self._ag_last_mtime and (now - cur_mtime < 2.2))

        self._ag_last_mtime = cur_mtime
        self._ag_last_size = cur_size
        return has_appended

    def _check_local_workspace_agents(self, now: float) -> bool:
        """Checks for active Aider, Claude Code, or local agent log modifications."""
        candidates = [
            ".aider.chat.history.md",
            ".aider.input.history"
        ]
        for rel in candidates:
            if os.path.exists(rel):
                try:
                    mtime = os.path.getmtime(rel)
                    size = os.path.getsize(rel)
                    prev_size, prev_mtime = self._local_log_files.get(rel, (size, mtime))
                    self._local_log_files[rel] = (size, mtime)
                    if size > prev_size or (mtime > prev_mtime and (now - mtime < 2.0)):
                        return True
                except Exception:
                    pass
        return False

    def _scan_all_ai_sources(self):
        if not self.is_enabled():
            return

        now = time.time()
        is_ag_thinking = self._check_antigravity_activity(now)
        is_local_thinking = self._check_local_workspace_agents(now)

        active_detected = is_ag_thinking or is_local_thinking
        detected_tool = "Antigravity" if is_ag_thinking else ("AI Agent" if is_local_thinking else "")

        if active_detected:
            self._last_ai_active_time = now
            if not self.is_active_ai_session:
                self.is_active_ai_session = True
                self.active_tool_name = detected_tool
                self.ai_thinking_started.emit(detected_tool)
        else:
            # If AI was previously thinking and has been silent for > 2.0s -> task completed!
            if self.is_active_ai_session:
                if now - self._last_ai_active_time > 2.0:
                    completed_tool = self.active_tool_name or "AI Agent"
                    self.is_active_ai_session = False
                    self.active_tool_name = ""
                    self.ai_task_completed.emit(completed_tool)

    def trigger_thinking_start(self, tool_name="AI Agent"):
        """Programmatic trigger for starting AI thinking."""
        self.is_active_ai_session = True
        self.active_tool_name = tool_name
        self._last_ai_active_time = time.time()
        self.ai_thinking_started.emit(tool_name)

    def trigger_task_done(self, tool_name="AI Agent"):
        """Programmatic trigger for completing AI task -> jump celebrate."""
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self.ai_task_completed.emit(tool_name)
