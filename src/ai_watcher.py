"""
AI Agent Auto-Watcher & Local Webhook Hub (Multi-Layer AI Engine)
Provides 100% synchronized reactions for:
1. Native Antigravity / Gemini Agent (Live Step-Level Transcript Streaming)
2. Web AI Prompt Detection (Gemini Web, ChatGPT Web, Claude Web via Global Enter Hook)
3. Embedded Local Webhook Server (http://127.0.0.1:59999) with Tampermonkey / cURL / Extension support
4. CLI / Workspace Agents (Aider, Claude Code, Local Models)
"""

import os
import sys
import time
import json
import glob
import ctypes
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# Keywords identifying web or desktop AI tools in window titles
AI_WINDOW_KEYWORDS = [
    "gemini", "chatgpt", "claude", "perplexity", "deepseek",
    "antigravity", "cursor", "windsurf", "copilot", "aider", "ollama"
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


class CatWebhookHandler(BaseHTTPRequestHandler):
    """Zero-latency HTTP webhook receiver on http://127.0.0.1:59999."""
    watcher_instance = None

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def _handle_request(self):
        parsed = urlparse(self.path)
        path = parsed.path.lower().rstrip("/")
        params = parse_qs(parsed.query)

        tool = params.get("tool", ["Web AI"])[0]
        msg = params.get("msg", [None])[0]

        if CatWebhookHandler.watcher_instance:
            watcher = CatWebhookHandler.watcher_instance
            if path in ("/thinking", "/start", "/think"):
                watcher.trigger_thinking_start(tool_name=tool)
            elif path in ("/celebrate", "/done", "/finish", "/jump"):
                watcher.trigger_task_done(tool_name=tool)
            elif path in ("/say", "/notify"):
                if msg:
                    watcher.external_message_received.emit(msg)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format, *args):
        pass


class AIAgentWatcher(QObject):
    # Signals
    ai_thinking_started = pyqtSignal(str)       # tool_name
    ai_task_completed = pyqtSignal(str)         # tool_name
    external_message_received = pyqtSignal(str) # custom speech bubble text

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self.celebrated_steps = set()
        self.last_seen_step_index = None

        # 1. Antigravity State Initialization
        self._init_antigravity_state()

        # 2. Start Embedded Webhook Server
        self._http_server = None
        self._http_thread = None
        self._start_webhook_server()

        # 3. High-Frequency Scan Timer (200ms interval, <0.01% CPU)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scan_all_sources)
        if self.is_enabled():
            self.timer.start(200)

    def is_enabled(self) -> bool:
        return self.settings.get("ai_watcher_enabled", True)

    def set_enabled(self, enabled: bool):
        self.settings["ai_watcher_enabled"] = enabled
        if enabled:
            self._init_antigravity_state()
            self.timer.start(200)
        else:
            self.timer.stop()
            self.is_active_ai_session = False

    def _start_webhook_server(self):
        """Starts embedded HTTP server on 127.0.0.1:59999."""
        try:
            CatWebhookHandler.watcher_instance = self
            self._http_server = HTTPServer(("127.0.0.1", 59999), CatWebhookHandler)
            self._http_thread = threading.Thread(target=self._http_server.serve_forever, daemon=True)
            self._http_thread.start()
        except Exception as e:
            print(f"[AIAgentWatcher] Webhook server init note: {e}")

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

    def _init_antigravity_state(self):
        latest = self._get_latest_antigravity_transcript()
        if not latest:
            return
        last_step = self._read_last_step(latest)
        if last_step:
            step_idx = last_step.get("step_index")
            if step_idx is not None:
                self.celebrated_steps.add(step_idx)
                self.last_seen_step_index = step_idx

    def on_user_pressed_enter(self):
        """Called by GlobalInputWatcher when Enter key is pressed without shift in an AI window."""
        if not self.is_enabled():
            return
        title = _get_active_window_title()
        if not title:
            return
        title_lower = title.lower()

        for kw in AI_WINDOW_KEYWORDS:
            if kw in title_lower:
                tool_display = kw.capitalize()
                self.trigger_thinking_start(tool_name=tool_display)
                break

    def _scan_all_sources(self):
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
        if step_idx is None:
            return

        step_type = step.get("type")
        tool_calls = step.get("tool_calls", [])
        tc_count = len(tool_calls) if tool_calls else 0
        source = step.get("source")

        # Active Antigravity step detection (only process on new step arrival)
        if time_since_mod < 30.0:
            if step_idx != self.last_seen_step_index:
                self.last_seen_step_index = step_idx
                if step_type == "USER_INPUT" or tc_count > 0 or step_type == "GENERIC":
                    self.is_active_ai_session = True
                    self.active_tool_name = "Antigravity"
                    self.ai_thinking_started.emit("Antigravity")
                elif step_type == "PLANNER_RESPONSE" and tc_count == 0 and source == "MODEL":
                    if step_idx not in self.celebrated_steps:
                        self.celebrated_steps.add(step_idx)
                        self.is_active_ai_session = False
                        self.active_tool_name = ""
                        self.ai_task_completed.emit("Antigravity")

    def trigger_thinking_start(self, tool_name="AI Agent"):
        """Programmatic / Webhook trigger for starting AI thinking."""
        self.is_active_ai_session = True
        self.active_tool_name = tool_name
        self.ai_thinking_started.emit(tool_name)

    def trigger_task_done(self, tool_name="AI Agent"):
        """Programmatic / Webhook trigger for completing AI task -> jump celebrate."""
        self.is_active_ai_session = False
        self.active_tool_name = ""
        self.ai_task_completed.emit(tool_name)
