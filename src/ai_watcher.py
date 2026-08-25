"""
AI Agent Auto-Watcher Module
Monitors active AI coding agents (Claude Code, Cursor, Windsurf, Antigravity,
Aider, Copilot, Ollama, etc.) in real-time.

When an AI agent starts processing -> triggers cat's thinking pose [O O] + [...]
When the AI agent finishes -> triggers cat's celebrate jump + meow!
"""

import os
import sys
import time
import ctypes
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# Supported AI tool signatures in window titles / process names
AI_TOOL_KEYWORDS = [
    "claude", "cursor", "windsurf", "antigravity", "aider",
    "copilot", "ollama", "chatgpt", "gemini", "opencode"
]


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
        self._cooldown_time = 0.0

        # Background scan timer (every 800ms, <0.01% CPU)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scan_active_ai_agent)
        if self.is_enabled():
            self.timer.start(800)

    def is_enabled(self) -> bool:
        return self.settings.get("ai_watcher_enabled", True)

    def set_enabled(self, enabled: bool):
        self.settings["ai_watcher_enabled"] = enabled
        if enabled:
            self.timer.start(800)
        else:
            self.timer.stop()
            self.is_active_ai_session = False

    def _detect_ai_tool_in_title(self, title: str) -> str:
        """Checks if a window title contains any supported AI agent keyword."""
        if not title:
            return ""
        title_lower = title.lower()
        for kw in AI_TOOL_KEYWORDS:
            if kw in title_lower:
                return kw.capitalize()
        return ""

    def _scan_active_ai_agent(self):
        if not self.is_enabled():
            return

        now = time.time()
        title = _get_active_window_title()
        tool = self._detect_ai_tool_in_title(title)

        if tool:
            # Active AI tool window in focus
            self._last_ai_active_time = now
            if not self.is_active_ai_session:
                if now - self._cooldown_time > 3.0:
                    self.is_active_ai_session = True
                    self.active_tool_name = tool
                    self.ai_thinking_started.emit(tool)
        else:
            if self.is_active_ai_session:
                if now - self._last_ai_active_time > 2.5:
                    completed_tool = self.active_tool_name
                    self.is_active_ai_session = False
                    self.active_tool_name = ""
                    self._cooldown_time = now
                    self.ai_task_completed.emit(completed_tool)

    def trigger_thinking_start(self, tool_name="AI Agent"):
        """Programmatic trigger for starting AI thinking."""
        self.is_active_ai_session = True
        self.active_tool_name = tool_name
        self.ai_thinking_started.emit(tool_name)

    def trigger_task_done(self, tool_name="AI Agent"):
        """Programmatic trigger for completing AI task -> jump celebrate."""
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self._cooldown_time = time.time()
        self.ai_task_completed.emit(tool_name)
